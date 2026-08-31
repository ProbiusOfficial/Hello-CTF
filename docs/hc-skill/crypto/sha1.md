---
comments: true
---

# SHA1

> CRYPTO · 知识域。SHA-1/SHA-2 系列哈希攻击,核心是长度拓展与选择性前缀碰撞。标签:**哈希长度拓展攻击**。

## 触发特征

- `sha1(MAC = SHA1(SECRET ‖ data))` 结构的 token/签名。
- 40 位十六进制哈希;git 对象校验、证书链题目。

## 哈希长度拓展攻击

- **原理**:Merkle-Damgård 结构输出即内部状态;已知 `SHA(secret‖msg)` 与 `len(secret)`,可计算 `SHA(secret‖msg‖padding‖append)` 不需知道 secret。
- **步骤**:
  1. `hashpumpy.hashpump(known_sig, known_data, append, keylen)` 枚举 keylen;
  2. 新 data = `msg + glue_padding + append` 带新 sig 发送;
  3. 服务端重算哈希恰好等于新 sig。
- 工具:`hashpump`(CLI)、`hashpumpy`(Python)、`Hash_Length_Extension` 脚本族。
- **UTF-8 高位字节绕过**:拓展时 padding 字节用高位变体绕服务端校验(2018 CTF 变体)。
- **组合利用**:长度拓展 + AES-CBC cookie 伪造(签名过了再用 CBC 位翻转改权限,2018)。
- 原题:PlaidCTF 2014、ASIS CTF 2017、SHA-256 变体(CryptoCat 套路)。

## SHA-1 碰撞

- **等价前缀碰撞**(SHAttered,2017):PDF 两文件同 SHA-1;CTF 中用于绕过"上传文件哈希唯一"校验。
- **选择性前缀碰撞**(2020):构造任意前缀的两消息同哈希 → polyglot 证书/文档(CTF 出题复刻成本高,识别为主)。
- 碰撞生成成本高时,题目实际考"碰撞检测缺陷":比较前 N 字节、大小写、截断。

## SHA-2 系攻击

- **SHA-256 基向量攻击**:XOR 聚合哈希 `⊕SHA256(x_i)` 中选基向量绕过(2019)。
- **海绵结构 MITM**:rate < state 时未受控字节可做中间相遇,2^48 → 2^24(BKP 2017)。
- **哈希环回**(Floyd/Brent 判圈):哈希链迭代中找环恢复前像(2018)。
- 迭代 SHA-256 逐字符时间差 oracle:字符匹配多迭代一轮 → 时间侧信道逐位恢复(2019)。

## 工具速查

```bash
hashpump -s <sig> --data <known> -a '&admin=1' -k 8   # 逐个试 keylen
hashcat -m 100 sha1.txt rockyou.txt
# SHA-1 碰撞样本:https://shattered.io
```

## 转向

- MAC 构造非 Merkle-Damgård(CRC/HMAC 变体)→ [FNV](fnv.md);签名体系 → [电子签名](digital-signature.md)

## 例题

### hashpump / hashpumpy 实战(PlaidCTF 2014)

`sig = SHA1(SECRET ‖ data)`,追加 `;admin=true` 重签:

```bash
hashpump --keylength 8 \
  --signature 'ef16c2...ed5c3' \
  --data 'original_data' \
  --additional ';admin=true'
# 输出新签名与新 data(含 glue padding 字节)
```

```python
import hashpumpy
new_hash, new_data = hashpumpy.hashpump(original_hash, original_data, append_data, secret_length)
# secret 长度未知时 1~32 逐个枚举,发过去看哪个通过校验
```

关键认知:MD5/SHA1/SHA256 的输出**就是**内部状态——从已知输出继续哈希即可续算;只有 HMAC(`H(K⊕opad ‖ H(K⊕ipad ‖ msg))`)免疫此攻击。
