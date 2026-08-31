---
comments: true
---

# 密钥交换

> CRYPTO · 知识域。密钥协商协议攻击。标签:**Diffie-Hellman**。

## 触发特征

- 题面有 `(g, p, A, B)` 协商对;流量里双方各自发公钥再算共享密钥。
- 提示"中间人/协商/共享密钥错误"。

## Diffie-Hellman

- **经典攻击路径**:
  1. p 可分解且平滑 → DLP(Pohlig-Hellman)解出私钥(→ [离散对数](discrete-log.md))。
  2. g 是原根校验缺失:小阶 g(如 g=2 配小阶 p 子群)→ 共享密钥落小子集直接枚举。
  3. 小子群注入:发送阶为 1 的点/元素(`A=1`、`A=p-1`、`A=0`)→ 共享密钥退化为常数(SRP 同类,→ [Web-认证绕过](../web/auth-bypass.md))。
- **无认证 = 中间人**:题目提供"转发者"角色时,分别与双方协商,再各自加密通信(经典 MITM 模拟题)。
- **BB-84 量子密钥分发**:经典信道无认证时完整 MITM——分别协商、强制常数位(PlaidCTF 2017)。
- **braid 群 DH**:Alexander 多项式可乘性直接算密钥(DiceCTF 2026)。
- **tropical 半环 DH**:min-plus 矩阵 residual 直接恢复共享密钥(2018 exotic)。
- **SRP 协议**:`A=0`/`A=n` 使共享密钥为 0 绕过口令验证(ASIS CTF Finals 2016)。

## 参数体检

- p 位长(过短直接 DLP);`factor(p-1)` 平滑性;g 是否原根;双方参数是否独立。
- ECC 侧:曲线阶平滑、点校验缺失(invalid curve,→ [ECC](ecc.md))。

## 会话密钥使用缺陷

- 协商出的密钥直接 XOR/单块加密(无 KDF)→ 结构泄露。
- 密钥确认缺失:密文可区分时逐候选验证(已知明文)。

## 工具速查

```python
# MITM 模拟:pwntools 双连接对敲
# 校验 g 原根:factor(p-1) 后逐素因子验 g^((p-1)/q) != 1
```

## 转向

- DLP 细节 → [离散对数](discrete-log.md);协议实现缺陷(会话/认证)→ [Web-认证绕过](../web/auth-bypass.md)
