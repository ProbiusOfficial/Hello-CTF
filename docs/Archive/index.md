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
    ### [x86的保护模式（2）——调用门，中断门，陷阱门与门描述符](https://xia0ji233.github.io/2024/10/05/x86_2/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-10-05

    今天开始学习各种门与门描述符先解决一下上节课的存疑。段选择子的检验尝试将段选择子装入 CS 或 SS 时，会进行检查，通常会产生一个保护异常。而装入其它的段寄存器不会立即检查，会在尝试访问的时候检查权限。前面提到，段描述符当 s=0 时，是一个系统段，而系统段根据 TYPE 域的变化有如下的区别其中就有各种各样的门描述符，包括调用门、中断门、陷阱门，门描述符的结构如下所示长调用和短调用，长跳转与短...
    ### [x86的保护模式（1）——段描述符与段寄存器](https://xia0ji233.github.io/2024/09/17/x86_1/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-09-17

    重新把内核基础学一遍，方便后续学习的展开。x86 是一个非常经典的复杂指令集架构（CISC），它的特点是指令不定长，解析指令时会根据头个字节甚至是第二个字节决定指令解析的长度，作为本篇学习的研究例子。x86 的 CPU 在早期都是以实模式运行的，在 80386 及以后，x86 CPU 新增了分页的虚拟内存机制，同时在 80286 CPU 中就新增了其它运行模式，比如保护模式，本篇将重点学习保护模式...
    ### [Hacking Thymeleaf With Spring(目前最新版，暂不公开)](https://y4tacker.github.io/2024/09/02/year/2024/9/Hacking-Thymeleaf-With-Spring-%E7%9B%AE%E5%89%8D%E6%9C%80%E6%96%B0%E7%89%88%EF%BC%8C%E6%9A%82%E4%B8%8D%E5%85%AC%E5%BC%80/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-09-02

    5d737de200998fa96fe50e14daeae4f936d6c2e263442da7b419cac91b5030bbfa0e26acc7e2d8e6be6b10ef0f9633b6f035c93526330d7b98ff6d625af66aab5e4f3c5bbc3fe17c81df02652f89f741e35999243afb75566bdbedf56b286ad102f569...
    ### [KCTF2024第八题 writeup](https://xia0ji233.github.io/2024/09/02/KCTF2024/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-09-02

    KCTF2024第八题——星门 writeup思路分析拿到题目，是一道典型的写shellcode的题目，白名单系统调用，只允许 read，wait4 和 ptrace。沙箱系统调用号白名单首先想到了切架构，但是它题目也有判断架构。因此就只能利用这个 ptrace 去做文章了。其次应当考虑信息以何种方式回传，因为原进程是连write都不能用的，侧信道也没法，所以便起了一个docker环境去试试。发现...
    ### [浅析禅道利用第二弹之从SQLi到RCE](https://y4tacker.github.io/2024/08/27/year/2024/8/%E7%A6%85%E9%81%93%E5%88%A9%E7%94%A8%E7%AC%AC%E4%BA%8C%E5%BC%B9%E4%B9%8B%E4%BB%8ESQLi%E5%88%B0RCE/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-08-27

    0a1cc6dfc9166f2d46858a423f462b71087aec7840c0b8ebcdf2959a7d6f18fa8621aecaedc917cc165666c63ee06bab620cca80e98e546baee70442d88603ce6d339115193f5d3bd84436b9e9ce4b28aa1bba5160c4b08007dc3307ddd4ccb47c1ea2...
    ### [浅析禅道前台SQL注入(Version<20.2)](https://y4tacker.github.io/2024/08/26/year/2024/8/%E6%B5%85%E6%9E%90%E7%A6%85%E9%81%93%E5%89%8D%E5%8F%B0SQL%E6%B3%A8%E5%85%A5-Version-20-2/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-08-26

    66a1f65ddff5e5fbaee1f939ddf44dcea4029f7582b06e522d1f0b6ddb88495ea7651bf11a6cf64290c5aba6d3cb65ac625a1c15349986dcd67002fc9c92f6f9ff53b981b42f886762bbeb3c53a57f28a78cbe50fc24227b675c76452330256a5de2ba...
    ### [Bamboocloud Pre-Auth RCE](https://y4tacker.github.io/2024/08/24/year/2024/8/Bamboocloud-Pre-Auth-RCE/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-08-24

    27f3e1195b7859eb4bd25dac1acac0a3042d467dab08eb39066b81caee36bbfd6f11e21d2737f808851594385a25c494dbe8b0ef17704abfb466618a0ed859635f7ab2a5b848bb7a8c639d3e37b60cd5ce48012d1f3786ebe99a85c3116eb786d57272...
    ### [浅析泛微ec10权限绕过到命令执行](https://y4tacker.github.io/2024/08/20/year/2024/8/%E6%B3%9B%E5%BE%AEec10%E6%9D%83%E9%99%90%E7%BB%95%E8%BF%87%E5%88%B0%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-08-20

    b19c15fd4dd9cbc0046f840c9697ff767ee735920624715daa4b248a6b55a2d45c1d3b4bd4f596a2a91a250df2f1d27df4dbf60e8474a8609a2deccd60107c31ac3597610ca2a58d2f8a391024c394270809fe49066896744b8b8ba883dd67119b9f0d...
    ### [浅谈帆软在Windows下写文件RCE姿势](https://y4tacker.github.io/2024/08/14/year/2024/8/%E6%B5%85%E8%B0%88%E5%B8%86%E8%BD%AF%E5%9C%A8Windows%E4%B8%8B%E5%86%99%E6%96%87%E4%BB%B6RCE%E5%A7%BF%E5%8A%BF/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-08-14

    写在前面之前上一篇文章中浅析帆软FineVis默认插件前台RCE提到jasper依赖没被加载，当时只是简单做了测试，没有具体看为什么jsp未被解析，只是疑惑了下tomcat下jspservlet配置明明正确配置页面却直接返回空(没有考虑到编译报错这一层问题)，今天无意间看到星球有师傅分享了如何解析jsp的过程，写文章同时也顺带分享下如何实现RCE的两种姿势当然至于为什么是windows，之前的两篇...
    ### [JeecgBoot最新版权限绕过第二弹之内存马注入实录](https://y4tacker.github.io/2024/08/02/year/2024/8/%E6%9C%80%E6%96%B0%E7%89%88JeecgBoot%E7%AC%AC%E4%BA%8C%E5%BC%B9%E4%B9%8B%E5%8F%97%E9%99%90%E6%9D%A1%E4%BB%B6%E4%B8%8B%E7%9A%84%E5%86%85%E5%AD%98%E9%A9%AC%E6%B3%A8%E5%85%A5%E5%AE%9E%E5%BD%95/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-08-02

    2356948a1ad7c887c79f19fc812ea158476a2d05ad621a8e8ad43ad15eed6aa04358928d8237c256deacbb01a81ac6f727557979123b7d202e97fdc8e9cd9984ac9dc71337c850b5e565eea7d7034b42ecae2a86f1ddb3613caa26e2e306a7102f259a...
    ### [浅析JeecgBoot-jmreport最新权限绕过](https://y4tacker.github.io/2024/08/01/year/2024/8/%E6%B5%85%E6%9E%90JeecgBoot-jmreport%E6%9C%80%E6%96%B0%E6%9D%83%E9%99%90%E7%BB%95%E8%BF%87/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-08-01

    a602003e04d22db1e33c89fb4b06650a58b8bd453fabc9118a8a636036f7f24b4ef78306b08678ccfd82cb8b0c3e122d61b8d9c99f724268689a6295f4f071c6c725ead49be7f4550209a0e59fb40f7c913657f7d99bfae52aacfbc177d4b995d6f521...
    ### [帆软channel接口反序列化前世今生及最新版利用链总结](https://y4tacker.github.io/2024/07/28/year/2024/7/%E5%B8%86%E8%BD%AFchannel%E6%8E%A5%E5%8F%A3%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%89%8D%E4%B8%96%E4%BB%8A%E7%94%9F%E5%8F%8A%E5%88%A9%E7%94%A8%E9%93%BE%E6%80%BB%E7%BB%93/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-07-28

    edb75cb95fa274697a13f0de16c2ee476727ef39af866137ce7abba675d366a2667c35534d4818bf16ba3f2a4062b556dfe52391e960c4665bb66cac3069e79df97713e0b70ba674bdbc250f295481e19e3a0d0cb7fe0dab3af3a3419646da40d1709a...
    ### [浅析帆软FineVis默认插件前台RCE](https://y4tacker.github.io/2024/07/26/year/2024/7/%E6%B5%85%E6%9E%90%E5%B8%86%E8%BD%AFFineVis%E9%BB%98%E8%AE%A4%E6%8F%92%E4%BB%B6%E5%89%8D%E5%8F%B0RCE/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-07-26

    75fe1026383dfaa0a967acb72c258091d824449c325b83a7a7fa894da20e58875ee9377f2f6b70632955e7127ad3d74064c0dd2bf0b57f712c6877d79ef90dc5c212f8b446a26e74ef229c33ebc9489a344fa6f8bc94237c48fec5c935d69abe222fe0...
    ### [泛微云桥文件上传与JFinal Bypass](https://y4tacker.github.io/2024/07/26/year/2024/7/%E6%B3%9B%E5%BE%AE%E4%BA%91%E6%A1%A5%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E4%B8%8EJFinal-Bypass/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-07-25

    896043c0663a30f9c5e8fa6f209f299d52ca1152753e3bc67b1969495fc4400355332baaf286443412f0083fee1730aec5c9aec0d05d2a2c383b4d4cee1dd6c0d3da7cd408b09d6a39632c443bf9205fd17da13158e2422a06d052cb98b0f09783fe38...
    ### [泛微EMobile4.0-EMobile6.6 FROM SSRF to RCE](https://y4tacker.github.io/2024/07/25/year/2024/7/EMobile4-0-EMobile6-6-FROM-SSRF-to-RCE/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-07-25

    d689addd663c4fafbe699341f52c070ba95624118db59735eebb4f65e523a94bcaf577129b4857de3a371ac73f86e98abf94d785001bd8f906cd46037ca05e99c46703d1d6f3b935cc7a429aed2d037a94e7dbdf7b591c85a9a23fc8b1646ac88de5e9...
    ### [某软Report高版本中利用的一些细节](https://y4tacker.github.io/2024/07/23/year/2024/7/%E6%9F%90%E8%BD%AFReport%E9%AB%98%E7%89%88%E6%9C%AC%E4%B8%AD%E5%88%A9%E7%94%A8%E7%9A%84%E4%B8%80%E4%BA%9B%E7%BB%86%E8%8A%82/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-07-23

    本文以目前官网的最新版为例，poc估计大家都有了，这里猥琐发育仅以思路分享为主原理浅析从官方公告的细节不难看出，一是让我们删除sqlite驱动，二是限制相关路由的访问，关于路由其实是比较烦人的，这个系统在高版本其实都是基于注解做的配置，所以寻找起来会相对麻烦，通过一番查找我们不难发现在猥琐发育.web.controller.ReportRequestCompatibleService中在代码中不难...
    ### [etw机制分析](https://xia0ji233.github.io/2024/07/08/etw/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-07-08

    尝试做一做模拟类外挂检测鼠标-键盘模拟监控鼠标-键盘模拟外挂相较于直接读/写内存的外挂相比，更加安全和可靠，因为它本质还是模拟人去操作的，只要频率设置不过分，那么不管是客户端检测还是服务端检测都是难以察觉的，因此这几天在思考一个可以检测这类外挂的方案。ETWWindows (ETW) 的事件跟踪提供一种机制来跟踪和记录由用户模式应用程序和内核模式驱动程序引发的事件。 ETW 在 Windows 操...
    ### [浅析GeoServer property 表达式注入代码执行(CVE-2024-36401)](https://y4tacker.github.io/2024/07/03/year/2024/7/%E6%B5%85%E6%9E%90GeoServer-property-%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%B3%A8%E5%85%A5%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C-CVE-2024-36401/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-07-03

    漏洞复现分析从公告来看，漏洞来源于geotools这个库使用apache xpath解析xpath导致的问题https://github.com/geoserver/geoserver/security/advisories/GHSA-6jj6-gm7p-fcvvhttps://github.com/geotools/geotools/pull/4797https://github.com/geo...
    ### [内网渗透信息搜集骚姿势](https://blog.zgsec.cn/archives/608.html)  
    >by [曾哥](https://blog.zgsec.cn/), 2024-06-30

    0# 概述哈哈，各位师傅好久不见啦，最近比较忙，抽空将本文写出来~说到信息搜集，一般大家都会联想到Web外部打点的暴露面信息搜集。但在内网渗透的过程中，信息搜集也是决定成败的决定性因素特别是做持久化渗透中，对内网的信息搜集是尤其重要的，让我们来看看内网渗透之信息搜集骚姿势。[...]...
    ### [某凌OA之一次后台变前台的故事](https://y4tacker.github.io/2024/06/30/year/2024/6/%E6%9F%90%E5%87%8COA%E4%B9%8B%E4%B8%80%E6%AC%A1%E5%90%8E%E5%8F%B0%E5%8F%98%E5%89%8D%E5%8F%B0%E7%9A%84%E6%95%85%E4%BA%8B/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-06-30

    c4f195e047c82f6832aad96b2b9ff0b06473ee6316a0ad546ce47ed7c55f3d2b3da5adb448e1093da0a53ef4866005d7d883c8217c7025cccd4f5ed01fcbbd0220e5e1cfea035436d835a63462858f54f192a02adbcf67627a966c546210ab06f242e1...

</div>
