---
comments: true
---

# 低级语言分析

> REVERSE · 知识域。汇编级分析:各 ISA 的阅读与调试。标签:**Intel汇编语言分析**、**ARM汇编语言分析**、**MIPS汇编语言分析**、**SMALI语言分析**、**MSIL语言分析**、**Python字节码分析**。

## 触发特征

- 反编译失败/不可用(混淆、 exotic 架构),只能读汇编。
- 字节码层题目:.pyc、APK smali、.NET IL。

## Intel汇编语言分析

- x86/x64 要点:调用约定(cdecl/x64 快速调用 rdi rsi)、栈帧(rbp 链)、CFA;
- **x86-64 坑**:符号扩展(movsxd)、指令编码重叠、`cdqe` 竞态符号溢出(Codegate 2017)。
- SSE/AVX 向量比较(pcmpeqb 批量比对)、`psadbw` 约束求解(CSAW 2017 MBR 题)。
- 混合模式(x64 调 x86 段)stager 识别。

## ARM汇编语言分析

- ARM/Thumb 双态:PC 低位、`bx`/`blx` 切换;条件执行(32 位 ARM IT 块)。
- AArch64:寄存器 x0-x30,无栈返回地址(lr),`ldp/stp` 帧操作(→ [Pwn-异构PWN](../pwn/arch-pwn.md) 调用约定表)。

## MIPS汇编语言分析

- 延迟槽;$gp/$t9 约定;分支 Likely 指令;MIPS64 Cavium OCTEON CP2 硬件加密指令(SEC-T CTF 2017)。

## SMALI语言分析

- APK 的 Dalvik 字节码:apktool 反编译资源 + baksmali;寄存器 v/p 命名。
- 常用:改 `const-string`、`invoke-*` 打日志、smali 注入绕 LocalBroadcastManager(TAMUctf 2019);RegisterNatives 混淆定位(HTB WonderSMS)。
- 重打包签名:apksigner;运行时 DEX patch 经 /proc/self/maps(Google CTF 2017)。

## MSIL语言分析

- .NET IL:ilspy/dnSpy 反编译为主,IL 级看混淆后逻辑;`box/unbox`、泛型实例化。
- C# 逆向通常 dnSpy 直改 IL/重编译(→ [高级语言逆向](high-level-lang.md))。
- Unity IL2CPP:Il2CppDumper 恢复元数据(SECCON 2018);Assembly-CSharp.dll 运行时 patch。

## Python字节码分析

- `dis.dis()` 读 CPython 字节码;常量抽取(`co_consts`)、栈机语义。
- XOR 分位校验模式:索引拆开的异或比较(常见 crackme);操作码重映射(opcode remap)识别与恢复。
- 版本敏感:字节码随 Python 版本变,`xdis`/`decompyle3`/`pycdc` 按版本选;VuwCTF 2025 版本特化题。
- Pyarmor 加壳(→ [Python程序逆向](python-reverse.md))。

## 工具速查

```bash
objdump -d -M intel ./chall
python -m dis pyc文件 / pycdc
apktool d app.apk
ilspycmd ./file.dll
```

## 转向

- 汇编里有反调试 → [动态调试对抗](anti-debug.md);识别出高级语言特征 → [高级语言逆向](high-level-lang.md)
