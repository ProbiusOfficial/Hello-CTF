---
comments: true
---

# 可执行文件逆向

> REVERSE · 知识域。按文件格式分域的逆向。标签:**DOS文件逆向**、**PE文件逆向**、**ELF文件逆向**、**APK逆向**、**其他可执行文件逆向**。

## 触发特征

- 拿到不认识的二进制;`file` 输出决定本页路由。

## DOS文件逆向

- MZ 头 + 16 位实模式;DOSBox/debug 反汇编;int 0x21 系统调用表。
- COM 文件(无头纯代码);MBR 引导扇区(16 位,CSAW 2017 psadbw 约束求解;QEMU+GDB 调 bootloader,Square CTF 2017)。
- DOS stub 伪装分析(PE 头前区域的隐藏逻辑)。

## PE文件逆向

- 结构:DOS 头 → NT 头 → 节表;导入表(IAT/INT)、导出表、重定位、TLS、资源、调试目录。
- 工具:PE-bear/CFF Explorer 结构查看;x64dbg/IDA 加载;` pestudio` 静态画像。
- 附加数据(overlay):签名后附加的 payload(binwalk 分离)。
- XOR 位图提取 + OCR(srdnlenCTF 2026);`RtlCaptureContext` 确定性栈泄露(Insomnihack 2017,pwn 联动)。
- 相关对抗:壳(→ [静态分析对抗](anti-static.md))、反调试(→ [动态调试对抗](anti-debug.md))。

## ELF文件逆向

- 结构:ELF header → Program headers → Sections;PLT/GOT、`.init/.fini_array`、动态符号。
- **节表损坏对抗**:ELF section header 破坏抗分析(BSIDSSF 2026)——IDA 手动建段或按 program header 读。
- 静态/动态链接判断;stripped 二进制符号恢复(runtime 符号、字符特征)。
- 自定义 binfmt 内核模块加载的 RC4 平坦二进制(BSIDSSF 2026);hash-resolved imports 无导入表勒索样本(BSIDSSF 2026)。
- `/proc/self/mem` 写原语、`LD_PRELOAD` dump 只执行段(BackdoorCTF 2017)。
- ASAN shadow 内存利用(pwn 联动);WebKit Array.slice OOB CVE-2016-4622(Codegate 2019)。

## APK逆向

- 流程:apktool(资源+smali)/ jadx(java)/ JEB(混合)→ Manifest 定组件与入口 → 找校验点。
- 关键位置:MainActivity、native 库(`lib/*.so` → JNI)、assets(加密资源)、证书(签名 SHA-256 作 AES key,ASIS Finals 2018)。
- Flutter(Dart AOT)→ Blutter;鸿蒙 HAP/ABC → abc-decompiler;Unity IL2CPP → Il2CppDumper。
- 运行时 patch:DEX 字节码经 /proc/self/maps(Google CTF 2017);smali 注入(TAMUctf 2019);native .so 换工程绕过(Codegate CTF 2018)。
- 详见 [Android程序逆向](android-reverse.md)。

## 其他可执行文件逆向

- **Mach-O**(macOS/iOS):dyld、ObjC/Swift 运行时、代码签名与 entitlements。
- **WASM**:wabt(wasm2wat/wasm2c)、wasmer 运行;线性内存操作(misc 联动)。
- **UEFI**:UEFITool 解析、GUID 定位模块。
- **固件**:binwalk 提取 → [IoT-固件分析](../iot/firmware.md)。
- **游戏引擎**:Unity/Unreal/Godot 资产与脚本;Roblox place 文件。
- **内核模块**:.ko/.sys → 驱动逆向(→ [Linux内核漏洞利用](../pwn/kernel-exploit.md) 环境)。
- **macOS/iOS 差异**:Mach-O 结构、dyld 共享缓存提取。

## 工具速查

```bash
file ./chall; binwalk ./firmware
upx -d ./packed; objdump -f ./chall
wasm2wat ./chall.wasm -o out.wat
```

## 转向

- 有壳/加密区段 → [静态分析对抗](anti-static.md);APK 深入 → [Android程序逆向](android-reverse.md)
