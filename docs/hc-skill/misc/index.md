---
comments: true
---

# MISC - 安全杂项

> 方向技能索引。隐写、取证、流量、编码、压缩包、日志、无线电,以及 pyjail/沙箱逃逸类杂题从本索引路由。目标若以解密为核心 → [Crypto](../crypto/index.md);以突破 Python 沙箱为核心 → 本方向 misc 兼容,国际惯例 pyjail 亦常单列。

## 知识域路由表

| 分组 | 知识域 |
| --- | --- |
| 文件与编码 | [文件结构](file-structure.md) · [数据及编解码转换](data-encoding.md) · [压缩包分析](archive.md) |
| 隐写 | [图片隐写](image-stego.md) · [音频隐写](audio-stego.md) · [视频隐写](video-stego.md) · [文档隐写](document-stego.md) · [其他隐写](other-stego.md) · [条码分析](barcode.md) |
| 流量与信号 | [WEB流量分析](web-traffic.md) · [USB流量分析](usb-traffic.md) · [其他流量分析](other-traffic.md) · [无线电信号分析](radio-signal.md) |
| 取证与日志 | [取证](forensics.md) · [日志分析](log-analysis.md) |
| OSINT | 信息搜集类 OSINT 题归入各隐写/流量页的转向提示;深度情报题暂以通用流程处理 |

## 通用解题流程

1. 文件体检:`file`、`binwalk`、010 Editor 看魔数与结构完整性。
2. 分类:像图片走隐写、像压缩包走 archive、像流量包走 traffic、像磁盘/内存走取证。
3. 每个知识域页都有"识别特征 + 工具链 + 常见套路",按页加载。
4. Misc 大忌:不试就猜。工具先跑一轮(strings/binwalk/zsteg/steghide)再人工。
