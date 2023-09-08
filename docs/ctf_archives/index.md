---
comments: true

---
# CTFer档案馆
## List
- [ek1ng｜Hidden Gem](https://ek1ng.com/)
- [曾哥｜弱小和无知不是生存的障碍，傲慢才是！](https://blog.zgsec.cn/)
- [Steven Lynn's Blog｜Steven的个人博客](https://blog.stv.lol)

## Recent Post
### [2023成都CCS大会&amp;&amp;补天城市沙龙有感](https://blog.zgsec.cn/index.php/archives/319/)  
>by [曾哥](https://blog.zgsec.cn/), 2023-09-01

前言今年很巧，8月23日项目结束后，24号2023成都CCS网络安全大会就召开了。我今年刚好在武汉做项目，想了想，结束直接一个飞机飞往成都，开启了本次成都安全之旅。成都的师傅们都很热情，也结识了不少新的朋友，参加了成都CCS大会以及补天城市沙龙，感觉收获颇多，故写本文记录一下。由于参加项目和大会的缘故，博客已经一个半月还未更新了，直到今日才有闲暇之时来落笔本文，各位师傅见谅哈哈。补天城市沙龙合照：...
### [渗透基本思路总结](https://www.ek1ng.com/Summary%20of%20penetration%20ideas.html)  
>by [ek1ng](https://ek1ng.com/), 2023-08-29

最近做了一阵子攻防相关的事，正好最近国护结束，做个总结，简单写一下渗透的基本思路（Check List）。不同的标题间内容并不完全独立，在实战中，比如先钓鱼获取到一台个人PC，但这台PC并不在办公网。而后通过收集个人PC的信息，能够登陆外网其他站点的后台，配合一个后台RCE进入办公网/生产网。这其中就有钓鱼，也有外网打点的部分。资产收集资产搜集通俗说就是“了解目标有什么东西”，讲究一个越全越好。路...
### [Java RMI 攻击梳理总结](https://www.ek1ng.com/java-rmi-attack.html)  
>by [ek1ng](https://ek1ng.com/), 2023-07-26

RMI 是什么定义RMI（Remote Method Invocation）是远程方法调用，类似RPC（Remote Procedure Calls）。RPC是打包和传送数据结构，而在Java中，通常传递一个完整的对象，包含数据和操作数据的方法。通过RMI，能够让客户端JVM上的对象，像调用本地对象一样调用服务端JVM上的对象。RMI引入了 Stubs（客户端存根）和 Skeletons（服务端骨...
### [重学 Java 反射机制](https://www.ek1ng.com/java-reflect-learning.html)  
>by [ek1ng](https://ek1ng.com/), 2023-07-25

近期跟一些java的最新漏洞，发现自己的语言基础太差了，跟着p牛的java安全漫谈重新学一下反射，p牛的文章确实是讲复杂的东西讲的浅显易懂。反射的定义对象可以通过反射获取对应的类，类可以通过反射获取所有方法，拿到的方法可以调用，这种机制就是反射。反射机制在安全方面的意义例如我们要完成RCE，但代码中绝大多数时候并没有Runtime，ProcessBuilder等常见的用于命令执行的类来让我们调用。...
### [java-sec-code 代码审计靶场题解](https://www.ek1ng.com/java-sec-code.html)  
>by [ek1ng](https://ek1ng.com/), 2023-07-20

这个靶场包含了各类基本漏洞在java语言上的场景以及java安全特有的JNDI注入，反序列化，表达式注入等等，并且给出了相关的利用手段和修复方案。java-sec-code搭建环境可以用Docker搭建，不过想了想不太熟练java的包管理和web server部署这一套，并且本地起相比于容器也方便调试，于是决定本地起一份。由于我是archlinux，包管理安装的都是最新的jdk版本，靶场的jdk版...
### [当无回显RCE碰上Win服务器](https://blog.zgsec.cn/index.php/archives/306/)  
>by [曾哥](https://blog.zgsec.cn/), 2023-07-17

0# 概述在日常的渗透过程中，总会碰到一些RCE漏洞，无回显的RCE漏洞更是家常便饭。对于无回显的漏洞利用，网上有不少文章，但我看了半天，都是Linux系统的当无回显RCE漏洞碰上Win服务器，我们又该何去何从呢？故创建本文做个记录本人才疏学浅，如本人有所疏漏，也望各位师傅指点一番1# 无回显上线C2遇到无回显的RCE漏洞，上线C2是不二之选，但这部分并不是今天的重点：上传C2到服务器一般有以下操...
### [CrewCTF 2023 Web Writeup](https://www.ek1ng.com/2023CrewCTFWP.html)  
>by [ek1ng](https://ek1ng.com/), 2023-07-14

环境还在，赛后看看题，一共四道Web，都挺有意思的。sequence_galleryDo you like sequences?http://sequence-gallery.chal.crewc.tf:8080/ 123456789101112131415sequence = request.args.get('sequence', None)if sequence is None:    re...
### [渗透必备：使用Proxifier玩转代理](https://blog.zgsec.cn/index.php/archives/278/)  
>by [曾哥](https://blog.zgsec.cn/), 2023-07-02

0# 概述在日常的渗透过程中，不管是前期的外部打点还是后渗透，代理总是绕不开的话题。在前期的外部打点过程中，扫描和渗透测试会不断受到WAF的拦截，需要不停的更换IP进行扫描和渗透测试；而在后期的后渗透过程中，通过Frp和Nps等等工具从入口点出网之后，也需要对接代理进入目标内网进行内网渗透。本文内容是我个人自己摸索出来的，也有可能别的师傅也有类似的方法哈哈。1# Proxifier介绍本文我们需要...
### [云原生安全分享会材料](https://www.ek1ng.com/cloudsecurity.html)  
>by [ek1ng](https://ek1ng.com/), 2023-06-28

这是一篇用于给协会小学弟们分享的文章，粗略从各个角度讲了一讲，有任何问题都欢迎联系我交流，email：ek1ng@qq.com。基础知识🧀在开始之前，你需要能够基本掌握Docker和Kubernetes的使用。基本使用推荐看官方文档，配合一些教程动手尝试。https://www.docker.com/Docker 能区分镜像/容器，能基本使用命令，能写Dockerfile，粗略了解原理即可。htt...
### [SQL注入恶劣环境之可执行文件上传骚姿势](https://blog.zgsec.cn/index.php/archives/258/)  
>by [曾哥](https://blog.zgsec.cn/), 2023-06-01

0# 概述在前期Web打点成功获得对应权限后，就进入了后渗透（提权、内网渗透、域渗透）的阶段，但是在有些时候，总会出现各种各样奇怪的情况，在此也分享一些经验出来。最近在打红队外援碰到了一个站点存在SQL注入，于是尝试用SqlMap对网站进行注入，发现注入成功，但由此也引发了一系列问题。可能你看完本篇文章，会觉得原理其实很简单。但试问你自己，在面对以下情况的时候，能想到通过这样的手法达成你的目的吗？...
### [阿里云 BrokenSesame RCE漏洞分析](https://www.ek1ng.com/BrokenSesame.html)  
>by [ek1ng](https://ek1ng.com/), 2023-05-12

学习了Wiz团队发表的文章 https://www.wiz.io/blog/brokensesame-accidental-write-permissions-to-private-registry-allowed-potential-r，有很多巧妙的利用方法可以学习Wiz Research在文章中披露了被命名为BrokenSesame的一系列阿里云数据库服务漏洞，会导致未授权访问阿里云客户的Po...
### [2023西湖论剑·数字安全大会有感](https://blog.zgsec.cn/index.php/archives/214/)  
>by [曾哥](https://blog.zgsec.cn/), 2023-05-12

前言今年终于抽空去参加西湖论剑·数字安全大会了，参加后感触颇多，回来的路上就想着写一篇文章来分享一下此行的收获。但苦于最近事务繁多，直到今日才有闲暇之时来落笔本文，各位师傅见谅。本来我们有四个人一块同行的，我和皓哥、垚垚以及俊哥，可惜中途由于私事，俊哥中途离开了我们回老家了。这是我们三个在西湖论剑的现场合影：PS：横跨整个杭州来参会，脚都要走废了哈哈注明：本文图片比较多，可以往下拉跳过图片，看一下...
### [Mysql是如何存储用户账号密码](https://www.ek1ng.com/mysql_password_storage.html)  
>by [ek1ng](https://ek1ng.com/), 2023-05-06

研究这个问题主要是基于主机安全的一个需求场景，即在能够访问主机文件系统的情形下，如何在代码中通过读文件拿到Mysql的账号密码，并且做对应的安全检测，例如检测是否存在弱密码。账号密码存在哪首先，mysql的用户密码是存储在一个叫做mysql的数据库的user数据表中的，这是一张系统表。mysql5.712345FROM mysql:5.7ENV MYSQL_ROOT_PASSWORD=rootEX...
### [五一小记](https://blog.zgsec.cn/index.php/archives/210/)  
>by [曾哥](https://blog.zgsec.cn/), 2023-05-01

概述今天是五一劳动节，先祝各位奋斗在一线的劳动者节日快乐！！！各位看到这篇文章的师傅们，你们也辛苦了，让我们一起做一名光荣的劳动者~这个月，算是最忙的一个月不为过了，不挺的面试、牵线搭桥、考证+比赛让人喘不过气来。说实话，我自己感觉身心俱疲，对各种事务都有些不上心了。但好在，随之而来的五一假期算是能给自己放松一下，顺便调整一下自己的心态。假期里面打开自己的博客看了一眼，博客已经有一个月没更新了，后...
### [Kubernetes 入门学习笔记](https://www.ek1ng.com/k8s-learning.html)  
>by [ek1ng](https://ek1ng.com/), 2023-04-25

仅为学习笔记，建议参考如下文档https://kubernetes.io/zh-cn/docs/home/https://github.com/guangzhengli/k8s-tutorialshttps://minikube.sigs.k8s.io/docs/基础概念K8s组件Control Plane Components控制平面组件主要为集群做全局决策，比如资源调度，以及检测和响应集群事件...
### [Rego在云原生安全场景的使用](https://www.ek1ng.com/rego.html)  
>by [ek1ng](https://ek1ng.com/), 2023-04-19

作者仅是云原生安全相关和opa相关生态的初学者，在此分享一些学习笔记和经验总结，以下是参考文章：http://blog.newbmiao.com/2020/03/13/opa-quick-start.htmlhttps://github.com/NewbMiao/opa-koanshttps://moelove.info/2021/12/06/Open-Policy-Agent-OPA-%E5%8...
### [MinIO信息泄漏漏洞分析](https://www.ek1ng.com/CVE-2023-28432.html)  
>by [ek1ng](https://ek1ng.com/), 2023-04-02

参考文章：https://mp.weixin.qq.com/s/GNhQLuzD8up3VcBRIinmgQhttps://github.com/minio/minio/security/advisories/GHSA-6xvq-wj2x-3h3q漏洞比较新，很多师傅也写了博客记录了自己的尝试，很多地方可能写的不是特别明确，这里也结合了一些自己的思考去尝试分析。漏洞复现可以用vulhub上配好的d...
### [开源项目信息泄露笔记](https://blog.zgsec.cn/index.php/archives/205/)  
>by [曾哥](https://blog.zgsec.cn/), 2023-04-01

目前本文并不完善，后续会持续更新0# 概述与现状当我们对一些项目进行渗透、审计的时候，以及HW红蓝攻防时，对目标的开源项目信息泄露就是重要一环整体现状2020年春，Unit 42研究人员通过GitHub Event API 分析了超过24,000份GitHub公开数据，发现有数千个文件中可能包含敏感信息在24,000份GitHub公开数据中，存在以下泄露：4109个配置文件2464个API密钥23...
### [安全测试工具（AST）学习笔记](https://www.ek1ng.com/iast.html)  
>by [ek1ng](https://ek1ng.com/), 2023-03-20

主要参考了土爷的博客文章以及一些搜到的其他文章进行的学习https://lorexxar.cn/2020/09/21/whiteboxaudithttps://cloud.tencent.com/developer/article/2235686https://tttang.com/archive/1375/https://www.freebuf.com/sectool/290671.html为什...
### [PHP从零学习到Webshell免杀手册](https://blog.zgsec.cn/index.php/archives/197/)  
>by [曾哥](https://blog.zgsec.cn/), 2023-03-18

手册概述手册版本号：V1.3-20230807 这是一本能让你从零开始学习PHP的WebShell免杀的手册，同时我会在内部群迭代更新开源地址： https://github.com/AabyssZG/WebShell-Bypass-Guide 如果师傅们觉得不错，可以给我点个Star哈哈~有什么新的WebShell免杀姿势、手法，欢迎与我交流渊龙Sec安全团队-AabyssZG整理本资料仅供学习...
