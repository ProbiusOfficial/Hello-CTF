---
comments: true
---

# 图片隐写

> MISC · 知识域。图片载体隐写。标签:**附加内容**、**图种**、**EXIF**、**图片宽高隐写**、**LSB隐写**、**数字水印隐写**。

## 触发特征

- 给图片求 flag;图片能看但"怪"(打不开/有噪声/尺寸异常)。

## 附加内容

- `binwalk -Me`、`foremost`:JPG FFD9 后、PNG IEND 后附加 zip/其他文件(MJPEG FFD9 后藏数据 PoliCTF 2017)。
- strings/hexdump 直接看尾部;010 模板看块完整性。

## 图种(合并文件)

- `copy /b a.jpg + b.zip out.jpg`(Windows)、`cat a.jpg b.zip > out.jpg`(Linux)。
- 识别:binwalk 出内嵌 zip;解压口令常在图片属性/LSB(连环套)。

## EXIF

- `exiftool ./x.jpg` 全量导出;关注 Comment/Description/Artist/GPS。
- EXIF 里藏 zlib 压缩数据 + 非默认 LSB 像素(ASIS CTF Finals 2017);EXIF ImageDescription 里塞 shell 命令(经 exiftool 执行,OTW Advent 2018,pwn 联动)。

## 图片宽高隐写

- PNG:`IHDR` 的 width/height 被改小 → CRC 报错;用脚本爆破正确宽高(CRC32 校验)。
- JPG:SOF0 段尺寸;GIF:逻辑屏幕尺寸。
- 修复后图片下半部分浮现 flag(H4ckIT CTF 2016 经典)。

## LSB隐写

- 工具:`zsteg`(PNG/BMP 全自动)、stegsolve(逐位面翻)、`Stegsolve` Data Extract、PIL 脚本。
- 通道组合:RGB 各通道、RGBA A 通道、按行/列序、比特序(LSB-first/MSB-first)穷举。
- **条件 LSB**:近黑像素过滤后提取(BaltCTF 2013);RGB 奇偶位(Break In 2016);跨通道多位 LSB(ApoorvCTF 2026);种子化像素置换 + 多位平面 QR(L3m0nCTF 2025)。
- JPEG 的 LSB 不适用(有损)→ 走 F5/JSteg(→ 下文)。
- BMP 位面藏 QR + steghide 密码(BYPASS CTF 2025)。

## 数字水印隐写

- 频域水印:DCT 系数(JPEG 量化表内 LSB——EHAX 2026);DWT/Fourier 域(FFT 频谱藏图,Pragyan 2026)。
- F5 隐写检测:DCT 系数比例统计(ApoorvCTF 2026);JSteg/stegdetect 辅助。
- 图像结构类:色调分离、调色板索引(PNG 未用调色板项,ApoorvCTF 2026)、JPEG slack space(BSIDSSF 2025)、最近邻插值像素网格(BSIDSSF 2025)。
- 像素坐标链(H4ckIT CTF 2016);GIF 帧差 + 摩斯(BaltCTF 2013);GIF PLTE 块拼 ELF(IceCTF 2018);AVI 帧差分像素(H4ckIT CTF 2016)。
- Arnold 猫映射置乱还原(Nuit du Hack 2017);渐进式 PNG 分层 XOR(OpenCTF 2016);套娃 QR(嵌套缩放叠加幸存像素,SECCON 2018);拼图复原(边缘匹配/ImageMagick +append + gaps 求解器,X-MAS CTF 2018)。
- 立体图(autostereogram)解密(BSIDSSF 2026);像素级 ECB 去重视觉还原(BackdoorCTF 2017,Crypto 联动)。

## 工具速查

```bash
zsteg -a x.png; exiftool x.jpg; binwalk -Me x.jpg
stegsolve.jar    # 逐位面/channal 翻
steghide extract -sf x.jpg -p ''   # jpg/bmp/wav;空密码先试
f5-_extraction / stegdetect      # JPEG 频域
```

## 转向

- 图片是二维码/条码 → [条码分析](barcode.md);音频 LSB → [音频隐写](audio-stego.md)
