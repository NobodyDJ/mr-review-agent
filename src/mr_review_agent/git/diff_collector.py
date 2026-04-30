from __future__ import annotations

from pathlib import Path

from mr_review_agent.core.models import ChangedFile, DiffSummary
from mr_review_agent.git.repository import Repository


class DiffCollector:
    """收集 reviewer 阅读代码前需要的 Git 上下文。"""

    def __init__(self, repo_path: Path) -> None:
        self.repo = Repository(repo_path)

    def collect(self, base: str, head: str) -> DiffSummary:
        # `base...head` 表示 head 相对共同祖先引入了什么变化。
        # 这和 PR/MR 页面展示 diff 的方式更接近。
        range_expr = f"{base}...{head}"
        stat = self.repo.git("diff", "--stat", range_expr).stdout.strip()
        name_status = self.repo.git("diff", "--name-status", range_expr).stdout
        # 提交列表使用 `base..head`：只看 head 有而 base 没有的提交。
        commits = self.repo.git("log", "--oneline", f"{base}..{head}", check=False).stdout
        return DiffSummary(
            base=base,
            head=head,
            stat=stat,
            commits=[line for line in commits.splitlines() if line.strip()],
            files=self._parse_changed_files(name_status),
        )

    def _parse_changed_files(self, name_status: str) -> list[ChangedFile]:
        """把 `M<TAB>src/app.vue` 这类行解析成 ChangedFile 对象。"""
        files: list[ChangedFile] = []
        for line in name_status.splitlines():
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            files.append(ChangedFile(status=parts[0], path=parts[-1]))
        return files
