---
comments: true

---

# 文件隐写

### 文件内容

这类题算是比赛的签到题

比赛方可能会给你各种各样的文件

你需要将文件用记事本打开

这同样也是很多复杂题的第一步

从文件的十六进制数据中找出线索


![图一](https://pic1.imgdb.cn/item/6770febcd0e0a243d4ec1776.jpg)

下载文件后用 txt 形式打开（推荐 VS Code）

![2](https://pic1.imgdb.cn/item/6770feedd0e0a243d4ec178a.jpg)

成功拿到 flag

![3](https://pic1.imgdb.cn/item/6770ff1bd0e0a243d4ec1793.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-10.md -->
### 字频统计


![](https://pic1.imgdb.cn/item/67711945d0e0a243d4ec2044.jpg)

前面步骤是 ForeMost 分离加解压密码爆破

爆破后拿到一个 txt 包含大量无特征、无规律的重复字符

![](https://pic1.imgdb.cn/item/67711a5ad0e0a243d4ec2065.jpg)

编写脚本拿到 flag

```python
import re
from collections import Counter

def count_letters(filename):
    """计算并返回文件中每个字母的出现次数"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            # 读取文件内容并转换为小写
            text = file.read().lower()
            
            # 使用正则表达式匹配字母
            letters = re.findall(r'[a-z]', text)
            
            # 计数每个字母的出现次数
            letter_count = Counter(letters)
            
            return letter_count
        
    except FileNotFoundError:
        print(f"文件 {filename} 未找到。")
        
        return None


def display_top_letters(letter_count, top_n):
    """显示出现次数最多的 top_n 个字母及其计数"""
    if letter_count:
        top_letters = letter_count.most_common(top_n)
        
        for letter, count in top_letters:
            print(f"'{letter}' 出现了 {count} 次")


def main():
    # 指定文件名
    filename = '1.txt'
    
    letter_count = count_letters(filename)
    
    if letter_count:
        # 你可以修改这个值来显示更多或更少的字母
        top_n = 20
        
        display_top_letters(letter_count, top_n)


if __name__ == '__main__':
    main()
```




<!-- Imported from D:\\Book\\Misc\\Chapter1\1-11.md -->
### TTL


![](https://pic1.imgdb.cn/item/67712b72d0e0a243d4ec24e3.jpg)

打开文件只有 63、255、127、191  四种数值

![](https://pic1.imgdb.cn/item/67711b38d0e0a243d4ec207e.jpg)

这四位数只有前两位不同

![](https://pic1.imgdb.cn/item/67711b58d0e0a243d4ec2082.jpg)

提取出来写入文件中

```python
import binascii


def decode_file(input_file, output_file):
    try:
        # 读取文件并将每行转换为整数列表
        with open(input_file, 'r') as fp:
            p = list(map(int, fp.readlines()))

        # 构建二进制字符串
        binary_string = ''.join(
            '00' if i == 63 else
            '01' if i == 127 else
            '10' if i == 191 else
            '11' for i in p
        )

        # 将二进制字符串分成每8位并转换为字符
        flag = ''.join(chr(int(binary_string[i:i + 8], 2)) for i in range(0, len(binary_string), 8))

        # 解码并写入输出文件
        with open(output_file, 'wb') as wp:
            wp.write(binascii.unhexlify(flag))

        print(f"文件成功解码并保存为 {output_file}")

    except FileNotFoundError:
        print(f"文件 {input_file} 未找到。")
    except Exception as e:
        print(f"发生错误: {e}")


def main():
    decode_file('attachment.txt', 'ans.zip')


if __name__ == '__main__':
    main()
```

打开压缩包最后是 Base64 套娃

![](https://pic1.imgdb.cn/item/67711d4cd0e0a243d4ec20be.png)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-12.md -->
### 零宽字符


![](https://pic1.imgdb.cn/item/67711ff9d0e0a243d4ec2266.jpg)

VS Code 打开文件发现很多零宽字符

![](https://pic1.imgdb.cn/item/677120dcd0e0a243d4ec22a8.png)

解码拿到 flag

![](https://pic1.imgdb.cn/item/67712044d0e0a243d4ec227f.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-13.md -->
### 文件异或


![](https://pic1.imgdb.cn/item/677124dcd0e0a243d4ec2383.jpg)

打开文件发现大多数十六进制数据是 A1

推测被做了异或处理

![](https://pic1.imgdb.cn/item/6771251bd0e0a243d4ec2390.jpg)

**一个数值连续异或两次同一个数值则结果不变**

异或回去是个音频文件，打开听 flag 就行

![](https://pic1.imgdb.cn/item/6771257cd0e0a243d4ec23ab.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-14.md -->
### Pickle 序列化


![](https://pic1.imgdb.cn/item/67712626d0e0a243d4ec23d2.jpg)

FFD9 结尾后的数据就是要序列化的内容

![](https://pic1.imgdb.cn/item/67712936d0e0a243d4ec2480.png)

在 Python 中，**Pickle** 是一个模块，用于将 Python 对象序列化（转换为字节流）和反序列化（从字节流恢复为 Python 对象）

我这里把两段代码写一起了，可以去掉格式化的代码查看数据内容会发现是坐标

```python
import pickle


def load_pickle_data(file_path):
    """加载 pickle 文件并返回数据"""
    with open(file_path, "rb") as fp:
        return pickle.load(fp)


def write_to_file(file_path, data):
    """将数据写入文件"""
    with open(file_path, 'w') as fw:
        fw.write(str(data))


def process_text(text):
    """处理文本并根据特定规则格式化输出"""
    i = 0
    a = 0

    while i < len(text):
        if text[i] == ']':
            print('\n')
            
            a = 0
            
        elif text[i] == '(':
            if text[i + 2] == ',':
                b = int(text[i + 1]) - a
                
                d = text[i + 1]
                
                print(" " * b, end="")
                
                print(text[i + 5], end="")
                
                a = int(d)
                
            else:
                b = int(text[i + 1] + text[i + 2]) - a
                
                d = text[i + 1] + text[i + 2]
                
                print(" " * b, end="")
                
                print(text[i + 6], end="")
                
                a = int(d)
                
        i += 1


def main():
    # 加载 pickle 数据
    a = load_pickle_data("123.txt")

    # 将数据写入到文件
    write_to_file("pickle.txt", a)

    # 读取文件并处理
    with open("pickle.txt", "r") as fw:
        text = fw.read()

    # 处理文本内容
    process_text(text)


if __name__ == "__main__":
    main()
```

拿到 flag

![](https://pic1.imgdb.cn/item/67712950d0e0a243d4ec2488.jpg)



<!-- Imported from D:\\Book\\Misc\\Chapter1\1-15.md -->
### PYC 或 PYO


![](https://pic1.imgdb.cn/item/677129e5d0e0a243d4ec24a4.jpg)

拿到文件先改个名吧，检测是 pyc 文件

在 Python 中，`.pyc` 文件是 **Python Compiled File**（Python 编译文件）的扩展名。当 Python 脚本（`.py` 文件）被执行时，Python 会将其源代码编译成字节码，并将字节码存储为 `.pyc` 文件。字节码是 Python 代码的低级表示，它是 Python 虚拟机（PVM）能够理解和执行的格式

![](https://pic1.imgdb.cn/item/67712a0ed0e0a243d4ec24ad.jpg)

在 WinHex 中发现隐藏文件

![](https://pic1.imgdb.cn/item/67712a45d0e0a243d4ec24ba.jpg)

使用常见的工具 stegosaurus 提取隐写

![](https://pic1.imgdb.cn/item/67712a56d0e0a243d4ec24be.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-16.md -->
### Word 文字

修改文字颜色就行了

![](https://pic1.imgdb.cn/item/67bb00fed0e0a243d40295fd.png)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-17.md -->
### Base64


![](https://pic1.imgdb.cn/item/67e4d2d40ba3d5a1d7e4b270.png)

下载附件后使用工具破解其伪加密

![](https://pic1.imgdb.cn/item/67e4d3f00ba3d5a1d7e4b5f7.png)

隐写信息藏在 **Base64 填充部分（`=`的位置）**：

- 当原始数据长度 **不是3的倍数** 时，Base64编码末尾会有`=`填充（1或2个）
- 这些`=`的位置对应的**最后几个有效 Base64 字符**可以被修改而不影响解码结果
- 脚本通过比较 **原始 Base64** 和 **重新编码后的 Base64** 的差异来提取隐藏信息

**解题思路：**

1. 读取文件
   逐行读取`stego.txt`中的 Base64 字符串（每行可能包含隐写数据）。

2. 解码再重新编码

   - 先解码该行 Base64 得到原始数据
   - 再将原始数据重新编码为标准的 Base64
   - 此时，重新编码的结果会和原始行有细微差异（如果存在隐写）

3. 计算偏移量（关键步骤）

   - 找到原始行和重新编码后行的最后一个非`=`字符

   - 比较这两个字符在`B64CHARS`中的索引差值（`offset`）

     ```python
     offset = abs(B64CHARS.index(steg_char) - B64CHARS.index(row_char))
     ```

4. 转换为二进制

   - 根据该行`=`的数量（`equalnum`），将`offset`转为二进制：

     - 1个`=` → 2位二进制（因为`=`对应最后 2 个隐藏位）
     - 2个`=` → 4位二进制（对应最后 4 个隐藏位）

     ```python
     bin_str += f"{offset:0{equalnum * 2}b}"  # 补零到指定位数
     ```

5. 输出隐藏信息

   - 每当`bin_str`累积够 8 位时，转换为 ASCII 字符并输出

```python
import base64

B64CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

def decode_b64_stego(filename):
    bin_str = ''
    with open(filename, 'rb') as f:
        for line in f:
            stegb64 = line.decode('utf-8').strip()
            try:
                decoded = base64.b64decode(stegb64)
                rowb64 = base64.b64encode(decoded).decode('utf-8').strip()
                
                steg_char = stegb64.rstrip('=')[-1]
                row_char = rowb64.rstrip('=')[-1]
                
                offset = abs(B64CHARS.index(steg_char) - B64CHARS.index(row_char))
                equalnum = stegb64.count('=')
                
                if equalnum:
                    bin_str += f"{offset:0{equalnum * 2}b}"
                
                # 实时解码并输出，每次换行
                message = ''
                for i in range(0, len(bin_str), 8):
                    if i + 8 <= len(bin_str):
                        message += chr(int(bin_str[i:i+8], 2))
                print(message)  # 每次输出后自动换行
                
            except Exception as e:
                print(f"Error processing line: {e}")

if __name__ == '__main__':
    decode_b64_stego('stego.txt')
```




<!-- Imported from D:\\Book\\Misc\\Chapter1\1-18.md -->
### 文件二进制图像化


![](https://pic1.imgdb.cn/item/67e8175f0ba3d5a1d7e689b4.png)

下载附件放入 010 中找到一串 Base64 编码

![](https://pic1.imgdb.cn/item/67e8176a0ba3d5a1d7e689b6.png)

解密提示 01 二进制

![](https://pic1.imgdb.cn/item/67e817850ba3d5a1d7e689be.png)

将其转为二进制形式

![](https://pic1.imgdb.cn/item/67e817980ba3d5a1d7e689c7.png)

原来是用 01 二进制画了个图

```
CatCTF{CAT_GOES_MEOW}
```

![](https://pic1.imgdb.cn/item/67e817ae0ba3d5a1d7e689cc.png)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-19.md -->
### .rock


![](https://pic1.imgdb.cn/item/67e911510ba3d5a1d7e6b928.png)

下载附件给了 .rock 文件

![](https://pic1.imgdb.cn/item/67e911920ba3d5a1d7e6b953.png)

去 GitHub 上下载转换工具将其转为 Python 代码

```python
pip install rockstar-py
```

![](https://pic1.imgdb.cn/item/67e912450ba3d5a1d7e6b9ba.png)

转换

```shell
rockstar-py -i Become_a_Rockstar.rock -o res.py
```

运行 res.py 多按几下回车拿到 flag

![](https://pic1.imgdb.cn/item/67e9158e0ba3d5a1d7e6bc08.png)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-2.md -->
### 文件属性


![1](https://pic1.imgdb.cn/item/6771000ed0e0a243d4ec17bd.jpg)

查看文件属性即可

![2](https://pic1.imgdb.cn/item/67710027d0e0a243d4ec17c8.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-20.md -->
### XORTools


![](https://pic1.imgdb.cn/item/67e9201e0ba3d5a1d7e6c205.png)

打开文件全是数据且文件头尾不和任何类型的文件头尾有相似的文件都是文件数据被异或加密了

下载工具 Xortools 解密

```python
pip3 install xortool
```

解密这里有问题，应该是 `GoodLuckToYou`

![](https://pic1.imgdb.cn/item/67e9218b0ba3d5a1d7e6c229.png)

使用脚本解密

```python
key = 'GoodLuckToYou'
flag = ''

with open('1') as f:
    con = f.read()
    for i in range(len(con)):
        flag += chr(ord(con[i]) ^ ord(key[i%13]))
        
f = open('flag.txt', 'w')
f.write(flag)
f.close()
```

![](https://pic1.imgdb.cn/item/67e922900ba3d5a1d7e6c24a.png)



<!-- Imported from D:\\Book\\Misc\\Chapter1\1-21.md -->


![](https://pic1.imgdb.cn/item/67ea22c50ba3d5a1d7e797a0.png)

题目附件给了一个后缀为 .pyc 文件，010 打开仔细查看数据，发现有倒置的 flag1 和 flag2

![](https://pic1.imgdb.cn/item/67ea241a0ba3d5a1d7e7982a.png)

因此我们写个 python 脚本将数据倒置回来

然后 foremost 一下可以得到一个伪加密的压缩包

![](https://pic1.imgdb.cn/item/67ea24440ba3d5a1d7e7982f.png)

压缩包的注释中有 flag1 和 flag2

![](https://pic1.imgdb.cn/item/67ea24560ba3d5a1d7e79833.png)

去除伪加密后解压可以得到一个 Dream It Possible.mp3

![](https://pic1.imgdb.cn/item/67ea247e0ba3d5a1d7e79839.png)

这里需要使用 DeEgger Embedder 提取出隐藏的数据

![](https://pic1.imgdb.cn/item/67ea24910ba3d5a1d7e7983b.png)

用上面那个工具可以提取出一大串 base32 编码的字符串，直接解码发现没有得到什么有用的信息

尝试 base32 隐写解密

```python
import base64

def get_base32_diff_value(stego_line, normal_line):
    base32chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    for i in range(len(normal_line)):
        if stego_line[i] != normal_line[i]:
            return abs(base32chars.index(chr(stego_line[i]))-base32chars.index(chr(normal_line[i])))
    return 0

# base32 隐写解密
def base32stego_decode(lines):
    res = ''
    for i in lines:
        stego_line = i.strip()
        normal_line = base64.b32encode(base64.b32decode(i.strip()))
        diff = get_base32_diff_value(stego_line, normal_line)
        if '=' not in str(stego_line):
            continue
        if diff:
            res += bin(diff)[2:]
        else:
            res += '0'
    return res

with open("Dream It Possible - extracted.txt", 'rb') as f:
    file_lines = f.readlines()
en=open("encrypt.txt","w")
en.write(base32stego_decode(file_lines))
en.close()
```

提取 base32 隐写的数据可以得到一大串二进制的字符，这里还不知道具体干啥用，转图片也没有发现有用的信息

因此我们回头分析那个 pyc 文件，直接使用 uncompyle6 就可以反编译出原来的 Python 源码

```python
# uncompyle6 version 3.9.1
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.8.10 (tags/v3.8.10:3d8993a, May  3 2021, 11:48:03) [MSC v.1928 64 bit (AMD64)]
# Embedded file name: Fl4g.py
# Compiled at: 2017-07-02 00:15:33
from os import urandom

def generate(m, k):
    result = 0
    for i in bin(m ^ k)[2:]:
        result = result << 1
        if int(i):
            result = result ^ m ^ k
        if result >> 256:
            result = result ^ P

    return result


def encrypt(seed):
    key = int(urandom(32).encode('hex'), 16)
    while True:
        yield key
        key = generate(key, seed) + 233333333333L


def convert(string):
    return int(string.encode('hex'), 16)


P = 115792089237316195423570985008687907853269984665640564039457584007913129640997L
flag1 = 'ThIs_Fl4g_Is_Ri9ht'
flag2 = 'Hey_Fl4g_Is_Not_HeRe'
key = int(urandom(32).encode('hex'), 16)
data = open('data.txt', 'r').read()
result = encrypt(key)
encrypt1 = bin(int(data, 2) ^ eval('0x' + hex(result.next())[2:-1] * 22))[2:]
encrypt2 = hex(convert(flag1) ^ result.next())[2:-1]
encrypt3 = hex(convert(flag2) ^ result.next())[2:-1]
print 'flag1:', encrypt2
print 'flag2:', encrypt3
f = open('encrypt.txt', 'w')
f.write(encrypt1)
f.close()

# okay decompiling .\reverse_1_PyHaHa.pyc
```

由上述代码可知我们之前得到的二进制数据应该就是上述代码中的 encrypt.txt

因此我们写一个 Python 脚本去还原出原来的数据，具体脚本如下：

```python
from PIL import Image
import libnum
import os


def generate(m, k):
    result = 0
    for i in bin(m ^ k)[2:]:
        result = result << 1
        if int(i):
            result = result ^ m ^ k
        if result >> 256:
            result = result ^ P

    return result


def draw2pic(data):
    if os.path.exists("pic_output"):
        print("[!] pic_output 目录已存在")
    else:
        print("[+] pic_output 目录创建成功")
        os.mkdir("pic_output")
    length = len(data)
    dic = {X: int(length / X)
           for X in range(1, length) if length % X == 0}
    for item in dic.items():
        pos = 0
        img = Image.new("RGB", (item[0], item[1]))
        for x in range(item[0]):
            for y in range(item[1]):
                if data[pos] == '0':
                    img.putpixel([x, y], (0, 0, 0))
                else:
                    img.putpixel([x, y], (255, 255, 255))
                pos += 1
        img.save(f"./pic_output/{item[0]}_{item[1]}.png")
        print(
            f"./pic_output/{item[0]}_{item[1]}.png Saved!")


if __name__ == "__main__":
    P = 115792089237316195423570985008687907853269984665640564039457584007913129640997
    flag1 = 'ThIs_Fl4g_Is_Ri9ht'
    flag2 = 'Hey_Fl4g_Is_Not_HeRe'
    encrypt2 = 0xec8d57d820ad8c586e4be0122b442c871a3d71cd8036c45083d860caf1793ddc
    encrypt3 = 0xc40a0be335babcfbd8c47aa771f6a2ceca2c8638caa5924da58286d2a942697e
    encrypt1 = open('encrypt.txt', 'r').read()
    key2 = encrypt2 ^ libnum.s2n(flag1)
    key3 = encrypt3 ^ libnum.s2n(flag2)
    print(key2)
    print(key3)
    tmp = key3 - 233333333333
    for i in range(0, 255):
        tmp = generate(tmp, 0)
    seed = tmp ^ key2
    print('Found seed:', seed)
    print('use seed generate key3:', generate(key2, seed)+233333333333)
    tmp = key2 - 233333333333
    for i in range(0, 255):
        tmp = generate(tmp, 0)
    key1 = tmp ^ seed
    print('Found key1:', key1)
    print('use key1 generate key2:', generate(key1, seed)+233333333333)
    tmp1 = hex(int(encrypt1, 2))
    tmp2 = '0x'+hex(key1)[2:]*22
    pic_data = bin(int(tmp1, 16) ^ int(tmp2, 16))[2:]
    draw2pic(pic_data)
```

![](https://pic1.imgdb.cn/item/67ea29720ba3d5a1d7e7a4cf.png)



<!-- Imported from D:\\Book\\Misc\\Chapter1\1-22.md -->
### .lnk


![](https://pic1.imgdb.cn/item/680cf94858cb8da5c8cfc93e.png)

放入 010 中显示 `.lnk` 后缀

![](https://pic1.imgdb.cn/item/680cf9af58cb8da5c8cfc954.png)

`cmd` 运行直接报错

![](https://pic1.imgdb.cn/item/680cfa5758cb8da5c8cfc974.png)

但是生成了一个 flag 文件

![](https://pic1.imgdb.cn/item/680cfab558cb8da5c8cfc986.png)

按路径打开拿到 flag

![](https://pic1.imgdb.cn/item/680cfae558cb8da5c8cfc99d.png)




<!-- Imported from D:\\Book\\Misc\\Chapter1\1-23.md -->
### 隐藏文件


![](https://pic1.imgdb.cn/item/6834808758cb8da5c80fb210.png)

新手题，在 Windows 中勾选查看隐藏文件即可

![](https://pic1.imgdb.cn/item/6834835c58cb8da5c80fb313.png)

进入 `.ThePassword` 目录拿到密码

![](https://pic1.imgdb.cn/item/6834838258cb8da5c80fb323.png)

打开 PDF 输入密码

![](https://pic1.imgdb.cn/item/683483ae58cb8da5c80fb33d.png)

拿到 flag

![](https://pic1.imgdb.cn/item/683483cd58cb8da5c80fb352.png)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-24.md -->
### .kdbx（Key）


![](https://pic1.imgdb.cn/item/68732b6658cb8da5c8a643f5.png)

下载文件后先把后缀名 `.zip` 补上，再解压缩

![](https://pic1.imgdb.cn/item/68732d4558cb8da5c8a64445.png)

`.kdbx` 文件需要 keepass 打开，打开发现需要密码

![](https://pic1.imgdb.cn/item/68732e6058cb8da5c8a6447f.png)

`keepass2john` 是 **John The Ripper**（简称 **JtR**）自带的辅助工具

用于把 **KeePass** 密码库（`.kdbx` 文件）转换为 **John the Ripper 可识别的哈希格式**

从而可以使用暴力破解（如字典攻击、规则攻击等）去破解主密码

```sh
keepass2john '/home/kali/len5.kdbx'
```

![](https://pic1.imgdb.cn/item/687330f858cb8da5c8a64cad.png)

删掉开头的 `len5:`

![](https://pic1.imgdb.cn/item/6873332558cb8da5c8a65e1e.png)

使用工具 HashCat 爆破

```sh
hashcat -m 13400 keepass.hash  -a 0 password.txt  --force
# m：破解的 hash类型，hashcat -h 何查看类型
# a：爆破的方法，0 表示字典爆破
# force：不报错
```

得到密码 13152，打开文件得到压缩包的密码

![](https://pic1.imgdb.cn/item/6873393e58cb8da5c8a675a0.png)

解压得到两个文件

![](https://pic1.imgdb.cn/item/687339ef58cb8da5c8a675aa.png)

`hint.txt` 是零宽隐写，得到 `22*160`

![](https://pic1.imgdb.cn/item/68733a0d58cb8da5c8a675ad.png)

这里涉及到 `塔珀自指公式(Tupper's self-referential formula)` 知识点，但默认的 online decode 标准是 `17*106` 的

![](https://pic1.imgdb.cn/item/68733ec258cb8da5c8a676c6.png)

参考提示写脚本重新绘图

```python
from functools import reduce


def Tuppers_Self_Referential_Formula():
    k = 92898203278702907929705938676672021500394791427205757369123489204565300324859717082409892641951206664564991991489354661871425872649524078000948199832659815275909285198829276929014694628110159824930931595166203271443269827449505707655085842563682060910813942504507936625555735585913273575050118552353192682955310220323463465408645422334101446471078933149287336241772448338428740302833855616421538520769267636119285948674549756604384946996184385407505456168240123319785800909933214695711828013483981731933773017336944656397583872267126767778549745087854794302808950100966582558761224454242018467578959766617176016660101690140279961968740323327369347164623746391335756442566959352876706364265509834319910419399748338894746638758652286771979896573695823608678008814861640308571256880794312652055957150464513950305355055495262375870102898500643010471425931450046440860841589302890250456138060738689526283389256801969190204127358098408264204643882520969704221896973544620102494391269663693407573658064279947688509910028257209987991480259150865283245150325813888942058

    def f(x, y):
        d = ((-22 * x) - (y % 22))
        e = reduce(lambda x, y: x * y, [2 for x in range(-d)]) if d else 1
        g = ((y // 22) // e) % 2
        return 0.5 < g

    for y in range(k + 21, k - 1, -1):
        line = ""
        for x in range(0, 160):
            if f(x, y):
                line += " ■"
            else:
                line += "  "
        print(line)


if __name__ == '__main__':
    Tuppers_Self_Referential_Formula()
```

运行结果得到三个数 `33`、`121`、`144`

```python
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■         ■ ■ ■ ■         ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■   ■ ■ ■ ■ ■ ■ ■   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■         ■ ■ ■ ■         ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■   ■ ■ ■ ■ ■ ■ ■   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■         ■ ■ ■ ■         ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■   ■ ■ ■         ■ ■ ■   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■   ■ ■ ■   ■ ■   ■ ■ ■   ■ ■   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■   ■ ■ ■ ■ ■ ■   ■ ■ ■   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■   ■ ■ ■   ■ ■   ■ ■ ■   ■ ■   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■   ■ ■ ■         ■ ■ ■   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■   ■ ■ ■         ■ ■ ■         ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■   ■ ■ ■   ■ ■ ■ ■ ■ ■   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■   ■ ■ ■ ■ ■ ■   ■ ■ ■ ■ ■ ■   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■   ■ ■ ■         ■ ■ ■   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■   ■ ■ ■ ■ ■ ■   ■ ■ ■ ■ ■ ■   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
 ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■  

Process finished with exit code 0
```

题目名有提示猫，最后应该是 Arnold 变换

```python
from PIL import Image

img = Image.open('flag.png')
if img.mode == "P":
    img = img.convert("RGB")
assert img.size[0] == img.size[1]
dim = width, height = img.size

st = 33
a = 121
b = 144
for _ in range(st):
    with Image.new(img.mode, dim) as canvas:
        for nx in range(img.size[0]):
            for ny in range(img.size[0]):
                y = (ny - nx * a) % width
                x = (nx - y * b) % height
                canvas.putpixel((y, x), img.getpixel((ny, nx)))
canvas.show()
canvas.save('result.png')
```

![](https://pic1.imgdb.cn/item/68733fc358cb8da5c8a67c00.png)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-25.md -->
### 加密 Word 的宏（Key）


![](https://pic1.imgdb.cn/item/687353d758cb8da5c8a6e751.png)

有个加密文档，所以要破解密码，010 打开分析一下

拉到尾部范围内也是有很多字符串信息，其中有一段十六进制，但这些都解不出来没啥用，仔细往上看可以发现一些宏的现象

![](https://pic1.imgdb.cn/item/6873564458cb8da5c8a6e7f1.png)

所以我们可以用 oletools 提取出 vba 脚本

`oletools` 是一套由 **Decalage** 开发的开源工具集

专门用于分析 **Microsoft OLE2 文件**（也称 **OLE Compound File**，如 `.doc`, `.xls`, `.ppt`, `.msi`, `.vsd` 等旧版 Office 格式）

以及一些现代 **OpenXML 格式**（`.docm`, `.xlsm` 等）

```sh
pip install oletools
olevba attachment.doc
```

![](https://pic1.imgdb.cn/item/687357fb58cb8da5c8a6e82e.png)

```vbscript
Sub XOREncryptFile()
    Dim numbers(8) As Integer
    numbers = [19, 71, 122, 99, 65, 111, 43, 67]

    ' 查找当前目录下是否存在名为 "abc" 的文件
    If Dir(".\abc") = "" Then Exit Sub

    ' 读取 abc 文件内容
    Open ".\abc" For Binary Read Write As #FileNumber
    FileContent = Input$(LOF(FileNumber), #FileNumber)
    Close #FileNumber

    ' XOR 加密
    For i = 1 To Len(FileContent)
        EncryptedContent = EncryptedContent & Chr(Asc(Mid(FileContent, i, 1)) Xor numbers((i - 1) Mod 8))
    Next i

    ' 写入 enc 文件
    Open ".\enc" For Binary Write As #FileNumber
    Put #FileNumber, , EncryptedContent
    Close #FileNumber
End Sub
```

注意这里我们通过脚本可以得到 `13477a63416f2b43` 这个就是异或的 Key

而被 XOR 的字符串感觉像是文档最下面的那一串十六进制

![](https://pic1.imgdb.cn/item/687361c158cb8da5c8a72b6e.png)

![](https://pic1.imgdb.cn/item/6873621558cb8da5c8a72b78.png)

然后得到密码去打开文档得到信息

```
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
```

Base64 解码后得到一个 ZIP 文件

![](https://pic1.imgdb.cn/item/687362ef58cb8da5c8a72b8b.png)

我们发现第 A 列下第二行处 04 这个地方文件名长度有问题，我们给它改回去改成 08

![](https://pic1.imgdb.cn/item/6873637058cb8da5c8a72ba9.png)

破解伪加密后拿到 flag

![](https://pic1.imgdb.cn/item/6873633158cb8da5c8a72ba1.png)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-26.md -->
### LOLCODE


![](https://pic1.imgdb.cn/item/6875b14e58cb8da5c8ae5a8f.png)

打卡文件

![](https://pic1.imgdb.cn/item/6875b16858cb8da5c8ae5a92.png)

**LOLCODE** 是一种诙谐幽默的 **怪诞型编程语言（Esoteric Programming Language）**，诞生于 2007 年，由 **Adam Lindsay** 设计。灵感来源于早期互联网流行的 **LOLCats 文化**，那种用滑稽错误英语（Engrish）写出来的迷因图，如 “I CAN HAS CHEEZBURGER?”。

这门语言本质是为了搞笑，语言结构模仿这种“猫语+错别字+网民黑话”，不具备实用性，但具备完整的编程语法特征

| 功能     | C语言写法       | LOLCODE 写法                         |
| -------- | --------------- | ------------------------------------ |
| 定义变量 | `int x = 5;`    | `I HAS A X ITZ 5`                    |
| 输出     | `printf("hi");` | `VISIBLE "hi"`                       |
| 条件     | `if ... else`   | `O RLY? YA RLY NO WAI`               |
| 循环     | `while`         | `IM IN YR LOOP ... IM OUTTA YR LOOP` |
| 输入     | `scanf`         | `GIMMEH VAR`                         |

解密得到 Key

![](https://pic1.imgdb.cn/item/6875b1ad58cb8da5c8ae5d80.png)

解压缩包得到 1.docx，内容提示 AES，无其他内容，尝试将 docx 修改成 .zip 解压发现 fllllllllll1ag.txt

![](https://pic1.imgdb.cn/item/6875b1ec58cb8da5c8ae5ffb.png)

Emoji 符号加上之前提示的 AES，猜测为 Emoji-AES，Key 继续猜测为之前的 Key，有点小脑洞 Rotation=4

![](https://pic1.imgdb.cn/item/6875b23958cb8da5c8ae6272.png)

![](https://pic1.imgdb.cn/item/6875b25b58cb8da5c8ae63fd.png)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-27.md -->
### Folders


![](https://pic1.imgdb.cn/item/6877175c58cb8da5c8b65c86.png)

一个流量包，wireshark 打开，追踪最后一个 TCP 流

读一下请求，发现是进入到了 flag 目录下执行了 tree 命令

得到的 response 是 gzip 压缩后的，取出内容，然后解压得到 tree 的结果

```sh
flag
`-- New\ folder
    |-- New\ folder
    |   |-- New\ folder
    |   |-- New\ folder\ (2)
    |   |-- New\ folder\ (3)
    |   `-- New\ folder\ (4)
    `-- New\ folder\ (2)
        |-- New\ Folder\ (3)
        |   |-- New\ folder
        |   |   |-- New\ folder
        |   |   |   |-- New\ folder
        |   |   |   |-- New\ folder(2)
        |   |   |   |   `-- New\ folder
        |   |   |   |-- New\ folder(3)
        |   |   |   |   `-- New\ folder
        |   |   |   `-- New\ folder(4)
        |   |   |       `-- New\ folder
        |   |   `-- New\ folder(2)
        |   |       |-- New\ folder
        |   |       |-- New\ folder(2)
        |   |       |   `-- New\ folder
        |   |       |-- New\ folder(3)
        |   |       |   `-- New\ folder
        |   |       `-- New\ folder(4)
        |   |-- New\ folder(10)
...
```

不难发现，是一堆空文件夹形成的结构

然后就回想起了之前看到的一种 esolang 叫 Folders，是通过一堆嵌套的空文件夹编写的，这个可能就是

先重建起这个目录结构，没找到逆 tree 的现成工具，只好手写一个了

```python
import os
from pathlib import Path

with open("test", "r") as f:
    tree = f.readlines()

path = Path("flag")
last_level = -1

for each in tree:
    level = each.find("N")//4
    if level < last_level:
        path = path.parent
    if level == last_level:
        path = path.parent
    diff = last_level - level
    for _ in range(diff):
        path = path.parent
    path = path / each.strip().replace("\\", "")
    last_level = level
    os.makedirs(path)
```

得到 flag：`vnctf{d23903879df57503879bcdf1efc141fe}`

[参考链接](https://note.tonycrane.cc/writeups/vnctf2022/)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-28.md -->
### Minecraft JSON


![](https://pic1.imgdb.cn/item/68771a5258cb8da5c8b6791e.png)

这题要在《我的世界》这个游戏里面做任务，拿到最后一本书才能拿到 flag

Everything 搜索 `flag` 关键字，发现 `.minecraft\saves\Where is the flag` 存档目录

![](https://pic1.imgdb.cn/item/68771e0c58cb8da5c8b6990d.png)

找到任务

![](https://pic1.imgdb.cn/item/68771e2c58cb8da5c8b69a61.png)

在 JSON 文件里找有关书的线索

![](https://pic1.imgdb.cn/item/68771e7258cb8da5c8b69d6e.png)

![](https://pic1.imgdb.cn/item/68771ea458cb8da5c8b69f1f.png)

一共有四个，结合起来就是 `GKCTF{w3lc0me_t0_9kctf_2021_Check_1n}`


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-29.md -->
### Git 历史版本


![](https://pic1.imgdb.cn/item/67b067fcd0e0a243d4ff9fac.jpg)

网页啥也没有，先扫他目录

![](https://pic1.imgdb.cn/item/67b06810d0e0a243d4ff9fb1.jpg)

有个 flag.txt，但是是假的

![](https://pic1.imgdb.cn/item/67b06823d0e0a243d4ff9fbf.jpg)

还有个 .git 文件，下载下来查看

![](https://pic1.imgdb.cn/item/67b0683ad0e0a243d4ff9fc3.jpg)

git show 查看历史版本找到 flag

![](https://pic1.imgdb.cn/item/67b0684cd0e0a243d4ff9fc7.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-3.md -->
### 数据逆序

**原理是通过分析文件末十六进制数据推测出数据是倒序的**


![1](https://pic1.imgdb.cn/item/677100bcd0e0a243d4ec17f0.jpg)

放入 WinHex 中发现文件末尾是 PNG

![2](https://pic1.imgdb.cn/item/677100dcd0e0a243d4ec17f7.jpg)

编写脚本将数据逆序排列，然后

```python
def reverse_hex_string(hex_str):
    # 将字符串按两个字符分组，然后逆序
    reversed_hex_str = ''.join([hex_str[i:i + 2] for i in range(0, len(hex_str), 2)][::-1])

    file_name = '十六进制逆序结果.txt'

    # 将十六进制字符串转换为字节对象
    reversed_hex_str = bytes.fromhex(reversed_hex_str)

    # 打开文件写入
    with open(file_name, 'wb') as f:
        f.write(reversed_hex_str)


def main():
    # 文件十六进制数据
    hex_string = ""

    reverse_hex_string(hex_string)


if __name__ == '__main__':
    main()
```

重命名后打开拿到 flag

![3](https://pic1.imgdb.cn/item/67710329d0e0a243d4ec18f0.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-30.md -->
### Git Stash


![](https://pic1.imgdb.cn/item/6878c1cc58cb8da5c8beb62e.png)

stash 用于保存 git 工作状态到 git 栈，在需要的时候再恢复

尝试访问敏感目录，发现 .git 目录

```
http://challenge-397308928286c868.sandbox.ctfhub.com:10800/.git/config
```

利用 GitHack 工具将网站源代码 Clone 到本地

```
python2 GitHack.py http://challenge-397308928286c868.sandbox.ctfhub.com:10800/.git/
```

执行 `git stash list` 发现有 stash

`git stash list` 用于**查看 Git 暂存栈（stash stack）中的所有保存项**

![](https://pic1.imgdb.cn/item/6878c23f58cb8da5c8beb69a.png)

执行 `git stash pop` 发现从 git 栈中弹出来一个文件，这个文件的内容就是 flag

`git stash pop` 用于**将最近的 stash 应用到当前分支，并自动从 stash 列表中删除该记录**

![](https://pic1.imgdb.cn/item/6878c35458cb8da5c8beb7bb.png)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-31.md -->
### YARA 恶意软件检测


![](https://pic1.imgdb.cn/item/68a299f058cb8da5c82c442e.png)

**YARA** = *Yet Another Ridiculous Acronym*

是一个用于 **恶意代码识别与分类** 的开源工具

通过编写 **规则（rule）** 来匹配文件或内存中的 **字符串、字节模式、正则表达式**

安全研究员常称它为 **恶意软件分析师的瑞士军刀**

```yara
rule test
{
    strings:
        $str1 = "UPX0" wide ascii
        $str2 = "AdjustTokenPrivileges" wide ascii
        $str3 = "LookupPrivilegeValueW" wide ascii

    condition:
        $str1 or ($str2 and $str3)
}
```

`rule test`

- 定义了一个规则，名字叫 **`test`**

- 当 YARA 扫描文件时，如果这个规则触发，就会输出：

  ```sh
  test suspicious.exe
  ```

这里定义了要匹配的字符串

- **`$str1 = "UPX0" wide ascii`**
  - 匹配文件中是否出现 `"UPX0"` 这个字符串
  - `ascii` = 普通 ASCII 字符串
  - `wide` = UTF-16LE 宽字节字符串
  - 也就是说，YARA 会同时匹配 `"UPX0"` 和 `"U\x00P\x00X\x000\x00"`
- **`$str2 = "AdjustTokenPrivileges" wide ascii`**
  - 匹配 Windows API 函数名 `"AdjustTokenPrivileges"`，通常用于修改进程权限
- **`$str3 = "LookupPrivilegeValueW" wide ascii`**
  - 匹配 API `"LookupPrivilegeValueW"`，常配合上一个 API 一起用来提升权限

`condition:` 部分

这是判断逻辑，决定什么时候触发

```yara
$str1 or ($str2 and $str3)
```

意思是：

- **情况 A**：文件里出现 `$str1`（即 `"UPX0"`）
- **情况 B**：文件里同时出现 `$str2` 和 `$str3`（即 `"AdjustTokenPrivileges"` + `"LookupPrivilegeValueW"`）

只要满足 **A 或 B**，这个规则就会触发

`"AdjustTokenPrivileges"` + `"LookupPrivilegeValueW"` → 这是 Windows 程序里典型的 **提权 API 组合**

开启终端会给出命令，匹配规则写入 `rules.txt `中

![](https://pic1.imgdb.cn/item/68a29d2258cb8da5c82c66a7.png)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-4.md -->
### DMG 文件

**DMG 文件是 Mac 操作系统中的一种磁盘映像文件格式**


![1](https://pic1.imgdb.cn/item/6771038ed0e0a243d4ec1902.jpg)

虚拟机中有 MacOS 的话直接拖入没有则只能网上找其他工具了

![2](https://pic1.imgdb.cn/item/677105e0d0e0a243d4ec1978.jpg)

打开发现需要密码

![3](https://pic1.imgdb.cn/item/67711214d0e0a243d4ec1d82.jpg)

在 WinHex 中发现字符串

![4](https://pic1.imgdb.cn/item/67711236d0e0a243d4ec1db7.jpg)

尝试一下解压缩

![5](https://pic1.imgdb.cn/item/67711255d0e0a243d4ec1dd2.jpg)

可以成功打开文件

![6](https://pic1.imgdb.cn/item/67711288d0e0a243d4ec1e56.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-5.md -->
### 文件格式

**具体原理就是修改文件格式来隐藏原来的真实文件**


![1](https://pic1.imgdb.cn/item/6771139ad0e0a243d4ec1f4e.jpg)

前面的步骤可以参考 Zip 明文攻击那一节

这里讲解本节重要内容

打开 word 没线索

![2](https://pic1.imgdb.cn/item/67711428d0e0a243d4ec1f64.jpg)

扔进 WinHex 中发现文件头是压缩文件，将文件 word 修改为 zip

![3](https://pic1.imgdb.cn/item/6771143cd0e0a243d4ec1f65.jpg)

解压缩后打开拿到 flag

![4](https://pic1.imgdb.cn/item/67711489d0e0a243d4ec1f72.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-6.md -->
### Snow 文件


![](https://pic1.imgdb.cn/item/677114f6d0e0a243d4ec1f8f.jpg)

前面步骤就是编写一个时间戳脚本

如果秒数大于 40，则记为 1，否则即为 0

再将得到的二进制转另存为 7z 文件

得到 snow.txt

```python
# ctf_check.py
import os, time, string, sys
from pathlib import Path

WORK_DIR = r'CTF\files'   # ← 改成你的目录（不要以 / 结尾也可以）
OUT_PREFIX = Path(WORK_DIR) / "result_variant"

def build_hex_from_mtime():
    flag = ''
    out = ''
    for i in range(1936):
        path = os.path.join(WORK_DIR, f"{i}.txt")
        if not os.path.exists(path):
            raise FileNotFoundError(f"缺少文件: {path}")
        file_time = os.path.getmtime(path)
        s = time.ctime(file_time)
        sec = int(s[17:19])   # 和你原来逻辑一致
        flag += '1' if sec >= 40 else '0'
        if len(flag) == 8:
            out += hex(int('0b' + flag, 2))[2:].zfill(2)
            flag = ''
    return out

def is_clean_hex(h):
    h2 = h.strip()
    return len(h2) % 2 == 0 and all(c in string.hexdigits for c in h2)

def hex_to_bitstr(h):
    return ''.join(f"{int(h[i:i+2],16):08b}" for i in range(0,len(h),2))

def bitstr_to_hex(bs):
    return ''.join(hex(int(bs[i:i+8],2))[2:].zfill(2) for i in range(0,len(bs),8))

def write_bytes_from_hex(h, outpath):
    data = bytes.fromhex(h)
    outpath.write_bytes(data)
    return data

def try_py7zr_extract(path, extract_to):
    try:
        import py7zr
    except Exception as e:
        return False, f"py7zr 未安装或导入失败: {e}"
    try:
        with py7zr.SevenZipFile(path, mode='r') as zf:
            zf.extractall(path=extract_to)
        return True, "OK"
    except Exception as e:
        return False, f"py7zr 解压失败: {e}"

def main():
    print("[*] 生成十六进制串 ...")
    out = build_hex_from_mtime()
    print(f"[*] 生成 hex 长度: {len(out)} chars, bytes: {len(out)//2}")
    if not is_clean_hex(out):
        print("[!] 十六进制串包含非法字符或长度为奇数。请打印查看 out 内容。")
        print(out[:2000])
        return

    # 基本检查
    header = out[:8].upper()
    print("[*] 前8字符 (4 bytes) :", header)
    # 7z signature = 37 7A BC AF -> '377ABCAF'
    if header == '377ABCAF':
        print("[+] 看起来已包含 7z 文件头，直接写入 result.ok.7z")
        dst = Path(WORK_DIR) / "result.ok.7z"
        data = write_bytes_from_hex(out, dst)
        print(f"[+] 写入 {dst} (size {len(data)} bytes). 尝试用 py7zr 解压 ...")
        ok, msg = try_py7zr_extract(dst, Path(WORK_DIR)/"extracted_ok")
        print("->", ok, msg)
        return

    print("[*] 未检测到标准 7z 文件头 (377ABCAF)。开始尝试常见位/字节变换 ...")

    bitstr = hex_to_bitstr(out)
    variants = []

    # Variant A: 原样（msb-first per byte）
    variants.append(("orig", out))

    # Variant B: 每字节内部反转位（例如 0bABCDEFGH -> HGFEDCBA）
    bs_b = ''.join(bitstr[i:i+8][::-1] for i in range(0, len(bitstr), 8))
    variants.append(("bits_reversed_in_each_byte", bitstr_to_hex(bs_b)))

    # Variant C: 反转字节序（最后一个字节变为第一个）
    bytes_list = [out[i:i+2] for i in range(0, len(out), 2)]
    bytes_rev = ''.join(reversed(bytes_list))
    variants.append(("bytes_reversed_order", bytes_rev))

    # Variant D: bytes order reversed + bits reversed in each byte
    # do bits reverse on bytes_rev
    bs_from_bytes_rev = hex_to_bitstr(bytes_rev)
    bs_d = ''.join(bs_from_bytes_rev[i:i+8][::-1] for i in range(0, len(bs_from_bytes_rev), 8))
    variants.append(("bytes_reversed_and_bits_reversed_in_each_byte", bitstr_to_hex(bs_d)))

    # Variant E: 全位反转（把整个位串反过来，然后按 8 位分组）
    bs_e = bitstr[::-1]
    variants.append(("all_bits_reversed_then_group", bitstr_to_hex(bs_e)))

    # 试写每个变体并检查 7z header +（若可用）尝试 py7zr 解压
    found = False
    for idx, (name, hexstr) in enumerate(variants, start=1):
        p = Path(WORK_DIR) / f"result_variant_{idx}_{name}.7z"
        try:
            data = write_bytes_from_hex(hexstr, p)
        except Exception as e:
            print(f"[!] 写入 {p} 失败: {e}")
            continue
        print(f"[>] 写入 {p} (size {len(data)} bytes); header: {data[:4].hex().upper()}")
        if data[:4] == bytes.fromhex("377ABCAF"):
            print(f"[+] 变换 {name} 命中 7z signature (377ABCAF)。尝试用 py7zr 解压 ...")
            ok, msg = try_py7zr_extract(p, Path(WORK_DIR)/f"extracted_{idx}_{name}")
            print("->", ok, msg)
            if ok:
                # 复制为最终成功文件
                final = Path(WORK_DIR) / "result.ok.7z"
                final.write_bytes(data)
                print(f"[+] 已生成 result.ok.7z 并解压到 extracted_{idx}_{name}，请查看 snow.txt")
                found = True
                break
        else:
            print(f"    header mismatch: {data[:4].hex().upper()} != 377ABCAF")

    if not found:
        print("[!] 尝试完所有常见变换后仍未找到有效 7z header。")
        print("建议：")
        print("  1) 检查 out 是否确实包含 1936 bit (即 len(out)//2 应 = 242 bytes)。")
        print("  2) 如果你手动 copy/paste 过 hex，可能粘贴时丢了字符或加入了换行。确保直接用脚本生成并用 bytes.fromhex 写入。")
        print("  3) 如果你想我继续深挖，可以把（或打印）前 64 个 hex 字节给我，我帮你看 header/签名。")
    else:
        print("[*] 成功结束。")

if __name__ == '__main__':
    main()
```

![](https://pic1.imgdb.cn/item/67711534d0e0a243d4ec1fab.jpg)

使用工具提取，密码我是爆破出来的 5201314

![](https://pic1.imgdb.cn/item/67711563d0e0a243d4ec1faf.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-7.md -->
### NTFS 文件


![](https://pic1.imgdb.cn/item/67711605d0e0a243d4ec1fc1.jpg)

使用工具 NtfsStreamsEditor 导出即可

![](https://pic1.imgdb.cn/item/6771162fd0e0a243d4ec1fc4.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-8.md -->
### 文件时间戳


![](https://pic1.imgdb.cn/item/67711697d0e0a243d4ec1fd8.jpg)

压缩包内容如下

![](https://pic1.imgdb.cn/item/67711733d0e0a243d4ec1feb.jpg)

在 010 Editor 中打开获取精确的时间戳

![](https://pic1.imgdb.cn/item/67711761d0e0a243d4ec1ff4.jpg)

每个时间戳后三位都不一样

提取出来转 ASCII 得到压缩包密码

![](https://pic1.imgdb.cn/item/67711789d0e0a243d4ec2010.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter1\1-9.md -->
### 文件合并


![](https://pic1.imgdb.cn/item/67711834d0e0a243d4ec2020.jpg)

下载文件在 WinHex 中发现有隐藏文件

![](https://pic1.imgdb.cn/item/67711850d0e0a243d4ec2026.jpg)

使用工具 ForeMost 提取

![](https://pic1.imgdb.cn/item/6784ff35d0e0a243d4f3f14a.jpg)

提取出压缩包

![](https://pic1.imgdb.cn/item/6771189fd0e0a243d4ec202a.jpg)

找到 flag 文件

![](https://pic1.imgdb.cn/item/677118b9d0e0a243d4ec202c.jpg)

成功拿到 flag

![](https://pic1.imgdb.cn/item/677118d1d0e0a243d4ec202f.jpg)

## 总结

很多题目都是考了不同或者多方向的知识点，总之，学得越多越好