---
comments: true
---

# 系统安全

> AI · 知识域。AI 系统载体层的安全:沙箱与智能体。标签:**沙箱攻击**、**模型智能体攻击**。

## 触发特征

- "AI 助手/Agent 有 shell/代码解释器,让它拿到 flag";LLM 应用带插件/工具调用。
- Python 执行沙箱(pyjail 形态)挂在 AI 题里。

## 沙箱攻击

- LLM 的代码解释器沙箱逃逸 → 复用 pyjail 全套技术(→ [Reverse](../reverse/index.md) 不适用时走 [Misc](../misc/index.md) pyjail 部分:装饰器链、`__loader__`、quine)。
- 工具调用沙箱:文件系统访问限制绕过(路径穿越,→ [WEB](../web/index.md))、网络限制(出站请求 SSRF → [WEB-SSRF](../web/ssrf.md))。
- 环境隔离缺陷:容器内 Agent 拿宿主凭证(env 泄露,→ [云安全](../cld/index.md))。

## 模型智能体攻击

- **直接提示注入**:用户输入覆盖系统指令("忽略以上指令")。
- **间接提示注入**:注入指令到 Agent 会读取的外部内容(网页/邮件/文档/代码注释)→ 劫持 Agent 行为;工具滥用(诱导调用删除/外带工具)。
- 上下文窗口操纵:超长输入挤出系统提示;上下文污染持久化(记忆型 Agent 写入恶意记忆)。
- 多 Agent 信任链:伪造"来自上级 Agent"的消息;输出解析层注入(让 LLM 输出带工具调用语法骗过解析器)。
- RAG 投毒:知识库文档投毒(→ [数据攻击](data-attack.md));检索结果注入。
- Agent 的 Web 面:聊天接口 XSS(payload 渲染)→ [WEB-XSS](../web/xss.md);API 越权调用 → [WEB-认证绕过](../web/auth-bypass.md)。

## 转向

- 载体是 Web 应用 → [WEB](../web/index.md);执行环境是代码解释器容器 → [云安全-容器安全](../cld/container.md)
