#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试模型加载 - 尝试不同的加载方式
用于诊断模型加载问题
"""

import torch
import sys
import traceback

def test_model_loading():
    """测试不同的模型加载方式"""
    print("=" * 60)
    print("模型加载测试工具")
    print("=" * 60)
    
    # 检查CUDA
    if not torch.cuda.is_available():
        print("\n✗ CUDA不可用，无法测试GPU加载")
        return
    
    print(f"\n✓ CUDA可用")
    print(f"  GPU: {torch.cuda.get_device_name(0)}")
    props = torch.cuda.get_device_properties(0)
    total_memory = props.total_memory / 1024**3
    allocated = torch.cuda.memory_allocated(0) / 1024**3
    free_memory = total_memory - allocated
    print(f"  总内存: {total_memory:.2f}GB")
    print(f"  已用: {allocated:.2f}GB")
    print(f"  可用: {free_memory:.2f}GB")
    
    # 测试1: 使用4bit量化
    print("\n" + "=" * 60)
    print("测试1: 使用4bit量化加载")
    print("=" * 60)
    try:
        from court_debate_sdk import CourtDebateModel
        print("\n尝试加载模型（4bit量化）...")
        model = CourtDebateModel(
            adapter_dir="court_debate_model",
            load_in_4bit=True,
            gpu_id=0
        )
        print("\n✓ 测试1成功: 4bit量化加载成功")
        
        # 检查模型设备
        first_param = next(model.model.parameters())
        print(f"  模型设备: {first_param.device}")
        allocated_after = torch.cuda.memory_allocated(0) / 1024**3
        print(f"  GPU内存使用: {allocated_after:.2f}GB")
        
        # 清理
        del model
        torch.cuda.empty_cache()
        print("  已清理模型")
        
    except Exception as e:
        print(f"\n✗ 测试1失败: {type(e).__name__}")
        print(f"  错误信息: {str(e)}")
        if "out of memory" in str(e).lower() or "OOM" in str(e).upper():
            print("\n  原因: GPU内存不足")
            print("  建议: 尝试不使用量化或关闭其他程序")
        traceback.print_exc()
    
    # 清理GPU内存
    torch.cuda.empty_cache()
    
    # 测试2: 不使用量化（如果测试1失败）
    print("\n" + "=" * 60)
    print("测试2: 不使用量化加载（需要更多内存）")
    print("=" * 60)
    print("提示: 如果GPU内存不足8GB，此测试可能会失败")
    
    user_input = input("\n是否继续测试2？(y/n): ").strip().lower()
    if user_input != 'y':
        print("跳过测试2")
        return
    
    try:
        from court_debate_sdk import CourtDebateModel
        print("\n尝试加载模型（不使用量化）...")
        model = CourtDebateModel(
            adapter_dir="court_debate_model",
            load_in_4bit=False,  # 不使用量化
            gpu_id=0
        )
        print("\n✓ 测试2成功: 不使用量化加载成功")
        
        # 检查模型设备
        first_param = next(model.model.parameters())
        print(f"  模型设备: {first_param.device}")
        allocated_after = torch.cuda.memory_allocated(0) / 1024**3
        print(f"  GPU内存使用: {allocated_after:.2f}GB")
        
        # 清理
        del model
        torch.cuda.empty_cache()
        print("  已清理模型")
        
    except Exception as e:
        print(f"\n✗ 测试2失败: {type(e).__name__}")
        print(f"  错误信息: {str(e)}")
        if "out of memory" in str(e).lower() or "OOM" in str(e).upper():
            print("\n  原因: GPU内存不足（不使用量化需要更多内存）")
            print("  建议: 使用4bit量化或使用更小的模型")
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_model_loading()
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n未预期的错误: {e}")
        traceback.print_exc()
        sys.exit(1)

