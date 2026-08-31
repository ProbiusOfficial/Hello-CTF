---
comments: true
---

# 数据及编解码转换

> MISC · 知识域。数据格式转换与编码识别的中枢页。标签:**编码转换**。

## 触发特征

- 拿到一段"不知道是什么"的数据:hex?base64?二进制位?坐标?
- Crypto 编码页(→ [Crypto-编码与解码](../crypto/encoding.md))管密码学向编码;本页管 Misc 杂项向数据转换。

## 识别决策树

1. **字符集**:纯 0/1 → 二进制位(按 8/7 位分组, LSB/MSB 两种序);0-9A-F → hex;A-Z2-7+`=` → base32;含 `+/=` → base64。
2. **数字串**:分组规律(两位→ASCII、五位→敲击码、九键、坐标对)。
3. **01/短长序列**:摩斯(点划)、曼彻斯特(边沿)、时钟编码。
4. **含特殊字符**:URL 编码、HTML 实体、Unicode 变体(零宽字符 → [其他隐写](other-stego.md))。
5. **多态文件**:二进制里 ASCII 图、像素矩阵、RGB 值列表(→ 各隐写页)。

## 高频转换套路

- 位串 → 字符:7 位(ASCII 老派)/8 位;字节序反转(UTF-16 字节序,LACTF 2026)。
- 像素颜色二进制编码:每像素 1 bit 拼图(Break In 2016);二进制网格 → QR 图像 + XOR key(Pragyan CTF 2019)。
- BCD 码(4 位一 digit,VuwCTF 2025);格雷码循环编码(EHAX 2026);二叉树路径编码键(EHAX 2026)。
- 二维坐标 → 文字(棋盘、像素位置链,H4ckIT CTF 2016)。
- 颜色值 → 字符:RGB 各通道分别取模/除法编码。
- 压缩层:zlib/gzip/brotli(原始流无头,靠 magic 检测,BSIDSSF 2026)/lzma 逐层解。
- 恶搞标准:UTF-9(RFC 4042,SECCON 2015);多进制混合(TOPKEK,Hack The Vote 2016)。

## 自动化工具

```text
CyberChef:Magic 模块自动逐层识别;From Charcode/From Binary/From Base64 串管线
ciphey:自动解码+解密混合
```

```python
# 位串转字符
bits = '01001000...'
''.join(chr(int(bits[i:i+8],2)) for i in range(0,len(bits),8))
```

## 转向

- 解码后是密码题 → [Crypto](../crypto/index.md);是图片/二维码 → [条码分析](barcode.md)/[图片隐写](image-stego.md)
