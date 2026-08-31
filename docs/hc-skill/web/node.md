---
comments: true
---

# Node

> WEB · 语言专题。Node.js 服务端与 npm 生态攻防。标签:**命令执行**、**语言特性**、**原型链污染**、**大小写特性**、**VM沙箱逃逸**、**模板注入**。

## 触发特征

- `X-Powered-By: Express`、`connect.sid`、`npm`/`package.json` 泄露、JS 为主的前后端同构应用。

## 语言特性

- 弱等与 NaN:`x!=x` 判 NaN、`[]+{}` 拼接特性、`parseInt` 前导解析。
- 大小写特性:`req.headers` 键全小写化;路径判断 `toLowerCase()` 后与原始路径不一致 → 绕过(turkish-I 类区域设置坑);正则 `i` 标志下的 `k`字符 (`\u0130`) 特例。
- `Object.assign`/lodash `merge`/`defaultsDeep` 递归合并 → 原型链污染入口。
- `child_process` 参数数组化差异;`eval`/`Function` 动态执行面。
- Buffer/`toString('latin1')` 编码错位用于 CRLF 注入(Uvicorn 等 N-Day 同类思路)。

## 原型链污染

- Payload:`{"__proto__":{"isAdmin":true}}`、`constructor.prototype`(防御了 `__proto__` 时换道)。
- 常见向量:JSON body 递归合并、`qs`/`body-parser` 嵌套参数、`path` 参数对象。
- 已知漏洞库:flatnest 循环引用绕过(CVE-2023-26135)、lodash merge 系列、jquery `$.extend(true,...)`。
- Gadget 链:污染后劫持库配置 → RCE,如 Lodash 污染到 Pug AST 注入(VuwCTF 2025)、`NODE_OPTIONS` 环境变量注入、EJS `outputFunctionName`、Handlebars 模板编译选项。
- 检测:`(new Error()).__proto__` 或 GET 参数 `?__proto__[polluted]=1` 后验证全局对象。

## VM沙箱逃逸

- `vm.runInNewContext(code)` 逃逸经典:`this.constructor.constructor('return process')().mainModule.require('child_process')`。
- `vm2` 新版与 ESM 场景:CVE-2025-61927 类 ESM 兼容逃逸;CommonJS `require` hook 逃逸;happy-dom 环境 `document.write` 的作用(vm 沙箱与宿主交互面)。
- 完整链:原型链污染 → VM 逃逸 → RCE(4llD4y);沙箱内 `process` 不可得时用 `Buffer.prototype` 链或异常对象链。
- `Function`/`setTimeout` 字符串执行本身就是隐式 eval,常作为逃逸跳板。

## 模板注入

- EJS:`<%= 7*7 %>` 探测;RCE 走 `settings['view options']` 污染或 `locals` 对象。
- Pug/Nunjucks/Handlebars:AST 注入、`lookupGetter` gadget;Nunjucks `{{range.constructor("return global.process.mainModule...")()}}`。
- 模板 + 原型链污染组合是 Node 题的主流难度分层。

## 命令执行杂项

- `child_process.exec` 字符串拼接 → 命令注入(分号、反引号、`$()`);`execFile` 数组参数注入文件名。
- `--inspect` 调试端口暴露 → 直接 RCE;`node-serialize` 反序列化 `"_$$ND_FUNC$$_"` IIFE 执行。

## 转向

- 前端 JS 逆向 → [JS](js.md);Express 中间件 ACL 绕过 → [HTTP请求](http-request.md)
