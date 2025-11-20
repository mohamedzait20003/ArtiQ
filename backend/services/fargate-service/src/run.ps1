#!/usr/bin/env pwsh

$ErrorActionPreference = "Stop"

# Resolve repo root and make your package importable
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = "$ROOT\src" + $(if ($env:PYTHONPATH) { ";$env:PYTHONPATH" } else { "" })

# Environment variables
$env:LOG_FILE = "$ROOT\logs\phase1.log"
# LOG_LEVEL defaults to 2 if not set
if (-not $env:LOG_LEVEL) { $env:LOG_LEVEL = "2" }
# GITHUB_TOKEN and GEN_AI_STUDIO_API_KEY should be provided by the environment (AWS Secrets Manager in Fargate)

$cmd = if ($args.Count -gt 0) { $args[0] } else { "" }

if ([string]::IsNullOrEmpty($cmd)) {
    Write-Host "Usage: .\run.ps1 install|test|<path_to_URL>"
    exit 1
}
elseif ($cmd -eq "install") {
    python -m pip install --user -r "$ROOT\requirements.txt"
    exit 0
}
elseif ($cmd -eq "test") {
    Set-Location $ROOT
    python "$ROOT\src\ece461\test_summary.py"
    exit 0
}
else {
    python -m ece461.main $cmd
    exit 0
}
cat $env:LOG_FILE
