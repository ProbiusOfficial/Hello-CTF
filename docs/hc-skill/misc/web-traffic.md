---
comments: true
---

# WEB流量分析

> MISC · 知识域。Web/HTTP/TLS 及 webshell 管理工具流量分析。标签:**HTTP流量分析**、**TLS流量分析**、**AntSword流量分析**、**Godzilla流量分析**、**Behinder流量分析**、**CS流量分析**。

## 触发特征

- 给 pcapng/pcap 求攻击过程或 flag;题目问"攻击者做了什么"。
- 国内赛中 webshell 流量分析是高频考点(应急响应联动)。

## HTTP流量分析

- Wireshark 过滤:`http.request`、`http contains "flag"`;`Follow TCP Stream` 逐流看。
- 导出对象:`File → Export Objects → HTTP` 拉全部传输文件;HTTP 分段重组。
- 上传外带:POST body 里的文件外带还原(MetaCTF 2026);分段传输拼合(ASIS CTF Finals 2013)。
- 邮件头分析(SMTP 流里的 header 线索);User-Agent 门禁 robots.txt(TAMUctf 2019)。

## TLS流量分析

- **有密钥**:`SSLKEYLOGFILE` 导入 Wireshark(Preferenes → TLS)解密;TLS master key 从 coredump 提取(PlaidCTF 2014)。
- **RSA 私钥**:服务器私钥导入(RSA 密钥交换场景;ECDHE 不可行)。
- **弱 RSA**:证书 RSA 可分解 → 自行解密会话(TLS 弱密钥解密,linux-forensics 场景)。
- RDP 会话:PKCS12 提取解密(HITB 2017);WPA/WEP 四步握手 + aircrack(DefCamp CTF 2016)。
- 假 TLS 流:伪 TLS 流 + mDNS key + 可打印性合并(取证向)。

## AntSword流量分析(蚁剑)

- 特征:默认 `ua` 可自定义但常见 `antSword/v2`;请求体 URL 编码。
- 默认编码器:base64(`cmd=base64(payload)`)响应带随机前缀(默认 16 字节噪音)+ 尾部随机注释。
- 解码流程:响应去前缀去尾注 → base64 解;请求体 URL 解码找执行命令。
- 自定义编码器:PHP 需要 eval 混淆层,顺着编码逻辑逆。

## Godzilla流量分析(哥斯拉)

- 特征:cookie/dapanda 类参数名可自定义;请求响应全 base64(或 AES)加密。
- 流程(默认 PHP_XOR_BASE64):key + pass(默认 pass=key 的 md5 前 16 位)→ XOR 解密 body。
- 响应结构:32 位 md5(key+session) + 加密数据 + 32 位 md5(key) 尾巴。
- Java 场景(memshell)流量特征:`xc` 参数(AES key)。

## Behinder流量分析(冰蝎)

- 特征:建立连接时两个长 POST(密钥协商);后续流量 AES-128-CBC(默认 key=连接口令 md5 前 16 位)。
- 默认口令:rebeyond(冰蝎2)、冰蝎3/4 可自定义 → 字典爆破 key。
- 解密:取 key md5[:16] AES 解密请求响应体。

## CS流量分析(Cobalt Strike)

- beacon 流量:HTTP beacon URI 规律(固定长度、checkin 任务);Malleable C2 profile 的特征。
- 解密:C2 配置提取(`dissect.cobaltstrike` / 178176 键 XOR 对称解密);任务与回传数据解析(FireShell CTF 2020 PCAP 中 beacon 分析)。
- 心跳间隔 + jitter;jitter 累计统计找 beacon(取证向)。

## 工具速查

```bash
tshark -r x.pcap -Y "http.request" -T fields -e http.request.uri
# Wireshark: Follow Stream / Export Objects / SSLKEYLOGFILE
# 在线:CyberChef 解 base64/AES;php 执行 dump 脚本还原 webshell 会话
```

## 转向

- 解密出的命令执行记录 → [应急响应](../ir/index.md);流量里藏文件 → [文件结构](file-structure.md)
