---
comments: true

---

### CTF密码学知识点一览

#### **Introduction**（介绍）
- 密码学基础概念
- 对称与非对称加密
- 密钥管理
- 加密算法的历史与应用

#### **General**（通用概念）
- 对称加密 vs 非对称加密
- 密钥交换协议
- 消息认证码（MAC）
- 数字签名
- 加密算法的安全性分析
- 随机数生成器（PRNG）

#### **Symmetric Ciphers**（对称加密）
- `AES`（高级加密标准）
- `DES`（数据加密标准）
- `3DES`（三重DES）
- `RC4`（流加密算法）
- `Blowfish`
- `Twofish`

#### **Mathematics**（数学基础）
- 数论基础（素数、模运算）
- 欧几里得算法
- 快速幂算法
- 大数运算与加密
- 群论与代数结构

#### **RSA**
- RSA加密原理
- 密钥生成与破解
- RSA的安全性分析
- 数字签名与验证
- RSA与模运算

#### **Diffie-Hellman**（Diffie-Hellman密钥交换）
- Diffie-Hellman协议原理
- 公钥加密与密钥交换
- 离散对数问题
- Diffie-Hellman中的安全性问题

#### **Elliptic Curves**（椭圆曲线）
- 椭圆曲线密码学（ECC）基础
- 椭圆曲线上的点加法
- 椭圆曲线离散对数问题（ECDLP）
- 椭圆曲线在公钥加密中的应用
- 常用的椭圆曲线（如 secp256k1）

#### **Hash Functions**（哈希函数）
- `MD5`, `SHA1`, `SHA256`
- 哈希碰撞与预影像攻击
- 加密哈希函数的性质
- HMAC（哈希消息认证码）
- 用于数字签名与证书的哈希算法

#### **Crypto on the Web**（Web上的密码学）
- `TLS/SSL`协议
- HTTPS与加密通信
- 公钥基础设施（PKI）
- 数字证书与证书链
- Web安全漏洞：如中间人攻击（MITM）

#### **Lattices**（格）
- 格密码学基础
- `Learning With Errors`（LWE）问题
- 基于格的加密方案
- 格相关攻击与量子计算抗性

#### **Isogenies**（同态映射）
- 同态映射在密码学中的应用（SIDH ...）
- 基于同态映射的加密系统
- 同态加密与量子安全

#### **ZKPs**（零知识证明）
- 零知识证明基础
- 零知识证明的应用场景
- zk-SNARKs 与 zk-STARKs
- 零知识证明在区块链中的应用（例如：Zcash）

