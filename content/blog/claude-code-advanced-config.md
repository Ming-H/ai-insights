---
title: "Claude Code 高级配置完全指南"
date: 2026-03-23
draft: false
tags: ["Claude Code", "教程", "配置"]
categories: ["博客"]
description: "CLAUDE.md、Skills、Agents、Permissions 四大配置支柱的完整指南。"
---

## 第一章：为什么需要高级配置？

刚装好 Claude Code，写了几行代码，感觉还行。但随着项目变大，问题来了——每次都要重复解释项目结构，Claude 总是忘记你的编码规范，复杂的重构任务需要反复沟通才能推进。

这不是 Claude 的问题，是**配置**的问题。

大多数用户把 `.claude/` 文件夹当成黑盒。知道它存在，看到它出现在项目根目录，但从未打开过，更不用说理解里面每个文件的作用。

这是巨大的机会浪费。

`.claude/` 文件夹是控制 Claude 在项目中行为的控制中心。它存放你的指令、自定义命令、权限规则，甚至跨会1会1的1的记忆。一旦理解什么放在哪里、为什么，就能把 Claude Code 配置成团队需要的样子。

Claude Code 有**四大配置支柱**：

| 支柱 | 作用 | 配置位置 | 核心价值 |
|------|------|----------|----------|
| CLAUDE.md | 项目级指令 | 项目根目录 | **持久记忆** - 每次对话自动加载 |
| Skills | 扩展能力 | `.claude/skills/` | **智能触发** - 匹配描述自动激活 |
| Agents | 多Agent协作 | `.claude/agents/` | **上下文隔离** - 保护主对话窗口 |
| Permissions | 安全边界 | `.claude/settings.json` | **风险控制** - 防止误操作 |

读完这篇指南，你会掌握这四大支柱的完整配置方法。

## 第二章：两个文件夹，不是一个

深入之前，有一点需要提前知道：实际上有**两个** `.claude/` 目录，不是一个。

**项目级** `.claude/` 存放在项目内部。你提交到 git。团队每个人获得相同的规则、相同的自定义命令、相同的权限策略。

**用户级** `~/.claude/` 存放在你的主目录。存放你的个人偏好和机器本地状态，比如会话历史和自动记忆。

### 加载优先级（从高到低）

| 优先级 | 位置 | 作用范围 | 使用场景 |
|--------|------|----------|----------|
| 1 (最高) | CLI 参数 `--agent` | 当前会话 | 临时测试、快速切换 |
| 2 | 项目级 `.claude/` | 当前项目 | 团队共享、项目特定 |
| 3 | 用户级 `~/.claude/` | 所有项目 | 个人偏好、通用配置 |
| 4 (最低) | 插件级 | 插件启用时 | 第三方扩展 |

**关键理解**：同名配置时，高优先级覆盖低优先级。这意味着你可以在用户级设置通用配置，在项目级覆盖特定项目的需求。

### 目录结构全景

```
your-project/
├── CLAUDE.md                  # 团队指令（提交到git）
├── CLAUDE.local.md            # 你的个人覆盖（gitignored）
│
└── .claude/
    ├── settings.json          # 权限+配置（提交）
    ├── settings.local.json    # 个人权限覆盖（gitignored）
    │
    ├── commands/              # 自定义斜杠命令
    │   ├── review.md          # → /project:review
    │   └── fix-issue.md       # → /project:fix-issue
    │
    ├── rules/                 # 模块化指令文件
    │   ├── code-style.md
    │   └── api-conventions.md
    │
    ├── skills/                # 自动触发的工作流
    │   ├── security-review/
    │   │   └── SKILL.md
    │   └── deploy/
    │       └── SKILL.md
    │
    └── agents/                # 专门的子Agent
        ├── code-reviewer.md
        └── security-auditor.md

~/.claude/
├── CLAUDE.md              # 你的全局指令
├── settings.json          # 你的全局设置
├── commands/              # 你的个人命令（所有项目）
├── skills/                # 你的个人技能（所有项目）
├── agents/                # 你的个人Agent（所有项目）
└── projects/              # 会话历史+自动记忆
```

## 第三章：CLAUDE.md - Claude 的指令手册

CLAUDE.md 是**整个系统中最重要的文件**。启动 Claude Code 会话时，它读取的第一件事就是 CLAUDE.md。直接加载到系统提示词，并在整个对话中保持在上下文中。

简单说：你在 CLAUDE.md 里写的任何内容，Claude 都会遵循。

如果你告诉 Claude "实现前总是写测试"，它就会。如果你说"永远不要用 console.log 做错误处理，总是用自定义日志模块"，它每次都会遵守。

### 多级 CLAUDE.md

项目根目录的 CLAUDE.md 是最常见设置。但你还可以：

- `~/.claude/CLAUDE.md` - 跨所有项目的全局偏好
- 子目录内的 CLAUDE.md - 文件夹级别的特定规则

Claude 会读取并**组合**所有这些文件。

### 什么应该放在 CLAUDE.md？

大多数人要么写太多，要么写太少。这里是有

**应该写**：
- 构建、测试、lint 命令（`npm run test`、`make build` 等）
- 关键架构决策（"我们使用 Turborepo 的 monorepo"）
- 不明显的坑点（"TypeScript 严格模式下，未使用的变量是错误"）
- 导入约定、命名模式、错误处理风格
- 主模块的文件和文件夹结构

**不应该写**：
- 属于 linter 或 formatter 配置的内容
- 已经有链接的完整文档
- 解释理论的长段落

**保持 CLAUDE.md 在 200 行以内**。超过这个长度的文件开始消耗太多上下文，Claude 的指令遵守率实际上会下降。

### 最小但有效的示例

```markdown
# Project: Acme API

## Commands
npm run dev          # Start dev server
npm run test         # Run tests (Jest)
npm run lint         # ESLint + Prettier check
npm run build        # Production build

## Architecture
- Express REST API, Node 20
- PostgreSQL via Prisma ORM
- All handlers live in src/handlers/
- Shared types in src/types/

## Conventions
- Use zod for request validation in every handler
- Return shape is always { data, error }
- Never expose stack traces to the client
- Use the logger module, not console.log

## Watch out for
- Tests use a real local DB, not mocks. Run `npm run db:test:reset` first
- Strict TypeScript: no unused imports, ever
```

大约 20 行。给了 Claude 在此代码库中高效工作所需的一切，无需持续澄清。

### CLAUDE.local.md - 个人覆盖

有时你有特定于自己的偏好，不是整个团队的。也许你偏好不同的测试运行器，或者想让 Claude 总是用特定模式打开文件。

在项目根目录创建 `CLAUDE.local.md`。Claude 会与主 CLAUDE.md 一起读取，并且会自动 gitignore，所以你的个人调整永远不会进入仓库。

### rules/ 文件夹 - 可扩展的模块化指令

CLAUDE.md 对单个项目很有效。但团队增长后，你最终会得到一个 300 行的 CLAUDE.md，没人维护，所有人都忽略。

**rules/ 文件夹解决这个问题。**

`.claude/rules/` 内的每个 markdown 文件都会与你的 CLAUDE.md 一起自动加载。不再是一个巨大的文件，而是按关注点拆分指令：

```
.claude/rules/
├── code-style.md
├── testing.md
├── api-conventions.md
└── security.md
```

每个文件保持专注且易于更新。负责 API 约定的团队成员编辑 `api-conventions.md`。负责测试标准的人编辑 `testing.md`。没人互相踩踏。

### 路径作用域规则

真正的力量来自**路径作用域规则**。在规则文件中添加 YAML frontmatter 块，它只在 Claude 处理匹配文件时激活：

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "src/handlers/**/*.ts"
---

# API Design Rules

- All handlers return { data, error } shape
- Use zod for request body validation
- Never expose internal error details to clients
```

当 Claude 编辑 React 组件时，不会加载这个文件。只有在 `src/api/` 或 `src/handlers/` 内工作时才加载。

没有 `paths` 字段的规则会在每个会话无条件加载。

## 第四章：Commands - 自定义斜杠命令

开箱即用，Claude Code 有内置的斜杠命令如 `/help` 和 `/compact`。**commands/ 文件夹让你添加自己的命令。**

放入 `.claude/commands/` 的每个 markdown 文件都会变成一个斜杠命令。

`review.md` 文件创建 `/project:review`。`fix-issue.md` 文件创建 `/project:fix-issue`。**文件名就是命令名。**

### 创建第一个命令

创建 `.claude/commands/review.md`：

```markdown
---
description: Review the current branch diff for issues before merging
---

## Changes to Review

!`git diff --name-only main...HEAD`

## Detailed Diff

!`git diff main...HEAD`

Review the above changes for:
1. Code quality issues
2. Security vulnerabilities
3. Missing test coverage
4. Performance concerns

Give specific, actionable feedback per file.
```

在 Claude Code 中运行 `/project:review`，它会自动将真实的 git diff 注入提示词，然后 Claude 才看到它。

**`!` 反引号语法**运行 shell 命令并嵌入输出。这就是让这些命令真正有用而不是只是保存文本的原因。

### 向命令传递参数

使用 `$ARGUMENTS` 传递命令名后的文本：

```markdown
---
description: Investigate and fix a GitHub issue
argument-hint: [issue-number]
---

Look at issue #$ARGUMENTS in this repo.

!`gh issue view $ARGUMENTS`

Understand the bug, trace it to the root cause, fix it, and write a test that would have caught it.
```

运行 `/project:fix-issue 234` 会将 issue 234 的内容直接输入提示词。

### 项目命令 vs 个人命令

`.claude/commands/` 中的项目命令会被提交并与团队共享。对于你想在所有项目中使用的命令，放在 `~/.claude/commands/`。这些会显示为 `/user:command-name`。

**有用的个人命令示例**：每日站会助手、按你的约定生成提交消息的命令、快速安全扫描。

## 第五章：Skills - 按需复用的工作流

你现在知道命令如何工作。**Skills 表面上看起来类似，但触发机制根本不同。**

**命令等待你**。**Skills 观察对话并在时机合适时行动。**

每个 Skill 存放在自己的子目录中，包含一个 SKILL.md 文件：

```
.claude/skills/
├── security-review/
│   ├── SKILL.md
│   └── DETAILED_GUIDE.md
└── deploy/
    ├── SKILL.md
    └── templates/
        └── release-notes.md
```

### SKILL.md 使用 YAML frontmatter 描述何时使用：

```markdown
---
name: security-review
description: Comprehensive security audit. Use when reviewing code for
  vulnerabilities, before deployments, or when the user mentions security.
allowed-tools: Read, Grep, Glob
---

Analyze the codebase for security vulnerabilities:

1. SQL injection and XSS risks
2. Exposed credentials or secrets
3. Insecure configurations
4. Authentication and authorization gaps

Report findings with severity ratings and specific remediation steps.
Reference @DETAILED_GUIDE.md for our security standards.
```

当你说"review this PR for security issues"，时，Claude 读取描述，识别匹配，并自动调用这个 skill。你也可以用 `/security-review` 显式调用。

**与命令的关键区别**：skills 可以捆绑支持文件。上面的 `@DETAILED_GUIDE.md` 引用会引入存放在 SKILL.md 旁边的详细文档。命令是单个文件。Skills 是包。

### Frontmatter 完整字段

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | 否 | 斜杠命令名称（默认用目录名） |
| `description` | **推荐** | Claude 何时自动使用此 Skill |
| `allowed-tools` | 否 | 限制可用工具（白名单） |
| `disable-model-invocation` | 否 | `true` 阻止自动触发 |
| `user-invocable` | 否 | `false` 从 `/` 菜单隐藏 |

### 触发方式详解

**自动触发**：当你的请求匹配 `description` 时：

```markdown
---
description: Fix GitHub issues. Use when user says "fix issue" or "解决bug"
---

修复 GitHub issue $ARGUMENTS...
```

用户说："修复 issue 123"，Claude 自动加载此 Skill。

**手动触发**：输入 `/skill-name` 直接调用。

**参数传递**：

```markdown
---
name: migrate
description: 迁移组件
---

将 $0 从 $1 迁移到 $2：
- $ARGUMENTS[0] = 第一个参数
- $ARGUMENTS[1] = 第二个参数
- $2 = 简写形式
```

调用 `/migrate Header React Vue`：
- `$0` → `Header`
- `$1` → `React`
- `$2` → `Vue`

### 动态上下文注入

使用 `` !`command` `` 语法执行命令并注入结果：

```markdown
---
name: pr-summary
description: 总结 PR 变更
---

## PR 上下文
- **Diff**: !`git diff main...HEAD`
- **Files**: !`git diff --name-only main...HEAD`
- **Stats**: !`git diff --stat main...HEAD`

## 任务
总结以上变更，重点关注：
1. 改动范围
2. 潜在风险
3. 测试建议
```

### Skill 在子进程中运行

```markdown
---
name: deep-research
description: 深度代码研究
context: fork
agent: Explore
---

研究 $ARGUMENTS：

1. 使用 Glob 和 Grep 查找相关文件
2. 分析代码结构
3. 返回简洁总结
```

**好处**：
- 隔离上下文，不污染主对话
- 可以并行执行多个研究任务
- 自动总结返回关键信息

## 第六章：Agents - 专门的子Agent

当任务复杂到需要专门专家时，可以在 `.claude/agents/` 中定义子Agent 人格。每个 Agent 是一个 markdown 文件，有自己的系统提示词、工具访问权限和模型偏好：

```
.claude/agents/
├── code-reviewer.md
└── security-auditor.md
```

### 创建 code-reviewer.md

```markdown
---
name: code-reviewer
description: Expert code reviewer. Use PROACTIVELY when reviewing PRs,
  checking for bugs, or validating implementations before merging.
model: sonnet
tools: Read, Grep, Glob
---

You are a senior code reviewer with a focus on correctness and maintainability.

When reviewing code:
- Flag bugs, not just style issues
- Suggest specific fixes, not vague improvements
- Check for edge cases and error handling gaps
- Note performance concerns only when they matter at scale
```

当 Claude 需要进行代码审查时，它会在自己的隔离上下文窗口中生成这个 agent。Agent 完成工作，压缩发现，然后报告回来。你的主会话不会被数千 token 的中间探索所混乱。

### Agent 配置字段

| 字段 | 说明 |
|------|------|
| `name` | Agent 名称 |
| `description` | Claude 何时委托给此 Agent |
| `tools` | 允许的工具列表（白名单） |
| `model` | 使用的模型（`haiku` 快 / `sonnet` 平衡 / `opus` 深度） |
| `permissionMode` | 权限模式 |
| `maxTurns` | 最大轮数限制 |

### 调用 Agent

**自然语言**：
```
让 code-reviewer agent 审查最近的改动
```

**@ 提及**：
```
@"code-reviewer (agent)" 审查认证模块的改动
```

**并行执行**：
```
并行研究认证模块、数据库模块和 API 模块
```

Claude 会启动三个独立的 Explore agent，每个负责一个模块，最后综合结果。

### 模型选择策略

| 模型 | 适用场景 |
|------|----------|
| `haiku` | 快速只读探索、简单任务 |
| `sonnet` | 大多数任务、平衡性能 |
| `opus` | 复杂推理、深度分析 |

`tools` 字段限制 agent 能做什么。安全审计员只需要 Read、Grep 和 Glob。它不应该写文件。这个限制是刻意的，值得明确。

## 第七章：Permissions - 安全边界

`.claude/` 内的 `settings.json` 控制 Claude 可以和不可以做什么。定义 Claude 可以运行哪些工具、可以读取哪些文件，以及运行某些命令前是否需要询问。

### 完整配置示例

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Read",
      "Write",
      "Edit"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

### 字段说明

**`$schema`**：在 VS Code 或 Cursor 中启用自动完成和内联验证。始终包含它。

**`allow` 列表**：包含无需 Claude 请求确认就能运行的命令。对于大多数项目，好的 allow 列表覆盖：
- `Bash(npm run *)` 或 `Bash(make *)` - Claude 可以自由运行你的脚本
- `Bash(git *)` - 只读 git 命令
- `Read`、`Write`、`Edit`、`Glob`、`Grep` - 文件操作

**`deny` 列表**：包含完全阻止的命令，无论如何。合理的 deny 列表阻止：
- 破坏性 shell 命令如 `rm -rf`
- 直接网络命令如 `curl`
- 敏感文件如 `.env` 和 `secrets/` 中的任何内容

**中间地带**：如果某事不在两个列表中都没有，Claude 会在继续之前询问。这个中间地带是刻意的。它给你一个安全网，而不必预先预期每个可能的命令。

### 权限模式

| 模式 | 行为 |
|------|------|
| `default` | 标准权限检查，未匹配的工具触发确认提示 |
| `acceptEdits` | 自动接受文件编辑 |
| `dontAsk` | 未预先批准的工具直接拒绝 |
| `bypassPermissions` | 跳过所有权限检查（谨慎使用） |

### settings.local.json - 个人覆盖

与 `CLAUDE.local.md` 相同的想法。创建 `.claude/settings.local.json` 存放你不想提交的权限更改。它会自动 gitignore。

## 第八章：从能用到好用

### 配置演进路径

**阶段1：基础**（1分钟）
```
CLAUDE.md        # 项目说明 + 常用命令
```

**阶段2：规范**（10分钟）
```
CLAUDE.md
.claude/
└── settings.json  # 配置权限
```

**阶段3：效率**（30分钟）
```
CLAUDE.md
.claude/
├── settings.json
├── commands/
│   ├── commit/
│   └── review/
└── agents/
    └── code-reviewer.md
```

**阶段4：团队**（1小时+）
```
CLAUDE.md
.claude/
├── settings.json
├── commands/          # 5-10 个
├── rules/             # 模块化指令
├── skills/            # 自动触发工作流
└── agents/            # 3-5 个
```

### 最佳实践

1. **CLAUDE.md 具体、可操作**
   - ✅ "组件命名用 PascalCase"
   - ❌ "遵循最佳实践"

2. **Skills 单一职责**
   - 一个 Skill = 一个任务
   - 复杂流程拆成多个 Skill

3. **Agents 用于隔离**
   - Explore agent：快速只读探索
   - 后台 agent：长时间任务
   - 主对话：需要频繁交互的任务

4. **Permissions 从严到宽**
   - 新项目：`default` 模式
   - 熟悉后：`acceptEdits` 模式
   - CI/CD：`dontAsk` 模式

### 常见问题

**Q: 配置不生效？**
```
1. 检查优先级：CLI > 项目 > 用户 > 插件
2. 确认文件位置正确
3. 重启 Claude Code
```

**Q: Skill 没触发？**
```
1. description 包含用户会说的关键词
2. 尝试手动 /skill-name
3. 检查是否有同名 Skill 被覆盖
```

**Q: Agent 太慢？**
```
1. 使用 model: haiku
2. 限制 tools 列表
3. 设置 maxTurns
```

### 实用起步配置

**步骤1**：在 Claude Code 中运行 `/init`。它会通过读取你的项目生成一个入门 CLAUDE.md。把它编辑到要点。

**步骤2**：添加 `.claude/settings.json`，包含适合你技术栈的 allow/deny 规则。至少，允许你的运行命令并拒绝 .env 读取。

**步骤3**：为你最常做的工作流创建一两个命令。代码审查和 issue 修复是好的起点。

**步骤4**：随着项目增长，CLAUDE.md 变得拥挤，开始将指令拆分到 `.claude/rules/` 文件中。在有意义的地方按路径作用域。

**步骤5**：添加 `~/.claude/CLAUDE.md` 存放你的个人偏好。可能是"总是在实现前写类型"或"偏好函数式模式而非基于类的"。

这真的是 95% 项目所需的全部。当你有值得打包的重复复杂工作流时，Skills 和 Agents 才派上用场。

---

`.claude/` 文件夹本质上是一个协议，用于告诉 Claude 你是谁、你的项目做什么、它应该遵循什么规则。你定义得越清晰，花在纠正 Claude 上的时间就越少，它花在做有用工作上的时间就越多。

**CLAUDE.md 是你最高杠杆的文件。先把它做好。其他都是优化。**

**从小开始，边做边改进，把它当作项目中任何其他基础设施一样对待：一旦正确设置，每天都会产生回报。**