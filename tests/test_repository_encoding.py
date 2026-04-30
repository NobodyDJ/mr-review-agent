from __future__ import annotations

from pathlib import Path
import subprocess

from mr_review_agent.git.repository import Repository


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def test_git_output_decodes_utf8_commit_messages(tmp_path: Path):
    run_git(tmp_path, "init")
    run_git(tmp_path, "config", "user.email", "review@example.com")
    run_git(tmp_path, "config", "user.name", "Review Bot")

    readme = tmp_path / "README.md"
    readme.write_text("hello\n", encoding="utf-8")
    run_git(tmp_path, "add", "README.md")
    run_git(tmp_path, "commit", "-m", "修复: 优化代码")

    result = Repository(tmp_path).git("log", "--oneline")

    assert "修复: 优化代码" in result.stdout
