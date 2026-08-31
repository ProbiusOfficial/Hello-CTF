---
comments: true
---

# 异构PWN

> PWN · 知识域。非 x86 架构与平台的二进制利用。标签:**ARM-PWN**、**AArch64-PWN**、**MIPS32-PWN**、**MIPS64-PWN**、**PowerPC-PWN**、**RISC-V-PWN**。

## 触发特征

- `file` 显示 ARM/MIPS/RISC-V/PowerPC/m68k;题目配 qemu-user 或真实开发板固件。

## 环境基线

```bash
apt install qemu-user qemu-user-static gdb-multiarch
qemu-arm -L /usr/arm-linux-gnueabihf ./pwn
gdb-multiarch -ex 'set arch arm' -ex 'target remote :1234'
# 交叉编译:arm-linux-gnueabihf-gcc / aarch64-linux-gnu-gcc / mips-linux-gnu-gcc
# pwntools: context.arch='arm' / 'aarch64' / 'mips'
```

## ARM-PWN(32位)

- 调用约定:r0-r3 传参;返回地址进 **lr**,栈上无返回地址时需 `pop {pc}` gadget。
- **Thumb 切换**:指令集切换靠 PC 低位(`bx`/`blx`);地址 +1 表 Thumb;shellcode 用 Thumb 缩短(HackIM 2016 ARM 溢出 + Thumb shellcode)。
- gadget 源:movt/movw 组合构造常数;`pop {r0-r3, pc}` 模板。
- dup2 + socket 重定向 shellcode(网络服务型)。

## AArch64-PWN

- 调用约定 x0-x7;无 `pop rdi` 类 gadget → `getusershell()` 这类 libc 函数当 x0 设定器(HITCON 2018);`ldp` 批量加载。
- ret2libc 流程同 x86_64;`system` 需要 x0 指向 "/bin/sh"(静态数据段或自写)。
- `mrs`/`msr` 系统寄存器;cache 指令在 side-channel 场景。

## MIPS32/MIPS64-PWN

- 延迟槽(delay slot):跳转后下一指令仍执行,gadget 链要考虑。
- $t9 寄存器约定:函数要求 $t9 = 函数地址(gp 计算),ret2libc 时先设 $t9。
- 缓存一致性问题(qemu 无感,真机注意);MIPS64 Cavium OCTEON 协处理器加密(SEC-T CTF 2017,逆向侧)。
- Big-endian/Little-endian 双形态确认。

## PowerPC-PWN

- 大端为主;调用约定 r3-r10;`bl` 后 lr 处理;TOC/GOT 结构。
- 出题少,多见于 IOT/固件场(旧路由器、工控设备)。

## RISC-V-PWN

- rv32/rv64;ABI:a0-a7 传参;`rdynamic` 缺符号时 GLIBC 符号版本补丁执行(Pwn2Win 2018)。
- 自定义扩展指令集(逆向向,→ [Reverse](../reverse/index.md));srdnlenCTF 2026 RISC-V 分析;EHAX 2026 RISC-V 题。

## 其他平台

- **m68k(Motorola 68000)**:两段式 shellcode(HackIT 2017);复古平台(老游戏机、工业设备)。
- **Xtensa(ESP32)**:ROM symbol map 辅助逆向(Insomni'hack 2017)→ [IoT](../iot/index.md)。
- **DOS COM 实模式**:int 0x21 shellcode(SEC-T CTF 2017);16 位 MBR(CSAW 2017 psadbw 约束)。
- **Chip-8/Game Boy 等解释器平台**:OOB → ret2libc(IceCTF 2018);bgb 调试 Z80(Square CTF 2017)。
- **Forth 解释器**:system word 调用(32C3 2015)。

## 工具速查

```bash
ROPgadget --binary ./pwn --arch arm
# pwntools shellcraft.arm.linux.sh() / shellcraft.aarch64.linux.sh()
objdump -m arm -b binary -D shellcode.bin   # 手动反汇编校验
```

## 转向

- 固件整体分析 → [IoT-固件分析](../iot/firmware.md);架构逆向基础 → [Reverse-低级语言分析](../reverse/low-level-lang.md)
