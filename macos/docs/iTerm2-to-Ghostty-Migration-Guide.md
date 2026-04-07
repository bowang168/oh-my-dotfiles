# iTerm2 → Ghostty 完整迁移指南

> Ghostty v1.3.1 | macOS | MapleMono NF | Catppuccin 主题

---

## 一、当前配置评估

| 配置项 | 当前值 | 评价 |
|--------|--------|------|
| 字体 | MapleMono NF 14pt + 加粗渲染 | ✅ Nerd Font 图标支持 |
| 主题 | Catppuccin Latte/Mocha 自动切换 | ✅ 跟随 macOS 明暗模式 |
| 窗口 | tabs 样式，保存状态 | ✅ |
| 光标 | block，不闪烁 | ✅ |
| Option as Alt | true | ✅ 对 zsh 快捷键至关重要 |
| copy-on-select | clipboard | ✅ 选中即复制 |
| URL 可点击 | 开启 | ✅ |
| 自定义图标颜色 | Catppuccin 紫 | ✅ |

配置文件位置：`~/.config/ghostty/config`

---

## 二、快捷键对照表

### 基础操作

| 功能 | iTerm2 | Ghostty | 备注 |
|------|--------|---------|------|
| 新建 Tab | `⌘T` | `⌘T` | ✅ 相同 |
| 关闭 Tab | `⌘W` | `⌘W` | ✅ 相同 |
| 切换 Tab | `⌘1-8` | `⌘1-8` | ✅ 相同 |
| 最后一个 Tab | `⌘9` | `⌘9` | ✅ 相同 |
| 上/下一个 Tab | `⌘←/→` 或 `⌃Tab` | `⌘⇧[` / `⌘⇧]` 或 `⌃Tab` | ⚠️ 略有不同 |
| 新建窗口 | `⌘N` | `⌘N` | ✅ 相同 |
| 全屏 | `⌘Enter` | `⌘Enter` 或 `⌘⌃F` | ✅ |

### 分屏 (Split Panes)

| 功能 | iTerm2 | Ghostty | 备注 |
|------|--------|---------|------|
| 水平分屏（右） | `⌘D` | `⌘D` | ✅ 相同 |
| 垂直分屏（下） | `⌘⇧D` | `⌘⇧D` | ✅ 相同 |
| 切换分屏 | `⌘⌥方向键` | `⌘⌥方向键` | ✅ 相同 |
| 调整分屏大小 | 拖拽 | `⌘⌃方向键` | 每次 10px |
| 均分分屏 | — | `⌘⌃=` | Ghostty 独有 |
| 最大化当前分屏 | `⌘⇧Enter` | `⌘⇧Enter` | ✅ 相同 |

### 搜索/编辑

| 功能 | iTerm2 | Ghostty | 备注 |
|------|--------|---------|------|
| 搜索 | `⌘F` | `⌘F` | ✅ |
| 下/上一个匹配 | `⌘G` / `⌘⇧G` | `⌘G` / `⌘⇧G` | ✅ |
| 清屏 | `⌘K` | `⌘K` | ✅ |
| 全选 | `⌘A` | `⌘A` | ✅ |
| 复制 | `⌘C` | `⌘C` | ✅ |
| 粘贴 | `⌘V` | `⌘V` | ✅ |
| 撤销 | `⌘Z` | `⌘Z` | ✅ |
| Command Palette | — | `⌘⇧P` | Ghostty 独有！类似 VS Code |
| 打开配置 | — | `⌘,` | 直接编辑配置文件 |
| 重载配置 | — | `⌘⇧,` | 无需重启 |

### Zsh 行编辑（Option as Alt 已启用）

| 功能 | 快捷键 | 说明 |
|------|--------|------|
| 跳词（左） | `⌥←` | 上一个词 |
| 跳词（右） | `⌥→` | 下一个词 |
| 行首 | `⌘←` 或 `⌃A` | |
| 行尾 | `⌘→` 或 `⌃E` | |
| 删除到行首 | `⌘⌫` 或 `⌃U` | |
| 删除前一个词 | `⌥⌫` | |

---

## 三、动手试试

### 1. Tab 管理

```
⌘T          → 新建 tab（连按 3 次建 3 个）
⌘1, ⌘2, ⌘3  → 在 tab 间跳转
⌘W          → 关闭当前 tab
```

### 2. 分屏

```
⌘D          → 右边新分屏
⌘⇧D         → 下方新分屏
⌘⌥↑↓←→      → 在分屏间切换
⌘⌃↑↓←→      → 调整分屏大小
⌘⌃=         → 均分所有分屏
⌘⇧Enter     → 最大化/还原当前分屏
```

### 3. 搜索和滚动

```bash
# 先输出一些内容
seq 1 500

# 然后：
⌘F          → 打开搜索，输入 "250"
⌘G          → 下一个匹配
Esc         → 关闭搜索
⌘↑ / ⌘↓    → 跳到上/下一个 prompt（shell integration）
⌘Home       → 滚到顶部
⌘End        → 滚到底部
```

### 4. Command Palette（Ghostty 独有）

```
⌘⇧P         → 打开 command palette
              输入 "split" 或 "font" 看看有什么
```

### 5. 字体即时调整

```
⌘+          → 放大字体
⌘-          → 缩小字体
⌘0          → 重置字体大小
```

### 6. 配置热更新

```
⌘,          → 打开配置文件（用默认编辑器）
              修改后保存
⌘⇧,         → 重载配置，立即生效！
```

### 7. URL 点击

```bash
echo "https://github.com/ghostty-org/ghostty"
# ⌘+点击链接 → 浏览器打开
```

### 8. 终端检查器（调试用）

```
⌘⌥I         → 打开 terminal inspector，查看渲染细节
```

---

## 四、iTerm2 功能对照

| iTerm2 功能 | Ghostty 替代方案 |
|-------------|-----------------|
| Profiles | 单配置文件，简单直接 |
| Broadcast input | 暂不支持 |
| Triggers/自动化 | 用 shell 脚本 + keybind 替代 |
| 图片显示 (imgcat) | 支持 Kitty image protocol |
| tmux integration | 原生 split/tab 已够用，也可继续用 tmux |
| 密码管理器 | 不支持，用系统 Keychain |

---

## 五、主题推荐

当前使用 **Catppuccin Latte/Mocha 跟随系统切换**，推荐保留。

其他可选：

| 风格 | Light 主题 | Dark 主题 | 适合场景 |
|------|-----------|-----------|---------|
| 柔和舒适 | Catppuccin Latte ✅ | Catppuccin Mocha ✅ | **当前选择，推荐** |
| 高对比 | Tokyo Night Light | Tokyo Night | 长时间编码 |
| 经典 | Solarized Light | Solarized Dark | 老牌经典 |
| 赛博 | — | Cyberdream | 深色控 |
| 极简 | Alabaster | Nord | 干净简洁 |

切换主题方法：
- 编辑 `~/.config/ghostty/config` 中的 `theme =` 行
- `⌘⇧,` 重载
- 或 `⌘⇧P` 打开 Command Palette 搜索 theme

Ghostty 内置 **463 个主题**，完整列表：终端运行 `ghostty +list-themes`

---

## 六、设为默认终端

打开 Ghostty → 菜单栏 `Ghostty` → `Make Default Terminal App`

---

## 七、配置文件参考

`~/.config/ghostty/config`：

```ini
# === 字体 ===
font-family = MapleMono NF
font-size = 14
font-thicken = true

# === 主题 ===
theme = light:Catppuccin Latte,dark:Catppuccin Mocha

# === 窗口 ===
window-padding-x = 8
window-padding-y = 4
window-decoration = true
macos-titlebar-style = tabs
window-save-state = always
confirm-close-surface = false

# === 光标 ===
cursor-style = block
cursor-style-blink = false
shell-integration-features = no-cursor

# === 性能 ===
window-vsync = true

# === 行为 ===
copy-on-select = clipboard
mouse-hide-while-typing = true
scrollback-limit = 10000
link-url = true

# === macOS 特定 ===
macos-option-as-alt = true
macos-icon = custom-style
macos-icon-ghost-color = #cba6f7
macos-icon-screen-color = #1e1e2e
```
