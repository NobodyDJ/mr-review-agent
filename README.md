# mr-review-agent

`mr-review-agent` 是一个面向合并请求的代码审查助手。它的目标不是替代人工 reviewer，而是在 `feature/demo1 -> dev` 这类合并前，先自动完成基础检查、变更汇总和审查报告生成。

第一阶段它会作为本地 CLI 工具运行；后续再接入 GitHub Pull Request / GitLab Merge Request，让检查结果自动出现在代码托管平台里。

## 项目定位

这个项目适合用来学习 LangChain，也适合逐步做成公司内部可用的代码质量辅助工具。

核心原则：

- 合规判断优先依赖确定性工具，例如 ESLint、TypeScript、Stylelint、构建命令
- LangChain 负责总结、解释、归类风险和生成更像人工 review 的报告
- 第一版先服务本地命令行，不急着做前后端页面
- 先支持一个真实项目，再逐步抽象成可复用工具

## 第一阶段：本地 MR 审查 CLI

目标：组长或开发者在合并前手动执行一条命令，检查某个分支合并到目标分支是否安全。

示例：

```powershell
.\scripts\mr-review.ps1 -Repo D:\workspace\square-mp -Base dev -Head feature/demo1 -NoLlm
```

第一阶段会做：

1. 读取目标仓库路径
2. 计算 `dev...feature/demo1` 的变更范围
3. 罗列本次改动涉及的文件
4. 罗列本次分支包含的提交
5. 按配置运行项目已有检查
6. 生成 Markdown 审查报告
7. 给出“可以合并 / 不建议合并”的结论

第一阶段暂时不做：

- 不自动执行真正的 merge
- 不自动评论 GitHub PR
- 不用 LLM 直接判断代码是否合规
- 不把整个仓库代码塞给大模型

报告示例：

```text
合并请求审查报告

基准分支: dev
合并分支: feature/demo1
结论: 不建议合并

变更文件:
- M src/pages/user/detail.vue
- M src/api/user.ts

检查结果:
- eslint: 失败
- type-check: 通过
- stylelint: 通过
- api-consistency: 通过
```

## 第二阶段：GitHub PR 自动审查

目标：把第一阶段的本地命令接入 GitHub Actions，让 PR 创建或更新时自动运行。

流程：

1. 开发者创建 PR：`feature/demo1 -> dev`
2. GitHub Actions 自动触发
3. workflow 调用本项目的 CLI
4. CLI 生成 Markdown 报告
5. workflow 上传报告 artifact
6. 后续扩展为自动评论到 PR 页面
7. 如果检查失败，可以配置为阻止合并

第二阶段的关键点是：审查逻辑仍然放在 Python 包里，GitHub Actions 只负责触发和发布结果。

## 第三阶段：LangChain 总结增强

目标：让报告不只是机械输出命令结果，而是更接近人工 review 说明。

LangChain 可以负责：

- 总结本次 MR 主要修改了哪些模块
- 根据检查结果解释为什么不建议合并
- 将问题分为阻塞问题和建议问题
- 给出开发者下一步整改建议
- 帮助 reviewer 识别重点关注文件

LangChain 不负责：

- 代替 ESLint 判断格式规则
- 代替 TypeScript 判断类型是否正确
- 在没有证据时推测业务逻辑错误
- 自动 approve 或 reject PR

## 第四阶段：项目上下文增强

目标：根据变更文件自动补充上下文，让 review 更有业务意义。

可能的增强：

- 修改 `src/api` 时，自动读取相关 types 和调用方
- 修改 Vue 页面时，自动读取相关 store、hooks、components
- 修改 `package.json` 时，检查 lockfile 是否同步
- 修改配置文件时，提示可能影响的构建环境

## 目录结构

```text
mr-review-agent/
├─ configs/                 # 被 review 项目的配置示例
├─ docs/                    # 阶段说明和设计文档
├─ scripts/                 # PowerShell 等本地调用脚本
├─ src/mr_review_agent/
│  ├─ cli.py                # 命令行入口
│  ├─ core/                 # 审查流程编排和核心模型
│  ├─ git/                  # Git diff、提交、合并检查
│  ├─ checks/               # ESLint/type-check/stylelint 等命令执行
│  ├─ llm/                  # LangChain 总结和提示词
│  ├─ reports/              # Markdown 报告生成
│  └─ integrations/         # GitHub/GitLab 平台集成
└─ tests/                   # 单元测试
```

## 运行流程

本项目当前的运行入口是 PowerShell 脚本，它会把参数转交给 Python CLI，再由 Python 代码完成 Git diff、规则检查和报告生成。

整体流程：

```text
.\scripts\mr-review.ps1
  -> python -m mr_review_agent.cli
  -> ReviewRunner.run()
  -> 读取 configs/square-mp.example.yml
  -> DiffCollector 收集 dev...feature 分支差异
  -> CheckRunner 执行配置中的检查命令
  -> MarkdownReportBuilder 生成 Markdown 报告
  -> 写入 reports/mr-review-<branch>.md
```

一次典型运行：

```powershell
cd D:\workspace\mr-review-agent
.\scripts\mr-review.ps1 -Repo D:\workspace\square-mp -Base dev -Head feature-clock-img-suffix -NoLlm
```

参数含义：

- `-Repo`：被审查的目标项目路径，例如 `D:\workspace\square-mp`
- `-Base`：目标分支，通常是 `dev`
- `-Head`：准备合并进目标分支的功能分支或修复分支
- `-Config`：审查配置文件，默认使用 `configs/square-mp.example.yml`
- `-NoLlm`：关闭 LLM 总结，第一阶段建议先保持关闭

运行时会发生这些事：

1. PowerShell 脚本设置 `PYTHONPATH`，让本地源码可以直接被 Python 找到
2. CLI 解析 `Repo/Base/Head/Config/NoLlm` 参数
3. `ReviewRunner` 读取 YAML 配置，得到需要执行的检查项
4. `DiffCollector` 执行 `git diff dev...feature`，拿到变更统计和文件列表
5. `DiffCollector` 执行 `git log dev..feature`，拿到本次 MR 包含的提交
6. `CheckRunner` 根据配置执行检查命令
7. 对于开启 `changed_files.enabled` 的检查，只把本次变更文件传给命令
8. 没有匹配文件时，该检查会显示为 `已跳过`，不会阻塞合并
9. `MarkdownReportBuilder` 汇总变更、提交、检查结果和失败输出
10. 报告以 `utf-8-sig` 写入，减少 Windows 打开 Markdown 时中文乱码的概率

报告生成位置：

```text
reports/mr-review-<head-branch>.md
```

例如：

```text
reports/mr-review-feature-clock-img-suffix.md
```

当前的增量检查策略：

- `eslint`：只检查本次变更的 `.js/.jsx/.ts/.tsx/.vue` 文件
- `stylelint`：只检查本次变更的 `.vue/.scss/.css/.sass/.less` 文件
- `api-consistency`：仍然执行项目级检查
- `type-check`：示例配置中暂时关闭，因为 `vue-tsc` 属于项目级类型检查，不适合简单按文件裁剪

如果你想新增一个检查项，可以在配置文件里加：

```yaml
checks:
  - name: custom-check
    command: your-command {files}
    required: true
    changed_files:
      enabled: true
      include_extensions:
        - .ts
        - .vue
```

其中 `{files}` 会被替换成本次 MR 中匹配到的变更文件列表。

## 本地开发

安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

运行示例：

```powershell
.\scripts\mr-review.ps1 -Repo D:\workspace\square-mp -Base dev -Head feature/demo1 -NoLlm
```

运行测试：

```powershell
pytest
```

PowerShell 脚本说明：

- `scripts/mr-review.ps1` 保存为 UTF-8 with BOM，兼容 Windows PowerShell 5.1 读取中文注释
- 如果后续编辑该脚本后再次出现 `Unexpected token`，优先检查文件是否被编辑器改成了 UTF-8 无 BOM

## 当前状态

当前仓库处于 `v0.1` 骨架阶段，重点是把项目边界、目录结构和第一阶段 CLI 流程搭起来。下一步应该优先完成 Git 合并冲突检查、检查命令结果解析和更友好的报告输出。
