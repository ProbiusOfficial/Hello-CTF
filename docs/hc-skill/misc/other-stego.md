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

- **可执行文件隐写**:PE 资源段(RSRC)藏文件(ResHacker 提取)、overlay 附加数据(→ [文件结构](file-structure.md) 尾部附加)、导入表序号/时间戳字段编码、证书表藏数据;ELF 的 note 段、padding 区同理。
- **拼图与马赛克还原**:碎图重排(边缘匹配 + 求解器,gaps 工具,X-MAS CTF 2018;撕纸文档像素边缘重组,Nuit du Hack CTF 2018);**马赛克还原** = 打码后恢复——先判断是否为像素化(等块均值)而非真删数据:对像素化块穷举原始小像素组合(必要时缩小候选域:原像素来自低色数集合),或数据库匹配(人脸/文字用检索);纯模糊(高斯)不可逆。
- **游戏相关**:游戏存档隐写(存档文件结构解析 + 字段改写)、游戏内截图坐标/进度当数据、Roblox/Godot 资源包藏文件(→ [可执行文件逆向](../reverse/executable.md) 游戏引擎节)。
- **键盘隐写**:键盘 LED 状态摩斯(ioctl 读,PlaidCTF 2013;视频中的大写锁定灯,STEM CTF 2018);键盘流量即按键序列(→ [USB流量分析](usb-traffic.md));按键时长/间隔编码。
- ANSI 转义序列隐写:终端艺术里的颜色/光标控制码(BSIDSSF 2026;网络捕获版,Square CTF 2017)。
- DNS 域名尾字节/子域名编码(→ [其他流量分析](other-traffic.md))。
- 文件名隐写(文件名首字母、长度);目录名编码。
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
