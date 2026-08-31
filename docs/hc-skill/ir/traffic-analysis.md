---
comments: true
---

# 流量分析

> IR · 知识域。应急响应中的流量取证。标签:**数据通信协议流量分析**、**Web攻击流量分析**、**远控通信流量分析**、**数据泄漏流量分析**、**数据加密流量分析**、**综合攻击类型事件流量分析**。

## 触发特征

- 给镜像口流量/pcap,要求判断"是否有失陷、外带什么、C2 在哪"。

## 数据通信协议流量分析

- 协议分层统计(tshark `io,phs`)先摸全貌 → 异常协议/端口定位;非常用端口跑加密流(疑 C2)。
- 内网横向协议:RDP/SMB/WMI/WinRM 流量与认证(NTLM/kerberos 异常)。
- DNS/ICMP 异常(隧道外带,→ [Misc-其他流量分析](../misc/other-traffic.md))。

## Web攻击流量分析

- 攻击链还原:扫描/爆破 → 注入/上传 → webshell 管理 → 内网动作;按时间线串请求。
- webshell 会话识别与解密(→ [Misc-WEB流量分析](../misc/web-traffic.md) 蚁剑/冰蝎/哥斯拉三件套)。
- 漏洞利用特征:log4j `${jndi}`、fastjson `@type`、Shiro rememberMe、Struts OGNL(→ [WEB](../web/index.md) 各页 N-Day 特征)。

## 远控通信流量分析

- beacon 识别:心跳周期规律、固定长度 URI、JA3/JA3S 指纹(→ [WEB-HTTP请求](../web/http-request.md))。
- CS 流量:配置提取解密(→ [Misc-WEB流量分析](../misc/web-traffic.md) CS 节);meterpreter TLS 特征(证书自签、密文长度模式)。
- 反连木马:外连目标聚合分析(单目标长连接 + 心跳),域名 newly registered(新注册域名)评估。
- 通道伪装识别:走 443 的非 TLS 流量、WebSocket 隧道、域前置(domain fronting)。

## 数据泄漏流量分析

- 外带检测:出站流量突增、单会话大上传、文件传输协议(FTP/SMTP 附件)、网盘/API 上传特征。
- 内容级:HTTP POST 体/邮件附件还原,敏感信息特征(身份证/手机号正则、源码特征)。
- 隐蔽通道:时序/长度编码识别(→ [Misc](../misc/index.md) 隐写思想)。

## 数据加密流量分析

- 无密钥场景的指纹分析:JA3/TLS 证书(自签/异常 SAN)、包长序列与方向序列(statistical fingerprint)、SNI 与实际目标不一致。
- 已知 C2 指纹库比对;加密流量的流量分级(正常业务 vs C2 心跳的时序特征)。
- 有条件获取密钥(内存/日志)→ 解密(→ [Misc-WEB流量分析](../misc/web-traffic.md) TLS 节)。

## 综合攻击类型事件流量分析

- 综合题套路:多阶段攻击全程在一份 pcap 中——按时间线拼接:入口(利用)→ 落地(webshell/马)→ C2 → 横向 → 目标(外带/破坏)。
- 产出物:攻击时间线表 + IOC(域名/IP/文件 hash/账户)+ 影响面评估。

## 转向

- 落地主机排查 → [入侵排查](intrusion-investigation.md);样本还原 → [恶意代码分析](../ics/malware.md)
