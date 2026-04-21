---
title: "Claude Code 从入门到精通 - 全文"
date: 2026-04-15
draft: false
description: "Anthropic 官方 AI 编程助手完全指南"
type: books
---

# Part 1: 概念

## §01 你的新同事不是人
Your New Teammate Is Not Human
你刚入职一家公司，工位旁边坐着一个新同事。它不喝咖啡、不摸鱼、不需要午休，24 小时待命。它能在 3 秒内读完一个 500 行的文件，能在 10 秒内告诉你某个 bug 藏在哪一行，能在 30 秒内把一个 Python 脚本改写成 TypeScript。
但它不是人。它是 Claude Code，Anthropic 的官方命令行编程助手。
你的第一反应可能是：又一个 AI 编程工具？Copilot 我还没用明白呢。
我理解这种疲惫。2023 年 GitHub Copilot 掀起 AI 辅助编程热潮，2024 年 Cursor 凭借 AI-First IDE 杀入战场。那段时间你的朋友圈大概率被"AI 要取代程序员"刷过屏。热潮还没完全散去，又一个新东西冒出来了。
2025 年，Anthropic 发布了 Claude Code。和之前的工具不一样，它不是插件，不是 IDE，而是一个跑在终端里的完整编程伙伴。
### 三个问题，一次性回答
**Claude Code 是什么？** 一个命令行工具。你在终端里输入 `claude`，然后像跟同事聊天一样描述你想做的事。它会自己读文件、写代码、跑测试、查文档——不需要你一步步指挥。
**它和 Copilot、Cursor 有什么不同？** Copilot 像高级自动补全，你写代码它接龙。Cursor 像带 AI 的编辑器，你点按钮它响应。Claude Code 像一个独立工作的同事，你给目标，它自己想办法完成。
**为什么要用 CLI 而不是 IDE 插件？** 因为 CLI 更接近开发者的真实工作环境。你的代码在文件系统里，你的构建工具在终端里，你的部署脚本在 shell 里。Claude Code 直接在这个环境里工作，不需要通过 IDE 的"窗口"来观察世界。
### 一个类比：从手动工具到万能工具台
把你的开发环境想象成一个工坊。以前的 AI 工具像电动螺丝刀——在你拧螺丝的时候帮你一把。
Claude Code 是一整个工具台。上面摆着 20 多种工具：读文件的放大镜、写代码的刻刀、搜索代码的探照灯、跑命令的扳手。工具台旁边还有一本说明书（CLAUDE.md，一个 Markdown 配置文件，用来记录项目规范和编码偏好），记录了你的项目规范和编码习惯。工具台背后有一排电源插座（MCP 协议，Model Context Protocol，一种让 AI 调用外部工具的开放协议），可以外接数据库、API、设计工具。工具台还有画图纸的桌子（Plan Mode，一种先规划后执行的工作模式），可以先把方案想清楚再动手。
最关键的是，这个工具台自己会学习。你用了几次之后，它知道你偏好 TypeScript 而不是 JavaScript，知道你用 Vitest 而不是 Jest，知道你写代码喜欢先写测试。
### 横向对比：一次看清楚
| 维度 | Claude Code | GitHub Copilot | Cursor | Windsurf |
|------|-------------|----------------|--------|----------|
| 形态 | CLI 命令行 | IDE 插件 | 独立 IDE | 独立 IDE |
| 交互方式 | 自然语言对话 | 代码补全+对话 | 对话+补全 | Cascade 流 |
| 自主程度 | 高（自己读文件、跑命令） | 低（你写它补） | 中（需手动触发） | 中高 |
| 上下文范围 | 整个项目文件系统 | 当前打开的文件 | 项目级 | 项目级 |
| 可扩展性 | MCP 协议+自定义 Agent | 有限 | 插件系统 | 有限 |
| 记忆能力 | CLAUDE.md + 自动记忆 | 无持久记忆 | .cursorrules | 有限 |
| 定价 | $20-200/月 或按 Token（Token 是 AI 处理文本的基本单位，约 1 个中文字 ≈ 1-2 Token） | $10-39/月 | $20-40/月 | 免费到付费 |
差距最大的两个维度是自主程度和可扩展性。Claude Code 不等你一步步喂指令，它能自己读代码、跑测试、查错误日志。MCP 协议让它能连接几乎任何外部服务——数据库、Figma（Figma，一款主流在线设计工具）、Slack、GitHub API。
> **核心建议**
>
> 如果你只是想在写代码时有个智能补全，Copilot 就够用了。如果你想要一个能独立完成完整任务的编程搭档——从理解需求到交付代码——Claude Code 是目前最接近这个目标的选择。
满足以下任意一条，就接着看：
- 你用过 AI 编程工具，但觉得它们"不够聪明"
- 你想了解 CLI 形态的 AI 工具到底能做到什么程度
- 你的团队在考虑引入 AI 编程工具，需要做技术选型
- 你对 Agent 和 MCP 这些概念好奇
接下来的章节，我们从安装配置开始，一步步搭建你的工具台。
## §02 十分钟，从安装到跑起来
From Zero to Running in Ten Minutes
别急着学原理。先用起来。
很多教程喜欢先讲一堆概念，等你看到实操部分的时候，热情已经凉了一半。这章反过来：先让你把 Claude Code 跑起来，亲身感受一下它的工作方式。有了体感之后，后面的原理解释才有锚点。
### 三种安装方式，选一种就行
| 方式 | 命令 | 适合谁 |
|------|------|--------|
| 原生安装 | `curl -fsSL https://claude.ai/install.sh \| bash` | 大多数人（推荐） |
| Homebrew | `brew install --cask claude-code` | Mac 用户 |
| npm | `npm install -g @anthropic-ai/claude-code` | Node.js 开发者 |
原生安装最简单。打开终端，粘贴那行命令，回车。脚本会自动检测你的操作系统，把 Claude Code 装到合适的位置，配好环境变量。整个过程不超过 30 秒。
Windows 用户用 PowerShell：

```powershell
irm https://claude.ai/install.ps1 | iex
```
### 安装后的第一次启动
装好之后，输入：

```bash
claude
```

第一次运行会打开浏览器，让你登录 Anthropic 账户。登录完成后回到终端，你会看到欢迎信息和闪烁的光标。
试试这个：

```text
帮我看看当前目录有什么文件，分析一下项目结构
```

Claude Code 会读取当前目录的文件，给出项目结构分析。它不是在猜——它真的在用内置的 Read、Glob、LS 工具读取你的文件系统。
### 五个基本操作，立刻掌握
**1. 直接对话**
```text
解释一下 @src/index.ts 的入口逻辑
```
`@` 符号让 Claude 读取指定文件。
**2. 执行命令**
```bash
!git status
```
`!` 前缀直接运行 bash 命令，不用退出会话。
**3. 切换模型**
```text
/model opus
```
遇到复杂问题时切到 Opus 4.6，日常用 Sonnet 4.6 就够了。
**4. 查看花费**
```text
/cost
```
显示当前会话的 Token 用量和预估费用。
**5. 压缩上下文**
```text
/compact
```
对话太长时，压缩历史保留关键信息。
### 一个真实的初次体验
假设你有一个 Python 项目，想给它加上单元测试。你只需要说：

```text
帮我的 @src/calculator.py 写单元测试，用 pytest
```

Claude Code 会：
1. 读取 `src/calculator.py`，分析里面的函数
2. 根据函数逻辑生成测试用例
3. 创建测试文件并写入代码
4. 运行 `pytest` 验证测试通过
全程不需要你打开文件、写代码、跑命令。你只需要在终端里说一句话。
这就是 Claude Code 和传统 AI 编程工具的核心区别：它不只是建议代码，而是自己动手完成整个流程。
### 键盘快捷键，不用全记
| 快捷键 | 功能 |
|--------|------|
| Ctrl+C | 中断当前操作 |
| Ctrl+L | 清屏（不清历史） |
| Shift+Tab | 切换权限模式 |
| Esc Esc | 回退上一步操作 |
| Option+Enter | 多行输入（Mac） |
实际上你只需要记住 Ctrl+C（停下来）和 Shift+Tab（切权限），其他的用的时候再查。
### 常见安装问题
**"command not found: claude"**——环境变量没配好。试试 `source ~/.zshrc` 或重启终端。
**"Git is not installed"**——Windows 用户需要先装 Git for Windows。
**登录失败**——检查网络，确保能访问 claude.ai。
> **核心建议**
>
> 安装完成后，先在你能看懂的项目里试。挑一个你写过的 Python 或 JavaScript 项目，让 Claude 帮你加注释、写测试、重构代码。因为你能判断结果对不对，这样才能建立对工具的信任。
接下来我们开始拆解 Claude Code 的核心机制。你已经有了体感，现在该理解它为什么能做到这些了。下一章从工具箱开始——20 多个内置工具，每一个都有明确的分工。
# Part 2: 核心机制

## §03 工具箱：20 把专用工具
The Toolkit: 20+ Specialized Tools
你的工具台上摆着一排工具。每把工具都有特定用途：螺丝刀拧螺丝，扳手拧螺母，钳子剪线。Claude Code 的工具箱也一样——20 多个内置工具，每个都为特定任务优化过。
上一章你体验了 Claude Code 帮你写测试的全过程。现在拆开看：它是怎么做到的？答案是它调用了 4 个工具——Read 读取源文件，Write 创建测试文件，Bash 运行 pytest，Read 再次读取测试结果。整个过程就像一个熟练工在工具台前，拿起一件工具用完放下，再拿起下一件。
![Claude Code 工具系统架构](images/tool-system-architecture.png)
### 两类工具：读取和执行
Claude Code 的工具分成两大类：
**读取类**——观察和理解代码
- **Read**：读取文件内容，支持文本、图片、PDF、Jupyter Notebook
- **Grep**：用正则搜索文件内容（底层是 ripgrep，一个极快的命令行搜索工具）
- **Glob**：按文件名模式查找文件（替代 find/ls）
- **LS**：列出目录内容
**执行类**——修改和操作
- **Edit**：精确替换文件中的指定内容
- **Write**：创建新文件或完全覆盖文件
- **Bash**：执行任意 shell 命令
- **NotebookEdit**：编辑 Jupyter Notebook 的单元格
读取类工具让 Claude Code 能"看到"你的项目，执行类工具让它能"动手"修改。两类工具配合，就实现了从理解到行动的完整链路。
### 为什么不用纯 Bash？
你可能会想：直接用 Bash 的 `cat`、`sed`、`find` 不就行了？
不完全是。Claude Code 更倾向于使用专用工具，原因有三个：
1. **精确性**——Edit 工具做的是精确字符串替换，而 `sed` 在处理多行内容时容易出错
2. **可审计性**——每次工具调用都会显示给用户，专用工具的意图更清晰
3. **安全性**——专用工具有内置的安全检查，Bash 命令的破坏力更大
| 操作 | Claude Code 优先选择 | 而不是 |
|------|----------------------|--------|
| 看文件内容 | Read | `cat file` |
| 搜索代码 | Grep | `grep -r "pattern"` |
| 找文件 | Glob | `find . -name "*.ts"` |
| 改文件 | Edit | `sed -i 's/old/new/'` |
| 跑命令 | Bash | 只在没有专用工具时使用 |
### 工具调用的完整生命周期
当你对 Claude Code 说"帮我的 calculator.py 写测试"，背后发生了这些事：

```text
你: 帮我的 @src/calculator.py 写测试
  ↓
Claude 思考: 需要先用 Read 读取源文件
  ↓
工具调用: Read("src/calculator.py")
  ↓
Claude 思考: 分析函数，生成测试代码
  ↓
工具调用: Write("tests/test_calculator.py", test_code)
  ↓
Claude 思考: 运行测试验证
  ↓
工具调用: Bash("pytest tests/test_calculator.py")
  ↓
Claude: 测试全部通过，创建了 5 个测试用例
```

每次工具调用都会在终端显示，你能实时看到 Claude 在做什么。如果它做了你不想做的事，Ctrl+C 随时能停下来。
### 进阶工具：Agent 和搜索
除了基础的读写执行工具，Claude Code 还有几个进阶工具：
**Agent**——启动一个子进程来处理复杂任务。主进程像项目经理，子进程像专员。比如你可以让一个 Agent 专门去搜索代码库中所有的 SQL 注入风险。
**WebSearch**——搜索互联网获取最新信息。当你的问题涉及 API 变更、新版本特性时，Claude 会主动搜索。
**WebFetch**——抓取指定 URL 的内容。比如你想看某个 GitHub issue 的讨论，Claude 可以直接拉取。
### 定时与任务
**CronCreate / CronDelete / CronList**——Cron（定时任务调度器）管理。设定周期性任务，比如每天早上跑一遍 lint 检查。
**TaskCreate / TaskUpdate / TaskList**——结构化任务管理。跟踪多步骤任务的进度。
这些工具构成了 Claude Code 的能力边界。只要某个需求能分解成这些工具的组合调用，Claude Code 就能完成。
> **核心建议**
>
> 理解工具箱的范围，你就理解了 Claude Code 的能力边界。它能做任何"读文件→理解→写文件→跑命令"链路能覆盖的事。超出这个范围——比如需要 GUI 操作或物理设备交互——它做不到。遇到不确定的情况，直接问它："你能完成这个任务吗？"它会诚实回答。
工具是动作，但光有动作不够。工具台还需要一本说明书，告诉它你的项目规范和编码习惯。这就是下一章要讲的 CLAUDE.md 记忆系统。
## §04 记忆系统：给工具台写说明书
The Memory System: Writing the Workbench Manual
你第一次让 Claude Code 帮你写代码，它不知道你偏好 TypeScript 还是 JavaScript，不知道你用 Tabs 还是 Spaces，不知道你的项目用 React 还是 Vue。就像一个新来的同事，什么都得你口头交代。
但如果这个同事有一本笔记本，把你说过的每条规范都记下来，下次就不用重复了呢？
Claude Code 有两套记忆系统：CLAUDE.md（你写的说明书）和 Auto Memory（它自己做的笔记）。两套系统配合，让 Claude 从"什么都不知道的新人"变成"熟悉你习惯的老搭档"。
![Claude Code 记忆系统层级](images/memory-system-layers.png)
### CLAUDE.md 的三个层级
CLAUDE.md 不是单个文件，而是三层叠加的系统：
| 层级 | 文件位置 | 谁写的 | 共享范围 |
|------|----------|--------|----------|
| 用户级 | `~/.claude/CLAUDE.md` | 你自己 | 你的所有项目 |
| 项目级 | `./CLAUDE.md` | 团队 | 通过 Git 共享 |
| 本地级 | `./CLAUDE.local.md` | 你自己 | 仅本机 |
这三层不是覆盖关系，而是叠加关系。Claude 会把所有层的内容拼在一起，从通用到具体。
一个典型的项目层 CLAUDE.md 长这样：

```markdown
# 项目说明
Next.js 14 + TypeScript + TailwindCSS 电商项目
## 技术栈
- 状态管理: Zustand
- 数据库: Prisma + PostgreSQL
- 测试: Vitest + Playwright
## 代码规范
- 组件用函数式写法，不用 class
- 文件命名: 组件用 PascalCase，工具用 camelCase
- 每个组件文件不超过 200 行
```
就这么简单。不需要写成长篇大论，几条关键规则就够了。
### 加载机制：按需读取
Claude Code 启动时，会从当前目录往上逐级查找 CLAUDE.md 文件。找到的文件全部加载到上下文中。
子目录里的 CLAUDE.md 不会立刻加载，只有当 Claude 读取该目录下的文件时才会触发。这种按需加载的设计保证了上下文不会被无关信息占满。
还有一个导入系统，用 `@path/to/file` 语法引用其他文件：

```markdown
# 主 CLAUDE.md
@docs/api-conventions.md
@docs/testing-standards.md
```

导入深度最多 5 层。每层文件建议不超过 200 行。
### Auto Memory：它自己在记笔记
除了你写的 CLAUDE.md，Claude Code 还会自动记录信息。这些笔记存在 `~/.claude/projects/<project>/memory/` 目录下。
Auto Memory 记什么？
- 你在对话中纠正过的偏好（"不要用 var，用 const"）
- 项目中常用的命令和路径
- 你反馈过的错误和解决方案
- 你认可的代码风格
你不需要手动管理 Auto Memory。每次对话中，当你纠正 Claude 的行为或表达偏好时，它会自动判断要不要记下来。
用 `/memory` 命令可以查看和编辑这些记忆。
### 规则系统：模块化的指令
`.claude/rules/` 目录下的 `.md` 文件提供另一种组织方式。每个文件是一条独立的规则：
`.claude/rules/typescript.md`：
```markdown
TypeScript 严格模式。
所有变量必须有类型注解。
禁止使用 any。
```
规则文件支持 YAML frontmatter，可以指定只在特定文件类型下生效：

```markdown
---
paths: ["**/*.test.ts"]
---
测试文件规则：
- 使用 describe/it 结构
- 每个测试用例只测一件事
```

### 记忆系统对比
| 维度 | CLAUDE.md | Auto Memory | Rules |
|------|-----------|-------------|-------|
| 谁写的 | 你 | Claude 自己 | 你 |
| 持久性 | 永久（文件在就在） | 永久 | 永久 |
| 触发方式 | 会话启动时加载 | 会话启动时加载 | Claude 执行操作时检查 |
| 适合内容 | 项目规范、技术栈 | 偏好、习惯、历史决策 | 细粒度规则 |
| 共享 | 项目级可 Git 共享 | 仅本地 | 项目级可 Git 共享 |
> **核心建议**
>
> 开始一个新项目时，第一件事就是写 CLAUDE.md。哪怕只有 5 行也行。随着项目推进，每次你发现自己在对话中重复解释某条规则，就把它加进去。CLAUDE.md 是活的文档，和项目一起成长。
记忆系统解决了"知道做什么"的问题。但工具台的能力是有限的，能不能外接更多工具？下一章讲 MCP 协议——给工具台接上电源插座，让它的能力没有上限。
## §05 MCP 协议：无限扩展的能力
The MCP Protocol: Unlimited Extensibility
你的工具台有 20 多把工具，看起来够用了。但总有那么些时候，你需要连数据库、调 API、访问 Figma 设计稿——这些都不是内置工具能做的。
MCP（Model Context Protocol）就是工具台背后的电源插座。插上什么设备，工具台就多了什么能力。它是 Anthropic 制定的开放协议，让 Claude Code 能连接任何外部服务。
![MCP 协议交互流程](images/mcp-protocol-flow.png)
### 一个类比说清楚 MCP
把 MCP 想象成 USB 接口。你的电脑（Claude Code）有 USB 口（MCP 协议），你可以插上 U 盘（数据库）、打印机（CI/CD 系统）、摄像头（设计工具）。每个外设（MCP Server）都通过统一协议和电脑通信。
你不需要知道 U 盘内部的电路设计，插上就能用。MCP 也是这样——配置好连接，Claude Code 就自动获得新的工具。
### 四种传输方式
| 方式 | 说明 | 典型用途 |
|------|------|----------|
| stdio | 本地子进程通信 | 本地工具（数据库客户端、文件处理器） |
| SSE | HTTP 服务器推送 | 远程服务 |
| HTTP | 直接 HTTP 连接 | REST API 服务 |
| WS | WebSocket 连接 | 实时数据服务 |
大多数场景用 stdio 就够了。你只需要在项目根目录创建一个 `.mcp.json`：

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
    }
```
配置好后重启 Claude Code，它就多了一个 `query` 工具，可以直接查询你的 PostgreSQL 数据库。
### 配置方法：三种入口
**方法 1：项目级配置文件**
在项目根目录创建 `.mcp.json`，团队成员共享：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    }
```

**方法 2：命令行添加**

```bash
claude mcp add my-server -- npx -y @some/mcp-server
```
**方法 3：交互式管理**
在 Claude Code 会话中输入 `/mcp`，可以查看、添加、删除 MCP 服务器。
### MCP 的实际效果
假设你配置了 PostgreSQL 的 MCP 服务器。在 Claude Code 里，你可以直接说：

```text
查一下用户表中最近 7 天注册的用户数量
```
Claude 会调用 MCP 提供的 `query` 工具，执行 SQL 查询，返回结果。你不需要写 SQL，不需要打开数据库客户端。
再比如你配置了 GitHub MCP：

```text
看看我最近提交的 PR 有没有冲突
```
Claude 会调用 GitHub API 工具，检查 PR 状态。
### 和内置工具的关系
MCP 工具和内置工具在使用上没有区别。Claude 看到的都是"工具列表"，它根据任务需要选择合适的工具。你也不需要区分——该用内置工具的时候用内置的，需要外部服务时 MCP 会自动介入。
> **核心建议**
>
> 不要一开始就配一堆 MCP 服务器。先用内置工具干活，当你发现某个需求反复出现、且内置工具无法满足时，再去搜对应的 MCP Server。GitHub 上有一个社区维护的 MCP Server 列表，需要什么先去那里找。
工具有了，记忆有了，扩展也有了。但有些任务太复杂，不能闷头就干——得先想清楚方案。这就是下一章要讲的 Plan Mode 和 Agent 系统。
## §06 Plan Mode 与 Agent：思考再行动
Plan Mode and Agents: Think Before You Act
你拿到一个复杂需求："把这个单体应用拆成微服务架构。"直接动手改代码？那大概率改到一半发现方向错了，得推倒重来。
有经验的工程师会先画架构图、列迁移步骤、评估风险，想清楚再动手。Claude Code 也一样——Plan Mode 就是它的"画图纸"模式，Agent 就是它的"分工协作"模式。
![Agent 工作流](images/agent-workflow.png)
### Plan Mode：先看后做
启动 Plan Mode：

```text
/plan 把用户认证模块从单体架构拆成独立微服务
```
Claude Code 会进入只读模式。它只能读取文件、搜索代码，不能修改任何东西。它会：
1. 遍历代码库，找到所有和用户认证相关的文件
2. 分析模块间的依赖关系
3. 生成一份结构化的迁移计划
计划写好后，你审核。觉得方案可行，再让它执行。
### opusplan：聪明的混合策略
有一个特殊的模型别名 `opusplan`，它会根据阶段自动切换模型：
| 阶段 | 使用的模型 | 原因 |
|------|------------|------|
| 规划阶段 | Opus 4.6 | 需要深度推理，理解复杂架构 |
| 执行阶段 | Sonnet 4.6 | 日常编码够用，速度更快成本更低 |
用 `claude --model opusplan` 启动，或者在会话中用 `/model opusplan` 切换。
这个策略的效果很直观：规划时用最强的大脑想问题，执行时用够快的工具写代码。既不浪费算力，也不牺牲质量。
### Agent 系统：分工协作
有些任务适合拆给多个专员并行处理。Claude Code 的 Agent 系统就是这个设计。
**内置 Agent**
| Agent | 模型 | 能力 | 用途 |
|-------|------|------|------|
| Explore | Haiku（最快） | 只读 | 快速搜索和分析代码库 |
| Plan | 继承父级 | 只读 | 为 Plan Mode 做调研 |
| General-purpose | 继承父级 | 全部 | 复杂多步骤任务 |
**自定义 Agent**
在 `.claude/agents/` 目录创建 Markdown 文件，就能定义自己的 Agent：

```markdown
---
name: code-reviewer
description: 专注代码审查，检查安全和性能问题
tools: Read, Glob, Grep
model: sonnet
---
你是一个代码审查专家。检查代码中的：
- 安全漏洞（SQL 注入、XSS）
- 性能问题（N+1 查询、内存泄漏）
- 代码风格（命名规范、函数长度）
给出具体的问题位置和修改建议。
```

定义好之后，Claude Code 遇到代码审查任务时会自动调度这个 Agent。你也可以在命令行指定：

```bash
claude --agent code-reviewer
```
### Agent 的运行模式
**前台模式**——阻塞主对话，你需要等待 Agent 完成后才能继续操作。
**后台模式**——Agent 在后台运行，你可以继续做其他事。用 Ctrl+B 把任务放到后台。
**Worktree 隔离**——Agent 在一个独立的 Git Worktree 里工作，不会影响你的主分支。完成后你再决定要不要合并。
### Agent 的局限
Agent 不是万能的：
- Agent 不能嵌套——一个 Agent 不能再启动另一个 Agent
- Agent 只看到自己的系统提示，不继承主对话的完整上下文
- Agent 默认不继承主对话的 Skills
这些限制是为了防止资源失控。一个 Agent 已经能处理大多数复杂任务了。
> **核心建议**
>
> 遇到复杂任务时，用 Plan Mode 先想清楚。涉及多个子任务时，考虑用 Agent 并行处理。简单任务直接对话就好——不是所有事都需要过度设计。判断标准：这个任务如果交给人，你会不会先画个流程图？会的话就用 Plan Mode。
概念和机制讲完了。你已经知道工具台上每件东西是干什么的。接下来的章节，我们开始动手搭建——从安装配置到实际项目中的运用。下一章从安装开始，一步步把工具台搭起来。
# Part 3: 动手搭建

## §07 安装与配置：搭建你的工具台
Setting Up Your Workbench
> §02 已经介绍了基本安装流程，这章补充进阶配置和故障排查。
别跳过这章。我见过太多人安装出问题后直接放弃——90% 的"这工具不好用"其实是"我装错了"。
这章的目标很明确：10 分钟内让你的工具台运转起来，并且验证它能正常工作。
安装命令在 §02 已经给过了。这章补充为什么选原生安装、怎么验证、怎么连接 IDE。
### 验证安装

```bash
claude --version
```
看到版本号就说明装好了。如果提示 "command not found"，试试：

```bash
# 重新加载 shell 配置
source ~/.zshrc  # 或 ~/.bashrc
# 如果还不行，检查 PATH
which claude
```

### 登录与账户

```bash
claude
```
首次启动会打开浏览器，登录你的 Anthropic 账户。支持 Claude 订阅账户和 API Key。
| 账户类型 | 月费 | 说明 |
|----------|------|------|
| Pro | $20/月 | 适合日常使用 |
| Max | $100-200/月 | 重度用户，更多配额 |
| Team | $150/座/月 | 团队协作 |
| API | 按 Token 计费 | 最灵活，无上限 |
如果你只是试试，Pro 就够了。后续可以随时升级。
### 连接你的 IDE
Claude Code 不只是终端工具，它和编辑器也能配合。
**VS Code**——在扩展商店搜索 "Claude Code" 安装。装好后侧边栏多一个 Claude 面板，你当前打开的文件会自动共享给 Claude。
**JetBrains**——在插件市场搜索 "Claude Code [Beta]" 安装。支持 IntelliJ IDEA、PyCharm、WebStorm 等全家桶。快捷键 `Cmd+Esc`（Mac）或 `Ctrl+Esc`（Windows）快速唤起。
### 跑一个验证任务

```bash
cd your-project
claude
```

进入你的任意项目目录，然后说：

```text
列出当前项目的技术栈和目录结构
```

如果 Claude Code 正确读取了你的文件并给出合理分析——恭喜，工具台搭建完成。
> **核心建议**
>
> 验证安装是否成功，最简单的方法是让 Claude 做一件你能立刻判断对错的事。比如"列出当前目录的文件"或"读取 package.json 并告诉我用了哪些依赖"。如果你能确认结果是对的，说明安装没问题。
### 常见问题速查
| 问题 | 原因 | 解决 |
|------|------|------|
| command not found | PATH 没配 | `source ~/.zshrc` 或重启终端 |
| Git not found | Windows 缺 Git | 安装 Git for Windows |
| 登录超时 | 网络问题 | 检查能否访问 claude.ai |
| 权限被拒 | 文件权限 | `chmod +x ~/.claude/bin/claude` |
工具台搭好了。下一章开始第一次真正的对话——用 Claude Code 完成一个完整的小任务。
## §08 第一次对话：从 Hello World 开始
Your First Conversation
工具台搭好了，灯也亮了。现在该上手了。
这章会用一个完整的小项目带你体验 Claude Code 的全部交互模式。不是截一段代码贴给你看，而是从头到尾走一遍，让你知道"和 Claude Code 一起工作"到底是什么感觉。
### 启动会话的四种姿势
| 命令 | 场景 |
|------|------|
| `claude` | 正常的交互式对话 |
| `claude -p "问题"` | 非交互模式，输出直接管道友好 |
| `claude -c` | 继续上一次对话 |
| `claude -n "名字"` | 启动一个命名会话，方便后续恢复 |
日常用 `claude` 就行。`-p` 模式适合脚本集成，比如在 CI/CD 管道里调用 Claude。
### 基础交互：说人话就行
Claude Code 不需要你学什么特殊语法。像跟同事说话一样描述你的需求：

```text
帮我创建一个 Python Flask 应用，有一个 /api/health 接口返回当前时间
```

Claude 会理解意图，创建文件，写入代码。全程你能看到每一步工具调用。
### 三个特殊前缀
在对话中，有三个前缀语法很有用：
**`!` 前缀——直接跑命令**

```bash
!pip list
```

在 Claude Code 里直接执行 bash 命令，不用开另一个终端。输出会被 Claude 看到，保持上下文连贯。
**`@` 符号——提及文件**

```text
帮我优化 @src/utils.py 的性能
```

Claude 会读取这个文件再给出建议。比你自己复制粘贴代码块方便。
**`/` 斜杠——调用命令**
最常用的几个：
| 命令 | 功能 |
|------|------|
| `/help` | 查看所有命令 |
| `/cost` | 查看 Token 消耗 |
| `/compact` | 压缩对话历史 |
| `/clear` | 清空当前对话 |
| `/model opus` | 切换模型 |
### 实战：从零创建一个 API 服务
让我们用 Claude Code 从零搭建一个 Flask 项目。
**步骤 1：描述需求**

```text
在当前目录创建一个 Flask 项目：
- 主文件 app.py，包含 /api/health 和 /api/time 两个接口
- health 接口返回 {"status": "ok"}
- time 接口返回当前 UTC 时间
- 创建 requirements.txt
- 创建 .gitignore
```

Claude 会：
1. 用 Write 创建 `app.py`
2. 用 Write 创建 `requirements.txt`
3. 用 Write 创建 `.gitignore`
**步骤 2：安装依赖并运行**

```bash
!pip install -r requirements.txt
```

```bash
!python app.py
```

Claude 能看到服务启动的输出。
**步骤 3：测试接口**

```bash
!curl http://localhost:5000/api/health
```

如果返回 `{"status": "ok"}`，说明一切正常。
**步骤 4：让它自我改进**

```text
给这个项目加上错误处理和日志
```

Claude 会读取现有代码，添加 try-except 块和 logging 配置。
整个过程不到 5 分钟。你说了 4 句话，Claude Code 做了创建文件、安装依赖、启动服务、修改代码这些事。
### 多行输入：复杂需求的写法
有时候一句话说不完需求。Claude Code 支持多行输入：
**Mac**: `Option+Enter` 换行
**Windows/Linux**: `Alt+Enter` 换行
**通用**: `\` + `Enter` 换行

```text
帮我重构这个项目的数据层：
1. 把 SQLAlchemy 换成 SQLAlchemy 2.0 的 async 写法
2. 所有查询添加类型注解
3. 连接池配置放到环境变量
```

这样分条列出的需求，Claude 会逐项处理。
### 会话管理
Claude Code 的会话会自动保存。你可以：

```bash
/clear          # 清空当前对话
claude -c       # 继续上一次对话
claude -r abc123  # 恢复指定 ID 的会话
/fork           # 在当前节点分叉出一个新会话
```

`/fork` 特别好用——当你在对话中想试试不同的方向，但又不想丢失当前进展，fork 一下就行。
> **核心建议**
>
> 第一次使用 Claude Code 时，选一个你熟悉的项目。让 Claude 做一些你能立刻判断对错的事——加注释、写测试、重构函数。先建立信任，再让它做你不确定能不能做好的事。
现在你已经能和 Claude Code 流畅对话了。但每次都要重复交代项目规范？太低效。下一章我们写 CLAUDE.md，让 Claude 永远记得你的项目规范。
## §09 写好你的 CLAUDE.md
Writing Your CLAUDE.md
> §04 已经介绍了 CLAUDE.md 的三层层级（用户级/项目级/本地级）、加载机制、Auto Memory 和规则系统。这章聚焦实操：怎么写一份好用的 CLAUDE.md，以及常见错误。
想象一个新同事入职第一天。你花了半小时跟他讲项目的技术栈、代码规范、文件结构。第二天他又来问一样的问题。第三天还是。
Claude Code 如果没有 CLAUDE.md，就是这个状态——每次对话都从头开始。
CLAUDE.md 是你给工具台写的操作手册。写一次，Claude 每次启动都会读。
### 一个好的 CLAUDE.md 长什么样
不需要长篇大论。一个实用的 CLAUDE.md 通常就这几个部分：

```markdown
# 项目：电商平台后端
## 技术栈
- Python 3.11 + FastAPI
- SQLAlchemy 2.0 async
- PostgreSQL + Redis
- pytest + httpx
## 代码规范
- 函数名用 snake_case，类名用 PascalCase
- 每个函数必须有类型注解
- 所有 API 路由必须有 docstring
- 禁止使用 print()，用 logger
## 文件结构
- app/api/ — 路由定义
- app/models/ — 数据模型
- app/services/ — 业务逻辑
- tests/ — 测试文件镜像 app/ 结构
## 测试要求
- 新功能必须有对应测试
- API 测试用 httpx.AsyncClient
- 测试数据用 factory_boy 生成
```
25 行，覆盖了技术栈、规范、结构、测试四个维度。这比口述 10 次高效得多。
关于 CLAUDE.md 的三个层级（用户级、项目级、本地级）和导入系统，§04 已经详细讲过。这里不重复。
### 常见错误
**写太多**——200 行是上限，不是目标。10-50 行的 CLAUDE.md 通常最有效。
**写太抽象**——"代码要简洁"不是好规则。"函数不超过 30 行"才是。
**不更新**——项目规范变了，CLAUDE.md 没跟着变。每当你发现自己在对话中重复解释某条规则，就该把它加进去。
> **核心建议**
>
> CLAUDE.md 的最佳实践是渐进式编写。先写 5 行最关键的规则，用几天后发现缺什么再加。一个月下来，你会有一份精准、实用的项目说明书——而不用一次性花两个小时写完然后再也不看。
现在工具台有了操作手册。但它还缺少安全保护——如果 Claude 执行了不该执行的命令怎么办？下一章讲 Hooks，给工具台装上安全开关。
## §10 Hooks：安全开关与自动化
Hooks: Safety Switches and Automation
工具台上的电锯很强大，但没有安全护罩你不敢用。Hooks 就是 Claude Code 的安全护罩——在你执行操作之前检查一遍，执行之后自动处理一遍。
### Hooks 做什么
Hooks 在特定事件发生时触发自定义逻辑。比如：
- 编辑文件前自动备份
- 写入代码后自动格式化
- 执行 bash 命令前检查是否危险
- 每次提交前自动跑 lint
这些不需要你记得去做——Hooks 会自动执行。
### 11 个 Hook 事件
| 事件 | 触发时机 | 典型用途 |
|------|----------|----------|
| SessionStart | 会话启动 | 初始化环境变量 |
| PreToolUse | 工具调用前 | **拦截危险操作** |
| PostToolUse | 工具调用后 | 自动格式化、日志记录 |
| PostToolUseFailure | 工具调用失败 | 错误通知 |
| PermissionRequest | 权限弹窗 | 自定义权限逻辑 |
| PermissionDenied | 权限被拒 | 返回重试选项 |
| SubagentStart | Agent 启动 | Agent 环境初始化 |
| SubagentStop | Agent 完成 | 清理资源 |
| Stop | 回合结束 | 会话总结 |
| StopFailure | 回合失败 | 错误恢复 |
| UserPromptSubmit | 用户提交输入 | 检查/修改输入内容 |
最常用的是 PreToolUse（事前拦截）和 PostToolUse（事后处理）。
### 配置方法
在 `.claude/settings.json` 中配置：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/scripts/check-bash-safety.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$FILE_PATH\""
          }
        ]
      }
    ]
  }
```
这个配置做了两件事：
1. 执行 Bash 命令前先运行安全检查脚本
2. 编辑或写入文件后自动用 Prettier 格式化
### 实战案例 1：阻止危险命令
创建 `~/.claude/scripts/check-bash-safety.sh`：

```bash
#!/bin/bash
# 从 stdin 读取 JSON 输入
input=$(cat)
# 提取要执行的命令
command=$(echo "$input" | jq -r '.tool_input.command // empty')
# 危险命令黑名单
dangerous=("rm -rf /" "rm -rf ~" "DROP TABLE" "chmod 777" "> /dev/sda")
for pattern in "${dangerous[@]}"; do
  if [[ "$command" == *"$pattern"* ]]; then
    echo "阻止危险命令: $command" >&2
    exit 2
  fi
done
exit 0
```

退出码 2 表示阻止操作，0 表示放行。这个脚本会在 Claude 尝试执行 `rm -rf` 之类的命令时自动拦截。
### 实战案例 2：自动格式化
PostToolUse Hook 在编辑文件后自动格式化：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "if [[ \"$FILE_PATH\" == *.py ]]; then black \"$FILE_PATH\" && isort \"$FILE_PATH\"; fi"
          }
        ]
      }
    ]
  }
```
只对 Python 文件执行 Black 格式化和 isort 排序。
### 三种 Hook 类型
| 类型 | 说明 | 适合场景 |
|------|------|----------|
| command | 执行 shell 命令 | 格式化、检查、通知 |
| http | POST 到指定 URL | 外部系统集成 |
| llm | 让 Claude 自己判断 | 需要智能判断的场景 |
command 类型最常用。llm 类型适合复杂的判断逻辑——比如让 Claude 决定一个 commit message 是否规范。
### Hook 的注意事项
- PostToolUse 不能撤销已执行的操作（工具已经跑完了）
- 非交互模式（`-p`）下 PermissionRequest 不会触发
- Hook 的 shell 脚本要快速执行，太慢会影响体验
- Subagent 可以定义自己的 scoped hooks
> **核心建议**
>
> Hooks 最有价值的场景是安全防护和自动格式化。不要试图用 Hooks 把所有事情都自动化——过度 Hook 会让调试变得困难。先从阻止危险命令和代码格式化开始，有需要再加。
动手搭建完成。工具台装好了，说明书写了，安全开关也加了。接下来的章节进入实战场景——用 Claude Code 解决真实项目中的问题。
# Part 4: 实战场景

## §11 代码审查自动化
Automated Code Review
代码审查是开发流程里最耗时的环节之一。一个 PR 50 行改动，审查可能要花 30 分钟。如果有 10 个 PR 等着你审查呢？
Claude Code 不只是帮你写代码——它还能帮你审代码。而且它审得比你快，还不带情绪。
### 三种审查方式
**方式 1：直接对话**

```text
审查 @src/services/payment.py 的代码质量，关注安全和性能
```
Claude 会读取文件，从安全、性能、可维护性三个维度给出分析。你能在终端里实时看到它调用 Read 工具读取文件，然后逐条列出问题。
**方式 2：自定义 Agent**
创建 `.claude/agents/code-reviewer.md`：

```markdown
---
name: code-reviewer
description: 代码审查，关注安全和性能
tools: Read, Glob, Grep
model: sonnet
---
你是代码审查专家。对每个文件检查：
1. 安全漏洞：SQL 注入、XSS、敏感信息泄露
2. 性能问题：N+1 查询、不必要的循环、大对象拷贝
3. 代码质量：命名规范、函数长度、重复代码
输出格式：
- [严重] 问题位置 + 修改建议
- [建议] 改进方向
```

然后指定 Agent 执行审查：

```bash
claude --agent code-reviewer -p "审查 src/ 目录下所有最近修改的文件"
```
**方式 3：/autofix-pr**

```text
/autofix-pr
```
这个命令会监控你的 GitHub PR，CI 失败时自动修复。不需要你盯着 PR 等结果。
### 实战：审查一个 Django 视图
假设你有这样一个文件：

```python
# views.py — 用户注册接口
def register(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    # 直接拼接 SQL，存在注入风险
    query = f"INSERT INTO users (username, email) VALUES ('{username}', '{email}')"
    cursor.execute(query)
    # 密码没有哈希，明文存储
    user = User(username=username, password=password, email=email)
    user.save()
    return JsonResponse({"status": "ok"})
```

让 Claude 审查：

```text
审查 @views.py，重点关注安全问题
```

Claude 的输出会是这样的：

```text
发现 3 个安全问题：
[严重] SQL 注入风险（第 7-8 行）
username 和 email 直接拼入 SQL 字符串。攻击者可以通过 username 字段注入恶意 SQL。
建议：使用 Django ORM 或参数化查询。
[严重] 密码明文存储（第 11 行）
密码没有哈希处理，直接存入数据库。
建议：使用 make_password() 或 django.contrib.auth.hashers。
[中等] 缺少输入验证（第 3-5 行）
没有检查 username/email 格式，没有限制密码长度。
建议：使用 Django Form 或 serializer 做输入验证。
```

| 维度 | 人工审查 | Claude Code 审查 |
|------|----------|------------------|
| 速度 | 30 分钟/PR | 3 分钟/PR |
| 一致性 | 受情绪/疲劳影响 | 始终如一 |
| 覆盖面 | 可能遗漏 | 系统性扫描 |
| 深度 | 能理解业务逻辑 | 擅长模式识别 |
| 成本 | 人力时间 | ~$0.05/次 |
Claude 的优势在速度和一致性。它的劣势是不理解业务上下文——它不知道某个"看似冗余"的代码是为了兼容老客户端。所以最佳实践是 Claude 先扫一遍，人再过一遍。
### /security-review：专门的安全审查

```text
/security-review
```

这个内置命令专门做安全审查，比通用的代码审查更深入。它会分析未提交的代码变更，查找 OWASP Top 10 级别的漏洞。
### /simplify：代码质量审查

```text
/simplify
```

审查最近修改的代码，检查代码质量和效率问题。如果发现可以简化的地方，它会直接修复。
> **核心建议**
>
> 把 Claude Code 的代码审查当第一道筛子用。每个 PR 提交后，先让 Claude 过一遍安全和性能问题，清理掉明显的低级错误，然后人再审查业务逻辑和架构设计。这样人的审查效率能提高 3-5 倍。
代码审查是一个场景。下一个场景更复杂——从零搭建一个完整的项目脚手架。
## §12 项目脚手架搭建
Project Scaffolding
"新建一个项目"听起来很简单，但实际做起来至少要 30 分钟：选框架、配 ESLint、设 TypeScript、写 Dockerfile、配 CI/CD……这些重复劳动，Claude Code 能在 5 分钟内完成。
### 用 Plan Mode 先规划
不要直接说"帮我建个项目"。用 Plan Mode 先把方案想清楚：

```text
/plan 创建一个全栈项目：
- 前端 Next.js 14 + TailwindCSS
- 后端 Node.js + Express
- 数据库 PostgreSQL + Prisma
- 包含 Docker 开发环境
```

Claude 会进入只读模式，生成一份项目结构方案。你审核通过后再执行。
### 实战：搭建一个全栈项目
**步骤 1：让 Claude 创建项目结构**

```text
按照刚才的方案，创建完整的项目结构。先不要写具体代码，只创建文件和目录。
```

Claude 会用 Bash 和 Write 工具创建：

```text
project/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   ├── package.json
│   └── next.config.js
├── backend/
│   ├── src/
│   │   ├── routes/
│   │   ├── middleware/
│   │   └── prisma/
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml
└── README.md
```

**步骤 2：填充配置文件**

```text
填充所有配置文件的内容：
- 两个 package.json 加好所有依赖
- tsconfig.json 开启严格模式
- docker-compose.yml 包含 app 和 postgres 服务
- next.config.js 配置好 API 代理
```

**步骤 3：安装依赖**

```bash
!cd frontend && npm install
!cd backend && npm install
```
**步骤 4：写入口代码**

```text
创建后端的 Express 入口，包含基本的健康检查路由和 Prisma 连接。
创建前端的首页，显示项目名称和后端状态。
```
**步骤 5：验证**

```text
启动 Docker 环境，验证前后端能正常通信
```
全程 5 句对话指令，Claude Code 做了通常需要 30 分钟的手工活。
### 用 /batch 批量创建
如果有大量文件需要创建，用 `/batch` 命令可以并行处理：

```text
/batch 为每个数据模型创建对应的 CRUD 路由文件，模型列表从 @prisma/schema.prisma 读取
```
`/batch` 会为每个模型启动一个独立的 Agent，在隔离的 Git Worktree 里工作，完成后合并。10 个模型同时创建，速度是串行的 5-8 倍。
### 生成 CLAUDE.md
项目脚手架搭好后，别忘了让 Claude 生成 CLAUDE.md：

```text
根据项目结构和配置文件，生成一份 CLAUDE.md，包含技术栈、文件结构、代码规范和常用命令
```
这样以后每次在这个项目里用 Claude Code，它都知道项目的全貌。
| 任务 | 手动耗时 | Claude Code 耗时 |
|------|----------|-------------------|
| 创建目录结构 | 5 分钟 | 30 秒 |
| 写配置文件 | 10 分钟 | 1 分钟 |
| 安装依赖 | 3 分钟 | 2 分钟 |
| 写入口代码 | 10 分钟 | 2 分钟 |
| 写 CLAUDE.md | 15 分钟 | 1 分钟 |
| **总计** | **43 分钟** | **约 7 分钟** |
> **核心建议**
>
> 用 Claude Code 搭建项目脚手架时，分步走比一步到位好。先创建结构，再填充配置，再写代码。每步验证一下。虽然多说了几句指令，但比一次性生成然后修 bug 要快得多。
## §13 自动化工作流
Automation Workflows
前面的章节你都是手动触发 Claude Code 执行任务。但有些任务是重复性的——每天跑 lint、每次提交前检查测试、定时生成报告。这些不需要你记得去做，让 Claude Code 自动完成。
### 定时任务：CronCreate
Claude Code 内置了定时任务系统。

```text
每天早上 9 点，检查项目的测试覆盖率，如果低于 80% 就通知我
```
Claude 会调用 CronCreate 工具，创建一个定时任务：

```json
{
  "cron": "3 9 * * *",
  "prompt": "运行 pytest --cov，检查覆盖率。如果低于 80%，生成报告并提示用户哪些模块需要补充测试。",
  "recurring": true,
  "durable": true
}
```

用 `/tasks` 查看所有定时任务，CronDelete 可以删除不需要的任务。
### /loop：周期性执行

```text
/loop 5m 运行测试，如果失败就自动修复
```

这个命令每 5 分钟运行一次测试。失败了就自动修复。适合在你重构代码的时候跑着。
### 自定义 Skill：把常用操作变成命令
在 `.claude/commands/` 目录创建 Markdown 文件，就能注册自定义 Skill：
`.claude/commands/deploy.md`：

```markdown
---
description: 部署到生产环境
---
执行以下步骤：
1. 运行完整测试套件
2. 类型检查
3. 构建
4. 部署到 Vercel
5. 验证部署是否成功
任何一步失败都停止并报告错误。
```
然后在 Claude Code 里用 `/deploy` 就能一键执行整个部署流程。
### Hooks + CI/CD 的集成
结合 Hooks，可以在每次编辑代码后自动触发 CI 相关操作：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "cd $PROJECT_DIR && npm run lint --silent 2>&1 | tail -1 >> /tmp/claude-lint.log"
          }
        ]
      }
    ]
  }
```

每次编辑文件后自动跑 lint，结果写入日志。你不用记得跑——Hooks 自动帮你跑。
### Agent Teams：多 Agent 协作
对于特别复杂的任务，可以用 TeamCreate 创建 Agent 团队：

```text
创建一个 3 人团队：
- 一个负责前端开发
- 一个负责后端开发  
- 一个负责测试
让他们并行开发用户管理模块
```

每个 Agent 有独立的上下文，通过共享的任务列表协调。适合大范围的重构或功能开发。
注意：Agent Teams 目前需要设置环境变量 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 来启用。
### 完整的自动化工作流示例
一个实际的场景：你在维护一个 SaaS 产品的后端，每天要做这些重复工作：

```text
1. 检查未处理的 GitHub Issues
2. 对有 bug 标签的 Issue 进行初步分析
3. 运行测试套件
4. 检查数据库迁移是否同步
5. 生成日报
```

让 Claude Code 建立自动化：

```text
帮我设置以下自动化：
1. 每天早上 8:30 检查 GitHub Issues（用 CronCreate）
2. 对 bug 标签的 Issue 用 Agent 分析根因
3. 每次我修改代码后自动跑测试（用 Hook）
4. 每天生成一份工作日报
```

Claude 会配置 Cron 任务、设置 Hooks、创建 Skill。你只需要早上看一份报告就行。
> **核心建议**
>
> 自动化的原则是：重复三次以上的任务就值得自动化。不要过度自动化一次性任务——设置自动化本身也要花时间。先从最频繁的重复任务开始，比如测试、lint、部署检查。
实战场景讲完了。你已经知道 Claude Code 能做什么、怎么做得好。接下来的最后一部分，我们退后一步，从更高的视角看问题：什么时候用什么模型？怎么最大化投入产出比？
# Part 5: 深度思考

## §14 模型选择策略
Choosing the Right Model
Claude Code 背后不是一个模型，而是三个：Opus 4.6、Sonnet 4.6、Haiku。它们各有擅长，价格差 5 倍。选对模型，同样的任务能省 80% 的钱。
### 三模型对比
| 维度 | Opus 4.6 | Sonnet 4.6 | Haiku |
|------|----------|------------|-------|
| 定位 | 最强推理 | 平衡性能 | 快速响应 |
| 输入价格 | $5/百万 Token | $3/百万 Token | $1/百万 Token |
| 输出价格 | $25/百万 Token | $15/百万 Token | $5/百万 Token |
| 速度 | 较慢 | 快 | 最快 |
| 适合场景 | 架构设计、复杂 debug | 日常编码、重构 | 快速查询、简单任务 |
差距最大的不是能力，而是性价比。Sonnet 处理 80% 的日常任务绰绰有余，价格只有 Opus 的 60%。
### 什么时候用 Opus
**架构决策**

```text
/plan 设计一个支持百万并发的消息队列系统
```

这种需要深度推理、权衡多种方案的复杂任务，Opus 的优势明显。
**棘手的 Bug**
当你遇到一个多天没解决的 bug，Sonnet 给不出满意答案时，切 Opus：

```text
/model opus
这个并发 bug 在压力测试下才出现，我已经排除了锁竞争和资源泄漏。帮我分析其他可能的原因。
```

**代码安全审查**
安全审查需要理解攻击链和边界条件，这是 Opus 的强项。
### 什么时候用 Sonnet
日常编码的 80% 场景。重构、写测试、添加功能、修改配置——Sonnet 又快又便宜，完全够用。
### 什么时候用 Haiku
**快速查询**

```text
/model haiku
Python 的 datetime.timezone.utc 和 pytz.UTC 有什么区别？
```

不需要深度推理的问题，Haiku 2 秒就能回答。
**Agent 内部**
自定义 Agent 指定 `model: haiku`，在做代码搜索、文件遍历等不需要深度理解的任务时，成本最低。
### opusplan：最佳混合策略

```text
/model opusplan
```

这个特殊别名在 Plan Mode 下用 Opus（想得深），执行阶段自动切到 Sonnet（做得快）。一个命令解决"规划要用最强模型，执行不想浪费钱"的矛盾。
### Effort 级别：控制思考深度
除了选模型，还能控制模型的努力程度：
| 级别 | 说明 | 适合场景 |
|------|------|----------|
| low | 快速响应，浅层思考 | 简单格式化、小修改 |
| medium | 默认平衡 | 大多数日常任务 |
| high | 深度思考 | 复杂逻辑、架构设计 |
| max | 最深思考（仅 Opus） | 特别困难的问题 |

```text
/effort high
```

`max` 级别只对 Opus 4.6 有效。对于特别困难的问题，在 prompt 里加 "ultrathink" 也能触发最大努力。
### 成本优化技巧
**1. 利用缓存**
Claude Code 自动启用 Prompt Caching。缓存读取比标准输入便宜 90%。这意味着在同一个会话里反复讨论同一个文件，后续的成本会大幅下降。
**2. 用 /compact 管理上下文**
对话越长，每次请求的 Token 越多。定期用 `/compact` 压缩历史，能显著降低成本。
**3. 子 Agent 用 Haiku**

```markdown
---
name: file-searcher
model: haiku
tools: Glob, Grep, Read
---
```
搜索类任务不需要强模型，Haiku 又快又便宜。
**4. 用 --max-budget-usd 设上限**

```bash
claude -p "重构这个模块" --max-budget-usd 1.00
```

非交互模式下设定预算上限，防止意外超支。
**5. 用 /cost 和 /usage 监控**

```bash
/cost    # 当前会话消耗
/usage   # 月度配额和限速状态
/stats   # 使用趋势
```

养成定期查看的习惯。
| 优化手段 | 节省幅度 | 实施难度 |
|----------|----------|----------|
| 用 Sonnet 代替 Opus | ~40% | 零 |
| /compact 压缩上下文 | 20-50% | 低 |
| 子 Agent 用 Haiku | 60-80% | 低 |
| Prompt 缓存 | ~90%（缓存命中部分） | 自动 |
| 预算上限 | 100%（防超支） | 低 |
> **核心建议**
>
> 默认用 Sonnet。遇到 Sonnet 搞不定的问题才切 Opus。Agent 内部的搜索任务用 Haiku。这个简单的三层策略能覆盖 95% 的场景，同时把成本控制在合理范围。
## §15 效率最大化
Maximizing Your Efficiency
你已经知道了 Claude Code 的每个功能。但功能和效率之间还有一段距离——就像你知道 Excel 的每个公式，不代表你是 Excel 高手。
这章分享一些经过验证的效率技巧。不是功能列表，而是工作方式的改变。
### 权限模式：减少确认弹窗
Claude Code 默认每次修改文件、执行命令都要你确认。这对于安全是好事，但对效率是灾难——如果你信任 Claude 在你的项目里操作，可以切换权限模式：
Shift+Tab 循环切换：
| 模式 | 行为 | 适合场景 |
|------|------|----------|
| default | 每次都确认 | 新项目、不确定时 |
| acceptEdits | 自动接受文件编辑 | 日常开发（推荐） |
| plan | 只读模式 | 审查代码 |
| auto | AI 自动判断 | Team/Enterprise 用户 |
大多数时候 `acceptEdits` 是最佳选择。Claude 可以自由编辑文件，但执行 bash 命令仍然需要确认。既高效又安全。
### 会话管理：不丢失上下文
**/compact——压缩但保留关键信息**
对话超过 50 轮时，主动压缩：

```text
/compact 保留所有关于支付模块的讨论
```

你可以指定保留哪些内容。
**/fork——试试不同的方向**

```text
/fork
```

在当前对话节点分叉。主会话继续走一条路，分叉出去的走另一条路。两条路互不影响。
**claude -c——继续上次对话**
第二天回到工位，输入 `claude -c`，昨天的上下文全都在。
### Worktree：并行工作
当你要同时处理多个任务时：

```bash
claude --worktree
```
Claude Code 会创建一个独立的 Git Worktree。你在主分支做 A 任务，Worktree 里做 B 任务，互不干扰。完成后合并。
也可以在 Agent 上使用：

```bash
claude --agent code-reviewer --worktree
```

Agent 在隔离环境里工作，不会弄乱你的工作目录。
### 快捷键肌肉记忆
效率的差别往往在细节。这些快捷键值得练成肌肉记忆：
| 快捷键 | 用途 | 频率 |
|--------|------|------|
| Ctrl+C | 中断当前操作 | 每天用 |
| Shift+Tab | 切换权限模式 | 每天用 |
| Ctrl+L | 清屏 | 每天用 |
| Option+P | 切换模型 | 经常用 |
| Ctrl+O | 查看工具调用详情 | 调试时用 |
| Esc Esc | 回退操作 | 偶尔用 |
最核心的就三个：Ctrl+C（停下来）、Shift+Tab（切权限）、Option+P（切模型）。
### 编写更好的 Prompt
Claude Code 很强，但你的指令质量决定了它的输出质量。
**差的指令**
```text
改一下这个代码
```

**好的指令**
```text
重构 @src/utils/format.js 中的 formatDate 函数：
- 支持 ISO 8601 和 Unix 时间戳两种输入
- 输出格式改为 "2024-01-15 14:30"
- 添加单元测试
```

区别在于：好的指令告诉 Claude 具体做什么、输入输出是什么、验收标准是什么。
**差的指令**
```text
帮我写个 API
```

**好的指令**
```text
用 FastAPI 创建一个 /api/users 接口：
- GET 方法，返回用户列表
- 支持 page 和 limit 分页参数
- 使用 SQLAlchemy async 查询
- 响应格式 {success: bool, data: [...], total: int}
- 写对应的 pytest 测试
```

### 最佳日常工作流
一个高效的 Claude Code 日常工作流：
**早上**
```bash
claude -c                          # 继续昨天的工作
```

**开发中**
```text
/plan 设计 xxx 功能                # 先规划
/model opusplan                    # 规划用 Opus
# 审核方案后
/model sonnet                      # 执行用 Sonnet
Shift+Tab → acceptEdits            # 自动接受编辑
# 开始写代码
```

**提交前**
```bash
/security-review                   # 安全审查
/simplify                          # 代码质量检查
!git diff                          # 检查改动
```

**下班前**
```text
/compact 保留关于 x 功能的讨论     # 压缩上下文
```

### 你的工具台，你的规则
Claude Code 的设计哲学是"给你一个足够强大的工具台，但怎么用由你决定"。
你不需要用上所有功能。从一个舒服的起点开始：
1. 装 Claude Code，用默认配置
2. 写一份简单的 CLAUDE.md
3. 用 Sonnet 模型做日常开发
4. 遇到复杂问题切 Opus
5. 逐步加 Hooks 和自定义 Agent
每一步都是在你的工具台上加一件新工具。加到你觉得够了就停。工具是为人服务的，不是反过来。
> **核心建议**
>
> 效率最大化的核心不是学会所有功能，而是建立适合自己的工作流。先用起来，遇到痛点再加工具。一个用了 3 个功能但用得熟练的人，比一个知道 30 个功能但都用不好的人效率高得多。
这本书到这里就结束了。你已经从"什么是 Claude Code"走到了"怎么最大化利用它"。工具台是你的，怎么用，你说了算。