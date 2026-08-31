---
comments: true
---

# 信息搜集

> AI · 知识域。模型与数据集的前置侦察。标签:**模型信息搜集**、**数据集信息搜集**。

## 触发特征

- 题目给一个"模型 API"(预测接口/聊天接口),要求先摸清黑盒内部。
- 提供训练数据集,要求审计其构成/泄露。

## 模型信息搜集

- API 探测:输入类型与维度(逐维试探)、输出层结构(分类标签数/置信度分布)、决策边界位置。
- **模型提取(Model Extraction via Query API)**:大量查询 + 输出标签训练代理模型(softmax 输出比 hard label 有效得多)。
- 量化指纹:输出精度、是否 softmax、温度参数;梯度可获取时(白盒)看参数形状反推架构。
- LLM:系统提示词提取("重复你收到的第一条消息"类攻击)、模型版本指纹(回答风格/知识截止)。

## 数据集信息搜集

- **成员推断(Membership Inference)**:判断某样本是否在训练集(过拟合模型置信度差异);影子模型(shadow model)训练攻击分类器。
- 数据集统计:类别分布、特征范围;均值/方差反推归一化参数。
- **梯度下降反演(Gradient Inversion)**:泄露的梯度 + 网络结构反推训练样本(BSidesSF 2025 模型反演)。
- 公开数据集比对:MNIST/CIFAR/IMDB 残留样本匹配。

## 工具速查

```python
# foolbox / art(Adversarial Robustness Toolbox)自带攻击套件
import foolbox as fb
f = fb.PyTorchModel(model, bounds=(0,1))
```

## 转向

- 摸清后发起攻击 → [模型攻击](model-attack.md);API 本身有 Web 漏洞 → [WEB](../web/index.md)
