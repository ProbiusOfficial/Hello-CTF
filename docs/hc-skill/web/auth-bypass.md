---
comments: true
---

# 认证绕过

> WEB · 知识域。身份认证体系攻击:JWT、会话、OAuth/SAML、协议级绕过。标签:**JWT绕过**、**HTTP基础验证绕过**、**Cookie绕过**。

## 触发特征

- `Authorization: Bearer eyJ...`(JWT)、`remember-me`、Basic 认证弹窗。
- SSO/OAuth/SAML 流程题;"伪造管理员身份"类目标。

## JWT绕过

- **alg:none**:头部改 `{"alg":"none"}` 去签名直接改 payload;各库的历史版本可打。
- **算法混淆 RS256→HS256**:用公开的 RSA 公钥当 HMAC 密钥签名。
- **弱密钥爆破**:`hashcat -m 16500` + jwt-secrets 字典(→ [暴力破解](brute-force.md))。
- **头注入**:JWK 注入(自带公钥)、JKU 注入(指向攻击者 jwks)、KID 注入(路径穿越读可控文件 / SQL 注入)。
- **业务复用**:余额/token 值放 payload 内直接改(MetaShop 模式);JWE 公钥暴露时伪造 token(UTCTF 2026)。
- 工具:`jwt_tool` 全模式自动化。

## Cookie绕过

- 明文/简单编码:`admin=0` → `1`、base64、rot13。
- Flask session:SECRET_KEY 爆破后伪造(→ [暴力破解](brute-force.md));Laravel `APP_KEY` 泄露解密改密文 → [文件泄露](file-leak.md)。
- 序列化型 cookie:PHP session 序列化注入、Rails Marshal、Python pickle(→ 对应语言页)。
- Cookie 属性绕过:改 `role`、`uid`、时间戳种子生成(CyberSecurityRumble 2016)。
- AES cookie 长度域截断 + CRC32 置换伪造(DefCamp 2018)。
- 哈希签名绕过:base64 解码宽松性 + 参数覆盖(BCTF 2016);哈希长度拓展(→ [Crypto-SHA1](../crypto/sha1.md))。

## HTTP基础验证绕过

- Basic 认证爆破(`hydra -L u -P p target http-get /admin`)。
- 路径级绕过:大小写、尾斜杠、`/./`、URL 编码、双斜杠绕过 location 匹配(→ [HTTP请求](http-request.md))。
- `.htpasswd` 泄露 → hashcat 爆破(`-m 1800` bcrypt/md5apr1)。
- 服务端 `memcmp` 短路 / `strncmp(n=0)` 空 token 绕过(UCSB iCTF 2018)。

## 协议与基础设施

- **SRP 绕过**:发送 `A=0`/`A=n` 使共享密钥恒 0(OTW Advent 2018);`std::unordered_set` 桶碰撞伪造会话(Hackover 2018)。
- **Unicode 同形用户名碰撞**:nodeprep.prepare 归一化冲突注册 `Admin` 变体(HCTF 2018);Java `hashCode()` 碰撞绕过(CSAW 2017)。
- **OAuth/OIDC**:开放重定向偷 code、state 缺失 CSRF、ID token 操纵、email 子地址绕过(`a+admin@x.com`,HITCON 2017)。
- **SAML**:XPath 摘要走私(CVE-2024-45409)、签名包裹攻击。
- **TOTP 恢复**:服务端 `srand(time())` 可预测种子还原 TOTP 密钥(TUM CTF 2016)。
- 固定会话/会话不轮换:登录前后 session 不变 → session fixation。
- 公开管理路由种 Cookie(EHAX 2026);永真哈希校验(0xFun 2026)。

## 检查清单

1. token 结构解码(JWT 三段、cookie 编码)。
2. 签名验在哪、密钥从哪来、能否降级/混淆。
3. 服务端校验点逐个试:改 payload、改头、去签名、换算法。

## 转向

- 爆破与字典 → [暴力破解](brute-force.md);拿下后台后 → 各注入/上传技能
