---
comments: true
---

# Burp Suite

Burp Suite 是 Web 安全测试的事实标准工具：它把自己架在浏览器和目标站点之间当一个代理，所有 HTTP 请求和响应都要从它手里过一遍，你可以拦截、查看、修改、重放、批量爆破。CTF 的 Web 题，九成以上的解题过程都离不开它。

本章按「装好 → 抓到包 → 改包重放 → 爆破 → 辅助小工具 → 被动信息收集」的顺序讲，每一步都以做题为目标，够用即止。

!!! note "版本选择"
    Community（免费）版已经覆盖了本章全部功能，足够打完绝大多数 CTF。Professional 版主要多了主动漏洞扫描器（Scanner）和无节流的 Intruder，CTF 场景不是刚需。社区版的 Intruder 有限速，小字典爆破完全够用。

## 安装与代理配置

### 安装

Burp Suite 是 Java 程序，去 PortSwigger 官网下载对应平台的安装包即可。Kali Linux 里自带（`burpsuite` 命令直接启动）。启动后选 `Temporary project`（做题不需要存项目文件），一路 Next 进入主界面。

界面顶部是一排功能标签，本章会用到的是：

- `Proxy`：抓包、拦截、改包。
- `Repeater`：手工重放一个请求。
- `Intruder`：自动化批量发包（爆破）。
- `Decoder` / `Comparer`：编码转换与报文对比。
- `Target`：站点地图与被动扫描结果。

### 浏览器代理设置

Burp 默认监听 `127.0.0.1:8080`（可在 `Proxy` → `Proxy settings` 里改）。让浏览器的流量走 Burp，两种常见做法：

1. 用 Burp 自带的浏览器：`Proxy` → `Intercept` 标签里点 `Open browser`，这个内置 Chromium 已经配好代理和证书，**零配置，强烈推荐做题时用**。
2. 用自己的浏览器：装一个代理切换插件（如 FoxyProxy），把 HTTP/HTTPS 代理指向 `127.0.0.1:8080`。

### HTTPS 证书

现在的 CTF 靶场越来越多用 HTTPS。HTTPS 是加密的，Burp 要在中间解密，就必须让浏览器信任 Burp 自己的 CA 证书，否则会报证书错误、抓不到包。

安装步骤：

1. 浏览器代理已经指向 Burp 的前提下，访问 `http://burp`（或 `http://127.0.0.1:8080`），页面右上角点 `CA Certificate` 下载 `cacert.der`。
2. 在浏览器证书管理里把它导入为「受信任的根证书颁发机构」。Firefox 用自己的证书库，要在 `设置 → 隐私与安全 → 查看证书 → 证书颁发机构 → 导入` 里操作，并勾选「信任此 CA 标识网站」。
3. 重新访问 HTTPS 站点，不再报证书错误即成功。

如果用 Burp 内置浏览器，这一步可以跳过——它内置信任了 Burp 的 CA。

## Proxy：抓包改包基本功

### 拦截开关与历史记录

`Proxy` → `Intercept` 标签里有个开关：`Intercept is on / off`。

- **on**：每个请求发出去之前都会停在 Burp 里等你处理。你可以点 `Forward` 放行（可改后再放）、`Drop` 丢弃。
- **off**：流量直接通过，Burp 只记录不拦截。

无论开关状态如何，所有经过的请求响应都记录在 `HTTP history` 里。做题时的常见姿势是：**平时关着 Intercept，正常浏览让流量进历史记录，想细看哪个包就在历史里翻**；只有要临时改一个 GET 参数之类的场景才临时打开拦截。

### 拦截改包示例

假设一道题要 `POST /login`，你想把提交的 `role=user` 改成 `role=admin` 看看有没有逻辑漏洞（配合《逻辑漏洞》一章的思路）：

1. 打开 `Intercept is on`。
2. 浏览器提交表单，请求停在 Burp 里：

```http
POST /login HTTP/1.1
Host: ctf.example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 29

username=tom&password=123&role=user
```

3. 直接把 `role=user` 改成 `role=admin`，点 `Forward`。
4. 响应回来，要么显示在浏览器，要么在历史记录里看。

拦截界面里还能右键选择 `Do intercept` → `Response to this request`，把 **响应** 也拦下来改——某些前端校验的题（比如 JS 判断响应里的 `success` 字段才显示下一关）就靠改响应绕过。

!!! tip "别在拦截里干活"
    拦截一次只能处理一个包，改包重放属于 Repeater 的活儿。拦到想要的包后，右键 `Send to Repeater`（Ctrl+R），然后关掉 Intercept，去 Repeater 里慢慢折腾。

## Repeater：重放与手工测试

Repeater 是 CTF 里使用频率最高的标签：把一个请求放进去，改一改，点 `Send`，右边立刻看响应，可以无限次重复，互不干扰。

### 基本用法

- 从 HTTP history 或 Intercept 里右键 `Send to Repeater`。
- 左边是请求编辑器，直接改任何部分：URL 参数、Header、Body。改完点 `Send`。
- 右边是响应，可以切换 `Pretty`（格式化）/ `Raw`（原始字节）/ `Hex` 视图。
- 可以开多个 Repeater 标签页，右键标签名 `Rename` 改名，比如「union 注入」「读 flag」，方便管理一道题的多条线。

### 手工 SQL 注入示例

配合《SQL注入》一章，假设 `GET /search?id=1` 存在注入。在 Repeater 里依次尝试：

```http
GET /search?id=1' HTTP/1.1
Host: ctf.example.com
```

响应报 500 错误 → 存在注入点。继续改：

```http
GET /search?id=1' order by 3--+ HTTP/1.1
```

正常 → 列数至少是 3。再试：

```http
GET /search?id=-1' union select 1,flag,3 from flag--+ HTTP/1.1
```

响应里直接带出 flag。整个过程就是在 Repeater 里「改一个字符 → Send → 看响应」的循环，比浏览器快得多，也不用担心 URL 编码问题——空格、`'`、`--` 都按原样发。

!!! tip "自动 URL 编码"
    有些 WAF 或后端对未编码的特殊字符敏感。在请求编辑器里选中一段文本，右键 `Convert selection` → `URL` → `URL-encode key characters`，Burp 会帮你编码。这也是测验「编码后还能不能注入」的快速办法。

## Intruder：爆破实战

Intruder 用来「把一个请求模板里的某些位置换成字典里的值，自动发完所有组合」。打开方式：右键任意请求 `Send to Intruder`（Ctrl+I）。

### 核心概念

- **Payload positions（位置标记）**：在 `Positions` 标签里，用 `§` 包住要替换的部分。先点 `Clear §` 清空自动标记，再选中目标字符串点 `Add §`。
- **Attack type（攻击模式）**：
    - `Sniper`：逐个位置替换，每次只动一个位置。适合单个参数爆破。
    - `Battering ram`：所有位置同时换成同一个值。
    - `Pitchfork`：多个位置各自配一本字典，按行一一对应（如用户名表对密码表）。
    - `Cluster bomb`：多个位置字典做笛卡尔积，全组合。用户名字典 × 密码字典就用它。
- **Payloads（字典）**：在 `Payloads` 标签为每个位置选字典类型，最常用 `Simple list`，直接粘贴或从文件加载。

### 实战：登录口爆破

题目给一个登录页 `POST /login`，提示「弱口令」。已知测试用户 `admin`，想爆破密码。

第一步，正常登录一次，在 HTTP history 里找到这个请求，右键 `Send to Intruder`。

第二步，在 `Positions` 标签点 `Clear §`，然后选中 Body 里密码的值 `123`，点 `Add §`：

```http
POST /login HTTP/1.1
Host: ctf.example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 29

username=admin&password=§123§
```

攻击模式保持 `Sniper`（只有一个位置）。

第三步，切到 `Payloads` 标签，Payload type 选 `Simple list`，在 `Payload settings` 里粘贴或加载字典。CTF 常用字典：

```text
123456
password
admin
admin123
12345678
qwerty
letmein
```

（Kali 自带 `/usr/share/wordlists/rockyou.txt`，社区版限速下建议先跑小字典。）

第四步，右上角点 `Start attack`。结果窗口按 `Length`（响应长度）或 `Status` 排序——**爆破成功的标志几乎总是「响应和别人不一样」**：密码错误的响应长度都相同，唯一长度不同（或状态码是 302 跳转）的那条就是正确密码。

### 实战：目录爆破

很多 CTF 题把关键页面藏在没有链接的目录里（配合《敏感信息泄露》一章的思路）。同样把一个 `GET / HTTP/1.1` 请求发进 Intruder，把位置标记在路径上：

```http
GET /§§ HTTP/1.1
Host: ctf.example.com
```

字典用常见路径列表（如 `admin`、`backup`、`upload`、`flag.php`、`.git/HEAD`），开始攻击后按状态码排序，重点看 `200` 和 `301/302` 的条目。发现 `GET /.git/HEAD` 返回 200，就是典型的 Git 泄露题入口。

!!! tip "判断结果的技巧"
    - 优先按 `Length` 排序，异类即答案。
    - 可以在结果窗口点 `Add` 一列 `Grep - Match`：在攻击设置里加一条匹配规则（比如响应中包含 `flag{`），命中的行直接标出来。
    - 错误密码返回 200、正确密码返回 302 的场景，按 `Status` 排序。

## Decoder 与 Comparer：够用的小功能

### Decoder：编码解码转换

`Decoder` 标签就是一个多格式转换器。粘贴一段文本，右边选择 `Encode as` / `Decode as` / `Hash`，支持 URL、HTML、Base64、Hex、JWT 等格式，还可以串联多次（Base64 套 URL 编码这种很常见）。

做题场景：

- 响应里看到 `ZmxhZ3toMGF...`，怀疑是 Base64，粘进 Decoder 点 `Decode as → Base64` 验证。
- 拿到一个 JWT（格式 `xxxxx.yyyyy.zzzzz`），Decoder 里 Base64-decode 第二段就能看到 payload 的 JSON 明文，改完再 encode 回去伪造（配合《逻辑漏洞》里越权的思路）。
- 在 Repeater / Proxy 的任何输入框里，选中文本右键也有 `Send to Decoder`，不用手抄。

### Comparer：报文对比

`Comparer` 用来对比两段文本的字节级差异。任意请求/响应右键 `Send to Comparer`，选两段后点 `Words` 或 `Bytes` 对比。

典型用途：

- 注入题里对比 `id=1` 和 `id=1'` 的响应差了几个字节，判断报错点。
- 爆破后对比「疑似成功」和「确定失败」的响应，找出成功标志字符串，回头配进 Intruder 的 Grep Match。

## Target 与被动扫描

### Target 站点地图

`Target` → `Site map` 按域名和目录树展示所有经过 Burp 的 URL——你只要正常浏览一遍目标站点，这里就自动拼出整站的结构。对 CTF 很有用的两点：

- 一眼看出站点有哪些目录和接口，包括你页面上没点到、但 JS 里引用了的接口。
- 任意节点右键 `Send to Repeater / Intruder`，不用回历史记录里翻。

### 被动扫描

「被动扫描」的意思是：Burp 不主动发任何攻击流量，只 **分析已经经过它的请求响应**，从中找出可疑点和信息泄露。Community 版也有这个功能。

结果看两处：

- `Target` → `Site map` 里节点旁边的图标：带感叹号的是有问题的。
- `Dashboard` → `Issue activity`：汇总所有发现的问题，如 `Cleartext submission of password`、`Frameable response`、响应里泄露的邮箱/注释等。

做题时浏览完一遍站点后扫一眼 Issue 列表，经常能捡到提示——比如响应注释里藏的路径、备份文件链接，直接指向《敏感信息泄露》类题目的突破口。

!!! note "主动扫描不在本章范围"
    Professional 版的主动 Scanner 会主动向目标发攻击载荷探测漏洞。CTF 靶机一般结构简单、题意明确，手工 + Intruder 远比挂机扫描高效；而且比赛环境通常不允许对平台发起扫描流量，注意规则。

## 一道综合例题的完整过程

题目：访问目标只有一个登录框，提示「管理员的后门不止一个」。

1. **抓包摸底**：开 Burp 内置浏览器访问站点，关着 Intercept 正常点一遍。`Target` 站点地图里看到 `/login`、`/static/`，没有别的链接。
2. **目录爆破**：把 `GET /` 发进 Intruder，标记路径位置，跑常见目录字典。发现 `/admin.php` 返回 302 跳回登录页，`/backup.zip` 返回 200。
3. **下载分析**：浏览器下载 `/backup.zip`，解压得到网站源码。代码审计（方法见《PHP代码审计》一章）发现登录 SQL 是拼接的：

```php
$sql = "SELECT * FROM users WHERE username='$u' AND password='$p'";
```

4. **Repeater 验证注入**：把登录请求发进 Repeater，Body 改成：

```text
username=admin'-- -&password=x
```

点 `Send`，响应 302 跳到 `/admin.php`——万能密码登录成功。
5. **拿 flag**：浏览器里用同样 payload 登录，后台页面显示 `flag{...}`。

整条链：Target 看结构 → Intruder 爆破目录 → 源码审计 → Repeater 手工验证注入。Burp 的每个标签都用在了刀刃上，这也是大多数 CTF Web 题的标准解题流程。

## 小结

- 装 Burp → 配代理 → 装 CA 证书，用内置浏览器可以省掉后两步。
- `Proxy` 负责看和拦，`HTTP history` 是你的流量账本。
- 改包重放去 `Repeater`，别在拦截里干活。
- 批量爆破去 `Intruder`：标位置、选模式、配字典，结果按 `Length` 找异类。
- `Decoder` 转码、`Comparer` 对比，随手右键 Send to 即可。
- `Target` 站点地图 + 被动扫描的 Issue 列表，是免费的线索收集器。
