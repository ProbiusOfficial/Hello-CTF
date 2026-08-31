---
comments: true
---

# FNV

> CRYPTO · 知识域。FNV 系列非加密哈希及其线性代数攻击面。标签:**FNV-1 Hash**、**FNV-1a Hash**、**FNV-0 Hash**、**FNV2 Hash**。

## 触发特征

- 题目使用"快速非加密哈希"做校验/去重/路由:FNV、CRC32、Adler-32、MurmurHash。
- 哈希函数是"乘法 + 异或"结构,可逆性强。

## 四个变体速览

| 变体 | 流程 | 备注 |
| --- | --- | --- |
| FNV-0 | `h = (h*16777619) ^ byte`,h0=0 | 已废弃,等价于无偏置 FNV-1 |
| FNV-1 | 先乘后异或 | 经典 |
| FNV-1a | 先异或后乘 | 分布更好,CTF 最常见 |
| FNV2 | 题目自造变体(位宽/素数不同) | 逆向确认参数 |

- 常用参数:32 位 offset 2166136261 / prime 16777619;64 位 offset 14695981039346656037 / prime 1099511628211。

## 攻击面

- **逐字节可逆**:给定目标哈希与长度,反向逐字节恢复输入(乘法逆元 mod 2^32 存在,奇素数可逆)——FNV 哈希没有"单向性",等同解线性方程。
- **多前像构造**:不限定长度时无限多解;要求可打印时按字符集约束逆向枚举。
- **碰撞构造**:固定长度下找两串同哈希 = GF(2^k) 线性方程组(把乘法拆成移位+加法后线性化)。
- **GF(2) 线性代数通用**:同族"自引用 CRC"(找到 CRC 等于自身的字符串)把约束变成线性系统求解,自由变量选可打印 ASCII(Google CTF 2017)。
- **HMAC-CRC 线性攻击**:CRC 对 GF(2) 线性 → 单条消息-MAC 对即可解出密钥(Boston Key Party 2016);FNV 同样不是密码学安全 MAC,不可做认证。
- 定位与逆向:哈希常数(2166136261/16777619)在二进制里搜索 → [Reverse-加密与解密](../reverse/crypto-in-reverse.md)。

## 工具速查

```python
M = (1 << 32)
inv = pow(16777619, -1, M)   # 素数模 2^32 的逆元
def fnv1a_rev(target, length):
    out = []
    h = target
    for _ in range(length):
        # 逆最后一轮: h_prev = (h ^ b) * inv, 枚举 b∈0..255 使结果合法
        ...
```

## 转向

- MAC 语义攻击 → [电子签名](digital-signature.md);哈希出现在验证逻辑中 → [Reverse](../reverse/index.md)
