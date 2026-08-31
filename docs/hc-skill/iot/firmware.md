---
comments: true
---

# 固件分析

> IOT · 知识域。固件全生命周期分析。标签:**固件提取**、**固件解包**、**固件逆向**、**固件补丁分析**、**固件签名验证**、**固件解密**。

## 触发特征

- 给 .bin/.img/.trx/.squashfs 固件;或要求从硬件/OTA 拿固件。

## 固件提取

- 软件层:OTA 升级包截获(→ [信息搜集](info-gathering.md));厂商官网。
- 硬件层:Flash 芯片离线读取(CH341A + SOP8 夹);在线 dump:UART shell 后 `dd if=/dev/mtd0`;SPI/I2C 总线在线嗅探。
- 引导层:U-Boot 命令行(串口打断)→ `md/cp` 内存 dump、tftp 导出。

## 固件解包

- `binwalk -Me`(识别 uImage/squashfs/cramfs/jffs2 并递归解);`firmware-mod-kit`/`unblob`。
- 文件系统挂载:squashfs(unsquashfs,注意 magic 偏移)、jffs2(jffs2dump,需端序处理)、cramfs。
- 头部格式:uImage(64 字节头)、TRX、加密头(→ 固件解密)。
- 嵌套:解出内含另一个完整固件(matryoshka)。

## 固件逆向

- 架构识别:`file` busybox → ARM/MIPS(大端常见于路由器);qemu-user 模拟跑二进制。
- 目标定位:busybox 配置 → httpd/telnetd/upnpd 等服务二进制 → IDA(→ [Reverse](../reverse/index.md) 流程)。
- 常见发现点:硬编码凭证(nvram 默认值)、后门接口(魔法字符串比较)、nvram 变量拼命令(→ [设备漏洞](device-vuln.md))。
- ESP32/Xtensa ROM symbol map 逆向(Insomni'hack 2017);RTOS(FreeRTOS/RT-Thread)镜像分析:符号表恢复 + 任务/队列结构。
- MBR/裸机镜像:QEMU+GDB 全系统调试(Square CTF 2017);Z80(Game Boy)等异构(→ [Pwn-异构PWN](../pwn/arch-pwn.md))。

## 固件补丁分析

- 版本 diff:新旧固件二进制对比(BinDiff/Diaphora;文件系统级 diff)定位修补点 → 反推漏洞(1-day 复现)。
- 补丁绕过:patch 校验函数(→ [Reverse-程序补丁](../reverse/basic-analysis.md))后回打包。

## 固件签名验证

- 校验逻辑分析:U-Boot/主程序的镜像校验(RSA/MD5 头)→ 找校验绕过(改 magic、降级攻击:签名链允许旧版本)。
- 重打包:修改文件系统后重算校验/绕过签名 → 刷回验证(FMK;注意 size/offset 字段同步)。

## 固件解密

- 识别:binwalk 无效、熵分析高(加密/压缩)→ 厂商私有加密。
- 常见:头部明文 key、XOR 常量、AES key 硬编码在下载器/主程序里(先逆向升级程序)。
- 从设备内提取解密后镜像(省去逆向解密):串口/Flash 直读。

## 转向

- 解包出的服务二进制漏洞 → [设备漏洞](device-vuln.md);汇编细节 → [Reverse-低级语言分析](../reverse/low-level-lang.md)
