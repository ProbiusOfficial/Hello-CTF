---
comments: true
---

# CLD - 云安全

> 方向技能索引。目标为云平台(AWS/阿里云/腾讯云)、容器/K8s、CI/CD、云原生应用时从本索引路由。云上 Web 漏洞本体 → [WEB](../web/index.md);容器逃逸后利用 → 本方向。

## 知识域路由表

| 知识域 | 触发特征 |
| --- | --- |
| [信息搜集](info-gathering.md) | 云服务枚举、配置文件、metadata |
| [身份与访问管理](iam.md) | AK/SK、角色、MFA、临时凭证 |
| [网络安全](network.md) | VPC/安全组/防火墙配置缺陷 |
| [数据保护](data-protection.md) | 对象存储权限、快照泄露 |
| [容器安全](container.md) | Docker/K8s 逃逸与编排滥用 |
| [无服务器计算](serverless.md) | FaaS 函数注入与权限滥用 |
| [监控与日志](monitoring.md) | 日志配置/篡改/绕过 |
| [DevOps安全](devops.md) | CI/CD 管道、代码仓库、凭证管理 |
| [云原生安全](cloud-native.md) | 服务网格、云原生 API 滥用 |
| [合规与审计](compliance.md) | 合规检查、审计方法 |
| [第三方服务](third-party.md) | 第三方 API/依赖/供应链面 |
| [灾难恢复](disaster-recovery.md) | 备份与恢复策略 |

## 环境基线

```bash
pip install aliyun-cli ossutil; aws cli; kubectl; trivy(镜像扫描)
# SSRF 打 metadata:curl http://100.100.100.200/latest/meta-data/(阿里云)
#                  curl http://169.254.169.254/latest/meta-data/(AWS)
```
