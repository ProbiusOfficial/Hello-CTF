---
comments: true
---

# 信息搜集

> ETH · 知识域。链上侦察。标签:**智能合约信息搜集**、**账户信息搜集**。

## 触发特征

- 给合约地址/RPC/私钥,要求先摸清目标结构。
- 代理合约、多合约系统、治理/金库结构还原。

## 智能合约信息搜集

- 代码获取:已验证合约读 etherscan/basescan 源码;未验证用 `cast implementation`、反编译(panoramix/heimdall)。
- **代理模式识别**:EIP-1967 存储槽(`0x360894...` implementation slot)读逻辑合约地址(→ [智能合约](smart-contract.md) 代理利用)。
- 存储布局:`forge inspect Target storageLayout` 读变量槽位;slot0 常有 owner。
- 权限面:owner/admin 的 modifier 分布;`onlyOwner` 函数清单。
- 合约余额/代币持仓(`cast balance`、ERC20 balanceOf)。

## 账户信息搜集

- EOA 画像:交易历史(来源资金链、常用对手方)、nonce、标签库(arkham/misttrack 国内同源思路)。
- 题目基础设施:题目合约的 setup 合约(isSolved() 接口)、 faucet、玩家实例部署参数。
- 交易来源分析:-funded-by 模式找出题方钱包关联的其他题目实例(跨题联动线索)。

## 工具速查

```bash
cast chain-id --rpc-url $RPC
cast storage <addr> 0            # 读 slot0
cast tx <hash>                   # 交易详情
tenderly debug <txhash>          # 交易调试还原调用栈
```

## 转向

- 发现漏洞模式 → [智能合约](smart-contract.md);交易流审计 → [交易分析](transaction.md)
