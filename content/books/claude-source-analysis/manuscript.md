---
title: "Claude 源码解析 - 全文"
date: 2026-04-15
draft: false
description: "从入口到工具调用，拆解 AI 编程助手的内部架构"
type: books
---

## 本书适合谁读
本书适合以下几类读者。当然，这不是一个排他性的清单——如果你对 AI 编码助手的内部实现感到好奇，你就是本书的目标读者。
### 想深入理解 AI 编程工具的工程师
你可能每天都在使用 Claude Code、Cursor 或 Copilot，但你不满足于"会用"——你想拆开黑盒，理解从用户输入到 LLM 调用到工具执行的每一步。本书将带你逐模块拆解一个生产级 AI 编码助手的完整架构。读完本书，你将理解 AI 编程工具的能力边界，不再把它当作魔法。
### 想构建 AI Agent 和工具的开发者
你可能正在开发自己的 AI Agent、IDE 插件或自动化工作流。Claude Code 的源码是一个极好的参考实现——Agent 循环、上下文管理、流式响应、权限控制、MCP 工具集成，该有的都有。本书不是教你怎么调 API，而是教你怎么设计一个完整的 AI 工程系统。
### 想提升工程能力的程序员
源码阅读是提升工程能力最高效的方式之一。Claude Code 的代码库使用 TypeScript，涉及 CLI 设计、并发调度、虚拟列表渲染、配置系统、安全沙箱等大量工程实践。即使你对 AI 不感兴趣，本书也是一次高质量的代码阅读训练。
### 阅读本书之前
本书不是编程入门书。我们假设你有至少一年的编程经验，能看懂 TypeScript/JavaScript（不需要精通），用过命令行工具，对 LLM 和 AI 有基本概念。如果你完全不编程，建议先学一门语言再回来。如果你已经是 TypeScript 专家，可以跳过基础语法解释，专注于架构设计。
# Part 1: 概念

## §01 你每天都在用的 Claude Code，里面到底有什么
What's Inside the Box
"我每天都在终端里跟 Claude Code 聊天写代码，但它到底是什么？一个 shell 脚本？一个 Electron 应用？一个 Python 程序？"
如果你有过这个念头，那你并不孤独。Claude Code 的黑盒感比大多数 CLI 工具都强——因为它不是一个普通的命令行工具，它是一座**工厂**。
### CCB 反编译还原项目
这本教程分析的代码来自 CCB（Claude Code Best）项目。CCB 是一个逆向工程还原项目：从 Anthropic 官方发布的 Claude Code npm 包出发，通过反编译和类型还原，重新构建出可读、可运行、可调试的源码。它的 `package.json` 里写得很直接：`"description": "Reverse-engineered Anthropic Claude Code CLI"`。
CCB 并非 1:1 完美还原——有些模块被裁剪了，有些类型标注在反编译过程中丢失了（约 1341 个 tsc 类型错误），但核心架构和运行逻辑完整保留。当前的版本号 `2.1.888` 里的 `888` 就是 CCB 的标识。
这意味着你读到的代码和 Anthropic 工程师写的原始代码在结构上高度一致，只是少了一些 Anthropic 内部专用的功能分支。
### 运行时：Bun，不是 Node.js
Claude Code 选择 Bun（一个高性能的 JavaScript/TypeScript 运行时）作为运行时。这不是一个随便的决定。Bun 在三个关键点上碾压 Node.js：
| 对比维度 | Node.js | Bun |
|---|---|---|
| 冷启动速度 | ~200ms（加载 Commander + React + SDK） | ~50ms（原生 TS/TSX 支持，无需转译） |
| TypeScript 支持 | 需要 ts-node 或先编译 | 原生执行 .ts/.tsx 文件 |
| 构建能力 | 需要 webpack/esbuild/rollup | 内置 Bun.build()，支持代码分割 |
| 包管理 | npm/yarn/pnpm | 内置 Bun Workspaces |
| `bun:bundle` | 无 | 编译时宏替换、feature flag 注入 |
当你运行 `bun run dev`，Bun 直接执行 `.tsx` 文件，零构建步骤。这让 Claude Code 的开发循环快得惊人。
Bun 在 CCB 项目里还有一个特殊用途：`bun:bundle` API。原版 Claude Code 用它在编译时注入 feature flag 和宏变量。CCB 用 polyfill 模拟了这一机制。
### 技术栈一览
把 Claude Code 拆开，核心组件清单如下：
| 层次 | 技术 | 作用 |
|---|---|---|
| 语言 | TypeScript + TSX | 全栈类型安全，JSX 用于终端 UI |
| 终端 UI | Ink（React for CLI） | 用 React 组件模型渲染终端界面 |
| 命令解析 | Commander.js | CLI 参数、子命令、选项定义 |
| AI SDK | @anthropic-ai/sdk | 与 Claude API 通信 |
| MCP 协议 | @modelcontextprotocol/sdk | 外部工具集成协议 |
| 状态管理 | 自建 Store（Zustand 风格） | 全局应用状态 |
| 构建 | Bun.build() + 代码分割 | 产出 ~450 个 chunk 文件 |
| 包管理 | Bun Workspaces monorepo | 内部包统一管理 |
| 可观测性 | OpenTelemetry | 日志、指标、链路追踪 |
| 模式验证 | Zod（一个 TypeScript 运行时类型校验库）+ Ajv | 运行时类型检查 |
用 React 写终端界面——这是 Claude Code 最独特的架构选择。`src/screens/REPL.tsx` 有 5009 行，是一个完整的 React 组件，管理着消息列表、用户输入、工具权限确认、键盘快捷键等所有交互。
### 项目目录结构速览

```text
claude-code-best/
├── build.ts              # 构建脚本（Bun.build + 代码分割）
├── package.json          # 项目配置（bun >= 1.2.0）
├── tsconfig.json         # TypeScript 配置（target: ESNext）
├── packages/             # 内部 workspace 包
│   ├── @ant/             # Anthropic 内部专用包（Chrome MCP、Computer Use）
│   ├── color-diff-napi/  # 完整实现的颜色差异计算
│   ├── audio-capture-napi/  # 音频捕获（stub）
│   └── ...               # 其他 napi 包（多数为 stub）
└── src/
    ├── entrypoints/
    │   ├── cli.tsx       # 真正的入口（375 行）
    │   ├── init.ts       # 一次性初始化
    │   └── mcp.ts        # MCP 入口
    ├── main.tsx          # Commander.js 主逻辑（约 4600 行）
    ├── query.ts          # 核心查询循环（约 1700 行）
    ├── QueryEngine.ts    # 会话引擎（1320 行）
    ├── tools.ts          # 工具注册表（497 行）
    ├── Tool.ts           # Tool 类型定义
    ├── screens/
    │   └── REPL.tsx      # 主交互界面（5009 行）
    ├── tools/            # 40+ 工具实现
    │   ├── BashTool/     # Shell 命令执行
    │   ├── FileReadTool/ # 文件读取
    │   ├── FileEditTool/ # 文件编辑
    │   ├── GrepTool/     # 内容搜索
    │   ├── AgentTool/    # 子代理
    │   └── ...
    ├── services/
    │   ├── api/          # API 客户端（claude.ts 有 3420 行）
    │   ├── mcp/          # MCP 协议实现
    │   └── compact/      # 上下文压缩
    ├── components/       # 100+ React 终端组件
    ├── hooks/            # 86 个自定义 React hooks
    ├── state/            # 状态管理（AppState + Store）
    ├── ink/              # Ink 框架（定制版）
    ├── bootstrap/        # 启动引导 + 全局状态单例
    ├── context/          # React Context
    ├── commands/         # 70+ 子命令（/help、/compact 等）
    ├── utils/            # 工具函数（含 model/ 子目录）
    ├── memdir/           # 记忆系统
    └── types/            # 类型定义
```

几个数字帮你建立规模感：`src/` 下有 40+ 目录、100+ 组件、86 个 hooks、40+ 工具、70+ 子命令。六个核心文件（cli.tsx、main.tsx、query.ts、QueryEngine.ts、claude.ts、REPL.tsx）总计超过 16000 行。
### Monorepo 与内部包
CCB 用 Bun Workspaces 管理 monorepo。`packages/` 目录下有两类包：
**完整实现**：`color-diff-napi/`——用于终端颜色差异计算的 NAPI 模块，有真正的 Rust 源码和编译产物。
**Stub 包**：`audio-capture-napi/`、`image-processor-napi/`、`modifiers-napi/`、`url-handler-napi/`——这些是空壳，只导出类型定义或空函数。`packages/@ant/` 下的四个包（`claude-for-chrome-mcp`、`computer-use-input`、`computer-use-mcp`、`computer-use-swift`）也是 stub。
在 `tools.ts` 里你会看到 `feature('PROACTIVE')`、`feature('KAIROS')` 这些条件——因为 CCB 的 `feature()`（一个内部特性开关函数）始终返回 `false`，所以依赖这些 flag 的工具（SleepTool、CronTool、MonitorTool 等）全部被死代码消除。这是 CCB 裁剪 Anthropic 内部功能的机制。
> **核心建议**
> 读源码时，把 `feature('XXX')` 包裹的代码块当成注释跳过。CCB 里大约 30 个 feature flag 全部关闭，它们控制的是 Anthropic 内部的实验性功能（自主代理、远程控制、语音模式等）。你只需要关注 `feature()` 返回 `false` 时走的那条分支。
不过，这座工厂的具体构造是什么样的？各个模块之间怎么配合？下一章会画出完整的蓝图。
## §02 一座智能工厂的蓝图
Architecture Blueprint
Claude Code 不是"一个 CLI 工具"——它是一套六层架构的分布式系统。如果你把它当成 `argparse + print()` 的传统 CLI 来读源码，你会在 5000 行的 REPL.tsx 里迷路。正确的打开方式是先看蓝图。
### 六层架构
从上到下，Claude Code 可以分成六个清晰的层：
| 层次 | 名称 | 核心文件 | 职责 |
|---|---|---|---|
| L1 | 入口层 | `cli.tsx` | 运行时 polyfill、快速路径分派 |
| L2 | 命令层 | `main.tsx` | Commander.js 参数解析、服务初始化 |
| L3 | 核心层 | `query.ts` + `QueryEngine.ts`（查询引擎，协调整个请求生命周期） | 对话循环、消息管理、压缩策略 |
| L4 | 工具层 | `tools.ts` + `src/tools/` | 工具注册与执行（Bash、Read、Edit 等） |
| L5 | 服务层 | `src/services/` | API 通信、MCP 协议、压缩、记忆 |
| L6 | 表现层 | `src/screens/` + `src/components/` | Ink/React 终端 UI |
![六层架构图](images/architecture-six-layers.png)
每一层只依赖它下面的层。入口层永远不知道 UI 长什么样，工具层永远不知道消息是怎么发送给 API 的。这种分层不是学术上的洁癖——它意味着你可以从任何一层切入阅读，不用先理解其他五层。
### 数据流：一条消息的旅程
你在终端敲下 `> 帮我重构这个函数`，然后看到 Claude 的回复。这条消息经过了完整的工厂流水线：
![消息数据流](images/message-data-flow.png)
`query.ts` 里的循环就是这个流程的核心。它不是"发送一次请求，拿到一次响应"的简单模式——它是一个**多轮循环**，因为 Claude 的回复可能包含工具调用（`tool_use`），每个工具调用产生结果后要再喂回 API，直到 Claude 认为任务完成（`stop_reason: "end_turn"`）。
![核心循环流程图](images/core-loop-flowchart.png)
### 工厂隐喻映射
全书使用一个统一的隐喻：Claude Code 是一座**智能工厂**。每个模块对应工厂的一个部门：
| 工厂部门 | 代码模块 | 干什么 |
|---|---|---|
| 工厂大门 + 门卫 | `cli.tsx` + `feature()` | 检查来者是谁，快速路径直接放行，其余引入调度中心 |
| 调度中心 | `main.tsx` (Commander.js) | 解析指令，分配任务到对应的车间 |
| 生产线 | `query.ts` 核心循环 | 反复执行"请求→响应→工具调用→再请求"的循环 |
| 总调度室 | `QueryEngine.ts` | 管理整条生产线的节奏：压缩、快照、成本追踪 |
| 车间工具站 | `src/tools/` (BashTool, ReadTool...) | 每个工具是一个工位，执行特定操作 |
| 外部供应商通道 | MCP 协议 (`src/services/mcp/`) | 连接外部服务，像供应商给工厂送货 |
| 安检门 | 权限系统 (`useCanUseTool`) | 工具执行前检查权限，危险操作需要人工确认 |
| 品控检测点 | Hook 系统 (`src/hooks/`) | 在关键节点插入检查逻辑，类似质检 |
| 控制面板 | UI 层 (Ink/React) | 终端界面就是工厂的控制面板，实时显示状态 |
| 仓库 + 档案馆 | 状态管理 + 记忆系统 (`memdir/`) | 仓库存当前状态，档案馆存历史记忆 |
| 节能压缩模式 | 自动压缩（compact，上下文压缩，防止 Token 溢出）(`src/services/compact/`) | 上下文太长时自动压缩历史，节省 Token |
这个映射不是牵强的比喻。`cli.tsx` 真的就是"大门"——它做的第一件事是检查参数（验身份），如果是 `--version` 这种简单请求，直接打印结果放行，连工厂都不用进。`query.ts` 真的就是"生产线"——它是一个 `while` 循环，每轮都是标准的"接收原料→加工→输出"流程。
### 和传统 CLI 工具的根本差异
如果你用过 Python 的 `argparse` 或 `click`，或者 Node.js 的 `commander`，你对 CLI 工具的心智模型大概是：

```text
解析参数 → 执行逻辑 → 打印结果 → 退出
```

Claude Code 完全不同。它是一个**长驻进程**：
| 维度 | 传统 CLI | Claude Code |
|---|---|---|
| 生命周期 | 一次执行，输出后退出 | 长驻 REPL，反复交互 |
| I/O 模型 | stdin → stdout | React 终端 UI + 流式 API |
| 状态 | 无状态 | 有状态（对话历史、权限、MCP 连接） |
| 外部依赖 | 文件系统、网络 | 文件系统 + AI API + MCP 服务器 |
| 复杂度 | 线性流程 | 多层嵌套循环 + 异步事件 |
| 用户交互 | 参数一次传完 | 对话式，随时中断、追问 |
这就解释了为什么 `main.tsx` 有约 4600 行——它不只是解析参数，它要初始化认证、启动遥测、加载配置、连接 MCP 服务器、设置权限策略，然后才启动 REPL。而 REPL 本身（`REPL.tsx`）又有 5009 行，因为它管理着整个交互循环。
> **核心建议**
> 读源码时，先在脑子里画出六层架构。遇到一个文件，先判断它在哪一层，然后只关注它的上下游。不要试图从 `main.tsx` 的第一行顺序读到最后一行——那个文件几乎是一个"粘合层"，把所有服务拉到一起，逐行读会被大量的初始化代码淹没。
蓝图画完了。但光看图纸不等于会开机器——下一章会带你走进工厂，从安装 Bun 开始，一步步让这座工厂在你本地跑起来。
## §03 准备好进厂了
Setting Up for Source Reading
你打开了 VS Code，clone 了 CCB 仓库，然后面对 5000 行的 `main.tsx` 和 100 多个组件目录，手指停在键盘上不知道从哪里开始。这是正常的。本章带你搭建环境并建立一套阅读策略，让你能在这座工厂里自如穿行。
### 环境搭建
CCB 的唯一运行时依赖是 Bun。它不需要 Node.js、不需要 Python、不需要 Docker。

```bash
# macOS / Linux 安装 Bun
curl -fsSL https://bun.sh/install | bash
# 验证版本（需要 >= 1.2.0）
bun --version
```

为什么必须是 Bun 而不是 Node.js？两个原因。第一，`package.json` 里声明了 `"engines": { "bun": ">=1.2.0" }`，且没有任何 Node engine 字段。第二，CCB 的构建脚本 `build.ts` 直接调用 `Bun.build()`，源码里有 `import { feature } from 'bun:bundle'` 这样的 Bun 专有 API。用 Node.js 跑不起来。
### Clone 与依赖安装

```bash
# Clone 仓库
git clone https://github.com/claude-code-best/claude-code.git
cd claude-code
# 安装依赖（Bun Workspaces 会自动处理内部包）
bun install
```

`bun install` 会处理 `packages/` 下的所有 workspace 包。多数内部包是 stub（只导出空函数），但 `color-diff-napi` 需要编译原生模块。如果你的环境缺少 Rust 工具链，这个包可能编译失败——不影响核心功能的阅读。
依赖安装完后，项目结构确认一下：

```bash
# 确认核心文件都在
ls -la src/entrypoints/cli.tsx     # 入口
ls -la src/main.tsx                 # 主逻辑
ls -la src/query.ts                 # 核心循环
ls -la src/QueryEngine.ts           # 会话引擎
ls -la src/screens/REPL.tsx         # 主界面
```

### 运行与调试
CCB 提供了两种运行模式：

```bash
# 开发模式：直接执行源码，零构建
bun run dev
# 等价于：bun run src/entrypoints/cli.tsx
# 构建模式：产出 dist/ 目录
bun run build
# 产出 dist/cli.js + 约 450 个 chunk 文件
```

开发模式是源码阅读的最佳搭档。Bun 直接执行 `.tsx` 文件，你的任何修改都在下次启动时立即生效。
**调试技巧一：快速路径验证**
在 `cli.tsx` 里，`--version` 是最简单的快速路径。你可以用它验证环境是否正常：

```bash
bun run src/entrypoints/cli.tsx --version
# 应输出：2.1.888 (Claude Code)
```

**调试技巧二：console.log 插桩**
因为 CCB 有大量反编译产生的类型错误（~1341 个 tsc 错误），IDE 的 TypeScript 类型提示可能不太可靠。最实用的调试方式是直接插 `console.log`：

```typescript
// 在 src/query.ts 的 query() 函数入口加一行
export async function query(params: QueryParams): Promise<QueryResult> {
    console.log('[DEBUG] query() called with:', params.messages.length, 'messages')
    // ... 原有代码
}
```

Bun 在终端模式下会正常输出 console.log 到 stderr。
**调试技巧三：环境变量控制**
CCB 有大量环境变量控制行为。几个有用的：
| 环境变量 | 作用 | 用途 |
|---|---|---|
| `CLAUDE_CODE_USE_BEDROCK=1` | 切换到 AWS Bedrock Provider | 测试不同 API 路径 |
| `CLAUDE_CODE_USE_VERTEX=1` | 切换到 Google Vertex Provider | 测试不同 API 路径 |
| `CLAUDE_CODE_REMOTE=true` | 启用远程模式（8GB 堆内存） | 模拟容器环境 |
| `DISABLE_AUTO_COMPACT=1` | 禁用自动压缩 | 观察完整对话上下文 |
### 关键文件速查表
把这张表打印出来贴在屏幕旁边，比翻目录快十倍：
| 文件 | 行数 | 一句话说明 |
|---|---|---|
| `src/entrypoints/cli.tsx` | 375 | 入口 + polyfill + 快速路径分派 |
| `src/main.tsx` | 约 4600 | Commander 命令定义 + 全局初始化 |
| `src/query.ts` | 约 1700 | 核心 API 查询循环（发请求、处理流、调工具） |
| `src/QueryEngine.ts` | 1320 | 会话引擎（压缩、快照、成本追踪） |
| `src/tools.ts` | 497 | 工具注册表（组装 + 过滤 + 合并 MCP） |
| `src/Tool.ts` | — | Tool 类型定义 + 匹配工具 |
| `src/services/api/claude.ts` | 3420 | API 客户端（构建请求、处理流式响应） |
| `src/screens/REPL.tsx` | 5009 | 主界面（React/Ink 组件） |
| `src/bootstrap/state.ts` | — | 全局状态单例（sessionId、projectRoot） |
| `src/state/AppState.tsx` | — | React Context 状态容器 |
| `src/utils/model/providers.ts` | 41 | API Provider 选择逻辑 |
| `build.ts` | 71 | 构建脚本 |
### 阅读策略：从大门开始
面对 16000+ 行的核心代码，"从第一行读到最后一行"是效率最低的策略。推荐这套路径：
**第一步：走通入口链。** 从 `cli.tsx` 的 `main()` 函数开始，跟踪它怎么跳到 `main.tsx`。注意快速路径（`--version`、`--claude-in-chrome-mcp`）和正常路径的区别。这条链路很短， 10 分钟就能走完。
**第二步：跟踪一次完整对话。** 在 `query.ts` 的 `query()` 函数入口打断点或插 log，然后通过 REPL 发送一条消息。观察参数怎么传进来、API 响应怎么回来、工具调用怎么触发。这一步让你理解工厂的生产线是怎么转的。
**第三步：挑一个工具读透。** 从 `BashTool` 开始——它最简单，也最核心。读它的 `inputSchema`（参数定义）、`call()`（执行逻辑）、渲染组件。然后把同样的模式套用到 `FileReadTool`、`FileEditTool`。
**第四步：看 UI 层。** `REPL.tsx` 太大了，不要从头读。先找到它调用 `QueryEngine` 的地方，理解 UI 和核心层怎么交互。
> **核心建议**
> 源码阅读的效率取决于你"跳跃"的能力，而不是"顺序阅读"的耐力。在 VS Code 里，多用"Go to Definition"（F12）和"Find All References"（Shift+F12）。遇到不认识的类型，跳到定义看一眼就回来，不要展开读整个文件。
你现在已经站在工厂大门外了——Bun 装好了，代码跑通了，地图也画好了。下一步就是推开 `cli.tsx` 这扇门，看看门卫是怎么工作的。
# Part 2: 核心机制

## §04 工厂大门
The Entry Gate — cli.tsx
你输入 `claude --version`，屏幕立刻打出 `2.1.888 (Claude Code)`，整个过程不到 10 毫秒。但如果你输入 `claude`，然后点根烟回来，终端里已经是一个完整的交互式对话界面了。同一个二进制文件，两条命令，启动速度差了几百倍。
反直觉的结论是：`--version` 和正常启动走的是完全不同的路径。前者连一个模块都没加载，后者拉起了约 4600 行代码。制造这个巨大差异的，就是 `cli.tsx` 这个只有 376 行的文件。
它不像你见过的那种"先 import 一百个模块再开始干活"的入口文件。它更像一座智能工厂的大门——门卫不查身份证不搜包，直接问你："你要干嘛？"如果你只是来问个版本号，门卫递张纸条你就走了，连厂房都不用进。
### 门卫的第一个问题：快速路径检测
`cli.tsx` 的 `main()` 函数做的第一件事，就是扫描命令行参数：

```typescript
async function main(): Promise<void> {
  const args = process.argv.slice(2);
  // 快速路径：--version/-v，零模块加载
  if (
    args.length === 1 &&
    (args[0] === "--version" || args[0] === "-v" || args[0] === "-V")
  ) {
    console.log(`${MACRO.VERSION} (Claude Code)`);
    return; // 直接返回，什么都不加载
  }
  // ...
}
```

这个 `if` 判断在函数最顶端，甚至没有 `await import` 任何东西。`MACRO.VERSION` 是个全局常量（后面会说怎么来的），`console.log` 是 Node.js 内置 API——这意味着整条路径零额外模块加载，零 IO 等待。
但这只是最简单的一条快速路径。往下看，你会发现一整棵决策树：
| 快速路径 | 参数 | 需要加载什么 | 谁能用 |
|----------|------|-------------|--------|
| 版本号 | `--version` | 无 | 所有人 |
| Chrome MCP | `--claude-in-chrome-mcp` | `claudeInChrome/mcpServer.js` | 所有人 |
| Chrome 原生宿主 | `--chrome-native-host` | `claudeInChrome/chromeNativeHost.js` | 所有人 |
| 系统提示词导出 | `--dump-system-prompt` | config + prompts 模块 | Ant 内部 |
| 守护进程工作器 | `--daemon-worker` | `daemon/workerRegistry.js` | Ant 内部 |
| 远程控制桥接 | `remote-control/bridge` | bridge 全套模块 | Ant 内部 |
| 后台会话管理 | `ps/logs/attach/kill` | `cli/bg.js` | Ant 内部 |
| 模板任务 | `new/list/reply` | `handlers/templateJobs.js` | Ant 内部 |
| 环境运行器 | `environment-runner` | `environment-runner/main.js` | Ant 内部 |
| 自托管运行器 | `self-hosted-runner` | `self-hosted-runner/main.js` | Ant 内部 |
| 完整 CLI | 其他所有参数 | `main.tsx`（约 4600 行） | 所有人 |
注意到"谁能用"那一列了吗？大部分快速路径被标记为"Ant 内部"——Anthropic 内部版本。你用的公开版本根本走不到这些分支。这个区分机制就是接下来要说的 `feature()` 门禁。
### feature() 门禁：全关的总闸
在 `cli.tsx` 的顶部，有一行看起来平平无奇的代码：

```typescript
const feature = (_name: string) => false;
```

这是一个始终返回 `false` 的函数。参数名叫 `_name`，下划线前缀表示"我不关心你传什么"。但它的作用极其关键——它控制着大约 30 个 feature flag，决定哪些代码路径活着、哪些是死代码。
在 Anthropic 内部的原始构建流程中，Bun 打包器会在编译时把这个函数替换成真正的 feature flag 检查。对于公开版本，`feature()` 始终返回 `false`，打包器再通过 tree-shaking 把被 `if (feature("XXX"))` 包裹的代码块整段删掉。
这就形成了一个精巧的安全网：

```typescript
// 这些代码在公开版本中根本不存在（被 tree-shaking 删掉了）
if (feature("DAEMON") && args[0] === "--daemon-worker") {
  const { runDaemonWorker } = await import("../daemon/workerRegistry.js");
  await runDaemonWorker(args[1]);
  return;
}
if (feature("BRIDGE_MODE") && args[0] === "remote-control") {
  // ... 一大段远程控制逻辑
  return;
}
```

在公开版本中，这些 `if` 块不会执行，对应的 `await import` 也不会触发。这不仅仅是功能开关——它是安全边界。守护进程、远程控制、后台会话管理这些高风险功能，通过编译时消除彻底从公开构建中剥离了。
> **核心建议**：理解 feature flag 门禁是阅读 Claude Code 源码的第一把钥匙。当你看到 `if (feature("XXX"))` 包裹的代码块，在公开版本中可以直接跳过——它要么已经被删掉了，要么永远不会执行。这能帮你过滤掉大约 40% 的条件分支，让约 4600 行的 `main.tsx` 不再那么吓人。
### MACRO 变量注入：编译时常量
紧跟 `feature()` 函数之后，你会看到一段给 `globalThis` 注入常量的代码：

```typescript
if (typeof globalThis.MACRO === "undefined") {
  (globalThis as any).MACRO = {
    VERSION: "2.1.888",
    BUILD_TIME: new Date().toISOString(),
    FEEDBACK_CHANNEL: "",
    ISSUES_EXPLAINER: "",
    NATIVE_PACKAGE_URL: "",
    PACKAGE_URL: "",
    VERSION_CHANGELOG: "",
  };
}
(globalThis as any).BUILD_TARGET = "external";
(globalThis as any).BUILD_ENV = "production";
(globalThis as any).INTERFACE_TYPE = "stdio";
```

在原始构建流程中，这些值由 Bun 打包器在编译时注入。对于逆向还原版本，它们被硬编码在这里。这解释了为什么 `--version` 能做到零模块加载——`MACRO.VERSION` 已经挂在全局对象上了，不需要任何 import。
`BUILD_TARGET` 设为 `"external"` 尤其有意思。代码中到处有 `"external" as string === 'ant'` 这样的比较（注意 `"external"` 作为字面量，而 `'ant'` 是比较对象）。这个值决定了 Anthropic 内部版和外部版的行为差异——内部版有更多的迁移逻辑、遥测收集和实验功能。
### 安全加固：工厂围墙
在进入主路径之前，`cli.tsx` 还做了两道安全加固。
第一道是防止 Corepack 自动修改 `package.json`：

```typescript
process.env.COREPACK_ENABLE_AUTO_PIN = "0";
```

第二道是内存限制。如果检测到运行在 CCR（Claude Code Runtime）容器环境中，会设置 Node.js 子进程的最大堆内存为 8GB：

```typescript
if (process.env.CLAUDE_CODE_REMOTE === "true") {
  const existing = process.env.NODE_OPTIONS || "";
  process.env.NODE_OPTIONS = existing
    ? `${existing} --max-old-space-size=8192`
    : "--max-old-space-size=8192";
}
```

为什么要 8GB？因为容器通常配 16GB 内存，给 Bun 主进程和其他进程留出足够空间。这个值不是拍脑袋定的——它是在生产环境中观测到 OOM 后调优出来的。
### 动态导入：只背你需要的包
当所有快速路径都匹配失败，代码最终会走到默认路径：

```typescript
// 开始捕获早期输入（用户在加载过程中键入的内容）
const { startCapturingEarlyInput } = await import("../utils/earlyInput.js");
startCapturingEarlyInput();
// 动态加载 main.tsx
const { main: cliMain } = await import("../main.jsx");
await cliMain();
```

这里有两个值得注意的设计。
第一，`startCapturingEarlyInput()`。在加载 `main.tsx` 的几毫秒到几百毫秒之间，用户可能已经在键盘上敲东西了。这个函数会开始缓冲 stdin 输入，等 REPL 界面准备好后再回放。这是一个追求极致体验的设计——连"加载中的键盘输入"都不放过。
第二，`main.jsx` 的扩展名。注意它是 `.jsx` 而不是 `.tsx`。Bun 运行时不关心扩展名——它能直接运行 TypeScript 和 TSX 文件。这里的 `.jsx` 只是源码文件的命名习惯。
沿途还有 `profileCheckpoint` 埋点，追踪每个阶段的耗时：

```typescript
profileCheckpoint("cli_entry");
// ... 快速路径检测 ...
profileCheckpoint("cli_before_main_import");
const { main: cliMain } = await import("../main.jsx");
profileCheckpoint("cli_after_main_import");
await cliMain();
profileCheckpoint("cli_after_main_complete");
```

这些埋点帮助 Anthropic 团队监控启动性能，定位瓶颈。在工厂的比喻里，它就像门口打卡机上记录每辆卡车进出时间的探头。
### 从大门到调度中心
`cli.tsx` 的设计哲学可以浓缩为一句话：**能不做的事就不做，能晚做的就晚做**。
快速路径检测避免了不必要的模块加载。`feature()` 门禁通过编译时消除让 40% 的条件分支消失。动态导入确保只有真正需要的代码才进入内存。MACRO 变量注入让常量在编译时就固定下来。
但大门终究只是大门。当 `cliMain()` 被调用，卡车驶入工厂大门的那一刻，它面对的是一座更复杂的调度中心——Commander.js 的命令体系、preAction 初始化链、交互与非交互模式的分叉。这些都在 `main.tsx` 里等着它。
现在，让我们跟着卡车走进调度中心。
---
## §05 调度中心
The Dispatch Center — main.tsx
你在终端里敲下 `claude`，然后等了大概一秒钟。这一秒钟里发生了什么？你的内心 OS 大概是这样的："不就是解析几个命令行参数，然后弹个界面出来吗？"
对，也不对。这一秒钟里，`main.tsx` 已经跑完了：MDM（移动设备管理）设置加载、钥匙串预取、遥测初始化、数据库迁移、远程配置拉取、权限模式设定、并行加载三组数据，然后根据你的运行环境分叉到交互式 REPL 或者无头模式。这些步骤里，任何一步失败都可能导致启动中断，但大部分步骤你甚至不知道它们存在。
`main.tsx` 大约 4600 行。别被这个数字吓到——大部分行是 Commander.js 的选项定义和 action handler。核心启动链路其实相当清晰：`main()` → `run()` → preAction 钩子 → action handler → REPL 或 Headless。
### main() 做的第一件事不是解析参数
`main()` 函数的前几行做的事，和命令行参数完全无关：

```typescript
export async function main() {
  // 安全：防止 Windows 从当前目录执行命令（PATH 劫持防护）
  process.env.NoDefaultCurrentDirectoryInExePath = '1';
  // 初始化警告处理器，捕获早期警告
  initializeWarningHandler();
  // 进程退出时重置光标
  process.on('exit', () => { resetCursor(); });
}
```

`NoDefaultCurrentDirectoryInExePath` 这个环境变量是 Windows 安全防护。在 Windows 上，如果你在当前目录有一个和系统命令同名的可执行文件（比如 `cls.exe`），系统会优先执行当前目录的版本。设置这个变量可以阻止这种行为。
光标重置也很巧妙——如果 Ink（终端 UI 框架）在异常退出时没有正确恢复光标状态，`exit` 事件处理器会兜底处理。这是防御性编程的典型例子。
然后才调用 `run()`——真正的命令解析和分派。
### preAction 钩子：启动前的初始化链
`run()` 函数创建 Commander.js 的 program 实例，然后挂载了一个关键的 `preAction` 钩子：

```typescript
program.hook('preAction', async thisCommand => {
  // 1. 等待 MDM 设置和钥匙串预取完成
  await Promise.all([
    ensureMdmSettingsLoaded(),
    ensureKeychainPrefetchCompleted(),
  ]);
  // 2. 初始化核心系统
  await init();
  // 3. 挂载日志管道
  initSinks();
  // 4. 运行数据库迁移
  runMigrations();
  // 5. 非阻塞：加载远程托管设置和策略限制
  void loadRemoteManagedSettings();
  void loadPolicyLimits();
});
```

这段代码的信息密度极高，值得逐行拆解。
`ensureMdmSettingsLoaded()` 和 `ensureKeychainPrefetchCompleted()` 为什么放在最前面？因为它们在 `main.tsx` 的模块顶层就已经通过 `startMdmRawRead()` 和 `startKeychainPrefetch()` 启动了子进程。在模块加载的 ~135 毫秒里，这些子进程在后台并行执行。到了 preAction 钩子，只需 `await` 它们的结果——几乎零等待。
| 初始化步骤 | 耗时 | 阻塞？ | 失败会怎样 |
|-----------|------|--------|-----------|
| MDM 设置加载 | ~50ms | 是（但已在后台运行） | 使用缓存值继续 |
| 钥匙串预取 | ~65ms | 是（但已在后台运行） | 跳过 OAuth 密钥 |
| `init()` | ~30ms | 是 | 启动中断 |
| `initSinks()` | <5ms | 是 | 日志丢失 |
| `runMigrations()` | ~10ms | 是 | 使用旧配置继续 |
| `loadRemoteManagedSettings()` | 网络请求 | 否（void） | 使用本地设置继续 |
| `loadPolicyLimits()` | 网络请求 | 否（void） | 使用默认策略继续 |
注意最后两个用 `void` 标记的调用。`void` 在 TypeScript 里不仅是类型关键字，作为语句时它的语义是"我主动丢弃这个 Promise 的结果"。这意味着 `loadRemoteManagedSettings()` 和 `loadPolicyLimits()` 是真正的 fire-and-forget——它们在后台运行，不会阻塞启动。即使网络请求超时或失败，用户也不会感知到。
> **核心建议**：在阅读 `main.tsx` 的初始化代码时，区分"阻塞"和"非阻塞"是关键。`await` 的调用是必须等它完成才能继续的；`void` 的调用是"能做就做，做不了拉倒"。后者的失败是设计上允许的，而不是 bug。
### Commander.js 选项：六个分类
`run()` 函数用了一长串 `.option()` 调用来定义命令行选项。按功能分类更清晰：
| 分类 | 代表选项 | 用途 |
|------|---------|------|
| 调试 | `--debug`, `--verbose`, `--debug-file` | 开发者调试和日志 |
| 模式 | `--print`, `--bare` | 交互 vs 无头 vs 极简 |
| 输出 | `--output-format`, `--json-schema` | 控制输出格式和结构 |
| 会话 | `--continue`, `--resume`, `--fork-session` | 恢复和管理对话 |
| 模型 | `--model`, `--effort`, `--fallback-model` | 模型选择和配置 |
| 配置 | `--settings`, `--mcp-config`, `--add-dir` | 外部配置注入 |
其中 `--bare` 是个特别有意思的选项。它设置 `CLAUDE_CODE_SIMPLE=1`，跳过 hooks、LSP、插件同步、自动记忆、后台预取、钥匙串读取和 CLAUDE.md 自动发现。相当于把工厂切换到"最小运行模式"——只保留核心生产线，关掉所有辅助系统。适合 CI/CD 和脚本化调用。
### 并行初始化：三个赛道同时起跑
当 action handler 确定要执行默认命令（启动 REPL 或 Headless）时，代码做了一个关键的并行化操作：

```typescript
// 在 setup() 启动前，先注册内置插件和技能（纯内存操作，<1ms）
initBuiltinPlugins();
initBundledSkills();
// setup() 负责工作目录、worktree、权限等初始化
const setupPromise = setup(preSetupCwd, permissionMode, ...);
// getCommands() 加载斜杠命令
const commandsPromise = worktreeEnabled ? null : getCommands(preSetupCwd);
// getAgentDefinitionsWithOverrides() 加载自定义 Agent 定义
const agentDefsPromise = worktreeEnabled ? null : getAgentDefinitionsWithOverrides(preSetupCwd);
// 等待 setup 完成后再等 commands 和 agents（它们和 setup 并行运行了）
await setupPromise;
```

这里的设计考虑了一个微妙的依赖关系：`setup()` 可能会执行 `process.chdir()`（当使用 `--worktree` 时），而 `getCommands()` 和 `getAgentDefinitionsWithOverrides()` 需要在正确的目录下读取文件。所以当 `worktreeEnabled` 为 true 时，后两者被跳过，等 setup 完成后再在后续逻辑里加载。
当 `worktreeEnabled` 为 false 时，三件事并行运行。`setup()` 的 ~28ms 主要是 UDS（Unix Domain Socket，一种进程间通信机制，不走网络）消息通道的建立，不涉及磁盘 IO，不会和文件读取密集的 `getCommands()` 争抢资源。
### 交互 vs 非交互：工厂的两条产线
在所有初始化完成后，代码来到一个关键的分叉点：

```typescript
const hasPrintFlag = cliArgs.includes('-p') || cliArgs.includes('--print');
const isNonInteractive = hasPrintFlag || hasInitOnlyFlag || hasSdkUrl || !process.stdout.isTTY;
if (isNonInteractive) {
  stopCapturingEarlyInput();
} else {
  // 交互模式：继续缓冲键盘输入
}
setIsInteractive(!isNonInteractive);
initializeEntrypoint(isNonInteractive);
```

判断非交互模式的条件有四个：
1. `-p` / `--print` 标志（pipe 模式）
2. `--init-only` 标志（只运行初始化钩子）
3. `--sdk-url` 标志（SDK 调用模式）
4. `!process.stdout.isTTY`（标准输出不是终端——比如被管道重定向了）
非交互模式走 `runHeadless()` 路径——接收输入、调用 API、输出结果、退出。没有 UI、没有键盘监听、没有实时渲染。
交互模式走 `launchRepl()` 路径——启动 Ink/React 渲染的终端界面，进入持续的事件循环。
| 维度 | 交互模式 (REPL) | 非交互模式 (Headless) |
|------|-----------------|----------------------|
| 入口 | `launchRepl()` | `runHeadless()` |
| UI | Ink/React 终端渲染 | stdout 直接输出 |
| 输入 | 键盘实时监听 | stdin 单次读取 |
| 会话持久化 | 支持 `/resume` | 可选（`--no-session-persistence`） |
| 权限提示 | 弹出交互式确认 | 必须预配置 |
| 典型场景 | 开发者日常使用 | CI/CD、脚本、SDK |
### 延迟预取：把活藏到用户看不见的地方
在 REPL 模式下，首次渲染完成后，会调用 `startDeferredPrefetches()`。这个函数的设计理念是"用户在看界面的时候，我们在后台偷偷干活"：

```typescript
export function startDeferredPrefetches(): void {
  // 如果是极简模式或只需要测量启动性能，跳过所有预取
  if (isBareMode() || isEnvTruthy(process.env.CLAUDE_CODE_EXIT_AFTER_FIRST_RENDER)) {
    return;
  }
  // 用户信息预取（等用户输入提示词时完成）
  void initUser();
  void getUserContext();
  prefetchSystemContextIfSafe();
  // 云服务凭证预取
  if (/* 使用 Bedrock */) void prefetchAwsCredentialsAndBedRockInfoIfSafe();
  if (/* 使用 Vertex */) void prefetchGcpCredentialsIfSafe();
  // 文件计数（用 ripgrep，3秒超时）
  void countFilesRoundedRg(getCwd(), AbortSignal.timeout(3000), []);
  // 功能开关初始化
  void initializeAnalyticsGates();
  void refreshModelCapabilities();
  // 文件变更检测器
  void settingsChangeDetector.initialize();
  void skillChangeDetector.initialize();
}
```

每个 `void` 调用都是非阻塞的。它们在事件循环的空闲时间执行，不会影响 UI 渲染和用户输入响应。等用户真正输入第一个提示词时，这些数据已经在内存里准备好了。
这里有一个细节值得注意：`prefetchSystemContextIfSafe()` 会检查是否已建立信任关系（trust dialog accepted）。在交互模式下，Git 命令可能执行任意代码（通过 hooks 和 config），所以只有确认用户已信任当前目录后才运行。非交互模式则默认信任——这也是 `--print` 模式跳过信任对话框的原因，帮助文档里已经说明了这一点。
### 从调度中心到生产线
`main.tsx` 的约 4600 行看起来吓人，但它的核心启动链路可以压缩成六步：
1. 安全初始化 + 信号处理
2. preAction 钩子：MDM/钥匙串/核心初始化/迁移/远程配置
3. Commander.js 选项解析和命令匹配
4. 并行加载 setup/commands/agents
5. 交互 vs 非交互分叉
6. 延迟预取启动
整个流程像一个精心编排的交响乐——每个模块在正确的时间进入，有些必须同步等待（`await`），有些在后台默默运行（`void`），有些被 feature flag 挡在门外（编译时消除）。
但不管是 REPL 还是 Headless，当用户输入的第一个提示词准备好发送时，它们都汇聚到同一个地方——`query.ts` 的核心循环。那是工厂里轰鸣的生产线，消息进去、工具调用出来、AI 回复产生、循环往复。
让我们走进那条生产线。
---
## §06 生产线
The Production Line — query.ts Core Loop
你输入了一句话："帮我把这个函数拆成两个。"然后你看着终端里的文字一段段出现，接着 Claude 开始读文件、编辑代码、运行测试。你看到的这一切，背后是一个 `while(true)` 循环在疯狂运转。
这个循环就在 `query.ts` 里，大约 1700 行。但核心循环结构本身并不复杂——它做的事可以浓缩成一句话：**把消息发给 API，拿到回复，如果回复里有工具调用就执行工具，然后把结果拼回去继续发，直到没有工具调用为止。**
问题在于"细节"二字。流式响应怎么处理？工具可以并发执行吗？上下文太长怎么办？API 报错了怎么恢复？用户按了 Ctrl+C 怎么办？这些才是 `query.ts` 真正要解决的问题。
### 函数签名：AsyncGenerator（一种可以暂停和恢复的异步迭代器）的妙用
`query()` 函数的签名长这样：

```typescript
export async function* query(
  params: QueryParams,
): AsyncGenerator<
  | StreamEvent        // 流式事件（文本片段、工具调用等）
  | RequestStartEvent  // 请求开始事件
  | Message            // 完整消息
  | TombstoneMessage   // 消息删除标记
  | ToolUseSummaryMessage,  // 工具使用摘要
  Terminal             // 返回值类型
> {
```

`async function*` 是 JavaScript 的异步生成器语法。它和普通 `async function` 的区别在于：普通函数 `return` 一次就结束了，而异步生成器可以 `yield` 多次，每次 yield 都把一个值推给调用者，然后暂停自己，等调用者再要下一个值时继续执行。
这个设计选择不是偶然的。`query()` 的调用者（REPL 或 Headless）需要实时接收流式事件来更新 UI——文本一个字一个字地出现、工具调用一个个地执行。如果用普通函数，要么等整个循环跑完再一次性返回所有结果（用户等半天什么也看不到），要么传入回调函数（代码耦合度高，控制流复杂）。
`AsyncGenerator` 提供了第三条路：`query()` 在循环里 `yield` 每个事件，调用者用 `for await...of` 消费。这是一个"推-拉"模型——生成器主动推数据，但节奏由调用者控制。
| 方案 | 实时性 | 控制流 | 取消支持 |
|------|--------|--------|---------|
| 同步返回 | 差（等全部完成） | 简单 | 不支持 |
| 回调函数 | 好 | 复杂（回调地狱） | 需手动实现 |
| AsyncGenerator | 好 | 清晰（for await） | `.return()` / `.throw()` |
`QueryParams` 包含循环需要的所有输入：

```typescript
export type QueryParams = {
  messages: Message[]              // 对话历史
  systemPrompt: SystemPrompt       // 系统提示词
  userContext: { [k: string]: string }   // 用户上下文
  systemContext: { [k: string]: string } // 系统上下文
  canUseTool: CanUseToolFn         // 权限检查函数
  toolUseContext: ToolUseContext    // 工具执行上下文
  fallbackModel?: string           // 备用模型
  querySource: QuerySource         // 查询来源标识
  maxTurns?: number                // 最大循环轮次
  taskBudget?: { total: number }   // Token 预算
  // ...
}
```

### while(true)：永远不会停的传送带
`queryLoop()` 里的核心结构是一个 `while(true)` 循环。每一轮循环做四件事：

```text
┌──────────────────────────────────────────────┐
│  while (true) {                               │
│    1. 消息预处理（压缩/裁剪/预算检查）          │
│    2. 调用 Anthropic API（流式）                │
│    3. 处理 SSE 事件流 → 收集文本和工具调用        │
│    4. 如有工具调用：执行工具 → 继续循环           │
│       如无工具调用：退出循环                     │
│  }                                            │
└──────────────────────────────────────────────┘
```

在代码中，它看起来像这样（简化后）：

```typescript
while (true) {
  let messagesForQuery = [...getMessagesAfterCompactBoundary(messages)];
  // ---- 阶段1：消息预处理 ----
  messagesForQuery = await applyToolResultBudget(messagesForQuery, ...);
  // snip 裁剪（如果 feature flag 开启）
  // microcompact 微压缩
  // autocompact 自动压缩
  yield { type: 'stream_request_start' };
  // ---- 阶段2和3：调用 API + 处理流式响应 ----
  const toolUseBlocks: ToolUseBlock[] = [];
  let needsFollowUp = false;
  for await (const message of deps.callModel({
    messages: prependUserContext(messagesForQuery, userContext),
    systemPrompt: fullSystemPrompt,
    tools: toolUseContext.options.tools,
    // ...
  })) {
    yield message;  // 实时推送给上层
    if (message.type === 'assistant') {
      // 收集工具调用
      if (msgToolUseBlocks.length > 0) {
        toolUseBlocks.push(...msgToolUseBlocks);
        needsFollowUp = true;
      }
  // ---- 阶段4：工具执行或退出 ----
  if (!needsFollowUp) {
    return { reason: 'completed' };  // 没有工具调用，循环结束
  }
  // 执行工具...
  for await (const update of runTools(toolUseBlocks, ...)) {
    yield update.message;
    toolResults.push(update.message);
  }
  // 把工具结果拼入消息，更新状态，继续下一轮循环
  state = {
    messages: [...messagesForQuery, ...assistantMessages, ...toolResults],
    turnCount: nextTurnCount,
    // ...
  };
}
```

每一轮循环代表一个"turn"（轮次）。用户的第一句话是 turn 1，API 返回的工具调用执行后产生的消息让循环进入 turn 2，依此类推。`turnCount` 追踪当前轮次，`maxTurns` 限制最大轮次（只在非交互模式下生效）。
### 消息预处理链：传送带上的四道工序
在把消息发给 API 之前，消息要经过最多四道预处理工序。每一道都解决一个特定的问题：
| 工序 | 函数 | 解决的问题 | 特点 |
|------|------|-----------|------|
| 工具结果预算 | `applyToolResultBudget` | 单条工具结果太大 | 截断超大结果 |
| Snip 裁剪 | `snipCompactIfNeeded` | 历史消息过长 | 保留近期，摘要远期 |
| 微压缩 | `microcompact` | 小范围上下文压缩 | 增量式，低成本 |
| 自动压缩 | `autocompact` | 上下文窗口溢出 | 完整摘要，高成本 |
它们按顺序执行，前一道的结果作为后一道的输入。autocompact 是最重的一步——它会调用另一个模型来生成对话摘要，替换掉之前的完整历史。这个操作的成本很高（额外的 API 调用），所以只在 Token 数接近上下文窗口上限时触发。
### 流式响应处理：流水线上的实时检测
`deps.callModel()` 返回的是一个异步可迭代对象，每次 yield 一个 SSE（Server-Sent Events）事件。`query.ts` 用 `for await...of` 逐个处理这些事件：

```typescript
for await (const message of deps.callModel({ ... })) {
  // withholding 机制：某些错误消息暂不推送给用户
  let withheld = false;
  if (isWithheldMaxOutputTokens(message)) withheld = true;
  if (reactiveCompact?.isWithheldPromptTooLong(message)) withheld = true;
  if (!withheld) {
    yield message;  // 实时推送给上层
  }
  // 收集 assistant 消息中的工具调用块
  if (message.type === 'assistant') {
    assistantMessages.push(message);
    const toolUseBlocks = message.message.content
      .filter(block => block.type === 'tool_use');
    if (toolUseBlocks.length > 0) {
      needsFollowUp = true;
    }
```

注意 `withheld` 机制。某些错误（如"输出 Token 超限"或"提示词太长"）在流式响应中被检测到后，不会立即推送给用户，而是先尝试自动恢复——比如重新压缩上下文后重试，或者调大输出 Token 限制后重试。只有恢复失败后，错误才会被 surface 出来。这是 `query.ts` 最精巧的设计之一：**先尝试自救，再告诉用户出了问题**。
### 工具执行：串行与并发的调度艺术
当 `needsFollowUp` 为 true 时，`query.ts` 会执行收集到的工具调用。入口是 `runTools()` 函数，它有一个聪明的调度策略：

```typescript
async function* runTools(toolUseMessages, ...): AsyncGenerator<MessageUpdate> {
  for (const { isConcurrencySafe, blocks } of partitionToolCalls(toolUseMessages)) {
    if (isConcurrencySafe) {
      // 只读工具批量并发执行
      yield* runToolsConcurrently(blocks, ...);
    } else {
      // 写入工具串行执行
      yield* runToolsSerially(blocks, ...);
    }
```

`partitionToolCalls()` 把工具调用分成批次。连续的只读工具（如 `Read`、`Grep`）被分到同一批并发执行，写入工具（如 `Edit`、`Write`、`Bash`）则单独串行执行。
举个例子：如果 API 返回了 5 个工具调用，按顺序是 `Read(A)` `Read(B)` `Edit(C)` `Read(D)` `Edit(E)`，那么 `partitionToolCalls` 会把它分成三批：
| 批次 | 工具 | 执行方式 |
|------|------|---------|
| 1 | `Read(A)` + `Read(B)` | 并发 |
| 2 | `Edit(C)` | 串行 |
| 3 | `Read(D)` | 并发（只有1个，和串行效果一样） |
| 4 | `Edit(E)` | 串行 |
这个分类通过每个工具的 `isConcurrencySafe()` 方法判断。`Read` 工具检查自己的输入参数，只读文件的操作标记为安全，并发执行不会产生冲突。`Bash` 工具虽然可能只执行 `git status` 这种只读命令，但保守起见仍然标记为不安全——因为无法静态分析 shell 命令的副作用。
### 循环终止：六条出路
`while(true)` 循环不会永远转下去。它有六条出路：

```typescript
// 出路1：没有工具调用，正常完成
if (!needsFollowUp) {
  return { reason: 'completed' };
}
// 出路2：达到最大轮次限制
if (maxTurns && nextTurnCount > maxTurns) {
  return { reason: 'max_turns', turnCount: nextTurnCount };
}
// 出路3：用户中断（Ctrl+C）
if (toolUseContext.abortController.signal.aborted) {
  return { reason: 'aborted_streaming' }; // 或 'aborted_tools'
}
// 出路4：Token 预算耗尽
if (decision.action !== 'continue') {
  return { reason: 'completed' };
}
// 出路5：Hook 阻止继续
if (shouldPreventContinuation) {
  return { reason: 'hook_stopped' };
}
// 出路6：API 错误
return { reason: 'model_error', error };
```

每条出路都返回一个 `Terminal` 对象，包含 `reason` 字段说明为什么退出。调用者可以根据这个原因做不同处理——比如 `max_turns` 时显示提示信息，`aborted` 时中断工具执行并清理资源。
### 错误处理与回退：自救三部曲
`query.ts` 的错误处理堪称教科书级别。它不是简单地 try/catch 然后报错，而是实现了"自救三部曲"：
**第一部：模型回退。** 如果主模型过载，自动切换到备用模型：

```typescript
if (innerError instanceof FallbackTriggeredError && fallbackModel) {
  currentModel = fallbackModel;
  attemptWithFallback = true;  // 重试
  yield createSystemMessage(
    `Switched to ${fallbackModel} due to high demand`,
    'warning'
  );
  continue;
}
```

**第二部：上下文压缩。** 如果提示词太长（413 错误），先尝试增量压缩（context collapse），再尝试完整压缩（reactive compact）：

```typescript
if (isWithheld413) {
  // 先尝试轻量恢复
  const drained = contextCollapse.recoverFromOverflow(messagesForQuery, ...);
  if (drained.committed > 0) { state = next; continue; }
  // 再尝试重量恢复
  const compacted = await reactiveCompact.tryReactiveCompact(...);
  if (compacted) { state = next; continue; }
}
```

**第三部：输出 Token 扩容。** 如果输出被截断，先自动从 8k 提升到 64k 重试。如果还是超限，注入一条"继续完成"的消息让模型接着输出：

```typescript
if (isWithheldMaxOutputTokens(lastMessage)) {
  // 先尝试 64k
  if (maxOutputTokensOverride === undefined) {
    state = { ..., maxOutputTokensOverride: ESCALATED_MAX_TOKENS };
    continue;
  }
  // 再尝试多轮恢复
  if (maxOutputTokensRecoveryCount < LIMIT) {
    const recoveryMessage = createUserMessage({
      content: 'Output token limit hit. Resume directly — pick up mid-thought.',
      isMeta: true,
    });
    state = { messages: [...previous, recoveryMessage] };
    continue;
  }
```

这三部曲的设计逻辑是**先低成本恢复，再高成本恢复，最后才告诉用户**。大部分情况下用户根本不知道发生了错误——循环在后台自动解决了问题，然后正常返回结果。
> **核心建议**：`query.ts` 最值得学习的设计不是循环结构本身，而是错误恢复策略。当你设计自己的 Agent 循环时，不要只考虑"出错怎么办"，更要考虑"出错后怎么自动恢复"。给循环加上重试、回退、压缩恢复这些机制，用户体验会有质的飞跃。
### 从生产线看总调度室
`query.ts` 的 `while(true)` 循环是 Claude Code 的心脏。它接收消息、调用 API、执行工具、处理错误、yield 事件。但它不知道自己在第几轮对话、不知道用户切换了什么模式、不知道会话什么时候该保存。这些"元信息"的管理在它之上——`QueryEngine`。
如果把 `query()` 比作一条不断运转的生产线，那 `QueryEngine` 就是总调度室。它决定什么时候启动生产线、什么时候压缩历史、什么时候结束会话。生产线只管干活，调度室管全局。
下一章，我们走进总调度室。
## §07 总调度室
The Control Room — QueryEngine.ts
凌晨三点，工厂里的警报响了。三号生产线的上下文窗口快要爆了，Token 数量逼近模型极限。你冲进总调度室，看到墙上的大屏闪烁着红色警告——但调度系统已经自动启动了压缩程序。五秒后，警报解除。总调度室把最近 200 条旧消息压缩成了一段精炼的摘要，生产线继续运转。
这就是 QueryEngine 干的事。上一章我们跟着 query() 走完了单次 API 调用的核心循环，但那只是车间里的一条产线。总调度室站在更高的位置，管理整座工厂的会话状态：消息来了要持久化、上下文太长要压缩、文件改了要记快照、钱花超了要踩刹车。理解了它，你就理解了 Claude Code 为什么能在一场对话中稳定运转几百个回合。
### 一个类，一场会话
QueryEngine 的设计原则很简单：**一个对话，一个实例**。每次你启动一个新的 Claude Code 会话，就有一个 QueryEngine 被创建出来。它贯穿整个会话的完整生命周期，管理所有跨回合的状态。

```typescript
// QueryEngine 持有会话的全部可变状态
export class QueryEngine {
  private config: QueryEngineConfig       // 会话配置（工具、命令、MCP 客户端等）
  private mutableMessages: Message[]      // 消息列表——会话的核心数据
  private abortController: AbortController // 中断控制器
  private permissionDenials: SDKPermissionDenial[]  // 权限拒绝记录
  private totalUsage: NonNullableUsage     // 累计 token 用量
  private readFileState: FileStateCache    // 文件状态缓存
  // ...
}
```

这些字段里，`mutableMessages` 是最重要的。它是整个会话的消息存储，每一条用户消息、助手回复、工具调用结果都追加到这个数组里。它也是后续压缩操作的目标——上下文窗口有限，消息不能无限增长。
`submitMessage()` 是 QueryEngine 对外暴露的唯一核心方法。每次用户发一条新消息，就调用一次 `submitMessage()`，它会：
1. 处理用户输入（包括斜杠命令展开）
2. 把新消息持久化到转录日志
3. 调用底层的 `query()` 函数进入核心循环
4. yield 格式化的 SDK 消息给调用方
整个过程是一个 `AsyncGenerator`——调用方通过 `for await...of` 消费消息流。这种设计让 QueryEngine 既能被 SDK 的 headless 模式使用，也能被交互式 REPL 使用。
### 消息的两次写入
你可能会问：为什么要管消息持久化？直接放在内存里不就行了？
不行。因为进程可能在任何时候挂掉。你发了一条消息、模型正在思考、用户点了 Stop——这时候进程被杀了。如果没有提前把用户消息写入磁盘，转录日志里就没有这条记录，下次用 `--resume` 恢复会话时就会丢失上下文。QueryEngine 的源码注释把这个场景写得很清楚：

```typescript
// 在进入查询循环之前持久化用户消息。
// 如果进程在 API 响应之前被杀死（比如用户在 cowork 模式下点击了 Stop），
// 转录日志只会有队列操作的条目；getLastSessionLog 返回 null，--resume 就会失败。
// 现在写入使得转录可以从用户消息被接受的那一刻恢复，即使没有收到任何 API 响应。
```

它还区分了阻塞写入和异步写入：在 bare/simple 模式下（脚本调用），写入是 fire-and-forget 的，不阻塞主流程；在普通模式下，写入是阻塞的，确保数据安全落盘后才继续。在 cowork 模式下，还会额外调用 `flushSessionStorage()` 强制刷新缓冲区。
### 四层压缩：工厂的废料回收系统
工厂运行久了，车间的库存（上下文）会越来越多。模型有一个固定的上下文窗口（比如 200K Token），一旦消息总量逼近这个限制，就必须想办法腾出空间。QueryEngine 管理着一套多层压缩策略，就像工厂的废料回收系统——不同类型的废料有不同的处理方式。
| 压缩策略 | 触发条件 | 工作方式 | 效果 |
|---|---|---|---|
| auto-compact | Token 数超过阈值（上下文窗口 - 13K 缓冲） | 调用 API 生成对话摘要，替换旧消息 | 大幅减少 Token（典型压缩比 5-10x） |
| micro-compact | API 返回 Token 数超限的警告 | 清除旧工具调用结果和思考块 | 轻量级，不调用额外 API |
| snip compaction | 检测到 snip 边界标记 | 裁剪旧消息，保留最近的活跃段 | 适用于长时间 SDK 会话 |
| reactive-compact | API 返回 `prompt_too_long` 错误 | 紧急压缩，响应式触发 | 兜底策略，防止崩溃 |
![压缩策略](images/compression-strategy.png)
auto-compact 是主力策略。它的工作方式很精妙：不是简单地删掉旧消息，而是把整个对话历史发给模型，让模型生成一段精炼的摘要。这个摘要被包装成一条特殊的"压缩边界"消息，替换掉之前的全部历史。压缩后，模型的上下文窗口一下子就有了大量可用空间。

```typescript
// auto-compact 的阈值计算
export const AUTOCOMPACT_BUFFER_TOKENS = 13_000  // 保留 13K 的缓冲空间
export function getAutoCompactThreshold(model: string): number {
  const effectiveContextWindow = getEffectiveContextWindowSize(model)
  return effectiveContextWindow - AUTOCOMPACT_BUFFER_TOKENS
}
```

13K Token 的缓冲看起来很大，但它是必要的。压缩本身需要消耗输出 Token（摘要通常几千 Token），而且压缩后模型还需要足够的空间来思考和调用工具。如果缓冲设得太小，模型刚压缩完就又触发了下一次压缩，陷入死循环。
micro-compact 是一种更轻量的策略。它不需要额外的 API 调用，而是利用 Anthropic API 的原生上下文管理功能（context management edits）。当 API 检测到输入 Token 过多时，可以在 API 层面直接清除旧的工具调用结果（比如文件搜索结果、命令输出）和思考块。这种方式速度极快，但压缩比有限。
还有一个细节很有趣：auto-compact 有一个熔断机制。如果连续压缩失败超过 3 次（比如摘要本身太长导致再次超限），就停止尝试。源码注释记录了真实的运维数据——2026 年 3 月的统计显示有 1,279 个会话出现了 50 次以上的连续失败，最极端的达到了 3,272 次，每天浪费约 25 万次 API 调用。加了熔断之后，这种情况被彻底杜绝了。
### 压缩后的消息管理
压缩完成后，总调度室需要做一件微妙的事：**清理消息数组**。如果只是往数组里追加压缩边界消息，旧消息仍然占据内存。在长时间的 SDK 会话中，`mutableMessages` 会无限增长——这是内存泄漏。
QueryEngine 的做法是：压缩边界消息被 push 进数组后，立即 `splice(0, boundaryIndex)`，把边界之前的所有消息删掉。只保留边界消息和之后的新消息。这样内存使用始终是有界的。

```typescript
// 释放压缩前的消息，让 GC 回收
const mutableBoundaryIdx = this.mutableMessages.length - 1
if (mutableBoundaryIdx > 0) {
  this.mutableMessages.splice(0, mutableBoundaryIdx)
}
```

同时，转录日志（transcript）仍然保留完整的压缩前记录——splice 只影响内存中的数组，不影响已经写入磁盘的文件。这意味着 `--resume` 恢复会话时，仍然能看到完整的对话历史。
### 文件历史快照：追踪每一处改动
工厂的质检部门需要记录每个零件的加工过程。QueryEngine 通过 `fileHistory` 模块做类似的事——在每次用户发消息之前，给当前工作目录的所有被跟踪文件拍一张"快照"。

```typescript
if (fileHistoryEnabled() && persistSession) {
  messagesFromUserInput
    .filter(messageSelector().selectableUserMessagesFilter)
    .forEach(message => {
      void fileHistoryMakeSnapshot(
        updater => { /* 更新 AppState 中的 fileHistory */ },
        message.uuid,
      )
    })
}
```

每个快照记录了被跟踪文件在那一刻的版本号和备份路径。当模型在后续回合中修改了文件，系统可以对比快照，计算出哪些行被增加、哪些行被删除。这些统计数据最终展示在会话的成本报告中。
快照有上限——最多保留 100 个，老的快照会被淘汰。但 `snapshotSequence` 计数器永远递增，即使快照被淘汰，这个计数器也可以作为活动信号使用。
### 归因跟踪：谁改了什么
工厂的产品追溯系统需要知道每个零件是哪条产线加工的。归因跟踪（commit attribution）做的是类似的事：追踪文件修改是哪个模型在哪个会话中做的。
当模型通过 FileEditTool 或 FileWriteTool 修改文件后，这些修改最终可能会被用户 `git commit`。归因系统会在 git commit 的 trailer 里添加 `Authored-by: claude-code` 和模型名称，这样就能在 git 历史中追溯哪些代码是 AI 生成的。对于 Anthropic 内部的私有仓库，甚至可以看到具体的模型代号（如 claude-sonnet-4-20250514），但对于公开仓库则只显示通用名称——这是防止内部代号泄露的安全措施。
### Token 预算与成本追踪
总调度室的大屏上有一栏是实时显示的：**累计成本**。
QueryEngine 在每一轮 API 调用后都会更新 Token 用量统计。它跟踪的粒度很细：
- 每条消息的输入 Token、输出 Token
- 缓存命中 Token（cache read / cache creation）
- 每个模型的单独用量（跨模型回退时会切换模型）
- 每次工具调用的执行时间
- 总 API 耗时（不含重试）和总耗时（含重试）

```typescript
// 在 stream_event 的 message_start 和 message_stop 之间累计用量
if (message.event.type === 'message_start') {
  currentMessageUsage = EMPTY_USAGE
  currentMessageUsage = updateUsage(currentMessageUsage, message.event.message.usage)
}
if (message.event.type === 'message_stop') {
  this.totalUsage = accumulateUsage(this.totalUsage, currentMessageUsage)
}
```

这些数据会在每次 `submitMessage()` 结束时打包成 result 消息，包含 `total_cost_usd`、`usage`、`modelUsage` 等字段。SDK 调用方可以据此实现成本控制。
QueryEngine 还支持两个硬性预算限制：`maxTurns`（最大回合数）和 `maxBudgetUsd`（最大美元成本）。每轮结束后检查是否超限，超了就立即 yield 一个错误结果并终止。

```typescript
// 检查美元预算是否已超出
if (maxBudgetUsd !== undefined && getTotalCost() >= maxBudgetUsd) {
  yield { type: 'result', subtype: 'error_max_budget_usd', ... }
  return
}
```

> **核心建议**
> 理解 QueryEngine 的关键在于把它看成"会话的一生"的管理者。它不关心单次 API 调用的细节（那是 query() 的事），它关心的是：消息不能丢、上下文不能爆、成本不能跑飞。这三件事就是总调度室的 KPI。当你在调试长时间会话的内存问题或成本异常时，第一时间看 QueryEngine 的状态管理逻辑。
### 权限拒绝追踪
还有一个小但重要的功能：权限拒绝记录。QueryEngine 包装了 `canUseTool` 回调，在每次权限检查后记录拒绝结果：

```typescript
// 包装 canUseTool 以跟踪权限拒绝
const wrappedCanUseTool: CanUseToolFn = async (...) => {
  const result = await canUseTool(...)
  if (result.behavior !== 'allow') {
    this.permissionDenials.push({
      tool_name: sdkCompatToolName(tool.name),
      tool_use_id: toolUseID,
      tool_input: input,
    })
  }
  return result
}
```

这些记录在会话结束时返回给 SDK 调用方，帮助他们了解哪些工具调用被权限系统拒绝了。
### ask()：一次性便捷包装
除了 QueryEngine 类，源码还导出了 `ask()` 函数——它是 QueryEngine 的一次性包装。如果你只需要发一条消息拿结果，不需要管理会话状态，直接调 `ask()` 就行。它内部创建一个临时 QueryEngine 实例，执行完就把文件读取缓存写回给调用方。

```typescript
// ask() 是 QueryEngine 的一次性便捷包装
export async function* ask({ ... }): AsyncGenerator<SDKMessage, void, unknown> {
  const engine = new QueryEngine({ ... })
  try {
    yield* engine.submitMessage(prompt, { uuid: promptUuid, isMeta })
  } finally {
    setReadFileCache(engine.getReadFileState())
  }
```

总调度室的故事到这里就差不多了。消息管理、压缩回收、成本控制——这些是让工厂持续运转的基础设施。但工厂光有调度室不行，还得有能干活的工具。下一站，我们去车间看看工具是怎么注册和执行的。
---
## §08 车间工具站
Tool Stations — Registration & Execution
你站在工厂的车间里，面前是一整面墙的工具架。左边是重型设备——BashTool、FileEditTool，用的时候得小心翼翼；右边是轻型量具——GlobTool、GrepTool，随手拿来就能用；角落里还有一台可以派生出微型车间的 AgentTool。每个工具上面贴着一张标签：名称、用途、安全等级。
这套工具管理系统是怎么运作的？工具怎么注册上来、怎么被发现、怎么被安全地执行？这一章我们走进工具站，拆解这套机制。
### 工具的定义格式
在 Claude Code 的世界里，每个工具都遵循同一个接口规范——`Tool` 类型。这个类型定义在 `Tool.ts` 里，是所有工具（无论是内置的还是 MCP 外部的）的"身份证"。它的核心字段如下：

```typescript
export type Tool = {
  name: string                    // 工具名称，如 "Bash"、"Read"、"Edit"
  aliases?: string[]              // 别名，用于向后兼容重命名
  description(input, options)     // 根据输入动态生成描述
  readonly inputSchema: z.ZodType // Zod schema，定义输入参数的类型约束
  call(args, context, ...)        // 执行工具，返回结果
  isConcurrencySafe(input)        // 是否可以与其他工具并发执行
  isReadOnly(input)               // 是否是只读操作
  isDestructive?(input)           // 是否有破坏性（不可逆）
  checkPermissions(input, ctx)    // 权限检查
  userFacingName(input)           // 用户可见的显示名称
  maxResultSizeChars: number      // 结果持久化的阈值
  // ... 渲染相关的方法（renderToolUseMessage 等）
}
```

其中最重要的三个方法是 `call()`、`isConcurrencySafe()` 和 `isReadOnly()`。`call()` 是工具的执行逻辑，后两个决定了工具的调度策略。
但实际开发中，大部分工具不需要实现所有方法。`buildTool()` 函数提供了一套安全默认值：

```typescript
const TOOL_DEFAULTS = {
  isEnabled: () => true,           // 默认启用
  isConcurrencySafe: () => false,  // 默认不可并发（安全优先）
  isReadOnly: () => false,         // 默认非只读
  isDestructive: () => false,      // 默认非破坏性
  checkPermissions: (input) =>     // 默认交给通用权限系统
    Promise.resolve({ behavior: 'allow', updatedInput: input }),
  toAutoClassifierInput: () => '', // 默认跳过安全分类器
  userFacingName: () => '',        // 默认无显示名
}
```

注意 `isConcurrencySafe` 的默认值是 `false`——这是一个"fail-closed"的设计。如果一个工具没有显式声明自己可以并发执行，系统就假设它不行。宁可牺牲一点性能，也不要冒并发冲突的风险。
![工具注册与过滤流水线](images/tool-filtering-pipeline.png)
### 注册流程：工具怎么上架
工具不是一股脑全堆在工具架上。`tools.ts` 中的 `getAllBaseTools()` 函数是所有内置工具的注册中心，但它不是简单地返回一个静态列表——它会根据环境动态过滤。
注册流程分为四层过滤：
**第一层：环境变量过滤。** 有些工具只在特定环境下可用。比如 REPLTool 只在 `USER_TYPE === 'ant'`（内部用户）时注册；LSPTool 需要 `ENABLE_LSP_TOOL` 环境变量开启；PowerShellTool 只在特定平台上启用。

```typescript
// 条件导入：Dead code elimination 让未使用的工具根本不进入打包
const REPLTool = process.env.USER_TYPE === 'ant'
  ? require('./tools/REPLTool/REPLTool.js').REPLTool
  : null
```

注意 `require()` 是条件执行的——如果环境不满足，变量直接是 `null`。配合 Bun 的 dead code elimination，这些代码路径在打包阶段就被移除了，不影响最终产物大小。
**第二层：Feature Flag 过滤。** 通过 `feature()` 函数（Bun 的编译时特性门控）控制的工具包括 SleepTool、CronTools、MonitorTool、WorkflowTool 等。这些通常是实验性功能或内部功能。
**第三层：模式过滤。** `getTools()` 函数在 `getAllBaseTools()` 的基础上进一步过滤。在 simple 模式下（`CLAUDE_CODE_SIMPLE=true`），只保留 Bash、Read、Edit 三个工具。在 REPL 模式下，某些原始工具（如 Bash、Read、Edit）会被隐藏，因为 REPL 工具会在虚拟机内部调用它们。
**第四层：权限过滤。** `filterToolsByDenyRules()` 把被权限规则明确禁止的工具过滤掉。注意这是"批量拒绝"——如果用户配置了拒绝某个 MCP 服务器的所有工具，这些工具根本不会出现在模型的工具列表中，而不是等到调用时才拒绝。
### 与 MCP 工具合并
内置工具和 MCP 工具最终要合并成一个统一的工具池。`assembleToolPool()` 函数负责这个合并：

```typescript
export function assembleToolPool(
  permissionContext: ToolPermissionContext,
  mcpTools: Tools,
): Tools {
  const builtInTools = getTools(permissionContext)
  const allowedMcpTools = filterToolsByDenyRules(mcpTools, permissionContext)
  // 按名称排序以保证提示缓存稳定性，内置工具优先
  const byName = (a, b) => a.name.localeCompare(b.name)
  return uniqBy(
    [...builtInTools].sort(byName).concat(allowedMcpTools.sort(byName)),
    'name',  // 内置工具同名时优先保留（uniqBy 保留首次出现）
  )
}
```

这里有一个精妙的设计：排序是为了提示缓存的稳定性。模型的系统提示包含了所有工具的定义，如果工具列表的顺序每次都变，提示缓存就会失效，导致重复发送大量相同的 Token。按名称排序保证了确定性。内置工具放在前面，`uniqBy` 在同名冲突时保留第一个出现——所以内置工具的优先级始终高于 MCP 工具。
### 并发安全与调度策略
工具执行不是一视同仁的。Claude Code 的调度策略根据工具的安全特性分为两条路径：**并发执行**和**串行执行**。
分区逻辑在 `partitionToolCalls()` 中实现：

```typescript
function partitionToolCalls(toolUseMessages, toolUseContext): Batch[] {
  return toolUseMessages.reduce((acc, toolUse) => {
    const tool = findToolByName(toolUseContext.options.tools, toolUse.name)
    const isSafe = tool?.isConcurrencySafe(parsedInput.data) ?? false
    // 连续的并发安全工具合并为一个批次
    if (isSafe && acc[acc.length - 1]?.isConcurrencySafe) {
      acc[acc.length - 1].blocks.push(toolUse)
    } else {
      acc.push({ isConcurrencySafe: isSafe, blocks: [toolUse] })
    }
    return acc
  }, [])
}
```

这个分区算法的关键在于：只有**连续的**安全工具才会被合并到一个批次。如果模型在一次回复中调用了三个工具：Read、Edit、Glob，那么 Read 和 Glob 各自是安全的，但因为中间夹了一个不安全的 Edit，它们会被分到不同的批次。
| 调度模式 | 条件 | 并发度 | 示例工具 |
|---|---|---|---|
| 并发执行 | `isConcurrencySafe()` 返回 true | 最大 10 | Glob、Grep、WebFetch、WebSearch、TaskGet |
| 串行执行 | `isConcurrencySafe()` 返回 false 或解析失败 | 1 | Bash、Edit、Write、Agent |
并发执行时使用 `pMap` 控制最大并发数为 10（可通过环境变量 `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY` 调整）。串行执行时，每个工具执行完后才会启动下一个。
还有一个安全细节：如果 `isConcurrencySafe()` 本身抛了异常（比如 shell-quote 解析失败），系统会保守地把工具归类为不安全。宁可少一点并发，也不要引入竞态条件。
### 关键工具实现
工具架上最常用的几件"重型设备"，各有各的绝活。
**BashTool**——工厂的通用机床。它执行 shell 命令，是最灵活也最危险的工具。安全措施包括：沙箱执行（通过 SandboxManager 隔离）、语义命令分类（把命令分为 search/read/list 等类型，决定输出截断策略）、安全检查（扫描命令中的危险模式）。`isConcurrencySafe()` 的判断基于语义分类——只读命令（如 `ls`、`grep`）可以并发，写入命令（如 `rm`、`npm install`）不行。
**FileReadTool**——工厂的质检探针。它不只读文本文件，还支持 PDF（分页读取）、图片（视觉模型处理）、Jupyter Notebook（按 cell 读取）。它有设备文件保护（不读 `/dev/random` 这类特殊文件）和文件大小限制（超大会被截断）。`isConcurrencySafe()` 始终返回 true——读文件不会产生副作用。
**FileEditTool**——工厂的精密切割机。它使用字符串替换式编辑，而不是传统的行号编辑。这种方式的好处是：即使文件在读取和编辑之间被修改了，只要目标字符串还在，编辑就能成功。`replace_all` 模式可以一次替换所有匹配。安全检查包括：拒绝 UNC 路径（Windows 网络路径）、扫描秘密信息（API key、密码等）。`isConcurrencySafe()` 始终返回 false——文件编辑不能并发。
**FileWriteTool**——工厂的焊接工。它负责创建新文件或完全覆盖已有文件。每次写入后会生成 diff，让用户可以预览变更。同样不可并发执行。
**AgentTool**——工厂的子车间。这是最特殊的工具：它可以派生出一个子代理，在隔离的 worktree 中独立执行任务。子代理有自己的消息历史和工具集，执行完后把结果返回给父代理。它支持后台运行（`run_in_background`），让主流程不必等待。这个工具的存在让 Claude Code 具备了"多线程"能力——多个任务可以并行推进。
### 工具特性对比
| 工具 | 并发安全 | 只读 | 典型用途 | 安全等级 |
|---|---|---|---|---|
| BashTool | 视命令而定 | 视命令而定 | 执行 shell 命令 | 高（沙箱隔离） |
| FileReadTool | 是 | 是 | 读取文件内容 | 低（只读） |
| FileEditTool | 否 | 否 | 字符串替换式编辑 | 中（秘密扫描） |
| FileWriteTool | 否 | 否 | 创建/覆盖文件 | 中（diff 预览） |
| GlobTool | 是 | 是 | 文件名模式匹配 | 低 |
| GrepTool | 是 | 是 | 内容搜索 | 低 |
| WebFetchTool | 是 | 是 | 抓取网页内容 | 低 |
| WebSearchTool | 是 | 是 | 网络搜索 | 低 |
| AgentTool | 否 | 否 | 派生子代理 | 高（worktree 隔离） |
| NotebookEditTool | 否 | 否 | 编辑 Jupyter Notebook | 中 |
> **核心建议**
> 工具系统的设计哲学是"默认安全"。`isConcurrencySafe()` 默认 false，权限检查默认交给通用系统，工具描述可以动态调整。当你在开发自定义工具时，先想清楚三个问题：它是只读的吗？它可以并发吗？它有破坏性吗？把这三个问题的答案明确地实现在对应的方法里，工具就会在调度系统中被正确对待。
工具站逛完了。这些是工厂自带的内置工具。但现实中的工厂不会什么都自己造——有些工序需要外协供应商来做。下一章，我们走进外部供应商通道，看看 MCP 协议如何把外部工具接入这座工厂。
---
# Part 3: 深入系统

## §09 外部供应商通道
The Supply Channel — MCP Protocol
工厂的围墙上有几扇特殊的门，外面停着一排供应商的卡车。每辆卡车代表一个 MCP 服务器——它们不是工厂自有的产线，但通过标准化的装卸协议（Model Context Protocol），可以把外部的工具、资源、命令无缝接入工厂的生产流程。
供应商来了，先要验明身份（OAuth 认证），然后登记货物清单（工具发现），最后把货物合并到工厂的总仓库里（与内置工具合并）。这套流程就是 MCP 协议在 Claude Code 中的实现。
### MCP 架构概览
MCP（Model Context Protocol）是一个开放协议，定义了 AI 应用如何与外部工具和数据源通信。在 Claude Code 中，MCP 的实现大约 12,000 行代码，分布在 `src/services/mcp/` 目录下。
![MCP 架构概览](images/mcp-architecture.png)
架构上分三层：

```text
应用层（Claude Code）
  ├── MCP 客户端（client.ts）——管理连接、工具发现、工具调用
  ├── 传输层 ——负责底层通信
  │     ├── StdioClientTransport  ——标准输入/输出（本地进程）
  │     ├── SSEClientTransport    ——Server-Sent Events（HTTP 长连接）
  │     ├── StreamableHTTPClientTransport ——流式 HTTP
  │     └── WebSocketTransport    ——WebSocket
  └── 认证层（auth.ts）——OAuth 流程管理
```

MCP 的核心理念是：**外部服务器提供工具，Claude Code 作为客户端消费工具**。每个 MCP 服务器是一个独立进程或远程服务，通过 JSON-RPC 协议与 Claude Code 通信。服务器提供三种能力：工具（tools）、资源（resources）、提示（prompts）。
### 传输层：供应商的配送方式
供应商怎么把货物送到工厂？有几种不同的配送方式。
**Stdio 传输**——最常见的本地配送。MCP 服务器作为子进程启动，通过标准输入/输出通信。配置方式很直观：

```json
{
  "my-server": {
    "command": "npx",
    "args": ["-y", "@my/mcp-server"],
    "env": { "API_KEY": "..." }
  }
```

Stdio 传输的好处是零配置网络——没有端口冲突、没有防火墙问题。缺点是每个服务器是一个独立的操作系统进程，消耗资源。关闭时的清理也很讲究：先发 SIGINT（Ctrl+C），等 100ms；没退出就发 SIGTERM，再等 400ms；还没退出就 SIGKILL 强杀。总共最多 600ms，保证 CLI 的响应速度不受拖累。
**SSE 传输**——远程配送的第一种方式。通过 HTTP 长连接接收服务器推送的事件。适合部署在远程的 MCP 服务器。
**StreamableHTTP 传输**——更新一代的 HTTP 传输。支持 POST 请求发送消息、GET 请求接收 SSE 事件流。有一个容易踩的坑：MCP 规范要求每个 POST 请求都带上 `Accept: application/json, text/event-stream` 头，某些运行时会丢掉这个头。Claude Code 在传输层的最外层强制设置了这个头，保证合规。
**WebSocket 传输**——双向实时通信。支持 IDE 集成（如 VS Code 扩展通过 WebSocket 连接）。
每种传输都有独立的超时管理。连接超时默认 30 秒（`MCP_TIMEOUT` 环境变量可调），单次请求超时 60 秒。一个容易遇到的 bug 是 `AbortSignal.timeout()` 在 Bun 中的内存泄漏——即使请求已完成，底层的定时器对象仍然占用内存直到被 GC。Claude Code 改用 `setTimeout` + 手动 `clearTimeout` 来解决这个问题。
### 连接管理：供应商准入流程
不是所有供应商都能直接把货物卸在工厂里。连接管理有一套准入流程。
`connectToServer()` 函数是整个准入流程的入口。它被 `memoize` 包装——相同配置的重复连接会复用缓存结果，避免重复建立连接。流程如下：
1. **选择传输层**——根据配置的 `type` 字段（stdio/sse/http/ws/ide）选择对应的传输实现
2. **创建 MCP 客户端**——`new Client()` 创建 MCP SDK 客户端实例
3. **建立连接**——`client.connect(transport)` 发起连接，有超时保护
4. **获取能力声明**——`client.getServerCapabilities()` 查询服务器支持哪些功能
5. **获取服务器指令**——`client.getInstructions()` 获取服务器的使用说明（截断到 2048 字符）
连接建立后，客户端会注册事件处理器。最关键的是 `onclose` 和 `onerror`——它们负责连接断开后的重连逻辑。当连接断开时，`onclose` 会清除 memoize 缓存、清除工具/资源/命令的获取缓存，这样下次访问时就会自动重建连接。
对于远程传输（SSE/HTTP），还有一个终端错误检测器。如果连续出现 3 次 ECONNRESET、ETIMEDOUT 等致命错误，就主动关闭连接触发重连。比等到所有工具调用超时才反应要快得多。
连接管理还区分了本地服务器和远程服务器的并发策略。本地服务器（stdio）因为要 fork 进程，并发数设为 3；远程服务器只是网络连接，并发数设为 20。两者通过 `pMap` 并行连接，每个服务器连接完成后立即回调通知上层，不用等其他服务器。
### 工具发现与合并
供应商通过准入后，需要把它的货物清单报上来。这就是工具发现。
`fetchToolsForClient()` 向 MCP 服务器发送 `tools/list` 请求，获取服务器提供的所有工具列表。每个工具被转换成 Claude Code 内部的 `Tool` 格式：

```typescript
// MCP 工具转换为内部 Tool 格式
return toolsToProcess.map(tool => ({
  ...MCPTool,                                  // 使用 MCP 工具的通用实现
  name: buildMcpToolName(client.name, tool.name),  // 如 "mcp__slack__search"
  mcpInfo: { serverName: client.name, toolName: tool.name },
  isMcp: true,
  isConcurrencySafe() {
    return tool.annotations?.readOnlyHint ?? false  // 读取 MCP 标准注解
  },
  async call(args, context, ...) {
    const connectedClient = await ensureConnectedClient(client)
    const result = await callMCPToolWithUrlElicitationRetry(...)
    return { data: result.content }
  },
  // ...
}))
```

注意工具命名规则：MCP 工具的全名是 `mcp__服务器名__工具名`。这个前缀确保了不同服务器的同名工具不会冲突。但在 SDK 模式下，可以通过 `CLAUDE_AGENT_SDK_MCP_NO_PREFIX` 环境变量去掉前缀，让 MCP 工具直接覆盖同名内置工具。
工具的 `isConcurrencySafe()` 直接读取 MCP 标准的 `readOnlyHint` 注解。这是 MCP 规范定义的标准字段，MCP 服务器实现者在工具的 annotations 中声明。如果服务器没有声明，默认是不可并发——又是 fail-closed 的思路。
合并到统一工具池的逻辑我们在上一章已经看过了：`assembleToolPool()` 把内置工具和 MCP 工具合并，按名称排序，同名冲突时内置工具优先。
### 资源与命令
除了工具，MCP 服务器还可以提供**资源**和**命令**。
资源（resources）是 MCP 服务器暴露的数据对象——比如数据库表、文件系统目录、API 响应。Claude Code 通过 `resources/list` 发现资源列表，通过 `ListMcpResourcesTool` 和 `ReadMcpResourceTool` 两个内置工具来操作它们。
命令（prompts，在 MCP 术语中叫 prompts）是预定义的交互模板。比如 Slack 的 MCP 服务器可以提供 "search-messages" 命令，Claude Code 会把它注册为斜杠命令 `/mcp__slack__search-messages`，用户可以直接调用。
### OAuth 认证：供应商的身份证
远程供应商（SSE/HTTP）通常需要认证。MCP 协议使用 OAuth 2.0 授权码流程，Claude Code 的 `ClaudeAuthProvider` 实现了完整的 OAuth 客户端：
1. **发现授权服务器元数据**（`discoverAuthorizationServerMetadata`）——从服务器的 `.well-known/oauth-authorization-server` 端点获取授权 URL
2. **打开浏览器授权页面**（`openAuthFlow`）——启动本地 HTTP 服务器监听回调，然后在浏览器中打开授权页面
3. **交换授权码获取令牌**（`exchangeCodeForTokens`）——用户授权后，用授权码换取 access Token 和 refresh Token
令牌被安全存储在操作系统的密钥管理器中（macOS Keychain、Windows Credential Manager、Linux Secret Service）。刷新令牌时使用文件锁（lockfile）防止并发竞争。
如果认证失败（401 Unauthorized），服务器会被标记为 `needs-auth` 状态，并生成一个特殊的 `McpAuthTool`。用户在 REPL 中看到这个工具的调用时，会触发重新认证流程。为了避免频繁重试已知需要认证的服务器，认证失败的状态会被缓存 15 分钟。
### MCP vs 内置工具
| 维度 | 内置工具 | MCP 工具 |
|---|---|---|
| 来源 | 编译时打包 | 运行时连接 |
| 注册方式 | `getAllBaseTools()` 静态列表 | `tools/list` 动态发现 |
| 命名格式 | `Bash`、`Read`、`Edit` | `mcp__server__tool` |
| 权限检查 | 通用权限系统 + 工具自定义 | 通用权限系统 + MCP 注解 |
| 并发安全 | 工具自行实现 | `readOnlyHint` 注解 |
| 输入验证 | Zod schema | JSON Schema |
| 连接管理 | 无需连接 | memoize 缓存 + 自动重连 |
| 安全隔离 | 进程内 | 子进程 / 远程服务 |
| 结果大小限制 | `maxResultSizeChars` | 自动截断或持久化到文件 |
| 描述长度 | 无限制 | 截断到 2048 字符 |
| 同名冲突 | 优先级高 | 优先级低（同名被内置覆盖） |
MCP 工具还有一个内置工具不具备的能力：**URL 引导**（URL Elicitation）。某些 MCP 工具在执行过程中可能需要用户在浏览器中完成某个操作（比如授权第三方服务）。工具会返回 `-32042` 错误码，Claude Code 拦截这个错误，弹出引导窗口让用户完成操作，然后自动重试工具调用。最多重试 3 次。
### 大结果处理
外部供应商返回的货物有时候会特别大——一个数据库查询可能返回几 MB 的文本。Claude Code 不会把这些大结果直接塞进模型的上下文窗口。
`processMCPResult()` 函数实现了多级处理策略：
1. 先检查结果大小是否需要截断（`mcpContentNeedsTruncation`）
2. 如果包含图片，走截断路径（持久化会破坏图片压缩）
3. 否则，把大结果保存到磁盘文件，返回一个简短的"请阅读文件"提示
4. 如果文件保存失败，回退到截断路径
文件名格式是 `mcp-server-tool-timestamp`，保存在 Claude Code 的临时目录中。模型收到的是一个包含文件路径和格式说明的文本提示，它可以后续用 Read 工具查看完整内容。
> **核心建议**
> MCP 的设计哲学是"协议优先、实现第二"。所有 MCP 相关的代码都围绕 JSON-RPC 协议构建，不依赖任何特定语言或运行时。当你在开发自己的 MCP 服务器时，最重要的是正确实现协议约定的注解（`readOnlyHint`、`destructiveHint`、`openWorldHint`）——这些注解决定了你的工具在 Claude Code 中如何被调度和安全检查。不要忽略它们。
供应商通道走完了。工厂现在有了自有的工具站和外部供应商的扩展能力。但无论是自有工具还是外部工具，每一次操作都需要通过安全检查——就像工厂的每一道工序都需要经过品控。下一章，我们走进安检与品控部门，看看权限系统和 Hook 机制如何保护你的代码安全。
## §10 安检与品控 — 权限与Hook
Security & Quality Gates
"不会吧，我明明只是让它帮我改个文件，它怎么把整个目录都删了？"
这个噩梦场景，是每一个把 AI Agent 接入真实项目的人最深的恐惧。Claude Code 的回答是一套精密的双重防线——安检门负责"你能不能进"，品控检测点负责"你做得对不对"。
### 安检门：六种通行模式
源码中定义了六种权限模式：
| 模式 | 安检行为 | 适用场景 |
|---|---|---|
| `default` | 每个敏感操作都弹出确认 | 日常开发 |
| `plan` | 只读放行，写操作需确认 | 阅读分析代码 |
| `acceptEdits` | 自动允许文件编辑 | 信任的自动化流程 |
| `dontAsk` | 不弹确认框，但遵守规则 | CI/CD 流水线 |
| `bypassPermissions` | 跳过所有权限检查 | 紧急修复（需额外确认） |
| `auto` | 分类器自动判断（仅内部版） | 高级自动化 |
`bypassPermissions` 看起来像"完全敞开大门"，其实不然。源码里的权限检查流程有一条铁律：**deny 规则和 safetyCheck 规则即使在 bypass 模式下也必须执行**。

```typescript
// bypass 模式下的安全检查（safetyCheck）——不可绕过
if (
  toolPermissionResult?.behavior === 'ask' &&
  toolPermissionResult.decisionReason?.type === 'safetyCheck'
) {
  return toolPermissionResult // 即使 bypass 模式也强制弹出确认
}
```

### 权限检查流水线：五道关卡

```text
关卡 1a: deny 规则匹配 → 命中则直接拒绝
关卡 1b: ask 规则匹配 → 命中则强制弹出确认
关卡 1c: 工具自身权限检查 → 工具自定义的安全逻辑
关卡 2a: 模式检查 → bypass 模式直接放行
关卡 2b: allow 规则匹配 → 命中则直接放行
关卡 3:  转为 ask → 以上都没命中，弹出确认
```

| 关卡 | 检查内容 | 可被 bypass 绕过？ |
|---|---|---|
| 1a | deny 规则 | 否 |
| 1b | ask 规则 | 否 |
| 1c | 工具自身检查 | 部分（safetyCheck 不可绕过） |
| 2a | 模式检查 | 是（bypass 本身） |
| 2b | allow 规则 | 是 |
| 3 | 兜底 | 是 |
规则有六个来源：`userSettings`、`projectSettings`、`localSettings`、`flagSettings`（企业管理员下发）、`policySettings`、`cliArg`。优先级从高到低，企业管理员的 deny 规则一票否决。
### 品控检测点：Hook 系统
Hook 在 `settings.json` 中配置，分三种触发时机：
| Hook 类型 | 触发时机 | 典型用途 |
|---|---|---|
| `PreToolUse` | 工具执行前 | 安全审计、输入验证 |
| `PostToolUse` | 工具执行后 | 代码格式化、自动测试 |
| `PostToolUseFailure` | 工具执行失败后 | 错误上报 |
Hook 返回值可以影响权限决策，但 **Hook 的 allow 不能覆盖 deny/ask 规则**——安检门始终有最终决定权。
> **核心建议**
> 权限系统的设计精髓是"分层防御，绝不信任单点"。deny 规则 > ask 规则 > Hook 决策 > allow 规则 > 模式检查。配置时先用 deny 锁定高危操作，再用 allow 放行可信操作，最后用 Hook 做实时审计。
下一章走进控制面板——那个用 React 构建的终端界面。
## §11 控制面板 — Ink/React终端UI
The Dashboard — Ink/React Terminal UI
你在终端里运行 `claude`，屏幕上弹出了一个完整的交互式界面——消息气泡、工具调用卡片、权限确认对话框、底部输入框。这看起来像一个桌面应用，但它运行在纯终端里。
这个"不可能"的界面是用 React 写的。Ink——一个用 React reconciler 直接把组件树渲染成终端字符的框架。Claude Code 团队维护了自己的 Ink 分支。
### Ink 的秘密：React 在终端里怎么渲染

```text
React 组件树 → reconciler → 虚拟 DOM
                    ↓
            Yoga 布局计算（Flexbox）
                    ↓
            render-node-to-output（ANSI 字符串）
                    ↓
            终端屏幕更新
```

你可以用 React 的全部能力：`useState`、`useEffect`、`useContext`、`useMemo`。甚至 React Compiler 的 memoization 也被保留了。
### REPL.tsx：5000 行的主界面
渲染结构简化为：

```text
<REPL>
  ├── <KeybindingSetup>         // 快捷键上下文
  ├── <VirtualMessageList>      // 虚拟列表渲染消息
  │   └── <MessageRow> × N
  ├── <PermissionRequest>       // 权限确认对话框
  ├── <PromptInput>             // 底部输入框
  └── <SpinnerWithVerb>         // 等待状态动画
```

### 虚拟列表：高效渲染的秘密
| 参数 | 值 | 设计意图 |
|---|---|---|
| DEFAULT_ESTIMATE | 3 行 | 低估安全，高估导致空白 |
| OVERSCAN_ROWS | 80 行 | 充足缓冲区 |
| SCROLL_QUANTUM | 40 行 | 减少 React 重渲染 |
| MAX_MOUNTED_ITEMS | 300 | 防止内存爆炸 |
| SLIDE_STEP | 25 | 控制单次挂载渲染成本 |
虚拟列表的核心思路是：只挂载可见区域（视口）加上下缓冲区内的组件，视口外的消息用等高的空 `<Box>` 占位，保持滚动条位置正确。当用户滚动时，`onScroll` 事件触发重新计算可见范围，按 `SCROLL_QUANTUM`（40 行）为粒度批量调整挂载窗口，避免逐行触发 React 重渲染。每条消息的高度通过 `DEFAULT_ESTIMATE`（3 行）预估值 + 实际渲染后回填的方式动态维护，初始低估确保首次渲染不出空白行。超过 `MAX_MOUNTED_ITEMS`（300）的旧消息会被卸载回收内存，`SLIDE_STEP`（25）控制单次卸载的数量上限，防止大批量 DOM 操作造成帧率抖动。
### 用户交互：键盘、输入与滚动
REPL 的交互层有三个核心关注点。**输入处理**由 `<PromptInput>` 组件负责——它监听 stdin 的 `keypress` 事件，维护一个行缓冲区，支持多行编辑（Shift+Enter 换行）、历史记录上下翻（通过 `useHistory` hook）、Tab 补全（斜杠命令和文件路径）。输入完成后触发 `onSubmit`，文本被解析、包装、推入消息流。**滚动行为**由 `VirtualMessageList` 管理——自动滚动跟随新消息，但一旦用户主动向上滚动查看历史，自动跟随暂停，直到用户重新滚到底部。这个判断通过一个 `isUserScrolling` 状态实现，监听滚动偏移量与最大偏移量的差值。**快捷键**由 `<KeybindingSetup>` 统一注册，包括 Escape（取消当前操作）、Ctrl+C（中断流式响应）、Ctrl+L（清屏）等，通过 Ink 的 `useInput` hook 捕获原始键码并分发到对应的 action handler。
### 状态管理：两层架构
**第一层：Bootstrap 状态（进程级单例）。** `bootstrap/state.ts` 管理 sessionId、cwd、成本追踪。不走 React 渲染。
**第二层：AppState（React Context + Zustand）。** 消息列表、工具权限、MCP 连接。触发 React 渲染。
> **核心建议**
> 调试 UI 问题时，先确定数据在哪一层。Bootstrap 层查 `state.ts` 的 getter/setter；React 层查 `AppStateStore.ts` 的状态定义。
控制面板是你看到的 Claude Code 的全部。下一章，我们把前面所有模块串起来——跟踪一个真实的请求走完它的完整旅程。
# Part 4: 实战场景

## §12 一个请求的一生 — 全链路追踪
Lifecycle of a Request — Full Chain Trace
60 秒。从你按下回车发送"帮我重构 parseConfig 函数"到看到完整的回复，大约 60 秒。这 60 秒里，你的这句话穿过了工厂的每一个车间、每一道安检门、每一个品控检测点。
现在我们把前面十一章的知识串起来，跟着这句话走完它的一生。

```text
用户按下回车
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  L6 表现层：PromptInput 捕获输入 → parseReferences() 解析引用   │
│           → 斜杠命令路由 → UserMessage 追加到 AppState          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  L3 核心层：QueryEngine.submitMessage()                         │
│           → 持久化到 transcript → fileHistory 快照              │
│           → query() while(true) 循环启动                        │
│           → 四道预处理：budget → snip → micro → autocompact     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  L5 服务层：deps.callModel() → 流式 SSE 响应                    │
│           → 逐 token yield 给 REPL 渲染                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    有 tool_use？
                    ╱          ╲
                  是            否
                  │              │
                  ▼              ▼
┌──────────────────────┐   返回最终回复
│  L4 工具层：权限检查   │   → 成本记录
│  → PreToolUse Hook   │   → 会话结束
│  → canUseTool()      │
│  → 工具执行           │
│  → 结果追加到消息      │
└──────────┬───────────┘
           │
           ▼
      回到 while(true) 循环顶部
```

### 第 0 秒：入口与命令解析
`PromptInput` 组件捕获 `onSubmit` 事件。文本先经过 `parseReferences()` 扫描文件引用，斜杠命令被 `commands.ts` 拦截路由。处理后的文本被包装成 `UserMessage`，追加到 AppState。
### 第 0.1 秒：QueryEngine 接管
REPL 调用 `QueryEngine.submitMessage()`。总调度室持久化用户消息到转录日志，`fileHistory` 给工作目录拍快照。
### 第 0.2 秒：进入生产线
`query()` 进入 `while(true)` 循环。消息经过四道预处理：`applyToolResultBudget` → `snipCompactIfNeeded` → `microcompact` → `autocompact`。构建请求：系统提示词 + 用户上下文 + 工具列表。
### 第 0.3 秒：API 调用
`deps.callModel()` 发起流式请求。SSE 事件逐个到达，每个文本片段被 yield 给 REPL 渲染。
### 第 3 秒：模型请求工具调用
模型返回 `tool_use` 块（如 Read 工具读取文件）。`query()` 设置 `needsFollowUp = true`，进入工具执行阶段。
### 第 3.1 秒：安检门开启
`runPreToolUseHooks()` 执行 PreToolUse Hook，然后 `canUseTool()` 进入五道权限检查关卡。通过后工具放行执行。
### 第 3.5-15 秒：循环
工具结果追加到消息历史 → 第二轮 API 调用 → 模型决定编辑文件 → Edit 工具 → 第三轮 API → 模型决定跑测试 → BashTool → 第四轮 API → 最终回复。
### 全链路时序
| 阶段 | 耗时 | 涉及模块 |
|---|---|---|
| 输入预处理 | ~10ms | PromptInput、commands.ts |
| 消息持久化 | ~20ms | QueryEngine、transcript |
| 消息预处理 | ~50ms | compact 链 |
| API 调用（×4轮） | ~7s | api/claude.ts、流式处理 |
| 权限确认（×3次） | ~3s | canUseTool、PermissionRequest |
| 工具执行 | ~5s | FileReadTool、FileEditTool、BashTool |
| 结果渲染 + 成本记录 | ~15ms | VirtualMessageList、costTracker |
| **总计** | **~15s** | **15+ 模块** |
> **核心建议**
> 全链路追踪是理解复杂系统的终极方法。遇到 bug 时从入口沿数据流一步步追踪，不要从 UI 组件开始猜。设置 `CLAUDE_CODE_DEBUG=1` 可以看到完整的权限决策日志。
到此，你已经理解了 Claude Code 从入口到输出的完整架构。接下来的章节，我们从"怎么做"转向"为什么这样做"。
## §13 给工厂加一条产线
Adding a New Production Line
假设你想让 Claude Code 帮你查天气——输入"北京明天天气怎么样"，它却一脸茫然，因为它根本没有天气查询这条产线。工厂再智能，缺少对应的车间也产不出你想要的货。好消息是，Claude Code 的工具系统是可扩展的：你可以给它接上任意新的"产线"，从天气查询到数据库操作，从 Slack 通知到 Jira 工单，只要你能定义清楚输入和输出。
这一章我要带你从零造一条天气产线，走完工具定义、注册、权限配置、测试验证的完整流程。最后还会提到一条替代路径——通过 MCP 协议发布工具，不走内置注册。
### 工具是什么：产线的规格书
在工厂隐喻里，每条产线都有一份规格书，写明它叫什么、能做什么、需要什么原料、产出什么成品。Claude Code 的工具定义就是这个规格书。核心类型如下：

```typescript
type Tool<Input, Output> = {
  name: string                              // 产线名称，全局唯一标识
  description?: string                      // 向调度中心说明这条产线能干什么
  inputSchema: z.ZodType<any>               // 原料规格——用 Zod 校验输入合法性
  call: (input: Input, context: ToolUseContext) => Promise<ToolResult<Output>>  // 生产过程
  isConcurrencySafe?: (input: Input) => boolean  // 标记是否可以并行投产
  aliases?: string[]                        // 产线别名，方便引用
}
```

逐个字段拆解：
**name**——工具的唯一标识符。调度中心（模型）靠这个名字选择工具。命名要简洁、表意清晰，比如 `WeatherQuery` 比 `tool_1` 好一万倍。
**description**——告诉模型这个工具在什么场景下该用。这段描述直接决定了模型会不会正确"调度"你的工具。写得模糊，模型就不会用；写得精准，模型就知道什么情况下该调用它。
**inputSchema**——用 Zod 定义的输入校验 schema。原料进厂前要先过质检，不合格的直接打回去。Zod 的好处是既能在运行时校验，又能自动生成 JSON Schema 给模型看。
**call**——核心生产函数。接收校验过的输入和上下文，返回处理结果。这是产线的心脏。
**isConcurrencySafe**——可选的并发安全标记。有些工具可以同时跑好几条（比如读取不同文件），有些必须排队（比如写同一个文件）。这个函数接收输入参数，返回 true 表示这次调用可以和其他调用并行执行。
**aliases**——工具的别名列表。比如你可以给 `WeatherQuery` 加个别名 `天气`，方便中文环境下的使用。
### 造一条天气产线
现在我们动手。目标是造一个 `WeatherTool`，输入城市名和日期，返回天气信息。
**第一步：定义原料规格。**用 Zod 写输入 schema：

```typescript
import { z } from "zod"
const WeatherInputSchema = z.object({
  city: z.string().describe("城市名称，如'北京'、'Shanghai'"),
  date: z.string().optional().describe("查询日期，格式 YYYY-MM-DD，默认今天")
})
// Zod 的 describe() 会生成 JSON Schema 里的 description 字段
// 模型通过这个字段理解每个参数的含义
```

这段代码同时完成了两件事：运行时校验（`parse()` 或 `safeParse()`）和编译时类型推导（TypeScript 自动推导出 `WeatherInput` 类型）。你不需要手写接口定义——Zod schema 就是唯一的类型来源。
**第二步：实现生产函数。**`call()` 是工具的核心逻辑：

```typescript
import type { Tool, ToolResult, ToolUseContext } from "./tool-types"
async function queryWeather(
  input: z.infer<typeof WeatherInputSchema>,
  context: ToolUseContext
): Promise<ToolResult<{ temperature: number; condition: string }>> {
  const { city, date } = input
  const targetDate = date ?? new Date().toISOString().slice(0, 10)
  // 实际项目中这里调用第三方天气 API
  // context 里包含会话信息、日志工具等，可以用来记录调试信息
  context.log?.debug(`Querying weather for ${city} on ${targetDate}`)
  // 模拟 API 返回
  const result = await fetchWeatherFromAPI(city, targetDate)
  return {
    output: {
      temperature: result.temp,
      condition: result.condition
    }
```

注意 `context` 参数——它不是摆设。`ToolUseContext` 里包含了会话 ID、消息历史、权限状态等信息。高级工具可能需要读取上下文来决定行为，比如一个数据库查询工具可能需要根据用户的权限级别限制查询范围。
**第三步：组装完整工具。**把字段拼起来：

```typescript
const WeatherTool: Tool<WeatherInput, WeatherOutput> = {
  name: "WeatherQuery",
  description: "查询指定城市和日期的天气预报。当用户询问天气、气温、是否下雨等问题时使用此工具。",
  inputSchema: WeatherInputSchema,
  call: queryWeather,
  // 天气查询是只读操作，多次并发调用不会冲突
  isConcurrencySafe: () => true,
  aliases: ["weather", "天气查询"]
}
```

`isConcurrencySafe` 返回 `true`，因为天气查询是只读操作——查十次也不会互相干扰。如果这是一个"修改天气记录"的工具，就得返回 `false`，调度中心会让它排队执行。
### 注册产线：把规格书交到调度中心
工具定义好了，还得让工厂知道它的存在。这一步叫注册。
Claude Code 内部使用 `buildTool()` 函数来注册工具。你不需要手动调用它——工具在模块加载时自动注册到工具表中。但在理解机制时，知道注册过程做了什么很重要：

```typescript
// buildTool 内部逻辑简化
function buildTool<Input, Output>(toolDef: Tool<Input, Output>): RegisteredTool {
  return {
    name: toolDef.name,
    description: toolDef.description,
    // Zod schema 自动转换为 JSON Schema 供模型消费
    inputSchema: zodToJsonSchema(toolDef.inputSchema),
    execute: async (rawInput: unknown, context: ToolUseContext) => {
      // 质检：校验输入参数
      const parsed = toolDef.inputSchema.safeParse(rawInput)
      if (!parsed.success) {
        return { error: `输入参数校验失败: ${parsed.error.message}` }
      }
      // 通过质检后执行生产函数
      return toolDef.call(parsed.data, context)
    }
```

注册过程中最关键的转换是 `zodToJsonSchema()`。模型不认识 Zod 对象，它只认 JSON Schema。这个转换把 Zod 的类型约束翻译成模型能理解的格式描述。
### 两种注册路径对比
| 维度 | 内置工具注册 | MCP 协议发布 |
|------|-------------|-------------|
| 注册方式 | 代码中 import 后自动注册 | 在 `.mcp.json` 中配置 MCP 服务器 |
| 开发语言 | 必须是 TypeScript（与主项目同语言） | 任意语言（Python、Go、Rust 均可） |
| 工具命名 | 直接用 name 字段 | 自动加前缀 `mcp__服务器名__工具名` |
| 进程模型 | 与 Claude Code 同进程 | 独立子进程，通过 stdio/SSE 通信 |
| 分发方式 | 需要 Claude Code 本身支持 | 作为独立 npm 包或 Docker 镜像分发 |
| 适用场景 | 核心内置工具（Read、Write、Bash 等） | 第三方集成、团队自定义工具 |
| 冷启动 | 无额外开销 | 需要启动子进程，首次调用有延迟 |
内置注册适合与核心功能紧耦合的工具；MCP 发布适合独立的第三方服务。我们的天气工具调用外部 API，逻辑独立，用 MCP 是更自然的路径。
### 通过 MCP 发布天气工具
MCP（Model Context Protocol）是 Claude Code 的标准扩展协议。你只需要启动一个 MCP 服务器，声明它有哪些工具，Claude Code 就会自动发现并注册。配置写在项目的 `.mcp.json` 里：

```json
{
  "mcpServers": {
    "weather": {
      "command": "node",
      "args": ["./mcp-servers/weather-server.ts"],
      "env": {
        "WEATHER_API_KEY": "${WEATHER_API_KEY}"
      }
```

Claude Code 启动时会扫描 `.mcp.json`，为每个 `mcpServers` 条目启动一个子进程。工具名会被自动映射为 `mcp__weather__WeatherQuery` 的格式。你在终端里问"北京明天天气"，调度中心就会找到这条产线，把请求转发给天气 MCP 服务器。
MCP 服务器的实现可以用任何语言。用 TypeScript 的 `@modelcontextprotocol/sdk` 写起来最简单：

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js"
import { z } from "zod"
const server = new McpServer({ name: "weather", version: "1.0.0" })
server.tool(
  "WeatherQuery",
  "查询指定城市和日期的天气预报",
  { city: z.string().describe("城市名称"), date: z.string().optional().describe("日期") },
  async ({ city, date }) => {
    const result = await fetchWeatherFromAPI(city, date ?? today())
    return { content: [{ type: "text", text: `${city} ${date}: ${result.condition}, ${result.temp}°C` }] }
  }
)
// MCP 框架会自动处理 schema 转换、错误处理、进程间通信
// 你只需关注业务逻辑
```

### 权限配置：产线门禁
每条产线都需要门禁。不是所有操作都应该自动批准——让模型随意执行 `rm -rf` 或者向外部 API 发送数据的后果不堪设想。
Claude Code 的权限系统分三档：
| 权限级别 | 行为 | 适用场景 |
|---------|------|---------|
| `allow` | 自动批准，不弹确认框 | 只读操作、低风险工具 |
| `ask`（默认） | 每次调用前询问用户 | 涉及写操作或外部通信 |
| `deny` | 直接拒绝，不可使用 | 危险操作或被策略禁止 |
对于天气工具，推荐配置为 `allow`，因为它是纯只读的外部 API 调用。在 `.claude/settings.json` 中配置：

```json
{
  "permissions": {
    "allow": [
      "mcp__weather__WeatherQuery"
    ]
  }
```

如果你们公司的安全策略要求所有外部通信都要审批，就把它设为 `ask`。企业级配置可以通过管理策略文件统一推送，不需要每个开发者手动设置。
### 测试验证：产线验收
工具上线前要过验收。测试策略分两层：
**单元测试**——测试 `call()` 函数本身，mock 掉外部依赖：

```typescript
import { describe, it, expect, vi } from "vitest"
describe("WeatherTool", () => {
  it("返回正确的天气数据", async () => {
    // mock 外部 API，避免测试依赖网络
    vi.mock("./api", () => ({
      fetchWeatherFromAPI: vi.fn().mockResolvedValue({ temp: 22, condition: "晴" })
    }))
    const result = await queryWeather(
      { city: "北京", date: "2025-06-01" },
      mockContext
    )
    expect(result.output.temperature).toBe(22)
    expect(result.output.condition).toBe("晴")
  })
  it("拒绝无效城市名", async () => {
    const parsed = WeatherInputSchema.safeParse({ city: 123, date: "invalid" })
    expect(parsed.success).toBe(false)
  })
```

**集成测试**——在 Claude Code 会话中实际调用工具，验证端到端流程：

```text
> 北京明天天气怎么样？
[工具调用] mcp__weather__WeatherQuery({"city":"北京","date":"2025-06-02"})
[返回] 北京 2025-06-02: 晴, 28°C
北京明天（6月2日）天气晴朗，气温约28°C，适合户外活动。
```

测试通过，产线验收完成。你的天气工具正式上线了。
> **核心建议**
> 工具定义的关键在于 description 和 inputSchema。description 决定模型能不能选对你的工具，inputSchema 决定模型传的参数对不对。把这两个字段写好，工具就成功了一大半。isConcurrencySafe 也别忘标——标错了可能导致并发冲突或者不必要的串行等待。
到这里，你已经学会了怎么给工厂加产线。但产线加得越多，选择就越多，选错的概率也越大。为什么 Claude Code 的工具系统要这样设计？为什么用 Zod 而不是别的校验库？为什么 MCP 工具要跑在独立进程里？这些问题的答案藏在设计决策里。下一章，我们要钻进工程师的大脑，看看那些取舍背后的逻辑。
# Part 5: 深度思考

## §14 工程师的选择
Design Decisions & Trade-offs
一个约 4600 行的单文件、一个用 React 写的终端界面、一个基于 AsyncGenerator 的主循环——单看任何一个，你都会觉得这是某个疯狂原型。但把它们放在一起，却组成了目前最强大的 AI 编程助手之一。反直觉吗？一点也不。每一个看似"奇怪"的选择背后都有清晰的推理，只是在权衡取舍的天平上，另一端的砝码被大多数人忽略了。
这一章我要分析 Claude Code 的七个关键设计决策。我不会只告诉你"他们选了什么"，更重要的——为什么选这个、放弃了什么、什么场景下这个选择可能反噬。
### 决策一：为什么选 Bun 不选 Node
| 维度 | Bun | Node.js |
|------|-----|---------|
| 冷启动时间 | ~50ms | ~200ms |
| TypeScript 支持 | 原生，无需编译 | 需要转译或 tsx 等工具 |
| 内置打包 | `Bun.build()` 一个 API 搞定 | 需要 esbuild/webpack 等外部工具 |
| 包管理 | `bun install`，兼容 npm 生态 | `npm`/`yarn`/`pnpm` |
| 生态成熟度 | 较新，部分 API 不兼容 | 久经考验，库覆盖率高 |
Claude Code 是一个终端工具，用户输入命令后等待的第一毫秒都肉眼可见。冷启动 50ms vs 200ms，差了 150ms——可能不明显，但加上后续的模块加载、配置初始化，差距会累积。Bun 的原生 TS 支持也省去了构建步骤，开发体验更流畅。
但选择 Bun 也有代价：遇到 Bun 特定的 bug 时（比如早期版本的 `fetch` 实现问题），团队要自己修或者等上游修复，不像 Node 那样有庞大的社区可以快速找到解决方案。
### 决策二：为什么用 Ink/React 做终端 UI
"在终端里用 React？"——第一次看到这个选择时，多数人的反应是这样。
但想一下终端 UI 的实际需求：输出是动态的、结构化的、需要局部更新的。模型一边生成 Token 一边渲染，用户可能随时中断，工具调用的状态要实时展示。这些需求用传统的 `console.log` 或 `readline` 来做，代码会变成意大利面。
| 维度 | Ink/React | 传统 readline/ncurses |
|------|-----------|---------------------|
| 组件模型 | 声明式，可组合 | 命令式，手动管理状态 |
| 生态复用 | 直接用 React 生态（hooks、状态管理） | 终端 UI 库少且质量参差 |
| 渲染性能 | 虚拟列表，只重绘变化部分 | 全量重绘，大输出时闪烁 |
| 学习曲线 | 会 React 就会 Ink | 需要学终端渲染的底层细节 |
| 包体积 | 较大（React 运行时） | 极小 |
Ink 把终端输出抽象成了组件树。你可以写一个 `<ToolCallProgress>` 组件来展示工具执行状态，写一个 `<StreamingText>` 组件来渲染模型的流式输出。每个组件只关心自己的状态和渲染逻辑，不需要知道整个屏幕该怎么重绘。虚拟列表的高效渲染在展示大量文件搜索结果时尤其明显——只渲染可见行，不管结果有几千条。
代价是 React 运行时的包体积。但对于一个 CLI 工具来说，多几百 KB 的依赖换来开发效率的巨大提升，这笔账算得过来。
### 决策三：为什么主循环用 AsyncGenerator
Claude Code 的核心循环是一个 `AsyncGenerator`——每 yield 一次就是一条新消息。为什么不用回调？为什么不用 Promise 链？为什么不用 EventEmitter？

```typescript
// AsyncGenerator 的核心骨架
async function* query(messages: Message[]): AsyncGenerator<SDKMessage> {
  while (hasTokenBudget) {
    const response = await callModel(messages)
    for (const block of response.content) {
      if (block.type === "text") {
        yield { type: "assistant", content: block.text }
      }
      if (block.type === "tool_use") {
        const result = await executeTool(block)
        yield { type: "tool_result", content: result }
        messages.push(result)  // 工具结果喂回消息列表
      }
```

| 维度 | AsyncGenerator | 回调/Promise | EventEmitter |
|------|---------------|-------------|-------------|
| 流式输出 | 原生支持 yield | 需要额外流机制 | 通过事件模拟 |
| 可中断 | `return()` 方法立即停止 | 需要 AbortController | 需要 `removeListener` |
| 背压控制 | 消费者暂停时自动暂停生产 | 需要手动实现 | 无内置支持 |
| 组合性 | `yield*` 委托子生成器 | 回调地狱/Promise 链 | 事件嵌套 |
背压控制是关键。模型生成 Token 的速度可能远快于终端渲染的速度。AsyncGenerator 天然支持背压——消费者（渲染层）没来得及处理上一条消息时，生产者（模型调用）会自动暂停，不需要手动管理队列。这种机制在高负载场景下防止了内存溢出。
可中断性同样重要。用户点击 Stop 时，调用生成器的 `return()` 方法，整个循环干净地退出——没有悬挂的回调、没有泄漏的事件监听器。
### 决策四：为什么文件编辑用字符串替换而非行号
Claude Code 的 Edit 工具接收的参数是 `old_string` 和 `new_string`，而不是文件路径加行号范围。为什么？
| 维度 | 字符串替换 | 行号编辑 |
|------|-----------|---------|
| 精确性 | 匹配具体内容，不受行号偏移影响 | 行号会因为其他编辑而失效 |
| 合并冲突 | 每次只改一小段，冲突概率低 | 范围编辑容易和并发修改冲突 |
| 可审计 | diff 即编辑意图，一目了然 | 看到行号范围还要去对照原文 |
| 局限性 | 同一字符串出现多次时需额外处理 | 行号总是唯一的 |
行号编辑最大的问题是**脆弱**。假设模型决定编辑第 50-55 行，但在此之前另一个工具调用已经在第 30 行插入了 5 行——现在目标内容跑到了第 55-60 行，行号编辑会改错地方。字符串替换用内容匹配，不依赖行号，天然免疫这类偏移问题。
代价是：如果 `old_string` 在文件中出现多次，编辑会失败。Claude Code 要求用户提供足够的上下文使 `old_string` 唯一。这是一个合理的权衡——少量额外的上下文换来的是编辑操作的正确性保证。
### 决策五：为什么压缩分多层策略
我们在 §07 详细分析过四层压缩。这里只说为什么不用单一策略。
| 策略 | 触发时机 | 压缩力度 | 信息损失 |
|------|---------|---------|---------|
| auto-compact | Token 用量达阈值 | 中等——整轮对话压缩为摘要 | 丢失细节，保留决策逻辑 |
| micro-compact | 每次工具调用后 | 轻量——合并相邻同类消息 | 几乎无损 |
| snip | 消息内大段内容 | 局部——裁剪过长文件内容 | 丢失被裁剪部分 |
| 用户手动 `/compact` | 用户主动触发 | 最强——全量压缩为摘要 | 损失最大 |
单一策略要么压缩太猛（小对话也要压缩），要么压缩太弱（大对话撑爆上下文）。分层策略的好处是"对症下药"：micro-compact 做日常维护，代价极低；auto-compact 在快撑爆时介入；snip 专门处理单个大文件；`/compact` 留给用户手动救急。
### 决策六：单文件巨石 vs 模块化的取舍
`main.tsx` 有约 4600 行。你没看错，四千六百行。一个文件。
"这不违反了所有软件工程原则吗？"——先别急。
| 维度 | 单文件巨石 | 模块化拆分 |
|------|-----------|-----------|
| 初始化耦合 | 所有代码在同一作用域，共享状态无障碍 | 跨模块状态传递需要 import/export |
| 重构成本 | 全局搜索替换即可 | 需要改接口、更新导入路径 |
| 代码审查 | 一个文件，grep 即可全局搜索 | 需要跳转多个文件 |
| 编译速度 | Bun 单文件编译反而快 | 模块图解析有额外开销 |
| 团队协作 | Git 合并冲突频繁 | 冲突分散到不同文件 |
| 认知负担 | 需要在巨量代码中定位 | 每个模块可独立理解 |
Claude Code 的初始化逻辑高度耦合——CLI 参数解析、配置加载、权限初始化、工具注册、UI 渲染之间有大量交叉引用。拆成模块后，模块间的依赖关系图可能比单文件更难理解。团队的判断是：拆分的收益（认知分层）不足以抵消成本（模块间通信的复杂度）。
这个选择是否可持续？当团队扩大、贡献者增多时，约 4600 行的单文件会成为协作瓶颈。未来大概率会逐步重构。但在当前阶段，单文件带来的开发速度优势是真实的。
### 决策七：Feature Flag 的工程价值
Claude Code 使用 Statsig 管理 Feature Flag。每个新功能上线前都裹在一层开关后面。
| Feature Flag 用途 | 示例 | 价值 |
|------------------|------|------|
| 灰度发布 | 新压缩算法先对 5% 用户开放 | 发现问题的影响范围可控 |
| A/B 测试 | 两种不同的工具选择策略 | 数据驱动的决策 |
| 死代码消除 | 功能下线后删除 flag 代码 | 防止代码腐化 |
| 紧急开关 | 某功能出问题时一键关闭 | 不需要发版修复 |
Feature Flag 不是一个"有没有必要"的问题，而是一个"没有它会怎样"的问题。没有灰度发布，一个 bug 会同时影响所有用户；没有 A/B 测试，优化决策全凭直觉；没有紧急开关，出问题只能走 hotfix 流程，响应时间以小时计。
> **核心建议**
> 理解设计决策的关键不是记住"选了什么"，而是理解"放弃了什么"。每一个选择都是在特定约束下的最优解。当你自己构建系统时，不要盲目复制 Claude Code 的选择——要复制的是它的决策框架：列出候选方案、评估各维度权重、明确你的约束条件，然后做取舍。
七个决策拆完了。你可能会想："这些我都知道了，但我该怎么用这些知识？"好问题。最后一章，我要帮你把这些零散的认知整合成一套可行动的设计模式——从读懂 Claude Code 到能造你自己的 AI Agent CLI。
## §15 从读懂到能写
From Reading to Building
"源码我都读完了，架构图也画了，但让我从零搭一个 AI Agent CLI，还是不知道从哪下手。"——如果你有这种感觉，说明你读到了正确的地方。读懂源码和能写出来之间有一道坎：前者是理解别人的决策，后者是在自己的约束下做决策。这道坎不能靠"再看一遍"跨过去，只能靠动手。
这一章我要做三件事：从 Claude Code 里提炼出 5 个可复用的设计模式、给出一个最小 AI Agent 的核心模块骨架、推荐技术栈并规划从玩具到生产的演进路径。
### 模式一：AsyncGenerator 流式循环
这是整个系统的心脏。我们拆过很多次了，但这次要从"理解"切换到"使用"。

```typescript
// 消息循环的骨架——所有 AI Agent 的核心
async function* agentLoop(
  messages: Message[],
  tools: Map<string, ToolDef>
): AsyncGenerator<AgentEvent> {
  while (true) {
    const response = await callLLM(messages)
    // 流式输出文本块
    for (const block of response.content) {
      if (block.type === "text") {
        yield { type: "stream", text: block.text }
      }
    // 收集并执行工具调用
    const toolCalls = response.content.filter(b => b.type === "tool_use")
    if (toolCalls.length === 0) return  // 没有工具调用，循环结束
    // 下一节会讲到的并发调度
    const results = await executeTools(toolCalls, tools)
    messages.push(...results)
    // 工具结果喂回 LLM，继续循环
    yield { type: "tool_results", results }
  }
```

为什么是 AsyncGenerator 而不是普通 async 函数？三个字：**流、断、压**。流式输出用 yield 逐条推送；可中断用生成器的 `return()` 方法；背压控制是生成器的天然特性。如果你只用一个设计模式，用这个。
### 模式二：工具并发调度
模型一次可能请求调用多个工具。有些能并行跑，有些必须排队。Claude Code 的做法是先分类、再调度：

```typescript
function partitionToolCalls(
  calls: ToolCall[],
  tools: Map<string, ToolDef>
): { parallel: ToolCall[]; serial: ToolCall[] } {
  return calls.reduce((acc, call) => {
    const tool = tools.get(call.name)
    // isConcurrencySafe 决定了这条产线能不能和其他产线同时开工
    const safe = tool?.isConcurrencySafe?.(call.input) ?? false
    if (safe) {
      acc.parallel.push(call)
    } else {
      acc.serial.push(call)
    }
    return acc
  }, { parallel: [], serial: [] })
}
```

| 并发策略 | 执行方式 | 典型工具 |
|---------|---------|---------|
| parallel（并行） | `Promise.all()` 同时执行 | Read、Grep、天气查询 |
| serial（串行） | `for...of` 顺序执行 | Write、Edit、Bash（写操作） |
这个分类的粒度是单次调用级别的。同一个工具，不同参数可能有不同的并发安全性。比如一个数据库工具，读操作可以并行，写操作必须串行。`isConcurrencySafe(input)` 接收具体参数来做判断，比整个工具级别的粗粒度标记灵活得多。
### 模式三：多层压缩策略
上下文窗口是有限的。对话越长、工具调用越多，Token 消耗越大。Claude Code 的三层压缩策略可以简化为：

```typescript
// 压缩决策的简化逻辑
function chooseCompressionStrategy(context: ContextMetrics): Strategy {
  if (context.tokenUsage > 0.9 * context.maxTokens) {
    return "auto-compact"  // 快撑爆了，紧急压缩
  }
  if (context.consecutiveToolCalls > 5) {
    return "micro-compact"  // 工具调用密集，轻量整理
  }
  if (context.largestMessage > 0.15 * context.maxTokens) {
    return "snip"  // 单条消息太大，裁剪
  }
  return "none"
}
```

| 层级 | 触发条件 | 动作 | 代价 |
|------|---------|------|------|
| auto-compact | Token 占用 >90% | 整轮对话压缩为摘要 | 丢失细节 |
| micro-compact | 连续工具调用 >5 次 | 合并相邻同类消息 | 几乎无 |
| snip | 单条消息 >15% 窗口 | 裁剪消息中的大段内容 | 局部信息损失 |
你的 Agent 不需要一开始就实现三层。从 auto-compact 开始，在遇到实际瓶颈时再加层。过早优化是万恶之源，上下文压缩也不例外。
### 模式四：权限分级
工具执行前的门禁系统。Claude Code 用 plan/auto/manual 三档：
| 档位 | 行为 | 适用阶段 |
|------|------|---------|
| plan | 只规划不执行，列出将要调用的工具 | 审计、学习 |
| auto | 自动批准所有工具调用 | 信任环境、CI/CD |
| manual（默认） | 每次调用前询问用户 | 日常开发 |
实现上就是一层中间件：

```typescript
async function executeWithPermission(
  call: ToolCall,
  level: PermissionLevel
): Promise<ToolResult> {
  if (level === "plan") {
    return { planned: true, description: `将调用 ${call.name}` }
  }
  if (level === "manual") {
    const approved = await askUser(call)
    if (!approved) return { error: "用户拒绝" }
  }
  // auto 直接执行
  return executeTool(call)
}
```

权限系统的核心原则是**最小权限**：默认拒绝，显式允许。auto 模式虽然方便，但在生产环境中应该只在受控条件下启用。
### 模式五：Hook 插件化
Hook 是工具执行前后的拦截器。Claude Code 支持 PreToolUse 和 PostToolUse 两类 Hook。
| Hook 类型 | 触发时机 | 用途 |
|-----------|---------|------|
| PreToolUse | 工具执行前 | 校验、拦截、修改输入 |
| PostToolUse | 工具执行后 | 日志、审计、触发后续操作 |
| Stop | Agent 循环结束 | 清理、总结 |
| UserPromptSubmit | 用户提交消息时 | 预处理、注入上下文 |
Hook 的实现是一个简单的管道：

```typescript
async function runPreHooks(call: ToolCall, hooks: Hook[]): Promise<HookResult> {
  for (const hook of hooks) {
    const result = await hook.execute(call)
    if (result.exitCode === 2) return { blocked: true, reason: result.stderr }
    if (result.exitCode === 1) console.error(result.stderr) // 警告但不阻止
  }
  return { blocked: false }
}
// Hook 的退出码决定了行为：
// 0 → 放行
// 1 → 警告，但继续执行
// 2 → 阻止执行
```

这个模式的威力在于它的可组合性。你可以叠加多个 Hook：安全检查 + 命令审计 + 日志记录，每个 Hook 独立开发、独立测试、按需组合。
### 最小 AI Agent 核心模块
把上面的模式组合起来，一个最小的 AI Agent CLI 只需要三个模块：

```typescript
// 1. 消息循环
async function* agentLoop(messages, tools): AsyncGenerator<Event> { ... }
// 2. 工具系统
const tools = new Map<string, ToolDef>()
function registerTool(def: ToolDef) { tools.set(def.name, buildTool(def)) }
// 3. 流式处理
async function main() {
  const messages: Message[] = []
  const loop = agentLoop(messages, tools)
  for await (const event of loop) {
    render(event)  // 渲染到终端
  }
```

三个模块、不到 50 行骨架代码，就是一个可工作的 AI Agent。剩下的都是增值功能：压缩、权限、Hook、UI 美化。
### 技术栈推荐
| 组件 | 推荐选择 | 备选 | 理由 |
|------|---------|------|------|
| 运行时 | Bun | Node.js + tsx | 冷启动快、原生 TS |
| 终端 UI | Ink v4 | blessed | React 组件模型、虚拟列表 |
| 参数校验 | Zod | valibot | 生态成熟、类型推导强 |
| LLM SDK | Vercel AI SDK | @anthropic-ai/sdk | 模型无关、流式支持好 |
| 构建工具 | Bun.build | tsup | 零配置、内置 |
| 测试框架 | Vitest | Bun:test | 与 Bun 兼容、快 |
不要在技术栈选择上花太多时间。Bun + Ink + Zod + Vercel AI SDK 是经过验证的组合，能让你快速出原型。等真正遇到瓶颈时再考虑替换组件。
### 从玩具到生产的演进路径
**阶段一：命令行玩具（1-2 周）**
实现消息循环 + 1-2 个工具（文件读取 + Bash 执行）。能在终端里和模型对话、让模型执行简单命令。这个阶段的目标是验证核心循环能跑通。
**阶段二：工具生态（2-4 周）**
增加工具数量，实现并发调度，加上 basic 权限控制。让 Agent 能完成多步骤任务（比如"读代码→写测试→跑测试→修 bug"）。
**阶段三：稳定性（4-8 周）**
加入上下文压缩、错误恢复、会话持久化。让 Agent 能处理长对话和大代码库而不崩溃。
**阶段四：可扩展性（持续）**
实现 Hook 系统、MCP 兼容、插件架构。让其他人能为你的 Agent 写扩展。
### 值得关注的开源项目
| 项目 | 方向 | 学习价值 |
|------|------|---------|
| Claude Code 本身 | AI 编程助手 | 本章分析的几乎所有模式 |
| Aider | 终端 AI 编程 | 多编辑策略、多模型切换 |
| OpenHands | 自主 AI Agent | 沙箱执行、浏览器操作 |
| SWE-agent | 自动 bug 修复 | 问题分解、验证循环 |
| Vercel AI SDK | LLM 应用框架 | 流式处理、工具调用的标准抽象 |
每个项目都用了不同的方式解决相似的问题。对比它们的方案，你会对设计决策有更深的直觉。
> **核心建议**
> 从最小的可工作版本开始，而不是从完美的架构开始。50 行骨架代码比 5000 行设计文档更能验证你的想法。先用 AsyncGenerator 搭起消息循环，加一两个工具跑通端到端流程，再逐步加压缩、权限、Hook。每一步都能跑、每一步都能测。AI Agent 的复杂度来自功能的叠加，而不是架构的精巧。
### 展望
AI Agent CLI 正在从一个新奇玩具变成日常开发工具。Claude Code 展示了一种可能的形态：终端原生的、工具驱动的、流式交互的 AI 编程助手。但它不会是最终形态。
三个方向值得持续关注：
**多模态输入**——现在的 Agent CLI 主要处理文本。但代码审查需要看截图，UI 开发需要看设计稿，调试需要看错误截图。支持图像输入的终端 Agent 会在这些场景中打开新的可能性。
**多 Agent 协作**——Claude Code 已经有了子 Agent（通过 Task 工具启动），但协作模式还比较初级。未来的 Agent 团队可能像真正的开发团队一样分工：一个 Agent 写代码、一个写测试、一个做审查，各有所长、互相校验。
**从 CLI 到平台**——Claude Code 的插件系统、MCP 协议、Hook 机制都在把一个 CLI 工具变成一个平台。当足够多的工具、Agent、工作流沉淀在平台上，价值会呈网络效应增长。
你手里的这份源码分析，与其说是对 Claude Code 的解剖，不如说是对 AI Agent 这个品类的蓝图。工厂的每条产线、每个调度决策、每层压缩策略，都是你在构建自己的智能系统时可以参考的模版。现在，该你动手了。