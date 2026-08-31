---
comments: true
---

# 动态调试对抗

> REVERSE · 知识域。反调试/反虚拟机/反插桩的识别与绕过。标签:**基于内存标志检测**、**基于API检测**、**基于进程跟踪检测**、**基于TLS**、**基于时间差检测**、**基于调试器特征检测**。

## 触发特征

- 直接跑正常,一挂调试器就退出/变慢/分支翻转。

## 基于内存标志检测

- **PEB**(Windows):`BeingDebugged`(+0x02)、`NtGlobalFlag`(+0xBC)、ProcessHeap 的 `Flags/ForceFlags`。
- 绕过:调试器插件(ScyllaHide 全家桶)、运行时 patch PEB 字节、直接 nop 检查。
- Linux:`/proc/self/status` 的 TracerPid(h1702ctf 2017 Android 版同源);`/proc/*/cmdline`、`/proc/*/maps` 扫描。

## 基于API检测

- `IsDebuggerPresent`、`CheckRemoteDebuggerPresent`、`NtQueryInformationProcess`(ProcessDebugPort/ProcessDebugObjectHandle/ProcessDebugFlags)。
- `OutputDebugString` 错误码检测;`FindWindow` 找 OllyDbg/x64dbg 窗口类名。
- 绕过:API hook(返回假值)、ScyllaHide、补丁函数体 `xor eax,eax; ret`。
- Linux:ptrace 自锁(`ptrace(PTRACE_TRACEME)` 失败即被调试)→ 双进程 nanomites(→ [代码注入](code-injection.md))。

## 基于进程跟踪检测

- 进程树检查(父进程非 explorer);进程名黑名单(常见调试器/分析工具)。
- 反插桩:Frida 检测(端口 27042、内存 "frida" 字符串、线程 gum-js-loop)、Pin/DynamoRIO 特征。
- 绕过:Frida 改名/重编译 gadget;分析工具重命名。
- 窗口/前台焦点检测(GetForegroundWindow 周期校验)。

## 基于TLS

- **TLS 回调**(Thread Local Storage Callback):在 main 之前执行检查/解密;IDA:视图→SEH/TLS 目录。
- 绕过:patch 回调表、调试器设置断在 tls_callback_0。
- Windows 驱动/服务常叠加以错开分析者注意力(→ [异常处理](exception-handling.md))。

## 基于时间差检测

- `rdtsc` 差值、`QueryPerformanceCounter`、`GetTickCount`:单步导致时间异常。
- 绕过:hook 时间函数返回固定值;ScyllaHide 的 time 加速;`LD_PRELOAD time()` 冻结(EKOPARTY 2017);unicorn 模拟时指令计数补偿。
- 时间锁定:二进制带日期 key,过期拒跑(Hack.lu 2017)——反向:改系统时间/patch 校验。

## 基于调试器特征检测

- 断点检测:INT3 扫描(代码段 hash 比对/直接扫 0xCC)、硬件断点寄存器(Dr0-Dr3)。
- 单步检测:pushfq 检查陷阱标志(TF);trap-flag 自检 + cmovz 补丁器(Hack.lu 2018)。
- 异常法:INT3/SEH 被调试器吃掉则回调不触发(→ [异常处理](exception-handling.md))。
- 代码完整性:self-hashing(运行时校验自身 CRC)→ patch 前先 patch 校验函数。
- 信号类:SIGILL 切换执行模式(Hack.lu 2015)、SIGFPE handler mprotect 代码变异(Hack.lu 2018)、fork+pipe 死分支(RCTF 2017)。

## 反VM/反沙箱

- CPUID hypervisor 位;MAC 地址前缀;CPU 核数/内存/磁盘大小阈值。
- 注册表/文件痕迹(VMware Tools、VBoxService);用户交互检测(鼠标移动、对话框)。
- 绕过:改硬件指纹、补丁检查分支、真机分析。

## 综合绕过清单(通用优先级)

1. 通用插件先行:ScyllaHide(x64dbg/IDA)、gdb 反反调试脚本。
2. 定位检测点:崩溃/退出点回溯;条件断点 + 日志。
3. patch 语义:改检测函数返回值/跳转。
4. 换执行环境:unicorn/Qiling 模拟(天然无调试器痕迹)。

## 工具速查

```bash
# Windows: ScyllaHide + x64dbg;sharpod
# Linux: gdb -ex 'set follow-fork-mode child'
# Android: Frida 反 anti-debug 脚本(TracerPid/su 检测,h1702ctf 2017)
```

## 转向

- 检测点藏在异常流 → [异常处理](exception-handling.md);多进程保护 → [代码注入](code-injection.md)
