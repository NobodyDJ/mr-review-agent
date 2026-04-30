from __future__ import annotations

from pathlib import Path
import re

import yaml

from mr_review_agent.checks.runner import CheckRunner
from mr_review_agent.core.models import CheckDefinition, ReviewResult
from mr_review_agent.git.diff_collector import DiffCollector
from mr_review_agent.llm.summarizer import ReviewSummarizer
from mr_review_agent.reports.markdown_report import MarkdownReportBuilder


class ReviewRunner:
    """编排完整的本地合并请求审查流程。"""

    def __init__(
        self,
        repo_path: Path,
        base: str,
        head: str,
        config_path: Path | None,
        use_llm: bool,
    ) -> None:
        self.repo_path = repo_path
        self.base = base
        self.head = head
        self.config_path = config_path
        self.use_llm = use_llm

    def run(self) -> Path:
        # 流程顺序：
        # 1. 加载项目配置。
        # 2. 收集合并差异。
        # 3. 执行配置中的检查命令。
        # 4. 按需生成 LLM 总结。
        # 5. 渲染并写入 Markdown 报告。
        config = self._load_config()
        checks = self._load_checks(config)

        diff = DiffCollector(self.repo_path).collect(self.base, self.head)
        # 删除的文件不能传给 eslint/stylelint 这类工具。
        # 因此增量检查只接收分支中仍然存在的文件。
        changed_files = [
            item.path
            for item in diff.files
            if not item.status.upper().startswith("D")
        ]
        check_results = CheckRunner(self.repo_path).run(checks, changed_files=changed_files)

        llm_summary = ""
        if self.use_llm and config.get("llm", {}).get("enabled", False):
            llm_summary = ReviewSummarizer().summarize(diff=diff, checks=check_results)

        review = ReviewResult(diff=diff, checks=check_results, llm_summary=llm_summary)
        report = MarkdownReportBuilder().render(review)

        output_dir = Path(config.get("report", {}).get("output_dir", "reports"))
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"mr-review-{self._safe_branch_name(self.head)}.md"
        # utf-8-sig 会写入 BOM，帮助 Windows 编辑器把中文 Markdown
        # 识别为 UTF-8，而不是误判成 GBK。
        report_path.write_text(report, encoding="utf-8-sig")
        return report_path

    def _load_config(self) -> dict:
        """加载 YAML 配置；没有配置时允许做一次无检查的试运行。"""
        if not self.config_path:
            return {}
        with self.config_path.open("r", encoding="utf-8") as file:
            loaded = yaml.safe_load(file) or {}
        if not isinstance(loaded, dict):
            raise ValueError("配置文件必须是 YAML 对象。")
        return loaded

    def _load_checks(self, config: dict) -> list[CheckDefinition]:
        """把 YAML 中的检查项转换成带类型的 CheckDefinition 对象。"""
        checks: list[CheckDefinition] = []
        for item in config.get("checks", []):
            if item.get("enabled", True) is False:
                continue
            changed_files = item.get("changed_files", {}) or {}
            checks.append(
                CheckDefinition(
                    name=item["name"],
                    command=item["command"],
                    required=bool(item.get("required", True)),
                    changed_files_only=bool(changed_files.get("enabled", False)),
                    include_extensions=list(changed_files.get("include_extensions", [])),
                )
            )
        return checks

    def _safe_branch_name(self, branch: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_.-]+", "-", branch).strip("-")
