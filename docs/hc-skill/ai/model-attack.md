---
comments: true
---

# 模型攻击

> AI · 知识域。针对模型本体的攻击。标签:**对抗样本攻击**、**模型反向工程**、**模型数据窃取**、**模型窃取攻击**、**模型越狱攻击**、**模型后门攻击**。

## 触发特征

- "让分类器把 X 判成 Y""从 API 复刻模型""绕过 LLM 安全策略"。

## 对抗样本攻击

- **FGSM**:单步梯度符号扰动,`x' = x + ε·sign(∇L)`;**PGD**:FGSM 多步迭代 + 投影回 ε 球(事实标准强基线);**C&W**:优化目标函数最小化扰动(最强)。
- 工具:foolbox(`fb.attacks.FGSM/L1BasicIterativeAttack`——nullcon 2019 Keras MNIST 认证题)、cleverhans、ART。
- **手写梯度获取**:框架不暴露梯度时手动实现(K.gradients,Keras FGSM,UTCTF 2019)。
- 对抗补丁(物理世界 patch);黑盒迁移攻击(代理模型生成后迁移)。
- **权重扰动抵消**:题目给"被扰动的模型"要求恢复——扰动是固定矩阵时可逆(DiceCTF 2026)。

## 模型反向工程

- 白盒:权重→结构还原(逐层读 shape);黑盒:查询拟合边界(→ [信息搜集](info-gathering.md))。
- **神经网络编码器碰撞**:构造同编码不同输入(RootAccess2026);**逆向 DNN sigmoid 逐层求逆**(N1CTF 2018)。

## 模型数据窃取 / 模型窃取攻击

- 成员推断、属性推断、训练数据重建(→ [信息搜集](info-gathering.md));LoRA 适配器权重合并窃取(ApoorvCTF 2026)。
- 模型文件泄露(.pt/.h5/.onnx)直接加载 → 权重级攻击面。

## 模型越狱攻击

- LLM 越狱:角色扮演、前缀注入("以…开头")、多轮上下文积累、Token 走私(编码绕过:base64/拼音/字母逐个)、低资源语言绕过。
- **安全模型类别缺口**:辅助安全分类器的分类盲区绕过(UTCTF 2026);Web 型 LLM 题结合直接 API 注入(→ [WEB](../web/index.md))。
- 系统提示提取;输出过滤器绕过(要求 JSON/markdown 包裹干扰审查)。

## 模型后门攻击

- 后门触发器检测:激活聚类、干净标签后门分析。
- 数据投毒型后门(→ [数据攻击](data-attack.md));题目"找出 poisoned 样本"用损失分布离群检测。

## 工具速查

```python
attack = fb.attacks.PGD(steps=40)
raw, adv, success = attack(f, images, labels)
```

## 转向

- LLM 应用的 Web 面 → [WEB](../web/index.md);智能体系统 → [系统安全](system-security.md)
