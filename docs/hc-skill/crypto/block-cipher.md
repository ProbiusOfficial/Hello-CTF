---
comments: true
---

# 分组密码

> CRYPTO · 知识域。分组结构与工作模式攻击的通用面,含 ARX/IDEA 等特定结构。标签:**ARX加密**、**IDEA加密**。

## 触发特征

- 密文按固定块长(8/16 字节)分段;题目给出 IV、模式(CBC/ECB/CTR/CFB/OFB)。
- 自定义 Feistel/ARX 结构的"轻量分组密码"。

## 模式级攻击(通用,详见 [AES](aes.md))

- ECB 块重排/字节逐块选择明文;CBC 位翻转、padding oracle;CTR 计数器复用;CFB-8 静态 IV 状态重建;OFB 密钥流重复。
- 密文长度侧信道 = 压缩 oracle(CRIME 同源,bctf 2015)。

## ARX加密

- Add-Rotate-XOR 结构(如 Speck/ChaCha/BLAKE 内核、自定义轮函数):
  - 识别:循环内有 `+`,`<<<`,`⊕` 组合,无常数盒。
  - 差分分析:轮数少(≤4)时找高概率差分路径,活动字少 → 输入差分遍历统计输出差分分布。
  - 旋转-加法线性化:小范围枚举进位,把模加近似线性化后联立。
- 轮函数可逆性检查:结构对称/常数相同 → 滑动攻击(slide attack)。

## IDEA加密

- 8.5 轮、16 位字、三种混合运算(模 2^16+1 乘、模 2^16 加、XOR)。
- CTF 考点:
  - **弱密钥**:IDEA 存在弱密钥类(部分密钥下加密退化为简单结构),加密黑盒恒等时命中。
  - 轮数削减变体(2-4 轮)差分/积分攻击。
  - 实现缺陷:子密钥生成逆推(已知全部轮子密钥时逆向密钥调度)。
- 已知完整轮密钥 → 直接逆向轮函数(各运算均可逆:乘法逆元 mod 65537)。

## 自定义结构通用流程

1. 逆向确认轮结构 → [Reverse](../reverse/index.md)。
2. 检查错误实现:轮数不够、常数硬编码、密钥直接参与末轮。
3. 结构攻击族:差分/积分/滑动/impossible differential,轮数 ≤4 优先差分。

## 工具速查

```python
# ECB/模式攻击工具:FeatherDuster、padbuster
# sagemath 差分统计小工具自写即可
```

## 转向

- AES/DES 专属攻击 → [AES](aes.md)/[DES](des.md);oracle 类 → [对称密码](symmetric.md)
