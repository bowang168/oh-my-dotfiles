# .zprofile — zsh login shell (runs once per login session)
# Platform-specific PATH setup

OS_TYPE="$(uname)"

if [[ "$OS_TYPE" == "Darwin" ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv zsh)"

    # Python 3.13
    PATH="/Library/Frameworks/Python.framework/Versions/3.13/bin:${PATH}"
    export PATH

    # Obsidian
    export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"
fi

export PATH="$HOME/.local/bin:$PATH"
