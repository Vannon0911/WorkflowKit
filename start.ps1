param(
    [ValidateSet("textual", "plain")]
    [string]$Ui = "textual",
    [switch]$SafeUi,
    [switch]$NoAnim
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Join-Path $repoRoot "PROJECT"
$venvPython = Join-Path $projectDir ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Error "Virtual environment not found. Run .\setup.ps1 first."
    exit 1
}

$args = @("-m", "shinon_os", "--ui", $Ui)
if ($SafeUi) { $args += "--safe-ui" }
if ($NoAnim) { $args += "--no-anim" }

Push-Location $projectDir
try {
    & $venvPython @args
}
finally {
    Pop-Location
}
