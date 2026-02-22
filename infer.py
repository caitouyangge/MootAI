#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用训练产物 court_debate_model（LoRA/PEFT adapter）进行本地推理/对话测试。

说明：
- court_debate_model/ 是 LoRA 适配器目录，不是完整 base model。
- 默认会从 court_debate_model/adapter_config.json 读取 base_model_name_or_path。
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Any, Optional

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoConfig,
    BitsAndBytesConfig,
)
from peft import PeftModel

# 设置 Hugging Face 镜像站点（解决网络连接问题）
def setup_hf_mirror():
    """设置 Hugging Face 镜像站点，解决网络连接问题"""
    # 检查是否已设置环境变量
    if "HF_ENDPOINT" not in os.environ:
        # 使用国内镜像站点
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        print("[信息] 已设置 Hugging Face 镜像站点: https://hf-mirror.com")
        print("[提示] 如果仍有网络问题，可以手动设置环境变量: set HF_ENDPOINT=https://hf-mirror.com")
    else:
        print(f"[信息] 使用已设置的 Hugging Face 端点: {os.environ.get('HF_ENDPOINT')}")

# 在导入后立即设置镜像
setup_hf_mirror()

# 修复 transformers 库中 quantization_config 为 None 时的序列化错误
def _patch_quantization_config():
    """修复 transformers 配置类中 quantization_config 为 None 时的序列化错误"""
    try:
        from transformers.configuration_utils import PretrainedConfig
        
        # 保存原始的 to_dict 方法
        original_to_dict = PretrainedConfig.to_dict
        
        def patched_to_dict(self, *args, **kwargs):
            # 在调用原始方法之前，检查并修复 quantization_config
            if hasattr(self, 'quantization_config') and self.quantization_config is None:
                # 临时删除 None 的 quantization_config 以避免序列化错误
                delattr(self, 'quantization_config')
                try:
                    result = original_to_dict(self, *args, **kwargs)
                finally:
                    # 不需要恢复，因为它是 None
                    pass
                return result
            else:
                return original_to_dict(self, *args, **kwargs)
        
        # 应用补丁
        PretrainedConfig.to_dict = patched_to_dict
        return True
    except Exception as e:
        print(f"[警告] 无法应用 quantization_config 补丁: {e}")
        return False

# 在导入后立即应用补丁
_patch_quantization_config()


def _load_base_model_name(adapter_dir: str, override: Optional[str]) -> str:
    if override:
        return override
    cfg_path = os.path.join(adapter_dir, "adapter_config.json")
    if not os.path.exists(cfg_path):
        raise FileNotFoundError(f"找不到 {cfg_path}，请用 --base_model 显式指定基座模型。")
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    base = cfg.get("base_model_name_or_path")
    if not base:
        raise ValueError(f"{cfg_path} 中缺少 base_model_name_or_path，请用 --base_model 指定。")
    return base


def _build_messages(system_prompt: str, history: List[Dict[str, str]], user_text: str) -> List[Dict[str, str]]:
    msgs: List[Dict[str, str]] = []
    if system_prompt.strip():
        msgs.append({"role": "system", "content": system_prompt})
    msgs.extend(history)
    msgs.append({"role": "user", "content": user_text})
    return msgs


def build_system_prompt_from_case(case_obj: Dict[str, Any]) -> str:
    """
    兼容训练时的数据字段：
    - duty_definition: { role_position, core_obligations, strategic_focus, ethical_boundaries }
    - case_background: str
    """
    duty = case_obj.get("duty_definition", {}) or {}
    role_position = duty.get("role_position", "")
    core_obligations = duty.get("core_obligations", []) or []
    strategic_focus = duty.get("strategic_focus", []) or []
    ethical_boundaries = duty.get("ethical_boundaries", []) or []
    case_background = case_obj.get("case_background", "") or ""

    prompt = (
        "你是一位专业的法律从业者，需要根据角色定位参与法庭辩论。\n\n"
        "角色定义：\n"
        f"- 角色：{role_position}\n"
        f"- 核心职责：{', '.join(core_obligations)}\n"
        f"- 策略重点：{', '.join(strategic_focus)}\n"
        f"- 道德边界：{', '.join(ethical_boundaries)}\n\n"
        "案件背景：\n"
        f"{case_background}\n\n"
        "请根据你的角色定位，在法庭辩论中：\n"
        "1. 根据对话历史理解当前辩论阶段和焦点\n"
        "2. 根据角色标记（审判员/公诉人/辩护人）切换相应的语言风格\n"
        "3. 遵循法庭辩论的逻辑顺序和程序规范\n"
        "4. 基于事实和法律条文进行专业辩论"
    )
    
    # 为审判员角色添加特殊约束
    if role_position == '审判员':
        prompt += "\n\n【重要约束】\n"
        prompt += "1. 作为审判员，你绝对不能让自己发言，不能说\"请审判员发言\"、\"请审判员继续\"等类似的话。\n"
        prompt += "2. 当你需要指定下一个发言人时，只能使用\"请原告继续\"或\"请被告继续\"。\n"
        prompt += "3. 法庭辩论中只有\"审判员\"、\"原告\"、\"被告\"三个角色可以发言，案件背景中的机构名称、公司名称等不是法庭角色。\n"
        prompt += "4. 【重要】当辩论阶段结束时，你必须发表完整的结束语，不能只说\"辩论阶段结束\"。\n"
        prompt += "   结束语应包含：对双方辩论内容的总结、对争议焦点的归纳、对从宽从重情节的说明、\n"
        prompt += "   对案件复杂性的认识、以及表明将依法公正判决的态度。\n"
        prompt += "   示例格式：\"双方围绕[争议焦点]等问题已进行多轮充分辩论。法庭注意到，[从宽情节]，\n"
        prompt += "   但[从重情节]的事实清楚，社会危害性[评价]。如何在依法惩处与合理考量其特殊情况之间作出裁量，\n"
        prompt += "   本庭将严格依照法律规定，结合全案事实与证据，作出公正判决。辩论阶段结束。\"\n"
    
    return prompt


def add_no_thought_constraint(system_prompt: str, assistant_role: str = "") -> str:
    role_line = f"\n\n你始终扮演：{assistant_role}。" if assistant_role else ""
    role_prefix = f"{assistant_role}：" if assistant_role else "公诉人："
    return (
        system_prompt.strip()
        + role_line
        + "\n\n【输出要求（必须严格遵守）】\n"
        + "1) 只输出你在法庭上的\"最终发言\"，绝对不要输出思考过程、分析过程、计划、旁白、元叙述。\n"
        + "2) 禁止出现以下任何内容：\n"
        + "   - 思考过程（如\"我需要\"、\"我将\"、\"我应该\"、\"首先\"、\"接下来\"）\n"
        + "   - 计划或列表（如\"1. 语气要...\"、\"2. 包含以下要素\"）\n"
        + "   - 元叙述（如\"给出一份符合要求的发言\"、\"构建一段\"）\n"
        + "   - 自述性语言（如\"让我\"、\"我现在需要\"、\"请根据以上要求\"）\n"
        + "3) 直接进入陈述或反驳，语言风格贴合法庭发言。\n"
        + f"4) 必须以\"{role_prefix}\"开头输出，且不要在开头自述你在做什么。\n"
        + "5) 只写最终发言内容，不要写任何过程性、计划性、分析性的文字。\n"
        + f"6) 输出格式必须严格按照以下格式，不能有任何偏差：\n"
        + f"   开始标签：必须完整输出左尖括号、final、右尖括号，即：<final>\n"
        + f"   内容：{role_prefix}你的最终发言内容\n"
        + f"   结束标签：必须完整输出左尖括号、斜杠、final、右尖括号，即：</final>\n"
        + f"   完整示例：<final>{role_prefix}你的最终发言内容</final>\n"
        + f"   重要：开始标签必须是完整的 <final>（包含左尖括号<、字母final、右尖括号>），不能缺少任何字符。\n"
        + "7) 如果输出不符合要求，系统会自动重试，请确保每次输出都是最终发言，不要包含任何思考过程。"
    )


def load_case_file(path: str) -> Dict[str, Any]:
    """加载案件JSON文件"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"找不到案件文件: {path}")
    if not os.path.isfile(path):
        raise ValueError(f"路径不是文件: {path}")
    
    print(f"[信息] 正在加载案件文件: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            case_obj = json.load(f)
        print(f"[信息] 案件文件加载成功")
        return case_obj
    except json.JSONDecodeError as e:
        raise ValueError(f"案件文件JSON格式错误: {e}")
    except Exception as e:
        raise RuntimeError(f"加载案件文件失败: {e}")


def extract_final(text: str) -> Optional[str]:
    """
    提取 <final> 标签中的内容
    如果标签不完整（只有开始标签没有结束标签），尝试提取开始标签后的所有内容
    """
    t = text.strip()
    start = t.find("<final>")
    end = t.find("</final>")
    
    if start != -1:
        if end != -1 and end > start:
            # 完整的标签
            return t[start + len("<final>") : end].strip()
        else:
            # 只有开始标签，没有结束标签，提取开始标签后的所有内容
            content = t[start + len("<final>") :].strip()
            # 记录警告（用于调试）
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"[extract_final] 检测到不完整的<final>标签，提取内容长度: {len(content)}")
            return content if content else None
    
    return None


def clean_special_tokens(text: str) -> str:
    """
    清理文本中的特殊标记（如 <|im_end|>, <|im_start|> 等）
    
    Args:
        text: 原始文本
    
    Returns:
        清理后的文本
    """
    if not text:
        return text
    
    # 移除所有特殊标记
    special_tokens = [
        '<|im_end|>',
        '<|im_start|>',
        '<|im_end|',
        '<|im_start|',
        '|im_end|>',
        '|im_start|>',
    ]
    
    cleaned = text
    for token in special_tokens:
        cleaned = cleaned.replace(token, '')
    
    return cleaned.strip()


def remove_role_prefix(text: str, role: str = "") -> str:
    """
    去除文本开头的角色前缀
    
    Args:
        text: 原始文本
        role: 角色名称（如"审判员"、"原告"、"被告"），如果为空则尝试自动检测
    
    Returns:
        去除角色前缀后的文本
    """
    if not text:
        return text
    
    text = text.strip()
    
    # 如果提供了角色名称，优先使用
    if role:
        # 尝试去除 "{role}：" 或 "{role}:"
        prefixes = [
            f"{role}：",
            f"{role}:",
        ]
        for prefix in prefixes:
            if text.startswith(prefix):
                return text[len(prefix):].strip()
    
    # 自动检测并去除角色前缀（支持常见角色）
    common_roles = ["审判员", "公诉人", "辩护人", "原告", "被告"]
    for role_name in common_roles:
        prefixes = [
            f"{role_name}：",
            f"{role_name}:",
        ]
        for prefix in prefixes:
            if text.startswith(prefix):
                return text[len(prefix):].strip()
    
    # 如果没有匹配到，返回原文本
    return text


def generate_with_retries(
    model,
    tokenizer,
    messages: List[Dict[str, str]],
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    assistant_role: str,
) -> str:
    """
    生成回复，直接返回结果，不进行思考过程检测和重试。
    """
    ans = generate_one(
        model=model,
        tokenizer=tokenizer,
        messages=messages,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    
    # 记录原始生成内容（优化：减少日志输出，改为debug级别）
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"[生成调试] 原始生成内容长度: {len(ans)}")
    
    # 尝试提取 <final> 标签中的内容
    final = extract_final(ans)
    if final:
        logger.debug(f"[生成调试] 提取到final标签，内容长度: {len(final)}")
        # 去除角色前缀（因为系统提示词要求输出时包含角色前缀，但前端会自己添加）
        cleaned = remove_role_prefix(final, assistant_role)
        # 清理特殊标记（如 <|im_end|>, <|im_start|> 等）
        cleaned = clean_special_tokens(cleaned)
        logger.debug(f"[生成调试] 最终返回内容长度: {len(cleaned)}")
        return cleaned
    
    # 如果没有 final 标签，尝试去除角色前缀后返回原始输出
    logger.debug(f"[生成调试] 未找到final标签，使用原始输出")
    cleaned = remove_role_prefix(ans, assistant_role)
    # 清理特殊标记（如 <|im_end|>, <|im_start|> 等）
    cleaned = clean_special_tokens(cleaned)
    logger.debug(f"[生成调试] 最终返回内容长度: {len(cleaned)}")
    return cleaned


def generate_one(
    model,
    tokenizer,
    messages: List[Dict[str, str]],
    max_new_tokens: int,
    temperature: float,
    top_p: float,
) -> str:
    """
    生成回复。对于 DeepSeek-R1 系列模型，尝试禁用 thinking 机制。
    """
    # 尝试禁用 thinking 模式（对于 DeepSeek-R1 系列模型）
    try:
        enc = tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
            enable_thinking=False,  # 尝试禁用思考模式
        )
    except TypeError:
        # 如果不支持 enable_thinking 参数，使用默认方式
        enc = tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
        )
    
    # 确定模型所在的设备 - 通过检查模型参数的实际设备
    first_param = next(model.parameters())
    device = first_param.device
    
    # 如果模型在CPU但CUDA可用，尝试移动到GPU（非量化模型）
    # 注意：这里不指定具体GPU，因为模型应该已经在正确的GPU上了
    if device.type == 'cpu' and torch.cuda.is_available():
        # 检查是否是量化模型
        is_quantized = getattr(model, 'is_loaded_in_4bit', False) or getattr(model, 'is_loaded_in_8bit', False)
        if not is_quantized:
            print(f"[警告] 推理时检测到模型在CPU上，尝试移动到GPU...")
            # 使用模型检测到的第一个可用GPU，或默认GPU 0
            target_gpu = 0 if torch.cuda.device_count() > 0 else None
            if target_gpu is not None:
                model = model.to(f"cuda:{target_gpu}")
                device = torch.device(f"cuda:{target_gpu}")
                print(f"[信息] 模型已移动到 {device}")
        else:
            print(f"[严重警告] 量化模型在CPU上，这会导致推理速度极慢！")
            print(f"[严重警告] 请检查模型加载时的device_map配置")
            print(f"[严重警告] 当前模型设备: {device}")
    
    # 验证设备
    if device.type == 'cuda':
        current_gpu = torch.cuda.current_device()
        if device.index != current_gpu:
            print(f"[调试] 设置当前CUDA设备为: {device.index}")
            torch.cuda.set_device(device.index)
    
    input_ids = enc["input_ids"].to(device)
    attention_mask = enc.get("attention_mask")
    if attention_mask is not None:
        attention_mask = attention_mask.to(device)
    
    # 验证输入在正确的设备上
    if input_ids.device != device:
        print(f"[警告] 输入设备不匹配: input_ids在{input_ids.device}, 模型在{device}")
        input_ids = input_ids.to(device)
        if attention_mask is not None:
            attention_mask = attention_mask.to(device)

    with torch.inference_mode():
        # 准备生成参数（优化：加快生成速度）
        # 如果temperature很低，使用greedy decoding（最快）
        use_greedy = temperature <= 0.1
        
        generation_kwargs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "max_new_tokens": max_new_tokens,
            "do_sample": not use_greedy and temperature > 0,  # 低temperature时使用greedy
            "temperature": temperature if (not use_greedy and temperature > 0) else None,
            "top_p": top_p if not use_greedy else None,  # greedy时不需要top_p
            "pad_token_id": tokenizer.eos_token_id,
            "eos_token_id": tokenizer.eos_token_id,
            "use_cache": True,  # 启用KV缓存，显著提升速度
            "repetition_penalty": 1.05 if use_greedy else 1.1,  # greedy时降低惩罚
            # 优化：使用更快的生成策略
            "num_beams": 1,  # 禁用beam search，使用greedy decoding更快
        }
        
        # 对于量化模型，使用torch.amp.autocast可能有助于性能（修复警告）
        if torch.cuda.is_available() and device.type == 'cuda':
            # 使用新的API避免警告
            try:
                with torch.amp.autocast(device_type='cuda', dtype=torch.float16):
                    output_ids = model.generate(**generation_kwargs)
            except AttributeError:
                # 兼容旧版本
                with torch.cuda.amp.autocast():
                    output_ids = model.generate(**generation_kwargs)
        else:
            output_ids = model.generate(**generation_kwargs)

    new_tokens = output_ids[0, input_ids.shape[-1] :]
    # 使用 skip_special_tokens=False 以确保所有字符都被正确解码
    # 这样可以避免 < 字符被错误处理
    decoded = tokenizer.decode(new_tokens, skip_special_tokens=False).strip()
    
    # 记录生成信息（优化：减少日志输出，改为debug级别）
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"[生成调试] 生成的新token数量: {len(new_tokens)}")
    logger.debug(f"[生成调试] 解码后内容长度: {len(decoded)}")
    
    # 检查是否包含 <final> 标签，如果没有则检查是否有 final>（可能是生成错误）
    if "<final>" not in decoded and "final>" in decoded:
        logger.warning(f"[生成调试] 检测到错误的标签格式 'final>'，应该是 '<final>'")
        logger.warning(f"[生成调试] 原始生成内容: {decoded[:500]}")
    
    return decoded


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter_dir", default="court_debate_model", help="LoRA 适配器目录")
    parser.add_argument("--base_model", default=None, help="可选：覆盖 adapter_config.json 里的 base model")
    parser.add_argument("--load_in_4bit", action="store_true", help="启用 4bit 量化加载（需要 bitsandbytes）")
    parser.add_argument("--max_new_tokens", type=int, default=2048, help="最大生成token数（默认2048，平衡速度和长度）")
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--top_p", type=float, default=0.9)
    parser.add_argument("--system", type=str, default="你是一位专业的法律从业者，需要根据角色定位参与法庭辩论。")
    parser.add_argument("--system_file", type=str, default=None, help="可选：从文本文件读取 system prompt（UTF-8）")
    parser.add_argument("--case_file", type=str, default=None, help="可选：案件 JSON 文件（包含 duty_definition/case_background）")
    parser.add_argument("--prompt", type=str, default=None, help="单次生成模式：直接输入一段用户提示词")
    parser.add_argument("--gpu", type=int, default=0, help="指定使用的GPU设备编号（默认: 0）")
    args = parser.parse_args()

    adapter_dir = args.adapter_dir
    if not os.path.isdir(adapter_dir):
        print(f"[错误] 找不到适配器目录: {adapter_dir}")
        return 2

    base_model_name = _load_base_model_name(adapter_dir, args.base_model)
    print(f"Base model: {base_model_name}")
    print(f"Adapter dir: {adapter_dir}")

    # 检查CUDA可用性
    if not torch.cuda.is_available():
        print("[警告] CUDA不可用，将使用CPU运行，速度会很慢！")
        print("请确保已安装CUDA和PyTorch的GPU版本。")
        gpu_id = None
    else:
        gpu_count = torch.cuda.device_count()
        print(f"[信息] 检测到 {gpu_count} 个GPU设备")
        
        # 验证GPU编号
        if args.gpu < 0 or args.gpu >= gpu_count:
            print(f"[错误] GPU编号 {args.gpu} 无效！可用GPU编号: 0-{gpu_count-1}")
            print(f"[信息] 将使用GPU 0作为默认设备")
            gpu_id = 0
        else:
            gpu_id = args.gpu
        
        print(f"[信息] 使用GPU: {gpu_id} ({torch.cuda.get_device_name(gpu_id)})")
        print(f"[信息] CUDA版本: {torch.version.cuda}")

    quant_config = None
    if args.load_in_4bit:
        if not torch.cuda.is_available():
            print("[警告] 4bit量化需要GPU支持，但CUDA不可用！")
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )

    try:
        tokenizer = AutoTokenizer.from_pretrained(adapter_dir, use_fast=True)
    except Exception as e:
        print(f"[警告] 从适配器目录加载 tokenizer 失败: {e}")
        print(f"[信息] 尝试从基础模型加载 tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            base_model_name,
            use_fast=True,
            trust_remote_code=True,
        )
    
    # 设置默认CUDA设备（在加载模型之前）
    if torch.cuda.is_available() and gpu_id is not None:
        torch.cuda.set_device(gpu_id)
        print(f"[信息] 设置默认CUDA设备为: cuda:{gpu_id}")
    
    # 确保使用GPU
    if torch.cuda.is_available() and gpu_id is not None:
        device_map = "auto"  # 自动分配到GPU
        torch_dtype = torch.float16
    else:
        device_map = "cpu"
        torch_dtype = torch.float32
        print("[警告] 强制使用CPU，推理速度会很慢！")
    
    # 如果使用4bit量化，需要更明确的设备映射
    if quant_config is not None and torch.cuda.is_available() and gpu_id is not None:
        # 4bit量化时，显式指定GPU设备 - 使用字典格式
        # 空字符串""表示所有未明确指定的层都放到指定设备
        device_map = {"": gpu_id}  # 将所有层放到指定的GPU
        print(f"[信息] 使用4bit量化，强制使用GPU {gpu_id}")
        print(f"[信息] 加载模型到设备: {device_map}, dtype: {torch_dtype}")
    else:
        print(f"[信息] 加载模型到设备: {device_map}, dtype: {torch_dtype}")
    
    # 加载模型
    print(f"[信息] 开始加载基础模型: {base_model_name}")
    print(f"[提示] 如果网络连接失败，请尝试：")
    print(f"  1. 设置环境变量: set HF_ENDPOINT=https://hf-mirror.com")
    print(f"  2. 或使用本地模型路径（如果已下载）")
    print(f"  3. 检查网络连接和防火墙设置")
    
    try:
        print(f"[信息] 提示: 模型加载可能需要几分钟，请耐心等待...")
        model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            device_map=device_map,
            dtype=torch_dtype,  # 使用 dtype 而不是 torch_dtype（已弃用）
            quantization_config=quant_config,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        )
        print(f"[信息] 基础模型加载完成")
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            print(f"\n[错误] 网络连接失败，无法从 Hugging Face 下载模型")
            print(f"[解决方案]")
            print(f"  1. 使用镜像站点（推荐）：")
            print(f"     在命令行中设置: set HF_ENDPOINT=https://hf-mirror.com")
            print(f"     然后重新运行此脚本")
            print(f"  2. 使用代理：")
            print(f"     set HTTP_PROXY=http://your-proxy:port")
            print(f"     set HTTPS_PROXY=http://your-proxy:port")
            print(f"  3. 手动下载模型到本地：")
            print(f"     如果模型已下载到本地目录，使用 --base_model 指定本地路径")
            print(f"     例如: --base_model ./models/deepseek-r1-distill-llama-8b")
            print(f"  4. 检查网络连接：")
            print(f"     尝试访问: https://hf-mirror.com")
            print(f"\n[详细错误信息]")
            print(f"{error_msg}")
        else:
            print(f"\n[错误] 加载模型失败: {error_msg}")
        raise
    
    # 加载PEFT适配器，确保也在GPU上
    print(f"[信息] 加载PEFT适配器: {adapter_dir}")
    
    # 在加载适配器前检查基础模型的设备
    if torch.cuda.is_available() and gpu_id is not None:
        base_first_param = next(model.parameters())
        print(f"[调试] 基础模型参数设备: {base_first_param.device}")
    
    model = PeftModel.from_pretrained(model, adapter_dir, device_map={"": gpu_id} if (torch.cuda.is_available() and gpu_id is not None) else None)
    model.eval()
    
    # 确认模型设备并强制移动到GPU（如果需要）
    if torch.cuda.is_available() and gpu_id is not None:
        # 检查多个参数以确保模型真的在GPU上
        params = list(model.parameters())[:5]  # 检查前5个参数
        devices = [p.device for p in params]
        unique_devices = set(devices)
        
        print(f"[调试] 检查模型参数设备分布:")
        for dev in unique_devices:
            count = sum(1 for d in devices if d == dev)
            print(f"  - {dev}: {count} 个参数")
        
        # 使用第一个参数作为主要设备
        first_param = params[0]
        actual_device = first_param.device
        
        if actual_device.type != 'cuda':
            print(f"[错误] 模型不在GPU上（当前设备: {actual_device}）！")
            print(f"[错误] 尝试强制移动到GPU {gpu_id}...")
            # 对于量化模型，可能需要特殊处理
            is_quantized = getattr(model, 'is_loaded_in_4bit', False) or getattr(model, 'is_loaded_in_8bit', False)
            if not is_quantized:
                try:
                    model = model.to(f"cuda:{gpu_id}")
                    # 再次检查
                    first_param = next(model.parameters())
                    actual_device = first_param.device
                    if actual_device.type == 'cuda':
                        print(f"[信息] 模型已成功移动到GPU {gpu_id}")
                    else:
                        print(f"[错误] 模型移动失败，仍在设备: {actual_device}")
                except Exception as e:
                    print(f"[错误] 移动模型到GPU {gpu_id}失败: {e}")
            else:
                print(f"[错误] 4bit/8bit量化模型无法直接移动！")
                print(f"[错误] 量化模型必须在加载时就指定正确的device_map")
                print(f"[错误] 请检查device_map配置是否正确")
        elif actual_device.index != gpu_id:
            print(f"[警告] 模型在GPU {actual_device.index}上，但期望在GPU {gpu_id}上")
        
        # 最终检查设备
        first_param = next(model.parameters())
        actual_device = first_param.device
        print(f"[信息] 模型参数实际设备: {actual_device}")
        
        # 显示GPU内存使用情况
        if actual_device.type == 'cuda':
            gpu_idx = actual_device.index
            gpu_memory = torch.cuda.get_device_properties(gpu_idx).total_memory / 1024**3
            allocated = torch.cuda.memory_allocated(gpu_idx) / 1024**3
            reserved = torch.cuda.memory_reserved(gpu_idx) / 1024**3
            print(f"[信息] GPU {gpu_idx} 内存 - 总计: {gpu_memory:.2f}GB, 已分配: {allocated:.2f}GB, 已保留: {reserved:.2f}GB")
            
            # 如果已分配内存很少，可能模型没有真正加载到GPU
            if allocated < 0.1:
                print(f"[严重警告] GPU已分配内存过少（{allocated:.2f}GB），模型可能未正确加载到GPU！")
                print(f"[严重警告] 这会导致推理速度极慢，请检查device_map配置")
            elif allocated < 1.0:
                print(f"[警告] GPU已分配内存较少（{allocated:.2f}GB），可能模型未完全加载到GPU")
            
            # 检查是否在正确的GPU上
            if gpu_idx != gpu_id:
                print(f"[警告] 模型在GPU {gpu_idx}上，但期望在GPU {gpu_id}上！")
        else:
            print(f"[错误] 模型未在GPU上，推理速度会很慢！")
    else:
        first_param = next(model.parameters())
        print(f"[信息] 模型参数设备: {first_param.device}")
        if not torch.cuda.is_available():
            print(f"[警告] CUDA不可用，将使用CPU推理，速度会很慢！")

    history: List[Dict[str, str]] = []

    # system prompt 优先级：case_file > system_file > --system
    system_prompt = args.system
    assistant_role = ""
    if args.system_file:
        print(f"[信息] 从文件加载系统提示: {args.system_file}")
        with open(args.system_file, "r", encoding="utf-8") as f:
            system_prompt = f.read().strip()
        print(f"[信息] 系统提示已加载，长度: {len(system_prompt)} 字符")
    if args.case_file:
        print(f"\n[信息] 使用案件文件: {args.case_file}")
        # 处理相对路径和绝对路径
        case_file_path = args.case_file
        if not os.path.isabs(case_file_path):
            # 相对路径：尝试当前目录
            if not os.path.exists(case_file_path):
                # 如果当前目录不存在，尝试脚本所在目录
                script_dir = os.path.dirname(os.path.abspath(__file__))
                potential_path = os.path.join(script_dir, case_file_path)
                if os.path.exists(potential_path):
                    case_file_path = potential_path
                    print(f"[信息] 使用脚本目录下的文件: {case_file_path}")
        
        case_obj = load_case_file(case_file_path)
        
        # 显示案件信息摘要
        duty = case_obj.get("duty_definition", {}) or {}
        role_position = duty.get("role_position", "")
        core_obligations = duty.get("core_obligations", []) or []
        strategic_focus = duty.get("strategic_focus", []) or []
        case_background = case_obj.get("case_background", "")
        
        print(f"[信息] 角色定位: {role_position}")
        print(f"[信息] 核心职责数量: {len(core_obligations)}")
        print(f"[信息] 策略重点数量: {len(strategic_focus)}")
        print(f"[信息] 案件背景长度: {len(case_background)} 字符")
        if case_background:
            print(f"[信息] 案件背景预览: {case_background[:100]}...")
        
        assistant_role = str(role_position or "").strip()
        system_prompt = build_system_prompt_from_case(case_obj)
        print(f"[信息] 从案件文件构建的系统提示长度: {len(system_prompt)} 字符")
        print(f"[信息] 系统提示预览（前200字符）:\n{system_prompt[:200]}...\n")
    
    system_prompt = add_no_thought_constraint(system_prompt, assistant_role=assistant_role)
    print(f"[信息] 最终系统提示长度: {len(system_prompt)} 字符")
    if assistant_role:
        print(f"[信息] 助手角色: {assistant_role}")

    # 单次生成
    if args.prompt is not None:
        msgs = _build_messages(system_prompt, history, args.prompt)
        ans = generate_with_retries(
            model=model,
            tokenizer=tokenizer,
            messages=msgs,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            assistant_role=assistant_role,
        )
        print(ans)
        return 0

    # 交互式对话
    print("\n" + "="*60)
    print("进入交互式测试模式")
    print("="*60)
    print("\n可用命令：")
    print("  /help      - 显示帮助信息")
    print("  /reset     - 清空对话历史")
    print("  /history   - 显示对话历史")
    print("  /save      - 保存对话历史到文件")
    print("  /exit      - 退出程序")
    print("\n提示：直接输入内容并回车即可与模型对话")
    print("-"*60 + "\n")
    
    conversation_count = 0
    
    while True:
        try:
            user_text = input("你> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n程序已退出。")
            break

        if not user_text:
            continue
            
        # 处理命令
        cmd = user_text.lower()
        
        if cmd in {"/exit", "exit", "quit"}:
            print("\n感谢使用！再见。")
            break
            
        if cmd in {"/reset", "reset"}:
            history.clear()
            conversation_count = 0
            print("（已清空对话历史）\n")
            continue
            
        if cmd in {"/help", "help", "/h"}:
            print("\n" + "="*60)
            print("帮助信息")
            print("="*60)
            print("\n命令说明：")
            print("  /help      - 显示此帮助信息")
            print("  /reset     - 清空所有对话历史，重新开始")
            print("  /history   - 显示当前对话历史（最近10轮）")
            print("  /save      - 将对话历史保存到文件（infer_conversation_YYYYMMDD_HHMMSS.txt）")
            print("  /exit      - 退出程序")
            print("\n使用提示：")
            print("  - 直接输入内容即可与模型对话")
            print("  - 建议在提示词中明确角色，如：'审判员：...' 或 '公诉人：...'")
            print("  - 使用 /reset 可以清空历史，开始新的对话")
            print("  - 使用 /save 可以保存对话记录")
            print("-"*60 + "\n")
            continue
            
        if cmd in {"/history", "history", "/his"}:
            if not history:
                print("（当前没有对话历史）\n")
            else:
                print("\n" + "="*60)
                print(f"对话历史（共 {len(history)} 条消息，显示最近10轮）")
                print("="*60)
                # 显示最近10轮对话（20条消息）
                recent_history = history[-20:] if len(history) > 20 else history
                for i, msg in enumerate(recent_history, 1):
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    # 截断过长的内容
                    if len(content) > 200:
                        content = content[:200] + "..."
                    role_name = "用户" if role == "user" else "模型"
                    print(f"\n[{i}] {role_name}:")
                    print(f"    {content}")
                print("-"*60 + "\n")
            continue
            
        if cmd in {"/save", "save"}:
            if not history:
                print("（没有对话历史可保存）\n")
                continue
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"infer_conversation_{timestamp}.txt"
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("="*60 + "\n")
                    f.write("模型交互对话记录\n")
                    f.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"适配器目录: {adapter_dir}\n")
                    f.write(f"基础模型: {base_model_name}\n")
                    if assistant_role:
                        f.write(f"助手角色: {assistant_role}\n")
                    f.write("="*60 + "\n\n")
                    
                    # 写入系统提示（如果有）
                    if system_prompt:
                        f.write("系统提示:\n")
                        f.write("-"*60 + "\n")
                        f.write(system_prompt[:500] + ("..." if len(system_prompt) > 500 else "") + "\n")
                        f.write("-"*60 + "\n\n")
                    
                    # 写入对话历史
                    f.write("对话历史:\n")
                    f.write("-"*60 + "\n\n")
                    for i, msg in enumerate(history, 1):
                        role = msg.get("role", "unknown")
                        content = msg.get("content", "")
                        role_name = "用户" if role == "user" else "模型"
                        f.write(f"[{i}] {role_name}:\n")
                        f.write(f"{content}\n\n")
                    f.write("="*60 + "\n")
                print(f"（对话历史已保存到: {filename}）\n")
            except Exception as e:
                print(f"（保存失败: {e}）\n")
            continue

        msgs = _build_messages(system_prompt, history, user_text)
        
        conversation_count += 1
        
        # 显示推理进度
        print(f"[第 {conversation_count} 轮对话] 正在生成回复...", end="", flush=True)
        
        import time
        start_time = time.time()
        ans = generate_with_retries(
            model=model,
            tokenizer=tokenizer,
            messages=msgs,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            assistant_role=assistant_role,
        )
        elapsed_time = time.time() - start_time
        
        # 清除进度提示，显示结果
        print("\r" + " " * 50 + "\r", end="")  # 清除进度提示
        
        print(f"模型> {ans}")
        print(f"[耗时: {elapsed_time:.2f}秒]\n")

        # 保存对话历史
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": ans})

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


