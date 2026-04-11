# oh-my-dotfiles

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-yellow?style=flat-square&logo=buy-me-a-coffee)](https://buymeacoffee.com/bowang168)
[![Sponsor](https://img.shields.io/badge/GitHub%20Sponsors-sponsor-ea4aaa?style=flat-square&logo=github-sponsors)](https://github.com/sponsors/bowang168)

Cross-platform dotfiles & config management for **macOS** + **Oracle Linux 9**.

Two scripts handle everything:

| Script | Direction | What it does |
|--------|-----------|--------------|
| `install.py` | repo -> system | Symlink configs, install packages, restore preferences |
| `backup.py` | system -> repo | Snapshot current configs back into the repo |

> **[Chinese README / 中文文档](README.zh.md)**

## Structure

```
oh-my-dotfiles/
├── install.py           # Restore: repo -> system
├── backup.py            # Backup:  system -> repo
│
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
│   ├── services/        # Automator Quick Actions
│   ├── omz-custom/      # Oh My Zsh plugin list
│   └── docs/            # macOS guides
│
├── linux/               # Oracle Linux 9 only
│   ├── packages.txt     # dnf packages
│   ├── kitty.conf       # Kitty terminal
│   ├── gnome-terminal-profiles.dconf
│   ├── bin/toggle_app   # Window toggle (xdotool)
│   └── docs/            # Linux guides
│
├── claude/              # Claude Code config (after backup)
│   ├── CLAUDE.md
│   ├── settings.json
│   └── projects/        # Project memories
│
└── ollama_models.txt    # Ollama model list (after backup)
```

## Quick Start

### Fresh machine (restore)

```bash
# 1. Clone
git clone git@github.com:bowang168/oh-my-dotfiles.git ~/g/oh-my-dotfiles
cd ~/g/oh-my-dotfiles

# 2. Install everything (interactive, confirms each step)
python3 install.py

# 3. Or skip confirmations
python3 install.py --yes

# 4. Or preview first
python3 install.py --dry-run

# 5. Or run specific steps only
python3 install.py --only prereqs brew configs omz
```

### Existing machine (backup)

```bash
cd ~/g/oh-my-dotfiles

# Full backup
python3 backup.py

# Preview what would be backed up
python3 backup.py --dry-run

# Specific steps only
python3 backup.py --only brew defaults

# Then commit and push
git add -A && git commit -m 'backup' && git push
```

## Install Steps

| # | Step | macOS | Linux | Description |
|---|------|:-----:|:-----:|-------------|
| 0 | `prereqs` | Yes | skip | Xcode CLT, Homebrew, git, gh |
| 1 | `brew` | Yes | Yes | `brew bundle` / `dnf install` |
| 2 | `configs` | Yes | Yes | Symlink all dotfiles |
| 3 | `omz` | Yes | Yes | Oh My Zsh + custom plugins |
| 4 | `defaults` | Yes | Yes | macOS `defaults import` / GNOME dconf |
| 5 | `services` | Yes | skip | Automator Quick Actions |
| 6 | `claude` | Yes | Yes | Claude Code CLI + config |
| 7 | `fonts` | Yes | skip | Nerd Font + CJK font |
| 8 | `hidefolders` | Yes | skip | Hide ~/Library, ~/Movies, etc. |
| 9 | `ollama` | opt | opt | Pull Ollama models (slow) |
| 10 | `clihelp` | Yes | Yes | Chinese CLI help (tldr) |

## Backup Steps

| # | Step | macOS | Linux | Description |
|---|------|:-----:|:-----:|-------------|
| 1 | `brew` | Yes | skip | Export Brewfile |
| 2 | `configs` | Yes | Yes | Copy config files to repo |
| 3 | `defaults` | Yes | Yes | Export macOS defaults / GNOME dconf |
| 4 | `services` | Yes | skip | Copy Automator workflows |
| 5 | `claude` | Yes | Yes | Claude Code config + project memories |
| 6 | `omz` | Yes | Yes | Record custom plugin URLs |
| 7 | `ollama` | Yes | Yes | Record installed model list |
| 8 | `shortcuts` | Yes | skip | Export macOS Shortcuts names |

## Sync Strategy

| Content | Method | Why |
|---------|--------|-----|
| Dotfiles & configs | **Git** (this repo) | Version control, diff review |
| Secrets (`.bashrc_private`, `.ssh/`) | **Manual copy** | Security |

## Theme

Unified dark/light toggle across all tools:

```bash
theme dark    # Catppuccin Mocha
theme light   # Catppuccin Latte
theme toggle  # Switch
```

Affects: macOS system appearance / GNOME GTK, Neovim, zsh syntax highlighting, terminal.

## Manual Steps After Install

These cannot be automated and must be done by hand:

1. Copy `~/.ssh/` and `~/.bashrc_private` from encrypted backup
2. Login: Apple ID / iCloud / Brave Browser sync
3. macOS permissions: Accessibility, Full Disk Access, Input Monitoring
4. Display settings: Night Shift, True Tone, resolution
5. Default browser, Lock screen / Touch ID

## License

[MIT](LICENSE)
