---
comments: true
---

# 逻辑漏洞

> WEB · 知识域。不依赖"注入"的纯业务逻辑缺陷:让程序在非法状态下接受操作。标签:**权限控制绕过**、**业务逻辑漏洞**、**数据校验绕过**。

## 触发特征

- 题面描述"管理员才能做X""只有一次机会""金额不能为负"。
- 无明显注入点,功能流程长(注册→验证→重置→支付)。

## 权限控制绕过

- **水平越权(IDOR)**:改 `uid/order_id/file_id` 遍历他人资源;未认证的 WIP 端点直接访问(srdnlenCTF 2026)。
- **垂直越权**:普通用户请求管理员接口;前端隐藏 ≠ 服务端校验。
- 隐藏端点:从 JS 路由表、API 文档(`/swagger`、`/api-docs`、GraphQL introspection)发现。
- 竞态(TOCTOU):签到/转账/次数限制,高并发击穿 check-then-act 窗口(Turbo Intruder / `asyncio` 并发)。
- 代理信任:信任 `X-Forwarded-For` 判断内网管理员;`HAProxy`/中间件 ACL 绕过(→ [HTTP请求](http-request.md))。

## 业务逻辑漏洞

- **支付/数量**:负数、超大数、精度(float 精度丢失)、小数截断、重复退款;`int` 溢出(`2^31`、`int8` 截断)。
- **状态机跳过**:未支付直接访问完成回调;验证码先校验后置空;密码重置流程 token 可预测(`uniqid()`、时间戳种子,→ [Crypto-MT19937](../crypto/mt19937.md))。
- **批量操作**:GraphQL aliasing 一次改多个;WebSocket mass assignment 批量改字段。
- **兑换/邀请**:邀请码哈希可碰撞、并发重复兑换。
- **到期/限次**:服务端只比时间字符串;cookie 检查点回滚(BYPASS CTF 2025 游戏型)。

## 数据校验绕过

- 类型混淆:数组/字符串双重身份(PHP `a[]=1`,JSON `{"id":[1]}`)、SQL 数组注入(→ [NoSQL注入](nosql.md))。
- 长度截断:数据库列截断注册变体用户(VolgaCTF 2014,→ [SQL注入](sql-injection.md));超长截断绕后缀判断。
- 编码不一致:前后端解码次数不同(`%252e` 双重编码)、Unicode 同形字符、`parse_url` 与下游解析分歧。
- mass assignment:接口接受未声明的 `{"isAdmin":true}`、`{"price":0}` 字段直接生效。
- 校验在前端:响应包改字段、hash 校验可重算、签名密钥泄露(→ [JS](js.md))。

## 检查清单

1. 画出完整业务流:注册 → 登录 → 重置 → 支付 → 兑换。
2. 每步标记:鉴权对象、校验字段、状态存储位置(session/DB/cache)。
3. 对每个校验问三句:服务端做没有?并发安全吗?类型/编码一致吗?

## 转向

- 越权拿到管理功能后 → 各类注入/上传技能;竞态属于并发类通病 → [Pwn-逻辑漏洞](../pwn/logic-vuln.md)
