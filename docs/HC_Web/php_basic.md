---
comments: true
---

# PHP 基础

在指导Web方向入门时，我们常说要有一点PHP基础，很对新生会对此疑惑 —— 什么程度的基础。
因为CTF或者说安全并不是要求你做开发工作，而是审计工作，你不需要完全学习一门语言之后再去处理工作，这没有太大意义。

本节内容将介绍在CTF比赛中涉及的 PHP 基础语法内容，当然因为篇幅原因，不会太过详细，读者需要结合内容自行在做题的基础上扩展。

### PHP基础格式

PHP 脚本以 **<?php** 开始，以 **?>** 结束：

```php
<?php
    //执行的相关PHP代码
?>
```

### 变量 赋值 以及 运算

PHP 中，变量以 **$** 符号开始，后面跟着变量的名称，并且变量名是区分大小写的（\$y 和 $Y 是两个不同的变量）

要注意的是 PHP 是一门弱类型语言，我们不必向 PHP 声明该变量的数据类型。

```php
<?php
$x_int = 1024;
$y_int = 0xFFF;
$float_num = 1.5;
$txt_string = "Hello CTF!";
$stat_Boolean = true;
?>
```

**赋值 以及 复合赋值**

| 运算符 | 等同于    | 描述                           |
| :----- | :-------- | :----------------------------- |
| x = y  | x = y     | 左操作数被设置为右侧表达式的值 |
| x ?= y | x = x ? y | 支持 `+=`, `-=`, `*=`, `/=`, `%=`,`.=`  |

**逻辑运算**

| 运算符 | 名称             | 描述                                                         |
| :----- | :--------------- | :----------------------------------------------------------- |
| x `and` / `&&` y  | 与   | 如果 x 和 y 都为 true，则返回 true           |
| x `or` / `||`  y   | 或   | 如果 x 和 y 至少有一个为 true，则返回 true   |
| x xor y  | 异或 | 如果 x 和 y 有且仅有一个为 true，则返回 true |
| ! x      | 非   | 如果 x 不为 true，则返回 true                |

### 类型比较

- 松散比较：使用两个等号 **==** 比较，只比较值，不比较类型。
- 严格比较：用三个等号 **===** 比较，除了比较值，也比较类型。

```php
0 == false: bool(true)
0 === false: bool(false)
```

### 输出

- `echo` - 可以输出一个或多个字符串
- `print` - 只允许输出一个字符串，返回值总为 1

```php
<?php
echo "Hello CTF 很有趣！";
?>
```

### 数组

**`array()` 函数用于创建数组**

```php
<?php
$cars=array("Hello","CTF");
echo "I like " . $cars[0] . " " . $cars[1] . ".";
?>
```

**使用 `[]` 定义数组**

```php
$z = ['H','e','l', 'l', 'o'];
$z[0] = 'H';
$z[1] = 'r';
$z[2] = 'l';
$z[3] = 'l';
$z[4] = 'o';
```

### 魔术常量

行如 **`__FILE__` ** 这样的 `__XXX__`  预定义常量，被称为魔术常量。

```php
__FILE__ //返回文件的完整路径和文件名
    
highlight_file(__FILE__); //代码高亮的显示当前文件内容
```

### 表单数据

**$_GET** —— 接受 GET 请求传递的参数。

**示例**：`example.com/index.php?book=HELLOCTF`，你可以使用 `$_GET['book']` 来获取相应的值。

**$_POST** —— 接受 POST 请求传递的参数。

**示例**：对 `example.com/index.php` 进行 POST 传参，参数名为 `book` 内容为 `HelloCTF`，你可以使用 `$_POST['book']` 来获取相应的值。

**$_REQUEST** —— 接受 GET 和 POST 以及 Cookie 请求传递的参数。

**示例**：

- 如果你通过 URL 传递了一个参数 `example.com/index.php?key=value_from_get`，你可以通过 `$_REQUEST['key']` 获取这个值。
- 如果你通过 POST 方法提交了一个表单，其中有一个名为 `key` 的字段且其值为 `value_from_post`，你也可以通过 `$_REQUEST['key']` 获取这个值。
- 同时，如果你设置了一个名为 `key` 的 cookie，其值为 `value_from_cookie`，你还是可以使用 `$_REQUEST['key']` 来获取这个值。

### 内建函数

**文件操作函数**：

- `include()`: 导入并执行指定的 PHP 文件。例如：`include('config.php');` 会导入并执行 `config.php` 文件中的代码。

- `require()`: 类似于 `include()`，但如果文件不存在，则会产生致命错误。

- `include_once()`, `require_once()`: 与 `include` 和 `require` 类似，但只导入文件一次。

- `fopen()`: 打开一个文件或 URL。例如：`$file = fopen("test.txt", "r");` 会以只读模式打开 `test.txt`。

- `file_get_contents()`: 读取文件的全部内容到一个字符串。例如：`$content = file_get_contents("test.txt");`

- `file_put_contents()`: 将一个字符串写入文件。例如：`file_put_contents("test.txt", "Hello World!");`

**代码执行函数**：

- `eval()`: 执行字符串中的 PHP 代码。例如：`eval('$x = 5;');` 会设置变量 `$x` 的值为 5。

- `assert()`: 用于调试，检查一个条件是否为 true。

- `system()`, `shell_exec()`, `exec()`, `passthru()`: 执行外部程序或系统命令。例如：`system("ls");` 会执行 `ls` 命令并显示输出。

**反序列化函数**：

- `unserialize()`: 将一个已序列化的字符串转换回 PHP 的值。例如：`$array = unserialize($serializedStr);` 可以将一个序列化的数组字符串转换为数组。

**数据库操作函数**：

- `mysql_query()`, `mysqli_query()`: 发送一个 MySQL 查询。例如：`$result = mysql_query("SELECT * FROM users");`

**其他函数**：

- `preg_replace()`: 执行正则表达式搜索和替换。例如：`$newStr = preg_replace("/apple/i", "orange", $str);` 会将 `$str` 中的 "apple" 替换为 "orange"。

- `create_function()`: 创建匿名的 lambda 函数。例如：`$func = create_function('$x', 'return $x + 1;');`

