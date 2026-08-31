---
comments: true
---

# 数据传输

> DS · 知识域。数据传输链路安全。标签:**数据加密**、**传输协议安全**。

## 触发特征

- 考察"数据在传输中是否被保护/能否被截获篡改"。

## 数据加密

- 传输加密 vs 应用层加密分层:TLS 之内还有业务加密(字段级加密)才是纵深。
- 密钥管理:密钥硬编码/传输中下发(→ [WEB](../web/index.md) 前端加密逆向)/密钥轮换缺失。
- 弱算法面:DES/MD5(密码存储,→ [Crypto-DES](../crypto/des.md)/[MD5](../crypto/md5.md))/ECB 模式泄露结构(→ [Crypto-AES](../crypto/aes.md))。
- 国密体系:SM2/SM3/SM4 在政企系统广泛部署(工具:gmssl、GmSSL-Python;签名/证书场景)。

## 传输协议安全

- 明文协议清理:HTTP/FTP/Telnet/SNMPv2/SMTP → 加密替代(H TTPS/SFTP/SSH/SNMPv3);内部通信同样明文(内网不等于安全)。
- TLS 配置:版本(TLS1.0/1.1 残留)、套件(RC4/3DES/CBC 优先级)、证书校验(客户端禁用校验 → 中间人,→ [IoT-网络安全](../iot/network.md))。
- 接口传输安全:签名机制(时间戳+nonce+签名)防重放;签名算法弱(无 HMAC 密钥,→ [Crypto-FNV](../crypto/fnv.md)/[SHA1](../crypto/sha1.md) 长度拓展)。
- 大文件/批传输通道:FTP 明文口令(抓包)、rsync 未鉴权、共享目录 SMB(NTLMv2 抓取破解,→ [Misc-其他流量分析](../misc/other-traffic.md))。

## 转向

- 协议流量还原 → [Misc](../misc/index.md)/[应急响应-流量分析](../ir/traffic-analysis.md);加密算法本体 → [Crypto](../crypto/index.md)
