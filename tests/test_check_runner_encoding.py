from __future__ import annotations

from pathlib import Path
import sys

from mr_review_agent.checks.runner import CheckRunner
from mr_review_agent.core.models import CheckDefinition


def test_check_runner_decodes_utf8_command_output(tmp_path: Path):
    script = tmp_path / "emit_utf8.py"
    script.write_text(
        (
            "import sys\n"
            "sys.stdout.buffer.write("
            "'\\u68c0\\u67e5\\u5931\\u8d25 - \\u4fee\\u590d'.encode('utf-8')"
            ")\n"
        ),
        encoding="utf-8",
    )

    result = CheckRunner(tmp_path).run(
        [
            CheckDefinition(
                name="utf8-output",
                command=f'"{sys.executable}" "{script}"',
            )
        ]
    )[0]

    assert result.output == "\u68c0\u67e5\u5931\u8d25 - \u4fee\u590d"


def test_check_runner_passes_only_matching_changed_files(tmp_path: Path):
    script = tmp_path / "print_args.py"
    script.write_text(
        "import sys\nprint('\\n'.join(sys.argv[1:]))\n",
        encoding="utf-8",
    )

    result = CheckRunner(tmp_path).run(
        [
            CheckDefinition(
                name="eslint",
                command=f'"{sys.executable}" "{script}" {{files}}',
                changed_files_only=True,
                include_extensions=[".js", ".ts", ".vue"],
            )
        ],
        changed_files=["src/page.vue", "src/style.scss", "README.md"],
    )[0]

    assert result.output == "src/page.vue"


def test_check_runner_skips_changed_file_check_without_matching_files(tmp_path: Path):
    result = CheckRunner(tmp_path).run(
        [
            CheckDefinition(
                name="eslint",
                command="unused {files}",
                changed_files_only=True,
                include_extensions=[".js", ".ts", ".vue"],
            )
        ],
        changed_files=["src/style.scss", "README.md"],
    )[0]

    assert result.skipped is True
    assert result.passed is True
