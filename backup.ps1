param()

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backupDir = Join-Path $repoRoot "BACKUPS"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

function Normalize-RelativePath {
    param([string]$Root, [string]$Path)
    $rootNorm = ([System.IO.Path]::GetFullPath($Root)).TrimEnd('\')
    $pathNorm = [System.IO.Path]::GetFullPath($Path)
    $rel = $pathNorm.Substring($rootNorm.Length).TrimStart('\')
    return $rel -replace '\\', '/'
}

function Should-Exclude {
    param([string]$RelativePath)
    if ([string]::IsNullOrWhiteSpace($RelativePath)) { return $true }

    $rel = $RelativePath
    if ($rel.StartsWith(".git/")) { return $true }
    if ($rel.StartsWith(".venv/")) { return $true }
    if ($rel.StartsWith("PROJECT/.venv/")) { return $true }
    if ($rel.StartsWith("BACKUPS/")) { return $true }
    if ($rel.StartsWith(".vscode/")) { return $true }
    if ($rel -match '(^|/)__pycache__(/|$)') { return $true }
    if ($rel -match '(^|/)\.pytest_cache(/|$)') { return $true }
    if ($rel.EndsWith(".pyc")) { return $true }
    return $false
}

function Next-BackupPath {
    param([string]$Dir)
    $idx = 1
    while ($true) {
        $candidate = Join-Path $Dir ("Shinon mvp v_{0}.zip" -f $idx)
        if (-not (Test-Path $candidate)) {
            return $candidate
        }
        $idx += 1
    }
}

$staging = Join-Path ([System.IO.Path]::GetTempPath()) ("shinon_backup_stage_" + [guid]::NewGuid().ToString("N"))
$zipPath = Next-BackupPath -Dir $backupDir

New-Item -ItemType Directory -Path $staging | Out-Null

try {
    $allFiles = Get-ChildItem -Path $repoRoot -Recurse -File -Force
    foreach ($file in $allFiles) {
        $relative = Normalize-RelativePath -Root $repoRoot -Path $file.FullName
        if (Should-Exclude -RelativePath $relative) {
            continue
        }

        $dest = Join-Path $staging ($relative -replace '/', '\')
        $destDir = Split-Path -Parent $dest
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        Copy-Item -Path $file.FullName -Destination $dest -Force
    }

    Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $zipPath -Force
    Set-Content -Path (Join-Path $backupDir "latest_backup.txt") -Encoding UTF8 -Value $zipPath

    Write-Host "Backup created: $zipPath"
}
finally {
    if (Test-Path $staging) {
        Remove-Item -Path $staging -Recurse -Force
    }
}
