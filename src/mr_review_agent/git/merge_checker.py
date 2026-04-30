from __future__ import annotations

from pathlib import Path

from mr_review_agent.git.repository import Repository


class MergeChecker:
    def __init__(self, repo_path: Path) -> None:
        self.repo = Repository(repo_path)

    def can_merge_cleanly(self, base: str, head: str) -> bool:
        result = self.repo.git("merge-tree", base, head, check=False)
        return result.returncode == 0 and "<<<<<<<" not in result.stdout

