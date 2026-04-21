# Only PATH and non-secret env vars here — runs for ALL zsh processes
typeset -U path PATH
export PATH="$HOME/.local/bin:$PATH"
