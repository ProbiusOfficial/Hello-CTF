Quick Start：加密与解密

本章节会简单的介绍一下在逆向中的各种加密算法，加密算法在逆向中几乎无处不在。基本大部分的中等难度的题目都会使用主流/小众（或经魔改的）加密算法。因此，如何识别加密算法和如何解密在逆向的学习中是必不可少的。

关于加密算法的原理和具体种类，可以前往[Crypto](https://hello-ctf.com/hc-crypto/Recap/)分区查看，这里只讲如何识别和解密。

# XOR 异或加密

异或加密几乎是逆向题中最常见的算法之一。他的特性是**对称**，如下所示：

`A XOR B XOR B = A`

A 在经过两次异或运算后，会还原成 A 。

## 加密

以下会使用一个简单的C程序来进行演示：

```c
#include <stdio.h>
#include <string.h>
int main() {
    const unsigned char flag[] = "flag{test}";
    const unsigned char key[]  = "key";
    size_t flen = strlen(flag);
    size_t klen = strlen(key);
    for (size_t i = 0; i < flen; i++) {
        unsigned char c = flag[i] ^ key[i % klen];
        printf("%02x", c);
    }
}
```

在汇编里面，他是长这样的：

```assembly
.LC0:
	.string	"%02x"
	.text
	.globl	main
	.type	main, @function
main:
.LFB0:
	.cfi_startproc
	push	rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	mov	rbp, rsp
	.cfi_def_cfa_register 6
	sub	rsp, 48
	movabs	rax, 8315180360373726310
	mov	QWORD PTR -36[rbp], rax
	mov	DWORD PTR -29[rbp], 8221811
	mov	DWORD PTR -40[rbp], 7955819
	mov	QWORD PTR -16[rbp], 10
	mov	QWORD PTR -24[rbp], 3
	mov	QWORD PTR -8[rbp], 0
	jmp	.L2
.L3:
	lea	rdx, -36[rbp]
	mov	rax, QWORD PTR -8[rbp]
	add	rax, rdx
	movzx	ecx, BYTE PTR [rax]
	mov	rax, QWORD PTR -8[rbp]
	mov	edx, 0
	div	QWORD PTR -24[rbp]
	mov	rax, rdx
	movzx	eax, BYTE PTR -40[rbp+rax]
	xor	eax, ecx
	mov	BYTE PTR -25[rbp], al
	movzx	eax, BYTE PTR -25[rbp]
	mov	esi, eax
	lea	rax, .LC0[rip]
	mov	rdi, rax
	mov	eax, 0
	call	printf@PLT
	add	QWORD PTR -8[rbp], 1
.L2:
	mov	rax, QWORD PTR -8[rbp]
	cmp	rax, QWORD PTR -16[rbp]
	jb	.L3
	mov	eax, 0
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
```

异或加密顾名思义，有一个很明显的特征就是会出现`xor`指令

简单介绍一下`xor`指令，`xor`指令的格式是`xor dest, src`。

其中`dest`是目标操作数，`src`则是来源操作数，操作数可以是是寄存器、内存单元或立即数。

    !!! Example
        内存单元：如 `[0x114514]`, `[eax]` 等

    !!! Example
        立即数：如 `0x114514`, `0x1919810` 等


而这一段汇编代码中的`xor eax, ecx`很明显就对应我们C代码中的`flag[i] ^ key[i % klen]`。

## 解密

接下来就到解密了，