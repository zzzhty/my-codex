[CmdletBinding()]
param(
    [string]$BootstrapPython,
    [string]$CodexPath,
    [string]$CodexHome,
    [string]$ToolingPython,
    [string]$MarketplaceName = "my-codex",
    [string]$GitMarketplaceSource,
    [string]$GitRef = "main",
    [switch]$DryRun,
    [switch]$SkipCheck
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-ExecutableCandidate {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Candidate
    )

    $expanded = [Environment]::ExpandEnvironmentVariables($Candidate)
    if ($expanded.StartsWith("~")) {
        $expanded = Join-Path $env:USERPROFILE $expanded.Substring(1).TrimStart("\", "/")
    }

    if (Test-Path -LiteralPath $expanded -PathType Leaf) {
        return (Resolve-Path -LiteralPath $expanded).Path
    }

    $command = Get-Command -Name $expanded -ErrorAction SilentlyContinue
    if ($command) {
        if ($command.Source) {
            return $command.Source
        }
        if ($command.Path) {
            return $command.Path
        }
        return $command.Name
    }

    return $null
}

function Resolve-Executable {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,

        [string[]]$Candidates
    )

    $checked = New-Object System.Collections.Generic.List[string]
    foreach ($candidate in $Candidates) {
        if (-not $candidate) {
            continue
        }
        $checked.Add($candidate)
        $resolved = Resolve-ExecutableCandidate -Candidate $candidate
        if ($resolved) {
            return $resolved
        }
    }

    throw "$Label not found. Checked:$([Environment]::NewLine)$($checked -join [Environment]::NewLine)"
}

function Get-LatestCodexCliCandidates {
    $candidates = New-Object System.Collections.Generic.List[string]

    if ($env:CODEX_BIN) {
        $candidates.Add($env:CODEX_BIN)
    }
    $candidates.Add("codex")

    $binRoot = Join-Path $env:LOCALAPPDATA "OpenAI\Codex\bin"
    if (Test-Path -LiteralPath $binRoot -PathType Container) {
        Get-ChildItem -LiteralPath $binRoot -Recurse -Filter "codex.exe" -File |
            Sort-Object LastWriteTime -Descending |
            ForEach-Object { $candidates.Add($_.FullName) }
    }

    $vscodeRoot = Join-Path $env:USERPROFILE ".vscode\extensions"
    if (Test-Path -LiteralPath $vscodeRoot -PathType Container) {
        Get-ChildItem -LiteralPath $vscodeRoot -Directory -Filter "openai.chatgpt-*" |
            Sort-Object LastWriteTime -Descending |
            ForEach-Object {
                $candidate = Join-Path $_.FullName "bin\windows-x86_64\codex.exe"
                if (Test-Path -LiteralPath $candidate -PathType Leaf) {
                    $candidates.Add($candidate)
                }
            }
    }

    return $candidates.ToArray()
}

function Resolve-BootstrapPython {
    param(
        [string]$ExplicitPath
    )

    if ($ExplicitPath) {
        return Resolve-Executable -Label "Bootstrap Python" -Candidates @($ExplicitPath)
    }

    return Resolve-Executable `
        -Label "Bootstrap Python" `
        -Candidates @(
            $env:MY_CODEX_BOOTSTRAP_PYTHON,
            "python",
            "py",
            (Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"),
            (Join-Path $env:USERPROFILE ".codex\venvs\my-codex\Scripts\python.exe")
        )
}

function Resolve-CodexCli {
    param(
        [string]$ExplicitPath
    )

    if ($ExplicitPath) {
        return Resolve-Executable -Label "Codex CLI" -Candidates @($ExplicitPath)
    }

    return Resolve-Executable -Label "Codex CLI" -Candidates (Get-LatestCodexCliCandidates)
}

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Exe,

        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,

        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    Write-Host ("+ {0} {1}" -f $Exe, ($Arguments -join " "))
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
}

function Confirm-Action {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Prompt
    )

    $answer = Read-Host "$Prompt [y/N]"
    return $answer -in @("y", "Y", "yes", "YES", "Yes")
}

function Sync-AgentsInstructions {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot,

        [Parameter(Mandatory = $true)]
        [string]$CodexHome,

        [Parameter(Mandatory = $true)]
        [bool]$DryRunMode
    )

    $source = Join-Path $RepoRoot "AGENTS.md"
    $target = Join-Path $CodexHome "AGENTS.md"

    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "source AGENTS.md does not exist: $source"
    }

    $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    if (Test-Path -LiteralPath $target) {
        $targetItem = Get-Item -LiteralPath $target -Force
        if ($targetItem.PSIsContainer) {
            throw "refusing to replace directory AGENTS.md target: $target"
        }
        if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
            throw "refusing to replace non-file AGENTS.md target: $target"
        }

        $targetHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
        if ($sourceHash -eq $targetHash) {
            Write-Host "AGENTS.md already matches: $target"
            return
        }
        Write-Host "AGENTS.md differs from source."
        Write-Host "Source=$source"
        Write-Host "Target=$target"
        Write-Host "SourceSHA256=$sourceHash"
        Write-Host "TargetSHA256=$targetHash"
    }
    else {
        Write-Host "AGENTS.md is missing at target: $target"
        Write-Host "Source=$source"
        Write-Host "SourceSHA256=$sourceHash"
    }

    if ($DryRunMode) {
        Write-Host ("+ Copy-Item -LiteralPath {0} -Destination {1} -Force" -f $source, $target)
        return
    }

    if (-not (Confirm-Action -Prompt "Copy source AGENTS.md to target")) {
        throw "AGENTS.md sync was not confirmed"
    }

    New-Item -ItemType Directory -Path $CodexHome -Force | Out-Null
    Copy-Item -LiteralPath $source -Destination $target -Force
    Write-Host "AGENTS.md synced: $target"
}

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
Set-Location -LiteralPath $repoRoot

if (-not $BootstrapPython) {
    $BootstrapPython = Resolve-BootstrapPython
}
else {
    $BootstrapPython = Resolve-BootstrapPython -ExplicitPath $BootstrapPython
}

$CodexPath = Resolve-CodexCli -ExplicitPath $CodexPath

$env:MY_CODEX_ROOT = $repoRoot
if (-not $CodexHome) {
    $CodexHome = Join-Path $env:USERPROFILE ".codex"
}
$env:CODEX_HOME = [System.IO.Path]::GetFullPath($CodexHome)

if (-not $ToolingPython) {
    $ToolingPython = Join-Path $env:CODEX_HOME "venvs\my-codex\Scripts\python.exe"
}
$env:MY_CODEX_PYTHON = [System.IO.Path]::GetFullPath($ToolingPython)
$env:MY_CODEX_TOOLING_PYTHON = $env:MY_CODEX_PYTHON
$env:PLUGIN_VALIDATOR = Join-Path $env:CODEX_HOME "skills\.system\plugin-creator\scripts\validate_plugin.py"

$venvPath = Join-Path $env:CODEX_HOME "venvs\my-codex"

Write-Host "MY_CODEX_ROOT=$env:MY_CODEX_ROOT"
Write-Host "CODEX_HOME=$env:CODEX_HOME"
Write-Host "MY_CODEX_PYTHON=$env:MY_CODEX_PYTHON"
Write-Host "MY_CODEX_TOOLING_PYTHON=$env:MY_CODEX_TOOLING_PYTHON"
Write-Host "PLUGIN_VALIDATOR=$env:PLUGIN_VALIDATOR"
Write-Host "BootstrapPython=$BootstrapPython"
Write-Host "CodexPath=$CodexPath"
Write-Host "MarketplaceName=$MarketplaceName"

$refreshArgs = @(
    "scripts\refresh_my_codex.py",
    "--codex", $CodexPath,
    "--codex-home", $env:CODEX_HOME,
    "--venv", $venvPath,
    "--python", $env:MY_CODEX_PYTHON,
    "--marketplace-name", $MarketplaceName,
    "--marketplace-source", $repoRoot,
    "--git-ref", $GitRef
)
if ($GitMarketplaceSource) {
    $refreshArgs += @("--git-marketplace-source", $GitMarketplaceSource)
}
if ($DryRun) {
    $refreshArgs += "--dry-run"
}

Invoke-Checked `
    -Exe $BootstrapPython `
    -Arguments $refreshArgs `
    -Label "my-codex refresh"

if ($DryRun -and -not $SkipCheck) {
    Write-Host "Dry run: skipping closure check because no local state was changed."
}
elseif (-not $SkipCheck) {
    Invoke-Checked `
        -Exe $BootstrapPython `
        -Arguments @(
            "scripts\check_my_codex.py",
            "--codex", $CodexPath,
            "--codex-home", $env:CODEX_HOME,
            "--venv", $venvPath,
            "--python", $env:MY_CODEX_PYTHON,
            "--marketplace-name", $MarketplaceName
        ) `
        -Label "my-codex closure check"
}

Sync-AgentsInstructions `
    -RepoRoot $repoRoot `
    -CodexHome $env:CODEX_HOME `
    -DryRunMode ([bool]$DryRun)
