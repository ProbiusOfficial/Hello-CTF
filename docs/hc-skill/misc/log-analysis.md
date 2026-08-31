---
comments: true
---

# 日志分析

> MISC · 知识域。各类日志的攻击痕迹提取。标签:**系统日志分析**、**HTTP日志分析**、**SQL盲注日志分析**。

## 触发特征

- 给 access.log/secure.log/evtx 求"攻击者做了什么"或提取 flag。
- 取证向的日志 → 也与 [应急响应](../ir/index.md) 重叠;本页偏 CTF 解题。

## 系统日志分析

- Linux:`/var/log/auth.log`(SSH 爆破/成功登录)、`secure`、`cron`、`history`(bash history 时间戳 HISTTIMEFORMAT)、wtmp/btmp(last/lastb)。
- 提权痕迹:sudoers 修改、SUID 文件、cron 新增任务(→ [应急响应-入侵排查](../ir/intrusion-investigation.md))。
- Windows:事件 ID 4624/4625(登录)、4720(建用户)、7045(服务安装)、RDP 会话 ID;evtx 用 python-evtx/EvtxExplorer 解析。
- PowerShell 历史作时间线;用户配置目录创建时间 = 首次登录指示(取证套路)。

## HTTP日志分析

- access.log 逐条过攻击特征:SQLi 关键字、`../` 穿越、webshell 路径(如 `POST /uploads/shell.php`)、异常 UA。
- URL 解码后分析(双重编码绕过);响应状态码序列判断攻击成败(200/500 交替)。
- 日志注入:UA/Referer 里的命令回显痕迹;日志投毒 + 文件包含链的确认。
- editor 备份文件访问痕迹(`.swp`/`.bak` 源码泄露,h4ckc0n 2017);User-Agent 门禁 robots.txt(TAMUctf 2019)。

## SQL盲注日志分析

- 特征:同一参数高频重复、长度渐变;布尔/时间盲注的 payload 序列(`AND (SELECT ...)`)。
- 还原攻击结果:按注入脚本逻辑(二分/逐字符)从请求序列反推拖出的数据。
- `randomblob()` 时间盲注流量识别(SECCON 2017);REGEXP 字节级 oracle(BSides Delhi 2018)。
- 写脚本回放:把日志中的 payload 参数化,按位拼出被拖字段。

## 工具速查

```bash
grep -E "union|select|\.\./|eval\(" access.log | awk '{print $1}' | sort | uniq -c
python: URL decode + 正则序列化分析
EvtxECmd / python-evtx    # evtx
logparser(Windows)
```

## 转向

- 攻击确认后找落点 → [应急响应](../ir/index.md);日志本身是隐写载体 → [其他隐写](other-stego.md)
