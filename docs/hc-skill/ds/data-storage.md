---
comments: true
---

# 数据存储

> DS · 知识域。存储层安全。标签:**数据库安全分析**、**文件系统安全**、**数据备份与恢复**、**数据完整性校验**。

## 触发特征

- 考察"静态数据"的保护:库、文件、备份。

## 数据库安全分析

- 访问面:默认口令/弱口令(root@%、sa 空密码)、公网暴露(→ [渗透测试-信息搜集](../pen/info-gathering.md));未授权访问(Redis/MongoDB/Elasticsearch 经典,→ [WEB-NoSQL注入](../web/nosql.md))。
- 权限面:应用账号高权(DBA 连业务库)、视图/行列权限未用(全表可查)、审计未开。
- 数据面:敏感字段明文存储(密码可逆加密/明文)、脱敏缺失;SQL 注入到数据的直接路径(→ [WEB-SQL注入](../web/sql-injection.md))。
- 备份文件:数据库 dump 泄露(.sql/.bak 文件落盘可下载,→ [WEB-文件泄露](../web/file-leak.md))。

## 文件系统安全

- 权限:共享目录(NTFS ACL/Samba)过宽、 Everyone 可写;敏感目录遍历(→ [WEB](../web/index.md) 目录穿越)。
- 加密:BitLocker/LUKS 未启用(物理访问即拿到数据);加密密钥与数据同盘(→ [Misc-取证](../misc/forensics.md) 加密磁盘)。
- 残留:已删除文件可恢复(→ [Misc-取证](../misc/forensics.md));缓存/临时文件/交换文件里的数据残留。

## 数据备份与恢复

- 备份策略审计:周期/保留期/异地;备份可访问面(公开桶/共享目录,→ [云安全-数据保护](../cld/data-protection.md))。
- 恢复演练与完整性(→ [云安全-灾难恢复](../cld/disaster-recovery.md))。

## 数据完整性校验

- 校验机制:哈希链/HMAC(→ [Crypto](../crypto/index.md))、数据库约束、区块链存证(→ [ETH](../eth/index.md))。
- 篡改检测:文件完整性监控(AIDE/osquery);日志完整性(→ [云安全-监控与日志](../cld/monitoring.md))。

## 转向

- 库本体漏洞 → [WEB](../web/index.md);取证恢复 → [Misc-取证](../misc/forensics.md)
