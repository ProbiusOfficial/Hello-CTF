---
comments: true

---
## 前言

> 版权声明：
>
> ​	文档源于项目[ProbiusOfficial/Hello-CTF: 针对0基础新手编写的CTF快速入门手册 (github.com)](https://github.com/ProbiusOfficial/Hello-CTF)
>
> ​	原作者为 GaoNengwWw

流量分析与取证在misc中也是较为常见的题目，流量分析主要是根据元数据（不是通信内容本身）识别对手活动和通信模式，每条记录多达几兆字节的全部活动内容，可能只产生100字节的元数据，如端点（包括ip地址和域名）、端口、收发字节数、连接时长及起止时间，我们将这样一组元数据称为“网络流”（network flows）。

### 常用工具

流量分析中最常使用的工具是 `wireshark` 当然也有其他的工具例如 `BruteShark`. 

wireshark下载地址

```
链接: https://pan.baidu.com/s/1WSzZkBhJECTY_ehwSs5U8Q?pwd=w1wa 
提取码: w1wa 复制这段内容后打开百度网盘手机App，操作更方便哦
```

## Wireshark 基本使用方法

### 窗口组成

![](./images/pcap/Snipaste_2023-10-05_14-03-02.png)

上图是Wireshark的基本窗口组成，接下来将会详细介绍每一个面板的功能以及基本使用

显示过滤窗口是最常用的功能之一，它可以迅速帮助我们筛选出我们所需要的包。例如，当我们需要分析TLS的时候，可以直接输入`tls`. 不过需要注意的是，筛选语法对大小写敏感 `TLS !== tls`


### 显示过滤器


Wireshark的显示过滤器允许您集中关注感兴趣的数据包，同时隐藏其他的包，本章你将学习到基本的显示过滤器语法

### 基本构成

过滤器表达式由一个或多个原语(Primitive)组成

形式化表达式为: `[not] primitive [and|or [not] primitive ...]`

> [A] 表示A是可选的
> 
> \<x\> 表示x为必选
>
> and(&&), or(||), not(!) 表示与或非
>

### 原语(Primitive)语法

`protocol[.attr1.attr2.attr3 ... .stringN] [Comparison operator] [Value]`

#### protocol

protocol表示需要显示的协议，目前wireshark支持的协议多达 2894 种，具体可以点击 `视图 -> 内部 -> Supported Protocols` 查看

常用的大概如下几种

```
tcp, udp, http, http2, http3, tls, dns ...
```

#### attr

attr一般用来表示protocol的属性，例如 `ip.addr == x.x.x.x` 表示，匹配ip地址为x.x.x.x的包

#### Comparison operator (比较值)

你可以使用语义化的英文缩写或逻辑符号来进一步的筛选你所需要的包，例如 `ip.addr eq 11.4.51.4` 表示，筛选所有ip包含 11.4.51.4 的包 该表达式与 `ip.addr == 11.4.51.4` 是等价的

常见的比较值如下表所示

|   English   | C-like |                   example                    |
| :---------: | :----: | :------------------------------------------: |
|     eq      |   ==   |              ip.addr == 1.2.3.4              |
|     ne      |   !=   |              ip.addr != 1.2.3.4              |
|     gt      |   >    |                frame.len > 10                |
|     lt      |   <    |                frame.len < 10                |
|     ge      |   >=   |               frame.len >= 10                |
|     le      |   <=   |               frame.len <= 10                |
|  contains   |   \    |          udp.payload contains "ftp"          |
|   matches   |   ~    | http.host matches "ace\.(org \| com \| net)" |
| bitwise_and |   &    |               tcp.flags & 0x02               |

#### Value

##### 整数

可以是8、16、24、32或64位整数，可以使用十进制、八进制、十六进制或二进制来表示

```
frame.len > 1500
frame.len > 02734
frame.len > 0xff
frame.len > 0b1100
```

上述均为有效表达

##### 布尔

可以直接使用True(TRUE)或False(FALSE)，也可以使用1来表达True，0表达False

例如，当tcp.flags.syn为True时，仅会输出SYN包.

##### Ethernet address

由冒号(:)、句号(.)、短划线(-)分割的六个字节

```
eth.dst == ff:ff:ff:ff:ff:ff
eth.dst == ff-ff-ff-ff-ff-ff
eth.dst == ffff.ffff.ffff
```

##### IPv4地址

可以直接 `ip.addr == 192.168.0.1` 表达，如果你需要选一类地址，可以使用CIDR表达法

```
ip.addr == 192.168.0.0/16
```

##### IPv6

与IPv4除了地址表达有差异外，其他无不同

##### 字符串类型

`http.request.uri == "https://www.bilibili.com/"` 

字符串文字用双引号指定，也可以使用十六进制`\xff`或八进制`\ddd`来转移，其中`f`与`d`为十六进制和八进制数字

##### 日期与时间

在wireshark中GMT、UTC、ISO8601表达法都是被允许的。同时，也可以对事件进行范围比较

`frame.time < "2020-01-01"` 该表达式是符合语法的

#### Combining Expressions (组合表达式)

有些时候我们需要组合其他Primitive(原语)来满足更复杂的筛选需求，例如我们需要筛选TCP包且发送方为172.17.0.2但我们不需要ack包。

很明显，一个Primitive(原语)无法满足我们的需求，这个时候我们需要将多个Primitive(原语)使用组合表达式来组合多个Primitive(原语)或称Express(表达式)

常见的组合表达式如下

| English | C-Like | Description |
| :-----: | :----: | :---------: |
|   and   |   &&   |   逻辑与    |
|   or    |  \|\|  |   逻辑或    |
|   xor   |   ^    |    异或     |
|   not   |   !    |   逻辑非    |
|   in    |   \    |  集合成员   |
|  [...]  |   \    |    切片     |

现在让我们尝试一下实现刚刚的要求，也就是`筛选TCP包且发送方为172.17.0.2但我们不需要ack包`，我们可以如下实现

```
tcp and ip.src == 172.17.0.2 and tcp.flags.ack == 0
```

这样，我们就可以成功的筛选出非ack包了

![](./images/pcap/Snipaste_2023-10-05_14-04-16.png)


## 实战

实战是验证是否掌握的最佳方案，本章使用\(DDCTF 流量分析\)题目作为实战

题目下载

```
 https://pan.baidu.com/s/1ZMFiORIPJGwGy_jdY-Z0Eg?pwd=g18w
```

### DDCTF 流量分析

下载好习题后，解压，发现有一个txt和pcap文件。打开txt，内容如下。

```
流量分析
200pt

提示一：若感觉在中间某个容易出错的步骤，若有需要检验是否正确时，可以比较MD5: 90c490781f9c320cd1ba671fcb112d1c
提示二：注意补齐私钥格式
-----BEGIN RSA PRIVATE KEY-----
-----END RSA PRIVATE KEY-----

```

从第一点得知，我们可能会解密出一个文件

从第二点得知，我们会需要一个密钥。

问题来了，密钥可能在哪？会不会解密出来的文件就是密钥，或者说是一个其他的文件但内部隐藏着密钥？

带着这两个问题，我们打开pcap文件

![](./images/pcap/Snipaste_2023-10-05_14-04-48.png)

可以看到右下角一共10183个分组，慢慢看恐怕是要看到天荒地老了。我们不妨筛选一下，但问题在于我们如何筛选？

不妨先统计一下，都有哪些协议?占比有多少?从而进一步的分析。点击`统计 -> 协议分级`

![Alt text](./images/pcap/Snipaste_2023-10-05_14-05-49.png)

从上到下我们简单分析一下，从上图我们可以看到基本上所有的帧都是由IPv4发送的，那么IPv6就可以不用看了。紧接着，我们发现，存在两个协议，UDP与TCP。TCP比UDP有更多的分组，而且我们可以注意到，有一个TLS和FTP协议。

还记得刚刚的文档提示吗

> 若感觉在中间某个容易出错的步骤，若有需要检验是否正确时，可以比较MD5: 90c490781f9c320cd1ba671fcb112d1c

那么，有没有一种可能，使用了ftp传输了文件呢？我们不妨分析一下，右键`FTP Data -> 作为过滤器应用 -> 选中`

![](./images/pcap/Snipaste_2023-10-05_14-07-13.png)

紧接着，关闭 `协议分级` 窗口，点击 `文件 -> 导出对象 -> FTP-DATA`

![Alt text](./images/pcap/Snipaste_2023-10-05_14-07-38.png)

选择`FL-G.zip`点击`save`

![Alt text](./images/pcap/Snipaste_2023-10-05_14-08-38.png)

计算MD5后我们发现是错误的

![Alt text](./images/pcap/Snipaste_2023-10-05_14-10-46.png)

解压发现需要密码，MD5也是错误的。回到统计图

![Alt text](./images/pcap/Snipaste_2023-10-05_14-05-49.png)

我们还发现`SMTP`协议，我们不妨也分析一下。在显示筛选器中输入`smtp`，报文非常的少一共179个报文。

点击 `统计 -> 会话` 

![Alt text](./images/pcap/Snipaste_2023-10-05_14-13-46.png)

其中有几个比较大的会话引起了我的注意。我们不妨跟踪一下，看看到底都发送了什么.

`选中第一个会话 -> 右键`

![Alt text](./images/pcap/Snipaste_2023-10-05_14-17-49.png)

`选中第一个分组 -> 跟踪流 -> TCP流 -> 左下角下拉列表选择第二个(最大的那个)`

![Alt text](./images/pcap/Snipaste_2023-10-05_14-18-43.png)

第一个会话是发送了一张base64编码的图片，后面的会话都是一些html文档。我们先将base64编码转为图片，得到了这样的一幅图片

![Alt text](./images/pcap/b64.png)

图片上的文字为RSA密钥，OCR识别后对齐密钥格式得到如下

```
-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQDCm6vZmclJrVH1AAyGuCuSSZ8O+mIQiOUQCvN0HYbj8153JfSQ
LsJIhbRYS7+zZ1oXvPemWQDv/u/tzegt58q4ciNmcVnq1uKiygc6QOtvT7oiSTyO
vMX/q5iE2iClYUIHZEKX3BjjNDxrYvLQzPyGD1EY2DZIO6T45FNKYC2VDwIDAQAB
AoGAbtWUKUkx37lLfRq7B5sqjZVKdpBZe4tL0jg6cX5Djd3Uhk1inR9UXVNw4/y4
QGfzYqOn8+Cq7QSoBysHOeXSiPztW2cL09ktPgSlfTQyN6ELNGuiUOYnaTWYZpp/
QbRcZ/eHBulVQLlk5M6RVs9BLI9X08RAl7EcwumiRfWas6kCQQDvqC0dxl2wIjwN
czILcoWLig2c2u71Nev9DrWjWHU8eHDuzCJWvOUAHIrkexddWEK2VHd+F13GBCOQ
ZCM4prBjAkEAz+ENahsEjBE4+7H1HdIaw0+goe/45d6A2ewO/lYH6dDZTAzTW9z9
kzV8uz+Mmo5163/JtvwYQcKF39DJGGtqZQJBAKa18XR16fQ9TFL64EQwTQ+tYBzN
+04eTWQCmH3haeQ/0Cd9XyHBUveJ42Be8/jeDcIx7dGLxZKajHbEAfBFnAsCQGq1
AnbJ4Z6opJCGu+UP2c8SC8m0bhZJDelPRC8IKE28eB6SotgP61ZqaVmQ+HLJ1/wH
/5pfc3AmEyRdfyx6zwUCQCAH4SLJv/kprRz1a1gx8FR5tj4NeHEFFNEgq1gmiwmH
2STT5qZWzQFz8NRe+/otNOHBR2Xk4e8IS+ehIJ3TvyE=
-----END RSA PRIVATE KEY-----
```

接着回到协议分级中，我们发现有一些TLS会话，不难想到这是否会和TLS有关？

![Alt text](./images/pcap/Snipaste_2023-10-05_14-05-49.png)

保存到一个txt/pem文件中, 点击`编辑 -> 首选项 -> Protocols -> TLS -> RSA key file list -> + `

![Alt text](./images/pcap/Snipaste_2023-10-05_14-26-22.png)

其余选项可以留空，点击Browse, 选择密钥文件后点击OK.

![Alt text](./images/pcap/Snipaste_2023-10-05_14-36-18.png)

再次打开协议分级，我们发现TLS下多出了 `Hypertext Transfer Protocol(http)` 协议。

接下来我们，` 右键 Hypertext Transfer Protocol(http) -> 作为过滤器应用 -> 选中`

![Alt text](./images/pcap/Snipaste_2023-10-05_14-37-18.png)

单击`HTTP流`

![Alt text](./images/pcap/Snipaste_2023-10-05_14-37-57.png)

即可得到flag

<!-- Imported from D:\\Book\\Misc\\Chapter5\5-1.md -->
### TLS 流量分析

TLS（Transport Layer Security）是一种安全协议，用于在计算机网络上实现加密通信

TLS 使用密钥交换算法来安全地生成一个共享的会话密钥，这个会话密钥将用于本次通信会话的加密和解密

常见的密钥交换算法包括 RSA、DH、ECDH 等


![](https://pic1.imgdb.cn/item/677fdd29d0e0a243d4f2d041.jpg)

下载文件给出了流量包以及加密的 key 文件

打开 Key 文件确认为 RSA 密钥

![](https://pic1.imgdb.cn/item/677fdd63d0e0a243d4f2d048.jpg)

使用 Wireshark 打开流量包导入 RSA 密钥

编辑➡首选项➡RSA 密钥➡Add new keyfile➡确定

![](https://pic1.imgdb.cn/item/677fdd77d0e0a243d4f2d04a.jpg)

退出再重新打开就有了解密后的数据包，成功拿到 flag

![](https://pic1.imgdb.cn/item/677fddabd0e0a243d4f2d053.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-10.md -->
### 键盘流量分析


![](https://pic1.imgdb.cn/item/6780b36ad0e0a243d4f2f1b2.jpg)

打开流量包找到数据位于 HID DATA 中

![](https://pic1.imgdb.cn/item/6780b37bd0e0a243d4f2f1b8.jpg)

编写脚本提取数据

```shell
tshark -r 1.pcapng -T fields -e usbhid.data > usbdata.txt
```

![](https://pic1.imgdb.cn/item/6780b3a5d0e0a243d4f2f1c4.jpg)

最后将提取出的数据用脚本转为敲击的字母即可

![](https://pic1.imgdb.cn/item/6780b3b0d0e0a243d4f2f1c8.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-11.md -->
### 冰蝎流量分析


![](https://pic1.imgdb.cn/item/6780ba2ed0e0a243d4f2f45d.jpg)

打开数据包，只有 HTTP，过滤一手

![](https://pic1.imgdb.cn/item/6780ba54d0e0a243d4f2f466.jpg)

追踪上传的木马，发现内容被加密了

![](https://pic1.imgdb.cn/item/6780ba6ad0e0a243d4f2f471.jpg)

但是通过 Accept 分析出这是冰蝎（q=0.01）

![](https://pic1.imgdb.cn/item/6780ba80d0e0a243d4f2f476.jpg)

冰蝎使用 AES 加密，密码默认是 e45e329feb5d925b，追踪一个响应流解密看看内容

![](https://pic1.imgdb.cn/item/6780ba9fd0e0a243d4f2f480.jpg)

解密

![](https://pic1.imgdb.cn/item/6780bac3d0e0a243d4f2f487.jpg)

再解密

![](https://pic1.imgdb.cn/item/6780bb03d0e0a243d4f2f499.jpg)

去查看请求包的内容

![](https://pic1.imgdb.cn/item/6780bb15d0e0a243d4f2f4aa.jpg)

发现在请求 secret2.txt，其内容为：Hello, but what you're looking for isn't me.

继续查找，找到关键内容

![](https://pic1.imgdb.cn/item/6780bbc7d0e0a243d4f2f4e8.jpg)

解密得到压缩包

![](https://pic1.imgdb.cn/item/6780bbedd0e0a243d4f2f4f8.jpg)

保存出来，使用 ZIP 明文攻击即可拿到 flag

![](https://pic1.imgdb.cn/item/6780bc01d0e0a243d4f2f4fe.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-12.md -->
### TCP 流量分析


![](https://pic1.imgdb.cn/item/6780caf1d0e0a243d4f2fcf6.jpg)

打开流量包只有 TCP

![](https://pic1.imgdb.cn/item/6780cb05d0e0a243d4f2fd0d.jpg)

追踪数据流是一张图片，导出即可拿到 flag

![](https://pic1.imgdb.cn/item/6780cb1ad0e0a243d4f2fd24.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-13.md -->
### RTP 流量分析


![](https://pic1.imgdb.cn/item/6780e72ad0e0a243d4f30b2b.jpg)

一堆 RTP 流，直接导出

![](https://pic1.imgdb.cn/item/6780e774d0e0a243d4f30b4d.jpg)

之后右键点分析 ➡ 播放流念出 flag

![](https://pic1.imgdb.cn/item/6780e77ed0e0a243d4f30b52.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-14.md -->
### IP 流量分析


![](https://pic1.imgdb.cn/item/67cc205f066befcec6e158e2.jpg)

最后发现隐写在 IP 中的 Identification 字段

![](https://pic1.imgdb.cn/item/67cc2076066befcec6e158e4.jpg)

使用 tshark 提取数据然后转 ASCII 最后在 Base91 解码

```shell
tshark -r attachment.pacp -T fields -e ip.id > data,txt
```

![](https://pic1.imgdb.cn/item/67cc208f066befcec6e158e7.jpg)




<!-- Imported from D:\\Book\\Misc\\Chapter5\5-15.md -->
### HTTPS 流量分析


![](https://pic1.imgdb.cn/item/67cc213f066befcec6e158fa.jpg)

给了个流量包和 log 文件

![](https://pic1.imgdb.cn/item/67cc2150066befcec6e15903.jpg)

打开流量包发现都是 HTTPS

在配置项中使用 log 文件解密 TLS

![](https://pic1.imgdb.cn/item/67cc216f066befcec6e15906.jpg)

这个时候再过滤 HTTP 就能看到数据了

![](https://pic1.imgdb.cn/item/67cc2185066befcec6e15909.jpg)

过滤状态码为 200 的浏览

![](https://pic1.imgdb.cn/item/67cc219a066befcec6e15911.jpg)

发现参数中存在隐写，这里是倒过来的题目

数据较少可以手动提取然后通过脚本逆向拿到 flag

![](https://pic1.imgdb.cn/item/67cc21af066befcec6e15912.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-16.md -->
### 端口扫描分析


![](https://pic1.imgdb.cn/item/67cc225d066befcec6e15931.jpg)

端口扫描要么 TCP 要么 UDP 或者 ICMP

题目提示 Nmap 经常使用的是 TCP，基于 TCP 三次握手扫描端口

首先肯定是过滤 FIN = 1，因为这是第一次握手请求包

如果端口开放则回应一个 FIN,ACK = 1，由此可以过滤

![](https://pic1.imgdb.cn/item/67cc2265066befcec6e15932.jpg)

点击上面统计➡会话拿到所有开放端口

![](https://pic1.imgdb.cn/item/67cc22b6066befcec6e15943.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-17.md -->
### EV3 分析


![](https://pic1.imgdb.cn/item/67cc232d066befcec6e15951.jpg)

打开图片提示 EV3 以及 flag 头

![](https://pic1.imgdb.cn/item/67cc2340066befcec6e1595e.jpg)

网上搜索 EV3 插件下载导入 WireShark 中

![](https://pic1.imgdb.cn/item/67cc2353066befcec6e15961.jpg)

过滤 EV3 协议

![](https://pic1.imgdb.cn/item/67cc2382066befcec6e1596b.jpg)

可以发现一些特定字节有“{”，“}” 等 58 个字符疑似 flag

它们的前面都会出现 '（'，'R'，'6'，'D' 

![](https://pic1.imgdb.cn/item/67cc23a0066befcec6e15972.jpg)

同时还会发现每个数据包的编号分别为 10、20、30 等

![](https://pic1.imgdb.cn/item/67cc23be066befcec6e1597b.jpg)

那么 '（'，'R'，'6'，'D' 代表的就是四组，Value 就是字符排序顺序，四组组合起来就是 flag

![](https://pic1.imgdb.cn/item/67cc23ed066befcec6e1598c.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-18.md -->
### Web 目录爆破分析


![](https://pic1.imgdb.cn/item/67cc2462066befcec6e159bb.jpg)

打开流量包过滤 http 请求发现大多数都是请求的 Web 文件，推测是对后台进行扫描

![](https://pic1.imgdb.cn/item/67cc247a066befcec6e159d0.jpg)

上方 ”统计” → “HTTP” → “请求”

![](https://pic1.imgdb.cn/item/67cc248e066befcec6e159d6.jpg)

过滤状态码为 200 的数据包发现 Base64 编码，解码拿到 flag

![](https://pic1.imgdb.cn/item/67cc24ab066befcec6e159db.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-19.md -->
### 哥斯拉流量分析


![](https://pic1.imgdb.cn/item/67cc2510066befcec6e159ed.jpg)

题目提示了哥斯拉，看看对哪个文件请求最多

![](https://pic1.imgdb.cn/item/67cc2536066befcec6e159f9.jpg)

使用命令筛选出这个文件的相关数据包

```shell
http.request.uri contains "aaa.php"
```

![](https://pic1.imgdb.cn/item/67cc2563066befcec6e159ff.jpg)

追踪流发现了 eval

![](https://pic1.imgdb.cn/item/67cc2576066befcec6e15a02.jpg)

再往下看发现哥斯拉显著特征

Cookie 后面带有分号 ;

响应包结构体特征是

md5 前十六位 + base64 + md5 后十六位

![](https://pic1.imgdb.cn/item/67cc25a1066befcec6e15a08.jpg)

找到 WebShell 连接密码

![](https://pic1.imgdb.cn/item/67cc25be066befcec6e15a12.jpg)

加密取前 16 位解密用，同时也是 flag 前半段

![](https://pic1.imgdb.cn/item/67cc25da066befcec6e15a19.jpg)

只取中间的来进行 base64 解码

解码后与连接的 Key 的 md5 值前 16 位进行按位异或






<!-- Imported from D:\\Book\\Misc\\Chapter5\5-2.md -->
### WPA 密钥爆破分析

我们知道 Wifi 是基于 WPA 的，最常见的 WPA 配置是 WPA-PSK（预共享密钥）

WPA-PSK 基本上意味着 Wi-Fi 网络有一个密码，由每个 Wi-Fi 网络客户端共享


![](https://pic1.imgdb.cn/item/677fdf5ad0e0a243d4f2d098.jpg)

发现都是基于 WLAN 的 802.11 协议数据包

![](https://pic1.imgdb.cn/item/677fdf87d0e0a243d4f2d09d.jpg)

首先分析 WIFI 的连接过程

第一步是扫描和关联，你会看到 Beacon帧，其中包含了 SSID、MAC 地址、支持的速率等信息

接着是 Probe Request 和 Probe Response帧

STA 用 Probe Request 来发现 AP

AP 用 Probe Response 来响应

![](https://pic1.imgdb.cn/item/677fdfbcd0e0a243d4f2d0a7.jpg)

接下来就是认证的 Authentication 请求和响应帧

它们包含认证算法和序列编号

![](https://pic1.imgdb.cn/item/677fe014d0e0a243d4f2d0b4.jpg)

最后就是重点内容：四次握手

因为它是使用 Eapol Key 进行封装传输的，所以需要过滤 Eapol 协议

![](https://pic1.imgdb.cn/item/677fe0a8d0e0a243d4f2d0d3.jpg)

握手包是完整的，破解的话需要密码，根据题目提示可以生成字典爆破，使用工具 Crunch

```shell
crunch 11 11 -t 1391040%%%% -o passwd.txt
```

![](https://pic1.imgdb.cn/item/677fe292d0e0a243d4f2d11f.jpg)

有字典后可以使用强大的 Aircrack-ng 爆破

![](https://pic1.imgdb.cn/item/677fe307d0e0a243d4f2d12e.jpg)

成功拿到密码

![](https://pic1.imgdb.cn/item/677fe100d0e0a243d4f2d0e2.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-20.md -->
### 蚁剑流量分析


![](https://pic1.imgdb.cn/item/67cc27f9066befcec6e15a5e.jpg)

一看 WebShell 直接过滤 POST

![](https://pic1.imgdb.cn/item/67cc2801066befcec6e15a5f.jpg)

追踪流看到一个压缩文件，显示为 Hex 后复制在 010 中新建写入

![](https://pic1.imgdb.cn/item/67cc281c066befcec6e15a61.jpg)

技巧：在之前过滤的 POST 中追踪流，重点看看有没有使用 WebShell 密码

![](https://pic1.imgdb.cn/item/67cc2869066befcec6e15a68.jpg)

解压缩后拿到木马文件，密码就是 n3wst4r

![](https://pic1.imgdb.cn/item/67cc2839066befcec6e15a65.jpg)

将密码前的参数解码，注意要删掉开头两个字符，这是蚁剑流量的特点

看到 env 显示系统的环境变量

![](https://pic1.imgdb.cn/item/67cc28aa066befcec6e15a6a.jpg)

将其对应的响应包内容解码拿到 JAVA 版本

![](https://pic1.imgdb.cn/item/67cc28c4066befcec6e15a6d.jpg)

继续追踪流看到查看了一个文件

![](https://pic1.imgdb.cn/item/67cc28e2066befcec6e15a71.jpg)

还是一样解码响应包，注意要删掉开头的几个混淆字符才行

解码的第一行就是文件内容

![](https://pic1.imgdb.cn/item/67cc28eb066befcec6e15a74.jpg)

这里我又试了一下，开头字符数量不是固定的，需要自己手动删除测试

![](https://pic1.imgdb.cn/item/67cc291d066befcec6e15a78.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-21.md -->
### SQL 布尔盲注分析


![](https://pic1.imgdb.cn/item/67837d69d0e0a243d4f39dab.png)

打开流量包发现一片绿

![](https://pic1.imgdb.cn/item/678384f8d0e0a243d4f39ff4.png)

直接过滤 HTTP 发现是 SQL 布尔盲注

![](https://pic1.imgdb.cn/item/678385ffd0e0a243d4f3a056.png)

在导出 HTTP 对象中按大小排列拿到注入成功的语句

![](https://pic1.imgdb.cn/item/67838646d0e0a243d4f3a076.png)

将十进制转 ASCII 码即可

![](https://pic1.imgdb.cn/item/678386e4d0e0a243d4f3a0c4.png)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-22.md -->
### 哥斯拉流量分析


![](https://pic1.imgdb.cn/item/678f8712d0e0a243d4f629bf.png)

题目名：**gza_Cracker**

给的是个流量包，打开只有 HTTP 和 TCP

![](https://pic1.imgdb.cn/item/678f8769d0e0a243d4f629cc.png)

直接过滤 HTTP 再排列找到木马文件 ini.php

![](https://pic1.imgdb.cn/item/678f87aad0e0a243d4f629da.png)

题目有描述说明了是哥斯拉，打开蓝队研判工具

选择解密 WebShell 流量再选择哥斯拉 3.x~4.x（为什么不选 1.x~2.x ……因为这个版本只有 Java 的）

选择 PHP 的

![](https://pic1.imgdb.cn/item/678f88f2d0e0a243d4f62a0d.png)

我们需要找到密码参数以及密钥参数才能解密流量包

![](https://pic1.imgdb.cn/item/678f8f67d0e0a243d4f62b3c.png)

去追踪流先拿到密码参数

![](https://pic1.imgdb.cn/item/678f9020d0e0a243d4f62b5c.png)

找到密码可参考[博客链接](https://forum.butian.net/share/2517)

![](https://pic1.imgdb.cn/item/678f9040d0e0a243d4f62b60.png)

Key 的参数没有直接给出，总共也就十五个流

全部翻完发现在第 11 个有组数据

![](https://pic1.imgdb.cn/item/678f90bdd0e0a243d4f62b73.png)

编写脚本比对爆破（原理参考脚本注释）

响应包开头数据总是固定的

![](https://pic1.imgdb.cn/item/678f913bd0e0a243d4f62b8b.png)

```python
import hashlib


def main():
    # 示例变量
    keylist = ["123456",
               "password",
               "12345678",
               "1234",
               "admin@123",
               "pussy",
               "12345",
               "dragon",
               "qwerty",
               "696969",
               "mustang",
               "letmein",
               "baseball",
               "master",
               "michael",
               "football",
               "shadow",
               "monkey",
               "abc123",
               "pass",
               "fuckme",
               "6969",
               "jordan",
               "harley",
               "ranger",
               "iwantu",
               "jennifer",
               "hunter",
               "fuck",
               "2000",
               "test",
               "batman",
               "trustno1",
               "thomas",
               "tigger",
               "robert",
               "access",
               "love",
               "buster",
               "1234567",
               "soccer",
               "hockey",
               "killer",
               "george",
               "sexy",
               "andrew",
               "charlie",
               "superman",
               "asshole",
               "fuckyou",
               "dallas",
               "jessica",
               "panties",
               "pepper",
               "1111",
               "austin",
               "william",
               "daniel",
               "golfer",
               "summer",
               "heather",
               "hammer",
               "yankees",
               "joshua",
               "Antsw0rd",
               "maggie",
               "biteme",
               "enter",
               "ashley",
               "thunder",
               "cowboy",
               "silver",
               "richard",
               "fucker",
               "orange",
               "merlin",
               "michelle",
               "corvette",
               "bigdog",
               "cheese",
               "matthew",
               "121212",
               "patrick",
               "martin",
               "freedom",
               "ginger",
               "blowjob",
               "nicole",
               "sparky",
               "yellow",
               "camaro",
               "secret",
               "dick",
               "falcon",
               "taylor",
               "111111",
               "131313",
               "123123",
               "bitch",
               "hello"]
    
    passphrase = "Antsword"

    # 遍历 keylist
    for key in keylist:
        # 计算 key 的 MD5 哈希值
        md5_key = hashlib.md5(key.encode()).hexdigest()

        # 截取 MD5 的前 16 位
        md5_key_16bit = md5_key[:16]

        # 将 passphrase 和 md5_key_16bit 拼接后计算新的 MD5
        combined = passphrase + md5_key_16bit

        final_md5 = hashlib.md5(combined.encode()).hexdigest()[:16]

        # 比较结果是否等于目标值
        if final_md5 == "e71f50e9773b23f9":
            print(f"Key is: {key}")
            print(f"16 bit: {md5_key_16bit}")


if __name__ == '__main__':
    main()
```

拿到参数后在工具箱中解密响应包拿到一串编码字符

![](https://pic1.imgdb.cn/item/678f91b0d0e0a243d4f62b9e.png)

工具梭哈拿到 flag

![](https://pic1.imgdb.cn/item/678f9201d0e0a243d4f62bb3.png)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-23.md -->
### SMB3 流量分析


![](https://pic1.imgdb.cn/item/67b8bd71d0e0a243d40184bb.png)

下载文件打开流量包发现加密的 SMB3 流量

SMB3（Server Message Block 3.0）是SMB协议的一个版本，广泛用于文件共享、网络打印和其他网络服务

SMB3 在 Windows 8 和 Windows Server 2012 中首次引入，并引入了许多新特性，包括加密、持久句柄、多通道支持等

![](https://pic1.imgdb.cn/item/67b8bf81d0e0a243d40185f4.png)

要解密SMB3流量，你需要以下信息之一：

- **会话密钥**：SMB3 加密使用的会话密钥
- **Kerberos票据**：如果 SMB3 使用 Kerberos 认证，可以通过 Kerberos 票据获取密钥
- **NTLM哈希**：如果 SMB3 使用 NTLM 认证，可以通过 NTLM 哈希获取密钥

首先提取哈希值，[脚本链接](https://github.com/mlgualtieri/NTLMRawUnHide)

![](https://pic1.imgdb.cn/item/67b95ac9d0e0a243d401c9e0.png)

只有一个用户的哈希值

![](https://pic1.imgdb.cn/item/67b95adfd0e0a243d401c9e3.png)

hashcat 爆破一下得到密码 36521478

```shell
hashcat -a 0 6.txt rockyou.txt
```

![](https://pic1.imgdb.cn/item/67b97588d0e0a243d401d69b.png)

在 WireShark 中输入密码解密

![](https://pic1.imgdb.cn/item/67b975e8d0e0a243d401d6c7.png)

解密成功可以看到有个 secret.doc 文件

![](https://pic1.imgdb.cn/item/67b9760dd0e0a243d401d6e4.png)

导出

![](https://pic1.imgdb.cn/item/67b9765ed0e0a243d401d734.png)

打开发现数据乱码，扔进 WinHex 中发现数据逆序了

逆序后参考取证 2.8 节

![](https://pic1.imgdb.cn/item/67b9776ed0e0a243d401d7db.png)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-24.md -->
### Ceph 流量分析


![](https://pic1.imgdb.cn/item/67e8f0750ba3d5a1d7e6b1ab.png)

打开流量包发现 Ceph 流量

![](https://pic1.imgdb.cn/item/67e8f0eb0ba3d5a1d7e6b1b9.png)

Ceph 指的是一个统一的分布式存储系统，需要工具 tcpxtract 来提取

![](https://pic1.imgdb.cn/item/67e8f4b80ba3d5a1d7e6b277.png)

查看图片拿到 flag

![](https://pic1.imgdb.cn/item/67e8f4ca0ba3d5a1d7e6b27a.png)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-25.md -->
### UDP 端口流量分析


![](https://pic1.imgdb.cn/item/67e8fb310ba3d5a1d7e6b3ee.png)

打开流量包发现 UDP 流量 Info 信息一直在 3400 和 3401 徘徊

![](https://pic1.imgdb.cn/item/67e8fb7e0ba3d5a1d7e6b415.png)

使用脚本提取

```shell
# 使用 cut 裁取端口的最后一位
tshark -r 8868f595665740159650d6e654aadc93.pcap -Tfields -e udp.srcport | cut -c 4
```

![](https://pic1.imgdb.cn/item/67e8fc280ba3d5a1d7e6b445.png)

最后编写脚本转 ASCII 码

```python
s = "10110111100110101001011010001100100110101001000110011101100110101000110110011000"
flag = ''

for i in range(len(s)):
    if s[i] == '0':
        flag += '1'
    else:
        flag += '0'

# 原始字符串翻译
print(''.join(chr(int(s[i : i + 8], 2)) for i in range(0, len(s), 8)))
# 取反码字符串翻译
print(''.join(chr(int(flag[i : i + 8], 2)) for i in range(0, len(flag), 8)))
```




<!-- Imported from D:\\Book\\Misc\\Chapter5\5-26.md -->
### 侧信道流量分析


![](https://pic1.imgdb.cn/item/67ea1c840ba3d5a1d7e782b4.png)

按照题目给出的要求转为二进制即可

![](https://pic1.imgdb.cn/item/67ea1cc60ba3d5a1d7e783d8.png)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-27.md -->
### ICMP Length 流量分析


![](https://pic1.imgdb.cn/item/67ea6f8a0ba3d5a1d7e82525.png)

看 ICMP 协议中 Length 不对劲

![](https://pic1.imgdb.cn/item/67ea71ec0ba3d5a1d7e82936.png)

提出来转 ASCII 码

```python
a = [100, 106, 95, 101, 121, 47, 65, 107, 78, 69, 62, 75, 49, 123]
flag = ""
for i in a:
    flag += chr(i + 2)
print(flag)
# flag{1CmPG@M3}
```




<!-- Imported from D:\\Book\\Misc\\Chapter5\5-28.md -->
### RDP 流量分析


![](https://pic1.imgdb.cn/item/67ea85470ba3d5a1d7e83712.png)

打开流量包发现 RDP 流量

![](https://pic1.imgdb.cn/item/67ea85620ba3d5a1d7e83714.png)

另外，我们注意到 RDP 流量是通过 SSL 加密的，具体如下：

![](https://pic1.imgdb.cn/item/67ea85dd0ba3d5a1d7e83736.png)

由此，我们可以猜测我们需要重放 RDP 会话，但要做到这一点，我们需要找到一个密钥来解密通信，这可能在 UDP 流中

跟踪 UDP 流后，我们看到大量二进制数据，其中包含一些有趣的字符串

“TSSecKeySet1” 和 “Microsoft Strong Cryptographic Provider” 看起来与我们想要找到的加密内容非常相似

![](https://pic1.imgdb.cn/item/67ea86be0ba3d5a1d7e8377c.png)

我们可以将整个流转储到一个文件中并尝试对其进行分析

首先，让我们看看它是否可以识别为文件

```shell
$ file extracted_data.bin
extracted_data.bin: data
```

它似乎没有可识别的标头

因此，让我们尝试在其上运行 Binwalk：

```shell
$ binwalk -e extracted_data.bin

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
30            0x1E            Certificate in DER format (x509 v3), header length: 4, sequence length: 2376
57            0x39            Certificate in DER format (x509 v3), header length: 4, sequence length: 1466
1546          0x60A           Private key in DER format (PKCS header length: 4, sequence length: 860
```

现在它似乎包含一些证书和一个私钥

尝试将单个文件转换为我们可以用 openssl 读取的纯文本似乎行不通

我们可以将其读取为 ASN.1 来调试它

ASN.1 是一种描述结构化数据的标准，常用于证书、密钥等密码学数据的编码

```shell
# asn1parse 用于解析 ASN.1 (Abstract Syntax Notation One) 编码的数据
# -inform 指定输入文件的编码格式
# DER (Distinguished Encoding Rules) 是 ASN.1 的一种二进制编码格式，另一种常见格式是 PEM（Base64 编码的文本格式）
$ openssl asn1parse -inform DER -in extracted_data.bin
    # d=0：嵌套深度为 0（顶层），hl=4：头部长度 4 字节，l=2467：总长度 2467 字节，SEQUENCE：表示这是一个复合结构
    0:d=0  hl=4 l=2467 cons: SEQUENCE
    # 版本号 3：对应 PKCS#7 的 SignedData 版本 1.5
    4:d=1  hl=2 l=   1 prim: INTEGER           :03
    # 内容类型为 pkcs7-data（OID 1.2.840.113549.1.7.1），表示封装的是普通数据
    7:d=1  hl=4 l=2399 cons: SEQUENCE
   11:d=2  hl=2 l=   9 prim: OBJECT            :pkcs7-data
   22:d=2  hl=4 l=2384 cons: cont [ 0 ]
   # OCTET STRING：实际加密数据，长度为 2380 字节
   # HEX DUMP：以 30 82 09 48 开头的 DER 数据，可能是嵌套的 ASN.1 结构（如加密的证书或密钥）
   26:d=3  hl=4 l=2380 prim: OCTET STRING      [HEX DUMP]:30820948308205D106092A864886F70D010701A08205C2048205BE308205BA308205B6060B2A864886F70D010C0A0102A08204F6308204F2301C060A2A864886F70D010C0103300E040866AFD4385D4302C4020207D0048204D093F23B4782B6438E5CB094A8C35CF1352F486FA1F7E3708A3F1BFC865A5EEF3C931DC82BA36EEF23609FE4717D0A021EEF8A981021BDADD04AFA64131A546CE65191A88C001ADCA9A5A15EDB1178E0DADDDCEDDCC3AB13BAADAE35B2B87378CC9158C0145DB1EB300E129D265C92E2C726E4790DA9F34AD0B80AF7BFD152B7AF4DD97B9B3BC4057CA245E4B871B871023F96832DCA3A4BA3E8628C34ACB48C75497CB8949CA48D1EF939495F2A0BE4B7497E0C19659EBE083ABFD8268D97149418C969CE28112F31255383994AA95B50C7A15285477A6D01B955E80C9F961FD03226C8233CA6F4851318D0B22B5B0E4D536CDF729827F2A12289E789675DDE3BBDC339376447AF09CD807AF811D216D148126B42177D7F1634BFAB0BB959A485BE82F7CE08FA8468FE526D48B02CA70CAF5EA55B786E7659DAFEFFC8292E15C251BC48D27F15860BD32E2FB67FB70DDED2CB7D199ECF107FEB5F57CA6D7D83ACA47DD20D23E3F7F73AF93753F1D6E6C42060A2F0A19CA9905CFCA4705F8DA96287D57584E9D0C9FEE127A1F8E91E6AA112FDD0AA42714BBFBDF1DB07BED4D3BB70B2AE3D614F75E17B8932E3ADCB8077DBE6EB9A3B723DFE7000B0B8DAD199D8FF4B8501BE45671BCAA8F3F5A9EB9EE67805F91C0734BE00F7EFDEAD031308879A852612AE3910830086EF4BC3CD6F9C14C5FA50F563EAB57C89F6AA49BBDF923D5E8847017C2F134AC4777E4E52D1DDDC1CCDDF800CC07DE1E733C8D233508E88306A0C9A035B1B61FA386F10CB1841C05C3442CAC764B0A5276A1047BF6EFA0E621A2FAE1A8792D8C5E20F692A472D88F96B32EB3D18B066BBEC04DAC120ADD3A0AFDAA2D81DF0A2CAFD1C135A0EC7AAEF4474B2853C125487DE8A7623F25F0029F912F9F689DD0AD5F4275FC8DFB6ADD908B677D3975AFBC207B0B24D225EDF28F88C17C451D6F0A8521CA55B873F611C742C5C7525B04C6C3E2BA0BC59D43C02EE517BA8D08E102F9837A6B37C505D2BD97D23AB4F6912B5EB67747EB572969057B923D347980E7F3338F2E70AE1E13B2071D9DD84991937B676838F8C42BB6A36A06A78B895063CBF9E20FD445EC96CF886D58FCA47230593FE7DA25535BBDAD2BED116FCF0A47BFEE90F6C0C227A5B9DFA33BDAB645585EBD3CC402DE595FF1A016A1B73472580FB2CB271CCEDFF473916D72334E4D5F4674EBA649636B00D05C852FFDF930360DCEFF949BEA357AF1DE79DD503E9705BAE51488F3B5F4468F15FC17593B7C06E2E5D7A26D02112E28034ED3D5C2956159CD2440D8B03BBA8E227608FE9C12FF0C0A12600AE3A3938AF7DDAB4BED9243A891D4EE684F5A0EC60DA908C5167F0302BBFB8940817D4C7D2F242DB6A980F196A2FF973223D73866B4E226D3F6EEB8177536FB10DA9E7BD864B0020C636F3A3673761A17B6865992FB0755AE9EB8036AA41776294D0FF8EA6F12CC9ECB45D45B154F2BF03B0A70E2B42DA1A7F99AA3FD4819857118FD77666D476C3C9BD258377994FB49EB5E820B416CCC5449895DEF2EAE3637CC8D5828D9DA7F1727FAEB740A7148BE35A4A689C75D152DD4DD431EAEA135E3AC5384BF7A226971B5BE18E041D046843F9BE8552292DF886C97F010DE239C4DD431163A88AB440BF14BD8B69D409C48366F289E59282EDE9796CAD4A1975FF52A2332DAC6756CB25AA24273B90E22B2B133A5C3F0805160E510B192D6BC18370F43181AC300D06092B06010401823711023100301306092A864886F70D0109153106040401000000302706092A864886F70D010914311A1E1800540053005300650063004B006500790053006500740031305D06092B060104018237110131501E4E004D006900630072006F0073006F006600740020005300740072006F006E0067002000430072007900700074006F0067007200610070006800690063002000500072006F007600690064006500723082036F06092A864886F70D010706A08203603082035C0201003082035506092A864886F70D010701301C060A2A864886F70D010C0106300E0408135DB999CA2CD6B1020207D0808203287D8BDD108BE4C5084D46D3A88CED4C6412DF2FA7D5346D9FB289B1DC4AF4AD2B791EDA0612555A56EC21EECD6FDCCF6E83647E8DDED72942F24F551FFCFB55B7181AE5D9B6B790EA8B3B27820139681726348100035B7D349B3F77FB5265FA83B73008FC1A4687687F30A3BFF0D7289BFBC82423D753F380B53B607E7C8A101B53781D0F0273F7C1E4E42E71E2739659A569A465710B3E34C1C9165592F5DD145ECCCE570C3F3E84606D5A14878DA6172F6DB403C3FC7AF92512B8406693D4405BD27070F58A8778C3AA8D71BDDD24327F4FC2BFD932E431B99CDD461B21B57B5D8F88E90597FDD2BCB709AF6CAA264E58C116D018DE4DEA7870B7C3BCC64A8E2A1EE29EA8CCA17A7D29B2C033E2F50ACE0E01A87E7CF24CBCB8A9F7366C95F05ACFB233670952CA38B265CC3FC0F6D5575B7B02C50E9C0E54FDE359D0D216A80F3C817166DE479B94D81EE0FC1130392E5BBABCD6E11D807A7FEE2F958C3785A5857BBBFCD1B1EC8DA4D3ABFD6E3077CEB5B572C5549660B73CD3981819B2ECE1527316E5DC3DC8A0A9BFADD6A0C0065E9A8E7E1F1C2F09166629DEDC0AC57B9328C112CF77B4F3CF0118102B94BD80B01B845B03BF079B2C4F9E461958F36FFDB7886C025A3A37D4D8E9E1804C773122FF6409FE819C4A50C1267058E93F6698DBD5D2D4D7D2EB6B4443C8D1AD0E253C1D7DFE23E3918D1F6399EBD4CB4FC9EFE18D83DF575C06F5D21F824297E26999A4DA9FBCFB626CDDF0B2A9FDAB56CAF10785FAAD847D8589AFF8B0A39601CB1BF6B6256E4FB65BABAFFC5C4E5208121E4175071D18763F9152962AE964DB271313D77B488C9A1AC176ADCE6E3B3A1DC092CA5A304B3FE93C1F8F4A58D8E1992C3445180FFD1EC126690E12FF09FCED1306B4D5BEB150888E15B435AEB3316FFA019C7B89AFE0D6823C459252AF9B30E643FAC481ABE6C5E6B09C1F0B7AEEFC6FA2FC40E6BF6741273C4CFEF2529B645DFE5B7FF18AF6B9FD6443B9D206BA2F1264A073DD1DF80E554D64DBFC934657C63BF5441CE223C1AF271C73525177ABCA5D8777916BF6D22908F3C22989349E3346BE0A4712FCF0A215B4A1F06C700A88290DA38FF6BF7B9C58DC01F0E35702F49F70C6858E2D75
 # 签名信息（偏移量 2410）
 2410:d=1  hl=2 l=  59 cons: SEQUENCE
 2412:d=2  hl=2 l=  31 cons: SEQUENCE
 2414:d=3  hl=2 l=   7 cons: SEQUENCE
 2416:d=4  hl=2 l=   5 prim: OBJECT            :sha1
 2423:d=3  hl=2 l=  20 prim: OCTET STRING      [HEX DUMP]:C6636BA1DC7A4063D2AD49F7DBB800AD92260253
 2445:d=2  hl=2 l=  20 prim: OCTET STRING      [HEX DUMP]:9BADF56CE6069E1EB9339E0E9FCD096ACD0DBC5B
 2467:d=2  hl=2 l=   2 prim: INTEGER           :07D0
```

我们得到了一大堆数据，但是由于结构可以包含嵌套数据，我们可以通过指定要解码的八位字节字符串来深入挖掘

```shell
# -strparse 26 表示从文件偏移量 26 字节处 开始重新解析 ASN.1 结构
$ openssl asn1parse -inform DER -in extracted_data.bin -strparse 26
    0:d=0  hl=4 l=2376 cons: SEQUENCE
    4:d=1  hl=4 l=1489 cons: SEQUENCE
    8:d=2  hl=2 l=   9 prim: OBJECT            :pkcs7-data
   19:d=2  hl=4 l=1474 cons: cont [ 0 ]
   23:d=3  hl=4 l=1470 prim: OCTET STRING      [HEX DUMP]:308205BA308205B6060B2A864886F70D010C0A0102A08204F6308204F2301C060A2A864886F70D010C0103300E040866AFD4385D4302C4020207D0048204D093F23B4782B6438E5CB094A8C35CF1352F486FA1F7E3708A3F1BFC865A5EEF3C931DC82BA36EEF23609FE4717D0A021EEF8A981021BDADD04AFA64131A546CE65191A88C001ADCA9A5A15EDB1178E0DADDDCEDDCC3AB13BAADAE35B2B87378CC9158C0145DB1EB300E129D265C92E2C726E4790DA9F34AD0B80AF7BFD152B7AF4DD97B9B3BC4057CA245E4B871B871023F96832DCA3A4BA3E8628C34ACB48C75497CB8949CA48D1EF939495F2A0BE4B7497E0C19659EBE083ABFD8268D97149418C969CE28112F31255383994AA95B50C7A15285477A6D01B955E80C9F961FD03226C8233CA6F4851318D0B22B5B0E4D536CDF729827F2A12289E789675DDE3BBDC339376447AF09CD807AF811D216D148126B42177D7F1634BFAB0BB959A485BE82F7CE08FA8468FE526D48B02CA70CAF5EA55B786E7659DAFEFFC8292E15C251BC48D27F15860BD32E2FB67FB70DDED2CB7D199ECF107FEB5F57CA6D7D83ACA47DD20D23E3F7F73AF93753F1D6E6C42060A2F0A19CA9905CFCA4705F8DA96287D57584E9D0C9FEE127A1F8E91E6AA112FDD0AA42714BBFBDF1DB07BED4D3BB70B2AE3D614F75E17B8932E3ADCB8077DBE6EB9A3B723DFE7000B0B8DAD199D8FF4B8501BE45671BCAA8F3F5A9EB9EE67805F91C0734BE00F7EFDEAD031308879A852612AE3910830086EF4BC3CD6F9C14C5FA50F563EAB57C89F6AA49BBDF923D5E8847017C2F134AC4777E4E52D1DDDC1CCDDF800CC07DE1E733C8D233508E88306A0C9A035B1B61FA386F10CB1841C05C3442CAC764B0A5276A1047BF6EFA0E621A2FAE1A8792D8C5E20F692A472D88F96B32EB3D18B066BBEC04DAC120ADD3A0AFDAA2D81DF0A2CAFD1C135A0EC7AAEF4474B2853C125487DE8A7623F25F0029F912F9F689DD0AD5F4275FC8DFB6ADD908B677D3975AFBC207B0B24D225EDF28F88C17C451D6F0A8521CA55B873F611C742C5C7525B04C6C3E2BA0BC59D43C02EE517BA8D08E102F9837A6B37C505D2BD97D23AB4F6912B5EB67747EB572969057B923D347980E7F3338F2E70AE1E13B2071D9DD84991937B676838F8C42BB6A36A06A78B895063CBF9E20FD445EC96CF886D58FCA47230593FE7DA25535BBDAD2BED116FCF0A47BFEE90F6C0C227A5B9DFA33BDAB645585EBD3CC402DE595FF1A016A1B73472580FB2CB271CCEDFF473916D72334E4D5F4674EBA649636B00D05C852FFDF930360DCEFF949BEA357AF1DE79DD503E9705BAE51488F3B5F4468F15FC17593B7C06E2E5D7A26D02112E28034ED3D5C2956159CD2440D8B03BBA8E227608FE9C12FF0C0A12600AE3A3938AF7DDAB4BED9243A891D4EE684F5A0EC60DA908C5167F0302BBFB8940817D4C7D2F242DB6A980F196A2FF973223D73866B4E226D3F6EEB8177536FB10DA9E7BD864B0020C636F3A3673761A17B6865992FB0755AE9EB8036AA41776294D0FF8EA6F12CC9ECB45D45B154F2BF03B0A70E2B42DA1A7F99AA3FD4819857118FD77666D476C3C9BD258377994FB49EB5E820B416CCC5449895DEF2EAE3637CC8D5828D9DA7F1727FAEB740A7148BE35A4A689C75D152DD4DD431EAEA135E3AC5384BF7A226971B5BE18E041D046843F9BE8552292DF886C97F010DE239C4DD431163A88AB440BF14BD8B69D409C48366F289E59282EDE9796CAD4A1975FF52A2332DAC6756CB25AA24273B90E22B2B133A5C3F0805160E510B192D6BC18370F43181AC300D06092B06010401823711023100301306092A864886F70D0109153106040401000000302706092A864886F70D010914311A1E1800540053005300650063004B006500790053006500740031305D06092B060104018237110131501E4E004D006900630072006F0073006F006600740020005300740072006F006E0067002000430072007900700074006F0067007200610070006800690063002000500072006F00760069006400650072
 1497:d=1  hl=4 l= 879 cons: SEQUENCE
 1501:d=2  hl=2 l=   9 prim: OBJECT            :pkcs7-encryptedData
 1512:d=2  hl=4 l= 864 cons: cont [ 0 ]
 1516:d=3  hl=4 l= 860 cons: SEQUENCE
 1520:d=4  hl=2 l=   1 prim: INTEGER           :00
 1523:d=4  hl=4 l= 853 cons: SEQUENCE
 1527:d=5  hl=2 l=   9 prim: OBJECT            :pkcs7-data
 1538:d=5  hl=2 l=  28 cons: SEQUENCE
 1540:d=6  hl=2 l=  10 prim: OBJECT            :pbeWithSHA1And40BitRC2-CBC
 1552:d=6  hl=2 l=  14 cons: SEQUENCE
 1554:d=7  hl=2 l=   8 prim: OCTET STRING      [HEX DUMP]:135DB999CA2CD6B1
 1564:d=7  hl=2 l=   2 prim: INTEGER           :07D0
 1568:d=5  hl=4 l= 808 prim: cont [ 0 ]
```

再次，让我们解码嵌套结构

```shell
$ openssl asn1parse -inform DER -in extracted_data.bin -strparse 26 -strparse 23
    0:d=0  hl=4 l=1466 cons: SEQUENCE
    4:d=1  hl=4 l=1462 cons: SEQUENCE
    8:d=2  hl=2 l=  11 prim: OBJECT            :pkcs8ShroudedKeyBag
   21:d=2  hl=4 l=1270 cons: cont [ 0 ]
   25:d=3  hl=4 l=1266 cons: SEQUENCE
   29:d=4  hl=2 l=  28 cons: SEQUENCE
   31:d=5  hl=2 l=  10 prim: OBJECT            :pbeWithSHA1And3-KeyTripleDES-CBC
   43:d=5  hl=2 l=  14 cons: SEQUENCE
   45:d=6  hl=2 l=   8 prim: OCTET STRING      [HEX DUMP]:66AFD4385D4302C4
   55:d=6  hl=2 l=   2 prim: INTEGER           :07D0
   59:d=4  hl=4 l=1232 prim: OCTET STRING      [HEX DUMP]:93F23B4782B6438E5CB094A8C35CF1352F486FA1F7E3708A3F1BFC865A5EEF3C931DC82BA36EEF23609FE4717D0A021EEF8A981021BDADD04AFA64131A546CE65191A88C001ADCA9A5A15EDB1178E0DADDDCEDDCC3AB13BAADAE35B2B87378CC9158C0145DB1EB300E129D265C92E2C726E4790DA9F34AD0B80AF7BFD152B7AF4DD97B9B3BC4057CA245E4B871B871023F96832DCA3A4BA3E8628C34ACB48C75497CB8949CA48D1EF939495F2A0BE4B7497E0C19659EBE083ABFD8268D97149418C969CE28112F31255383994AA95B50C7A15285477A6D01B955E80C9F961FD03226C8233CA6F4851318D0B22B5B0E4D536CDF729827F2A12289E789675DDE3BBDC339376447AF09CD807AF811D216D148126B42177D7F1634BFAB0BB959A485BE82F7CE08FA8468FE526D48B02CA70CAF5EA55B786E7659DAFEFFC8292E15C251BC48D27F15860BD32E2FB67FB70DDED2CB7D199ECF107FEB5F57CA6D7D83ACA47DD20D23E3F7F73AF93753F1D6E6C42060A2F0A19CA9905CFCA4705F8DA96287D57584E9D0C9FEE127A1F8E91E6AA112FDD0AA42714BBFBDF1DB07BED4D3BB70B2AE3D614F75E17B8932E3ADCB8077DBE6EB9A3B723DFE7000B0B8DAD199D8FF4B8501BE45671BCAA8F3F5A9EB9EE67805F91C0734BE00F7EFDEAD031308879A852612AE3910830086EF4BC3CD6F9C14C5FA50F563EAB57C89F6AA49BBDF923D5E8847017C2F134AC4777E4E52D1DDDC1CCDDF800CC07DE1E733C8D233508E88306A0C9A035B1B61FA386F10CB1841C05C3442CAC764B0A5276A1047BF6EFA0E621A2FAE1A8792D8C5E20F692A472D88F96B32EB3D18B066BBEC04DAC120ADD3A0AFDAA2D81DF0A2CAFD1C135A0EC7AAEF4474B2853C125487DE8A7623F25F0029F912F9F689DD0AD5F4275FC8DFB6ADD908B677D3975AFBC207B0B24D225EDF28F88C17C451D6F0A8521CA55B873F611C742C5C7525B04C6C3E2BA0BC59D43C02EE517BA8D08E102F9837A6B37C505D2BD97D23AB4F6912B5EB67747EB572969057B923D347980E7F3338F2E70AE1E13B2071D9DD84991937B676838F8C42BB6A36A06A78B895063CBF9E20FD445EC96CF886D58FCA47230593FE7DA25535BBDAD2BED116FCF0A47BFEE90F6C0C227A5B9DFA33BDAB645585EBD3CC402DE595FF1A016A1B73472580FB2CB271CCEDFF473916D72334E4D5F4674EBA649636B00D05C852FFDF930360DCEFF949BEA357AF1DE79DD503E9705BAE51488F3B5F4468F15FC17593B7C06E2E5D7A26D02112E28034ED3D5C2956159CD2440D8B03BBA8E227608FE9C12FF0C0A12600AE3A3938AF7DDAB4BED9243A891D4EE684F5A0EC60DA908C5167F0302BBFB8940817D4C7D2F242DB6A980F196A2FF973223D73866B4E226D3F6EEB8177536FB10DA9E7BD864B0020C636F3A3673761A17B6865992FB0755AE9EB8036AA41776294D0FF8EA6F12CC9ECB45D45B154F2BF03B0A70E2B42DA1A7F99AA3FD4819857118FD77666D476C3C9BD258377994FB49EB5E820B416CCC5449895DEF2EAE3637CC8D5828D9DA7F1727FAEB740A7148BE35A4A689C75D152DD4DD431EAEA135E3AC5384BF7A226971B5BE18E041D046843F9BE8552292DF886C97F010DE239C4DD431163A88AB440BF14BD8B69D409C48366F289E59282EDE9796CAD4A1975FF52A2332DAC6756CB25AA24273B90E22B2B133A5C3F0805160E510B192D6BC18370F4
 1295:d=2  hl=3 l= 172 cons: SET
 1298:d=3  hl=2 l=  13 cons: SEQUENCE
 1300:d=4  hl=2 l=   9 prim: OBJECT            :Microsoft Local Key set
 1311:d=4  hl=2 l=   0 cons: SET
 1313:d=3  hl=2 l=  19 cons: SEQUENCE
 1315:d=4  hl=2 l=   9 prim: OBJECT            :localKeyID
 1326:d=4  hl=2 l=   6 cons: SET
 1328:d=5  hl=2 l=   4 prim: OCTET STRING      [HEX DUMP]:01000000
 1334:d=3  hl=2 l=  39 cons: SEQUENCE
 1336:d=4  hl=2 l=   9 prim: OBJECT            :friendlyName
 1347:d=4  hl=2 l=  26 cons: SET
 1349:d=5  hl=2 l=  24 prim: BMPSTRING
 1375:d=3  hl=2 l=  93 cons: SEQUENCE
 1377:d=4  hl=2 l=   9 prim: OBJECT            :Microsoft CSP Name
 1388:d=4  hl=2 l=  80 cons: SET
 1390:d=5  hl=2 l=  78 prim: BMPSTRING
```

这实际上看起来像一个 PKCS12 文件，这是一种捆绑证书和私钥的存档格式

我们可以从中提取私钥

```shell
# openssl pkcs12 调用 OpenSSL 的 PKCS#12 工具
# -nocerts 不提取证书，仅提取私钥
# -nodes 不加密私钥
$ openssl pkcs12 -in extracted_data.bin -nocerts -nodes -out private.key
Enter Import Password: mimikatz
MAC verified OK
```

我猜证书文件的密码是 “mimikatz”，但我们可以从这里获得相关信息

获取私钥后，我们可以使用名为 RDP-Replay 的工具重放 RDP 会话，并找出攻击者在入侵期间所做的事情

编译后，我们可以运行 `rdp_replay` 可执行文件，并可以选择保存攻击者按下的键并将捕获的剪贴板事件数据转储到文件中

此外，我们还将重播的视频保存到文件中

```shell
# -o recording.avi 将重放的 RDP 会话录制成 AVI 视频文件
# -p ./private.key 指定私钥文件（用于解密 TLS/SSL 加密的 RDP 流量）
# --save_clipboard 记录剪贴板内容（如果 RDP 会话中有复制粘贴操作）
# --show_keys 显示按键记录（在录制的视频中显示用户按下的键）
$ rdp_replay -r ../e8e2ceb9-b77f-4b26-b09a-fcec86e27497.pcap  -o recording.avi -p ./private.key --save_clipboard --show_keys > output
```

他所做的是使用不向用户显示的密码压缩和加密标志文件，然后进行 base64 编码并复制到剪贴板

这就是为什么我们必须保存键入的密钥和剪贴板事件信息

键入的按键记录：

```
RDP SSL MODE Requested by server!!
SSL private key found.
1024x756x8
REALLY DELICIOUS PANCAKES<Tab>REALLY DELICIOUS PANCAKES
```

剪贴板的内容：

```
N3q8ryccAATjAlOVMAAAAAAAAABqAAAAAAAAACmoQ4fA1DQXZvCzJGIg/8cxnh8QXnWoDkwNxjGL
37P7rvVC2SMn8+wquEv/A5HBL9djQewBBAYAAQkwAAcLAQACJAbxBwEKUweBdxD1DDirkCEhAQAB
AAwrJwAICgGwcALcAAAFARkJAAAAAAAAAAAAERMAZgBsAGEAZwAuAHQAeAB0AAAAGQAUCgEAAFNu
lssb0wEVBgEAIAAAAAAA
```

综合起来：

```shell
$ cat ../clip-00000000-down | base64 -d -i > flag.7z
$ 7z x flag.7z

7-Zip [64] 9.20  Copyright (c) 1999-2010 Igor Pavlov  2010-11-18
p7zip Version 9.20 (locale=en_US.UTF-8,Utf16=on,HugeFiles=on,2 CPUs)

Processing archive: flag.7z


Enter password (will not be echoed) :
Extracting  flag.txt

Everything is Ok

Size:       39
Compressed: 186
$ cat flag.txt
HITB{44519a67ffc654e40febc09e20e8e745}
```




<!-- Imported from D:\\Book\\Misc\\Chapter5\5-29.md -->
### MSF 流量分析


![](https://pic1.imgdb.cn/item/67f25d6f0ba3d5a1d7eec9b2.png)

打开流量包追踪 TCP 流，看到这个基本上确认就是 MSF 了

![](https://pic1.imgdb.cn/item/67f260e90ba3d5a1d7eecd26.png)

往下找红色响应部分

![](https://pic1.imgdb.cn/item/67f261690ba3d5a1d7eecd84.png)

MSF 流量特征：

用开始的 4 字节异或密钥对后续报文进行异或解密，得到 32 字节的报文头

然后如果无加密，则是TLV报文；不然就是 16 自己的 IV，然后是 TLV 报文

```
Values: [XOR KEY][session guid][encryption flags][packet length][packet type][ .... TLV packets go here .... ]
Size:   [   4   ][    16      ][      4       ][       4     ][     4     ][ ....          N          .... ]
```



```python
def DECPAK(PKT, AES_key = None):
    PKT = PKT.decode("hex")
    PKT_dec = ""
    XOR_KEY = PKT[:4]
    #PKT_dec += p32(XOR_KEY)
    for i in range(0, len(PKT)):
        deced = chr(ord(PKT[i]) ^ ord(XOR_KEY[i % 4]))
        PKT_dec += deced

    PKT_ret={}
    PKT_ret["XOR_KEY"] = XOR_KEY
    PKT_ret["GUID"] = PKT_dec[4:4+16]
    PKT_ret["ENC_FLAGS"] = u32(PKT_dec[20:24][::-1])
    PKT_ret["PKT_LENGTH"] = u32(PKT_dec[24:28][::-1])
    PKT_ret["PKT_TYPE"] = u32(PKT_dec[28:32][::-1])
    PKT_ret["TLVS"] = []

    pos = 32
    if PKT_ret["ENC_FLAGS"] == 0:
        while pos < len(PKT_dec):
            #print PKT_dec[pos:].encode("hex")
            tlv_len = u32(PKT_dec[pos: pos + 4][::-1])
            tlv_type = u32(PKT_dec[pos + 4: pos + 8][::-1])
            tlv_content = PKT_dec[pos + 8: pos + tlv_len]
            pos += tlv_len
            PKT_ret["TLVS"].append([tlv_len, tlv_type, tlv_content])
    elif PKT_ret["ENC_FLAGS"] == 1 and AES_key != None:
        PKT_ret["IV"] = PKT_dec[pos: pos + 16]
        aes_cipher = AESCipher(AES_key, PKT_ret["IV"])
        PKT_dec = PKT_dec[ :32 + 16] + aes_cipher.decrypt(PKT_dec[32 + 16: ])
        pos += 16
        while pos < len(PKT_dec):
            #print PKT_dec[pos:].encode("hex")
            tlv_len = u32(PKT_dec[pos: pos + 4][::-1])
            tlv_type = u32(PKT_dec[pos + 4: pos + 8][::-1])
            tlv_content = PKT_dec[pos + 8: pos + tlv_len]
            pos += tlv_len
            PKT_ret["TLVS"].append([tlv_len, tlv_type, tlv_content])

    return PKT_ret
```

首先 Meterpreter 主机会向被控端发送公钥，这部分默认是不加密的，本题给了私钥，所以公钥就没有必要用了

然后被控端根据公钥，对 AES25 6的密钥进行加密，发送给服务端

服务端和被控端接下来就根据 IV 对密文进行打乱，互相使用 AES256 密钥解密

依照这个思路，我们对报文进行追踪，解密出 AES256 的密钥，从后往前解包查找攻击者的命令

```python
AES_PAK = DECPAK("2926993adf8c06b90319d8059f51ec99b401f9b42926993a292698b52926993b2926991c2927993b4a49eb5f7648fc5d4652f05b5d43c64e4550c65f4745eb435952f0554726993a290f993b2924ac0e181fac0f1110a90d1f10ab031e13ac081b16aa0f1a16a0031813af0a1f15993a2926953a2b24be3a2926983a2927913a2d24b039ec75e27c93f3e0167fb28dd2c98ea0fd2ff42887d961f4e205a619311cf4b8dd93f189d24b8eb45af277bc76cc0ea8d5a0b3332812e6c8f73cced9f1d32189311dc13c30b80ebf944228979fd974a6ce23aacf386ebb5dbc1ac414a49678e6425944edf4a56f263a9c9e2a80e4d1884b35fc8da6e68bff64d33265350bf3e2b72dc5b0f0580cc12925074fc5505c9cd250b279150b9701cf5b2666ae9d0a0722f8b72aed8ffaa51f43594ebebe13b5bcb75e8a33c8cd396445c0c9da3d5a5b862bde38f62d13afd5387a62abce70e3d4192e3e96996ceaa0d1b0c7796028bdeabfbd8eddd13576f23135e1e7b06a0057a4b07bc786394ba1cd691547fad5db3a2926953a2b269d3a2926993a2926813a2d27542832d93a2fb12d08349729256baeb187")
print AES_PAK

AES_key_enc = AES_PAK["TLVS"][3][2]

AES_key = rsa_decode(AES_key_enc, privkey_pem)

print AES_key.encode("hex"), len(AES_key)

print DECPAK("7e30af14889a3097540fee2bc847dab7e317cf9a7e30af157e30af7c7e30af144a1999b733e68b894ee6b64581a31e4f800f1e2413c6ffabc4690df0ffdf5ad592f3d3de710b43f85611c113dff2d03a4a91fc6cf046cafc37d823f986dee137e05368e717be6acbd31e87435f8bc7601dae969be7b5888050246f2f01b9cab8")

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4effd2ab4ef54b835d361e2e784b4e2e9168aa4cd074c5b434009388fb2550a98ee6d49ea108c50b1f1b6c4c17a6fa0b01cd5e04f5fe5ba536da008841f20cef4324fe752f92923ea05e1d683bf991306b6878e301a68c933579c58c47482afc576545cc3cc2610d3f2ee70a3a36404996ff877b3a7756efe57bd043ad32f04ca9a137846cfeb6f53c817f32986117c0f26fc30b60b70a1f072987c80eda747fcc5ae85da2ed3", AES_key)

print DECPAK("2926993adf8c06b90319d8059f51ec99b401f9b42926993b292699b22926993b0438eb2dc77a917a03839c6bb9f6afb8192bbf8baf251e45d7f08cb799975ab8c4661cee35f7d4c9c63b7d1607fabdd602313a66d04c4fe8570ddd650eb2e9595358f04c0e781a347ddb62027dea0a0e899709fa3eeaa238600e4abb48d28fce74817d9ce4a627d36b5ee9e9d59719e4ae246ef1d39f8468dbe5ca236dbee597", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4eddd2ab4ef54a64307198e637c0fd0dfc74aad3b1fbcd26e62d8113e05e6af14d5cf78b82c11a0761ba6e95a984da59db055e44b9d5830cf6ec34a0e7ff0686fef9472546c93cd169eebf86e933f424f8a6f116bfa447a286bed01168019eb59eb83f5d455be5bf7fe55c49db5e7752b9b3135d1a4ccb6da5ca2c37af0c9311e6e335bc57642debf54952abd91b589527436429128a062f587edf20a215bf4161253898cc89a146c92c77cc6b34dd782f97007444f674dba89901758b8a7e55f1c82c7f0f0af78b41bae90d0d008518668d7fadf570da991365e09048b70d162b0e0b281cc28df2b64e759e480fa3dab1bb8635f85237205c66d6926fd85c829921956403b454598d57a7185ec80ea7ca1a8494d3c6ed7b7580dfbaaa585f018ca8c8efd5dd15b38e9281c3fc0385312544d7f24cb0fd3e8392fce9f07501028be0b6fa656dccb9247ab9b99fd3ff8cc04199d26398ea7fb4fac7be96769c8fa5f7e0d63cc524f0699104e89c91411d5a2168bbd7b59237b65143f81107667fddc2ba0e5c5382cf4dd672950da2ee088ba8e74039e872d89e69aeca904dac87463bb691075cd888a93d07c9ca792ffc53bd25a8487389a1776ffdfc4232028ea08d5f555d7738574ddd942d95d7cc5d0b086798c991ed140c72257b039a7aa8b61727976c6cd939b3815a4e04e94bafe8d5cb69f9dc11930431207ddc03517ccfd5e4499609b87914c40be1481a5ef174a45ce0fa70e8f6a683a2975a1b6b1905613444dac3ba12e8902d41f6ba2e7c940e347a6fdade78c6560e79f2f2313a90b74af7c1137e0bb3cd9f721af2a13deade2551a4be241b095992a608fb0e5aa063a10207414c2f2c18f7272bcffe0ecac0cfa8b4c2bf2bb3232044cccecaf91ed310d07ca1c", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4ef9d2ab4ef5415d984862f64b0e891b131ecc5d2a06c8ec29332954025fa1b2807cb007edcb73bba65e5c12cb31a40db6b26a4fa05a8d3e5a67d3871228a8cd6b6f6ce75a263823fecc17be818e1bd27a4cc9d512372e5f2f58f0aea4a11bfb631ceee791e0f5682f4dd94fc8b1aa59514037a8d76ff8b8d72ca32c2a299049f9089f430e403b9c64419d1eb8b6577c440bec9a16a5c51081ad4040fa32759ef37740c20a1a3893f511b08d37926ae67abedfa4084d1c3cb97f47a130dea915cd000fb51873c", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4effd2ab4ef549568c9bca4f5201e93dbdb4852d51967a2e9b23cc1a88ce4b2a37950450a8586cde6043906b7803994a8ce6db44ede0258b2b5d29318145c26075ddb963991ad85007119e0ad4de637818aa78e8fbe14631c113894ff87aefc336a427eb6c90cfc4e8b2efb088d63c1a301381cf90270e2b7c96371530800724ed4762f963d17b9ce23ab12cc4d656fbfc999d144f5f7cedee8eb9cc56200d51bede00a242bea", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4eddd2ab4ef54e1a628a81569018cd0f5bf315d7b320e5b77b0f8b8345c79e0fc4594a74a390315f368d3c474883c2aa91a6e0573ff936f5bb5aba31790051bb71dc50bba249affef1b06d4fa9d297abbc5142c40a90d031af7e4cf885d6ad3e09bc0338a8d0e8675b7f332797ec9d87c48b37e8a2e3a75c8f80d78c3de96029eb298203090029a32a858b55714fb5a805dcd52c02734d04d04285f729285ba731207c73ee0c7c2ef52ecb3e973e787cce4fd720c83a3a221f8a98de6180c939785c52fec692acb34f3cf2a36de23a850928dd405afd0abd376c4dac3582153ea8de6e3cdf19fd4706688782e9a48b8b05c591abcc892555e2a061601f73a3498bdcbd1f1baf142a6471065d42312b48ded576689a1bb5bcdb877e8160995be495603a4405e2a2892f2b650760640286b1ad93461909518fd8392929e251157b0c5461825badfa065a42bb12b60bb7bc0fdbd62bc376b188f705e76820e832c0226f536b0c2620ab917dbebb346c9bf01c2a0c81832fed64e6f64407d3d7f051c6c8460900c50d2d8c361f57afb5958888c1bf983bd314ea54697d87ce70b9230837a98398b4d1cba073b86615712078079362f6fb1b0c80e2b25af230ce8016a0b0115607f730195f0811d21db64cc422e5b0f73d6fbcc88a0843fbdbed51db87851c940c99e4a0d72d3fa7604caf585b40b962f93cbd252373b78bbecf891975d8e152358534d999fe0008453b9f6952acccdce89d2f31021f67b5d4ae2099ff7b38d92a9f2f7541e9fcf9a89d9b8146dfbee579bfbd933ca07bb7ba04efda4c24cf5e9ca43afdd5bdaea05677fd293bcd74c31b37b24196f8e0d0be9e79831f7794ea91a52db03e8f35230ed75adbb5a0974380905b510883af3be066a03b984af5effc060", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4ef9d2ab4ef54a74abf08695adaad8be818da14b4dadc981f6157553f5d955e82e35ff422847f969300e94f38c7ec84dcc4fef465f3e62b0fbc142e3761c036cdfe4c5e7a880445ad31a51ee1112a89fec6e8693852d739fbd91d05327c0d6cda8cb26a17c3ae9b43f28774f991afb2545a69210f47d82339c219d7f7bfbd5d76c2a4a82e376ef1d2ff1142a0713b1e055bd6c6c78866e4da63c65cb6d161da9d55222c90984a6295e5b68bf4dce2ce684b9d067c02352b8f3fa457783c911a340f2b9c552fa6", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4effd2ab4ef545042629ac50792c2d9f387304e12245dcb7bc137fcf865d9548f52c1f4b4d7662a2e5b4a04ce32d51bdb99b725807534a9b288fdcce5512a4801b71d7a97de1624de6175b884a4ef080e2b8b39683a98d86cb9ff8ce0e1c1c7300fc582f2ed5d8f8a2b23b77ddb01e65e059738478f9aab61ec7e93f8f17eb1903786ae1c654edaf7ca60cd5c4d7012bffea32c54f5091952d4ddf7573efe77bda7d974bc4bb3", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4eddd2ab4ef54a0c32aa9adca2454808fa09531321b03dade8023acab14d49f4bd36589277683be8ad1f5483cff7411c3db741baca849b7647a94650614d5ca05acadffd7ead06a172d74f279bbcf94a7c1365a1f6c624ae42f39644511bcecdddd516ba7e64280b6ee9300837628b207057b3c1d67abace40bb66ea250c438daac90110725da12c7b4fdca846a84ff3c842355eb5ae9c5814a83f0266e8e304b7c18c99ee2e6dddba999ef6c16bd459f7e5e0133a89f93c139887816477b133e70e333fd2c8187c39b504d983dded4b8d2ed57124dd564ecf36212a8208864dbaa756317d084d85a54066fb1179efb7e1d2ae41d49e5f79691f83676cd6d9d9f7e69ef5be859398c00bbed2dae001f80f7e784ed3ecd37e860a1a0b7eada9cae6cd34a78fd383ffb006597de7a427cf3fe2109edbbc9bbd8a4e58b7e9137c836b0ee899e8228c536e78664cf6f1626a298b635250d1e3c8b67dc33ce96ad33d8562e7bbc2eac3b0268aaec137377fa29542af2ffb940ad168fa6bc28a24d671c71432ac557026f7bd6cb5c4a3d6295ba03f9732138b74c6c0190c6d03cc65ec7ff90dbbd6a033d3d8f464af5523ddc1eec87f4a8920204bea066b62463f7055fc3a3443eb6831e068ff7c7884534c8c961b59ab638cc2c68f996c1e04938e6b36982940470775a8d67842d62db2a8fa297057816e3c1a8494ab8d8605cd363e7b02398f9462b29d4c6ae6d054e34df2de2960da4d2ecdc03da04a8b8c0f0429f5b6d69f654f895d39d538d772a54aa99e6ff4c9f2553a8d562e67de80bb6ce6f7b64f4a15006a97f3e356201b0ec1f35cb01d8e3121658f2f07db46174c1332dcda43e11ea9aab1d6da405ddeea61ebaca8db07aab89dbc971a107144f77d1e34fa5d162da5a", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4ef9d2ab4ef547eeb277e493e9d2dad9be2f9bb47f0b6355a47223f26e74ea01c55dbd02f3a256bebb806798caae2813f140c39b000a2b8d366c28b88bf92e71ba5760993884f3661f258cac484858353a5e430f20ab1ea10e2b9d58a92d395804ac305c8620cc25a0e41c33543723871e32dd2551b740e083d9524d8ab912d7d33ebc574ac103aa3b6d960d6812a40eb371be855151846d027dac6694e01d3ce26bcb648309c721316d0baf1c167a1ff4f21181a4f45fd1bb8b4219047d7cdcbbc0befff021c", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4effd2ab4ef5416d7e52b7aafb3d98d01695ad4dad9c844c16f1f5ab9c6524bd888fa10316d0f8cc027e58ca6abac24105f2b006c5c1687ee80da56344e9915c81c88195897056dbe672a7d5ed6060ca3b079edb8bd7c7137ba8f78160c16fec5ce685439cebd31761f47527f04cf840da0cdb430e5f71f13c6bd45ee04e8aa6670c2f3265b8663c1c9b600f68afd7b943ae566f9e9bf8eab2ea9714bf1fdce89e89e522af060", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4eddd2ab4ef549ed176f02b7f872de8b1a1c09035e4c445e4eefd55f8b21766398cebdbbbac51638200564e211698faade01639890646b5a7df93dbfe2ab6fed342d53fe139f6d698075298003c873a3b394d52d5fa2db04ca3ced01e26f505a9dae196e528cf229390e572fd3c4f49712d4552f182e903e4cab21880065813920d8eb27d40a57b691a8cef7e83abaaec5b6d27b653942481771236a9e1fa96de9fa7013539f4f51a632c7d5377087c1e5ff04ece37e31be0201d8acb15f3ffea099ba7161a8b099fe436babe9ec972f5acd7b1b13c8fc63531a0e48613fe0828f70263c21af801c1cdbae91dc7f05dfd348e9120230dbbe52dfbc7d6f4ff4281a26e04d64ac17be5ffdd46c38bfd4d5f23e536bb976210e764922a9fa1a4a0d32676c2a3ae77376b0fdee2e484877cca94e36d38b7fe4370ab2cd24dd1c1daf37a3025b82c4cdd43808997fbab7ae1bbfb38039f225f238a05c7a43d75d325964cc8709d06e4a0201760bd978ae7719af4f44bde5e55bcfd4cb5e20f71fb9c2ac3bf71eb7b4552f1ea466e11218b291d2311344e72232c71286fc1b41464aff44975bda745c78ae7309c1c6cafdc22833de0585e879d8fa1257421c6372cf5d6159eb927a64b32b4a26f93e119983e1b75dcb51588d666ce3f66078a9f9ed1b843bd82a0d8ba2020869fd49ef9434610961c7d95ce2e43cdf3b4d8cf1a1eaeadcfc0deb5651a6af86cecce1ab15172160eb25c17421e65d34e4efbdd6917860610360b662aa4d7e3fa62157ab07d1e2a2af88f1387fd82df72155f0602ece0ce617215c5bef59a393e0d7cd2572d848510c5c09c78916d6240778f2d2efead1dd1795096554a8100d61bcf1a7d51e5fd22e9633d0673268745990827da0027c7812fbdefb0d1", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4ef9d2ab4ef54f6cf111c29995e8ddf9cfc68568b392a827cbd823b57a5b72e8a5befc5581afc9a3d62dc240ec020910740d3d782ec0d25232da13f1f1634569d749562e8e9c65de0016af28faa98409554e21b7932eb5587670935ddc66138139828832adb339b6e390090432eb4ea1f292ad9918345903aae300c1ece3e8e04b19d3a95856d908975f370b4e4dbb054f7d2b62325e95578df134e23e15478855f5015318f78d6e5cf9ea0808207153432f12f6c916dba4d73a5b603abd5944ff81873278e0c", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4effd2ab4ef548a457a00a50fdd743b833ace6e884f5e1ee7d93e1d5465013006b47661b78a31cb121fddc9cad7539a91d2f876775063efb3517bcadb658160ec961b4482cd1ef4ac797936a9061a48318c67ff7e5d2055f8d2b0e7e5fbca0fef43935e23afe3daaee2c0400d950f96c2a41e3a36dc82b6f02f8ce2031d95fee1c4129e3b11e352afa470bc219fd9ebc0f70cec328071cd9ee9c423559debc72a4b82997bcf72", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4eddd2ab4ef5417935c499443c593861b309077d9bde14d10e835529bf1ae2d48cf5eb8732fe500780aef921e1e4c9d42400ef3aa0d8642e9a53a17cc4115093bdfe64b15af6ddb9ba8a928e8aee3c693712a25cc9776956dd2bd88e2eb1b340e49c7c06004025d4018b5cb963edb72d36335c0e46599684bbacba9be975919d374cf36f8036bc85dc7b6eb28f2db271d89f2a6884850fba6a4223a607cfc6ea27ad5967fbf111193c80dc5651e5875bdde2590d3759c6229012c82f571bac7e9c34278a2c6510c5440a563282078f75437a6b83a2795628747c8a42cd1962d5892a301f240fa0ab2ff2ffdc37fd9c31681c7be58bb211fa2a65656612936aee9610785fba11a8fb5eeffecffd28da7257a06147b8b3f7b4840b9e14ff58a62de5d895a72192db8da9bc8eab0018dba287c2259a2424ef2c07320ecf8333bad402ed073fdfec3a9074e4ac483adffaae6827363292969b0a8b667ce87608c280eea0d588636862e7c685a1098c4cfe5be6ced796dcb68a13dc8d627c0a1507f29118c873538eca45775ff552df3caeeffd83dda2b690c577a4ac2a6b2ee1fb6292f30b92f653817b1347a2511f4ce6b16b8b326561788207153b8e34abe2c01f18084c39d8d112f30abba79c18fd41364dc6569700ba8e50bfd3698c364c980185e41983b5b8a2123e05c8d2d20e8ff344d45eba3a696c168a41828e89dfd52b933ae2fda939115e33388f8d001f222968cdff85014df2a13012e8ed2de7b7e344016a31fe040c4f499b11405331825d792889f6ff88de901bb22c63b3b2ed03230f466dcfd266b9de98a9555e55612be2488cd4725d8dbc082821d5de0579c71755d2f1546e88eb20a0f4bfd15d6ee97a560e73fd9a428af958e2d8f4359ddb89de5d02e387a", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4ef9d2ab4ef54673f20ea63ed7dcee5ad41191624f11654116ea6e529188198f3d8c99fb8c7a4cd02d95c775fcd228293c4e07f457fff20f4dd86beecd707729f7e320557c541568e499880bd3d60edd8d517ef847314fa92add61d1ebad74bb38fe874defc674d5c0a185089963ec494879a56af9fd814a476e41e057c4c1a00a9d1f69e1b7c45bbb769791636ae9a42514c366eee52f9f5346c92c6fa9138845f0c3eaf3a30f3f71c048ee4f9fd3e5dec452cde0bf13794ad43c7c7334c1b841294ed61d3bc", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4effd2ab4ef54bf7b08dd116835468ca87c273505a310dab1059bfd1ba816574d1e3f35f8429788dccf3848b0872bfc5b5d149ca192532ee30b2291bb57fca70ed1fb4f7653445f1c373a74f0e324ea23efdf3c3be17aa51821c4fac4a2b26f73f7ac306ad49b7cbaf5edbdd2e9962a1ee0d3127ae049a5823e8f2ab88879dbb679f37323e1497fdea2d807af51c94a7f8a9a27dbffcc65ee8778848a5315a994b9a7c71c914d", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4efcd2ab4ef543db8b8d5acda5a1235b3ad7d07db722102cd9e53750cef7e31131b2d59afa2206d5adc9c877d8ea88bef37dfdff1ffe46e42443d29429793ab306042ee0b2173de2b24e750a0ec61eae0fb8dc5ba0c9961330cfc253aa550022cbf03120d8561e96d54ff94e08ca352d1c069065caceb101e16845fe69db34893f8cb9f3c1e7749b573c1e3f4f2caf2486620cab399fd", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4efdd2ab4ef54e28b751ce10cff077f8445dfe8ddc32363ccef83833a6e9c72f75026116d0253b77e884b483db4b28ab58a9397911ed8afd892a938b4eaee9806d96c070f1f1e587bca16e8e8e16e2b2af5a530e84cc95221f13ce3c66b391318c11f6740bb16d7216dbf70004cbdf4e451b13cb70223235f7e63a33d32c631f512bd5ca7511b", AES_key)

print DECPAK("2ab4ef55dc1e70d6008bae6a9cc39af6b7938fdb2ab4ef542ab4ef8d2ab4ef549df15c8d63e084ea41796e1080c422c10c4af26c0b5563cb3058bd6e4aa3f2cc22de1c6edf7e6468ad7e1ff8fa11bd0d2955218906c89bc9c1aca68485ba41d6c1363d26e1ca77e379eede5843a78cf2890a4a4d48d532564d081638df298d10b5b8e57b4714d29993407e26b857a054f18cbba0769a9d7a3ab9b2fc503b9b4e0f13e3e0e4086d9def861eb75b54df80426839c540b6836702d3585c1d11b1fcc1f56d6a2a58bee99fa22ea3792bd764075cdd0bfe11d2a7953c9174210b35afc3a38ab0ff13abebf06b74046bc902df", AES_key)
```

发现攻击者对目录进行了罗列，出现关键词 `flag.txt`

```shell
{'PKT_TYPE': 1, 'TLVS': [[24, 65537, 'stdapi_fs_getwd\x00'], [41, 65538, '35193328683991905719198692993325\x00'], [28, 66736, 'C:\\Users\\PC\\Desktop\x00'], [12, 131076, '\x00\x00\x00\x00'], [24, 262605, '\x12\x1b\xff\xa3\x15\x98\x0b\x91\x0e\xbe\x0f\xbcQ\x87\x97\x1e']], 'PKT_LENGTH': 168, 'IV': '\xa0\xf1\x95U\x8f\xbb2!\x117\xd5\x9bD<\xa0\x0b', 'XOR_KEY': '*\xb4\xefU', 'ENC_FLAGS': 1, 'GUID': "\xf6\xaa\x9f\x83*?A?\xb6wu\xa3\x9d'`\x8e"}
{'PKT_TYPE': 1, 'TLVS': [[21, 65537, 'stdapi_fs_ls\x00'], [41, 65538, '92992205236495284461596905472999\x00'], [10, 66737, '.\x00'], [30, 66738, 'C:\\Users\\PC\\Desktop\\.\x00'], [9, 66741, '\x00'], [72, 2147484869, '\x00\x00\x00\x00mA\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00C\x999_\x00\x00\x00\x00C\x999_\x00\x00\x00\x00\x0f\x18._\x00\x00\x00\x00'], [11, 66737, '..\x00'], [31, 66738, 'C:\\Users\\PC\\Desktop\\..\x00'], [9, 66741, '\x00'], [72, 2147484869, '\x00\x00\x00\x00\xffA\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x19\x18._\x00\x00\x00\x00\x19\x18._\x00\x00\x00\x00\x0f\x18._\x00\x00\x00\x00'], [20, 66737, 'desktop.ini\x00'], [40, 66738, 'C:\\Users\\PC\\Desktop\\desktop.ini\x00'], [9, 66741, '\x00'], [72, 2147484869, '\x00\x00\x00\x00\xb6\x81\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x01\x00\x00\x00\x00\x00\x00\x18\x18._\x00\x00\x00\x00\x1a\x18._\x00\x00\x00\x00\x18\x18._\x00\x00\x00\x00'], [17, 66737, 'flag.txt\x00'], [37, 66738, 'C:\\Users\\PC\\Desktop\\flag.txt\x00'], [9, 66741, '\x00'], [72, 2147484869, '\x00\x00\x00\x00\xb6\x81\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x005\x00\x00\x00\x00\x00\x00\x00?\x999_\x00\x00\x00\x00\x80\x999_\x00\x00\x00\x00?\x999_\x00\x00\x00\x00'], [12, 131076, '\x00\x00\x00\x00'], [24, 262605, '\x12\x1b\xff\xa3\x15\x98\x0b\x91\x0e\xbe\x0f\xbcQ\x87\x97\x1e']], 'PKT_LENGTH': 648, 'IV': "='\xb3\x1c\xbe\xf7*\xc6\xac\xaf\xdf\xc5]mR\xb4", 'XOR_KEY': '*\xb4\xefU', 'ENC_FLAGS': 1, 'GUID': "\xf6\xaa\x9f\x83*?A?\xb6wu\xa3\x9d'`\x8e"}
{'PKT_TYPE': 1, 'TLVS': [[23, 65537, 'stdapi_fs_stat\x00'], [41, 65538, '81395400468542538926467524183079\x00'], [72, 2147484869, '\x00\x00\x00\x00mA\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00C\x999_\x00\x00\x00\x00C\x999_\x00\x00\x00\x00\x0f\x18._\x00\x00\x00\x00'], [12, 131076, '\x00\x00\x00\x00'], [24, 262605, '\x12\x1b\xff\xa3\x15\x98\x0b\x91\x0e\xbe\x0f\xbcQ\x87\x97\x1e']], 'PKT_LENGTH': 200, 'IV': 'M\x8b\xcf\xbfIY\x92\x9b\xcf\x19\xaeL<\x90\x1eC', 'XOR_KEY': '*\xb4\xefU', 'ENC_FLAGS': 1, 'GUID': "\xf6\xaa\x9f\x83*?A?\xb6wu\xa3\x9d'`\x8e"}
{'PKT_TYPE': 1, 'TLVS': [[24, 65537, 'stdapi_fs_getwd\x00'], [41, 65538, '65703151916968344032521729631525\x00'], [28, 66736, 'C:\\Users\\PC\\Desktop\x00'], [12, 131076, '\x00\x00\x00\x00'], [24, 262605, '\x12\x1b\xff\xa3\x15\x98\x0b\x91\x0e\xbe\x0f\xbcQ\x87\x97\x1e']], 'PKT_LENGTH': 168, 'IV': '\x95\xcf\xe7\x88;\xdc\xda\x13\xa6\x1c\x93r\x1f\xb1LE', 'XOR_KEY': '*\xb4\xefU', 'ENC_FLAGS': 1, 'GUID': "\xf6\xaa\x9f\x83*?A?\xb6wu\xa3\x9d'`\x8e"}
{'PKT_TYPE': 1, 'TLVS': [[27, 65537, 'core_channel_close\x00'], [41, 65538, '58287235164616228196360033701482\x00'], [12, 131122, '\x00\x00\x00\x01'], [12, 131076, '\x00\x00\x00\x00'], [24, 262605, '\x12\x1b\xff\xa3\x15\x98\x0b\x91\x0e\xbe\x0f\xbcQ\x87\x97\x1e']], 'PKT_LENGTH': 152, 'IV': '\x17\x0cW\x80\x86n\xb5G\x1f\x07B(-o\x9dt', 'XOR_KEY': '*\xb4\xefU', 'ENC_FLAGS': 1, 'GUID': "\xf6\xaa\x9f\x83*?A?\xb6wu\xa3\x9d'`\x8e"}
{'PKT_TYPE': 1, 'TLVS': [[25, 65537, 'core_channel_eof\x00'], [41, 65538, '68965028063958896069137527866199\x00'], [9, 524300, '\x01'], [12, 131076, '\x00\x00\x00\x00'], [24, 262605, '\x12\x1b\xff\xa3\x15\x98\x0b\x91\x0e\xbe\x0f\xbcQ\x87\x97\x1e']], 'PKT_LENGTH': 136, 'IV': '\xc8?\x9aI\xcb\xb8\x10RU0\xaa\x8a\xc2i,v', 'XOR_KEY': '*\xb4\xefU', 'ENC_FLAGS': 1, 'GUID': "\xf6\xaa\x9f\x83*?A?\xb6wu\xa3\x9d'`\x8e"}
{'PKT_TYPE': 1, 'TLVS': [[26, 65537, 'core_channel_read\x00'], [41, 65538, '51236609532627967781124094944166\x00'], [61, 262196, 'flag{Meterpreter_Has_A_Greater_Enc_Method_Than_Shell}'], [12, 131097, '\x00\x00\x005'], [12, 131122, '\x00\x00\x00\x01'], [12, 131076, '\x00\x00\x00\x00'], [24, 262605, '\x12\x1b\xff\xa3\x15\x98\x0b\x91\x0e\xbe\x0f\xbcQ\x87\x97\x1e']], 'PKT_LENGTH': 216, 'IV': '\xb7E\xb3\xd8ITk\xbfk\xcd\x81E\xaap\xcd\x94', 'XOR_KEY': '*\xb4\xefU', 'ENC_FLAGS': 1, 'GUID': "\xf6\xaa\x9f\x83*?A?\xb6wu\xa3\x9d'`\x8e"}
```

继续查找就可以发现 flag.txt 内容

```
flag{Meterpreter_Has_A_Greater_Enc_Method_Than_Shell}
```




<!-- Imported from D:\\Book\\Misc\\Chapter5\5-3.md -->
### 鼠标运动轨迹分析


![](https://pic1.imgdb.cn/item/677fe3f3d0e0a243d4f2d15c.jpg)

对于这种 USB 流量我们重点观察 Capture Data

![](https://pic1.imgdb.cn/item/677fe52dd0e0a243d4f2d197.jpg)

键盘流量一般都是 8 字节，这里显然是鼠标流量

使用工具 USB-Mouse-Pcap-Visualizer 提取数据为 csv

```shell
python usb-mouse-pacp-visualizer.py -i 1.pacp -o 1.csc
```

![](https://pic1.imgdb.cn/item/677fe549d0e0a243d4f2d199.jpg)

最后去这个网站绘图

`https://usb-mouse-pcap-visualizer.vercel.app/`

![](https://pic1.imgdb.cn/item/677fe733d0e0a243d4f2d223.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-30.md -->
### WIFI 流量分析


![](https://pic1.imgdb.cn/item/6810a81d58cb8da5c8d458f2.png)

下载附件根据题目提示 `wifi` 使用工具 CTF-NetA 搜索关键字拿到密码及名称

```shell
ssid: MyWifi	key: 88888888
```

![](https://pic1.imgdb.cn/item/6810ad4b58cb8da5c8d45b35.png)

使用工具 `airdecap-ng` 破解 WEP/WPA-PSK 加密的抓包文件

```shell
airdecap-ng '/home/morant/capture.cap' -e MyWifi -p 88888888
```

![](https://pic1.imgdb.cn/item/6810afef58cb8da5c8d45c69.png)

执行完后会生成一个新的 `.cap` 文件

继续扔进 CTF-NetA 解析拿到 flag

![](https://pic1.imgdb.cn/item/6810b05c58cb8da5c8d45ca0.png)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-31.md -->
### MySQL 流量分析


![](https://pic1.imgdb.cn/item/688213d058cb8da5c8d6073c.png)

MySQL 流程图如下

```sql
+-------------+                                    +-------------+
|  MySQL 客户端 |                                    |  MySQL 服务端 |
+-------------+                                    +-------------+
       |                                                  |
       | 1. 建立 TCP 连接 (端口 3306)                      |
       |------------------------------------------------->|
       |                                                  |
       | 2. 接收 Handshake Initialization Packet          |
       |<-------------------------------------------------|
       |                                                  |
       | 3. 发送 Login Request Packet (用户名、密码等)     |
       |------------------------------------------------->|
       |                                                  |
       | 4. 验证成功 → 发送 OK Packet                     |
       |    验证失败 → 发送 ERR Packet                    |
       |<-------------------------------------------------|
       |                                                  |
       | 5. 发送 SQL 请求（COM_QUERY）                    |
       |------------------------------------------------->|
       |                                                  |
       | 6. 返回结果（OK / ERR / ResultSet）              |
       |<-------------------------------------------------|
```

发现有 MySQL 流量，直接过滤

![](https://pic1.imgdb.cn/item/6882151a58cb8da5c8d60b13.png)

按照顺序前三个为一组可以发现在第三次时登录成功

![](https://pic1.imgdb.cn/item/6882185558cb8da5c8d61d70.png)

在后续的 Request 包中可以看到查询语句

![](https://pic1.imgdb.cn/item/6882191958cb8da5c8d6262f.png)

`row packet` 里都是返回结果

![](https://pic1.imgdb.cn/item/68821b0958cb8da5c8d63db5.png)



在响应包中可以找到 flag

![](https://pic1.imgdb.cn/item/688219c558cb8da5c8d62d28.png)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-32.md -->
### Redis 流量分析


![](https://pic1.imgdb.cn/item/68821d6e58cb8da5c8d65f4d.png)

Redis 协议流程图如下

```
[客户端]
    |
    |  发送命令（RESP 协议格式）
    v
  +------------------------------------+
  | *3                                |
  | $3                                |
  | SET                               |
  | $4                                |
  | key1                              |
  | $6                                |
  | value1                            |
  +------------------------------------+
    |
    |  等待响应
    v
[Redis 服务器]
    |
    |  解析命令并执行
    v
  +--------------+
  | +OK\r\n      |  ← 简单字符串响应
  +--------------+
    |
    v
[客户端接收响应]
```

直接过滤 RESP 协议

![](https://pic1.imgdb.cn/item/68821f6958cb8da5c8d679b8.png)

首先来看第一个包

```yaml
6	12.525675	30.0.250.11	30.0.30.10	RESP	83	Request: COMMAND
```

`COMMAND` 是 Redis 的**元命令**，用于获取服务器支持的所有命令及其详细描述

所以后续这些响应都是 `COMMAND` 的结果

![](https://pic1.imgdb.cn/item/6882233658cb8da5c8d692a8.png)

这里可以直接看到设置的 flagflag

![](https://pic1.imgdb.cn/item/6882238758cb8da5c8d69343.png)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-33.md -->
### MongoDB 流量分析


![](https://pic1.imgdb.cn/item/6882277358cb8da5c8d69bb0.png)

MongoDB 协议流程图如下

```
+-----------------+       +------------------+
|  Client         |       |  MongoDB Server  |
+-----------------+       +------------------+
| OP_MSG (find)   |  -->  |                  |
|                 |       | 执行查询         |
|                 |  <--  | OP_MSG (结果文档)|
+-----------------+       +------------------+
```

直接过滤 Mongo 协议

![](https://pic1.imgdb.cn/item/6882289258cb8da5c8d6a6fb.png)

细看流量包

![](https://pic1.imgdb.cn/item/688229f358cb8da5c8d6b761.png)

| 字段名               | 值           | 含义说明                                    |
| -------------------- | ------------ | ------------------------------------------- |
| `fullCollectionName` | `admin.$cmd` | 表示要操作的完整集合名（数据库名 + 集合名） |

`$cmd` 是 **MongoDB 的内部虚拟集合名**，代表“我要发送一个数据库命令”，而不是常规的 CRUD（增删改查）操作

![](https://pic1.imgdb.cn/item/68822a4c58cb8da5c8d6bcbd.png)

| 字段          | 意图                                        |
| ------------- | ------------------------------------------- |
| `ismaster`    | 请求服务器返回自身状态（已被 `hello` 取代） |
| `client`      | 提供客户端系统和驱动信息（诊断用途）        |
| `compression` | 提出支持的压缩协议（优化网络传输）          |

再来看对应的响应包

![](https://pic1.imgdb.cn/item/68822aa658cb8da5c8d6c2ea.png)

响应内容大致如下

```json
{
  "ismaster": true,
  "maxBsonObjectSize": 16777216,
  "maxMessageSizeBytes": 48000000,
  "maxWriteBatchSize": 100000,
  "localTime": "2025-07-24T12:34:56.123Z",
  "logicalSessionTimeoutMinutes": 30,
  "minWireVersion": 0,
  "maxWireVersion": 13,
  "readOnly": false,
  "ok": 1
}
```

| 字段名                         | 类型     | 说明                                          |
| ------------------------------ | -------- | --------------------------------------------- |
| `ismaster` / `hello`           | 布尔值   | 表示服务器是主节点（primary）                 |
| `maxBsonObjectSize`            | 整数     | 单个 BSON 文档的最大字节数（默认 16MB）       |
| `maxMessageSizeBytes`          | 整数     | 最大消息包大小（默认约 48MB）                 |
| `maxWriteBatchSize`            | 整数     | 批量写入的最大文档数（默认 100,000）          |
| `localTime`                    | 日期时间 | 服务器的本地时间（ISO8601 格式）              |
| `logicalSessionTimeoutMinutes` | 整数     | 逻辑会话超时时间，单位分钟                    |
| `minWireVersion`               | 整数     | 支持的协议版本范围下限                        |
| `maxWireVersion`               | 整数     | 支持的协议版本范围上限（13 对应 MongoDB 7.x） |
| `readOnly`                     | 布尔值   | 是否为只读实例（如只读副本或监控节点）        |
| `ok`                           | 数值     | 是否成功执行该命令（1 = 成功）                |

其具体的值在 Value 中查看

![](https://pic1.imgdb.cn/item/68822adb58cb8da5c8d6c677.png)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-4.md -->
### USB 流量分析

主要观察数据包长度，有图片的往往长度很大，复制其十六进制写入新文件中


![](https://pic1.imgdb.cn/item/67728c51d0e0a243d4ecc67c.jpg)

数据包按长度排序发现两个数据包异常

![](https://pic1.imgdb.cn/item/677fe7cdd0e0a243d4f2d249.jpg)

打开其中一个看到了 PNG 头文件

![](https://pic1.imgdb.cn/item/677fe7e3d0e0a243d4f2d24f.jpg)

复制其值十六进制

![](https://pic1.imgdb.cn/item/677fe80bd0e0a243d4f2d257.jpg)

在 WinHex 中写入新文件保存为 PNG

![](https://pic1.imgdb.cn/item/677fe820d0e0a243d4f2d25b.jpg)

成功打开

![](https://pic1.imgdb.cn/item/677fe871d0e0a243d4f2d261.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-5.md -->
### DNS 请求域名分析

DNS 请求题一般看请求域名就行


![](https://pic1.imgdb.cn/item/677ff285d0e0a243d4f2d387.jpg)

打开流量包先过滤 DNS

因为只有两个 IP，所以直接按源地址排序

看到请求域名是 Zip 的文件头

![](https://pic1.imgdb.cn/item/677ff2a4d0e0a243d4f2d391.jpg)

使用 Tshark 脚本提取出来

```shell
tshark -r capture.pacpng -T fields -Y ip.src=192.168.43.1 -e dns.qry.name
```

![](https://pic1.imgdb.cn/item/67809b5bd0e0a243d4f2ead3.jpg)

还要在过滤下数据，使用 awk 过滤

```
awk 内置函数 match：搜索第一个参数找到与第二个参数匹配的字符串存在第三个参数中

$0 代表当前行

. ：匹配单个任意字符

：出现零次或多次

\ ：转义
```

![](https://pic1.imgdb.cn/item/67809de6d0e0a243d4f2ec21.jpg)

在 WinHex 中创建新文件写入

![](https://pic1.imgdb.cn/item/67809e60d0e0a243d4f2ec57.jpg)

打开拿到 flag

![](https://pic1.imgdb.cn/item/67809e75d0e0a243d4f2ec69.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-6.md -->
### UDP 流量分析


![](https://pic1.imgdb.cn/item/67809ef7d0e0a243d4f2ecb3.jpg)

打开只有三种协议：TLS、TCP、UDP

![](https://pic1.imgdb.cn/item/67809f0fd0e0a243d4f2ecbd.jpg)

TLS 需要密钥才能解出，TCP 一般没东西，所以我们先看 UDP

![](https://pic1.imgdb.cn/item/67809f4ad0e0a243d4f2ecdc.jpg)

第一个数据包右键追踪数据流拿到 flag

![](https://pic1.imgdb.cn/item/67809ff9d0e0a243d4f2ed22.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-7.md -->
### FTP-DATA 分析


![](https://pic1.imgdb.cn/item/67722be8d0e0a243d4ec6d2e.jpg)

打开有 FTP-DATA，优先看 FTP-DATA

![](https://pic1.imgdb.cn/item/6780a094d0e0a243d4f2ed4b.jpg)

追踪流提取转存图片（原始数据）

![](https://pic1.imgdb.cn/item/6780a0e4d0e0a243d4f2ed5c.jpg)

成功拿到图片

![](https://pic1.imgdb.cn/item/6780a0fad0e0a243d4f2ed63.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\5-8.md -->
### SQL 时间盲注分析

SQL 时间盲注原理：

**黑客构造一个使用延时函数的 SQL 查询，延时函数的触发条件与数据库中的数据进行比较**

**如果比较为真，延时函数执行，查询执行时间变长**

**如果比较为假，延时函数不执行，查询执行时间较短**


![](https://pic1.imgdb.cn/item/6780a2dcd0e0a243d4f2ee00.jpg)

打开流量包有 HTTP 则先过滤 HTTP

![](https://pic1.imgdb.cn/item/6780a2fad0e0a243d4f2ee09.jpg)

随机复制一个请求 URL 去 URL 解码

![](https://pic1.imgdb.cn/item/6780a318d0e0a243d4f2ee11.jpg)

知道了延时是 1s，我们就要过滤出大于 1s 的请求

```shell
tshark -r 40…….pacpng -Tfields -e http.resopnse_for.uri -Y 'http.response and http.time > 1' > queries.txt
```

![](https://pic1.imgdb.cn/item/6780a34cd0e0a243d4f2ee1d.jpg)

将请求全部 URL 解码，然后将图中比较的十进制数转 ASCII 拼接就是 flag

![](https://pic1.imgdb.cn/item/6780a363d0e0a243d4f2ee29.jpg)


<!-- Imported from D:\\Book\\Misc\\Chapter5\README.md -->
## 总结

很多题目都是考了不同或者多方向的知识点，总之，学得越多越好