---
comments: true

---

# 音频隐写

<!-- Imported from D:\\Book\\Misc\\Chapter4\4-1.md -->
### MP3 （Key）

这是 MP3 最常见的隐写方法，主要是使用 MP3Stego 工具进行隐写


![](https://pic1.imgdb.cn/item/677f83b4d0e0a243d4f28523.jpg)

下载文件后是一段 MP3 音频，同时题目给出了 key：syclovergeek

因为 MP3Stego 工具隐写是需要密码的，那么可以先尝试使用工具解密提取

```shell
Decode.exe -X -P syclovergeek mp3
```

![](https://pic1.imgdb.cn/item/677f83c5d0e0a243d4f28529.jpg)

成功拿到 flag

![](https://pic1.imgdb.cn/item/677f8436d0e0a243d4f2856f.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter4\4-10.md -->
### Wav 文件 LSB


![](https://pic1.imgdb.cn/item/677f8cdad0e0a243d4f287e7.jpg)

下载文件发现是 Wav 文件，题目提示是 LSB 隐写

使用 Wav 文件 LSB 隐写工具：Stegolsb

```shell
-h：隐藏声音文件中的数据
-r：从声音文件中恢复数据
-i text：文件的路径
-s text：隐藏在声音文件中的文件路径
-o text：输出文件的路径
-n integer：使用多少个 LSB [默认值：2]
-b integer：从声音文件中恢复多少字节
```

![](https://pic1.imgdb.cn/item/677f8d5ad0e0a243d4f287fa.jpg)

成功拿到 flag

![](https://pic1.imgdb.cn/item/677f8dd0d0e0a243d4f28810.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter4\4-11.md -->
### 慢扫描电视


![](https://pic1.imgdb.cn/item/67e2ad060ba3d5a1d7e34bb3.png)

题目名提示了信号类型

![](https://pic1.imgdb.cn/item/67e2ad3b0ba3d5a1d7e34bd2.png)

将 MP3 文件外放，便可以得到一张图片（一定要安静）

![](https://pic1.imgdb.cn/item/67e2b0530ba3d5a1d7e34d93.png)

得到字符

```
f7liavga{1M_0105n_cC@okmei_nFge!s}
```

最后栅栏解密

![](https://pic1.imgdb.cn/item/67e2b0ba0ba3d5a1d7e34daa.png)


<!-- Imported from D:\\Book\\Misc\\Chapter4\4-12.md -->
### Private Bit


![](https://pic1.imgdb.cn/item/67e378840ba3d5a1d7e370ac.png)

使用 010 打开文件发现存在保留字位 private bit

![](https://pic1.imgdb.cn/item/67e37a1f0ba3d5a1d7e37120.png)

第一个是 0，第二个是 1

提前前八个得到 01000110，转为 ASCII 码是 F

以下是对于 struct MPEG_FRAME mf 的解析

| 名称               | 长度 (bit) | 作用                                                         |
| ------------------ | ---------- | ------------------------------------------------------------ |
| syncword           | 12         | 同步头，表示一帧数据的开始，共 12 位，全 1 即 0xFFF          |
| ID                 | 1          | 算法标识位，"1" 表示 MPEG 音频                               |
| layer              | 2          | 用来说明是哪一层编码                                         |
| protection_bit     | 1          | 用来表明冗余信息是否被加到音频流中，以进行错误检测和错误隐蔽；"1" 是未增加，"0" 是增加 |
| bitrate_index      | 4          | 用来指示该帧的 bitrate                                       |
| sampling_frequency | 2          | 用来指示采样频率                                             |
| padding_bit        | 1          | 如果该位为 1，那么帧中包含一个额外槽，用于把平均位率调节到采样频率，否则该位必须为 0 |
| private_bit        | 1          | 留做私用                                                     |
| mode               | 2          | 定义通道模式                                                 |
| mode_extension     | 2          | 用来标识采用了哪一种 joint_stereo                            |
| copyright          | 1          | 表明版权用，"1" 表示有版权，"0" 表示没有版权                 |
| original/home      | 1          | 表明原版还是复制，"1" 表示原版，"0" 表示复制                 |
| emphasis           | 2          | 表明加重音类型                                               |

一个 mf 的 HEADER 总共 12+1+2+1+4+2+1+1+2+2+1+1+2=32，即总共 4 字节

private_bit 为 24，所在的字节为第 3 个字节，因此该字节对应的地址为 235984+2=235986，即为第一个 private_bit 开始地址

可以发现在每个 MPEG_FRAME mf 下的 4 字节 MPEG_HEADER mpeg_hdr 中的第 24 个 bit 有一个 private bit

观察每一个 mf 组,大小为 417 或 418 字节，因此需要编写脚本

```python
import re

def extract_hidden_data(file_path):
    # ========== 参数设置部分 ==========
    # 初始读取位置(第一个 private bit 的起始位置)
    start_pos = 235986
    # 结束读取位置(通过分析发现此位置后 private_bit 都为 0)
    end_pos = 1369844
    # 基本组大小
    group_size = 417
    # 需要跳过额外字节的位置集合(使用集合提高查找效率)
    skip_positions = {0, 1, 26, 50, 75, 99, 124, 148, 173, 197,
                      222, 246, 271, 295, 320, 344, 369, 393, 418}

    # ========== 数据提取部分 ==========
    binary_data = []  # 用于存储提取的二进制位
    current_pos = start_pos  # 当前文件指针位置
    counter = 0  # 位置计数器

    with open(file_path, 'rb') as file:
        while current_pos < end_pos:
            # 移动文件指针到当前位置
            file.seek(current_pos)

            # 决定前进的步长:
            # - 如果在 skip_positions 中，前进 group_size(417)
            # - 否则前进 group_size + 1(418)
            step = group_size if counter in skip_positions else group_size + 1
            current_pos += step

            # 读取 1 个字节
            byte = file.read(1)
            if not byte:  # 如果读到文件末尾则终止
                break

            # 提取字节的最后一位(使用位运算比bin()更高效):
            # 1. ord(byte) 获取字节的整数值
            # 2. & 1 获取最低位
            # 3. str()转换为字符串形式('0'或'1')
            binary_data.append(str(ord(byte) & 1))

            counter += 1  # 位置计数器递增

    # ========== 数据处理部分 ==========
    # 将二进制位列表拼接成字符串
    binary_str = ''.join(binary_data)

    # 使用正则表达式将二进制字符串按 8 位一组分割
    # 然后将每组二进制转换为对应的 ASCII 字符
    hidden_text = ''.join([
        chr(int(byte, 2))  # 将 8 位二进制字符串转换为整数再转换为字符
        for byte in re.findall('.{8}', binary_str)  # 每 8 位分割
    ])

    # 返回处理后的文本(去除首尾空白字符)
    return hidden_text.strip()


if __name__ == '__main__':
    result = extract_hidden_data('1.mp3')
    print(result)
```

成功拿到 flag

![](https://pic1.imgdb.cn/item/67e37fc60ba3d5a1d7e37244.png)


<!-- Imported from D:\\Book\\Misc\\Chapter4\4-13.md -->
### 采样率


![](https://pic1.imgdb.cn/item/67e91dc10ba3d5a1d7e6c1b3.png)

放入 Audacity 中没有线索

![](https://pic1.imgdb.cn/item/67e91dd90ba3d5a1d7e6c1c3.png)

调整采样率看看

![](https://pic1.imgdb.cn/item/67e91e020ba3d5a1d7e6c1ca.png)

设置为 900

![](https://pic1.imgdb.cn/item/67e91e110ba3d5a1d7e6c1d1.png)

再查看频谱图就有了

![](https://pic1.imgdb.cn/item/67e91e290ba3d5a1d7e6c1d7.png)


<!-- Imported from D:\\Book\\Misc\\Chapter4\4-14.md -->
### Raw 无线电 AFSK1200


![](https://pic1.imgdb.cn/item/67e9ff680ba3d5a1d7e739f7.png)

先看文件类型

![](https://pic1.imgdb.cn/item/67e9ffc00ba3d5a1d7e73a3f.png)

在1100 Hz 和 2200 Hz 处有两个峰值

这是 AX.25 的 BFSK 中使用的两个音调

![](https://pic1.imgdb.cn/item/67ea001a0ba3d5a1d7e73ab0.png)

首先转换类型

需要先用 `sox` 把 wav 转为 raw

```shell
sox -t wav 997a0b28705f4ef086acfb7e1b932336 -esigned-integer -b16 -r 22050 -t raw latlong.raw

# sox: 调用 SoX 音频处理工具
# -t wav: 指定输入文件的类型为 WAV 格式
# 997a0b28705f4ef086acfb7e1b932336: 输入文件名（看起来像是一个哈希值命名的 WAV 文件）
# -esigned-integer: 指定输出音频的编码格式为有符号整数
# -b16: 指定输出音频的位深为 16 位（即每个样本占 16 位）
# -r 22050: 指定输出音频的采样率为 22050 Hz
# -t raw: 指定输出文件的类型为 RAW（原始音频数据，无文件头）
# latlong.raw: 输出文件名
```

![](https://pic1.imgdb.cn/item/67ea00db0ba3d5a1d7e73b48.png)

再使用工具 `multimon-ng` 解密

```shell
multimon-ng -t raw -a AFSK1200 latlong.raw

# -t 指定输入文件的类型
# -a 指定要使用的解码协议
# AFSK1200 表示解码 1200 bps 的音频频移键控（Audio Frequency-Shift Keying） 信号，这是 APRS（自动分组报告系统）等协议常用的调制方式
```

![](https://pic1.imgdb.cn/item/67ea01d90ba3d5a1d7e73bc5.png)


<!-- Imported from D:\\Book\\Misc\\Chapter4\4-15.md -->
### DeEgger Embedder


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


<!-- Imported from D:\\Book\\Misc\\Chapter4\4-16.md -->
### OGG/WAV 单色图像


![](https://pic1.imgdb.cn/item/67eb99090ba3d5a1d7e90136.png)

“120 LPM”提示指的是[天气传真](http://en.wikipedia.org/wiki/Radiofax)，一种传输单色图像的模拟模式

有一个名为 Multimode 的 OS X 应用程序可用于将音频转换回原始传真图像

但它只接受 WAV 文件作为输入，所以我首先转换 `similar.ogg` 为 `similar.wav` 使用 Audacity

![](https://pic1.imgdb.cn/item/67eb99e50ba3d5a1d7e90187.png)

正文如下：

```
section 1 of 1 of file rfax_man
begin 644 rfax_man
h5sg60BSxwp62+57aMLVTPK3i9b-t+5pGLKyPA-FxxuysvFs+BT8+o0dVsM24
hcZHRaWYEHRBGFGtqk-cMV7oqqQRzbobGRB9Kwc-pTHzCDSSMJorR8d-pxdqd
hLWpvQWRv-N33mFwEicqz+UFkDYsbDvrfOC7tko5g1JrrSX0swhn64neLsohr
h26K1mSxnS+TF1Cta8GHHQ-t1Cfp7nh-oZeFuVi5MEynqyzX8kMtXcAynSLQx
hg4o56Pu4YUZHMqDGtczKeCwXU8PZEc4lY0FbDfFfgZpJFC-a-sHGLtGJgCMZ
hksr6XNTedEUdVJqxOO5VaReoH68eEPJ2m6d9mKhlhVE7zw4Yru4DUWRCJH28
hyeth+l2I0gPnEfrTLwAc+-TPS0YKYY3K0np58gVPgdAN8RY7+rQfRDin9JSa
hPG32WG7-rTl3uthvrnDO-wD09GDIRCniuoefs8UsfiWZOLq+0awOrQxAPM+C
hxLwOJ9VUKwdn7dJduLn1KhBucvL1pr5lGiBFfUbL79cFFex+G27kT+fsQ7X5
h87mgPivWhDSQHKPXqpKGniDkYsIYpg66ZWbHp4PfcgtPukElDWENlQPSuNAQ
hnboE4Bd8kyyokt67GgfGvBVS45sMFPtlgKRlG-QPFSgbMHujA3qYemxnuqGx
hp97aXpdKpvAE8zx-oUzazoVFz32X3OxAuiWJhKEjaYKpM7f95yv1S62v+k++
+
end
sum —r/size 7468/769 section (from "begin" to "end")
sum —r/size 36513/540 entire input file
```

使用 XXdecoder 解码生成一个名为 的文件 `rfax_man`

![](https://pic1.imgdb.cn/item/67eb9e0f0ba3d5a1d7e90513.png)

```shell
$ file rfax_man
rfax_man: gzip compressed data, was "rfax_man.py", from FAT filesystem (MS-DOS, OS/2, NT), last modified: Thu Feb  6 17:52:39 2014, max speed
```

解压缩是一个 Python 脚本

```python
import socket,os,sys,hashlib

KEY  = "CTF{4BDF4498E4922B88642D4915C528DA8F}" # DO NOT SHARE THIS!
HOST = '109.233.61.11'
PORT = 8001

if len(sys.argv)<3:
  print 'Usage: rfax_man.py add|del file.png'
  print '\nAdd your pictures to transmission!\nSizes: 800<=width<=3200 and height/width <= 2.0.\nUse contrast grayscale pictures.'
  sys.exit(0)

data=open(sys.argv[2],'rb').read(1000000)

m=hashlib.md5(); m.update(KEY); KEYH=m.hexdigest().upper()
m=hashlib.md5(); m.update(data); h=m.hexdigest().upper()
print 'File hash',h

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print 'Connected.'

if sys.argv[1]=='add':
  s.sendall(KEYH+':ADD:'+data)
  s.shutdown(socket.SHUT_WR)
  print s.recv(1024)
elif sys.argv[1]=='del':
  s.sendall(KEYH+':DEL:'+h)
  print s.recv(1024)

s.close()
print 'Done.'
```




<!-- Imported from D:\\Book\\Misc\\Chapter4\4-17.md -->
### MP3 原版标志位


![](https://pic1.imgdb.cn/item/6872249758cb8da5c8a22313.png)

[数据帧分析参考博客](https://www.cnblogs.com/shakin/p/4012780.html)

重点在这，MP3 的数据帧第四字节倒数第三位为原版标志

![](https://pic1.imgdb.cn/item/687224cf58cb8da5c8a22f85.png)

可以在 010 的 template Results 窗口右键将结构数据导出到 csv 或者xml 文件，然后使用脚本读取

![](https://pic1.imgdb.cn/item/687224fd58cb8da5c8a23c45.png)

```python
import pandas as pd ,numpy as np,matplotlib.pyplot as plt,cv2 
tr = pd.read_csv('z:/ctf/fox01.csv')
mp3 = open('z:/ctf/fox01.mp3','rb').read()  
org =''.join([' ' if mp3[int(i['Start'][:-1],16)+3] &4 == 0 else '8' for _,i in tr[tr['Name'].str.startswith('struct MPEG_FRAME')].iterrows()])
print(org)
```

同样粘贴到文本编辑器里面，选择合适的宽度，结果就是下面这样

![](https://pic1.imgdb.cn/item/6872254158cb8da5c8a24e06.png)




<!-- Imported from D:\\Book\\Misc\\Chapter4\4-2.md -->
### 波形（Wav）

波形隐写原理就是将波形的高低转为二进制


![](https://pic1.imgdb.cn/item/677f84bdd0e0a243d4f28583.jpg)

下载文件后是一段 WAV 音频，放入工具 Audacity 中看波形图

![](https://pic1.imgdb.cn/item/677f84d6d0e0a243d4f2858d.jpg)

只有两种格式即分别对应二进制 0、1，写脚本跑一下

```python
import wave
import numpy as np

def main():
    wavfile = wave.open('music.wav', "rb")

    # 获取 WAV 文件的参数
    params = wavfile.getparams()

    # 获取音频的采样点数
    nframes = params[3]

    # 从 WAV 文件中读取所有帧的数据
    datawav = wavfile.readframes(nframes)

    wavfile.close()

    # 将读取的二进制数据（datawav）转换为一个 NumPy 数组，数据类型为短整型（np.short）
    datause = np.frombuffer(datawav, dtype=np.short)

    result_bin = ''

    # 记录当前的最大值
    mx = 0

    # 循环遍历 datause 数组，除了最后一个元素
    for i in range(len(datause) - 1):
        # 更新记录最大值的变量 mx
        if datause[i] > mx:
            mx = datause[i]

        # 检查当前元素是否为负数且下一个元素为非负数
        # 如果是，这意味着音频波形从负数跨越到0或正数，这可能是隐藏数据的标记点
        if datause[i] < 0 <= datause[i + 1]:

            # 检查从负数到非负数的跨越是否足够大（大于24000）
            # 用于区分隐藏数据位是 '1' 还是 '0' 的阈值
            if mx - 24000 > 0:
                result_bin += '1'

                mx = datause[i + 1]
            else:
                result_bin += '0'

                mx = datause[i + 1]


    result_hex = ''

    # 将二进制数据转换为十六进制
    for i in range(0, len(result_bin), 4):
        result_hex += hex(int(result_bin[i: i + 4], 2))[2:]

    print(result_hex)


if __name__ == '__main__':
    main()
```

最后跑出来是一个 RAR 文件（看文件头）

![](https://pic1.imgdb.cn/item/677f860bd0e0a243d4f285e0.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter4\4-3.md -->
### 音频倒放


![](https://pic1.imgdb.cn/item/677f8669d0e0a243d4f28606.jpg)

打开 Audacity 反转即可

![](https://pic1.imgdb.cn/item/677f867dd0e0a243d4f2862a.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter4\4-4.md -->
### 频谱图


![](https://pic1.imgdb.cn/item/677f86dad0e0a243d4f28662.jpg)

在 Audacity 中打开文件，打开多视图

![](https://pic1.imgdb.cn/item/677f86f4d0e0a243d4f28668.png)

有细有粗，分别对应摩斯密码 . -

摩斯密码解码即可拿到 flag

![](https://pic1.imgdb.cn/item/677f8714d0e0a243d4f28669.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter4\4-5.md -->
### 按键式电话


![](https://pic1.imgdb.cn/item/677f8848d0e0a243d4f2869f.jpg)

在线网站 DTMF 检测演示

![](https://pic1.imgdb.cn/item/677f8868d0e0a243d4f286aa.jpg)

最后解码即可

![](https://pic1.imgdb.cn/item/677f8888d0e0a243d4f286ba.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter4\4-7.md -->
### SilentEye （音频）


![](https://pic1.imgdb.cn/item/677f890bd0e0a243d4f286e3.jpg)

一般在使用这工具情况下是因为它的音频没有隐写，使用工具打开文件解密拿到密码

![](https://pic1.imgdb.cn/item/677f8913d0e0a243d4f286e5.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter4\4-8.md -->
### DeepSound （Key）


![](https://pic1.imgdb.cn/item/677f890bd0e0a243d4f286e3.jpg)

接上一节拿到了密码，想到要用密码加密的工具

使用 DeepSound 工具打开文件，输入密码

![](https://pic1.imgdb.cn/item/677f8a0ad0e0a243d4f2873c.jpg)

成功拿到 flag

![](https://pic1.imgdb.cn/item/677f8a63d0e0a243d4f28744.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter4\4-9.md -->
### Velato 编译（Mid）


![](https://pic1.imgdb.cn/item/677f8b88d0e0a243d4f28785.jpg)

MIDI 文件优先考虑 Velato 编译

Velato 是一种编程语言，使用 MIDI 文件作为源代码，音符模式决定命令

```shell
Vlt.exe music.mid
```

![](https://pic1.imgdb.cn/item/677f8baed0e0a243d4f28789.jpg)

接着运行编译好的文件，将这段字符解密即可拿到 flag

```shell
music.exe
```

![](https://pic1.imgdb.cn/item/677f8bc5d0e0a243d4f287a0.jpg)

<!-- Imported from D:\\Book\\Misc\\Chapter4\README.md -->
## 总结

很多题目都是考了不同或者多方向的知识点，总之，学得越多越好