---
comments: true

---

# SCD 文件

## 定义

在 IEC 61850 标准体系中，SCD（Substation Configuration Description）文件是变电站配置描述文件，它是整个变电站自动化系统的 "总配置文件"

它包含了：

- 一次设备接线拓扑：母线、线路、开关、互感器等的连接关系

- 二次智能电子设备（IED）信息：保护、测控、智能终端等装置的模型，包括逻辑设备、逻辑节点、数据对象等

- 通信配置：GOOSE、SV 等报文的控制块、发布/订阅关系，MMS 报告设置等

- 映射关系：将设备间的逻辑信号绑定到具体网络报文

简单说，SCD 文件是变电站二次系统集成和运维的基础数据，必须保证正确性和唯一性，否则会导致保护误动、拒动或通信故障

## 实战案例

### 智能变电站设备异常诊断（SCD 文件）

010 打开发现文件头被颠倒了

![](https://pic1.imgdb.cn/item/6a3427c791b65c4475ae6310.png)

改回来后打开就是一个 `dcs.dcs` 文件

![](https://pic1.imgdb.cn/item/6a34280791b65c4475ae631c.png)

初步查看文件类型

```bash
file dcs.dcs
strings -a dcs.dcs | head
```

可以看到文件不是普通 XML

```bash
dcs.dcs: data
```

但文件头附近有明显标识

```
$KEMOV-SCD-FILE$
```

继续查看十六进制

```
od -Ax -tx1z -N 128 dcs.dcs

ff ff 24 4b 45 4d 4f 56 2d 53 43 44 2d 46 49 4c 45 24
```

对应了 `$KEMOV-SCD-FILE$`

同时后面出现了类似

```
20 31 20 31 20 30 20 6b 20 76 20 2e 20 73 20 63 20 64
```

这种结构解出来是

```
110kv.scd
```

说明这个文件本质上保存的是一个变电站 SCD 配置信息，只是被厂商工具二进制化了

观察文件里的 ASCII 字符串会发现它不是正常连续保存的

```
20 49 20 4c 20 31 20 31 20 30 20 31
```

这不是普通 ASCII，而是类似

```
0x20 + ASCII 字符
```

所以

```
20 49 -> I
20 4c -> L
20 31 -> 1
20 31 -> 1
20 30 -> 0
20 31 -> 1
```

解出来是

```
IL1101
```

中文部分则基本可以按 UTF-16BE 理解

也就是说，文件里的大量字段是 1 字节长度 + 2 字节字符序列

编写脚本来恢复

```python
from pathlib import Path
import re
from collections import Counter

b = Path("dcs.dcs").read_bytes()

print("[+] header:", b[2:18].decode())

def dec(pos):
    if pos >= len(b):
        return None

    L = b[pos]

    # 字符串长度一般为偶数，每个字符 2 字节
    if L < 2 or L > 200 or L % 2:
        return None

    data = b[pos + 1:pos + 1 + L]
    if len(data) != L:
        return None

    out = []

    for hi, lo in zip(data[0::2], data[1::2]):
        # ASCII 字符：20 xx
        if hi == 0x20 and 0x20 <= lo <= 0x7e:
            out.append(chr(lo))
        else:
            try:
                ch = bytes([hi, lo]).decode("utf-16be")
            except Exception:
                return None

            # 本题需要的非 ASCII 基本都是中文，严格过滤误判
            if not (0x4e00 <= ord(ch) <= 0x9fff):
                return None

            out.append(ch)

    s = "".join(out)

    if not re.search(r"[A-Za-z0-9\u4e00-\u9fff]", s):
        return None

    return s, pos + 1 + L


def strs(start=0, end=None):
    p = start
    end = len(b) if end is None else min(end, len(b))
    out = []

    while p < end:
        r = dec(p)
        if r:
            s, p2 = r
            out.append((p, s))
            p = p2
        else:
            p += 1

    return out


allstr = strs()

print("[+] decoded strings:", len(allstr))
print("[+] first strings:")
for off, s in allstr[:8]:
    print(hex(off), repr(s))


print("\n[+] 110kV line intelligent terminals:")
for idx, (off, s) in enumerate(allstr):
    if "110kV" in s and "线路智能终端" in s:
        print("---")
        for o, t in allstr[max(0, idx - 3):idx + 2]:
            print(hex(o), t)


print("\n[+] duplicated IED_GOCB:")

records = []

for m in re.finditer(b"IED_GOCB", b):
    vals = [s for _, s in strs(m.end(), m.end() + 700)]

    gocb = next((x for x in vals if re.fullmatch(r"gocb\d+", x)), None)
    ref = next((x for x in vals if "/LLN0" in x), "")

    mi = re.search(r"0?([A-Z]{1,4}\d{3,4})(?=[A-Z]+/LLN0)", ref)

    if gocb and mi:
        ied = mi.group(1)
        records.append((m.start(), ied, gocb, vals[:6]))

cnt = Counter((ied, gocb) for _, ied, gocb, _ in records)

for (ied, gocb), c in sorted(cnt.items()):
    if c > 1:
        print(ied, gocb, "count =", c)

        for off, ied2, gocb2, vals in records:
            if (ied2, gocb2) == (ied, gocb):
                print("   ", hex(off), vals[:5])
```

脚本首先能恢复出原始 SCD 文件名

```
[+] header: $KEMOV-SCD-FILE$
[+] decoded strings: 8174
[+] first strings:
0x21 '九曲110kv.scd'
0x3b 'version'
0x4d 'reversion'
0x63 'template'
0x77 'toolID'
```

接着筛选 110kV 线路智能终端，可以看到

```
[+] 110kV line intelligent terminals:
---
0x2525d IL1101
0x2526d 110kV1#线路智能终端
---
0x30a87 IL1102
0x30a97 110kV2#线路智能终端
```

题目说问题可能来源于线路智能终端，所以重点检查

```
IL1101
IL1102
```

然后分析 IED_GOCB 记录，即 GOOSE Control Block 配置，异常输出为

```
[+] duplicated IED_GOCB:
IL1101 gocb5 count = 10
    0x28756 ['gocb5', '0IL1101RPIT/LLN0', 'GOOSE采样', '0IL1101RPIT/LLN0', 'GO$gocb5 0IL1101RP']
    0x2953e ['gocb5', '0IL1101RPIT/LLN0', 'GOOSE采样', '0IL1101RPIT/LLN0', 'GO$gocb5 0IL1101RP']
    0x2a24e ['gocb5', '0IL1101RPIT/LLN0', 'GOOSE采样', '0IL1101RPIT/LLN0', 'GO$gocb5 0IL1101RP']
    ...
```

这里的异常点非常明确：

```
IL1101 / RPIT / LLN0 / gocb5
```

被重复配置了 10 次

在 IEC 61850/SCD 配置里，同一个 IED、同一个逻辑节点下的 GOOSE 控制块名称应该唯一。重复的 `gocb5` 会导致控制块引用冲突、GOOSE 配置异常，从而引发运行异常

题目问的是 "分析存在问题根源"

真正的问题是 "变电站基础配置文件 SCD 存在错误"

所以 flag 是 `flag{scdisbad}`

### 黑客的大意