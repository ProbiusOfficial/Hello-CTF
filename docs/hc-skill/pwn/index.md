---
comments: true
---

# PWN - 二进制安全

> 方向技能索引。目标为原生二进制内存破坏、解释器/VM 漏洞、内核漏洞时从本索引路由。不要用于:纯静态逆向找 key(转 [Reverse](../reverse/index.md))、HTTP 应用漏洞(转 [WEB](../web/index.md))。

## 知识域路由表

| 知识域 | 触发特征 |
| --- | --- |
| [内存破坏漏洞](memory-corruption.md) | 溢出/越界/未初始化类基础 bug |
| [栈漏洞利用](stack-exploit.md) | 栈溢出 + ret2xxx / ROP / SROP |
| [堆漏洞利用](heap-exploit.md) | 菜单堆题、glibc 分配器、House of X |
| [格式化字符串](format-string.md) | printf 用户可控格式串 |
| [IO_FILE利用](other-pwn.md) | FSOP、stdout 劫持(glibc 2.34+ 主流) |
| [逻辑漏洞](logic-vuln.md) | 条件竞争/类型混淆/鉴权/整数语义 |
| [Linux内核漏洞利用](kernel-exploit.md) | 题目给 boot 镜像/initramfs |
| [异构PWN](arch-pwn.md) | ARM/MIPS/RISC-V/m68k 等非 x86 |

## 环境基线

```bash
pip install pwntools; apt install gdb
git clone https://github.com/pwndbg/pwndbg && cd pwndbg && ./setup.sh   # 或 gef / pwn-dbg
patchelf --set-interpreter /lib64/ld-2.31.so --set-rpath . ./pwn        # 本地 libc 对齐
one_gadget libc.so.6; ROPgadget --binary ./pwn; seccomp-tools dump ./pwn
checksec ./pwn    # 第一步永远是 checksec
```

## 通用解题流程

1. `checksec`:看 NX/PIE/Canary/RELRO/fortify 决定技术树。
2. 试运行 + 读反编译:找输入点(数组、菜单、printf、read)。
3. 判定漏洞类:溢出/格式串/UAF/整数 → 进对应知识域。
4. 确认 libc 版本(字符串、`__libc_start_main` 偏移、libc-database)。
5. 写 exploit:先本地打通 → 迁移远端(地址偏移、libc、缓冲对齐)。

## 常见保护与对策

| 保护 | 对策 |
| --- | --- |
| NX | ROP / ret2libc / shellcode 写入后 mprotect |
| PIE | 泄露代码段地址;PIE 低 12 位不变(同页单字节改) |
| Canary | 泄露 canary(格式串/ fork 逐字节爆)或绕过(覆盖 LSB) |
| Full RELRO | 改 `__free_hook`(glibc<2.34)/ FSOP / exit handlers / ret2dl-resolve(部分 RELRO) |
| seccomp | orw(read-open-write)/ openat2 / RETF 降架构 / x32 ABI 别名 |
