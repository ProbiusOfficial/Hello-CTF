---
comments: true
---

# 单表替换加密

> CRYPTO · 知识域。一张固定映射表替换字母。标签:**乘法密码**、**仿射密码**、**词频分析**。

## 触发特征

- 密文字母频率分布与英文相似但映射不同(高频字符仍是高频,只是换了字母)。
- 提示"替换/映射表未知"。

## 乘法密码

- `E(x)=ax mod 26`,要求 `gcd(a,26)=1` 可选 a ∈ {1,3,5,7,9,11,15,17,19,21,23,25} 共 12 个。
- 解密乘逆元;`a=1` 退化为恒等,`a=25` 即 ATBASH。

## 仿射密码

- `E(x)=(ax+b) mod 26`;两组已知明密对解二元方程求 a,b;或对 12×26=312 组合全试。
- **复合模数变体**:`c = a·x+b mod M`,M 非素数(如 65=5×13)——逐素因子域内求解后 CRT 合并,选择明文用 one-hot 向量(nullcon 2026)。
- 非素数模下的可逆性检查:`gcd(a,M)=1` 才可解。

## 词频分析

- 流程:统计密文字母频率 → 与英文频率表(e,t,a,o,i,n)对齐假设 → 用双字母组(th,he,in)与单词模式(`QXZ` 少见字母定位)交叉验证 → 迭代修正。
- 自动化:quipqiup.com、`pycipher`;hill-climbing + n-gram 评分脚本(国际赛标准解法)。
- 同音替换(homophonic,变长密文组映射单字符):找出频率相同的 n-gram 组替换成符号后按单表处理(ASIS CTF Finals 2013)。

## 工具速查

```python
# 仿射暴力
from string import ascii_lowercase as L
for a in [1,3,5,7,9,11,15,17,19,21,23,25]:
    for b in range(26):
        pt = ''.join(L[(a*L.index(c)+b)%26] for c in ct if c.isalpha())
```

## 转向

- 映射规则带结构(方格/关键字)→ [多表替换](polyalphabetic.md)/[简单代换](simple-substitution.md)
