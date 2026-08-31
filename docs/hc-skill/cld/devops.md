---
comments: true
---

# DevOps安全

> CLD · 知识域。CI/CD 与研发工具链攻击。标签:**CI/CD管道安全**、**代码仓库泄露**、**自动化工具漏洞**、**凭证管理不足**、**配置管理错误**。

## 触发特征

- 目标为 GitHub/GitLab/Jenkins/TeamCity/流水线;题目给仓库或 CI 环境。

## CI/CD管道安全

- **PR/Issue 触发注入**:workflow YAML 里 `$(github.event...)` 直接拼 shell → PR 标题/正文命令注入(GitHub Actions 经典)。
- pipeline 定义注入:可修改 `.gitlab-ci.yml`/`Jenkinsfile` → 加恶意 stage 拿 runner shell。
- runner 权限:自托管 runner 上的缓存/工件投毒;并行 job 间共享目录互踩。
- 构建环境逃逸:CI 容器挂 docker.sock(→ [容器安全](container.md));云凭证默认注入到环境变量。
- 变量窃取:CI 变量打印(`env`/构建日志回显);fork PR 拿仓库 secrets 的防护绕过(改为 pull_request_target + checkout fork 代码的组合)。

## 代码仓库泄露

- `.git` 目录暴露(→ [WEB-文件泄露](../web/file-leak.md));历史 commit 里的密钥(git log -p 搜 secret/password/AK)。
- 内部仓库公开误配(GitLab 公开项目);组织成员权限枚举。
- LFS/大文件、tag/release 附件中的敏感产物。

## 自动化工具漏洞

- N-Day 匹配:Jenkins(脚本控制台未授权/Groovy RCE)、GitLab(CVE-2021-22205 ExifTool RCE 系)、Gogs 符号链接 RCE(CVE-2025-8110)、TeamCity REST API RCE(Watcher HTB)、Gitea/Drone/ArgoCD 历史漏洞。
- 未授权接口:`/script` 控制台、`/api` 匿名枚举、调试端点。

## 凭证管理不足

- 硬编码:代码里的 AK、数据库口令、SSH 私钥(仓库全史 grep);deploy key 滥用。
- 凭证轮换缺失:泄露的旧凭证仍有效;共享凭证(个人级 token 而非机器人)。
- 凭证传递链:CI → 云 → 生产环境的信任链被单点突破。

## 配置管理错误

- IaC(Terraform/Ansible)状态文件泄露(state 里有资源与敏感字段);Ansible vault 弱口令。
- 配置漂移审计;默认配置未改(Jenkins 未授权匿名读、GitLab 注册开放)。

## 转向

- 拿到云凭证 → [身份与访问管理](iam.md);runner 是容器 → [容器安全](container.md)
