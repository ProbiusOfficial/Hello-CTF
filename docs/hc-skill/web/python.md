---
comments: true
---

# Python

> WEB · 语言专题。Python Web 栈(Django/Flask/Tornado/web.py)及解释器特性利用。标签:**命令执行**、**沙箱逃逸**、**反序列化**、**模板注入**、**文件读取**、**原型链污染**(Python 侧等价:属性链遍历)。

## 触发特征

- Flask/Django 特征头、`Werkzeug` debug 页、`Jinja2` 报错。
- 题目 eval/exec 用户输入(计算器、表达式题目)、pickle 传输对象。

## 命令执行

- 直连入口:`eval()/exec()/os.system()/subprocess`。沙箱限制见"沙箱逃逸"。
- `str.format()` 属性遍历信息泄露:`'{0.__class__.__init__.__globals__}'`(PlaidCTF 2017);f-string 格式注入盲提取(Meepwn CTF Quals 2018)。
- `web.py reparam()` eval + `__subclasses__` 在 builtins 被清空时的利用(HITCON 2018)。
- LaTeX 注入 RCE:`\immediate\write18`(Hack.lu CTF 2012),受限时用 `mpost` 绕 write18 限制(33C3 2016)。

## 沙箱逃逸

- 经典链:`__class__.__base__.__subclasses__()` 找 `os._wrap_close`/`file`/`warnings` 类 → `__init__.__globals__['sys'].modules['os']`。
- 关键字过滤:`getattr(builtins,'ev'+'al')`、`__import__('o'+'s')`、`chr()` 拼接;`dir()` 属性枚举绕 `__class__` 黑名单(InCTF 2018)。
- 更系统的 pyjail 逃生(装饰器链、`__loader__`、quine 等)→ 转 [Misc](../misc/index.md) pyjail 部分。
- Flask/Werkzeug debug 模式:PIN 由用户名/modname/appname/flask路径/mac/机器id 派生,容器内可读时本地算 PIN 进交互 console。

## 反序列化

- `pickle.loads(user_data)` → `__reduce__` RCE;payload 包装:`base64(b'')`、`ROT13(base64(pickle))`(TAMUctf 2019)、STOP 操作码剥离实现链式 pickle(VolgaCTF 2013)。
- Werkzeug SecureCookie 用 pickle 存储,泄露 `SECRET_KEY` 后伪造 → RCE(CSAW 2018 Finals)。
- `python-marshel`/`marshal` 代码注入(iCTF 2013);`PyYAML.load` 非 safe_load → `!!python/object/apply:os.system`。
- 防御识别:框架如果只允许反序列化白名单类,转对象注入/属性污染思路。

## 模板注入

- Jinja2:`{{7*7}}` 探测 → `{{config}}` 泄露 SECRET_KEY → RCE payload `{{ ''.__class__.__mro__[1].__subclasses__() }}` 定位 subprocess;引号被过滤用 `__dict__.update()` 或 request 对象传参(ApoorvCTF 2026);`globals.__self__.exec()` 字符串拼接绕过(InCTF 2018)。
- Mako:`<%import os%>` 直接执行;Tornado:`{{handler.settings}}` 泄露 cookie_secret。
- Flask 错误页把用户输入回显进模板 → XSS 转 SSTI 链(SECUINSIDE 2016)。

## 文件读取

- `send_file()/send_from_directory` 路径穿越;`os.path.join` 以 `/` 开头的参数重置路径(拼接绕过)。
- 读取点清单:`/proc/self/environ`、`/proc/self/cmdline`、`/app/app.py`、Docker socket 探测 `/proc/self/mounts`。
- zip 解压未校验路径 → ZipSlip;zip 符号链接穿越(UTCTF 2024)。

## 工具速查

```bash
flask-unsign --decode --cookie '<c>'
flask-unsign --sign --cookie "{'admin':True}" --secret '<key>'
tplmap -u 'URL?name=*'           # SSTI 自动化
```

## 转向

- 逃逸受限在 pyjail 环境 → [Misc](../misc/index.md)
- 模板属于 Go/Ruby/Java → 对应语言页
