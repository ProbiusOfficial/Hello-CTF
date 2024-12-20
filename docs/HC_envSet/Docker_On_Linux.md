---
comments: true

---

# 在Linux上部署Docker环境

本文也有配套视频，建议结合食用：(给个三连吧www)
https://www.bilibili.com/video/BV1684y1z7L6

## About

本文档完整的流程可以帮助您在 **Kali Linux** 上完成Docker环境，并且基于 VSCode 的Remote 功能，利用SSH协议，构建 VSCode + SSH + Docker 的工作流，提高效率。
同样，本文档也考虑了非Kali，用于开发/生产环境的 **Ubuntu / Debian** 系统 ，如果您想要在开发/生产中使用该工作流，可以直接从 **Get Docker** 或者 **Build SSH + VSCode + Docker Workflow** 章节开始。
笔者水平有限，错误疏漏之处在所难免，烦请各位师傅斧正。
以及非常感谢 **陈橘墨 (@*Randark_JMT*) 师傅** 提供的帮助。

## Get Kali

### Download

在Kali官网下载即可，建议直接下载封装好的虚拟机版本：
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108984.png)
解压下载好的压缩包到您想要放置虚拟机的位置，然后双击配置文件直接打开自动添加，或者在VMware中手动添加：
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108041.png)
添加完成后，启动即可：
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108250.png)
（当然，作为Docker Runner，您可能需要设置一个稍微大点的内存值）
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108214.png)

### Change Source？

笔者并不建议换源，Kali官方源的速度还是不错的，换源可能会导致您软件管理出现问题。

## Get Docker

### Install

Docker安装目前有两个版本，一个是官方的 **docker.ce** 版本，一个是有Debian团队维护的 **[docker.io](http://docker.io/)** 版本。  
之前有争议说 [docker.io](http://docker.io/) 是旧版本的Docker 而新版的Docker是 docker.ce  
然而docker.io的版本有时会比docker.ce高，事实上，两者只是负责维护的组织不同，前者是Debian官方维护，后者则为Docker官方维护，并没后新旧之分：

#### [docker.io](http://docker.io/)

该版本由Debian团队维护，采用 apt 的方式管理依赖  
安装过程：

```bash
sudo apt-get update
sudo apt install docker.io
```

![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108106.png)
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108155.png)
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108090.png)

#### docker.ce

由Docker官方维护的版本，采用 go 的方式管理依赖，如果您要在开发/生产环境中使用Docker，推荐使用该版本。  
如果您的Linux版本为Ubuntu/Debian，可以使用一下命令自动安装：

```bash
wget -qO- https://get.docker.com/ | sh
```

（注意，Docker并不支持Kali一键安装，同样笔者也不推荐您用Kali作为开发生产环境，Kali满足日常需要，使用io版本即可，当然您也可以使用.ce版本的手动安装）

手动安装：  
可以参考[Docker官方的 Docker Engine安装步骤](https://docs.docker.com/engine/install/debian/)  
但是该步骤在 Kali Linux上面可能会存在一定问题，以Kali为例，完整的安装流程如下：  

```bash
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108273.png)  
选项选择Yes就好。  
然后按照官网提示，添加Docker官方的 GPG key：

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

然后设置仓库：

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

然后开始安装：

```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

随后，如果您是Kali Linux，您可能会遭遇以下报错：

![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108058.png)
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108673.png)  
这是由于Docker官方并没有提供直接支持Kali的源，所以我们使用Debian的源就好：

```bash
printf "%s\n" "deb [arch=amd64] https://download.docker.com/linux/debian buster stable" |\
sudo tee /etc/apt/sources.list.d/docker-ce.list
```

并且添加对应的密钥：

```bash
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
```

注意不要忘了给密钥相应权限：

```bash
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

此时再跑一次 `sudo apt-get update`:

您可能会遇到一个找不到的源，这个是正常的。
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108201.png)

接下来安装Docker：

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

就能正常获取了：
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108660.png)

安装完成后，运行hello-world容器，得到图示则安装成功。

```bash
sudo docker run hello-world
```

![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108202.png)

### Docker Hub

尝试登录您的**Docker Hub**账号：
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108423.png)  
如果出现类似错误，请手动配置DNS：

```bash
sudo vim /etc/resolv.conf
```

![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108043.png)  
保存，再次尝试即可成功登录：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108243.png)

## Build SSH + VSCode + Docker Workflow

该步骤适用于支持SSH协议的Linux ~~（废话，哪个Linux没有个SSH）~~ ，除了在本地的Kali或者其他Linux上面构建，也支持远程构建该工作流。

### Start SSH Service

#### Kali Linux

Kali虚拟机默认是没有开启SSH服务的 （SSH状态：`/etc/init.d/ssh status`）
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108687.png)  
所以需要手动启动一下：

```bash
sudo /etc/init.d/ssh start 
```

当然，为了方便，我们将ssh添加到开机自启中：

```bash
sudo update-rc.d ssh enable
# Or use:
systemctl enable ssh.service
```

![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108870.png)  
启动之后就可以开始后面的步骤了。

#### Ubuntu

由于Ubuntu默认不自带openssh-server，所以这里需要手动安装。
安装openssh-server：

```bash
sudo apt-get install openssh-server
```

安装完成后启动服务：

```bash
sudo service ssh start
```

### Get Remote - SSH Extension

为了使用VSCode的远程SSH功能 您可能需要在扩展中安装`Remote - SSH`插件：
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108363.png)

### Let VSCode Connect to Host

连接方式有两种：`密码连接` 和 `SSH的公私钥`。
一般情况下我们使用密码连接，这样的方法安全性较低，而且每次连接和每次切换目录的时候都会要求输入密码，所以在确保能够密码连接情况下，我们可以进一步使用公私钥验证的方式来提升安全性和优化操作友好性。

#### Using Password Connection

打开VSCode，点击左下角的远程连接（绿色的部分）  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108580.png)  
接着在弹出的窗口中选择 Connect to Host  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108159.png)  
选择 `Add New SSH Host`：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108672.png)  
按照要求输入对应的指令：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108860.png)  
IP可通过 `ip a` 获取  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108321.png)  
`ssh kali@192.168.28.145 -A`  
保存位置默认第一个就好：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108500.png)  
然后连接：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108023.png)  
选择对应的系统：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108268.png)  
选择继续：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108889.png)  
输入密码：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108092.png)  
初始化完成后就连接上了：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108596.png)  

#### Using Public and Private Keys

##### Create Public and Private Keys

首先在本机上生成对应的公钥私钥：

```
ssh-keygen
```

![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108885.png)

```
Enter file in which to save the key (C:\Users\Probius/.ssh/id_rsa):
```

输入保存路径，如果为空默认为 `C:\Users\USERNAME\.ssh\id_rsa`，这里笔者直接输入了名字，让其以该名字直接保存在当前目录

```
Enter passphrase (empty for no passphrase):
```

输入私钥密码，为空则没有

```
Enter same passphrase again:
```

注意：如果您使用了私钥密码，那么在进行ssh登录的时候，会提示您输入私钥密码，相当于再使用公私钥登录的情况下又加了一层密码，安全性有很大的提升，但是这样会变得和密码登录一样每次都要输入，这里笔者建议，如果是本地一路回车就好了，如果是远程资源的管理，可以综合安全性考虑

生成过后，得到的`id_rsa.pub`(Kali_test.pub)是 **公钥** ，`id_rsa`(Kali_test)是 **私钥**  
将得到的私钥放在我们的.ssh(C:\Users\USERNAME\\.ssh\\)中。  
(您也可以在生成的时候就让他放置在此，当然这并不是重点）

##### Configure Remote Host

将得到的公钥上传到 Kali/服务器中对应用户的.ssh文件夹中(请确保该文件夹至少有700的权限)：
（注意 Kali默认没有该文件夹，需要用户手动创建，并且赋700权限 `mkdir ~/.ssh` ）
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108425.png)  
在此处打开终端，用公钥文件来生成 authorized_keys：

```bash
cat id_rsa.pub >> authorized_keys
# 此处即 cat Kali_test.pub >> authorized_keys
```

![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108635.png)  
由于Linux系统对.ssh拥有比较严格的权限限制，请确保权限配置正确：

```bash
sudo chmod 600 authorized_keys
sudo chmod 700 ~/.ssh
```

编辑ssh配置文件

```bash
sudo vim /etc/ssh/sshd_config
```

确保拥有以下条目：

```
RSAAuthentication yes
PubkeyAuthentication yes
```

注意Kali的SSH默认配置是没有上述两项的，需要自行添加：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108226.png)  
然后搞定一切后，重启SSH服务：

```bash
sudo service ssh restart
```

Linux部分的配置这样就搞定啦~  
（在您确保您的连接无误后，如果是服务器等远程设备，可以在config中关闭密码登录以提升安全性：
`PasswordAuthentication no`）

##### Configure Local Host

然后是Windows，也就是VSCode这边的配置：

添加New Host：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108830.png)

使用：

```bash
ssh USERNAME@IP -i C:\\Users\\USERNAME\\.ssh\\RSA_ID
```

（注意使用指令添加时，务必使用双斜杠）  
当然，也可以在已经添加的配置文件上改：

```
Host IP
	HostName HOSTNAME
	User USERNAME
	IdentityFile C:\Users\USERNAME\.ssh\Kali_test
```  
(根据自己的实际配置修改IP、HOSTNAME、USERNAME值)

如果操作无误，且没有设置私钥密码，那么点击连接之后无需其他额外操作即可连接；如果设置了私钥密码，那么按照提示输入即可。

##### Other - About SSH Key Login

关于SSH密钥登录的更多知识可以看这一篇文章：[SSH 密钥登录](https://webdoc.p2hp.com/ssh/key.html)

### Get Docker Extension

#### Install

![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108387.png)  
（当然 如果显示的是 `安装`也是一样的）  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108927.png)

#### Common Problem Solution

如果您安装Docker时使用自动安装，应该不会遇到该问题，自动安装的脚本会自动完成用户组添加的操作。  
由于权限原因，我们可能无法访问到 `/var/run/docker.sock`  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108599.png)

##### By Adding User Group

一劳永逸的解决权限问题，将当前用户组添加到Docker组即可。
创建Docker用户组，默认安装时就会自动创建，所以执行可能会显示`exist`

```bash
sudo groupadd docker 
```

添加当前用户到该组：

```bash
sudo usermod -aG docker ${USER} 
```

然后重新启动容器服务：

```bash
sudo systemctl restart docker 
```

再次重新登入即可，如果重新登录之后依旧报错无法读取，请尝试重启：

```bash
reboot
```

##### By chmod Command

也可以使用`sudo chmod 777 /var/run/docker.sock`，但是每次重启之后权限都会重置，不推荐  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108210.png)  
然后就能正常访问了：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108359.png)

### Start Using Docker

（以下操作使用 **Docker Hub** 演示）
因为在安装Docker的时候登录过Docker Hub，所以这里连接之后，系统会自动获取您的凭证，您可以在这查看您的Docker Hub仓库：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108556.png)  
当然，您也可以添加其他仓库，具体的用法可以参考官方文档：

#### Pull Images

当然 对于自己仓库的镜像还是比较方便的233：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108132.png)  
当然如果是公开镜像的话 还是免不了指令啦，不过还是比较方便的，旁边就是终端：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108350.png)  
完成之后就能在IMAGES栏看到了：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108863.png)

#### Run Docker

运行容器有两个选项Run / Run Ineractive

##### Run

默认后台运行，Run执行后效果和在Linux执行 -d的效果相同：
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108098.png)
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108618.png)

##### Run Ineractive

该选项运行执行后，除了运行容器，还会跳到容器的汇总shell处，这里会实时打印容器日志，  
效果和 `View Log`效果相同：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108893.png)

#### View Log

直达容器后台日志，如果在运行的时候选择`Run Ineractive`那么也会跳转到该log页面。  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108575.png)  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108780.png)

#### Attach Shell

右键选中之后可以直接建立一个容器内部的shell，省去`docker exec -i -t ID /bin/bash`  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108362.png)  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108563.png)

#### Edit Container

在CONTAINERS中下拉一个容器的file可以对其进行查看和编辑：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108051.png)  
可以看到对于容器来说 修改是即时的（支持热更新的）  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108737.png)

#### Attach Container (Advanced Edit?)

我们也可以用VSCode建立类似SSH的连接，直接连接到整个容器：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108906.png)  
并且操作同步：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108429.png)  
而且容器支持文件拖拽，相比单纯的COPY指令 拥有更好的体验（个人感觉

#### Port Forward

通过SSH直接将远程端口转发到本地，免除防火墙困扰ww  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108117.png)  
一般来讲在您启动容器的时候 VSCode会自动配置 当然为了更好的区分和避免冲突 也可以手动分配  
配置如图：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108383.png)

#### Open in Browser

如果您配置完成了端口转发(或者VSCode自动为您完成配置) 那么点击Open in Browser将在您的默认浏览器中快速打开该端口对应的页面：  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108971.png)  
![image.png](https://nssctf.wdf.ink//img/WDTJ/202302072108177.png)



