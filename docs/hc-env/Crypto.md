# Crypto 环境配置

## 前言

> 善于百度, 哪里不懂先去百度, 其实搜索引擎上更推荐 `Bing` 或是 `谷歌`, 百度只是要求搜索解决的统一说辞, 还有疑惑则去读 [提问的智慧](https://zhuanlan.zhihu.com/p/38176992), 如果依旧不理解, 可以用从 [提问的智慧](https://zhuanlan.zhihu.com/p/38176992) 中学到的提问方式来请教别人.

ida 和编辑器不做限定, 语言可以用 Python 入门(但需要任何一门编程语言的编程基础, 无基础请先在 b 站搜索 [翁凯c 语言](https://www.bilibili.com/video/BV1XZ4y1S7e1/), 随后(如何界定随后呢, 接着往下看)学习[黑马程序员 python](https://www.bilibili.com/video/BV1qW4y1a7fU/) 即可, 学习时间随个人接受程度, 翁凯 c 语言课程全集(总 129p)建议控制在 1 个月内掌握其中提到的各种用法, 学到函数后(这时便是上面提到的随后)即可开始同步学习 Python), 后续随个人爱好发展...

> 写这篇工具集合的时候越写越发现没什么是必须这里列出来的, 又容易写的很多, 所以推荐没有编程基础或编程基础薄弱的同学, 速速上此门课, 一周内学完会让你对计算机有个初步之上的认知 [MIT 公开课](https://csdiy.wiki/编程入门/MIT-Missing-Semester/)

## 初步工具的安装

### 系统或发行版: Arch Linux

因其可以方便的安装比较新版本的 SageMath. 安装教程网上有(搜索时注意避开 `CSDN` 就会发现很多宝藏), 自己找, 并不难找

### 编译器和解释器: GCC, Python(Python3)

如果使用我上面提到的 Arch Linux, 那么安装这两个工具时需要先执行以下命令:

```bash
# Arch 终端下执行此命令以更新软件包列表 和 更新可升级项
# sudo 提升权限, 注意: 输入密码的时候是不可见的, 输入完成回车即可
sudo pacman -Syu
```

---

```bash
# Arch 终端下执行此命令以安装 gcc
sudo pacman -S gcc
```

```bash
# Arch 终端下执行此命令以安装 Python3, Arch Linux 默认安装了 Python3，所以你可能不需要再次安装.
sudo pacman -S python
```

### 编辑器: VS Code

前期使用完全可以不安装 VS Code 下的插件, 当然也可以选择性安装简体中文插件和 clangd 以及 Python 插件套装, 其余插件没有是必须安装的, 请不要在配置编辑器方面消耗过多时间

同时前期编译和执行程序时均不建议直接使用编辑器或者 ide 自带的一键运行按钮, 本人更推荐直接在终端里进行操作, 下附简单操作, 也当做是对终端的初步熟练, 且此举的时间开销并不大

### 编译运行 `C/C++` 程序

> ↓ `gcc` 简单使用方式  
> 仅仅是使用方式 你并不能原封地不改执行它, 如果发现进行文章上面提到的操作后还是无法执行, 则请你直接跳到下面最佳实践看, 其实就是加入可选选项(暂时无需了解), file 替换为你的文件名, 一般为 `.c` 或者 `.cpp` 结尾

```bash
# 终端执行
gcc [options] file...
```

> ↓ 最佳实践  
> 这里假设你的 `c` 源代码叫做 `nihao.c`, 执行这句代码后便会编译执行你想让其编译执行的源代码

```bash
# 终端执行
gcc nihao.c && ./a.out
```

> 这里假设你的 `cpp` 源代码叫做 `nihao.cpp`, 执行这句代码后便会编译执行你想让其编译执行的源代码

```bash
# 终端执行
gcc nihao.cpp && ./a.out
```

> Ps: 不推荐新手用 CLion 

尽管这是个非常好用的 ide, 然而因为新手不熟悉 CMake 而会耽搁进度, 不过个人觉得如果时间很宽泛的话无所谓, 均可, 但仍然建议有了编程基础后(这个基础如何界定呢? 至少在没有网络和 ai 以及各种学习毕竟和语言手册的情况下凭自身能解决 **洛谷** 入门等级大部分问题的时候, 这段话是可以划掉的, 毕竟洛谷容易让人误入竞技性编程歧途(暴论??))再去学习[如何配置 CMake | 打不开大概率是网络问题](https://lov2.netlify.app/c++vscode/), 这样会更有体系和轻松

---

### 运行 Python 源代码

> ↓ 最佳实践  
> 这里假设你的 `Python3` 源代码叫做 `nihao.py`, 执行这句代码后便会执行你想要执行的源代码

```bash
# 终端执行
python3 nihao.py
```

***

这时基本工具已经准备好(关于 Python 的数学模组不要着急 暂时用不到, 遇到了就学习如何手动完成所需要的函数), 可以开始在 buuCTF 刷题, 刷题时 密码分类中第一页差不多接近一般的时候就可以暂停刷题, 来先把时间用在初等数论的学习了, (时间不紧迫的同时有条件的话可以同时学数学分析)

> 如何使用 [buuCTF](https://buuoj.cn/challenges)? 点击←蓝色的字, 登录后顶部选择 `练习场`, 后选择 `题目列表` 即可

<br>

现在开始已经是环境配置之外的内容了, 来到

## 如何学习密码学

等到数论知识学到差不多(这里的差不多指的是)的时候为学完以下内容, 如何界定学会, 只要自己能给别人讲清楚这个知识点, 即可作为初步**学会**的标准:

- 整除和带余除法
- 同余的概念和性质
- 同余类和剩余系
- 欧几里得算法
- 扩展欧几里得算法
- 模运算
- 素数的性质和判定
- 费马定理
- 欧拉定理
- 中国剩余定理
- 原根

↑这个知识列表引用自: [知乎文章: 初学者怎样学习密码学](https://zhuanlan.zhihu.com/p/455104888)

自己看不出来是什么数学原理就搜 `WP`(Writeup, 含义为题解), 不过前提是自己已经思考过确认一段时间内思考不出来

***

有了一点点数论基础后

### 工具配置: 各种 `Python 模块` 和 `SageMath`

#### `Python 模块` 配置

首先配置 `pip3`

```bash
# 更新软件包列表
sudo pacman -Syu
```

```bash
# 安装 pip3, 用以管理 Python3 的模块
sudo pacman -S python-pip
```

下面有不知道是什么, 或者不知道怎么使用的模块, 打开 [pypi](https://pypi.org/) 搜索即可

```bash
# 安装 gmpy2
pip3 install gmpy2
```

```bash
# 安装 python 进度条模块
pip install tqdm
```

```bash
# 安装 libnum
pip install libnum
```

```bash
# 安装维纳攻击模块
pip install owiener
```

```bash
# 安装 pwntools, 来让密码学可以打远程服务器的题目
pip install pwntools
```

```bash
# 安装 python - z3
pip3 install z3-solver
```

[z3教程](https://microsoft.github.io/z3guide/)

<br>

#### `SageMath` 配置

`SageMath` [配置教程](https://doc.sagemath.org/html/en/installation/index.html)

`SageMath` [增强插件](https://github.com/n-WN/sagemath-vscode-enhanced)

> 为什么只甩了个网站呢, 因为这时候的你应该有自己搜集信息的能力了, 在未知领域探索也是能力, 会用工具也是能力

> 依旧建议将其配置到 `Linux`

- Arch Linux

```bash
sudo pacman -S sagemath
```

- [MacOS](https://github.com/3-manifolds/Sage_macOS)

---

```bash
 给 notebook 下的 SageMath 加上打交互题的能力
%pip install pwntools
```

同时别的模块也是可以安装进来的, 只需要像👆🏻这条命令一样, 前面加个 `%` 即可, 被称为: 魔法命令

交互如果报错, 考虑使用 [精简版](https://github.com/n-WN/Pwn4Sage) 交互

<br>

 配置完成啦!

这时推荐刷题网站: [CryptoHack](https://cryptohack.org/courses/) 做这个平台 `Course` 分类下的题目即可

 **不要为了做题而做题, 更重要的是自己的思考, 长时间自己无法解决一个问题的时候, 这时候可能是你没有学过的一个新知识点, 也有可能是单纯脑子没转(这种情况先去做别的题/事, 不要耗费时间)**

> by: LOV3
