---
comments: true
---

# 反馈移位寄存器

> CRYPTO · 知识域。LFSR/NLFSR 流密码生成器攻击。标签:**LFSR**、**NLFSR**。

## 触发特征

- 密钥流按位生成、状态只有 n 位;题目给出"线性反馈""特征多项式""抽头"。
- 密钥流前 2n 位可获得(已知明文 XOR 密文)。

## LFSR

- **Berlekamp-Massey**:2n 位密钥流直接恢复线性复杂度与反馈多项式(sympy/sagemath 有实现,手写约 30 行)。
- **已知明文攻击**:密钥流 = 明文 ⊕ 密文;状态转移是 GF(2) 线性方程组,高斯消元求解初始状态与抽头。
- **相关攻击(correlation attack)**:组合生成器的合并函数有偏向时,逐个生成器单独穷举 2^n 并统计吻合率。
- **Galois 抽头恢复**:XOR 已知文件头得密钥流,按 N 位窗口计算 `(state>>1) ⊕ next_state`,LSB=1 的转移直接给出抽头掩码;自相关滑动找正确长度(BSIDSSF 2026)。
- **位折叠恢复**:ASCII 奇偶性泄露 LFSR 位信息的折叠恢复(2017+ CTF 套路)。
- Galois vs Fibonacci 两种实现互转(抽头等价);注意位序(左移/右移)与初态方向。

## NLFSR

- 非线性反馈:BM 法失效,攻击面转向:
  - 过滤生成器:输出是状态的布尔函数 → 代数攻击(消元)或相关攻击。
  - 布尔函数真值表可枚举时用 Z3/SAT 求状态(→ [Z3](z3.md))。
  - 前馈序列的组合逻辑:展成 ANF(代数范式)后线性化求解。
- 软件级 NLFSR(题面自定义生成函数)直接逆向生成逻辑 → [Reverse-加密与解密](../reverse/crypto-in-reverse.md)。

## 工具速查

```python
# Berlekamp-Massey(GF(2))
# https://gist.github.com Storingvo/BM; 或 sagemath:
# sage: from sage.all import *; berlekamp_massey(GF(2)['x']...)
# 验证:用恢复的抽头重放密钥流比对
```

## 转向

- 密钥流像 MT/LCG 输出 → [MT19937](mt19937.md)/[LCG](lcg.md);约束求解 → [Z3](z3.md)

## 例题

### Berlekamp-Massey(SageMath)

已知明文 XOR 密文拿密钥流,2L 位恢复反馈多项式:

```python
from sage.all import *
keystream = [1,0,1,1,0,0,1,0,1,1,1,0,0,1]     # 已知明文 XOR 密文
R = berlekamp_massey([GF(2)(b) for b in keystream])
print(R, R.degree())                            # 反馈多项式与级数 L
state = keystream[:R.degree()]                  # 初态取前 L 位
```

### 已知明文直接解线性方程组(≥2L 位)

密钥流关系 `k[i+L] = ⊕ c_j·k[i+j]` 是 GF(2) 线性方程组:

```python
def solve_lfsr(keystream, L):
    A = [keystream[i:i+L] for i in range(L)]
    b = [keystream[i+L] for i in range(L)]
    from sage.all import matrix, vector, GF
    return list(matrix(GF(2), A).solve_right(vector(GF(2), b)))
```

### 相关攻击(组合生成器有偏向时)

合并函数偏向某一路 LFSR(`P(out = LFSR_i) > 0.5`)→ 单独穷举该路的 2^L 初态,按吻合率筛:

```python
def correlation_attack(keystream_bits, lfsr_length, taps, threshold=0.6):
    best_corr, best_state = 0, None
    for seed in range(2**lfsr_length):
        state = [(seed >> i) & 1 for i in range(lfsr_length)]
        matches, s = 0, state[:]
        for i, bit in enumerate(keystream_bits):
            if s[0] == bit: matches += 1
            s = lfsr_next(s, taps)
        if matches / len(keystream_bits) > best_corr:
            best_corr, best_state = matches/len(keystream_bits), seed
    return best_state, best_corr
```

复杂度从"联合状态 2^(L1+L2+...)"降到"逐路 2^L"——相关攻击的本质。
