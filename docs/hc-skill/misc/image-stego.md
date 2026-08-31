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

## 格式专项(GIF/BMP/APNG)

- **GIF相关**:帧差分(GIF 帧差 + 摩斯,BaltCTF 2013);调色板(PLTE)藏文件拼接 ELF(IceCTF 2018);帧延迟(Graphic Control Extension)编码;调色板操纵还原 QR(3DSCTF 2017)。
- **BMP相关**:位面 LSB(→ LSB 隐写节)、像素行 padding 字节隐写(4 字节对齐的填充位)、BMP 信息头偏移错位藏数据。
- **APNG**:acTL/fcTL/fdAT 块——普通 PNG 查看器只显示首帧,`-C` 全帧导出(`ffmpeg -i x.png frames/%d.png`);隐藏后续帧是经典套路(IceCTF 2016)。

## DCT 域与频域隐写

- **DCT域JPG隐写**:JPEG 有损压缩下 LSB 不可用 → 隐写在 DCT 系数上:F5(系数 ±1 调整,检测看系数比例,ApoorvCTF 2026)、JSteg(系数 LSB)、OutGuess;工具 f5/stegdetect/stegseek。
- **FFT隐写(频域藏图)**:图片 FFT 变换后频谱/相位藏图或文字(numpy `fft2` + `fftshift` 看频谱,逆变换还原);频谱图直接观察或差分。
- 数字水印的频域实现(DWT/DCT 域)同属此类(→ 下文数字水印)。

## 数字水印隐写

- 频域水印:DCT 系数(JPEG 量化表内 LSB——EHAX 2026);DWT/Fourier 域(FFT 频谱藏图,Pragyan 2026)。
- F5 隐写检测:DCT 系数比例统计(ApoorvCTF 2026);JSteg/stegdetect 辅助。
- Arnold 置乱还原(Arnold 猫映射图像置乱解密,Nuit du Hack 2017);渐进式 PNG 分层 XOR(OpenCTF 2016)。
- 图像结构类:色调分离、调色板索引(PNG 未用调色板项,ApoorvCTF 2026)、JPEG slack space(BSIDSSF 2025)、最近邻插值像素网格(BSIDSSF 2025)。
- 像素坐标链(H4ckIT CTF 2016);GIF 帧差 + 摩斯(BaltCTF 2013);GIF PLTE 块拼 ELF(IceCTF 2018);AVI 帧差分像素(H4ckIT CTF 2016)。
## 图片结构隐写与容差类

- **图片结构隐写**:不藏像素、藏结构——块顺序(IDAT 重排,0xFun 2026)、IHDR 字段(→ 宽高隐写)、多余块/自定义块、调色板未用项(ApoorvCTF 2026)、JPEG 量化表 LSB(EHAX 2026)、slack space(BSIDSSF 2025)。
- **图片容差隐写**:利用显示/压缩的量化容差——像素值微调(±1)在视觉上不可见但数据可读;对抗二次压缩时把信息藏在压缩后不变的系数/像素上(鲁棒隐写思想);解题时对比"原图 vs 提供图"的逐像素 diff(`PIL.ImageChops.difference`)直接暴露修改区域。
- Arnold 置乱还原(Arnold 猫映射图像置乱解密,Nuit du Hack 2017);渐进式 PNG 分层 XOR(OpenCTF 2016)。
- 图像结构类:色调分离、像素坐标链(H4ckIT CTF 2016)、套娃 QR(嵌套缩放叠加幸存像素,SECCON 2018)、拼图复原(边缘匹配/ImageMagick +append + gaps 求解器,X-MAS CTF 2018)。
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
