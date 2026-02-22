#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速检查脚本 - 诊断模型加载中断问题
"""

import torch
import os
import sys

def quick_check():
    """快速检查常见问题"""
    print("=" * 60)
    print("快速诊断检查")
    print("=" * 60)
    
    # 1. 检查CUDA
    print("\n[1] CUDA环境:")
    if torch.cuda.is_available():
        print(f"  ✓ CUDA可用")
        print(f"  - 版本: {torch.version.cuda}")
        print(f"  - GPU: {torch.cuda.get_device_name(0)}")
        props = torch.cuda.get_device_properties(0)
        total = props.total_memory / 1024**3
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        free = total - allocated
        print(f"  - 总内存: {total:.2f}GB")
        print(f"  - 已用: {allocated:.2f}GB")
        print(f"  - 可用: {free:.2f}GB")
        
        if free < 4.0:
            print(f"  ⚠ 警告: 可用内存较少（{free:.2f}GB），可能不足以加载模型")
    else:
        print("  ✗ CUDA不可用")
        return
    
    # 2. 检查模型文件
    print("\n[2] 模型文件:")
    adapter_dir = "court_debate_model"
    if os.path.exists(adapter_dir):
        print(f"  ✓ 适配器目录存在: {adapter_dir}")
        
        # 检查adapter_config.json
        config_file = os.path.join(adapter_dir, "adapter_config.json")
        if os.path.exists(config_file):
            print(f"  ✓ 配置文件存在")
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    base_model = config.get("base_model_name_or_path", "")
                    if base_model:
                        print(f"  - 基础模型路径: {base_model}")
                        if os.path.exists(base_model):
                            print(f"    ✓ 基础模型目录存在")
                            # 检查模型文件大小
                            model_files = []
                            for root, dirs, files in os.walk(base_model):
                                for file in files:
                                    if file.endswith(('.bin', '.safetensors')):
                                        file_path = os.path.join(root, file)
                                        size = os.path.getsize(file_path) / 1024**3
                                        model_files.append((file, size))
                            
                            if model_files:
                                print(f"    - 找到 {len(model_files)} 个模型文件:")
                                total_size = 0
                                for file, size in model_files[:5]:  # 只显示前5个
                                    print(f"      {file}: {size:.2f}GB")
                                    total_size += size
                                if len(model_files) > 5:
                                    print(f"      ... 还有 {len(model_files) - 5} 个文件")
                                print(f"    - 总大小（部分）: {total_size:.2f}GB")
                        else:
                            print(f"    ✗ 基础模型目录不存在: {base_model}")
                            print(f"    提示: 模型可能需要从网络下载")
                    else:
                        print(f"  ⚠ 配置文件中没有基础模型路径")
            except Exception as e:
                print(f"  ✗ 读取配置文件失败: {e}")
        else:
            print(f"  ✗ 配置文件不存在: {config_file}")
    else:
        print(f"  ✗ 适配器目录不存在: {adapter_dir}")
        return
    
    # 3. 检查内存
    print("\n[3] 内存检查:")
    try:
        import psutil
        ram = psutil.virtual_memory()
        print(f"  - 系统RAM: {ram.total / 1024**3:.2f}GB")
        print(f"  - 已用: {ram.used / 1024**3:.2f}GB")
        print(f"  - 可用: {ram.available / 1024**3:.2f}GB")
        print(f"  - 使用率: {ram.percent:.1f}%")
        
        if ram.available < 8 * 1024**3:  # 小于8GB
            print(f"  ⚠ 警告: 可用RAM较少，可能影响模型加载")
    except ImportError:
        print("  ℹ 无法检查系统内存（需要psutil库）")
    
    # 4. 建议
    print("\n[4] 建议:")
    suggestions = []
    
    if torch.cuda.is_available():
        props = torch.cuda.get_device_properties(0)
        free = (props.total_memory - torch.cuda.memory_allocated(0)) / 1024**3
        if free < 4.0:
            suggestions.append("GPU内存不足，建议:")
            suggestions.append("  - 关闭其他占用GPU的程序")
            suggestions.append("  - 使用4bit量化（已启用）")
            suggestions.append("  - 如果仍然失败，尝试不使用量化但需要更多内存")
    
    if not suggestions:
        suggestions.append("配置看起来正常")
        suggestions.append("如果加载仍然失败，可能是:")
        suggestions.append("  - 模型文件损坏")
        suggestions.append("  - 加载过程中出现未知错误")
        suggestions.append("  - 建议运行 test_model_loading.py 进行详细测试")
    
    for s in suggestions:
        print(f"  {s}")
    
    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)
    print("\n下一步:")
    print("  1. 如果GPU内存充足，运行: python test_model_loading.py")
    print("  2. 如果仍然失败，查看详细错误信息")
    print("  3. 检查是否有其他程序占用GPU")

if __name__ == "__main__":
    try:
        quick_check()
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

