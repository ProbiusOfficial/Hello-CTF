---
comments: true
---

# 文档隐写

> MISC · 知识域。PDF/Office/RTF 等文档载体。标签:**隐藏文字**、**文本隐水印**、**文档结构隐写**。

## 触发特征

- 给 pdf/docx/rtf/txt 求 flag;文档"看着正常"但复制不出/打印不同。

## 隐藏文字

- PDF:`pdftotext` 全文提取;隐藏图层(OCG 可选内容组)、渲染模式 3(不可见文字)。
- 颜色隐写:白底白字;字号 0.1;被上层对象遮挡(逐对象解析)。
- unreferenced PDF 对象藏页(对象树不被引用,SharifCTF 7 2016)。
- Word:隐藏文字属性(字体→隐藏);批注/修订残留;脚注尾注。

## 文本隐水印

- 零宽字符(→ [其他隐写](other-stego.md));同形 Unicode 字符。
- **行/字间距编码**:行距、字距、标点前后空格微调编码二进制。
- 词序/同义词替换水印;字体差异(特定字替换成相近字形)。
- 电子表格频率分析恢复二进制(Sharif CTF 2016)。

## 文档结构隐写

- **PDF 内部结构**:xref 表生成号隐藏通道(SEC-T CTF 2017);对象流压缩层(zlib 解开);附件(embedded files);JavaScript 层;多层 PDF 隐写(Pragyan 2026)。
- **Office(zip 容器)**:docx/pptx/xlsx 解 zip → document.xml 里翻;`word/media/` 藏文件;settings.xml/自定义属性;VBA 宏藏二进制(Excel 单元格拼 ELF,Sharif CTF 2016;宏二进制恢复,Sharif CTF 2016)。
- **RTF**:自定义标签藏数据(VolgaCTF 2013)。
- byte-reversed `.docx`(双向 ZIP,Security Fest CTF 2018);unreferenced 对象流。
- Angecryption:AES-CBC 使一个合法文件加密成另一个合法文件(PDF 前后都是合法文档,34C3 CTF 2017)。
- corkami/pocs MD5 PDF 碰撞管线(35C3 2018)。

## 工具速查

```bash
pdftotext x.pdf -; pdf-parser.py x.pdf; peepdf x.pdf
mutool clean -d x.pdf decompressed.pdf
unzip x.docx -d out; oletools(olevba)  # VBA 宏
binwalk x.pdf
```

## 转向

- 提取出图片/压缩包 → 对应知识域;宏是 ELF/马 → [取证](forensics.md)
