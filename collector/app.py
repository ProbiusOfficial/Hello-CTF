"""Hello-CTF 消息收集器 —— 部署在有公网 IP 的机器上。

因为面板服务器没有公网 IP，赛事提交和意见反馈先由本站收集，
管理面板再主动来拉取（拉取代推送，天然穿透 NAT）。

零依赖（纯标准库），直接 python3 app.py 即可运行。

接口：
  POST /api/submit            提交消息（公开，CORS 放开）
    body: {"type": "event"|"feedback", "title": "...", "content": ...}
    content 对 event 是赛事 JSON 对象，对 feedback 是纯文本
  GET  /api/messages          拉取全部消息（需 X-Token 头）
  POST /api/messages/delete   删除消息 {"id": N}（需 X-Token 头）

配置（环境变量）：
  COLLECTOR_TOKEN  管理端令牌，必填（面板侧填同一个值）
  COLLECTOR_PORT   监听端口，默认 9100
  COLLECTOR_FILE   消息存储文件，默认同目录 messages.json
"""
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = os.environ.get("COLLECTOR_TOKEN", "")
PORT = int(os.environ.get("COLLECTOR_PORT", 9100))
STORE = os.environ.get(
    "COLLECTOR_FILE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "messages.json"),
)

_lock = threading.Lock()


def _load():
    try:
        with open(STORE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save(messages):
    tmp = STORE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STORE)


class Handler(BaseHTTPRequestHandler):
    server_version = "HelloCTF-Collector/1.0"

    # ---------- 工具 ----------

    def _json_body(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            return json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return None

    def _send(self, code, obj, cors=False):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if cors:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def _authed(self):
        return TOKEN and self.headers.get("X-Token", "") == TOKEN

    def log_message(self, fmt, *args):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {self.address_string()} {fmt % args}")

    # ---------- 路由 ----------

    def do_OPTIONS(self):
        self._send(200, {"ok": True}, cors=True)

    def do_GET(self):
        if self.path == "/api/messages":
            if not self._authed():
                return self._send(401, {"ok": False, "error": "未授权"})
            with _lock:
                messages = _load()
            return self._send(200, {"ok": True, "messages": messages})
        if self.path == "/health":
            return self._send(200, {"ok": True})
        self._send(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        if self.path == "/api/submit":
            body = self._json_body()
            if not isinstance(body, dict):
                return self._send(400, {"ok": False, "error": "请求体应为 JSON"}, cors=True)
            mtype = body.get("type")
            title = str(body.get("title", "")).strip()
            content = body.get("content")
            if mtype not in ("event", "feedback") or not title or content in (None, ""):
                return self._send(
                    400,
                    {"ok": False, "error": "需要 type(event/feedback)、title、content"},
                    cors=True,
                )
            with _lock:
                messages = _load()
                msg = {
                    "id": (messages[-1]["id"] + 1) if messages else 1,
                    "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "type": mtype,
                    "title": title[:200],
                    "content": content,
                }
                messages.append(msg)
                _save(messages)
            return self._send(200, {"ok": True, "id": msg["id"]}, cors=True)

        if self.path == "/api/messages/delete":
            if not self._authed():
                return self._send(401, {"ok": False, "error": "未授权"})
            body = self._json_body() or {}
            with _lock:
                messages = _load()
                before = len(messages)
                messages = [m for m in messages if m.get("id") != body.get("id")]
                _save(messages)
            if len(messages) == before:
                return self._send(404, {"ok": False, "error": "消息不存在"})
            return self._send(200, {"ok": True})

        self._send(404, {"ok": False, "error": "not found"})


if __name__ == "__main__":
    if not TOKEN:
        print("警告：未设置 COLLECTOR_TOKEN，管理接口将拒绝所有请求")
    print(f"Hello-CTF 消息收集器已启动：0.0.0.0:{PORT}，存储 {STORE}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
