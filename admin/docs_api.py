"""docs/ 目录下 Markdown 文件的浏览与编辑，所有路径限制在 docs/ 内。"""
import os


class DocsError(Exception):
    """业务错误，消息可直接展示给用户。"""


class DocsAPI:
    def __init__(self, docs_dir):
        self.docs_dir = os.path.realpath(docs_dir)

    def _safe_path(self, rel_path):
        """把用户给的相对路径解析成 docs/ 内的绝对路径，防目录穿越。"""
        if not rel_path or os.path.isabs(rel_path):
            raise DocsError("非法路径")
        full = os.path.realpath(os.path.join(self.docs_dir, rel_path))
        if os.path.commonpath([self.docs_dir, full]) != self.docs_dir:
            raise DocsError("路径越界：必须位于 docs/ 内")
        if not full.endswith(".md"):
            raise DocsError("仅支持 .md 文件")
        return full

    def tree(self):
        """返回 docs/ 下所有 .md 文件的相对路径列表（按目录、文件名排序）。"""
        files = []
        for root, dirs, names in os.walk(self.docs_dir):
            dirs.sort()
            for name in sorted(names):
                if name.endswith(".md"):
                    full = os.path.join(root, name)
                    files.append(os.path.relpath(full, self.docs_dir))
        return files

    def read_file(self, rel_path):
        full = self._safe_path(rel_path)
        if not os.path.isfile(full):
            raise DocsError(f"文件不存在：{rel_path}")
        with open(full, "r", encoding="utf-8") as f:
            return f.read()

    def save_file(self, rel_path, content):
        full = self._safe_path(rel_path)
        if not os.path.isfile(full):
            raise DocsError(f"文件不存在：{rel_path}（请用新建接口）")
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)

    def new_file(self, rel_path, content=""):
        full = self._safe_path(rel_path)
        if os.path.exists(full):
            raise DocsError(f"文件已存在：{rel_path}")
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
