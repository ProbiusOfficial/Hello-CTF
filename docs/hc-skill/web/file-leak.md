---
comments: true
---

# 文件泄露

> WEB · 知识域。定位并利用暴露在 Web 侧的源码、备份、版本库与配置。标签:**源码文件泄露**、**备份文件泄露**、**网站信息泄露**。

## 触发特征

- 提示"源码找 flag"、依赖审计、需要 SECRET_KEY/APP_KEY。
- 部署残留:`.git`、`.svn`、`.DS_Store`、编辑器备份、压缩包备份。

## 源码文件泄露

- **版本库还原**:`/.git/` 用 GitHack / dvcs-rippers;提交被 squash 后用 `git reflog` + `git fsck --lost-found` 恢复(BearCatCTF 2026);`.bzr` 仓库用 `bzr check` 循环修复还原(STEM CTF 2019)。
- **历史泄密**:commit 作者邮箱挖凭据(Hackover 2018);密钥藏于 git 历史(Hack.lu 2017:DNSSEC key)。
- **依赖清单**:`composer.json`/`package-lock.json`/`requirements.txt` 版本 → 匹配 gadget 链与 CVE。

## 备份文件泄露

- 模式字典:`index.php.bak`、`*.php~`、`www.zip`、`.index.php.swp`(vim swap 还原源码,h4ckc0n 2017)、`*.sql`。
- Windows 8.3 短文件名探测存在性:`INDEX~1.PHP`(Tokyo Westerns 2016)。
- IDE 残留:`.idea/`、`.vscode/` 携带连接串与任务配置。

## 网站信息泄露

- `.env`/`config.php`:数据库口令、Laravel `APP_KEY`(可解密 cookie)、Flask `SECRET_KEY`(可伪造 session)→ 衔接 [认证绕过](auth-bypass.md)。
- **Nginx alias 穿越**:`location /backup { alias /app/backup/; }` 缺尾斜杠 → `..%2f` 穿越(VolgaCTF 2018 读 `.env`)。
- `.DS_Store` 目录枚举:python-dsstore 还原目录结构(35C3 2018)。
- 云凭证:SSRF 打 metadata `169.254.169.254` 拿临时 AK/SK → [云安全](../cld/info-gathering.md)。

## 泄露后动作

1. `grep -rE "key|secret|pass|token|flag" .`
2. 按框架版本选反序列化链(Java: ysoserial;PHP: composer 组件链)。
3. 泄露口令撞库后台;`uniqid()` 可预测文件名直接猜路径(EKOPARTY 2017)。

## 工具速查

```bash
python GitHack.py http://target/.git/
bkcrack -C enc.zip -c flag.txt -p plain.txt   # 明文攻击见 Misc-压缩包
```
