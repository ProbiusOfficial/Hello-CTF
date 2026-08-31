---
comments: true
---

# 信息搜集

> CLD · 知识域。云环境侦察。标签:**云服务信息枚举**、**云服务配置文件收集**、**云服务元数据收集**。

## 触发特征

- 题目给云上靶机/带云凭证的 Web 应用;云原生 CTF(如 aws 巾 CloudGoat、阿里云靶场)。

## 云服务信息枚举

- 对象存储桶枚举:命名猜测(公司名-app/backup/static)、bucket 枚举工具(国内 oss:ossutil ls;AWS:s3scanner);公开桶列目录。
- 未授权服务探测:Redis/MongoDB/Elasticsearch 公网暴露、云数据库默认口令(→ [渗透测试-信息搜集](../pen/info-gathering.md))。
- 域名指向:解析到云厂商(CNAME 到 oss/cos/s3);`dig` 判断资源类型后选工具。

## 云服务配置文件收集

- 泄露点:`.env`(AK/SK)、`~/.aws/credentials`、`~/.kube/config`、`/etc/kubernetes/` 配置、docker-compose.yml 环境变量。
- Git 仓库历史里的密钥(→ [WEB-文件泄露](../web/file-leak.md));CI 日志里的变量打印(→ [DevOps安全](devops.md))。
- 客户端打包的临时凭证:前端 JS / APK 内嵌 AK。

## 云服务元数据收集

- **SSRF → metadata 是云题的标准链**(→ [WEB-SSRF](../web/ssrf.md)):
  - 阿里云:`http://100.100.100.200/latest/meta-data/ram/security-credentials/<role>`
  - AWS:`http://169.254.169.254/latest/meta-data/iam/security-credentials/`;IMDSv2 需先 PUT token(_HEADER 头携带)。
  - GCP:`http://metadata.google.internal/computeMetadata/v1/`(需 Metadata-Flavor 头)。
- 拿到临时凭证后:`aliyun configure`/`aws configure` 导入 → 枚举权限(`GetSecurityToken`、`sts get-caller-identity`)。

## 转向

- 凭证到手 → [身份与访问管理](iam.md);目标容器/集群 → [容器安全](container.md)
