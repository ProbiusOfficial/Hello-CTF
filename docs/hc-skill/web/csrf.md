---
comments: true
---

# CSRF

> WEB · 知识域。跨站请求伪造:借受害者浏览器身份发起状态变更请求。标签:**基本利用**、**JSONP**。

## 触发特征

- 题目要求"让 admin/bot 完成某操作"(改密码、转账、点赞)。
- 状态变更接口仅靠 Cookie 鉴权、无 CSRF token 或 token 可预测。

## 基本利用

- 自动提交表单:`<form method=POST action=...><input name=...><script>document.forms[0].submit()</script>`。
- CORS 放宽(`Access-Control-Allow-Origin: *` + credentials 配置矛盾)时直接 fetch。
- SameSite 时代:Lax 默认下 GET 型跨站仍可;`None` + Secure 场景找子域漏洞借同站性。
- 子域接管:接管废弃 CNAME 后在同站内发请求(见 [HTTP请求](http-request.md))。
- GraphQL CSRF:CSRF 双提交缺陷 + 图片加载时序逐字符读响应(HTB GrandMonty);introspection 泄露变更字段。

## JSONP

- JSONP 端点本质是"第三方可执行回调"→ 既是 XSSI 数据泄露源,也是 CSRF 载体。
- 泄露:受害者浏览器带 Cookie 请求 JSONP 端点,回调把敏感数据发到攻击者域(BSidesSF 2026:JSONP 回调 + Cloud Function 外带)。
- 回调函数名注入:`?callback=<script>alert(1)</script>` → XSS 跳板。
- 现代替代品:CORS 反射、postMessage 监听(`*` targetOrigin)滥用、`Vary` 缺失导致的缓存型泄露。

## OAuth/会话类 CSRF

- OAuth `state` 参数缺失 → 授权码注入绑定攻击者账号(OIDC ID token 操纵同理,见 [认证绕过](auth-bypass.md))。
- 登录 CSRF:诱使受害者用攻击者会话登录。
- WebSocket 无 origin 校验 → 跨站 WebSocket 劫持(批量篡改游戏状态类题目)。

## 检查清单

1. 鉴权靠什么:Cookie(自动携带,CSRF 可行)、Header token(需先泄露)。
2. token 是否绑定会话、是否校验 Origin/Referer。
3. 是否有"无副作用转副作用"的 GET 接口。

## 转向

- payload 触发后需要浏览器执行 → [XSS](xss.md);第三方基础设施探查 → [信息搜集](info-gathering.md)
