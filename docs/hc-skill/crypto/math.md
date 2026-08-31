---
comments: true
---

# 数理

> CRYPTO · 知识域。密码题背后的数学工具箱。标签:**Costas阵列**、**欧拉降幂**、**BSGS**、**同余**。

## 触发特征

- 题目核心是数学结构:幂次、同余、计数、阵列构造。
- "数学题"型 Misc/Crypto 混合题。

## Costas阵列

- 定义:每行每列恰一个点、所有差向量互异(置换 + 距离向量唯一)。
- 攻击/构造:回溯生成 n≤10 的全部解;Welch/Lempel/Golomb 代数构造。
- CTF 形态:阵列作"密钥图案"或地图路径(按差向量序列解码)。

## 欧拉降幂

- `a^b ≡ a^(b mod φ(n) + φ(n)) (mod n)`(b ≥ log₂n 时通用降幂公式);n 为素数时退化为费马小定理 `a^(p-1) ≡ 1`。
- 应用:指数爆炸(`a^(b^c)` 型塔指数)先降模再求;`gcd(a,n)≠1` 时拆素因子分别处理再 CRT。
- 扩展:g 与 φ 不互素时用扩展欧拉定理。

## BSGS

- 见 [离散对数](discrete-log.md) 全节;作为"数学工具"常出现在:大幂方程、高次同余求根。

## 同余

- **线性同余方程** `ax≡b (mod n)`:先 gcd 判解数,再除 g 缩域;逆元(pow(x,-1,n))。
- **中国剩余定理**:两两互素合并;非互素扩展 CRT(逐个合并带 gcd 校验)。
- **高次同余**:`x^k ≡ a (mod p)` → ADH/Baby-step;复合模数逐素域。
- **二次剩余**:欧拉判别 `a^((p-1)/2)`;Tonelli-Shanks 开平方根;CRT 组合出 mod n 的四根(Rabin)。
- **Hensel 引理**:模 p 的根提升到 p^k(2018)。
- **威尔逊/卢卡斯定理**:组合数取模(C(n,m) mod p)大 n 小 p 场景。

## 其他高频工具

- **GF(2) 线性代数**:异或方程组高斯消元(XOR 哈希、CRC、S 盒攻击通用);GF(2^8) 消元(AES 列混淆求逆)。
- **GF(2)[x] 多项式 CRT**:模多项式余式合并(2018)。
- **Vandermonde 矩阵**:多项式系数恢复(2018)。
- **斐波那契/矩阵快速幂**:线性递推第 N 项(Pwn2Win 2018、FireShell 2019 递推计数题)。
- **质数工具**:Miller-Rabin、Pollard rho 大数分解、原根查找。
- **四元数 RSA**(2018 exotic)、**热 tropical 半ring**(residuation 直接解)。

## 工具速查

```python
import sympy as sp
sp.discrete_log / sp.sqrt_mod / sp.ntheory.residue_ntheory.ntheory
pow(a, -1, n)          # 逆元
sp.crt([...], [...])   # CRT
# sage: GF(2^8)、PolynomialRing、matrix(ZZ,...).LLL()
```

## 转向

- 同余系统规模大且带小未知量 → [格密码](lattice.md);约束非线性 → [Z3](z3.md)
