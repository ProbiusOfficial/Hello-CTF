---
comments: true
---

# 多表替换加密

> CRYPTO · 知识域。多个映射表轮换使用。标签:**维吉尼亚密码**、**Playfair密码**、**棋盘密码**、**关键字密码**、**希尔密码**、**自动密钥密码**。

## 触发特征

- 密文频率被"抹平",同一字母在不同位置映射不同。
- 提示带密钥词;密文长度 = 明文长度(非扩展)。

## 维吉尼亚密码

- 已知密钥长度:按列拆分逐列做凯撒(列内是单表);未知长度用 Kasiski 检验(重复串距离的 GCD)或重合指数(IoC)估计。
- 求各列密钥:重合指数最大的移位即密钥字母;已知明文(`flag` 前缀)直接差分:`(ct-pt) mod 26` 逐列得 key。
- 3D 维吉尼亚/回文对称密钥恢复:密钥序列对称时利用对称位置差分(3D Vigenere 变体)。

## Playfair密码

- 5x5 字母矩阵(去 Q 或 I/J 合并),双字母加密(同行取右、同列取下、矩形取对角)。
- 破解:双字母频率 + 已知明文片段模拟;或 hill-climbing 全矩阵搜索。
- 变体:Two-square、Four-square 同族。

## 棋盘密码(Polybius)

- 5x5 坐标(行,列)→ 数字对;数字对可再编码(01 序列、坐标图)。
- 变体:6x6(含数字)、ADFGVX(坐标再经列移位 → 见 [其他古典](other-classical.md));原题见 Qiwi Infosec 2016。

## 关键字密码

- 关键字构造表(Keyword cipher)或作为 Vigenere 密钥;先试常见关键字(题名、作者名)。

## 希尔密码(Hill)

- n×n 矩阵乘明文向量 mod 26;已知 n² 对明密文解矩阵方程(求逆元 mod 26)。
- 明文不足补齐;密钥矩阵要求可逆(det 与 26 互素)。

## 自动密钥密码

- 密钥 = 初始密钥 + 明文自身;已知首段明文即可滚雪球恢复全部。
- 变体:ciphertext-autokey(密文自馈),已知明文反向推。

## 工具速查

```python
# Vigenere 已知 key 解密
pt = ''.join(chr((ord(c)-ord(k[i%len(k)]))%26+97) for i,c in enumerate(ct))
# 已知明文求 key
key = ''.join(chr((ord(c)-ord(p))%26+97) for c,p in zip(ct,known_pt))
```

## 转向

- 坐标输出后像图案 → [Misc-条码分析](../misc/barcode.md);加解密在二进制流里 → [Reverse-加密与解密](../reverse/crypto-in-reverse.md)
