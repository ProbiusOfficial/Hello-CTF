# KOH题目出题文档_NSSCTF

## KOH后端原理

KOH题目是基于HTTP服务与后端评判系统进行交互的,故题目容器需要启动一个标准的HTTP服务，并对外暴露HTTP服务端口。

为了确保题目能够正常与后端进行交互，HTTP服务需要包含以下路由并进行相应处理：

### upload

```python
@app.route('/upload', methods=['POST'])
def upload():
	pass
```

该路由负责接收用户上传的数据。数据将以表单数据的形式进行上传，参数名为file。

例如，后端向容器内的HTTP服务发送请求的代码如下，其中超时时间为5秒：

```python
requests.post(f'http://{url}/upload', files={
'file': (filename, content)
}, timeout=5)
```

如果HTTP服务在5秒内正常处理该路由，并且没有异常发生，应返回以下JSON数据：

```json
{
	"code": 200
}
```

如果遇到异常（例如服务异常、连接异常、超时异常、返回值异常），则直接判定此次结果为**错误**。

（一般情况下，200以外的任何返回代码，我们都记为 **错误** ）

### check

```python
@app.route('/check', methods=['POST'])
def check():
	pass
```

当后端完成对/upload路由的访问且没有异常时，将访问/check路由。访问示例代码如下：

```python
requests.post(f'http://{url}/check', timeout=10)
```

超时时间为**10**秒。靶机需要在此时间内评估用户上传内容的得分情况，并返回JSON结果，例如：

```json
{
	"code": 200,
	"score": 100
}
```

如果遇到异常（例如服务异常、连接异常、超时异常、返回值异常），则直接判定此次结果为**错误**。如果以上过程没有异常，判断过程结束，并将得到的score更新为用户的得分。

- 判题靶机目前为一人一机，上次判题完成前无法上传新的文件，无需考虑多线程以及资源抢占的情况。
- 应尽可能保证服务的可用性。对于需要运行时要求的靶机，应使用chroot等沙盒技术来运行独立的进程，以防止用户代码直接控制靶机来控制HTTP服务的返回值。
- HTTP返回数据应确保返回头包含Content-Type: application/json头，而不是直接返回JSON字符串。



## DockerFile文件说明

* 该题为文件上传KOH题，故只需要完成保存文件 比较文件即可判断得分，如果需要进行代码执行，可以参考app.py中注释代码中使用subprocess建立chroot沙盒的方式进行执行。

* 注意为了安全起见，在Dockerfile中删除了一些包，如有使用需要请手动更改。

    ```bash
    RUN rm -f /home/ctf/usr/local/lib/python3.10/sockert.py && \
    rm -f /home/ctf/usr/local/lib/python3.10/sockertserver.py && \
    rm -rf /home/ctf/usr/local/lib/python3.10/site-package && \
    rm -f /home/ctf/usr/local/lib/python3.10/subprocess.py
    ```

* 该靶机为python3靶机，如需使用其他环境，关于chroot部分依然可以参考Dockerfile中对/home/ctf的改造方法（/home/ctf即为沙盒环境根目录）