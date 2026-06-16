# setup_env.ps1
# Windows PowerShell interactive .env generator
# Usage: Right click -> Run with PowerShell, or run: powershell -ExecutionPolicy Bypass -File .\setup_env.ps1

$ErrorActionPreference = "Stop"

function Ask-WithDefault {
    param(
        [string]$Prompt,
        [string]$DefaultValue
    )
    if ([string]::IsNullOrWhiteSpace($DefaultValue)) {
        $value = Read-Host $Prompt
    } else {
        $value = Read-Host "$Prompt [$DefaultValue]"
        if ([string]::IsNullOrWhiteSpace($value)) {
            $value = $DefaultValue
        }
    }
    return $value
}

function Ask-Required {
    param([string]$Prompt)
    do {
        $value = Read-Host $Prompt
        if ([string]::IsNullOrWhiteSpace($value)) {
            Write-Host "该项不能为空，请重新输入。" -ForegroundColor Yellow
        }
    } while ([string]::IsNullOrWhiteSpace($value))
    return $value
}

Write-Host "=========================================="
Write-Host " .env 配置生成器"
Write-Host "=========================================="
Write-Host "1. 中转站 / OpenAI-compatible proxy"
Write-Host "2. GPT / Claude 官方直连"
Write-Host ""

$mode = ""
do {
    $mode = Read-Host "请选择配置方式，输入 1 或 2"
} while ($mode -ne "1" -and $mode -ne "2")

$envPath = Join-Path $PSScriptRoot ".env"

if (Test-Path $envPath) {
    $overwrite = Read-Host ".env 已存在，是否覆盖？输入 y 覆盖，其他任意键取消"
    if ($overwrite.ToLower() -ne "y") {
        Write-Host "已取消。"
        exit 0
    }
}

if ($mode -eq "1") {
    Write-Host ""
    Write-Host "你选择了：中转站配置"

    $proxyBase = Ask-WithDefault "请输入你的中转站 OpenAI API Base" "https://4router.net/v1"
    $proxyAnthropicBase = Ask-WithDefault "请输入你的中转站 Anthropic Base URL" "https://4router.net"
    $proxyKey = Ask-Required "请输入你的中转站 API Key"

    $modelAnalysis = Ask-WithDefault "请输入分析 Agent 使用的模型 MODEL_ANALYSIS" "gpt-5.5"
    $modelCoderApi = Ask-WithDefault "请输入代码 Agent API 模式使用的模型 MODEL_CODER_API" "gpt-5.4-mini"
    $modelManagerSummary = Ask-WithDefault "请输入管理/总结 Agent 使用的模型 MODEL_MANAGER_SUMMARY" "gpt-5.4-mini"
    $modelDataProcess = Ask-WithDefault "请输入数据处理 Agent 使用的模型 MODEL_DATA_PROCESS" "claude-opus-4-6"
    $coderExecutionMode = Ask-WithDefault "请输入代码 Agent 执行模式 CODER_EXECUTION_MODE，可选 API / CLI_CODEX / CLI_CLAUDE" "API"

    $content = @"
# ==========================================
# 4Router / 中转站 API 配置
# 由 setup_env.ps1 自动生成
# ==========================================

# --- OpenAI 兼容模型 (GPT & Codex) ---
OPENAI_API_KEY=$proxyKey
OPENAI_API_BASE=$proxyBase
MODEL_ANALYSIS=$modelAnalysis
MODEL_CODER_API=$modelCoderApi
MODEL_MANAGER_SUMMARY=$modelManagerSummary
CODER_EXECUTION_MODE=$coderExecutionMode

# --- Anthropic 模型 (Claude) ---
ANTHROPIC_API_KEY=$proxyKey
ANTHROPIC_BASE_URL=$proxyAnthropicBase
MODEL_DATA_PROCESS=$modelDataProcess
"@
} else {
    Write-Host ""
    Write-Host "你选择了：GPT / Claude 官方直连配置"

    $openaiKey = Ask-Required "请输入你的 OpenAI API Key"
    $openaiBase = Ask-WithDefault "请输入 OpenAI API Base，官方直连可直接回车留空" ""
    $anthropicKey = Ask-Required "请输入你的 Anthropic API Key"
    $anthropicBase = Ask-WithDefault "请输入 Anthropic Base URL，官方直连可直接回车留空" ""

    $modelAnalysis = Ask-WithDefault "请输入分析 Agent 使用的模型 MODEL_ANALYSIS" "gpt-5.5"
    $modelCoderApi = Ask-WithDefault "请输入代码 Agent API 模式使用的模型 MODEL_CODER_API" "gpt-5.4-mini"
    $modelManagerSummary = Ask-WithDefault "请输入管理/总结 Agent 使用的模型 MODEL_MANAGER_SUMMARY" "gpt-5.4-mini"
    $modelDataProcess = Ask-WithDefault "请输入数据处理 Agent 使用的模型 MODEL_DATA_PROCESS" "claude-opus-4-6"
    $coderExecutionMode = Ask-WithDefault "请输入代码 Agent 执行模式 CODER_EXECUTION_MODE，可选 API / CLI_CODEX / CLI_CLAUDE" "API"

    $content = @"
# ==========================================
# 官方直连 API 配置
# 由 setup_env.ps1 自动生成
# ==========================================
OPENAI_API_KEY=$openaiKey
OPENAI_API_BASE=$openaiBase
MODEL_ANALYSIS=$modelAnalysis
MODEL_CODER_API=$modelCoderApi
MODEL_MANAGER_SUMMARY=$modelManagerSummary
CODER_EXECUTION_MODE=$coderExecutionMode

ANTHROPIC_API_KEY=$anthropicKey
ANTHROPIC_BASE_URL=$anthropicBase
MODEL_DATA_PROCESS=$modelDataProcess
"@
}

Set-Content -Path $envPath -Value $content -Encoding UTF8

Write-Host ""
Write-Host "已生成 .env 文件：$envPath" -ForegroundColor Green
Write-Host "请确认 .env 不要上传到 GitHub。"
