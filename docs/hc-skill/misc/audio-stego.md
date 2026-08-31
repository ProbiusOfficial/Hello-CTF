---
comments: true
---

# 音频隐写

> MISC · 知识域。音频载体隐写与信号解码。标签:**波形图**、**频谱图**、**MP3Stego**、**DTMF**、**Deepsound**、**SSTV**。

## 触发特征

- 给 wav/mp3/flac 求 flag;播放"有杂音/滴滴声/像收音机"。

## 波形图

- Audacity/Sonic Visualiser 打开:波形横向藏摩斯(长短)、幅值 0/1 编码(BackdoorCTF 2013)。
- 倒放:反向音频藏信息(ASIS CTF Finals 2013);音轨差分:多轨相减留隐藏轨(EHAX 2026)。
- 通道分析:左右声道差 = 隐藏数据(常见套路);位深/采样率异常。
- `wav` 尾部附加数据;LSB(→ LSB 套路与 [图片隐写](image-stego.md) 相同,工具 stegsolve 不支持则脚本)。

## 频谱图

- Audacity 频谱图/spectrogram 视图:文字/QR 直接"画"在频谱上(BaltCTF 2013 藏 QR)。
- FFT 频域细节:音符频率对应对(音符序列编码,BYPASS CTF 2025);音频元数据八进制编码(BYPASS CTF 2025)。
- DTMF:双音多频(电话按键)解码工具 `dtmf2num`/multimon-ng(EHAX 2026 自定义频率表变体)。

## MP3Stego

- MP3 压缩层 LSB;工具 MP3Stego(需密码,密码常在文件元数据/题目描述)。
- 识别:mp3 无明显异常但其他全试完。

## Deepsound

- DeepSound 工具制作的 wav 隐写:密码 + 内嵌文件;`DeepSound` GUI 打开;密码爆破( john/hashcat + rockyou,INShAck 2018)。
- 识别:wav 结构里 DeepSound 特征头。

## SSTV

- 慢扫描电视:音频" decoded" 出图片;工具 `qsstv`、`RX-SSTV`、Robot36(手机)。
- 高分辨率 SSTV 自定义 FM 解调(PlaidCTF 2017);SSTV 红鲱鱼(解出来是假 flag)+ LSB 音频真 flag(0xFun 2026);DotCode 条码经 SSTV 传输(0xFun 2026)。
- 识别:2200/1200Hz 起始(VIS 头)。

## 其他音频套路

- Morse:morse2ascii/multimon-ng;键盘敲击声侧信道(ApoorvCTF 2026);Voyager 金唱片音频(0xFun 2026)。
- MIDI:Note-On/Off 音高对编码(X-MAS CTF 2018);字节拍(bytebeat)合成代码识别(RITSEC 2018)。
- WAV 经 UART 解码:音频其实是串口信号(EasyCTF 2017);TTL/电平信号分析。
- 音乐音程隐写(DefCamp 2017);steghide 也支持 wav。

## 工具速查

```bash
multimon-ng -t wav x.wav          # DTMF/摩斯/SSTV 万金油
qsstv / Robot36                    # SSTV
deepsound2john x.wav > hash; john hash --wordlist=rockyou.txt
binwalk x.wav; steghide extract -sf x.wav
```

## 转向

- 解出图片/QR → [条码分析](barcode.md);无线电原始 IQ → [无线电信号分析](radio-signal.md)
