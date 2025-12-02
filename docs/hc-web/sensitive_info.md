---
comments: true

---

# 敏感信息泄露


<!-- Imported from D:\\Book\\Web\\Chapter1\1-1.md -->
### 代码注释泄露


![](https://pic1.imgdb.cn/item/67b065bdd0e0a243d4ff9ef3.jpg)

打开网页一堆滑稽笑脸

![](https://pic1.imgdb.cn/item/67b065c8d0e0a243d4ff9efb.jpg)

F12 查看源代码拿到注释中的 flag

![](https://pic1.imgdb.cn/item/67b065f3d0e0a243d4ff9f14.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter1\1-10.md -->
### .DS_Store 文件泄露


![](https://pic1.imgdb.cn/item/6878b6d358cb8da5c8be7ec8.png)

`.DS_Store` 是 MacOS 保存文件夹的自定义属性的隐藏文件

通过 `.DS_Store` 可以知道这个目录里面所有文件的清单

访问下载文件

```
http://challenge-925075ffed70f5ad.sandbox.ctfhub.com:10800/.DS_Store
```

[使用工具解析文件](https://github.com/gehaxelt/Python-dsstore)

![](https://pic1.imgdb.cn/item/6878b79f58cb8da5c8be82bb.png)

再通过 curl 访问

![](https://pic1.imgdb.cn/item/6878b80658cb8da5c8be833c.png)


<!-- Imported from D:\\Book\\Web\\Chapter1\1-11.md -->
### .svn 文件泄露


![](https://pic1.imgdb.cn/item/6878ce9d58cb8da5c8bec1a7.png)

扫描发现有 `.svn/` 目录，确认是  `.svn`  泄露

使用 `dvcs-ripper` 工具中的 `rip-svn.pl` 脚本进行 clone

```perl
perl rip-svn.pl -u http://challenge-f54504e10cb99eb1.sandbox.ctfhub.com:10800/.svn/
```

![](https://pic1.imgdb.cn/item/6878cf9558cb8da5c8bec2bb.png)

1️⃣ **`entries`**

> **仅在旧版本 SVN（1.6 及以前）有用，新版废弃**

- **作用**：旧版 SVN 的目录、文件、状态信息记录（版本号 / 修改 / 是否忽略 / 路径关系等）
- **内容**：伪 XML 格式或纯文本
- **历史遗留**，现代 1.7+ 使用 `wc.db` 替代

```
plaintext复制编辑dir
9
https://svn.example.com/repo
...
```

------

2️⃣ **`format`**

> **作用**：标识当前 `.svn` 目录的元数据版本

| 数字 | 意义            | 对应版本 |
| ---- | --------------- | -------- |
| 8    | SQLite（wc.db） | 1.7      |
| 12   |                 | 1.8      |
| 29   |                 | 1.9      |
| ...  |                 | ...      |



举例内容：

```
12
```

> 表示该工作副本是 SVN 1.8 版本格式

------

3️⃣ **`pristine/`**

> **核心：文件内容仓库**

- 保存了**所有干净版本的源文件（未修改的原始版本）**
- 文件名是通过 `SHA1 哈希` 重命名后的，防止冲突、利于查找

```
.svn/pristine/ab/cd/abcdef1234567890.svn-base
```

- **作用**：用于对比工作区是否改动
- **本质**：存储的是**未被编辑的原始版本**，类似 Git 的 `objects/`

------

4️⃣ **`text-base/`**

> **1.6 以前旧结构**，现代 SVN 不再使用。

- 保存清理缓存的基线内容， `.svn-base` 后缀
- 每个工作区文件对比改动时用
- 与 `pristine/` 相似，但这是**旧版设计**

------

5️⃣ **`tmp/`**

> **临时文件目录**

- 执行 checkout / update / revert 时产生临时数据
- 类似于 `.git/objects/tmp`
- 意外中断操作后可安全删除

------

6️⃣ **`wc.db`**

> **SQLite 数据库，现代 SVN 的核心**

- **作用**：记录所有元数据信息
- **类型**：标准 SQLite 数据库
- **包含内容**：
  - 仓库信息（URL / UUID / 根路径）
  - 各文件状态（版本 / 是否修改 / lock 信息）
  - 各目录与版本号映射
  - 目录树层级关系
  - pristine 哈希索引

可以用 `sqlite3 wc.db .tables` 查看表：

| 表          | 含义                         |
| ----------- | ---------------------------- |
| NODES       | 各个节点（目录、文件）状态   |
| ACTUAL_NODE | 工作区实际状态（冲突、属性） |
| REPOSITORY  | 仓库信息                     |
| PRISTINE    | 哈希表映射至 pristine 目录   |
| LOCK        | 锁信息                       |
| WC_LOCK     | 工作目录锁                   |



👉 **核心：工作副本的实际状态都在这里！**

------

7️⃣ **`wc.db-journal`**

> SQLite 数据库的 **事务日志**

- 突然断电、进程崩溃，未提交事务保留在这里
- **正常关闭后自动消失**，此处为临时遗留无影响
- 如果一直存在可能表示该工作区未正常关闭

![](https://pic1.imgdb.cn/item/6878cfb258cb8da5c8bec2d7.png)

找到 flag

![](https://pic1.imgdb.cn/item/6878cff758cb8da5c8bec2f6.png)




<!-- Imported from D:\\Book\\Web\\Chapter1\1-12.md -->
### .hg 文件泄露


![](https://pic1.imgdb.cn/item/6878d0de58cb8da5c8bec787.png)

扫描发现有 `.hg/` 目录，确认是  `.hg`  泄露

使用 `dvcs-ripper` 工具中的 `rip-hg.pl` 脚本进行 clone

```perl
perl rip-hg.pl -u http://challenge-01f03d0aee8e33f2.sandbox.ctfhub.com:10800/.hg/
```

![](https://pic1.imgdb.cn/item/6878d15758cb8da5c8bec7ac.png)

1️⃣ **00changelog.i**

- **作用**：存储提交历史（changelog）的索引信息
- **内容**：二进制格式，指向实际存储内容（通常在 `store/data` 内的 `.i` / `.d` 文件）
- **理解**：类似 Git 的 `refs`，用于追踪变更集元信息的位置
- **扩展**：如果被删，仓库历史版本就会断裂不可恢复

------

2️⃣ **dirstate**

- **作用**：跟踪当前工作区（Working Directory）的状态
- **内容**：记录哪些文件被追踪，哪些被修改、添加、删除
- **理解**：Mercurial 使用它来快速判断 `status`
- **结构**：二进制，包含：
  - 当前父提交节点 ID
  - 文件状态（正常 / 修改 / 删除 / 添加 / 忽略 / 未追踪）
  - 时间戳缓存信息等

------

3️⃣ **last-message.txt**

- **作用**：记录最近一次提交信息的提交说明
- **内容**：纯文本，通常是最近一次 `hg commit -m '...'` 的内容
- **用途**：辅助撤销、恢复操作

------

4️⃣ **requires**

- **作用**：列出该仓库所依赖的 Mercurial 功能模块

- **内容**：文本格式，每行一个模块名。例如：

  ```
  revlogv1
  store
  fncache
  ```

- **影响**：Mercurial 启动仓库时读取它，确保兼容性

- **常见值**：

  - `revlogv1`：使用 revlog 第一版格式
  - `store`：数据在 `.hg/store`
  - `fncache`：文件名缓存机制（避免路径过长）

------

5️⃣ **undo.branch**

- **作用**：记录 `undo` 操作时恢复的分支
- **内容**：纯文本，分支名
- **用途**：撤销到该分支

------

6️⃣ **undo.desc**

- **作用**：记录 `undo` 的描述信息
- **内容**：纯文本，比如 "update"、"revert"
- **用途**：提示你撤销了什么操作

------

7️⃣ **undo.dirstate**

- **作用**：撤销时使用的 `dirstate` 快照
- **内容**：二进制，同 `dirstate` 格式
- **用途**：`hg undo` 时恢复工作目录状态

------

8️⃣ **store/**

- **作用**：存储仓库所有版本数据的核心目录
- **内容**：
  - `00manifest.i`: 跟踪清单（manifest）的索引
  - `data/`: 存放具体文件变更的 revlog 数据
  - `phaseroots`, `obsstore`: 变更历史的高级特性数据（可能未启用）
- **结构**：使用 `.i`（索引）与 `.d`（数据）二进制文件配对
- **重要性**：这里存储了全部版本数据。如果被破坏，仓库彻底失效

------

9️⃣ **wcache/**

- **作用**：`working directory cache`
- **内容**：缓存某些工作目录的状态，辅助性能
- **影响**：删除它不会丢数据，只是性能下降（会重新生成）

拿到 flag 名

![](https://pic1.imgdb.cn/item/6878d1e658cb8da5c8bec7d3.png)


<!-- Imported from D:\\Book\\Web\\Chapter1\1-2.md -->
### JavaScript 源码泄露


![](https://pic1.imgdb.cn/item/67b06656d0e0a243d4ff9f43.jpg)

打开网页是一个输入框

![](https://pic1.imgdb.cn/item/67b06676d0e0a243d4ff9f4a.jpg)

这里输入被限制了长度

可以通过前端修改 input 框的 text 的 max-length 值

也可以直接查看 JavaScript 源代码拿到 flag

先查看源码

![](https://pic1.imgdb.cn/item/67b0668fd0e0a243d4ff9f53.jpg)

看到引入了一个 code.js 文件（jquery 是框架的不用管）点击查看代码拿到 flag

![](https://pic1.imgdb.cn/item/67b066b0d0e0a243d4ff9f5c.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter1\1-3.md -->
### .git 文件泄露


![](https://pic1.imgdb.cn/item/67b067fcd0e0a243d4ff9fac.jpg)

网页啥也没有，先扫他目录

![](https://pic1.imgdb.cn/item/67b06810d0e0a243d4ff9fb1.jpg)

有个 flag.txt，但是是假的

![](https://pic1.imgdb.cn/item/67b06823d0e0a243d4ff9fbf.jpg)

还有个 .git 文件，下载下来查看

![](https://pic1.imgdb.cn/item/67b0683ad0e0a243d4ff9fc3.jpg)

git show 查看历史版本找到 flag

![](https://pic1.imgdb.cn/item/67b0684cd0e0a243d4ff9fc7.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter1\1-4.md -->
### .bak 文件泄露


![](https://pic1.imgdb.cn/item/67b062c5d0e0a243d4ff9d3c.jpg)

打开网页是个 md5

![](https://pic1.imgdb.cn/item/67b06891d0e0a243d4ff9fcc.jpg)

解密啥也不是

![](https://pic1.imgdb.cn/item/67b068afd0e0a243d4ff9fd0.jpg)

扫描后台发现 .bak 备份文件

![](https://pic1.imgdb.cn/item/67b068c5d0e0a243d4ff9fd1.jpg)

下载下来得到网页源码

![](https://pic1.imgdb.cn/item/67b068d9d0e0a243d4ff9fd6.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter1\1-5.md -->
### robots.txt 文件泄露


![](https://pic1.imgdb.cn/item/67b0692ed0e0a243d4ff9fe0.jpg)

访问页面啥也没有

![](https://pic1.imgdb.cn/item/67b06940d0e0a243d4ff9fe2.jpg)

扫描后台只有一个 robots.txt 文件

![](https://pic1.imgdb.cn/item/67b0695cd0e0a243d4ff9fe6.jpg)

访问得到一个禁止访问的 resusl.php

![](https://pic1.imgdb.cn/item/67b0696ed0e0a243d4ff9fe9.jpg)

URL 跟上访问给出了一段源代码

![](https://pic1.imgdb.cn/item/67b0691ed0e0a243d4ff9fdf.jpg)

结合题目名称传参 x=admin 拿到 flag

![](https://pic1.imgdb.cn/item/67b06910d0e0a243d4ff9fdc.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter1\1-6.md -->
### SSL 证书泄露


![](https://pic1.imgdb.cn/item/67b069ced0e0a243d4ff9ff6.jpg)

题目翻译就问这个网站什么时候从 HTTP 转到了 HTTPS

如果自己搭建过网站同学都知道，申请 HTTPS 是需要 SSL 证书的

这个证书可以去在线网站查询的，去这个网站查询域名可以看到证书信息

![](https://pic1.imgdb.cn/item/67b069fad0e0a243d4ff9ffe.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter1\1-7.md -->
### 网站历史信息泄露


![](https://pic1.imgdb.cn/item/67b06a7bd0e0a243d4ffa008.jpg)

考察的信息搜集能力，web.archive.org 免费提供全球网站历史信息查询服务，最早可追溯到 1996 年

![](https://pic1.imgdb.cn/item/67b06a96d0e0a243d4ffa00d.jpg)

具体题目提供的时间查找快照

![](https://pic1.imgdb.cn/item/67b06aaad0e0a243d4ffa00e.jpg)

往下翻拿到 flag

![](https://pic1.imgdb.cn/item/67b06abed0e0a243d4ffa011.jpg)


<!-- Imported from D:\\Book\\Web\\Chapter1\1-8.md -->
### JavaScript 接口泄露


![](https://pic1.imgdb.cn/item/68166abe58cb8da5c8da0592.png)

打开网页不让 F12 以及右键

![](https://pic1.imgdb.cn/item/68166ab358cb8da5c8da0591.png)

Ctrl + U 发现有个 PHP 文件

![](https://pic1.imgdb.cn/item/68166b0a58cb8da5c8da059e.png)

访问页面后再次查看源码给出了提示

![](https://pic1.imgdb.cn/item/68166b4958cb8da5c8da05a8.png)

[安装工具](https://github.com/s0md3v/Arjun?tab=readme-ov-file)

```python
pip install arjun
```

![](https://pic1.imgdb.cn/item/68166bab58cb8da5c8da05b0.png)

执行命令

```shell
arjun -u http://challenge.qsnctf.com:31303/c3s4f.php
```

可以发现有个 `shell` 参数

![](https://pic1.imgdb.cn/item/68166c4c58cb8da5c8da05c4.png)

传入参数给出了新提示

![](https://pic1.imgdb.cn/item/68166cbb58cb8da5c8da05d0.png)

扫描目录发现有个 `secret.php`

![](https://pic1.imgdb.cn/item/68166dab58cb8da5c8da05e3.png)

只允许本地访问

![](https://pic1.imgdb.cn/item/68166d8958cb8da5c8da05dd.png)

结合提示以为是要伪造 XFF 或者 Client-IP，试过了都不行

利用 `shell` 参数构造 SSRF

```html
?shell=http://127.0.0.1/secret.php
```

无果

![](https://pic1.imgdb.cn/item/68166e4e58cb8da5c8da05ef.png)

使用域名跳转绕过

```
?shell=http://localtest.me/secret.php
```

![](https://pic1.imgdb.cn/item/68166ec458cb8da5c8da05fa.png)

访问拿到源码

![](https://pic1.imgdb.cn/item/68166f2258cb8da5c8da0601.png)

```php
<?php
show_source(__FILE__);
include('k4y.php');
include_once('flag.php');


// Challenge 1
if (isset($_GET['DrKn'])) {
    $text = $_GET['DrKn'];
    if(@file_get_contents($text) == $key) {
        echo "有点东西呢"."</br>".$key1."</br>";
    } else {
        die("貌似状态不在线啊(╯_╰)</br>");
    }
} 
    

// Challenge 2
if (isset($_GET[$key1])) {
    $damei = $_GET[$key1];
    if (hash("md4", $damei) == $damei) {
        echo "又近了一步呢，宝~"."</br>".$key2."</br>".$key3;
    } else {
        die("达咩哟~");
    }
} 


// Challenge 3
if (isset($_POST[$key2]) && isset($_POST[$key3])) {
    $user = $_POST[$key2];
    $pass = $_POST[$key3];
  
    if (strlen($user) > 4 || strlen($pass) > 5) {
          die("还得练");
      }
     if ($user !== $pass && md5($user) === md5($pass)) {  
          echo "还不错哦"."$flag";
      }
      else {
          die("nonono") ;
      }
    }

?>
```

第一关就是传入给出的 Key，但是需要用到 `data` 伪协议

![](https://pic1.imgdb.cn/item/6816712558cb8da5c8da0628.png)

第二关是一个 `md4` 的弱比较绕过，其实可以通过科学计算法比较绕过

也就是说要找一个明文是一个科学计算法 0e 开头的，然后其加密也是 0e 开头后面都是数字

```
&M_ore.8=0e001233333333333334557778889
```

最后一关就是 `md5` 强比较绕过，都为数组即可

![](https://pic1.imgdb.cn/item/681671c258cb8da5c8da0638.png)


<!-- Imported from D:\\Book\\Web\\Chapter1\1-9.md -->
### .swp 文件泄露


![](https://pic1.imgdb.cn/item/6878b49d58cb8da5c8be6cca.png)

利用 wget 下载文件

因为 vim 使用的缓存存储为一种`固定格式的二进制文件`，而我们一般编辑的时明问可见字符，在 vim 的缓存中这些可见字符会原样保留

![](https://pic1.imgdb.cn/item/6878b5f458cb8da5c8be7677.png)
