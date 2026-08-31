---
comments: true
---

# 代码注入

> REVERSE · 知识域。进程注入/Hook 类技术的识别与逆向(红蓝双向知识)。标签:**远程线程注入**、**DLL注入**、**IAT Hook**、**Inline Hook**、**Process Hollowing**、**Message Hook**。

## 触发特征

- 题目样本/程序把代码写进别的进程执行;分析"为什么某函数行为变了"。
- 恶意代码分析场景:注入器 + 载荷两段结构。

## 远程线程注入

- 经典链:`OpenProcess` → `VirtualAllocEx` → `WriteProcessMemory` → `CreateRemoteThread`(LoadLibrary/函数地址)。
- 变体:`NtCreateThreadEx`、**APC注入**(`QueueUserAPC`:把执行函数挂到目标线程 APC 队列,线程可警报时执行;早鸟 Early Bird 变体在进程初始化即注入)、`RtlCreateUserThread`。
- **DLL反射加载(Reflective DLL Injection)**:不落盘、不经 LoadLibrary——DLL 自带 loader 在内存中完成节表映射与重定位;特征:内存中无文件路径对应的映像;dump 后按内存对齐修复(pe-sieve 自动)。
- 逆向:扫 API 导入组合;注入的 shellcode 在 `VirtualAllocEx` 后 dump。
- 父子进程互动:parent patch child 经 `strace process_vm_writev`(Google CTF Quals 2018)→ Linux 侧等价手法。

## DLL注入

- `LoadLibrary` 路径写入目标进程 + 远程线程;注册表 AppInit_DLLs、IFEO 劫持(持久化场景)。
- 逆向:可疑 DLL 的 DllMain 分析;后门共享库检测:字符串 diff(对比正常库,Hack.lu CTF 2012)。
- `.so` 注入(Linux):LD_PRELOAD(→ 绕过向 [动态调试对抗](anti-debug.md) 与分析向双向)。

## IAT Hook

- 改导入地址表项指向 hook 函数(常见在 `LoadLibrary` 后修 IAT)。
- 识别:函数地址落在非模块范围;IAT 项与磁盘 PE 不一致。
- 逆向:对比内存 IAT 与原始导入表;跟踪 hook 蹦床。

## Inline Hook

- 改函数开头字节 jmp 到 hook(蹦床 trampoline 保留原指令)。
- 识别:函数头部异常跳转/热补丁特征;`detours`/`minhook` 特征模式。
- 逆向:恢复原函数字节;hook 链多层时逐层剥。
- LD_PRELOAD memcmp 侧信道(Blaze CTF 2018)、time 冻结(EKOPARTY 2017)都是用户态 hook 思想。

## Process Hollowing(傀儡进程)

- `CreateProcess(挂起)` → `NtUnmapViewOfSection` → 写入恶意映像 → `SetThreadContext`(改入口)→ 恢复执行。
- 识别:进程内存映像与磁盘文件不一致(ghost 进程);`Process Hollowing` 检测对比 PEB 的 ImageBase。
- 变体:Process Doppelgänging(NTFS 事务)、transacted hollowing。
- 逆向:dump 无载体内存映像(pe-sieve/Scylla)再静态分析。

## SSDT Hook(内核层)

- 修改内核 `KeServiceDescriptorTable`(SSDT)系统服务分发表项指向 hook 函数——用户态 API 的"源头"被改。
- 识别:内核模块分析中 sys_call_table 项指向非 nt 模块地址;ARK 工具(Autoruns/PowerTool 类)对照。
- 逆向场景:rootkit 样本分析(→ [恶意代码分析](../ics/malware.md)),先 dump 被 hook 的服务号再追 hook 函数逻辑;x64 下 SSDT 钩子受 PatchGuard 限制,样本多用驱动回调替代。

## 其他代码注入

- 进程镂空以外的内存加载:Hollowing 变体(Process Doppelgänging NTFS 事务、transacted hollowing,见 Process Hollowing 节)。
- Shellcode 注入框架:sRDI/Donut(任意 DLL/exe → PIC shellcode)——样本里见到 Donut 特征头先解包。
- 内核态注入:APC(内核)、IdeaNomad 类;驱动加载点分析。
- 排查清单:谁能写内存(VirtualAllocEx/WriteProcessMemory/NtMapViewOfSection 交叉引用)+ 谁能起执行线程(CreateRemoteThread/APC/Rtl)。

## Message Hook

- `SetWindowsHookEx`(WH_KEYBOARD/WH_MOUSE/WH_CBT)全局钩子劫持消息流。
- 键盘记录器样本分析:回调里找记录/外带逻辑。
- Linux 对等:X11/global keylog;`input_event` keylogger dump 解析(Pwn2Win 2016,取证向)。

## 分析通用流程

1. 判定注入方向:谁注入谁(loaderdll→svchost?)。
2. 定位载荷:内存 dump(shellcode/DLL/EXE)。
3. dump 载荷 → 回到常规静态分析([可执行文件逆向](executable.md))。
4. 还原 C2/配置 → [恶意代码分析](../ics/malware.md)/[应急响应](../ir/index.md) 场景。

## 工具速查

```bash
# Windows: x64dbg + ScyllaHide;pe-sieve /scantime; Process Hacker
# Linux: strace -f; ltrace; /proc/<pid>/maps + mem dump
volatility malfind    # 内存取证找注入(→ Misc-取证)
```

## 转向

- 注入后载荷自保护 → [动态调试对抗](anti-debug.md);内存镜像里的注入 → [Misc-取证](../misc/forensics.md)
