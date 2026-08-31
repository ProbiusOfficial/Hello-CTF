---
comments: true
---

# 视频隐写

> MISC · 知识域。视频载体隐写。标签:**帧提取**、**视频结构隐写**。

## 触发特征

- 给 mp4/avi/gif 求 flag;画面闪帧、内容"抖动"。

## 帧提取

- `ffmpeg -i x.mp4 frames/%04d.png` 全帧导出逐张看; `ffmpeg -i x.mp4 -vf "select=gt(scene\,0.9)"` 场景切换帧。
- 闪帧:1-2 帧的 flag 画面;播放时肉眼不可见,提取即得。
- **帧累积**:多帧叠加/平均出隐藏图(ASIS CTF Finals 2013、SECCON 2015)。
- **帧差分**:相邻帧异或/差分(GIF 帧差 + 摩斯,BaltCTF 2013;AVI 帧差分像素,H4ckIT CTF 2016)。

## 视频结构隐写

- 容器结构:mp4 的 moov/udta/meta atom、avi 的 RIFF 块——附加数据藏在容器元数据。
- 视频流层:H.264 SEI/NAL 附加单元藏字节;多流容器多路隐写(BSIDSSF 2026)。
- GIF:帧调色板(PLTE)拼接 ELF(IceCTF 2018);APNG 帧提取(IceCTF 2016);GIF 调色板操纵还原 QR(3DSCTF 2017)。
- SVG 动画关键帧隐写(UTCTF 2024);Kitty 终端图形协议流(BSIDSSF 2026)。
- 字幕轨/章节/附件流(mkv attachments):ffmpeg/mediainfo 全列。

## 光学与物理变体

- 弯曲玻璃反射还原 QR(PlaidCTF 2018);视频里 LED 摩斯(大小写锁定灯,Caps-Lock LED Morse,STEM CTF 2018)。
- 逐帧 OCR / QR 扫码(ZXing/pyzbar 批量)→ 拼接。
- 撕碎文档像素边缘重组(Nuit du Hack CTF 2018)。

## 工具速查

```bash
ffmpeg -i in.mp4 frames/%05d.png
ffmpeg -i in.mp4 -filter:v "setpts=0.2*PTS" out.mp4   # 放慢闪帧
python: opencv 逐帧 diff / 累加
mkvinfo / mediainfo 容器全解
```

## 转向

- 提取出的帧是二维码 → [条码分析](barcode.md);帧内 LSB → [图片隐写](image-stego.md)
