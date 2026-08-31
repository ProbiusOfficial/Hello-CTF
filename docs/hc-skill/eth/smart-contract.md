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
- 合约随机数问题:块变量(blockhash/timestamp/prevrandao)可预测/可操纵;commit-reveal 缺失。
- DoS:revert 拒绝(循环内退款给恶意合约)、gas 耗尽(无上限循环)。

## Proxy模式漏洞(代理与升级)

- **EIP-1967 代理利用**:implementation slot 劫持、未初始化的 implementation 直接 init(原题范式)。
- UUPS 升级函数无权限 → 自升级恶意逻辑;存储碰撞(变量槽位重叠)。
- ABI Coder v1/v2 差异:dirty address 位绕过;非标准 calldata 编码解析分歧;bytes32 字符串编码。
- **Solidity transient storage**(0.8.28-0.8.33):helper 冲突清零导致的重入窗口(0xFun 2026 系列)。
- CBOR 元数据剥离:codehash 判定绕过。

## 合约代币标准与授权漏洞(ERC20 系)

- **ERC20 漏洞**:approve 竞态(先 approve 新额度前旧额度仍可被 spender 用掉——先减到 0 再 approve);decimals 处理错误导致数量放大;transfer 返回值未检查(bool false 静默失败,非 revert)→ 记账错乱;`transferFrom` 边界。
- **合约授权漏洞**:无限授权(`approve(type(uint256).max)`)后代币被任意划走(钓鱼签名/恶意合约,链上钓鱼主通道,→ [交易分析](transaction.md) 钓鱼模式);permit2 离线签名钓鱼;`increaseAllowance` 实现错误。
- **合约多重签名漏洞**:签名收集流程竞态(门限恰好达成瞬间状态变更)、owner 重复签名计数、execute 与 confirm 未分离导致的单签执行。

## 合约实现细节漏洞

- **合约函数可见性**:本应 external/private 的函数被标 public → 关键初始化/清算函数可被任意调用;initializer 未加防重入标志(→ 权限控制节初始化)。
- **合约函数选择器冲突**:两个函数 4 字节选择器相同(EIP-165 思想的滥用)→ 调用 A 实际进 B;Solidity 0.4.22 前 `fallback` 与函数选择器碰撞的历史 CVE。
- **合约短地址攻击**:ABI 编码在 calldata 尾部缺字节时,部分旧路由器/pad 逻辑会错位解析参数(ERC20 transfer 地址尾零被吃)——现代编译器已校验 calldata 长度,CTF 场景经手写汇编/低级调用复刻。
- **合约编译器漏洞**:Solidity 版本锁定后查编译器已知 bug(abi.encodePacked 哈希碰撞、0.8 前 unchecked 溢出、optimizer 缺陷列表,SWC 注册表);`forge inspect` 看编译器版本匹配。
- **Gas限制与操控(Gas Griefing)**,即合约拒绝服务攻击:循环无上限 → 阻塞调用(out of gas DoS);强制小 gas 转发(63/64 规则)让 fallback 逻辑失效;`gasleft()` 当随机数/条件 → 可被 gas 操纵。
- **合约自毁漏洞**:未鉴权的 `selfdestruct`/`suicide` → 强制转 ETH 破坏"余额==X"不变量、销毁金库(0.8 后 selfdestruct 仅剩强制发 ETH 语义,仍可用于不变量攻击);代理合约被 selfdestruct 后逻辑永久丢失。
- **合约时间戳依赖**:`block.timestamp`(可被矿工/出块者 ±数秒操纵)与 `block.number` 参与关键判定 → 竞标的最后一刻操纵(→ 逻辑漏洞节随机数条目同源)。

- **Groth16 证明伪造**:setup 参数 delta==gamma 时直接构造假证明(A=alpha,B=beta,C=-vk_x);无 nullifier 追踪时无限重放(DiceCTF 2026 治理场景)。
- **DV-SNARG 伪造**:oracle 下学习秘密 v 后 CRS 消除伪造;KZG 配对 oracle 恢复置换(→ [Crypto-Z3](../crypto/z3.md)/[ECC](../crypto/ecc.md))。
- Phantom market 不结算 + 强注资金组合(DiceCTF 2026)。

## 合约访问控制(权限面补充)

- 访问控制缺失总检:external 函数逐个过"谁能调"——modifier 缺失、msg.sender 与 tx.origin 混用、角色检查写错(`require(hasRole(x))` 参数序)、代理上下文下的权限存储错位(delegatecall 上下文,→ 权限控制节)。
- 角色管理漏洞:OpenZeppelin AccessControl 的 grant/revoke 流程滥用、角色继承链过宽、admin 角色单点。
- 合约整数溢出在代币语义下的放大:mint/burn 路径的 unchecked 运算 → 凭空增发/余额下溢成天文数字(→ 溢出漏洞节)。

## 审计工具与流程

```bash
slither ./target --print inheritance-graph   # 静态审计
echidna-test contract.yaml                   # 性质 fuzz
forge test -vvv                              # 写 PoC 测试
# 审计清单:重入 → 权限 → 溢出 → 预言机 → 随机数 → 升级 → DoS
```

## 转向

- 密码学组件(Groth16/KZG)→ [Crypto-ECC](../crypto/ecc.md);链下基础设施(Web/API)→ [WEB](../web/index.md)
