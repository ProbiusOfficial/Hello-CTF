---
comments: true
---

# 入侵排查

> IR · 知识域。主机侧失陷排查。标签:**Web失陷事件入侵排查**、**勒索病毒事件入侵排查**、**挖矿木马事件入侵排查**、**系统后门事件入侵排查**、**容器失陷事件入侵排查**、**综合攻击类型事件入侵排查**。

## 触发特征

- "这台机器失陷了,请排查":各类应急响应赛(国赛/护网复盘)的标准形态。

## Web失陷事件入侵排查

- webshell 定位:D 盾/河马(国内工具)、`find` 最近修改的脚本文件(`-mtime -3`)、日志里 POST 大体量请求对应文件(→ [Misc-日志分析](../misc/log-analysis.md))。
- webshell 溯源:落地时间 → 入口漏洞日志时间点对齐(→ [流量分析](traffic-analysis.md) Web攻击流量)。
- 关联检查:临时目录残留(冰蝎/哥斯拉生成的载荷)、计划任务拉起、php/jsp 内存马(tomcat filter 型,检查 class 加载)。

## 勒索病毒事件入侵排查

- 样本定位:加密行为进程(高磁盘 IO、可疑父进程)、加密备注文件(TXT/后缀名)→ 家族识别(ID Ransomware/360 勒索家族库)。
- 入口还原:RDP 爆破日志(→ [日志分析](log-analysis.md) Windows 日志)、共享投递、钓鱼邮件(→ 社工面)。
- 恢复评估:加密是否完整(部分家族有缺陷可解)、影子副本(`vssadmin list shadows`)、备份完好性;关键决策:断网隔离、不重启(内存取证窗口)。
- 系统改动:账户(新建管理员)、防火墙/安全软件被停用记录。

## 挖矿木马事件入侵排查

- 定位:CPU 高进程(`top`/`tasklist` 异常进程名如 kinsing/xmrig/RandomName)、隐藏进程(comparison `/proc` vs ps)、cron/系统定时任务(挖矿守护经典:curl | bash)。
- 传播链:Redis 未授权/Hadoop Yarn/Debug SSRF/弱口令 SSH(国内挖矿主要入口)。
- 持久化清除顺序:停守护(cron/systemd/ld.so.preload 检查!)→ 杀进程 → 清文件 → 补入口漏洞(否则复发)。
- 外连矿池域名提取(IOC)。

## 系统后门事件入侵排查

- 账户后门:隐藏账户(Windows `$` 结尾/注册表 F 值检查)、SSH authorized_keys、Linux `/etc/passwd` UID 0 多账户。
- 持久化点全查:计划任务、systemd service/timer、启动项/注册表 Run、驱动/内核模块(`lsmod` 未知模块)、LD_PRELOAD/ld.so.preload 劫持、SSH 包装后门(ssh-wrapper 进程级,对比 sshd 版本)。
- Rootkit 排查:rkhunter/chkrootkit;对比只读基线(黄金镜像 diff);内存取证(→ [Misc-取证](../misc/forensics.md) 内存镜像)。
- 历史动作:history/PowerShell 历史/日志清空痕迹(→ [日志分析](log-analysis.md))。

## 容器失陷事件入侵排查

- 逃逸判断:宿主异常挂载/新特权容器、docker.sock 访问记录、宿主出现容器内文件(→ [云安全-容器安全](../cld/container.md) 逃逸手法反查)。
- 排查范围:容器内(进程/历史/env)+ K8s 审计日志(谁部署了恶意 pod)+ 镜像层 diff。
- 云凭证检查:容器内 env/metadata 访问痕迹 → AK 泄露面(→ [云安全-身份与访问管理](../cld/iam.md))。

## 综合攻击类型事件入侵排查

- 全景排查套路:先定性(哪类事件)→ 时间线锚点(第一个可疑点)→ 沿时间线双向扩展 → 三视图对齐(主机/日志/流量)→ 出报告(路径 + IOC + 处置)。
- 处置原则:固定证据先于清除;清除先于加固;全账号轮换兜底。

## 转向

- 技术细节:日志 → [日志分析](log-analysis.md);流量 → [流量分析](traffic-analysis.md);取证 → [Misc-取证](../misc/forensics.md)
