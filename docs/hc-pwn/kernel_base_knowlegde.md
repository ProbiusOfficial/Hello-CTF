---
comments: true

---

# Linux 内核 PWN 基础

本文档基于6.x版本内核

## 整体架构图

```plain
第 0 章  环境搭建：QEMU + initramfs + GDB
第 1 章  内核视角基础：syscall、地址空间、SLUB
第 2 章  内核 PWN 的利用模型与漏洞分类
第 3 章  堆利用核心：SLUB 与 Slab 喷射
第 4 章  提权原语：cred、commit_creds 与 modprobe_path
第 5 章  控制流劫持：ret2usr 与内核 ROP
第 6 章  栈与竞态：栈溢出、double-fetch、race
第 7 章  保护机制与绕过：KASLR / SMEP / SMAP / KPTI / FGKASLR
第 8 章  实战模板：从漏洞到稳定 exploit
```

配套视频资源：[【CTF-Pwn基础教程-Kernel-Pwn-第一课-内核基础】](https://www.bilibili.com/video/BV1Pef2BXE6S)

_本节作者:EROORvbsyes_

## 第 0 章 环境搭建：QEMU + initramfs + GDB

**核心内容**：构建一个“可换内核版本、可开关 mitigation、可 GDB 调试、可投放 exploit”的标准化工作站。内核 PWN 不存在“用 Docker 代替 QEMU”的捷径，QEMU + initramfs 是唯一与真实题目和 kernelCTF 对齐的路径。

**必须覆盖的点**：

- **工具链**：`build-essential`、`qemu-system-x86`、`gdb-multiarch`、`cpio`、`libelf-dev`、`libssl-dev`、`flex`、`bison`。推荐 WSL2 + Ubuntu 22.04，避免 gcc-13 对旧内核模块的兼容问题。
- **典型题目包结构**：`bzImage`（压缩内核，题目常给这个）、`vmlinux`（带符号，GDB 用，我们解题常用）、`initramfs.cpio.gz`、`vuln.ko`、`run.sh`。
- **initramfs 修改流程**：解包 → 修改 `init`（CTF 学习时可临时切 root，真实题目通常保持 `setuid 1000`） → 重新打包 `find . | cpio -o --format=newc | gzip > ../initramfs.cpio.gz`。
- **QEMU 启动参数模板**：`-m [内核内存，例如256M] -kernel [内核文件] -initrd [根文件系统] -cpu [CPU参数，例如kvm64,+smep,+smap] -append [启动参数，例如"console=ttyS0 nokaslr quiet oops=panic panic=1"] -nographic -s`。`-s` 开启 GDB 端口 1234。
- **参数与保护的对应关系**：`+smep` / `+smap` 决定能否 ret2usr；`nokaslr` / `kaslr` 决定是否需要 leak；`pti=on` 决定返回用户态是否需要 KPTI trampoline。
- **GDB 调试**：`target remote :1234`，`b commit_creds`，结合 pwndbg/GEF 的内核结构体支持。

## 第 1 章 内核视角基础：syscall、地址空间、SLUB

**核心内容**：从用户态 PWN 的已知概念出发，重新校准内核 PWN 的底层模型。

**必须了解的点**：

- **Ring 与状态切换**：以intel CPU为例，CPU中分为4层0-3 Ring，可执行命令的权限逐级递减，一般来说我们只涉及到Ring0/ Ring3。要从用户态进入内核，`syscall` / `sysenter` 进入内核，相反`iret` / `sysret` 返回用户态；其中`swapgs` 是在返回路径中切换页表的角色。（页表：是虚拟空间对应物理地址的很多张表，决定了虚拟地址如何计算得到物理地址）
- **内核共享地址空间**：内核是单一 monolithic 地址空间，任何子系统的漏洞都可能危及整机。与用户态进程每次 `exec` 重新随机化不同，内核布局在**启动时固定**，直到下一次重启。
- **内核权限管理**：在内核中程序所持有的权限通过cred结构体表示，uid,euid,gid,egid为0即该进程被视为root权限运行。

```C

struct cred {
 atomic_t usage;
#ifdef CONFIG_DEBUG_CREDENTIALS
 atomic_t subscribers; /* number of processes subscribed */
 void  *put_addr;
 unsigned magic;
#define CRED_MAGIC 0x43736564
#define CRED_MAGIC_DEAD 0x44656144
#endif
 kuid_t  uid;  /* real UID of the task */
 kgid_t  gid;  /* real GID of the task */
 kuid_t  suid;  /* saved UID of the task */
 kgid_t  sgid;  /* saved GID of the task */
 kuid_t  euid;  /* effective UID of the task */
 kgid_t  egid;  /* effective GID of the task */
 kuid_t  fsuid;  /* UID for VFS ops */
 kgid_t  fsgid;  /* GID for VFS ops */
 unsigned securebits; /* SUID-less security management */
 kernel_cap_t cap_inheritable; /* caps our children can inherit */
 kernel_cap_t cap_permitted; /* caps we're permitted */
 kernel_cap_t cap_effective; /* caps we can actually use */
 kernel_cap_t cap_bset; /* capability bounding set */
 kernel_cap_t cap_ambient; /* Ambient capability set */
#ifdef CONFIG_KEYS
 unsigned char jit_keyring; /* default keyring to attach requested
      * keys to */
 struct key *session_keyring; /* keyring inherited over fork */
 struct key *process_keyring; /* keyring private to this process */
 struct key *thread_keyring; /* keyring private to this thread */
 struct key *request_key_auth; /* assumed request_key authority */
#endif
#ifdef CONFIG_SECURITY
 void  *security; /* LSM security */
#endif
 struct user_struct *user; /* real user ID subscription */
 struct user_namespace *user_ns; /* user_ns the caps and keyrings are relative to. */
 struct ucounts *ucounts;
 struct group_info *group_info; /* supplementary groups for euid/fsgid */
 /* RCU deletion */
 union {
  int non_rcu;   /* Can we skip RCU deletion? */
  struct rcu_head rcu;  /* RCU deletion hook */
 };
} __randomize_layout;

```

  **UID/GID 族**：uid、euid、suid、fsuid 以及对应的 GID。将 euid 等字段置 0 是“直接改 cred”路线的最小操作，但要注意 fsuid 影响文件访问判定，只改 euid 在某些场景下并不等于完整 root。

  **capability 集合**： `cap_effective`、`cap_permitted`、`cap_inheritable`、`cap_bset`、`cap_ambient`。其中 `cap_effective` 是内核实际用来判定是否具有相应特权(例如发出ping包需要具有CAP_NET_RAW特权)的那一组位，只改 UID 而不改 capability，在现代内核上可能不足以完成所有提权动作；直接覆盖 cred 时，通常需要把 capability 字段一并设为全 1（或至少 CAP_FULL_SET 对应的位图）。

  **user_namespace * 指针**：这是 cred 中容易被忽略但对提权语义至关重要的字段。一个 capability 永远相对于某个 user namespace 才有意义。这意味着 cred 的覆盖不仅要改数值，还要考虑目标进程当前所处的 namespace 上下文。例如我们的EXP如果不具备相应的特权，我们就可以内部自己创建一个namespace，在自己的namespace中拥有相应特权。

- **SLUB 分配器的最小必要模型**：
  - 内核中每一个最小内存分配单位被称为`obj`，和用户态的`chunk`含义差不多
  - `kmalloc(size)` 向上对齐到 `kmalloc-{32, 64, 96, 128, 192, 256, 512, ...}` cache。
  - 每个 CPU 有 `cpu_slab`，`freelist` 是**对象内嵌指针**，fast path 无锁 pop。
  - `kfree` 将对象 push 回 per-CPU freelist；free 完的对象**立刻**可被下一次同 cache 分配拿走——这是 UAF reclaim 的基础。
  - 专用 cache（如 `cred_jar`）与通用 `kmalloc-N` cache 的隔离：跨 `cache` 覆盖需要 `cross-cache` 技术。
  - 与用户态的chunk不同，内核态中正在使用的obj中是**不存在元数据**的，只有在空闲的时候被挂载到freelist链表上，其中存储数据的区域才会有一个next指针，指向下一个空闲obj。同时Linux为了防御堆溢出攻击，给next指针添加了早obj中的偏移，由s->offset决定。

- **`task_struct` 与 `cred` 的关系**：内核中使用task_struct表示一个进程，内核通过 `task_struct->cred` 索引权限凭证；`cred` 中的 `uid/euid/gid/egid` 全为 0 即视为 root 权限。

## 第 2 章 内核 PWN 的利用模型与漏洞分类

**核心内容**：建立一条从“漏洞”到“root”的通用流水线，以及按原语（primitive）而非按 CVE 编号来归类漏洞的思维方式。

**必须覆盖的点**：

- **五步利用模型**：
  1. 发现漏洞（UAF、OOB、race、integer overflow、type confusion）；
  2. 构建原语（arbitrary read、arbitrary write、controlled RIP）；
  3. 绕过保护（KASLR、SMEP、SMAP、KPTI）；
  4. 提权（`commit_creds`、`modprobe_path`、namespace escape）；
  5. 干净返回用户态（KPTI trampoline、`iretq` / `swapgs`）。
- **漏洞分类框架**：
  - **空间安全**：栈溢出、堆溢出（SLUB）、OOB read/write、off-by-one。
  - **时间安全**：UAF、double-free、未初始化内存使用。UAF 已是 Linux 内核中被利用最多的单一漏洞类别。这一漏洞类别在用户态比较少见。
  - **类型安全**：type confusion、错误的 `container_of()`。
  - **竞态与输入验证**：double-fetch、spinlock/mutex race、整数溢出导致的大小计算错误。
  - **文件系统/命题漏洞**: 利用出题人的疏忽巧妙借助文件系统漏洞/OOM Killer提权
  - **CVE提权**: 例如Copy Fail/Dirty Frag
- **漏洞类型到利用基线的快速映射**：栈溢出 → Canary + KASLR 绕过 + ROP；堆溢出 → slab 喷射覆盖相邻对象；UAF → 重新申请同 slab 对象；任意读写 → 直接改 `cred` 或 `modprobe_path`。

## 第 3 章 堆利用核心：SLUB 与 Slab 喷射

**核心内容**：内核 PWN 的主战场。用户态 glibc heap 的 tcache / fastbin 技巧在这里**全部作废**，必须围绕 SLUB 的 per-CPU freelist 和对象生命周期重新建立直觉。

**必须覆盖的点**：

- **SLUB 对象生命周期**：`kmalloc` → per-CPU freelist → per-CPU partial list → per-node partial list → 新 slab page；`kfree` 的逆过程。
- **Slab 喷射四步法**：
  1. 确定目标对象的 cache（按大小匹配）；
  2. 排空已有空闲对象（喷射 dummy allocation）；
  3. 触发漏洞释放目标对象；
  4. 喷射同大小替换对象，落在 freed slot 上。
- **经典喷射对象**：

  | 对象 | 分配方式 | cache 大小 | 利用价值 |
  | --- | --- | --- | --- |
  | `msg_msg` | `msgsnd()` | 可控（`kmalloc-N`） | 任意 size 可控数据、头部可控，适合 reclaim 和 leak |
  | `pipe_buffer` | `pipe()` + `splice()` | `kmalloc-64`（40 字节） | 含 `ops` 函数表指针，UAF 后可劫持 RIP |
  | `sk_buff` | 网络数据包 | 多种 | 大数据喷射、跨 cache |
  | `setxattr` | `setxattr()` | 可控 | 快速堆喷 |

  `msg_msg` 通过 `msgsnd` 分配、`msgrcv` 释放；`pipe_buffer` 的 `ops` 指针在 `release()` 时被调用，是天然的控制流劫持点。
  **经典跳转劫持对象**：

  | 对象 | 劫持虚表 |
  | --- | --- |
  | `pipe_buffer` | `pipe_buffer_ops` |
  | `seq_operations` | `seq_operations_ops` |
  | `tty_struct` | `pipe_buffer_ops` |

- **Double-free 与 freelist 腐蚀**：SLUB 上 double-free 可以让 freelist 指向同一对象，下一次分配可能返回**任意指针**（如果 freelist 被控制）。
- **Cross-cache attack**：当目标对象在专用 cache（如 `cred_jar`）中，无法直接用 `kmalloc-N` 覆盖时，通过耗尽 slab 页、迫使页返回 buddy allocator，再用其他 cache 重新占据同一物理页。
- **Freelist 硬化**：`SLAB_FREELIST_RANDOM` 随机化 slab 内分配顺序，`SLAB_FREELIST_HARDENED` 对 freelist 指针做 XOR 编码（类似 glibc safe-linking），直接影响喷射可靠性。

## 第 4 章 提权原语：cred、commit_creds 与 modprobe_path

**核心内容**：拿到任意写或 RIP 控制之后，**最终要把权限变成 root**。这一章聚焦两个最常用的终点：直接改 `cred`，以及劫持 `modprobe_path`。

**必须覆盖的点**：

- **`cred` 直接覆盖**：定位 `current->cred`，将 `uid/euid/gid/egid` 置 0 即可提权，无需调用 `commit_creds`。`cred_jar` 的对象大小为 184 字节，`objs_per_slab=42`（典型 Ubuntu 6.17 配置），是 cross-cache 或同 cache 覆盖的常见目标。
- **标准 ROP 提权链**：`commit_creds(prepare_kernel_cred(NULL))`。`prepare_kernel_cred(NULL)` 创建带 root 权限的新 cred(高版本内核不可用)，`commit_creds` 将其安装到当前进程。
- **`modprobe_path` 覆盖**：`modprobe_path` 是内核 `.data` 中的全局字符串（默认 `/sbin/modprobe`）。将其改写为攻击者控制的脚本路径，触发未知格式二进制执行，内核会以 root 调用该路径，脚本中完成 `chmod` / 读 flag。需注意 `STATIC_USERMODEHELPER` 会阻断该技术。
- **选择逻辑**：有任意写且能定位 `cred` → 直接改 `cred`，最稳定；有 RIP 控制但没有任意写 → ROP `commit_creds` 或覆盖 `modprobe_path`（后者需要 leak 到 `.data` 地址）。

## 第 5 章 控制流劫持：ret2usr 与内核 ROP

**核心内容**：当漏洞提供了**函数指针覆盖**或**返回地址覆盖**时，如何接管 RIP 并执行提权逻辑。

**必须覆盖的点**：

- **ret2usr**：在没有 SMEP/SMAP 的情况下，将内核函数指针直接指向用户态映射的 shellcode。这是最原始的内核控制流劫持技术；一旦开启 SMEP，该路径失效。
- **内核 ROP 的必要性**：SMEP 阻止内核执行用户页，SMAP 阻止内核直接读写用户页，因此 ROP 链必须**完全位于内核空间**（堆喷的 `msg_msg`、`pipe_buffer` 数据区，或内核栈上可控制的内容）。
- **栈迁移**：当可控数据在堆上而非栈上时，用 `leave; ret` 或 `xchg esp, eax` 等 gadget 将栈指针迁移到堆上的 ROP 链。
- **返回用户态**：ROP 提权完成后，不能简单地 `ret` 回用户态。需要经过 KPTI trampoline（`swapgs_restore_regs_and_return_to_usermode`），或在无 KPTI 时手动构造 `swapgs; iretq` 序列，恢复用户态 CS/SS/RFLAGS/RSP/RIP。

## 第 6 章 栈与竞态：栈溢出、double-fetch、race

**核心内容**：堆利用之外的两类重要漏洞面，在真实 CVE 和 kernelCTF 中占比不容忽视。

**必须覆盖的点**：

- **内核栈溢出**：内核栈通常 16 KiB（x86-64），没有用户态那样的 guard page 隔离；历史上默认不启用栈金丝雀，现在虽有 `-fstack-protector`，但并非全量覆盖。典型来源是 `copy_from_user` 长度可控。利用需要金丝雀 leak（或绕过）+ KASLR 绕过 + ROP。
- **Double-fetch**：用户指针被内核访问两次——第一次验证，第二次使用；攻击者在两次访问之间通过另一线程修改数据。经典模式：先验证 `size`，再 `copy_from_user` 时 `size` 已被改大 → 堆溢出。可利用 `userfaultfd` 或 FUSE 拉长窗口。
- **Race condition**：自旋锁/互斥锁的释放-重获间隙、缺失锁保护、或 COW 路径的时序窗口（DirtyCOW 类）。利用需要多线程 pin 核、扩大窗口或使用 `userfaultfd` 精确控制时序。

## 第 7 章 保护机制与绕过：KASLR / SMEP / SMAP / KPTI / FGKASLR

**核心内容**：现代内核 PWN 的“门槛层”。不了解保护状态， exploit 无法稳定；了解之后，绕过路径基本是模块化的。

**必须覆盖的点**：

| 保护 | 作用 | 绕过基线 |
| --- | --- | --- |
| **KASLR** | 随机化内核代码/数据基址 | 栈 leak、堆对象 leak、`msg_msg` 越界读、侧信道 |
| **SMEP** | 内核态不可执行用户页 | 内核 ROP；CR4 翻转（需 native write gadget） |
| **SMAP** | 内核态不可访问用户页 | ROP 链放在内核堆；用 `stac` / `clac` gadget |
| **KPTI** | 用户页表与内核页表分离 | `swapgs_restore_regs_and_return_to_usermode` trampoline |
| **FGKASLR** | 函数粒度的 `.text` 随机化 | 利用未随机化的 `.text` 区段或 `__ksymtab` 相对偏移解析 |

- **FGKASLR 的特殊性**：它不是整体基址随机化，而是函数级重排。稳定 gadget 和 `__ksymtab`（导出符号表）的相对偏移是常见突破口。
- **保护状态的第一动作**：拿到题目后**先读 `run.sh`**，确认 `smep` / `smap` / `kpti` / `kaslr` / `oops=panic` 的开关状态，再决定利用路线。
- **`oops=panic` 的影响**：任何导致内核 oops 的错误都会直接 panic，exploit 必须**一次成功**，调试时可以先去掉该参数降低难度。

## 第 8 章 实战模板：从漏洞到稳定 exploit

**核心内容**：把前七章的能力收敛为一个可复用的 exploit 骨架，并建立“先 leak、再原语、后提权、最后稳定返回”的工程化习惯。

**必须覆盖的 exploit 骨架结构**：

```c
// 0. 保存用户态上下文（用于最终返回）
save_state();

// 1. 打开漏洞设备
int fd = open("/dev/vuln", O_RDWR);

// 2. Leak（如有 KASLR）
//    - 利用漏洞读内核指针 / msg_msg 越界读 / pipe_buffer 残留
//    得到 kernel_base 或 cred 地址

// 3. 构建原语
//    - 堆 UAF：free 目标 -> slab spray 替换对象
//    - 任意写：覆盖函数指针 / cred / modprobe_path
//    - RIP 控制：构造 ROP 链到内核堆

// 4. 提权
//    commit_creds(prepare_kernel_cred(NULL))
//    或 cred->uid = 0
//    或 overwrite modprobe_path

// 5. 干净返回用户态
//    KPTI trampoline / swapgs; iretq

// 6. 起 shell / 读 flag
system("/bin/sh"); //推荐使用SYS_execve系统调用起 shell，避免栈平衡
```

**稳定化清单**：

- 在 `nokaslr` 下验证 exploit 逻辑，再开启 KASLR 调试 leak。
- 堆喷数量需要根据 `objs_per_slab` 和 slab 页大小估算，不是越多越好；过多喷射可能触发内存压力或打乱 per-CPU freelist 布局。
- 如果目标环境有 `oops=panic`，在触发漏洞前完成所有可能失败的准备（leak 失败应干净退出，而不是让内核 panic）。
