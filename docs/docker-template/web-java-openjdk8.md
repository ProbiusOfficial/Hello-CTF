# web-java-jar-openjdk8

## 环境说明

提供 `Openjdk 1.8.0` 的基础环境，默认服务暴露端口由程序决定

适用于基于 `jar` 程序包部署环境的需求

## 如何使用

直接将 `jar` 程序包放入 `./src` 目录即可，jar程序包请使用 `app.jar` 作为文件名，便于环境识别 `jar` 程序包

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