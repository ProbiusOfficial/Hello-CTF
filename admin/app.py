"""Hello-CTF 站点管理面板 — Flask 入口。

运行：python3 admin/app.py（或在仓库根 python3 -m admin.app 之外直接跑脚本即可）。
监听 0.0.0.0:9000，所有 /api/*（除登录）需要 session 登录。
"""
import functools
import json
import os
import secrets

import requests
from flask import Flask, jsonify, request, send_from_directory, session

import ctftime
import docs_api
import deployer
import repo_sync

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
HOME_CONTENT_PATH = os.path.join(DOCS_DIR, "index_content.json")
TOOLS_PATH = os.path.join(DOCS_DIR, "sidebar", "tools_data.json")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")


def load_config():
    """优先读 admin/config.json，缺失字段用环境变量兜底。"""
    cfg = {}
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    return {
        "admin_password": cfg.get("admin_password")
        or os.environ.get("ADMIN_PASSWORD", ""),
        "proxy": cfg.get("proxy", ""),
        "inbox_url": cfg.get("inbox_url", "").rstrip("/"),
        "inbox_token": cfg.get("inbox_token", ""),
        "port": int(cfg.get("port", 9000)),
    }


CONFIG = load_config()

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
app.secret_key = secrets.token_hex(32)  # 每次重启会使旧 session 失效，可接受

docs = docs_api.DocsAPI(DOCS_DIR)
deploy = deployer.Deployer(REPO_ROOT, proxy=CONFIG["proxy"])


# ---------- 认证 ----------

def login_required(view):
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("authed"):
            return jsonify({"ok": False, "error": "未登录"}), 401
        return view(*args, **kwargs)

    return wrapper


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/api/login")
def login():
    password = (request.get_json(silent=True) or {}).get("password", "")
    if not CONFIG["admin_password"]:
        return jsonify({"ok": False, "error": "服务端未设置管理密码"}), 500
    if secrets.compare_digest(password, CONFIG["admin_password"]):
        session["authed"] = True
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "密码错误"}), 401


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/me")
@login_required
def me():
    return jsonify({
        "ok": True,
        "preview_running": deploy.preview_status(),
    })


# ---------- 赛事（国内赛事 CN.json） ----------

@app.get("/api/events")
@login_required
def events_list():
    try:
        events, _ = ctftime.read_events()
        return jsonify({"ok": True, "events": events})
    except ctftime.CtftimeError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.get("/api/events/archive")
@login_required
def events_archive_list():
    try:
        events, _ = ctftime.read_archive()
        return jsonify({"ok": True, "events": events})
    except ctftime.CtftimeError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.post("/api/events/<action>")
@login_required
def events_mutate(action):
    actions = ("add", "update", "delete",
               "archive_update", "archive_delete", "restore")
    if action not in actions:
        return jsonify({"ok": False, "error": "未知操作"}), 400
    body = request.get_json(silent=True) or {}
    event = body.get("event")
    if action == "add":
        if not isinstance(event, dict) or not event.get("name"):
            return jsonify({"ok": False, "error": "缺少赛事数据或 name"}), 400
        name = event["name"]
    elif action in ("update", "archive_update"):
        name = body.get("original_name") or (event or {}).get("name")
        if not name or not isinstance(event, dict):
            return jsonify({"ok": False, "error": "缺少 original_name 或赛事数据"}), 400
    else:  # delete / archive_delete / restore
        name = body.get("name")
        if not name:
            return jsonify({"ok": False, "error": "缺少 name"}), 400

    try:
        result = ctftime.write(action, name, event, proxy=CONFIG["proxy"])
        return jsonify({"ok": True, "result": result})
    except ctftime.CtftimeError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


# ---------- 消息盒子（collector 拉取） ----------

def _inbox_request(method, path, **kwargs):
    """请求公网 collector，未配置或失败抛 RuntimeError。

    注意不走 proxy：collector 是自有国内服务器，代理是给 GitHub/CTFtime 用的。
    """
    if not CONFIG["inbox_url"]:
        raise RuntimeError("未配置 inbox_url，消息盒子不可用")
    try:
        resp = requests.request(
            method,
            CONFIG["inbox_url"] + path,
            headers={"X-Token": CONFIG["inbox_token"]},
            timeout=30,
            **kwargs,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        raise RuntimeError(f"collector 请求失败：{e}")
    if not data.get("ok"):
        raise RuntimeError(data.get("error") or "collector 返回失败")
    return data


@app.get("/api/inbox")
@login_required
def inbox_list():
    try:
        data = _inbox_request("GET", "/api/messages")
        return jsonify({"ok": True, "messages": data.get("messages", [])})
    except RuntimeError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.post("/api/inbox/delete")
@login_required
def inbox_delete():
    body = request.get_json(silent=True) or {}
    if body.get("id") is None:
        return jsonify({"ok": False, "error": "缺少 id"}), 400
    try:
        _inbox_request("POST", "/api/messages/delete", json={"id": body["id"]})
        return jsonify({"ok": True})
    except RuntimeError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


# ---------- 首页内容 ----------

@app.get("/api/home-content")
@login_required
def home_content_get():
    try:
        with open(HOME_CONTENT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return jsonify({"ok": False, "error": f"读取 index_content.json 失败：{e}"}), 500
    return jsonify({"ok": True, "content": data})


@app.post("/api/home-content")
@login_required
def home_content_save():
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or not isinstance(body.get("content"), dict):
        return jsonify({"ok": False, "error": "请求体应为 {content: {...}}"}), 400
    data = body["content"]
    list_keys = ("navCards", "projects")  # 卡片类 key，值为对象数组
    for key, value in data.items():
        if key in list_keys:
            if not isinstance(value, list) or not all(
                isinstance(c, dict) for c in value
            ):
                return jsonify({"ok": False, "error": f"{key} 必须是对象数组"}), 400
        elif not isinstance(value, str):
            return jsonify({"ok": False, "error": f"{key} 必须是字符串"}), 400
    with open(HOME_CONTENT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return jsonify({"ok": True})


# ---------- 工具页数据 ----------

def _validate_tools(items):
    """校验工具数组，返回规范化后的列表；不合法抛 ValueError。"""
    if not isinstance(items, list):
        raise ValueError("数据必须是数组")
    out = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"第 {i + 1} 项必须是对象")
        name, url = item.get("name"), item.get("url")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"第 {i + 1} 项缺少 name")
        if not isinstance(url, str) or not url.strip():
            raise ValueError(f"第 {i + 1} 项缺少 url")
        desc = item.get("desc", "")
        tags = item.get("tags", [])
        if not isinstance(desc, str):
            raise ValueError(f"第 {i + 1} 项 desc 必须是字符串")
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            raise ValueError(f"第 {i + 1} 项 tags 必须是字符串数组")
        out.append({"name": name, "desc": desc, "url": url, "tags": tags})
    return out


@app.get("/api/tools")
@login_required
def tools_get():
    try:
        with open(TOOLS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return jsonify({"ok": True, "tools": []})
    except Exception as e:
        return jsonify({"ok": False, "error": f"读取 tools_data.json 失败：{e}"}), 500
    return jsonify({"ok": True, "tools": data})


@app.post("/api/tools")
@login_required
def tools_save():
    body = request.get_json(silent=True)
    items = body if isinstance(body, list) else (body or {}).get("tools")
    try:
        data = _validate_tools(items)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    with open(TOOLS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return jsonify({"ok": True})


# ---------- 文档 ----------

@app.get("/api/docs/tree")
@login_required
def docs_tree():
    return jsonify({"ok": True, "files": docs.tree()})


@app.get("/api/docs/file")
@login_required
def docs_file():
    try:
        content = docs.read_file(request.args.get("path", ""))
        return jsonify({"ok": True, "content": content})
    except docs_api.DocsError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.post("/api/docs/save")
@login_required
def docs_save():
    body = request.get_json(silent=True) or {}
    try:
        docs.save_file(body.get("path", ""), body.get("content", ""))
        return jsonify({"ok": True})
    except docs_api.DocsError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.post("/api/docs/new")
@login_required
def docs_new():
    body = request.get_json(silent=True) or {}
    try:
        docs.new_file(body.get("path", ""), body.get("content", ""))
        return jsonify({"ok": True})
    except docs_api.DocsError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# ---------- 仓库同步（git 修复操作） ----------

@app.get("/api/repo/status")
@login_required
def repo_status():
    try:
        return jsonify({"ok": True, "status": repo_sync.status(CONFIG["proxy"])})
    except Exception as e:
        return jsonify({"ok": False, "error": f"获取仓库状态失败：{e}"}), 502


@app.post("/api/repo/<op>")
@login_required
def repo_op(op):
    try:
        if op == "pull":
            result = repo_sync.pull(CONFIG["proxy"])
        elif op == "push":
            result = repo_sync.push(CONFIG["proxy"])
        elif op == "rebase-abort":
            result = repo_sync.rebase_abort()
        else:
            return jsonify({"ok": False, "error": "未知操作"}), 400
        return jsonify({"ok": True, "result": result})
    except repo_sync.RepoError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


# ---------- 部署 ----------

@app.post("/api/deploy/<action>")
@login_required
def deploy_action(action):
    if action in ("full", "build"):
        ok, msg = deploy.start_task(action)
        return jsonify({"ok": ok, "result": msg}), (200 if ok else 409)
    if action == "preview":
        ok, msg = deploy.start_preview()
        return jsonify({"ok": ok, "result": msg})
    if action == "stop_preview":
        ok, msg = deploy.stop_preview()
        return jsonify({"ok": ok, "result": msg})
    return jsonify({"ok": False, "error": "未知操作"}), 400


@app.get("/api/deploy/logs")
@login_required
def deploy_logs():
    try:
        since = int(request.args.get("since", 0))
    except ValueError:
        since = 0
    lines, next_index = deploy.logs.since(since)
    return jsonify({"ok": True, "lines": lines, "next": next_index})


if __name__ == "__main__":
    port = CONFIG["port"]
    print(f"Hello-CTF 管理面板已启动：http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
