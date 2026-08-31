---
comments: true
---

# 交易分析

> ETH · 知识域。链上交易数据审计。标签:**交易历史分析**、**交易模式分析**、**交易流量分析**。

## 触发特征

- 给交易哈希/区块范围,要求还原"发生了什么";链上取证类题目。

## 交易历史分析

- 单笔:from/to/value/data(calldata)/签名(v,r,s)/gas;calldata 用 `cast calldata-decode` / 4byte 目录还原函数与参数。
- 事件(Events):按 topic0 索引事件签名,解码 Transfer/Approval 流。
- 内部交易(internal tx):`trace_transaction`/tenderly 还原 call/delegatecall 树。
- 失败交易:revert reason 还原(`cast --trace`,四字节 selector 查错误定义)。

## 交易模式分析

- MEV 模式:三明治(sandwich)、抢跑(front-run)、back-run;`tx.pool` 排序与 mempool 行为。
- 洗钱模式:链式转移、混币器进出(Tornado 类)、跨链桥跳跃;peel chain 剥离模式。
- 钓鱼模式:approve 授权钓鱼(黑名单地址批量 TransferFrom)、签名钓鱼(Permit2/离线签名)。
- 蜜罐合约识别:假余额显示、交易回退陷阱(买入可以卖出 revert)。

## 交易流量分析

- 时间序列:资金流向图(graph 分层布局)、交易频率异常(狙击 bot)。
- 地址聚类:共同输入启发式(CIHM)、找零地址识别。
- 题目形态:给一堆交易日志,还原"攻击者如何偷走资金"完整链路(战后复盘题)。

## 工具速查

```bash
cast receipt <txhash>
cast 4byte <selector>
# dune/bitquery 类 SQL 查链上数据;arkham 做地址画像
```

## 转向

- 定位到漏洞合约 → [智能合约](smart-contract.md);资金链画像 → OSINT 思路(→ [Misc](../misc/index.md))
