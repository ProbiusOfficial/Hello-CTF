---
comments: true
---

# HTTP协议

HTTP 是 Web 题的"通用语言"：无论是 SQL注入、XSS攻击 还是 文件上传，最终都要落到一个 HTTP 请求上。很多入门题（改 UA、改 Referer、伪造 XFF、弱 Cookie）本质上就是在考你是否看得懂、改得动一个 HTTP 报文。本章不展开 RFC，只讲做题够用的部分：先抓一个真实的包逐行读，再讲方法与 Header 的常见考点，最后简单说清 Cookie/Session 的传输方式和 HTTPS 抓包。

## 从一次抓包读起

### 抓一个完整的请求

打开 Burp Suite，浏览器代理指向 `127.0.0.1:8080`，随便访问一个登录页并提交表单，在 Burp 的 HTTP history 里能看到类似这样的原始请求：

```http
POST /login.php HTTP/1.1
Host: challenge.example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: text/html,application/xhtml+xml
Accept-Language: zh-CN,zh;q=0.9
Referer: http://challenge.example.com/login.php
Content-Type: application/x-www-form-urlencoded
Content-Length: 29
Cookie: PHPSESSID=a1b2c3d4e5f6; role=guest
Connection: close

username=admin&password=123456
```

以及服务器返回的响应：

```http
HTTP/1.1 200 OK
Date: Wed, 12 Jun 2024 08:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Set-Cookie: role=user; Path=/; HttpOnly
Content-Type: text/html; charset=utf-8
Content-Length: 512

<html><body><h1>Login Failed</h1>...</body></html>
```

下面把这两段报文拆开，逐块讲清楚。

### 请求行

请求的第一行叫 **请求行（Request Line）**，由三部分组成，空格分隔：

```http
POST /login.php HTTP/1.1
```

- `POST`：请求方法（Method），告诉服务器"我要提交数据"，详见下文的方法小节。
- `/login.php`：请求路径（Request-URI），即 URL 去掉协议和域名后的部分。CTF 中改路径是基本功——目录穿越、任意文件读取 等章节里的 payload 都是在这里做文章。
- `HTTP/1.1`：协议版本。做题时几乎不需要关心，知道有 1.1 和 2 即可；Burp Repeater 里改包一般用 1.1。

### 请求头（Header）

从第二行开始，到第一个空行为止，是 **请求头**。每行一个 `字段名: 值`，顺序无关。Header 是 CTF 出题的重灾区，上面抓包里加粗关注的几个：

- `Host`：目标域名。虚拟主机靠它区分站点，SSRF 和一些越权题会考 Host 头伪造。
- `User-Agent`：客户端身份。经典考点：题目要求"请使用 xxx 浏览器访问"，改它就行。
- `Referer`：从哪个页面跳转过来的。经典考点："只能从某页面访问"，直接改 Referer 绕过。
- `Cookie`：携带会话凭证，单独在后面的 Cookie 小节讲。
- `Content-Type`：告诉服务器 Body 的格式。改它可以绕过部分校验（如文件上传时改成 `image/png`），也能触发 XXE（改成 `application/xml`）等漏洞。

**空行** 是请求头与请求体的分界，千万不能丢——Burp Repeater 里如果删了空行，服务器会把 Body 当成畸形的 Header 处理。

### 请求体（Body）

空行之后的部分是 **请求体**，只有 POST/PUT 等方法才有。最常见的是表单格式：

```http
username=admin&password=123456
```

即 `键=值&键=值`，与 `Content-Type: application/x-www-form-urlencoded` 对应。其他常见格式：

- `application/json`：`{"username":"admin"}`，注意 PHP 里 json 格式不走 `$_POST`，要读 `php://input`。
- `multipart/form-data`：文件上传用的格式，Body 被 boundary 分成多段，细节见 文件上传 章节。

### 响应行与状态码

响应的第一行是 **状态行**：`协议版本 状态码 状态短语`。状态码三位数字，第一位是类别，CTF 里常见的就这几个：

| 状态码 | 含义 | CTF 中的意义 |
|--------|------|--------------|
| `200` | 成功 | 正常返回，flag 常常就藏在页面里 |
| `301/302` | 重定向 | 跳转到新地址，**Location 头指向的页面可能没做权限校验**，在 Burp 里别跟着跳转，直接看本次响应体 |
| `401` | 未认证 | 需要登录，常见于 HTTP Basic Auth |
| `403` | 禁止访问 | 有东西但不让看，试试目录穿越、改 UA/IP 头等绕过 |
| `404` | 不存在 | 扫目录时的"基准值"，区别 403 和 404 很重要 |
| `500` | 服务器错误 | 参数可能打进了危险函数，配合报错信息往往有戏（如 SQL注入 的报错注入） |

响应头里值得关注的有 `Set-Cookie`（服务器下发 Cookie）、`Location`（302 跳转目标）、`Server`（泄露中间件版本，属于 敏感信息泄露 的范畴）。

### 自己动手：用 curl 复现这个包

不依赖 Burp，命令行也能构造同样的请求：

```bash
curl -v -X POST 'http://challenge.example.com/login.php' \
  -H 'Referer: http://challenge.example.com/admin' \
  -H 'Cookie: PHPSESSID=a1b2c3d4e5f6; role=admin' \
  -d 'username=admin&password=123456'
```

- `-v`：打印完整的请求和响应头，相当于"抓包"。
- `-X POST`：指定方法；`-d` 携带 Body 时默认就是 POST。
- `-H`：自定义任意 Header，做题时 90% 的操作就是用它改头。

建议读者现在就用 `-v` 抓一个自己访问任意网站的包，对照上面的结构读一遍。

## 常见请求方法

| 方法 | 语义 | CTF 考点 |
|------|------|----------|
| `GET` | 获取资源，参数放在 URL query 里 | 参数直接可见可改，是注入题的主战场 |
| `POST` | 提交数据，参数放在 Body | 表单登录、文件上传；注意 Body 格式由 Content-Type 决定 |
| `PUT` | 上传/替换资源 | 若服务器开启 WebDAV 且配置不当，`PUT /shell.php` 直接 getshell |
| `DELETE` | 删除资源 | 同上，危险的 HTTP 方法应当被禁用 |
| `HEAD` | 只要响应头，不要 Body | 探测文件是否存在，比 GET 快 |
| `OPTIONS` | 询问服务器支持哪些方法 | 响应的 `Allow` 头会暴露可用的方法，信息收集时常用 |

一个典型考法：题目对 GET/POST 做了过滤，但代码里用了 `$_REQUEST` 或允许其他方法，换成 `PUT` 或 `X-HTTP-Method-Override` 头就能绕过。遇到"方法被拦"的 405 响应，先 `OPTIONS` 一下看看还支持什么。

## 常见 Header 的 CTF 考点

这一节是全章最"应试"的部分，每个 Header 配一个最小示例。

### Host

同一台服务器托管多个站点时，靠 Host 头区分。考点：

- 越权访问内部 vhost：`Host: admin.internal`，配合 SSRF 章节食用。
- 密码重置投毒：重置链接的域名取自 Host 头，改成攻击者域名可劫持 token。

### User-Agent

服务器靠 UA 判断客户端类型。最经典的入门题：

> "请使用 HAHA 浏览器访问本站"

在 Burp Repeater 或 curl 里改一行即可：

```bash
curl -v 'http://challenge.example.com/' -A 'HAHA Browser 1.0'
```

另一种考法：页面只把 flag 回显给搜索引擎爬虫，UA 改成 `Baiduspider` 或 `Googlebot` 即可。还有一种进阶考法是把 UA 原样写进日志或页面，造成 UA 头注入（XSS 或 SQL注入），思路见对应章节。

### Referer

表示请求来源页面。经典考点：

> "本页面只允许从 index.php 跳转访问"

```bash
curl -v 'http://challenge.example.com/secret.php' \
  -H 'Referer: http://challenge.example.com/index.php'
```

Referer 是客户端发的，**任何"基于 Referer 的访问控制"都等于没有控制**——这也是 逻辑漏洞 章节反复强调的一点。

### X-Forwarded-For（XFF）

反向代理会把真实客户端 IP 写进 `X-Forwarded-For` 头。如果后端用 `$_SERVER['HTTP_X_FORWARDED_FOR']` 取 IP 来做限制（比如"仅允许本地访问"），直接伪造：

```bash
curl -v 'http://challenge.example.com/admin.php' \
  -H 'X-Forwarded-For: 127.0.0.1'
```

同类头还有 `X-Real-IP`、`X-Client-IP`、`Client-IP`，一个不行就换着试。更隐蔽的写法是 `127.0.0.1` 的变形（如 `127.1`），取决于后端解析方式。

### Content-Type

决定服务器如何解析 Body，考点集中在三处：

1. **文件上传绕过**：上传 PHP 时把 `Content-Type` 从 `application/octet-stream` 改成 `image/png`，骗过只校验头的代码，详见 文件上传 章节。
2. **XXE 触发**：把 `Content-Type` 改成 `application/xml` 并提交 XML Body，见 XXE注入 章节。
3. **PHP 解析差异**：`application/json` 的 Body 要用 `file_get_contents('php://input')` 读取，不少"提交了参数却没效果"的疑惑都源于此。

### 其他值得记住的

- `Accept` / `Accept-Language`：偶尔有题要求"请使用某国语言"，改 `Accept-Language: en-US`。
- `Authorization`：HTTP Basic Auth 用，格式是 `Basic base64(user:pass)`，弱口令爆破的对象。
- `Origin`：CORS 相关，部分逻辑漏洞题会考 Origin 校验缺失。

## Cookie 与 Session（传输层面）

这一节只讲"Cookie 是怎么在网线上跑的"，认证逻辑的安全问题（伪造、篡改、会话固定等）留给「会话与认证安全」章节。

### Cookie 的一生

Cookie 是服务器通过响应头 **下发**、浏览器在后续请求中 **自动带回** 的一小段键值对：

服务器下发：

```http
HTTP/1.1 200 OK
Set-Cookie: PHPSESSID=a1b2c3d4e5f6; Path=/; HttpOnly
```

浏览器之后每个请求都会带上：

```http
GET /profile.php HTTP/1.1
Host: challenge.example.com
Cookie: PHPSESSID=a1b2c3d4e5f6
```

要点就三个：

- Cookie 存在 **客户端**，所以客户端可以任意查看和修改——`role=guest` 改成 `role=admin` 就是这么来的。
- `Set-Cookie` 的常用属性：`Path`（生效路径）、`HttpOnly`（禁止 JS 读取，防 XSS 偷 Cookie）、`Secure`（仅 HTTPS 传输）。
- 在 Burp 里直接改请求头的 `Cookie` 值，是 Web 题最高频的操作之一。

### Session 是什么

Session 数据存在 **服务器端**，客户端只拿一个编号（Session ID，通常通过 `PHPSESSID` 之类的 Cookie 携带）。服务器收到请求后，拿 ID 去查对应的会话数据，从而知道"你是谁"。

用一句话区分：**Cookie 是"数据放在你手里"，Session 是"数据放在服务器、你只拿钥匙"**。所以 `role=admin` 这种明文 Cookie 可以直接改，而 Session 只能寄希望于预测 Session ID 或服务端逻辑缺陷。

### 最小实验

用 curl 观察一次完整的会话建立过程：

```bash
# 第一次请求：-c 保存服务器下发的 Cookie 到文件
curl -v -c cookies.txt 'http://challenge.example.com/login.php' \
  -d 'username=admin&password=123456'

# 后续请求：-b 带上保存的 Cookie
curl -v -b cookies.txt 'http://challenge.example.com/profile.php'
```

注意第一次请求响应里的 `Set-Cookie`，和第二次请求里的 `Cookie`——这就是会话在传输层面的全部真相。

## HTTPS 与证书抓包

HTTPS = HTTP + TLS，报文内容与明文 HTTP **完全一样**，只是套了一层加密。所以本章讲的所有内容对 HTTPS 同样适用，区别只在于抓包环节。

### 为什么 HTTPS 抓不到明文

Burp 是中间人代理：浏览器把加密流量发给 Burp，Burp 解密后再用自己的证书加密发给服务器（反之亦然）。浏览器默认不信任 Burp 自签的 CA 证书，会报"证书不受信任"，这就是 HTTPS 站点在 Burp 下抓不到/报错的原因。

### 让 Burp 能抓 HTTPS

三步即可：

1. 浏览器代理指向 Burp（`127.0.0.1:8080`）后，访问 `http://burp` 或 `http://127.0.0.1:8080/cert`，下载 CA 证书 `cacert.der`。
2. 把证书导入浏览器（Firefox：设置 → 隐私与安全 → 查看证书 → 导入，并勾选"信任由此证书颁发机构标识的网站"）。
3. 重新访问 HTTPS 站点，Burp 里即可看到明文。

命令行场景更简单，`curl -k` 直接跳过证书校验：

```bash
curl -kv 'https://challenge.example.com/' -x http://127.0.0.1:8080
```

其中 `-x` 指定走 Burp 代理。做题时 `-k` 几乎是必加参数，因为很多靶机用的是自签证书。

## 例题：一道经典的 Header 综合题

用一个虚构但极具代表性的入门题，把本章内容串起来走完一遍完整流程。

> 题目：访问 `http://challenge.example.com:8080/`，页面显示：
> "只有使用 HAHA 浏览器，并且从 index.html 跳转过来说"我是内网用户"的人，才能获得 flag。"

### 第一步：抓包看原始请求

正常访问，Burp 里抓到：

```http
GET / HTTP/1.1
Host: challenge.example.com:8080
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
Accept: text/html
```

响应 `200 OK`，页面提示条件不满足。三个线索逐一拆解：

- "HAHA 浏览器" → 改 `User-Agent`
- "从 index.html 跳转过来" → 改 `Referer`
- "我是内网用户" → 伪造来源 IP，改 `X-Forwarded-For`

### 第二步：逐个条件尝试

先在 Burp Repeater 里只改 UA：

```http
GET / HTTP/1.1
Host: challenge.example.com:8080
User-Agent: HAHA Browser
```

页面提示变成"浏览器对了，但你不是从 index.html 来的"——逐条提示是这类题的常见设计，照着提示加 Header 即可。加上 Referer：

```http
Referer: http://challenge.example.com:8080/index.html
```

提示再变成"你不是内网用户"。加上 XFF：

```http
X-Forwarded-For: 127.0.0.1
```

页面回显 `flag{http_header_m4ster}`，解题完成。

### 第三步：用 curl 一把梭

脱离 Burp，一条命令也能做完：

```bash
curl -v 'http://challenge.example.com:8080/' \
  -A 'HAHA Browser' \
  -H 'Referer: http://challenge.example.com:8080/index.html' \
  -H 'X-Forwarded-For: 127.0.0.1'
```

### 小结

这类题的全部套路就是：**读提示 → 定位对应的 Header → 改包重发**。真正的难点从来不在改包本身，而在于你能认出每个提示对应 HTTP 协议里的哪个字段——这正是本章存在的意义。同类型的题目可以在 Web入门题单 里找到大量练习。
