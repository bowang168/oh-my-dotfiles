---
layout: default
---

# oh-my-dotfiles

Cross-platform dotfiles & config management for **macOS** + **Oracle Linux 9**.

Two Python scripts handle everything:

```
install.py   repo -> system   (restore on a fresh machine)
backup.py    system -> repo   (snapshot before committing)
```

---

## Quick Start

```bash
git clone git@github.com:bowang168/oh-my-dotfiles.git ~/g/oh-my-dotfiles
cd ~/g/oh-my-dotfiles
python3 install.py          # interactive restore
python3 backup.py           # backup current configs
```

Both scripts support `--dry-run` (preview), `--yes` (skip prompts), and `--only <step>` (run specific steps).

---

## What's Managed

### Shared (Cross-Platform)

| Config | Tool |
|--------|------|
| `.zshrc` / `.bashrc` / `.shell_common` | Shell |
| `.gitconfig` | Git (delta, gh auth) |
| `starship.toml` | Starship prompt |
| `nvim/init.lua` | Neovim (lazy.nvim + catppuccin) |
| `zsh/catppuccin/` | Zsh syntax highlighting |
| `bin/theme` | Dark/light toggle |

### macOS Only

| Config | Tool |
|--------|------|
| `Brewfile` | Homebrew packages |
| `.aerospace.toml` | AeroSpace tiling WM |
| `ghostty/config` | Ghostty terminal |
| `defaults/*.plist` | macOS system preferences |
| `services/*.workflow` | Automator Quick Actions |
| Oh My Zsh plugins | zsh-autosuggestions, syntax-highlighting |

### Oracle Linux 9 Only

| Config | Tool |
|--------|------|
| `kitty.conf` | Kitty terminal |
| `gnome-terminal-profiles.dconf` | GNOME Terminal |
| `packages.txt` | dnf packages |
| `bin/toggle_app` | Window toggle (xdotool) |

---

## Install Steps

| # | Step | macOS | Linux | Description |
|---|------|:---:|:---:|-------------|
| 0 | prereqs | ✓ | — | Xcode CLT, Homebrew, git, gh |
| 1 | brew | ✓ | ✓ | brew bundle / dnf install |
| 2 | configs | ✓ | ✓ | Symlink all dotfiles |
| 3 | omz | ✓ | ✓ | Oh My Zsh + custom plugins |
| 4 | defaults | ✓ | ✓ | macOS defaults / GNOME dconf |
| 5 | services | ✓ | — | Automator Quick Actions |
| 6 | claude | ✓ | ✓ | Claude Code CLI + config |
| 7 | fonts | ✓ | — | Nerd Font + CJK font |
| 8 | hidefolders | ✓ | — | Hide ~/Library, ~/Movies, etc. |
| 9 | ollama | opt | opt | Pull Ollama models |
| 10 | clihelp | ✓ | ✓ | Chinese CLI help (tldr) |

---

## Theme Toggle

```bash
theme dark    # Catppuccin Mocha
theme light   # Catppuccin Latte
theme toggle  # Switch
```

Affects: system appearance, Neovim, zsh highlighting, terminal.

---

## Sync Strategy

| Content | Method | Why |
|---------|--------|-----|
| Dotfiles & configs | Git (this repo) | Version control |
| Secrets | Manual copy | Security |

---

**[View on GitHub](https://github.com/bowang168/oh-my-dotfiles)** ·
**[中文文档](https://github.com/bowang168/oh-my-dotfiles/blob/main/README.zh.md)**
