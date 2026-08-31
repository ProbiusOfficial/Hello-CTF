---
comments: true
---

# 身份与访问管理

> CLD · 知识域。云 IAM 体系攻击。标签:**弱口令攻击**、**权限提升**、**多因素认证绕过**、**API密钥泄露**、**临时凭证滥用**、**角色切换攻击**。

## 触发特征

- 拿到 AK/SK 或临时 STS 凭证;题目给低权限身份要求提权。

## 弱口令攻击

- 云控制台子账号弱口令;RAM/ CAM / IAM 用户密码策略缺失;AccessKey 成对泄露(console+API 双面)。

## 权限提升

- 思路:枚举当前身份权限(`ListPolicies`/`AttachUserPolicy` 可写时直接自授权)。
- 常见提升链(AWS 语境,国内云同构):`iam:PassRole` + 服务角色滥用(给 EC2/Lambda 挂高权角色)、`sts:AssumeRole` 信任链跳转、`lambda:UpdateFunctionCode` 改高权函数代码、`ec2:RunInstances` 起新实例挂角色。
- 资源策略反转:S3/OSS 桶策略允许 `Principal:*` 写入 → 写入策略文件/函数代码。

## 多因素认证绕过

- MFA 仅在控制台层、API 层无 MFA(AK 直接调 API 绕过);remember-device token 复用。
- 逻辑:验证码可枚举/不校验(→ [WEB-暴力破解](../web/brute-force.md))。

## API密钥泄露

- 泄露面:前端代码、移动端 APK、GitHub、公开仓库 commit 历史、日志打印、错误页。
- AK 权限最小化失败:一对 AK 打通 OSS+RAM+ECS 常见。
- 泄露后动作:身份识别(`sts get-caller-identity`)→ 权限枚举 → 数据面优先(OSS 数据库备份)。

## 临时凭证滥用

- STS 临时凭证:有效期内的完整 API 权限;从 metadata/日志/前端拿到即用。
- 会话标签/来源身份校验缺失时跨角色使用。

## 角色切换攻击

- `AssumeRole` 信任策略过宽(任意账户/服务可扮演);角色链(经中间角色跳到高权角色)。
-混淆代理问题(confused deputy):外部账户经受信任服务代理调用角色动作。

## 转向

- 提权后数据面 → [数据保护](data-protection.md);控制计算资源 → [容器安全](container.md)
