---
comments: true
---

# 加法密码

> CRYPTO · 知识域。移位类替换:凯撒、ROT13、ASCII 移位。标签:**凯撒密码**、**ROT13**、**ASCII移位**。

## 触发特征

- 明文形似英文但整体"错位";`flag` 变成 `synt`(ROT13)。
- 提示"shift/caesar/位移"。

## 凯撒密码

- 暴力 26 个移位逐一输出,肉眼或词频选正确项。
- 密钥空间小到可以全试;非字母字符通常保留原样。
- 变体:ATBASH(倒序表,属单表但常一起考)、凯撒对 ASCII 全集移位(含符号)。

## ROT13

- 自逆变换(加密=解密);识别最快:字符串里 `n` 多半是 `a`。
- 变体:ROT5(数字)、ROT18(ROT13+ROT5)、ROT47(ASCII 33-126)。

## ASCII移位

- 对整段 ASCII(含标点/数字)统一加 n;解法:`for n in range(128): ''.join(chr((ord(c)+n)%128))`。
- 逐字符不同偏移(如 +i 或斐波那契偏移)→ 找已知明文(`flag{`、`CTF`)差分出偏移序列。
- 图片化变体:像素行/列按 strip 偏移做凯撒,对比原图读出偏移量即 ASCII(BSIDSSF 2026)。

## 工具速查

```python
ct = input()
for k in range(26):
    print(k, ''.join(chr((ord(c)-97+k)%26+97) if c.isalpha() else c for c in ct.lower()))
# CyberChef: ROT13 Bruteforce / ROT47
```

## 转向

- 移位+多表轮换 → [多表替换](polyalphabetic.md);移位藏在图片里 → [Misc-图片隐写](../misc/image-stego.md)
