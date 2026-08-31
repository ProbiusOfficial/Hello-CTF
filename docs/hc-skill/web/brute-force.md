---
comments: true
---

# 暴力破解

> WEB · 知识域。对可枚举的口令、token、验证码进行系统性枚举。标签:**常规暴力破解**、**Hash生日攻击**、**验证码识别**。

## 触发特征

- 登录口存在、无速率限制或限速可绕过。
- token/session 由弱密钥或时间种子生成。
- 验证码可机器识别或逻辑上可绕过。

## 常规暴力破解

- 字典优先:rockyou、国内社工组合(姓名拼音+生日+工号)。
- Flask session:`flask-unsign --unsign --cookie '<c>' --wordlist rockyou.txt`,拿到 `SECRET_KEY` 后伪造 session(国内赛高频)。
- JWT 弱密钥:`hashcat -m 16500 jwt.txt jwt-secrets.txt`(见 [认证绕过](auth-bypass.md))。
- 限速绕过:`X-Forwarded-For` 轮换、GraphQL batching/aliasing 合并查询(Hack.lu CTF 2020、HeroCTF v5)。

## Hash生日攻击

- 碰撞下界 2^(n/2):MD5 用 `fastcoll` 量产碰撞,链式生成 2^k 个同哈希文件(BackdoorCTF 2016);MD5 PDF 碰撞管线用 corkami/pocs(35C3 2018)。
- 双重加密 → 中间相遇,O(2^2k) 降为 O(2^k)。
- 哈希长度拓展:对 `hash(SECRET||data)` 追加数据并续算哈希,`hashpumpy`(详见 [Crypto-SHA1](../crypto/sha1.md),原题 PlaidCTF 2014、ASIS CTF 2017)。

## 验证码识别

- 静态图:`ddddocr` 一行识别(国内事实标准);算式验证码正则抽取后求值。
- 字体混淆 CAPTCHA:Selenium 渲染 + Tesseract(Square CTF 2018);TTF 字形轮廓 diff 破解(Square CTF 2018)。
- 逻辑绕过:验证码不刷新、校验后销毁顺序错误、返回包携带答案、前端校验可删。

## 与其他技能的衔接

- 逐位 oracle 爆破 → [SQL注入](sql-injection.md) 盲注
- 时间戳种子会话伪造(CyberSecurityRumble 2016)→ [Crypto-MT19937](../crypto/mt19937.md)
- 服务端指纹匹配枚举 → [认证绕过](auth-bypass.md)

## 工具速查

```bash
hydra -L u.txt -P p.txt target http-post-form "/login:user=^USER^&pass=^PASS^:F=fail"
ffuf -X POST -d "u=FUZZ&p=admin" -w p.txt -u URL
ddddocr --onnx  # 或 python: import ddddocr; ocr.classification(img)
```
