---
comments: true
---

# 逆向分析基础

> REVERSE · 知识域。工具使用与静态/动态基本功。标签:**工具使用**、**静态分析**、**动态调试**、**程序补丁**、**其他逆向分析基础**。

## 触发特征

- 入门级 crackme/签到逆向;题目给二进制求 key/flag。
- 任何逆向题的第一阶段都用本页。

## 工具使用

- **IDA**:F5 反编译;结构体重建、签名库(Flirt)、IDAPython 脚本。
- **Ghidra**:免费替代;headless 批量分析(`analyzeHeadless`);脚本 Java/Python。
- **x64dbg / gdb**:动态核心;插件 pwndbg/gef/x64dbg+SharpOD。
- **在线**:dogbolt.org 多反编译器交叉对比(Ghidra/IDA/RetDec/Angr)。
- **辅助**:Detect It Easy/ExeinfoPE(壳与编译器指纹)、pestudio/PE-bear、CFF Explorer、WASD 加壳识别。

## 静态分析

- 流程:文件指纹 → 字符串(ASCII/UNICODE,关注 "flag"/"correct"/"wrong"/提示语)→ 导入表敏感函数(strcmp/memcmp/CryptoAPI)→ 反编译读逻辑。
- 算法识别:魔数表(S盒/常量)查 IDA 插件 FindCrypt/signsrch;异或、BASE64 表魔改。
- 常量核对清单:0x67452301(MD5/SHA1 系)、0x9E3779B9(TEA 系)、CRC 表、AES S-Box、RC4 KSA 结构。

## 动态调试

- 断点策略:字符串引用处、比较函数调用点、输入回显点。
- 运行时观察:寄存器、内存窗口跟 key;`getchar` 后的缓冲区内容。
- 补丁式调试:跳过反调试先 patch 再分析(见 [动态调试对抗](anti-debug.md))。
- Linux:gdb + pwntools 联动喂输入;corefile 找 offset。

## 程序补丁

- 语义 nop:条件跳转反转(jz↔jnz)、比较值改改(高位字节 patch)。
- patch 校验函数直接 `mov al,1; ret`;patch 加密轮数/密钥常量后让程序输出 flag。
- 工具:IDA patch 字节 → Apply patches;x64dbg 直接改内存验证。

## 其他逆向分析基础

- 输入变换通用模式:逐字节异或常量/位置、交换字节、查表替换(→ [加密与解密](crypto-in-reverse.md))。
- 期望值表:比较目标为常量表时逆变换逐字节(→ [低级语言分析](low-level-lang.md) 配合)。
- 迭代求解模式:每轮依赖前轮输出 → 写脚本复现;Unicorn 模拟跑加密函数直接调用(免逆向轮内细节)。

## 工具速查

```bash
file ./chall; strings -n 6 ./chall | less
python -c "import angr" ...
# Unicorn 调函数模板:
# mu.mem_write / mu.emu_start(函数地址, 返回地址) 直接黑盒调用
```

## 转向

- 有壳/混淆 → [静态分析对抗](anti-static.md);调试被反 → [动态调试对抗](anti-debug.md)
