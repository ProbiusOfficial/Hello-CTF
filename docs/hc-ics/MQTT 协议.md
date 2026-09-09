---
comments: true

---

# MQTT 协议

## 概述

MQTT（Message Queuing Telemetry Transport）是一种基于发布/订阅模式的轻量级通信协议，专为低带宽、不可靠网络下的物联网设备设计

## 报文结构

每个 MQTT 报文由三部分构成：固定报头（所有报文必含）、可变报头（部分报文）、有效载荷（部分报文）

### 固定报头

字节 1：高 4 位为 MQTT 控制报文类型，低 4 位为标志位（特定位有含义，如 PUBLISH 的 DUP/QoS/RETAIN）

剩余长度（Remaining Length）：从字节 2 开始，用 变长编码（每字节低 7 位为值，最高位为继续位），表示可变报头 + 有效载荷的总字节数

在 Wireshark 中，固定报头被解析为

```
MQ Telemetry Transport Protocol, ...
    Header Flags: 0x... (类型和标志)
    Msg Len: 剩余长度数值
```

### 可变报头

内容根据报文类型不同，如 CONNECT 包含协议名、协议等级、连接标志、保活时间；PUBLISH 包含 Topic Name 和可能的 Packet Identifier

### 有效载荷

内容亦因类型而异，如 CONNECT 有 Client ID、Will Topic/Message、Username、Password；PUBLISH 有实际消息内容

## 报文类型


### CONNECT 报文（连接请求）


固定报头类型 = 1（0x10），标志全0，Wireshark 显示 Connect Command


可变报头（Wireshark 逐字段显示）：


- `Protocol Name Length: 4`


- `Protocol Name: MQTT` （v3.1.1 固定为 "MQTT"，旧版是 "MQIsdp"）


- `Protocol Level: 4` （3.1.1 为 4，5.0 为 5）


- `Connect Flags: 0x..` 展开可看到：`User Name Flag`、`Password Flag`、`Will Retain`、`Will QoS`、`Will Flag`、`Clean Session`


- `Keep Alive: 60` （秒）


有效载荷：


- `Client ID Length: ...`、`Client ID: my_client`


- 如果 Will Flag 为 1，则出现 `Will Topic` 和 `Will Message`


- 如果 User Name Flag 为 1，出现 `User Name`


- 如果 Password Flag 为 1，出现 `Password`


### CONNACK 报文（连接确认）


固定报头类型 = 2（0x20）


可变报头：`Connect Acknowledge Flags`（如 Session Present）、`Return Code`（0 表示连接成功，其余为失败原因）


无有效载荷


### PUBLISH 报文（发布消息）


固定报头类型 = 3（0x30），低 4 位标志携带着 DUP、QoS Level、RETAIN


可变报头：


- Topic Length（2字节） + Topic（主题名）


- 若 QoS > 0，则紧跟 Packet Identifier（2字节）


有效载荷：


- 应用消息内容（二进制/文本）


### PUBACK 报文（发布确认 - QoS 1 应答）


固定报头类型 = 4（0x40），剩余长度 = 2


可变报头：仅包含报文标识符（2字节），与确认的 PUBLISH 中的标识符相同


无有效载荷


### PUBREC 报文（发布收到 - QoS 2 第一步应答）


固定报头类型 = 5（0x50），剩余长度 = 2


可变报头：报文标识符（2字节）


无有效载荷


### PUBREL 报文（发布释放 - QoS 2 第二步）


固定报头类型 = 6（0x62），标志位固定为 0010（必须）


可变报头：报文标识符（2字节）


无有效载荷


### PUBCOMP 报文（发布完成 - QoS 2 第三步）


固定报头类型 = 7（0x70），剩余长度 = 2


可变报头：报文标识符（2字节）


无有效载荷


### SUBSCRIBE 报文（订阅请求）


固定报头类型 = 8（0x82），标志位固定为 0010


可变报头：`Packet Identifier`（2字节）


有效载荷：可包含多个 `Topic Filter`（长度+字符串）+ `Requested QoS`（1字节）对


### SUBACK 报文（订阅确认）


固定报头类型 = 9（0x90）


可变报头：与对应 SUBSCRIBE 相同的 `Packet Identifier`


有效载荷：每个订阅的授予 QoS 列表（每个 1 字节，低 2 位有效）


### UNSUBSCRIBE 报文（取消订阅请求）


固定报头类型 = 10（0xA2），标志位固定为 0010


可变报头：`Packet Identifier`（2字节）


有效载荷：一个或多个要取消的 `Topic Filter`（长度+字符串）


### UNSUBACK 报文（取消订阅确认）


固定报头类型 = 11（0xB0），剩余长度 = 2


可变报头：与 UNSUBSCRIBE 相同的 `Packet Identifier`


无有效载荷


### PINGREQ 报文（心跳请求）


固定报头类型 = 12（0xC0），剩余长度 = 0


只有固定报头，报文仅两个字节：`0xC0 0x00`


### PINGRESP 报文（心跳响应）


固定报头类型 = 13（0xD0），剩余长度 = 0


只有固定报头，报文仅两个字节：`0xD0 0x00`


### DISCONNECT 报文（断开连接）


固定报头类型 = 14（0xE0），剩余长度 = 0


只有固定报头，报文仅两个字节：`0xE0 0x00`


### AUTH 报文（认证交换 - 仅 MQTT 5.0）


固定报头类型 = 15（0xF0）


可变报头：认证方法（UTF-8 字符串）、认证数据（二进制）、可能包含原因码和属性（Properties）


有效载荷：视认证机制而定，通常在属性中携带

## 实战案例

### 工业物联网智能网关数据分析（MQTT 协议 + PNG 宽高篡改 + LSB 隐写）

![](https://pic1.imgdb.cn/item/6a36f8412830ce602a50ee62.png)

先分析 MQTT PUBLISH 消息，过滤语法

```
mqtt.hdrflags == 0x30
```

可以看到这些关键字的长度有明显异常

```
f : ZIP 十六进制数据开头，payload 以 504B0304 开始
l : ZIP 中间碎片
a : ZIP 中间碎片
g : ZIP 十六进制数据结尾
d : ZIP 密码 pass_1s_ea4y
```

![](https://pic1.imgdb.cn/item/6a36ff212830ce602a50eefd.png)

拼接 `f + l + a + g` 的 ZIP 数据得到压缩包

再用 `d` 的解压密码解压缩出图片

修改宽高拿到 `flag{21png_` 上半部分

剩下的一半需要 LSB 隐写提取出来然后拼接再反转颜色即可，如图所示

![](https://pic1.imgdb.cn/item/6a36ffe32830ce602a51136e.png)
