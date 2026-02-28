# web-nginx-php73

部分容器逻辑参考自：[CTFTraining / base_image_nginx_php_73](https://github.com/CTFTraining/base_image_nginx_php_73)，在此感谢 [陌竹 - mozhu1024](https://github.com/mozhu1024) 师傅做出的贡献

## 环境说明

提供 `Nginx` +`PHP 7.3.33` 的基础环境，默认暴露端口位于 80

> 请注意 !!!
>
> 需要注意的是，模板默认会将 flag 保存在 / flag 文件中，如果 PHP 项目中需要直接从环境变量中读取 flag 数据，请在./service/docker-entrypoint.sh 中修改相关操作语句

## 如何使用

直接将 PHP 项目放入 `./src` 目录即可

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
