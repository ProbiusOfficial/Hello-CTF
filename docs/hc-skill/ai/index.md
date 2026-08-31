---
comments: true
---

# AI - 人工智能安全

> 方向技能索引。攻击对象为机器学习模型、LLM 应用、智能体系统时从本索引路由。模型相关的密码学(神经网络碰撞、格验证)同时参考 [Crypto](../crypto/index.md)。

## 知识域路由表

| 知识域 | 触发特征 |
| --- | --- |
| [信息搜集](info-gathering.md) | 探测模型 API/数据集构成 |
| [模型攻击](model-attack.md) | 对抗样本、模型窃取、越狱、后门 |
| [数据攻击](data-attack.md) | 投毒、数据伪造 |
| [模型评估](model-eval.md) | 性能/公平性/可解释性考察题 |
| [模型防御](model-defense.md) | 加固类题目或防御方案设计 |
| [数据处理](data-processing.md) | 预处理链路利用 |
| [安全防御](security-defense.md) | 安全模型训练相关 |
| [系统安全](system-security.md) | 沙箱逃逸、智能体/Agent 攻击 |

## 环境基线

```bash
pip install torch torchvision foolbox cleverhans transformers openai z3-solver
# GPU 可选;MNIST/CIFAR 是对抗样本题的事实标准数据集
```
