---
comments: true
glightbox: false
hide:
  - footer
  - toc
  - edit
  - view
---

<div class="grid" style="display: grid;grid-template-columns: 30% 69%" markdown>

<div class="grid cards" markdown>

-   :material-tooltip-edit:{ .lg .middle } __关于__

    ---

    针对CTF的工具合集,快速定位:
    
    - [效率][Software]
    [Software]: javascript:document.getElementById('software').scrollIntoView()
    - [环境][Environment]
    [Environment]: javascript:document.getElementById('environment').scrollIntoView()
    - [Web][Web]
    [Web]: javascript:document.getElementById('tool_web').scrollIntoView()
    - [MISC][MISC]
    [MISC]: javascript:document.getElementById('tool_misc').scrollIntoView()
    - [Cypto][Cypto]
    [Cypto]: javascript:document.getElementById('tool_cypto').scrollIntoView()
    - [Reverse][Reverse]
    [Reverse]: javascript:document.getElementById('tool_reverse').scrollIntoView()
    - [Pwn][Pwn]
    [Pwn]: javascript:document.getElementById('tool_pwn').scrollIntoView()
    - [AWD/AWDP][AWD]
    [AWD]: javascript:document.getElementById('tool_awd').scrollIntoView()

</div>

<div class="grid cards" style="display: grid; grid-template-columns: 1fr;" markdown>

-   :material-star-shooting:{ .lg .middle } __推荐__

    ---

    :material-eye-check:{ .lg .middle } [LovelyMem](https://github.com/Tokeii0/LovelyMem) - 让取证像喝水一样简单@Tokeii0

<div class="grid cards" style="display:grid; grid-template-columns: 49% 49% !important;" markdown>


-   :material-file-link:{ .lg .middle } __Release__

    ---

    更新中...

    [→ 所有版本](https://github.com/ProbiusOfficial/CTFtools-wiki)


-   :material-flag-variant-minus:{ .lg .middle } __CTF-OS__

    ---

    更新中...

    [→ 了解更多](https://github.com/ProbiusOfficial/CTF-OS)

</div>

</div>

</div>

<div class="grid cards" markdown>

-   :octicons-heart-fill-24:{ .heart .middle } __Activity__

    ---
    更新中...
    

</div>

<div id="software" class="grid cards" markdown>

-   :fontawesome-solid-computer:{ .lg .middle } __常用软件__

    ---

    > 该栏目提供的工具只为提高效率，可能与项目核心有一定偏差。  
    > 欢迎在issue中推荐更多的效率工具，但是请注意，适合自己的工具才是最好的，您并不需要下载所有的工具，请勿持有 ALL IN 思想。

    | 项目名称                                                 | 项目简介                                                     | 项目地址                                           | 项目文档                                     |
    | :------------------------------------------------------- | :----------------------------------------------------------- | :------------------------------------------------- | :------------------------------------------- |
    | [Maye Lite](https://github.com/25H/MayeLite)             | 专注于文件快速启动的简洁、轻量级工具 :fontawesome-brands-windows: | [GitHub](https://github.com/25H/MayeLite)          | https://t.arae.cc/p/25804.html               |
    | [uTools](https://u.tools/)                               | 一个极简、插件化的现代桌面软件。 :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [官网](https://u.tools/)                           | https://u.tools/docs/guide/about-uTools.html |
    | [Everything](https://www.voidtools.com/zh-cn/downloads/) | 一款强大的本地文件索引和搜索工具 :fontawesome-brands-windows: | [官网](https://www.voidtools.com/zh-cn/downloads/) | /                                            |
    
</div>

<div id="environment" class="grid cards" markdown>

-   :octicons-gear-24:{ .lg .middle } __环境基础__

    ---

    | 项目名称           | Usage                                                        | 项目地址                                                     | 使用文档 |
    | ------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | :------: |
    | Vscode             | 最好用 最轻量的 文本编辑器 依靠扩展可实现包括但不限于 IDE 各种功能 :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [官网](https://code.visualstudio.com/)                       |    /     |
    | Vmware Workstation | 虚拟机软件 :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [官网](https://www.vmware.com/products/workstation-pro/workstation-pro-evaluation.html) |    /     |
    | PyCharm            | Python 集成开发环境(IDE) :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [官网](https://www.jetbrains.com/zh-cn/pycharm/)             |    /     |
    | IDEA               | Java 集成开发环境(IDE) :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [官网](https://www.jetbrains.com/zh-cn/idea/)                |    /     |
    | PHPStorm           | PHP 集成开发环境(IDE) :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [官网](https://www.jetbrains.com/zh-cn/phpstorm/)            |    /     |
    | Phpstudy           | Web环境 (Apache / Nginx + FTP + MySQL) 快速部署  :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple:  <br />常用于 Web初学阶段的一些本地web页面的搭建 | [官网](https://www.xp.cn/download.html)                      |    /     |
    | Docker             | 容器服务  :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple:<br />常用于 题目本地搭建测试  靶场环境，漏洞复现环境搭建等 <br /> 除了静态附件题目，几乎所有的CTF题目都依赖Docker | [官网](https://www.docker.com/)                              |    /     |
    | Navicat            | 优秀的数据库 管理 操作 调试 以及 可视化软件<a href="https://www.ghxi.com/navicat16.html"> :fontawesome-brands-windows:</a>:fontawesome-brands-linux: :simple-apple: | [官网](https://navicat.com.cn/download/navicat-premium)      |    /     |
    | Watt Toolkit       | GitHub Discord 部分谷歌服务 页面元素CDN 访问加速 \| <br />不是用来让你打游戏的啊喂(#`O′)！ :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [GitHub](https://github.com/BeyondDimension/SteamTools)      |    /     |
    | Clash              | 部分服务访问加速 \| 我也只能说这么多 :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [GitHub](https://github.com/Dreamacro/clash)                 |    /     |

</div>

<div id="tool_web" class="grid cards" markdown>

-   :material-web:{ .lg .middle } __Web | Web安全__

    ---

    - 注意 工具包含 应用程序 :material-application-braces: 和 浏览器插件 :material-microsoft-internet-explorer: 
    - 以下为Web常用工具或者说基础工具，一些漏洞利用程序将不会被归纳到这，您可以 点击此处 查看后方的CTF项目归档来查找更多工具。

    | 项目名称                                                     | Usage                                                        | 项目地址                                                     | 使用文档 | 其他 |
    | :----------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | -------- | ---- |
    | hackbar :material-microsoft-internet-explorer:  | 浏览器插件，能够在页面上直接完成 请求/响应内容编辑，完成各种包括但是不限于伪造的工作。 | [谷歌商店](https://chrome.google.com/webstore/detail/ginpbkfigcoaokgflihfhhmglmbchinc)<br />[GitHub](https://github.com/Mr-xn/hackbar2.1.3) | /        | /    |
    | Proxy SwitchyOmega  :material-microsoft-internet-explorer:  | 代理管理软件，方便一个浏览器多个代理端口的切换。             | [GitHub](https://github.com/FelisCatus/SwitchyOmega)         | /        | /    |
    | Wappalyzer  :material-microsoft-internet-explorer:  | 页面技术识别软件，方便快速定位页面的框架技术等信息           | [官网](https://www.wappalyzer.com/)                          | /        | /    |
    | Burp Suite  :material-application-braces: | 代理抓包软件，用于Web应用程序的渗透测试和攻击 :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [官网](https://portswigger.net/burp)                         | /        | /    |
    | Antsword  :material-application-braces: | 开源Webshell管理工具 :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [GitHub](https://github.com/AntSwordProject/antSword)        | /        | /    |
    | dirsearch  :material-application-braces: | 目录扫描工具 :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [GitHub](https://github.com/maurosoria/dirsearch)            | /        | /    |
    | SQLMap :material-application-braces: | 自动化的SQL注入利用工具 :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [GitHub](https://github.com/sqlmapproject/sqlmap)            | /        | /    |
    | JD-GUI  :material-application-braces: | Jar包反编译工具  :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [GitHub](https://github.com/java-decompiler/jd-gui)          | /        | /    |
    | Ysoserial :material-application-braces: | Java 反序列漏洞利用工具  :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [GitHub](https://github.com/frohoff/ysoserial)               | /        | /    |

</div>

<div id="tool_misc" class="grid cards" markdown>

-   :material-spider-web:{ .lg .middle } __MISC | 杂项__

    ---

    -   :material-snowflake: __基础工具__  

        ---

        - **基础语言 | 模块**

        | 项目名称 | Usage                      | 项目地址                        | 文档 |
        | -------- | -------------------------- | ------------------------------- | ---- |
        | Python   | MISC方向中用途最广的语言。 | [官网](https://www.python.org/) | /    |

        - **编码 / 解码 / 解密 工具**

        | 项目名称      | Usage                                                        | 项目地址                                                     | 文档 |
          | ------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ---- |
          | CyberChef     | 近乎全能的编码解码工具。 :material-microsoft-internet-explorer:  | [官网](https://cyberchef.org/)<br />[国内中文镜像站](https://ctf.mzy0.com/CyberChef3/) | /    |
          | Ciphey        | 自动化解密工具。                                             | [GitHub](https://github.com/Ciphey/Ciphey)                   |      |
          | CTFCrackTools | 国内首个CTF工具框架,内涵多个主流密码加解密，支持添加支持Python编写的插件。 | [GitHub](https://github.com/0Chencc/CTFCrackTools)           | /    |

        - **文本 / Hex 编辑 | 文件工具**	

        | 项目名称   | Usage                                                        | 项目地址                                        | 文档 |
          | ---------- | ------------------------------------------------------------ | ----------------------------------------------- | ---- |
          | 010 Editor | 专业的文本编辑器和16进制编辑器，可通过加载模块脚本，解析文件结构。 :fontawesome-brands-windows::fontawesome-brands-linux: | [官网](http://www.010editor.com/)               | /    |
          | lmHex      | 开源的16进制编辑器。  :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [GitHub](https://github.com/WerWolv/ImHex)      |      |
          | WinHex     | 16 进制编辑器为核心的数据处理软件。 :fontawesome-brands-windows: | [官网](https://www.x-ways.net/winhex/)          | /    |
          | Binwalk    | 可识别文件分离提取工具，常用于从文件中提取隐写到其中的其他文件。:fontawesome-brands-linux: | [GitHub](https://github.com/ReFirmLabs/binwalk) | /    |
          | Foremost   | 用于提取一个文件中包含的多个文件。:fontawesome-brands-linux: | /                                               | /    |

        - **隐写工具 | 图像 / 音频**

        | 项目名称                                                     | Usage                                                        | 项目地址                                                     | 文档                                                       |
          | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ---------------------------------------------------------- |
          | Qrazybox :material-microsoft-internet-explorer:  | 二维码分析和恢复 :material-microsoft-internet-explorer:  | [GitHub](https://github.com/Merricx/qrazybox)<br />[Usagepage](https://merri.cx/qrazybox/) |                                                            |
          | QR Research                                                  | 专业的二维码扫描识别软件，支持多个纠错等级，掩码选项(已停止维护)。 :fontawesome-brands-windows: | /                                                            | /                                                          |
          | UleadGIFAnimator                                             | 高级GIF编辑器 :fontawesome-brands-windows: | /                                                            | [吾爱论坛](https://www.52pojie.cn/thread-1276299-1-1.html) |
          | **-----图像类**                                              |                                                              |                                                              |                                                            |
          | Stegsolve                                                    | 图像分析工具。  :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [GitHub](https://github.com/Giotino/stegsolve)               | /                                                          |
          | TweakPNG                                                     | 用于检查和修改PNG图像文件 \|类似于010的Png Template功能  :fontawesome-brands-windows: | [官网](https://entropymine.com/jason/tweakpng/)              | /                                                          |
          | BlindWaterMark(python)                                       | 基于 python 的图像盲水印                                     | [GitHub1](https://github.com/chishaxie/BlindWaterMark)<br />[GitHub2](https://github.com/fire-keeper/BlindWatermark)             | /                                                          |
          | BlindWatermark(java)                                         | 基于 java 的图像盲水印                                       | [GitHub](https://github.com/ww23/BlindWatermark)             | /                                                          |
          | WaterMark(隐藏水印)                                          | 图像隐写工具，在频域添加数字水印  :fontawesome-brands-windows: | /                                                            | [吾爱论坛](https://www.52pojie.cn/thread-709668-1-1.html)  |
          | WaterMarkH                                                   | 单图盲水印(频域隐写)工具                                     | /                                                            | /                                                          |
          | zsteg                                                        | PNG 和 BMP 图片隐写                                          | [GitHub](https://github.com/zed-0xff/zsteg)                  | /                                                          |
          | StegoVeritas                                                 | 隐写工具                                                     | [GitHub](https://github.com/bannsec/stegoVeritas)            | /                                                          |
          | Stegdetect                                                   | 检测jpeg图像隐写工具，搭配stegbreak食用更佳                  | [GitHub](https://github.com/abeluck/stegdetect)              | /                                                          |
          | **-----音频类**                                              |                                                              |                                                              |                                                            |
          | Steghide                                                     | 将文件隐藏到**图片或音频**中的工具  :fontawesome-brands-windows: :fontawesome-brands-linux: | [官网](https://steghide.sourceforge.net/)                    | /                                                          |
          | Audacity                                                     | 多轨音频处理软件。 :fontawesome-brands-windows: | [GitHub](https://github.com/audacity/audacity)               | /                                                          |
          | Mp3stego                                                     | 音频隐写提取工具 :fontawesome-brands-windows: | [官网](https://www.petitcolas.net/steganography/mp3stego/)   | /                                                          |
          | Silenteye                                                    | 音频/图像隐写工具  :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [官网](https://achorein.github.io/silenteye/)                | /                                                          |
          | DeepSound                                                    | 可以将文件加密保存到一段声音文件中 :fontawesome-brands-windows: | [官网](https://jpinsoft.net/deepsound/documentation.aspx)    | /                                                          |
          | Mp3tag                                                       | 音频文件元资料编辑器  :fontawesome-brands-windows::simple-apple: | [官网](https://www.mp3tag.de/en/)                            | /                                                          |

        - **取证工具**

        | 项目名称                | Usage                                                        | 项目地址                                                     | 文档                                                         |
          | ----------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
          | Forensics-Wiki          | 取证综合资料库 :material-microsoft-internet-explorer:  | [官网](https://www.forensics-wiki.com/)                      | /                                                            |
          | **-----密码爆破**       |                                                              |                                                              |                                                              |
          | ZipCenOp                | 伪加密加/解密工具  :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [GitHub](https://github.com/442048209as/ZipCenOp)            | /                                                            |
          | ARCHPR                  | 压缩文件密码暴力破解工具。 :fontawesome-brands-windows: | /                                                            | /                                                            |
          | Ziperello               | zip压缩包密码恢复软件。 :fontawesome-brands-windows: | /                                                            | /                                                            |
          | Aopr                    | Office文件密码暴力破解工具。 :fontawesome-brands-windows: | /                                                            | /                                                            |
          | Passware Kit Forensic   | 十分强大的解密工具，各类文件/磁盘密码爆破，密钥搜索等        | /                                                            | - [依依的汉化包](https://blog.csdn.net/u010418732/article/details/120189354)<br />- [汉化版](https://www.mzy0.com/archives/82/) |
          | Hashcat                 | 高性能，GPU/CPU 兼容的本地密码破解，支持多种不同格式         | [GitHub](https://github.com/hashcat/hashcat)                 | /                                                            |
          | John the Ripper         | 简单易用的离线破解                                           | [GitHub](https://github.com/openwall/john)                   | /                                                            |
          | Hydra                   | 远程或在线密码的并行暴力破解。                               | [GitHub](https://github.com/vanhauser-thc/thc-hydra)         | /                                                            |
          | **-----流量分析**       |                                                              |                                                              |                                                              |
          | Wireshark               | 流量分析取证软件。  :fontawesome-brands-windows: :simple-apple: | [官网](https://www.wireshark.org/)                           | /                                                            |
          | **-----内存 磁盘 取证** |                                                              |                                                              |                                                              |
          | Volatility              | 内存分析取证软件。  :fontawesome-brands-windows: :fontawesome-brands-linux: :simple-apple: | [官网](https://www.volatilityfoundation.org/)<br />[GitHub](https://github.com/volatilityfoundation) | /                                                            |
          | MemProcFS               | 新型内存取证框架 :fontawesome-brands-windows: | [GitHub](https://github.com/ufrisk/MemProcFS)                | /                                                            |
          | NtfsStreamsEditor       | NTFS流分析 :fontawesome-brands-windows: | [官网](https://www.nirsoft.net/utils/alternate_data_streams.html) | /                                                            |
          | R-Studio                | 内存取证tick+磁盘文件恢复分析 :fontawesome-brands-windows: | [官网](https://www.r-studio.com/zhcn/data-recovery-software) | /                                                            |
          | AutoPsy                 | 用来分析磁盘映像和恢复文件的开源取证工具 :fontawesome-brands-windows: | [官网](https://www.autopsy.com/)                             | /                                                            |
          | RegistryExplorer        | 注册表文件分析器 :fontawesome-brands-windows: | [官网](http://www.regxplor.com/download.html)                | /                                                            |
          | PowerToy                | 注册表文件分析器 :fontawesome-brands-windows: | [GitHub](https://github.com/microsoft/PowerToys)             | /                                                            |

    -   :material-snowflake: __解题工具__  

        ---

        :octicons-alert-24: 请不要过分依赖下面工具！！！

        - MISC是一个对编程能力要求比较高的方向，不过大多数考点的固定衍生出比较多的"轮子"，当然轮子减少手动操作，确实是好东西，但是容易产生一些弊端，因为跳过了手动操作所以不懂原理也能梭题目，可能会导致选手略过本来应该学的原理，手动会做之后再碰到了用工具减少操作是完全没问题的，即便没有这些整合工具，用现成脚本说到底本质也是一样的。

          ```
          使用工具获取便利的同时 请不要忽略对原理的学习！
          ```

        | 项目名称     | Usage                                                    | 相关地址                           |
        | ------------ | -------------------------------------------------------- | ---------------------------------- |
        | 随波逐流     | 离线加密解密，字符编码进行转换，文件隐写查看等多项功能。 | [官网](http://1o1o.xyz/index.html) |
        | PuzzleSolver | MISC 综合解题工具，由Byxs20开发。                        | [神秘数字](https://github.com/Byxs20/PuzzleSolver)              |

    -   :material-snowflake: __开源脚本__  

        ---

        🔔MISC是一个十分注重编程能力 ~~和 脑洞~~ 的方向，希望你能从下面的开源脚本中获得启发，也欢迎pr投稿你的开源脚本x

        | 项目名称                          | 项目地址                                                     | 项目作者                                         |
        | --------------------------------- | ------------------------------------------------------------ | ------------------------------------------------ |
        | 自动爆破PNG图片宽高并一键修复工具 | [GitHub](https://github.com/AabyssZG/Deformed-Image-Restorer) | [AabyssZG (曾哥) )](https://github.com/AabyssZG) |
        | 文件反转、倒置、导出工具          | [GitHub](https://github.com/AabyssZG/FileReverse-Tools)      | [AabyssZG (曾哥) )](https://github.com/AabyssZG) |
        | CRC碰撞全自动化脚本               | [GitHub](https://github.com/AabyssZG/CRC32-Tools)            | [AabyssZG (曾哥) )](https://github.com/AabyssZG) |
        | 自动化内存取证_GUI版本            | [GitHub](https://github.com/Tokeii0/VolatilityPro)           | [Tokeii0 (猫捉鱼) ](https://github.com/Tokeii0)  |

</div>

<div id="tool_cypto" class="grid cards" markdown>

-   :material-key-variant:{ .lg .middle } __Crypto | 密码学__

    ---

    | 项目名称                                                     | Usage                                                        | 项目地址                                                     | 其它                                                      |
    | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | --------------------------------------------------------- |
    | ---**语言 \| 模块**                                          |                                                              |                                                              |                                                           |
    | Python                                                       | CTF密码学中离不开的语言x                                     | [官网](https://www.python.org/)                              | /                                                         |
    | Crypto 包 :fontawesome-brands-python: | 密码学工具库，用于在Python中实现各种加密、解密和哈希算法。   | [GitHub](https://github.com/Legrandin/pycryptodome)          | /                                                         |
    | gmpy2 包 :fontawesome-brands-python: | 包含了许多常用的数论函数和算法，适配各种大整数情况，算法效率高于原生库。 | [GitHub](https://github.com/aleaxit/gmpy)                    | /                                                         |
    | numpy 包 :fontawesome-brands-python: | 基于C代码实现了底层数据结构和计算函数优化，适用于处理大型数据集和高性能计算，在密码学中常用于矩阵类运算。 | [GitHub](https://github.com/numpy/numpy)<br />[官网](https://numpy.org/) | /                                                         |
    | ---**应用程序**                                              |                                                              |                                                              |                                                           |
    | Sagemath                                                     | 开源的数学软件系统,整合了许多开源Python包。 :fontawesome-brands-linux::simple-apple: | [官网](https://www.sagemath.org/)<br />[GitHub](https://github.com/sagemath) | [Sage 中文文档](https://www.osgeo.cn/sagemath/index.html) |
    | Yafu                                                         | 本地的因数分解程序                                           | [官网](https://sourceforge.net/projects/yafu/)               | /                                                         |
    | Factordb                                                     | 在线的因数分解网站                                           | [官网](http://factordb.com/)                                 | /                                                         |
    | z3                                                           | 开源的约束求解器，针对约束求解题型                           | [GitHub](https://github.com/Z3Prover/z3/)                    | /                                                         |

</div>

<div id="tool_reverse" class="grid cards" markdown>

-   :octicons-terminal-24:{ .lg .middle } __Reverse | 逆向__

    ---

    | 项目名称       | Usage | 项目地址 | 其他 |
    | ------------   | ----- | -------- | -------- |
    | 微步沙箱 | 文件敏感操作检查 :material-microsoft-internet-explorer:  | [UsagePage](https://s.threatbook.com) | / |
    | Binaryai             | 基于开源项目代码匹配度在线反编译工具 :material-microsoft-internet-explorer:  | [UsagePage](https://www.binaryai.cn/)                        | /                                                            |
    | IDA            | 最常用的静态逆向工具 | [官网](https://hex-rays.com/ida-pro/)        |  [ida pro权威指南](https://github.com/Coldwave96/WebSecurity/blob/master/IDA%20Pro%E6%9D%83%E5%A8%81%E6%8C%87%E5%8D%97%EF%BC%88%E7%AC%AC%E4%BA%8C%E7%89%88%EF%BC%89.pdf)        |
    | Ghidra         | 开源的静态逆向工具，和IDA作用相同      | [官网](https://ghidra-sre.org/)         | / |
    | Ollydbg        | 同为反汇编调试器(官方已经停止维护)     | [官网](https://www.ollydbg.de/)         | /         |
    | x64dbg / x32dbg | 在windows上使用的开源 x64 / x32 调试器  | [官网](https://x64dbg.com/)         | / |
    | DIE            | 查壳工具，拿到程序第一件事就是分析文件类型，是否有壳   | [GitHub](https://github.com/horsicq/Detect-It-Easy)   | [GitHub](https://github.com/horsicq/Detect-It-Easy)  |
    | Exeinfope      | 同为查壳工具      | [官网](http://www.exeinfo.byethost18.com)    | /         |
    | Cheat Engine   | 对程序的内存数据进行扫描和调试。 | [官网](https://www.cheatengine.org/)   |  /        |
    | GDB         | 一般用于ELF的动态调试，配合插件(如pwngdb，gdb-peda)使用更佳   | 使用包管理工具安装      | [Sourceware](https://www.sourceware.org/gdb/documentation/)   |
    | z3                   | 开源的约束求解器，针对约束求解题型                           | [GitHub](https://github.com/Z3Prover/z3/)                    | /                                                            |
    | dnSpy                | 强大的.NET调试、修改和反编译的工具(已停止维护)               | [GitHub](https://github.com/dnSpy/dnSpy)                     | /                                                            |
    | ----**Java反编译**   |                                                              |                                                              |                                                              |
    | JADX                 | 开源 更好的代码可读性 自动恢复丢失的类和方法、变量和方法名称、可以将反编译结果导出为 Eclipse 或 IDEA 项目 | [GitHub](https://github.com/skylot/jadx)                     | /                                                            |
    | JD-GUI               | 更好的代码可读性 可导出为 Java 文件或 Jar 包                 | [GitHub](http://java-decompiler.github.io/)                  | /                                                            |
    | JEB                  | 支持wasm 可交叉引用、可看字节码、反编译结果纯粹              | [官网](https://www.pnfsoftware.com/)                         | /                                                            |
    | GDA                  | 支持apk, dex, odex, oat, jar, class, aar文件的反编译， 支持python及java脚本自动化分析 | [官网](http://www.gda.wiki:9090/)                            | /                                                            |
    | Fernflower           | IDEA 采用的反编译工具,支持Jar包反编译。                      | [GitHub](https://github.com/fesh0r/fernflower)               | /                                                            |
    | ----**Python反编译** |                                                              |                                                              |                                                              |
    | pycdc                | pyc反编译,对高版本有不错兼容性。                       | [GitHub](https://github.com/zrax/pycdc)                      | /                                                            |
    | Unpy2exe             | 对py2exe打包的python程序提取字节码文件  **(.pyc)**。         | [GitHub](https://github.com/matiasb/unpy2exe)               | /                                                            |
    | Pyinstxtractor       | 对pyInstaller打包的python程序提取字节码文件  **(.pyc)**。    | [GitHub](https://github.com/extremecoders-re/pyinstxtractor) | /                                                            |
    | [Python]uncompyle    | 用于对Python字节码文件 **(.pyc)** 的反汇编，将其变成python源代码。 | [官网](https://pypi.org/project/uncompyle6/)                 | /                                                            |

<!-- 拿到一个文件，先分析它是什么类型的文件，可以在Linux下使用flie来查看他是什么类型的文件(一般是一个可执行文件)，分析后查看它是否有壳，有的话先脱壳，脱壳后针对文件类型来使用逆向工具，如Jar包我们就用jd-gui，.NET文件我们就使用dnSpy，IDA一般是万金油，不知道用什么的话就先用IDA静态分析。在了解程序大概结构后，我们可以对程序关键部分下断点进行动态调试，但在这之前，我们或许还会遇到需要解决混淆和反调试保护等问题......本文注重工具的介绍，这里不再对题型过多赘述。 -->

</div> 

<div id="tool_pwn" class="grid cards" markdown>

-   :octicons-file-binary-16:{ .lg .middle } __PWN | 二进制__

    ---

    | 项目名称       | Usage | 项目地址 | 其他 |
    | ------------   | ----- | -------- | -------- |
    | GDB       | 一般用于ELF的动态调试，配合插件(如pwngdb，gdb-peda)使用更佳。    | [Sourceware](https://www.sourceware.org/gdb/documentation/)  | /  |
    | Pwntools    | 用于编写EXP。    | [GitHub](https://github.com/Gallopsled/pwntools)     | /   |
    | Pwncli | 一款简单、易用的`pwn`题调试与攻击工具，帮助你快速编写`pwn`题攻击脚本，并实现本地调试和远程攻击的便捷切换，提高你在`CTF`比赛中调试`pwn`题脚本的速度与效率。 | [GitHub](https://github.com/RoderickChan/pwncli) | / |
    | Checksec    | 查看二进制文件开启了哪些保护机制。  | [GitHub](https://github.com/slimm609/checksec.sh)  | /        |
    | ROPgadget   | 编写ROP的EXP时需要用到，可以帮助你寻找合适的gadgets。    | [GitHub](https://github.com/JonathanSalwan/ROPgadget) | /        |
    | objdump     | 反汇编工具，查看文件的一些表信息，如got表。  | /                                                           | /                                                           |
    | radare2 | UNIX-like reverse engineering framework and command-line toolset. | [GitHub](https://github.com/radareorg/radare2) | / |
    | windbg | Window 内核模式和用户模式代码调试。 | [Microsoft Learn](https://learn.microsoft.com/zh-cn/windows-hardware/drivers/debugger/debugger-download-tools) | /    |

<!-- Pwn的解题过程与Reverse差不多，我们拿到文件需要先分析文件类型，然后再对文件开启的保护机制分析，反汇编出它的源代码，对源代码的逻辑分析，找出漏洞，编写EXP,在编写EXP的过程中，我们可以使用gdb在本地动态调试，一步一步修改我们的EXP,Pwn掉这题！ -->

</div> 

<div id="tool_awd" class="grid cards" markdown>

-   :material-shield-sword-outline:{ .lg .middle } __AWD | 网络攻防__

    ---

    | 项目名称       | Usage | 项目地址 | 其他 |
    | ------------   | ----- | -------- | -------- |
    | evilPather | awd pwn题的通防御 ｜ [Github](https://github.com/TTY-flag/evilPatcher) |
    | Prepare-for-AWD | 攻击和防御用脚本 | [Github](https://github.com/admintony/Prepare-for-AWD) |
    | 0rays-edr-filechecker | 文件监控器，防止别人传马 | [Github](https://github.com/christarcher/0RAYS-AWD-Filechecker) |
    | awf-watchbird | web题的通防 ｜ [Github](https://github.com/leohearts/awd-watchbird) |
    | AoiAWD | 也是web题的通防 ｜ [Github](https://github.com/DasSecurity-HatLab/AoiAWD) |
    | PWN WAF | pwn的通防，还能以牙还牙（大嘘 | [Github](https://github.com/i0gan/pwn_waf) |
    | 0E7 | AWD工具箱 | [Github](https://github.com/huangzheng2016/0E7) |
    | S4DFarm | Flag农场，用于管理flag和一件提交 ｜ [Github](https://github.com/C4T-BuT-S4D/S4DFarm) |