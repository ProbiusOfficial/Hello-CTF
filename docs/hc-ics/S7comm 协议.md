---
comments: true

---

# S7comm 协议

## 概述

S7comm 是西门子专有的工业控制协议，主要用于西门子S7-300/400系列PLC（可编程逻辑控制器）的编程、数据交换和诊断

## 报文结构

一个典型的 S7comm 报文由三部分组成：

- Header (头部)：固定 12 字节，包含协议标识、PDU 类型等关键信息。

- Parameter (参数)：长度可变，包含具体的功能码（如读取、写入）及其参数

- Data (数据)：长度可变，在写入等操作中携带实际数据

## 通信过程

Wireshark 可以清晰捕捉到 S7 通信的建立过程，分为三步：

- TCP 三次握手：客户端通过 TCP 端口 102 与 PLC 建立连接

- COTP 层连接：双方交换 COTP 连接请求和确认报文，协商通信参数

- S7comm 层会话建立：客户端发送功能码为 `0xf0` 的 "建立通信" 请求，双方协商 S7comm 层参数，完成连接

## 核心功能码

| 功能码 | 描述 | 说明 |
| :--- | :--- | :--- |
| **0x00** | CPU 服务 | 用于执行与 CPU 本身相关的系统级功能|
| **0xF0** | 建立通信 | 在数据传输前，用于协商通信参数，如 PDU 大小 |
| **0x04** | 读取变量 | 请求读取 PLC 中一个或多个变量的值 |
| **0x05** | 写入变量 | 请求向 PLC 写入一个或多个变量的值 |
| **0x1A** | 请求下载  | 开始下载程序块或数据块前的请求 |
| **0x1B** | 下载块 | 传输程序块或数据块的实际数据内容 |
| **0x1C** | 下载结束 | 通知 PLC 下载过程已全部完成 |
| **0x1D** | 开始上传 | 开始从 PLC 上传程序块或数据块 |
| **0x1E** | 上传 | 传输从 PLC 上传的数据内容 |
| **0x1F** | 上传结束 | 通知上位机上传过程已全部完成 |
| **0x28** | PLC 控制 | 用于远程控制 PLC 的运行模式，例如启动（Start） |
| **0x29** | 停止 PLC | 远程停止 PLC 的运行 |

## 实战案例

### S7 协议恶意攻击分析（S7comm 协议）

![](https://pic1.imgdb.cn/item/6a33579da6693733f7e20ba4.png)

S7comm（S7 Communication）是西门子专有的工业控制协议，主要功能码如下：

| 功能码 | 描述 | 说明 |
| :--- | :--- | :--- |
| **0x00** | CPU 服务 | 用于执行与 CPU 本身相关的系统级功能|
| **0xF0** | 建立通信 | 在数据传输前，用于协商通信参数，如 PDU 大小 |
| **0x04** | 读取变量 | 请求读取 PLC 中一个或多个变量的值 |
| **0x05** | 写入变量 | 请求向 PLC 写入一个或多个变量的值 |
| **0x1A** | 请求下载  | 开始下载程序块或数据块前的请求 |
| **0x1B** | 下载块 | 传输程序块或数据块的实际数据内容 |
| **0x1C** | 下载结束 | 通知 PLC 下载过程已全部完成 |
| **0x1D** | 开始上传 | 开始从 PLC 上传程序块或数据块 |
| **0x1E** | 上传 | 传输从 PLC 上传的数据内容 |
| **0x1F** | 上传结束 | 通知上位机上传过程已全部完成 |
| **0x28** | PLC 控制 | 用于远程控制 PLC 的运行模式，例如启动（Start） |
| **0x29** | 停止 PLC | 远程停止 PLC 的运行 |

题目说了是 "突然发生停机事件"，所以推测是 `0x29` 或者 `0x28`，直接过滤出来

`P_PROGRAM` 是实现 PLC 模式转换的关键服务。它主要包含两种操作：

- 启动：将 PLC 从停止状态切换至运行状态

- 停止：将 PLC 从运行状态切换至停止状态

![](https://pic1.imgdb.cn/item/6a335e6aa6693733f7e20e73.png)

本题的 flag 是 `flag{3201414d}`

### 上位机通讯异常分析（S7comm 协议）

![](https://pic1.imgdb.cn/item/6a335ee3a6693733f7e20ea6.png)

题目说 "无法查询控制设备异常情况"

观察数据包发现功能码都是 `0x04`，所以判断是因为响应不正常才导致的 "无法查询"

![](https://pic1.imgdb.cn/item/6a3362e1a6693733f7e23913.png)

我们随便一个响应来分析一下结构

![](https://pic1.imgdb.cn/item/6a336422a6693733f7e239a4.png)

📦 1. Header (头部) — 确认响应类型

| 字段 | 值 | 说明 |
| :--- | :--- | :--- |
| Protocol Id | 0x32 | S7 协议固定标识，表明这是 S7comm 报文 |
| ROSCTR | Ack_Data (3) | 表示这是一个数据确认包，即对请求的响应并携带数据 |
| PDU Reference | 52417 | 用于匹配请求与响应的流水号 |
| Parameter length | 2 | 参数部分的长度为 2 字节（仅包含 "Item count"） |
| Data length | 6 | 数据部分的长度为 6 字节（包含 1 个数据项的元信息+实际值） |
| Error class / code | 0x00 / 0x00 | 无错误，表示操作成功 |

📋 2. Parameter (参数) — 确认读取内容

| 字段 | 值 | 说明 |
| :--- | :--- | :--- |
| Function | Read Var (0x04) | 响应的是 "读取变量" 请求 |
| Item count | 1 | 数据部分包含 1个 数据项，与请求中的项数对应 |

💾 3. Data (数据) — 实际读取到的值

| 字段 | 值 | 说明 |
| :--- | :--- | :--- |
| Return code | Success (0xff) | 该项读取成功 |
| Transport size | BYTE/WORD/DWORD (0x04) | 表示数据长度以字节为单位，且 "Length" 字段按字节计数 |
| Length | 2 | 数据长度为 2个字节 |
| Data | 01 00 | 实际读取到的原始值，按大端序存储 |

可以看到 `Return code` 的值决定是否读取成功，成功的话为 `0xff`

我们右键这个值，选择 "准备作为过滤器" --> "选中"

![](https://pic1.imgdb.cn/item/6a338bb791b65c4475ab01af.png)

然后加上 `!` 筛选出没有读取成功的流量包

![](https://pic1.imgdb.cn/item/6a338c3291b65c4475ab0218.png)

其 `data` 内容就是 `flag{010400100100}`

![](https://pic1.imgdb.cn/item/6a338c6091b65c4475ab2cbe.png)

### 工控协议数据分析（S7comm 协议）

![](https://pic1.imgdb.cn/item/6a33af1a91b65c4475abac4f.png)

题目说 "获取到了哪些信息"，过滤协议可以看到全部都是 `0x04` 和 `0x05` 的流量

![](https://pic1.imgdb.cn/item/6a33e3ef91b65c4475ad0a3d.png)

过滤 `s7comm.param.func == 0x05` 可以看到多次写入，每个写入包的 `data` 字段里都有类似内容：

```
01100110
```

![](https://pic1.imgdb.cn/item/6a33e52d91b65c4475ad0a98.png)

提取出来拼接转成 ASCII 码得到 `flag{flag_is_here}

### 异常的 S7 数据（S7comm 协议）

大概看了一下，全是 `0x05` 功能码

![](https://pic1.imgdb.cn/item/6a34018a91b65c4475ada627.png)

绝大多数写入数据都以 `ffff` 开头

![](https://pic1.imgdb.cn/item/6a340e2591b65c4475adf946.png)

右键作为过滤器应用

![](https://pic1.imgdb.cn/item/6a34100c91b65c4475adf96f.png)

WireShark 生成的语法是 `s7comm.resp.data == ff:ff:96:e7:8f:51:c4:d0:3a:2b`

我们更改为 `s7comm.resp.data[0:2] != ff:ff`，筛选出数据包

![](https://pic1.imgdb.cn/item/6a34106e91b65c4475adf978.png)

所以 flag 是 `flag{FFAD28A0CE69DB34751F}`


### 黑客的 Fuzz（S7comm 协议）

![](https://pic1.imgdb.cn/item/6a36f15e2830ce602a50ec82.png)

打开流量包过滤 `s7comm`，全是写入和读取变量

题目说的是 FUZZ，所以重点应该看读取的流量，功能码为 `0x04`

FUZZ 的参数每次请求肯定都是不一样的

最后比对发现就 Address 字段的最后一个字节每次不一样

![](https://pic1.imgdb.cn/item/6a36f3272830ce602a50ed24.png)

编写脚本提取

```python
import struct
import re

# 打开 pcapng 文件并读取全部内容
pcap = "s7.pcapng"
raw = open(pcap, "rb").read()

# 默认使用小端字节序
endian = "<"
# 当前读取偏移
off = 0
# 存放提取出的隐藏数据
hidden = bytearray()

def parse_tcp(pkt):
    """解析以太网帧中的 TCP 报文，返回 (src_ip, dst_ip, src_port, dst_port, payload)"""
    # 以太网帧最小长度 14 字节（目的 MAC + 源 MAC + 类型）
    if len(pkt) < 14:
        return None

    # 以太类型字段（大端）
    eth_type = int.from_bytes(pkt[12:14], "big")
    pos = 14

    # 若存在 802.1Q VLAN 标签（0x8100），再读取内层类型
    if eth_type == 0x8100:
        eth_type = int.from_bytes(pkt[16:18], "big")
        pos = 18

    # 只处理 IPv4（0x0800）
    if eth_type != 0x0800:
        return None

    # IP 头部长度（ihl * 4 字节）
    ihl = (pkt[pos] & 0x0f) * 4
    # IP 协议字段（6 = TCP）
    proto = pkt[pos + 9]

    if proto != 6:
        return None

    # 源 IP 和目标 IP（点分十进制）
    src = ".".join(map(str, pkt[pos + 12:pos + 16]))
    dst = ".".join(map(str, pkt[pos + 16:pos + 20]))

    # TCP 首部起始位置
    tcp = pos + ihl
    # 源端口、目的端口
    sport = int.from_bytes(pkt[tcp:tcp + 2], "big")
    dport = int.from_bytes(pkt[tcp + 2:tcp + 4], "big")
    # TCP 数据偏移（4 位，单位 4 字节）
    doff = (pkt[tcp + 12] >> 4) * 4

    # TCP 有效载荷
    payload = pkt[tcp + doff:]
    return src, dst, sport, dport, payload

# 解析 pcapng 文件：逐块读取
while off + 12 <= len(raw):
    # 块类型和块长度（使用当前字节序）
    block_type, block_len = struct.unpack(endian + "II", raw[off:off + 8])

    # 块长度不合理则退出
    if block_len < 12 or off + block_len > len(raw):
        break

    # 块体（去除头部类型/长度和尾部重复长度）
    body = raw[off + 8:off + block_len - 4]

    # 块类型 0x0A0D0D0A 是 Section Header Block（SHB），用于判断字节序
    if block_type == 0x0A0D0D0A:
        # 魔术数字判断大小端：b"\x4d\x3c\x2b\x1a" 表示小端，否则大端
        endian = "<" if body[:4] == b"\x4d\x3c\x2b\x1a" else ">"

    # 块类型 6 是 Enhanced Packet Block（EPB），包含数据包
    elif block_type == 6:
        if len(body) >= 20:
            # 块选项中的捕获长度（caplen）在固定字段的第三个 int 里
            caplen = struct.unpack(endian + "IIIII", body[:20])[3]
            # 提取数据包字节
            pkt = body[20:20 + caplen]

            # 解析 TCP 报文
            parsed = parse_tcp(pkt)
            if parsed:
                src, dst, sport, dport, payload = parsed

                # 只取攻击者发往 PLC 102 端口的数据
                if dport == 102 and payload.startswith(b"\x03\x00"):
                    # S7Comm Job 包，Read Var 功能，固定长度 31
                    if (
                        len(payload) == 31
                        and payload[7] == 0x32   # 功能码：Read Var
                        and payload[8] == 0x01   # 读取变量数量：1
                        and payload[17] == 0x04  # 数据长度：4 字节
                    ):
                        # 提取最后一个字节（读取到的数据）
                        hidden.append(payload[-1])

    # 移动到下一个块
    off += block_len

# 将隐藏数据写入文件
open("hidden", "wb").write(hidden)

# 打印恢复信息
print("hidden length:", len(hidden))
print("file header:", hidden[:10].hex())

# 搜索 flag 并输出
flags = re.findall(rb"flag\{[^}]+\}", hidden)
for f in flags:
    print(f.decode())
```

最后得到 flag：`flag{50f84daf3a6dfd6a9f20c9f8ef428942}`

### 被篡改的数据（S7comm 协议）

![](https://pic1.imgdb.cn/item/6a36f5672830ce602a50ee0a.png)

"被大量修改的数据" 对应的写入内容，也就是功能码 `0x05`

```python
import struct
import socket
import re

# 读取 pcapng 文件
pcap = "/mnt/data/s702(1).pcapng"
data = open(pcap, "rb").read()

# -------- 解析 pcapng 块 --------
packets = []
off = 0
endian = "<"  # 默认小端

while off + 12 <= len(data):
    # 块类型和块总长度（含固定尾）
    block_type, block_len = struct.unpack(endian + "II", data[off:off+8])
    if block_len < 12 or off + block_len > len(data):
        break

    body = data[off+8:off+block_len-4]  # 排除尾部的块总长度字段

    # Section Header Block (SHB)
    if block_type == 0x0A0D0D0A:
        # 字节序标记：0x1A2B3C4D 表示大端
        endian = ">" if body[:4] == b"\x1a\x2b\x3c\x4d" else "<"

    # Enhanced Packet Block (EPB)
    elif block_type == 0x00000006 and len(body) >= 20:
        # 接口ID、时间戳高低位、捕获长度、原始长度
        iface, ts_high, ts_low, cap_len, orig_len = struct.unpack(
            endian + "IIIII", body[:20]
        )
        # 提取实际捕获的报文数据
        packets.append(body[20:20+cap_len])

    off += block_len


def get_tcp_payload(pkt):
    """从原始以太网帧中提取 TCP 载荷及四元组"""
    if len(pkt) < 54:  # 最小长度：以太网14 + IP20 + TCP20
        return None

    # 以太网类型必须为 IPv4 (0x0800)
    if pkt[12:14] != b"\x08\x00":
        return None

    # IP 协议字段必须为 TCP (6)
    if pkt[23] != 6:
        return None

    # IP 头长度（IHL）及偏移
    ihl = (pkt[14] & 0x0F) * 4
    ip_start = 14
    tcp_start = ip_start + ihl

    # 源IP、目的IP
    src = socket.inet_ntoa(pkt[ip_start+12:ip_start+16])
    dst = socket.inet_ntoa(pkt[ip_start+16:ip_start+20])

    tcp = pkt[tcp_start:]
    if len(tcp) < 20:
        return None

    # 源端口、目的端口
    sport, dport = struct.unpack("!HH", tcp[:4])
    # TCP 数据偏移
    data_offset = (tcp[12] >> 4) * 4
    payload = tcp[data_offset:]

    return src, sport, dst, dport, payload


def parse_s7_write_values(payload):
    """从 TCP 载荷中提取 S7 写变量操作的写入值（每次写1字节）"""
    values = []
    off = 0

    while off + 4 <= len(payload):
        # TPKT 头部：版本 0x03，保留 0x00，总长度
        if payload[off:off+2] != b"\x03\x00":
            break

        tpkt_len = int.from_bytes(payload[off+2:off+4], "big")
        tpkt = payload[off:off+tpkt_len]

        # COTP 数据 TPDU：DT Data (0x0f) 且最后字节 0x80 表示数据
        if len(tpkt) >= 17 and tpkt[4:7] == b"\x02\xf0\x80":
            s7 = tpkt[7:]

            # S7 协议标识 (0x32)
            if len(s7) >= 10 and s7[0] == 0x32:
                rosctr = s7[1]  # 报文类型

                # 0x01 = Job（请求）
                if rosctr == 0x01:
                    # 参数长度、数据长度
                    param_len = int.from_bytes(s7[6:8], "big")
                    data_len = int.from_bytes(s7[8:10], "big")

                    param = s7[10:10+param_len]
                    d = s7[10+param_len:10+param_len+data_len]

                    # 功能码 0x05 = 写变量
                    if param and param[0] == 0x05:
                        # 本题每次写入 1 字节，S7 写数据前 4 字节为：
                        # 保留/传输大小/位长度
                        if len(d) >= 5:
                            values.append(d[4:5])  # 提取写入值

        off += tpkt_len

    return values


# 累积所有写入值，拼接成字节序列
seq = b""

for pkt in packets:
    item = get_tcp_payload(pkt)
    if not item:
        continue

    src, sport, dst, dport, payload = item

    # 只看上位机 (192.168.88.2) 发给 PLC (192.168.88.23) 端口 102 的 S7 写入
    if src == "192.168.88.2" and dst == "192.168.88.23" and dport == 102:
        for v in parse_s7_write_values(payload):
            seq += v

print("extracted length:", len(seq))

# 在累积的序列中搜索 flag{...} 模式
m = re.search(rb"flag\{[^}]+\}", seq)
if m:
    print(m.group().decode())
else:
    print("not found")
```

得到 `flag{931377ad4a}`