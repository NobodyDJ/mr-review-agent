# 第二阶段：GitHub Action

第二阶段会把本地审查流程接入 GitHub Pull Request。

当 Pull Request 指向配置的基准分支时，GitHub workflow 应该自动运行。它会检出代码、执行第一阶段同一个审查命令、把报告上传为 artifact，并在后续扩展为自动评论到 Pull Request 页面。

审查逻辑应该继续留在 Python 包中。GitHub Actions 只负责触发、编排和发布结果。
