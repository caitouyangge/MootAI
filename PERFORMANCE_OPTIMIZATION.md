# 模型生成速度优化指南

## 问题诊断

如果模型生成速度很慢，可能的原因包括：

1. **模型在CPU上运行** - 这是最常见的原因，CPU推理速度比GPU慢100-1000倍
2. **max_new_tokens设置过大** - 默认值已从8192调整为2048
3. **未启用KV缓存** - 已添加 `use_cache=True` 优化
4. **GPU内存不足** - 可能导致模型部分在CPU上
5. **量化配置不当** - 4bit量化需要正确配置

## 已实施的优化

### 1. 启用KV缓存
```python
use_cache=True  # 避免重复计算，显著提升速度
```

### 2. 调整默认max_new_tokens
- 从 8192 调整为 2048
- 平衡生成长度和速度
- 如需更长文本，可手动设置更大值

### 3. 添加重复惩罚
```python
repetition_penalty=1.1  # 避免重复生成，减少无效计算
```

## 性能优化建议

### 1. 检查模型是否在GPU上

运行诊断脚本：
```bash
python diagnose_speed.py
```

或手动检查：
```python
from court_debate_sdk import CourtDebateModel

model = CourtDebateModel()
first_param = next(model.model.parameters())
print(f"模型设备: {first_param.device}")  # 应该是 cuda:0
```

### 2. 验证GPU内存使用

```python
import torch
if torch.cuda.is_available():
    allocated = torch.cuda.memory_allocated(0) / 1024**3
    print(f"GPU内存使用: {allocated:.2f}GB")
    # 如果 < 1GB，模型可能未完全加载到GPU
```

### 3. 使用torch.compile优化（可选）

PyTorch 2.0+ 支持模型编译，可以进一步提升速度：

```bash
# 设置环境变量启用编译
set TORCH_COMPILE=true
python your_script.py
```

注意：首次编译会花费一些时间，但后续推理会更快。

### 4. 调整生成参数

根据需求调整参数：

```python
# 快速生成（短文本）
response = model.generate(
    prompt="...",
    max_new_tokens=512,  # 减少token数
    temperature=0.6
)

# 长文本生成（较慢）
response = model.generate(
    prompt="...",
    max_new_tokens=4096,  # 增加token数
    temperature=0.6
)
```

### 5. 检查CUDA和PyTorch版本

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA可用: {torch.cuda.is_available()}'); print(f'CUDA版本: {torch.version.cuda}')"
```

确保：
- PyTorch版本 >= 2.0.0（支持torch.compile）
- CUDA版本匹配
- 安装了GPU版本的PyTorch

### 6. 优化量化配置

如果使用4bit量化，确保配置正确：

```python
model = CourtDebateModel(
    adapter_dir="court_debate_model",
    load_in_4bit=True,  # 启用4bit量化
    gpu_id=0
)
```

## 性能基准

正常情况下的生成速度（在GPU上）：

- **短文本（<500 tokens）**: 10-30 tokens/秒
- **中等文本（500-2000 tokens）**: 5-20 tokens/秒
- **长文本（>2000 tokens）**: 3-15 tokens/秒

如果速度明显低于上述基准，请检查：
1. 模型是否在GPU上
2. GPU内存是否充足
3. CUDA驱动是否正确安装

## 常见问题

### Q: 为什么生成速度很慢？
A: 最常见原因是模型在CPU上运行。检查 `first_param.device` 是否为 `cuda:0`。

### Q: 如何确认模型在GPU上？
A: 运行 `diagnose_speed.py` 脚本，或检查GPU内存使用情况。

### Q: max_new_tokens应该设置多少？
A: 
- 短回复：512-1024
- 中等回复：1024-2048（默认）
- 长回复：2048-4096
- 超长回复：4096-8192（会很慢）

### Q: 可以使用CPU推理吗？
A: 可以，但速度会慢100-1000倍。不推荐用于生产环境。

### Q: torch.compile会提升多少速度？
A: 通常提升20-50%，但首次编译需要额外时间。

## 进一步优化

如果以上优化仍不够，可以考虑：

1. **使用更小的模型** - 如果精度要求不高
2. **使用8bit量化** - 比4bit更快但占用更多内存
3. **使用Flash Attention** - 对于长序列可以加速（需要模型支持）
4. **批量生成** - 如果有多条请求，可以批量处理
5. **使用专门的推理框架** - 如TensorRT、ONNX Runtime等

## 联系支持

如果问题仍未解决，请提供：
1. `diagnose_speed.py` 的输出
2. GPU型号和驱动版本
3. PyTorch和CUDA版本
4. 模型加载时的日志

