# oh-my-dotfiles

Cross-platform dotfiles manager for macOS and Linux.

## Quick Start

```bash
python3 install.py --dry-run        # Preview changes without applying
python3 install.py                   # Interactive install (confirm each step)
python3 install.py --yes             # Non-interactive full install
python3 install.py --only configs omz  # Run specific steps only

python3 backup.py --dry-run          # Preview what would be backed up
python3 backup.py --yes              # Snapshot current system configs into repo
```

## Project Structure

```
oh-my-dotfiles/
├── shared/              # Cross-platform configs (symlinked to ~)
│   ├── .zshrc, .zshenv, .bashrc, .shell_common, .gitconfig
│   ├── nvim/            # Neovim (init.lua + lazy-lock.json)
│   ├── zsh/             # Catppuccin syntax highlighting themes
│   ├── bin/             # Custom scripts (theme toggle)
│   └── starship.toml    # Starship prompt config (currently disabled)
├── macos/               # macOS-specific
│   ├── .aerospace.toml  # AeroSpace window manager config
│   ├── Brewfile         # Homebrew packages
│   ├── defaults/        # macOS plist defaults (dock, finder, etc.)
│   ├── ghostty/         # Terminal emulator config
│   ├── omz-custom/      # Oh-my-zsh plugin list
│   ├── services/        # Automator workflows
│   ├── shortcuts_list.txt
│   └── docs/            # Setup guides
├── linux/               # Linux-specific (kitty, GNOME, systemd)
├── install.py           # Restore configs to system (symlink + import)
├── backup.py            # Snapshot system configs into repo
└── ollama_models.txt    # Ollama model list for restore
```

## Key Scripts

- **install.py** — Deploys configs: detects OS, symlinks shared/ configs to `~`, imports macOS defaults, copies services.
- **backup.py** — Reverse of install: copies current system configs back into repo. Same CLI flags.

### Available steps for `--only`

| install.py | backup.py | What it does |
|------------|-----------|--------------|
| `prereqs` | — | Xcode CLT, Homebrew, git, gh |
| `brew` | `brew` | Brewfile install / dump |
| `configs` | `configs` | Symlink shared configs to ~ |
| `omz` | `omz` | Oh-my-zsh plugins |
| `defaults` | `defaults` | macOS plist defaults import/export |
| `services` | `services` | Automator workflows |
| `fonts` | — | Font installation |
| `hide_folders` | — | Hide ~/Public etc. on macOS |
| `ollama` | `ollama` | Ollama model pull / list |
| `cli_help` | — | Print manual post-install steps |
| — | `shortcuts` | Export macOS keyboard shortcuts |

## Conventions

- Shared configs are **symlinked** (not copied) so edits propagate.
- macOS defaults are **imported/exported** via `defaults import/export`.
- Secrets go in `.bashrc_private` (gitignored). Template: `shared/.bashrc_private.example`.
- Fonts excluded from git (too large) — stored in `fonts/` (gitignored).

## Editing Rules

- Do NOT modify `.bashrc_private` or any file matching `*private*`, `*secret*`, `*token*`, `*credential*`.
- When editing shell configs (.zshrc, .zshenv, etc.), keep POSIX compatibility in mind for .bashrc.
- Python scripts (install.py, backup.py) target Python 3.9+ with no external dependencies.
