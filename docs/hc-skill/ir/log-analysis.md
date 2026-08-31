---
comments: true
---

# 日志分析

> IR · 知识域。应急响应中的日志取证。标签:**Windows日志分析**、**Linux日志分析**、**数据库日志分析**、**容器日志分析**、**其它应用日志分析**。

## 触发特征

- 给日志包(或直接给主机)要求还原"入侵怎么发生、做了什么"。

## Windows日志分析

- 关键事件 ID:4624/4625(登录成功/失败,类型 10=RDP 3=网络)、4720/4726(建/删用户)、4732(入管理组)、7045(新服务安装)、6005/6006(开关机)、1102(清日志!)、4698(计划任务创建)、4688(进程创建,需开审计)。
- PowerShell:4104 脚本块日志(混淆命令还原)、4103 模块日志;PSReadLine 历史文件。
- 登录分析:爆破(4625 密集)+ 成功(4624)时间点;异常时间登录、非常规账户(→ [Misc-日志分析](../misc/log-analysis.md) 系统日志部分)。
- 工具:LogParser、EvtxECmd+Timeline Explorer、python-evtx。

## Linux日志分析

- `auth.log/secure`:SSH 爆破与成功、sudo 提权记录、su 切换;`last/lastb/w`(登录链)。
- Web 日志:webshell 命中(POST 大体量、异常参数)、SQLi/扫描路径(→ [Misc-日志分析](../misc/log-analysis.md) HTTP 部分)。
- `cron/at` 日志(计划任务后门确认)、`history`(带时间戳还原操作者动作)、`messages/syslog`(服务异常)。
- 登录相关文件被清空/截断本身就是 IOC;`/var/log/wtmp` 时间戳异常。

## 数据库日志分析

- MySQL:general_log(全量语句,注入/读文件痕迹 `load_file`/`into outfile`)、binlog(数据变更还原);慢日志里的盲注延时特征。
- MSSQL:xp_cmdshell 调用记录、错误日志;Oracle:审计日志。
- 数据库账号爆破与异常查询来源 IP(应用服务器 vs 陌生 IP)。

## 容器日志分析

- 容器逃逸痕迹:privileged 容器创建、docker.sock 挂载、宿主路径挂载;`/var/log/containers/`(K8s)+ API Server 审计日志(who did what when)。
- 镜像层 diff:运行时产生的异常文件(挖矿程序/webshell 落点,→ [云安全-容器安全](../cld/container.md))。
- 容器内 history/env 残留(环境变量注入的密钥泄露)。

## 其它应用日志分析

- 中间件:Tomcat catalina.out(部署 war)、Nginx error/ access、IIS 日志(ex 命名,字段顺序与 Apache 不同)。
- 服务器组件:Redis(写文件操作)、FTP(vsftpd 上传)、宝塔/面板日志(国内场景高发:面板操作记录)。
- 云平台操作日志(→ [云安全-监控与日志](../cld/monitoring.md));VPN/堡垒机日志(跳板溯源)。

## 转向

- 日志指向主机后门 → [入侵排查](intrusion-investigation.md);攻击流量 → [流量分析](traffic-analysis.md)
