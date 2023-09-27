---
comments: true

---
类型介绍:

反射型

反射型跨站脚本（Reflected Cross-Site Scripting）是最常见，也是使用最广的一种，可将恶意脚本附加到 URL 地址的参数中

反射型 XSS 的利用一般是攻击者通过特定手法（如电子邮件），诱使用户去访问一个包含恶意代码的 URL，当受害者点击这些专门设计的链接的时候，恶意代码会直接在受害者主机上的浏览器执行。此类 XSS 通常出现在网站的搜索栏、用户登录口等地方，常用来窃取客户端 Cookies 或进行钓鱼欺骗。

 

存储型

持久型跨站脚本（Persistent Cross-Site Scripting）也等同于存储型跨站脚本（Stored Cross-Site Scripting）。

此类 XSS 不需要用户单击特定 URL 就能执行跨站脚本，攻击者事先将恶意代码上传或储存到漏洞服务器中，只要受害者浏览包含此恶意代码的页面就会执行恶意代码。持久型 XSS 一般出现在网站留言、评论、博客日志等交互处，恶意脚本存储到客户端或者服务端的数据库中。

 

DOM型

传统的 XSS 漏洞一般出现在服务器端代码中，而 DOM-Based XSS 是基于 DOM 文档对象模型的一种漏洞，所以，受客户端浏览器的脚本代码所影响。客户端 JavaScript 可以访问浏览器的 DOM 文本对象模型，因此能够决定用于加载当前页面的 URL。换句话说，客户端的脚本程序可以通过 DOM 动态地检查和修改页面内容，它不依赖于服务器端的数据，而从客户端获得 DOM 中的数据（如从 URL 中提取数据）并在本地执行。另一方面，浏览器用户可以操纵 DOM 中的一些对象，例如 URL、location 等。用户在客户端输入的数据如果包含了恶意 JavaScript 脚本，而这些脚本没有经过适当的过滤和消毒，那么应用程序就可能受到基于 DOM 的 XSS 攻击。

 

常见的标签

1.alert()

alert(‘xss’)

alert(“xss”)

alert(/xss/)

alert(document.cookie)

2.confirm()

confirm(‘xss’)

confirm(“xss”)

confirm(/xss/)

confirm(document.cookie)

3.prompt()

prompt(‘xss’)

prompt(“xss”)

prompt(/xss/)

prompt(document.coolkie)

(/xss/)以上三种方法都可以实现，但是会多出两个‘/’

4.document.write()

- document.write('<script>alert("xss")<\/script>')

- document.write('<script>alert(/xss/)<\/script>')

- document.write('<script>alert(document.cookie)<\/script>')

括号里不能使用单引号；

alert也可以换成其他弹窗方式；

5.console.log()

console.log(alert(‘xss’))

console.log(alert(“xss”))

console.log(alert(/xss/))

console.log(alert(document.cookie))

6.输出控制台

1.console.error(111)

2.console.log(document.cookie)

3.console.dir(111)
靶场练习

https://alf.nu/alert1

https://github.com/do0dl3/xss-labs

http://xss-ctf.xiejiahe.com/