# 手动步骤指南

> 场景: macOS / Linux 全新安装后，配合 `backup.py` / `install.py` 使用
>
> 本文档覆盖脚本无法自动化的部分。

---

## 一、备份阶段 (在当前系统上执行)

### 1.1 运行自动备份脚本

```bash
cd ~/g/oh-my-dotfiles
python3 backup.py              # 完整备份
python3 backup.py --dry-run    # 预览
python3 backup.py --only brew configs defaults  # 指定步骤
```

### 1.2 手动备份敏感文件

以下文件包含敏感信息，不会被脚本收集，需手动备份到 **加密存储**:

```bash
# SSH 密钥
cp -r ~/.ssh/ /Volumes/ENCRYPTED_USB/manual_backup/ssh/

# API Keys / 私有环境变量
cp ~/.bashrc_private /Volumes/ENCRYPTED_USB/manual_backup/

# Claude Code 配置 (含 API key、memory、项目设置)
cp -r ~/.claude/ /Volumes/ENCRYPTED_USB/manual_backup/claude/

# Personal AI Brain
cp -r ~/d/Personal_AI_Brain/ /Volumes/ENCRYPTED_USB/manual_backup/Personal_AI_Brain/
```

### 1.3 手动备份字体 (macOS)

字体文件过大，不适合存入 git:

```bash
mkdir -p /Volumes/ENCRYPTED_USB/manual_backup/fonts
cp -r ~/Library/Fonts/ /Volumes/ENCRYPTED_USB/manual_backup/fonts/
```

关键字体:

| 字体 | 用途 |
|------|------|
| MapleMono NF | 代码/终端 |
| 霞鹜文楷 (LXGWWenKai) | 中文阅读 |
| 霞鹜文楷 Mono | 含中文注释的代码 |

### 1.4 记录显示器设置 (macOS)

System Settings > Displays, 截图或记录:

| 项目 | 当前值 |
|------|--------|
| 分辨率 / 缩放 | ______ |
| 外接显示器 | ______ |
| Night Shift 时间 | ______ |

### 1.5 推送备份到 GitHub

```bash
cd ~/g/oh-my-dotfiles
git add -A && git diff --cached  # 审查
git commit -m "backup: $(date +%Y-%m-%d)"
git push
```

---

## 二、恢复阶段

### 2.1 获取仓库

```bash
# macOS 自带 git (Xcode CLT), Linux 需先 sudo dnf/apt install git
mkdir -p ~/g && cd ~/g
git clone https://github.com/bowang168/oh-my-dotfiles.git
cd oh-my-dotfiles
```

### 2.2 运行自动恢复脚本

```bash
python3 install.py --dry-run     # 预览
python3 install.py               # 交互式 (逐步确认)
python3 install.py --yes         # 跳过确认
python3 install.py --only configs omz  # 指定步骤
```

### 2.3 手动恢复敏感文件

```bash
# SSH
cp -r /Volumes/ENCRYPTED_USB/manual_backup/ssh/ ~/.ssh/
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# API Keys
cp /Volumes/ENCRYPTED_USB/manual_backup/.bashrc_private ~/

# Claude Code
cp -r /Volumes/ENCRYPTED_USB/manual_backup/claude/ ~/.claude/

# Personal AI Brain
mkdir -p ~/d
cp -r /Volumes/ENCRYPTED_USB/manual_backup/Personal_AI_Brain/ ~/d/Personal_AI_Brain/
```

### 2.4 安装 Claude Code

```bash
curl -fsSL https://claude.ai/install.sh | bash
claude  # 首次运行完成登录
```

### 2.5 手动恢复字体 (macOS)

```bash
cp -r /Volumes/ENCRYPTED_USB/manual_backup/fonts/* ~/Library/Fonts/
```

验证: 打开 **Font Book**, 确认 MapleMono NF / 霞鹜文楷等已安装。

### 2.6 macOS 手动配置

这些设置无法通过 `defaults import` 可靠恢复:

**System Settings > Accessibility > Display:**
- Reduce transparency
- Reduce motion
- Increase contrast

**System Settings > Accessibility > Pointer Control > Trackpad Options:**
- 启用三指拖移

**System Settings > Privacy & Security:**
- Accessibility 权限 (Terminal, AeroSpace, HyperKey)
- Full Disk Access
- Input Monitoring

**HyperKey 设置:**
- Remap: Caps Lock -> Hyper Key
- Quick press: Esc
- Include Shift: ON
- Open on login: ON

**其他:**
- 默认浏览器 (Desktop & Dock)
- Night Shift / f.lux
- Lock screen / Touch ID

### 2.7 浏览器同步

- **Brave**: Settings > Sync > 扫码同步
- **Chrome**: 登录 Google 账号
- 安装 **Vimium** 扩展

### 2.8 输入法

macOS: 从 App Store 安装讯飞输入法, System Settings > Keyboard > Input Sources 添加。

### 2.9 Ollama 模型 (可选)

```bash
# 先启动 Ollama, 然后:
python3 install.py --only ollama
# 或手动:
ollama pull qwen3-embedding:0.6b
```

---

## 三、恢复验证清单

| 项目 | 验证方法 | 平台 |
|------|----------|------|
| Shell (zsh + OMZ) | 新终端, 检查 prompt 和 alias | All |
| Neovim | `nvim`, 检查插件和主题 | All |
| Git | `git config --list` | All |
| SSH | `ssh -T git@github.com` | All |
| Homebrew | `brew doctor` | macOS |
| Ghostty / Kitty | 打开终端, 检查字体和配色 | macOS / Linux |
| AeroSpace | 窗口管理快捷键 | macOS |
| Dock | 自动隐藏, 无动画 | macOS |
| Finder | 偏好设置 | macOS |
| f.lux | 白天 3400K / 日落 2700K / 睡前 2300K | macOS |
| Claude Code | `claude`, 检查 memory | All |
| Ollama | `ollama list` | All |
| 截图 | jpg, 前缀 sc, 无阴影, ~/Desktop | macOS |

---

## 四、日常维护

```bash
cd ~/g/oh-my-dotfiles

# 备份当前配置
python3 backup.py
git add -A && git diff --cached
git commit -m "backup: $(date +%Y-%m-%d)" && git push

# 新增 brew 包后
python3 backup.py --only brew

# 修改系统偏好后
python3 backup.py --only defaults
```
