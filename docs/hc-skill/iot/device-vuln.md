---
comments: true
---

# 设备漏洞

> IOT · 知识域。设备侧漏洞利用。标签:**默认密码利用**、**硬编码密码**、**命令注入**、**缓冲区溢出**、**权限提升**、**未授权访问**。

## 触发特征

- 已拿到设备服务面/固件,要求实际利用拿 shell 或数据。

## 默认密码利用

- 默认凭证字典:admin/admin、admin/password、厂商默认表(设备型号 → 官方默认);test/cisco/linksys 系历史默认库。
- 弱口令 telnet/ssh/web(→ [WEB-暴力破解](../web/brute-force.md)); Mirai 字典即 IoT 弱口令事实标准。

## 硬编码密码

- 固件里找:`strings`/`grep -r "password"`(→ [固件分析](firmware.md) 逆向);后门账号(魔法用户名触发)。
- 云对接密钥:设备-云通信密钥硬编码 → 伪造设备入网。

## 命令注入

- 高发点:Web 管理接口(ping/traceroute/diagnostic 功能)、UPnP、wifi 配置(SSID 参数拼 shell)。
- nvram 变量注入:`nvram_get` 值参与 `system()`(路由器漏洞经典模式)。
- 过滤绕过:`;` 被滤用 `$( )`/反引号/换行;空格用 `${IFS}`(→ [WEB](../web/index.md) 注入技巧通用)。
- 验证:telnetd 反弹(`telnetd -l /bin/sh`)、busybox 环境适配(精简命令集)。

## 缓冲区溢出

- 目标:管理接口 httpd/upnpd 的长参数、长 SSID/主机名、认证前可达的溢出(未授权 RCE)。
- 架构:MIPS/ARM 栈溢出(→ [Pwn-异构PWN](../pwn/arch-pwn.md) 调用约定);NX 常关闭(老设备)→ shellcode 直注。
- qemu-user 本地复现 + 真机验证;大端 MIPS 的 gadget 搜索。
- 漏洞挖掘:静态(IDA 找 `strcpy/sprintf/system` 交叉引用)→ fuzz(boofuzz 对协议;AFL 对文件解析)。

## 权限提升

- 服务以 root 跑(IoT 常态)→ 拿 shell 即 root;受限 shell(none/ash 限定)→ busybox 快捷方式滥用、`/etc/passwd` 可写(→ [渗透测试-后渗透](../pen/post-exploitation.md))。
- SUID/ capabilities 在固件内的滥用;启动脚本(rcS)注入持久化。

## 未授权访问

- 管理接口无鉴权(静态 token/空鉴权逻辑);API 路径未保护(/api/config 直读)。
- RTSP/ONVIF/UPnP 未授权(→ [网络安全](network.md));调试接口暴露(串口 telnetd、ssh authorized_keys 残留)。

## 转向

- 溢出利用细节 → [Pwn](../pwn/index.md);设备持久化后内网横向 → [渗透测试](../pen/index.md)
