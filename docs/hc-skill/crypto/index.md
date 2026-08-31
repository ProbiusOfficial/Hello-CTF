---
comments: true
---

# CRYPTO - 密码学

> 方向技能索引。攻击对象为加密、哈希、签名、PRNG、ZKP、数论类题目时从本索引路由。不要用于:二进制逆向出的自定义密码(先转 [Reverse](../reverse/index.md)),纯编码解谜(转 [Misc](../misc/index.md)),题目主体是 Web 但用了 JWT/哈希(转 [WEB](../web/index.md))。

## 知识域路由表

| 分组 | 知识域 |
| --- | --- |
| 编码与古典 | [编码与解码](encoding.md) · [加法密码](additive-cipher.md) · [单表替换](monoalphabetic.md) · [简单代换](simple-substitution.md) · [多表替换](polyalphabetic.md) · [其他古典](other-classical.md) · [键盘密码](keyboard-cipher.md) |
| 对称与现代 | [流密码](stream-cipher.md) · [RC4](rc4.md) · [LFSR](lfsr.md) · [分组密码](block-cipher.md) · [对称密码](symmetric.md) · [DES](des.md) · [AES](aes.md) |
| 非对称 | [RSA](rsa.md) · [ElGamal](elgamal.md) · [DSA](dsa.md) · [ECC](ecc.md) · [非对称密码](asymmetric.md) · [离散对数](discrete-log.md) · [密钥交换](key-exchange.md) · [格密码](lattice.md) |
| 哈希与签名 | [MD5](md5.md) · [SHA1](sha1.md) · [FNV](fnv.md) · [电子签名](digital-signature.md) |
| 随机数与求解 | [LCG](lcg.md) · [MT19937](mt19937.md) · [Z3](z3.md) · [数理](math.md) |

## 环境与工具基线

```bash
pip install pycryptodome z3-solver sympy gmpy2 hashpumpy fpylll py_ecc
apt install hashcat sagemath        # SageMath 用于 ECC/Coppersmith/格
python RsaCtfTool.py -n <n> -e <e> --uncipher <c>   # RSA 自动化攻击套件
```

## 通用解题流程

1. 识别类型:密文形态(base64/hex/数字串)、给出的参数(n,e / c,p,q / 签名)。
2. RSA 先做体检:位长、e 大小、N 可否分解(factordb/yafu/RsaCtfTool)。
3. 对称/流密码找"预言机":服务端是否返回解密结果、padding 合法性、长度变化。
4. PRNG 题先问:种子从哪来(时间?用户输入?)、泄露了多少输出。
5. 解出明文后检查 flag 格式;`m` 可能是逐字符拆开、分层加密或与密钥异或的复合结构。
