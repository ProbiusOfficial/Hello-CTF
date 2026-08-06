<div align="center">
     <h2>Hello CTF</h2>
     <div align="center">
    </div> 
    <a href="http://hello-ctf.com/"> <img src="https://badgen.net/badge/Mkdocs/%E5%9C%A8%E7%BA%BF%E9%98%85%E8%AF%BB?icon=chrome&color=black"></a>
    <a href="https://github.com/ProbiusOfficial/Hello-CTF"> <img src="https://badgen.net/github/stars/ProbiusOfficial/Hello-CTF?icon=github&color=black"></a>
    <a href="https://github.com/ProbiusOfficial/Hello-CTF"> <img src="https://badgen.net/github/forks/ProbiusOfficial/Hello-CTF?icon=github&color=black"></a>
    <a href="https://github.com/ProbiusOfficial/Hello-CTF/blob/main/LICENSE"> <img src="https://badgen.net/badge/license/GPLv3/"></a>
    <br>
     <a href="http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=wJ35e-T-qSlU7Y3Cs-PAasrAvZfRSc9k&authKey=WNEQbZUpolxgfKjUHHoUIoTBvSnvk2jZtcyWlhaDcUZ6ZYGgvywqi1ah5D7UwUrg&noverify=0&group_code=590430891"> <img src="https://img.shields.io/badge/QQ%20Group-590430891-black"></a>
     <a href="https://gitcode.com/Probius/Hello-CTF"> <img src="https://gitcode.com/Probius/Hello-CTF/star/badge.svg"></a>
    <br>
    </div>


文档基于 Mkdocs-Material 构建，通过 GitHub Pages 部署在 [https://hello-ctf.com/](https://hello-ctf.com/) ，感谢渊龙Sec安全团队[@AabyssZG](https://github.com/AabyssZG) 曾哥提供的CDN支持~

您可以直接访问该页面[在线阅读](https://hello-ctf.com/)，如果您想要转载本项目，请带上项目源地址：https://github.com/ProbiusOfficial/Hello-CTF

如果文档有帮助到你，麻烦点一个 :star: 支持一下！！

## 关于

随着网络安全的发展，有越来越多的小伙伴了解到了 **CTF** ，并且想要参与到比赛中来，但仅仅寻找学习资源就耗费了大量精力；  
同时每年招新时 或者带新人入门的时候 都会面临很多相似的问题，于是本项目应运而生。  
本项目旨在创建一本开源免费、新手友好的「 **夺旗赛 | CTF(Capture The Flag)** 」入门教程。  

- 对于每个方向的基础知识点，我们都会尽力提供相应的题目(包括题目附件 题目源码 Dockerfile),所有题目均可本地部署也可在NSSCTF平台上直接开启,我们会在教程中逐步引导读者,并且鼓励读者自行复现,使学习过程更加具象;  
- 在提供基础知识外，本书也将提供CTF相关的信息聚合，以消除信息差;  
- 书籍在每篇文章下都设置有讨论区，欢迎讨论，提问，以及建议;   

## 功能与板块

- **主教程**：MISC / Web / Crypto / Reverse / Pwn 五大方向，以及 AWD / AI / Blockchain 等扩展方向，覆盖入门到提高各个阶段，每个知识点配有配套题目；
- **赛事中心**：国内外赛事聚合，国外赛事基于 CTFtime RSS 每日自动更新，国内赛事手动维护，提供 ICS 日历订阅与「提交比赛」入口；
- **工具**：CTF 工具百科，以及工具 / MCP 导航页；
- **知识点标签**：收集 CTF 中出现过的各项知识点，提供简介与相关 Payload；
- **配套靶场**：Hello-CTF 系列靶场的部署与解题文档，也可在合作平台在线体验；
- **命题与容器**：Docker 教学、CTF 命题技巧与封装教程，以及动态 Flag 容器模板项目 [ctf-docker-template](https://github.com/CTF-Archives/ctf-docker-template)；
- **CTF档案馆**：博客与友情链接、联合战队招新、CTF 相关 UP 主等内容收录。

## 本地构建

本项目基于 Python，克隆仓库后：

```bash
pip install -r requirements.txt
mkdocs serve
```

或使用 Docker：

```bash
docker compose up --build
```

随后访问 [http://127.0.0.1:8000](http://127.0.0.1:8000) 即可预览。

## 项目结构

- `docs/` — 站点源码：教程文档、自定义首页与 sidebar 功能页、赛事数据等；
- `overrides/` — Mkdocs-Material 主题覆写；
- `build.py` / `events_update.py` — 赛事数据更新脚本，由 GitHub Action 每日自动运行；
- `admin/` — 站点管理面板（管理赛事、首页内容、文档和部署）；
- `collector/` — 消息收集器（接收赛事提交与意见反馈）。

## 加入我们

本书仍然处于更新阶段，我们还有很多内容需要完善，欢迎您加入我们，一起完善本书，让更多的人了解CTF，参与CTF，享受CTF的乐趣。
您随时可以通过提交 [「 PR (Pull Request) 」](https://github.com/ProbiusOfficial/Hello-CTF/pulls)来协助我们完成本项目。

- 如果您在阅读过程中发现任何 知识点错误，内容模糊，名词拼写错误等等的问题，还请您协助我们进行修改，您可以直接在评论区中提出，也可以直接提交PR。
- 如果您有好的题目，好的题解，好的知识点讲解，或者其他合作意向，也欢迎您联系探姬([By QQ](2293808331))或者开启issue。

## 致谢
本项目基于[Mkdocs-material](https://github.com/squidfunk/mkdocs-material)搭建，感谢该项目提供的优秀的文档编写平台。  

项目最初只是一个Readme文档，受到 **[Hello-algo](https://github.com/krahets/hello-algo/)** 项目的启发，这才有了这个项目现在的样子，如果你对算法感兴趣，强烈推荐这本在数据结构期末考试前帮了我大忙的书籍。  

在提出这个项目的想法的时候，因为国内的环境问题，我怀疑过很多次自己这样做是否有意义，感谢 [*Ari @deCafLatte*](https://github.com/deCafLatte) 的支持和鼓励，让我有动力做自己喜欢的事情。

本项目的完成离不开以下小伙伴的贡献，感谢他们的付出。
<p align="left">
    <a href="https://github.com/ProbiusOfficial/Hello-CTF/graphs/contributors">
        <img width="550" src="https://contrib.rocks/image?repo=ProbiusOfficial/Hello-CTF" />
    </a>
</p>

**向每一个为开源社区做出努力和贡献的人，致以崇高的敬意！！！**
