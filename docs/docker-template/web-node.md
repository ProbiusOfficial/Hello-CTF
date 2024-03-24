# web-tomcat-jdk8

## 环境说明

提供 `Tomcat 9.0.78 Openjdk 1.8.0` 的基础环境，默认服务暴露端口由程序决定

适用于基于 `war` 程序包部署环境的需求

**实例用war包来自于[ pH-7 / SimpleJspWebsite ](https://github.com/pH-7/SimpleJspWebsite)**

## 如何使用

直接将 `war` 程序包放入 `./src` 

源码放置进 `./src` 目录之后，执行 
```shell
docker build .
```
即可开始编译镜像

也可以在安放好相关项目文件之后，直接使用 `./docker/docker-compose.yml` 内的 `docker-compose` 文件实现一键启动测试容器（默认服务端口为8080，如服务暴露在其他端口，请修改 `./docker/docker-compose.yml` 文件）

```shell
cd ./docker
docker-compose up -d
```