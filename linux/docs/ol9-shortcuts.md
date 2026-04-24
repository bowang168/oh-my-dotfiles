# Oracle Linux 9 — Keyboard Shortcuts

## keyd (key remapping)

[keyd](https://github.com/rvaiya/keyd) remaps CapsLock to **Escape** (tap) / **Super** (hold).

```ini
# /etc/keyd/default.conf
[ids]
*

[main]
capslock = overload(meta, esc)
```

### Install keyd

```bash
git clone https://github.com/rvaiya/keyd
cd keyd
make && sudo make install
sudo systemctl enable --now keyd
```

After editing `/etc/keyd/default.conf`, reload with `sudo keyd reload`.

## GNOME Window Management

| Shortcut | Action |
|----------|--------|
| `Super+f` | Toggle maximize |
| `Super+r` | Unmaximize (restore) |
| `Super+h` | Minimize |
| `Super+w` | Close window |
| `Super+d` | Show desktop |
| `Super+e` | File manager |
| `Super+Tab` | Switch applications |
| `Super+,` / `Super+.` | Switch workspace left / right |
| `Super+3` | Maximize horizontally |
| `Super+4` | Maximize vertically |
| `Ctrl+Space` | Switch input source |
| `Ctrl+Alt+Delete` | Logout |
| `Shift+Alt+Super+l` | Lock screen |

## Custom Shortcuts (toggle_app)

### Wayland prerequisite: Window Calls extension

On a Wayland session, `toggle_app` can't inspect or focus windows via
`xdotool`/`wmctrl`. It uses the **Window Calls** GNOME Shell extension over
D-Bus instead. Without it, every invocation just spawns a new instance of the
target app (no toggle, no focus).

- Install: <https://extensions.gnome.org/extension/4724/window-calls/>
- UUID: `window-calls@domandoman.xyz`
- After installing, log out/in (or restart GNOME Shell) and enable it in the
  Extensions app. Verify with:
  ```bash
  gdbus call --session --dest org.gnome.Shell \
      --object-path /org/gnome/Shell/Extensions/Windows \
      --method org.gnome.Shell.Extensions.Windows.List
  ```
  Should return a JSON payload, not `UnknownMethod`.

X11 sessions don't need this — `xdotool` + `wmctrl` handle it.

| Shortcut | Command | Description |
|----------|---------|-------------|
| `Super+Return` | `toggle_app gnome-terminal` | Toggle terminal |
| `Super+g` | `toggle_app google-chrome` | Toggle Chrome |
| `Super+Shift+f` | `toggle_app firefox` | Toggle Firefox |
| `Super+b` | `toggle_app gedit` | Toggle gedit |
| `Super+j` | `[custom tool]` | Quick open |
| `Super+u` | `[custom tool] --no-open` | Quick open without opening |
| `Super+y` | `[custom tool] --one-value` | Quick open single value |
| `Super+o` | `[custom tool] --raw-capture` | Quick open raw capture |

## Volume

| Shortcut | Action |
|----------|--------|
| `Super+[` | Volume up |
| `Super+/` | Volume down |

## Restore shortcuts

```bash
# Custom shortcuts are stored in dconf. To export:
dconf dump /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/ > custom-shortcuts.dconf

# To restore:
dconf load /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/ < custom-shortcuts.dconf
```
