#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查本地模型是否是微调过的模型
"""

import os
import json
from pathlib import Path


def check_finetuned_model(adapter_dir="court_debate_model"):
    """
    检查模型是否是微调过的模型
    
    Args:
        adapter_dir: 适配器目录路径
    """
    print("=" * 60)
    print("检查本地模型是否为微调模型")
    print("=" * 60)
    print()
    
    # 检查适配器目录是否存在
    adapter_path = Path(adapter_dir)
    if not adapter_path.exists():
        print(f"❌ 错误: 适配器目录不存在: {adapter_dir}")
        print()
        print("提示: 请确保模型目录存在，或使用 --adapter_dir 指定正确的路径")
        return False
    
    print(f"✓ 适配器目录存在: {adapter_dir}")
    print()
    
    # 检查关键文件
    adapter_config_file = adapter_path / "adapter_config.json"
    adapter_model_file = adapter_path / "adapter_model.safetensors"
    adapter_model_bin = adapter_path / "adapter_model.bin"
    
    # 检查配置文件
    if not adapter_config_file.exists():
        print(f"❌ 错误: 找不到适配器配置文件: {adapter_config_file}")
        print()
        print("提示: 这不是一个有效的PEFT/LoRA适配器目录")
        return False
    
    print(f"✓ 适配器配置文件存在: {adapter_config_file}")
    
    # 检查适配器权重文件
    has_adapter_weights = False
    if adapter_model_file.exists():
        size_mb = adapter_model_file.stat().st_size / (1024 * 1024)
        print(f"✓ 适配器权重文件存在: {adapter_model_file} ({size_mb:.2f} MB)")
        has_adapter_weights = True
    elif adapter_model_bin.exists():
        size_mb = adapter_model_bin.stat().st_size / (1024 * 1024)
        print(f"✓ 适配器权重文件存在: {adapter_model_bin} ({size_mb:.2f} MB)")
        has_adapter_weights = True
    else:
        print(f"⚠ 警告: 未找到适配器权重文件 (adapter_model.safetensors 或 adapter_model.bin)")
        print("   这可能是未完成的训练或文件丢失")
    
    print()
    
    # 读取配置文件
    try:
        with open(adapter_config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ 错误: 无法读取配置文件: {e}")
        return False
    
    # 检查关键配置项
    print("=" * 60)
    print("适配器配置信息")
    print("=" * 60)
    
    peft_type = config.get("peft_type", "未知")
    base_model = config.get("base_model_name_or_path", "未知")
    task_type = config.get("task_type", "未知")
    peft_version = config.get("peft_version", "未知")
    
    print(f"微调类型: {peft_type}")
    print(f"PEFT版本: {peft_version}")
    print(f"任务类型: {task_type}")
    print(f"基础模型: {base_model}")
    print()
    
    # 如果是LoRA，显示LoRA参数
    if peft_type == "LORA":
        r = config.get("r", "未知")
        lora_alpha = config.get("lora_alpha", "未知")
        lora_dropout = config.get("lora_dropout", "未知")
        target_modules = config.get("target_modules", [])
        
        print("LoRA参数:")
        print(f"  - 秩 (r): {r}")
        print(f"  - Alpha: {lora_alpha}")
        print(f"  - Dropout: {lora_dropout}")
        print(f"  - 目标模块: {', '.join(target_modules) if target_modules else '未知'}")
        print()
    
    # 检查基础模型是否存在
    print("=" * 60)
    print("基础模型检查")
    print("=" * 60)
    
    if base_model and base_model != "未知":
        base_model_path = Path(base_model)
        if base_model_path.exists():
            print(f"✓ 基础模型目录存在: {base_model}")
            
            # 检查模型文件
            model_files = list(base_model_path.glob("*.safetensors")) + list(base_model_path.glob("*.bin"))
            if model_files:
                total_size = sum(f.stat().st_size for f in model_files) / (1024 ** 3)
                print(f"  - 找到 {len(model_files)} 个模型文件")
                print(f"  - 总大小: {total_size:.2f} GB")
            else:
                print(f"  ⚠ 警告: 未找到模型权重文件")
        else:
            print(f"⚠ 警告: 基础模型目录不存在: {base_model}")
            print("  提示: 模型可能从Hugging Face Hub下载，或路径配置不正确")
    else:
        print("⚠ 警告: 配置文件中未指定基础模型路径")
    
    print()
    
    # 总结
    print("=" * 60)
    print("检查结果")
    print("=" * 60)
    
    is_finetuned = (
        adapter_config_file.exists() and
        has_adapter_weights and
        peft_type != "未知"
    )
    
    if is_finetuned:
        print("✅ 确认: 这是一个微调过的模型！")
        print()
        print("模型信息:")
        print(f"  - 微调方法: {peft_type}")
        print(f"  - 基础模型: {base_model}")
        if peft_type == "LORA":
            print(f"  - LoRA秩: {config.get('r', '未知')}")
            print(f"  - LoRA Alpha: {config.get('lora_alpha', '未知')}")
    else:
        print("❌ 警告: 无法确认这是一个完整的微调模型")
        print()
        if not adapter_config_file.exists():
            print("  - 缺少适配器配置文件")
        if not has_adapter_weights:
            print("  - 缺少适配器权重文件")
        if peft_type == "未知":
            print("  - 配置文件格式异常")
    
    print()
    print("=" * 60)
    
    return is_finetuned


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="检查本地模型是否是微调过的模型")
    parser.add_argument(
        "--adapter_dir",
        type=str,
        default="court_debate_model",
        help="适配器目录路径（默认: court_debate_model）"
    )
    
    args = parser.parse_args()
    
    check_finetuned_model(args.adapter_dir)


