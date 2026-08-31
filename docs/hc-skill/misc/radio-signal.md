---
comments: true
---

# 无线电信号分析

> MISC · 知识域。RF/SDR 与硬件信号。标签:**遥控器信号分析**、**蓝牙信号分析**、**Zigbee信号分析**。

## 触发特征

- 给 IQ 采样文件(.cfile/.raw IQ/ wav 高采样率)、RTL-SDR 录制;题面"遥控/无线门禁/对讲机"。

## 基础管线(IQ 分析)

- 格式:复数 IQ(float32/uint8 交错);`gnuradio`、`URH(Universal Radio Hacker)`、`SDR#`、MATLAB。
- 流程:频谱观察(找中心频率/带宽)→ 滤波 → 解调(ASK/OOK/FSK/GFSK/QAM)→ 位流 → 协议帧(前导/同步字/地址/数据/CRC)。
- QAM-16 解调:载波恢复 + 定时恢复(EHAX 2026 套路);常见帧模式识别。

## 遥控器信号分析

- 常见:315/433MHz OOK/ASK 固定码(PT2262/EV1527)——URH 直接解出码段 → 重放。
- 滚动码 KeeLoq/HCS301:逆码密钥派生(高级);Flipper Zero .sub 文件直接分析(0xFun 2026)。
- 门禁卡:125kHz EM4100(ID 卡号直接读)、13.56MHz ISO14443(Mifare Classic:嵌套攻击/默认密钥)。

## 蓝牙信号分析

- HCI log:`btmon`/Android btsnoop_hci.log → Wireshark 蓝牙解析;ATT/GATT 数据看特征值。
- 经典蓝牙音频流;BLE 广播数据(manufacturer data 藏字节)。
- RFCOMM 重组(HITCON 2018)。

## Zigbee信号分析

- 802.15.4 帧: KillerBee/URH 解;网络密钥(传输密钥)提取后解密 APS 载荷。
- 智能家居设备流量(灯/传感器指令重放)。

## 其他信号面

- SSTV → [音频隐写](audio-stego.md);卫星(NOAA APT 解码);ADS-B(dump1090);POCSAG 寻呼。
- 数字模式:RTTY/PSK31/FT8(multimon-ng/fldig);CW 摩斯(手听或工具)。
- 硬件线信号:UART/I2C/SPI 逻辑分析(→ [其他流量分析](other-traffic.md) 硬件节);电源侧信道(EHAX 2026)。

## 工具速查

```bash
# URH: 全流程 GUI(推荐入门)
gnuradio-companion
cat x.cfile | gnuradio 解调流图
multimon-ng -t wav x.wav     # AFSK/POCSAG 等
```

## 转向

- 解调出音频 → [音频隐写](audio-stego.md);解出按键/命令 → [USB流量分析](usb-traffic.md)
