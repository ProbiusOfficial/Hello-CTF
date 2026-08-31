---
comments: true
---

# 离散对数

> CRYPTO · 知识域。DLP 求解算法全家桶。标签:**暴力破解**、**Baby-step giant-step**、**Pollard's rho**、**Pollard's kangaroo**、**Pohlig-Hellman算法**。

## 触发特征

- 已知 `g^x = h (mod p)` 求 x;ECC 上 `xG = Q` 求 x。
- 提示"平滑阶/子群/BSGS"。

## 暴力破解

- x 空间小(如 x < 2^20 或来自小口令字典)直接枚举;`pow(g, i, p) == h` 逐个验。
- 配合约束(Z3 表达式)缩小范围 → [Z3](z3.md)。

## Baby-step giant-step(BSGS)

- 复杂度 O(√n) 时间与空间:`x = i·m + j`,查表碰撞;m = ceil(√n)。
- Python 实现十几行;SageMath `discrete_log` 默认自动选算法。
- 变体:**稀疏/低汉明重量指数**——x 的置 1 位极少时按位组合枚举而非连续搜索(2019)。

## Pollard's rho

- 期望 O(√n) 时间、O(1) 空间:伪随机游走找碰撞 `g^a h^b = g^c h^d`。
- Floyd/Brent 判圈实现;适合空间受限(大 p)场景。

## Pollard's kangaroo(λ)

- 已知 x 在区间 [a,b] 内(低位泄露/口令派生)时 O(√(b-a)) 求解。
- 袋鼠跳跃集(2 的幂)构造;Pollard kangaroo 工具(kolbasisher/kangaroo)。

## Pohlig-Hellman算法

- 前置:群阶 `n` 的因子分解 `∏ p_i^e_i` → 每个素因子子群内小规模 DLP(BSGS)→ CRT 合并。
- 判定:`factor(p-1)` 或 `factor(n)` 全平滑(最大因子 < 2^40)时必杀。
- 时钟群(p+1 阶)、ECC(`factor(n)` 平滑)同适用(→ [ECC](ecc.md))。

## 算法选择决策

1. `n` 可分解且平滑 → Pohlig-Hellman。
2. x 范围已知且窄 → kangaroo。
3. 一般情况 n < 2^60 → BSGS(内存够)/ rho。
4. 更大且无结构 → 题目必有其他弱点(回 [RSA](rsa.md)/[ECC](ecc.md) 体检)。

## 工具速查

```python
from sympy.ntheory import discrete_log       # 自动选
discrete_log(p, h, g)
# sagemath: discrete_log(Mod(h,p), Mod(g,p))
```

## 转向

- 平滑性来自参数生成缺陷 → [RSA](rsa.md);曲线结构 → [ECC](ecc.md)
