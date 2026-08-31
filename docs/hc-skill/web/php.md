---
comments: true
---

# PHP

> WEB · 语言专题。PHP 特性利用是国内 CTF Web 的最大票仓。标签:**弱类型特性**、**其他语言特性**、**变量覆盖**、**PHP特性**、**反序列化**、**伪协议**。

## 触发特征

- `PHPSESSID`、`X-Powered-By: PHP/x.y`、`.php` 后缀、报错页带 `Warning:`。
- 源码审计题给出 PHP 片段,考比较、哈希、正则、序列化。

## 弱类型特性

- `==` 松散比较:`"admin"==0`(PHP7)、`0e` 科学计数法哈希相等(`md5('2406107085')=='0e...'`)、`true` 与任意字符串相等。
- `md5()/sha1()` 数组绕过:传 `a[]=1&a[]=2` 返回 NULL,`md5($a)==md5($b)` 成立;`strcmp`、`strpos`、`preg_match` 同理(AceBear 2018:`hash_hmac` 数组参数返回 NULL 绕过校验)。
- `in_array` 第三参不严 → 类型混淆;`switch` 松散比较;`json_decode` 后的弱比较。

## PHP特性(过滤对抗)

- `strpos` 子串黑名单可嵌入绕过(TUCTF 2018);全角字符 `$` 绕过 `^` 锚点正则(Hack.lu CTF 2018)。
- PCRE 回溯上限 100 万次,超长 payload 使 `preg_match` 返回 false 跳过过滤(SECUINSIDE 2017)。
- `parse_str()` 变量注入(TokyoWesterns 2018);`extract()`/`register_globals` 变量覆盖(SecuInside 2013);`$$var` 可变变量(bugs_bunny 2017)。
- 顺序替换过滤绕过:替换即消除的循环逻辑用嵌套构造(Tokyo Westerns 2017);双写、编码、递归 `....//`(35C3 2018)。
- `(int)` 强转取前导数字做路径穿越(35C3 2018);`log()/INF` 数学相等 + 递归 urldecode(Pragyan CTF 2019)。

## 变量覆盖

- `extract($_GET)` / `parse_str` 覆盖 `$password`、`$flag` 等业务变量。
- `$$` 动态变量拼接;`compact()` 反向泄露;`import_request_variables`(老版本)。
- foreach 引用遍历导致的键值覆盖(常见于框架路由分发)。

## 反序列化

- `unserialize()` → POP 链:从 `__destruct`/`__wakeup` 入口找 gadget;常见链:各种 composer 组件(参考 phpggc)。
- 序列化长度篡改:过滤词替换导致长度膨胀,用长属性名吃掉后续字段(0CTF 2016)。
- `SoapClient.__call()` 发 CRLF 请求 → SSRF(N1CTF 2018);`unserialize` + `curl` 双重 URL 编码 LFI(FireShell CTF 2019)。
- `phar://` 触发元数据反序列化:`file_exists('phar://evil.jpg')` 即可打点,配合上传图片马绕过无上传解析的限制(35C3 2018 `.phar` 黑名单绕过思路同源)。
- Cookie 序列化直接控对象(见 [server-side-exec] 的 PHP Cookie 反序列化套路)。

## 伪协议

- `php://filter/convert.base64-encode/resource=index.php` 读源码;`read=convert.iconv.utf-8.utf-16` 做编码过滤绕死亡 exit。
- `php://input` 写入 POST 体执行;`data://text/plain,<?php ...`;`zip://`/`phar://` 读包内文件——PNG+ZIP polyglot 后 `zip://a.png#shell.php` LFI(PlaidCTF 2016)。
- `php://input` + NULL 字节 + `~` 按位取反绕 base64 过滤(DefCamp 2018);`file=` 参数黑名单用 `/dev/fd/` 符号链接绕 `/proc` 过滤(Google CTF 2017)。
- `file://`、`http://`、`ftp://`、`expect://`(需扩展)、`glob://` 列目录。

## 命令执行/代码执行入口

- `eval`/`assert`(字符串求值,CSAW 2016)/`preg_replace('/x/e',...)`(PHP<7,PlaidCTF 2014)/`create_function` 注入(FireShell 2019)/`call_user_func`。
- 反引号执行受字符限制时:`current(getallheaders())` 从头注入绕正则(RCTF 2018)。
- disable_functions 绕过:LD_PRELOAD + mail()/imap、PHP7 OPcache 二进制 webshell(ALICTF 2016)、`scandir` 替代目录列举(MetaCTF Flash 2026)。
- 其他入口:日志包含(`session.upload_progress`、NGINX access log)、`session` 文件包含。

## 模板注入(PHP 侧)

- **Twig**:`{{7*7}}` 探测;RCE 走 `{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}`(Twig <3.14 常用链);新版用 `map/filter` 回调。
- **Smarty**:`{php}` 标签(旧版)、`{$smarty.template}` 信息泄露;CVE-2017-1000480(注释注入 `getStreamVariable`)、CVE-2021-26120(`{math}` 执行);静态方法 `{Smarty_Internal_Write_File::...}`。
- 文件读取:模板引擎的 include/display 路径可控 → 任意文件读(→ [文件泄露](file-leak.md) 衔接)。

## 框架漏洞(指纹命中即打 N-Day)

- **Laravel**:debug 模式(`/_ignition/execute-solution` RCE,CVE-2021-3129)、`APP_KEY` 泄露 → 反序列化 RCE(phpggc Laravel 链)。
- **ThinkPHP**:5.x `s=` 路由 RCE(2018 年国内爆发,`\think\app\invokefunction`)、多版本反序列化链;国内赛事与实战出现率最高。
- **Yii/CodeIgniter/CakePHP**:cookie 反序列化、phar 入口扫描。
- 通用路径:composer.json 定位框架与版本 → phpggc 找链 → 找反序列化入口(cookie/phar/上传)。

## 代码审计(面向 PHP 源码题)

- 入口追踪:路由分发 → 参数接收(`$_GET/$_POST/php://input`)→ 危险函数汇(eval/system/include/unserialize/extract/preg_replace)。
- 审计工具:Seay(国内)、RIPS 思路;`grep -rn "危险函数"` + 人工回溯数据流。
- 代码混淆:php-obfuscator/源码加密(eval-gz-inflate 套娃)→ 动态 dump(`hook eval` 打印解密后源码)。
- 衔接:反序列化 POP 链与伪协议见上文;变量覆盖三件套见上文。

## 工具速查

```bash
# filter 读源码
curl "URL?file=php://filter/convert.base64-encode/resource=index" | base64 -d
# phpggc 生成 POP 链
phpggc Laravel/RCE5 "system('cat /flag');" -b   # -b 输出 URL 编码
```

## 转向

- 拿到 Webshell 后提权/内网 → [渗透测试](../pen/index.md)
- 序列化题目升级(Java/.NET)→ [Java](java.md)、[Windows相关](windows.md)
