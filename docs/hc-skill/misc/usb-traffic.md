---
comments: true
---

# USB流量分析

> MISC · 知识域。USB 总线数据还原。标签:**USB数据流量分析**、**键盘流量分析**、**鼠标流量分析**、**数位板流量分析**、**手柄流量分析**、**打印机流量分析**。

## 触发特征

- pcap 里有 USB 总线包;题目给"键盘/鼠标记录"。

## USB数据流量分析

- 结构:USB Capture 里关注 `URB_INTERRUPT` 的 data 段;过滤:`usb.capdata || usbhid.data`。
- tshark 提取:`tshark -r x.pcap -T fields -e usb.capdata | grep -v "^$" > data.txt`。
- HID 报文 8 字节结构:`[modifier][reserved][key1..key6]`。

## 键盘流量分析

- HID Usage Table 映射 keycode → 字符;Shift 修饰(0x02/0x20)大小写与符号。
- 脚本:键值表 + 修饰位处理;注意 NumLock、方向键(EKOPARTY CTF 2016 键盘捕获解码)。
- **方向键导航追踪**:方向键在 TUI/游戏中导航画字符(HackIT 2017)。
- LED 摩斯:键盘 LED 状态位摩斯(BITSCTF 2017)。

## 鼠标流量分析

- HID 鼠标报文:`[button][dx][dy]`(boot protocol);相对坐标累积画轨迹。
- 脚本:matplotlib/PIL 连线;按钮位区分左右键(点击分段)(EHAX 2026 鼠标/数位板绘图恢复)。
- 高级协议(报告描述符不同):解析 Report Descriptor 确定字段布局。

## 数位板流量分析

- 数位板(绘图板)报文:压力/坐标字段更宽(16 bit 坐标 + 压力值)。
- 按 descriptor 解析;绘制时压力控制线宽(EHAX 2026)。

## 手柄流量分析

- Xbox/PS 手柄 HID:摇杆轴 + 按键位图;按键序列对应游戏操作解谜。
- USB MIDI Launchpad 流量重构(Sthack 2017);GBA USB URB_INTERRUPT 帧缓冲提取(hxp 2018)。

## 打印机流量分析

- 打印任务语言:PCL/PostScript/Epson ESC/P 指令流还原页面内容。
- RAW 9100 端口直印;pcap 里 `tcp stream` 组装后按指令集渲染(ghostscript/pil 手画)。

## 工具速查

```bash
tshark -r usb.pcap -T fields -e usb.capdata -Y usb.capdata
# 已知工具:UsbKeyboardDataHacker(键盘)、windmouse 类脚本(鼠标)
```

## 转向

- 键入内容是命令/shell 记录 → [应急响应](../ir/index.md);画出的图是 QR → [条码分析](barcode.md)
