---
comments: true
---

# JS

> WEB · 语言专题。前端 JavaScript 攻防:混淆还原、客户端逻辑逆向。标签:**混淆逆向**。与 [XSS](xss.md) 互补:本页面向"读懂并还原 JS",XSS 面向"注入执行 JS"。

## 触发特征

- 题目要求从前端 JS 中提取密钥、隐藏接口、加密逻辑。
- 页面脚本被 JSFuck / AAEncode / JJEncode / obfuscator.io 混淆。

## 混淆类型与还原

| 混淆 | 识别特征 | 还原方式 |
| --- | --- | --- |
| JSFuck | `[]()[+!+[]]` 全符号 | 浏览器控制台直接 eval 打印,或 `jsfuck` 库 decode |
| AAEncode | `ﾟωﾟﾉ= /｀ｍ´)ﾉ ~┻━┻` 日文颜文字 | 控制台执行取返回函数 |
| JJEncode | `$=~[];$={___:++$,...}` | 控制台执行 |
| obfuscator.io | `_0x4c2a` 十六进制变量名+字符串数组 | AST 工具 `obfuscator-io-deobfuscator`,或控制台逐函数解 |
| 自定义 VM/解释器 | 页面实现 opcode 分发 | 静态读 dispatch 表,或 hook 解释函数打印执行流 |

## 关键信息提取点

- 加密函数:`CryptoJS.AES.encrypt(data, KEY)` — KEY/IV 常硬编码在前端或由前端"伪随机"生成(随机数可预测 → [Crypto-MT19937](../crypto/mt19937.md))。
- 请求签名:`sign = md5(timestamp+token+params)` 之类算法,直接照抄到本地脚本重放。
- 隐藏 API:axios/fetch 的 baseURL、路由表、GraphQL endpoint。
- 泄露的 secret 用于客户端 HMAC 绕过(Codegate 2013:JS 中硬编码密钥本地重签)。
- React 状态提取:`__reactInternalInstance$` 遍历组件树拿 props/state(RCTF 2018)。

## 调试手段

- 断点前置:Sources 面板对 `JSON.parse`、`crypto.subtle`、`atob` 下断。
- Hook:重写 `Function.prototype.call` / `String.prototype.replace` 打印参数(注意 `replace` 回调二次执行漏洞——开发者用 replace 做过滤时可被注入 `$'` 引用匹配串)。
- AST 级:babel 解析后常量折叠、控制流还原。
- WASM 出现时 → 转 [Reverse](../reverse/index.md) WASM 分析;Node 服务端逻辑 → [Node](node.md)。

## 工具速查

```js
// 控制台快速解码
console.log(Function("return " + jsfuckCode)());
// hook fetch 看全部请求
const o = window.fetch; window.fetch = (...a) => { console.log(a); return o(...a); };
```
