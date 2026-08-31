---
comments: true
---

# 静态分析对抗

> REVERSE · 知识域。让静态分析失效的手段与还原方法。标签:**可执行式花指令**、**不可执行式花指令**、**代码混淆**、**Obfuscator LLVM**、**Virtual Machine**、**API动态调用**。

## 触发特征

- 反编译爆红/伪代码缺失/函数边界错乱;字符串加密;关键逻辑"看不见"。

## 可执行式花指令

- 定义:垃圾字节实际执行但不影响语义(跳过/自修改)。
- 常见:`jz+1 跨指令边界`、call/jmp 混叠、`jmp over garbage`。
- 还原:ida 手动 nop/undefine;脚本扫固定模式(常见花指令模板库);Unicorn 从入口模拟到正确边界再重分析。

## 不可执行式花指令

- 定义:干扰反汇编器数据流判断的假字节(永不执行的区域故意放"指令")。
- 表现:函数列表被污染、伪代码混入垃圾。
- 还原:定位真实跳转边界,把垃圾段转 data;IDA `U` + `C` 手工;写 IDAPython 按跳转目标重建。

## 代码混淆

- **控制流平坦化**:分发器 + 状态变量;还原:D-810(IDA)/GOOMBA(Ghidra)/Dewolf;手动:符号执行恢复真实路径,或 trace 后按块重排。
- **不透明谓词**:恒真/恒假表达式;识别:数学恒等式(x²≥0、(x·y)² mod 4∈{0,1});用 Z3 验证谓词恒定性后化简。
- **MBA 混淆**(Mixed Boolean-Arithmetic):位运算+算术恒等混淆;识别与化简:D-810、SiMBA、手写规则库。
- **函数块化/散落**(function chunking):一个函数被切到多处;IDA 手动 join tail chunks。
- **字符串加密**:逐字符异或/栈构造(stack string);动态 dump 运行时字符串,或 hook 输出函数。
- 决策树函数混淆(HTB WonderSMS);GLSL shader VM(ApoorvCTF 2026)。

## Obfuscator LLVM

- OLLVM 家族:fla(平坦化)、bcf(虚假控制流)、sub(指令替换)、字符串混淆。
- 识别:特征常量(全局差分变量)、分发器 switch 形态。
- 还原:OLLVM-deobfuscation 工具链;Unicorn+angr 路径符号化;最新版(Obfuscator-LLVM 4.0 复刻、Arxan 类商用)。
- VMProtect/Themida 商业壳(→ 下文 VM 小节 + 动态工具链)。

## Virtual Machine

- 自定义 VM 逆向通用流程:
  1. 找 dispatch 主循环(`switch`/跳转表)。
  2. 恢复指令集:opcode → handler 语义逐个标注。
  3. 提取字节码 dump;按语义翻译成伪代码/LLVM IR(Google CTF 2017 提升到 LLVM IR 再优化)。
- 捷径:trace diff 代替全量反汇编(CONFidence CTF 2019 Teaser);fuzz 发现指令集(hxp CTF 2017);VM 顺序键链暴力(Midnight Flag 2026);90K+ 状态的状态机 VM(按块处理)。
- 商业壳:VMProtect(找 VM entry,识别 handler 模式)、Themida/WinLicense(反调试极强,先脱环境)。
- GLSL/浏览器 JS VM:按对应平台工具链。

## API动态调用

- `GetProcAddress`/`dlsym` 按哈希取函数 → 导入表干净但运行时全动态。
- 还原:hook 动态解析函数打印名称/地址(LD_PRELOAD、Frida);哈希算法逆推(hash-resolved imports 识别)。
- 间接系统调用/syscall stub;PEB 走 GS 段定位。
- 静态识别特征:`mov r10, imm; mov eax, ssn; syscall` 直接系统调用。

## 工具速查

```bash
# 动态 trace 替代静态硬刚
ltrace ./chall; strace ./chall
frida-trace -i '*compare*' ./chall
# unicorn 快速执行片段
```

## 转向

- 运行时检测(反调试)→ [动态调试对抗](anti-debug.md);VM 内嵌加密 → [加密与解密](crypto-in-reverse.md)
