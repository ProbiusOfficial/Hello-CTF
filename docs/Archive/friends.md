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
    ### [windows驱动开发（1）——Windows驱动字符串](https://xia0ji233.github.io/2024/11/24/WindowsDriver1/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-11-24

    来简单实战几个字符串API初始化ASCII 字符和宽字符的版本分别是12RtlInitAnsiStringRtlInitUnicodeString第一个参数都是对应的字符串结构体的指针，也就是说，在使用的时候需要先定义一个结构体变量再去使用这个 API 去初始化字符串变量。1234567LPSTR str2 = "123456789 hello";ANSI_STRING astr;RtlInitA...
    ### [windows驱动开发（0）——Windows驱动开发的基础知识](https://xia0ji233.github.io/2024/11/23/WindowsDriver0/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-11-22

    今天来学习一下Windows驱动开发基础由于之前操之过急，对驱动开发很多东西都没有了解便强行上手，导致后面困难重重，于是痛定思痛，开始推翻重来，相信之前的一些开发经验会让这一路好走一点。环境搭建Vmware + VirtualKD + windbg preview 做调试环境。VS 2022 + WDK 做开发环境。参考链接1参考链接2内核API的使用对于导出的函数，只需要包含对应的头文件直接使用...
    ### [windows内核（6）——中断与异常和控制寄存器](https://xia0ji233.github.io/2024/11/22/WindowsKernel6/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-11-22

    今天来学习一下X86中断与异常和控制寄存器中断中断通常是由CPU外部的输入输出设备（硬件）所触发的，供外部设备通知CPU有事情需要处理，因此又叫中断请求，英文为Interrupt Request。中断请求的目的是希望CPU暂时停止执行当前正在执行的程序，转去执行中断请求所对应的中断处理例程，中断处理程序由 IDT 表决定。80x86 有两条中断请求线：非屏蔽中断线，NMI，全称NonMaskabl...
    ### [windows内核（5）——TLB](https://xia0ji233.github.io/2024/11/11/WindowsKernel5/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-11-11

    今天来学习一下TLB的一些细节TLB简介TLB（Translation Lookaside Buffer，转换后援缓冲器），是一个硬件单元，它用于保存每个进程虚拟地址到物理地址的映射，这里做的对进程的区分大概是使用 CR3 区分的，这个点看很多文章都没有提到，但是仅仅保存线性地址到物理地址的映射是必然不够的，因为不同的进程的同一线性地址不一定对应相同的物理页，但是猜测大概是这样的。TLB 做了指令...
    ### [windows内核（4）——挂物理页](https://xia0ji233.github.io/2024/11/10/WindowsKernel4/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-11-10

    挂物理页的一些细节线性地址有效性判断之前我们分析过 MmIsValidAddress 函数，在 10-10-12 分页模式下就是去拿到页表的线性地址，然后判断 PTE 和 PDE 的P位是否都有效。一般来说，如果都有效说明进程在这个线性地址这里挂上了物理页。零地址挂页考虑以下代码：12int *x=NULL;*x=100;通常情况下我们会认为这两条语句执行之后必然出错，这就是所谓的空指针错误，但是...
    ### [windows内核（3）——PAE分页（2-9-9-12分页）](https://xia0ji233.github.io/2024/11/09/WindowsKernel3/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-11-09

    来学一下2-9-9-12分页，也叫PAE分页为什么要有2-9-9-12分页这一定一定是最会疑惑的一个问题，为什么要多拆一个 2 出来呢？回答：扩展物理内存。我们都知道，32位的系统最大只能装 4GB 的内存，多了它用不上，然而这个说法比较片面，实则它可以装更多的内存，在 10-10-12 分页的模式中，我们知道，物理地址就是 32 位的，而物理地址位宽决定了物理内存最大的限度。那么 2-9-9-1...
    ### [windows内核（2）——页属性实验](https://xia0ji233.github.io/2024/11/07/WindowsKernel2/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-11-07

    来具体学习一下页属性看前必读本文所述的第 x 位均表示下标从 0 开始的计数制。120000100010001           *例如上面星号所指示的位置表示第 1 位。有效属性可以关注内核函数 MmIsAddressValid 实现原理，取出虚拟机 C:\Windows\System32\ntoskrnl.exe 内核文件，找到该函数，F5可得以下逻辑12345678910111213141...
    ### [强网杯S8初赛pwn writeup](https://xia0ji233.github.io/2024/11/07/qwb2024_pre/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-11-07

    本次强网杯初赛做出两道pwn题，把详细题解写一下记录。baby_heap附件下载2.35 的版本，IDA打开，堆菜单题，经典增删改查之外，还有两个额外的操作，一个是环境变量，另一个是任意地址写 0x10 字节。del 里面有很明显的UAF漏洞。show 只有一次机会，但是可以同时将 libc 和堆地址一起泄露出来，只需要我们释放两个相同大小的堆块之后，bk_nextsize 和 fd_nextsi...
    ### [windows内核（1）——分页](https://xia0ji233.github.io/2024/11/07/WindowsKernel1/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-11-07

    今天开始正式学习分页的相关知识分页与物理地址什么是物理地址在学习二进制的时候就有区分过物理地址和虚拟地址这两个概念，其实就是内存条真正的地址，这里不再赘述。而学习保护模式我们知道，实际的线性地址 = 逻辑地址+段寄存器.base，在汇编和C指针层面所使用的地址都是逻辑地址。但是似乎它等同于虚拟地址（线性地址），这是因为通常情况下段寄存器的 base 都为 0。10-10-12分页详解基本结构拿到一...
    ### [x86的保护模式（4）——任务门](https://xia0ji233.github.io/2024/11/04/x86_4/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-11-03

    学习一下任务门相关的知识从堆栈切换开始说起，不管是中断、陷入还是调用，提权之后 ESP 和 SS 都会被切换到对应权限的栈，那么必然有一个地方会维护这个栈所在的位置，其实就是使用任务段去维护的。任务段任务段介绍任务状态段简称任务段，英文缩写为TSS，Task-state segment，任务段的结构体如下所示，大小为 104 字节。观察结构体成员，可以很明显地看到有 SS2，ESP2，SS0，ES...
    ### [eoffice前台权限绕过致代码执行](https://y4tacker.github.io/2024/10/14/year/2024/10/eoffice%E5%89%8D%E5%8F%B0%E6%9D%83%E9%99%90%E7%BB%95%E8%BF%87%E8%87%B4%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-10-14

    1fde8e13c0800e34bf83b87666dd4d9cc35b143eda24e0c7f10fb09b8f001c0492c29e66ae7d59bed9b15650dfd29403df74c0cac6726b0adac99daaf44ace5d3b290a873a368292a289fb0e4a84be522f1f5f2248fcd6d1c86b9d39f861123c353f2a...
    ### [浅析Edoc2前台远程代码执行](https://y4tacker.github.io/2024/10/09/year/2024/10/%E6%B5%85%E6%9E%90Edoc2%E5%89%8D%E5%8F%B0%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C/)  
    >by [Y4tacker](https://y4tacker.github.io), 2024-10-09

    4780fbcdbf7405ce90fd6e499eaf6095781862f7317b4a3cc99e0d387e923799bc023cb7a5fac5102aecc9c2174f007a6ef602947b468ee2ed2eb62878f73d759273d2ee31e9aedf6a203293ea59932363ad1cc17de9ea622351f9207f23fcd6744576...
    ### [x86的保护模式（3）——门描述符实验](https://xia0ji233.github.io/2024/10/08/x86_3/)  
    >by [xia0ji233](https://xia0ji233.pro/), 2024-10-07

    通过做实验来加深一下印象首先是环境搭建，寻找32位虚拟机花了很长时间，最后在52破解上找到了合适的系统。如果你尝试自己搭建你会发现，win7 32镜像很难寻找，而且大部分不支持 Vmware Tools，帧率很低很卡，调试起来很不舒服。而笔者给出的链接中的 32 位虚拟机还是很不错的，能调试，能装 Vmware Tools。还需要提醒一点的是，解压好之后把 CPU 个数和核心数全部改成 1，不然实...
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

</div>
