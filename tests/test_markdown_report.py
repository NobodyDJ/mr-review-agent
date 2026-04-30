from mr_review_agent.core.models import CheckResult, DiffSummary, ReviewResult
from mr_review_agent.reports.markdown_report import MarkdownReportBuilder


def test_markdown_report_marks_failed_required_check_as_blocker():
    review = ReviewResult(
        diff=DiffSummary(base="dev", head="feature/demo1", stat="1 file changed"),
        checks=[
            CheckResult(
                name="eslint",
                command="pnpm lint",
                required=True,
                exit_code=1,
                output="no-console",
            )
        ],
    )

    report = MarkdownReportBuilder().render(review)

    assert "# 合并请求审查报告" in report
    assert "- 基准分支: `dev`" in report
    assert "- 合并分支: `feature/demo1`" in report
    assert "- 结论: **\u4e0d\u5efa\u8bae\u5408\u5e76**" in report
    assert "## 检查结果" in report
    assert "| eslint | 是 | 失败 | `pnpm lint` |" in report
    assert "\u4e0d\u5efa\u8bae\u5408\u5e76" in report
    assert "eslint" in report
    assert "no-console" in report


def test_markdown_report_adds_failure_summary_and_cleans_ansi_output():
    output = """
\x1b[31mInvalid Option:\x1b[39m Invalid option name "ignoreUnits"

src/components/DataList/index.vue
  \x1b[2m266:5\x1b[22m  \x1b[31m✖\x1b[39m  Expected "margin-top" to come before "margin-bottom"  \x1b[2morder/properties-order\x1b[22m
  \x1b[2m278:9\x1b[22m  \x1b[31m✖\x1b[39m  Unexpected empty line before declaration              \x1b[2mdeclaration-empty-line-before\x1b[22m
"""
    review = ReviewResult(
        diff=DiffSummary(base="dev", head="feature/demo1", stat="1 file changed"),
        checks=[
            CheckResult(
                name="stylelint",
                command="pnpm exec stylelint src/components/DataList/index.vue",
                required=True,
                exit_code=1,
                output=output,
            )
        ],
    )

    report = MarkdownReportBuilder().render(review)

    assert "## 失败摘要" in report
    assert "`stylelint` 解析到 2 个问题。" in report
    assert "`src/components/DataList/index.vue` - 2 个问题" in report
    assert "`order/properties-order` - 1 个问题" in report
    assert "\x1b[" not in report
