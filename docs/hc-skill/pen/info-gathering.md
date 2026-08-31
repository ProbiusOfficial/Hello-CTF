---
comments: true
---

# 信息搜集

> PEN · 知识域。渗透测试侦察。标签:**网络扫描**、**子域名枚举**、**端口扫描**、**服务版本探测**、**操作系统探测**、**漏洞扫描**。

## 触发特征

- 拿到授权目标(域名/IP 段)开始打点;HW/渗透赛首轮。

## 网络扫描

- 存活探测:nmap `-sn`、masscan(大段快速)+ nmap 精扫组合;ICMP 被禁时 TCP ping(80/443/22)。
- 扫描隐蔽性:限速(`--max-rate`)、分片(`-f`)、诱饵(`-D`);扫描行为本身就是告警源(蓝队视角)。

## 子域名枚举

- 被动:cert 证书透明度(crt.sh)、DNS 数据集(SecurityTrails)、搜索引擎、fofa/hunter/quake(国内测绘三件套:语法 `domain="target.com"`)。
- 主动:subfinder/amass/OneForAll 字典爆破 + 解析验证;子域接管检查(悬空 CNAME,→ [WEB-HTTP请求](../web/http-request.md))。

## 端口扫描

- 全端口策略:masscan 65535 快筛 → nmap `-sV` 精扫确认;TCP SYN(`-sS`)半开扫描。
- 重点端口映射:80/443(Web)、22/3389(远程)、445(SMB)、3306/6379/27017(数据库,未授权高发)、6448/9090(容器与 K8s 面,→ [云安全](../cld/index.md))。

## 服务版本探测

- `-sV --version-all`、`-O`(OS 指纹);banner 抓取(nc/手工)。
- 指纹 → N-Day 匹配:版本号搜 CVE/ exploits 索引(searchsploit);云厂商/中间件默认页识别(→ [WEB-信息搜集](../web/info-gathering.md) 指纹清单)。

## 操作系统探测

- TCP/IP 栈指纹(nmap -O)、TTL 初值估算、SMB/SSH banner、netbios 名。
- 用途:选择 exploit 版本(Windows 内核漏洞按版本号)、口令策略猜测。

## 漏洞扫描

- 自动化:nexpose/awvs/xray(国内被动扫描联动爬虫)/goby(资产+漏扫一体,国内 HW 常用)。
- 结果处理:误报验证(手工 PoC 复现)优先于数量;高危面(未授权/RCE)优先打点。
- 红线注意:扫描可能打挂脆弱设备(工控/老系统,→ [ICS](../ics/index.md)),需白名单沟通。

## 转向

- 漏洞验证利用 → [漏洞利用](exploitation.md);Web 侦察细节 → [WEB-信息搜集](../web/info-gathering.md)
