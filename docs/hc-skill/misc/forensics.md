---
comments: true
---

# 取证

> MISC · 知识域。磁盘/内存/文件系统取证。标签:**磁盘镜像**、**Bitlocker**、**AD1磁盘取证**、**VMDK磁盘取证**、**加密磁盘取证**、**内存镜像**。

## 触发特征

- 给 .E01/.AD1/.raw/.vmdk/.mem/.dmp 镜像求"谁干了什么"或恢复文件。

## 磁盘镜像

- 挂载与分析:Autopsy/F TK Imager(Windows)、`mount -o loop`(Linux raw);E01 用 ewfmount。
- 文件系统工具集(Sleuth Kit):`fls`(列文件含删除)、`icat`(按 inode 恢复);FAT16 删除文件恢复(MetaCTF Flash 2026)、FAT16 空闲空间数据(BSIDSSF 2026)、FAT 镜像里恢复被删 .git(Square CTF 2017)、ext2 孤儿 inode(fsck)、XFS 元数据重建(BSIDSSF 2025)、BTRFS 子卷快照(BSIDSSF 2026)、ZFS(Nullcon 2026)、APFS 快照恢复历史文件(srdnlenCTF 2026)、RAID 5 XOR 恢复(Crypto-Cat)、GPT 分区 GUID 数据编码(VuwCTF 2025)、删除分区恢复。
- **NTFS 专题**:MFT($MFT 解析:mftparser)、ADS 备用流、USN Journal($J)、回收站($Recycle.Bin)、Bitlocker(FVEK 从内存提 → dislocker)。
- KAPE 分诊镜像(UTCTF 2026);反 carved:NULL 字节交错反雕刻(BSIDSSF 2024)。
- Windows 伪影:OEMInformation 后门、hosts 藏数据、`.contact` 文件、SAM 账户创建时间线、Defender MPLog、certutil base64 ZIP 内存恢复(SEC-T CTF 2017)、cipher.exe 擦除伪影(Security Fest CTF 2018)。
- 云与容器:云存储取证(S3/GCP/Azure)、Docker 容器取证(镜像层 diff,Pragyan 2026)、Android 取证。

## Bitlocker / 加密磁盘

- FVEK 提取:内存镜像里找(aeskeyfind)→ dislocker/bitlocker2john 挂载。
- TrueCrypt/VeraCrypt 卷挂载(GreHack CTF 2016);密钥藏在内存/注册表/题目其他文件。
- LUKS 主密钥内存恢复(Hack.lu 2015);PRNG 时间种子暴力恢复加密密钥(CSAW 2015)。

## AD1磁盘取证

- FTK Imager 的 AD1 逻辑镜像:FTK/ewf 工具解包;内容即文件树 → 常规文件取证。

## VMDK磁盘取证

- 虚拟磁盘:`qemu-nbd`/vmware-mount 挂载;sparse 解析(0xFun 2026);VMware 快照(vmsn/vmem)差异取证(内存快照并入)。
- OVA 解包 → vmdk+ovf;快照时间线。

## 内存镜像

- **Volatility 2/3**:进程列表(pstree)、网络(netscan)、命令行(cmdline)、注册表(printkey/hashdump)、凭据(mimikatz 插件)、剪贴板(clipboard,OtterCTF 2018)、malfind(注入检测)、mftparser(删除文件,BSides Delhi 2018)。
- 字符串雕刻:memory dump 直接 strings + 上下文(Pragyan 2026);恶意软件提取 + XOR 解密(VuwCTF 2025);勒索密钥内存恢复(MetaCTF 2026)。
- 视觉分析:GIMP 打开 raw 内存当原始图(INShAck 2018);Minidump 字符串雕刻(0xFun 2026)、Minidump ISO 9660 恢复(srdnlenCTF 2026)。
- GIMP raw 打开内存找图;TLS master key 提取(→ [WEB流量分析](web-traffic.md));AES key 搜索(aeskeyfind)。
- Python 内存源码恢复(pyrasite,Insomni'hack 2017)。
- SQLite 编辑历史从 diff 表重建(Google CTF 2017);Kyoto Cabinet 哈希库取证(ASIS CTF 2018)。

## 平台与介质专项取证

- **macOS 内存取证**:格式相对统一但生态工具少——内存里 `strings` + Volatility 3 的 mac 插件族(pslist/bash);Keychain 导出破解(chainbreaker);APFS 快照恢复历史文件(srdnlenCTF 2026);HFS+ 资源叉藏二进制(CONFidence CTF 2017)。
- **U盘取证(USB 存储介质)**:注册表 `USBSTOR` 枚举插入历史(设备型号/序列号/首次插入时间)、`setupapi.dev.log` 的设备安装时间线、`MountedDevices` 盘符分配;取出 U 盘本体 → 删除文件恢复(Sleuth Kit)+ 分区表异常检查;Windows 事件 20001/20003(驱动安装)交叉验证。
- **数据库取证**:SQLite(浏览器/APP 常用)——主文件 + `journal/WAL` 恢复已删数据、`freelist` 页 carving、编辑历史从 diff 表重建(Google CTF 2017);MySQL:ibd 文件页级解析(innodb_unicode 工具族)、binlog 重放还原变更;序列类型字节解析(RITSEC 2018)。
- **浏览器取证**:Chrome/Edge——`History`(SQLite:URL/下载/时间戳 epoch 1607 基准)、`Cookies`(加密值 + DPAPI 解密)、`Login Data`(AES-GCM 密钥在 Local State,经 DPAPI)、`Cache` 目录 carving;Firefox——`places.sqlite`、`logins.json` + `key4.db` 解密;时间线拼接 = 用户行为还原。
- **安全事件分析**:取证向的事件定位入口——先时间锚(告警/已知恶意文件时间)→ 该时间窗内的进程创建/网络连接/文件落盘/注册表改动 → 三视图(→ [应急响应](../ir/index.md))对齐;取证输出(IOC + 时间线 + 影响面)是最终交付物。

## 工具速查

```bash
vol -f mem.raw windows.pstree     # Volatility3
mftparser / fls -r disk.img / icat disk.img 34
binwalk -Me mem.raw; strings -el mem.raw | grep -i flag
qemu-nbd --connect=/dev/nbd0 x.vmdk; mount /dev/nbd0p1 /mnt
```

## 转向

- 内存里的 C2/beacon → [WEB流量分析](web-traffic.md)/[恶意代码分析](../ics/malware.md);完整事件还原 → [应急响应](../ir/index.md)
