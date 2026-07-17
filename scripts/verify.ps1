$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'
$PnpmCommand = Get-Command pnpm.cmd -ErrorAction SilentlyContinue
$BundledRuntime = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies'
$BundledPnpm = Join-Path $BundledRuntime 'bin\fallback\pnpm.cmd'
$Pnpm = if ($null -ne $PnpmCommand) {
    $PnpmCommand.Source
}
elseif (Test-Path -LiteralPath $BundledPnpm) {
    $BundledPnpm
}
else {
    throw 'pnpm.cmd not found'
}
$BundledNodeDir = Join-Path $BundledRuntime 'node\bin'
if (Test-Path -LiteralPath $BundledNodeDir) {
    $env:Path = "$BundledNodeDir;$env:Path"
}

function Invoke-Checked {
    param([string]$FilePath, [string[]]$Arguments)
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $FilePath $($Arguments -join ' ')"
    }
}

if (-not (Test-Path -LiteralPath $Python)) {
    throw 'Missing .venv. Complete Task 1 before running repository verification.'
}

Push-Location $Root
try {
    Invoke-Checked $Python @('-m', 'ruff', 'check', 'backend')
    Invoke-Checked $Python @('-m', 'mypy', 'backend/src')
    Invoke-Checked $Python @('-m', 'pytest', 'backend/tests', '-q')
    Invoke-Checked $Pnpm @('--dir', 'frontend', 'lint')
    Invoke-Checked $Pnpm @('--dir', 'frontend', 'test', '--run')
    Invoke-Checked $Pnpm @('--dir', 'frontend', 'build')
}
finally {
    Pop-Location
}
