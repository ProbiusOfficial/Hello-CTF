---
comments: true
---

# ECC

> CRYPTO · 知识域。椭圆曲线密码攻击。标签:**模数攻击**、**Pohlig-Hellman**。

## 触发特征

- 曲线参数 `(a, b, p, G, n)`;点运算;提示"曲线/Smart/异常曲线"。

## 模数攻击

- **小阶子群**:曲线阶有小因子 → Pohlig-Hellman 分而治之(先判 `n` 的因子结构)。
- **无效曲线(invalid curve)**:点校验缺失时,把点发到弱曲线(a,b 变化)上做 DLP 再 CRT 合并。
- **异常曲线(Smart's attack)**:`#E = p`(迹为 0)→ p-adic 提升把 ECDLP 映为 F_p 内普通对数,O(1) 求解(SageMath 十几行)。
- **奇异曲线(singular)**:判别式 `4a³+27b²=0` → 群结构退化为加法群或乘法群,DLP 直接解(2018)。
- **共享素数**:多曲线模数 gcd 出公共素因子(ASIS CTF Finals 2016)。
- Ed25519 扭曲侧信道:cofactor h=8 泄露标量位(`key = master·uid mod l` 场景,2 的幂查询看 y 坐标一致性)。

## Pohlig-Hellman

- 流程:分解曲线阶 `n = ∏ p_i^e_i` → 每个子群解 DLP(小因子 BSGS/Pollard)→ CRT 合并。
- 判定:曲线阶全平滑(smooth)时秒杀;`n` 小素因子列表用 `factor(n)`。
- 时钟群变体:`x²+y²=1` 曲线阶为 p+1(不是 p-1!),p+1 平滑时同法(2018)。

## ECDSA/DSA 在曲线上的攻击

- nonce 复用/共享 → 私钥(→ [DSA](dsa.md))。
- 部分 nonce 泄露 → HNP + 格归约(→ [格密码](lattice.md))。
- 小子群注入 + 验签不校验点阶 → 私钥位泄露。

## 其他曲线结构

- **同源(isogeny)**:模多项式图遍历 + LCA 寻路(2018 advanced,识别为主)。
- 双线性配对:Groth16 setup 缺陷(delta==gamma 时直接伪造证明)、KZG 配对 oracle 恢复置换(→ [Z3](z3.md) 之外的 ZKP 族)。
- Braid 群 DH:Alexander 多项式在编织拼接下的可乘性直接算共享密钥(DiceCTF 2026)。

## 工具速查

```python
# sagemath
E = EllipticCurve(GF(p), [a,b]); n = E.order(); factor(n)
P = E(x,y); k = discrete_log(Q, P, ord=n, operation='+')   # Pohlig-Hellman 自动
# Smart's attack 脚本:/github.com/crypto101 或 jvdsn.crypto-attacks
```

## 转向

- 签名 nonce 攻击 → [DSA](dsa.md);配对与 ZKP → [Z3](z3.md)
