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
    ### [东方通TongWeb最新反序列化利用分析](https://y4tacker.github.io/2025/11/13/year/2025/11/%E4%B8%9C%E6%96%B9%E9%80%9ATongWeb%E6%9C%80%E6%96%B0%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%88%A9%E7%94%A8%E5%88%86%E6%9E%90/)  
    >by [Y4tacker](https://y4tacker.github.io), 2025-11-13

    d89a383fba0dfbe5e04ae635e1bec07fae4cba8f85006ae22cb5a929bd201cec852660f67fcdd81091d1e7f6c1b6432c75a209103db66625e82a285d341bc3f6d8c9ac2868a9345f1ecef5b809b5ee8befddb13f780436598aa19443aaae13f6af6784...
    ### [No-FTP:高版本JDK如何通过XXE-OOB读取多行文件](https://y4tacker.github.io/2025/11/10/year/2025/11/No-FTP-%E9%AB%98%E7%89%88%E6%9C%ACJDK%E5%A6%82%E4%BD%95%E9%80%9A%E8%BF%87XXE-OOB%E8%AF%BB%E5%8F%96%E5%A4%9A%E8%A1%8C%E6%96%87%E4%BB%B6/)  
    >by [Y4tacker](https://y4tacker.github.io), 2025-11-10

    No-FTP:高版本JDK如何通过XXE-OOB读取多行文件写在前面在XXE（XML External Entity Injection）的实际利用中，当遇到没有回显的场景时，通常需要通过OOB（Out-of-Band）方式将数据带出。传统的XXE-OOB利用中，如果目标文件包含换行符，直接通过HTTP协议外带会因为HTTP请求格式的限制(sun.net.www.protocol.http.Htt...
    ### [强网杯S9初赛Reverse writeup](https://xia0ji233.github.io/2025/10/20/qwb2025_pre_reverse/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2025-10-20

    强网杯初赛的这道 re 挺有意思的，做了快 20h 出了。tradere基本vm结构分析ptrace 父子进程调试，父进程追踪子进程 int 3 指令的位置，替换成相应的操作，因为开始的赋值操作导致数据结构不好看，可以考虑 dump + nop 初始化的方式。每次 int 3 触发之后，会执行一个结构体中的函数，结构体如下定义。1234567struct data{    data* lchild...
    ### [部分博客密码删除临时通知](https://y4tacker.github.io/2025/09/02/year/2025/09/%E9%83%A8%E5%88%86%E5%8D%9A%E5%AE%A2%E5%AF%86%E7%A0%81%E5%88%A0%E9%99%A4%E4%B8%B4%E6%97%B6%E9%80%9A%E7%9F%A5/)  
    >by [Y4tacker](https://y4tacker.github.io), 2025-09-02

    加密的还是比较多，这里选几篇问的多的先公开吧，碎碎念的思路分享为主，部分文章因为不难写的也比较简单，临近的漏洞仍然不公开博客，主要还是考虑到一些风险吧，以下博客已删除密码，可直接访问:泛微E-Office10最新远程代码执行漏洞分析浅析Panalog-SQL注入到命令执行(Version<20240130)某凌OA之一次后台变前台的故事泛微云桥文件上传与JFinal Bypass浅析帆软FineV...
    ### [浅析用友U8Cloud文件上传绕过](https://y4tacker.github.io/2025/09/02/year/2025/09/%E6%B5%85%E6%9E%90%E7%94%A8%E5%8F%8BU8Cloud%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E7%BB%95%E8%BF%87/)  
    >by [Y4tacker](https://y4tacker.github.io), 2025-09-02

    b2963ed3cf610cdbf71afa8f8ae1ed42faa800749325fb01df42ebf527266f25d0d5e7eb9f41fa82066f620d019fd4c64786baeb73afd9e2cdd205dfbf7346caaf7b04c2db7f9ebe7b8436778dc80240cb9fe7182f18c78e30e33410a1b6a17184bbd6...
    ### [浅析SmarBI最新权限绕过致RCE](https://y4tacker.github.io/2025/08/18/year/2025/08/%E6%B5%85%E6%9E%90SmarBI%E6%9C%80%E6%96%B0%E6%9D%83%E9%99%90%E7%BB%95%E8%BF%87%E8%87%B4RCE/)  
    >by [Y4tacker](https://y4tacker.github.io), 2025-08-18

    ec2d0f78db75185967c034d0900e9ea801690312c2501018c94f710ed617710ca87fed3700ccebdfb0e1e0414e66d5e0b7a7b9f12e1afe02813157ca7de2493d7f3d602bcd13db3c64990ce8aae91a5029c392c0725b07b7720085bdfb65097dc5611a...
    ### [浅析U8Cloud最新权限绕过至RCE](https://y4tacker.github.io/2025/07/30/year/2025/07/%E6%B5%85%E6%9E%90U8Cloud%E6%9C%80%E6%96%B0%E6%9D%83%E9%99%90%E7%BB%95%E8%BF%87%E8%87%B3RCE/)  
    >by [Y4tacker](https://y4tacker.github.io), 2025-07-30

    188fdb5a90e862409c62335614d03b9fc1fb489ee368a48d2adae972466363f6b4381b265f91d116ee77cc5e4b1a04e0a73be2d6a6830a1fb3c3c0925484501d1bfe2c517fe10ef843b1f29adb7670b3c12e8970f0c15cc99bded967217d7515b21e20...
    ### [契约锁前台代码执行补丁绕过(20250707)](https://y4tacker.github.io/2025/07/12/year/2025/07/%E5%A5%91%E7%BA%A6%E9%94%81%E5%89%8D%E5%8F%B0%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C%E8%A1%A5%E4%B8%81%E7%BB%95%E8%BF%87-20250707/)  
    >by [Y4tacker](https://y4tacker.github.io), 2025-07-12

    e6c11300420b389ced87a6974eed3fab25dac09bd1f6aee4a7a8e52e59f0711db643f38498979ffe7362af42a65818e6199d8458ea6277f1977e8e1d6193112aaa1fec2d6e20820e691a9bea2a94fe1cd41921e21853c253b70b81d7a051699e986703...
    ### [如何从灰盒角度快速复现Weaver最新SQL注入](https://y4tacker.github.io/2025/07/09/year/2025/07/%E5%A6%82%E4%BD%95%E4%BB%8E%E7%81%B0%E7%9B%92%E8%A7%92%E5%BA%A6%E5%BF%AB%E9%80%9F%E5%A4%8D%E7%8E%B0Weaver-SQL%E6%B3%A8%E5%85%A5/)  
    >by [Y4tacker](https://y4tacker.github.io), 2025-07-09

    如何从灰盒角度快速复现Weaver最新SQL注入​    好久没写不加密的博客了，因为比较简单外面也半公开了，就简单写写思路吧，至于POC就不直接贴出来了，这篇文章主要是面向像漂亮鼠这样的Java新手​    作为安全从业者的我们，每天都会面对各种各样的补丁和系统更新，很多时候不知道该如何下手，尤其是对于初学者，在尝试复现闭源漏洞时，经常会感到无从下手。面对复杂的系统架构、冗长的代码，以及各种陌生...
    ### [泛微最新补丁分析(20250704)](https://y4tacker.github.io/2025/07/09/year/2025/07/%E6%B3%9B%E5%BE%AE%E6%9C%80%E6%96%B0%E8%A1%A5%E4%B8%81%E5%88%86%E6%9E%90-20250704/)  
    >by [Y4tacker](https://y4tacker.github.io), 2025-07-08

    69b1ac3a8c7b27f3f5f24b3b8a7400bd6b1e48e4e4a74e3a9d5b0d94adacfef139866dca5f9c0752a208c27b415054195b8c9b09fcf4ba840127a35d6fbe535eecd06f6e3687d07dd41c43e8c9e03d37b2fa2fd462518b848ba4ce55dbd50da8160a3b...
    ### [契约锁最新前台命令执行及花式绕WAF思路](https://y4tacker.github.io/2025/07/02/year/2025/07/%E5%A5%91%E7%BA%A6%E9%94%81%E6%9C%80%E6%96%B0%E5%89%8D%E5%8F%B0%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E5%8F%8A%E8%8A%B1%E5%BC%8F%E7%BB%95WAF%E6%80%9D%E8%B7%AF/)  
    >by [Y4tacker](https://y4tacker.github.io), 2025-07-02

    d5bbf63b983168fb9cf0422698dce164b3b689fc252cba3faf3c75a652cdd7c0542690352b3ccfd95568bcdfd22e06b269ecaac13fedf5ec80edcfabe636ba58c0bd7707365d4cb09a79587d7876384f00fb8b2d3df17b696f7eefba94b5c2d66b93ca...
    ### [浅析Gogs 远程命令执行(CVE-2024-56731)](https://y4tacker.github.io/2025/06/25/year/2025/06/%E6%B5%85%E6%9E%90Gogs-%E8%BF%9C%E7%A8%8B%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C-CVE-2024-56731/)  
    >by [Y4tacker](https://y4tacker.github.io), 2025-06-25

    61250ef0d935a4a9d2eb682839325b52407d6a12bdde2eb831889d10036bea8106e2cbab4d0545b5551fe1a0fea6f3d58b8ee44d7110304bee8ff7333000d35c5b12e6d6807bdab93f096bd15b0c005660b70215b08b001ec238e70442e03904450ea3...
    ### [浅析Weaver Getdata前台SQL注入](https://y4tacker.github.io/2025/06/17/year/2025/06/%E6%B5%85%E6%9E%90Weaver-Getdata%E5%89%8D%E5%8F%B0SQL%E6%B3%A8%E5%85%A5/)  
    >by [Y4tacker](https://y4tacker.github.io), 2025-06-17

    1762bba105fb4c18fef9087d338fa0b386b5358d10250f8e320625eb752af13c9ab59c9d28e6b6cb26b41da8222a972a0fa17762539b600808df7928c3ec8de1798e61e6143d2b6e5a33a8bdf0c82a34fa42ca5b7d6a601a92e4946e55935648a81345...
    ### [浅析契约锁电子签章系统远程代码执行](https://y4tacker.github.io/2025/06/11/year/2025/06/%E6%B5%85%E6%9E%90%E5%A5%91%E7%BA%A6%E9%94%81%E7%94%B5%E5%AD%90%E7%AD%BE%E7%AB%A0%E7%B3%BB%E7%BB%9F%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C/)  
    >by [Y4tacker](https://y4tacker.github.io), 2025-06-11

    e1bd3e68fe0e95aad543147235f13aa8c07db101f08238b29c49348e526ca2c395ff16b5184fe4ee67b8dd1840f69936917a685390975ecb78405622c312487d5e6b45d97870e169a38f37bd7a2e95cc5b864202dba1787e366b00f3973f1aa3686ad8...
    ### [某系统前台RCE浅析](https://y4tacker.github.io/2025/04/16/year/2025/04/%E6%9F%90%E7%B3%BB%E7%BB%9F%E5%89%8D%E5%8F%B0RCE%E6%B5%85%E6%9E%90/)  
    >by [Y4tacker](https://y4tacker.github.io), 2025-04-16

    0a2416636d8596a6d89c133c7b60f6971ce99630884cdf6afd1d97649cdbe39606893f02e42a381ce0a49fc7535b4f6324e067de6d706384b3635b1ce021ea9edb6c0e081168a4c4fec62a99b6b4bc15b79e3a3b96705b7933478cec4f488c764ce87c...
    ### [腾讯游戏安全竞赛2025决赛题解](https://xia0ji233.github.io/2025/04/14/tencent-race-2025-final/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2025-04-14

    记录一下今年 2025 决赛过程题目描述（1）在intel CPU/64位Windows10系统上运行sys，成功加载驱动（0.5分）（2）能在双机环境运行驱动并调试（1分）（3）优化驱动中的耗时算法，并给出demo能快速计算得出正确的key（1分）（4）分析并给出flag的计算执行流程（1.5分），能准确说明其串联逻辑（0.5分）（5）正确解出flag（1分）（6）该题目使用了一种外挂常用的隐藏...
    ### [腾讯游戏安全大赛2025初赛题解](https://xia0ji233.github.io/2025/03/31/tencent-race-2025-pre/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2025-03-31

    记录一下今年 2025 初赛过程参赛选手信息题目描述小Q是一位热衷于PC客户端安全的技术爱好者，为了不断提升自己的技能，他经常参与各类CTF竞赛。某天，他收到了一封来自神秘人的邮件，内容如下：“我可以引领你进入游戏安全的殿堂，但在此之前，你需要通过我的考验。打开这扇大门的钥匙就隐藏在附件中，你有能力找到它吗？找到正确的flag（2分）flag：flag{ACE_We1C0me!T0Z0Z5GamE...
    ### [从CVE-2025-30208看任意文件读取利用](https://blog.zgsec.cn/archives/713.html)  
    >by [曾哥](https://blog.zgsec.cn/), 2025-03-30

    0# 概述师傅们好久不见！最近不是特别忙，就研究研究最新的漏洞。刚好最近一大批漏洞都爆出来了，比如 CVE-2025-1097, CVE-2025-1098, CVE-2025-24514, CVE-2025-1974 Kubernetes Ingress-Nginx Admission Controller RCE Escalation，是危害性极大的高危漏洞，在内网渗透中能直接击穿K8S集群。...
    ### [【白帽访谈录】云安全将成为未来安全研究主战场-会议纪要](https://blog.zgsec.cn/archives/711.html)  
    >by [曾哥](https://blog.zgsec.cn/), 2025-02-28

    {bilibili bvid="BV19T9gY4ETm" page=""/}很高兴能参与这期白帽访谈录，也感谢各位师傅的支持~也随时欢迎各位师傅和我友好交流哈哈！本期访谈的回放直播已经上传B站，链接： https://www.bilibili.com/video/BV19T9gY4ETm，感谢各位师傅的一键三连！！！欢迎大家关注渊龙Sec安全团队公众号，干货满满哦~{dotted startCo...
    ### [某系统前台组合拳RCE](https://y4tacker.github.io/2025/02/23/year/2025/02/%E6%9F%90%E7%B3%BB%E7%BB%9F%E5%89%8D%E5%8F%B0%E7%BB%84%E5%90%88%E6%8B%B3RCE/)  
    >by [Y4tacker](https://y4tacker.github.io), 2025-02-23

    8133babd8f05e144d8e8c2c4c8ee0fb3d40c2c031c3925709b74cb30c7b27fca92bfd93cf7cf65a6834a805821993b6c9674428ad9fdcf275cf47eb5e07cfd2d776e01401bdf1c9d1052d24b573abb3ff41508c0d801b0496ab9e4257b11885ae0e4bf...

</div>
