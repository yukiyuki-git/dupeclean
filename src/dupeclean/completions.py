"""Shell completion generation for DupeClean.

Generates shell completion scripts for bash, zsh, and fish.
"""

from __future__ import annotations

BASH_COMPLETION = """\
# DupeClean bash completion
_dupeclean_completions() {
    local cur prev commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    commands="--cli --duplicates --top --report --compare --quick --api --api-port --output --threads --follow-symlinks --show-hidden --ignore --no-dedup --config --help --version"

    case "${prev}" in
        --report)
            COMPREPLY=( $(compgen -W "json csv html" -- ${cur}) )
            return 0
            ;;
        --output)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --config)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --threads|--api-port)
            return 0
            ;;
    esac

    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
        return 0
    fi

    COMPREPLY=( $(compgen -d -- ${cur}) )
}

complete -F _dupeclean_completions dupeclean
complete -F _dupeclean_completions dc
"""

ZSH_COMPLETION = """\
#compdef dupeclean dc

_dupeclean() {
    local -a commands
    commands=(
        '--cli[Run in CLI mode (no TUI)]'
        '--duplicates[Find and show duplicate files]'
        '--top[Show top N largest files]:N:'
        '--report[Generate report]:(json csv html)'
        '--compare[Compare two directories]:DIR_A:DIR_B'
        '--quick[Quick scan (size-based)]'
        '--api[Start REST API server]'
        '--api-port[API server port]:PORT:'
        '--output[Output file for report]:FILE:_files'
        '--threads[Number of threads]:N:'
        '--follow-symlinks[Follow symbolic links]'
        '--show-hidden[Include hidden files]'
        '--ignore[Additional glob patterns]:PATTERN:'
        '--no-dedup[Skip duplicate detection]'
        '--config[Path to config file]:FILE:_files'
    )

    _arguments -s $commands '*:directory:_directories'
}

_dupeclean "$@"
"""

FISH_COMPLETION = """\
# DupeClean fish completion

complete -c dupeclean -c dc -l cli -d "Run in CLI mode (no TUI)"
complete -c dupeclean -c dc -l duplicates -d "Find and show duplicate files"
complete -c dupeclean -c dc -l top -d "Show top N largest files" -r
complete -c dupeclean -c dc -l report -d "Generate report" -a "json csv html"
complete -c dupeclean -c dc -l compare -d "Compare two directories" -r
complete -c dupeclean -c dc -l quick -d "Quick scan (size-based)"
complete -c dupeclean -c dc -l api -d "Start REST API server"
complete -c dupeclean -c dc -l api-port -d "API server port" -r
complete -c dupeclean -c dc -l output -d "Output file for report" -r -F
complete -c dupeclean -c dc -l threads -d "Number of threads" -r
complete -c dupeclean -c dc -l follow-symlinks -d "Follow symbolic links"
complete -c dupeclean -c dc -l show-hidden -d "Include hidden files"
complete -c dupeclean -c dc -l ignore -d "Glob patterns to ignore" -r
complete -c dupeclean -c dc -l no-dedup -d "Skip duplicate detection"
complete -c dupeclean -c dc -l config -d "Path to config file" -r -F
complete -c dupeclean -c dc -l help -d "Show help"
complete -c dupeclean -c dc -l version -d "Show version"
"""


def get_completion(shell: str) -> str | None:
    """Get shell completion script for the specified shell.

    Args:
        shell: Shell name ("bash", "zsh", or "fish").

    Returns:
        Completion script string, or None if shell not supported.
    """
    completions = {
        "bash": BASH_COMPLETION,
        "zsh": ZSH_COMPLETION,
        "fish": FISH_COMPLETION,
    }
    return completions.get(shell.lower())


def print_completion(shell: str) -> bool:
    """Print shell completion script.

    Returns True if shell is supported.
    """
    script = get_completion(shell)
    if script:
        print(script)
        return True
    return False
