---
comments: true
---

# 云原生安全

> CLD · 知识域。云原生应用与架构层攻击。标签:**云原生应用漏洞**、**云原生API滥用**、**服务网格安全**、**云原生架构误配置**、**云原生安全策略**。

## 触发特征

- 目标为微服务/服务网格/Istio/API 网关体系;K8s 之上的应用层。

## 云原生应用漏洞

- 微服务横向:服务间信任(内网明文/无鉴权互调)→ 攻陷一个服务即横向(→ [WEB-SSRF](../web/ssrf.md) 打内网)。
- 服务间传递身份:JWT 内部转发、mTLS 证书滥用;默认凭据注入(sidecar)。
- 配置中心(Nacos/Apollo/Consul)未授权 → 改配置注入(数据库连接指向攻击者/动态开关后门)。

## 云原生API滥用

- API 网关层:路由重写规则滥用、跨命名空间代理、限流键伪造(X-Forwarded-For,→ [WEB-HTTP请求](../web/http-request.md))。
- 管理面 API 未授权:Ingress controller(Prometheus/NGINX Ingress snippet 注入 RCE)、Istio/Envoy admin 端口(15000)。
- 指标面:Prometheus 未授权(查/写指标、告警投毒)、Grafana 匿名/插件目录穿越 CVE。

## 服务网格安全

- mTLS 配置缺陷:PERMISSIVE 模式(可明文)、证书根泄露后全域伪造。
- Sidecar 逃逸:Envoy admin API、istio-proxy 配置注入(EnvoyFilter 权限)。
- 流量劫持:虚拟服务/目标规则被改 → 流量重定向到恶意服务(中间人)。

## 云原生架构误配置

- 默认组件暴露:`kubernetes` 默认 service、dashboard、metrics-server 匿名。
- 命名空间隔离缺失:跨 ns 访问(DNS 全局解析)。
- Pod 安全标准缺失:privileged/宿主挂载类 pod 可创建(→ [容器安全](container.md))。

## 云原生安全策略

- 策略引擎(OPA/Gatekeeper/Kyverno)绕过:规则不覆盖的字段、controller 版本漏洞。
- 镜像准入策略缺失(未签名镜像可跑);策略即代码的规则逻辑 bug。

## 转向

- 集群面 → [容器安全](container.md);服务本体漏洞 → [WEB](../web/index.md)
