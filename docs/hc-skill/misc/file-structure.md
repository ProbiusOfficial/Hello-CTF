---
comments: true
---

# 文件结构

> MISC · 知识域。文件类型判定与损坏文件修复。标签:**文件检测**、**文件修复**。

## 触发特征

- `file` 报 data/损坏;图片打不开;压缩包报错;binwalk 出嵌套文件。

## 文件检测

- 魔数对照:[文件签名表](https://hello-ctf.com/) 常备;`file`、`hexdump -C` 头 64 字节。
- 结构化查看:010 Editor 模板(PNG/JPG/ZIP/GIF 各有模板,块级可视化);kaitai struct。
- 嵌套检测:`binwalk -Me` 自动提取;`foremost`/`scalpel` 文件雕刻。
- 常见嵌套链:PNG→PDF→DOCX→PNG→Base64 递归 binwalk(TAMUctf 2019);matryoshka 嵌套文件系统(BSIDSSF 2025);tar 重复条目差分(BSIDSSF 2025)。
- 尾部附加数据:JPG `FFD9` 后、PNG `IEND` 后、ZIP EOCD 后的藏匿区(MJPEG FFD9 后藏数据,PoliCTF 2017);Brotli blob ASCII 艺术签名识别(ASIS Finals 2018)。
- 不常见魔数:QOIF、G-code(3D 打印,0xFun 2026)。

## 文件修复

- **PNG**:魔数损坏(头 8 字节)+ 块名小写修复(Pragyan CTF 2019);宽高改小(→ [图片隐写](image-stego.md));CRC 校验脚本重算;IDAT 块重排(0xFun 2026)。
- **JPG**:FFD9 截断补尾;量化表缺失补默认表;单 bit 翻转暴力 + OCR(SECCON 2017)。
- **ZIP**:EOCD 损坏手工重建(central directory 偏移修正,PlaidCTF 2017);byte-reversed `.docx` ZIP 双向归档(Security Fest CTF 2018);XZ 流头 CRC32 重建(Hackover 2018)。
- **PCAP**:pcapfix 修复全局头与包记录(CSAW CTF 2016);分片重组按 checksum 校验(Break In 2016)。
- **GIT**:损坏 blob 字节级暴力修复(CSAW CTF 2015);reflog/fsck 恢复 squash(→ [WEB-文件泄露](../web/file-leak.md))。
- **磁盘/文件系统**:XFS 元数据重建、BTRFS 子卷快照、ext2 孤儿 inode fsck(→ [取证](forensics.md))。

## 工具速查

```bash
file ./x; binwalk -Me ./x
pngcheck -v ./x.png; zip -FF broken.zip --out fixed.zip
pcapfix broken.pcap
# 010 Editor + 模板是结构修复第一生产力
```

## 转向

- 图片专项 → [图片隐写](image-stego.md);压缩包密码 → [压缩包分析](archive.md);磁盘镜像 → [取证](forensics.md)
