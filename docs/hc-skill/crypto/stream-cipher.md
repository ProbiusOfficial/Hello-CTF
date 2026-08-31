---
comments: true
---

# 流密码

> CRYPTO · 知识域。XOR 与密钥流体系。标签:**XOR**。

## 触发特征

- 密文与明文等长、无结构;`flag{` 前缀异或已知即可验证。
- "重复密钥异""多次一密""未知密钥异或文件"题面。

## XOR 基础套路

- 单字节 XOR:256 全试,按可打印率/字母频率打分;`from pwn import xor; xor(ct, b'flag{')` 直接用已知前缀验证。
- 重复密钥 XOR(多字节):按 key 位置分列 → 每列单字节频率分析(空格 0x20 权重高);Hamming 距离估 key 长度(经典 Cryptopals 流程)。
- 级联 XOR(cascade):先爆首字节(256 次),其余字节随首字节确定级联推导。
- 幂次旋转 XOR:按 2 的幂旋转时奇偶位永不相混,候选状态只有 4 个。

## OTP 与密钥流弱点

- **多次一密(OTP 密钥复用)**:`C1⊕C2⊕P1=P2`;无已知明文时 crib-dragging(拖动猜测词):国际赛场经典。
- 确定性 OTP:负载均衡后端共用密钥流,已知明文恢复 keystream 后全量解密。
- **文件头恢复密钥**:密文声称是 PDF/PNG/ZIP 但 `file` 报 data → 前几字节与魔数 XOR 得重复密钥,再用 `%%EOF`/`IEND` 尾部结构延展(MetaCTF Flash 2026)。
- 三轮 XOR 协议:三层密钥两两相消,剩余即为明文差(2017 年 CTF 常见结构)。
- 连续字节相关性:XOR 相邻密文字节消除密钥(固定密钥时 `C[i]⊕C[i+1]=P[i]⊕P[i+1]`)。

## 流密码与 LFSR/RC4/PRNG 的边界

- 密钥流由 LFSR 生成 → [LFSR](lfsr.md);RC4 → [RC4](rc4.md);Python random/MT → [MT19937](mt19937.md);LCG → [LCG](lcg.md)。
- Z3 求解流密码约束 → [Z3](z3.md)。

## 工具速查

```python
from pwn import xor
# 已知明文差分
ks = xor(ct1, pt1)
pt2 = xor(ct2, ks)
# xortool 自动猜 key 长度
# xortool -c 20 cipher.bin
```

## 转向

- 密钥流像"随机数" → 各 PRNG 页;密文是图片 → [Misc-图片隐写](../misc/image-stego.md)
