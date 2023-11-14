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
### [2023浙江省大学生网络与信息安全决赛-Misc篇](https://blog.zgsec.cn/archives/504.html)  
>by [曾哥](https://blog.zgsec.cn/), 2023-11-12

比赛概述emmmm怎么说呢，难受死了，好多题目都是临门一脚的状态。。。比赛当时是断网环境，真的是可惜了Misc-1：Xcode v5.81# 题目内容直接给了一个 flag.txt，里面有一串字符串2# 解题思路题目提示使用 X encode，于是在 CaptfEncoder 中可以找到 XXencode 编码：解密后，看着像Base编码，遂尝试：成功解出FlagMisc-2：Ez_Signin1...
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
### [计算机网络(谢希仁)](https://xia0ji233.github.io/2023/10/31/ComputerNetwork-Sum/)  
>by [xia0ji233](https://xia0ji233.pro/), 2023-10-31

谢书作为考纲，也是需要好好看看的，接下来时间把谢书再过一遍把。首先列一下考纲吧，然后把重点知识列出来。计算机网络体系结构计算机网络概述计算机网络的概念、组成与功能什么是计算机网络？计算机网络是由若干节点和链路组成的互连的网络。计算机网络的组成？硬件软件的视角：是由软件，硬件及其对应的协议所组成。从工作方式来看：可以由核心部分和边缘部分组成（核心部分负责路由互联，边缘部分负责提供服务）。从组成上看：...
### [域名解析系统](https://xia0ji233.github.io/2023/10/30/DNS/)  
>by [xia0ji233](https://xia0ji233.pro/), 2023-10-30

来学一学DNS吧。简介域名解析系统采用 客户端/服务器（Client/Server）模型，是一种应用层协议，它的作用是把我们所熟知的域名（domain ）翻译成 ip 地址。主要是人们通常乐意记住域名而不是记住ip，就好比学校里老师喜欢叫名字而不是叫你学号，但是学号又是唯一确定的一个学生，而名字是可以重复的。给出一个学生名称，查询对应学号的一个系统就叫学号解析系统，类似的，给出一个域名，查询一个对...
### [从零学习AWD比赛指导手册](https://blog.zgsec.cn/archives/484.html)  
>by [曾哥](https://blog.zgsec.cn/), 2023-10-21

如果你要参加AWD相关比赛，相信本项目能给你带来帮助~手册版本号：V1.2.2-2023/10/21这是一本能让你从零开始学习AWD并深入AWD的手册，我也会根据经验和需求逐步完善相关内容如果你觉得本项目不错，欢迎给我点个Star，万分感谢~~ 有什么新的攻击或者防守的姿势、手法，欢迎与我交流0# 什么是AWD0.1# AWD赛制介绍「 攻防模式 | AWD (Attack With Defens...
### [记一次抑郁诊断和开药用药记录](https://blog.stv.lol/archives/76/)  
>by [Steven Lynn's Blog](https://blog.stv.lol), 2023-10-12

前因自我判定进入比较明显的焦虑抑郁状态已经至少两年多了，前因可看这篇文章[post cid="58" /]当然更主要的还是远因，一些童年成长时的家庭、环境因素，造成了长期表达能力受到压制，进而失去表达情感的能力，比如不会大笑也不会大哭受到这些因素的影响，开始不断地侵蚀我的自我意识，在高中那会就开始出现记忆力下降和无法专注等情况，但在当时由于并未了解过相关心理学知识并不知道这是长期焦虑抑郁所致症状进...
### [一种基于HSTS的防域名劫持的方法](https://blog.stv.lol/archives/75/)  
>by [Steven Lynn's Blog](https://blog.stv.lol), 2023-10-04

事情是这样的：国庆期间国内网络对很多域名进行了污染，其中影响最大的是Minecraft正版验证api以及VSCode官网。当尝试登录或使用上述应用时，其HTTP请求会被重定向到国家反诈中心以及工信部反诈中心的提示页面也因为这波莫名其妙的风波，最近某位朋友的手头大量部署在vercel上的服务被运营商劫持，被301跳转到反诈中心页面对于用户而言，只能切换DNS或者使用代理来防止劫持昨天和一位大佬交流过...
### [香港借记卡：汇丰(HSBC)&amp;中银香港(BOCHK)开卡过程全记录](https://blog.stv.lol/archives/74/)  
>by [Steven Lynn's Blog](https://blog.stv.lol), 2023-10-04

前段时间有幸抢到了去香港的免费机票，于是顺路去香港开了中国银行香港和汇丰香港的账户本文就仅作一个开卡全过程记录吧汇丰(HSBC)周六那天经过了三家中银都没有成功，抱着一丝希望来到了HSBC葵芳分行，试图碰碰运气。当时并没有进行预约。入门后，我先询问前台是否还有号码。因为我没有预约，所以实际上是碰运气。结果，前台小姐姐非常客气地把我带到了一个办公小隔间门口，并告诉我等前一位先生结束之后就可以进去（没...
### [HaE入门到精通：三条影响你一生的HaE规则](https://blog.zgsec.cn/archives/481.html)  
>by [曾哥](https://blog.zgsec.cn/), 2023-10-01

0# 概述最近一段时间项目也比较多，再加上最近还在维护开源项目，所以挺忙的。乘着国庆时间，好好放松一下，顺便借着国庆期间更新一下自己许久未更新的博客哈哈~本篇文章，我们将深入学习著名BurpSuite工具的插件 HaE 的使用和拓展，希望这三条影响你一生的HaE规则能给你带来帮助~读者：你TM还知道回来啊！！！快两个月都没更新了都！！！在此，祝各位师傅们国庆节快乐！！！为国之安全而奋斗，为信息安全...
### [Flask的部署](https://xia0ji233.github.io/2023/10/01/Flask-deploy/)  
>by [xia0ji233](https://xia0ji233.pro/), 2023-10-01

最近在做毕业设计的时候搞了一下，记录一下。环境在使用 app run 去跑 flask 项目的时候，会出现这么一句话：WARNING: This is a development server. Do not use it in a production deployment.大概意思就是，不要用这种方式部署到生产环境中，之前我倒是直接就是这么部署的，但是明显会感觉部分操作会发生卡顿，因此这里顺着...
### [Fourier-Serials](https://xia0ji233.github.io/2023/09/15/Forier-Serials/)  
>by [xia0ji233](https://xia0ji233.pro/), 2023-09-15

Today study something about Fourier serials Taylor SerialAs we all know,Taylor formula give us the way for expressing complicated function as simple polynomial function.We should clearly remember the...
### [Markdown editor CVE of Marktext](https://www.ek1ng.com/MarkdownEditorCVE1.html)  
>by [ek1ng](https://ek1ng.com/), 2023-09-13

无CVE编号 XSS2RCEhttps://github.com/marktext/marktext/issues/2601https://github.com/marktext/marktext/commit/0dd09cc6842d260528c98151c394c5f63d733b62影响 <= 0.16.3 的marktext版本，点击链接触发。POC：123<a href="javasc...
### [Probability Theory（5）](https://xia0ji233.github.io/2023/09/11/Probability-Theory5/)  
>by [xia0ji233](https://xia0ji233.pro/), 2023-09-11

another question about confidence interval. ProblemToday I got a problem about the difference of two normal distribution variables of confidence interval. Obviously it is much harder than  the ratio b...
