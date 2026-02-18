param(
    [switch]$RunAfterSetup,
    [switch]$KeepVenv
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Join-Path $repoRoot "PROJECT"
$venvDir = Join-Path $projectDir ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"
$requirements = Join-Path $projectDir "requirements.txt"
$constraints = Join-Path $projectDir "constraints.lock.txt"

if (-not (Test-Path $projectDir)) {
    throw "PROJECT folder not found at $projectDir"
}
if (-not (Test-Path $constraints)) {
    throw "Missing lock file: $constraints"
}

function Resolve-PythonCommand {
    if (Get-Command python -ErrorAction SilentlyContinue) { return "python" }
    if (Get-Command py -ErrorAction SilentlyContinue) { return "py -3" }
    throw "Python was not found. Install Python 3.11+ and rerun setup.ps1."
}

$pythonCmd = Resolve-PythonCommand

Write-Host "== SHINON setup =="
Write-Host "Repository: $repoRoot"
Write-Host "Project:    $projectDir"

if ((Test-Path $venvDir) -and (-not $KeepVenv)) {
    Write-Host "Removing existing virtual environment for a clean setup..."
    Remove-Item -Recurse -Force $venvDir
}

if (-not (Test-Path $venvPython)) {
    Write-Host "Creating virtual environment..."
    Invoke-Expression "$pythonCmd -m venv `"$venvDir`""
} else {
    Write-Host "Reusing existing virtual environment (-KeepVenv)."
}

Write-Host "Installing dependencies..."
Push-Location $projectDir
try {
    & $venvPython -m pip install -r $requirements -c $constraints
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Setup complete."
Write-Host "Run with:"
Write-Host "  .\start.ps1"

if ($RunAfterSetup) {
    Write-Host ""
    Write-Host "Starting SHINON..."
    & (Join-Path $repoRoot "start.ps1")
}
