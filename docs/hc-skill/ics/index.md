---
comments: true
---

# ICS - 工控安全

> 方向技能索引。目标为 PLC、SCADA、DCS、工业协议(Modbus/S7/DNP3/OPC UA)、工控组态软件时从本索引路由。工控类 CTF(强网杯工控赛道、"信创杯"、ICS 三大件)以协议分析与控制逻辑篡改为核心。

## 知识域路由表

| 知识域 | 触发特征 |
| --- | --- |
| [信息搜集](info-gathering.md) | 设备/拓扑/协议识别 |
| [网络通信](network.md) | 工业协议流量与中间人 |
| [设备漏洞](device-vuln.md) | 固件、默认口令、设备后门 |
| [逻辑漏洞](logic-vuln.md) | PLC 程序/组态/控制逻辑篡改 |
| [物理安全](physical.md) | 硬件接口、旁路攻击 |
| [补丁管理](patch-mgmt.md) | 补丁缺失与回退 |
| [安全监控](monitoring.md) | 工控入侵检测与日志 |
| [安全策略](security-policy.md) | 分段、访问控制策略 |
| [供应链安全](supply-chain.md) | 组件与供应链投毒 |
| [恶意代码分析](malware.md) | 工控恶意样本(震网族) |

## 环境基线

```bash
nmap --script modbus-discover -p 502 <ip>     # Modbus 发现
# 协议分析:Wireshark 自带 Modbus/S7/DNP3/IEC104 解析
# PLC 仿真:OpenPLC、Snap7、pymodbus;组态:OpenPCS、CODESYS(仿真节点)
# 工具:SCADAShutdownPack、PLCscan、isfs(西门子)
```
