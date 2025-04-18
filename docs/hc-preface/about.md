---
comments: true

---

# 关于本书

本项目旨在创建一本开源免费、新手友好的CTF(Capture The Flag，夺旗赛)入门教程。

- 对于每个方向的基础知识点，我们都会尽力提供相应的题目(包括题目附件 题目源码 Dockerfile)，所有题目均可本地部署也可在NSSCTF平台上直接开启，我们会在教程中逐步引导读者，并且鼓励读者自行复现，使学习过程更加具象;  
- 在提供基础知识外，本书也将提供CTF相关的信息聚合，以消除信息差;  
- 书籍在每篇文章下都设置有讨论区，欢迎讨论，提问，以及建议。  


## 读者对象

如果你对CTF感兴趣，但是不曾了解，亦或者是了解但不知从何学起，是很纯正的「CTF萌新选手，那建议仔细阅读本书 (bushi  

如果你熟悉CTF并且已经有一门或者多门熟悉的方向，是「CTF老手」，那么本书也可以作为您尝试其他方向，成为全栈✌路上的垫脚石 (x   

如果你的CTF已经炉火纯青，是「CTFの神」，我们期待您的宝贵建议，或者，您也可以加入我们一起创作！！　　

!!! Note "前置条件"

    您需要至少熟悉任意一个方向，对该方向有一定的认知，能够针对该方向知识点完成对应题目的命题。
    (以Web方向举例 您除了需要会Web方向的基础以外，还需要熟悉Docker技术)

## 内容结构

![image-20231105050702232](../assets/structureDiagram.png)

本项目围绕CTF分为了下面几个板块.  

### **[HelloCTF](https://hello-ctf.com/) (/HC)** 

HelloCTF项目的核心部分，包含CTF各个方向 (包括但不限于MISC,WEB,CRYPTO,REVERSE,PWN),覆盖入门到提高各个阶段,每个知识点享有配套题目。 

### **[赛事](https://hello-ctf.com/ET/) Event (/ET)**

涵盖CTF 国内外 即将进行、正在进行、已经结束的所有比赛信息。

对于有办赛需求的团队提供相关支持。

### **[工具](https://hello-ctf.com/hc-toolkit/) CTFhc-toolkit (/hc-toolkit)** 

与项目 [CTFtools-wiki](https://github.com/ProbiusOfficial/CTFtools-wiki) 同步，分类收录各种 CTF 工具。  

### **[团队](https://hello-ctf.com/TB/) TeamBuilding (/TB)** 
应对高校CTF战队 / 网络安全社团 等建设，提供必要的解决方案(如培训资料，公文模板，比赛材料申报等)

### **[扩展](https://hello-ctf.com/EE) Extension (/EE)** 
目前围绕容器技术提供如Docker的相关教学以及命题技巧和封装教程。  

后续会更新如何从CTF过渡到安全实战领域，以及CTFer会面临的就业问题。

### **[CTF档案馆](https://hello-ctf.com/Archive) Archives (/Archive)** 

收录CTF相关内容，包括但不限于: 

- 师傅们的博客收录

- CTF联合战队信息以及招新公告(如果有的话)

- CTFChannel 会列出CTF相关内容的UP主

- CTF历届比赛信息，题目，以及WriteUp (题目包括对附件 / Docker存档)
  
  该部分 (CTF档案馆) 将基于GitHub组织 [CTF-Archives](https://github.com/CTF-Archives) 进行维护，所有涉及到的题目都会上传到 [NSSCTF](https://www.nssctf.cn/) 平台上，方便大家复现。

## 一些Q&A
**这个项目和 CTF-Wiki 相比有什么优势或者特点👀**  

：一个问的比较多的问题，但是如果你阅读过两个项目的内容，你问不出来这个问题——知识库和入门书有什么区别？Wiki不会一步一步的引导你，这就是最直观的区别。笔者写这本书的原因就是，自己太笨了看不懂Wiki。

**为什么不在CTF-wiki上继续创作？**  

：参考上一个QA，两者内容面向的群体是不同的。

**未来会出书么？**  

：原则上没有这个打算，我个人觉得CTF这玩意真不适合出书，不过考虑到有些师傅会喜欢纸质化阅读，可能会在内容彻底完善后出纸质版的打算，不过我建议是把项目down下来，然后给一些线上打印商铺让其帮忙封装，从我高中那会复印教材的经验来讲，很便宜，也比较方便。

当然如果有强烈需求，说不定呢（懒.jpg

**我有一些类似讲课 培训的任务，我能用这个项目么？**  

：可以，招新培训，甚至师傅们有一些培训私单也可以引用该项目，不过所有的使用都需要注明来源。比较特殊的一点是，如果你需要用它录制付费向视频，请来找我授权，因为本项目从许可证来讲，是不支持商用的。

如果项目帮助到了你，可以给我点颗 Star⭐ 这是对我最大的鼓励w，当然，你要是能捐赠这个项目，那我就更感激不尽啦～

**我想二开这个项目，或者说我想把他放到我们学校的知识库之类的行为？**  

：没有太大要求，保持开源，不允许收费和商用，标注源项目地址即可。

要注意的是，如果你确定使用了本项目，那么你所有基于本项目创作的后续内容必须保持开源

