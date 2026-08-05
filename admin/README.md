# Hello-CTF 站点管理面板

Flask 后端 + 无构建步骤的原生 HTML/JS 前端，用于在浏览器里管理赛事、首页内容、文档和部署。

## 安装与首次运行

面板自身依赖只有 Flask 和 requests（系统 Python 已装）。部署功能需要 mkdocs，
由于系统 Python 受 PEP 668 限制，mkdocs 等站点依赖装在项目根的 `.venv` 里：

```bash
# 站点依赖（只需一次）：创建 .venv 并安装
python3 -m venv .venv            # 若提示缺 python3-venv，用 python3 -m venv --without-pip .venv 再引导 pip
.venv/bin/pip install -r requirements.txt

# 面板配置与启动
cp admin/config.example.json admin/config.json   # 然后编辑 config.json
python3 admin/app.py
```

部署/预览任务会自动优先使用 `.venv/bin/python` 和 `.venv/bin/mkdocs`，无需手动激活虚拟环境。

面板监听 `0.0.0.0:9000`，内网访问地址：`http://<本机IP>:9000`。
`admin/config.json` 已加入 `.gitignore`，不会被提交。密码也可以用环境变量
`ADMIN_PASSWORD` 代替配置文件。

## 配置项

| 键 | 说明 |
| --- | --- |
| `admin_password` | 面板登录密码（必填） |
| `port` | 监听端口，默认 9000 |

## 功能

- **赛事管理**：直接维护本仓库 `docs/Event/json/CN.json`（仅国内赛事），支持添加 / 编辑 / 删除，
  保存后自动 `git pull --rebase → commit → push`（commit message：`admin: add/update/delete event <name>`）。
  字段只有名称 / 链接 / 起止时间 / 详情（默认 `赛制/类型: Jeopardy`），状态由比赛时间自动推导
  （即将开始 / 正在进行 / 已经结束）。国外赛事由 `build.py` 每日从 CTFtime RSS 抓取，无需人工维护。
- **首页内容**：编辑 `docs/index_content.json` 的三个有效字段：`announcement` 公告（每行一条纯文本，首页只显示前 4 行）、`projects` 项目推荐（图标下拉选择）、`navCards` 导航卡片。
- **工具页**：管理 `docs/sidebar/tools_data.json`（工具一览页数据源），按 tag 分组展示，支持多标签、新建标签。
- **文档编辑**：浏览 `docs/` 下全部 Markdown 文件，在线编辑 / 预览 / 新建，路径限制在 `docs/` 内。
- **部署**：一键部署（`python build.py` → `mkdocs build` → `git add/commit/push`）、仅构建、
  `mkdocs serve` 预览开关（0.0.0.0:8000）。任务异步执行，日志实时轮询。
  命令自动优先使用 `.venv/bin/` 下的 python/mkdocs；
  git push 失败（如 HTTPS remote 无凭据）也会在日志和返回信息中说明。
