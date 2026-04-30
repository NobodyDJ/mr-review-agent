from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChangedFile:
    """来自 `git diff --name-status` 的单个变更文件。"""

    status: str
    path: str


@dataclass(frozen=True)
class DiffSummary:
    """本次合并请求的 Git 上下文。"""

    base: str
    head: str
    stat: str
    commits: list[str] = field(default_factory=list)
    files: list[ChangedFile] = field(default_factory=list)


@dataclass(frozen=True)
class CheckDefinition:
    """从 YAML 配置加载出来的质量检查定义。"""

    name: str
    command: str
    required: bool = True
    changed_files_only: bool = False
    include_extensions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CheckResult:
    """单个质量检查的执行结果，包含已执行和已跳过两种情况。"""

    name: str
    command: str
    required: bool
    exit_code: int
    output: str
    skipped: bool = False
    skip_reason: str = ""

    @property
    def passed(self) -> bool:
        return self.skipped or self.exit_code == 0


@dataclass(frozen=True)
class ReviewResult:
    """报告生成器和未来平台集成会使用的最终审查数据。"""

    diff: DiffSummary
    checks: list[CheckResult]
    llm_summary: str = ""

    @property
    def has_blockers(self) -> bool:
        return any(check.required and not check.passed for check in self.checks)

    @property
    def conclusion(self) -> str:
        return "不建议合并" if self.has_blockers else "可以合并"
