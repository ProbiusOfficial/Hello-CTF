---
comments: true
---

# 对称密码

> CRYPTO · 知识域。AES/DES 双雄及其工作模式攻击的总览页。标签:**AES密码**、**DES密码**。

## 触发特征

- 题面给出 IV/密文/模式;服务端提供加解密 oracle。
- cookie/token 被对称加密后传输。

## AES密码(攻击总览,细节见 [AES](aes.md))

- 模式类:ECB 泄露与块操作、CBC 位翻转/padding oracle、CTR 计数器复用、CFB-8 重建、GCM nonce 复用(forbidden attack)。
- 实现类:S 盒被魔改、字节逐块清零 oracle 恢复密钥、错误消息解密 oracle 伪造密文。
- 密钥派生弱:`SHA256(public_key)⊕seed` 派生可还原(BSIDSSF 2026)。

## DES密码(攻击总览,细节见 [DES](des.md))

- 弱密钥(4 个)在 OFB 下密钥流周期 2 → 16 字节重复 XOR(Boston Key Party 2016)。
- 暴力(短密钥)、侧信道、差分(轮数削减)。
- 8 字节块特征:密文长度是 8 的倍数 = DES/3DES/Blowfish 提示。

## 模式速查表

| 模式 | 特征 | 攻击点 |
| --- | --- | --- |
| ECB | 同明文块→同密文块 | 块重排、剪切粘贴、选择明文逐字节(ABCTF 2016) |
| CBC | 链式 + IV | 位翻转改明文(Google CTF 2016)、padding oracle(约 4096 次/块) |
| CTR | 密钥流计数器 | nonce/counter 复用=多次一密 |
| CFB-8 | 字节反馈 | 16 字节已知明文后可重建内部状态 |
| OFB | 密钥流独立于密文 | RNG 可逆时反向解密(BSIDSSF 2026) |
| GCM | 认证加密 | nonce 复用→GHASH 认证密钥恢复(nonce-disrespect 工具) |

## oracle 类通用打法

- padding oracle:改前块测 padding 合法性,逐字节恢复中间值(PadBuster / `padding-oracle` 库)。
- 解密错误回显 oracle:发零块学习中间态,异或目标明文伪造密文块(Nuit du Hack CTF 2018)。
- 压缩 oracle:密文长度变化泄露内容(bctf 2015 CRIME 同类)。
- 命令注入组合:padding oracle 解密 + CBC 位翻转注入命令参数(BSIDSSF 2017)。

## 转向

- 模式细节与 AES 专属 → [AES](aes.md);密钥来自 PRNG → [MT19937](mt19937.md)
