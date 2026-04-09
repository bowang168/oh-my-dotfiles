# .bashrc — interactive bash sessions
# Compatible with macOS and Linux

# Private env vars — MUST be before .shell_common
[ -f "$HOME/.bashrc_private" ] && source "$HOME/.bashrc_private"

# Shared aliases and functions
[ -f "$HOME/.shell_common" ] && source "$HOME/.shell_common"

# bash-only: 'which' shows all locations (zsh has this built-in)
alias which='type -a'
