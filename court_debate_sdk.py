#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
法庭辩论模型 Python SDK
提供简单的Python接口供应用调用
"""

import os
import json
from typing import List, Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

from infer import (
    _load_base_model_name,
    build_system_prompt_from_case,
    load_case_file,
    generate_one,
    generate_with_retries,
    _build_messages,
    add_no_thought_constraint,
)


class CourtDebateModel:
    """法庭辩论模型封装类"""
    
    def __init__(
        self,
        adapter_dir: str = "court_debate_model",
        base_model: Optional[str] = None,
        load_in_4bit: bool = True,
        gpu_id: int = 0,
    ):
        """
        初始化模型
        
        Args:
            adapter_dir: LoRA适配器目录
            base_model: 基础模型路径（可选，默认从adapter_config.json读取）
            load_in_4bit: 是否使用4bit量化
            gpu_id: GPU设备ID
        """
        self.adapter_dir = adapter_dir
        self.base_model = base_model
        self.load_in_4bit = load_in_4bit
        self.gpu_id = gpu_id
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """加载模型和tokenizer"""
        print(f"[SDK] 开始加载模型...")
        
        # 检查CUDA
        if not torch.cuda.is_available():
            print("[SDK] 警告: CUDA不可用，将使用CPU（速度很慢）")
            self.gpu_id = None
            device_map = "cpu"
            torch_dtype = torch.float32
        else:
            print(f"[SDK] 使用GPU: {self.gpu_id} ({torch.cuda.get_device_name(self.gpu_id)})")
            torch.cuda.set_device(self.gpu_id)
            device_map = {"": self.gpu_id}
            torch_dtype = torch.float16
        
        # 加载基础模型名称
        base_model_name = self.base_model or _load_base_model_name(self.adapter_dir, None)
        print(f"[SDK] 基础模型: {base_model_name}")
        
        # 加载tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.adapter_dir, use_fast=True)
        
        # 量化配置
        quant_config = None
        if self.load_in_4bit:
            if not torch.cuda.is_available():
                print("[SDK] 警告: 4bit量化需要GPU支持")
            else:
                quant_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                )
        
        # 加载基础模型
        print(f"[SDK] 加载基础模型...")
        print(f"[SDK] 提示: 模型加载可能需要几分钟，请耐心等待...")
        
        # 检查GPU内存
        if torch.cuda.is_available() and self.gpu_id is not None:
            props = torch.cuda.get_device_properties(self.gpu_id)
            total_memory = props.total_memory / 1024**3
            allocated = torch.cuda.memory_allocated(self.gpu_id) / 1024**3
            free_memory = total_memory - allocated
            print(f"[SDK] GPU内存状态: 总计 {total_memory:.2f}GB, 已用 {allocated:.2f}GB, 可用 {free_memory:.2f}GB")
            
            if free_memory < 4.0 and self.load_in_4bit:
                print(f"[SDK] 警告: GPU可用内存较少（{free_memory:.2f}GB），4bit量化可能需要至少4GB")
        
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                device_map=device_map,
                dtype=torch_dtype,  # 使用 dtype 而不是 torch_dtype（已弃用）
                quantization_config=quant_config,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
            )
        except RuntimeError as e:
            error_msg = str(e)
            if "out of memory" in error_msg.lower() or "OOM" in error_msg.upper():
                print(f"\n[SDK] 错误: GPU内存不足！")
                print(f"[SDK] 错误信息: {error_msg}")
                print(f"\n[SDK] 解决方案:")
                print(f"  1. 尝试不使用4bit量化（需要更多内存但可能更稳定）")
                print(f"  2. 关闭其他占用GPU的程序")
                print(f"  3. 使用更小的模型")
                print(f"  4. 检查GPU内存是否足够（建议至少8GB）")
                raise
            else:
                print(f"\n[SDK] 错误: 模型加载失败")
                print(f"[SDK] 错误信息: {error_msg}")
                raise
        except Exception as e:
            print(f"\n[SDK] 错误: 模型加载时出现异常")
            print(f"[SDK] 错误类型: {type(e).__name__}")
            print(f"[SDK] 错误信息: {str(e)}")
            import traceback
            print(f"\n[SDK] 详细错误堆栈:")
            traceback.print_exc()
            raise
        
        # 加载PEFT适配器
        print(f"[SDK] 加载PEFT适配器...")
        try:
            self.model = PeftModel.from_pretrained(
                self.model,
                self.adapter_dir,
                device_map=device_map if self.gpu_id is not None else None
            )
            self.model.eval()
        except Exception as e:
            print(f"\n[SDK] 错误: PEFT适配器加载失败")
            print(f"[SDK] 错误类型: {type(e).__name__}")
            print(f"[SDK] 错误信息: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        
        # 可选：使用torch.compile优化（PyTorch 2.0+，需要CUDA）
        # 注意：首次编译会花费一些时间，但后续推理会更快
        if torch.cuda.is_available() and self.gpu_id is not None:
            try:
                # 检查PyTorch版本是否支持compile
                if hasattr(torch, 'compile') and torch.__version__ >= "2.0.0":
                    compile_mode = os.getenv("TORCH_COMPILE", "false").lower() == "true"
                    if compile_mode:
                        print(f"[SDK] 启用torch.compile优化（首次运行会较慢）...")
                        self.model = torch.compile(self.model, mode="reduce-overhead")
                        print(f"[SDK] torch.compile优化已启用")
            except Exception as e:
                print(f"[SDK] torch.compile优化失败（可忽略）: {e}")
        
        # 验证模型设备
        if torch.cuda.is_available() and self.gpu_id is not None:
            first_param = next(self.model.parameters())
            actual_device = first_param.device
            print(f"[SDK] 模型设备: {actual_device}")
            if actual_device.type == 'cuda':
                allocated = torch.cuda.memory_allocated(actual_device.index) / 1024**3
                print(f"[SDK] GPU内存使用: {allocated:.2f}GB")
        
        print(f"[SDK] 模型加载完成！")
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 2048,  # 默认值改为2048，平衡速度和长度
        temperature: float = 0.6,
        top_p: float = 0.9,
        system_prompt: Optional[str] = None,
        assistant_role: Optional[str] = None,
    ) -> str:
        """
        单次生成
        
        Args:
            prompt: 用户提示词
            max_new_tokens: 最大生成token数
            temperature: 生成温度
            top_p: 核采样参数
            system_prompt: 系统提示词
            assistant_role: 助手角色
        
        Returns:
            生成的回复
        """
        if not system_prompt:
            system_prompt = "你是一位专业的法律从业者，需要根据角色定位参与法庭辩论。"
        
        if assistant_role:
            system_prompt = add_no_thought_constraint(system_prompt, assistant_role)
        
        messages = _build_messages(system_prompt, [], prompt)
        
        response = generate_with_retries(
            model=self.model,
            tokenizer=self.tokenizer,
            messages=messages,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            assistant_role=assistant_role or "",
        )
        
        return response
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 2048,  # 默认值改为2048，平衡速度和长度
        temperature: float = 0.6,
        top_p: float = 0.9,
        system_prompt: Optional[str] = None,
        assistant_role: Optional[str] = None,
    ) -> str:
        """
        对话生成（带历史）
        
        Args:
            messages: 对话历史，格式：[{"role": "user", "content": "..."}, ...]
            max_new_tokens: 最大生成token数
            temperature: 生成温度
            top_p: 核采样参数
            system_prompt: 系统提示词
            assistant_role: 助手角色
        
        Returns:
            生成的回复
        """
        if not system_prompt:
            system_prompt = "你是一位专业的法律从业者，需要根据角色定位参与法庭辩论。"
        
        if assistant_role:
            system_prompt = add_no_thought_constraint(system_prompt, assistant_role)
        
        # 构建完整消息列表
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)
        
        response = generate_with_retries(
            model=self.model,
            tokenizer=self.tokenizer,
            messages=full_messages,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            assistant_role=assistant_role or "",
        )
        
        return response
    
    def generate_from_case(
        self,
        case_file: str,
        prompt: str,
        max_new_tokens: int = 2048,  # 默认值改为2048，平衡速度和长度
        temperature: float = 0.6,
        top_p: float = 0.9,
    ) -> str:
        """
        使用案件文件生成
        
        Args:
            case_file: 案件JSON文件路径
            prompt: 用户提示词
            max_new_tokens: 最大生成token数
            temperature: 生成温度
            top_p: 核采样参数
        
        Returns:
            生成的回复
        """
        case_obj = load_case_file(case_file)
        system_prompt = build_system_prompt_from_case(case_obj)
        assistant_role = case_obj.get("duty_definition", {}).get("role_position", "")
        
        return self.generate(
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            system_prompt=system_prompt,
            assistant_role=assistant_role,
        )
    
    def __del__(self):
        """清理资源"""
        if self.model is not None:
            del self.model
        if self.tokenizer is not None:
            del self.tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


# ==================== 使用示例 ====================
if __name__ == "__main__":
    # 初始化模型
    model = CourtDebateModel(
        adapter_dir="court_debate_model",
        load_in_4bit=True,
        gpu_id=0
    )
    
    # 单次生成
    response = model.generate(
        prompt="审判员：请公诉人开始陈述指控事实。",
        max_new_tokens=2048,  # 设置为2048，平衡速度和长度
        temperature=0.6
    )
    print("生成结果:")
    print(response)
    print("\n" + "="*60 + "\n")
    
    # 对话生成
    messages = [
        {"role": "user", "content": "审判员：请公诉人开始陈述。"},
        {"role": "assistant", "content": "公诉人：根据起诉书指控..."},
        {"role": "user", "content": "辩护人：针对公诉人的指控..."}
    ]
    response = model.chat(messages, max_new_tokens=2048)  # 使用2048，平衡速度和长度
    print("对话结果:")
    print(response)
    print("\n" + "="*60 + "\n")
    
    # 使用案件文件
    if os.path.exists("case_demo.json"):
        response = model.generate_from_case(
            case_file="case_demo.json",
            prompt="请开始陈述指控事实。",
            max_new_tokens=2048  # 使用2048，平衡速度和长度
        )
        print("案件文件生成结果:")
        print(response)


