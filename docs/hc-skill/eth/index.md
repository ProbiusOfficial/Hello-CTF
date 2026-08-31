---
comments: true
---

# ETH - 区块链安全

> 方向技能索引。目标为智能合约、链上交易、钱包/DApp 时从本索引路由。区块链基础教学( Move 语言入门等)见主站 [blockchain 章节](https://hello-ctf.com/)。

## 知识域路由表

| 知识域 | 触发特征 |
| --- | --- |
| [信息搜集](info-gathering.md) | 链上侦察:合约代码、账户画像 |
| [交易分析](transaction.md) | calldata/事件/交易模式审计 |
| [智能合约](smart-contract.md) | 合约漏洞利用:重入/溢出/权限/代理 |

## 环境基线

```bash
# 框架:foundry(forge cast anvil)、hardhat、remix(在线)
# CTF 平台形态:ethernaut、damnvulnerabledefi、paradigm-ctf
# 工具:slither(静态审计)、echidna/mythril(fuzz/符号)、tenderly(tx 调试)
cast call <addr> "functionName()" --rpc-url $RPC   # cast 命令行交互
```
