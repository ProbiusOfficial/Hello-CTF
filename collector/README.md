# Hello-CTF 消息收集器

部署在有公网 IP 的机器上，代替面板服务器接收浏览器端的赛事提交和意见反馈
（面板服务器没有公网 IP，由面板主动来拉取，拉取代推送）。

## 运行

### Docker（推荐）

```bash
cd collector
echo "COLLECTOR_TOKEN=一串足够长的随机串" > .env
docker compose up -d --build
```

消息持久化在 `./data/messages.json`，容器重启不丢。更新代码后 `docker compose up -d --build` 即可。

### 裸机

零依赖（Python 3 标准库）：

```bash
export COLLECTOR_TOKEN=一串足够长的随机串   # 必填，管理接口令牌
python3 app.py                              # 默认 0.0.0.0:9100
```

可选环境变量：`COLLECTOR_PORT`（默认 9100）、`COLLECTOR_FILE`（消息存储路径，
容器内默认 `/data/messages.json`，裸机默认同目录 `messages.json`）、
`COLLECTOR_PUSH_URL`（[Server酱³](https://doc.sc3.ft07.com/zh/serverchan3) 推送地址，
形如 `https://<uid>.push.ft07.com/send/<sendkey>.send`，设置后新留言实时推送到手机，
推送失败不影响提交）。
建议前面套一层 Caddy/Nginx 上 HTTPS。

## 接口

| 接口 | 鉴权 | 说明 |
| --- | --- | --- |
| `POST /api/submit` | 公开（CORS 放开） | `{type: "event"\|"feedback", title, content}` |
| `GET /api/messages` | `X-Token` 头 | 拉取全部消息 |
| `POST /api/messages/delete` | `X-Token` 头 | `{id}` 删除 |

## 面板侧配置

在管理面板 `admin/config.json` 填：

```json
"inbox_url": "https://你的公网域名或IP:9100",
"inbox_token": "与 COLLECTOR_TOKEN 相同的值"
```

网站侧 `docs/submit_event.html` 的推送地址指向本收集器的 `/api/submit`。
