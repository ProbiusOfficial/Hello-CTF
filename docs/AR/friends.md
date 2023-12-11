---
comments: true

---
# CTFer档案馆
## List
- [ek1ng｜Hidden Gem](https://ek1ng.com/)
- [曾哥｜弱小和无知不是生存的障碍，傲慢才是！](https://blog.zgsec.cn/)
- [Y4tacker｜宁静致远，淡泊明志](https://y4tacker.github.io)
- [4ra1n｜许少！](https://4ra1n.github.io/)
- [crazymanarmy｜A Noob's Learning Record](https://crazymanarmy.github.io/)
- [xia0ji233｜Nepnep team](https://xia0ji233.pro/)
- [Steven Lynn's Blog｜Steven的个人博客](https://blog.stv.lol)

## Recent Post
### [Apache Struts2 文件上传分析(S2-066)](https://y4tacker.github.io/2023/12/09/year/2023/12/Apache-Struts2-%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E5%88%86%E6%9E%90-S2-066/)  
>by [Y4tacker](https://y4tacker.github.io), 2023-12-09

Apache Struts2 文件上传分析(S2-066)struts2也很久没出过漏洞了吧，这次爆的是和文件上传相关相关的commit在https://github.com/apache/struts/commit/162e29fee9136f4bfd9b2376da2cbf590f9ea163首先从commit可以看出，漏洞和大小写参数有关，后面会具体谈及同时结合CVE描述我们可以知道，大概和...
### [某某通漏洞浅析](https://y4tacker.github.io/2023/12/08/year/2023/12/%E6%9F%90%E6%9F%90%E9%80%9A%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/)  
>by [Y4tacker](https://y4tacker.github.io), 2023-12-08

e1bd3e68fe0e95aad543147235f13aa8c07db101f08238b29c49348e526ca2c395ff16b5184fe4ee67b8dd1840f69936917a685390975ecb78405622c312487d5e6b45d97870e169a38f37bd7a2e95cc5b864202dba1787e366b00f3973f1aa3686ad8...
### [Linux ptrace](https://xia0ji233.github.io/2023/12/03/Ptrace/)  
>by [xia0ji233](https://xia0ji233.pro/), 2023-12-03

这次学习Linux进程调试相关的知识。调试对于二进制选手来说，调试的重要性不言而喻，对于Linux来说，基本就是 gdb 一家独大，其余插件只是给gdb起了锦上添花的一些作用罢了，那么下面就来学习一下 gdb 的内核。ptrace在Linux调试程序，离不开一个系统调用就是 ptrace（%rax=101,%eax=26），来看看这个函数原型：12long ptrace(enum __ptrace...
### [Apache ActiveMQ Jolokia远程代码执行不依赖JDK打法](https://y4tacker.github.io/2023/11/30/year/2023/11/%E6%9F%90%E7%B3%BB%E7%BB%9F%E6%9C%80%E6%96%B0%E5%89%8D%E5%8F%B0RCE%E5%88%86%E6%9E%90/Apache-ActiveMQ-Jolokia%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C%E4%B8%8D%E4%BE%9D%E8%B5%96JDK%E6%89%93%E6%B3%95/)  
>by [Y4tacker](https://y4tacker.github.io), 2023-11-30

Apache ActiveMQ Jolokia远程代码执行不依赖JDK打法想着最近连写了几篇加密博客有点对不起看我博客的粉丝了，今天抽空简单分享一个姿势影响版本大概测了一下Apache ActiveMQ 5.16.x系列无log4j2的mbeanApache ActiveMQ 5.17.x系列漏洞版本受影响初探从网上已公开的打法可以知道使用jdk.management.jfr:type=Fligh...
### [Apache ActiveMQ Jolokia远程代码执行(CVE-2022-41678)简析及绕Waf技法](https://y4tacker.github.io/2023/11/29/year/2023/11/Apache-ActiveMQ-Jolokia%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C-CVE-2022-41678-%E7%AE%80%E6%9E%90%E5%8F%8A%E7%BB%95Waf%E6%8A%80%E6%B3%95/)  
>by [Y4tacker](https://y4tacker.github.io), 2023-11-29

b911718fdd890810916fcf22cb8016ca11ae7d872d624941bd9b20d0cf7e4036a45e816cf5955164cc4e0d7bc4e06277d1f41e412de1243b7603f6b8db578947e40f8bad6233f702a2ae224c03f173d620410ea4abfdb0fba73dbe0f45d4327f2d262b...
### [HITCTF2023题解](https://xia0ji233.github.io/2023/11/27/HITCTF2023/)  
>by [xia0ji233](https://xia0ji233.pro/), 2023-11-27

重铸mininep荣光，我辈义不容辞战队信息战队名称：mininep本次比赛附件，WEB和Reverse就不放了，主要是 Pwn，MISC和Cry。因为超过了 Github 的上传限制，因此单独放 MISC 的音频题附件Pwnscanf会先读入一个序列，然后根据序列去调用功能。[ ：分配大小为 0x20 的堆块，并读入一个 int 数据。] ：输出堆块的 int 数据并 free 掉堆块并且马上将...
### [某系统最新前台权限绕过分析](https://y4tacker.github.io/2023/11/26/year/2023/11/%E6%9F%90%E7%B3%BB%E7%BB%9F%E6%9C%80%E6%96%B0%E5%89%8D%E5%8F%B0%E6%9D%83%E9%99%90%E7%BB%95%E8%BF%87%E5%88%86%E6%9E%90/)  
>by [Y4tacker](https://y4tacker.github.io), 2023-11-26

f8699a5360fe9f42f41b98c5cc3203c7cbe9b0e7b973590e7fd52b27b474d14b936d11c308462091084b3defadb8d998d3381b897b97ebf2923245170a43a3ab58393c3b23741eb3526a32145ff738802bd1881ac66ab453888465f4f27015647ba7da...
### [某系统最新前台RCE分析](https://y4tacker.github.io/2023/11/26/year/2023/11/%E6%9F%90%E7%B3%BB%E7%BB%9F%E6%9C%80%E6%96%B0%E5%89%8D%E5%8F%B0RCE%E5%88%86%E6%9E%90/)  
>by [Y4tacker](https://y4tacker.github.io), 2023-11-26

c2aca488ade3c6d7b8f66283f4fa5a919b5dffc64099fc7db64c2f89071e8f6e918d82a30070255c82ae3a58fc0fae28d71d31e89829a30577fbbf97e15fbb296a140d9667e248db8ee6fcb90c7b88bd06693de9c753ec30a7d6b12f9f2c47f1fd21cc...
### [一场跨越十年的超时空思维碰撞](https://blog.zgsec.cn/archives/535.html)  
>by [曾哥](https://blog.zgsec.cn/), 2023-11-25

0# 概述最近反正也没啥事情干，突然看到朋友 青山ya 师傅审计出了腾讯开源的xSRC系统的逻辑漏洞，于是我就没事干，把开源的xSRC源码拉下来跟着审计了一波但在审计的过程中，我在TSRC（腾讯安全应急响应中心）的在线平台中，看到了一个好玩的东西：ScanWebshell：此工具可用于检测php Webshell咦，我平时不也在研究WebShell的免杀吗？兴趣使然，我打算下载下来看看[...]...
### [I Doc View全版本前台RCE漏洞分析汇总](https://y4tacker.github.io/2023/11/22/year/2023/11/I%20Doc%20View%E5%85%A8%E7%89%88%E6%9C%AC%E5%89%8D%E5%8F%B0RCE%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90%E6%B1%87%E6%80%BB/)  
>by [Y4tacker](https://y4tacker.github.io), 2023-11-22

a74529e06839b00590019b3586ee8768e1429c91fb6e284b9e29886c48d32fe4096cab8993661d6b4761d862048986990a1e631c6094927b39cb47d72b8a0e59f33fa5458fba36a86f95dd6613af37d9474c70c33a9fd0989c3a2ae49c64e3923ed130...
### [Pwnable.kr-otp](https://xia0ji233.github.io/2023/11/14/pwnable_otp/)  
>by [xia0ji233](https://xia0ji233.pro/), 2023-11-14

pwnable.kr-otp，一次性密码验证（one time password）漏洞分析。题目分析同样来看看题目描述：I made a skeleton interface for one time password authentication system.I guess there are no mistakes.could you take a look at it?hint : not...
### [2023浙江省大学生网络与信息安全决赛-Misc篇](https://blog.zgsec.cn/archives/504.html)  
>by [曾哥](https://blog.zgsec.cn/), 2023-11-12

比赛概述这是2023浙江省大学生网络与信息安全决赛的Misc篇，将本次比赛的相关题目进行了整理，欢迎各位师傅的复现和交流学习~比赛总体emmmm怎么说呢，难受死了，好多题目都是临门一脚的状态。。。比赛当时是断网环境，真的是可惜了相关题目附件已经上传到开源项目，题库地址：https://github.com/CTF-Archives/2023-zjsdxs/如有需要，从上面拉取题目即可[...]...
### [某系统全版本前台RCE绕过总结](https://y4tacker.github.io/2023/11/12/year/2023/11/%E6%9F%90%E7%B3%BB%E7%BB%9F%E5%85%A8%E7%89%88%E6%9C%AC%E5%89%8D%E5%8F%B0RCE%E7%BB%95%E8%BF%87%E6%80%BB%E7%BB%93/)  
>by [Y4tacker](https://y4tacker.github.io), 2023-11-12

63ad3c308aa90afd6725b0adbc5aaf396fe6a49769435089ef5574bd32ca40449c3e06df20814f543efe985c53634aa612382f7cfbf67a5114f90aa226b1f3a2117126741fb1bce45422cc45d5b0203b4dc897356c33545fc1853dbda4a028d98a21c3...
### [OJ-Bypass-WAF](https://xia0ji233.github.io/2023/11/09/OJ-Bypass-WAF/)  
>by [xia0ji233](https://xia0ji233.pro/), 2023-11-09

第一次做生产环境的项目和运维，也是出现了很多问题，下面是遇到的其中一个问题。绕过WAF向OJ提交代码的方案随着网络安全越来越严格，防火墙也是做了很多升级，有些防火墙为了防止上传恶意代码甚至暴力匹配某些字符或者是字符组合，这对于ACM选手来说是不太友好的，因为特殊的需要，我们经常要向服务器提交我们写的代码，里面难免会出现一些所谓的“恶意字符”，因此需要对OJ进行特殊地处理来使得代码不被WAF拦截。一...
### [Pwnable.kr-lotto](https://xia0ji233.github.io/2023/11/07/pwnable_lotto/)  
>by [xia0ji233](https://xia0ji233.pro/), 2023-11-07

pwnable.kr-lotto  又是一个很有趣的逻辑漏洞分析。题目分析根据所给信息Mommy! I made a lotto program for my homework.do you want to play?ssh lotto@pwnable.kr -p2222 (pw:guest)我也是搜了一下 lotto 是什么意思，大概好像是彩票的意思，它给了C源码和二进制文件，先来看看源码吧：1...
### [Pwnable.kr-blackjack](https://xia0ji233.github.io/2023/11/07/pwnable_blackjack/)  
>by [xia0ji233](https://xia0ji233.pro/), 2023-11-07

pwnable.kr-blackjack 一个很有趣的逻辑漏洞分析。题目分析根据所给信息Hey! check out this C implementation of blackjack game!I found it onlinehttp://cboard.cprogramming.com/c-programming/114023-simple-blackjack-program.htmlI l...
### [Pwnable.kr-coin1](https://xia0ji233.github.io/2023/11/07/pwnable_coin1/)  
>by [xia0ji233](https://xia0ji233.pro/), 2023-11-07

pwnable.kr-coin1 简单的二分查找。题目分析根据所给信息Mommy, I wanna play a game!(if your network response time is too slow, try nc 0 9007 inside pwnable.kr server)Running at : nc pwnable.kr 9007这题没有给我们账号，不过可以用其它的账号去连接欸...
### [Pwnable.kr-shellshock](https://xia0ji233.github.io/2023/11/06/pwnable_shellshock/)  
>by [xia0ji233](https://xia0ji233.pro/), 2023-11-06

pwnable.kr-shellshock 这一关仅仅是帮助我们复现shellshock漏洞的。题目分析根据所给信息Mommy, there was a shocking news about bash.I bet you already know, but lets just make it sure :)ssh shellshock@pwnable.kr -p2222 (pw:guest)连接...
### [Pwnable.kr-mistake](https://xia0ji233.github.io/2023/11/06/pwnable_mistake/)  
>by [xia0ji233](https://xia0ji233.pro/), 2023-11-06

Pwnable.kr-mistake 这一关HINT已经给了，但是光看C真的很难分析出来题目分析根据所给信息We all make mistakes, let’s move on.(don’t take this too seriously, no fancy hacking skill is required at all)This task is based on real eventThan...
### [pwnable.kr-leg](https://xia0ji233.github.io/2023/11/06/pwnable_leg/)  
>by [xia0ji233](https://xia0ji233.pro/), 2023-11-06

Pwnable.kr-leg 这一关挺有意思的，也不是很难，也借此学习一下ARM汇编。题目分析根据所给信息Daddy told me I should study arm.But I prefer to study my leg!Download : http://pwnable.kr/bin/leg.cDownload : http://pwnable.kr/bin/leg.asmssh leg...
