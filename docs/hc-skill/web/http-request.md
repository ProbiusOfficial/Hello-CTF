---
comments: true
---

# HTTP请求

> WEB · 知识域。HTTP 协议层攻防:请求头伪造、响应分析、解析器分歧利用。标签:**来源头伪造**、**UA头伪造**、**返回头分析**、**返回内容分析**、**请求伪造**。

## 触发特征

- 服务端按 IP/来源/UA 做访问控制或内容区分。
- 前置代理/CDN + 后端应用的双层结构(走私、缓存投毒)。
- 报错页、响应头、响应时延本身是信息源。

## 来源头伪造

- 校验链优先级(框架各异,逐个试):`Client-IP` → `X-Forwarded-For` → `X-Real-IP` → `Referer`。
- 取第一个还是最后一个 IP 决定注入位置;`X-Forwarded-For` 进入日志/XML 时可注入 CRLF 或实体(Pwn2Win 2016:该头注入 XML)。
- 本地校验绕过:`127.0.0.1`、`localhost`、内网段、`Host: localhost`。

## UA头伪造

- UA 门禁:`robots.txt` 按 UA 返回不同内容(TAMUctf 2019);Googlebot/baiduspider UA 解锁隐藏路径。
- UA 参与模板渲染 → SSTI;进入日志 → 日志投毒(见 [文件上传](file-upload.md) 的日志包含)。

## 返回头分析

- `Server`/`X-Powered-By` 版本号 → 匹配 N-Day(CVE 清单思路:Next.js 中间件绕过 CVE-2025-29927、Apache HttpOnly 泄露 CVE-2012-0053)。
- `Set-Cookie` 结构泄露序列化格式(Flask-itsdangerous、Laravel-encrypted、PHP-session)。
- `Location`/`Refresh` 跳转链挖开放重定向与 token 传递。

## 返回内容分析

- 时间差 oracle:SQLite `randomblob()` 盲注(SECCON 2017)、盲 SQLi 经脚本引擎超时报错(35C3 2018)。
- 报错页回显:Flask debug PIN 计算、Werkzeug 控制台;`/proc/self/mem` 经 HTTP Range 读取(UTCTF 2024)。
- 前端混淆解码:JSFuck、AAEncode、JJEncode(0xFun 2026)。

## 请求伪造与解析分歧

- **请求走私**:CL-TE/TE-CL 差异;走私 + 缓存代理组合投毒(CSAW 2018:`X-Forwarded-Host` 控制 CDN 模板拉取)。
- **HTTP TRACE**:开启时回显请求头,绕过 `HttpOnly` 读 Cookie(BYPASS CTF 2025)。
- **中间件 ACL 绕过**:HAProxy 正则缺陷(EHAX 2026)、Express `%2F` 路径绕过(srdnlenCTF 2026)、多斜杠 `path.startswith` 前缀绕过(CSAW 2018 Finals)。
- **URL 解析分歧**:代理与后端对 `@`、`//`、`%2f` 处理不一致 → SSRF(33C3 2016:parse_url 与 curl 双 `@` 分歧)。
- 协议复用:同端口 SSH+HTTP 识别(0xFun 2026);TCP 分包绕过防火墙特征。

## 工具速查

```bash
curl -v -H "X-Forwarded-For: 127.0.0.1" -H "UA: Googlebot" URL
# Burp Repeater 手工走私;Turbo Intruder 并发竞态
```

## 转向

- 头注入最终指向内网 → [SSRF](ssrf.md)
- 走私用于劫持 admin bot → [XSS](xss.md)
