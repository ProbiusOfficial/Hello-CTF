"""部署相关：build.py / mkdocs build / git push / mkdocs serve 预览。

所有任务异步跑在线程里，输出进内存日志 buffer，前端轮询增量。
"""
import os
import shutil
import subprocess
import threading

BUILD_TIMEOUT = 600  # build 类命令超时
GIT_TIMEOUT = 300


class LogBuffer:
    """线程安全的行日志，支持 since=N 增量读取。"""

    def __init__(self):
        self._lines = []
        self._lock = threading.Lock()

    def append(self, text):
        with self._lock:
            for line in text.splitlines() or [""]:
                self._lines.append(line)

    def since(self, n):
        with self._lock:
            n = max(0, min(n, len(self._lines)))
            return self._lines[n:], len(self._lines)


class Deployer:
    def __init__(self, repo_root):
        self.repo_root = repo_root
        # 优先使用项目 .venv 里的 python / mkdocs（系统 Python 受 PEP 668 限制）
        self.python = "python3"
        self.mkdocs = "mkdocs"
        self._resolve_tools()
        self.logs = LogBuffer()

    def _resolve_tools(self):
        """每次执行前惰性探测 .venv，避免面板启动后新装依赖还要重启。"""
        venv_bin = os.path.join(self.repo_root, ".venv", "bin")
        venv_python = os.path.join(venv_bin, "python")
        venv_mkdocs = os.path.join(venv_bin, "mkdocs")
        self.python = venv_python if os.path.exists(venv_python) else "python3"
        self.mkdocs = venv_mkdocs if os.path.exists(venv_mkdocs) else "mkdocs"
        self._task_running = False
        self._task_lock = threading.Lock()
        self._preview_proc = None
        self._preview_lock = threading.Lock()

    # ---------- 内部工具 ----------

    def _log(self, text):
        self.logs.append(text)

    def _run(self, cmd, timeout):
        """同步跑一条命令，输出实时进日志。返回是否成功。"""
        self._log(f"$ {' '.join(cmd)}")
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=self.repo_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        except FileNotFoundError:
            self._log(f"命令不存在：{cmd[0]}")
            return False
        try:
            out, _ = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            self._log(f"命令超时（{timeout}s），已终止")
            return False
        if out:
            self._log(out.rstrip("\n"))
        if proc.returncode != 0:
            self._log(f"命令退出码 {proc.returncode}")
            return False
        return True

    def _mkdocs_available(self):
        self._resolve_tools()
        if shutil.which(self.mkdocs):
            return True
        self._log(
            "未找到 mkdocs 命令，请先安装依赖："
            ".venv/bin/pip install -r requirements.txt"
        )
        return False

    # ---------- 构建 / 部署 ----------

    def _do_build(self):
        self._resolve_tools()
        if not self._run([self.python, "build.py"], BUILD_TIMEOUT):
            self._log("build.py 执行失败，中止")
            return False
        if not self._mkdocs_available():
            return False
        if not self._run([self.mkdocs, "build"], BUILD_TIMEOUT):
            self._log("mkdocs build 失败，中止")
            return False
        return True

    def _do_deploy(self):
        if not self._do_build():
            return
        if not self._run(["git", "add", "-A"], GIT_TIMEOUT):
            return
        # 没有变更时 commit 会失败，这里先检查
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.repo_root, capture_output=True, text=True, timeout=60,
        )
        if not status.stdout.strip():
            self._log("没有需要提交的变更，跳过 commit/push")
            return
        if not self._run(
            ["git", "commit", "-m", "admin: deploy site"], GIT_TIMEOUT
        ):
            self._log("git commit 失败，中止")
            return
        if not self._run(["git", "push"], GIT_TIMEOUT):
            self._log(
                "git push 失败：请确认本机已配置推送凭据"
                "（remote 为 HTTPS，需凭据管理器或改用 SSH）"
            )
            return
        self._log("部署完成")

    def start_task(self, kind):
        """kind: 'full' | 'build'。返回 (ok, message)。"""
        with self._task_lock:
            if self._task_running:
                return False, "已有部署/构建任务在运行中"
            self._task_running = True

        def runner():
            try:
                self._log(f"===== 开始任务：{kind} =====")
                if kind == "build":
                    if self._do_build():
                        self._log("构建完成")
                else:
                    self._do_deploy()
            except Exception as e:
                self._log(f"任务异常：{e}")
            finally:
                self._log(f"===== 任务结束：{kind} =====")
                with self._task_lock:
                    self._task_running = False

        threading.Thread(target=runner, daemon=True).start()
        return True, "任务已启动"

    # ---------- 预览 ----------

    def preview_status(self):
        with self._preview_lock:
            running = self._preview_proc is not None and self._preview_proc.poll() is None
        return running

    def start_preview(self):
        with self._preview_lock:
            if self._preview_proc is not None and self._preview_proc.poll() is None:
                return True, "预览已在运行：http://<本机IP>:8000"
            if not self._mkdocs_available():
                return False, "未安装 mkdocs，无法启动预览：.venv/bin/pip install -r requirements.txt"
            try:
                self._preview_proc = subprocess.Popen(
                    [self.mkdocs, "serve", "-a", "0.0.0.0:8000"],
                    cwd=self.repo_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
            except Exception as e:
                return False, f"启动预览失败：{e}"

            def pump():
                proc = self._preview_proc
                for line in proc.stdout:
                    self._log("[preview] " + line.rstrip("\n"))
                proc.wait()
                self._log(f"[preview] 进程退出，码 {proc.returncode}")

            threading.Thread(target=pump, daemon=True).start()
            self._log("预览服务已启动：http://0.0.0.0:8000")
            return True, "预览已启动：http://<本机IP>:8000"

    def stop_preview(self):
        with self._preview_lock:
            proc = self._preview_proc
            if proc is None or proc.poll() is not None:
                return False, "预览未在运行"
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            self._preview_proc = None
            self._log("预览服务已停止")
            return True, "预览已停止"
