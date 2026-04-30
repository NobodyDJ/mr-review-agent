from __future__ import annotations

import argparse
from pathlib import Path

from mr_review_agent.core.review_runner import ReviewRunner


def build_parser() -> argparse.ArgumentParser:
    """定义 PowerShell 脚本和未来 CI 任务共用的命令行参数。"""
    parser = argparse.ArgumentParser(
        prog="mr-review",
        description="审查某个分支合并到基准分支时引入的变更。",
    )
    parser.add_argument("--repo", required=True, help="目标 Git 仓库路径。")
    parser.add_argument("--base", default="dev", help="基准分支，例如 dev。")
    parser.add_argument("--head", required=True, help="待合并分支，例如 feature/demo1。")
    parser.add_argument("--config", help="项目审查配置文件路径。")
    parser.add_argument("--no-llm", action="store_true", help="关闭 LLM 总结生成。")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    # 命令行入口刻意保持很薄：这里只解析用户输入，然后把完整流程交给 ReviewRunner。
    # 这样 Git、检查命令、LLM 和报告生成都能作为独立单元测试。
    runner = ReviewRunner(
        repo_path=Path(args.repo),
        base=args.base,
        head=args.head,
        config_path=Path(args.config) if args.config else None,
        use_llm=not args.no_llm,
    )
    report_path = runner.run()
    print(f"合并请求审查报告已生成: {report_path}")


if __name__ == "__main__":
    main()
