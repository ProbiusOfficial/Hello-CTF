---
comments: true
---

# 电子签名

> CRYPTO · 知识域。数字签名体系攻击。标签:**RSA数字签名**、**ElGamal数字签名**、**DSA数字签名**。

## 触发特征

- 题面给 (message, signature, public key) 要求伪造或验证出漏洞。
- "签名服务器"黑盒:可对任意(除目标外)消息签名。

## RSA数字签名

- **乘法同态伪造**:无 padding 的 textbook RSA 满足 `S(a)·S(b)=S(ab)`;目标消息被黑名单时分解成两因子分别签名后相乘(MMA CTF 2015)。
- **低指数伪造**:e=3 时构造 `PKCS1_pad(msg) + junk` 的立方根,Bleichenbacher 签名伪造(Google CTF 2017);尾部垃圾吸收余数。
- **e=1 + 自定模数**:验签端接受用户 (n,e) → e=1、`n = sig - PKCS1_pad(msg)` 使验签通过(BackdoorCTF 2018)。
- **textbook RSA 取负**:`enc(-1)` 配合同态绕过(2018)。
- **CRT 故障攻击**:单条错误签名 `gcd(s^e - m, n)` 泄漏因子(Bellcore,CSAW CTF 2016)。
- padding 缺失识别:签名值直接是 `m^d mod n`,m 可控时全部同态攻击适用。

## ElGamal数字签名

- **完全破译**:已知 `k`(随机数)或 `r,s` 重用 → 直接解私钥。
- **通用伪造**:选 `e=gcd(r,p-1)`,构造满足验签方程的 (r,s) 不需私钥。
- **已知/选择签名伪造**:收集多组签名拟合 k 的同余关系(CRT 合并)。
- 验签方程 `g^m ≡ y^r · r^s` 的结构弱点:任两参数可控时可解第三参数。

## DSA数字签名

- **已知 k 攻击**:`k = (H(m1)-H(m2))·(s1-s2)^-1 mod q` → 私钥 `d=(s1·k-H(m1))·r^-1`(VolgaCTF 2016 ECDSA 同式)。
- **k 共享攻击**:两签名同 r 即 k 复用(索尼 PS3 事件原型);跨消息扫描 r 值。
- **小 k 暴力**:k 位数很小(如 20 bit)全枚举(ASIS CTF Finals 2016)。
- **部分 k 泄露 → HNP 格攻击**(→ [格密码](lattice.md));`randcrack` 预测 k(当 k 由 MT 生成)。
- **k 由 MD5 碰撞源生成**:fastcoll 强制 nonce 复用(Confidence CTF 2017)。

## 协议级

- 签名 malleability(Schnorr/ECDSA `s↦q-s`)、Ed25519 同 nonce 密钥恢复(2018)。
- 证书链:SHA-1 选择前缀碰撞伪造证书(概念识别)。

## 工具速查

```bash
RsaCtfTool --attack private            # dp/dq 泄露恢复
# x509/pem 解析:openssl asn1parse
```

## 转向

- nonce 来自 PRNG → [MT19937](mt19937.md);部分 nonce 泄露 → [格密码](lattice.md)
