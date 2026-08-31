---
comments: true
---

# 容器安全

> CLD · 知识域。Docker/K8s 攻防。标签:**容器逃逸**、**镜像漏洞利用**、**不安全的容器编排**、**容器网络隔离不足**、**容器注册表安全**。

## 触发特征

- 目标是容器内服务/K8s 集群;拿到容器 shell 后要求逃逸或横向。

## 容器逃逸

- **特权容器**:`--privileged` → 直接挂载宿主磁盘(`fdisk -l` 看盘 → mount);cap 检查 `capsh --print`(CAP_SYS_ADMIN 可 cgroup release_agent 逃逸)。
- **Docker Socket 挂载**:`/var/run/docker.sock` 在容器内 → 起特权新容器挂宿主根。
- **内核漏洞逃逸**:DirtyCow/CVE-2022-0185(shenhav)/DirtyPipe(→ [Pwn-Linux内核漏洞利用](../pwn/kernel-exploit.md) 同源)。
- **CAP_SYS_ADMIN 缺失时**: `/proc/sysrq-trigger`、core_pattern 容器内可写(宿主共享内核参数)时逃逸;hostPID/hostNetwork 配置滥用。
- BuildKit 守护进程构建密钥窃取(BSIDSSF 2026);Squid 代理跳板内网(Bamboo HTB)。
- 检测面:`/proc/self/mountinfo`(宿主路径泄漏)、`/proc/1/cgroup`(在容器内吗)、capabilities、seccomp(`grep Seccomp /proc/self/status`)。

## 镜像漏洞利用

- 镜像内敏感信息:历史层(`docker history`)里的 ARG/ENV 凭证;`.dockerconfig`/拉取凭证;层 diff 提取被删除文件(`docker save` 逐层解)。
- 基础镜像 CVE(nginx/redis 老版本)→ N-Day 匹配;镜像内打包的调试工具(ssh 私钥)。
- 镜像扫描:trivy/grype;CTF 常考"从镜像层里恢复被删的 flag 文件"。

## 不安全的容器编排(K8s)

- **RBAC 绕过**:当前 ServiceAccount 权限枚举(`kubectl auth can-i --list`);create pods → 挂宿主根的新 pod;patch daemonset;读 secret 权限直接拿 token。
- K8s 组件未授权:API Server 10250 匿名、etcd 2379、dashboard 匿名、kubelet 只读端口 10255。
- Service Account token 文件(`var/run/secrets/kubernetes.io/...`)窃取后 `kubectl --token` 直接用。
- 容器内信息收集:env(K8S_SERVICE_HOST、注入的密钥)、DNS(服务发现)→ 内网横向。

## 容器网络隔离不足

- 同宿主/同网段容器互信(默认 bridge 全通);容器内网横向(→ [渗透测试](../pen/index.md))。
- NetworkPolicy 缺失:被攻陷容器可访问所有 service。

## 容器注册表安全

- 私有 registry 未授权(API v2 `/v2/_catalog` 列镜像);拉取私有镜像分析(→ 镜像漏洞利用)。
- 镜像签名校验缺失 → 投毒镜像替换。

## 转向

- 逃逸到宿主后 → [渗透测试-后渗透](../pen/post-exploitation.md);云凭证 → [身份与访问管理](iam.md)
