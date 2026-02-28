---
comments: true
glightbox: false
hide:
  - footer
  - toc
---



> 项目地址：https://github.com/CTF-Archives/ctf-docker-template
>
> Release：https://github.com/CTF-Archives/ctf-docker-template/releases
>
> 当然您也可以点击本文档中的对应下载按钮获取模板的打包文件 (基于GitHub直链)





![ctf-docker-template](https://nssctf.wdf.ink//img/WDTJ/202403121324799.png)

## About

**ctf-docker-template** 是一个用于支持动态 Flag 的Docker容器模板项目，支持主流的各类CTF平台.

项目存有一定局限性，但已可适用于绝大多数初中级别题目的命题需求。

本仓库内的Docker容器模板支持的 FLAG 注入类型如下：

- `$FLAG`（[CTFd](https://github.com/CTFd/CTFd)，[NSSCTF](https://www.nssctf.cn/)）
- `$GZCTF_FLAG`（[GZCTF](https://github.com/GZTimeWalker/GZCTF)）
- `$DASCTF`（DASCTF）

三种动态flag部署方式，支持GZCTF、CTFd、安恒DASCTF等支持Docker动态部署题目靶机的平台。

> 一般情况下，CTF题目动态FLAG使用环境变量注入的方式来实现:
>
> `docker run -dtP -e FLAG=HelloCTF{This1sFl4g} [imagesName:Tag]`
>
> 而上面所说的注入类型 "`$xxx`" xxx就是FLAG的变量名。

**有问题请开issue，好用请点star，有问题的话欢迎通过 [CTF-Archives售后快速服务群](http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=KFamhBpmURTZpndhc0MI7_1l3a6Xezrf&authKey=Yenwm7%2B%2F%2FT%2BtSXCSyr%2B7fYS47Ot0MwFqesH4HOLT8ZADE2e9XO6AS96HQvjxh%2B%2BG&noverify=0&group_code=894957229) 联系维护人员寻求帮助**

!!! Warning "注意"
    
    **此仓库内的模板仅在Linux环境（linux/amd64）下进行测试并保证可用性,如果为windows（windows/amd64）或者macos（linux/arm）等其他架构，不保证可用性😔
    **
    
    建议直接在linux下执行 `git clone` 操作，或者直接从github下载zip版本的源码.

## Structure

在一般情况下，每个模板的文件结构如下：

```
.
├── README.md
├── Dockerfile
├── config # Web容器 中间件配置需要定义的专属
│   └── nginx.conf
├── data # Web容器 且 有数据库需求容器专属
│   └── db.sql
├── docker
│   └── docker-compose.yml
├── service
│   └── docker-entrypoint.sh
└── src
    └── main.py
```

- `Dockerfile` 为docker容器编译文件，用于设计docker容器，可在其中设置换源、增添软件包等等

- `config` 文件夹内存放着容器内服务相关的配置文件，如 `nginx` 的配置文件等等

- `data` 文件夹内存放着容器内服务相关的配置文件，如 `nginx` 的配置文件等等

- `docker` 文件夹内存放与docker有关的文件，如 `docker-compose.yml` 文件，内部已经设置好了端口转发和测试用flag，便于测试容器环境

- `service` 文件夹内存放着与服务有关的文件，如 `docker-entrypoint.sh` 用于定义容器的入口点

- `src` 文件夹内存放着题目的项目源码，也可以是pwn题目的二进制文件，即为题目的相关文件

- `flag.php` 用于直接查看flag文件的测试文件，访问可直接查看当前题目根目录下的flag文件，如果文件不存在则会输出error

- `shell.php` 一句话木马，用于测试web容器稳定性

  ......

## 常见问题

### no_socket with crypto

`no_socket`指的是源代码中没有引入`socket`相关的库，当希望达到的效果是类似于当用户通过特定端口连接到靶机时，就运行python代码，并将代码的运行界面转发给用户。

如果已经引入了`socket`相关的库，请直接使用如`python app.py`这类语句启动python程序，并让程序自行监听特定端口。

### 软件源换源

环境中涉及软件包处理的情形，如apt、yum，均已换源为ustc源，如不处于中国大陆网络环境/启用了全局代理环境，请自行修改相关换源语句，避免由于还原带来的负优化。

### 日志sh文件错误

由于DOS/Windows 和 Linux/Unix的文件换行回车格式不同，DOS/Windows 的文本文件在每一行末尾有一个 CR（回车）和 LF（换行），而 UNIX 文本只有一个LF（换行），从而造成Linux的Docker出现下面的报错：

```bash
/docker-entrypoint.sh: line 2: $'\r': command not found
/docker-entrypoint.sh: line 26: syntax error: unexpected end of file
```

解决方案如下:

```bash
sed -i ""s/\r//"" docker-entrypoint.sh
```

即通过正则匹配，直接替换掉 `\r` 字符，不过此方案不一定能完全解决问题。

建议直接在linux下执行 `git clone` 操作，或者直接从github下载zip版本的源码，避免一些奇奇怪怪的编码问题。

请注意，`sed`指令在`unix（macos）`下的预期执行效果与`linux`下的预期执行效果不同。

## Detail

每个容器模板均为独立封装，您可以在每个容器模板文件夹中找到对应的 README 文件，请在使用前仔细阅读，如有任何疑问请加入项目中的  **[CTF-Archives售后快速服务群](http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=KFamhBpmURTZpndhc0MI7_1l3a6Xezrf&authKey=Yenwm7%2B%2F%2FT%2BtSXCSyr%2B7fYS47Ot0MwFqesH4HOLT8ZADE2e9XO6AS96HQvjxh%2B%2BG&noverify=0&group_code=894957229)**  联系维护人员获取帮助。

当然，我们也在 [**Hello-CTF 命题部分**](https://hello-ctf.com/Create/) 页面提供命题相关的教程，也附带本项目的所有文档，欢迎访问查阅。

!!! note "一般情况"

    在无特殊声明的情况下，完成使用中提及对应模板的必要步骤后,执行后续操作：
       
    ```shell
    docker build .
    ```
       
    开始编译镜像。
       
    也可以在安放好相关项目文件之后，直接使用 `./docker/docker-compose.yml` 内的 `docker-compose` 文件实现一键启动测试容器。
       
    ```shell
    cd ./docker
    docker-compose up -d
    ```
       
    **特别注意！！**
       
    **对于Python相关环境，如使用了 第三方库，请先在 `./Dockerfile` 内补充 pip 安装语句。**
       
    **大部分项目对SRC文件中需求的 程序 / 脚本 文件有特定命名要求，请仔细阅读您所用模板的 README 文件。**

### Crypto

#### python_3.8/3.10-no_socket / with_socket

**环境：**

提供 `Python 3.8 / Python 3.10` 的基础环境，并已经添加 `pycryptodome` 库，并基于项目本身实现相关接口。

*实现*：当选手连接到对应服务端口（由项目自行定义）的时候，运行 `.py项目`

**with_socket** 适用于项目中引入了 `socket` 等库，需要镜像做到：

- 选手通过端口连接到容器/靶机
- 启动项目
- 项目自行处理会话

**no_socket** 适用于项目中没有引入 `socket` 等库，需要镜像做到：

- 选手通过端口连接到容器/靶机
- 服务启动项目，生成Python会话
- 将会话转发给选手的连接

**使用：**

将py文件/项目放入 `./src` 目录后执行后续操作，文件名建议使用 `main.py` ，便于环境识别，如需更改文件名，请在 `./service/docker-entrypoint.sh` 内更改。

### sagemath_9.6

**环境：**

提供 `SageMath 9.6` + `Python 3.10.3` 的基础环境，并已经添加 `pycryptodome` + `gmpy2` 库，并基于 `socat` 实现服务转发，默认暴露端口位于9999

实现：当选手连接到对应端口（默认为9999端口，默认选手使用 `netcat` ）的时候，运行 `.py项目`，并将会话转发至选手的连接

此环境适用于项目中没有引入 `socket` 等库，并依赖于 `SageMath` 核心，需要镜像做到：

- 选手通过端口连接到容器/靶机

- 服务启动项目，生成SageMath会话

- 将会话转发给选手的连接


**使用：**

直接将SageMath文件/项目放入 `./src` 目录后执行后续操作，文件名建议使用 `main.sage` ，便于环境识别，如需更改文件名，请在 `./service/docker-entrypoint.sh` 内更改

### KOH（NSSCTF_Only）

KOH题目是基于HTTP服务与后端评判系统进行交互的,故题目容器需要启动一个标准的HTTP服务，并对外暴露HTTP服务端口。

为了确保题目能够正常与后端进行交互，HTTP服务需要包含以下路由并进行相应处理：

**upload:**

```python
@app.route('/upload', methods=['POST'])
def upload():
	pass
```

该路由负责接收用户上传的数据。数据将以表单数据的形式进行上传，参数名为file。

例如，后端向容器内的HTTP服务发送请求的代码如下，其中超时时间为5秒：

```python
requests.post(f'http://{url}/upload', files={
'file': (filename, content)
}, timeout=5)
```

如果HTTP服务在5秒内正常处理该路由，并且没有异常发生，应返回以下JSON数据：

```json
{
	"code": 200
}
```

如果遇到异常（例如服务异常、连接异常、超时异常、返回值异常），则直接判定此次结果为**错误**。

（一般情况下，200以外的任何返回代码，我们都记为 **错误** ）

**check:**

```python
@app.route('/check', methods=['POST'])
def check():
	pass
```

当后端完成对/upload路由的访问且没有异常时，将访问/check路由。访问示例代码如下：

```python
requests.post(f'http://{url}/check', timeout=10)
```

超时时间为**10**秒。靶机需要在此时间内评估用户上传内容的得分情况，并返回JSON结果，例如：

```json
{
	"code": 200,
	"score": 100
}
```

如果遇到异常（例如服务异常、连接异常、超时异常、返回值异常），则直接判定此次结果为**错误**。如果以上过程没有异常，判断过程结束，并将得到的score更新为用户的得分。

- 判题靶机目前为一人一机，上次判题完成前无法上传新的文件，无需考虑多线程以及资源抢占的情况。

- 应尽可能保证服务的可用性。对于需要运行时要求的靶机，应使用chroot等沙盒技术来运行独立的进程，以防止用户代码直接控制靶机来控制HTTP服务的返回值。

- HTTP返回数据应确保返回头包含Content-Type: application/json头，而不是直接返回JSON字符串。

**DockerFile文件说明:**

该题为文件上传KOH题，故只需要完成保存文件 比较文件即可判断得分，如果需要进行代码执行，可以参考app.py中注释代码中使用subprocess建立chroot沙盒的方式进行执行。

注意为了安全起见，在Dockerfile中删除了一些包，如有使用需要请手动更改。

```bash
RUN rm -f /home/ctf/usr/local/lib/python3.10/sockert.py && \
rm -f /home/ctf/usr/local/lib/python3.10/sockertserver.py && \
rm -rf /home/ctf/usr/local/lib/python3.10/site-package && \
rm -f /home/ctf/usr/local/lib/python3.10/subprocess.py
```

该靶机为python3靶机，如需使用其他环境，关于chroot部分依然可以参考Dockerfile中对/home/ctf的改造方法（/home/ctf即为沙盒环境根目录）

### MISC

#### pyjail-python_3.10-socat / xinetd

**感谢 [@gtg2619](https://github.com/gtg2619) 师傅对此模板的贡献 **

**环境：**

提供 `Python 3.10` 的基础环境，并已经添加 `pycryptodome` 库，并基于 `socat`  / `xinetd` 实现服务转发，默认暴露端口位于9999

实现：当选手连接到对应端口（默认为9999端口，默认选手使用 `netcat` ）的时候，运行 `server.py`，并将会话转发至选手的连接

镜像做到：

- 选手通过端口连接到容器/靶机
- `socat`  / `xinetd` 服务检测到连接，启动一个 `python3` 会话
- `python3` 通过参数 `-u /home/ctf/server.py` 限制了程序运行时的账户权限为`ctf`，然后在限制环境中启动程序
- `socat`  / `xinetd` 将程序会话转发给选手的连接

**使用：**

将程序文件放入 `./src` 目录后执行后续操作，文件名请修改为 `server.py` 作为文件名，便于镜像定位程序位置

如果需要更改为自己的文件名，需要在 `./config/ctf.xinetd`、`./Dockerfile` 和 `./service/docker-entrypoint.sh` 中进行修改

### PWN

#### ubuntu_16.04 /18.04 / 20.04 /22.04

**环境：**

提供 `Ubuntu 16.04 GLIBC 2.23` / `Ubuntu 18.04 GLIBC 2.27` / `Ubuntu 20.04 GLIBC 2.31` / `Ubuntu 22.04 GLIBC 2.35` 的基础环境，并已经添加 `lib32z1` + `xinetd` 软件包，并基于 `xinetd` 实现服务转发，默认暴露端口位于9999

实现：当选手连接到对应端口（默认为9999端口，默认选手使用 `netcat` ）的时候，运行 `程序文件`，并将会话转发至选手的连接

镜像做到：

- 选手通过端口连接到容器/靶机
- xinted服务检测到连接，启动一个 `chroot` 会话
- `chroot` 通过参数 `--userspec=1000:1000 /home/ctf` 限制了程序运行时的账户权限，并更改了程序运行时的root根目录环境位置为 `/home/ctf` ，然后在限制环境中启动程序
- `xinted` 将程序会话转发给选手的连接

**使用：**

将程序文件放入 `./src` 目录即可，文件名请修改为 `attachment` 作为文件名，便于镜像定位程序位置

如果需要更改为自己的文件名，需要在 `./config/ctf.xinetd`、`./Dockerfile` 和 `./service/docker-entrypoint.sh` 中进行修改

### Web

#### flask-python_3.8 / 3.10

提供 `Python 3.8 + Flask` /  `Python 3.10 + Flask` 的基础环境，默认暴露端口位于8080

直接将Flask文件/项目放入 `./src` 目录即可，Flask项目主文件请使用 `app.py` 作为文件名，便于环境识别Flask项目位置

如使用了 `pycryptodome` 等第三方库，请在 `./Dockerfile` 内补充pip安装语句

#### java-openjdk8

提供 `Openjdk 1.8.0` 的基础环境，默认服务暴露端口由程序决定

适用于基于 `jar` 程序包部署环境的需求

直接将 `jar` 程序包放入 `./src` 目录即可，jar程序包请使用 `app.jar` 作为文件名，便于环境识别 `jar` 程序包

#### jetty-jdk8

提供 `Jetty 9.4.49 Openjdk 1.8.0` 的基础环境，默认服务暴露端口由程序决定

适用于基于 `war` 程序包部署环境的需求

直接将 `war` 程序包放入 `./src` 目录即可，war程序包请使用 `root.war` 作为文件名，便于环境识别 `war` 程序包

#### tomcat-jdk8

提供 `Tomcat 9.0.78 Openjdk 1.8.0` 的基础环境，默认服务暴露端口由程序决定

适用于基于 `war` 程序包部署环境的需求

直接将 `war` 程序包放入 `./src` 

#### LAMP-php80 / LNMP-php73 / nginx-php73

> 部分容器参考 https://github.com/CTFTraining/ 感谢 [陌竹 - mozhu1024](https://github.com/mozhu1024) 师傅 和 [赵总 - glzjin](https://github.com/glzjin) 师傅做出的贡献

`Apache2` +`PHP 8.0.30`+`10.5.21-MariaDB` 的基础环境，默认暴露端口位于 80

- L: Linux alpine
- A: Apache2
- M: MySQL
- P: PHP 8.0
- PHP MySQL Ext
  - mysql
  - mysqli

`Nginx` +`PHP 7.3.33`+`10.6.14-MariaDB` 的基础环境，默认暴露端口位于 80

- L: Linux alpine
- N: Nginx
- M: MySQL
- P: PHP 7.3
- PHP MySQL Ext
  - mysql
  - mysqli

`Nginx` +`PHP 7.3.33` 的基础环境，默认暴露端口位于 80

直接将 PHP 项目放入 `./src` 目录后执行后续操作。

!!! Warning "注意！！"

    **模板默认会将 flag 保存在 数据库中，如果 需要改变flag在数据库中的存放位置，请在./service/docker-entrypoint.sh 中修改相关操作语句**
