---
comments: true
---

# 内网信息收集

在 CTF 的内网渗透题（尤其是 AWD、多层网络架构的综合渗透题）中，当你通过 [RCE](./rce.md)、[文件上传](./file_upload.md) 或 [SSRF](./ssrf.md) 等手段拿到第一台跳板机（边界机）的 shell 后，真正的挑战才刚刚开始：flag 往往不在边界机上，而在内网某台不直接对外的机器上。要从跳板机走到目标机，第一步永远是 **信息收集**——搞清楚自己在哪、周围有什么、下一步能打谁。

本章按「本机 → 网段 → 内网资产」的顺序展开，最后给出一份可直接照着执行的清单。

## 本机信息搜集

拿到 shell 的第一件事不是乱扫，而是先摸清楚本机。本机信息有三个价值：确认权限和系统类型（决定后续用什么命令和工具）、找到网卡和网段（决定扫哪里）、翻到凭据（直接用于横向移动）。

### Linux 常用命令

**系统信息**：

```bash
uname -a            # 内核版本，判断能否用脏牛之类的内核提权漏洞
cat /etc/os-release # 发行版信息
hostname            # 主机名，有时直接提示角色（如 db01、web02）
```

**用户与权限**：

```bash
id                  # 当前用户及所属组，重点看是否在 sudo / docker / lxd 组
whoami
cat /etc/passwd     # 系统上有哪些用户，找出可登录的（shell 为 /bin/bash 的）
sudo -l             # 当前用户能以 sudo 执行什么命令，免密的直接提权
ls -la /home/       # 各用户家目录，翻 .bash_history、.ssh/ 往往有惊喜
history             # 当前 shell 的历史命令，管理员手滑输过的密码可能在里面
```

**进程与服务**：

```bash
ps aux              # 全部进程，找数据库、中间件、运维脚本的痕迹
ss -tlnp            # 监听端口与对应进程（老系统用 netstat -tlnp）
crontab -l          # 当前用户计划任务
ls /etc/cron.d/     # 系统计划任务，运维脚本可能硬编码密码
```

**网络连接**：

```bash
ip addr             # 网卡与 IP，确认有几张网卡、各自网段（老系统用 ifconfig）
ip route            # 路由表，找默认网关和其他可达网段
ss -tnp             # 当前建立的 TCP 连接，看本机在和谁通信
cat /etc/hosts      # 静态域名映射，常泄露内网主机名和 IP
arp -a              # ARP 缓存，近期通信过的同网段主机（也可 cat /proc/net/arp）
```

**敏感文件与凭据**：

```bash
ls -la ~/.ssh/                        # id_rsa、authorized_keys、known_hosts
cat ~/.ssh/known_hosts                # 这台机器 ssh 连过哪些主机，等于一张内网地图
find / -name "*.conf" -o -name "config*.php" 2>/dev/null | head
grep -rn "password" /var/www/html/ 2>/dev/null | head    # Web 目录里翻数据库密码
cat /var/www/html/config.php          # 站点配置里的数据库凭据，库和后台经常不同机
find / -name "flag*" 2>/dev/null      # CTF 题别忘了直接找 flag
```

### Windows 常用命令

```cmd
systeminfo                :: 系统版本、补丁情况、域信息
whoami /all               :: 当前用户、组、特权
net user                  :: 本地用户列表
net user administrator    :: 查看某用户详情
tasklist /svc             :: 进程与对应服务
netstat -ano              :: 端口与连接，配合 tasklist 按 PID 找进程
ipconfig /all             :: 网卡、IP、DNS、域
route print               :: 路由表
arp -a                    :: ARP 缓存
netsh firewall show state :: 防火墙状态（决定能不能扫出去）
type C:\Users\*\Desktop\flag.txt    :: CTF 题惯例位置
```

凭据方面，Windows 重点关注浏览器/远程桌面保存的密码、`C:\Windows\System32\config\` 下的 SAM/SYSTEM 文件（需要高权限导出），以及各类配置文件中写死的密码。在 CTF 里更常见的是直接翻翻桌面、Web 根目录和计划任务脚本。

!!! tip "记忆口诀"
    先 `id` / `whoami` 看权限，再 `ip addr` / `ipconfig` 看网段，然后 `ss -tlnp` / `netstat` 看端口，最后翻配置文件和历史命令找凭据。四步走完，本机就摸清了。

## 网段测绘思路

知道了本机 IP（比如 `172.18.0.2`），下一个问题是：**还有哪些网段可达、网段里有哪些存活主机**。

### 确认可达网段

- **多张网卡**：`ip addr` 出现两个以上非 `lo` 接口，说明机器跨在多个网络之间，每个接口的网段都要探测。这是多层内网题的常见设计——边界机连外网和一个内网段，内网机再连更深的网段。
- **路由表**：`ip route` 里的非默认路由条目（如 `10.1.0.0/24 via 172.18.0.1`）直接告诉你还能到达哪些网段。
- **ARP 缓存与 known_hosts**：`arp -a` 给出同网段近期通信过的主机，`~/.ssh/known_hosts` 给出管理员登录过的机器。这两处是零噪音的"免费情报"，优先看。

### 存活主机探测

确定了网段（如 `172.18.0.0/24`），先找哪些 IP 是活的，再扫端口，避免对 254 个地址全端口扫描浪费时间。

```bash
# ICMP ping 扫，可能被防火墙拦
for i in $(seq 1 254); do ping -c 1 -W 1 172.18.0.$i & done; wait

# ARP 探测（仅限同网段二层，但几乎无法被拦，最可靠）
arp-scan -l            # 需要安装 arp-scan
# 或用 nmap 的 ARP ping：
nmap -sn -PR 172.18.0.0/24

# 无工具纯 shell 兜底：对常见端口发 TCP 连接测试
for i in $(seq 1 254); do (echo > /dev/tcp/172.18.0.$i/80) 2>/dev/null && echo "172.18.0.$i:80 open" & done; wait
```

实际做题时的取舍：同网段优先 ARP 探测（快、难拦截）；跨网段用 ICMP 加常见 TCP 端口（80/445/22/3389）组合探测。拿到存活列表后再进入下一步的端口扫描。

## 资产扫描与端口探测

存活主机有了，就要弄清楚每台机器开了什么服务。三个工具的取舍是 CTF 内网题的基本功。

### nmap：精准但重

```bash
nmap -sT -Pn -p 22,80,443,445,3306,6379,8080 172.18.0.5   # 指定常见端口快速扫
nmap -sT -Pn -p- 172.18.0.5                               # 全端口，CTF 中冷门端口常藏 flag
nmap -sV -sC -p 80 172.18.0.5                             # 服务版本识别 + 默认脚本
```

- 跳板机没有公网时用 `-sT`（TCP connect 扫描），不依赖 raw socket 权限；有 root 才用 `-sS`（SYN 半开扫描，更快更隐蔽）。
- `-Pn` 跳过主机存活检测，直接扫端口——目标禁 ping 时必加。
- nmap 的优点是 `-sV`/`-sC` 能识别服务版本甚至跑出 banner 里的 flag；缺点是体积大，内网靶机上经常没有，需要静态编译版或代理转发扫描。

### fscan：内网一把梭

[fscan](https://github.com/shadow1ng/fscan) 是 Go 写的单文件内网扫描器，扔上去就能跑，是 CTF 内网题最常用的工具：

```bash
chmod +x fscan
./fscan -h 172.18.0.0/24 -o result.txt
```

一条命令默认完成：存活探测 → 常见端口扫描 → 服务识别（Web 标题、Redis/SSH/MySQL banner）→ 弱口令爆破（SSH、MySQL、Redis 未授权）→ 部分漏洞探测（MS17-010 等）。CTF 里 fscan 的输出经常直接给出下一个突破口，比如某台机器 Redis 6379 未授权访问，或者 Web 服务标题里就写着线索。

注意 fscan 默认行为较"重"（会爆破），在 AWD 对抗环境中可能触发告警；只想安静扫端口时用 `-nopoc -nobr` 关掉漏洞探测和爆破。

### masscan：速度优先

```bash
masscan -p 1-65535 172.18.0.0/24 --rate 1000
```

masscan 全端口扫一个 /24 只要几十秒，但它只做端口开放探测，不做服务识别，且需要 raw socket（通常要 root）。在 CTF 中它的典型用法是配合 nmap：masscan 快速圈出开放端口，nmap 再对这些端口做 `-sV` 精细识别。

**三者取舍一句话**：机器上有哪个用哪个；都能装的话，fscan 一把梭出概貌，nmap 对可疑端口做版本识别，masscan 只在大网段全端口普查时上场。

## 收集到的信息如何指导下一步

信息收集不是目的，每一条信息都应该对应一个动作。常见的对应关系：

- **`/etc/hosts` 或 known_hosts 里的主机名** → 这些就是内网拓扑，优先探测它们。
- **Web 配置里的数据库密码** → 数据库往往在另一台内网机上，密码可能复用——拿它去试 SSH 和其他服务（这在「横向移动」一章会详细展开）。
- **fscan 报出 Redis 6379 未授权** → 结合 [SSRF](./ssrf.md) 学到的 gopher 打 Redis 思路，写计划任务或 SSH key 拿 shell。
- **开了 80/8080 的内网 Web** → 内网服务常是"弱防护"，把外网学到的 SQL注入、文件包含、反序列化再试一遍；内网 CMS 还经常保留默认口令。
- **445 / 3389 开放的 Windows** → 试 SMB 弱口令、MS17-010，或拿收集到的密码远程登录。
- **`history` / 计划任务里的运维脚本** → 脚本里常硬编码其他机器的账号密码，是最直接的横向跳板。

原则只有一条：**每收集到一条信息，都问一句"这能让我到达哪台新机器、拿到什么新权限"**。收集和攻击交替进行，一步步向 flag 所在的内网深处推进，这正是「横向移动」章要系统讲的内容。

## 典型例题：多层内网中的第二面 flag

题目描述：一个 PHP 站点存在命令执行漏洞，提示"真正的 flag 在内网"。这是 CTF 综合渗透题的经典模板。

**第一步：拿到边界机 shell**。通过命令执行漏洞执行 `id`，回显 `uid=33(www-data)`。确认拿到的是 Web 服务权限。

**第二步：本机信息搜集**。

```bash
ip addr
```

发现除了 `eth0: 172.20.0.2/24` 外还有一块 `eth1: 192.168.1.2/24`——机器跨两个网段，内网入口就是 `192.168.1.0/24`。

```bash
cat /var/www/html/config.php
```

拿到数据库密码 `Passw0rd@2024`，先记下来。再找一找有没有直接的情报：

```bash
arp -a; cat /root/.ssh/known_hosts 2>/dev/null
```

ARP 缓存显示 `192.168.1.10`，说明这台机器近期和同网段的 .10 通信过——优先目标锁定。

**第三步：存活与端口探测**。跳板机没有 nmap，上传静态编译的 fscan：

```bash
./fscan -h 192.168.1.0/24 -nopoc -nobr -o result.txt
```

结果中 `192.168.1.10` 开放了 `80` 和 `6379`（Redis）。80 端口的 Web 标题显示是内部运维系统。

**第四步：利用信息打下一台**。边界机无法直接访问外网，但浏览器侧可以通过题目的 SSRF 点或在边界机上用 curl 访问内网：

```bash
curl http://192.168.1.10/
```

页面是登录框，想起第二步翻到的数据库密码 `Passw0rd@2024`——密码复用是内网常态，用 `admin / Passw0rd@2024` 尝试登录，成功进入后台，页面中放着第二段 flag。

如果登录失败，下一步就是结合 [SSRF](./ssrf.md) 的 gopher 协议打法，从 6379 端口的 Redis 未授权访问写入 SSH key 或计划任务，同样能拿下 .10。

**复盘本题的信息链**：双网卡（发现内网段）→ 配置文件（凭据）→ ARP 缓存（锁定目标）→ fscan（确认服务）→ 密码复用（拿下内网机）。每一步都用上了上一步收集到的信息。

## 信息收集清单

拿到内网 shell 后按此清单逐项执行，基本不会漏掉关键信息：

- [ ] **权限**：`id` / `whoami /all`，确认当前用户和所属组
- [ ] **系统**：`uname -a` / `systeminfo`，判断系统类型与提权方向
- [ ] **网络**：`ip addr` + `ip route` / `ipconfig /all` + `route print`，列出所有网卡与可达网段
- [ ] **免费情报**：`arp -a`、`/etc/hosts`、`~/.ssh/known_hosts`、`history` / `~/.bash_history`
- [ ] **监听端口**：`ss -tlnp` / `netstat -ano`，本机自己开了什么服务
- [ ] **凭据**：Web 配置文件、计划任务脚本、`~/.ssh/id_rsa`，全部记录备用
- [ ] **顺手找 flag**：`find / -name "flag*" 2>/dev/null`，CTF 题先排除 flag 就在本机的情况
- [ ] **存活探测**：同网段 ARP 探测，跨网段 ping + 常见 TCP 端口
- [ ] **端口扫描**：fscan 出概貌（`-nopoc -nobr` 保持安静），nmap `-sV` 识别可疑服务，大网段全端口用 masscan
- [ ] **建立信息-动作映射**：每条信息标注"能用它打谁"，形成下一步攻击计划
- [ ] **持续迭代**：每拿下一台新机器，从头把这份清单再执行一遍

信息收集的水平决定了内网渗透的速度。把这份清单练成肌肉记忆，再结合「横向移动」一章的技术，多层内网题就有清晰的推进路线了。
