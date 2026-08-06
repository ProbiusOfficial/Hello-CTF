"""仓库同步状态与修复操作（拉取 / 推送 / 中止变基）。

面板用：git 出错时不用 SSH 上服务器，直接在面板里修。
所有操作非破坏性；不提供的操作（reset --hard 之类）请手动处理。
"""
import os
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GIT_TIMEOUT = 120


class RepoError(Exception):
    """业务错误，消息可直接展示给用户。"""


def _run(proxy, *args):
    """跑 git，返回 (rc, stdout+stderr)。不抛异常，由调用方判断。"""
    env = None
    if proxy:
        env = os.environ.copy()
        for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
            env[k] = proxy
    try:
        proc = subprocess.run(
            ["git", "-C", REPO_ROOT, *args],
            capture_output=True, text=True, timeout=GIT_TIMEOUT, env=env,
        )
    except subprocess.TimeoutExpired:
        return -1, f"git {' '.join(args)} 超时"
    out = (proc.stdout + proc.stderr).strip()
    return proc.returncode, out


def _rebase_in_progress():
    git_dir = os.path.join(REPO_ROOT, ".git")
    return (
        os.path.isdir(os.path.join(git_dir, "rebase-merge"))
        or os.path.isdir(os.path.join(git_dir, "rebase-apply"))
    )


def status(proxy=""):
    """仓库同步状态：分支、落后/领先、未提交文件数、变基是否进行中。"""
    _run(proxy, "fetch")  # 失败也继续，状态里会体现
    rc, branch = _run(proxy, "branch", "--show-current")
    rc, counts = _run(proxy, "rev-list", "--left-right", "--count", "HEAD...@{u}")
    ahead = behind = None
    if rc == 0 and counts:
        parts = counts.split()
        if len(parts) == 2:
            ahead, behind = int(parts[0]), int(parts[1])
    rc, porcelain = _run(proxy, "status", "--porcelain")
    dirty = len([l for l in porcelain.splitlines() if l.strip()]) if rc == 0 else -1
    return {
        "branch": branch if branch else "未知",
        "ahead": ahead,
        "behind": behind,
        "dirty": dirty,
        "rebase": _rebase_in_progress(),
    }


def pull(proxy=""):
    """git pull --rebase --autostash。失败抛 RepoError 并带上输出。"""
    rc, out = _run(proxy, "pull", "--rebase", "--autostash")
    if rc != 0:
        raise RepoError(out or "pull 失败")
    return out or "已是最新"


def push(proxy=""):
    rc, out = _run(proxy, "push")
    if rc != 0:
        raise RepoError(out or "push 失败")
    return out or "已推送"


def rebase_abort():
    """中止进行中的变基（冲突修复入口）。"""
    if not _rebase_in_progress():
        raise RepoError("当前没有进行中的变基")
    rc, out = _run(None, "rebase", "--abort")
    if rc != 0:
        raise RepoError(out or "rebase --abort 失败")
    return "已中止变基，仓库回到变基前状态"
