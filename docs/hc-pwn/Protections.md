---
comments: true

---

# 常见保护

做 Pwn 这件事，最怕的不是“题太难”，而是“方向选错”。

通过分析题目程序开启了哪些保护机制可以了解本题考察的知识点。

> [!INFO]
> 先看保护，再定打法。
> 拿到 ELF 的第一件事应该是 `checksec ./pwn`。

## 开题先看这几条

```bash
file ./pwn
checksec --file=./pwn
readelf -h ./pwn | grep Type
```

- `file`：确认架构（`i386` / `amd64`）和是否动态链接
- `checksec`：快速看主流保护开关
- `readelf`：辅助判断 PIE（`DYN` 常见于 PIE 程序）

## checksec 的输出分析

`checksec` 里最值得优先看的字段通常是这几个：

- `Canary found`：栈溢出要先考虑 canary 泄漏
- `NX enabled`：默认放弃栈上直接执行 shellcode
- `PIE enabled`：程序基址随机，优先找代码地址泄漏
- `RELRO: Full`：GOT 基本不可改，别执着老式 GOT 劫持
- `FORTIFY`：字符串/内存类函数有额外检查，低级错更难打穿

## 为什么要先看保护

同一个漏洞，在不同保护组合下，题目几乎会变成两道题：

- 没保护：可能直接 `ret2text` 或 `ret2shellcode`
- 保护较全：通常先信息泄漏，算出基址后再构造 ROP 链

可以把保护机制看成题目的指路牌，为本题大致标注出方向与思路。

## NX（No-eXecute）

### 是什么

NX 表示不可执行，原理是将数据所在的内存页标识为不可执行。

在linux中，程序载入到内存后，会将程序的`text`节标记为可执行 `.bss` `.data` 为不可执行。堆栈等均不可知性，修改GOT表的方法便不再可行，但是代码重用攻击ret2libc依旧可行。

### 硬件基础

NX 依赖于 CPU 的页表（Page Table）权限控制：

| 组件           | 作用                                                |
| ------------ | ------------------------------------------------- |
| **页表项（PTE）** | 存储内存页的访问权限位                                       |
| **NX Bit**   | x86\_64 中称为 **XD (eXecute Disable)** 位，位于页表项的第63位 |
| **AP\[2:0]** | ARM 架构中的访问权限位，包含 XN (eXecute Never) 位             |

> Linux 实现
> // 内核中设置页保护
>// mprotect() 系统调用底层实现
>pte_t pte = pte_modify(old_pte, newprot);
>// 设置 _PAGE_NX 位标记不可执行

### 思路

- `NX disabled`：可考虑 `ret2shellcode`
- `NX enabled`：优先考虑 `ROP` / `ret2libc` / `syscall` 链

### GCC 编译选项

``` bash
gcc -z noexecstack    # 标记栈不可执行（默认通常已启用）
gcc -z execstack      # 允许栈执行
```
## Canary（栈保护）

### 是什么

stack canaries取名自地下煤矿的金丝雀，能比矿工更快发现煤气泄露，有预警的作用。这个概念应用在栈保护上则是在初始化一个栈帧时在栈底设置一个随机的canary值 ，栈帧销毁前测试该值是否“死掉”，即是否被改变，若被改变则说明栈溢出发生，程序走另一个流程结束，以免漏洞利用成功。

Canary 是函数返回前的栈完整性校验。你一旦覆盖到返回地址附近，通常会先触发 canary 检查，程序直接异常退出。

### 类型

>主要为terminator, random, random XOR 三类

 - Terminator 是一种栈保护机制，通过在缓冲区中插入特定的"终结符"字符（通常是 0x00 空字节或换行符 \n）来防止字符串操作函数溢出。

``` C
// 在缓冲区边界放置终结符
char buffer[64];
memset(buffer, 0, sizeof(buffer));  // 填充空字节作为 terminator
// 或者
buffer[63] = '\0';  // 确保字符串以 null 结尾
```

- Random  是一种内存布局随机化技术，使程序的栈、堆、库等基地址在每次运行时随机变化。程序初始化的时候会随机生成canary，保存在安全的地方。

-  Random XOR（随机异或 ） 比 random 多了一层 XOR 异或操作
  
``` C
void function() {
    uintptr_t *frame = __builtin_frame_address(0);  // 获取栈帧地址
    uintptr_t xor_canary = __stack_chk_guard ^ (frame[0]);  // 与返回地址异或
    
    // 存储在栈上
    uintptr_t saved_canary = xor_canary;

    // 检查
    if ((saved_canary ^ frame[0]) != __stack_chk_guard) {
        __stack_chk_fail();  // 触发失败
    }
}
```

### 值得留意

Canary 防的是“无脑覆盖返回地址”，不是把栈利用彻底封死。

> [!INFO]
>在 64 位 Linux 下，canary 的最低字节常见为 `\x00`，这会影响你对泄漏字符串的解析方式，也会影响某些“拼接输入”的策略。

## PIE 与 ASLR

### PIE 是什么

PIE 会让程序代码段基址随机化。函数绝对地址不再固定，每次运行都可能不同。

### ASLR 是什么

ASLR 会随机化栈、堆、`libc` 等地址布局，防止你写死地址一把梭。

Linux 里你会经常看到这个开关：

```bash
cat /proc/sys/kernel/randomize_va_space
```

- `0`：关闭随机化
- `1`：部分随机化
- `2`：完全随机化（常见默认值）

### 思路

PIE 位置无关可执行文件，其在编译器上实现，通过将程序编译为位置无关代码PIC，使程序加载到任意位置，就像是一个特殊的共享库。PIE会一定程度上影响性能。


> [!INFO]
    习惯 `base + offset` 的思路，不要迷信固定地址。

## RELRO

RELRO 主要影响 GOT 表是否可写，常见三种状态：

1. `No RELRO`
2. `Partial RELRO`
3. `Full RELRO`

### 思路

- `No/Partial RELRO`：部分场景还能走 GOT 覆写路线
- `Full RELRO`：GOT 只读，很多“改 GOT 劫持流程”的老套路失效

## FORTIFY_SOURCE

FORTIFY 是一类编译期/运行期强化检查，常见在字符串、内存拷贝相关函数上。其本质是对gcc与glibc的patch。

通过检查危险函数并替换，在不损失大量性能的前提下可以提升程序安全性

## 常用编译参数

```bash
# 关闭 canary
-fno-stack-protector

# 开启不同强度 canary
-fstack-protector
-fstack-protector-strong
-fstack-protector-all

# 控制 PIE
-no-pie
-fpie -pie

# 控制 NX（GNU_STACK）
-z execstack
-z noexecstack

# 控制 RELRO
-Wl,-z,norelro
-Wl,-z,relro
-Wl,-z,relro,-z,now

# FORTIFY（一般配合优化）
-D_FORTIFY_SOURCE=2 -O2
```

## 保护组合 -> 对应思路

| 保护组合（常见） | 第一反应 | 常见路线 |
| --- | --- | --- |
| `No Canary + No PIE + NX off` | 直接控流 | `ret2text` / `ret2shellcode` |
| `No Canary + No PIE + NX on` | 直接 ROP | `ret2libc` / `syscall` |
| `Canary + PIE + NX on` | 先 leak | 泄漏 canary + 基址后再 ROP |
| `Full RELRO` | 放弃 GOT 覆写 | 改走 ROP / 堆利用 / FSOP 等 |
| `seccomp` 存在 | 先看 syscall 白名单 | 转 `orw` 路线 |

## 新题到手，应该做甚

1. 先确认漏洞点和可控范围（仅溢出？可控返回地址？有无泄漏）
2. 看 canary，决定是否必须先做信息泄漏
3. 看 PIE/ASLR，决定是否必须先拿程序或 libc 基址
4. 看 NX，决定走 shellcode 还是 ROP
5. 看 RELRO/seccomp，排除不可能路线

## 一个简短例子

假设 `checksec` 输出如下：

```text
RELRO:    Full RELRO
Canary:   Canary found
NX:       NX enabled
PIE:      PIE enabled
FORTIFY:  Enabled
```

那么初始思路通常会是：

1. 先找信息泄漏点（至少 leak canary 和一个代码/`libc` 地址）
2. 根据泄漏值反推基址
3. 构造 ROP（`system("/bin/sh")` 或 `orw`）
4. 放弃 GOT 覆写类打法

## 对应阅读

- 栈基础 [栈上数组越界&栈溢出](./Stack_Overflow.md)
- ROP 基础 [ROP入门](./ROP.md)
- 常见利用套路 [常见的ROP技巧](./ROP_Tricks.md)

## 小结

保护机制不是来劝退你的，它是在提示你“这题该怎么打”。

越早养成“先看保护再动手”的习惯，后面排错会轻松很多，做题也会稳很多。


