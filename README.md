# oh-my-dotfiles

Cross-platform dotfiles & config management for **macOS** + **Oracle Linux 9**.

## Structure

```
oh-my-dotfiles/
├── shared/              # Cross-platform (macOS + Linux)
│   ├── .shell_common    # Shared aliases & functions
│   ├── .zshrc           # Zsh config (oh-my-zsh + starship)
│   ├── .bashrc          # Bash config
│   ├── .gitconfig       # Git config (delta, gh auth)
│   ├── starship.toml    # Starship prompt
│   ├── bin/theme        # Dark/light theme toggle
│   ├── nvim/            # Neovim (lazy.nvim + catppuccin)
│   └── zsh/catppuccin/  # Zsh syntax highlighting themes
│
├── macos/               # macOS only
│   ├── Brewfile         # Homebrew packages
│   ├── .aerospace.toml  # AeroSpace tiling WM
│   ├── ghostty/         # Ghostty terminal
│   ├── defaults/        # macOS plist exports
│   ├── services/        # Automator workflows
│   └── docs/            # macOS guides
│
├── linux/               # Oracle Linux 9 only
│   ├── packages.txt     # dnf packages
│   ├── kitty.conf       # Kitty terminal
│   ├── gnome-terminal-profiles.dconf
│   ├── bin/toggle_app   # Window toggle (xdotool)
│   └── docs/            # Linux guides
│
└── install.sh           # Bootstrap: detects OS → symlinks configs
```

## Quick Start

```bash
# Clone
git clone git@github.com:bowang168/oh-my-dotfiles.git ~/g/oh-my-dotfiles

# Install (auto-detects macOS vs Linux)
cd ~/g/oh-my-dotfiles && ./install.sh
```

The install script will:
1. Symlink shared configs to `~/`
2. Symlink OS-specific configs based on `uname`
3. Back up any existing files to `~/.dotfiles_backup/`

## Sync Strategy

| Content | Method | Why |
|---------|--------|-----|
| Dotfiles & configs | **Git** (this repo) | Version control, diff review |
| User data (`~/d/`) | **Syncthing** P2P | Real-time sync, no server |
| Secrets (`.bashrc_private`, `.ssh/`) | **Manual copy** | Security |

## After Install

1. Edit `~/.bashrc_private` with your API keys
2. macOS: `brew bundle --file=macos/Brewfile`
3. Linux: `sudo dnf install $(grep -v '^#' linux/packages.txt | tr '\n' ' ')`
4. Open a new terminal or `exec zsh`

## Theme

Unified dark/light toggle across all tools:

```bash
theme dark    # Catppuccin Mocha
theme light   # Catppuccin Latte
theme toggle  # Switch
```

Affects: macOS system appearance / GNOME GTK, Neovim, zsh syntax highlighting, terminal.
