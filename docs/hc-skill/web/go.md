---
comments: true
---

# Go

> WEB · 语言专题。Go/Golang Web 服务与语言特性利用。标签:**模板注入**、**命令执行**。

## 触发特征

- Go 特征响应头/报错格式、`text/template`、`html/template`、gin/echo 框架指纹、Go 二进制服务。

## 模板注入

- `text/template` 语义:字段访问而非方法调用,无法直接 `exec`——利用面在"能访问的对象图"上:
  - `{{.Env}}`、`{{.Flag}}` 直接读上下文字段(题目常把敏感数据挂在渲染上下文)。
  - 借助挂载的 `os.File`/`exec.Cmd` 类型字段调用方法(若上下文含)。
- **Pongo2**(Go 版 Jinja):经路径穿越控制模板文件内容 → 完全 SSTI → `{{ }}` 内调用受限;配合文件上传写模板文件完成 RCE(Nullcon 2026)。
- html/template 上下文编码对 `{{}}` 无影响,但 JS 上下文注入点可 XSS。
- 模板路径可控(如 `render tmpl=用户输入`)→ 任意文件读(`{{template "/etc/passwd"}}` 类)或包含攻击者模板。

## 命令执行

- `os/exec` 注入面:`exec.Command("sh","-c",userinput)` 拼接即注入;`Command(name, args...)` 数组形式不解析 shell 元字符,但参数本身被下游解析时仍可注入(如 git `-c` 参数、tar 文件名注入——CyberSecurityRumble 2016:tar 文件名命令注入)。
- Go rune/byte 长度错位:`len()` 按 byte、range 按 rune,过滤按 byte 计数而校验按 rune → 构造多字节字符挤掉过滤词(VuwCTF 2025 命令注入同源)。
- net/http 上传落盘文件名未净化 → 命令注入点;`os.OpenFile` 路径拼接穿越。
- CGO/插件场景少见于 CTF;Go 二进制本身的漏洞 → [Reverse](../reverse/index.md)。

## 解析与并发特性

- `net/url` 解析差异:`#` 片段截断、分号参数处理 → 与上游代理分歧做 ACL 绕过或 SSRF(见 [HTTP请求](http-request.md))。
- map 遍历无序导致的逻辑竞态;`context` 超时被用作"盲注时间窗"。
- JSON 处理:字段标签大小写匹配宽松(`json:"Name"` 接受 `name`)→ mass assignment。

## 工具速查

```go
// 探测 text/template 可访问字段
{{.}}
{{printf "%+v" .}}
```

## 转向

- Go 编写的 Pwn/逆向题二进制 → [Reverse](../reverse/index.md)
