#!/usr/bin/env bash
# install.sh — symlink dotfiles to home directory
# Detects OS and deploys shared/ + platform-specific configs
# Usage: cd ~/g/oh-my-dotfiles && ./install.sh
# Safe to run multiple times — existing symlinks are overwritten,
# existing regular files are backed up to ~/.dotfiles_backup/

set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKUP_DIR="$HOME/.dotfiles_backup/$(date +%Y%m%d_%H%M%S)"
OS_TYPE="$(uname)"

# --- Helpers ---

link() {
    local src="$1" dst="$2"

    # If destination is already a correct symlink, skip
    if [[ -L "$dst" && "$(readlink "$dst")" == "$src" ]]; then
        echo "  ok  $dst"
        return
    fi

    # Back up existing file (not symlink) before overwriting
    if [[ -e "$dst" && ! -L "$dst" ]]; then
        mkdir -p "$BACKUP_DIR"
        mv "$dst" "$BACKUP_DIR/"
        echo "  bak $dst → $BACKUP_DIR/$(basename "$dst")"
    fi

    mkdir -p "$(dirname "$dst")"
    ln -sf "$src" "$dst"
    echo "  ln  $dst → $src"
}

# ============================================================
# Shared (cross-platform) configs
# ============================================================
echo "=== Shared configs ==="

echo "Shell:"
link "$DOTFILES_DIR/shared/.bash_profile"  "$HOME/.bash_profile"
link "$DOTFILES_DIR/shared/.bashrc"        "$HOME/.bashrc"
link "$DOTFILES_DIR/shared/.shell_common"  "$HOME/.shell_common"
link "$DOTFILES_DIR/shared/.zprofile"      "$HOME/.zprofile"
link "$DOTFILES_DIR/shared/.zshenv"        "$HOME/.zshenv"
link "$DOTFILES_DIR/shared/.zshrc"         "$HOME/.zshrc"
link "$DOTFILES_DIR/shared/.hushlogin"     "$HOME/.hushlogin"
link "$DOTFILES_DIR/shared/.gitconfig"     "$HOME/.gitconfig"

echo "Scripts:"
link "$DOTFILES_DIR/shared/bin/theme"      "$HOME/.local/bin/theme"

echo "Starship:"
link "$DOTFILES_DIR/shared/starship.toml"  "$HOME/.config/starship.toml"

echo "Zsh themes:"
link "$DOTFILES_DIR/shared/zsh/catppuccin/mocha.zsh" "$HOME/.zsh/catppuccin/mocha.zsh"
link "$DOTFILES_DIR/shared/zsh/catppuccin/latte.zsh" "$HOME/.zsh/catppuccin/latte.zsh"

echo "Neovim:"
link "$DOTFILES_DIR/shared/nvim/init.lua"       "$HOME/.config/nvim/init.lua"
link "$DOTFILES_DIR/shared/nvim/lazy-lock.json" "$HOME/.config/nvim/lazy-lock.json"

# ============================================================
# Platform-specific configs
# ============================================================

if [[ "$OS_TYPE" == "Darwin" ]]; then
    echo ""
    echo "=== macOS configs ==="

    echo "Ghostty:"
    link "$DOTFILES_DIR/macos/ghostty/config" "$HOME/.config/ghostty/config"

    echo "AeroSpace:"
    link "$DOTFILES_DIR/macos/.aerospace.toml" "$HOME/.aerospace.toml"

    echo "Fonts:"
    if command -v brew &>/dev/null; then
        brew list --cask font-maple-mono-nf &>/dev/null 2>&1 || brew install --cask font-maple-mono-nf
        brew list --cask font-lxgw-wenkai-mono &>/dev/null 2>&1 || brew install --cask font-lxgw-wenkai-mono
        echo "  ok  fonts installed via brew"
    else
        echo "  skip fonts (brew not found)"
    fi

else
    echo ""
    echo "=== Linux configs ==="

    echo "Kitty:"
    link "$DOTFILES_DIR/linux/kitty.conf" "$HOME/.config/kitty/kitty.conf"

    echo "Scripts:"
    link "$DOTFILES_DIR/linux/bin/toggle_app" "$HOME/.local/bin/toggle_app"

    echo "GNOME Terminal:"
    if command -v dconf &>/dev/null; then
        dconf load /org/gnome/terminal/legacy/profiles:/ < "$DOTFILES_DIR/linux/gnome-terminal-profiles.dconf"
        echo "  ok  loaded terminal profiles"
    else
        echo "  skip (dconf not found)"
    fi
fi

# ============================================================
# Common post-install
# ============================================================
echo ""
echo "=== Post-install ==="

# Theme mode (don't overwrite existing preference)
if [[ ! -f "$HOME/.theme_mode" ]]; then
    echo "dark" > "$HOME/.theme_mode"
    echo "  new ~/.theme_mode (dark)"
else
    echo "  ok  ~/.theme_mode ($(cat "$HOME/.theme_mode"))"
fi

# Secrets template (copy, never symlink)
if [[ ! -f "$HOME/.bashrc_private" ]]; then
    cp "$DOTFILES_DIR/shared/.bashrc_private.example" "$HOME/.bashrc_private"
    chmod 600 "$HOME/.bashrc_private"
    echo "  new ~/.bashrc_private (from template — edit with real values)"
else
    echo "  ok  ~/.bashrc_private (exists)"
fi

# Chinese CLI help
echo "Chinese CLI help:"
if ! command -v tldr &>/dev/null; then
    if command -v pip3 &>/dev/null; then
        pip3 install --user tldr
        echo "  ok  tldr installed"
    else
        echo "  skip tldr (pip3 not found)"
    fi
else
    echo "  ok  tldr already installed"
fi

# --- Summary ---
echo ""
echo "Done. OS: $OS_TYPE"
if [[ -d "$BACKUP_DIR" ]]; then
    echo "Backups saved to: $BACKUP_DIR"
fi
echo ""
echo "Next steps:"
echo "  1. Edit ~/.bashrc_private with your API keys"
echo "  2. Open a new terminal or run: exec zsh"
if [[ "$OS_TYPE" == "Darwin" ]]; then
    echo "  3. Run 'brew bundle --file=macos/Brewfile' to install packages"
else
    echo "  3. Run 'sudo dnf install \$(grep -v \"^#\" linux/packages.txt | tr \"\\n\" \" \")' to install packages"
fi
