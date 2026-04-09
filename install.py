#!/usr/bin/env python3
"""
install.py — Restore configs from this repo to the current system.

Detects macOS vs Linux and deploys shared + platform-specific configs.
Shared configs are symlinked; macOS defaults are imported; services are copied.

Usage:
    python3 install.py                  # interactive (confirm each step)
    python3 install.py --dry-run        # preview only, no changes
    python3 install.py --yes            # skip confirmations
    python3 install.py --only configs omz  # run specific steps only

Prerequisites (macOS):
    The script will auto-install Xcode CLT and Homebrew if missing.
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────

HOME = Path.home()
REPO = Path(__file__).resolve().parent
IS_MACOS = platform.system() == "Darwin"

# ── Terminal colours ─────────────────────────────────────────────────

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def info(msg):
    print(f"{GREEN}  [ok]{RESET}  {msg}")


def warn(msg):
    print(f"{YELLOW}  [skip]{RESET} {msg}")


def error(msg):
    print(f"{RED}  [err]{RESET} {msg}")


def section(title):
    print(f"\n{BOLD}{CYAN}{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}{RESET}")


# ── Shell helpers ────────────────────────────────────────────────────


def run(cmd, **kw):
    """Run a shell command quietly; return (returncode, stdout)."""
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)
    return r.returncode, r.stdout.strip()


def run_visible(cmd):
    """Run a shell command with output shown to user."""
    return subprocess.run(cmd, shell=True).returncode


def has_cmd(name):
    rc, _ = run(f"which {name}")
    return rc == 0


def ensure_brew_path():
    """Add /opt/homebrew/bin to PATH if it exists (Apple Silicon)."""
    brew_bin = "/opt/homebrew/bin"
    if os.path.isdir(brew_bin) and brew_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{brew_bin}:{os.environ['PATH']}"


# ── File operations ──────────────────────────────────────────────────

BACKUP_DIR = None


def _backup_dir():
    """Lazily create a timestamped backup directory."""
    global BACKUP_DIR
    if BACKUP_DIR is None:
        BACKUP_DIR = HOME / ".dotfiles_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
    return BACKUP_DIR


def symlink(src, dst, dry_run=False):
    """Create a symlink dst -> src.  Back up existing regular files."""
    src, dst = Path(src), Path(dst)
    if not src.exists():
        warn(f"source missing: {src}")
        return

    # Already correct
    if dst.is_symlink() and dst.resolve() == src.resolve():
        info(f"{dst}")
        return

    if dry_run:
        info(f"[dry-run] ln -sf {src} -> {dst}")
        return

    # Back up existing regular file (not symlink)
    if dst.exists() and not dst.is_symlink():
        bak = _backup_dir()
        bak.mkdir(parents=True, exist_ok=True)
        shutil.move(str(dst), str(bak / dst.name))
        info(f"backed up {dst} -> {bak}/{dst.name}")

    # Remove stale symlink
    if dst.is_symlink():
        dst.unlink()

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.symlink_to(src)
    info(f"ln  {dst} -> {src}")


def copy_file(src, dst, dry_run=False):
    src, dst = Path(src), Path(dst)
    if not src.exists():
        warn(f"source missing: {src}")
        return False
    if dry_run:
        info(f"[dry-run] cp {src} -> {dst}")
        return True
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    info(f"cp  {src} -> {dst}")
    return True


def copy_dir(src, dst, dry_run=False):
    src, dst = Path(src), Path(dst)
    if not src.exists():
        warn(f"source missing: {src}")
        return False
    n = sum(1 for _ in src.rglob("*") if _.is_file())
    if dry_run:
        info(f"[dry-run] cp -R {src}/ ({n} files) -> {dst}/")
        return True
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True, symlinks=True)
    info(f"cp -R {src}/ ({n} files) -> {dst}/")
    return True


def defaults_import(domain, plist, dry_run=False):
    plist = Path(plist)
    if not plist.exists():
        warn(f"plist missing: {plist}")
        return
    if dry_run:
        info(f"[dry-run] defaults import {domain} <- {plist.name}")
        return
    rc, _ = run(f'defaults import "{domain}" "{plist}"')
    if rc == 0:
        info(f"defaults import {domain}")
    else:
        error(f"defaults import failed: {domain}")


def confirm(msg, auto_yes=False):
    if auto_yes:
        return True
    answer = input(f"\n{YELLOW}[?]{RESET} {msg} [Y/n] ").strip().lower()
    return answer in ("", "y", "yes")


# ══════════════════════════════════════════════════════════════════════
#  Steps — each step is registered in STEPS dict
# ══════════════════════════════════════════════════════════════════════

STEPS = {}


def step(name, label, check=None):
    """Decorator to register a restore step.

    check: optional callable() -> (bool, str)
           True  = step has work to do (prompt user)
           False = already up-to-date (skip silently)
    """
    def decorator(func):
        STEPS[name] = (label, func, check)
        return func
    return decorator


# ── 0. Prerequisites ─────────────────────────────────────────────────


def _check_prereqs():
    if not IS_MACOS:
        # Linux: just verify git + gh present
        missing = [t for t in ("git", "gh") if not has_cmd(t)]
        if missing:
            return True, f"missing: {', '.join(missing)}"
        return False, "git and gh already installed"
    # macOS: need brew or xcode-select
    rc, _ = run("xcode-select -p")
    if rc != 0:
        return True, "Xcode CLT not installed"
    if not has_cmd("brew"):
        return True, "Homebrew not installed"
    return False, "Xcode CLT and Homebrew already installed"


@step("prereqs", "0. Prerequisites (git, gh)", check=_check_prereqs)
def step_prereqs(dry_run=False, **_):
    section("0. Prerequisites")

    if not IS_MACOS:
        info("Linux detected — skipping macOS prerequisites")
        return

    # Xcode Command Line Tools
    rc, _ = run("xcode-select -p")
    if rc != 0:
        info("Installing Xcode Command Line Tools ...")
        if not dry_run:
            run_visible("xcode-select --install")
    else:
        info("Xcode CLT already installed")

    # Homebrew
    if has_cmd("brew"):
        info("Homebrew already installed")
    else:
        info("Installing Homebrew ...")
        if not dry_run:
            run_visible(
                '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            )
            ensure_brew_path()

    ensure_brew_path()

    # git via brew (newer than system git)
    _, git_path = run("which git")
    if "/opt/homebrew" not in (git_path or ""):
        if not dry_run:
            run_visible("brew install git")
    else:
        info("git (brew) already installed")

    # GitHub CLI
    if has_cmd("gh"):
        info("GitHub CLI already installed")
    else:
        if not dry_run:
            run_visible("brew install gh")

    # Check gh auth
    if not dry_run:
        rc, _ = run("gh auth status 2>/dev/null")
        if rc != 0:
            warn("GitHub CLI not logged in — run 'gh auth login' later")


# ── 1. Homebrew / dnf packages ───────────────────────────────────────


def _check_brew():
    if IS_MACOS:
        brewfile = REPO / "macos" / "Brewfile"
        if not brewfile.exists():
            return False, "macos/Brewfile not found"
        rc, _ = run(f'brew bundle check --file="{brewfile}" --no-upgrade 2>/dev/null')
        if rc == 0:
            return False, "all Brewfile packages already installed"
        return True, "Brewfile has packages to install"
    else:
        pkg_file = REPO / "linux" / "packages.txt"
        if not pkg_file.exists():
            return False, "linux/packages.txt not found"
        pkgs = [l.strip() for l in pkg_file.read_text().splitlines()
                if l.strip() and not l.startswith("#")]
        rc, out = run(f"rpm -q {' '.join(pkgs)} 2>/dev/null | grep 'not installed'")
        if rc != 0:  # grep found nothing = all installed
            return False, "all packages already installed"
        return True, "packages to install"


@step("brew", "1. Install packages (Homebrew / dnf)", check=_check_brew)
def step_brew(dry_run=False, **_):
    section("1. Install Packages")

    if IS_MACOS:
        ensure_brew_path()
        brewfile = REPO / "macos" / "Brewfile"
        if not brewfile.exists():
            warn("macos/Brewfile not found")
            return
        lines = brewfile.read_text().splitlines()
        taps  = sum(1 for l in lines if l.startswith("tap"))
        brews = sum(1 for l in lines if l.startswith("brew"))
        casks = sum(1 for l in lines if l.startswith("cask"))
        info(f"Brewfile: {taps} taps, {brews} formulas, {casks} casks")
        if dry_run:
            info("[dry-run] brew bundle install")
            return
        run_visible(f'brew bundle install --file="{brewfile}"')
    else:
        pkg_file = REPO / "linux" / "packages.txt"
        if not pkg_file.exists():
            warn("linux/packages.txt not found")
            return
        pkgs = [l.strip() for l in pkg_file.read_text().splitlines()
                if l.strip() and not l.startswith("#")]
        info(f"{len(pkgs)} packages to install")
        if dry_run:
            info("[dry-run] dnf install ...")
            return
        run_visible(f"sudo dnf install -y {' '.join(pkgs)}")


# ── 2. Config files (symlinks) ───────────────────────────────────────


def _check_configs():
    shared = REPO / "shared"
    targets = [
        (shared / f, HOME / f)
        for f in [".bash_profile", ".bashrc", ".shell_common",
                  ".zprofile", ".zshenv", ".zshrc",
                  ".hushlogin", ".gitconfig"]
    ]
    targets += [
        (shared / "starship.toml", HOME / ".config" / "starship.toml"),
        (shared / "bin" / "theme", HOME / ".local" / "bin" / "theme"),
    ]
    if IS_MACOS:
        targets += [
            (REPO / "macos" / "ghostty" / "config", HOME / ".config" / "ghostty" / "config"),
            (REPO / "macos" / ".aerospace.toml", HOME / ".aerospace.toml"),
        ]
    else:
        targets += [
            (REPO / "linux" / "kitty.conf", HOME / ".config" / "kitty" / "kitty.conf"),
        ]

    missing = [
        str(dst) for src, dst in targets
        if src.exists() and not (dst.is_symlink() and dst.resolve() == src.resolve())
    ]
    if missing:
        return True, f"{len(missing)} symlink(s) need updating"
    return False, "all symlinks already up-to-date"


@step("configs", "2. Config files (symlinks)", check=_check_configs)
def step_configs(dry_run=False, **_):
    section("2. Config Files (symlinks)")

    shared = REPO / "shared"

    # --- Shell dotfiles ---
    shell_files = [
        ".bash_profile", ".bashrc", ".shell_common",
        ".zprofile", ".zshenv", ".zshrc",
        ".hushlogin", ".gitconfig",
    ]
    for f in shell_files:
        symlink(shared / f, HOME / f, dry_run)

    # --- Scripts (cross-platform) ---
    symlink(shared / "bin" / "theme", HOME / ".local" / "bin" / "theme", dry_run)

    # --- Starship prompt ---
    symlink(shared / "starship.toml", HOME / ".config" / "starship.toml", dry_run)

    # --- Catppuccin zsh colours ---
    for f in ["mocha.zsh", "latte.zsh"]:
        symlink(shared / "zsh" / "catppuccin" / f,
                HOME / ".zsh" / "catppuccin" / f, dry_run)

    # --- Neovim ---
    for f in ["init.lua", "lazy-lock.json"]:
        symlink(shared / "nvim" / f, HOME / ".config" / "nvim" / f, dry_run)

    # --- Platform-specific ---
    if IS_MACOS:
        symlink(REPO / "macos" / "ghostty" / "config",
                HOME / ".config" / "ghostty" / "config", dry_run)
        symlink(REPO / "macos" / ".aerospace.toml",
                HOME / ".aerospace.toml", dry_run)
    else:
        symlink(REPO / "linux" / "kitty.conf",
                HOME / ".config" / "kitty" / "kitty.conf", dry_run)
        symlink(REPO / "linux" / "bin" / "toggle_app",
                HOME / ".local" / "bin" / "toggle_app", dry_run)

    # --- Theme mode (don't overwrite existing preference) ---
    theme_file = HOME / ".theme_mode"
    if not theme_file.exists():
        if not dry_run:
            theme_file.write_text("dark")
        info("new ~/.theme_mode (dark)")
    else:
        info(f"~/.theme_mode ({theme_file.read_text().strip()})")

    # --- Secrets template (copy, never symlink) ---
    private = HOME / ".bashrc_private"
    example = shared / ".bashrc_private.example"
    if not private.exists() and example.exists():
        if not dry_run:
            shutil.copy2(example, private)
            private.chmod(0o600)
        info("new ~/.bashrc_private (template — edit with real values)")
    elif private.exists():
        info("~/.bashrc_private exists, skipping template")


# ── 3. Oh My Zsh + plugins ──────────────────────────────────────────


def _check_omz():
    omz_dir = HOME / ".oh-my-zsh"
    if not omz_dir.exists():
        return True, "Oh My Zsh not installed"
    plugins_file = REPO / "macos" / "omz-custom" / "plugins.txt"
    if not plugins_file.exists():
        return False, "Oh My Zsh installed, no plugins.txt"
    custom_dir = omz_dir / "custom" / "plugins"
    missing = []
    for line in plugins_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) == 2:
            name = parts[0]
            if not (custom_dir / name).exists():
                missing.append(name)
    if missing:
        return True, f"{len(missing)} plugin(s) not installed: {', '.join(missing)}"
    return False, "Oh My Zsh and all plugins already installed"


@step("omz", "3. Oh My Zsh + custom plugins", check=_check_omz)
def step_omz(dry_run=False, **_):
    section("3. Oh My Zsh")

    omz_dir = HOME / ".oh-my-zsh"

    # Install Oh My Zsh
    if not omz_dir.exists():
        info("Installing Oh My Zsh ...")
        if not dry_run:
            run_visible(
                'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended'
            )
    else:
        info("Oh My Zsh already installed")

    # Install custom plugins from plugins.txt
    plugins_file = REPO / "macos" / "omz-custom" / "plugins.txt"
    if not plugins_file.exists():
        warn("omz-custom/plugins.txt not found")
        return

    custom_dir = omz_dir / "custom" / "plugins"
    seen = set()
    for line in plugins_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        name, url = parts
        if name in seen:          # skip duplicates
            continue
        seen.add(name)

        target = custom_dir / name
        if target.exists():
            info(f"plugin exists: {name}")
            continue
        if dry_run:
            info(f"[dry-run] git clone {name}")
            continue
        rc = run_visible(f'git clone "{url}" "{target}"')
        if rc == 0:
            info(f"installed plugin: {name}")
        else:
            error(f"plugin failed: {name}")


# ── 4. macOS defaults ────────────────────────────────────────────────


def _check_defaults():
    if not IS_MACOS:
        dconf_file = REPO / "linux" / "gnome-terminal-profiles.dconf"
        if not has_cmd("dconf") or not dconf_file.exists():
            return False, "dconf not available or no profile file"
        return True, "GNOME terminal profiles to load"
    defaults_dir = REPO / "macos" / "defaults"
    if not defaults_dir.exists():
        return False, "macos/defaults/ not found"
    return True, "macOS defaults to apply (no efficient pre-check)"


@step("defaults", "4. macOS defaults (system preferences)", check=_check_defaults)
def step_defaults(dry_run=False, **_):
    section("4. macOS Defaults")

    if not IS_MACOS:
        # Linux: load GNOME terminal profiles
        dconf_file = REPO / "linux" / "gnome-terminal-profiles.dconf"
        if has_cmd("dconf") and dconf_file.exists():
            if dry_run:
                info("[dry-run] dconf load terminal profiles")
            else:
                run(f'dconf load /org/gnome/terminal/legacy/profiles:/ < "{dconf_file}"')
                info("loaded GNOME terminal profiles")
        else:
            warn("dconf not found or no profile file")
        return

    # --- Import plist files ---
    defaults_dir = REPO / "macos" / "defaults"
    if not defaults_dir.exists():
        warn("macos/defaults/ not found")
        return

    # Map: macOS domain -> plist filename (without .plist)
    domain_map = {
        "com.apple.dock":              "dock",
        "com.apple.finder":            "finder",
        "NSGlobalDomain":              "NSGlobalDomain",
        "com.apple.screencapture":     "screencapture",
        "com.apple.desktopservices":   "desktopservices",
        "com.apple.universalaccess":   "universalaccess",
        "com.apple.AppleMultitouchTrackpad":                    "trackpad",
        "com.apple.driver.AppleBluetoothMultitouch.trackpad":   "trackpad_bt",
        "com.apple.symbolichotkeys":   "symbolichotkeys",
        "com.apple.TextEdit":          "com.apple.TextEdit",
        "abnerworks.Typora":           "abnerworks.Typora",
        "bobko.aerospace":             "bobko.aerospace",
        "com.anthropic.claudefordesktop": "com.anthropic.claudefordesktop",
        "com.knollsoft.Hyperkey":      "com.knollsoft.Hyperkey",
        "org.herf.Flux":               "org.herf.Flux",
    }

    for domain, filename in domain_map.items():
        defaults_import(domain, defaults_dir / f"{filename}.plist", dry_run)

    # --- Hardcoded writes (values that plist import may not cover) ---
    extra_cmds = [
        # Screenshot settings
        'defaults write com.apple.screencapture disable-shadow -bool true',
        'defaults write com.apple.screencapture show-thumbnail -bool false',
        'defaults write com.apple.screencapture type jpg',
        'defaults write com.apple.screencapture name "sc"',
        'defaults write com.apple.screencapture include-date -bool false',
        f'defaults write com.apple.screencapture location -string "{HOME}/Desktop"',
        # Disable .DS_Store on network/USB volumes
        'defaults write com.apple.desktopservices DSDontWriteNetworkStores -bool true',
        'defaults write com.apple.desktopservices DSDontWriteUSBStores -bool true',
        # Click desktop to show desktop: only in Stage Manager
        'defaults write com.apple.WindowManager EnableStandardClickToShowDesktop -bool false',
    ]
    for cmd in extra_cmds:
        if dry_run:
            info(f"[dry-run] {cmd.split('write ')[1].split()[0]}")
        else:
            run(cmd)

    if not dry_run:
        info("screenshot: no shadow, no thumbnail, jpg, prefix 'sc', ~/Desktop")
        info("desktopservices: no .DS_Store on network/USB")
        info("WindowManager: click-to-show-desktop only in Stage Manager")

    # --- Restart affected services ---
    if not dry_run:
        info("Restarting Dock, Finder, SystemUIServer ...")
        for svc in ["Dock", "Finder", "SystemUIServer"]:
            run(f"killall {svc}")
        info("UI services restarted")


# ── 5. Services (Automator Quick Actions) ────────────────────────────


def _check_services():
    if not IS_MACOS:
        return False, "Services are macOS-only"
    src = REPO / "macos" / "services"
    if not src.exists():
        return False, "macos/services/ not found"
    dst = HOME / "Library" / "Services"
    items = [i for i in sorted(src.iterdir()) if not i.name.startswith(".")]
    missing = [i for i in items if not (dst / i.name).exists()]
    if missing:
        return True, f"{len(missing)} service(s) not installed"
    return False, "all services already installed"


@step("services", "5. Services (Automator workflows)", check=_check_services)
def step_services(dry_run=False, **_):
    section("5. Services")

    if not IS_MACOS:
        warn("Services are macOS-only")
        return

    src = REPO / "macos" / "services"
    dst = HOME / "Library" / "Services"
    if not src.exists():
        warn("macos/services/ not found")
        return

    items = [i for i in sorted(src.iterdir()) if not i.name.startswith(".")]
    if dry_run:
        info(f"[dry-run] restore {len(items)} services")
        return

    dst.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in items:
        target = dst / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
        count += 1
    info(f"restored {count} services -> ~/Library/Services/")


# ── 6. Fonts ──────────────────────────────────────────────────────────


def _check_fonts():
    if not IS_MACOS:
        return False, "font install via brew is macOS-only"
    ensure_brew_path()
    font_casks = ["font-maple-mono-nf", "font-lxgw-wenkai-mono"]
    missing = [c for c in font_casks
               if run(f"brew list --cask {c} 2>/dev/null")[0] != 0]
    if missing:
        return True, f"{len(missing)} font(s) not installed"
    return False, "all fonts already installed"


@step("fonts", "6. Fonts (Nerd Font + CJK)", check=_check_fonts)
def step_fonts(dry_run=False, **_):
    section("6. Fonts")

    if not IS_MACOS:
        warn("font install via brew is macOS-only")
        return

    ensure_brew_path()
    font_casks = ["font-maple-mono-nf", "font-lxgw-wenkai-mono"]
    for cask in font_casks:
        rc, _ = run(f"brew list --cask {cask} 2>/dev/null")
        if rc == 0:
            info(f"{cask} already installed")
        else:
            if dry_run:
                info(f"[dry-run] brew install --cask {cask}")
            else:
                run_visible(f"brew install --cask {cask}")


# ── 7. Hide home folders ─────────────────────────────────────────────


def _check_hide_folders():
    if not IS_MACOS:
        return False, "chflags hidden is macOS-only"
    folders = ["Applications", "Library", "Movies", "Music", "Pictures", "Public"]
    visible = []
    for name in folders:
        folder = HOME / name
        if not folder.exists():
            continue
        rc, flags = run(f'GetFileInfo -aa "{folder}" 2>/dev/null')
        # GetFileInfo -aa returns "1" if hidden flag set
        if rc != 0 or flags.strip() != "1":
            visible.append(name)
    if visible:
        return True, f"{len(visible)} folder(s) not yet hidden"
    return False, "all folders already hidden"


@step("hidefolders", "7. Hide unused home folders", check=_check_hide_folders)
def step_hide_folders(dry_run=False, **_):
    section("7. Hide Home Folders")

    if not IS_MACOS:
        warn("chflags hidden is macOS-only")
        return

    folders = [
        "Applications", "Library", "Movies",
        "Music", "Pictures", "Public",
    ]
    count = 0
    for name in folders:
        folder = HOME / name
        if not folder.exists():
            continue
        if dry_run:
            info(f"[dry-run] chflags hidden ~/{name}")
            count += 1
            continue
        rc, _ = run(f'chflags hidden "{folder}"')
        if rc == 0:
            count += 1
        else:
            error(f"chflags hidden failed: ~/{name}")
    info(f"hidden {count} folders")


# ── 8. Ollama models ─────────────────────────────────────────────────


def _check_ollama():
    models_file = REPO / "ollama_models.txt"
    if not models_file.exists():
        return False, "ollama_models.txt not found"
    if not has_cmd("ollama"):
        return False, "ollama not installed"
    rc, out = run("ollama list 2>/dev/null")
    if rc != 0:
        return True, "ollama not running (start it first)"
    installed = set(out.splitlines()[1:])  # skip header
    installed_names = {l.split()[0] for l in installed if l.strip()}
    lines = models_file.read_text().splitlines()
    needed = [l.split()[0] for l in lines[1:] if l.split()]
    missing = [m for m in needed if m not in installed_names]
    if missing:
        return True, f"{len(missing)} model(s) not pulled"
    return False, "all Ollama models already present"


@step("ollama", "8. Ollama models (optional, slow)", check=_check_ollama)
def step_ollama(dry_run=False, **_):
    section("8. Ollama Models")

    models_file = REPO / "ollama_models.txt"
    if not models_file.exists():
        warn("ollama_models.txt not found")
        return

    if not has_cmd("ollama"):
        warn("ollama not installed — skipping")
        return

    # Parse model names from `ollama list` output format
    lines = models_file.read_text().splitlines()
    models = []
    for line in lines[1:]:          # skip header
        parts = line.split()
        if parts:
            models.append(parts[0])

    if not models:
        warn("no models to pull")
        return

    info(f"{len(models)} models to pull:")
    for m in models:
        print(f"      - {m}")

    if dry_run:
        info("[dry-run] ollama pull ...")
        return

    # Check ollama service is running
    rc, _ = run("ollama list 2>/dev/null")
    if rc != 0:
        warn("ollama not running — start Ollama.app first, then re-run with --only ollama")
        return

    for m in models:
        info(f"pulling {m} ...")
        rc = run_visible(f"ollama pull {m}")
        if rc == 0:
            info(f"pulled: {m}")
        else:
            error(f"pull failed: {m}")


# ── 9. Chinese CLI help ──────────────────────────────────────────────


def _check_clihelp():
    if has_cmd("tldr"):
        return False, "tldr already installed"
    return True, "tldr not installed"


@step("clihelp", "9. Chinese CLI help (tldr)", check=_check_clihelp)
def step_cli_help(dry_run=False, **_):
    section("9. Chinese CLI Help")

    if has_cmd("tldr"):
        info("tldr already installed")
    elif has_cmd("pip3"):
        if dry_run:
            info("[dry-run] pip3 install tldr")
        else:
            run_visible("pip3 install --user tldr")
    else:
        warn("pip3 not found — install tldr manually")


# ══════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════


def print_manual_steps():
    """Post-install manual steps that can't be automated."""
    print(f"\n{BOLD}{YELLOW}Manual steps remaining:{RESET}")
    print("  1. Copy ~/.ssh/ and ~/.bashrc_private from encrypted backup")
    print("  2. Copy ~/d/vault.sparsebundle from encrypted backup, then vault-open")
    print("  3. Install Claude Code: curl -fsSL https://claude.ai/install.sh | bash")
    print("  4. Login: Apple ID / iCloud")
    print("  5. Login: Brave Browser sync")
    print("  6. Configure input method (if applicable)")
    print("  7. Open a new terminal or run: exec zsh")

    if IS_MACOS:
        print(f"\n{BOLD}{YELLOW}macOS settings that require manual confirmation:{RESET}")
        print("  Accessibility (System Settings > Accessibility > Display):")
        print("    - Reduce transparency")
        print("    - Reduce motion")
        print("    - Increase contrast")
        print("  Privacy & Security:")
        print("    - Accessibility permissions (Terminal, AeroSpace, HyperKey)")
        print("    - Full Disk Access")
        print("    - Input Monitoring")
        print("  Other:")
        print("    - Night Shift / True Tone (Displays)")
        print("    - Default browser (Desktop & Dock)")
        print("    - Lock screen / Touch ID")


def main():
    parser = argparse.ArgumentParser(
        description="Restore dotfiles & system configs from this repo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
steps: {', '.join(STEPS.keys())}

examples:
  python3 install.py                     interactive restore
  python3 install.py --yes               full restore, no prompts
  python3 install.py --only configs omz  only configs + Oh My Zsh
  python3 install.py --dry-run           preview all changes
""",
    )
    parser.add_argument("--dry-run", action="store_true", help="preview only")
    parser.add_argument("--yes", "-y", action="store_true", help="skip confirmations")
    parser.add_argument(
        "--only", nargs="+", choices=list(STEPS.keys()),
        help="run only these steps",
    )
    args = parser.parse_args()

    os_label = "macOS" if IS_MACOS else "Linux"
    print(f"\n{BOLD}{'=' * 60}")
    print(f"  oh-my-dotfiles — install ({os_label})")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Source: {REPO}")
    if args.dry_run:
        print(f"  {YELLOW}*** DRY-RUN MODE ***{RESET}")
    print(f"{'=' * 60}{RESET}")

    # Default: run all steps except ollama (slow, needs manual start)
    if args.only:
        steps_to_run = args.only
    else:
        steps_to_run = [s for s in STEPS if s != "ollama"]

    for name in steps_to_run:
        label, func, check_func = STEPS[name]

        # Pre-check: skip steps where nothing needs to be done
        if check_func and not args.dry_run:
            needs, reason = check_func()
            if not needs:
                warn(f"skip [{label}]: {reason}")
                continue

        if not args.dry_run and not args.yes:
            reason_hint = f" ({reason})" if check_func else ""
            if not confirm(f"Run {label}?{reason_hint}"):
                warn(f"skipped: {label}")
                continue
        func(dry_run=args.dry_run)

    # Summary
    print(f"\n{BOLD}{GREEN}{'=' * 60}")
    print(f"  Install complete!")
    print(f"{'=' * 60}{RESET}")

    bak = _backup_dir()
    if bak and bak.exists():
        print(f"\n  Old files backed up to: {bak}")

    print_manual_steps()


if __name__ == "__main__":
    main()
