"""国内赛事 CN.json / CN_archive.json 的读取与写回。

数据文件就在本仓库：docs/Event/json/。
写回流程：git pull --rebase -> 改文件 -> commit -> push。
proxy 不为空时通过 HTTP(S)_PROXY 环境变量走代理（git 会读取）。
"""
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)  # 复用根目录 events_update 的时间/状态工具

import events_update

JSON_DIR = os.path.join(REPO_ROOT, "docs", "Event", "json")
CN_PATH = os.path.join(JSON_DIR, "CN.json")
ARCHIVE_PATH = os.path.join(JSON_DIR, "CN_archive.json")

GIT_TIMEOUT = 120

DEFAULT_DETAIL = "赛制/类型: Jeopardy"


class CtftimeError(Exception):
    """业务错误，消息可直接展示给用户。"""


def _load(path, kind):
    """读取赛事 JSON，kind 为 data（在列）或 archive（存档）。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {kind: {"result": []}}
    except Exception as e:
        raise CtftimeError(f"读取 {os.path.basename(path)} 失败：{e}")
    result = data.get(kind, {}).get("result")
    if not isinstance(result, list):
        raise CtftimeError(f"{os.path.basename(path)} 结构异常：缺少 {kind}.result 列表")
    return result, data


def read_events():
    """读取在列赛事 CN.json，返回 (events_list, 完整数据对象)。"""
    return _load(CN_PATH, "data")


def read_archive():
    """读取存档赛事 CN_archive.json，返回 (events_list, 完整数据对象)。"""
    return _load(ARCHIVE_PATH, "archive")


def _dump(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.write("\n")


def _apply_mutation(data, kind, action, name, event):
    """在完整数据对象上应用 add/update/delete，按 name 匹配。"""
    result = data[kind]["result"]
    if action == "add":
        if any(e.get("name") == name for e in result):
            raise CtftimeError(f"已存在同名赛事：{name}")
        result.append(event)
    elif action == "update":
        for i, e in enumerate(result):
            if e.get("name") == name:
                result[i] = event
                break
        else:
            raise CtftimeError(f"未找到赛事：{name}")
    elif action == "delete":
        before = len(result)
        data[kind]["result"] = [e for e in result if e.get("name") != name]
        if len(data[kind]["result"]) == before:
            raise CtftimeError(f"未找到赛事：{name}")
    else:
        raise CtftimeError(f"未知操作：{action}")
    if kind == "data":
        data["data"]["total"] = len(data["data"]["result"])
    return data


def _normalize_event(event):
    """补默认 detail、按比赛时间写入状态（pending 为「时间待定」）。"""
    if not event.get("detail"):
        event["detail"] = DEFAULT_DETAIL
    if not event.get("pending"):
        event.pop("pending", None)  # 未勾选时不留字段，保持 JSON 简洁
    event["status"] = events_update.cn_derived_status(event)
    return event


def _git(proxy, *args):
    env = None
    if proxy:
        env = os.environ.copy()
        for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
            env[k] = proxy
    proc = subprocess.run(
        ["git", "-C", REPO_ROOT, *args],
        capture_output=True, text=True, timeout=GIT_TIMEOUT, env=env,
    )
    if proc.returncode != 0:
        raise CtftimeError(
            f"git {' '.join(args)} 失败：{proc.stderr.strip() or proc.stdout.strip()}"
        )
    return proc.stdout.strip()


def write(action, name, event=None, proxy=""):
    """改本地赛事 JSON 并 commit + push。返回提交描述字符串。

    action: add/update/delete（在列 CN.json）、
            archive_update/archive_delete（存档 CN_archive.json）、
            restore（从存档移回在列）。
    """
    # 先同步远程（每日构建可能改过赛事文件）；autostash 容忍工作区未提交改动
    try:
        _git(proxy, "pull", "--rebase", "--autostash")
    except CtftimeError as e:
        raise CtftimeError(
            f"同步远程仓库失败：{e}。请在服务器上手动 git pull 解决后再操作。"
        )
    changed = [os.path.relpath(CN_PATH, REPO_ROOT)]

    if action == "restore":
        _, archive = read_archive()
        target = next((e for e in archive["archive"]["result"]
                       if e.get("name") == name), None)
        if target is None:
            raise CtftimeError(f"存档中未找到赛事：{name}")
        archive["archive"]["result"] = [
            e for e in archive["archive"]["result"] if e.get("name") != name
        ]
        _, cn = read_events()
        cn = _apply_mutation(cn, "data", "add", name, _normalize_event(target))
        _dump(CN_PATH, cn)
        _dump(ARCHIVE_PATH, archive)
        changed.append(os.path.relpath(ARCHIVE_PATH, REPO_ROOT))
    elif action in ("archive_update", "archive_delete"):
        _, archive = read_archive()
        archive = _apply_mutation(
            archive, "archive",
            "update" if action == "archive_update" else "delete",
            name, event,
        )
        _dump(ARCHIVE_PATH, archive)
        changed = [os.path.relpath(ARCHIVE_PATH, REPO_ROOT)]
    elif action in ("add", "update", "delete"):
        _, cn = read_events()
        if event is not None:
            event = _normalize_event(event)
        cn = _apply_mutation(cn, "data", action, name, event)
        _dump(CN_PATH, cn)
    else:
        raise CtftimeError(f"未知操作：{action}")

    message = f"admin: {action} event {name}"
    _git(proxy, "add", *changed)
    _git(proxy, "commit", "-m", message)
    # 先提交再同步：工作区常年有未提交改动，autostash 避免 pull --rebase 被拒
    try:
        _git(proxy, "pull", "--rebase", "--autostash")
    except CtftimeError as e:
        raise CtftimeError(
            f"赛事改动已在本地提交（{message}），但同步远程失败：{e}。"
            "可能是每日构建也改了赛事文件，请在服务器上手动 git pull 解决冲突后推送。"
        )
    _git(proxy, "push")
    return f"已提交并推送到本仓库：{message}"
