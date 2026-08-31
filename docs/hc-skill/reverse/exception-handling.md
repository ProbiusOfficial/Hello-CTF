---
comments: true
---

# 异常处理

> REVERSE · 知识域。异常机制被用作控制流/反调试。标签:**VEH**、**SEH**、**UEF**、**VCH**、**其他异常处理**。

## 触发特征

- 程序频繁"崩溃又继续";反编译看不到关键逻辑(在异常回调里)。
- 反调试:调试器吞掉异常导致回调不执行。

## VEH(Vectored Exception Handler)

- `AddVectoredExceptionHandler`:进程级异常链,先于 SEH。
- 逆向用途:异常做隐藏控制流(int3/除零/访问违例跳转);注册回调处下断。
- 混淆:RtlInstallFunctionTableCallback 干扰展开;VEH + MBA 多线程诱饵(ApoorvCTF 2026)。

## SEH(Structured Exception Handling)

- 栈帧异常链(fs:[0]);`try/except` 编译产物;`__except_handler4`。
- 逆向:关键逻辑常在 filter/except 块;SEH 链遍历(x64dbg 命令)。
- 反调试经典:`int 3`/除零触发,正常程序走 except 继续,被调试则调试器先接管 → 检测调试存在。
- pwn 联动:SEH 覆写(老 32 位 exploit,→ [Pwn](../pwn/index.md));SafeSEH/SEHOP 校验。

## UEF(Unhandled Exception Filter)

- `SetUnhandledExceptionFilter`:无人处理的异常最后兜底;藏最终解密/退出逻辑。
- 逆向:ExitProcess 前的异常流;filter 回调内解密 key。

## VCH(Vectored Continue Handler)

- `AddVectoredContinueHandler`:继续执行时触发,常与 VH 配对做"两段式"控制流。
- 逆向:VH 里改上下文 → VCH 收尾;跟踪 CONTEXT 结构变化。

## 其他异常处理

- **C++ 异常**:throw/catch 逆 ABI(`__cxa_throw/__cxa_catch`、MSVC `__CxxFrameHandler`);异常对象携带数据。
- **信号(Linux)**:SIGFPE handler 当除零分支(PlaidCTF 2017 strace 计数侧信道)、SIGILL 模式切换(Hack.lu 2015)、SIGSEGV 当跳板、SIGFPE + mprotect 代码自变异(Hack.lu 2018)。
- **nanomites**:父进程 debug 子进程,子进程 int3 由父进程代填结果(Linux 信号版/Windows 调试事件版)。
- **长跳转**:`setjmp/longjmp` 跨函数跳转控制流。
- 展开与恢复:x64 SEH 基于表(RtlAddFunctionTable),逆向看 RUNTIME_FUNCTION。

## 处理流程

1. 异常触发点定位:崩溃地址、`RaiseException`/`int 3`/`div 0` 调用。
2. 找注册:`AddVectoredExceptionHandler`/`__try` 作用域/`signal()`。
3. 回调内分析;调试器设置"异常传递给程序"(`_ignore` 配置)让流程正常走。
4. 需要时伪造上下文:修改 EXCEPTION_RECORD/CONTEXT 绕校验。

## 工具速查

```bash
# x64dbg: 选项→异常→让程序处理指定异常
# gdb: handle SIGFPE nostop noprint pass
# IDA: 搜索 AddVectoredExceptionHandler/SetUnhandledExceptionFilter 交叉引用
```

## 转向

- 异常链里发现反调试 → [动态调试对抗](anti-debug.md);SEH 覆写利用 → [Pwn](../pwn/index.md)
