---
comments: true
---

# 文件上传

> WEB · 知识域。从上传到 getshell 的全链路对抗。标签:**基础上传利用**、**前端绕过**、**黑名单绕过**、**白名单绕过**、**服务端特性绕过**、**文件内容检查绕过**。

## 触发特征

- 任何上传入口:头像、附件、导入(zip/xml)、资料图片。
- 提示"如何让马被解析"——考点在扩展名/内容/解析三者错位。

## 基础上传利用

- 流程:传 → 找回显路径(响应、 burp 拦截、目录爆破)→ 验证解析(访问返回内容)→ 连接(蚁剑/冰蝎/哥斯拉)。
- 直接传 php/jsp/aspx 成功 = 送分;失败进入绕过分支。

## 前端绕过

- JS 校验扩展名/MIME:bp 抓包改包即可,或禁用 JS。
- 前端切片/加密上传:逆向前端 JS 拼包逻辑(→ [JS](js.md))。

## 黑名单绕过

- 别名后缀:`php3/php4/php5/php7/pht/phtml/phar`(35C3 2018 `.phar` 绕黑名单)、`pHp` 大小写、`php.`、`php `、`php::$DATA`(Windows 流)。
- `.htaccess` 上传:`AddType application/x-httpd-eval .jpg` 让图片按 PHP 解析;`.user.ini`(同目录所有 php 包含指定文件)——需要目录可列且 CGI/FastCGI 模式。
- 解析漏洞:Nginx `xx.jpg/a.php`、IIS 6 `xx.asp;.jpg`/目录解析 `xx.asp/1.jpg`、Apache 多后缀从右向左(`xx.php.abc` 需配置)。
- Windows 特性:尾点、尾空格、`::$DATA`(见 [Windows相关](windows.md))。

## 白名单绕过

- 截断:%00(PHP<5.3.4 路径截断)、文件名注入二次处理。
- 双扩展 + 服务器错误配置;`basename()` 隐藏文件绕过(Nullcon 2026)。
- 扩展名截断:超长文件名截断(文件系统 255 限制)——BMP 像素马 + 文件名截断拿可控后缀(Nuit du Hack CTF 2018)。
- `.wave` 改名绕过类型校验(WAV polyglot,PlaidCTF 2018)。

## 服务端特性绕过

- 二次渲染:GIF 插入渲染不变的帧区;JPG 找渲染不动的块;PNG 拆 IDAT 重排(stegsolve/脚本辅助)。
- 条件竞争:先传后删的服务端,高并发上传+访问抢在 unlink 前(Turbo Intruder)。
- 移动/重命名逻辑缺陷:`move_uploaded_file` 目标可控 → 任意写。
- zip 解压:ZipSlip 路径穿越写任意文件(UTCTF 2024 zip 符号链接);zip:// 伪协议配合(→ [PHP](php.md))。
- nginx alias/proxy 路径拼接错误 → 上传目录被当作执行目录。

## 文件内容检查绕过

- 文件头:`GIF89a`、`\xFF\xD8\xFF`(JPG)、`\x89PNG` 混合 PHP 代码;`getimagesize()` 只认头部。
- 完整 polyglot:PNG+ZIP(PlaidCTF 2016)、PNG+PHP(双扩展+disable_functions 绕过,MetaCTF Flash 2026)、JPEG+HTML(EHAX 2026)、BMP 像素编码 webshell(Nuit du Hack CTF 2018)。
- 内容关键词过滤:`<?php` → `<?=`、`<script language="php">`(老版本);`assert`/`eval` 被禁 → 变量函数、`system` 替代。
- 图片马 + 包含:配合 LFI(`include $_GET['f']`)或 `.user.ini`/`.htaccess` 触发解析。
- 免杀:哥斯拉/冰蝎/蚁剑的马按各自流量特征生成,配合 PHP7 OPcache/`auto_prepend_file`(见 [PHP](php.md))。

## 上传后动作

1. 验证解析:`curl URL/shell.php?cmd=id`。
2. 蚁剑/冰蝎连接,读 `/flag` 或继续内网(→ [渗透测试](../pen/index.md))。
3. 马失效排查:扩展名没被解析?内容被改?路径不对?

## 转向

- 上传 xml/docx → [XXE](xxe.md);上传的是压缩包 → [Misc-压缩包分析](../misc/archive.md)
