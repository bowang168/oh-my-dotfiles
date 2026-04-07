# f.lux 护眼配置完全指南

> 适用于 macOS 26 (Tahoe) + f.lux 42.2 | 位置: 奥克兰 (-36.7, 174.8)

---

## 目录

- [为什么用 f.lux](#为什么用-flux)
- [预设模式选择](#预设模式选择)
- [三个时段色温设置](#三个时段色温设置)
- [Options 菜单](#options-菜单)
- [Color Effects 菜单](#color-effects-菜单)
- [Disable 菜单](#disable-菜单)
- [我的推荐配置](#我的推荐配置)
- [macOS 配合设置](#macos-配合设置)
- [f.lux 护眼的局限性](#flux-护眼的局限性)
- [常见问题](#常见问题)

---

## 为什么用 f.lux

| 作用 | 科学依据 |
|------|---------|
| 减少蓝光 (380-500nm) | 降低对褪黑素的抑制，改善睡眠质量 |
| 降低屏幕色温 | 暖色调减少视觉刺激，缓解眼疲劳 |
| 自动跟随日出日落 | 模拟自然光周期，维持昼夜节律 |

**注意**: f.lux 主要帮助**睡眠**，对眼健康是辅助作用。真正护眼靠亮度控制 + 用眼习惯。

---

## 预设模式选择

在 Preferences 窗口右上角下拉菜单中选择：

| 模式 | 色温策略 | 适合谁 |
|------|---------|--------|
| **Recommended colors** | f.lux 默认推荐，平衡护眼和色彩 | 普通用户 |
| **Custom colors** | 完全自定义 Daytime/Sunset/Bedtime 三个色温 | 高级用户，想精确控制 |
| **Classic f.lux** | 旧版默认值，滤蓝光力度中等 | 怀旧用户 |
| **Far from the equator** | 更激进的暖色，冬天更早更强过滤 | 高纬度地区 (60°+) |
| **Working late** | 深夜时色温不会降太低，保持屏幕可读性 | 夜猫子 / 程序员 |

**推荐**: 程序员选 **Custom colors** 手动调，或 **Working late** 开箱即用。

---

## 三个时段色温设置

通过 Preferences 窗口的滑块调节，或选 Custom colors 后手动设定。

### 色温参考

| 色温 (K) | 对应光源 | 视觉感受 |
|----------|---------|---------|
| 6500K | 正午日光 | 冷白，蓝光最多 |
| 5500K | 上午日光 | 自然白 |
| 4000K | 日光灯 | 微暖 |
| 3400K | 卤素灯 | 暖白 |
| 2700K | 白炽灯 | 暖黄 |
| 2300K | 蜡烛光 | 深暖，非常黄 |
| 1900K | 篝火 | 极暖，几乎全红 |

### 推荐设置（程序员深夜工作）

| 时段 | 推荐色温 | 说明 |
|------|---------|------|
| **Daytime** | 5500K | 白天轻微暖色，不影响代码语法高亮辨识 |
| **Sunset** | 3500K | 日落后舒适过渡，屏幕明显变暖 |
| **Bedtime** | 2500K | 睡前助眠，代码仍可辨认 |

### 其他设置项

| 设置 | 说明 |
|------|------|
| **Wake time** (起床时间) | 设为实际起床时间（如 8:00 AM），f.lux 据此计算恢复正常色温的时间 |
| **Location** | 自动获取或手动输入坐标，用于计算日出日落时间 |
| **Start f.lux at login** | 开机自启，建议勾选 |

---

## Options 菜单

从菜单栏 f.lux 图标 → Options 进入。

| 选项 | 效果 | 建议 |
|------|------|------|
| **Fast transitions** | 色温瞬间切换（默认是 20 分钟渐变） | **不勾** — 慢过渡对眼睛更友好，突变刺眼 |
| **Sleep in on weekends** | 周末起床时间自动延后，色温恢复也延后 | **勾选** — 周末多睡一会儿 |
| **Expanded daytime settings** | 白天也能把色温调到很暖（默认白天锁定在较高色温） | **不勾** — 白天不需要过滤蓝光 |
| **Dim on disable** | 临时关闭 f.lux 时降低亮度补偿，避免突然刺眼 | **勾选** — 偶尔关 f.lux 看准确颜色时不会闪眼 |
| **Notifications from f.lux website** | f.lux 官方推送通知 | **不勾** — 无用，纯广告 |
| **Backwards alarm clock** | 显示"距离起床还有 X 小时"提醒，催你去睡觉 | **可以勾** — 对夜猫子程序员有用 |

---

## Color Effects 菜单

从菜单栏 f.lux 图标 → Color Effects 进入。

| 选项 | 效果 | 适用场景 | 建议 |
|------|------|---------|------|
| **Darkroom** | 屏幕变成全红 + 极暗，类似暗房红光 | 天文观星、完全黑暗环境 | **不勾** — 太极端，代码看不清 |
| **Movie mode** | 临时降低滤镜强度，保留更多原始色彩 | 看电影/视频时想看准确颜色 | **不勾** — 需要时手动开，看完自动恢复 |
| **macOS Dark theme at sunset** | 日落自动切 Dark Mode，日出切回 Light Mode | 想要日夜主题自动切换 | **看情况** — 如果 24 小时都用 Dark Mode 就不勾 |

---

## Disable 菜单

从菜单栏 f.lux 图标 → Disable 进入。临时关闭 f.lux 的选项：

| 选项 | 说明 |
|------|------|
| **Disable for 1 hour** | 1 小时后自动恢复 |
| **Disable until sunrise** | 到日出时恢复 |
| **Disable for current app** | 只对当前应用关闭（如设计软件需要准确颜色） |

**使用场景**: 做 UI 设计、看照片/视频颜色、校色时临时关闭。

---

## 我的推荐配置

### f.lux Preferences

```
预设模式:     Custom colors
Daytime:     5500K
Sunset:      3500K
Bedtime:     2500K
Wake time:   8:00 AM
Location:    自动检测 (奥克兰)
Start at login: ✅
```

### Options

```
Fast transitions:            ❌
Sleep in on weekends:        ✅
Expanded daytime settings:   ❌
Dim on disable:              ✅
Notifications:               ❌
Backwards alarm clock:       ✅ (可选)
```

### Color Effects

```
Darkroom:                         ❌
Movie mode:                       ❌
macOS Dark theme at sunset:       看个人偏好
```

---

## macOS 配合设置

f.lux 只管色温，以下 macOS 原生设置配合使用效果最佳：

### 1. 显示器色彩配置

**System Settings → Displays → Color profile**

选择 **Apple Display (P3-600 nits)** — 亮度上限适中，色彩准确。

| 配置 | 护眼评分 | 说明 |
|------|---------|------|
| Apple Display (P3-600 nits) | ★★★★★ | 日常最佳 |
| Apple XDR Display (P3-1600 nits) | ★★ | 峰值亮度太高 |
| Internet & Web (sRGB) | ★★★ | 色域窄，不是最优 |
| Photography (P3-D65) | ★★★★ | 摄影优化，日常也可 |

### 2. True Tone

**System Settings → Displays → True Tone → 开启**

根据环境光自动调色温，减少环境光与屏幕的色差（色差是眼疲劳主因之一）。

### 3. 亮度

- 手动调到 **40-60%**
- 避免用自动亮度（波动反而累眼）
- 环境光不要太暗，屏幕与环境亮度差是伤眼主因

### 4. Dark Mode

**System Settings → Appearance → Dark**

减少整体屏幕光量，编辑器 / 终端推荐主题：

| 主题 | 特点 |
|------|------|
| Solarized Dark | 经典，对比度适中 |
| One Dark | 流行，色彩丰富 |
| Catppuccin Mocha | 现代，柔和暖色 |
| Tokyo Night | 冷色系但不刺眼 |

### 5. Night Shift (与 f.lux 二选一)

如果使用 f.lux，**关闭 Night Shift** 避免冲突：

**System Settings → Displays → Night Shift → Off**

### 6. Reduce White Point（降低白点值）

**System Settings → Accessibility → Display → Reduce White Point**

开启后滑块调到 **20-30%**，在不降低亮度的情况下降低刺眼白光强度。

> 注意：部分 macOS 版本可能没有此选项或位置有变化。

---

## f.lux 护眼的局限性

| f.lux 能做的 | f.lux 不能做的 |
|-------------|---------------|
| 减少蓝光 → 改善睡眠 | 不能代替调低亮度 |
| 降低色温 → 减少视觉刺激 | 不能防止长时间用眼的疲劳 |
| 自动跟随日出日落 | 不能治疗近视或干眼 |

### 真正护眼的核心习惯

1. **20/20/20 法则** — 每 20 分钟看 20 英尺 (6 米) 远处 20 秒
2. **环境光匹配** — 不要关灯看屏幕
3. **亮度控制** — 比滤蓝光重要得多
4. **眨眼频率** — 专注屏幕时眨眼频率下降 60%，有意识多眨眼
5. **屏幕距离** — 保持 50-70cm（一臂距离）
6. **定期休息** — macOS 工具: Time Out (免费) 或 Stretchly (开源)

---

## 常见问题

### f.lux 和 Night Shift 能同时开吗？

不建议。两个都改色温会叠加，效果不可预测。选一个用，f.lux 比 Night Shift 调节更细腻（支持到 1200K，Night Shift 最低约 2700K）。

### f.lux 菜单栏图标不显示？

macOS 26 上可能有兼容性问题。解决方案：
1. 重启 f.lux: `killall Flux && open /Applications/Flux.app`
2. 检查是否被菜单栏管理工具 (Ice/Bartender) 隐藏
3. 更新到最新版: https://justgetflux.com/

### 做设计 / 看照片时需要准确颜色？

菜单栏 → Disable → **Disable for current app** 或 **Disable for 1 hour**。

### 白天需要开 f.lux 吗？

Daytime 设 5500-6500K 基本等于不过滤。白天蓝光是自然的，不需要刻意过滤。

### f.lux 会影响截图 / 录屏颜色吗？

**不会**。f.lux 通过显卡色彩表 (gamma table) 修改输出，截图和录屏捕获的是原始颜色。
