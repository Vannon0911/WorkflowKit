param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("start", "add", "finish")]
    [string]$Action,

    [string]$SessionId,
    [ValidateSet("user", "assistant", "system", "idea", "change")]
    [string]$Role = "user",
    [string]$Text = "",
    [ValidateSet("ok", "error")]
    [string]$Status = "ok"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-TranscriptDir {
    $base = if ($env:LOCALAPPDATA) { $env:LOCALAPPDATA } else { Join-Path $HOME "AppData\\Local" }
    $dir = Join-Path $base "copilot_docs\\transcripts"
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    return $dir
}

function Find-SessionJsonPath {
    param([Parameter(Mandatory = $true)][string]$Id)
    $dir = Get-TranscriptDir
    $hit = Get-ChildItem -Path $dir -Filter "session_*_$Id.json" -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $hit) {
        throw "Session nicht gefunden: $Id"
    }
    return $hit.FullName
}

function Save-TranscriptFiles {
    param(
        [Parameter(Mandatory = $true)][string]$JsonPath,
        [Parameter(Mandatory = $true)]$Doc
    )

    $txtPath = [System.IO.Path]::ChangeExtension($JsonPath, ".txt")
    ($Doc | ConvertTo-Json -Depth 12) | Set-Content -Path $JsonPath -Encoding UTF8

    $lines = @(
        "session_id: $($Doc.session_id)",
        "started_at: $($Doc.started_at)",
        "finished_at: $($Doc.finished_at)",
        "status: $($Doc.status)",
        "error: $($Doc.error)",
        "",
        "entries:"
    )
    foreach ($e in $Doc.entries) {
        $lines += "[{0}] {1}: {2}" -f $e.ts, $e.role, $e.text
        if ($e.meta) {
            $lines += "  meta: $($e.meta | ConvertTo-Json -Compress)"
        }
    }
    $lines | Set-Content -Path $txtPath -Encoding UTF8
    return @{ json = $JsonPath; txt = $txtPath }
}

if ($Action -eq "start") {
    $dir = Get-TranscriptDir
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $sid = if ($SessionId) { $SessionId } else { ([guid]::NewGuid().ToString("N")).Substring(0, 8) }
    $id = "session_${stamp}_$sid"
    $jsonPath = Join-Path $dir "$id.json"
    $now = (Get-Date).ToString("o")
    $doc = @{
        session_id = $id
        started_at = $now
        finished_at = ""
        status = "running"
        error = ""
        source = "chatgpt_copilot"
        entries = @()
    }
    if ($Text) {
        $doc.entries += @{
            ts = $now
            role = "system"
            text = $Text
            meta = @{ event = "session_started" }
        }
    }
    $saved = Save-TranscriptFiles -JsonPath $jsonPath -Doc $doc
    Write-Output "SESSION_ID=$sid"
    Write-Output "JSON=$($saved.json)"
    Write-Output "TXT=$($saved.txt)"
    exit 0
}

if (-not $SessionId) {
    throw "SessionId ist erforderlich fuer Action '$Action'."
}

$targetJson = Find-SessionJsonPath -Id $SessionId
$raw = Get-Content -Path $targetJson -Raw -Encoding UTF8
$doc = ConvertFrom-Json -InputObject $raw

if ($Action -eq "add") {
    if (-not $Text) {
        throw "Text ist fuer 'add' erforderlich."
    }
    $doc.entries = @($doc.entries) + @(
        [pscustomobject]@{
        ts = (Get-Date).ToString("o")
        role = $Role
        text = $Text
        meta = [pscustomobject]@{}
    })
    $saved = Save-TranscriptFiles -JsonPath $targetJson -Doc $doc
    Write-Output "JSON=$($saved.json)"
    Write-Output "TXT=$($saved.txt)"
    exit 0
}

if ($Action -eq "finish") {
    $doc.status = $Status
    $doc.finished_at = (Get-Date).ToString("o")
    if ($Status -eq "error" -and $Text) {
        $doc.error = $Text
    }
    $saved = Save-TranscriptFiles -JsonPath $targetJson -Doc $doc
    Write-Output "JSON=$($saved.json)"
    Write-Output "TXT=$($saved.txt)"
    exit 0
}
