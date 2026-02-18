param(
    [ValidateSet("major", "minor", "patch")]
    [string]$Bump = "patch",
    [string]$SetVersion
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyprojectPath = Join-Path $repoRoot "PROJECT\pyproject.toml"
$initPath = Join-Path $repoRoot "PROJECT\src\shinon_os\__init__.py"

if (-not (Test-Path $pyprojectPath)) {
    throw "Missing file: $pyprojectPath"
}
if (-not (Test-Path $initPath)) {
    throw "Missing file: $initPath"
}

function Write-Utf8NoBom {
    param(
        [string]$Path,
        [string]$Content
    )
    $enc = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $enc)
}

function Assert-SemVer {
    param([string]$Value, [string]$Name)
    if ($Value -notmatch '^\d+\.\d+\.\d+$') {
        throw "$Name must match semantic version X.Y.Z. Got: $Value"
    }
}

function Parse-Version {
    param([string]$Value)
    $parts = $Value.Split(".")
    return [int[]]@([int]$parts[0], [int]$parts[1], [int]$parts[2])
}

Push-Location $repoRoot
try {
    $dirty = git status --porcelain
    if ($LASTEXITCODE -ne 0) {
        throw "git status failed."
    }
    if ($dirty) {
        throw "Working tree is not clean. Commit or stash changes before version bump."
    }

    $pyproject = Get-Content -Raw $pyprojectPath
    $initFile = Get-Content -Raw $initPath

    $pyMatch = [regex]::Match($pyproject, '(?m)^version\s*=\s*"([^"]+)"\s*$')
    if (-not $pyMatch.Success) {
        throw "Could not parse project version from PROJECT/pyproject.toml."
    }
    $initMatch = [regex]::Match($initFile, '(?m)^__version__\s*=\s*"([^"]+)"\s*$')
    if (-not $initMatch.Success) {
        throw "Could not parse __version__ from PROJECT/src/shinon_os/__init__.py."
    }

    $currentPy = $pyMatch.Groups[1].Value
    $currentInit = $initMatch.Groups[1].Value

    Assert-SemVer -Value $currentPy -Name "pyproject version"
    Assert-SemVer -Value $currentInit -Name "__init__ version"
    if ($currentPy -ne $currentInit) {
        throw "Version mismatch: pyproject=$currentPy, __init__=$currentInit"
    }

    $target = $null
    if ($SetVersion) {
        Assert-SemVer -Value $SetVersion -Name "SetVersion"
        $target = $SetVersion
    }
    else {
        $parts = Parse-Version -Value $currentPy
        if ($Bump -eq "major") {
            $parts[0] += 1
            $parts[1] = 0
            $parts[2] = 0
        }
        elseif ($Bump -eq "minor") {
            $parts[1] += 1
            $parts[2] = 0
        }
        else {
            $parts[2] += 1
        }
        $target = "$($parts[0]).$($parts[1]).$($parts[2])"
    }

    if ($target -eq $currentPy) {
        throw "Target version equals current version ($target)."
    }

    $tagName = "v$target"
    git rev-parse -q --verify "refs/tags/$tagName" *> $null
    if ($LASTEXITCODE -eq 0) {
        throw "Tag already exists: $tagName"
    }

    $updatedPy = [regex]::Replace(
        $pyproject,
        '(?m)^version\s*=\s*"([^"]+)"\s*$',
        "version = `"$target`"",
        1
    )
    $updatedInit = [regex]::Replace(
        $initFile,
        '(?m)^__version__\s*=\s*"([^"]+)"\s*$',
        "__version__ = `"$target`"",
        1
    )

    Write-Utf8NoBom -Path $pyprojectPath -Content $updatedPy
    Write-Utf8NoBom -Path $initPath -Content $updatedInit

    git add "PROJECT/pyproject.toml" "PROJECT/src/shinon_os/__init__.py"
    if ($LASTEXITCODE -ne 0) {
        throw "git add failed."
    }

    git commit -m "chore: bump version to $target"
    if ($LASTEXITCODE -ne 0) {
        throw "git commit failed."
    }

    git tag -a $tagName -m "Release $tagName"
    if ($LASTEXITCODE -ne 0) {
        throw "git tag failed."
    }

    Write-Host "Version bumped: $currentPy -> $target"
    Write-Host "Created commit and tag: $tagName"
}
finally {
    Pop-Location
}
