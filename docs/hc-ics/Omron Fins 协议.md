---
comments: true

---

# Omron Fins 协议

## 概述

欧姆龙（Omron）的通信协议体系是其工业自动化生态系统的核心，它并非单一协议，而是一套为不同层级和应用场景设计的多层次协议家族

这些协议共同构建了一个从设备级、控制级到信息级的无缝通信网络，使得PLC、上位机、传感器、执行器等设备能够高效协同工作

FINS（Factory Interface Network Service）是欧姆龙（Omron）为其工业自动化网络设计的核心指令/响应系统

它的核心优势在于能够实现以太网、控制网络和串行通信等多种物理网络间的无缝通信

## 协议类型

FINS 协议主要在 TCP/IP 模型的应用层工作，并有两种主要实现方式：

- FINS/UDP：基于 UDP 协议，是一种无连接的通信方式，通信前不需要建立连接，速度更快，适合实时性要求高的数据交换

- FINS/TCP：基于 TCP 协议，是一种面向连接的通信方式，需要先建立会话，提供更可靠的通信，适合大数据量或对可靠性要求高的传输

两种方式默认都使用 端口 9600 进行通信

## FINS/TCP 会话建立

当使用FINS/TCP时，通信双方在传输数据前需要建立一个会话

- 连接请求：客户端向服务器的9600端口发起TCP连接，并发送一个连接请求帧

- 确认响应：服务器收到请求后，会回复一个连接确认帧，其中包含其自身的节点参数

- 数据传输：会话建立成功后，双方即可开始进行FINS命令和数据的交换

## FINS 报文结构

一个 FINS 报文主要由报头（Header） 和数据（Data） 两大部分构成

其结构会因底层传输协议（UDP 或 TCP）的不同而有所差异

### FINS/UDP 报文结构

FINS/UDP 的报文结构最为基础，由 FINS/UDP 报头和命令数据组成

FINS/UDP 报头长度为 12 个字节，包含以下关键字段

好的，这是您要求的 Markdown 格式表格：

| 字段 (Field) | 长度 (字节) | 描述 (Description) |
| :--- | :--- | :--- |
| **ICF** | 1 | 信息控制字段。包含是否使用网关、是命令还是响应等信息 |
| **RSV** | 1 | 保留字段，通常为 `0x00` |
| **GCT** | 1 | 网关计数字段。表示数据包经过的网关/桥接数量 |
| **DNA** | 1 | 目标网络地址。`0x00` 代表本地网络 |
| **DA1** | 1 | 目标节点地址。目标 PLC 的节点号 |
| **DA2** | 1 | 目标单元地址。`0x00` 代表 CPU 单元 |
| **SNA** | 1 | 源网络地址 |
| **SA1** | 1 | 源节点地址 |
| **SA2** | 1 | 源单元地址 |
| **SID** | 1 | 服务 ID。用于标识不同的通信进程 |
| **Command Code** | 2 | 命令码。标识具体的操作，如读取、写入等 |

### FINS/TCP 报文结构

FINS/TCP 的报文是在 FINS/UDP 报文的基础上，增加了一个 FINS/TCP 报头

- FINS/TCP 报头：长度固定，用于 TCP 层面的连接管理和数据传输控制。其结构通常包含协议 ID、数据长度等信息

- FINS/UDP 报文：作为 FINS/TCP 报头后面的数据负载（Payload）存在

## 功能码

FINS 协议通过不同的命令码来实现对 PLC 的各种操作。命令码是两个字节的十六进制数

以下是您需要的 Markdown 表格：

| 功能分类 | 命令码 (Hex) | 命令名称 (Name) | 功能描述 (Description) |
| :--- | :--- | :--- | :--- |
| I/O内存访问 | 01 01 | MEMORY AREA READ | 读取连续I/O内存区域的数据 |
| I/O内存访问 | 01 02 | MEMORY AREA WRITE | 向连续I/O内存区域写入数据 |
| I/O内存访问 | 01 03 | MEMORY AREA FILL | 用相同数据填充指定范围的I/O内存 |
| I/O内存访问 | 01 04 | MULTIPLE MEMORY AREA READ | 在一个命令中读取多个不连续的I/O内存区域 |
| I/O内存访问 | 01 05 | MEMORY AREA TRANSFER | 将数据从一个I/O内存区域复制到另一个 |
| 参数区访问 | 02 01 | PARAMETER AREA READ | 读取PLC参数区域 |
| 参数区访问 | 02 02 | PARAMETER AREA WRITE | 写入PLC参数区域 |
| 参数区访问 | 02 03 | PARAMETER AREA FILL (CLEAR) | 填充或清除参数区域 |
| 程序区访问 | 03 06 | PROGRAM AREA READ | 读取用户内存（UM）区域的程序数据 |
| 程序区访问 | 03 07 | PROGRAM AREA WRITE | 写入用户内存（UM）区域的程序数据 |
| 程序区访问 | 03 08 | PROGRAM AREA CLEAR | 清除用户内存（UM）区域的程序数据 |
| 运行模式控制 | 04 01 | RUN | 将CPU单元的运行模式切换为RUN或MONITOR |
| 运行模式控制 | 04 02 | STOP | 将CPU单元的运行模式切换为PROGRAM（停止） |
| 状态/数据读取 | 05 01 | CPU UNIT DATA READ | 读取CPU单元数据（如型号等） |
| 状态/数据读取 | 06 01 | CPU UNIT STATUS READ | 读取CPU单元的运行状态 |
| 状态/数据读取 | 06 20 | CYCLE TIME READ | 读取CPU的循环时间（最大、最小、平均） |
| 时钟访问 | 07 01 | CLOCK READ | 读取PLC的内部时钟 |
| 时钟访问 | 07 02 | CLOCK WRITE | 写入/修改PLC的内部时钟 |
| 访问权限 | 0C 01 | ACCESS RIGHT ACQUIRE | 获取访问权限（如果未被其他设备占用） |
| 访问权限 | 0C 02 | ACCESS RIGHT FORCED ACQUIRE | 强制获取访问权限（即使被其他设备占用） |
| 访问权限 | 0C 03 | ACCESS RIGHT RELEASE | 释放已获取的访问权限 |
| 错误日志 | 21 01 | ERROR LOG READ | 读取CPU单元的错误日志 |
| 错误日志 | 21 02 | ERROR LOG CLEAR | 清除错误日志 |
| 错误日志 | 21 03 | ERROR CLEAR | 清除错误或错误信息 |

## 实战案例

### Omron Fins

![](https://pic1.imgdb.cn/item/6a33a36991b65c4475ab6c19.png)

过滤 `omron` 协议，可以看到操作中有读取有写入

![](https://pic1.imgdb.cn/item/6a33ad4991b65c4475abab15.png)

根据题目描述找写入的流量，其 `Command Data` 就是 flag

![](https://pic1.imgdb.cn/item/6a33ad7d91b65c4475abab2b.png)