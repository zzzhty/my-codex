#!/usr/bin/env sh
set -eu

usage() {
    cat <<'EOF'
Usage: scripts/upgrade_my_codex.sh [options]

Options:
  --bootstrap-python PATH       Python used to run the helper scripts.
  --codex PATH                  Codex CLI executable. Defaults to CODEX_BIN or codex on PATH.
  --codex-home PATH             Codex home directory. Defaults to CODEX_HOME or ~/.codex.
  --tooling-python PATH         Python installed into Codex hooks.
  --marketplace-name NAME       Marketplace name. Defaults to my-codex.
  --git-marketplace-source URL  Git marketplace source. Defaults to remote.origin.url.
  --git-ref REF                 Git ref for first-time Git marketplace add. Defaults to main.
  --dry-run                     Print commands without changing Codex state.
  --skip-check                  Skip the final closure check.
  -h, --help                    Show this help.
EOF
}

require_value() {
    option=$1
    value=${2-}
    if [ -z "$value" ]; then
        echo "missing value for $option" >&2
        exit 2
    fi
}

resolve_command() {
    label=$1
    value=$2
    if [ -z "$value" ]; then
        echo "$label not found" >&2
        exit 1
    fi
    if [ -f "$value" ]; then
        printf '%s\n' "$value"
        return
    fi
    resolved=$(command -v "$value" 2>/dev/null || true)
    if [ -n "$resolved" ]; then
        printf '%s\n' "$resolved"
        return
    fi
    echo "$label not found: $value" >&2
    exit 1
}

codex_version() {
    "$codex_path" --version 2>/dev/null || printf '%s\n' "unknown"
}

require_codex_subcommand() {
    command_label=$1
    shift
    if "$codex_path" "$@" --help >/dev/null 2>&1; then
        return
    fi

    echo "required Codex CLI command is unavailable: codex $command_label" >&2
    echo "CodexPath=$codex_path" >&2
    echo "CodexVersion=$(codex_version)" >&2
    echo "FailedCommand=$codex_path $* --help" >&2
    echo "Breakpoint=before marketplace refresh in scripts/upgrade_my_codex.sh" >&2
    echo "Upgrade Codex CLI to 0.131.0 or newer; 0.130.0 lacks non-interactive plugin add/list commands." >&2
    exit 1
}

require_codex_plugin_commands() {
    require_codex_subcommand "plugin marketplace add" plugin marketplace add
    require_codex_subcommand "plugin add" plugin add
    require_codex_subcommand "plugin list" plugin list
}

canonical_path() {
    path=$1
    if command -v realpath >/dev/null 2>&1; then
        resolved=$(realpath "$path" 2>/dev/null || true)
        if [ -n "$resolved" ]; then
            printf '%s\n' "$resolved"
            return
        fi
        resolved=$(realpath -m "$path" 2>/dev/null || true)
        if [ -n "$resolved" ]; then
            printf '%s\n' "$resolved"
            return
        fi
    fi

    dir=$(dirname -- "$path")
    base=$(basename -- "$path")
    if [ -d "$dir" ]; then
        printf '%s/%s\n' "$(CDPATH= cd -- "$dir" && pwd -P)" "$base"
    else
        printf '%s\n' "$path"
    fi
}

resolve_link_target() {
    link_path=$1
    link_target=$(readlink "$link_path")
    case "$link_target" in
        /*)
            canonical_path "$link_target"
            ;;
        *)
            canonical_path "$(dirname -- "$link_path")/$link_target"
            ;;
    esac
}

confirm_action() {
    prompt=$1
    printf '%s [y/N] ' "$prompt"
    IFS= read -r answer || answer=
    case "$answer" in
        y|Y|yes|YES|Yes)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

sync_agents_instructions() {
    source_path="$repo_root/AGENTS.md"
    target_path="$CODEX_HOME/AGENTS.md"

    if [ ! -f "$source_path" ]; then
        echo "source AGENTS.md does not exist: $source_path" >&2
        exit 1
    fi

    desired_target=$(canonical_path "$source_path")
    if [ -L "$target_path" ]; then
        current_target=$(resolve_link_target "$target_path")
        if [ "$current_target" = "$desired_target" ]; then
            echo "AGENTS.md already points at source: $target_path -> $source_path"
            return
        fi
        echo "AGENTS.md points at a different source."
        echo "CurrentTarget=$current_target"
        echo "DesiredTarget=$desired_target"
    elif [ -e "$target_path" ]; then
        if [ -d "$target_path" ]; then
            echo "refusing to replace directory target: $target_path" >&2
            exit 1
        fi
        echo "AGENTS.md target exists but is not a symlink: $target_path"
        echo "DesiredTarget=$desired_target"
    else
        echo "AGENTS.md target is missing: $target_path"
        echo "DesiredTarget=$desired_target"
    fi

    if [ "$dry_run" -eq 1 ]; then
        echo "+ ln -sfn $source_path $target_path"
        return
    fi

    if ! confirm_action "Link source AGENTS.md to target"; then
        echo "AGENTS.md sync was not confirmed" >&2
        exit 1
    fi

    mkdir -p "$CODEX_HOME"
    ln -sfn "$source_path" "$target_path"
    echo "AGENTS.md linked: $target_path -> $source_path"
}

find_bootstrap_python() {
    if [ -n "${MY_CODEX_BOOTSTRAP_PYTHON:-}" ]; then
        resolve_command "Bootstrap Python" "$MY_CODEX_BOOTSTRAP_PYTHON"
        return
    fi
    if command -v python3 >/dev/null 2>&1; then
        command -v python3
        return
    fi
    if command -v python >/dev/null 2>&1; then
        command -v python
        return
    fi
    echo "Bootstrap Python not found. Set MY_CODEX_BOOTSTRAP_PYTHON or install python3." >&2
    exit 1
}

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd)

bootstrap_python=${MY_CODEX_BOOTSTRAP_PYTHON:-}
codex_path=${CODEX_BIN:-}
codex_home=${CODEX_HOME:-"$HOME/.codex"}
tooling_python=${MY_CODEX_PYTHON:-}
marketplace_name=my-codex
git_marketplace_source=
git_ref=main
dry_run=0
skip_check=0

while [ "$#" -gt 0 ]; do
    case "$1" in
        --bootstrap-python)
            require_value "$1" "${2-}"
            bootstrap_python=$2
            shift 2
            ;;
        --bootstrap-python=*)
            bootstrap_python=${1#*=}
            shift
            ;;
        --codex)
            require_value "$1" "${2-}"
            codex_path=$2
            shift 2
            ;;
        --codex=*)
            codex_path=${1#*=}
            shift
            ;;
        --codex-home)
            require_value "$1" "${2-}"
            codex_home=$2
            shift 2
            ;;
        --codex-home=*)
            codex_home=${1#*=}
            shift
            ;;
        --tooling-python)
            require_value "$1" "${2-}"
            tooling_python=$2
            shift 2
            ;;
        --tooling-python=*)
            tooling_python=${1#*=}
            shift
            ;;
        --marketplace-name)
            require_value "$1" "${2-}"
            marketplace_name=$2
            shift 2
            ;;
        --marketplace-name=*)
            marketplace_name=${1#*=}
            shift
            ;;
        --git-marketplace-source)
            require_value "$1" "${2-}"
            git_marketplace_source=$2
            shift 2
            ;;
        --git-marketplace-source=*)
            git_marketplace_source=${1#*=}
            shift
            ;;
        --git-ref)
            require_value "$1" "${2-}"
            git_ref=$2
            shift 2
            ;;
        --git-ref=*)
            git_ref=${1#*=}
            shift
            ;;
        --dry-run)
            dry_run=1
            shift
            ;;
        --skip-check)
            skip_check=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if [ -z "$bootstrap_python" ]; then
    bootstrap_python=$(find_bootstrap_python)
else
    bootstrap_python=$(resolve_command "Bootstrap Python" "$bootstrap_python")
fi

if [ -z "$codex_path" ]; then
    codex_path=$(resolve_command "Codex CLI" codex)
else
    codex_path=$(resolve_command "Codex CLI" "$codex_path")
fi
require_codex_plugin_commands

if [ -z "$tooling_python" ]; then
    tooling_python="$codex_home/venvs/my-codex/bin/python"
fi
venv_path="$codex_home/venvs/my-codex"

export CODEX_HOME="$codex_home"
export MY_CODEX_ROOT="$repo_root"
export MY_CODEX_PYTHON="$tooling_python"
export MY_CODEX_TOOLING_PYTHON="$tooling_python"
export PLUGIN_VALIDATOR="${PLUGIN_VALIDATOR:-$CODEX_HOME/skills/.system/plugin-creator/scripts/validate_plugin.py}"

echo "MY_CODEX_ROOT=$MY_CODEX_ROOT"
echo "CODEX_HOME=$CODEX_HOME"
echo "MY_CODEX_PYTHON=$MY_CODEX_PYTHON"
echo "MY_CODEX_TOOLING_PYTHON=$MY_CODEX_TOOLING_PYTHON"
echo "PLUGIN_VALIDATOR=$PLUGIN_VALIDATOR"
echo "BootstrapPython=$bootstrap_python"
echo "CodexPath=$codex_path"
echo "MarketplaceName=$marketplace_name"

cd "$repo_root"

set -- "$repo_root/scripts/refresh_my_codex.py" \
    --codex "$codex_path" \
    --codex-home "$CODEX_HOME" \
    --venv "$venv_path" \
    --python "$MY_CODEX_PYTHON" \
    --marketplace-name "$marketplace_name" \
    --marketplace-source "$repo_root" \
    --git-ref "$git_ref"

if [ -n "$git_marketplace_source" ]; then
    set -- "$@" --git-marketplace-source "$git_marketplace_source"
fi
if [ "$dry_run" -eq 1 ]; then
    set -- "$@" --dry-run
fi

echo "+ $bootstrap_python $*"
"$bootstrap_python" "$@"

if [ "$dry_run" -eq 1 ] && [ "$skip_check" -eq 0 ]; then
    echo "Dry run: skipping closure check because no local state was changed."
elif [ "$skip_check" -eq 0 ]; then
    set -- "$repo_root/scripts/check_my_codex.py" \
        --codex "$codex_path" \
        --codex-home "$CODEX_HOME" \
        --venv "$venv_path" \
        --python "$MY_CODEX_PYTHON" \
        --marketplace-name "$marketplace_name"
    echo "+ $bootstrap_python $*"
    "$bootstrap_python" "$@"
fi

sync_agents_instructions
