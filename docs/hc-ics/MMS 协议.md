---
comments: true

---

# MMS 协议

## 概述

MMS 提供了一套面向对象的客户端/服务器通信模型，核心功能包括：

- 读/写变量：读取或修改设备内部的数据点（如温度、电压、开关状态）

- 报告：设备在数据变化或事件触发时主动向客户端推送信息

- 文件操作：上传/下载设备上的配置文件或固件

- 控制：启停设备、执行预定义程序等。

- 设备建模：通过虚拟制造设备（VMD）和域（Domain）等抽象概念，统一不同厂家的设备数据接口

最常见的应用场景是 电力系统 IEC 61850 通信（变电站自动化），以及制造业的 SCADA 系统、机器人控制等

## 报文结构

MMS 协议的 PDU 完全使用 ASN.1 基本编码规则（BER） 来描述，也就是 Tag - Length - Value 结构

### BER 快速回顾

- Tag（标签）：1~多字节，说明数据类型及上下文

- Length（长度）：1~多字节，指明后续 Value 的字节数

- Value（内容）：可以是简单整数、字符串，也可以是嵌套的 TLV 结构

MMS 中几乎都用上下文特定的构造标签（如 0xA0、0xA1 等）

### 顶层的 MMS PDU 类型

MMS 顶层 PDU 使用 ASN.1 BER 编码中的 Context-specific 标签。
对于 `[0]`～`[13]` 这类低编号标签，其顶层 BER Tag 可直接对应为
`A0`～`AD`。

| PDU 类型                  | ASN.1 标签 | BER 顶层标签 | 说明 |
|---------------------------|-----------:|-------------:|------|
| confirmed-RequestPDU      | [0]  | A0 | 确认请求，需要对端响应 |
| confirmed-ResponsePDU     | [1]  | A1 | 对确认请求的正常响应 |
| confirmed-ErrorPDU        | [2]  | A2 | 对确认请求返回的错误 |
| unconfirmed-PDU           | [3]  | A3 | 无确认报文，如 InformationReport |
| rejectPDU                 | [4]  | A4 | 拒绝某个 MMS PDU |
| cancel-RequestPDU         | [5]  | A5 | 取消请求 |
| cancel-ResponsePDU        | [6]  | A6 | 取消响应 |
| cancel-ErrorPDU           | [7]  | A7 | 取消操作错误 |
| initiate-RequestPDU       | [8]  | A8 | MMS 会话初始化请求 |
| initiate-ResponsePDU      | [9]  | A9 | MMS 会话初始化响应 |
| initiate-ErrorPDU         | [10] | AA | 初始化过程错误 |
| conclude-RequestPDU       | [11] | AB | 请求结束 MMS 会话 |
| conclude-ResponsePDU      | [12] | AC | 对结束会话请求的响应 |
| conclude-ErrorPDU         | [13] | AD | 结束会话过程错误 |

## 实战案例

### 窃取数据的黑客

![](https://pic1.imgdb.cn/item/6a3678eb2830ce602a4e8adb.png)

查看会话可以看到一直在跟 `192.168.51.34:102` 通信

所以 `192.168.51.34` 就是服务器

![](https://pic1.imgdb.cn/item/6a367fe12830ce602a4e8cda.png)

按照长度排列，第 3096 包没有 info 信息有点可疑（3022、3059 也一样）

![](https://pic1.imgdb.cn/item/6a3682232830ce602a4ee6b7.png)

展开后可以看到 `flag.7z` 以及 `flag.txt`

![](https://pic1.imgdb.cn/item/6a3682c32830ce602a4ee6e0.png)

按照最先发包顺序，从 3022 之后看攻击者 IP `192.168.51.33` 请求操作

在 3066 包中可以看到访问了 `flag.7z`

![](https://pic1.imgdb.cn/item/6a3683c22830ce602a4ee746.png)

编写脚本去响应中找到这个压缩文件

```python
import struct

pcap = "tmflag(1).pcapng"               # 要解析的 pcapng 文件
data = open(pcap, "rb").read()           # 一次性读取全部二进制内容

endian = "<"                             # 默认小端字节序，后续可根据块类型修正
pos = 0                                  # 当前解析位置（字节偏移）
packets = []                             # 存储提取的原始数据包内容

# 逐块解析 pcapng 文件
while pos + 12 <= len(data):            # 至少需要类型(4) + 块长(4) + 尾部块长(4)
    block_type, block_len = struct.unpack(endian + "II", data[pos:pos+8])
    if block_len < 12 or pos + block_len > len(data):  # 非法块长度则停止解析
        break

    body = data[pos+8:pos+block_len-4]  # 块体，去掉头和尾的块长度字段

    if block_type == 0x0A0D0D0A:        # Section Header Block：决定字节序
        bom = struct.unpack("<I", body[:4])[0]  # 读取字节序标记
        endian = "<" if bom == 0x1A2B3C4D else ">"  # 根据标记设置端序
    elif block_type == 6:               # Enhanced Packet Block
        if len(body) >= 20:
            # 接口ID、时间戳高/低、捕获长度、原始长度（只关注 caplen）
            _, _, _, caplen, _ = struct.unpack(endian + "IIIII", body[:20])
            packets.append(body[20:20+caplen])  # 保存捕获到的数据包

    pos += block_len                     # 移动到下一个块

# 分析提取的以太网数据包
for idx, pkt in enumerate(packets, 1):
    if len(pkt) < 14:
        continue                         # 不够以太网帧头长度，跳过

    eth_type = struct.unpack("!H", pkt[12:14])[0]  # 以太网类型字段
    if eth_type != 0x0800:
        continue                         # 非 IPv4 包则跳过

    ip = pkt[14:]                        # IP 头部起始
    ihl = (ip[0] & 0x0f) * 4            # IP 头长度（字节）
    proto = ip[9]                        # 传输层协议号
    if proto != 6:
        continue                         # 非 TCP 则跳过

    total_len = struct.unpack("!H", ip[2:4])[0]  # IP 总长度
    tcp = ip[ihl:total_len]              # TCP 段（头部+数据）
    sport, dport = struct.unpack("!HH", tcp[:4])  # 源端口、目的端口
    tcp_hlen = (tcp[12] >> 4) * 4        # TCP 头长度（字节）
    payload = tcp[tcp_hlen:]             # TCP 有效载荷（应用层数据）

    # 7z 文件魔数签名
    sig = b"7z\xbc\xaf\x27\x1c"
    off = payload.find(sig)              # 在载荷中查找该签名

    if off != -1:                        # 找到 7z 文件头
        # 提取从签名开始的一段数据（长度 0x8f 字节）
        filedata = payload[off:off + 0x8f]
        open("flag.7z", "wb").write(filedata)  # 写出文件
        print(f"[+] frame {idx}: extracted flag.7z, size={len(filedata)} bytes")
```

![](https://pic1.imgdb.cn/item/6a3684ba2830ce602a4ee77a.png)

解压后拿到 flag 值

![](https://pic1.imgdb.cn/item/6a36851e2830ce602a4ee793.png)
