---
comments: true

---

# MIFARE Classic 1K IC 卡

## 概述

门禁卡、电梯卡、水卡大量使用它

用读卡器 dump 出的文件通常就是一个二进制镜像，大小正好 1KB（1024字节），在十六进制编辑器里就是 1024 个字节，每行 16 字节

## 总体结构

16 个扇区，扇区号 0~15

每个扇区 4 个块，块号 0~3，每块 16 字节（32 个十六进制字符）

总块数 64，线性排列

## 扇区与十六进制地址的对应

MIFARE Classic 1K 共 16 个扇区，每个扇区包含 4 个块，每块 16 字节，因此每个扇区占：

4 × 16 = 64 字节 = 0x40 字节

所以扇区 n 的起始偏移为：

起始地址 = n × 0x40

结束地址 = (n + 1) × 0x40 - 1

例如：

- 扇区 0：`000–03F`
  
- 扇区 1：`040–07F`
  
- 扇区 2：`080–0BF`
  
- 扇区 3：`0C0–0FF`
  
- 扇区 4：`100–13F`
  
- ...
  
- 扇区 15：`3C0–3FF`

整个 MIFARE Classic 1K Dump 的地址范围为：`000–3FF`，共 `0x400 = 1024` 字节

## 访问控制字节的十六进制规律

以常见门禁卡为例，若块 3 为：

```
FF FF FF FF FF FF  78 77 88  C1  FF FF FF FF FF FF
│                 │         │   │
│                 │         │   └─ Key B：6 字节
│                 │         └──── GPB / 用户字节：1 字节
│                 └────────────── Access Bits：3 字节
└──────────────────────────────── Key A：6 字节
```

- 78 77 88 就是访问控制位（以及它的非值，实际存储是取反备份）

- C1 是用户字节，在不同应用中意义不同

- 从这些十六进制就能判断每个数据块是用密钥 A 还是密钥 B 读写，以及控制块自身能否更改

这种格式是分析卡片权限的基础

## 实战案例

### IC 卡分析（MIFARE Classic 1K IC 卡）

![](https://pic1.imgdb.cn/item/6a36cfc32830ce602a508bb3.png)

两个文件只有 sector 2 的两个 Value Block 不同

```
文件 1 block 9:
ce 63 00 00 31 9c ff ff ce 63 00 00 01 fe 01 fe

文件 2 block 9:
78 69 00 00 87 96 ff ff 78 69 00 00 01 fe 01 fe
```

这题的关键是通过金额块发现 IC 卡 Value Block 的存储规律

```
[ value ][ ~value ][ value ][ addr ][ ~addr ][ addr ][ ~addr ]
```

其中金额是小端序

```
0x000063ce = 25550
0x00006978 = 27000
```

金额差是 `27000 - 25550 = 1450`

更重要的是可以看出加密/校验规律

```
ce 63 00 00  ->  31 9c ff ff
78 69 00 00  ->  87 96 ff ff
```

也就是

```
后 4 字节 = 前 4 字节按位取反
```

后面有多组伪造的 Value Block，结构类似

```
7b 00 00 00 a6 ff ff ff 30 00 00 00 01 fe 01 fe
75 00 00 00 a0 ff ff ff 34 00 00 00 03 fe 03 fe
72 00 00 00 9a ff ff ff 5f 00 00 00 05 fe 05 fe
31 00 00 00 96 ff ff ff 6b 00 00 00 07 fe 07 fe
65 00 00 00 a0 ff ff ff 6d 00 00 00 09 fe 09 fe
79 00 00 00 a0 ff ff ff 73 00 00 00 a1 fe a1 fe
69 00 00 00 8c ff ff ff 74 00 00 00 a2 fe a3 fe
65 00 00 00 8d ff ff ff 7d 00 00 00 a5 fe a5 fe
```

每组取 3 个位置

```
第 1 字节：明文
第 5 字节：取反后得到明文
第 9 字节：明文
```

```python
from pathlib import Path

data = Path("1").read_bytes()

# 每组隐藏信息所在的 block
blocks = [17, 21, 25, 29, 33, 37, 41, 45]

res = ""

for b in blocks:
    blk = data[b * 16:(b + 1) * 16]

    c1 = blk[0]
    c2 = (~blk[4]) & 0xff
    c3 = blk[8]

    res += chr(c1) + chr(c2) + chr(c3)

print("flag" + res)
```

得到 `flag{Y0u_4re_1ike_my_sister}`
