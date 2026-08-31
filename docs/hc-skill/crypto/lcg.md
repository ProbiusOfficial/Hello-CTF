---
comments: true
---

# LCG

> CRYPTO · 知识域。线性同余生成器状态恢复。标签:**A/B/M/N0已知**、**增量未知**、**增量和乘数都未知**、**增量/乘数/模数均未知**。

## 触发特征

- `x_{n+1} = (a·x_n + b) mod m` 结构;连续输出若干个;Java `Random`/C `rand`(部分)底层同族。
- 提示"随机数连续输出/预测下一个"。

## A/B/M/N0已知

- 参数全知 → 直接前推/后推:`x_prev = a^-1·(x_next - b) mod m`(乘法逆元)。
- 预测/回溯输出;跳位:`x_{n+k}` 用几何级数和公式一步算。

## 增量未知

- 两个连续输出消 a:`b = (x2 - a·x1) mod m`;`x2-x1 = a·(x1-x0) mod m` 解 a。
- 已知 m 与 ≥2 个连续输出即可解。

## 增量和乘数都未知

- 已知 m:三个连续输出解 a、b(消元)。
- `x2-x1 = a·(x1-x0)` → a = (x2-x1)·(x1-x0)^-1 mod m。

## 增量/乘数/模数均未知

- **步骤 1 恢复 m**:对输出差 `t_i = x_{i+1}-x_i` 求多重 GCD:`gcd(t1·t3 - t2², t2·t4 - t3², ...)`(若干乘积取 gcd),剔除小因子候选后验证。
- **步骤 2 恢复 a、b**:m 已知后回到上一节。
- Java LCG(48 位高位输出):**中间相遇**部分模数恢复(2018);高位截断输出 → 逐个状态写成 `observed·2^t + hidden`,HNP 格攻击(→ [格密码](lattice.md))。
- **前向/后向跳变**:模逆求前驱;`a` 不可逆(gcd(a,m)≠1)时多态枚举。
- **周期检测**:结构可疑时先找周期(2018 变体)。

## 关联体系

- C `rand()`:glibc 为 additiveFeedback(TYPE_3)非 LCG,用 ctypes 直接同步调用复现(L3akCTF 2024、MireaCTF)。
- 微软 VB/Excel LCG 族参数公开,套表即可。
- LFSR 型 → [LFSR](lfsr.md);MT 型 → [MT19937](mt19937.md);非线性 → Z3。

## 工具速查

```python
# 已知 m 求参数
a = (x2 - x1) * pow(x1 - x0, -1, m) % m
b = (x1 - a * x0) % m
# randcrack 库支持 LCG/MT 状态注入
```

## 转向

- 截断输出(高位/低位缺失)→ [格密码](lattice.md);预测后打什么(签名 k、token)→ 对应页

## 例题

### 参数全恢复(jvdsn/crypto-attacks)

输出序列足够长时,m/a/c 一步全解:

```python
# github.com/jvdsn/crypto-attacks
from attacks.lcg import parameter_recovery
m, a, c = parameter_recovery.attack(sequence)   # sequence: 连续输出列表
```

手推路径:差分求 `gcd(t1·t3 - t2², t2·t4 - t3², ...)` 得 m → 消元解 a、b(见上节)。

### LCG 生成素数 → RSA 弱化(组合套题)

RSA 的 p、q 来自 LCG 时,先从密文/已知明文差分恢复 LCG 输出,再生成本素数序列分解 N:

```python
def recover_lcg_output(plaintext, ciphertext, timestamp):
    pt_bytes = plaintext.encode().ljust(32, b'\0')
    ct_int = int.from_bytes(bytes.fromhex(ciphertext), 'big')
    return timestamp ^ int.from_bytes(pt_bytes, 'big') ^ ct_int

# 参数恢复后重放素数生成
lcg = LCG(a, c, m, seed)
primes = []
while len(primes) < 8:
    cand = lcg.next()
    if is_prime(cand) and cand.bit_length() == 256:
        primes.append(cand)
n = prod(primes)
phi = prod(p - 1 for p in primes)
d = pow(65537, -1, phi)
```

套路认知:凡"密钥材料来自弱 PRNG"的题,把 PRNG 攻击当作整条链的第一环(→ [MT19937](mt19937.md) 同理)。
