---
comments: true
---

# 智能合约

> ETH · 知识域。合约漏洞利用主战场。标签:**合约漏洞分析**、**合约代码审计**、**合约逻辑漏洞**、**合约权限控制**、**合约重入攻击**、**合约溢出漏洞**。

## 触发特征

- Ethernaut/Damn Vulnerable DeFi/paradigm-ctf 形态:部署实例 → 让 `isSolved()` 为真。

## 重入攻击(DAO 模式)

- 经典:external call(转账)在状态更新前 → 回调再入取款(DefCamp 2017 原型 DAO 事件)。
- 变体:ERC777 hook 重入、ERC721 `onReceived` 重入、`receive/fallback` 逻辑。
- 检查点:状态更新与外部调用顺序;reentrancy guard 缺失;**跨函数重入**(经共享状态变量)。

## 溢出漏洞

- Solidity <0.8 无内置检查:加/减/乘溢出(`SafeMath` 缺失);0.8+ 用 unchecked 块的溢出。
- 类型截断:uint256→uint32 强转;epoch 时间截断。
- 变体:批量铸造数组长度伪造(短地址历史攻击)。

## 权限控制

- `tx.origin` 鉴权(钓鱼合约代发交易绕过);`msg.sender` 与 delegatecall 上下文混淆。
- **delegatecall 存储上下文滥用**:库/代理调用下存储槽错位覆盖 owner(EHAX 2026)。
- 初始化函数未设防(可重复 init);`selfdestruct` 强制注 ETH 破坏"余额等于 X"判定(0.8 后 selfdestruct 仍可强制发币给合约)。
-修饰器逻辑 bug:非真条件短路。

## 逻辑漏洞

- 整数精度:除法先乘后除顺序、精度丢失套利偏差。
- 预言机操纵:spot price(.balance/getReserves)被闪电贷操纵;TWAP 短窗操纵。
- 闪电贷组合攻击:无自有资金完成"需要大量本金"的操作(damnvulnerabledefi 核心思想)。
- 随机数:块变量(blockhash/timestamp/prevrandao)可预测/可操纵;commit-reveal 缺失。
- DoS:revert 拒绝(循环内退款给恶意合约)、gas 耗尽(无上限循环)。

## 代理与升级漏洞

- **EIP-1967 代理利用**:implementation slot 劫持、未初始化的 implementation 直接 init(原题范式)。
- UUPS 升级函数无权限 → 自升级恶意逻辑;存储碰撞(变量槽位重叠)。
- ABI Coder v1/v2 差异:dirty address 位绕过;非标准 calldata 编码解析分歧;bytes32 字符串编码。
- **Solidity transient storage**(0.8.28-0.8.33):helper 冲突清零导致的重入窗口(0xFun 2026 系列)。
- CBOR 元数据剥离:codehash 判定绕过。

## 高级密码学面

- **Groth16 证明伪造**:setup 参数 delta==gamma 时直接构造假证明(A=alpha,B=beta,C=-vk_x);无 nullifier 追踪时无限重放(DiceCTF 2026 治理场景)。
- **DV-SNARG 伪造**:oracle 下学习秘密 v 后 CRS 消除伪造;KZG 配对 oracle 恢复置换(→ [Crypto-Z3](../crypto/z3.md)/[ECC](../crypto/ecc.md))。
- Phantom market 不结算 + 强注资金组合(DiceCTF 2026)。

## 审计工具与流程

```bash
slither ./target --print inheritance-graph   # 静态审计
echidna-test contract.yaml                   # 性质 fuzz
forge test -vvv                              # 写 PoC 测试
# 审计清单:重入 → 权限 → 溢出 → 预言机 → 随机数 → 升级 → DoS
```

## 转向

- 密码学组件(Groth16/KZG)→ [Crypto-ECC](../crypto/ecc.md);链下基础设施(Web/API)→ [WEB](../web/index.md)
