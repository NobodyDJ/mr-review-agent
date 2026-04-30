# 第一阶段：本地命令行

第一阶段会构建一个本地合并请求审查命令。

该命令接收目标仓库路径、基准分支和待合并分支。它会计算待合并分支合入基准分支时引入的变化，执行配置中的质量检查，并写入 Markdown 报告。

Example:

```powershell
.\scripts\mr-review.ps1 -Repo D:\workspace\square-mp -Base dev -Head feature/demo1 -NoLlm
```

Expected output:

```text
合并请求审查报告已生成: reports/mr-review-feature-demo1.md
```
