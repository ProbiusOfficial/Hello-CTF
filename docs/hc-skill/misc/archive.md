---
comments: true
---

# 压缩包分析

> MISC · 知识域。zip/rar/7z 类容器的攻防。标签:**伪加密**、**暴力破解**、**字典攻击**、**掩码攻击**、**明文攻击**、**CRC32碰撞**。

## 触发特征

- 压缩包打不开/有密码;binwalk 出内嵌压缩包;套娃压缩包。

## 伪加密

- ZIP:general purpose bit flag 第 0 位(0x0001)加密标志;全局/局部头不一致 → 手工改 09→00(010 Editor 模板)。
- RAR:HEAD_FLAGS 0x0004 加密位;7z:header 加密与内容加密区分。
- 判断:密码错误 vs 伪加密(伪加密可直接解压但 CRC 可能报错)。

## 暴力破解

- ARCHPR/hascat:zip(`-m 13600` WinZip/`-m 17200`/`-m 11600` 7zip)、rar(`-m 12500`)。
- CPU 优先 GPU;已知内容特征时用明文对齐加速。

## 字典攻击

- rockyou + 国内定制字典(123456、生日、题面关键词);规则变换(`-r best64.rule`)。

## 掩码攻击

- 已知长度与字符集:`?d?d?d?d`(4 位数字秒解);部分已知前缀。
- CRC32 爆破小文件(≤6 字节可直接撞 CRC,见下)。

## 明文攻击

- ZipCrypto(传统加密):已知文件部分明文(≥12 字节)→ bkcrack 恢复内部密钥后解密全包或改密(密码可移除)(Codegate 2019)。
- 明文来源:同包已知文件(说明书/README)、文件头魔数、网上同版本文档。
- WinZip AES(较新)不可用此法。

## CRC32碰撞

- ZIP 未加密条目的 CRC32 是明文的哈希:文件 ≤4-6 字节时全空间暴力还原内容(弱工具脚本)。
- 套娃场景:多层压缩包每层都是小 CRC 题。

## 压缩包结构分析

- **ZIP 结构**:local file header(PK\x03\x04)→ central directory(PK\x01\x02)→ EOCD(PK\x05\x06);三处记录的偏移/标志位需自洽——伪加密、修复题都在改这些字段。
- 010 Editor 的 `ZIP.bt`/`RAR.bt` 模板逐字段可视化;`zipinfo -v`、`rar vt` 命令行查看结构详情。
- 日期时间字段、Made by 版本、NTFS 扩展字段(高精度时间戳)都是隐写候选位。

## 注释查看

- ZIP:`zipinfo -z x.zip` / 010 看 EOCD 注释段;分卷压缩注释常藏下一层密码。
- RAR:`rar vt x.rar` 显示注释块;7z:`7z l -slt`。

## 套娃与结构技巧

- 嵌套 zip + 密码互相引用(密码在上层包文件名/注释);`binwalk -Me` 自动解。
- tar 重复条目:同名条目覆盖差异提取(BSIDSSF 2025);嵌套 matryoshka 文件系统(BSIDSSF 2025)。
- FemtoZip 共享字典压缩还原(Sharif CTF 2016);Brotli 炸弹缝分析(BearCatCTF 2026)。
- 正则密码嵌套链 exrex 生成(UTCTF 2019);whitespace 编码嵌套 tar(UTCTF 2026)。
- zip 注释/扩展字段/文件名编码(GBK vs UTF8)藏信息。

## 工具速查

```bash
binwalk -Me x.zip
bkcrack -C enc.zip -c known.txt -p known_plain.txt
hashcat -m 13600 hash.txt ?d?d?d?d?d?d
python: zipfile + CRC32 爆破脚本
```

## 转向

- 解压出图片/流量包 → 对应知识域;压缩包里是密码题 → [Crypto](../crypto/index.md)
