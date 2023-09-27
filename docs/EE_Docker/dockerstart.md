## About

!!! alert "注意"  
    阅读本文需要一定自学能力基础，本文将尽量以最小的篇幅来辅助您从docker基础操作快速过渡到使用docker对题目进行复现 封装 以及部署等操作，大多地方本文将略写如有需要请自行使用搜索引擎或者在StackOverflow上寻找相关解决方案，当然您也可以按照顺序阅读我们后面Docker部分的详细教程。

不管是在实际开发中，还是单说CTF 或者安全领域，学会使用容器技术可以极大的提升工作效率，docker拥有许多优点，配置简化，跨平台，方便共享，快速部署，快速启动......  

本文涉及的使用场景：

- Docker镜像的封装 | Docker容器的使用
- Dockerfile | Docker-compose

- 【Dockers在CTF中的使用】CTF题目的本地部署 / 复现 | 命题 | 封装 | 分发

文档所用的docker模板文件均可在 [CTF-Archives/ctf-docker-template](https://github.com/CTF-Archives/ctf-docker-template) 中获取。

## Docker简介

>快速开始你看什么历史（
>如果有需要，该部分读者可以自行搜索，篇幅原因，就不再介绍了。

Docker 三个基本概念： **「 镜像 Image 」** **「 容器（Container）」** **「 仓库（Repository）」**

>Docker 容器通过 Docker 镜像来创建。

对于CTF题目，除了纯附件题目，大部分题目均使用docker进行分发，题目通常被封装为镜像存储于Docker仓库中，第一次分发时，比赛平台会先从仓库获取镜像到本地，然后再通过镜像去创建容器，从而实现为每个选手分发题目。

这里说到的仓库，指的是[Docker Hub](https://hub.docker.com/)，一般情况下，我们对镜像的分发都基于该仓库。

在本地使用时 我们不会对 镜像名字有特殊要求 但是当您需要将您的镜像上传到仓库分发 供他人或者平台使用时，您需要了解下面几个点：

- 您需要一个DockerHub账号来完成镜像的推送分发操作
- 您的镜像名要按照类似于 **<用户名> / <仓库名>:<标签>**
    > 例如：`probius/litctf2023:Web_SQL`  ,如果不给出标签，将以 latest 作为默认标签
    > 当您或者平台需要拉取该镜像时，将会使用 `docker pull probius/litctf2023:Web_SQL` 将镜像拉取到本地
    

## Docker安装

>本文默认你已经配置好了docker环境，如果没有，请自行搜索安装教程，或者参考[官方文档](https://docs.docker.com/install/)。
>或者您也可以访问我们的教程



## 基础操作

>请养成使用产品前阅读文档的好习惯，官方文档地址：[https://docs.docker.com/](https://docs.docker.com/)

```bash
docker run    # - 创建一个新的容器并运行一个命令
docker attach # - 连接到正在运行中的容器
docker exec   # - 在运行的容器中执行命令
docker commit # - 从容器创建一个新的镜像
docker build  # - 命令用于使用Dockerfile创建镜
docker cp     # - 用于容器与主机之间的数据拷贝
docker ps     # - 列出容器
docker images # - 列出本地镜像
docker pull   # - 从镜像仓库中拉取或者更新指定镜像
docker push   # - 将本地的镜像上传到镜像仓库，要先登陆到镜像仓库
docker kill   # - 杀掉一个运行中的容器
docker login  # - 登陆到一个Docker镜像仓库，如果未指定镜像仓库地址，默认为官方仓库Docker Hub
docker logs   # - 获取容器的日志
docker rm     # - 删除一个或多少容器
docker rmi    # - 刷除本地一个或多少镜像?
...
```

## Dockerfile

Dockerfile是构建docker镜像的基础 
