#!/usr/bin/env python3
"""
backup.py — Snapshot current system configs into this repo.

Detects macOS vs Linux and backs up shared + platform-specific configs.
Run this before committing to keep the repo up to date with your system.

Usage:
    python3 backup.py              # full backup
    python3 backup.py --dry-run    # preview only, no changes
    python3 backup.py --only brew defaults  # specific steps only

After running:
    cd ~/g/oh-my-dotfiles && git diff   # review changes
    git add -A && git commit -m 'backup' && git push
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


def has_cmd(name):
    rc, _ = run(f"which {name}")
    return rc == 0


# ── File operations ──────────────────────────────────────────────────


def copy_file(src, dst, dry_run=False):
    """Copy a single file from system to repo.  Resolves symlinks."""
    src, dst = Path(src), Path(dst)
    if not src.exists():
        warn(f"source missing: {src}")
        return False

    # If src is a symlink pointing INTO this repo, skip (already tracked)
    if src.is_symlink():
        target = str(src.resolve())
        if str(REPO) in target:
            info(f"{dst.relative_to(REPO)}  (symlink to repo)")
            return True
        src = src.resolve()     # follow symlink to external target

    if dry_run:
        info(f"[dry-run] {src} -> {dst}")
        return True

    dst.parent.mkdir(parents=True, exist_ok=True)

    # Show "updated" vs "unchanged"
    if dst.exists() and _files_equal(src, dst):
        info(f"{dst.relative_to(REPO)}  (unchanged)")
    else:
        shutil.copy2(src, dst)
        info(f"{dst.relative_to(REPO)}  (updated)")
    return True


def copy_dir(src, dst, dry_run=False):
    """Copy a directory from system to repo."""
    src, dst = Path(src), Path(dst)
    if not src.exists():
        warn(f"source missing: {src}")
        return False
    n = sum(1 for _ in src.rglob("*") if _.is_file())
    if dry_run:
        info(f"[dry-run] {src}/ ({n} files) -> {dst}/")
        return True
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, dirs_exist_ok=True, symlinks=False)
    info(f"{dst.relative_to(REPO)}/  ({n} files)")
    return True


def _files_equal(a, b):
    """Quick byte comparison of two files."""
    try:
        return Path(a).read_bytes() == Path(b).read_bytes()
    except Exception:
        return False


def defaults_export(domain, dst, dry_run=False):
    """Export a macOS defaults domain to a plist file."""
    dst = Path(dst)
    if dry_run:
        info(f"[dry-run] defaults export {domain}")
        return True
    rc, _ = run(f'defaults read "{domain}" 2>/dev/null')
    if rc != 0:
        warn(f"{domain} (not found)")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    rc, _ = run(f'defaults export "{domain}" "{dst}"')
    if rc == 0:
        info(f"defaults/{dst.name}")
        return True
    error(f"defaults export failed: {domain}")
    return False


# ══════════════════════════════════════════════════════════════════════
#  Backup steps
# ══════════════════════════════════════════════════════════════════════

STEPS = {}


def step(name, label):
    """Decorator to register a backup step."""
    def decorator(func):
        STEPS[name] = (label, func)
        return func
    return decorator


# ── 1. Homebrew Brewfile ─────────────────────────────────────────────


@step("brew", "1. Homebrew Brewfile")
def step_brew(dry_run=False, **_):
    section("1. Homebrew Brewfile")

    if not IS_MACOS:
        warn("Brewfile backup is macOS-only")
        return

    dst = REPO / "macos" / "Brewfile"
    if dry_run:
        info("[dry-run] brew bundle dump -> macos/Brewfile")
        return
    rc, _ = run(f'brew bundle dump --describe --force --no-vscode --file="{dst}"')
    if rc == 0:
        lines = dst.read_text().splitlines()
        taps  = sum(1 for l in lines if l.startswith("tap"))
        brews = sum(1 for l in lines if l.startswith("brew"))
        casks = sum(1 for l in lines if l.startswith("cask"))
        info(f"Brewfile: {taps} taps, {brews} formulas, {casks} casks")
    else:
        error("brew bundle dump failed")


# ── 2. Config files ──────────────────────────────────────────────────


@step("configs", "2. Config files")
def step_configs(dry_run=False, **_):
    section("2. Config Files")

    shared = REPO / "shared"

    # Shell dotfiles
    shell_files = [
        ".bash_profile", ".bashrc", ".shell_common",
        ".zprofile", ".zshenv", ".zshrc",
        ".hushlogin", ".gitconfig",
    ]
    for f in shell_files:
        copy_file(HOME / f, shared / f, dry_run)

    # Scripts
    copy_file(HOME / ".local" / "bin" / "theme", shared / "bin" / "theme", dry_run)

    # Starship
    copy_file(HOME / ".config" / "starship.toml", shared / "starship.toml", dry_run)

    # Catppuccin zsh colours
    for f in ["mocha.zsh", "latte.zsh"]:
        copy_file(HOME / ".zsh" / "catppuccin" / f,
                  shared / "zsh" / "catppuccin" / f, dry_run)

    # Neovim
    for f in ["init.lua", "lazy-lock.json"]:
        copy_file(HOME / ".config" / "nvim" / f, shared / "nvim" / f, dry_run)

    # Platform-specific
    if IS_MACOS:
        copy_file(HOME / ".config" / "ghostty" / "config",
                  REPO / "macos" / "ghostty" / "config", dry_run)
        copy_file(HOME / ".aerospace.toml",
                  REPO / "macos" / ".aerospace.toml", dry_run)
    else:
        copy_file(HOME / ".config" / "kitty" / "kitty.conf",
                  REPO / "linux" / "kitty.conf", dry_run)
        copy_file(HOME / ".local" / "bin" / "toggle_app",
                  REPO / "linux" / "bin" / "toggle_app", dry_run)


# ── 3. macOS defaults (macOS only) ────────────────────────────────────


@step("defaults", "3. macOS defaults (system preferences)")
def step_defaults(dry_run=False, **_):
    section("3. System Preferences")

    if not IS_MACOS:
        warn("macOS-only — Linux users: see the `dconf` step")
        return

    # macOS: export defaults domains
    defaults_dir = REPO / "macos" / "defaults"
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
        defaults_export(domain, defaults_dir / f"{filename}.plist", dry_run)

    # Export NSUserKeyEquivalents (custom keyboard shortcuts across all apps)
    if not dry_run:
        rc, stdout = run("defaults find NSUserKeyEquivalents 2>/dev/null")
        if rc == 0 and stdout:
            out = defaults_dir / "NSUserKeyEquivalents_all.txt"
            out.write_text(stdout)
            info("NSUserKeyEquivalents_all.txt")


# ── 4. Services (Automator Quick Actions) ────────────────────────────


@step("services", "4. Services (Automator workflows)")
def step_services(dry_run=False, **_):
    section("4. Services")

    if not IS_MACOS:
        warn("Services are macOS-only")
        return

    src = HOME / "Library" / "Services"
    dst = REPO / "macos" / "services"
    if not src.exists():
        warn("~/Library/Services/ not found")
        return

    items = [f for f in sorted(src.iterdir()) if not f.name.startswith(".")]
    if dry_run:
        info(f"[dry-run] backup {len(items)} services")
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
    info(f"backed up {count} services")


# ── 5. Oh My Zsh custom plugins ──────────────────────────────────────


@step("omz", "5. Oh My Zsh custom plugins/themes")
def step_omz(dry_run=False, **_):
    section("5. Oh My Zsh Custom")

    omz_custom = HOME / ".oh-my-zsh" / "custom"
    if not omz_custom.exists():
        warn("~/.oh-my-zsh/custom/ not found")
        return

    dst = REPO / "macos" / "omz-custom"

    # Record git-cloned plugins as name\tURL (instead of copying full repos)
    for subdir_name in ["plugins", "themes"]:
        src_sub = omz_custom / subdir_name
        if not src_sub.exists():
            continue

        list_file = dst / f"{subdir_name}.txt"
        entries = []
        for item in sorted(src_sub.iterdir()):
            if item.name.startswith(".") or item.name.startswith("example"):
                continue
            # If it's a git repo, record the URL; otherwise copy it
            if (item / ".git").exists():
                rc, url = run(f'git -C "{item}" remote get-url origin 2>/dev/null')
                if rc == 0 and url:
                    entries.append(f"{item.name}\t{url}")
                    info(f"recorded: {item.name} -> {url}")
            else:
                copy_dir(item, dst / subdir_name / item.name, dry_run)

        # Write de-duplicated list
        if entries and not dry_run:
            seen = set()
            unique = []
            for e in entries:
                name = e.split("\t")[0]
                if name not in seen:
                    seen.add(name)
                    unique.append(e)
            list_file.parent.mkdir(parents=True, exist_ok=True)
            list_file.write_text("\n".join(unique) + "\n")
            info(f"{subdir_name}.txt ({len(unique)} entries)")


# ── 7. Ollama models list ────────────────────────────────────────────


@step("ollama", "6. Ollama models list")
def step_ollama(dry_run=False, **_):
    section("6. Ollama Models")

    dst = REPO / "ollama_models.txt"
    if not has_cmd("ollama"):
        warn("ollama not installed")
        return
    if dry_run:
        info("[dry-run] ollama list -> ollama_models.txt")
        return
    rc, stdout = run("ollama list 2>/dev/null")
    if rc == 0 and stdout:
        dst.write_text(stdout + "\n")
        count = len(stdout.splitlines()) - 1    # minus header
        info(f"recorded {count} models")
    else:
        warn("ollama not running or no models")


# ── 8. Shortcuts list (macOS) ────────────────────────────────────────


@step("shortcuts", "7. Shortcuts (Quick Actions list)")
def step_shortcuts(dry_run=False, **_):
    section("7. Shortcuts")

    if not IS_MACOS:
        warn("Shortcuts are macOS-only")
        return

    dst = REPO / "macos" / "shortcuts_list.txt"
    if dry_run:
        info("[dry-run] shortcuts list -> shortcuts_list.txt")
        return
    rc, stdout = run("shortcuts list 2>/dev/null")
    if rc == 0 and stdout:
        dst.write_text(stdout + "\n")
        count = len(stdout.splitlines())
        info(f"recorded {count} shortcuts")
    else:
        warn("shortcuts command not available or empty")


# ── 8. GNOME dconf settings (Linux only) ──────────────────────────────


# Ordered list of (dconf path, filename) pairs. Must stay in sync with
# install.py's DCONF_PATHS so backup + restore cover the same subtrees.
DCONF_PATHS = [
    ("/org/gnome/desktop/interface/",                   "desktop-interface.dconf"),
    ("/org/gnome/desktop/wm/keybindings/",              "desktop-wm-keybindings.dconf"),
    ("/org/gnome/desktop/wm/preferences/",              "desktop-wm-preferences.dconf"),
    ("/org/gnome/desktop/input-sources/",               "desktop-input-sources.dconf"),
    ("/org/gnome/desktop/peripherals/",                 "desktop-peripherals.dconf"),
    ("/org/gnome/mutter/keybindings/",                  "mutter-keybindings.dconf"),
    ("/org/gnome/shell/keybindings/",                   "shell-keybindings.dconf"),
    ("/org/gnome/shell/extensions/",                    "shell-extensions.dconf"),
    ("/org/gnome/settings-daemon/plugins/media-keys/",  "media-keys.dconf"),
    ("/org/gnome/settings-daemon/plugins/color/",       "settings-daemon-color.dconf"),
    ("/org/gnome/terminal/legacy/profiles:/",           "gnome-terminal-profiles.dconf"),
]


@step("dconf", "8. GNOME dconf settings (Linux only)")
def step_dconf(dry_run=False, **_):
    section("8. GNOME dconf Settings")

    if IS_MACOS:
        warn("dconf is Linux-only")
        return

    if not has_cmd("dconf"):
        warn("dconf not found")
        return

    dconf_dir = REPO / "linux" / "dconf"
    if not dry_run:
        dconf_dir.mkdir(parents=True, exist_ok=True)

    dumped = empty = failed = 0
    for path, filename in DCONF_PATHS:
        dst = dconf_dir / filename
        if dry_run:
            info(f"[dry-run] dconf dump {path} -> linux/dconf/{filename}")
            dumped += 1
            continue
        rc, stdout = run(f'dconf dump "{path}"')
        if rc != 0:
            error(f"failed: {path}")
            failed += 1
            continue
        # Skip writing (and remove any stale file) when the subtree is empty.
        if not stdout.strip() or stdout.strip() == "[/]":
            if dst.exists():
                dst.unlink()
            empty += 1
            continue
        dst.write_text(stdout + "\n" if not stdout.endswith("\n") else stdout)
        info(filename)
        dumped += 1
    info(f"{dumped} dumped, {empty} empty (skipped), {failed} failed")


# ══════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="Backup system configs into this repo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
steps: {', '.join(STEPS.keys())}

examples:
  python3 backup.py                      full backup
  python3 backup.py --only brew defaults specific steps
  python3 backup.py --dry-run            preview only
""",
    )
    parser.add_argument("--dry-run", action="store_true", help="preview only")
    parser.add_argument(
        "--only", nargs="+", choices=list(STEPS.keys()),
        help="run only these steps",
    )
    args = parser.parse_args()

    os_label = "macOS" if IS_MACOS else "Linux"
    print(f"\n{BOLD}{'=' * 60}")
    print(f"  oh-my-dotfiles — backup ({os_label})")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Target: {REPO}")
    if args.dry_run:
        print(f"  {YELLOW}*** DRY-RUN MODE ***{RESET}")
    print(f"{'=' * 60}{RESET}")

    steps_to_run = args.only if args.only else list(STEPS.keys())

    for name in steps_to_run:
        label, func = STEPS[name]
        func(dry_run=args.dry_run)

    print(f"\n{BOLD}{GREEN}{'=' * 60}")
    print(f"  Backup complete!")
    print(f"{'=' * 60}{RESET}")

    print(f"\n{YELLOW}Reminder — these are NOT backed up (sensitive/manual):{RESET}")
    print("  - ~/.ssh/              (SSH keys)")
    print("  - ~/.bashrc_private    (API keys)")
    print("  - ~/.claude/           (Claude Code config, memories, API keys)")
    print("  - ~/d/vault.sparsebundle  (encrypted vault: Personal AI Brain + Media + Qdrant)")
    print(f"\n  Next: cd {REPO} && git diff && git add -A && git commit -m 'backup' && git push")


if __name__ == "__main__":
    main()
