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
