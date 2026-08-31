---
name: helloctf-skill
description: Hello CTF 技能树 —— 基于国内 CTF 竞赛体系整理的全方向攻防知识库。当用户在学习 CTF、备战比赛、解赛题（Web / Crypto / Misc / Pwn / Reverse / AI / 云安全 / 数据安全 / 区块链 / 工控 / 物联网 / 应急响应 / 渗透测试）需要定位知识点、查询利用手法或规划学习路线时使用。也适用于按知识域出题、查漏补缺。
---

# Hello CTF 技能树

基于国内 CTF 竞赛体系整理的 13 个方向、150+ 知识域的攻防知识库。

## 使用方式

1. 根据题目类型或学习目标，在下表中定位方向。
2. 打开对应方向的索引文件 `docs/hc-skill/<方向>/index.md`，按其「知识域路由表」的触发特征进一步路由到具体知识域文件。
3. 知识域文件内是按国内赛事标签体系组织的考点清单与利用手法，直接按需查阅。

不要在未确认方向时通读全部文件 —— 先路由，再加载。

## 方向路由表

| 方向 | 索引文件 | 触发特征 |
| --- | --- | --- |
| WEB · Web安全 | [web](docs/hc-skill/web/index.md) | HTTP 应用、注入、XSS、上传、SSRF、认证绕过 |
| CRYPTO · 密码学 | [crypto](docs/hc-skill/crypto/index.md) | 古典密码、RSA/ECC、哈希、伪随机数、格密码 |
| MISC · 安全杂项 | [misc](docs/hc-skill/misc/index.md) | 隐写、流量分析、取证、编解码、压缩包 |
| PWN · 二进制安全 | [pwn](docs/hc-skill/pwn/index.md) | 栈/堆溢出、格式化字符串、内核、异构架构 |
| REVERSE · 逆向工程 | [reverse](docs/hc-skill/reverse/index.md) | 静态/动态分析、反混淆、脱壳、多语言逆向 |
| AI · 人工智能安全 | [ai](docs/hc-skill/ai/index.md) | 对抗样本、模型窃取、数据投毒、越狱 |
| CLD · 云安全 | [cld](docs/hc-skill/cld/index.md) | 容器逃逸、IAM 提权、云原生、DevOps |
| DS · 数据安全 | [ds](docs/hc-skill/ds/index.md) | 数据分类分级、传输/存储安全、脱敏、DLP |
| ETH · 区块链安全 | [eth](docs/hc-skill/eth/index.md) | 智能合约审计、重入、溢出、交易分析 |
| ICS · 工控安全 | [ics](docs/hc-skill/ics/index.md) | PLC、SCADA 协议、固件逆向、控制逻辑 |
| IOT · 物联网安全 | [iot](docs/hc-skill/iot/index.md) | 固件提取、无线协议、硬件调试接口 |
| IR · 应急响应 | [ir](docs/hc-skill/ir/index.md) | 日志分析、流量分析、入侵排查 |
| PEN · 渗透测试 | [pen](docs/hc-skill/pen/index.md) | 信息搜集、漏洞利用、提权、横向移动 |

## 在线版本

技能树的可视化浏览与最新内容见 <https://hello-ctf.com>。
