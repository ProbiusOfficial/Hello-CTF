---
comments: true
---

# REVERSE - 逆向工程

> 方向技能索引。目标是还原独立可执行文件/固件/字节码的算法与逻辑时从本索引路由。不要用于:内存破坏型利用(转 [Pwn](../pwn/index.md));题目只需解码数据(转 [Crypto](../crypto/index.md)/[Misc](../misc/index.md))。

## 知识域路由表

| 分组 | 知识域 |
| --- | --- |
| 基础 | [逆向分析基础](basic-analysis.md) · [低级语言分析](low-level-lang.md) · [高级语言逆向](high-level-lang.md) · [可执行文件逆向](executable.md) |
| 对抗 | [静态分析对抗](anti-static.md) · [动态调试对抗](anti-debug.md) · [异常处理](exception-handling.md) · [代码注入](code-injection.md) |
| 平台 | [GUI程序逆向](gui-reverse.md) · [Python程序逆向](python-reverse.md) · [Android程序逆向](android-reverse.md) · [Golang程序逆向](golang-reverse.md) · [Rust程序逆向](rust-reverse.md) |
| 综合 | [加密与解密](crypto-in-reverse.md) |

## 环境基线

```bash
# 反编译:IDA Pro / Ghidra / Binary Ninja / dogbolt.org(在线多编译器对比)
# 调试:x64dbg(Windows)、gdb+pwndbg(Linux)、lldb、Frida
# 动静态辅助:angr(符号执行)、Unicorn(模拟)、Qiling(全系统模拟)、DynamoRIO/Pin(插桩)
pip install angr unicorn qiling frida-tools
```

## 通用解题流程

1. `file`/DIE 识别:格式(PE/ELF/Mach-O/APK/固件)、架构、是否壳/混淆。
2. 静态首轮:字符串窗口找提示;`main`/`WinMain` 定位;导入表找敏感 API。
3. 拖入反编译:恢复伪代码语义;识别加密常量(S盒、魔数)。
4. 遇对抗(花指令/反调试/VM)→ 先解对抗再读逻辑。
5. 三种落地:直接逆算法手写解密 / patch 后运行 / 约束求解(angr/Z3)。
