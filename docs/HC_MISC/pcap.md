---
comments: true

---
## 前言

> 版权声明：
>
> ​	文档源于项目[ProbiusOfficial/CTF-QuickStart: 针对0基础新手编写的CTF快速入门手册 (github.com)](https://github.com/ProbiusOfficial/CTF-QuickStart)
>
> ​	原作者为 GaoNengwWw

流量分析与取证在misc中也是较为常见的题目，流量分析主要是根据元数据（不是通信内容本身）识别对手活动和通信模式，每条记录多达几兆字节的全部活动内容，可能只产生100字节的元数据，如端点（包括ip地址和域名）、端口、收发字节数、连接时长及起止时间，我们将这样一组元数据成为“网络流”（network flows）。

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

#### proctol

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
|     eg      |   ==   |              ip.addr == 1.2.3.4              |
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

下载好习题后，解压，发现有一个txt和pcap文件。打开txt，内如如下。

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

从上到下我们简单分析一下，从上图我们可一看到基本上所有的帧都是由IPv4发送的，那么IPv6就可以不用看了。紧接着，我们发现，存在两个协议，UDP与TCP。TCP比UDP有更多的分组，而且我们可以注意到，有一个TLS和FTP协议。

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

第一个会话是发送了一张base64编码的图片，后面的绘画都是一些html文档。我们先将base64编码转为图片，得到了这样的一幅图片

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

接下类我们，` 右键 Hypertext Transfer Protocol(http) -> 作为过滤器应用 -> 选中`

![Alt text](./images/pcap/Snipaste_2023-10-05_14-37-18.png)

单击`HTTP流`

![Alt text](./images/pcap/Snipaste_2023-10-05_14-37-57.png)

即可得到flag