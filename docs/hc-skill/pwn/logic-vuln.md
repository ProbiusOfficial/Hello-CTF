---
comments: true
---

# 逻辑漏洞

> PWN · 知识域。非内存错误类二进制缺陷:语义/时序/类型层面。标签:**条件竞争**、**类型混淆**、**鉴权绕过**、**命令注入**、**信息泄露**。

## 触发特征

- 程序无明显溢出但有"菜单流程""权限判断""多线程"。
- 数值语义可疑:符号、截断、精度、顺序。

## 条件竞争

- fork/线程服务:TOCTOU 窗口(check 与 use 之间改状态)。
- 双线程/双连接同时操作同一资源:余额、次数、标识位。
- 信号竞争:SIGFPE/SIGSEGV handler 改执行流(→ [Reverse](../reverse/index.md) 信号向导);线程竞态符号溢出 `cdqe` 符号扩展(Codegate 2017)。
- kernel 场景 userfaultfd/MADV_DONE 扩窗 → [Linux内核漏洞利用](kernel-exploit.md)。

## 类型混淆

- 有符号/无符号混用:负数绕过数量/长度检查;`char` 符号性(>0x80 变负)堆下溢(Midnightflag 2026)。
- 整数截断:int32→int16(ApoorvCTF 2026)、运算顺序截断(CSAW 2015)、`strlen` int8 截断(ASIS CTF Finals 2017)、uint16 跳转截断(JIT 沙箱逃逸,BSidesSF 2026)。
- 解释器类型混淆:动态语言 JIT/VM 中把对象 A 当 B(VuwCTF 2025)→ 字段错位读写。
- 坐标系符号错配:关卡格式 signed/unsigned(BSidesSF 2026)。
- 元数据解析符号扩展下流(BSidesSF 2026)。

## 鉴权绕过

- 空令牌:`strncmp(n=0)` 空 token 比较恒真(UCSB iCTF 2018);哈希永真检查(0xFun 2026,Web 联动)。
- 结构体标志位被相邻溢出/逻辑置位:auth 字段单字节覆盖。
- `std::unordered_set` 桶碰撞伪造身份(Hackover 2018);SRP `A=0` 协议级绕过(OTW Advent 2018)。
- 哈希碰撞:Java `hashCode()` 碰撞(CSAW 2017);双精度浮点快速排序迁移 canary 位置(CSAW 2018)。

## 命令注入

- 二进制内 `system("cmd " + user)`:分号/管道/反引号;未锚定正则替换黑名单(picoCTF 2018)。
- 参数注入:git CLI 换行注入(BSIDSSF 2026)、sendmail CGI 参数注入(SECCON 2015)、tar 文件名注入(CyberSecurityRumble 2016)。
- 无空格:`${IFS}`、花括号扩展(Bash)、`$' '`;条码拼接多段注入(BSIDSSF 2024)。
- Prolog 注入(PoliCTF 2015)、Common Lisp reader macro(Insomnihack 2016)、Redis Lua `redis.call` 注入(HumanCTF 2018)。
- 稀有解释器注入族:LaTeX(write18)、XSLT、LaTeX mpost 绕受限(→ [WEB](../web/index.md) 语言页详表)。

## 信息泄露

- 未初始化变量/残留内存打印(→ [内存破坏漏洞](memory-corruption.md))。
- argv[0] 栈粉碎打印、`__environ` 栈泄露(BSIDSSF 2026)。
- 时间侧信道逐字符恢复 flag(RC3 CTF 2016);9 字节 test+je 连接超时位泄露(hxp 2018);4 字节 shellcode 持久寄存器时序侧信道(Google CTF 2017)。
- CRC/长度 oracle 当读取原语(ASIS CTF 2017);写阻塞时时间盲 shellcode(DEF CON 2017)。

## 工具速查

```bash
# 并发竞态
turbo-intruder / python threading + socket 重放
# 整数语义
python -c "import ctypes; ctypes.c_int16(0x8000)"
```

## 转向

- 竞态打堆/内核原语 → [堆漏洞利用](heap-exploit.md)/[Linux内核漏洞利用](kernel-exploit.md);注入最终落地 Web → [WEB](../web/index.md)
