param(
    [Parameter(Mandatory = $true)]
    [string]$Repo,

    [string]$Base = "dev",

    [Parameter(Mandatory = $true)]
    [string]$Head,

    [string]$Config = "configs/square-mp.example.yml",

    [switch]$NoLlm
)

$ErrorActionPreference = "Stop"

# 根据脚本位置反推出项目根目录，这样用户从任意目录执行都能正常工作。
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$SourcePath = Join-Path $ProjectRoot "src"

# 项目早期不要求先安装成 Python 包。
# 设置 PYTHONPATH 后，`python -m mr_review_agent.cli` 就能直接导入 `src/` 下的源码。
if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "$SourcePath;$env:PYTHONPATH"
}
else {
    $env:PYTHONPATH = $SourcePath
}

$ConfigPath = $Config
if (-not [System.IO.Path]::IsPathRooted($ConfigPath)) {
    $ConfigPath = Join-Path $ProjectRoot $ConfigPath
}

# 这个脚本只做薄封装，真正的审查流程都放在 Python 代码里。
$ArgsList = @(
    "-m", "mr_review_agent.cli",
    "--repo", $Repo,
    "--base", $Base,
    "--head", $Head,
    "--config", $ConfigPath
)

if ($NoLlm) {
    $ArgsList += "--no-llm"
}

python @ArgsList
exit $LASTEXITCODE
