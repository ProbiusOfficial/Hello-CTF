---
comments: true
---

# 非对称密码

> CRYPTO · 知识域。RSA/ECC 之外的非对称体系:背包、Paillier 及其他。标签:**背包密码**、**Paillier加密**。

## 触发特征

- 提示"Merkle-Hellman/背包""Paillier/同态""knapsack"。
- 密文结构:超递增序列、n² 模数。

## 背包密码

- **Merkle-Hellman**:私钥是超递增序列,公钥 = 超增序列模 n 乘 w 的扰动 → LLL 归约恢复私有结构(SageMath `Matrix(...).LLL()`)。
- **低密度子集和**:密度 `d = n / log2(max(a_i)) < 0.94` 时 CJLOSS/LO 格攻击可解。
- 直接解密路径:恢复超增结构后贪心(从大到小选)。
- 判定:公钥是 N 个大整数、密文单数 → 背包;密文给 0/1 串向量 → 子集和。

## Paillier加密

- 结构:`n=p·q`,`g=n+1` 标准参数;密文 `c = g^m·r^n mod n²`。
- **同态性**:加法同态 → oracle 题直接算 `E(m1)·E(m2)=E(m1+m2)`;**倍增 LSB oracle**:密文乘 `g^2` 使明文翻倍,oracle 告知奇偶 → 二分恢复(2018)。
- **密文分解绕过 oracle 大小判断**:c 可分解时直接约简(2018)。
- 私钥泄露路径:p、q 已知 → λ=n/p·q 的 lcm;参数非标准(g≠n+1)先归一化。
- **噪声消除**:差分隐私噪声叠加可被多次平均消除(2018 exotic)。
- 全同态比特提取:乘法同态逐位 oracle(2018)。

## 其他非对称体系

- **Goldwasser-Micali**:每密文 1 bit;复制单密文 N 次强制全 0/全 1 密钥,哈希 oracle 区分,128 次查全 AES 密钥(BSIDSSF 2026)。
- **Blum-Goldwasser**:BBS 平方序列;逐位扩展 oracle(PlaidCTF 2013)。
- **Rabin**:`c=m² mod n`;LSB oracle 二分;四根 CRT 合并解密;多项式素数变体(2018)。
- **NTRU**:格归约解密失败泄露 → 私钥恢复(→ [格密码](lattice.md))。
- **OSS 签名**(Ong-Schnorr-Shamir):Pollard 方法伪造(2018)。
- **Cayley-Purser**:无私钥也能解(2018 exotic)。
- **BIP39 助记词**:部分词 + 校验和暴力(2018)。
- **Asmuth-Bloom 门限**:CRT 门限秘密共享恢复(2018)。

## 工具速查

```python
# Paillier 手写:pip install phe 也能打标准参数
n2 = n*n
c2 = (c * pow(g, 2, n2)) % n2   # 明文+2
```

## 转向

- 格归约通用 → [格密码](lattice.md);RSA/Rabin 细节 → [RSA](rsa.md)
