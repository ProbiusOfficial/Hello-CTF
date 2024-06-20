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
    ### [浅析Panalog-SQL注入到命令执行(Version<20240130)](https://y4tacker.github.io/2024/06/05/year/2024/6/%E6%B5%85%E6%9E%90Panalog-SQL%E6%B3%A8%E5%85%A5%E5%88%B0%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C-Version-20240130/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-06-05

    e0be8b9b97a0a946bbc3486ed27560158231b3162434d60e608073684a55034f261e783ff562d662dc8e982abf94fc31bebb038fd18a8a51b5e7719d04af116c3352828d6acf04d587ee8d1e5f3019734c5143ad2120b6c364a39b6f614efd646c8bb8...
    ### [ShowDocV3.2.5最新版SQL注入及老版本反序列化分析](https://y4tacker.github.io/2024/05/28/year/2024/5/ShowDocV3-2-5%E6%9C%80%E6%96%B0%E7%89%88SQL%E6%B3%A8%E5%85%A5%E5%8F%8A%E8%80%81%E7%89%88%E6%9C%AC%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%88%86%E6%9E%90/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-05-28

    ShowDocV3.2.5最新版SQL注入及老版本反序列化分析注入从提交记录我们能找到一些提示https://github.com/star7th/showdoc/commit/805983518081660594d752573273b8fb5cbbdb30#diff-b4363835fc1321f859d1faaad5a5a283db695849ca98c4e949fbf1bed8c84a31首...
    ### [浅析通天星CMSV6车载定位监控平台远程代码执行漏洞](https://y4tacker.github.io/2024/05/18/year/2024/5/%E6%B5%85%E6%9E%90%E9%80%9A%E5%A4%A9%E6%98%9FCMSV6%E8%BD%A6%E8%BD%BD%E5%AE%9A%E4%BD%8D%E7%9B%91%E6%8E%A7%E5%B9%B3%E5%8F%B0%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-05-18

    浅析通天星CMSV6车载定位监控平台远程代码执行漏洞写在前面看了一下通告看着还是比较有意思的，通天星CMSV6车载定位监控平台远程代码执行漏洞第一步是通过任意文件读取漏洞，读取log日志获取admin的session信息第二步通过默认密码登录ftp服务器上传文件(或通过后台任意文件上传漏洞)第三步触发上传文件中的恶意代码正文采用了经典SSH架构任意文件读取关于任意文件读取，从官方安全公告也不难看出...
    ### [浅析H3C-CAS虚拟化管理系统权限绕过致文件上传漏洞](https://y4tacker.github.io/2024/05/11/year/2024/5/%E6%B5%85%E6%9E%90H3C-CAS%E8%99%9A%E6%8B%9F%E5%8C%96%E7%AE%A1%E7%90%86%E7%B3%BB%E7%BB%9F%E6%9D%83%E9%99%90%E7%BB%95%E8%BF%87%E8%87%B4%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E6%BC%8F%E6%B4%9E/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-05-11

    浅析H3C-CAS虚拟化管理系统权限绕过致文件上传漏洞写在前面之前四月就关注到了，可是后面不知道什么原因某步下了公众号，今天又被再次提起，当时分析了一半也就是权限相关的调用，现在补上另一半正文鉴权相关配置简析既然和权限绕过相关那么第一步我们必然要去先看看相关配置，在web.xml配置文件当中，可以看到相关的如下配置这里我们只要关注两点，第一servelet需要以/carsrs开头，第二配置文件在/...
    ### [浅析瑞友天翼应用虚拟化系统前台反序列化(V<=7.0.5.1)](https://y4tacker.github.io/2024/05/07/year/2024/5/%E6%B5%85%E6%9E%90%E7%91%9E%E5%8F%8B%E5%A4%A9%E7%BF%BC%E5%BA%94%E7%94%A8%E8%99%9A%E6%8B%9F%E5%8C%96%E7%B3%BB%E7%BB%9F%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-05-07

    浅析瑞友天翼应用虚拟化系统前台反序列化(V<=7.0.5.1)看到应急公告简单分析学习一波，漏洞不算难，代码也比较简单，有些细节还是蛮有意思，算是温故而知新，顺便也捡起一些很久没碰的PHP知识鉴权这个系统文件不多，功能点大多是需要登录，我们可以重点关注一下鉴权部分，在为数不多的控制器当中可以看到，在admin/index两个控制器中部分功能点都存在对于登录用户的判断，分别对应函数checklogi...
    ### [可能是全网第一个粤语Qwen/从零开始的LLM微调教程](https://blog.stv.lol/archives/88/)  
    >by [Steven Lynn's Blog](https://blog.stv.lol), 2024-05-05

    这几天趁着五一假期在家里，做了一下LLM微调大概是全网第一个做粤语微调的Qwen-7B，还请到huggingface和魔搭社区点心支持一下repo:https://huggingface.co/stvlynn/Qwen-7B-Chat-Cantonesehttps://www.modelscope.cn/models/stvlynn/Qwen-7B-Chat-Cantonese今天就整理一下微调的...
    ### [在闲置手机上部署大模型并开启公网访问](https://blog.stv.lol/archives/87/)  
    >by [Steven Lynn's Blog](https://blog.stv.lol), 2024-05-01

    前言前两天微软发布了phi3大模型，是目前少数可以在移动设备上运行的本地语言模型，号称可以和ChatGPT-3.5相当，仅3.8亿参数本文将教你如何在本地部署这个大模型，利用闲置的手机，并且让公网的设备也能远程访问Step 0: Termux下载安装需要注意的是不要从play上下载termux，否则会出现报错，应该从F-droid上下载安装换源：因为你懂的原因，需要把软件源换成国内源清华源的文档里...
    ### [CrushFTP后利用提权分析(CVE-2024-4040)](https://y4tacker.github.io/2024/04/25/year/2024/4/CrushFTP%E5%90%8E%E5%88%A9%E7%94%A8%E6%8F%90%E6%9D%83%E5%88%86%E6%9E%90-CVE-2024-4040/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-04-25

    CrushFTP后利用提权分析(CVE-2024-4040)写在前面这个漏洞的利用最终还是被曝光了，这里也不做重复的分析，具体可以点击访问CVE-2024-4040了解漏洞的详情，在这里作者在分析利用的时候仍然使用的sessions.obj文件去读取历史cookie再做提权的尝试，但在最早的一篇文章当中我也曾提到过，只有在程序退出时才会生成这样一个文件，它充当了服务器的一个缓存功能(CrushFT...
    ### [浅析CrushFTP之VFS逃逸](https://y4tacker.github.io/2024/04/23/year/2024/4/%E6%B5%85%E6%9E%90CrushFTP%E4%B9%8BVFS%E9%80%83%E9%80%B8/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-04-23

    浅析CrushFTP之VFS逃逸写在前面本篇的内容可能并不是最新的漏洞(毕竟我也没最新版代码)，是去年十一月份更新的漏洞，只是当时由于各种各样的项目导致分析被搁置了许久，再次关注它则是因为看到出了新的安全公告，又想起来当时并未分析完全，于是接着之前的工作继续研究（当然另一方面是因为没有各个版本的代码所以不想看最新版的漏洞，另外漏洞的描述中也并不能让我看出什么）再次回顾，从描述中可以看到，漏洞利用的...
    ### [浅析SmartBi逻辑漏洞(3)](https://y4tacker.github.io/2024/04/19/year/2024/4/%E6%B5%85%E6%9E%90SmartBi%E9%80%BB%E8%BE%91%E6%BC%8F%E6%B4%9E-3/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-04-19

    浅析SmartBi逻辑漏洞(3)前言这个系列终于到了第三篇，指条路，如果忘记了可以再看看之前写的文章浅析Smartbi逻辑漏洞浅析Smartbi逻辑漏洞(2)之前我就曾在第二篇末尾提到过（没人继续深入看），仍然存在一个问题，今天这个问题终于得以修复当然老规矩，这里仅分享逻辑漏洞部分补丁绕过思路，不提供完整payload补丁补丁中新增了一个规则12345"rules": [{    "classNa...
    ### [保研or就业---阿里云实习之旅](https://y4tacker.github.io/2024/04/17/year/2022/10/%E4%BF%9D%E7%A0%94or%E5%B0%B1%E4%B8%9A---%E9%98%BF%E9%87%8C%E4%BA%91%E5%AE%9E%E4%B9%A0%E4%B9%8B%E6%97%85/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-04-17

    保研or就业 — 阿里云实习之旅始章​    昨天刚回成都，之前一直在问自己结果真的有那么重要吗，现在我也能鼓起勇气对自己说，不重要了，我的世界属于我，我的人生也没有那么多的观众，我也没必要在意他人的目光，我终于又成长了一点。实习经历​    （经历这部分就挑着重点的或者和时间性有关的说说，我也懒）​    七月中旬收拾好行李独自前往一个陌生的城市，起初对杭州的影响也就是赛博群里说的饭不好吃，说我...
    ### [IP-Guard权限绕过浅析](https://y4tacker.github.io/2024/04/17/year/2024/4/IP-Guard%E6%9D%83%E9%99%90%E7%BB%95%E8%BF%87%E6%B5%85%E6%9E%90/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-04-17

    IP-Guard权限绕过浅析比较适合新手学习的一个审计案例，代码简单无阅读障碍权限绕过IP-Guard采用CodeIgniter框架二次开发，从微步情报看作用仅是”可以绕过权限验证，调用后台接口进行任意文件读取、删除。攻击者可利用该漏洞读取数据库配置信息，进而接管数据库”通常来说，CodeIgniter中的鉴权通常是在控制器中的构造函数中因为代码不多，最后可以发现涉及文件读写的在mApplyLis...
    ### [泛微E-Office10最新远程代码执行漏洞分析](https://y4tacker.github.io/2024/03/27/year/2024/3/%E6%B3%9B%E5%BE%AEE-Office10%E6%9C%80%E6%96%B0%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-03-27

    4051ee28ede465c82f8d9e9a0fa8eab16e3556aa3b07573ca2be1e94b32943219c592cfd0f6b9b8ba9dffa7847e659f691f9c36226794e2e1f461094fd3ba8b45787938c16f361e050587e1b9e88af1e074905380ca645979003bc652f767290e7fd68...
    ### [52PoJie论坛2024春节红包-Web解题思路](https://blog.zgsec.cn/archives/577.html)  
    >by [曾哥](https://blog.zgsec.cn/), 2024-02-19

    0# 概述注：本文原创首发自T00ls论坛，文章链接：https://www.t00ls.com/thread-71282-1-1.html最近刷了刷公众号，偶然看到吾爱破解论坛官方公众号发布了这么一篇文章咦，有春节红包领耶，就点进去看了看，原来是52pojie论坛举办的解题领红包活动官方论坛帖子链接：https://www.52pojie.cn/thread-1889163-1-1.html 总...
    ### [浅析Jenkis任意文件读取(CVE-2024-23897)](https://y4tacker.github.io/2024/01/27/year/2024/1/%E6%B5%85%E6%9E%90Jenkis%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96-CVE-2024-23897/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-01-27

    浅析Jenkis任意文件读取(CVE-2024-23897)很久没更新博客了，还是浅浅更新一下补丁分析首先从官方公告可以看到漏洞其实来源于CLI工具，同时可以看到用户拥有(Overall/Read)权限可以读取整个文件，而如果没有权限则仅能读取第一行同时从commit可以看出[SECURITY-3314] · jenkinsci/jenkins@554f037 ，主要对CLICommand.jav...
    ### [深圳·香港·澳门一星期单人行小记](https://blog.stv.lol/archives/80/)  
    >by [Steven Lynn's Blog](https://blog.stv.lol), 2024-01-25

    前因珠三角一直是我好奇和中意的城市群，尤其是香港。在去年九月的匆忙拜访香港和深圳后仍然意犹未尽，在学校的所有事忙完之后便立刻订机票飞往深圳。深圳抵达买了最便宜的东海航空的航班，并且是深夜的红眼航班。据说这家航司的准点率很差，但好在本次航班的时间都很准时。在机场附近的小酒店休息了一晚上，一早便乘机场线立刻出发地铁站第一件事是前往两个顺路的地铁站盖章打卡，这是一个跨年时的活动，因为章还在客服中心那边所...
    ### [浅析Gitlab未授权密码重置(CVE-2023-7028)](https://y4tacker.github.io/2024/01/12/year/2024/1/%E6%B5%85%E6%9E%90Gitlab%E6%9C%AA%E6%8E%88%E6%9D%83%E5%AF%86%E7%A0%81%E9%87%8D%E7%BD%AE-CVE-2023-7028/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-01-12

    浅析Gitlab未授权密码重置(CVE-2023-7028)补丁在https://gitlab.com/rluna-gitlab/gitlab-ce/-/commit/24d1060c0ae7d0ba432271da98f4fa20ab6fd671，由于问题非常简单，这里就不多说了可以看到在原来的逻辑当中app/models/concerns/recoverable_by_any_email.rb...
    ### [如何判断在IDEA中程序正在运行或正在Debug](https://y4tacker.github.io/2024/01/04/year/2024/1/%E5%A6%82%E4%BD%95%E5%88%A4%E6%96%AD%E5%9C%A8IDEA%E4%B8%AD%E7%A8%8B%E5%BA%8F%E6%AD%A3%E5%9C%A8%E8%BF%90%E8%A1%8C%E6%88%96%E6%AD%A3%E5%9C%A8Debug/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-01-04

    如何判断在IDEA中程序正在运行或正在Debug给大家分享一个有趣又无用的东西，如何判断在IDEA中程序正在运行或正在Debug在这个之前我们首先需要了解一个类ManagementFactory ，它是 Java 标准库中的一个类，它提供了访问运行时系统管理接口的工厂方法。通过 ManagementFactory 类，可以获取包括操作系统、内存、线程、类加载器等在内的多种系统管理信息。一些常用的用...
    ### [感谢，渊龙三周年与龙年展望](https://blog.zgsec.cn/archives/573.html)  
    >by [曾哥](https://blog.zgsec.cn/), 2024-01-01

    1# 概述今天是2024年的第一天，很高兴能再次和大家见面，我是渊龙Sec安全团队的创始人——曾哥 @AabyssZG。首先，在这个日子里面祝各位师傅元旦快乐，在新的一年里面：事业如虎添翼，财运如虹贯日，家庭和谐美满，幸福安康常伴！也很感谢各位师傅，平时给予团队和我的关注和支持~同时，也非常感谢各位团队成员的共同建设和鼎力相助，团队正因为有了你们，才能走到今天！2# 关于渊龙三周年今年是渊龙Sec...
    ### [又又又是一个属性覆盖带来的漏洞](https://y4tacker.github.io/2023/12/28/year/2023/12/%E5%8F%88%E5%8F%88%E5%8F%88%E6%98%AF%E4%B8%80%E4%B8%AA%E5%B1%9E%E6%80%A7%E8%A6%86%E7%9B%96%E5%B8%A6%E6%9D%A5%E7%9A%84%E6%BC%8F%E6%B4%9E/)  
    >by [Y4tacker](https://y4tacker.github.io), 2023-12-28

    又又又是一个属性覆盖带来的漏洞想到最近出了好几个与属性覆盖有关的漏洞，突然想到有一个国产系统也曾经出过这类问题，比较有趣这里简单分享一下，希望把一些东西串起来分享方便学到一些东西前后端框架信息梳理首先简单从官网可以看出所使用的框架信息以及技术选型https://gitee.com/mingSoft/MCMS?_from=gitee_search我们主要关注几个点一个是shiro，一个是freema...

</div>
