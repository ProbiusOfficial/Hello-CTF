---
comments: true
---

# MD5

> CRYPTO · 知识域。MD5 哈希攻击。标签:**暴力攻击**。

## 触发特征

- 32 位十六进制哈希;题目要求找相同哈希的不同输入,或还原短输入。

## 暴力攻击

- 还原短输入(≤6 位数字/字母):hashcat(`-m 0`)/John 全空间;国内常用 `md5.decode` 类网站库(仅限公开弱哈希)。
- 字典/规则攻击:hashcat `-a 0` + rule;掩码 `-a 3` 定长构造。
- 彩虹表:固定"加盐无盐"确认;盐在题面前缀时退化为自定义字符集爆破。

## 碰撞构造

- **单碰撞**:fastcoll 一键生成任意前缀的 MD5 碰撞对(需同前缀)。
- **多碰撞**:链式 fastcoll → 2^k 个文件同一 MD5;Merkle-Damgård 结构使碰撞向后延伸(附加任意后缀仍碰撞)(BackdoorCTF 2016)。
- **相同前缀不同后缀语义**:脚本解析对比(如文件类型判定取前缀、哈希取全文)→ polyglot 文件通过"防碰撞"校验。
- 识别 MD5 碰撞文件:corkami/pocs 的 MD5 PDF/EXE 样本管线(35C3 2018 同源)。

## 结构与变种攻击

- **哈希长度拓展**:MD5 属 Merkle-Damgård,`MD5(SECRET‖data)` 可追加数据续算(`hashpump`)(→ [SHA1](sha1.md) 详述)。
- **中间态泄露**:迭代哈希暴露中间值 → 按块隔离逆推、逐块爆破(BackdoorCTF 2016 自定义哈希套路)。
- **生日攻击界限**:n 位哈希 2^(n/2) 次碰撞;MD5=2^64 理论、实际远低。
- 变体:MD4/RIPEMD/NTLM(`-m 1000`)同族,hashcat 模式号不同;"两次 MD5"(`md5(md5(p))`)定制后仍可分阶段打。

## 工具速查

```bash
hashcat -m 0 hash.txt rockyou.txt
fastcoll -p prefix.bin -o c1 c2            # 前缀碰撞
hashpump -s <sig> --data <known> -a 'admin' -k 16
```

## 转向

- 长度拓展攻击细节 → [SHA1](sha1.md);哈希做 MAC 的线形性 → [FNV](fnv.md)
