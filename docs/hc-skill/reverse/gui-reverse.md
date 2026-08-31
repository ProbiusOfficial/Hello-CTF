---
comments: true
---

# GUI程序逆向

> REVERSE · 知识域。图形界面程序的逆向:事件流定位与框架识别。标签:**MFC逆向**、**Qt逆向**、**其他GUI程序逆向**。

## 触发特征

- 题目是带界面的 exe(点击/输入框/按钮触发校验)。
- 直接看 main 找不到逻辑 —— 逻辑在消息处理/信号槽里。

## MFC逆向

- **消息映射(Message Map)**:`BEGIN_MESSAGE_MAP` 宏展开的静态表 —— 找 `AfxWndProc` → 定位 `CWnd::WindowProc` → 查消息映射表(ON_BN_CLICKED 等)找按钮处理函数。
- 事件处理器定位:WhiteHat 2015 消息映射调试法(在 CWnd::OnCmdMsg 下断看分发)。
- 对话框事件:MFC Dialog 的 DDX/DDV 数据交换;资源编辑器(ResHacker)看控件 ID → 对照 `ON_BN_CLICKED(IDC_BUTTON1, &Handler)`。
- 关键:控件 ID ↔ 处理函数映射,字符串引用反查。

## Qt逆向

- **信号槽**:`connect(sender, SIGNAL, receiver, SLOT)` —— 字符串表里 `1slot名`/`2signal名` 元对象信息(metaobject)。
- 识别:Qt 字符串特征("qt_meta_stringdata")、QWidget 导入。
- 定位逻辑:`QMetaObject::activate` 下断看槽调用;`QMetaObject` 静态数据中槽索引。
- QML 应用:`.qml` 文件可解析(资源里),逻辑常在 JS 层;资源释放(qrc)。
- PyQt/PySide:Python 层逻辑(→ [Python程序逆向](python-reverse.md));pyinstaller 解包后直接看 .pyc。

## 其他GUI程序逆向

- **Win32 原生**:GetMessage/DispatchMessage 循环 + `WndProc` switch;DialogProc;控件 ID 反查。
- **Electron**:app.asar 解包(npm 工具)→ JS 层审计(→ [WEB-JS](../web/js.md));native 模块配合分析(RootAccess2026)。
- **游戏引擎**:Unity(Mono → dnSpy;IL2CPP → Il2CppDumper)、Unreal(蓝图+UBT 产物)、Godot(资源解包)、Roblox place 文件。
- **Delphi/VB**:专有运行时与窗体资源(DeDe/VB 反编译器)。
- **Java Swing/JavaFX**:jar 反编译(→ [高级语言逆向](high-level-lang.md))。
- **Flutter 桌面**:Dart AOT → Blutter。

## 通用技巧

1. 资源先行:按钮文本/窗口标题字符串引用 → 事件函数。
2. 运行时:API 监控(BP GetWindowTextA/SetDlgItemText)抓输入输出点。
3. 界面逻辑一般"薄",校验函数与加密才是主体(→ [加密与解密](crypto-in-reverse.md))。
4. 控件内容联动 patch:改界面判定后让程序打印 flag。

## 工具速查

```bash
# ResHacker / ResourceHacker 看资源
# spy++ 看窗口类与消息流
# dnSpy(Unity Mono) / Il2CppDumper(Unity IL2CPP)
```

## 转向

- 主体逻辑在 native → [高级语言逆向](high-level-lang.md);资源里藏文件 → [Misc-文件结构](../misc/file-structure.md)
