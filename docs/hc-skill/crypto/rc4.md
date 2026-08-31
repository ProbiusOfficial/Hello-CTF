---
comments: true
---

# RC4

> CRYPTO · 知识域。RC4 流密码及其统计弱点。标签:**密钥泄露**。

## 触发特征

- 题面提到 RC4/WEP/SSL 旧版;密钥重复使用加密多条消息。
- 密文前缀偏移(第二字节偏向 0x00)。

## 密钥泄露

- **密钥重复 = 密钥流重复**:两条密文 XOR 消去密钥流得 `P1⊕P2`, crib-dragging 恢复(同 [流密码](stream-cipher.md) OTP 套路)。
- **WEP 类 IV 弱点**:IV 与固定密钥拼接 → `FMS/KoreK` 攻击恢复密钥(aircrack-ng 直接支持)。
- **密钥可预测**:密钥来自时间戳/用户名 → 枚举种子重放 KSA(时间种子思路同 [MT19937](mt19937.md))。
- KSA 状态泄露:题目暴露 S 盒初态或部分交换记录 → 逆推密钥。

## 统计偏差攻击

- **第二字节偏差**:RC4 输出第二字节偏向 0x00(概率 1/128 vs 1/256);约 2048 条样本即可区分 RC4 与随机(Hackover CTF 2015)。
- 更多样本偏差:前 N 字节联合偏差构造区分器/明文恢复(现代 TLS RC4 弃用的原因,CTF 中作为"判断是否 RC4"的依据)。
- 逐字节恢复:大量同密钥密文下,第 i 字节频率分布固定 → 每个位置取最常见值。

## 实现细节坑

- KSA/PRGA 的 256 取模;密钥长度任意(CTF 常见 5-16 字节)。
- drop-N(丢弃前 N 字节)变体:验证时同样跳过;某些库默认 drop(如 `arc4` 与 `RC4-drop512` 混淆)。
- 与"伪 RC4"区分:出题人常魔改 KSA(如步长 2),逆向确认 → [Reverse-加密与解密](../reverse/crypto-in-reverse.md)。

## 工具速查

```python
def rc4(key, data):
    S = list(range(256)); j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    out = bytearray(); i = j = 0
    for c in data:
        i = (i + 1) % 256; j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(c ^ S[(S[i] + S[j]) % 256])
    return bytes(out)
```

## 转向

- 流密钥来自 PRNG → [LCG](lcg.md)/[MT19937](mt19937.md)
