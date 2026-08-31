---
comments: true
---

# 基于格的密码

> CRYPTO · 知识域。格归约攻击:SVP/CVP、NTRU、HNP、LWE。标签:**SVP问题**、**CVP问题**、**NTRU密码**。

## 触发特征

- 题面有"模线性方程 + 隐藏量小/稀疏/部分泄露"的组合 → 一律先当格题。
- 关键词:LLL、BKZ、NTRU、LWE、Hidden Number Problem、子集和。

## 快速分诊(Quick triage)

- 模 m 下线性关系 + 小未知量 → 构造格求短向量。
- 关键词映射:
  - 小未知量方程组 → CVP(Babai)
  - 签名 nonce 高/低位泄露 → HNP
  - LCG 高/低位泄露 → 截断 LCG = 伪装的 HNP
  - knapsack/子集和 → 低密度格
  - LWE/RLWE/Module-LWE → 嵌入 CVP

## SVP问题

- 目标:找格中最短向量。工具链:LLL(先跑)→ BKZ(LLL 差一点时)→ 块大小上调。
- fpylll / SageMath:`Matrix(B).LLL()`;BKZ `M.BKZ(block_size=20)`。
- 近似 GCD:多组 `a_i = q_i·p + r_i` 共享小素 → SVP 直接出 p(2017)。

## CVP问题

- Babai 最近平面/最近角算法:fpylll `CVP.babai`。
- **LWE 嵌入**:格 `[q·I | 0; Aᵀ | I]`,Babai 找最近向量后投影到 {-1,0,1};注意服务端描述与实际编码的端序差异(2017 CTFzone 等)。
- **RLWE/Module-LWE 识别**:多项式/负循环结构看似复杂,CTF 常用小系数、错表示或足够泄露把它"拍平"成普通 LWE(PlaidCTF 2016、DiceCTF 2022 经验)。
- **正交格**:隐藏子集/子空间问题(HSSP/AHSSP)先求正交格再重构二进制/短基(zer0pts CTF 2022)。

## NTRU密码

- 私钥 (f, g) 是短多项式,公钥 `h = f⁻¹·g` → 构造 `[I, h]` 格求短向量恢复 (f,g)。
- 参数小(N,p,q 都小)时 LLL 直接出;解密失败 oracle 变体逐位泄露。

## 经典场景模板

- **HNP**:签名 nonce 偏差 → `A·k + B·λ + C ≡ 0 (mod q)` 标准构造,归约后暴力末几位。
- **截断 LCG**:`state = observed·2^t + hidden` 逐状态成行(→ [LCG](lcg.md))。
- **子集和/背包**:密度 < 0.94 CJLOSS;建标准基,看归约行末坐标是否为 0(HITCON CTF 2017、BackdoorCTF 2023)。
- **多层组合**:几何 → 子空间恢复 → LWE → AES-GCM 解密链(终局题形态)。
- 失败排查:端序、系数符号、缩放因子、格基列序——五类常见"归约不出"原因。

## 工具速查

```python
from fpylll import IntegerMatrix, LLL, BKZ, CVP
B = IntegerMatrix.from_matrix(mat); LLL.reduction(B)
# sagemath: Matrix(ZZ, mat).LLL() / .BKZ(block_size=25)
```

## 转向

- 格攻击的输入来自 nonce 泄露 → [DSA](dsa.md);截断随机数 → [LCG](lcg.md)
