---
comments: true
---

# Python程序逆向

> REVERSE · 知识域。Python 打包/编译产物的还原。标签:**Pyinstaller程序解包**、**PYC反编译**、**PYD逆向**、**Nuitka程序逆向**、**其他Python程序逆向**。

## 触发特征

- `file`/运行报错提示 Python;exe 打包产物(python3x.dll、_MEIPASS)。

## Pyinstaller程序解包

- 识别:运行报错含 `_MEIPASS`、exe 内含 `pyi` 特征。
- 解包:pyinstxtractor.py → 得 pyc(需补 magic header——高版本缺头部);`pyinstxtractor-ng` 自动。
- 解包后:主逻辑在 `xxx.pyc`(与 exe 同名);资源在 `PYZ-00.pyz` 解出。
- 版本对齐:解出的 pyc 需对应 Python 版本反编译(魔数表)。

## PYC反编译

- 反编译器选择(按版本):`uncompyle6`(≤3.8)、`decompyle3`、`pycdc`(新版兼容)、`pylingual`(在线,新版)。
- 反编译失败 → 读字节码:`dis.dis()` + `xdis`(跨版本);操作码重映射题(→ [低级语言分析](low-level-lang.md))。
- Pyarmor 加壳:运行时解密字节码;静态解包方案(1shot 脚本族:恢复 code object);动态:hook `exec`/`eval` dump code(`marshal.loads` 后 `dis`)。
- `marshal` 层分析:code object 直接反汇编,跳过反编译器。

## PYD逆向

- PYD = Windows 下的 CPython 扩展(Cython/C 编译)。
- 分析:IDA 打开 → 找 `PyMethodDef` 表恢复函数名与入口;`PyArg_ParseTuple` 解参数。
- Cython 产物:大量 `__pyx_*` 符号,可读性尚可;纯 C 编译无符号 → 按调用约定逆。
- 导出函数直接用 ctypes/unicorn 调用当黑盒(免逆加密细节)。

## Nuitka程序逆向

- 识别:Nuitka 特征字符串("__compiled_")、运行时模块名。
- 难点:编译为 C 后再编译,源码级信息大量丢失。
- 思路:
  1. 定位主函数(字符串引用/`__main__` 模块初始化)。
  2. 常量表恢复:Nuitka 常量池(字符串/数值集中存放)。
  3. 模块存根注入(X-MAS CTF 2018:注入伪造 Python 模块劫持 import)。
  4. 动态 hook:运行时 Frida/调试器抓比较函数。

## 其他Python程序逆向

- **Cython 源码型**:build 产物附 `*.c` 时直接读。
- **py2exe**:解包与 PyInstaller 类似(unpack 工具族)。
- **embeddable 分发**:python 目录整体附带 → 直接找 pyc。
- **Nuitka/Pyarmor 双层**:先剥外层保护再回常规流程。
- **内存取证恢复源码**:pyrasite 注入取内存中运行源码(Insomni'hack 2017)。
- **服务端 marshal 注入**(pwn 联动,→ [Misc](../misc/index.md))。

## 工具速查

```bash
python pyinstxtractor.py target.exe
pycdc main.pyc > main.py
uncompyle6 main.pyc
pip install xdis    # 跨版本字节码
```

## 转向

- PYD 主体是 C 加密 → [加密与解密](crypto-in-reverse.md);pyjail 类 → [Misc](../misc/index.md)
