---
comments: true

---

# 文件上传

<!-- Imported from D:\\Book\\Web\\Chapter10\10-1.md -->
### JavaScript WebShell

话不多说，直接上题（BugKu CTF）

![](https://pic1.imgdb.cn/item/681daef958cb8da5c8e8cec0.jpg)

打开网页啥也没有

![](https://pic1.imgdb.cn/item/681db68f58cb8da5c8e8f341.jpg)

查看源代码发现注释

![](https://pic1.imgdb.cn/item/681dba1558cb8da5c8e906aa.jpg)

访问是一个文件上传

![](https://pic1.imgdb.cn/item/681dba2f58cb8da5c8e9090c.jpg)

前面试了各种过滤方法

要使用 HTML 标签定义 PHP 一句话木马，最后保存为图片文件，任意均可

![](https://pic1.imgdb.cn/item/681dba5258cb8da5c8e90b14.jpg)

上传文件回显路径

![](https://pic1.imgdb.cn/item/681dc52d58cb8da5c8e9608c.jpg)

访问路径可以看到命令被执行了

![](https://pic1.imgdb.cn/item/681dc54658cb8da5c8e96270.jpg)

上传一句话木马

![](https://pic1.imgdb.cn/item/681dc55c58cb8da5c8e96408.jpg)

使用中国蚁剑连接

![](https://pic1.imgdb.cn/item/681dc57758cb8da5c8e965c4.jpg)

成功拿到 flag

![](https://pic1.imgdb.cn/item/681dc58c58cb8da5c8e96743.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-10.md -->
### .user.ini 解析绕过

话不多说，直接上题（BUUCTF）

![](https://pic1.imgdb.cn/item/681e21a158cb8da5c8e9fdad.jpg)

打开页面考察文件上传

![](https://pic1.imgdb.cn/item/681e21ed58cb8da5c8e9fdd4.jpg)

`.user.ini` 文件是一个配置文件，并且是可以由用户自定义的

`php.ini` 不一样的是，`.user.ini` 可以被动态加载，只需要等待一段时间就会刷新了

![](https://pic1.imgdb.cn/item/681e222f58cb8da5c8e9fdf3.jpg)

BurpSuite 抓包修改 MIME 类型再上传

![](https://pic1.imgdb.cn/item/681e224258cb8da5c8e9fdfc.jpg)

再上传同名的木马发现有过滤

![](https://pic1.imgdb.cn/item/681e228d58cb8da5c8e9fe1d.jpg)

修改木马后再上传

![](https://pic1.imgdb.cn/item/681e22ac58cb8da5c8e9fe26.jpg)

访问给出的目录路径下的 index.php 拿到 flag

![](https://pic1.imgdb.cn/item/681e22bd58cb8da5c8e9fe29.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-11.md -->
### Content-type 大小写混淆绕过

话不多说，直接上题（BugKu CTF）

![](https://pic1.imgdb.cn/item/67e225e80ba3d5a1d7e30232.png)

打开网页正常的文件上传

![](https://pic1.imgdb.cn/item/67e226040ba3d5a1d7e3028c.png)

`strpos()` 函数查找字符串在另一字符串中第一次出现的位置（区分大小写）

所以这里使用大小写混淆绕过

![](https://pic1.imgdb.cn/item/67e226df0ba3d5a1d7e30455.png)

常规的 php 后缀被替换，换成 php4 可以

最后是修改 Content-Type 类型为图片即可

![](https://pic1.imgdb.cn/item/67e2291a0ba3d5a1d7e304c4.png)

上传成功

![](https://pic1.imgdb.cn/item/67e2296f0ba3d5a1d7e304f6.png)

使用蚁剑连接拿到 flag

![](https://pic1.imgdb.cn/item/67e229540ba3d5a1d7e304ce.png)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-12.md -->
### php4 后缀绕过

话不多说，直接上题（BugKu CTF）

![](https://pic1.imgdb.cn/item/67e225e80ba3d5a1d7e30232.png)

打开网页正常的文件上传

![](https://pic1.imgdb.cn/item/67e226040ba3d5a1d7e3028c.png)

`strpos()` 函数查找字符串在另一字符串中第一次出现的位置（区分大小写）

所以这里使用大小写混淆绕过

![](https://pic1.imgdb.cn/item/67e226df0ba3d5a1d7e30455.png)

常规的 php 后缀被替换，换成 php4 可以

最后是修改 Content-Type 类型为图片即可

![](https://pic1.imgdb.cn/item/67e2291a0ba3d5a1d7e304c4.png)

上传成功

![](https://pic1.imgdb.cn/item/67e2296f0ba3d5a1d7e304f6.png)

使用蚁剑连接拿到 flag

![](https://pic1.imgdb.cn/item/67e229540ba3d5a1d7e304ce.png)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-13.md -->
### 参数置空绕过

话不多说，直接上题（青少年 CTF 练习平台）

![](https://pic1.imgdb.cn/item/68196bba58cb8da5c8de8893.png)

扫描目录发现有个 `index.php.bak`

```php+HTML
<?php 
error_reporting(0);
$token = $_COOKIE['token'] ?? null;

if($token){
    extract($_GET);
    $token = base64_decode($token);
    $token = json_decode($token, true);


    $username = $token['username'];
    $password = $token['password'];
    $isLocal = false;
    
    if($_SERVER['REMOTE_ADDR'] == "127.0.0.1"){
        $isLocal = true;
    }

    if($isLocal){
        echo 'Welcome Back，' . $username . '!';
        if(file_exists('upload/' . $username . '/' . $token['filename'])){
            echo '<br>';
            echo '<img src="upload/' . $username . '/' . $token['filename'] .'" width="200">';
        } else {
            echo '请上传您高贵的头像。';
            $html = <<<EOD
            <form method="post" action="upload.php" enctype="multipart/form-data">
                <input type="file" name="file" id="file">
                <input type="submit" value="Upload">
            </form>
            EOD;
            echo $html;
        }
    } else {
        // echo "留个言吧";
        $html = <<<EOD
        <h1>留言板</h1>
        <label for="input-text">Enter some text:</label>
        <input type="text" id="input-text" placeholder="Type here...">
        <button onclick="displayInput()">Display</button>
        EOD;
        echo $html;
    }
} else {
    $html = <<<EOD
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
</head>
<body>
    <h2>Login</h2>
    <form method="post" action="./login.php">
        <div>
            <label for="username">Username:</label>
            <input type="text" name="username" id="username" required>
        </div>
        <div>
            <label for="password">Password:</label>
            <input type="password" name="password" id="password" required>
        </div>
        <div>
            <input type="submit" value="Login">
        </div>
    </form>
</body>
</html>
EOD;
    echo $html;
}
?>

<script>
    function displayInput() {
      var inputText = document.getElementById("input-text").value;
      document.write(inputText)
    }
</script>
```

**主要功能流程：**

1. 获取 Cookie 中的 `token` 值

   ```php
   $token = $_COOKIE['token'] ?? null;
   ```

2. 解析 `token` 内容

   ```php
   $token = base64_decode($token);
   $token = json_decode($token, true);
   ```

3. 判断访问者是否为 `127.0.0.1`

   ```php
   if ($_SERVER['REMOTE_ADDR'] == "127.0.0.1")
   ```

4. 本地用户功能

   显示欢迎语；

   检查头像文件是否存在；

   若存在则展示头像；

   若不存在则提示上传表单（提交到 `upload.php`）

5. 远程用户功能：

   显示留言板（前端 HTML + JS 动态展示）

6. 未登录用户

   显示登录表单，提交至 `login.php`

**extract($_GET) 工作原理：**

```php
<?php
extract($_GET);
echo "Hello, $name!";
?>
```

请求：

```
http://example.com/index.php?name=Alice
```

结果：

```
Hello, Alice!
```

**变量污染攻击：**

```php
<?php
$token = "secure-token";
extract($_GET);
echo "Token is: $token";
?>
```

请求：

```
http://example.com/index.php?token=hacked
```

结果：

```
Token is: hacked
```

**`extract($GET);` 存在变量覆盖，可以利用这个把 `$SERVER['REMOTE_ADDR']` 覆盖成 `127.0.0.1`**

```
?_SERVER[REMOTE_ADDR]=127.0.0.1
```

首先登录

![](https://pic1.imgdb.cn/item/681acaf158cb8da5c8e1cc96.png)

然后污染找到文件上传点

![](https://pic1.imgdb.cn/item/681acb1658cb8da5c8e1ccf0.png)

上传成功后没有返回路径，在源码上可以看到这个

```php
if(file_exists('upload/' . $username . '/' . $token['filename']))
```

猜测文件上传到 `/upload/[username]/[filename]`，尝试发现是正确的

当存在 `username` 时，无论上传什么都不能被解析成 PHP 代码

把 `username` 置空，成功将文件上传到 upload 目录

```
token=eyJ1c2VybmFtZSI6IiIsInBhc3N3b3JkIjoiIn0=
```

![](https://pic1.imgdb.cn/item/687f6cab58cb8da5c8cb68b1.png)




<!-- Imported from D:\\Book\\Web\\Chapter10\10-14.md -->
### Apache 多后缀解析漏洞

话不多说，直接上题（青少年 CTF 练习平台）

![](https://pic1.imgdb.cn/item/6863fe2c58cb8da5c88589d4.png)

打开网页是直接给出了源码

```php+HTML
<?php
header("Content-Type:text/html; charset=utf-8");
// 每5分钟会清除一次目录下上传的文件
require_once('pclzip.lib.php');

if(!$_FILES){

        echo '

<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta http-equiv="X-UA-Compatible" content="ie=edge" />
    <title>文件上传章节练习题</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <style type="text/css">
        .login-box{
            margin-top: 100px;
            height: 500px;
            border: 1px solid #000;
        }
        body{
            background: white;
        }
        .btn1{
            width: 200px;
        }
        .d1{
            display: block;
            height: 400px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box col-md-12">
        <form class="form-horizontal" method="post" enctype="multipart/form-data" >
            <h1>文件上传章节练习题</h1>
            <hr />
            <div class="form-group">
                <label class="col-sm-2 control-label">选择文件：</label>
                <div class="input-group col-sm-10">
                    <div >
                    <label for="">
                        <input type="file" name="file" />
                    </label>
                    </div>
                </div>
            </div>
                
        <div class="col-sm-8  text-right">
            <input type="submit" class="btn btn-success text-right btn1" />
        </div>
        </form>
        </div>
    </div>
</body>
</html>
';

    show_source(__FILE__);
}else{
    $file = $_FILES['file'];

    if(!$file){
        exit("请勿上传空文件");
    }
    $name = $file['name'];

    $dir = 'upload/';
    $ext = strtolower(substr(strrchr($name, '.'), 1));
    $path = $dir.$name;

    function check_dir($dir){
        $handle = opendir($dir);
        while(($f = readdir($handle)) !== false){
            if(!in_array($f, array('.', '..'))){
                if(is_dir($dir.$f)){
                    check_dir($dir.$f.'/');
                 }else{
                    $ext = strtolower(substr(strrchr($f, '.'), 1));
                    if(!in_array($ext, array('jpg', 'gif', 'png'))){
                        unlink($dir.$f);
                    }
                }
            
            }
        }
    }

    if(!is_dir($dir)){
        mkdir($dir);
    }

    $temp_dir = $dir.md5(time(). rand(1000,9999));
    if(!is_dir($temp_dir)){
        mkdir($temp_dir);
    }

    if(in_array($ext, array('zip', 'jpg', 'gif', 'png'))){
        if($ext == 'zip'){
            $archive = new PclZip($file['tmp_name']);
            foreach($archive->listContent() as $value){
                $filename = $value["filename"];
                if(preg_match('/\.php$/', $filename)){
                     exit("压缩包内不允许含有php文件!");
                 }
            }
            if ($archive->extract(PCLZIP_OPT_PATH, $temp_dir, PCLZIP_OPT_REPLACE_NEWER) == 0) {
                check_dir($dir);
                   exit("解压失败");
            }

            check_dir($dir);
            exit('上传成功!');
        }else{
            move_uploaded_file($file['tmp_name'], $temp_dir.'/'.$file['name']);
            check_dir($dir);
            exit('上传成功!');
        }
    }else{
        exit('仅允许上传zip、jpg、gif、png文件!');
    }
}
```

在上传时，使用白名单验证上传文件后缀

```php
if(in_array($ext, array('zip', 'jpg', 'gif', 'png'))){
```

不过本上传点支持上传 zip 压缩包，且会将 zip 包解压到文件上传目录中，有可能会导致一些安全问题

```php
if($ext == 'zip'){
            $archive = new PclZip($file['tmp_name']);
            foreach($archive->listContent() as $value){
                $filename = $value["filename"];
                if(preg_match('/\.php$/', $filename)){
                     exit("压缩包内不允许含有php文件!");
                 }
            }
            if ($archive->extract(PCLZIP_OPT_PATH, $temp_dir, PCLZIP_OPT_REPLACE_NEWER) == 0) {
                check_dir($dir);
                   exit("解压失败");
            }

            check_dir($dir);
            exit('上传成功!');
        }
```

首先会检测压缩包内是否含有 `.php` 文件，如果存在 `.php` 文件就直接退出解压流程

在解压完成后，会调用 `check_dir()` 方法再次检测解压出来的文件是否含有恶意文件

```php
    function check_dir($dir){
        $handle = opendir($dir);
        while(($f = readdir($handle)) !== false){
            if(!in_array($f, array('.', '..'))){
                if(is_dir($dir.$f)){
                    check_dir($dir.$f.'/');
                 }else{
                    $ext = strtolower(substr(strrchr($f, '.'), 1));
                    if(!in_array($ext, array('jpg', 'gif', 'png'))){
                        unlink($dir.$f);
                    }
                }
            
            }
        }
    }
```

并且因为解压到的目录是一个随机生成的目录，目录名无法预测，与导致不能使用条件竞争方法

```php
if(!is_dir($dir)){
        mkdir($dir);
    }

    $temp_dir = $dir.md5(time(). rand(1000,9999));
    if(!is_dir($temp_dir)){
        mkdir($temp_dir);
    }
```

首先来绕第一个过滤， 黑名单过滤了 php 文件，压缩包内不能含有 `.php` 文件，这里正则为 `.php$` 限制了结尾

所以可以尝试 `php3、php5、phtml` 等绕过，不过服务端只配置了解析 php 文件，导致该类绕过不可用

![](https://pic1.imgdb.cn/item/68640ab258cb8da5c885b9ee.png)

根据 404 页面,发现使用的是 apache，很容易联想到 apache 的多后缀文件解析漏洞

这里选择上传一个 `x.php.xxx` 文件

通过 010editor 构造恶意压缩包，这里需要注意修改后的文件名长度与修改前一致，否则解压会报错

这里改为 `/../../jason07.php.xxx`

![](https://pic1.imgdb.cn/item/68640efd58cb8da5c885bcb9.png)

上传压缩包，访问 `jason07.php.xxx`，得到 flag

![](https://pic1.imgdb.cn/item/6864103458cb8da5c885be31.png)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-15.md -->
### %00 截断绕过

话不多说，直接上题（CTFHUB）

![](https://pic1.imgdb.cn/item/687c934e58cb8da5c8c85f59.png)

`%00` 是 URL 编码中**空字节（null byte，\x00）**的表示方式

空字节在**C 语言等底层语言**中，常用作字符串的结束标志

例如，`char filename[100] = "shell.php\x00.jpg";`  实际上等同于  `shell.php`，`\x00`  之后的内容被忽略

**`%00` 的使用是在路径上！**

**`%00` 的使用是在路径上！**

**`%00` 的使用是在路径上！**

重要的话说三遍，如果在文件名上使用，就无法正常截断了

这个路径可能在 POST  数据包中，也可能在 URL 中

![](https://pic1.imgdb.cn/item/687c94f758cb8da5c8c86010.png)

成功拿到 flag

![](https://pic1.imgdb.cn/item/687c950358cb8da5c8c8601d.png)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-16.md -->
### 双写后缀绕过

话不多说，直接上题（CTFHUB）

![](https://pic1.imgdb.cn/item/687c956258cb8da5c8c86039.png)

准备一个 `*.pphphp` 文件上传

后端会自动替换其中的 `php` 为空值，这样两边的 `p` + `hp` 自动合并成了 `php`

![](https://pic1.imgdb.cn/item/687c95b758cb8da5c8c86054.png)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-17.md -->
### PNG 图片马绕过

话不多说，直接上题（PicoCTF）

![](https://pic1.imgdb.cn/item/68a48ebe58cb8da5c83a625e.png)

上传木马回显必须包含 `.png`

![](https://pic1.imgdb.cn/item/68a4902a58cb8da5c83a6394.png)

修改文件名后发现回显文件头不对

![](https://pic1.imgdb.cn/item/68a490f458cb8da5c83a64a9.png)

直接在文件头前添加 PNG

![](https://pic1.imgdb.cn/item/68a4957458cb8da5c83a6af5.png)

上传成功

![](https://pic1.imgdb.cn/item/68a4959358cb8da5c83a6b32.png)

文件放在了 `/uploads` 目录下

![](https://pic1.imgdb.cn/item/68a496bf58cb8da5c83a6e26.png)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-18.md -->
### 文件名加 / 绕过

漏洞本质 Tomcat 配置了可写（readonly=false），导致我们可以往服务器写文件

```jsp
<servlet>
    <servlet-name>default</servlet-name>
    <servlet-class>org.apache.catalina.servlets.DefaultServlet</servlet-class>
    <init-param>
        <param-name>debug</param-name>
        <param-value>0</param-value>
    </init-param>
    <init-param>
        <param-name>listings</param-name>
        <param-value>false</param-value>
    </init-param>
    <init-param>
        <param-name>readonly</param-name>
        <param-value>false</param-value>
    </init-param>
    <load-on-startup>1</load-on-startup>
</servlet>
```

虽然 Tomcat 对文件后缀有一定检测（不能直接写 JSP），但我们使用一些文件系统的特性（如 Linux下可用 `/`）来绕过了限制

![](https://pic1.imgdb.cn/item/68ba4d9b58cb8da5c87f280a.png)

![](https://pic1.imgdb.cn/item/68ba4da458cb8da5c87f2834.png)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-2.md -->
### Python WebShell

话不多说，直接上题（BugKu CTF）

![](https://pic1.imgdb.cn/item/681de0ca58cb8da5c8e9daa6.jpg)

打开网页是一个文件上传

![](https://pic1.imgdb.cn/item/681de0fa58cb8da5c8e9dab8.jpg)

这是 Python 的 Flask 框架，编写 Python 的木马

```python
import os
os.system('cat /flag')
```

![](https://pic1.imgdb.cn/item/681de11258cb8da5c8e9dabc.jpg)

上传文件

![](https://pic1.imgdb.cn/item/681de14158cb8da5c8e9daf7.jpg)

代码被执行拿到 flag

![](https://pic1.imgdb.cn/item/681de14c58cb8da5c8e9daff.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-20.md -->
### Nginx 文件上传绕过（CVE-2013-4547）

这个漏洞的原理是，Nginx 错误地解析了请求的 URI，错误地获取到用户请求的文件名，导致出现权限绕过、代码执行等连带影响

```nginx
location ~ \.php$ {
    include        fastcgi_params;

    fastcgi_pass   127.0.0.1:9000;
    fastcgi_index  index.php;
    fastcgi_param  SCRIPT_FILENAME  /var/www/html$fastcgi_script_name;
    fastcgi_param  DOCUMENT_ROOT /var/www/html;
}
```

正常情况下（关闭 pathinfo 的情况下），只有 .php 后缀的文件才会被发送给 Fastcgi 解析

而存在 CVE-2013-4547 的情况下，我们请求 `1.gif[0x20][0x00].php`，这个 URI 可以匹配上正则 `\.php$`，可以进入这个 Location 块；但进入后，Nginx 却错误地认为请求的文件是 `1.gif[0x20]`，就设置其为 `SCRIPT_FILENAME` 的值发送给Fastcgi

Fastcgi 根据 `SCRIPT_FILENAME`的值进行解析，最后造成了解析漏洞

上传反弹 Shell，先添加两个空格

![](https://pic1.imgdb.cn/item/68ba91b158cb8da5c8802b9a.png)

将两个 `20` 的最后一个改为 `00`

![](https://pic1.imgdb.cn/item/68ba91de58cb8da5c8802d2c.png)

上传成功

![](https://pic1.imgdb.cn/item/68ba91f058cb8da5c8802db8.png)

访问上传的文件

![](https://pic1.imgdb.cn/item/68ba994558cb8da5c8806992.png)

成功连接

![](https://pic1.imgdb.cn/item/68ba99a658cb8da5c8806ab2.png)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-3.md -->
### JavaScript 加密绕过

话不多说，直接上题（BugKu CTF）

![](https://pic1.imgdb.cn/item/681de1ee58cb8da5c8e9db25.jpg)

实战打网站

![](https://pic1.imgdb.cn/item/681de20a58cb8da5c8e9db2b.jpg)

先去注册账号

![](https://pic1.imgdb.cn/item/681de21e58cb8da5c8e9db2d.jpg)

然后登录

![](https://pic1.imgdb.cn/item/681de24358cb8da5c8e9db3a.jpg)

看到头像是一个上传点

![](https://pic1.imgdb.cn/item/681de25358cb8da5c8e9db3c.jpg)

上传图片试试

![](https://pic1.imgdb.cn/item/681de25b58cb8da5c8e9db3f.jpg)

头像变了确认可以上传

![](https://pic1.imgdb.cn/item/681de27158cb8da5c8e9db44.jpg)

再次上传打开 BurpSuite 抓包拦截

![](https://pic1.imgdb.cn/item/681de2c358cb8da5c8e9db4e.jpg)

前端进行了 Base64 编码，同时设置了文件类型

![](https://pic1.imgdb.cn/item/681de2da58cb8da5c8e9db5b.jpg)

修改类型为 PHP，上传 Base64 编码的一句话木马

![](https://pic1.imgdb.cn/item/681de30d58cb8da5c8e9db61.jpg)

打开中国蚁剑测试连接

![](https://pic1.imgdb.cn/item/681de32f58cb8da5c8e9db8e.jpg)

拿到 flag

![](https://pic1.imgdb.cn/item/681de36d58cb8da5c8e9dbd2.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-4.md -->
### Content-type 图片绕过

话不多说，直接上题（BugKu CTF）

![](https://pic1.imgdb.cn/item/67e225e80ba3d5a1d7e30232.png)

打开网页正常的文件上传

![](https://pic1.imgdb.cn/item/67e226040ba3d5a1d7e3028c.png)

`strpos()` 函数查找字符串在另一字符串中第一次出现的位置（区分大小写）

所以这里使用大小写混淆绕过

![](https://pic1.imgdb.cn/item/67e226df0ba3d5a1d7e30455.png)

常规的 php 后缀被替换，换成 php4 可以

最后是修改 Content-Type 类型为图片即可

![](https://pic1.imgdb.cn/item/67e2291a0ba3d5a1d7e304c4.png)

上传成功

![](https://pic1.imgdb.cn/item/67e2296f0ba3d5a1d7e304f6.png)

使用蚁剑连接拿到 flag

![](https://pic1.imgdb.cn/item/67e229540ba3d5a1d7e304ce.png)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-5.md -->
### disable_functions 绕过

话不多说，直接上题（BugKu CTF）

![](https://pic1.imgdb.cn/item/67b0a0b9d0e0a243d4ffaef3.jpg)

加密混淆，这一步因为解密网站挂了就跳过

![](https://pic1.imgdb.cn/item/67b0a0c2d0e0a243d4ffaefa.jpg)

网上找的图

![](https://pic1.imgdb.cn/item/67b0a0eed0e0a243d4ffaf20.jpg)

使用中国蚁剑远程连接

![](https://pic1.imgdb.cn/item/67b0a0d6d0e0a243d4ffaf05.jpg)

访问别的目录报错，应该设置了 `disable_function()` 函数

![](https://pic1.imgdb.cn/item/67b0a122d0e0a243d4ffaf47.jpg)

基于黑名单来实现对某些函数使用的限制

![](https://pic1.imgdb.cn/item/67b0a138d0e0a243d4ffaf5a.jpg)

使用蚁剑的插件绕过，网不行的自己去 GitHub 上下插件

![](https://pic1.imgdb.cn/item/67b0a152d0e0a243d4ffaf70.jpg)

LD_PRELOAD 是一个可选的 Unix 环境变量，  包含一个或多个共享库或共享库的路径

它允许你定义在程序运行前优先加载的动态链接库，即我们可以自己生成一个动态链接库加载

以覆盖正常的函数库，也可以注入恶意程序，执行恶意命令

最后远程连接这个新木马就行了，密码一样的

![](https://pic1.imgdb.cn/item/67b0a1bed0e0a243d4ffafc4.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-6.md -->
### phtml 后缀绕过

话不多说，直接上题（BUUCTF）

![](https://pic1.imgdb.cn/item/681e18d358cb8da5c8e9f9d2.jpg)

考察的是文件上传

![](https://pic1.imgdb.cn/item/681e1ae358cb8da5c8e9faf3.jpg)

上传正常的 PHP 改 MIME 都不行

![](https://pic1.imgdb.cn/item/681e1af558cb8da5c8e9faff.jpg)

尝试修改后缀为 php3、Php、phtml 等，发现 phtml 可以

![](https://pic1.imgdb.cn/item/681e1b0f58cb8da5c8e9fb45.jpg)




<!-- Imported from D:\\Book\\Web\\Chapter10\10-7.md -->
### GIF 文件头绕过

话不多说，直接上题（BUUCTF）

![](https://pic1.imgdb.cn/item/681e18d358cb8da5c8e9f9d2.jpg)

继上一节发现它过滤 < 及 ? 之后

可以使用第一节的 JavaScript WebShell 绕过

但还是被拦截了，要求是图片类型

![](https://pic1.imgdb.cn/item/681e1be358cb8da5c8e9fb91.jpg)

添加一个 GIF 的文件头绕过

![](https://pic1.imgdb.cn/item/681e1bf858cb8da5c8e9fb94.jpg)

上传成功

![](https://pic1.imgdb.cn/item/681e1c5658cb8da5c8e9fbbd.jpg)

扫描后台有个 upload 目录可以访问

![](https://pic1.imgdb.cn/item/681e1c6b58cb8da5c8e9fbbe.jpg)

打开蚁剑连接我们上传的文件

![](https://pic1.imgdb.cn/item/681e1c7658cb8da5c8e9fbc1.jpg)

成功拿到 flag

![](https://pic1.imgdb.cn/item/681e1c9158cb8da5c8e9fbce.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-8.md -->
### JavaScript 验证绕过

话不多说，直接上题（BUUCTF）

![](https://pic1.imgdb.cn/item/681e201058cb8da5c8e9fd18.jpg)

与上一节方法一样，只不过多了一个前端 JS 验证

浏览器设置禁用 JS 就可以绕过

![](https://pic1.imgdb.cn/item/681e201e58cb8da5c8e9fd20.jpg)

上传文件成功

![](https://pic1.imgdb.cn/item/681e203a58cb8da5c8e9fd29.jpg)

拿到 flag

![](https://pic1.imgdb.cn/item/681e205558cb8da5c8e9fd31.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter10\10-9.md -->
### .htaccess 解析绕过

话不多说，直接上题（BUUCTF）

![](https://pic1.imgdb.cn/item/681e208358cb8da5c8e9fd46.jpg)

打开网页考察文件上传

![](https://pic1.imgdb.cn/item/681e209358cb8da5c8e9fd51.jpg)

利用 Apache 的 .htaccess 解析漏洞，将要上传的文件按 PHP 解析

![](https://pic1.imgdb.cn/item/681e20a658cb8da5c8e9fd67.jpg)

上传时修改 MIME 类型为图片类

![](https://pic1.imgdb.cn/item/681e20c458cb8da5c8e9fd81.jpg)

上传成功

![](https://pic1.imgdb.cn/item/681e20e558cb8da5c8e9fd89.jpg)

接着上传木马文件（要与 .htaccess 中的保持一致）

![](https://pic1.imgdb.cn/item/681e20f858cb8da5c8e9fd8b.jpg)

打开中国蚁剑建立远程连接

![](https://pic1.imgdb.cn/item/681e210858cb8da5c8e9fd99.jpg)

成功拿到 flag

![](https://pic1.imgdb.cn/item/681e211758cb8da5c8e9fd9b.jpg)
