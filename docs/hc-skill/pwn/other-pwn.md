---
comments: true
---

# 其他类型PWN

> PWN · 知识域。IO_FILE/FSOP、侧信道、Shellcode 工程、Blind、提权、解释器等专题。标签:**IO_FILE利用**、**侧信道攻击**、**Shellcode编写**、**Blind-PWN**、**提权利用**、**解释器PWN**。

## 触发特征

- glibc 2.34+(无 `__free_hook`)堆题、orw/seccomp 题、无回显服务、"自定义语言/解释器"题。

## IO_FILE利用(FSOP)

- 背景:`_IO_2_1_stdout_` 等结构体 + vtable 调用链。
- **stdout 劫持**:伪造 FILE 结构借 `_IO_wfile_overflow`/`_IO_str_jumps` → 泄露或直接 setcontext(全版本通用的 2.34+ 主路径)。
- 2.24+ vtable 校验绕过:合法 jumps 段内转移(HITCON 2017);fastbin stdout 两段劫持破 Full RELRO(ASIS CTF 2017);stdin `_IO_buf_base` null 字节改写(Tokyo Westerns 2017)。
- **setcontext 系**:`setcontext+61`(rdi 指向可控块)寄存器全家桶加载;SUID 变体(Midnight Flag 2026)。
- **exit handlers**:2.34+ 走 `__run_exit_handlers`/TLS destructor(`__call_tls_dtors`)/atexit PTR_MANGLE 逆转(0x00CTF 2017 任意读配合)。
- **leakless libc**:多 fgets stdout FILE 覆写(Midnightflag 2026);TLS 段泄露后 destructor 接力。
- FSOP + seccomp:openat/mmap/write orw 链(EHAX 2026)。

## 侧信道攻击

- 时间:逐字符恢复(RC3 CTF 2016)、连接超时位(hxp 2018)、比较轮数。
- 计数:Intel Pin 指令计数侧信道(Hackover CTF 2015);信号触发次数 strace 统计(PlaidCTF 2017)。
- 内存:设计好的页错误/timing;fork 服务 canary 逐字节爆。
- 盲 SQLi 经脚本引擎超时(35C3 2018,跨域参考)。

## Shellcode编写

- 工程化:`shellcraft.sh()/cat_flag()`;pwntools `asm()`。
- 约束对抗:坏字符(编码/寄存器变换)、长度(分阶段、syscall 复用)、字符集(字母数字/x86 解码器)、架构(x86/ARM/Thumb/RISC-V,→ [异构PWN](arch-pwn.md))。
- orw 通用模板:open("flag") → read → write;openat2 绕新 seccomp(→ 栈页 RETF/x32)。
- 游戏化变体:Game of Life 静物演化 shellcode(DEF CON Quals 2016)、IEEE 754 双精度当 shellcode(Kaspersky 2018)、Game Genie 6 字符补丁码(BSIDSSF 2019)。

## Blind-PWN

- 无二进制只给服务:全靠"注入-观察"。
- 栈迁移盲打、GOT 覆盖试探;格式串盲写:逐字节 `%n` 写 shellcode 加载器,无回显时以"进程是否退出/是否回显后续输入"为 oracle。
- 泄露栈内容:fmt `%p` 序列 + 语义解析(找 libc 指纹、环境变量)。
- dump 二进制:盲 fmt 读 GOT→ 逐地址 `%s` 还原 ELF 常见段。

## 提权利用

- SUID 程序漏洞 → root;`modprobe_path`/`core_pattern` 覆写(内核侧)。
- 环境继承:FD 未加 `O_CLOEXEC` 泄漏高权限描述符(BSIDSSF 2026);提权路径绕过(→ [渗透测试-后渗透](../pen/post-exploitation.md))。
- Linux 栈提权组合:SUID + 溢出。

## 解释器PWN

- 自定义 VM/字节码解释器:指令调度越界、栈机深度不检查、寄存器索引 OOB。
- 解释器逃逸族:CPU 模拟器 print opcode 的 Python eval 注入(Midnight Sun CTF 2018);Unicorn sysenter/冷门 syscall 绕黑名单(Meepwn CTF Quals 2018);自定义 VM swap 指针自覆写(HITCON 2018);Lua 游戏逻辑整数下流(ASIS CTF Finals 2017);Ruby TracePoint 沙箱逃逸(HITCON 2017)。
- bf/JIT 类:Brainfuck JIT 括号不平衡 → RWX shellcode(VuwCTF 2025);GC null-ref 级联损坏(DiceCTF 2026);io_uring UAF SQE 注入(ApoorvCTF 2026)。
- 沙箱逃逸(Sandbox Escape)与 VM Escape 的通用判定:沙箱边界 = 哪些 syscall/能力被过滤;逃逸 = 找过滤器未覆盖的语义等价路径(→ [栈漏洞利用](stack-exploit.md) RETF/x32、[渗透测试](../pen/index.md))。
- **Browser PWN**:V8/SpiderMonkey 引擎漏洞(CVE 样本复刻)→ JIT 编译器类型混淆、Array slice 越界(WebKit CVE-2016-4622,Codegate 2019);V8 Math.random 可预测(XorShift128+,→ [Crypto-MT19937](../crypto/mt19937.md));Electron 渲染进程 RCE 面(→ [WEB-XSS](../web/xss.md) Electron 节)。需要引擎调试环境(d8/gdb + debug symbols),CTF 出现于高阶场。
- Python/marshal 沙箱 → [Misc](../misc/index.md) pyjail。

## 工具速查

```bash
seccomp-tools dump ./pwn          # 看 seccomp 规则
one_gadget ./libc.so.6            # og 约束
# FSOP 工具:house-of-apple 模板 / fsop.py 生成器
```

## 转向

- seccomp 对抗细节 → [栈漏洞利用](stack-exploit.md);内核侧 → [Linux内核漏洞利用](kernel-exploit.md)
