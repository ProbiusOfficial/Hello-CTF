---
comments: true
---

# JS逆向

在「敏感信息泄露」一章里，我们通过查看 JS 源码找到了硬编码的 key、接口路径等信息。但实际站点和稍难一点的 CTF 题里，JS 往往是压缩、混淆、打包过的，关键逻辑（比如登录参数的加密）藏在几千行代码里，光看是看不出所以然的。

JS 逆向的核心思路就一句话：**不要通读代码，让浏览器替你跑代码，在关键位置停下来看**。本章讲四件基本功：DevTools 调试、加解密定位、webpack 扣代码、AST 解混淆概念，够用即止。

## 浏览器 DevTools 调试基本功

按 `F12` 打开开发者工具，JS 逆向主要用到三个面板：

- **Sources**：看源码、下断点、看调用栈。
- **Console**：执行临时代码、做 Hook。
- **Network**：抓请求，确认哪个参数是加密的（比如 `?sign=a1b2c3...`）。

### 断点

断点是逆向的起点。常用三种：

- **行断点**：在 Sources 里点行号，代码执行到这一行就暂停。
- **XHR 断点**：在 Sources 面板右侧的 `XHR/fetch Breakpoints` 里添加一个 URL 关键字（比如 `login`），只要发出包含该关键字的请求就会断住。这是最常用的——当你不知道加密代码在哪，但知道加密结果会随哪个请求发出去时，直接对请求下断。
- **事件断点**：`Event Listener Breakpoints` 里勾选 `click`、`submit` 等，点按钮时断在事件处理函数里，适合从「点登录按钮」这个动作顺藤摸瓜。

断住之后用右侧的调试按钮单步：`Step over`（跳过函数调用）、`Step into`（进入函数内部）、`Step out`（跳出当前函数）。把鼠标悬停在变量上能看到当前值。

### 调用栈（Call Stack）

断住后看右侧的 **Call Stack** 面板，它按「从内到外」列出了当前函数是被谁一层层调用的。逆向时的标准动作是：

1. 在加密参数出现的位置（或 XHR 断点处）断住；
2. 沿调用栈 **从下往上** 逐帧点击，观察每一帧的局部变量；
3. 找到「明文变成密文」的那一帧——它的上一帧变量还是明文，这一帧就变成密文了，加密函数就在这两帧之间。

比起在压缩后的代码里肉眼搜索，跟栈几乎不会迷路。

### Hook 关键函数

Hook 就是「偷梁换柱」：在目标代码执行前，把原函数替换成我们自己的包装函数，打印参数和返回值后再调用原函数。在 Console 里执行：

```javascript
// Hook JSON.stringify，凡是序列化的数据都打印出来
(function () {
    var _stringify = JSON.stringify;
    JSON.stringify = function (obj) {
        console.log('[JSON.stringify]', obj);
        return _stringify.apply(this, arguments);
    };
})();
```

注意 Console 里的 Hook 在页面刷新后就失效了。如果目标代码在页面加载阶段就执行（Hook 来不及注入），可以在 Sources 面板启用 `Overrides`（本地覆盖），把修改后的 JS 保存下来让浏览器加载本地版本；或者用抓包工具（如 mitmproxy）在响应里注入 Hook 代码。

常用 Hook 目标：`JSON.stringify` / `JSON.parse`、`btoa`、`String.fromCharCode`、`XMLHttpRequest.prototype.send`、以及确认加密库后的 `CryptoJS.AES.encrypt` 等。

## 前端加解密定位

面对一个加密参数（比如登录请求里的 `password` 是一串 hex），定位加密代码的套路是：

### 第一步：搜关键词

全局搜索（Sources 面板按 `Ctrl+Shift+F`）这些关键词：

- 参数名本身：`password`、`sign`、`encrypt`，这是最快的；
- 加密库特征：`CryptoJS`、`encrypt`、`decrypt`、`setPublicKey`；
- 编码特征：`btoa`、`atob`、`md5`、`sha1`。

压缩后的代码里函数名会被改成 `a.b.c(d)` 这种，但 **字符串常量不会被压缩**——参数名、`"AES"`、`"RSA"`、`"mode"` 这些字符串搜得到。

### 第二步：跟栈找 AES/RSA 入口

搜不到时就回到上一节的套路：对登录请求下 XHR 断点，跟调用栈找明文变密文的位置。

经验判断：

- 密文是 32 位 hex 且长度固定 → 多半是 MD5，直接拿去在线反查试试；
- 密文是 Base64 且长度是 16 的倍数 → 多半是 AES，去找 key 和 iv；
- 密文很长（几百字符 Base64）且代码里有 `setPublicKey`、`JSEncrypt` → 是 RSA，公钥一般就硬编码在 JS 里，加密不可逆，但你可以 **直接用它的公钥和库复现加密**，把密文换成任意明文的加密结果。

### CryptoJS 特征识别

CryptoJS 是最常见的前端加密库，压缩后也有明显指纹。搜到类似下面的代码基本就能确认：

```javascript
// AES 加密典型写法
CryptoJS.AES.encrypt(
    CryptoJS.enc.Utf8.parse(data),
    CryptoJS.enc.Utf8.parse(key),
    {
        iv: CryptoJS.enc.Utf8.parse(iv),
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
    }
).toString()
```

特征点：

- `CryptoJS.enc.Utf8.parse` / `CryptoJS.enc.Hex.parse`：把字符串转成 WordArray，每个 32 位整数按大端存储；
- `mode: CryptoJS.mode.xxx`、`padding: CryptoJS.pad.xxx`：模式和填充直接写在参数里，抄下来就行；
- `.toString()` 默认输出 Base64，`.toString(CryptoJS.enc.Hex)` 输出 hex。

确认参数后用 Python 复现（先 `pip install pycryptodome`）：

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

key = b'1234567890abcdef'   # 从 JS 里抄来的 key
iv = b'1234567890abcdef'    # 从 JS 里抄来的 iv
cipher = AES.new(key, AES.MODE_CBC, iv)
ct = cipher.encrypt(pad(b'admin123', 16))
print(base64.b64encode(ct).decode())
```

能复现出和请求里一样的密文，就说明你找对了。

## webpack 打包站点

### 识别与模块定位

现代站点常用 webpack 打包，特征是所有 JS 被裹进一个大的立即执行函数，里面长这样：

```javascript
(function (modules) {
    // webpackBootstrap：加载器
    function __webpack_require__(moduleId) { ... }
    return __webpack_require__(0);
})({
    0: function (module, exports, __webpack_require__) { /* 模块0 */ },
    1: function (module, exports, __webpack_require__) { /* 模块1 */ },
    // ... 几百个模块
});
```

每个模块就是一个函数，`__webpack_require__(模块id)` 相当于 `import`。业务代码藏在某个编号不起眼的模块里，全局搜索关键词依然是第一步；搜到后注意它处于哪个模块函数内。

### 扣代码思路

「扣代码」指把站点里的加密逻辑原样抠出来，在本地 Node.js 里跑，省去用 Python 重写。对 webpack 站点，套路是固定的：

1. **抠加载器**：把 `webpackBootstrap` 那一小段（`__webpack_require__` 函数）整个复制下来；
2. **抠模块**：把目标加密模块、以及它 `__webpack_require__` 依赖的模块，按原编号一个个复制进 `modules` 对象（缺哪个跑起来会报 `Cannot find module`，照着报错补）；
3. **补环境**：浏览器特有的 `window`、`document`、`navigator` 在 Node 里没有，在文件开头补上桩：

```javascript
// env.js：在 Node 里模拟浏览器环境
var window = global;
var navigator = { userAgent: 'Mozilla/5.0' };
var document = {};
```

4. **导出调用**：在文件末尾调用入口模块，拿到加密函数：

```javascript
// 假设加密函数在 23 号模块里
var enc = __webpack_require__(23);
console.log(enc.encrypt('admin123'));
```

本地 `node env.js` 能跑出和浏览器一致的密文，扣代码就成功了。CTF 里 webpack 题一般模块很少，手工抠比写通用工具快。

## AST 解混淆入门

### 混淆与 AST 思路

混淆代码长这样：变量名全是 `_0x1a2b`，字符串被编码成 `'\x61\x62\x63'` 或放进一个数组里用 `_0x1a2b[0]` 引用，还套着各种恒真恒假的花指令。肉眼读不动，但有个关键事实：**混淆不改变程序的功能，只改变写法**。浏览器能跑，说明代码里的一切信息都是可计算的。

AST（抽象语法树）是把代码解析成结构化节点树的表示。解混淆的思路就是：用工具把 JS 解析成 AST，在树上做「等价变换」（比如把 `'a' + 'b'` 直接算成 `'ab'`，把数组引用替换成真实字符串），再生成回代码。社区的主流方案是用 Babel 提供的三个包：

```bash
npm install @babel/parser @babel/traverse @babel/generator @babel/types
```

- `@babel/parser`：代码 → AST；
- `@babel/traverse`：遍历树，挂 visitor 函数匹配并修改节点；
- `@babel/generator`：AST → 代码。

一个最小骨架：

```javascript
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generate = require('@babel/generator').default;
const fs = require('fs');

const code = fs.readFileSync('obfuscated.js', 'utf-8');
const ast = parser.parse(code);

// 常量折叠：把 "a" + "b" 这种二元字符串拼接直接算出来
traverse(ast, {
    BinaryExpression(path) {
        const { left, right } = path.node;
        if (left.type === 'StringLiteral' && right.type === 'StringLiteral'
            && path.node.operator === '+') {
            path.replaceWith({
                type: 'StringLiteral',
                value: left.value + right.value
            });
        }
    }
});

fs.writeFileSync('deobfuscated.js', generate(ast).code);
```

这里不追求写全功能的解混淆器（那是另一个大话题），只需理解「解析 → 遍历改写 → 生成」这三板斧，遇到混淆题知道有这条路、能搜到对应的现成插件即可。

### 一个手工解混淆小例子

CTF 入门题的混淆往往手算就够了，不用上 Babel。看这段：

```javascript
var _0x4b2a = ['bG9hZGluZw==', 'ZmxhZ3tqc19yZXY=', 'aXNfZnVu'];
function _0x1c3d(i) {
    return atob(_0x4b2a[i]);
}
var check = function (s) {
    return _0x1c3d(1) + _0x1c3d(2) === s;
};
console.log(check('flag{js_rev_is_fun}'));
```

手工还原步骤：

1. **认清字符串数组**：`_0x4b2a` 里三个 Base64，在 Console 或本地 `atob` 解码：`loading`、`flag{js_rev`、`is_fun`；
2. **替换引用**：`_0x1c3d(1)` 就是 `'flag{js_rev'`，`_0x1c3d(2)` 就是 `'is_fun'`；
3. **代回逻辑**：`check` 实际是判断 `s === 'flag{js_rev' + 'is_fun'`，即 `'flag{js_revis_fun}'`。

还原后的等价代码只有一行：

```javascript
var check = s => s === 'flag{js_revis_fun'};
```

绝大多数入门混淆题的套路就是「字符串数组 + 索引引用 + 编码函数」，识别出这三件套，手工代换几分钟就能还原。

## CTF 例题：混淆 JS 登录校验

题目：一个登录页，输入任意密码都提示错误，只有一个 `login.js`（已按上节方法还原）：

```javascript
function encrypt(pwd) {
    var key = 'key12345';
    var out = '';
    for (var i = 0; i < pwd.length; i++) {
        out += String.fromCharCode(pwd.charCodeAt(i) ^ key.charCodeAt(i % key.length));
    }
    return btoa(out);
}

// 正确密码加密后应等于：
var target = 'FBBRVFkLVVNQWw==';
```

完整解题过程：

1. **审逻辑**：加密是「明文逐字节与循环 key 异或，再 Base64」。XOR 是自逆运算，解密就是同样的操作再来一遍；
2. **写解密脚本**：

```python
import base64

key = b'key12345'
ct = base64.b64decode('FBBRVFkLVVNQWw==')
pwd = bytes(c ^ key[i % len(key)] for i, c in enumerate(ct))
print(pwd.decode())   # 输出即正确密码
```

3. **拿 flag**：把解出的密码填进登录框，页面返回 flag。

这类题的考点不在密码学，而在「敢不敢读混淆 JS + 会不会跟栈/还原」。先用 DevTools 确认 `login.js` 是唯一的校验逻辑（Network 里没有真正的后端校验请求），再放心地纯本地解题。

## 实站例题：某登录接口的 AES 参数

场景：某站点登录请求中 `data` 参数是一串 Base64 密文，目标是写出能自动登录的脚本。

完整过程：

1. **定位**：Network 里确认 `POST /api/login` 携带加密 `data`；在 Sources 添加 XHR 断点 `api/login`，点击登录，断住；
2. **跟栈**：沿 Call Stack 往上翻，在第三帧看到局部变量里 `password` 还是明文、下一行变成了密文，锁定这一帧，找到：

```javascript
data: encryptParam(JSON.stringify({ u: username, p: password, t: Date.now() }))
```

3. **扒参数**：单步进入 `encryptParam`，确认是 CryptoJS 的 AES-CBC，`key = 'a1b2c3d4e5f60718'`，`iv = 'a1b2c3d4e5f60718'`（实际站点 key 往往就硬编码在附近，或藏在某个常量模块里——webpack 站点按上一节方法抠出该模块）；
4. **复现**：用前文「CryptoJS 特征识别」小节的 Python 脚本，把 key/iv/明文结构换成这里的，加密结果与抓包一致；
5. **自动化**：封装成「构造 JSON → AES 加密 → 发请求」的 Python 脚本，完成自动登录。

实站和 CTF 的区别只在于：实站的代码量更大、key 藏得更深，但「断点 → 跟栈 → 抄参数 → 复现」这条主线完全一样。

## 小结

- 逆向靠 **调试** 不靠硬读：XHR 断点 + 调用栈是定位加密代码的万能钥匙；
- 压缩不会动字符串，**搜关键词** 永远先试；
- 认出 CryptoJS / JSEncrypt 的特征，把 key、iv、mode、padding 抄下来用 Python 复现；
- webpack 站点按「加载器 + 所需模块 + 浏览器环境桩」三段式扣代码；
- 混淆代码用 AST 三板斧（parse → traverse → generate）做等价还原，入门题手算即可。

掌握了这些，再回头看「敏感信息泄露」里直接读 JS 找 key 的题，以及「Web入门题单」里的前端题，就是同一个技能树的不同难度了。
