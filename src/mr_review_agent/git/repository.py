from __future__ import annotations

from pathlib import Path
import subprocess


class Repository:
    """围绕单个仓库路径封装 Git 命令。"""

    def __init__(self, path: Path) -> None:
        self.path = path.resolve()
        if not (self.path / ".git").exists():
            raise ValueError(f"不是 Git 仓库: {self.path}")

    def git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        # Git 可能输出中文提交信息。这里显式按 UTF-8 解码，
        # 避免 Windows 回退到 GBK 后因为 Unicode 错误丢失 stdout。
        result = subprocess.run(
            ["git", *args],
            cwd=self.path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if check and result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(f"git {' '.join(args)} 执行失败: {detail}")
        return result
