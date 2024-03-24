# web-flask-python_3.10

## 环境说明

提供 `Python 3.10 + Flask` 的基础环境，默认暴露端口位于8080

## 如何使用

直接将Flask文件/项目放入 `./src` 目录即可，Flask项目主文件请使用 `app.py` 作为文件名，便于环境识别Flask项目位置

如使用了 `pycryptodome` 等第三方库，请在 `./Dockerfile` 内补充pip安装语句

源码放置进 `./src` 目录之后，执行 
```shell
docker build .
```
即可开始编译镜像

也可以在安放好相关项目文件之后，直接使用 `./docker/docker-compose.yml` 内的 `docker-compose` 文件实现一键启动测试容器

```shell
cd ./docker
docker-compose up -d
```