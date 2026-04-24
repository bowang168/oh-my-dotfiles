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
import tempfile
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


def _has_ssh_keys():
    """True if ~/.ssh/ contains at least one common private key."""
    ssh_dir = HOME / ".ssh"
    if not ssh_dir.is_dir():
        return False
    return any((ssh_dir / k).exists() for k in
               ("id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"))


def _gitconfig_rewrites_github_to_ssh():
    """True if ~/.gitconfig has url.git@github.com:.insteadOf = https://github.com/."""
    rc, out = run('git config --global --get-all "url.git@github.com:.insteadOf"')
    return rc == 0 and "https://github.com" in out


def _git_clone_env():
    """Env dict for git clone. Bypasses ~/.gitconfig `insteadOf` HTTPS→SSH
    rewrites when ~/.ssh/ has no keys, so HTTPS clones succeed on a fresh box."""
    env = os.environ.copy()
    if not _has_ssh_keys() and _gitconfig_rewrites_github_to_ssh():
        empty = Path("/tmp/.oh-my-dotfiles-empty-gitconfig")
        empty.touch()
        env["GIT_CONFIG_GLOBAL"] = str(empty)
        env["GIT_CONFIG_SYSTEM"] = "/dev/null"
    return env


def git_clone(url, target, dry_run=False):
    """Clone a repo, transparently bypassing the gitconfig insteadOf rewrite
    when SSH keys are unavailable. Returns (returncode, message)."""
    target = Path(target)
    if target.exists():
        return 0, f"exists: {target}"
    if dry_run:
        return 0, f"[dry-run] git clone {url} -> {target}"
    env = _git_clone_env()
    r = subprocess.run(["git", "clone", url, str(target)], env=env)
    return r.returncode, f"cloned {url} -> {target}" if r.returncode == 0 else f"clone failed: {url}"


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


def _ol_major_version():
    """Return Oracle Linux major version ('9', '10', ...) or None if not OL."""
    try:
        content = Path("/etc/os-release").read_text()
    except OSError:
        return None
    kv = {}
    for line in content.splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip().strip('"')
    if kv.get("ID") != "ol":
        return None
    ver = kv.get("VERSION_ID", "")
    return ver.split(".")[0] if ver else None


def _epel_enabled():
    """True if an enabled repo looks like EPEL (Oracle's developer_EPEL or generic epel)."""
    rc, out = run("dnf repolist 2>/dev/null")
    if rc != 0:
        return False
    low = out.lower()
    return "_developer_epel" in low or "\nepel " in low or out.startswith("epel ")


def _find_repos_by_suffix(*suffixes):
    """Return enabled-or-disabled repo ids whose name ends with any suffix."""
    rc, out = run("dnf repolist --all 2>/dev/null")
    if rc != 0:
        return []
    found = []
    for line in out.splitlines():
        parts = line.split()
        if not parts:
            continue
        repo_id = parts[0]
        if any(repo_id.endswith(s) for s in suffixes):
            found.append(repo_id)
    return found


def _check_prereqs():
    if not IS_MACOS:
        reasons = []
        if _ol_major_version() and not _epel_enabled():
            reasons.append("EPEL/CRB not enabled")
        missing = [t for t in ("git", "gh") if not has_cmd(t)]
        if missing:
            reasons.append(f"missing: {', '.join(missing)}")
        if reasons:
            return True, "; ".join(reasons)
        return False, "EPEL enabled, git/gh present"
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
        ol_major = _ol_major_version()
        if not ol_major:
            info("Linux (non-Oracle) — skipping EPEL setup")
            return
        if _epel_enabled():
            info(f"EPEL/CRB already enabled (OL{ol_major})")
            return
        info(f"Enabling EPEL + CodeReady Builder for OL{ol_major} ...")
        if dry_run:
            info(f"[dry-run] sudo dnf install -y oracle-epel-release-el{ol_major}")
            info("[dry-run] sudo dnf config-manager --enable *_developer_EPEL *_codeready_builder")
            return
        rc = run_visible(f"sudo dnf install -y oracle-epel-release-el{ol_major}")
        if rc != 0:
            error(f"failed to install oracle-epel-release-el{ol_major}")
            return
        repos = _find_repos_by_suffix("_developer_EPEL", "_codeready_builder")
        if not repos:
            warn("no EPEL/CRB repo ids found to enable")
            return
        rc = run_visible(f"sudo dnf config-manager --enable {' '.join(repos)}")
        if rc == 0:
            info(f"enabled: {', '.join(repos)}")
        else:
            error(f"failed to enable repos: {', '.join(repos)}")
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
        (shared / "yazi" / "yazi.toml", HOME / ".config" / "yazi" / "yazi.toml"),
        (shared / "yazi" / "package.toml", HOME / ".config" / "yazi" / "package.toml"),
        (shared / "yazi" / "plugins" / "glow.yazi",
         HOME / ".config" / "yazi" / "plugins" / "glow.yazi"),
    ]
    if IS_MACOS:
        targets += [
            (REPO / "macos" / "ghostty" / "config", HOME / ".config" / "ghostty" / "config"),
            (REPO / "macos" / ".aerospace.toml", HOME / ".aerospace.toml"),
        ]
    else:
        targets += [
            (REPO / "linux" / "kitty.conf", HOME / ".config" / "kitty" / "kitty.conf"),
            (REPO / "linux" / "bin" / "obsidian", HOME / ".local" / "bin" / "obsidian"),
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

    # --- Yazi (file manager) config + pinned plugins ---
    symlink(shared / "yazi" / "yazi.toml",
            HOME / ".config" / "yazi" / "yazi.toml", dry_run)
    symlink(shared / "yazi" / "package.toml",
            HOME / ".config" / "yazi" / "package.toml", dry_run)
    symlink(shared / "yazi" / "plugins" / "glow.yazi",
            HOME / ".config" / "yazi" / "plugins" / "glow.yazi", dry_run)

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
        symlink(REPO / "linux" / "bin" / "obsidian",
                HOME / ".local" / "bin" / "obsidian", dry_run)

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
            env = _git_clone_env()
            subprocess.run(
                'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended --keep-zshrc',
                shell=True, env=env,
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
        # plugins.txt uses git@github.com: URLs; rewrite to HTTPS so the
        # SSH-less override in git_clone() can take effect.
        clone_url = url
        if clone_url.startswith("git@github.com:"):
            clone_url = "https://github.com/" + clone_url[len("git@github.com:"):]
        rc, msg = git_clone(clone_url, target, dry_run=dry_run)
        if rc == 0:
            info(f"installed plugin: {name}")
        else:
            error(f"plugin failed: {name} ({msg})")


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


FONTS = [
    {
        "name": "Maple Mono NF",
        "url": "https://github.com/subframe7536/maple-font/releases/latest/download/MapleMono-NF.zip",
        "dir": "MapleMono-NF",
    },
]


def _font_target_dir():
    return HOME / "Library" / "Fonts" if IS_MACOS else HOME / ".local" / "share" / "fonts"


def _font_installed(font):
    target = _font_target_dir() / font["dir"]
    return target.exists() and any(target.glob("*.ttf"))


def _check_fonts():
    missing = [f["name"] for f in FONTS if not _font_installed(f)]
    if missing:
        return True, f"missing: {', '.join(missing)}"
    return False, "all fonts already installed"


@step("fonts", "6. Fonts", check=_check_fonts)
def step_fonts(dry_run=False, **_):
    section("6. Fonts")

    target_dir = _font_target_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    installed_any = False
    for font in FONTS:
        if _font_installed(font):
            info(f'{font["name"]} already installed')
            continue
        dest = target_dir / font["dir"]
        if dry_run:
            info(f'[dry-run] download {font["name"]} -> {dest}')
            continue
        info(f'installing {font["name"]} -> {dest}')
        rc = run_visible(
            f'tmp=$(mktemp -d) && '
            f'curl -fsSL -o "$tmp/f.zip" "{font["url"]}" && '
            f'mkdir -p "{dest}" && '
            f'unzip -oq "$tmp/f.zip" -d "{dest}" && '
            f'rm -rf "$tmp"'
        )
        if rc != 0:
            error(f'failed to install {font["name"]}')
        else:
            installed_any = True

    if installed_any and not IS_MACOS and has_cmd("fc-cache"):
        run_visible(f'fc-cache -f "{target_dir}"')
        info("fc-cache refreshed")


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


# ── 9. keyd (CapsLock → Esc/Super on Linux) ─────────────────────────


KEYD_SRC_DIR = Path("/tmp/keyd-build")
KEYD_CONFIG = Path("/etc/keyd/default.conf")


def _check_keyd():
    if IS_MACOS:
        return False, "keyd is Linux-only (use Hyperkey on macOS)"
    src_conf = REPO / "linux" / "keyd" / "default.conf"
    if not src_conf.exists():
        return False, "linux/keyd/default.conf not found"

    reasons = []
    if not has_cmd("keyd"):
        reasons.append("keyd binary missing")
    if not KEYD_CONFIG.exists():
        reasons.append(f"{KEYD_CONFIG} missing")
    elif KEYD_CONFIG.read_text() != src_conf.read_text():
        reasons.append(f"{KEYD_CONFIG} differs from repo")
    rc, _ = run("systemctl is-active keyd")
    if rc != 0:
        reasons.append("keyd.service not active")
    if reasons:
        return True, "; ".join(reasons)
    return False, "keyd installed, config matches, service active"


@step("keyd", "9. keyd (CapsLock → Esc tap / Super hold)", check=_check_keyd)
def step_keyd(dry_run=False, **_):
    section("9. keyd")

    if IS_MACOS:
        warn("keyd is Linux-only")
        return

    src_conf = REPO / "linux" / "keyd" / "default.conf"
    if not src_conf.exists():
        warn("linux/keyd/default.conf not found")
        return

    # 1. Build + install keyd if missing
    if not has_cmd("keyd"):
        if dry_run:
            info(f"[dry-run] clone rvaiya/keyd -> {KEYD_SRC_DIR}, make, sudo make install")
        else:
            if KEYD_SRC_DIR.exists():
                shutil.rmtree(KEYD_SRC_DIR)
            rc, msg = git_clone("https://github.com/rvaiya/keyd.git", KEYD_SRC_DIR)
            if rc != 0:
                error(msg)
                return
            rc = run_visible(f'make -C "{KEYD_SRC_DIR}" && sudo make -C "{KEYD_SRC_DIR}" install')
            if rc != 0:
                error("keyd build/install failed")
                return
            info("keyd built and installed")
    else:
        info("keyd already installed")

    # 2. Deploy config
    if dry_run:
        info(f"[dry-run] sudo install -Dm644 {src_conf} {KEYD_CONFIG}")
    else:
        rc = run_visible(f'sudo install -Dm644 "{src_conf}" "{KEYD_CONFIG}"')
        if rc != 0:
            error(f"failed to deploy {KEYD_CONFIG}")
            return
        info(f"{KEYD_CONFIG} deployed")

    # 3. Enable + start/reload service
    if dry_run:
        info("[dry-run] sudo systemctl enable --now keyd && sudo keyd reload")
    else:
        run_visible("sudo systemctl enable --now keyd")
        run("sudo keyd reload")
        info("keyd.service enabled + reloaded")


# ── 10. Yazi binary (Linux only; macOS uses Homebrew) ───────────────


YAZI_URL = (
    "https://github.com/sxyazi/yazi/releases/latest/download/"
    "yazi-x86_64-unknown-linux-gnu.zip"
)


def _check_yazi():
    if IS_MACOS:
        return False, "yazi on macOS is installed via Homebrew (Brewfile)"
    missing = [b for b in ("yazi", "ya") if not (HOME / ".local" / "bin" / b).exists()
               and not has_cmd(b)]
    if missing:
        return True, f"missing binaries: {', '.join(missing)}"
    return False, "yazi + ya already installed"


@step("yazi", "10. Yazi file manager (Linux binary)", check=_check_yazi)
def step_yazi(dry_run=False, **_):
    section("10. Yazi (Linux binary)")

    if IS_MACOS:
        warn("yazi on macOS comes from Homebrew — see Brewfile")
        return

    bin_dir = HOME / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    already = all((bin_dir / b).exists() or has_cmd(b) for b in ("yazi", "ya"))
    if already:
        info("yazi + ya already present")
        return

    if dry_run:
        info(f"[dry-run] curl -L {YAZI_URL} | unzip -> {bin_dir}/{{yazi,ya}}")
        return

    if not has_cmd("unzip"):
        error("unzip not found — install it (sudo dnf install unzip)")
        return

    with tempfile.TemporaryDirectory() as td:
        zip_path = Path(td) / "yazi.zip"
        rc = run_visible(f'curl -fL --output "{zip_path}" "{YAZI_URL}"')
        if rc != 0 or not zip_path.exists():
            error("yazi download failed")
            return
        rc = run_visible(f'unzip -q "{zip_path}" -d "{td}"')
        if rc != 0:
            error("yazi unzip failed")
            return
        installed = []
        for name in ("yazi", "ya"):
            matches = list(Path(td).rglob(name))
            matches = [m for m in matches if m.is_file() and os.access(m, os.X_OK)]
            if not matches:
                error(f"{name} not found in archive")
                continue
            dst = bin_dir / name
            shutil.copy2(matches[0], dst)
            dst.chmod(0o755)
            installed.append(name)
        if installed:
            info(f"installed to {bin_dir}: {', '.join(installed)}")


# ── 11. Flatpak apps (Linux only) ───────────────────────────────────


def _flatpak_apps():
    """Read app-ids from linux/flatpaks.txt, skipping blanks + comments."""
    pkg_file = REPO / "linux" / "flatpaks.txt"
    if not pkg_file.exists():
        return []
    return [l.strip() for l in pkg_file.read_text().splitlines()
            if l.strip() and not l.startswith("#")]


def _check_flatpak():
    if IS_MACOS:
        return False, "flatpak is Linux-only (macOS uses Homebrew casks)"
    apps = _flatpak_apps()
    if not apps:
        return False, "linux/flatpaks.txt empty or missing"
    reasons = []
    if not has_cmd("flatpak"):
        reasons.append("flatpak binary missing")
        return True, "; ".join(reasons)
    rc, _ = run("flatpak remotes --user | grep -q '^flathub'")
    if rc != 0:
        reasons.append("flathub remote missing")
    rc, out = run("flatpak list --user --app --columns=application")
    installed = set(out.splitlines()) if rc == 0 else set()
    missing = [a for a in apps if a not in installed]
    if missing:
        reasons.append(f"{len(missing)} app(s) to install")
    if reasons:
        return True, "; ".join(reasons)
    return False, f"flathub + {len(apps)} app(s) already installed"


@step("flatpak", "11. Flatpak apps (Linux only)", check=_check_flatpak)
def step_flatpak(dry_run=False, **_):
    section("11. Flatpak Apps")

    if IS_MACOS:
        warn("flatpak is Linux-only")
        return

    if not has_cmd("flatpak"):
        warn("flatpak binary missing — run the `brew` step first (installs flatpak via dnf)")
        return

    apps = _flatpak_apps()
    if not apps:
        warn("linux/flatpaks.txt empty or missing")
        return

    # 1. Ensure flathub remote (user-level install, no sudo needed)
    rc, _ = run("flatpak remotes --user | grep -q '^flathub'")
    if rc != 0:
        if dry_run:
            info("[dry-run] flatpak remote-add --user flathub https://dl.flathub.org/repo/flathub.flatpakrepo")
        else:
            rc = run_visible(
                "flatpak remote-add --if-not-exists --user flathub "
                "https://dl.flathub.org/repo/flathub.flatpakrepo"
            )
            if rc != 0:
                error("failed to add flathub remote")
                return
            info("flathub remote added")
    else:
        info("flathub remote present")

    # 2. Install any missing apps
    rc, out = run("flatpak list --user --app --columns=application")
    installed = set(out.splitlines()) if rc == 0 else set()
    missing = [a for a in apps if a not in installed]
    if not missing:
        info(f"all {len(apps)} app(s) already installed")
        return
    info(f"{len(missing)} app(s) to install: {', '.join(missing)}")
    if dry_run:
        info(f"[dry-run] flatpak install --user -y flathub {' '.join(missing)}")
        return
    rc = run_visible(f"flatpak install --user -y flathub {' '.join(missing)}")
    if rc != 0:
        error("flatpak install failed")


# ── 12. Chinese CLI help ─────────────────────────────────────────────


def _check_clihelp():
    if has_cmd("tldr"):
        return False, "tldr already installed"
    return True, "tldr not installed"


@step("clihelp", "12. Chinese CLI help (tldr)", check=_check_clihelp)
def step_cli_help(dry_run=False, **_):
    section("12. Chinese CLI Help")

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

    if not _has_ssh_keys() and _gitconfig_rewrites_github_to_ssh():
        print(f"\n{YELLOW}Note:{RESET} ~/.ssh/ has no keys but .gitconfig rewrites "
              f"github HTTPS → SSH.")
        print(f"      git clones in this run will bypass the rewrite via "
              f"GIT_CONFIG_GLOBAL override.")

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
