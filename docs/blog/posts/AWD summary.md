---
date: 2023-09-08
authors: [probius]
description: >
     攻防模式 | AWD (Attack With Defense) 」是 CTF比赛 「CTF Capture The Flag」几种主要的比赛模式之一.
categories:
  - CTF
links:
  - docs/blog/posts/AWD summary.md
comments: true
---

# 从0开始的AWD攻防攻略
### 简介

「 **攻防模式 | AWD (Attack With Defense)** 」 是 CTF比赛 「**CTF Capture The Flag**」 该模式常见于线下赛，在该模式中，每个队伍都拥有一个相同的初始环境 ( 我们称其为 GameBox )，该环境通常运行着一些特定的服务或应用程序，而这些服务通常包含一些安全漏洞。参赛队伍需要挖掘利用对方队伍服务中的安全漏洞，获取 Flag 以获得积分 ; 同时，参赛队伍也需要修补自身服务漏洞进行防御，以防被其他队伍攻击和获取 Flag。

<!-- more -->
### 类别

根据题目漏洞点或者方向可分为 Web-AWD 和 PWN-AWD，考察内容和对应方向类似。

#### Web-AWD

- **目标**: Web应用或服务的服务器。
- **常见挑战**: SQL注入、XSS（跨站脚本攻击）、CSRF（跨站请求伪造）、文件上传漏洞等 **OWASP(Open Web Application Security Project)**」 漏洞。
- **防守策略**: 高危代码修补，规则过滤，输入输出过滤，基础WAF编写（非通防）等。
- **技能要求**: 需要良好的Web安全基础。

#### PWN-AWD

- **目标**: 底层漏洞利用，例如缓冲区溢出、整数溢出等。
- **常见挑战**: Stack Buffer Overflow、Heap Overflow、Format String Bugs等。
- **防守策略**: 使用各种内存保护机制（如ASLR、NX、Canary）和补丁。
- **技能要求**: 深入了解操作系统、C/C++编程，以及逆向工程。

### 特点

该模式通常具备以下特点 :

- **实时性强**: 攻防模式可以实时通过得分反映出比赛情况，最终也以得分直接分出胜负。
- **全面性**: 该模式不仅测试参赛队伍的攻击能力，还测试他们的防御和团队协作能力。
- **高度动态**: 参赛队伍可能需要不断地更新和调整防御策略，以应对不断变化的攻击环境。

### 元素

该模式通常包含以下元素 :

**目标标志（Flag）**: 类似密码或特殊字符串，存储在服务中，需要被取出以获得积分。

**积分板（Scoreboard）**: 显示各队伍的积分，通常实时更新。

**漏洞利用（Exploit）**: 队伍开发或使用已有的攻击代码，以攻击对手。

**修补（Patch）**: 当找到漏洞后，队伍需要尽快修补自己的系统，防止被攻击。

**日志和监控（Log and Monitor）**: 为了更好地进行防御和攻击，队伍通常需要设置日志和监控系统。

### 规则

该模式通常采用**「  零和积分方式（Zero-Sum Scoring）」** 即 一个队伍从另一个队伍那里获得积分（通常是通过成功的攻击和获取标志）时，被攻击的队伍将失去相应的积分。

通常情况下 :

- 每个队伍会被给定一个初始分数 ( 根据比赛时间 难度等多维度预估 )。
- 通常以 5/10 分钟为一个回合，每回合刷新Flag值或者重置Flag提交冷却时间。
- 每回合内，一个队伍的一个服务被渗透攻击成功（被拿 Flag 并提交），则扣除一定分数，攻击成功的队伍获得相应分数。
- 每回合内，如果队伍能够维持自己的服务正常运行，则分数不会减少；
- 如果一个服务宕机或异常无法通过测试，则会扣分。在不同规则下，扣除的分数处理不同，在一些规则下为仅扣除，一些则为正常的队伍加上平均分配的分数。
- 在某些情况下，环境因自身或者其他原因导致服务永久损坏或丢失，无法恢复，需要申请环境重置。根据比赛规则的不同，一些主办方会提供重置服务，但需要扣除对应分数;也有可能主办方不提供重置服务，则每轮扣除环境异常分。

### 环境

根据物理环境的不同，即 线上AWD 和 线下AWD ，参赛队伍可能会有不同的配置需求，该差异主办方会提前下发材料说明。无论线下还是线上，该模式的环境都具有以下共同特点。

- 环境由 选手终端，GameBox，FlagServer 三部分组成
- 选手终端在线上可采取VPN接入，Web映射转发接入等多种接入方式；选手终端在线下则需要自行配网（通常主办方会给出配网引导文件）方式可能为 WIFI 接入或者 使用网线和标准的 RJ45 接口进行连接。

- GameBox 通常位于同一个D段中，主办方通常会提供ip资产列表，其中 IP 通常与队伍序号或者 ID 对应。
- GameBox 一般使用 ssh 进行登录管理，登录方式为密码或者私钥。
- FlagServer 提供类似Flag提交的相关服务。

### 平台

国内目前能够提供AWD训练的平台：

**[NSSCTF](https://www.nssctf.cn/)**

- 上线不久的AWD功能，题目比较少但持续更新。

- 每隔一段时间会有官方AWD比赛，也可自定义比赛。

**[Bugku](https://ctf.bugku.com/)**

- 国内成熟的AWD供应平台，题目基数大。

- 定期会有排位赛，也可自定义比赛训练。



## NSSCTF 使用

### 流程

请在进行比赛前仔细阅读平台规则。

#### 报名比赛

登录NSSCTP平台后 在上方导航栏中选择 **比赛**

跳转到比赛页面后 在右侧功能区的 **来源** 选择 **自定义竞赛**

**权限** 选择为 **公开** 时 可报名公开比赛 **私密** 同理 但需要提供比赛密码。

![image-20230907044317954](./AWD%20summary.assets/image-20230907044317954.png)

报名成功后，

在比赛开始前 点击 **已报名** 即可进入比赛界面 以配置队伍；

若比赛 **已开始** 或者 **已结束** 则点击绿色的 **进入** 可进入比赛页面

![image-20230907045032263](./AWD%20summary.assets/image-20230907045032263.png)

通过输入队伍token加入队伍。

![image-20230907045312555](./AWD%20summary.assets/image-20230907045312555.png)

比赛开始后，点击 **进入** 按钮进入比赛

![image-20230907135318155](./AWD%20summary.assets/image-20230907135318155.png)

在比赛主页 会显示比赛信息，右侧会显示计分板。

![image-20230907135434508](./AWD%20summary.assets/image-20230907135434508.png)

在赛题选项中查看队伍GameBox信息，计分板会一直跟随显示。

![image-20230907135628004](./AWD%20summary.assets/image-20230907135628004.png)

#### 建立连接

```
beescms(AWD)

题目描述：NULL

攻击标识：curl http://flagserver/flag?token=NSS_XDNEMU
状态：
运行中

题目端口：80

靶机地址：sjcyns1995-1.ecs190.awd.nssctf.cn

SSH端口：22300

SSH用户密码：nss/265i7ckumxqh
```

对于该靶机，我们使用ssh如下指令可建立连接：

```
ssh nss@sjcyns1995-1.ecs190.awd.nssctf.cn -p 22300
```

![image-20230907140014792](./AWD%20summary.assets/image-20230907140014792.png)

通常为了方便管理，我们会依赖一些ssh工具，因为他们会集成一些 诸如 文件下载 修改的交互功能。

![image-20230907140448687](./AWD%20summary.assets/image-20230907140448687.png)

#### 备份加固

通常我们选择将整个 www 文件夹 下载下来

![image-20230907140759999](./AWD%20summary.assets/image-20230907140759999.png)

- 用作备份
- 本地审计加固

#### 攻击得分

另一队视角：

![image-20230907142437736](./AWD%20summary.assets/image-20230907142437736.png)

在对方机器上面任意能够执行命令的地方成功运行攻击标识时，我方得分，对方扣分 ( NSS平台目前为被攻击不扣分) ：

![image-20230907142557435](./AWD%20summary.assets/image-20230907142557435.png)

攻击成功后，在服务器check后则会反应得分情况：（分数数据会稍有延迟）

![image-20230907142755366](./AWD%20summary.assets/image-20230907142755366.png)

每一轮中，对每个队伍只能攻击成功一次：

![image-20230907142901208](./AWD%20summary.assets/image-20230907142901208.png)

### 规则

见 [ [Version 2.4 更新说明 ](https://www.nssctf.cn/note/set/2716)] ，内容如下：

- 在NSS AWD中，你只需要向`flagserver`发送相应的请求即算攻击成功。例如题目界面为

![img](./AWD%20summary.assets/1694032923918-4.png)

- 这里你只需要成功入侵其他队伍/人员靶机后发起这个请求即算攻击成功，你可以通过flagserver的返回内容判断是否攻击成功，响应如下

```Plaintext
code: 0, 攻击成功
code: -1, 参数不全，例如token没有带上
code: -2, 无效的Token参数，请检测token是否正确或者是否被过滤
code: -3, 您不能攻击自己的靶机
code: -4, 该轮已攻击过当前靶机，每轮只会有一次请求会被判定为有效攻击
code: -5, 还未到攻击时间
code: -999, 其他错误
```

- 开赛后你可以通过SSH服务登录自己（队伍）的靶机进行源码下载、防御部署等服务。每个队伍的SSH端口和密码都不相同，你可以通过下列命令进行登录

```Plaintext
ssh nss@靶机地址 -p SSH端口
```

- 同样你也可以使用其他SSH管理软件进行访问。
- **你不需要扫描其他服务器的地址** ，可在题目界面右侧获得本题所有 **靶机地址** （包括自己的也在内）用于编写自动化脚本。
- 同时所有题目除了 **题目端口** 和 **SSH端口** 外，其他端口上不包含任何题目相关信息。你不需要对靶机服务器发起端口扫描。
- 攻击成功的反馈不会实时更新在页面上，你可以通过上述提到的flagserver返回内容来进行判定。
- 服务器会在每轮 **随机** 时间对靶机进行检查，检查内容包括但不限于
  - 特定内容是否存在
  - 特定功能是否可用
  - 特定流程是否完整
- 任意一项检查不可用时将会判断服务器为宕机，并进行扣分，服务器状态会在每轮结束时进行更新，请不要对靶机上的正常功能或题目描述中指定的特殊内容进行修改，被判定宕机你可以通过备份更新等操作重新恢复（服务器状态不会立即更新，同样是在每轮结束时进行更新）

## [WEB]经验技巧

![image-20230908014808577](./AWD%20summary.assets/image-20230908014808577.png)

### 建立信息网络

> 《孙子兵法·谋攻》：「知彼知己，百战不殆。」

**组件发现**：

```bash
find / -name "nginx.conf"                 #定位nginx目录
find / -path "*nginx*" -name nginx*conf   #定位nginx配置目录
find / -name "httpd.conf"                 #定位apache目录
find / -path "*apache*" -name apache*conf #定位apache配置目录
```

**网站发现**：

通常都位于 /var/www/html 中，如果没有试试 find 命令

```bash
find / -name "index.php"   #定位网站目录
```

**日志发现**：

对日志的实时捕捉，除了能有效提升防御以外，还能捕捉攻击流量，得到一些自己不清楚的攻击手段，平衡攻击方和防守方的信息差。

```bash
/var/log/nginx/        #默认Nginx日志目录
/var/log/apache/       #默认Apache日志目录
/var/log/apache2/      #默认Apache日志目录
/usr/local/tomcat/logs #Tomcat日志目录
tail -f xxx.log        #实时刷新滚动日志文件
```

以上是定位常见文件目录的命令或方法，比赛需要根据实际情况类推，善用find命令！

**文件监控**

文件监控能及时木马文件后门生成,及时删除防止丢分。

**其他命令**：

```bash
netstat -ano/-a    #查看端口情况
uname -a           #系统信息
ps -aux ps -ef     #进程信息
cat /etc/passwd    #用户情况
ls /home/          #用户情况
id                 #用于显示用户ID，以及所属群组ID
find / -type d -perm -002      #可写目录检查
grep -r “flag” /var/www/html/  #查找默认FLAG
```

### 口令更改

这里需要更改的口令包括但不限于服务器SSH口令、数据库口令，WEB服务口令以及WEB应用后台口令。

```bash
passwd username    #ssh口令修改
set password for mycms@localhost = password('123'); #MySQL密码修改
find /var/www//html -path '*config*’                #查找配置文件中的密码凭证
```

### 建立备份

除了攻击成功可以让对手扣分，还能破坏对方环境使其宕机被check扣分；同时己方也有可能在修复过程中存在一些误操作，导致源码出错，致使服务停止；对页面的快速恢复时机器必要的，因此页面备份至关重要。

**压缩文件**：

要注意的是 有的题目环境可能不支持 zip

```bash
tar -cvf web.tar /var/www/html
zip -q -r web.zip /var/www/html
```

**解压文件**：

```bash
tar -xvf web.tar -c /var/www/html
unzip web.zip -d /var/www/html
```

**备份到服务器**：

```bash
mv web.tar /tmp
mv web.zip /home/xxx
```

**上传下载文件**：

```bash
scp username@servername:/path/filename /tmp/local_destination  #从服务器下载单个文件到本地
scp /path/local_filename username@servername:/path             #从本地上传单个文件到服务器
scp -r username@servername:remote_dir/ /tmp/local_dir          #从服务器下载整个目录到本地
scp -r /tmp/local_dir username@servername:remote_dir           #从本地上传整个目录到服务器
```

**备份指定数据库**：

数据库配置信息一般可以通过如config.php/web.conf等文件获取。

```bash
mysqldump –u username –p password databasename > bak.sql
```

**备份所有数据库**：

```bash
mysqldump –all -databases > bak.sql
```

**导入数据库**：

```bash
mysql –u username –p password database < bak.sql
```

### 代码审计

将备份下载下来后，立即在本地开展审计工作，确定攻击手段和防御策略，要注意因为awd时间短，且代码量多所以考核的题目应该也不会太难，通常不会涉及到太难的代码审计。

- D盾：查杀后门
- seay源代码审计：审计代码

**一般AWD模式中存在的后门：**

- 官方后门 / 预置后门

  ```bash
  # 可以使用下面的代码进行查找
  find /var/www/html -name "*.php" |xargs egrep 'assert|eval|phpinfo\(\)|\(base64_decoolcode|shell_exec|passthru|file_put_contents\(\.\*\$|base64_decode\('
  ```

- 常规漏洞 如SQL注入 文件上传 代码执行 序列化及反序列化...

- 选手后门（选手后期传入的木马）

### 漏洞修复

在代码审计结束后，及时对自身漏洞进行修补，要注意的是漏洞修复遵循保证服务不长时间宕机的原则, 应当多使用安全过滤函数，能修复尽量修复,不能修复先注释或删除相关代码，但需保证页面显示正常。

### 应急响应

通过命令查看可疑文件：

```bash
find /var/www/html -name *.php -mmin -20                         #查看最近20分钟修改文件
find ./ -name '*.php' | xargs wc -l | sort -u                    #寻找行数最短文件
grep -r --include=*.php  '[^a-z]eval($_POST'  /var/www/html      #查包含关键字的php文件
find /var/www/html -type f -name "*.php" | xargs grep "eval(" |more
```

**不死马查杀**：

杀进程后重启服务，写一个同名的文件夹和写一个sleep时间低于别人的马(或者写一个脚本不断删除别人的马)

比如写个马来一直杀死不死马进程：

```php
<?php system("kill -9 pid;rm -rf .shell.php"); ?>  #pid和不死马名称根据实际情况定
```

**后门用户查杀**：

UID大于500的都是非系统账号，500以下的都为系统保留的账号，使用`userdel -r username` 完全删除账户

**其他查杀**：

部分后门过于隐蔽，可以使用`ls -al`命令查看所有文件及文件修改时间和内容进行综合判断，进行删除。`可以写脚本定时清理上传目录、定时任务和临时目录等`

**进程查杀**

```bash
ps -aux  #查看进程
kill -9 pid #强制进程查杀
```

**关闭端口**

```bash
netstat -anp  #查看端口
firewall-cmd --zone= public --remove-port=80/tcp –permanent #关闭端口
firewall-cmd –reload #重载防火墙
```



*咳咳，本着不重复造轮子的原则（ 才不是懒ww，经验中大部分内容就直接搬过来了，稍微改了下分组和补充了点内容，原 [【先知社区】AWD比赛入门攻略总结](https://xz.aliyun.com/t/10995)
