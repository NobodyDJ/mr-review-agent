from __future__ import annotations

from pathlib import Path
import subprocess

from mr_review_agent.core.models import CheckDefinition, CheckResult


class CheckRunner:
    """执行项目检查命令并捕获输出。"""

    def __init__(self, repo_path: Path) -> None:
        self.repo_path = repo_path.resolve()

    def run(
        self,
        checks: list[CheckDefinition],
        changed_files: list[str] | None = None,
    ) -> list[CheckResult]:
        results: list[CheckResult] = []
        for check in checks:
            command = self._build_command(check, changed_files or [])
            if command is None:
                # 当本次 MR 没有匹配扩展名的文件时，增量检查不应该失败。
                results.append(
                    CheckResult(
                        name=check.name,
                        command=check.command,
                        required=check.required,
                        exit_code=0,
                        output="",
                        skipped=True,
                        skip_reason="没有匹配该检查项的变更文件。",
                    )
                )
                continue

            completed = subprocess.run(
                command,
                cwd=self.repo_path,
                text=True,
                capture_output=True,
                shell=True,
                # Node 工具可能输出 UTF-8 文本和 ANSI 控制字符。
                # 显式解码可以避免 Windows GBK 读取失败。
                encoding="utf-8",
                errors="replace",
            )
            output = "\n".join(
                part.strip()
                for part in [completed.stdout, completed.stderr]
                if part and part.strip()
            )
            results.append(
                CheckResult(
                    name=check.name,
                    command=command,
                    required=check.required,
                    exit_code=completed.returncode,
                    output=output,
                )
            )
        return results

    def _build_command(self, check: CheckDefinition, changed_files: list[str]) -> str | None:
        """构造最终执行命令，并在需要时替换 `{files}`。"""
        if not check.changed_files_only:
            return check.command

        matched_files = self._matching_changed_files(check, changed_files)
        if not matched_files:
            return None

        files_arg = subprocess.list2cmdline(matched_files)
        # `{files}` 让配置作者决定文件路径应该出现在命令的哪个位置。
        if "{files}" in check.command:
            return check.command.replace("{files}", files_arg)
        return f"{check.command} {files_arg}"

    def _matching_changed_files(
        self,
        check: CheckDefinition,
        changed_files: list[str],
    ) -> list[str]:
        """按扩展名过滤参与增量检查的变更文件。"""
        if not check.include_extensions:
            return changed_files

        allowed = {extension.lower() for extension in check.include_extensions}
        return [
            path
            for path in changed_files
            if Path(path).suffix.lower() in allowed
        ]
