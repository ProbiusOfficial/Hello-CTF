---
comments: true
---

# Rust程序逆向

> REVERSE · 知识域。Rust 编译二进制的还原。标签:**Rust程序符号恢复**、**其他Rust程序逆向**。

## 触发特征

- panic 字符串("index out of bounds"、"called `Option::unwrap()` on a `None` value")、`RUST_BACKTRACE` 提示、符号带 `17h` 哈希后缀。

## Rust程序符号恢复

- **demangle**:`rustfilt`/`rust-demangle` 还原 ` _ZN...17h...E` 格式符号。
- 未 strip 的二进制:crate 路径(`core::`/`std::`/`alloc::`)+ crate 内部函数直接可读;main 逻辑通常在 `chall::main`。
- strip 后:panic 字符串关联定位(panic 信息含源文件路径与函数!)——**Rust panic 内嵌 file!()/line!() 宏展开**,strip 也常留源文件名,是定位关键。
- 常量提取:`xmmword` 大常量块(Rust 优化后常量向量),IDAPython 脚本辅助(Insomnihack 2019)。

## 其他Rust程序逆向

- **语义还原要点**:
  - `Option/Result`:判别联合(枚举 niche 优化,指针低位/空指针表示 None)。
  - 迭代器:零成本抽象,反编译常"消失"成循环;`collect/zip/chain` 模式识别。
  - 所有权:大量 memcpy 是移动语义,非数据复制。
  - String/&str:栈上 fat pointer(ptr,len)。
- **serde_json schema 恢复**:从 Deserialize 派生代码还原 JSON 字段结构(结构体 ↔ 字符串常量表)。
- **加密 crate 识别**:aes/ring/chacha20 crate 符号;魔数常量同 C(→ [加密与解密](crypto-in-reverse.md))。
- **混淆对抗**:release 优化 + LTO 后内联爆炸 → 按 panic/字符串锚点切块。
- **特殊利用面**(pwn/reverse 交叉):
  - 编译器 #25860 生命周期逃逸(Hack.lu 2018)。
  - `#[no_mangle]` 覆写 libc 符号绕 seccomp(Hack.lu 2018)。
  - Rust 前端 PWN:panic unwrap 后的 UB 场景(unsafe 块)。
- **WASM 出品**:Rust→wasm(→ [可执行文件逆向](executable.md) WASM 节)。

## 工具速查

```bash
rustfilt < 符号表
strings ./chall | grep "src/"     # panic 泄露的源文件路径
# IDA:启用 demangle(Rust); cargo 符号: nm -C
```

## 转向

- 主体校验逻辑 → [加密与解密](crypto-in-reverse.md);Rust 系统级利用 → [Pwn](../pwn/index.md)
