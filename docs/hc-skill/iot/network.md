---
comments: true
---

# 网络安全

> IOT · 知识域。设备网络面攻击。标签:**端口扫描**、**服务枚举**、**漏洞扫描**、**协议漏洞利用**、**中间人攻击**、**DoS攻击**。

## 触发特征

- 设备可网络访问(路由器/摄像头/NVR/网关);要求拿下设备或其数据。

## 端口扫描

- `nmap -sT -p-`(设备常全端口开放但服务罕见);慢速扫描避免设备崩溃(嵌入式栈脆弱)。
- UDP 扫描(设备常用 UDP 私有协议:discovery/广播)。

## 服务枚举

- banner 抓取;HTTP 服务指纹(管理页面/接口文档残留);RTSP(摄像头 554:describe 拿路径,未授权看流)。
- 已知设备服务:UPnP、ONVIF(摄像头标准协议,工具 onvif 探测)、TR-069(CWMP,路由器管理协议)。
- 云对云接口:设备→云的连接证书/密钥在固件里(→ [固件分析](firmware.md))。

## 漏洞扫描

- 指纹 → CVE 匹配:路由器/摄像头历史漏洞库(router software 版本比对);shodan/fofa(国内)/ censys 同型号公开指纹。
- 默认口令字典(→ [设备漏洞](device-vuln.md))。

## 协议漏洞利用

- 私有协议:逆向结构后伪造控制包(帧头+命令字+校验);校验弱(CRC/加法校验)可任意改写。
- 历史协议漏洞:Mirai 族(telnet 弱口令蠕虫)、UPnP SOAP 注入、ONVIF 未授权、TR-069 命令注入(CVE-2016-10372 族)。
- MQTT:匿名接入订阅全部 topic、payload 命令注入;CoAP 未授权。

## 中间人攻击

- ARP 欺骗截获设备-网关流量(→ [Misc-其他流量分析](../misc/other-traffic.md) 还原);自建 AP/ rogue DHCP 让设备连攻击者热点。
- TLS 校验缺陷设备:装根证书截获设备↔云流量(拿 token/固件 URL)。
- 配网协议劫持:SmartConfig/AirKiss(一键配网广播密钥可截获 WiFi 密码)。

## DoS攻击

- 嵌入式栈脆弱:大包/慢速连接拖死 httpd;reboot 命令 DoS(题目要求"让设备重启"类)。
- 资源耗尽:并发连接耗尽 socket;畸形包崩溃服务(配合重启拿 shell 的组合)。

## 转向

- 服务有注入/溢出 → [设备漏洞](device-vuln.md);流量里的协议 → [固件分析](firmware.md) 逆向
