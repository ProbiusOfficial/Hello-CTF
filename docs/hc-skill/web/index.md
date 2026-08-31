---
comments: true
---

# WEB - Web安全

> 方向技能索引。目标以 HTTP 应用、API、浏览器客户端、模板引擎、身份认证流为主界面时,从本索引路由到对应知识域技能。不要用于:原生二进制内存破坏(转 [Pwn](../pwn/index.md))、独立可执行文件逆向(转 [Reverse](../reverse/index.md))、纯密码分析(转 [Crypto](../crypto/index.md))、磁盘/内存取证(转 [Misc](../misc/index.md))。

## 知识域路由表

| 知识域 | 技能文件 | 触发特征 |
| --- | --- | --- |
| 信息搜集 | [info-gathering](info-gathering.md) | 需要侦察:目录、子域、备份、源码、指纹 |
| HTTP请求 | [http-request](http-request.md) | 协议层考点:头伪造、走私、缓存投毒、解析差异 |
| 暴力破解 | [brute-force](brute-force.md) | 存在可枚举的口令/token/验证码 |
| 文件泄露 | [file-leak](file-leak.md) | `.git`/备份/`.env` 暴露在 Web 根 |
| SQL注入 | [sql-injection](sql-injection.md) | 报错、回显异常、过滤绕过类数据库交互 |
| NoSQL注入 | [nosql](nosql.md) | MongoDB/Redis/ArangoDB 等非关系型后端 |
| XSS | [xss](xss.md) | 有 admin bot / 富文本渲染 / DOM 操作 |
| CSRF | [csrf](csrf.md) | 状态变更操作无防护、JSONP、GraphQL |
| XXE | [xxe](xxe.md) | XML/Office/SVG 解析入口 |
| SSRF | [ssrf](ssrf.md) | 服务端可指定 URL:webhook、导入、内网探测 |
| 文件上传 | [file-upload](file-upload.md) | 上传入口,考扩展名/内容/解析绕过 |
| 逻辑漏洞 | [logic-vuln](logic-vuln.md) | 越权、IDOR、条件竞争、业务状态机 |
| 认证绕过 | [auth-bypass](auth-bypass.md) | JWT/Cookie/OAuth/SAML/会话伪造 |
| 语言专题 | [js](js.md) [php](php.md) [python](python.md) [java](java.md) [node](node.md) [ruby](ruby.md) [go](go.md) | 指纹识别出对应语言栈后加载 |
| Windows相关 | [windows](windows.md) | IIS/Aspx/NTFS/域环境 |

## 通用起手流程

1. 判定信任边界:纯前端、纯后端、混合应用还是认证流。
2. 每个主要功能先抓一对正常请求/响应,再开始 fuzz。
3. 从 JS bundle、响应头、路由、HTTP 方法枚举隐藏功能。
4. 给 bug 归类:注入 / 越权 / 解析器分歧 / 上传 / 代理信任 / 状态机 / 客户端执行。
5. 先构造最小原语(泄露一个文件、伪造一个 token、触发一次 bot 访问),再考虑完整利用链。

## 常见利用链形态

- 侦察 → 隐藏路由 → 越权 → 内部文件读取 → token/flag
- XSS/HTML 注入 → admin bot → 特权操作 → 秘密泄露
- 穿越/上传 → 配置或源码泄露 → key 恢复 → 会话伪造
- SSRF → metadata 或内网 API → 凭据泄露 → RCE
- SQLi/NoSQLi → 登录绕过 → 二阶段模板或上传利用

## 常见 flag 位置

- 文件:`/flag.txt`、`/flag`、`/app/flag.txt`、`/home/*/flag*`
- 环境:`/proc/self/environ`、进程命令行、调试配置导出
- 数据库:`flag`、`secret` 表或种子数据
- HTTP:自定义头、归档响应、隐藏路由、管理员导出
- 浏览器:隐藏 DOM、`data-*` 属性、内联状态对象、source map
