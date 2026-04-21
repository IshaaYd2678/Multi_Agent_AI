param(
    [switch]$SkipTests,
    [switch]$SkipDockerBuild
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Fail {
    param([string]$Message)
    Write-Host ""
    Write-Host "ERROR: $Message" -ForegroundColor Red
    exit 1
}

Write-Step "Running pre-deployment checks"

if (-not (Test-Path ".\Dockerfile")) {
    Fail "Dockerfile not found at repo root."
}

if (-not (Test-Path ".\streamlit_app.py")) {
    Fail "streamlit_app.py not found at repo root."
}

Write-Step "Checking for unresolved merge conflict markers"
$conflicts = git grep -n -E "^(<<<<<<<|=======|>>>>>>>)" -- "*.py" "*.md" "*.toml" "*.txt" "*.yaml" "*.yml" "*.json" 2>$null
if ($LASTEXITCODE -eq 0 -and $conflicts) {
    $conflicts | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
    Fail "Unresolved merge conflict markers found."
}
Write-Host "No merge conflict markers found."

if (-not $SkipTests) {
    Write-Step "Running test suite"
    python -m pytest -q
    if ($LASTEXITCODE -ne 0) {
        Fail "Tests failed."
    }
    Write-Host "Tests passed."
} else {
    Write-Step "Skipping tests by request"
}

if (-not $SkipDockerBuild) {
    Write-Step "Checking Docker availability"
    docker --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Fail "Docker is not installed or not available in PATH."
    }

    Write-Step "Building Docker image for deployment validation"
    $tag = "multi-agent-ai:predeploy-check"
    docker build -t $tag .
    if ($LASTEXITCODE -ne 0) {
        Fail "Docker build failed."
    }
    Write-Host "Docker build succeeded."
} else {
    Write-Step "Skipping Docker build by request"
}

Write-Step "Pre-deployment checks completed successfully"
exit 0
