---
comments: true
---

# IOT - 物联网安全

> 方向技能索引。目标为智能设备、固件、无线协议、嵌入式系统时从本索引路由。固件逆向的汇编细节 → [Reverse](../reverse/index.md);设备服务的 Web 面 → [WEB](../web/index.md)。

## 知识域路由表

| 知识域 | 触发特征 |
| --- | --- |
| [信息搜集](info-gathering.md) | 设备/固件/协议/无线信号侦察 |
| [固件分析](firmware.md) | 提取、解包、逆向、补丁、签名、解密 |
| [网络安全](network.md) | 设备服务扫描、协议漏洞、中间人 |
| [无线安全](wireless.md) | Wi-Fi/BLE/Zigbee/NFC/RF |
| [设备漏洞](device-vuln.md) | 默认口令、命令注入、溢出、提权 |

## 环境基线

```bash
binwalk -Me firmware.bin          # 固件解包
firmware-mod-kit / FMK            # 改包重打包
file  ***; strings; qemu-user     # 架构识别与模拟
# 硬件:逻辑分析仪、万用表、UART/JTAG/SPI 读写器(CH341A、FlashCat)
```
