---
comments: true

---
# 文件基础

## 文件格式

文件是信息的基本载体。无论是文本文档、图像、音频、还是可执行程序，每个文件都遵循特定的格式和结构，以便计算机系统能够正确识别、处理和呈现数据。

在MISC方向中，理解文件格式是一项不可或缺的技能 —— 这个抽象的方向 80% 以上都要和文件扯上关系，尤其是隐写技术和取证技术，以及压缩包分析技术（如果压缩包独立出来的话）。

### 简介

所有文件格式的本质都是二进制文件，这是易于计算机操作的进制格式，而对我们而言，我们时常使用 **十六进制** 对文件进行分析。

为了便于计算机识别，文件通常会包含除文件内容本身以外的一些特征标识，我们会在稍后介绍这些标识，在此之前我们需要先告知你为什么我们用十六进制的方式分析文件。

请看下面的例子，这是压缩包文件 .zip 格式的 **文件头**  ，在不同数据格式下的呈现方式。

```
Binary : 01010000 01001011 00000011 00000100
Hex	   : 50 4b 03 04
Hexdump: 00000000  50 4b 03 04 ..(优化阅读压缩部分空间)..|PK..|
```

我们可以看到，在  **十六进制 Hex** 下，文件头有着不错的可读性和可识别性，甚至在 **Hexdump** 下可以转化出 **可打印字符串(ISO 8859-1)** - `PK`。

### 魔法数字 Magic number

为了区分不同类型的文件，每个文件都会拥有一个自己的  **「 特征签名  File Signatures 」** 。

按照英文释义，特征签名又有： "**File Magic number**" 和 "**File checksum or more generally the result of a hash function over the file contents**" ，即 **魔法数字** 和 **校验值**。

上面例子中提到的 **文件头** ，特指的"`50 4b 03 04`"，而这里的 "`50 4b 03 04`" 就是 .zip压缩文件的 **「 魔法数字 Magic number 」** 特征签名 。

这种签名标识通常被放于头部，所以我们常用文件头来代指，严格的概念区分可以看下面关于三者的解释，但在实际中，我们不会做太严格的区分，用文件头来代指魔法数字也不会影响理解。

??? note "关于 文件头 特征签名 魔法数字"
    在中文维基百科中，文件头 特征签名 魔法数字 被揉到一起，以一种奇怪的方式翻译：
    "特征签名 File header"  
    " **文件头** "，这个词，在中文语境中是比较口语化的，一般我们把类似 `50 4b 03 04` 这样的文件头部hex信息都叫文件头。但这玩意其实是 File signature 的 Magic number，也就是文件特征签名中的魔法数字 (上面我们说到特征签名主要有两种 一是魔法数字 二是校验值)   
    所以个人更倾向于把前面说所的文件头 翻译成 "文件头部签名" 指魔法数字刚好放于头部用于标识文件。  
    拿 PNG 图片举例，PNG头部八字节其实是特征签名 - 魔法数字，IHDR块才是正式意义下的文件头，所谓的文件头未必是全部用来辩识文件类型的，更多情况是用来存放一些其他必要信息。  
    在中文语境下，文件头三个字 涵盖了文件的整个头部，这也是歧义产生的重要原因。  
    refe:   
    https://en.wikipedia.org/wiki/File_signature   
    https://en.wikipedia.org/wiki/Magic_number_(programming)  
    https://en.wikipedia.org/wiki/List_of_file_signatures

在Wiki [List_of_file_signatures](https://en.wikipedia.org/wiki/List_of_file_signatures) 中有详细的表格，包含各个文件格式的十六进制文件签名以及其签名在常见 **ISO 8859-1** 编码中的文本时的显示方式，当然你也可以展开下表 或者在 [附:文件签名表](./file_sign.md) 中查看翻译后的表格。

??? Abstract "List of FileSignatures"
    | Hex 签名                                              | ISO 8859-1          | 偏移 | 扩展名   | 描述                                                         |
    | :---------------------------------------------------- | ------------------- | ---- | -------- | ------------------------------------------------------------ |
    | 23 21                                                 | #!                  | 0    |          | 用于传递给紧随其后的 shebang（#!）之后的程序的脚本或数据  |
    | 00 00 02 00 06 04 06 00 08 00 00 00 00 00             | ..............      | 0    | wk1      | Lotus 1-2-3 电子表格（版本1）文件                            |
    | 00 00 1A 00 00 10 04 00 00 00 00 00                   | ..............      | 0    | wk3      | Lotus 1-2-3 电子表格（版本3）文件                            |
    | 00 00 1A 00 02 10 04 00 00 00 00 00                   | ..............      | 0    | wk4      | wk5                                                          |
    | 00 00 1A 00 05 10 04                                  | ........            | 0    | 123      | Lotus 1-2-3 电子表格（版本9）文件                            |
    | 00 00 03 F3                                           | ....                | 0    |          | Amiga Hunk 可执行文件                                        |
    | 00 00 49 49 58 50 52 (小端)                           | ..IIXPR             | 0    | qxd      | Quark Express 文档                                           |
    | 00 00 4D 4D 58 50 52 (大端)                           | ..MMXPR             | 0    | qxd      | Quark Express 文档                                           |
    | 50 57 53 33                                           | PWS3                | 0    | psafe3   | Password Gorilla 密码数据库                                  |
    | D4 C3 B2 A1 (小端)                                    | ÔÃ²¡                | 0    | pcap     | Libpcap 文件格式                                          |
    | A1 B2 C3 D4 (大端)                                    | ¡²ÃÔ                | 0    | pcap     | Libpcap 文件格式（纳秒分辨率）                            |
    | 0A 0D 0D 0A                                           | ␊␍␍␊                | 0    | pcapng   | PCAP Next Generation 转储文件格式                         |
    | ED AB EE DB                                           | í«îÛ                | 0    | rpm      | RedHat Package Manager (RPM) 包                           |
    | 53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00       | SQLite format 3␀    | 0    | sqlitedb | SQLite 数据库                                             |
    | 53 50 30 31                                           | SP01                | 0    | bin      | Amazon Kindle 更新包                                      |
    | 49 57 41 44                                           | IWAD                | 0    | wad      | Doom 的主要资源文件                                          |
    | 00                                                    | ␀                   | 0    | PIC      | IBM Storyboard 位图文件<br />Windows 程序信息文件<br />Mac Stuffit 自解压缩存档<br />IRIS OCR 数据文件 |
    | 00 00 00 00 00 00 00 00                               | ␀␀␀␀␀␀␀␀            | 11   | PDB      | PalmPilot 数据库/文档文件                                    |
    | BE BA FE CA                                           | ¾ºþÊ                | 0    | DBA      | Palm Desktop 日历存档                                        |
    | 00 01 42 44                                           | ␀␁BD                | 0    | DBA      | Palm Desktop 待办事项存档                                    |
    | 00 01 44 54                                           | ␀␁DT                | 0    | TDA      | Palm Desktop 日历存档                                        |
    | 54 44 46 24                                           | TDF$                | 0    | TDF$     | Telegram Desktop 文件                                        |
    | 54 46 58 44                                           | TFXD                | 0    | tfxd     | Telegram Desktop 文件                                        |
    | 30 31 4F 52                                           | 01OR                | 0    | or1      | Oracle 7.3 数据库                                         |
    | FD FF FF FF                                           | ýÿÿÿ                | 0    | db       | SQLite 3 数据库                                           |
    | 4D 53 46 54 02                                        | MSFT␂               | 512  | MSFT     | Compound 文件文档                                            |
    | 00 01 00 00 00 03 00 00                               | ␀␁␀␀␀␃␀␀            | 0    | ndif     | Apple 包括对称差异（Binary II）文件                          |
    | 4F 52 43 01                                           | ORC␁                | 0    | orc      | Oracle 数据库                                                |
    | 1A 45 DF A3                                           | Eß£                 | 0    | ldf      | SQL Server 日志文件                                          |
    | 50 4B 03 04                                           | PK␃␄                | 0    | zip      | ZIP 压缩文件                                                 |
    | 50 4B 05 06                                           | PK␅␆                | 0    | zip      | ZIP 压缩文件（带数据描述符）                                 |
    | 50 4B 07 08                                           | PK␇␈                | 0    | zip      | ZIP 压缩文件（带 64 位结束头）                               |
    | 50 4B 4C 49 54 45                                     | PKLITE              | 0    | zlite    | PKLITE 压缩文件                                           |
    | FF 57 50 43 07 10 00 03 00 00 00 00                   | WPC◇␀␃␀␀␀␀          | 0    | wcp      | WordPerfect 文档                                             |
    | FF 57 50 43 07 20 00 03 00 00 00 00                   | WPC◠␀␃␀␀␀␀          | 0    | wcp      | WordPerfect 文档                                             |
    | FF 57 50 43 07 40 00 03 00 00 00 00                   | WPC◐␀␃␀␀␀␀          | 0    | wcp      | WordPerfect 文档                                             |
    | FF 57 50 43 07 80 00 03 00 00 00 00                   | WPC◘␀␃␀␀␀␀          | 0    | wcp      | WordPerfect 文档                                             |
    | 46 4C 56 01                                           | FLV␁                | 0    | flv      | Flash 视频文件                                               |
    | E2 68 6E 6F                                           | âhno                | 0    | nomedia  | Android 无媒体文件（.nomedia）                               |
    | 38 42 50 53                                           | 8BPS                | 0    | psd      | Adobe Photoshop 文档                                         |
    | 47 49 46 38 39 61                                     | GIF89a              | 0    | gif      | GIF 图像                                                     |
    | FF D8 FF E0                                           | Øÿà                 | 0    | jpeg     | JPEG 图像                                                    |
    | FF D8 FF E1                                           | Øÿá                 | 0    | jpeg     | JPEG 图像（Exif 格式）                                       |
    | 42 4D                                                 | BM                  | 0    | bmp      | BMP 图像                                                     |
    | 89 50 4E 47 0D 0A 1A 0A                               | ‰PNG␍␊␊             | 0    | png      | PNG 图像                                                     |
    | 47 49 46 38 37 61                                     | GIF87a              | 0    | gif      | GIF 图像                                                     |
    | FF D8 FF E8                                           | Øÿè                 | 0    | jpeg     | JPEG 图像（SPIFF 格式）                                      |
    | 4D 4D 00 2A                                           | MM␀*                | 0    | tif      | TIFF 图像                                                    |
    | 49 49 2A 00                                           | II*␀                | 0    | tif      | TIFF 图像                                                    |
    | 42 41 4D 53                                           | BAM$                | 0    | bam      | Wayback Machine 存档文件                                     |
    | 21 3C 61 72 63 68 3E 0A 64 6F 63 74 79 70 65 20       | <!arch>␊doctype␠    | 0    |          | HTML 文档                                                    |
    | 23 44 4F 43                                           | #DOC                | 0    | doc      | WordPerfect 文档                                         |
    | 50 4B 03 04                                           | PK␃␄                | 0    | jar      | Java 存档文件                                                |
    | FF D8 FF E0 00 10 4A 46 49 46 00 01                   | Øÿà␀␑JFIF␀␁         | 0    | jpg      | JPEG 图像                                                    |
    | FF D8 FF E1 00 60 45 78 69 66 00 00                   | Øÿá␀`Exif␀␀         | 0    | jpg      | JPEG 图像（Exif 格式）                                       |
    | FF D8 FF E1 4C 45 56 45 4C 00 00 00                   | ØÿáLEVEL␀␀␀         | 0    | jpg      | JPEG 图像（Exif 格式，带 GPS 数据）                          |
    | FF D8 FF E1 41 53 43 49 49 00 00 00                   | ØÿáASCII␀␀␀         | 0    | jpg      | JPEG 图像（Exif 格式，Adobe APP14 标记）                     |
    | FF D8 FF E1 45 78 69 66 00 00 00 00                   | ØÿáExif␀␀␀␀         | 0    | jpg      | JPEG 图像（Exif 格式，没有 TIFF 标记）                       |
    | 47 49 46 38 39 61                                     | GIF89a              | 0    | gif      | GIF 图像                                                     |
    | FF D8 FF E0 00 10 4A 46 49 46 00 01                   | Øÿà␀␑JFIF␀␁         | 0    | jpeg     | JPEG 图像                                                    |
    | FF D8 FF E1 00 60 45 78 69 66 00 00                   | Øÿá␀`Exif␀␀         | 0    | jpeg     | JPEG 图像（Exif 格式）                                       |
    | FF D8 FF E1 4C 45 56 45 4C 00 00 00                   | ØÿáLEVEL␀␀␀         | 0    | jpeg     | JPEG 图像（Exif 格式，带 GPS 数据）                          |
    | FF D8 FF E1 41 53 43 49 49 00 00 00                   | ØÿáASCII␀␀␀         | 0    | jpeg     | JPEG 图像（Exif 格式，Adobe APP14 标记）                     |
    | FF D8 FF E1 45 78 69 66 00 00 00 00                   | ØÿáExif␀␀␀␀         | 0    | jpeg     | JPEG 图像（Exif 格式，没有 TIFF 标记）                       |
    | FF D8 FF E0 00 10 4A 46 49 46 00 01                   | Øÿà␀␑JFIF␀␁         | 0    | jpeg     | JPEG 图像                                                    |
    | FF D8 FF E1 00 60 45 78 69 66 00 00                   | Øÿá␀`Exif␀␀         | 0    | jpeg     | JPEG 图像（Exif 格式）                                       |
    | FF D8 FF E1 4C 45 56 45 4C 00 00 00                   | ØÿáLEVEL␀␀␀         | 0    | jpeg     | JPEG 图像（Exif 格式，带 GPS 数据）                          |
    | FF D8 FF E1 41 53 43 49 49 00 00 00                   | ØÿáASCII␀␀␀         | 0    | jpeg     | JPEG 图像（Exif 格式，Adobe APP14 标记）                     |
    | FF D8 FF E1 45 78 69 66 00 00 00 00                   | ØÿáExif␀␀␀␀         | 0    | jpeg     | JPEG 图像（Exif 格式，没有 TIFF 标记）                       |
    | FF D8 FF E0 00 10 4A 46 49 46 00 01                   | Øÿà␀␑JFIF␀␁         | 0    | jpeg     | JPEG 图像                                                    |
    | FF D8 FF E1 00 60 45 78 69 66 00 00                   | Øÿá␀`Exif␀␀         | 0    | jpeg     | JPEG 图像（Exif 格式）                                       |
    | FF D8 FF E1 4C 45 56 45 4C 00 00 00                   | ØÿáLEVEL␀␀␀         | 0    | jpeg     | JPEG 图像（Exif 格式，带 GPS 数据）                          |
    | FF D8 FF E1 41 53 43 49 49 00 00 00                   | ØÿáASCII␀␀␀         | 0    | jpeg     | JPEG 图像（Exif 格式，Adobe APP14 标记）                     |
    | FF D8 FF E1 45 78 69 66 00 00 00 00                   | ØÿáExif␀␀␀␀         | 0    | jpeg     | JPEG 图像（Exif 格式，没有 TIFF 标记）                       |
    | 49 49 2A 00 10 00 00 00 01 00 02 00                   | II*␀␐␀␀␀␁␀␂␀        | 0    | tif      | TIFF 图像                                                    |
    | 4D 4D 00 2A 00 00 00 08 00 0B 01 0F                   | MM␀*␀␀␀␈␀ ␁         | 0    | tif      | TIFF 图像                                                    |
    | 49 49 2A 00 10 00 00 00 02 00 03 00                   | II*␀␐␀␀␀␀␀          | 0    | tif      | TIFF 图像                                                    |
    | 4D 4D 00 2A 00 00 00 08 00 0B 01 0F                   | MM␀*␀␀␀␈␀ ␁         | 0    | tif      | TIFF 图像                                                    |
    | 4D 5A                                                 | MZ                  | 0    | exe      | Windows 可执行文件（DOS MZ 格式）                            |
    | 5A 4D                                                 | ZM                  | 0    | exe      | Windows 可执行文件（新版 DOS MZ 格式）                       |
    | 00 00 01 00                                           | ␀␀␁␀                | 0    | eot      | 嵌入式 OpenType 字体                                         |
    | 7F 45 4C 46                                           | ␡ELF                | 0    | elf      | 可执行和链接格式 (ELF) 文件                                  |
    | 00 01 00 00                                           | ␀␁␀␀                | 0    | wmf      | Windows 图形元文件                                           |
    | 3C 3F 78 6D 6C 20                                     | <?xml␠              | 0    | xml      | XML 文档                                                     |
    | 25 21 50 53 2D 41 64 6F 62 65 2D 33                   | %!PS-Adobe-3        | 0    | ps       | PostScript 文档                                              |
    | 1F 8B                                                 | ␟⸏                  | 0    | gz       | Gzip 压缩文件                                                |
    | 42 5A 68 39                                           | BZh9                | 0    | bz2      | Bzip2 压缩文件                                               |
    | 78 9C                                                 | x⸟                  | 0    | zlib     | zlib 压缩数据流                                              |
    | FD 37 7A 58 5A 00 00                                  | ý7zXZ␀␀             | 0    | 7z       | 7-Zip 压缩文件                                               |
    | 37 7A BC AF 27 1C                                     | 7z¼¯'␟              | 0    | 7z       | 7-Zip 压缩文件（较早版本）                                   |
    | 04 22 4D 18                                           | ␄"M␘                | 0    | lz4      | LZ4 压缩文件                                                 |
    | 1A 45 DF A3                                           | Eß£                 | 0    | ldf      | SQL Server 日志文件                                          |
    | 4C 41 49 52                                           | LAIR                | 0    | lair     | Lair 录音文件                                                |
    | 4D 41 52 31                                           | MAR1                | 0    | mar      | Mozilla 存档                                                 |
    | 50 4B 03 04                                           | PK␃␄                | 0    | xpi      | Mozilla 扩展或附加组件                                       |
    | 43 6F 6E 64 69 74 69 6F 6E 73 20 20 20 20 20 20 20 20 | Conditions␠␠␠␠␠␠␠␠␠ | 0    | conds    | Windows 网络条件文件                                         |
    | 23 21 41 4D 52 00                                     | #!AMR␀              | 0    | amr      | AMR 音频文件                                                 |
    | 4D 54 68 64                                           | MThd                | 0    | mid      | MIDI 音乐文件                                                |
    | 52 49 46 46                                           | RIFF                | 0    | wav      | WAV 音频文件                                                 |
    | 49 44 33 03                                           | ID3␃                | 0    | mp3      | MP3 音频文件                                                 |
    | 00 01 00 00 00 00 10 00 00 02 00 00                   | ␀␁␀␀␀␀␐␀␀␂␀␀        | 0    | icns     | Apple 图标文件                                               |
    | 46 4F 52 4D 00 00 00 00                               | FORM␀␀␀␀            | 0    | aiff     | AIFF 音频文件                                                |
    | 52 4E 4D 53                                           | RNMS                | 0    | nes      | NES ROM 图像                                                 |
    | 53 45 51 36                                           | SEQ6                | 0    | seq      | Sierra 字体资源文件                                          |
    | 4E 45 53 1A                                           | NES␚                | 0    | nes      | NES ROM 映像                                                 |
    | 49 4D 41 20                                           | IMA␠                | 0    | ima      | IMA 音频文件                                                 |
    | 66 4C 61 43                                           | fLaC                | 0    | flac     | FLAC 音频文件                                                |
    | 52 49 46 46                                           | RIFF                | 0    | webp     | WebP 图像                                                    |
    | 47 49 46 38 39 61                                     | GIF89a              | 0    | webp     | WebP 图像                                                    |
    | 50 41 4B 20                                           | PAK␠                | 0    | pak      | Quake PAK 文件                                               |
    | 1A 45 DF A3                                           | Eß£                 | 0    | ldf      | SQL Server 日志文件                                          |
    | 30 30 00 00                                           | 00␠␠␀␀              | 0    | jis      | JIS 文字文件                                                 |
    | 4F 53 2F 32                                           | OS/2                | 0    | bmp      | OS/2 位图文件                                                |
    | 4F 53 2F 32                                           | OS/2                | 0    | os2      | OS/2 位图文件                                                |
    | 4F 53 2F 32                                           | OS/2                | 0    | ras      | OS/2 位图文件                                                |
    | 0A 0D 0D 0A                                           | ␊␍␍␊                | 0    | netcdf   | NetCDF 文件                                                  |
    | 44 42 46 48                                           | DBFH                | 0    | dbf      | dBASE II 文件                                                |
    | 50 53 46 1A                                           | PSF␚                | 0    | psf      | PSF 字体文件                                                 |
    | 4C 4E 02 00                                           | LN␂␀␀               | 0    | lnt      | Microsoft Linker 大纲文件                                    |
    | 7B 5C 72 74 66 31                                     | {\rtf1              | 0    | rtf      | 富文本格式 (RTF) 文档                                        |
    | 46 4C 56 01                                           | FLV␁                | 0    | flv      | Flash 视频文件                                               |
    | 57 41 56 45 66 6F 72 6D 61 74 20 33                   | WAVEform␠3          | 0    | wav      | WAV 音频文件                                                 |
    | 57 41 56 45 66 6F 72 6D 61 74 20 33                   | WAVEform␠3          | 0    | webm     | WebM 视频文件                                                |
    | 57 45 42 4D                                           | WEBM                | 0    | webm     | WebM 视频文件                                                |
    | 44 45 58 01                                           | DEX␁                | 0    | dex      | Dalvik 可执行文件                                            |
    | 30 33 35 00                                           | 035␀                | 0    | elf      | ELF 可执行文件                                               |
    | 57 69 6E 64 6F 77 73 20 33 2E 31 00                   | Windows␠3.1␀        | 0    | exe      | Windows 可执行文件                                           |
    | 25 21 50 53 2D 41 64 6F 62 65 2D 33                   | %!PS-Adobe-3        | 0    | ps       | PostScript 文档                                              |
    | 49 44 33 03                                           | ID3␃                | 0    | mp3      | MP3 音频文件                                                 |
    | 4D 54 68 64                                           | MThd                | 0    | mid      | MIDI 音乐文件                                                |
    | 52 49 46 46                                           | RIFF                | 0    | wav      | WAV 音频文件                                                 |
    | 4F 53 2F 32                                           | OS/2                | 0    | bmp      | OS/2 位图文件                                                |
    | 4F 53 2F 32                                           | OS/2                | 0    | os2      | OS/2 位图文件                                                |
    | 4F 53 2F 32                                           | OS/2                | 0    | ras      | OS/2 位图文件                                                |
    | 0A 0D 0D 0A                                           | ␊␍␍␊                | 0    | netcdf   | NetCDF 文件                                                  |
    | 44 42 46 48                                           | DBFH                | 0    | dbf      | dBASE II 文件                                                |
    | 50 53 46 1A                                           | PSF␚                | 0    | psf      | PSF 字体文件                                                 |
    | 4C 4E 02 00                                           | LN␂␀␀               | 0    | lnt      | Microsoft Linker 大纲文件                                    |
    | 7B 5C 72 74 66 31                                     | {\rtf1              | 0    | rtf      | 富文本格式 (RTF) 文档                                        |
    | 46 4C 56 01                                           | FLV␁                | 0    | flv      | Flash 视频文件                                               |
    | 57 41 56 45 66 6F 72 6D 61 74 20 33                   | WAVEform␠3          | 0    | wav      | WAV 音频文件                                                 |
    | 57 41 56 45 66 6F 72 6D 61 74 20 33                   | WAVEform␠3          | 0    | webm     | WebM 视频文件                                                |
    | 57 45 42 4D                                           | WEBM                | 0    | webm     | WebM 视频文件                                                |
    | 44 45 58 01                                           | DEX␁                | 0    | dex      | Dalvik 可执行文件                                            |
    | 30 33 35 00                                           | 035␀                | 0    | elf      | ELF 可执行文件                                               |
    | 57 69 6E 64 6F 77 73 20 33 2E 31 00                   | Windows␠3.1␀        | 0    | exe      | Windows 可执行文件                                           |

## 文件操作

### 工具篇

#### 010 Editor

#### Python

### 命令篇

#### file

#### strings

#### binwalk

#### stegsolve