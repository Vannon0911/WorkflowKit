param()

$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectDir ".venv\Scripts\python.exe"
$requirements = Join-Path $projectDir "requirements.txt"
$lockPath = Join-Path $projectDir "constraints.lock.txt"

if (-not (Test-Path $venvPython)) {
    Write-Error "Missing virtual environment at $venvPython. Run ..\setup.ps1 first."
    exit 1
}

Push-Location $projectDir
try {
    # Install current requirements first so freeze reflects intended dependency graph.
    & $venvPython -m pip install -r $requirements | Out-Host
    $freeze = & $venvPython -m pip freeze
}
finally {
    Pop-Location
}

$pins = $freeze |
    Where-Object { $_ -match '^[A-Za-z0-9_.-]+==[^=]+$' } |
    ForEach-Object { $_.ToLowerInvariant() } |
    Sort-Object -Unique

$content = @(
    "# Generated dependency lock for reproducible setup."
    "# Refresh intentionally via: PROJECT/scripts/refresh_lock.ps1"
    ""
) + $pins

Set-Content -Encoding UTF8 $lockPath $content
Write-Host "Updated lock file: $lockPath"
