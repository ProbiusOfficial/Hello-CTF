---
comments: true
---

# PHP特性与常见绕过

在 Web 方向的 CTF 题目里，PHP 是出现频率最高的语言。出题人特别喜欢利用 PHP 语言本身的"特性"（或者说历史遗留的坑）来设置考点：弱类型比较、魔术哈希、变量覆盖、伪协议……这些特性本身并不复杂，但如果不了解，审计代码时完全看不出漏洞在哪。

本章把这些高频特性体系化地过一遍，每一节都遵循「原理 → 最小示例 → 典型 bypass 思路」的结构。后续章节如 SQL 注入绕过、RCE、WAF 绕过、文件包含 中涉及的特性，基本都能在本章找到出处。阅读前建议先过一遍 PHP基础。

## 弱类型比较

### `==` 与 `===`

PHP 有两种比较：

- `==`（松散比较）：只比较值，比较前会自动做类型转换；
- `===`（严格比较）：同时比较类型和值。

漏洞几乎都出在 `==` 的类型转换上。核心规则是：**当字符串与数字比较时，字符串会被强制转换成数字**（PHP 8 之前）。转换方式是取字符串开头最长的一串合法数字，如果开头不是数字，结果就是 `0`。

```php
<?php
var_dump(0 == "a");        // PHP 7: true  ("a" 转成 0)
var_dump("1" == "01");     // true  (都转成 1)
var_dump("10" == "1e1");   // true  (10 == 10.0)
var_dump(100 == "1e2");    // true  (100 == 100.0)
var_dump("abc" == 0);      // PHP 7: true; PHP 8: false
var_dump(null == false);   // true
?>
```

注意 PHP 8 修改了字符串与数字比较的规则：`0 == "a"` 在 PHP 8 中已经是 `false`。做题时先看题目环境的 PHP 版本，很多老题在新环境下根本复现不出来。

**典型 bypass**：题目用 `if ($_GET['a'] == 0)` 判断，直接传 `?a=abc` 即可让条件成立（PHP 7 下）。

### 0e 开头 MD5 碰撞（魔术哈希）

这是 `==` 比较最经典的应用。MD5 哈希是 32 位十六进制字符串，如果两个不同字符串的 MD5 值都满足「以 `0e` 开头、后面全是数字」，那么按上面 `1e2 == 100` 的规则，它们在 `==` 比较时都会被当成科学计数法的 `0`，于是相等：

```php
<?php
$a = md5("QNKCDZO");   // 0e830400451993494058024219903391
$b = md5("240610708"); // 0e462097431906509019562988736854
var_dump($a == $b);    // true
var_dump($a === $b);   // false
?>
```

常用 payload（MD5 为 `0e` 开头的字符串）：`QNKCDZO`、`240610708`、`s878926199a`、`s155964671a`、`s214587387a`。

如果题目比较的是 `md5($a) == md5($b)` 且要求 `$a != $b`，就用两个不同的 `0e` 字符串；如果用的是 `===`，就得换思路——数组绕过或真实 MD5 碰撞（fastcoll 工具生成），后者在 PHP代码审计 章节还有展开。

### 数组绕过

`md5()`、`sha1()`、`strcmp()` 等函数参数预期是字符串，传入数组会返回 `null` 并抛出 warning。两个 `null` 用 `==` 或 `===` 比较都是 `true`：

```php
<?php
var_dump(md5([]) === md5([]));  // true（PHP 7 下，函数返回 null）
var_dump(strcmp([], []) === 0); // true
?>
```

**典型 bypass**：

```http
GET /?a[]=1&b[]=2 HTTP/1.1
```

当题目用 `md5($a) === md5($b)` 比较且 `0e` 被卡掉时，传数组是最常用的解法。同理，`strcasecmp`、`strpos`、`strlen` 等参数为字符串的函数都可以这样"打数组"。

### strcmp 与 in_array 的漏洞

`strcmp($a, $b)` 在两者相等时返回 `0`。如果题目写成：

```php
<?php
if (strcmp($_GET['pass'], $flag) == 0) {
    echo $flag;
}
?>
```

直接传 `pass[]=1`，`strcmp` 返回 `null`，而 `null == 0` 为 `true`，绕过成功。

`in_array($needle, $haystack)` 默认是松散比较，第三个参数不传 `true` 就不会检查类型：

```php
<?php
var_dump(in_array("1abc", [0, 1, 2]));  // true！"1abc" 转成 1
var_dump(in_array("abc",  [0, 1, 2]));  // true！转成 0，在数组里
?>
```

文件上传白名单校验用 `in_array` 而没有加严格模式时，传 `0abc.php` 之类的文件名就可能绕过，这在 文件上传 章节还会用到。

### switch 与 intval 的坑

`switch` 语句的 case 比较使用的是 `==` 松散比较：

```php
<?php
$i = "2abc";
switch ($i) {
    case 0: case 1: case 2:
        echo "hit";   // 会命中 case 2
        break;
}
?>
```

`intval()` 只取字符串开头的数字部分，且第二个参数是进制：

```php
<?php
var_dump(intval("1024abc"));     // 1024
var_dump(intval("0x1A", 16));    // 26
var_dump(intval("0x1A", 0));     // 26，base=0 时自动识别进制
var_dump(intval("42", 8));       // 34，按八进制解析
?>
```

典型考法：`if (intval($num) == 1024 && $num !== "1024")`，答案就是传 `1024abc` 或者 `1024e0`。这类"既要==又要!="的题目，第一反应就是利用类型转换。

## PHP 自增特性与字母数字绕过

PHP 中字符串变量可以自增，且遵循 Perl 风格而不是 C 风格：只处理字母数字，到达 `z`/`Z` 后向高位进位，**永远不会变成数字类型**：

```php
<?php
$a = "a"; $a++;        // "b"
$b = "z"; $b++;        // "aa"
$c = "Az"; $c++;       // "Ba"
$d = "Zz"; $d++;       // "AAa"
?>
```

减法则没有这个效果（`$a--` 对纯字母字符串不生效）。利用自增，我们可以在 **不允许使用任何字母数字**（正则 `/\W/` 级别的过滤）的环境下构造出任意函数名：

```php
<?php
$_ = [];
$_ = @"$_";          // "Array"，数组转字符串
$_ = $_['!' == '@']; // "A"（'!'=='@' 为 false 即 0，取下标 0）
$__ = $_; $__++; $__++; $__++;  // "D"
// 不断 ++ 并拼接，就能得到 "_GET"、"_POST"、"system" 等
?>
```

**典型 bypass 思路**：题目过滤了所有字母数字，只允许 `$_++();` 之类的符号组合时，用自增从 `"Array"` 出发拼出 `_GET`，再通过 `$_=${_GET}[_];$_();` 执行任意函数。这类题在 RCE 章节的"无字母数字 RCE"部分会系统展开，本章只需要理解自增原理。

## 闭合标签与短标签

PHP 代码块的标准写法是 `<?php ... ?>`，但还有几种变体：

- `<?= ... ?>`：短输出标签，等价于 `<?php echo ... ?>`，**始终可用**，不受 `short_open_tag` 配置影响；
- `<? ... ?>`：短标签，需要 php.ini 中 `short_open_tag=On`；
- `<% ... %>`：ASP 风格标签，需要 `asp_tags=On`，PHP 7 已移除。

两个考点：

**文件尾部的 `?>` 可以省略**，而且官方推荐省略——如果文件结尾有 `?>`，后面多出来的换行或空格会被当作输出内容，可能造成 `header()` 之类的函数报错。反过来说，在文件上传题目中，如果题目把过滤逻辑写成"在文件末尾追加内容"，可以故意利用闭合标签让追加的内容落到 PHP 代码块外。

**`.htaccess` / `user.ini` 配合短标签**：当上传点过滤了 `<?` 但允许 `=` 开头时，`<?=` 组合不含完整 `<?` 的情况曾用于绕过某些弱正则。更常见的是：过滤 `<?` 时用 `<script language="php">...</script>`（PHP 7 已移除）或短标签绕。

## 可变变量与变量覆盖

### 可变变量 `$$`

PHP 允许用变量的值作为变量名：

```php
<?php
$a = "hello";
$$a = "world";       // 等价于 $hello = "world";
echo $hello;         // world
echo "$a ${$a}";     // hello world
?>
```

几个高频考点：

- `$$a` 与 `${$a}` 等价；
- `${$_GET[1]}` 可以动态取变量，`$${$_GET[1]}` 则可以动态覆盖任意变量；
- 特殊全局变量如 `$GLOBALS` 不能被 `$$` 覆盖。

**经典例题**：

```php
<?php
error_reporting(0);
include "flag.php";  // $flag = "flag{...}";
$highlight_file = "index.php";
if (isset($_GET['a'])) {
    $a = $_GET['a'];
    $a = str_replace("flag", "????", $a);  // 过滤 flag
    $$a = $highlight_file;
    echo $$a;
}
?>
```

`str_replace` 过滤了 `flag` 字符串，没法直接覆盖 `$flag`。但 `${$a}` 能读任意变量：传 `?a=GLOBALS`，`$$a` 即 `$GLOBALS`，随后 `echo $GLOBALS` 会 dump 出所有变量包括 `$flag`。这是"过滤了变量名字符串但没过滤变量本身"的标准解法。

### extract()

`extract()` 把数组的键值导入为变量，默认会 **覆盖同名变量**：

```php
<?php
$flag = "flag{real_flag}";
extract($_GET);
if ($flag == "givemeflag") {   // 已被 GET 参数覆盖
    echo $flag;
}
?>
```

传 `?flag=givemeflag` 即绕过。还可以利用 `EXTR_SKIP` 之外的标记控制行为，但 CTF 中默认模式（`EXTR_OVERWRITE`）最常见。另一个考点是 `extract($_POST)` 后判断两个变量相等，此时同时覆盖两个变量即可。

### parse_str()

`parse_str($str, $result)` 解析 URL 查询字符串。如果 **省略第二个参数**，解析结果会直接注入当前作用域，效果等同 `extract`：

```php
<?php
$flag = "flag{xxx}";
parse_str($_SERVER['QUERY_STRING']);  // 危险用法
if ($flag == "1") echo "ok";
?>
```

传 `?flag=1` 即可。另外 `parse_str` 会把变量名中的 `.` 和空格替换成 `_`，某些题目会反过来利用这一点绕过对特定参数名的过滤。

### 变量覆盖防护结论

审计时看到 `extract($_GET)`、无第二参数的 `parse_str()`、`$$` 直接拼接用户输入、以及 `foreach ($_GET as $k => $v) { $$k = $v; }` 这种注册全局变量的老代码，基本就是考点所在。

## 伪协议总览

PHP 的 stream wrapper（伪协议）允许把文件操作函数（`file_get_contents`、`include`、`fopen`、`readfile` 等）的目标从本地文件扩展到各种特殊来源。这是 文件包含、任意文件读取、SSRF注入 等章节的共同基础，这里先建立总览，文件包含场景下的深入利用留在对应章节。

常用伪协议一览：

| 协议 | 作用 | 依赖配置 |
| :--- | :--- | :--- |
| `php://filter` | 读写时对数据流做过滤/编码 | 无 |
| `php://input` | 读取 POST 原始请求体 | `allow_url_include`（include 时） |
| `php://stdin` / `php://stdout` | 标准输入输出流 | 无 |
| `data://` | 把内联数据当文件读 | `allow_url_fopen` + `allow_url_include` |
| `file://` | 访问本地文件（绝对路径） | 无 |
| `phar://` | 访问 phar 归档内文件，可触发反序列化 | 无 |
| `zip://` / `compress.bzip2://` 等 | 访问压缩包内文件 | 对应扩展 |
| `glob://` | 目录匹配（不支持远程） | 无 |

### php://filter

读文件场景最常用的协议，可以把源码先 Base64 编码再读出来，从而拿到 `.php` 源码而不执行：

```php
<?php
$src = file_get_contents("php://filter/read=convert.base64-encode/resource=flag.php");
echo $src;  // flag.php 源码的 Base64，解码即得源码
?>
```

也可以链式叠加多个过滤器，如 `convert.base64-encode|string.rot13|convert.base64-encode`。在"读文件但会 die 掉内容"的题目里，常用过滤器链把 flag 内容破坏成无法触发 die 的形式再读出来。进阶玩法（利用编码转换爆破出任意前缀的 `convert.iconv.*` 链）属于文件包含章节的内容。

### php://input

配合 `include` 时可以直接执行 POST 体中的 PHP 代码：

```http
POST /index.php?file=php://input HTTP/1.1
Content-Type: application/x-www-form-urlencoded

<?php phpinfo(); ?>
```

读文件函数下它返回 POST 原始数据，可以用来绕过 `file_get_contents($file) === "hello"` 这类校验：`file=php://input`，POST body 写 `hello`。

### data://

把数据直接写在 URL 里：

```php
<?php
include "data://text/plain;base64,PD9waHAgcGhwaW5mbygpOz8+";  // 执行 phpinfo()
?>
```

当 `allow_url_include` 开启且题目过滤了 `php://`、`http://` 时，`data://` 是常见替代方案。SSRF 题目里 `data://` 也常被用来内联构造响应内容。

### phar://

phar 是 PHP 的打包归档格式，其元数据（meta-data）以序列化形式存储。**任何文件操作函数在解析 `phar://` 路径时都会反序列化 phar 的元数据**——这意味着只要能把精心构造的 phar 文件上传到服务器任意位置（伪装成图片都行），再找到一处可控的文件操作参数，就能触发反序列化，而不需要 `unserialize()` 调用点。具体利用链构造见 PHP反序列化 与 文件上传 章节。

## 正则绕过

出题人常用 `preg_match` / `preg_replace` 做黑名单过滤，正则本身的特性又成了新的考点。

### %00 截断

`preg_match` 处理的是字节流，传入带 `%00`（URL 编码的 NUL 字节）的字符串时，某些场景下正则匹配和字符串处理对 NUL 之后的部分处理不一致。最经典的场景是 `preg_replace` 的 `/e` 修饰符（PHP 5.5 前）配合 `\0` 截断，以及老式代码用 `ereg` 系函数（已废弃）时的 `%00` 截断——`ereg` 读到 NUL 就认为字符串结束，而后面的文件函数不这么认为。

现代题目里 `%00` 更多出现在文件路径截断（PHP < 5.3.4 的 `include $_GET['f'].".php"` 用 `?f=../../etc/passwd%00` 截掉后缀），属于 文件包含 与 目录穿越 章节的考点。

### 换行绕过

正则默认 `.` 不匹配换行符，且 `^`、`$` 只匹配整个字符串的首尾（除非加 `/m`）。所以：

```php
<?php
if (preg_match("/^flag$/", $_GET['x'])) die("no");
// 传入 "flag\n" 或 "flag\nxxx" 就可能绕过
?>
```

反过来，用 `$` 锚定检测"危险字符串结尾"的正则，在 payload 后加一个 `\n`（URL 编码 `%0a`）即可绕过，因为 `$` 在 `/m` 缺失时允许字符串末尾有一个换行。这在 SQL 注入和命令注入过滤绕过中极常用。

### 回溯上限绕过

PHP 的 PCRE 引擎有回溯次数上限 `pcre.backtrack_limit`（默认 100 万）。当 `preg_match` 因超过回溯上限而失败时，**返回值是 `false` 而不是 `0`**。如果题目用 `==` 判断：

```php
<?php
if (preg_match('/(.+)*flag/', $_GET['x']) == 0) {
    // 认为没有匹配到 flag，放行
}
?>
```

构造超长重复字符串（如 `"a" * 1000000 . "flag"`）让正则回溯爆炸，`preg_match` 返回 `false`，而 `false == 0` 为 `true`，绕过检测。Python 里一行生成 payload：

```bash
python3 -c "print('a'*1000000 + 'flag')"
```

### 换行与数组补充

另外两个小点：`preg_match` 传入数组会返回 `false` 并 warning，同样可配合 `==` 绕过；`preg_replace` 的第一个参数支持数组，逐个替换的顺序差异也偶有出题。

## each 与 create_function 等历史函数考点

这些函数在现代 PHP 中已被移除，但大量"老题"依赖它们，比赛环境为了兼容也常常跑老版本 PHP，所以仍需掌握。

### each()

PHP 7.2 起废弃、8.0 移除。`each($arr)` 返回数组当前指针处的键值对，返回数组中同时有数字索引和字符串键：

```php
<?php
$arr = ["a" => "1", "b" => "2"];
$pair = each($arr);
// $pair = [1 => "1", "value" => "1", 0 => "a", "key" => "a"]
?>
```

考点通常在变量覆盖/键名注入：当代码用 `each` 遍历用户可控数组并拼接字符串时，控制返回的 `key`/`value` 位置可以注入恶意内容。

### create_function()

PHP 7.2 废弃、8.0 移除。`create_function($args, $code)` 动态创建匿名函数，第二个参数会被拼进函数体执行——这等于一个隐蔽的 `eval`：

```php
<?php
$f = create_function('$a', 'return $a;');
echo $f("hi");  // hi

// 注入：$code 可控时闭合函数体即可执行任意代码
$g = create_function('$a', '}phpinfo();/*');
$g(1);  // 实际执行 phpinfo()
?>
```

因为函数体被拼成 `function __lambda($a) { }phpinfo();/* }`，`}` 提前闭合函数，后面的代码在函数定义时即被执行。题目若用 `create_function($_GET['arg'], $_GET['code'])` 且过滤不严格，传 `?arg=&code=}system("cat /flag");/*` 即可 RCE。这类"字符串拼接进 eval 上下文"的思路与 RCE 章节的 `assert`、`preg_replace /e` 一脉相承。

### 其他历史考点速览

- `assert("...")`：PHP 7 前接受字符串参数并 eval 执行，常用于一句话木马：`assert($_POST[1])`；
- `preg_replace` 的 `/e` 修饰符（PHP 5.5 移除）：替换结果会被当作 PHP 代码执行；
- `call_user_func` / `array_map` 等回调函数：第一个参数可控时等于任意函数调用；
- `money_format`、`IntlChar` 等冷门函数偶尔用于无字母数字 RCE 构造。

## 例题：综合演练

下面这道综合题串起了本章的多个考点，也是真实比赛中"签到难度"PHP 特性题的典型长相：

```php
<?php
include "flag.php";  // $flag = "flag{php_features_master}";

$a = $_GET['a'];
$b = $_GET['b'];
$c = $_GET['c'];
$d = $_GET['d'];

// 第一关：a 和 b 不能相等，但 MD5 要"相等"
if ($a == $b) die("a 和 b 不能相等");
if (md5($a) != md5($b)) die("md5 要相等");

// 第二关：c 不能是字符串 "1024"，但 intval 后要严格等于 1024
if ($c === "1024") die("不许直接传 1024");
if (intval($c) !== 1024) die("c 要等于 1024");

// 第三关：d 里必须出现 flag，但结尾不能是 flag
if (strpos($d, "flag") === false) die("d 要包含 flag");
if (preg_match("/flag$/", $d)) die("结尾不能是 flag");

echo $flag;
?>
```

逐步分析：

**第一关**：`$a == $b` 为假，但 `md5($a) != md5($b)` 为假。比较用的是松散的 `!=`，所以魔术哈希有效——找两个不同的字符串，MD5 都是 `0e` 开头：

```http
GET /?a=QNKCDZO&b=240610708
```

`md5("QNKCDZO")` 是 `0e8304...`，`md5("240610708")` 是 `0e4620...`，两者按科学计数法都等于 `0`，松散比较相等，过关。

**第二关**：`$c === "1024"` 是严格字符串比较，而 `intval($c) !== 1024` 也是严格比较。`intval` 只取字符串开头的数字部分，所以只要开头是 `1024`、整体不等于字符串 `"1024"` 即可：

```http
GET /?c=1024abc
```

`intval("1024abc") === 1024` 成立，`"1024abc" === "1024"` 不成立，过关。`1024.0`、`+1024`、`1024e0` 也都是合法答案。

**第三关**：`strpos` 要求包含 `flag`，正则 `/flag$/` 禁止以 `flag` 结尾。注意 `$` 在默认模式下匹配的是"字符串末尾或末尾换行之前"，并不能锚定中间内容——所以只要 `flag` 后面跟任意字符即可：

```http
GET /?d=flag%0ax
```

`d` 为 `"flag\nx"`：包含 `flag`，`strpos` 过关；`flag` 不在结尾，正则匹配失败，过关。

最终 payload：

```http
GET /?a=QNKCDZO&b=240610708&c=1024abc&d=flag%0ax HTTP/1.1
```

回顾解题路径：第一关用 **魔术哈希**，第二关用 **`intval` 截断 **，第三关用** 正则锚点语义 **。PHP 特性题的核心方法就是：** 逐条列出条件，确定每个条件对应哪个特性，然后用最小 payload 逐个击破**。遇到不确定的函数行为，本地 `php -r 'var_dump(intval("1024abc"));'` 跑一遍，永远比猜快。

## 小结

本章覆盖了 PHP 特性题的六块基石：

- 弱类型比较：`==` 的类型转换、魔术哈希、数组打函数、`strcmp`/`in_array`/`switch`/`intval` 的坑；
- 自增特性：从 `"Array"` 出发构造任意字符串，支撑无字母数字 RCE；
- 标签变体：`<?=` 始终可用、文件尾 `?>` 可省略；
- 变量覆盖：`$$`、`extract`、`parse_str` 三件套；
- 伪协议：`php://filter` 读源码、`php://input` 执行 POST 体、`data://` 内联数据、`phar://` 触发反序列化；
- 正则与历史函数：`%00` 截断、换行绕过、回溯上限、`create_function` 注入。

做题时的心态建议：遇到可疑比较先想类型转换，遇到函数参数先想传数组，遇到过滤先想编码和协议。剩下的交给实践——去 Web入门题单 里找几道 PHP 特性题练手，比把本文背下来有用得多。
