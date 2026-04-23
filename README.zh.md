# oh-my-dotfiles

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-yellow?style=flat-square&logo=buy-me-a-coffee)](https://buymeacoffee.com/bowang168)
[![Sponsor](https://img.shields.io/badge/GitHub%20Sponsors-sponsor-ea4aaa?style=flat-square&logo=github-sponsors)](https://github.com/sponsors/bowang168)

跨平台 dotfiles 与配置管理，支持 **macOS** + **Oracle Linux 9 / 10**。

两个脚本搞定一切：

| 脚本 | 方向 | 功能 |
|------|------|------|
| `install.py` | 仓库 -> 系统 | 创建 symlink、安装软件包、恢复系统偏好 |
| `backup.py` | 系统 -> 仓库 | 将当前配置快照保存到仓库 |

> **[English README](README.md)**

## 目录结构

```
oh-my-dotfiles/
├── install.py           # 恢复: 仓库 -> 系统
├── backup.py            # 备份: 系统 -> 仓库
│
├── shared/              # 跨平台 (macOS + Linux)
│   ├── .shell_common    # 共享 aliases 和函数
│   ├── .zshrc           # Zsh 配置 (oh-my-zsh + starship)
│   ├── .bashrc          # Bash 配置
│   ├── .gitconfig       # Git 配置 (delta, gh auth)
│   ├── starship.toml    # Starship 提示符
│   ├── bin/theme        # 深色/浅色主题切换
│   ├── nvim/            # Neovim (lazy.nvim + catppuccin)
│   └── zsh/catppuccin/  # Zsh 语法高亮主题
│
├── macos/               # 仅 macOS
│   ├── Brewfile         # Homebrew 软件包
│   ├── .aerospace.toml  # AeroSpace 平铺窗口管理器
│   ├── ghostty/         # Ghostty 终端
│   ├── defaults/        # macOS plist 导出
│   ├── services/        # Automator 快捷操作
│   ├── omz-custom/      # Oh My Zsh 插件列表
│   └── docs/            # macOS 指南
│
├── linux/               # Oracle Linux 9 / 10
│   ├── packages.txt     # dnf 软件包
│   ├── kitty.conf       # Kitty 终端
│   ├── gnome-terminal-profiles.dconf
│   ├── bin/toggle_app   # 窗口切换 (Wayland + X11)
│   └── docs/            # Linux 指南
│
├── claude/              # Claude Code 配置 (备份后生成)
│   ├── CLAUDE.md
│   ├── settings.json
│   └── projects/        # 项目记忆
│
└── ollama_models.txt    # Ollama 模型列表 (备份后生成)
```

## 快速开始

### 全新系统 (恢复)

```bash
# 1. 克隆仓库
git clone git@github.com:bowang168/oh-my-dotfiles.git ~/g/oh-my-dotfiles
cd ~/g/oh-my-dotfiles

# 2. 交互式安装 (每步确认)
python3 install.py

# 3. 跳过确认，全部执行
python3 install.py --yes

# 4. 仅预览，不执行
python3 install.py --dry-run

# 5. 只执行指定步骤
python3 install.py --only prereqs brew configs omz
```

**Oracle Linux 10 先决条件** —— 运行 `install.py` 之前先启用 EPEL 和
CodeReady Builder，否则基础仓库中缺少大部分 CLI 工具：

```bash
sudo dnf install -y oracle-epel-release-el10
sudo dnf config-manager --enable ol10_u1_developer_EPEL ol10_codeready_builder
```

以下工具 EPEL10 中也没有 —— 从上游安装：

```bash
# eza, git-delta: 从 GitHub releases 下载二进制到 ~/.local/bin
# starship:
curl -sS https://starship.rs/install.sh | sh -s -- -b ~/.local/bin -y
# zoxide:
curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh -s -- --bin-dir ~/.local/bin
```

### 现有系统 (备份)

```bash
cd ~/g/oh-my-dotfiles

# 完整备份
python3 backup.py

# 仅预览
python3 backup.py --dry-run

# 指定步骤
python3 backup.py --only brew defaults

# 然后提交推送
git add -A && git commit -m 'backup' && git push
```

## 安装步骤一览

| # | 步骤 | macOS | Linux | 说明 |
|---|------|:-----:|:-----:|------|
| 0 | `prereqs` | Yes | 跳过 | Xcode CLT, Homebrew, git, gh |
| 1 | `brew` | Yes | Yes | `brew bundle` / `dnf install` |
| 2 | `configs` | Yes | Yes | Symlink 所有 dotfiles |
| 3 | `omz` | Yes | Yes | Oh My Zsh + 自定义插件 |
| 4 | `defaults` | Yes | Yes | macOS `defaults import` / GNOME dconf |
| 5 | `services` | Yes | 跳过 | Automator 快捷操作 |
| 6 | `claude` | Yes | Yes | Claude Code CLI + 配置 |
| 7 | `fonts` | Yes | 跳过 | Nerd Font + 中文字体 |
| 8 | `hidefolders` | Yes | 跳过 | 隐藏 ~/Library, ~/Movies 等 |
| 9 | `ollama` | 可选 | 可选 | 拉取 Ollama 模型 (较慢) |
| 10 | `clihelp` | Yes | Yes | 中文 CLI 帮助 (tldr) |

## 备份步骤一览

| # | 步骤 | macOS | Linux | 说明 |
|---|------|:-----:|:-----:|------|
| 1 | `brew` | Yes | 跳过 | 导出 Brewfile |
| 2 | `configs` | Yes | Yes | 复制配置文件到仓库 |
| 3 | `defaults` | Yes | Yes | 导出 macOS defaults / GNOME dconf |
| 4 | `services` | Yes | 跳过 | 复制 Automator workflows |
| 5 | `claude` | Yes | Yes | Claude Code 配置 + 项目记忆 |
| 6 | `omz` | Yes | Yes | 记录自定义插件 URL |
| 7 | `ollama` | Yes | Yes | 记录已安装模型列表 |
| 8 | `shortcuts` | Yes | 跳过 | 导出 macOS 快捷指令名称 |

## 同步策略

| 内容 | 方式 | 原因 |
|------|------|------|
| Dotfiles 和配置 | **Git** (本仓库) | 版本控制，可 diff 审查 |
| 密钥 (`.bashrc_private`, `.ssh/`) | **手动复制** | 安全性 |

## 主题切换

统一的深色/浅色切换，覆盖所有工具：

```bash
theme dark    # Catppuccin Mocha (深色)
theme light   # Catppuccin Latte (浅色)
theme toggle  # 切换
```

影响范围：macOS 系统外观 / GNOME GTK、Neovim、zsh 语法高亮、终端。

## 安装后手动步骤

以下内容无法自动化，需手动完成：

1. 从加密备份恢复 `~/.ssh/` 和 `~/.bashrc_private`
2. 登录：Apple ID / iCloud / Brave 浏览器同步
3. macOS 权限：辅助功能、完全磁盘访问权限、输入监控
4. 显示设置：Night Shift、True Tone、分辨率
5. 默认浏览器、锁屏 / Touch ID

## 许可

[MIT](LICENSE)
