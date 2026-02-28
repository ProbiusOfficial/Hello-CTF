# crypto-python_3.8-with_socket

## 环境说明

提供 `Python 3.8` 的基础环境，并已经添加 `pycryptodome` 库，并基于项目本身实现相关接口

实现：当选手连接到对应服务端口（由项目自行定义）的时候，运行 `.py项目`

此环境适用于项目中引入了 `socket` 等库，需要镜像做到：
- 选手通过端口连接到容器/靶机
- 启动项目
- 项目自行处理会话

## 如何使用

直接将py文件/项目放入 `./src` 目录即可，文件名建议使用 `main.py` ，便于环境识别，如需更改文件名，请在 `./service/docker-entrypoint.sh` 内更改

如使用了 `gmpy2` 等第三方库，请在 `./Dockerfile` 内补充pip安装语句

源码放置进 `./src` 目录之后，执行 
```shell
docker build .
```
即可开始编译镜像

也可以在安放好相关项目文件之后，直接使用 `./docker/docker-compose.yml` 内的 `docker-compose` 文件实现一键启动测试容器

```shell
cd ./docker
docker-compose up -d
