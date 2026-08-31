---
comments: true
---

# RSA

> CRYPTO · 知识域。RSA 攻击全谱系,密码学方向第一大题库。标签:**e和phi不互素**、**暴力分解N**、**p&q不当分解N**、**中国剩余定理**、**提取PEM文件信息**、**私钥文件修复**。

## 触发特征

- 题面给 n, e, c 三元组;PEM 公钥文件;多个密文/多组公钥。
- 起手体检:`n` 位长 → `factordb` 查已知分解 → `e` 大小 → 密文间关系。

## 暴力分解N

- 小 N(<256 bit):yafu / msieve / SageMath `factor`。
- 在线:factordb.com;`sympy.factorint` 试小因子。
- 试除结构:p = next_prime(2^k+small)(2019)、多素数 N(直接 sympy 分解)、受限数字素数(逐位从 LSB 确定剪枝,2018)。
- **Fermat 分解**:p,q 相邻(`q=next_prime(p)`)或 `q≈k·p`(Coppersmith 广义,→ 下文);`isqrt` 迭代。
- **Pollard p-1**:p-1 平滑 → `pow(a, lcm(1..B), n)` gcd;变体 p+1(Williams)。
- **batch GCD**:多把公钥共享素因子(2016-2019 各赛常出);N1·N2 gcd。
- **Coppersmith**:已知素数高位(部分密钥泄露)→ `f.small_roots()`(SageMath);线性相关素数 `q=k·p+δ` 近似 `sqrt(k·n)` 后 small_roots(ASIS CTF 2018)。

## p&q不当分解N

- p、q 相邻/相近:Fermat;p、q 来自同一 PRNG 种子(→ [MT19937](mt19937.md));`p = kp·B + tp` 基表示结构暴力(BACKDOOR 风格)。
- p=q:验签端 `phi=(p-1)^2` 错误 → 解密失败泄露密文(2018)。
- 共享素数:batch GCD;ROCA 漏洞指纹检测(CVE-2017-15361,roca-detect)。

## e和phi不互素

- `g = gcd(e,phi) > 1`:令 `e' = e/g`,算 `d' = e'^-1 mod phi`,得 `m^g mod n` 后**在整数域开 g 次方**;g 与素因子结构耦合时逐素数域开根再 CRT 枚举组合(2018 cube root CRT)。
- e=1 直接得 m;e 过大 → 对应 d 小(Wiener)。

## 经典攻击速查

| 场景 | 攻击 | 备注 |
| --- | --- | --- |
| e 小 + m 小 | 直接开 e 次根 | m^e < n 时 |
| e 小 + 多密文同 m | Hastad 广播,CRT 合并开根 | 带线性 padding → CRT+Coppersmith(PlaidCTF 2017) |
| d 小 | Wiener(e 很大) | 格/连分数 |
| p±1 平滑 | Pollard p-1 / Williams p+1 | |
| 两密文线性相关 (e=3) | Franklin-Reiter 多项式 GCD(N1CTF 2018) | |
| LSB oracle | 二分搜索 log2(n) 次(Rabin 版 PlaidCTF 2016;噪声版 SharifCTF 后处理纠错) | |
| Manger oracle | 倍增+二分 ~128 次恢复 AES 密钥;OAEP 时序版(2018) | |
| 共模攻击 | 两密文同 n 不同 e 互素 → 扩展 GCD | |
| dp/dq/qinv 泄露 | 逐 k 迭代 `(dp·e-1)/k+1` 为素即 p(0CTF 2016) | |
| n=p²q | Schmidt-Samoa 类结构 | 2018+ |
| phi 的倍数泄露 | Miller-Rabin 平方根技巧分解(≥1/2 成功率) | `e·d-1` 即 phi 倍数 |
| 同态解密绕过 | oracle 拒解 c → 解 `c·r^e` 再除 r(ectf 2016) | |
| 小素因子 CRT | 试除 + 逐素域解 + CRT 合并(Hack the Vote 2016) | |
| Montgomery 时序 | 泄露额外减法次数按位恢复密钥(DEF CON 2017) | |

## 中国剩余定理

- CRT 合并广播密文;多模数残余 `r = flag mod f` 收集后 GF(2)[x] CRT(多项式域,2018)。
- Hensel 引理:p^k 上多项式根逐级提升(2018)。
- Rabin 四平方根 CRT 组合(2018)。

## 提取PEM文件信息

```bash
openssl rsa -pubin -in key.pub -text -noout     # n, e
openssl asn1parse -in key.pem                   # 完整结构
```
- 多文件比对 n/gcd;`bit_length()` 快速判位长;私钥文件直接 `openssl rsa -in key.pem -text -noout`。

## 私钥文件修复

- PEM 缺头/损坏:补 `-----BEGIN...` 头、base64 对齐;DER 解析定位 asn1 断点。
- 部分字段泄露(dp/dq/qinv)→ 上述恢复攻击;PEM 中 p 泄露一半字节 → Coppersmith。
- 工具:RsaCtfTool `--attack` 全家桶、`rsatool` 重建 PEM。

## 工具速查

```bash
python RsaCtfTool.py --publickey key.pub --uncipherfile flag.enc
sage: f = x*... ; f.small_roots(X=2^256, beta=0.5)   # Coppersmith
```

## 转向

- 多组公钥/签名体系 → [电子签名](digital-signature.md);大数运算细节 → [数理](math.md)

## 例题

### Wiener 小私钥攻击(d < N^0.25)

e 巨大(接近 n)即提示 d 很小,对 `e/n` 做连分数展开,在收敛分数中检验 `phi=(e·d-1)/k` 是否合法(反推 p+q 后判别式开方为整数):

```python
def wiener_attack(e, n):
    def continued_fraction(num, den):
        cf = []
        while den:
            q, r = divmod(num, den)
            cf.append(q); num, den = den, r
        return cf
    def convergents(cf):
        convs = []; h0, h1, k0, k1 = 0, 1, 1, 0
        for a in cf:
            h0, h1 = h1, a*h1 + h0
            k0, k1 = k1, a*k1 + k0
            convs.append((h1, k1))
        return convs
    from math import isqrt
    for k, d in convergents(continued_fraction(e, n)):
        if k == 0 or (e*d - 1) % k: continue
        phi = (e*d - 1) // k
        s = n - phi + 1
        disc = s*s - 4*n
        if disc < 0: continue
        t = isqrt(disc)
        if t*t == disc: return d
    return None

d = wiener_attack(e, n); m = pow(c, d, n)
```

也可直接 `pip install owiener`。原理:`k/φ ≈ d/n` 的连分数收敛分数中必含 `k/d`。

### Fermat 分解(p、q 相邻)

`q = next_prime(p)` 时 `|p-q|` 小,从 `sqrt(n)` 向下找第一个整除的素数:

```python
from sympy import prevprime, isqrt
root = isqrt(n)
p = prevprime(root + 1)
while n % p != 0:
    p = prevprime(p)
q = n // p
```

多层变体:1024 层嵌套加密、每层素数位长递增——逐层倒序解密即可。

### Coppersmith:线性相关素数 q ≈ k·p(ASIS CTF 2018)

已知 `q ~ k·p`(k 公开)时 `q ~ sqrt(k·n)`,对误差项跑 small_roots——Fermat 的推广:

```python
# SageMath
qbar = isqrt(4 * n)                 # k=4 时
R.<x> = PolynomialRing(Zmod(n))
f = x + qbar
roots = f.small_roots(X=2^200, beta=0.5)
q = qbar + int(roots[0]); p = n // q
```

### Franklin-Reiter 相关消息攻击 e=3(N1CTF 2018)

同一明文 m 加已知线性 padding 加密两次(padding 差已知),多项式 GCD 直接出 m:

```python
# SageMath
def franklin_reiter(n, pad1, pad2, c1, c2):
    R.<X> = PolynomialRing(Zmod(n))
    f1 = (X + pad1)^3 - c1
    f2 = (X + pad2)^3 - c2
    return -gcd(f1, f2).coefficients()[0]
```

### CRT 部分私钥泄露恢复 dp/dq/qinv(0CTF 2016)

PEM 文件尾部泄露出 dp 即够:`dp = d mod (p-1)`,枚举 k 检验 `(dp·e-1)/k + 1` 是否为素数,O(e) 秒出:

```python
import gmpy2
for k in range(3, e):
    p_candidate = (dp * e - 1) // k + 1
    if gmpy2.is_prime(p_candidate):
        p = p_candidate; break
# 同法从 dq 恢复 q;用 qinv·q % p == 1 校验
```

关键认知:**CRT 指数泄露即等于整把私钥泄露**。

### 多素数 RSA

N 为多个小素数之积时先分解再合成 phi:

```python
from sympy import factorint
factors = factorint(n)              # {p1: e1, p2: e2, ...}
phi = 1
for p, e in factors.items():
    phi *= (p-1) * p**(e-1)
d = pow(e, -1, phi); m = pow(c, d, n)
```
