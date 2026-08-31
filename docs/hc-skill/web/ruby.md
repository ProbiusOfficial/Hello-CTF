---
comments: true
---

# Ruby

> WEB · 语言专题。Ruby/Sinatra/Rails 栈与解释器特性利用。标签:**全局变量**、**模板注入**。

## 触发特征

- `Rack` cookie(` Rack::Session::Cookie` base64+签名)、`Sinatra`/`Rails` 特征、ERB 模板报错。

## 全局变量与解释器特性

- 全局变量滥用:`$SAFE` 老沙箱机制(SRuby<2.6 已废弃,出现即提示老版本)、`$LOAD_PATH` 劫持、`ENV` 泄露。
- `Regexp.escape` 多字节字符绕过转义(Square CTF 2017)——多字节首字节吃掉反斜杠,后续字符逃出转义。
- `instance_eval` 代码注入:eval 上下文逃逸,关键词黑名单用 `send('ev'+'al',...)`、`public_send` 绕过。
- `ObjectSpace.each_object` 内存扫描找 flag/密钥(Tokyo Westerns 2016)——无需 RCE 的"读内存"式解题。
- `TracePoint.trace` 沙箱逃逸(HITCON 2017):宿主注册的钩子在受限上下文外执行,借其拿到干净 `Kernel`。
- `Array#unpack` 越界读 CVE-2018-8778(Codegate 2019);Ruby Marshal 反序列化(`Marshal.load` 任意对象图)。
- `open("|cmd")` 管道语义 RCE——文件名以 `|` 开头即执行命令(Ruby 经典)。

## 模板注入

- **ERB**:`<%= 7*7 %>` 探测 → `<%= `id` %>` 反引号执行;`TrustedBlank` 场景走 `Sequel::DATABASES` 拿连接配置再扩展(BearCatCTF 2026)。
- **Slim/HAML**:语法不同payload不同,思路一致:定位 `eval`/`Kernel` → 执行。
- Rails 动态渲染 `render params[:tpl]` → 任意模板文件渲染或代码注入。

## 命令执行与杂项

- `system/spawn/backtick/Open3` 注入点;`Kernel#open` 管道坑同样适用于 `File.read("|cmd")` 老版本。
- Cookie 伪造:`Rack::Session::Cookie` secret 爆破后 Marshal 注入(新版默认 JSON 序列化则转向)。
- YAML.load 非 safe_load → `!ruby/object:Gem::Installer` 系列 gadget。

## 工具速查

```bash
# Rack cookie 签名爆破
# ruby: require 'rack'; Rack::Session::Cookie 可解可签
irb -e 'puts ERB.new("<%= `id` %>").result'
```

## 转向

- ERB 属于 SSTI 大类,横向对比各语言 payload → 对应语言页
