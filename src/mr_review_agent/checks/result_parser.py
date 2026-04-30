from __future__ import annotations

from dataclasses import dataclass, field
import re


ANSI_PATTERN = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
FILE_LINE_PATTERN = re.compile(r"^[A-Za-z0-9_./\\:@() -]+\.(?:js|jsx|ts|tsx|vue|css|scss|sass|less)$")
PROBLEM_LINE_PATTERN = re.compile(
    r"^\s*(?P<line>\d+):(?P<column>\d+)\s+"
    r"(?P<severity>[×✖x!]|error|warning)?\s*"
    r"(?P<message>.*?)\s{2,}"
    r"(?P<rule>[A-Za-z0-9@/_-]+(?:/[A-Za-z0-9@/_-]+)?)\s*$"
)
FIXABLE_PATTERN = re.compile(r"(?P<count>\d+)\s+errors?\s+potentially fixable", re.IGNORECASE)
TOTAL_PATTERN = re.compile(r"(?P<count>\d+)\s+problems?", re.IGNORECASE)


@dataclass(frozen=True)
class ParsedProblem:
    file_path: str
    line: int
    column: int
    message: str
    rule: str


@dataclass(frozen=True)
class LintOutputSummary:
    problems: list[ParsedProblem] = field(default_factory=list)
    by_file: dict[str, int] = field(default_factory=dict)
    by_rule: dict[str, int] = field(default_factory=dict)
    total_problems: int = 0
    fixable_count: int = 0

    @property
    def has_problems(self) -> bool:
        return self.total_problems > 0


def strip_ansi(output: str) -> str:
    """移除命令输出中的终端颜色和控制字符。"""
    return ANSI_PATTERN.sub("", output)


def parse_lint_output(output: str) -> LintOutputSummary:
    """把常见 eslint/stylelint 文本输出解析成紧凑摘要。"""
    cleaned = strip_ansi(output)
    problems: list[ParsedProblem] = []
    current_file = ""
    total_from_tool = 0
    fixable_count = 0

    for raw_line in cleaned.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue

        if FILE_LINE_PATTERN.match(stripped):
            current_file = stripped.replace("\\", "/")
            continue

        total_match = TOTAL_PATTERN.search(stripped)
        if total_match:
            total_from_tool = int(total_match.group("count"))

        fixable_match = FIXABLE_PATTERN.search(stripped)
        if fixable_match:
            fixable_count = int(fixable_match.group("count"))

        if not current_file:
            continue

        problem_match = PROBLEM_LINE_PATTERN.match(line)
        if not problem_match:
            continue

        problems.append(
            ParsedProblem(
                file_path=current_file,
                line=int(problem_match.group("line")),
                column=int(problem_match.group("column")),
                message=problem_match.group("message").strip(),
                rule=problem_match.group("rule").strip(),
            )
        )

    by_file: dict[str, int] = {}
    by_rule: dict[str, int] = {}
    for problem in problems:
        by_file[problem.file_path] = by_file.get(problem.file_path, 0) + 1
        by_rule[problem.rule] = by_rule.get(problem.rule, 0) + 1

    return LintOutputSummary(
        problems=problems,
        by_file=by_file,
        by_rule=by_rule,
        total_problems=total_from_tool or len(problems),
        fixable_count=fixable_count,
    )


def truncate_output(output: str, max_lines: int = 80) -> str:
    lines = strip_ansi(output).splitlines()
    if len(lines) <= max_lines:
        return "\n".join(lines)
    omitted = len(lines) - max_lines
    return "\n".join(lines[:max_lines] + [f"... omitted {omitted} lines"])
