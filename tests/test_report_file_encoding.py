from __future__ import annotations

from pathlib import Path
import subprocess

from mr_review_agent.core.review_runner import ReviewRunner


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def test_review_runner_writes_report_with_utf8_bom(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    run_git(repo, "init")
    run_git(repo, "config", "user.email", "review@example.com")
    run_git(repo, "config", "user.name", "Review Bot")
    run_git(repo, "checkout", "-b", "dev")

    readme = repo / "README.md"
    readme.write_text("hello\n", encoding="utf-8")
    run_git(repo, "add", "README.md")
    run_git(repo, "commit", "-m", "init")

    run_git(repo, "checkout", "-b", "feature/demo1")
    readme.write_text("hello\nchange\n", encoding="utf-8")
    run_git(repo, "add", "README.md")
    run_git(repo, "commit", "-m", "change")

    output_dir = tmp_path / "reports"
    config = tmp_path / "config.yml"
    config.write_text(
        f"report:\n  output_dir: {output_dir.as_posix()}\n",
        encoding="utf-8",
    )

    report_path = ReviewRunner(
        repo_path=repo,
        base="dev",
        head="feature/demo1",
        config_path=config,
        use_llm=False,
    ).run()

    assert report_path.read_bytes().startswith(b"\xef\xbb\xbf")
    assert "\u53ef\u4ee5\u5408\u5e76" in report_path.read_text(encoding="utf-8-sig")
