"""国内赛事 CN.json 的读取与写回。

数据文件就在本仓库：docs/Event/json/CN.json。
写回流程：git pull --rebase -> 改文件 -> commit -> push。
"""
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)  # 复用根目录 events_update 的时间/状态工具

import events_update

CN_PATH = os.path.join(REPO_ROOT, "docs", "Event", "json", "CN.json")

GIT_TIMEOUT = 120

DEFAULT_DETAIL = "赛制/类型: Jeopardy"


class CtftimeError(Exception):
    """业务错误，消息可直接展示给用户。"""


def read_events():
    """读取本地 CN.json，返回 (events_list, 完整数据对象)。"""
    try:
        with open(CN_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise CtftimeError(f"读取 CN.json 失败：{e}")
    result = data.get("data", {}).get("result")
    if not isinstance(result, list):
        raise CtftimeError("CN.json 结构异常：缺少 data.result 列表")
    return result, data


def _apply_mutation(data, action, name, event):
    """在完整数据对象上应用 add/update/delete，按 name 匹配。"""
    result = data["data"]["result"]
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
        data["data"]["result"] = [e for e in result if e.get("name") != name]
        if len(data["data"]["result"]) == before:
            raise CtftimeError(f"未找到赛事：{name}")
    else:
        raise CtftimeError(f"未知操作：{action}")
    data["data"]["total"] = len(data["data"]["result"])
    return data


def _normalize_event(event):
    """补默认 detail、按比赛时间写入三档 status。"""
    if not event.get("detail"):
        event["detail"] = DEFAULT_DETAIL
    event["status"] = events_update.cn_derived_status(event)
    return event


def _git(*args):
    proc = subprocess.run(
        ["git", "-C", REPO_ROOT, *args],
        capture_output=True, text=True, timeout=GIT_TIMEOUT,
    )
    if proc.returncode != 0:
        raise CtftimeError(
            f"git {' '.join(args)} 失败：{proc.stderr.strip() or proc.stdout.strip()}"
        )
    return proc.stdout.strip()


def write(action, name, event=None):
    """改本地 CN.json 并 commit + push。返回提交描述字符串。"""
    _git("pull", "--rebase")
    _, data = read_events()
    if event is not None:
        event = _normalize_event(event)
    data = _apply_mutation(data, action, name, event)
    with open(CN_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.write("\n")

    message = f"admin: {action} event {name}"
    _git("add", os.path.relpath(CN_PATH, REPO_ROOT))
    _git("commit", "-m", message)
    _git("push")
    return f"已提交并推送到本仓库：{message}"
