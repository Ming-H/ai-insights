---
title: "用 Claude Code 开发复杂项目：8 个实用技巧"
date: 2026-03-03
draft: false
tags: ["Claude Code", "实战", "AI 编程"]
categories: ["博客"]
description: "8个经过实战验证的技巧，帮你用 Claude Code 高效开发复杂项目。"
---

## CLAUDE.md——给AI的项目说明书

**问题**：每次新开对话，都要重新告诉AI项目信息。

**方案**：在项目根目录创建 `CLAUDE.md`。

**模板**：
```markdown
# CLAUDE.md

## 项目概述
- 技术栈：TypeScript + React + Node.js
- 包管理：pnpm

## 编码规范
- 缩进：2空格
- 引号：单引号

## 常用命令
- 开发：pnpm dev
- 测试：pnpm test
- 构建：pnpm build
```

---

## Skills——把重复操作变成命令

**问题**：代码审查、写周报这些重复流程，每次都要描述一遍。

**方案**：用Skills封装成斜杠命令。

**目录**：
```
~/.claude/skills/           # 用户级
{project}/.claude/skills/   # 项目级
```

**模板**：
```markdown
---
description: 执行代码审查
triggers:
  - "review"
---

# 代码审查

## 检查清单
1. 代码风格是否符合规范
2. 是否存在安全漏洞
3. 测试是否充分
```

**安装**：
```bash
# 方式1：插件市场
claude plugin install code-reviewer

# 方式2：手动复制
cp -r skills/* ~/.claude/skills/
```

---

## planning-with-files——解决AI"健忘症"

**问题**：复杂任务做着做着，AI就忘了之前说的。

**方案**：用文件系统当AI的"外挂大脑"。

**安装**：
```bash
git clone https://github.com/OthmanAdi/planning-with-files.git
cp -r planning-with-files/skills/* ~/.claude/skills/
```

**三个核心文件**：

| 文件 | 作用 |
|------|------|
| `context.md` | 项目背景、技术栈、约束 |
| `plan.md` | 任务列表、完成状态 |
| `deliverable.md` | 验收标准 |

**使用**：
```bash
"用planning-with-files规划这次重构任务"
```

---

## Git Worktree——多任务并行开发

**问题**：同时开发多个功能，代码会冲突。

**方案**：用Worktree创建隔离的工作目录。

**命令**：
```bash
# 创建
git worktree add ../project-feature feature/new-feature

# 列出
git worktree list

# 删除
git worktree remove ../project-feature
```

**并行开发**：
```bash
# 创建3个隔离环境
git worktree add ../project-auth feature/auth
git worktree add ../project-api feature/api
git worktree add ../project-ui feature/ui

# 3个终端同时运行Claude Code
cd ../project-auth && claude "实现用户认证"
cd ../project-api && claude "重构API层"
cd ../project-ui && claude "优化首页性能"
```

---

## MCP——让AI连接外部服务

**问题**：AI无法操作数据库、浏览器。

**方案**：配置MCP服务器。

**命令**：
```bash
# 添加
claude mcp add-json filesystem '{
  "command": "npx",
  "args": ["-y", "@anthropic-ai/mcp-server-filesystem", "/allowed/path"]
}'

# 查看已安装
claude mcp list

# 删除
claude mcp remove filesystem
```

**配置示例**：
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-filesystem", "/projects"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-postgres"],
      "env": {"DATABASE_URL": "postgresql://localhost/mydb"}
    }
  }
}
```

---

## Subagent——把子任务"外包"

**问题**：复杂任务需要不同专家处理。

**方案**：创建专门的Subagent。

**内置类型**：Explore（探索代码）、Plan（规划方案）、general-purpose（通用）

**自定义配置**：
```yaml
# .claude/subagents/code-reviewer.yaml
name: code-reviewer
model: sonnet
description: 专门负责代码审查
tools:
  - Read
  - Grep
  - Glob
prompt: |
  你是专业代码审查员。
  检查代码质量、安全性、性能。
```

**调用**：
```bash
"用code-reviewer审查这段代码"
"/code-reviewer 检查src/auth模块"
```

---

## 常用命令速查表

| 命令 | 功能 |
|------|------|
| `/compact` | 压缩上下文 |
| `/context` | 查看上下文占用 |
| `/clear` | 清除对话 |
| `/cost` | 查看token消耗 |
| `/model` | 切换模型 |
| `/init` | 初始化CLAUDE.md |

**Git Worktree**：
```bash
git worktree add <path> <branch>    # 创建
git worktree list                   # 列出
git worktree remove <path>          # 删除
```

**MCP**：
```bash
claude mcp add <name> <cmd>         # 添加
claude mcp list                     # 列出
claude mcp remove <name>            # 删除
```

---

## 实战案例——从0到1配置项目

**场景**：新建Next.js项目，配置Claude Code环境。

**步骤**：

```bash
# 1. 创建项目
npx create-next-app@latest my-app && cd my-app

# 2. 初始化CLAUDE.md
claude
/init

# 3. 安装planning-with-files
git clone https://github.com/OthmanAdi/planning-with-files.git /tmp/pwf
cp -r /tmp/pwf/skills/* ~/.claude/skills/

# 4. 创建第一个Skill
mkdir -p .claude/skills/component-creator
# 编写SKILL.md...

# 5. 配置MCP（可选）
claude mcp add-json filesystem '{...}'

# 6. 验证
ls ~/.claude/skills/
claude mcp list
```

**完整目录结构**：
```
my-app/
├── .claude/
│   └── skills/
│       └── component-creator/SKILL.md
├── CLAUDE.md
└── src/
```

---

## 总结

| 技巧 | 解决的问题 |
|------|-----------|
| CLAUDE.md | 重复解释项目信息 |
| Skills | 重复描述操作流程 |
| planning-with-files | AI"健忘"问题 |
| Git Worktree | 并行开发冲突 |
| MCP | AI无法操作外部服务 |
| Subagent | 任务需要不同专家 |

**核心原则**：把信息写进文件，不要指望AI记住所有东西。