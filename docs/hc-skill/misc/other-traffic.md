---
comments: true
---

# 其他流量分析

> MISC · 知识域。非 HTTP/USB 的协议流量。标签:**网络协议**、**硬件通讯协议**、**损坏流量恢复**、**FTP流量分析**、**ICMP流量分析**、**SMTP流量分析**。

## 触发特征

- pcap 里协议混杂;非 TCP 80/443 端口;串口/总线信号。

## 网络协议

- **协议分层排查**:Statistics → Protocol Hierarchy 先看全貌;Conversations 看会话对。
- DNS:子域名编码、隧道(dnscat2 重组,BSIDSSF 2017)、尾字节二进制(UTCTF 2026)、NSEC 走查;DNS 外带 oracle(ASIS CTF Finals 2017)。
- ICMP:payload 隐写(字节旋转 HackIM 2016)、时序通道(DefCamp 2018)、长度通道(TokyoWesterns 2018)。
- TCP flag 隐蔽通道(BearCatCTF 2026);包间隔时序编码(EHAX 2026);TCP Fast Open SYN 载荷命令注入(Insomnihack 2019)。
- 5G/NR 协议分析;SAP Dialog 协议解密(GreHack CTF 2016);RADIUS 共享密钥破解(radius2john,UConn CyberSEED 2017);NTLMv2 hash 提取破解(Pragyan 2026);SMB RID 循环(Midnight 2026)、Timeroasting/MS-SNTP(Midnight 2026)。
- 蓝牙:HCI log 与 RFCOMM 包重组(HITCON 2018);**蓝牙流量分析**:btsnoop_hci.log 用 Wireshark 蓝牙解析,GATT 特征值读写即数据流;经典蓝牙音频流(A2DP)与 SPP 串口数据分离。
- **ADB流量分析**:5555 端口的 ADB 协议(cnxd 服务流)——Wireshark 无原生解析,按 ADB 协议帧(CONN/AUTH/OPEN/WRTE)手工还原 shell 会话与推送文件;`adbsnapshot` 类工具辅助。
- **MQTT 流量分析**:1883 明文主题与 payload 直接读——订阅 `#`(通配)语义上等于"看全部消息";CONNECT 报文里的 clientId/凭证是隐写/情报点;8883 TLS 场景 → 加密流量节。
- **SMB流量分析**:会话建立(NEGOTIATE/SESSION SETUP)→ NTLMv2 hash 抓取破解(→ [应急响应-流量分析](../ir/traffic-analysis.md));SMB2 文件读写(CREATE/READ)按文件 ID 重组传输内容;RID 枚举(Midnight 2026)。
- **Telnet 流量分析**:全明文交互,Follow TCP Stream 即完整会话(登录凭证、执行命令逐字可见);IAC 协商字节(0xFF)需过滤后再读。
- **加密流量分析**:无密钥时的指纹学——JA3/JA3S(TLS 握手指纹)、包长/时序统计、SNI 与目标不一致检测(→ [应急响应-流量分析](../ir/traffic-analysis.md) 数据加密流量节);有侧信息(内存密钥/日志)→ 解密还原。
- **无线密码破解**:WPA/WEP 四步握手 + 字典(aircrack-ng / hashcat -m 22000)、PMKID 无客户端攻击(→ [IoT-无线安全](../iot/wireless.md) Wi-Fi 节)。
- WiFi:WPA/WEP 解密(aircrack-ng + 握手包,DefCamp CTF 2016)。

## 硬件通讯协议

- 串口 UART:波特率识别(信号分析版)→ 数据还原;逻辑分析仪 CSV(Saleae 导出)时钟边沿提取(35C3 2018 Tektronix CSV)。
- I2C 总线解码(EKOPARTY CTF 2016);SPI;1-Wire。
- VGA/HDMI 信号解码(TSIG 系);DisplayPort 8b/10b + LFSR。
- USB 全速包分析、CAN 总线(车联网)。
- 电源侧信道:功耗轨迹分析(EHAX 2026);键盘声学侧信道(ApoorvCTF 2026)。

## 损坏流量恢复

- pcapfix 修复(CSAW CTF 2016);包记录 checksum 校验重组(Break In 2016)。
- 分片重组:TCP 流重组失败的手工 seq 拼接;跨流文件分段重组(ASIS CTF Finals 2013)。
- 环回口/裸以太帧格式变化。

## FTP流量分析

- 明文协议:USER/PASS 直接看;STOR/RETR 传文件 → Follow Stream 按 TYPE I(二进制)还原文件。
- 被动模式数据端口跟踪;断点续传(REST)拼接。

## ICMP流量分析

- 过滤:`icmp`;按 identifier/session 分组。
- payload 直接藏文件/编码(逐包 1 字节);时序/payload 长度当通道(见上)。

## SMTP流量分析

- 邮件流:`DATA` 命令后为 MIME 邮件 → 导出 → 解 base64 附件。
- 邮件头(Received/X-Originating)溯源;附件密码藏在头/正文。

## 工具速查

```bash
tshark -r x.pcap -q -z io,phs          # 协议分层
tshark -r x.pcap -Y "icmp" -T fields -e data.data
follow any stream; python scapy 重组脚本
multimon-ng / uart 工具链
```

## 转向

- 流量里是 USB → [USB流量分析](usb-traffic.md);是 webshell 会话 → [WEB流量分析](web-traffic.md)
