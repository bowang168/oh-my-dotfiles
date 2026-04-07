---
title: Claude Code CLI 使用指南
tags:
  - 工具/Claude
  - 职业/Linux
updated: 2026-04-05
sensitivity: public
---

# Claude Code CLI 使用指南

> 终端里的 AI 编程助手 · 读写文件、执行命令、搜索代码、联网查询

---

## 核心能力

| 项目 | 说明 |
|------|------|
| 本质 | 终端 AI 编程助手 |
| 核心 | 读写文件、shell 命令、搜索代码、联网、MCP 工具 |
| 最佳场景 | 代码开发、文件处理、项目管理、自动化 |

---

## 常用命令

### 对话与上下文

| 命令 | 作用 |
|------|------|
| `/clear` | 清空对话历史（**不清** Memory 和 CLAUDE.md） |
| `/compact` | 压缩对话历史，释放上下文空间 |
| `/rewind` | 回退到上一个状态 |
| `/stash` | 暂存当前提示词（同 Ctrl+S） |

### 代码与项目

| 命令 | 作用 |
|------|------|
| `/commit` | 智能生成 git commit 信息并提交 |
| `/review` | 代码审查 |
| `/init` | 在当前项目生成 CLAUDE.md |
| `/effort` | 调整响应详细程度（快速 / 标准 / 深度） |

### 工具与配置

| 命令 | 作用 |
|------|------|
| `/config` | 打开配置界面（模型、语言、权限等） |
| `/memory` | 管理跨会话记忆文件 |
| `/doctor` | 诊断环境问题（必跑一次确认配置正常） |
| `/insights` | 查看使用统计，帮助优化与 Claude 的协作方式 |
| `/statusline` | 显示当前模型、上下文占用、5h/7d 限额使用情况 |
| `/cost` | 查看本次会话 token 消耗 |

### 输入与会话

| 命令 | 作用 |
|------|------|
| `/voice` | 语音输入模式（`/config` 可改听写语言，默认 en） |
| `/copy` | 复制最后一条回复到剪贴板 |
| `/teleport` | 将 claude.ai Web 会话（含历史）迁移到当前终端 |
| `/remote-control` | 将终端会话暴露到手机 / claude.ai，远程发送提示、审批操作 |
| `/powerup` | 新手功能导览（推荐初次使用时运行） |

### 其他 / 彩蛋

| 命令 | 作用 |
|------|------|
| `/btw` | 旁路提问（不打断主任务的侧边提问） |
| `/buddy (pet\|off)` | 开关吉祥物小鹅 Trellis |
| `/fast` | 切换快速模式（同 Meta+O） |

---

## 快捷键

### 输入模式

| 快捷键 | 作用 |
|--------|------|
| `!` + 命令 | Bash 模式，直接执行 shell（结果进入对话） |
| `/` | 命令模式 |
| `@<file-path>` | 引用文件内容到提示词 |
| `&` | 后台任务模式 |
| `\` + `Enter` | 提示词内换行 |
| `Double Esc` | 清空当前输入框 |
| `Shift+Tab` | 自动接受所有待审批编辑 |

### 编辑与控制

| 快捷键 | 作用 |
|--------|------|
| `Ctrl+G` | 在 `$EDITOR` 中编辑提示词 |
| `Ctrl+S` | 暂存当前提示词 |
| `Ctrl+Shift+-` | 撤销上一步操作 |
| `Ctrl+Z` | 挂起 Claude Code（`fg` 恢复） |
| `Ctrl+V` | 粘贴图片（支持截图直接粘贴） |
| `Ctrl+O` | 切换详细输出模式 |
| `Ctrl+T` | 切换任务面板 |

### 模型与速度

| 快捷键 | 作用 |
|--------|------|
| `Meta+P` | 切换模型 |
| `Meta+O` | 切换快速模式（Fast Mode） |

---

## 内置工具

| 工具 | 用途 |
|------|------|
| Read | 读取文件（含图片、PDF、Jupyter Notebook） |
| Write | 创建新文件 |
| Edit | 精确局部编辑（优先于 Write） |
| Glob | 按文件名/路径模式搜索 |
| Grep | 按内容正则搜索 |
| Bash | 执行 shell 命令 |
| Agent | 派遣子代理处理子任务 |
| WebSearch / WebFetch | 联网搜索 / 抓取页面 |

---

## 工作原则

1. **先读后改** — 先理解现状再修改
2. **并行执行** — 独立操作同时进行，提高效率
3. **最小改动** — 不做超出需求的"优化"
4. **安全优先** — 危险操作（删除、force push 等）先确认

---

## 高效协作技巧

### 指令要具体

```
❌ "帮我改一下这个文件"
✅ "把 config.py 的数据库连接从 localhost 改为 192.168.1.100"
```

### 管道输入

```bash
git diff | claude "review these changes"
cat error.log | claude "analyze errors"
```

### 非交互模式（脚本/CI 使用）

```bash
claude -p "list all TODO comments"
claude -p "summarize" < README.md > summary.txt
```

### 在当前会话执行 shell 并注入结果

```bash
! git log --oneline -10     # 结果直接出现在对话上下文中
```

---

## 进阶功能

### CLAUDE.md 项目配置
项目根目录放 `CLAUDE.md`，写入项目规则、约定、禁止行为，每次启动自动读取。
全局配置在 `~/.claude/CLAUDE.md`。

### Memory 记忆系统
- 路径：`~/.claude/projects/<project-hash>/memory/`
- 跨会话保留偏好、上下文、项目背景
- `/clear` 只清对话，**不清 Memory**

### MCP 服务器
支持 Gmail、Google Calendar、Slack、数据库直连等第三方工具集成。

### 子代理（Agent）

| 子代理 | 适用场景 |
|--------|----------|
| Explore | 快速探索大型代码库，按需指定 quick / medium / thorough |
| Plan | 设计实现方案、架构决策 |
| General | 多步骤复杂任务、并行研究 |

---

## 常见场景速查

| 场景 | 示例提示词 |
|------|-----------|
| 理解项目 | "分析项目结构和主要功能" |
| 修 Bug | "npm test 报错 TypeError: cannot read..." |
| 写功能 | "给 Express 添加 JWT 登录" |
| Git 提交 | `/commit` |
| 创建 PR | "创建 PR，标题和描述自动生成" |
| 批量处理 | "把 docs/ 下所有 .txt 转为 .md" |
| 技术调研 | "Next.js App Router vs Pages Router 对比" |
| 读 PDF | "读取这个 PDF 并总结要点" |
| 远程会话 | `/teleport` 从手机 / Web 迁移到终端 |
