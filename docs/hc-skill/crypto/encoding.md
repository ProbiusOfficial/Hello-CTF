---
comments: true
---

# 编码与解码

> CRYPTO · 知识域。可逆编码的识别与还原,是密码题的"前置解码层"。标签:**电话拨号编码**、**Morse编码**、**敲击码**、**曼彻斯特编码**、**格雷编码**、**字母表编码**。

## 触发特征

- 字符集受限(0/1、A-Z、数字对)、无密钥、纯格式变换。
- 密文长度是明文长度的整数倍(2/4/5 倍常见)。

## 识别与解码速查

| 编码 | 密文特征 | 还原 |
| --- | --- | --- |
| Base16/32/58/64/85 | `0-9A-F`、大写+`=`、混合大小写、全字符 | CyberChef 逐层试,长度对齐表 |
| 电话拨号编码(九键) | 数字串 `21 22 23` 每组对应字母位置 | 2=ABC,组内第 n 个 |
| Morse 编码 | `.-/-...` 或 01 表示 | `.-=A`;分隔符识别(空格/斜杠) |
| 敲击码(Tap code) | 数字对(1-5)x(1-5) | 5x5 网格,常省 C/K |
| 曼彻斯特编码 | 01/10 交替规律 | 每位拆两半取后半(或前半,注意 IEEE 802.3 反相) |
| 差分曼彻斯特 | 边界翻转规律 | 首位参照位,看位首是否跳变 |
| 格雷编码 | 二进制但多位变化平滑 | `g→b: b1=g1, bi=bi-1^gi` |
| 字母表编码 | 数字→字母(A=1)或反 | `chr(64+n)`;注意 A=0 变体 |
| URL/Unicode/HTML实体 | `%xx`、`\uXXXX`、`&#x;` | CyberChef URL Decode / unescape |

## 多层嵌套处理

- 自动逐层解码器:CyberChef Magic、`ciphey`;但嵌套超过 3 层建议人工确认每层。
- 复合套路:base64(hex(morse(x)))、base65536 CJK 字符二进制编码(IceCTF 2018)、UTF-16 字节序反转(LACTF 2026)、BCD 码(VuwCTF 2025)、UTF-9(RFC 4042 恶搞标准,SECCON 2015)。
- SMS PDU 解码(RuCTF 2013)、RTF 自定义标签藏数据(VolgaCTF 2013)。

## 工具速查

```python
import base64
base64.b64decode(s)          # b32decode/b85decode
bytes.fromhex(s)
# 曼彻斯特
bits = ''.join(b[1] for b in pairs)   # 取后半
```

## 转向

- 有密钥参与 → [流密码](stream-cipher.md)/[加法密码](additive-cipher.md)
- 编码藏在文件/图片里 → [Misc-数据及编解码](../misc/data-encoding.md)
