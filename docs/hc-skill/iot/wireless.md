---
comments: true
---

# 无线安全

> IOT · 知识域。无线协议攻防。标签:**Wi-Fi安全**、**Bluetooth安全**、**Zigbee安全**、**NFC安全**、**RF信号分析**。

## 触发特征

- 目标通信在无线层:WiFi/BLE/Zigbee/NFC/普通 RF。

## Wi-Fi安全

- WPA/WPA2-PSK:握手包捕获(airodump-ng)→ 字典爆破(aircrack-ng/hashcat -m 22000);PMKID 攻击(无需客户端)。
- WPA2-Enterprise:EAP 类型分析;evil twin + captive portal 钓鱼凭据。
- WPA3:降级攻击(时间泄漏侧信道 Dragonblood);过渡模式(WPA2/WPA3 混合)攻击面。
- WEP:直接 aircrack-ng(IV 收集);设备"只支持旧加密"时的利用。
- 设备特有:SmartConfig/AirKiss 配网明文密钥;WiFi Direct/P2P 未授权接入。

## Bluetooth安全

- BLE:GATT 特征值枚举(nRF Connect/bleak)→ 写特征值控制设备;未配对读写。
- 经典蓝牙:RFCOMM 通道未授权(→ [Misc-USB流量分析](../misc/usb-traffic.md) 重组);PIN 配对破解(旧版 PIN 协商)。
- HCI log 分析:配对密钥提取、厂商私有 profile 逆向。
- BlueDucky 类注入;蓝牙蠕虫历史面(Blueborne CVE 匹配)。

## Zigbee安全

- 抓包:KillerBee + CC2531/ApiMote;Zigbee 网络密钥获取(入网明文传输窗口/默认 "ZigBeeAlliance09" 链路密钥)。
- 解密后 APS 层命令重放(开关灯/传感器数据伪造);重配对攻击(强制设备离网重新入网截获密钥)。
- 工具:zbdump/zbreplay、URH。

## NFC安全

- Mifare Classic:默认密钥/嵌套攻击/暗通道(mfoc/mfcuk)→ 全扇区 dump;UID 卡(可写 UID 卡克隆门禁)。
- Mifare Ultralight:密码缺陷、计数器/OTP 滥用。
- EMV/公交卡:数据读取(非钱包扣款向)、未加密余额字段篡改(离线显示层)。
- NFC 中继(Relay)攻击思路;NDEF 数据注入。

## RF信号分析

- 固定码遥控(315/433MHz EV1527):URH/RTL-SDR 解码重放(→ [Misc-无线电信号分析](../misc/radio-signal.md))。
- 滚动码:KeeLoq 密钥恢复(逆向遥控器固件拿 master key);Rolljam( jam+capture 拖延码)。
- 私有协议:频谱定位 → 解调 → 协议还原 → 伪造。

## 转向

- 解调出数字数据 → [Misc-数据及编解码](../misc/data-encoding.md);遥控固件逆向 → [固件分析](firmware.md)
