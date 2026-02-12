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
    BitsAndBytesConfig,
)
from peft import PeftModel


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

    return (
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


def add_no_thought_constraint(system_prompt: str, assistant_role: str = "") -> str:
    role_line = f"\n\n你始终扮演：{assistant_role}。" if assistant_role else ""
    return (
        system_prompt.strip()
        + role_line
        + "\n\n【输出要求（必须遵守）】\n"
        + "1) 只输出你在法庭上的“最终发言”，不要输出思考过程、分析过程、计划、旁白、元叙述。\n"
        + "2) 不要出现类似“我现在需要/首先/接下来/让我/我将/我应该/切换角色/回顾对话历史”等描述过程的话。\n"
        + "3) 直接进入陈述或反驳，语言风格贴合法庭发言。\n"
        + "4) 必须以“{角色}：”开头输出（例如“公诉人：...”/“辩护人：...”），且不要在开头自述你在做什么。\n"
        + "5) 只写最终发言内容，不要写‘我将…/我需要…/我应该…’这类过程句。"
        + "\n6) 输出格式必须为：<final>你的最终发言</final>。除了 <final>...</final> 之外不要输出任何内容。"
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


def looks_like_thought(text: str) -> bool:
    t = text.strip()
    bad_markers = [
        "我现在需要",
        "我需要切换",
        "切换到",
        "首先",
        "接下来",
        "让我",
        "我将",
        "我应该",
        "回顾对话历史",
        "确保在新的角色下",
        "语言风格",
        "辩论的逻辑顺序",
    ]
    return any(m in t for m in bad_markers)


def extract_final(text: str) -> Optional[str]:
    t = text.strip()
    start = t.find("<final>")
    end = t.find("</final>")
    if start != -1 and end != -1 and end > start:
        return t[start + len("<final>") : end].strip()
    return None


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
    DeepSeek-R1 类模型有时会把“思考/计划”当成可见输出。
    这里做最多 2 次重试：逐步加硬约束，并在最后一次把温度压到 0。
    """
    ans = generate_one(
        model=model,
        tokenizer=tokenizer,
        messages=messages,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    final = extract_final(ans)
    if final:
        return final
    if not looks_like_thought(ans):
        return ans

    role_prefix = f"{assistant_role}：" if assistant_role else "公诉人："

    # 重试 1：额外 system 强约束 + 要求以角色前缀开头
    msgs_retry = list(messages)
    msgs_retry.insert(
        1,
        {
            "role": "system",
            "content": (
                f"严格执行：只输出 <final>{role_prefix}...你的最终发言</final>。"
                "不要输出任何过程/思考/解释/计划。"
            ),
        },
    )
    ans2 = generate_one(
        model=model,
        tokenizer=tokenizer,
        messages=msgs_retry,
        max_new_tokens=max_new_tokens,
        temperature=max(0.0, min(temperature, 0.3)),
        top_p=top_p,
    )
    final2 = extract_final(ans2)
    if final2:
        return final2
    if not looks_like_thought(ans2):
        return ans2

    # 重试 2：再加一个 user 指令，并把温度降到 0（更确定）
    msgs_retry2 = list(msgs_retry)
    msgs_retry2.append(
        {
            "role": "user",
            "content": (
                f"只输出这一种格式：<final>{role_prefix}（此处写你的最终发言）</final>。"
                "不要输出任何其它文字。"
            ),
        }
    )
    ans3 = generate_one(
        model=model,
        tokenizer=tokenizer,
        messages=msgs_retry2,
        max_new_tokens=max_new_tokens,
        temperature=0.0,
        top_p=1.0,
    )
    final3 = extract_final(ans3)
    return final3 if final3 else ans3


def generate_one(
    model,
    tokenizer,
    messages: List[Dict[str, str]],
    max_new_tokens: int,
    temperature: float,
    top_p: float,
) -> str:
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
        # 对于量化模型，使用torch.cuda.amp.autocast可能有助于性能
        if torch.cuda.is_available() and device.type == 'cuda':
            with torch.cuda.amp.autocast():
                output_ids = model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    max_new_tokens=max_new_tokens,
                    do_sample=temperature > 0,
                    temperature=temperature if temperature > 0 else None,
                    top_p=top_p,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
        else:
            output_ids = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=max_new_tokens,
                do_sample=temperature > 0,
                temperature=temperature if temperature > 0 else None,
                top_p=top_p,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

    new_tokens = output_ids[0, input_ids.shape[-1] :]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter_dir", default="court_debate_model", help="LoRA 适配器目录")
    parser.add_argument("--base_model", default=None, help="可选：覆盖 adapter_config.json 里的 base model")
    parser.add_argument("--load_in_4bit", action="store_true", help="启用 4bit 量化加载（需要 bitsandbytes）")
    parser.add_argument("--max_new_tokens", type=int, default=512)
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

    tokenizer = AutoTokenizer.from_pretrained(adapter_dir, use_fast=True)
    
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
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        device_map=device_map,
        torch_dtype=torch_dtype,
        quantization_config=quant_config,
        low_cpu_mem_usage=True,
        trust_remote_code=True,
    )
    print(f"[信息] 基础模型加载完成")
    
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
    print("\n进入交互模式：直接输入内容回车；输入 /reset 清空历史；输入 /exit 退出。\n")
    while True:
        try:
            user_text = input("你> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_text:
            continue
        if user_text.lower() in {"/exit", "exit", "quit"}:
            break
        if user_text.lower() in {"/reset", "reset"}:
            history.clear()
            print("（已清空历史）")
            continue

        msgs = _build_messages(system_prompt, history, user_text)
        
        # 调试信息：显示消息结构
        if len(history) == 0:  # 只在第一次交互时显示
            print(f"[调试] 消息结构: {len(msgs)} 条消息")
            for i, msg in enumerate(msgs):
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                preview = content[:100] + "..." if len(content) > 100 else content
                print(f"  [{i+1}] {role}: {preview}")
            print()
        
        # 显示GPU使用情况（推理前）
        if torch.cuda.is_available():
            first_param = next(model.parameters())
            if first_param.device.type == 'cuda':
                gpu_idx = first_param.device.index
                allocated_before = torch.cuda.memory_allocated(gpu_idx) / 1024**3
                print(f"[调试] 推理前GPU内存: {allocated_before:.2f}GB (设备: cuda:{gpu_idx})")
        
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
        
        # 显示GPU使用情况（推理后）
        if torch.cuda.is_available():
            first_param = next(model.parameters())
            if first_param.device.type == 'cuda':
                gpu_idx = first_param.device.index
                allocated_after = torch.cuda.memory_allocated(gpu_idx) / 1024**3
                print(f"[调试] 推理后GPU内存: {allocated_after:.2f}GB, 耗时: {elapsed_time:.2f}秒")
        
        print(f"模型> {ans}\n")

        # 保存对话历史
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": ans})

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


