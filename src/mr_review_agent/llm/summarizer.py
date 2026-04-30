from __future__ import annotations

from mr_review_agent.core.models import CheckResult, DiffSummary


class ReviewSummarizer:
    def summarize(self, diff: DiffSummary, checks: list[CheckResult]) -> str:
        failed_checks = [check.name for check in checks if not check.passed]
        if failed_checks:
            return f"本次 MR 存在未通过检查项：{', '.join(failed_checks)}。建议修复后再合并。"
        return "本次 MR 的基础检查均已通过，可以进入人工 review 或合并确认。"

