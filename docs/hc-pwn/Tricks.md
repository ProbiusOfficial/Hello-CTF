---
comments: true

---

# 杂七杂八的解题技巧

如果你经常遇到这种情况：

- 理论好像懂了
- 一开调试就乱
- 本地能过远程就挂

那不妨来看看

## 开题先做四件事

### 1. 信息收集走一遍

```bash
file ./pwn
checksec --file=./pwn
strings -a ./pwn | head
ldd ./pwn
cat /proc/sys/kernel/randomize_va_space
```

### 2. 先跑程序，记录交互

至少记录：

1. 有几次输入机会
2. 每次可输入的大致长度
3. 是否有回显
4. 程序崩溃发生在第几轮交互

### 3. 明确“你到底能控什么”

别看到溢出就默认“我能控 RIP”。先判断是：

- 只能改局部变量
- 能改函数指针
- 能改返回地址
- 还是只有信息泄漏

这一步会直接决定你后面是走劫持流程、栈迁移，还是先做泄漏。

### 4. 保护状态要交叉验证

不建议一条命令就下结论，试试交叉看：

```bash
# GNU_STACK 是否可执行（辅助判断 NX）
readelf -W -l ./pwn | grep GNU_STACK

# 是否存在 canary 相关符号
readelf -s ./pwn | grep __stack_chk_fail

# 观察 RELRO 段
readelf -W -l ./pwn | grep GNU_RELRO
```

有助于更快识别“题目环境/二进制和我想的不一样”的诱因。

## 找偏移：别手算

```python
from pwn import *

pattern = cyclic(400)
# 把 pattern 喂给程序，崩溃后取 RIP/返回地址对应的值
print(cyclic_find(0x6161616c))
```

> [!Warning] "一个小坑"
    64 位环境里最常见翻车点是“4 字节和 8 字节宽度混用”。

## 调试时值得留意的四个点

1. `RSP/ESP` 当前位置
2. 返回地址是否已被正确覆盖
3. 参数寄存器是否满足调用约定（如 `rdi/rsi/rdx`）
4. 泄漏值是否可信（是否被截断、是否带换行）


## 写 exp 的结构化习惯

建议把脚本拆成可单测的几段，不要一把梭到底：

1. 连接与环境初始化
2. Stage1：泄漏
3. Stage2：利用
4. 日志与异常处理

示例骨架：

```python
from pwn import *

context.binary = elf = ELF('./pwn')


def start():
    if args.REMOTE:
        return remote('host', 31337)
    return process(elf.path)


def leak(io):
    # 构造第一阶段 payload，拿 canary/libc/base
    return {
        'canary': 0,
        'libc_base': 0,
    }


def pwn(io, info):
    # 构造第二阶段 payload
    pass


io = start()
info = leak(io)
log.success(f"canary = {hex(info['canary'])}")
log.success(f"libc   = {hex(info['libc_base'])}")
pwn(io, info)
io.interactive()
```

## 一些编译器参数

在刷题时，经常要手搓二进制对比保护差异，一些机制参数

```bash
# Canary
-fno-stack-protector
-fstack-protector-strong

# PIE
-no-pie
-fpie -pie

# NX
-z execstack
-z noexecstack

# RELRO
-Wl,-z,norelro
-Wl,-z,relro
-Wl,-z,relro,-z,now
```


## 本地通远程挂的排查项

1. 本地 `libc/ld` 和远程不一致
2. `recvuntil` 边界写错，导致泄漏值截断
3. 交互节奏不一致（远程多了 banner 或提示）
4. 超时（`alarm`）没处理
5. 栈对齐问题（`ret` 补对齐）

> [INFO]
> 如果地址都能 leak 出来但仍不稳定，先查交互边界和解析逻辑，很多时候不是平台问题。

## 卡住时的排障项

1. 偏移对不对
2. 地址对不对
3. 交互边界对不对
4. 寄存器和栈对齐对不对
5. 远程依赖（`libc` / `ld`）对不对

> 先排低成本错误，避免刚卡住就陷入深坑。


## 对应阅读

- 栈基础： [栈上数组越界&栈溢出](./Stack_Overflow.md)
- ROP 入门： [ROP入门](./ROP.md)
- ROP 进阶： [常见的ROP技巧](./ROP_Tricks.md)

## 小结

技巧是为了减少弯路，不是为了跳过原理。



