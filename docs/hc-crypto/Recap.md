---
comments: true

---

## 前情提要

### 关于 编码,古典密码,现代密码

由于密码学的发展 以及CTF比赛的不断革新，编码和古典密码已经很少出现在密码学方向的题目中了，即使出现也会跟随现代密码学一同使用，更常见的反而是在「 **杂项 MISC** 」中作为签到题或者一般简单题目考察。

严谨起见，我们依据密码学的wiki词条来决定密码学需要书写的内容。

在密码学wiki中，对于密码学的描述在前面这样写道：

> **密码学**（英语：Cryptography）可分为[古典密码学](https://zh.wikipedia.org/wiki/古典密碼)和现代密码学。在西方语文中，密码学一词源于[希腊语](https://zh.wikipedia.org/wiki/希臘語)*kryptós*“隐藏的”，和*gráphein*“书写”。古典密码学主要关注资讯的保密书写和传递，以及与其相对应的破译方法。而现代密码学不只关注资讯保密问题，还同时涉及资讯完整性验证（[消息验证码](https://zh.wikipedia.org/wiki/消息验证码)）、资讯发布的不可抵赖性（[数码签名](https://zh.wikipedia.org/wiki/数字签名)）、以及在[分布式计算](https://zh.wikipedia.org/wiki/分布式计算)中产生的来源于内部和外部的攻击的所有信息安全问题。
>
> —— [中文wiki-密码学](https://zh.wikipedia.org/zh-sg/%E5%AF%86%E7%A0%81%E5%AD%A6)

 **「古典密码学 Classic cryptography 」** 和 **「现代密码学 Modern cryptography 」** 均属于密码学分支，只是重心发生了侧移，大家更加关心现代密码学相关使用和研究。

对 **「编码 Encoding  」** 的解释如下：

> In [cryptology](https://en.wikipedia.org/wiki/Cryptology), a **code** is a method used to encrypt a [message](https://en.wikipedia.org/wiki/Message) that operates at the level of meaning; that is, words or phrases are converted into something else. A code might transform "change" into "CVGDK" or "cocktail lounge". The U.S. [National Security Agency](https://en.wikipedia.org/wiki/National_Security_Agency) defined a code as "A substitution cryptosystem in which the plaintext elements are primarily words, phrases, or sentences, and the code equivalents (called "code groups") typically consist of letters or digits (or both) in otherwise meaningless combinations of identical length."[[1\]](https://en.wikipedia.org/wiki/Code_(cryptography)#cite_note-boaklectures-1): Vol I, p. 12  A *[codebook](https://en.wikipedia.org/wiki/Codebook)* is needed to encrypt, and decrypt the phrases or words.
>
> —— [英文wiki-编码(密码学)](https://en.wikipedia.org/wiki/Code_(cryptography))

这里国内外存在一些差异，在中文wiki上这样写着：
>编码：它意指以[码字](https://zh.wikipedia.org/w/index.php?title=碼字&action=edit&redlink=1)取代特定的[明文](https://zh.wikipedia.org/wiki/明文)。例如，以‘苹果派’（apple pie）替换‘拂晓攻击’（attack at dawn）。[编码](https://zh.wikipedia.org/zh-sg/編碼)已经不再被使用在严谨的密码学，它在[资讯论](https://zh.wikipedia.org/wiki/信息论)或[通讯原理](https://zh.wikipedia.org/w/index.php?title=通訊原理&action=edit&redlink=1)上有更明确的意义

虽然不再符合现代 严谨的密码学 的定义，但在广义的密码学上 **「编码 Encoding  」**  依旧被承认为密码学分支，同时编码在现代密码学信息承载上依旧有巨大作用，综合考虑，密码学会 一起更新 **「编码 Encoding  」** , **「古典密码学 Classic cryptography 」** 和 **「现代密码学 Modern cryptography 」** 的相关知识，如果MISC方向有需要会链接到此。

笔者认为，作为计算机领域信息传递最基本的一环，不论你是否选择密码学或者杂项，编码技术都值得你详细阅读和了解。

### 引用
- https://en.wikipedia.org/wiki/Cryptography
- https://en.wikipedia.org/wiki/Code_(cryptography)