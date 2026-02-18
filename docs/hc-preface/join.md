---
comments: true

---

# 帮助我们完善内容

CTF是一个涉及面很广的比赛，而作者一个人的能力又很有限，所以书中难免会有一些错误或者不完善的地方，如果您在阅读过程中发现任何知识点错误、内容模糊、名词拼写错误等问题，还请您协助我们进行修改，我们一直在为CTF和网络安全的开源生态努力，也希望您能够加入我们，一起完善本书，共同维护CTF社区的开放性。每一个[ PR ](https://github.com/ProbiusOfficial/Hello-CTF/graphs/contributors)都会被记录在本书的贡献者名单中，我们向每一个为开源社区做出努力和贡献的人，致以崇高的敬意！

## 直接编辑

在每个页面的右上角有一个「编辑」图标，您可以按照以下步骤修改文本或代码：

1. 点击编辑按钮，如果遇到“需要 Fork 此仓库”的提示，请同意该操作；
2. 修改 Markdown 源文件内容，并确保内容正确，同时尽量保持排版格式的统一；
3. 在页面底部填写修改说明，然后点击 `Propose file change` 按钮；页面跳转后，点击 `Create pull request` 按钮即可发起拉取请求。

## 本地编辑

!!! Info "注意"
    本项目基于 Mkdocs-Material 构建，如果您对 Mkdocs-Material 不熟悉，建议您先阅读 [Mkdocs-Material 官方文档](https://squidfunk.github.io/mkdocs-material/)。

直接编辑的方式对于小改动来说是非常方便的，但是如果您需要修改大量内容，或者需要在本地进行编辑，那么您可以按照以下步骤进行：

1. 首先 Fork 本仓库到您的 GitHub 账户；
2. 将您 Fork 的仓库使用 `git clone` 命令将仓库克隆至本地；
3. 将本地所做更改 Commit ，然后 Push 至仓库；
4. 发起 Pull Request ，我们会尽快回复。

## 本地构建

对于 Mkdocs-Material 项目的本地构建，您需要具备Python环境，随后使用
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple mkdocs-material
```
安装Mkdocs-Material，然后在您仓库的克隆目录下执行
```bash
mkdocs serve
```

随后访问 127.0.0.1:8000 即可查看本地构建的效果。

!!! Bug "如果你的mkdocs构建失败……"
    可以采用以下处理方式：  
    1. 将报错的文件内容清空（如编译过程中提示`无效的参数：RCE.md`，但是别忘了pr的时候还原回去）  
    2. 更换端口（编译命令中添加参数`--dev-addr=127.0.0.1:【新的端口号】`）  
    3. 提出问题并等待回复（这可能需要很久！）



## 贡献者名单

本项目的完成离不开以下小伙伴的贡献，感谢他们的付出。

<p align="left">
    <a href="https://github.com/ProbiusOfficial/Hello-CTF/graphs/contributors">
        <img width="550" src="https://contrib.rocks/image?repo=ProbiusOfficial/Hello-CTF" />
    </a>
</p>