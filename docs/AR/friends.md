---
isarchive: true
comments: true
glightbox: false
hide:
  - footer
  - toc
  - edit
  - view
---

<div class="grid" style="display: grid;grid-template-columns: 32% 33% 32%;" markdown>

<div class="grid cards" style="display: grid; grid-template-columns: 1fr;" markdown>

-   :material-archive-plus:{ .lg .middle } __最近归档__

    ---

    待更新ww


-   :material-archive-star:{ .lg .middle } __完整归档__

    ---

    待更新ww



</div>

<div class="grid cards" markdown>

-   :material-star-face:{ .lg .middle } __社区推荐__

    ---

    待更新ww


</div>

<div class="grid cards" markdown>

-   :material-account-group:{ .lg .middle } __战队招新__

    ---

    待更新ww


</div>

</div>

<div class="grid cards" markdown>

-   :octicons-people-24:{ .lg .middle } __师傅们__

    ---
    - [ek1ng｜Hidden Gem](https://ek1ng.com/)
    - [曾哥｜弱小和无知不是生存的障碍，傲慢才是！](https://blog.zgsec.cn/)
    - [Y4tacker｜宁静致远，淡泊明志](https://y4tacker.github.io)
    - [4ra1n｜许少！](https://4ra1n.github.io/)
    - [crazymanarmy｜A Noob's Learning Record](https://crazymanarmy.github.io/)
    - [xia0ji233｜Nepnep team](https://xia0ji233.pro/)
    - [Steven Lynn's Blog｜Steven的个人博客](https://blog.stv.lol)

</div>
<div class="grid cards" markdown>

-   :fontawesome-solid-blog:{ .lg .middle } __最近更新__

    ---
    ### [浅析Jenkis任意文件读取(CVE-2024-23897)](https://y4tacker.github.io/2024/01/27/year/2024/1/%E6%B5%85%E6%9E%90Jenkis%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96-CVE-2024-23897/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-01-27

    浅析Jenkis任意文件读取(CVE-2024-23897)很久没更新博客了，还是浅浅更新一下补丁分析首先从官方公告可以看到漏洞其实来源于CLI工具，同时可以看到用户拥有(Overall/Read)权限可以读取整个文件，而如果没有权限则仅能读取第一行同时从commit可以看出[SECURITY-3314] · jenkinsci/jenkins@554f037 ，主要对CLICommand.jav...
    ### [深圳·香港·澳门一星期单人行小记](https://blog.stv.lol/archives/80/)  
    >by [Steven Lynn's Blog](https://blog.stv.lol), 2024-01-25

    前因珠三角一直是我好奇和中意的城市群，尤其是香港。在去年九月的匆忙拜访香港和深圳后仍然意犹未尽，在学校的所有事忙完之后便立刻订机票飞往深圳。深圳抵达买了最便宜的东海航空的航班，并且是深夜的红眼航班。据说这家航司的准点率很差，但好在本次航班的时间都很准时。在机场附近的小酒店休息了一晚上，一早便乘机场线立刻出发地铁站第一件事是前往两个顺路的地铁站盖章打卡，这是一个跨年时的活动，因为章还在客服中心那边所...
    ### [LLVM——Pass模块的调试](https://xia0ji233.github.io/2024/01/23/LLVM4/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-01-23

    记录一下动调dll项目的过程调试DLL的问题正常试过一遍用 clang 作为启动项目或者是用 dll 作为启动项目，但是都不能成功断下来，这里我说一下我所使用的方法。首先在项目属性中开启调试符号项目->属性->配置属性->链接器->调试->生成调试信息选择为生成调试信息（/DEBUG）然后把项目->属性->配置属性->C/C++ ->常规 ->调试信息格式 ，设置为程序数据库（/ZI）打开这两个选...
    ### [LLVM——简单指令混淆](https://xia0ji233.github.io/2024/01/22/LLVM3/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-01-22

    通过LLVM简单学习一下指令混淆。注册Pass添加文件以LLVMHello项目为起点，在上面做改动，首先找到 llvm-project/llvm/lib/transforms/hello 文件夹，添加一个头文件和一个 CPP 源文件，并向 Cmakelists 添加 cpp 源文件，重新生成就可以发现源文件出现在了项目中。我们让 Hello.cpp 仅仅注册 pass 即可，要写新的 pass 最...
    ### [LLVM——LLVMHello](https://xia0ji233.github.io/2024/01/21/LLVM2/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-01-21

    学习一下LLVM的hello world。LLVM简介简单编译原理学过编译原理的人都知道（然而我没学过），编译过程主要可以划分为前端与后端：前端（Front End）会把高级语言源代码翻译成中间表示（IR）。后端（Back End）将IR翻译成目标平台的机器码。对于现在大部分编译器来说，中间表示即汇编语言，并且前端与后端之间强耦合，不会给你接口操作 IR。LLVM 提供了 LLVM IR 这样的中...
    ### [LLVM入门](https://xia0ji233.github.io/2024/01/16/LLVM1/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-01-16

    这个寒假准备学习LLVM，作为奆型C++项目，还是很有学习价值的，且在二进制逆向中经常被使用到，因此非常有学习的必要，这里我准备在 Windows 上编译 LLVM。此时 LLVM 的大版本号在 17。多的概念就不介绍了，因为我自己也还没有完全理解qwq编译首先，作为学习，我们必须要生成一个对自己友好的编译环境，方便自己调试，我们不仅仅是去使用它，而是要去理解+分析，方便我们的二次开发和插件的编写...
    ### [浅析Gitlab未授权密码重置(CVE-2023-7028)](https://y4tacker.github.io/2024/01/12/year/2024/1/%E6%B5%85%E6%9E%90Gitlab%E6%9C%AA%E6%8E%88%E6%9D%83%E5%AF%86%E7%A0%81%E9%87%8D%E7%BD%AE-CVE-2023-7028/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-01-12

    6d1cc102401c745b93e78f65644d42e8acdebe888643ff48d6f7cfdb5192f763857bafd30ff3df8edacec48331a685443e2bfd9b2096789fbde94bf2019e9400ec1373012537fa79b1378fa55fed7d5bbaaee884c63d7e7318c1559a5c176fbdd61c18...
    ### [如何判断在IDEA中程序正在运行或正在Debug](https://y4tacker.github.io/2024/01/04/year/2024/1/%E5%A6%82%E4%BD%95%E5%88%A4%E6%96%AD%E5%9C%A8IDEA%E4%B8%AD%E7%A8%8B%E5%BA%8F%E6%AD%A3%E5%9C%A8%E8%BF%90%E8%A1%8C%E6%88%96%E6%AD%A3%E5%9C%A8Debug/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-01-04

    如何判断在IDEA中程序正在运行或正在Debug给大家分享一个有趣又无用的东西，如何判断在IDEA中程序正在运行或正在Debug在这个之前我们首先需要了解一个类ManagementFactory ，它是 Java 标准库中的一个类，它提供了访问运行时系统管理接口的工厂方法。通过 ManagementFactory 类，可以获取包括操作系统、内存、线程、类加载器等在内的多种系统管理信息。一些常用的用...
    ### [再见2023 | 捡起六便士也不忘心中的月亮](https://www.ek1ng.com/Goodbye2023.html)  
    >by [ek1ng](https://ek1ng.com/), 2024-01-01

    再见2023 | 捡起六便士也不忘心中的月亮写下这篇文章的时候，我刚来到上海入职新公司一周，回看过去一年的竞赛，工作，学习，锻炼等等生活，大体上还是差强人意，但总归有不少值得唏嘘的地方，还得从在北京的生活说起。当时为什么会在北京呢？是去年年末时，有协会学长在群里问有没有学弟想找实习，当时除了CTF以外的经验几乎为零，也从来没有考虑过业界的安全岗都在做什么，我自己想做什么，于是在学长的内推和两轮面试...
    ### [感谢，渊龙三周年与龙年展望](https://blog.zgsec.cn/archives/573.html)  
    >by [曾哥](https://blog.zgsec.cn/), 2024-01-01

    1# 概述今天是2024年的第一天，很高兴能再次和大家见面，我是渊龙Sec安全团队的创始人——曾哥 @AabyssZG。首先，在这个日子里面祝各位师傅元旦快乐，在新的一年里面：事业如虎添翼，财运如虹贯日，家庭和谐美满，幸福安康常伴！也很感谢各位师傅，平时给予团队和我的关注和支持~同时，也非常感谢各位团队成员的共同建设和鼎力相助，团队正因为有了你们，才能走到今天！2# 关于渊龙三周年今年是渊龙Sec...
    ### [2024的目标](https://xia0ji233.github.io/2023/12/31/Summary2023/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2023-12-30

    2023年也快过去了，至此，大学生涯算是快结束了。2023总结2023 01-14经过了很久的申诉，ICPC2023 侥幸拿铜（check）02-01CSAPP看完03-29XCTF FINALS 二等（真的很感谢队里师傅的认可，能让我去参加）04-15ZJCPC 又双叒叕打铁了，哭了04-25自顶向下计算机网络看完05-20CISCN 直接没去（因为一些意外）11-13ZJCTF 二等（单挑省一...
    ### [又又又是一个属性覆盖带来的漏洞](https://y4tacker.github.io/2023/12/28/year/2023/12/%E5%8F%88%E5%8F%88%E5%8F%88%E6%98%AF%E4%B8%80%E4%B8%AA%E5%B1%9E%E6%80%A7%E8%A6%86%E7%9B%96%E5%B8%A6%E6%9D%A5%E7%9A%84%E6%BC%8F%E6%B4%9E/)  
    >by [Y4tacker](https://y4tacker.github.io), 2023-12-28

    又又又是一个属性覆盖带来的漏洞想到最近出了好几个与属性覆盖有关的漏洞，突然想到有一个国产系统也曾经出过这类问题，比较有趣这里简单分享一下，希望把一些东西串起来分享方便学到一些东西前后端框架信息梳理首先简单从官网可以看出所使用的框架信息以及技术选型https://gitee.com/mingSoft/MCMS?_from=gitee_search我们主要关注几个点一个是shiro，一个是freema...
    ### [Apache OFBiz未授权命令执行浅析(CVE-2023-51467)](https://y4tacker.github.io/2023/12/27/year/2023/12/Apache-OFBiz%E6%9C%AA%E6%8E%88%E6%9D%83%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E6%B5%85%E6%9E%90-CVE-2023-51467/)  
    >by [Y4tacker](https://y4tacker.github.io), 2023-12-27

    Apache OFBiz未授权命令执行浅析(CVE-2023-51467)未修复的权限绕过还是之前那个遗留的问题，首先是权限绕过，首先还是做一个简单的回顾关于登录的校验在org.apache.ofbiz.webapp.control.LoginWorker#checkLogin做处理来判断用户是否登录，可以看到这里的判断逻辑非常简单，跳过前两个判断，在后面只需要login返回的不是error，则为...
    ### [Apusic权限绕过浅析](https://y4tacker.github.io/2023/12/26/year/2023/12/Apusic%E6%9D%83%E9%99%90%E7%BB%95%E8%BF%87%E6%B5%85%E6%9E%90/)  
    >by [Y4tacker](https://y4tacker.github.io), 2023-12-26

    Apusic权限绕过浅析真的是浅析前几天去参加补天了，一直想写但是一直抽不出时间学习，由于漏洞比较简单这里也不过多篇幅的讲解，仅分享一些关键的点，在这里关于权限校验Apusic没有使用第三方框架(毕竟是迫真信创产品)而是使用了自定义实现的安全性约束(关于什么安全性约束百度搜很多文章了不作搬运工)去实现了访问控制1234567891011<security-constraint>    <displ...
    ### [Hacking FernFlower](https://y4tacker.github.io/2023/12/22/year/2023/12/Hacking-FernFlower/)  
    >by [Y4tacker](https://y4tacker.github.io), 2023-12-22

    Hacking FernFlower前言​    今天很开心，第一次作为speaker参与了议题的分享，也很感谢补天白帽大会给了我这样的一次机会​    其实本该在去年来讲Java混淆的议题，不过当时赶上疫情爆发，学校出于安全的考虑没让出省。在当时我更想分享的是对抗所有反混淆的工具cfr、procyon，但今年在准备过程中发现主题太大了其实不太好讲，再考虑到受众都是做web安全的，因此我最终还是将...
    ### [Airpods Pro 2上手体验](https://blog.stv.lol/archives/79/)  
    >by [Steven Lynn's Blog](https://blog.stv.lol), 2023-12-16

    Airpods Pro 2 大概算是我今年买的最后一个产品了，也是我馋了很久却一直没买的产品在此之前，我的主力耳机是 Airpods Pro 一代，考虑到一代已经用了将近三年时间，也是时候换一个了没考虑其他耳机的原因主要还是因为我的主要使用的生态产品还是苹果生态为主，Airpods的无缝连接在各设备之间互相流转很方便于是在tb的双十二活动中以1500出头的价格拿下（耳机本体+一年以换代修）开箱包装...
    ### [一周年小记&amp;&amp;那些快乐的技术时光](https://blog.zgsec.cn/archives/548.html)  
    >by [曾哥](https://blog.zgsec.cn/), 2023-12-14

    1# 概述不知不觉，个人博客已经开办了一年了回头看一年前的自己，仍有些感触，遂在闲暇时光提笔写下一些碎碎念数了数我在这一年发表过的博客文章，共计约二十余篇，其实我是真没想到能有那么多文章，比我原定的目标（每个月写一篇原创技术文）多出不少，也算是suprise吧[...]...
    ### [亿赛通电子文档安全管理系统远程代码执行漏洞浅析](https://y4tacker.github.io/2023/12/13/year/2023/12/%E4%BA%BF%E8%B5%9B%E9%80%9A%E7%94%B5%E5%AD%90%E6%96%87%E6%A1%A3%E5%AE%89%E5%85%A8%E7%AE%A1%E7%90%86%E7%B3%BB%E7%BB%9F%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E%E6%B5%85%E6%9E%90/)  
    >by [Y4tacker](https://y4tacker.github.io), 2023-12-13

    亿赛通电子文档安全管理系统远程代码执行漏洞浅析漏洞分析最近天天曝亿赛通的漏洞，又是这个新手向的项目，有点烦其实不是很想写的，本次原理也很简单熟悉的人可能知道这个系统在windows与linux下有点区别，在linux系统下多了一个8021端口相较于CDGServer3服务下又臭又长的代码，这个fileserver下的代码还是很短小的任意文件读取在com.esafenet.fileserver.co...
    ### [年轻人第一块电表：酷安人均一只酷态科10号移动电源简评&amp;杂谈](https://blog.stv.lol/archives/78/)  
    >by [Steven Lynn's Blog](https://blog.stv.lol), 2023-12-11

    前言前段时间有幸去了酷科南京总部参观，被问到有没有酷安人均一只的酷态科10号时汗流浃背了，因为一直以来我都在用闪极的产品，唯一的酷态科产品还是酷态科前身紫米的紫米200W移动电源而对于紫米200W移动电源，我的评价是很优秀，但是太大太重不便于日常携带，并且上次出去旅游的时候外壳被摔坏导致只有一个口可以用了于是在两周前淘宝百亿补贴的一次机会以189元的价格赶紧补票了酷态科10号开箱酷态科10号的包装...
    ### [CrushFTP Unauthenticated Remote Code Execution(CVE-2023-43177)](https://y4tacker.github.io/2023/12/10/year/2023/12/CrushFTP-Unauthenticated-Remote-Code-Execution-CVE-2023-43177/)  
    >by [Y4tacker](https://y4tacker.github.io), 2023-12-10

    CrushFTP  Unauthenticated Remote Code Execution路由分析不像传统套件，这里自己实现了协议的解析并做调用，写法比较死板，不够灵活，在crushftp.server.ServerSessionHTTP可以看到具体的处理过程，代码”依托答辩”，不过漏洞思路值得学习前台权限绕过简单来说，原理是因为程序实现存在匿名访问机制，并且可以通过header污染当前会话的...

</div>
