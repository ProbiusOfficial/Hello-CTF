## Quick Start：汇编语言

本章节将会简单介绍一下汇编语言，汇编语言在逆向工程中占据的地位还是比较重要的。此章节并不会系统地去介绍整个汇编语言体系，而是以 CTF 逆向 为背景，介绍比较实用的部分。

下面我们以一个简单的 Hello World 程序为背景，初步介绍汇编：

```c
#include <stdio.h>
int main(int argc, char* argv []) {
    printf("Hello, world!\n");
    return 0;
 }
```

我们通过 GCC 将以上程序编译为 ASM 形式并输出，可以得到以下内容：

```assembly
      .section .rodata
  .LC0:
      .string "Hello, world!"
      .text
      .globl   main
      .type    main, @function
  main:
      push     rbp
      mov      rbp, rsp
      sub      rsp, 16
      mov      DWORD PTR [rbp-4], edi
      mov      QWORD PTR [rbp-16], rsi
      mov      edi, OFFSET FLAT:.LC0
      call     puts
      mov      eax, 0
      leave
      ret
```

这是一个很简单的执行过程，下面我们来简单的介绍一下这块汇编：

首先 `.LC0:` 定义了一个字符串，也即我们的 `“Hello, world!”`，它的作用就是告诉编译器这个字符串的位置（地址）。对于我们直接输入的字符串，系统会自动为其分配一个临时内存，用来临时储存这个字符串。

下面就是 `main` 函数的汇编块了：

从第 8 行到第 12 行，进行的操作就是初始化堆栈，为这个函数执行开辟适合的内存区域，其中的 `rbp，rsp，edi` 等都是寄存器，它们负责储存数据。

从第 13 行开始就进入了主要执行段：通过 `mov` 指令将字符串的值赋值给 `edi`，作为 `printf` 函数的第一个参数，之后传参完毕，通过 `call` 指令调用 `printf` 函数，输出字符串到屏幕；接着将 `eax` 赋值为 0，这里 `eax` 一般作为函数的返回值；之后 `leave` 然后 `ret` 返回，该函数就执行完毕了。

在这个过程中，我们可以看到一些常见的汇编指令：`mov、sub、call、ret` 等，下面来说说它们的作用吧。
`mov` 是赋值指令，它的格式为 `mov 被赋值方, 要赋的值`；
`sub` 是递减指令，其格式为 `sub 目标, 递减的值`；
`call` 为调用指令，其格式为 `call 要调用的函数地址`；
`ret` 和 `leave` 连用是出栈指令，也即代表了一个函数的结束。通常在 masm 里，我们只会看到 `ret`，`leave` 并不常见。

------

了解了一些基本的汇编指令后，下面我们来看看 CTF 中常见的一些指令：

1、`loop` 循环指令：

```assembly
mov rax,0
mov rcx,236
s:
add rax,123
loop s
leave
ret
```

上面的指令执行的是对 123 累加 236 次，从以上代码中我们可以看到，`rcx` 寄存器保存的是循环次数，`loop` 指令每执行一次，`rcx` 的数值就会减少 1，当其数值减少到 0 时，`loop` 指令就会停止，继续执行下面的指令。

2、无条件跳转指令：

```assembly
lable:
mov edx,0

jmp lable
```

无条件跳转指令为 `jmp`，其意思从字面上就可以看出来，只要是执行到 `jmp` 这里，无论什么情况，都会直接跳转到 `lable` 的代码块中继续往下执行指令。

3、条件跳转：

```assembly
lable:
mov ebx,1

cmp ebx,0
je lable
```

以上代码将 `ebx` 的值与 `0` 对比，如果相等，则会跳转到 `lable` 处，条件跳转指令 `je` 代表相等则跳转，还有其他与之条件不一样的条件跳转指令，一般条件跳转指令是与 `cmp`、`test` 指令混在一起用的。以上代码也可以用 `test` 来写：

```assembly
lable:
mov ebx,1

test ebx,0
jnz lable
```

`test` 是逻辑与指令，以上代表的即为 `ebx&0`，`jnz` 代表标志位为 0 就跳转，其实现效果与 `cmp` 相同。

下面是一些常见的条件跳转指令：

- `JE`：等于（Jump if Equal）
- `JNE`：不等于（Jump if Not Equal）
- `JZ`：零标志位为 1（Jump if Zero）
- `JNZ`：零标志位为 0（Jump if Not Zero）
- `JS`：符号标志位为 1（Jump if Sign）
- `JNS`：符号标志位为 0（Jump if Not Sign）
- `JP` 或 `JPE`：奇偶标志位为 1（Jump if Parity/Even）
- `JNP` 或 `JPO`：奇偶标志位为 0（Jump if Not Parity/Odd）
- `JB` 或 `JNAE`：以下标志位为 1（Jump if Below/Not Above or Equal）
- `JAE` 或 `JNB`：以下标志位为 0（Jump if Above or Equal/Not Below）
- `JBE` 或 `JNA`：以下标志位或零标志位为 1（Jump if Below or Equal/Not Above）
- `JA` 或 `JNBE`：以下标志位和零标志位都为 0（Jump if Above/Not Below or Equal）
- `JO`：溢出标志位为 1（Jump if Overflow）
- `JNO`：溢出标志位为 0（Jump if Not Overflow）
- `JC` 或 `JB`：进位标志位为 1（Jump if Carry/Not Below）
- `JNC` 或 `JAE`：进位标志位为 0（Jump if Not Carry/Below or Equal）
- `JG` 或 `JNLE`：大于（Jump if Greater/Not Less or Equal）
- `JGE` 或 `JNL`：大于或等于（Jump if Greater or Equal/Not Less）
- `JL` 或 `JNGE`：小于（Jump if Less/Not Greater or Equal）
- `JLE` 或 `JNG`：小于或等于（Jump if Less or Equal/Not Greater）

下面是一些常见的位运算指令：

- `AND`：与运算，`AND AX,BX` 将 `AX` 与 `BX` 进行逻辑与运算，并将结果保存到 `AX` 寄存器中
- `OR`：或运算，`OR AX,BX` 将 `AX` 与 `BX` 进行逻辑或运算，并将结果保存到 `AX` 寄存器中
- `XOR`：异或运算，`XOR AX,BX` 将 `AX` 与 `BX` 进行异或运算，并将结果保存到 `AX` 寄存器中
- `NOT`：取反操作，`NOT CX` 将 `CX` 进行取反，并将结果保存到 `CX` 寄存器中
- `TEST`：逻辑与运算，`TEST AX,BX` 将 `AX` 与 `BX` 进行与运算，并设置标志位，结果不保存

4、函数传参：

在汇编中，我们有时候需要知道参数被保存在那个寄存器里，这里我列举一般情况：

通常函数的返回值保存在 `ax` 寄存器里，比如 `eax，rax` 等；
函数的参数一般按顺序保存在 `cx、dx、si` 中，在 64 位汇编中，一般按 `rcx rdx r8 r9 r10 r11 ...` 的顺序保存参数。

有时候根据函数调用约定以及编译器和平台的不同，这个储存规律也会发生改变，我们需要根据当时情况动态调整。

5、`lea` 地址加载：

其使用格式为 `lea rdx,[my_var]` 将 `my_var` 的地址而不是内容赋值给 `rdx` 寄存器。

6、`xchg` 数值交换指令：

其使用格式为 `xchg ax,bx` 将 `ax` 和 `bx` 的数值交换。