---
comments: true
---

# ElGamal

> CRYPTO · 知识域。ElGamal 加密/签名攻击。标签:**完全破译攻击**、**通用伪造签名**、**已知签名伪造**、**选择签名伪造**。

## 触发特征

- 参数三元组 `(p, g, y)`;密文对 `(c1=g^k, c2=m·y^k)`;签名对 `(r, s)`。
- 提示"DDH/同态/再加密"。

## 完全破译攻击

- 私钥 x = DLP(g→y):p 平滑用 Pohlig-Hellman;一般规模用 BSGS(→ [离散对数](discrete-log.md))。
- **平凡 DLP**:基点 B=p-1 时 `B^k = ±1` 只剩符号位,直接读明文(2017+)。
- c2/c1 比值:`m = c2 · (c1^x)^-1 mod p`;私钥不可得时找 c1 的可消解结构。
- 弱随机 k:同 [DSA](dsa.md) 已知 k 攻击思想;k 复用时签名直接破。

## 通用伪造签名

- ElGamal 验签方程 `g^m ≡ y^r·r^s (mod p)`:
  - 选 `e = gcd(r, p-1)`,构造 (r, s, m') 满足方程的无私钥伪造族(经典 Bleichenbacher 方法)。
  - 令 `r = g^i·y^j` 类参数化代入,解 s 的离散式。
- 识别:验签器不校验 `1<r<p` 与 `0<s<p-1` 范围 → 伪造空间打开。

## 已知签名伪造

- 已知多组 (m, r, s):拟合 k 的同余关系,CRT 合并外推新签名。
- 重放与延展:同 r 不同消息对比提取 k(→ [DSA](dsa.md) k 共享)。
- 哈希弱化:m 直接用消息(无哈希)时按代数关系直接造。

## 选择签名伪造

- 黑盒签名 oracle 拒签目标消息 → 拆分:签 `m1·m2`(乘法同态)或 `m+a`(加法结构)后组合出目标签名。
- 自适应选择:利用验签错误回显逐参数调整(报错 oracle)。

## 结构性弱点

- **通用再加密**:无需私钥对密文再加密(语义安全破坏)→ 密文替换攻击(2017 exotic 系列)。
- 矩阵域 ElGamal:Jordan 标准型下幂运算可解析 → 私钥运算降维(2018)。
- 与 Paillier/GM 对比识别:密文结构对不上 ElGamal → [非对称密码](asymmetric.md)。

## 工具速查

```python
from sympy.ntheory import discrete_log
x = discrete_log(p, y, g)   # 平滑 p 用 Pohlig-Hellman 自动
m = c2 * pow(c1, -x, p) % p
```

## 转向

- DLP 细节 → [离散对数](discrete-log.md);ECC 上同构问题 → [ECC](ecc.md)
