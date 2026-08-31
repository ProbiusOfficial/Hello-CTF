---
comments: true
---

# 其他隐写

> MISC · 知识域。非常规载体的隐写。标签:**零宽隐写**、**NTFS流隐写**、**PYC隐写**、**Emoji隐写**、**SNOW隐写**、**TTL隐写**。

## 触发特征

- 文本文件"看起来空的";文件属性里藏东西;ping 流量异常。

## 零宽隐写

- 零宽字符(U+200B/200C/200D/FEFF/2060):不可见字符编码二进制。
- 工具:zwsp-steg、Unicode Steganography 在线解码器;`xxd` 看到多余 UTF-8 字节即确认。

## NTFS流隐写(NTFS ADS)

- `echo secret > file.txt:hidden` 备用数据流;`dir /r` 查看;`more < file.txt:hidden` 读取。
- 取证向:USN/MFT 分析(→ [取证](forensics.md));下载文件 Zone.Identifier 流。
- 传到 Linux 会丢失流 → "拿到文件没内容"先想 ADS。

## PYC隐写

- .pyc 常量/字段名/注释区藏数据;字节码 padding 槽位。
- 反编译后对比源码差异;marshal 层直接翻常量表(→ [Reverse-Python程序逆向](../reverse/python-reverse.md))。

## Emoji隐写

- Emoji 字符作为 base-N 字符集(base65536 的 CJK 族、Emoji base);变体选择符(U+FE0F)与肤色修饰符编码位。
- 工具:emoji-aware 解码脚本;Unicode 码点全列(`python: [hex(ord(c)) for c in s]`)。

## SNOW隐写

- SNOW 工具:行尾空白(空格/Tab)藏数据,可加密。
- 识别:行尾大量不可见空白;`snow -C -p pass x.txt` 提取。
- 同族:行尾 tab/space 二进制、尾部换行数量。

## TTL隐写

- ping 包 TTL 值低位藏数据(每个包 1-2 bit);ICMP payload 隐写的字节旋转变体(HackIM 2016);ICMP 包间隔时序通道(DefCamp 2018);payload 长度当通道(TokyoWesterns CTF 4th 2018)。
- 从 pcap 里提取 ICMP 系列 → 按序拼位(→ [其他流量分析](other-traffic.md))。

## 其他常见杂项载体

- ANSI 转义序列隐写:终端艺术里的颜色/光标控制码(BSIDSSF 2026;网络捕获版,Square CTF 2017)。
- DNS 域名尾字节/子域名编码(→ [其他流量分析](other-traffic.md))。
- 文件名隐写(文件名首字母、长度);目录名编码。
- 键盘 LED 摩斯(ioctl 读,PlaidCTF 2013;视频中的大写锁定灯,STEM CTF 2018)。
- heap/进程名/环境变量类出题(联动 OSINT/取证)。

## 工具速查

```bash
xxd x.txt | head      # 看不可见字节
python: ord 遍历筛非 BMP/零宽
dir /r; streams.exe   # ADS
snow -C x.txt
```

## 转向

- 数据藏在流量里 → [其他流量分析](other-traffic.md);零宽藏的是加密文本 → [Crypto](../crypto/index.md)
