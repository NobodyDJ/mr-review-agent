from __future__ import annotations


class GitHubIntegration:
    """第二阶段 GitHub PR 评论和状态检查的预留集成点。"""

    def publish_report(self, report_markdown: str) -> None:
        raise NotImplementedError("GitHub 集成将在第二阶段实现。")
