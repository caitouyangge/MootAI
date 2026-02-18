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
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            device_map=device_map,
            torch_dtype=torch_dtype,
            quantization_config=quant_config,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        )
        
        # 加载PEFT适配器
        print(f"[SDK] 加载PEFT适配器...")
        self.model = PeftModel.from_pretrained(
            self.model,
            self.adapter_dir,
            device_map=device_map if self.gpu_id is not None else None
        )
        self.model.eval()
        
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
        max_new_tokens: int = 512,
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
        max_new_tokens: int = 512,
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
        max_new_tokens: int = 512,
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
        max_new_tokens=512,
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
    response = model.chat(messages, max_new_tokens=512)
    print("对话结果:")
    print(response)
    print("\n" + "="*60 + "\n")
    
    # 使用案件文件
    if os.path.exists("case_demo.json"):
        response = model.generate_from_case(
            case_file="case_demo.json",
            prompt="请开始陈述指控事实。",
            max_new_tokens=512
        )
        print("案件文件生成结果:")
        print(response)


