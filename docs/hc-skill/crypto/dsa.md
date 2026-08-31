---
comments: true
---

# DSA

> CRYPTO · 知识域。DSA/ECDSA 签名中 nonce 相关攻击。标签:**已知k攻击**、**k共享攻击**。

## 触发特征

- 签名参数 (r, s);提示"nonce/随机数";多条签名可收集。

## 已知k攻击

- 任意一条签名泄露 k(题面直接给或从 PRNG 推)→ 私钥一步解出:
  `d = (s·k - H(m)) · r^-1 mod q`。
- k 的来源排查:时间戳(枚举)、计数器(递增)、PRNG 输出(→ [MT19937](mt19937.md)/[LCG](lcg.md))。

## k共享攻击

- 两条签名 r 相同 ⇒ k 相同:
  `k = (H(m1)-H(m2))·(s1-s2)^-1 mod q` → 代回求 d。
- 自动化:收集全部签名,按 r 分组;跨会话扫描。
- 原型事件:索尼 PS3 ECDSA 固定 nonce;CTF 原题 VolgaCTF 2016(DSA nonce 复用)、Ed25519 同 nonce 密钥恢复(2018)。
- 变体:**k 部分重复**(高位/低位相同)→ 差分转 HNP(→ [格密码](lattice.md))。

## 其他 nonce 缺陷

- **小 k**:位数受限(20 bit)全枚举,校验 `g^k mod p == r`(ASIS CTF Finals 2016)。
- **k 偏差**(高/低位泄露):归一化后格归约,HNP(Hackim 2020、Ledger Donjon 2020)。
- **k 由弱 PRNG 生成**:`randcrack` 喂 MT 输出预测下一条 k;LCG 中间相遇(Java LCG 部分 mod,2018)。
- **k 由 MD5 碰撞生成**:fastcoll 构造前缀碰撞强制两次 k 相同(Confidence CTF 2017)。
- ** biased LSB oracle / runs 恢复**:oracle 模式跑长统计恢复(2018)。

## 实现校验缺陷

- 验签不校验 r,s ∈ [1,q-1]:malleability(`s↦q-s`)与伪造空间。
- `H(m)` 直接传消息(无哈希):签名方程可参数化求解。
- DSA 参数组共享且 q 小 → Pohlig-Hellman 直接解 DLP。

## 工具速查

```python
def dsa_recover_d(m1, s1, m2, s2, r, q):
    k = ((h(m1) - h(m2)) * pow(s1 - s2, -1, q)) % q
    return (s1 * k - h(m1)) * pow(r, -1, q) % q
```

## 转向

- ECDSA/ECC 曲线细节 → [ECC](ecc.md);k 与格 → [格密码](lattice.md)
