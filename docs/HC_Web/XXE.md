---
comments: true

---

# XXE (XML External Entity) 

## 简介

XML External Entity (XXE) 是一种利用 XML 解析器漏洞的攻击技术。通过利用 XXE 漏洞，攻击者可以访问服务器文件系统，执行远程代码，或实施其他恶意行为。本文将介绍 XXE 攻击的基本原理、常见的攻击手法以及防御措施。

## 什么是 XXE 攻击

XXE 攻击是一种基于 XML 的攻击技术，攻击者通过在 XML 文档中注入外部实体 (External Entity)，诱使 XML 解析器读取或解析不应该访问的资源。常见的外部实体包括文件、网络资源等。

