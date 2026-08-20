[CmdletBinding()]
param(
    [ValidateSet("universal", "plugin")]
    [string]$DiscoveryProfile,
    [string]$BootstrapPython,
    [string]$CodexPath,
    [string]$CodexHome,
    [string]$ToolingPython,
    [string]$MarketplaceName = "my-codex",
    [string]$GitMarketplaceSource,
    [string]$GitRef = "main",
    [switch]$PrunePlugins,
    [switch]$DryRun,
    [switch]$SkipCheck
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$CodexPathWasProvided = $PSBoundParameters.ContainsKey("CodexPath")
$GitRefWasProvided = $PSBoundParameters.ContainsKey("GitRef")

if (-not $DiscoveryProfile) {
    throw "missing required -DiscoveryProfile universal|plugin"
}
if ($DiscoveryProfile -eq "universal" -and $PrunePlugins) {
    throw "-PrunePlugins is incompatible with -DiscoveryProfile universal"
}

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

    $command = Get-Command -Name $expanded -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($command) {
        if ($command.Path) {
            return $command.Path
        }
        if ($command.Source) {
            return $command.Source
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

$env:MY_CODEX_ROOT = $repoRoot
if (-not $CodexHome) {
    if ($env:CODEX_HOME) {
        $CodexHome = $env:CODEX_HOME
    }
    else {
        $CodexHome = Join-Path $env:USERPROFILE ".codex"
    }
}
$env:CODEX_HOME = [System.IO.Path]::GetFullPath($CodexHome)

if (-not $BootstrapPython) {
    $BootstrapPython = Resolve-BootstrapPython
}
else {
    $BootstrapPython = Resolve-BootstrapPython -ExplicitPath $BootstrapPython
}

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
if ($CodexPathWasProvided) {
    Write-Host "CodexPath=$CodexPath"
}
else {
    Write-Host "CodexPath=auto-if-plugin-removal-is-required"
}
Write-Host "MarketplaceName=$MarketplaceName"
Write-Host "DiscoveryProfile=$DiscoveryProfile"
if ($PrunePlugins) {
    Write-Host "PrunePlugins=enabled"
}
else {
    Write-Host "PrunePlugins=disabled"
}

if ($PrunePlugins -and -not $DryRun) {
    Write-Host "Plugin pruning removes installed or cached $MarketplaceName plugins that are not selected by .agents/plugins/install-manifest.json."
    if (-not (Confirm-Action -Prompt "Prune stale $MarketplaceName plugins during refresh")) {
        throw "plugin pruning was requested but not confirmed"
    }
}

$bootstrapArgs = @(
    "scripts\bootstrap_tooling_env.py",
    "--venv", $venvPath
)
if ($DryRun) {
    $bootstrapArgs += "--dry-run"
}
Invoke-Checked `
    -Exe $BootstrapPython `
    -Arguments $bootstrapArgs `
    -Label "my-codex tooling bootstrap"

if (-not (Test-Path -LiteralPath $env:MY_CODEX_PYTHON -PathType Leaf)) {
    if ($DryRun) {
        throw "tooling Python is unavailable after dry-run bootstrap: $env:MY_CODEX_PYTHON. Run the wrapper without -DryRun once to create the tooling environment."
    }
    throw "tooling Python is unavailable after bootstrap: $env:MY_CODEX_PYTHON"
}

$refreshArgs = @(
    "scripts\refresh_my_codex.py",
    "--discovery-profile", $DiscoveryProfile,
    "--codex-home", $env:CODEX_HOME,
    "--venv", $venvPath,
    "--python", $env:MY_CODEX_PYTHON,
    "--marketplace-name", $MarketplaceName,
    "--marketplace-source", $repoRoot,
    "--skip-bootstrap"
)
if ($CodexPathWasProvided) {
    $refreshArgs += @("--codex", $CodexPath)
}
if ($GitMarketplaceSource) {
    $refreshArgs += @("--git-marketplace-source", $GitMarketplaceSource)
}
if ($GitRefWasProvided) {
    $refreshArgs += @("--git-ref", $GitRef)
}
if ($DryRun) {
    $refreshArgs += "--dry-run"
}
if ($PrunePlugins) {
    $refreshArgs += "--prune-plugins"
}

Invoke-Checked `
    -Exe $env:MY_CODEX_PYTHON `
    -Arguments $refreshArgs `
    -Label "my-codex refresh"

if ($DryRun -and -not $SkipCheck) {
    Write-Host "Dry run: skipping closure check because no local state was changed."
}
elseif (-not $SkipCheck) {
    $checkArgs = @(
        "scripts\check_my_codex.py",
        "--discovery-profile", $DiscoveryProfile,
        "--codex-home", $env:CODEX_HOME,
        "--venv", $venvPath,
        "--python", $env:MY_CODEX_PYTHON,
        "--marketplace-name", $MarketplaceName
    )
    if ($CodexPathWasProvided) {
        $checkArgs += @("--codex", $CodexPath)
    }
    Invoke-Checked `
        -Exe $env:MY_CODEX_PYTHON `
        -Arguments $checkArgs `
        -Label "my-codex closure check"
}

Sync-AgentsInstructions `
    -RepoRoot $repoRoot `
    -CodexHome $env:CODEX_HOME `
    -DryRunMode ([bool]$DryRun)
