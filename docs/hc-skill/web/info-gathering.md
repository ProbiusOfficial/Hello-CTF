---
comments: true
---

# 信息搜集

> WEB · 知识域。漏洞利用前的前置侦察技能:确认技术栈、枚举资产、发现隐藏入口。标签:**域名信息搜集**、**个人信息搜集**。

## 触发特征

- 题目只有一个"什么都没有"的站点,提示找不到入口。
- 需要确定后端语言/框架/中间件以选择攻击面。
- flag 或 key 藏在注释、元数据、历史资产中。

## 域名信息搜集

- 域传送:`dig axfr @ns.target.com`;子域枚举:`subfinder`、`OneForAll`、crt.sh 证书透明度查询。
- 国内题目常带 ICP 备案号,反查主体可关联出出题方业务背景。
- 历史资产:Wayback Machine 挖已下线路径;`web.archive.org` 的旧 JS 可能引用已删除接口。

## 个人信息搜集

- 页面注释、`git log` 作者邮箱、JS bundle 中的 API Key / AccessKey。
- 邮件头 `Received` 链路、附件 EXIF / Office 元数据泄露内网主机名、用户名。
- 社工线索(姓名拼音、生日)用于构造爆破字典。

## 高价值侦察清单

1. 先读 HTML、内联脚本、JS bundle,再猜 API;对比前端提交字段与后端接受字段,可选 JSON 字段常解锁隐藏路径。
2. 优先访问:`/robots.txt`、`/sitemap.xml`、`/.well-known/`、`/.git/`、`/.env`、`/debug`、`/admin`、`/console`(Flask debug)、`/actuator`(Spring)。
3. 同一路由尝试多动词多格式:`GET/POST/PUT/PATCH/TRACE`,form / JSON / multipart / XML。
4. 上传、PDF 导出、webhook、OAuth 回调、admin bot 是漏洞放大器。
5. 响应头指纹:`Server`、`X-Powered-By`、Cookie 名(PHPSESSID/JSESSIONID)、默认报错页。

## 工具速查

```bash
curl -sI https://target/            # 响应头指纹
whatweb / wappalyzer                # 技术栈识别
ffuf -u https://target/FUZZ -w dict.txt
dirsearch -u https://target -e php,aspx,jsp,html,zip,bak,git
```

## 转向

- 发现 `.git`/备份/`.env` → [文件泄露](file-leak.md)
- 认证界面出现 → [认证绕过](auth-bypass.md)
- 需要 OSINT 级深挖(社交平台、地理定位)→ [Misc-其他](../misc/index.md)
