---
comments: true
---

# Windows相关

> WEB · 知识域。Windows/IIS/.NET 栈的 Web 攻防。标签:**Aspx反序列化**、**文件通配符**、**IIS漏洞**、**NTFS流绕过文件上传**。

## 触发特征

- `IIS/x.x`、`ASP.NET`、`.aspx/.asmx/.ashx` 页面、Windows 报错路径(`C:\inetpub`)。
- 域内环境提示(配合 AD 攻击,→ [渗透测试](../pen/index.md))。

## Aspx反序列化

- **ViewState**:未启用 MAC 校验或泄露 `machineKey` → 伪造 ViewState 直接 RCE;`ysoserial.net` 生成:`ysoserial.exe -p ViewState -g TextFormattingRunProperties -c "cmd" --path=/ --apppath=/ --validationalg=sha1 --validationkey=...`。
- **JSON.NET TypeNameHandling**:开启 `TypeNameHandling.All/Auto` 时 `$type` 指向 gadget 类(ObjectInputFormatCheck 防御时找白名单旁路)(DefCamp 2017)。
- **BinaryFormatter/Blosxom 系**:老 .NET 服务常见;`ysoserial.net -g ActivitySurrogateSelector` 等 gadget。
- WebResource.axd / ScriptResource.axd 的老漏洞打点。

## 文件通配符

- Windows 通配符语义:`?` 单字符、`*` 任意串——文件存在性判断 `File.Exists("C:\inetpub\wwwroot\*.aspx")` 可被通配符利用探测/绕过黑名单后缀。
- 8.3 短文件名:`PROGRA~1`、`INDEX~1.ASP` 枚举存在性(Tokyo Westerns 2016);IIS 短文件名漏洞(iis_shortname_scanner)逐字符猜目录文件。
- 大小写不敏感:`INCLUDE.PHP` = `include.php`;`ADS` 备用数据流隐写(→ [Misc-其他隐写](../misc/other-stego.md))。

## IIS漏洞

- IIS 6.0 解析:`xx.asp;.jpg` 分号截断、`/xx.asp/` 目录内任意后缀按 asp 解析。
- IIS 7.x + FastCGI:与 Nginx `cgi.fix_pathinfo` 同类,`xx.jpg/a.php` 解析。
- HTTP.sys 远程代码执行 MS15-034(`Range: bytes=0-18446744073709551615` 探测);WebDAV 恶意方法、PUT 上传(proppatch/movet)。
- 短文件名爆破脚本 + `~` 特征枚举隐藏文件。

## NTFS流绕过文件上传

- 上传 `shell.asp::$DATA` 绕过黑名单,保存为流后 `shell.asp` 可被解析(IIS 场景)。
- `shell.jpg::$DATA.jpg`、`shell.asp;.jpg` 组合变形。
- 流的检测与读取:`dir /r`、`streams.exe`;取证视角见 [Misc-其他隐写](../misc/other-stego.md)。

## .NET 栈其他考点

- CSRF/ViewState-less 场景:`__EVENTVALIDATION` 伪造。
- XSLT(Razor/XslCompiledTransform)`document()` 函数任意读。
- 服务枚举:`/trace.axd`、`/elmah.axd`、`/web.config` 备份泄露。

## 转向

- 拿下 webshell 后 → [渗透测试](../pen/index.md) 提权/域内
- 内存取证里的 Windows 伪影 → [Misc-取证](../misc/forensics.md)
