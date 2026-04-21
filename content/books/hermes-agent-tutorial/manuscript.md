---
title: "Hermes Agent 实用教程 - 全文"
date: 2026-04-15
draft: false
description: "驯养一只会自己变聪明的 AI Agent"
type: books
---

## 本书适合谁读
本书适合以下几类读者。如果你对"一个会自己变聪明的 AI Agent"感兴趣，你就是本书的目标读者。
### 想让 AI 持续帮你干活的开发者
你可能每天都在和 ChatGPT 或 Claude 聊天，但每次对话都是"从零开始"——它不记得昨天帮你做了什么，不知道你的编码偏好，更不会自己学会新技能。你想让 AI 从"对话玩具"变成一个 7x24 小时在线、会自己变聪明的助手。本书将带你理解并搭建一个具备三层记忆和自改进能力的 Agent。
### 想构建 AI Agent 系统的工程师
你可能正在设计自己的 Agent 架构，需要解决记忆持久化、技能提炼、工具集成、多平台部署这些核心问题。Hermes Agent 是一个参考实现——它的自改进循环、Skill 系统、MCP（Model Context Protocol，一种 AI 调用外部工具的协议）工具链集成都是可以直接借鉴的设计模式。
### 对 AI 学习机制好奇的程序员
Hermes 的核心卖点是"用得越多，它越懂你"。你想知道这背后的技术实现：热记忆和冷召回怎么配合？Agent 怎么自己决定该记住什么？Skill 是怎么从经验中自动提炼出来的？本书会一层一层拆开这些机制。
### 阅读本书之前
本书假设你有至少一年的编程经验，熟悉 Python 或 JavaScript，用过命令行工具，对 LLM 和 API 调用有基本了解。
---
# Part 1: 概念
## §01 你需要的不是更聪明的 AI，是一个会记住你的 AI
You Don't Need a Smarter AI — You Need One That Remembers
又来一个 AI Agent？
你的朋友圈大概率被类似的东西刷过屏。2024 年 Cursor 掀起了 AI 编程的热潮，2025 年 Claude Code 成了很多开发者的日常工具，MCP 协议让 AI 能连接外部服务。那段时间你的信息流里大概率全是"AI Agent 将取代程序员"的讨论。热潮还没散去，又有一个新东西冒出来了。
2026 年 2 月，Nous Research 发布了 Hermes Agent。一个月内 GitHub Star 破万，社区贡献了 643 个 Skill。
你的第一反应可能是：Claude Code 我还没搞明白，又来？
且慢。这一次不一样。不是"又来一个"的问题，是"之前那些都缺了一块"的问题。
### 你真正缺的不是更聪明的 AI
回想一下你用 AI 做事的典型场景。
你打开一个新会话，花了 20 分钟告诉 AI 你的项目背景、代码风格偏好、技术栈选择。它开始帮你干活了。效果不错。你关掉窗口，觉得挺满意。
### 从零开始
第二天，你打开一个新会话。一切从零开始。你的偏好？忘了。昨天踩过的坑？没了。你那个"用 httpx 不用 requests"的习惯？它完全不知道。
这就是问题所在。
不是 AI 不够聪明。是它记不住你。
这个隐形成本比你想象的大。每次重新建立上下文的时间、反复纠正同一偏好的精力、永远无法积累的信任感 — 这些加起来，才是 AI 工具真正卡住你的地方。
### Hermes Agent：一个会自己变聪明的 Agent
Hermes Agent 解决的就是这个问题。
一句话版本：它是一个开源的、会自己变聪明的 AI Agent。用得越多，它越懂你。
| 维度 | 传统 AI 助手 | Hermes Agent |
|------|------------|-------------|
| 记忆 | 关掉窗口就没了 | 三层记忆，跨会话持久化 |
| 学习 | 不会从经验中学习 | 自动从成功路径中提炼 Skill |
| 用户理解 | 每次重新猜测你的意图 | 持续构建你的偏好画像 |
| 平台 | 绑定在某个界面里 | Telegram、Discord、Slack、终端，随便切换 |
| 模型 | 绑定某个 LLM 提供商 | 200+ 模型随便选，本地 Ollama 也行 |
这不是营销话术。背后是一个可以验证的闭环机制。
### 驯养，而不是使用
在展开技术细节之前，我想用一个比喻贯穿全书。
Hermes Agent 更像是在**驯养一只工作犬**，而不是在使用一个工具。
| 现实世界 | Hermes Agent |
|----------|-------------|
| 幼犬到家 | 首次安装部署 |
| 基本服从训练 | 配置和基础工具 |
| 学会新指令 | Skill 创建 |
| 反复训练纠正 | 自改进循环 |
| 认主人 | 用户建模 |
| 记住路线 | 记忆系统 |
| 24 小时看家 | Cron（定时任务调度器）定时 + Gateway（消息网关，负责平台接入） |
| 多个犬舍都能干活 | 多平台部署 |
| 派出去单独执行任务 | Subagent（子 Agent）委派 |
为什么选这个比喻？因为几乎所有养过狗的人都理解一个事实：**狗不是生来就懂你的，但相处越久，默契越深。** 这正是 Hermes Agent 和其他 AI 工具的根本区别。
其他工具是买一个成品机器狗 — 按按钮就动，关机就停。Hermes 是领养一只幼犬 — 你花时间训练它，它花时间了解你，最终你们之间的配合远超任何预设程序。
但比喻就是比喻，不能替代技术细节。从下一章开始，我们一层一层拆开 Hermes 的内部机制。现在你只需要记住一件事：**它是一个会记住你、会学习、会变聪明的 Agent，开源免费，跑在你的机器上。**
### 30 秒版：它是什么
如果有人问你 Hermes Agent 是什么，你可以这样回答：
> Hermes Agent 是 Nous Research 开源的一个 AI Agent 框架。它的核心卖点是"自改进" — 用得越多越懂你。它能记住你的偏好，从成功经验中自动提炼可复用的 Skill，跨会话、跨平台持续学习。支持 200+ 种 LLM 模型，可以部署在 5 美元的 VPS 上，MIT 协议，完全免费。
> **核心建议**
>
> 如果你对 AI 工具的期望还停留在"帮我写代码"这个层面，Hermes 可能暂时不是你的最优选 — Cursor 或 Claude Code 的编程体验更直接。但如果你想要一个**长期搭档** — 一个会用得越久越懂你的 AI 助手，而不仅仅是按次计费的代码生成器 — 那就是时候认真看看 Hermes 了。
满足以下任意一条，就接着看：
- 你用过 ChatGPT 或 Claude，但觉得"每次重新开始"很烦
- 你对 AI Agent 有耳闻，想知道它被产品化之后长什么样
- 你想在 Telegram 或 Discord 上有一个随时可用的 AI 助手
- 你好奇"自改进 Agent"到底是什么机制
下一章，我们把 Hermes 和其他 AI 工具放到一起，看看它们各自的定位和适用场景。
## §02 Hermes Agent vs 其他 Agent：四种"狗"的对比
Hermes vs the Rest: Four Breeds Compared
选 AI 工具跟选狗一样，没有"最好的品种"，只有"最适合你的品种"。
你可能在好几个工具之间纠结：Hermes Agent、OpenClaw、Claude Code、Cursor。每个都有自己的粉丝群，每个都说自己最好。网上对比文章一堆，但大多是功能罗列，看完还是不知道选哪个。
这张表和后面的分析，帮你 5 分钟内做决定。
### 先搞清楚它们不是一类东西
这是最常见的误解。
把这四个工具放在一起比，就像把牧羊犬、遥控车、电动螺丝刀和瑞士军刀放在一起比"哪个更好"。它们有重叠的场景，但根本定位不同。
| 工具 | 定位 | 核心隐喻 |
|------|------|----------|
| **Hermes Agent** | 自主型 Agent 框架，会自己变聪明 | 驯养工作犬 |
| **OpenClaw** | 控制面网关，人工管理行为 | 遥控机器狗 |
| **Claude Code** | 编程 Copilot，绑定 Anthropic 模型 | 高级电动工具 |
| **Cursor** | IDE 集成编程助手 | 智能螺丝刀 |
定位不同，对比才有意义。
### 核心维度对比
| 维度 | Hermes Agent | OpenClaw | Claude Code | Cursor |
|------|-------------|----------|-------------|--------|
| 记忆 | 三层自改进记忆 | 文件式，人工维护为主 | 会话内，无跨会话学习 | 项目级，无自改进 |
| 自改进 | 核心功能 — 自动提炼 Skill | 不内置，Skill 需人工写 | 不内置 | 不内置 |
| 模型 | 模型无关，200+ 可选 | 模型无关 | 仅 Anthropic 模型 | 多提供商 |
| 平台 | CLI + 15 个通讯平台 | CLI + 通讯平台 | CLI | IDE (VS Code 系) |
| 部署 | 本地/Docker/SSH/Serverless | 本地/Docker | 本地 CLI | 本地 IDE |
| 定时任务 | 内置 Cron | 有限支持 | 不支持 | 不支持 |
| 生态 | 643+ 社区 Skill | 44000+ 社区 Skill | MCP 生态 | 插件生态 |
| 开源 | MIT | 开源 | 闭源 | 闭源（有免费层） |
| 安全 | 命令审批 + 容器隔离 + SSRF 防护 | 可配置 | Anthropic 安全护栏 | IDE 级控制 |
差距最大的两个维度是**自改进能力**和**部署灵活性**。这直接决定了工具的上限。
### 什么时候选什么
不用纠结，按场景选：
| 你的需求 | 选什么 | 理由 |
|----------|--------|------|
| 每天写代码，要 AI 辅助编辑 | **Cursor** | IDE 集成最深的编程体验 |
| 处理代码仓库级任务，不在乎模型锁定 | **Claude Code** | Anthropic 模型能力强，CLI 体验好 |
| 想精确控制 Agent 行为，手动写每条规则 | **OpenClaw** | 人工编写 Skill，控制粒度最细 |
| 要一个 7x24 小时运行、会自己学习的助手 | **Hermes Agent** | 自改进循环 + 持久记忆 + 定时任务 |
| 想在 Telegram 上有个 AI 助手 | **Hermes Agent** 或 OpenClaw | 两者都支持通讯平台 |
| 想用本地模型（Ollama） | **Hermes Agent** | 原生支持，一行配置 |
> **核心建议**
>
> 如果你只是写代码，Cursor 或 Claude Code 就够用了。如果你想要一个 7x24 小时会自己变聪明的后台 Agent — 能定时帮你干活、能在 Telegram 上随时找、会从错误中学习 — 那就是 Hermes Agent 的主场。OpenClaw 适合想要精确手动控制的人，但代价是你得自己维护每条规则。
### 一个常见误解
"Hermes Agent 是不是只能跑 Hermes 模型？"
不是。Hermes Agent 和 Hermes 模型是两个独立项目。Hermes 模型（Hermes 3、Hermes 4）是 Nous Research 开发的开源 LLM，Hermes Agent 是一个 Agent 框架。Agent 支持任何 OpenAI 兼容的模型 — OpenRouter 上 200+ 种、本地 Ollama、甚至 Anthropic 的 Claude。名字一样只是因为同一个团队做的。
概念和定位都清楚了。接下来的章节，我们从记忆系统开始，一层一层拆开 Hermes Agent 的核心机制。
---
# Part 2: 核心机制
## §03 三层记忆：热记忆、冷召回、技能库
Memory Architecture: Hot, Cold, and Procedural
你的狗记得你的气味、记得回家的路、记得你每天几点出门。这不是一种记忆，是三种完全不同的记忆在工作。
Hermes Agent 也是如此。它的"记性"不是一块东西，而是三层架构，每层的存储方式、访问速度、容量上限都不一样。理解这三层，你就理解了 Hermes 和其他 Agent 最根本的区别。
### 第一层：热记忆 — 随身笔记本
热记忆是 Agent 每次醒来第一个看到的东西。
它由两个文件组成，存在 `~/.hermes/memories/` 目录下：
| 文件 | 内容 | 容量 |
|------|------|------|
| `MEMORY.md` | 环境细节、项目约定、踩过的坑、学到的经验 | ~2,200 字符（~800 Token） |
| `USER.md` | 你的偏好、沟通风格、身份信息 | ~1,375 字符（~500 Token） |
总预算约 1,300 Token。很紧，但这是有意为之的。
为什么这么小？因为这两个文件在每次会话开始时被**冻结加载到系统提示词**中。如果太大，LLM 的前缀缓存就不稳定，每次对话的启动成本会飙升。所以 Agent 必须自己判断什么值得记住、什么不值得 — 就像你只会在笔记本上写最重要的东西，不会把每天说的话全抄下来。
Agent 通过 `memory` 工具管理这些文件，有三个操作：`add`（添加）、`replace`（替换）、`remove`（删除）。还有一个**周期性 Nudge** 机制 — 每隔一定轮数，系统会提醒 Agent 回顾最近的对话，把值得持久化的内容存下来。
关键细节：在会话中间修改的记忆**不会立即出现在当前会话里**。修改会立刻写入磁盘，但系统提示词中的快照是会话开始时的版本。这是为了缓存稳定性做的取舍。
### 第二层：冷召回 — 地下室图书馆
热记忆太小，装不下所有东西。但你过去的所有对话都在，存在一个 SQLite（一个轻量级嵌入式数据库）数据库里。
这个数据库叫 `state.db`，存在 `~/.hermes/` 目录下，使用 **FTS5（SQLite 的全文搜索扩展）** 索引。当 Agent 需要回忆过去的某个对话时，它通过 `session_search` 工具搜索这个数据库。
搜索结果不是直接塞进上下文的。Agent 会先用 LLM 对搜索结果做一次**摘要**，只把和当前任务相关的内容注入上下文。这个设计很聪明 — 你的地下室图书馆可能有几万条记录，但每次只取回你正在看的那个话题相关的几段话。
两种记忆的关键区别：
| 维度 | 热记忆 | 冷召回 |
|------|--------|--------|
| 存储位置 | MEMORY.md / USER.md 文件 | SQLite 数据库 |
| 总容量 | ~1,300 Token | 无硬上限 |
| 加载方式 | 每次会话自动全量加载 | Agent 主动搜索时才加载 |
| 更新频率 | 周期性 Nudge 触发 | 每次会话自动归档 |
| 在上下文中 | 始终存在 | 按需摘要注入 |
一个比喻：热记忆是你口袋里的笔记本，冷召回是家里的书柜。口袋里的笔记本容量有限但随时可读，书柜能放很多但每次要去翻。

![三层记忆架构](images/memory-architecture.png)
### 第三层：技能库 — 训练手册
前两层记住的是"信息" — 偏好、经验、对话历史。第三层记住的是"能力" — 怎么做某件事。
Skill 是 Hermes Agent 的核心创新。它本质上是一个 Markdown 文件，记录了一个可复用的任务流程。比如"代码审查的步骤"、"部署到 K8s 的检查清单"、"写周报的格式要求"。
Skill 文件存在 `~/.hermes/skills/` 目录下，遵循 agentskills.io（一个开放 Skill 标准的社区平台）开放标准。加载方式很特别 — **渐进式披露**：
| 阶段 | 加载内容 | Token 成本 |
|------|----------|-----------|
| 启动时 | 仅 Skill 名称 + 摘要 | 每个 Skill ~100 Token |
| 使用时 | 完整 Skill 内容 | 按需加载 |
| 深度使用 | 引用文件、脚本 | 按需加载 |
这意味着即使你有 200 个 Skill，启动时的上下文成本和 40 个差不多。Agent 根据当前任务判断需要哪个 Skill，再加载完整内容。
### 上下文压缩：快满了怎么办
对话进行到一定长度，上下文窗口会快满。Hermes 的处理方式不是粗暴截断，而是**先存再压**：
1. **内存刷新**：触发一次专门的模型调用，只有 `memory` 工具可用，让 Agent 把重要内容存到热记忆
2. **压缩**：用辅助模型（默认 Gemini Flash）对中间轮次做摘要
3. **继续**：Agent 继续对话，但历史被压缩了
这个"先存再压"的机制是关键 — 很多 Agent 框架的压缩会直接丢信息，Hermes 先给 Agent 一个存盘的机会。
### 可选的第四层：外部记忆提供商
前三层是内置的，开箱即用。如果你需要更强的记忆能力，Hermes 还支持 7 个外部记忆提供商：
| 提供商 | 特色 | 适用场景 |
|--------|------|----------|
| **Honcho（一个外部记忆服务提供商）** | 辩证用户建模，12 层身份追踪 | 需要深度理解用户 |
| **Hindsight** | 知识图谱，LongMemEval 91.4% | 需要精确事实回忆 |
| **Mem0** | 云端提取，有免费层 | 不想本地维护 |
| **Holographic** | 零依赖，本地 SQLite + HRR（全息减少表示，一种向量编码方法） | 极简主义 |
| **OpenViking** | 三级分层加载 | 大规模 Skill 库 |
同时只能激活一个外部提供商。对大多数人来说，内置的三层已经够用。
> **核心建议**
>
> 如果你刚开始用，别折腾外部记忆提供商。内置的三层（热记忆 + 冷召回 + 技能库）覆盖了 90% 的场景。等你发现 Agent 的记忆不够用的时候，再考虑加 Honcho 或 Hindsight。
三层记忆各司其职：热记忆保证关键信息始终在上下文里，冷召回让你不丢失历史，技能库把经验变成可复用的能力。
下一章看自改进循环 — Agent 怎么决定记什么、怎么从经验中提炼 Skill、怎么在使用中持续改进。
## §04 自改进循环：用得越多，它越懂你
The Self-Improvement Loop
Agent 最让人意外的不是它能做什么，而是它会变。用得越多，它越好用。
假设你第一次让 Hermes 帮你审查一段代码。你说：帮我看看这个 PR 有没有明显问题。
它会审查，但可能遗漏一些你关注的维度 — 比如你团队特别在意错误处理模式，或者你对 SQL 注入特别敏感。挺正常的，毕竟它还不认识你。
### 蜕变
到了第十次，情况完全不同。它知道你团队用自定义错误类而不是原生 Exception，知道你在 PR 审查中关注性能回归，知道你喜欢在 catch 块里加上下文日志。
没有人教它这些。它是自己学会的。
这就是自改进循环在做的事。
### 四个环节，一个闭环
自改进循环有四个环节。单看都不复杂，但串起来形成了一个持续改进的飞轮：
**周期性 Nudge → Skill 创建 → Skill 自改进 → 会话搜索反馈**
### 环节 1：周期性 Nudge
每隔一定轮数（默认 10 轮），系统会给 Agent 一个内部提示：回头看一眼最近的对话，有没有什么值得记住的？
这个 Nudge 不需要你做任何事。Agent 自己判断什么值得存到热记忆、什么只留在冷召回里、什么值得提炼成 Skill。
在 Gateway 模式下（比如你在 Telegram 上和 Agent 聊天），Agent 在空闲超时前会主动做一次内存刷新 — 把这个会话中学到的东西存好再"睡觉"。
### 环节 2：Skill 创建
不是每次任务都会创建 Skill。Agent 会在以下情况评估是否值得提炼：
| 触发条件 | 说明 |
|----------|------|
| 5 次以上工具调用 | 说明这个任务比较复杂，有流程价值 |
| 从错误中恢复 | 踩坑后的解决路径值得记录 |
| 用户做了纠正 | 你告诉它"不对，应该这样做" — 这是最珍贵的学习信号 |
| 非显而易见的成功路径 | 找到了一个巧妙解法 |
如果条件满足，Agent 调用 `skill_manage` 工具的 `create` 操作，生成一个 Skill 文件到 `~/.hermes/skills/` 目录。
### 环节 3：Skill 自改进
Skill 创建后不是冻结的。Agent 在后续使用中如果发现更好的做法，会更新它。
这里有个关键设计：Agent 优先使用 `patch`（局部替换）而不是 `edit`（全文重写）。为什么？
| 操作 | 行为 | 风险 |
|------|------|------|
| `patch` | 只替换目标字符串 | 不影响其他内容 |
| `edit` | 重写整个文件 | 可能丢失已经验证有效的部分 |
就像你不会因为一个步骤需要修改就把整本训练手册重抄一遍 — 你只会划掉那一步，在旁边写上新的。Hermes 也是这个思路。
### 环节 4：会话搜索反馈
每次会话结束后，完整对话被存入 SQLite FTS5 数据库。下次遇到类似问题时，Agent 会搜索过去的会话，找到相关经验，用 LLM 摘要后注入当前上下文。
这构成了一个反馈回路：**过去的经验 → 搜索召回 → 指导当前决策 → 新的经验再存回去**。
### 和手动方式的对比
| 维度 | 手动写规则 | 自改进循环 |
|------|-----------|-----------|
| 规则来源 | 你观察后手写 | Agent 从反馈中自动提炼 |
| 触发改进 | 你记得才加 | 每次自动评估 |
| 维护成本 | 规则越多越难维护 | Skill 自动精简，patch 不重写 |
| 跨项目迁移 | 需要手动复制 | Skill 全局共享 |
| 遗漏风险 | 你想不到的就没写 | Agent 从错误中自动发现 |
看左列和右列的对比。左边全是手动操作，右边是开箱即用。

![自改进循环](images/self-improvement-loop.png)
> **核心建议**
>
> 自改进循环是 Hermes 和其他 Agent 框架最根本的区别。但别神化它 — 它不是万能的。它依赖足够的交互次数来积累经验。前几次对话你和 Agent 还在磨合期，给它时间，也主动给它纠正信号（"不对，这样做"），它学得最快。
自改进循环产生的 Skill 存在哪里、长什么样、怎么管理？下一章拆开 Skill 系统。
## §05 Skill 系统：从经验中提炼可复用的能力
The Skill System: Distilling Reusable Capabilities
训练一只狗学会"坐下"之后，你不希望明天它又忘了。你希望这个能力被固化下来，每次用到都能自动执行。
Skill 就是 Hermes Agent 的"坐下"、"握手"、"接飞盘" — 被固化的、可复用的能力单元。
### Skill 是什么
Skill 本质上是一个目录，里面有一个必须的 `SKILL.md` 文件和可选的辅助文件：

```text
my-skill/
├── SKILL.md          # 必需：元数据 + 指令
├── scripts/          # 可选：可执行脚本
├── references/       # 可选：参考文档
└── assets/           # 可选：模板、资源
```
核心是 `SKILL.md`，它有两部分：
**YAML 前置信息：**

```yaml
---
name: code-reviewer
description: 审查代码变更，关注安全性、性能和可维护性
version: 1.0.0
metadata:
hermes:
tags: [code-review, security]
category: development
requires_toolsets: [terminal, file]
---
```
**Markdown 正文：**

```markdown
# Code Reviewer
## 审查流程
1. 获取变更文件列表
2. 检查安全漏洞（SQL 注入、XSS、硬编码密钥）
3. 检查性能问题（N+1 查询、不必要的全量加载）
4. 按严重程度分级输出，给出修复建议
```
就这么简单。一个 Markdown 文件，不需要写代码，不需要懂 Python。
### Skill 的三种来源
| 来源 | 怎么创建 | 谁写的 |
|------|----------|--------|
| **自动创建** | Agent 完成复杂任务后自动提炼 | Agent 自己 |
| **手动编写** | 你在 `~/.hermes/skills/` 下创建目录和 SKILL.md | 你自己 |
| **社区安装** | `hermes skills search <关键词>` + `hermes skills install <name>` | 社区贡献 |
三种来源的 Skill 在 Agent 看来完全一样 — 它不区分是谁写的，只看内容质量。
### 渐进式披露：200 个 Skill 不会撑爆上下文
如果你有 200 个 Skill，启动时会不会把上下文窗口占满？
不会。Hermes 用了**渐进式披露**策略：

```text
启动时：只加载每个 Skill 的名称 + 描述 → 200 × ~100 token = ~20,000 token
使用时：按需加载匹配到的 Skill 完整内容
深度使用：按需加载 references、scripts 等辅助文件
```
这意味着 Agent 能"知道"自己有哪些能力（名称和描述），但只在需要时才"读"具体怎么做。就像你知道工具箱里有螺丝刀、扳手、锤子，但你不会在每次修东西时把所有工具都拿出来摆在桌上。
### Skills Hub：643 个社区 Skill
Hermes 有一个集中的 Skill 分发平台，叫 Skills Hub：

```bash
# 搜索 Skill
hermes skills search "code review"
# 查看详情
hermes skills info code-reviewer
# 安装
hermes skills install code-reviewer
# 列出已安装
hermes skills list
```
截至 2026 年 4 月，Skills Hub 有 643 个 Skill，分布如下：
| 注册表 | 数量 | 说明 |
|--------|------|------|
| 内置 | 77 | 安装时自带 |
| 可选 | 45 | 官方维护但需手动安装 |
| 社区 | 521 | 社区贡献，质量参差 |
选社区 Skill 的时候注意看 Star 数和最后更新日期。热门的 Skill 通常维护得更好。
### 一个 Skill 的完整生命周期
以"代码审查"这个 Skill 为例：
1. **你第一次让 Agent 审查代码** — 没有任何 Skill 指导，Agent 凭通用能力做
2. **你纠正了几次** — "你应该检查 SQL 注入"，"漏了错误处理"
3. **Agent 创建了 Skill** — 把学到的审查流程写进了 `~/.hermes/skills/code-reviewer/SKILL.md`
4. **下次审查代码** — Agent 自动加载这个 Skill，按流程走
5. **发现新的审查维度** — 比如"检查环境变量泄露"，Agent 用 `patch` 更新 Skill
6. **你把 Skill 分享到 Skills Hub** — 其他人也能用
这就是从经验到能力、从个人到社区的完整路径。
### 手动创建 Skill 的最佳实践
虽然 Agent 会自动创建 Skill，但有些 Skill 你可能想自己写 — 比如团队规范、部署流程这类你比 Agent 更清楚的东西。
几个要点：
| 要点 | 做法 | 原因 |
|------|------|------|
| 描述要精准 | 描述决定 Agent 什么时候激活这个 Skill | 描述模糊 = 错误激活 |
| 步骤要具体 | 不要写"审查代码"，写"检查 SQL 拼接、XSS、硬编码密钥" | 具体步骤 = 可执行 |
| 控制长度 | SKILL.md 不超过 500 行，细节放 references/ | 渐进式披露的效率 |
| 说明前置条件 | 用 `requires_toolsets` 声明依赖 | 避免在没有终端工具时执行 |
| 不要写代码逻辑 | Skill 是指令，不是程序 | Agent 会根据指令选择工具 |
> **核心建议**
>
> 手动写 Skill 和让 Agent 自动创建，不是二选一。团队规范、部署流程这类"你知道但 Agent 不知道"的东西，手动写更靠谱。而"Agent 踩坑后的经验"这类"它知道但你不知道"的东西，让它自己提炼更好。两者混合使用效果最好。
Skill 系统给了 Agent "能力"。但 Agent 还需要"工具"来执行这些能力 — 下一章看工具链和 MCP。
## §06 工具链与 MCP：给它装上牙齿和爪子
Tools & MCP: Giving Your Agent Teeth and Claws
一只工作犬光有训练不够，还得有合适的装备 — 嗅探犬需要鼻子护具，牧羊犬需要活动空间，救援犬需要安全绳。
Hermes Agent 的"装备"就是它的工具系统。47 个内置工具，加上 MCP 协议的无限扩展能力。理解工具系统，你就知道 Agent 能做什么、不能做什么、怎么扩展它的能力边界。
### 47 个工具，20 个工具集
所有工具都注册在 `tools/registry.py` 中，按功能分成 20+ 个工具集（Toolset）：
| 工具集 | 工具 | 做什么 |
|--------|------|--------|
| `web` | web_search, web_extract | 搜索网页、提取页面内容（4 个后端可选） |
| `terminal` | terminal, process | 执行命令、管理进程 |
| `file` | read_file, write_file, patch, search_files | 文件读写、搜索、补丁 |
| `browser` | 11 个浏览器操作工具 | 导航、点击、输入、截图、滚动等 |
| `vision` | vision_analyze | 分析图片内容 |
| `image_gen` | image_generate | 生成图片 |
| `tts` | text_to_speech | 文字转语音 |
| `memory` | memory | 管理热记忆 |
| `session_search` | session_search | 搜索历史会话 |
| `skills` | 相关工具 | 搜索、加载 Skill |
| `todo` | todo | 任务管理 |
| `clarify` | clarify | 主动向你提问澄清 |
| `code_execution` | execute_code | 在沙箱中执行代码 |
| `delegation` | delegate_task | 委派Subagent |
| `cronjob` | cronjob | 管理定时任务 |
| `send_message` | send_message | 跨平台发送消息 |
| `homeassistant` | 4 个 HA 工具 | 控制 Home Assistant 设备 |
| `rl_training` | 10 个 RL 工具 | 强化学习训练（研究用） |
Home Assistant 工具集特别有意思 — 只要你的环境变量里设了 `HASS_TOKEN`，它就会自动激活。Agent 直接就能控制你的智能家居。

![工具系统架构](images/tool-system-architecture.png)
### Toolset 机制：按需开关
不是所有工具都应该在所有场景下可用。比如你在 Telegram 上聊天时，可能不想让 Agent 有终端执行权限。
Toolset 就是为这个设计的 — 工具分组，按平台开关：

```bash
# CLI 启动时指定工具集
hermes chat --toolsets "web,terminal,file"
# 在 config.yaml 中按平台配置
platforms:
telegram:
toolsets: ["web", "file", "memory", "session_search"]
cli:
toolsets: ["web", "terminal", "file", "browser", "vision"]
```
这就像给工作犬分场合配装备 — 在家里不用戴牵引绳，去公共场所必须戴。
### MCP：无限扩展能力
内置工具覆盖了常见场景，但如果你需要连接 GitHub、操作数据库、调用内部 API 呢？
这就是 MCP（Model Context Protocol）的用处。MCP 是一个标准协议，让 Agent 能连接外部工具服务器。Hermes 的 MCP 实现约 2,200 行代码，支持 stdio 和 SSE 两种传输方式。
**配置一个 MCP 服务器：**

```yaml
# ~/.hermes/config.yaml
mcp_servers:
github:
command: npx
args: ["-y", "@modelcontextprotocol/server-github"]
env:
GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_your_token_here"
```
保存后重启 Agent，它就自动获得了 GitHub 操作能力 — 创建 Issue、管理 PR、搜索代码，全部通过 MCP。
MCP 工具的发现是自动的：启动时 `discover_mcp_tools()` 扫描所有配置的 MCP 服务器，把它们的工具注册到同一个工具注册表中。Agent 看到的 MCP 工具和内置工具没有区别。
### 三种扩展路径
除了 MCP，还有两种方式给 Agent 加能力：
| 方式 | 怎么做 | 适合场景 |
|------|--------|----------|
| **MCP 服务器** | 在 config.yaml 中配置 | 连接外部服务（GitHub、数据库、内部 API） |
| **插件** | 放到 `~/.hermes/plugins/` | 在 Agent 行为层面做拦截和修改 |
| **Shell 工具** | 写 bash 脚本作为工具定义 | 简单的命令行工具封装 |
插件有 4 个钩子：`pre_llm_call`（调用 LLM 前）、`post_llm_call`（调用后）、`on_session_start`（会话开始）、`on_session_end`（会话结束）。适合做日志记录、内容过滤、自定义路由等。
### 工具的同步-异步桥接
一个技术细节，不影响使用但很有意思：Hermes 的主线程是同步的（TUI 用的是 Textual（一个 Python 终端 UI 框架）），但很多工具（Web 请求、浏览器操作）是异步的。怎么桥接？

```text
主线程 → 持久事件循环 (_get_tool_loop) → 异步工具执行
Worker 线程 → 线程本地事件循环 (_get_worker_loop) → 异步工具执行
异步上下文 → 临时线程 + asyncio.run() → 异步工具执行
```
三种场景三种桥接方式，避免了 "Event loop is closed" 这种常见的 asyncio 陷阱。
> **核心建议**
>
> 刚开始用的时候，别急着配 MCP。先用内置工具集跑通流程。等你发现 Agent 需要"连 XX 但没有对应工具"的时候，再去配 MCP 服务器 — 这时候你很清楚自己需要什么。常见的第一批 MCP 服务器：GitHub（管 PR/Issue）、数据库（查询数据）、内部 API（公司工具集成）。
工具系统是 Agent 的"爪牙"，记忆系统是"大脑"，Skill 系统是"训练手册"。三者组合起来，就是一个能干活的 Agent。但这些都还是概念。接下来的章节，我们动手搭建。
从概念到原理的旅程结束了。接下来的章节，我们从安装 Hermes Agent 开始，一步步把它变成你自己的 24 小时 AI 助手。
---
# Part 3: 动手搭建
## §07 5 分钟把"幼犬"接回家
5 Minutes to Bring Your Puppy Home
领养一只幼犬，最重要的是什么？把它安全地带回家。
Hermes Agent 的安装是我见过最简化的 Agent 框架安装流程之一。一行命令，全自动。但理解它在做什么，出了问题才知道怎么排查。
### 前置条件
你只需要一样东西：**Git**。
其他所有东西 — Python 3.11、Node.js v22、uv、ripgrep、ffmpeg — 安装脚本都会自动帮你装好。不需要 sudo 权限。
支持的平台：
| 平台 | 支持 | 备注 |
|------|------|------|
| Linux | 原生支持 | 最佳体验 |
| macOS | 原生支持 | Intel 和 Apple Silicon 都行 |
| WSL2 | 原生支持 | 推荐 Ubuntu 发行版 |
| Termux/Android | 支持 | 技术上可行，体验有限 |
| Windows 原生 | 不支持 | 请用 WSL2 |
### 一行命令安装

```bash
curl -fsSL \
  https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh \
  | bash
```
这行命令做了什么？拆开看：
| 步骤 | 做什么 | 为什么 |
|------|--------|--------|
| 1 | 安装 `uv`（Astral 的 Python 包管理器） | 比 pip 快 10-100 倍 |
| 2 | 通过 uv 下载 Python 3.11 | 不影响系统 Python |
| 3 | 安装 Node.js v22 | 浏览器自动化和 WhatsApp 桥需要 |
| 4 | 安装 ripgrep、ffmpeg | 文件搜索和语音转写需要 |
| 5 | 克隆 Git 仓库（含子模块） | 获取源码 |
| 6 | 创建虚拟环境 + 安装依赖 | 隔离环境 |
| 7 | 创建 `~/.hermes/` 目录结构 | 配置、记忆、Skill 的家 |
| 8 | 符号链接 CLI 到 `~/.local/bin/hermes` | 全局可用 |
| 9 | 运行 LLM 配置向导 | 选模型、填 API Key |
整个过程大约 2-5 分钟，取决于网络速度。
### 配置 LLM 提供商
安装完成后最重要的一步：选择 LLM 提供商。

```bash
hermes model
```
这会启动一个交互式向导，让你选择：
| 提供商 | 特点 | 成本 |
|--------|------|------|
| **OpenRouter** | 200+ 模型可选，推荐新手 | 按 Token 计费 |
| **Anthropic** | Claude 系列模型，能力强 | 按 Token 计费 |
| **OpenAI** | GPT 系列 | 按 Token 计费 |
| **Ollama** | 本地运行，完全免费 | 硬件成本 |
| **Nous Portal** | Nous 自己的推理服务 | 有免费层 |
API Key 存在 `~/.hermes/.env` 文件中，不会被 Git 追踪。
### 验证安装

```bash
hermes doctor
```
这个命令会检查所有依赖是否就绪、API Key 是否有效、工具是否可用。如果一切正常，你会看到绿色的 ✅。如果有问题，它会告诉你具体缺什么。
### 常见问题排查
| 问题 | 原因 | 解决 |
|------|------|------|
| `hermes: command not found` | `~/.local/bin` 不在 PATH 中 | `source ~/.bashrc` 或 `source ~/.zshrc` |
| Python 版本不对 | 系统 Python 不是 3.11 | 安装脚本会自动用 uv 管理，检查虚拟环境是否激活 |
| API Key 无效 | 复制时多了空格或换行 | 重新运行 `hermes model` |
| 网络超时 | GitHub 或 PyPI 访问慢 | 设置代理：`export HTTPS_PROXY=http://127.0.0.1:7890` |
| Node.js 相关报错 | 浏览器自动化模块装不上 | 不影响核心功能，`hermes chat --toolsets "web,terminal,file"` 跳过浏览器工具 |
### 手动安装（可选）
如果你不想用一键脚本，或者需要在特殊环境中安装：

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# 克隆仓库
git clone --recurse-submodules \
  https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
# 创建虚拟环境并安装依赖
uv venv venv --python 3.11
export VIRTUAL_ENV="$(pwd)/venv"
uv pip install -e ".[all]"
# 创建目录结构
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills,pairing,hooks}
# 配置
cp cli-config.yaml.example ~/.hermes/config.yaml
touch ~/.hermes/.env
# 链接 CLI
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes
# 选择模型
hermes model
```
> **核心建议**
>
> 新手直接用一键安装脚本。手动安装更适合需要定制环境的高级用户（比如在 Docker 里、CI/CD 中、或 Nix 环境下）。安装完一定跑 `hermes doctor`，确认没问题再继续。
安装好了。下一章，我们和 Agent 进行第一次对话。
## §08 第一次对话：从混沌到默契
First Conversation: From Chaos to Chemistry
幼犬到家第一天，你们之间没有默契。它不知道你的指令，你不知道它的脾气。但第一天的互动，决定了它对你的第一印象。
和 Hermes Agent 的第一次对话也是一样。它的界面、操作方式、反馈节奏可能和你之前用的 AI 工具不一样。花 10 分钟熟悉一下，后面会顺畅很多。
### 启动 TUI

```bash
hermes
```
你会看到一个终端 UI 界面。这不是普通的命令行 — 它是一个完整的 TUI（Terminal User Interface），支持多行编辑、自动补全、流式输出。
界面底部是输入框，顶部是状态栏。状态栏的信息很关键：

```text
Model: claude-sonnet-4-6 | Tokens: 1.2k/200k (0.6%) \
  | Cost: $0.02 | Session: 8m
```
| 状态信息 | 含义 |
|----------|------|
| Model | 当前使用的 LLM 模型 |
| Tokens | 已用/总量（百分比），< 50% 绿色，50-80% 黄色，80-95% 橙色，> 95% 红色 |
| Cost | 本次会话累计费用 |
| Session | 本次会话时长 |
### 常用快捷键
| 快捷键 | 功能 |
|--------|------|
| `Enter` | 发送消息 |
| `Alt+Enter` / `Ctrl+J` | 换行（多行输入） |
| `Ctrl+C` | 中断 Agent（双击强制退出） |
| `Ctrl+D` | 退出 |
| `Ctrl+Z` | 挂起到后台（`fg` 恢复） |
| `Alt+V` | 粘贴剪贴板图片 |
| `Tab` | 接受自动补全 |
### 常用斜杠命令
| 命令 | 功能 |
|------|------|
| `/help` | 查看所有命令 |
| `/model` | 切换模型 |
| `/tools` | 查看/管理工具集 |
| `/skills browse` | 浏览已安装 Skill |
| `/background <提示>` | 后台执行任务 |
| `/reasoning high` | 提高推理深度 |
| `/compress` | 手动触发上下文压缩 |
| `/new` | 开始新会话 |
| `/usage` | 查看用量统计 |
### 一个真实的第一次对话
让我模拟一个有意义的第一次对话。不是"你好，今天天气怎么样"那种无意义测试。
**你说：**
> 我是一个 Python 后端开发者，主要用 FastAPI + PostgreSQL。帮我检查一下当前目录的代码结构有没有明显问题。
**Agent 会做什么：**
1. 调用 `terminal` 工具执行 `ls -la` 和 `find . -type f -name "*.py"` 了解项目结构
2. 调用 `read_file` 工具查看关键文件（`pyproject.toml`、`requirements.txt`、主入口文件）
3. 分析结构，给出建议
**Agent 的回复可能长这样：**
> 看了一下你的项目结构。几个建议：
> 1. `requirements.txt` 和 `pyproject.toml` 都存在，建议统一用 `pyproject.toml`
> 2. `alembic/` 目录存在但没有 `alembic.ini`，数据库迁移配置缺失
> 3. 所有路由都堆在 `main.py` 里，建议按功能拆分
> 4. 没有看到 `.env.example`，建议加一个
注意到了吗？Agent 主动调用了工具来了解你的项目，而不是直接猜。这就是 Agent 和聊天机器人的区别 — 它能**动手**。
### `/background`：让它干活，你继续聊天
这是 Hermes 的一个实用功能。你可以让 Agent 在后台执行耗时任务，同时继续在前台聊天。

```text
/background 帮我把这个项目的所有 Python 文件加上类型注解
```
Agent 会启动一个完全隔离的后台会话来执行这个任务。前台你可以继续问别的问题。任务完成后结果会出现在面板中。
> **核心建议**
>
> 第一次对话不要测试"你好"这种无意义内容。直接给 Agent 一个和你工作相关的真实任务 — 审查代码、分析日志、写个脚本。这样你才能感受到它调用工具、执行命令、搜索文件的完整能力。而且，真实的互动能触发 Agent 的记忆和学习机制，让第一次对话就产生价值。
第一次对话结束。你和 Agent 之间已经有了初步了解。下一章，我们创建第一个 Skill — 把这次互动中学到的东西固化下来。
## §09 创建你的第一个 Skill
Creating Your First Skill
训练一只狗学会"坐下"，通常有两种方式：一种是它观察你的行为自己领悟，一种是你在它做完正确动作后立刻给奖励强化。
Hermes Agent 的 Skill 也是两种来源：Agent 自己从经验中提炼，或者你手动写好让它直接学。两种方式都能用，但这次我们先动手写一个 — 这样你对 Skill 格式的理解会更深刻。
### 场景设定：让 Agent 学会"代码审查"
假设你是一个团队的技术负责人，每天要审查好几个 PR。你希望 Agent 按你团队的特定标准来审查，而不是用通用的审查逻辑。
你的团队关注这些维度：
- 错误处理是否用了自定义错误类
- 数据库操作是否有事务保护
- API 响应格式是否符合团队规范
- 是否有硬编码的配置项
这些是你团队的"特殊知识"，Agent 不可能自动知道。需要你手动写进 Skill。
### 手动创建 Skill 的完整过程
**第一步：创建目录结构**

```bash
mkdir -p ~/.hermes/skills/team-code-reviewer/references
```
**第二步：写 SKILL.md**

```yaml
---
name: team-code-reviewer
description: 按团队特定标准审查代码变更，关注错误处理、事务保护、API 规范和配置管理
metadata:
hermes:
tags: [code-review, team-standards]
category: development
requires_toolsets: [terminal, file]
---
```

```markdown
# Team Code Reviewer
## 审查标准
### 1. 错误处理
- 使用 `AppError` 自定义错误类，catch 块包含上下文日志
### 2. 数据库事务
- 写操作包裹在事务中，范围最小化
### 3. API 响应格式
- 符合 `{code, message, data}` 统一格式
### 4. 配置管理
- 无硬编码密钥，配置通过环境变量读取
## 输出格式
| 严重程度 | 文件 | 问题 | 修复建议 |
|----------|------|------|----------|
| 🔴 阻断 | ... | ... | ... |
```
**第三步（可选）：添加参考文档**
把团队的完整编码规范放到 `references/` 目录：

```bash
# 把团队的编码规范文档放进来
cp ~/team-standards.md \
  ~/.hermes/skills/team-code-reviewer/references/coding-standards.md
```
Skill 内容可以引用这个文件，Agent 在深度使用时会按需加载。
**第四步：验证**
重启 Agent 或在对话中输入：

```text
/skills browse
```
你应该能看到 `team-code-reviewer` 出现在列表中。现在当你让 Agent 审查代码时，它会自动加载这个 Skill。
### 观察自动创建：让 Agent 自己提炼一个 Skill
手动写 Skill 适合你有明确标准的场景。但有些时候，最佳实践是 Agent 在干活的过程中自己发现的。
试试这样做：
1. 让 Agent 帮你做一个复杂的、多步骤的任务（比如"帮我配置这个项目的 CI/CD 流水线"）
2. 在过程中纠正它几次（"不对，我们用 GitHub Actions 不用 GitLab CI"，"test 阶段需要先建测试数据库"）
3. 任务完成后，检查 `~/.hermes/skills/` 目录
你可能会发现一个新的 Skill 目录 — Agent 在任务完成后评估了整个流程，认为值得记录，于是自动创建了。
| 特征 | 手动 Skill | 自动 Skill |
|------|-----------|-----------|
| 来源 | 你的专业知识 | Agent 的实战经验 |
| 格式 | 结构清晰、文档化 | 偏向操作步骤 |
| 适用 | 团队规范、部署流程 | 踩坑经验、最佳路径 |
| 维护 | 你来更新 | Agent 自改进 |
### 渐进式加载验证
你可以验证 Skill 的渐进式加载：
1. 启动 Agent 时，只有 Skill 的名称和描述被加载（~100 Token/个）
2. 在对话中提到"代码审查"，Agent 会判断 `team-code-reviewer` 相关，加载完整内容
3. 如果 Skill 里引用了 `references/` 下的文件，Agent 在需要时才加载
这个设计意味着即使你后续装了几十个 Skill，启动速度和上下文占用几乎不受影响。
### 常见 Skill 编写错误
| 错误 | 问题 | 正确做法 |
|------|------|----------|
| 描述太宽泛 | "帮我做各种事" → Agent 不知道什么时候该用 | 精确描述触发场景 |
| 步骤太抽象 | "检查代码质量" → 不可执行 | 写具体检查项 |
| 超过 500 行 | 完整内容加载时浪费 Token | 细节移到 references/ |
| SKILL.md 名字和目录不一致 | name 字段必须和父目录名匹配 | 两者保持一致 |
| 没声明工具依赖 | Agent 可能在没有工具时尝试执行 | 用 requires_toolsets 声明 |
> **核心建议**
>
> 第一个 Skill 别写太复杂。挑一个你每天都在做的、步骤固定的任务 — 代码审查、部署检查、日报生成，什么都行。先跑通一个，理解格式和加载机制，再扩展到更复杂的场景。记住：Skill 的价值在于"可复用"，写一个你每周都会用到的 Skill 比写一个偶尔用一次的复杂 Skill 更有价值。
Skill 写好了，Agent 有了可复用的能力。但到目前为止，你只能在终端里和它交互。下一章，我们把它接到 Telegram 和 Discord 上 — 让它住进你的日常通讯工具。
## §10 接入 Telegram 和 Discord：让它住进你的通讯工具
Connecting to Telegram & Discord
一只工作犬只会呆在后院是没用的。你得让它跟着你 — 去办公室、去仓库、去任何需要它的地方。
Hermes Agent 的 Gateway 就是它的"出门许可"。启动 Gateway 后，Agent 就能在 Telegram、Discord、Slack 等 15 个平台上待命。你在哪里，它就在哪里。
### Gateway 架构：一个进程，15 个平台
Gateway 是一个长驻进程，负责五件事：**消息收发、会话路由、内容推送、用户配对、定时任务调度**。
支持的 15 个平台：
| 平台 | 类型 | 特色功能 |
|------|------|----------|
| Telegram | 即时通讯 | Project Conversations（私聊话题隔离） |
| Discord | 社区 | 频道权限控制 |
| Slack | 办公协作 | 工作空间集成 |
| WhatsApp | 即时通讯 | 需要手机桥接 |
| Signal | 加密通讯 | 隐私优先 |
| Matrix | 去中心化 | 开源协议 |
| Mattermost | 自托管 | 企业场景 |
| Email | 异步 | IMAP/SMTP |
| SMS | 移动 | 需 Twilio 等 |
| DingTalk | 企业 | 国内常用 |
| Feishu/Lark | 企业 | 字节系 |
| WeCom | 企业 | 微信系 |
| Home Assistant | IoT | 智能家居控制 |
| BlueBubbles | iMessage | Mac 用户 |
| Webhooks | 通用 | 自定义集成 |
一个 Gateway 进程同时服务所有平台。不需要为每个平台启动单独的实例。

![Gateway 架构](images/gateway-architecture.png)
### Telegram 接入（最常用）
**第一步：创建 Telegram Bot**
1. 在 Telegram 里找 `@BotFather`
2. 发送 `/newbot`
3. 给 Bot 起个名字
4. 拿到 Bot Token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）
**第二步：配置 Gateway**

```bash
hermes gateway setup
```
选择 Telegram，输入 Bot Token。配置保存在 `~/.hermes/config.yaml` 中。
或者手动编辑配置：

```yaml
# ~/.hermes/config.yaml
gateway:
telegram:
enabled: true
token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
```
**第三步：启动 Gateway**

```bash
hermes gateway
```
**第四步：配对授权**
Gateway 启动后，在 Telegram 里给你的 Bot 发一条消息。Bot 不会立刻回复 — 它需要你先授权。

```bash
# 查看待审批的配对请求
hermes pairing list
# 批准
hermes pairing approve telegram ABC12DEF
```
配对码是 8 位随机字符，1 小时内有效。这是安全设计 — 防止别人知道你的 Bot Token 就能用。
**第五步：设为系统服务（推荐）**

```bash
hermes gateway install --system
```
这样 Gateway 会随系统启动自动运行，崩溃后自动重启。
### Discord 接入
流程类似，但配置略有不同：
1. 去 Discord Developer Portal 创建 Bot
2. 获取 Bot Token
3. 设置 Intents（需要 Message Content Intent）
4. 生成邀请链接，把 Bot 拉进你的服务器

```yaml
gateway:
discord:
enabled: true
token: "MTIzNDU2Nzg5..."
```
### 跨平台连续性
这是 Gateway 最酷的功能之一。
你在 Telegram 上开始了一个对话 — 让 Agent 帮你分析一段日志。聊到一半，你要出门了。到了办公室，打开终端：

```bash
hermes --continue
```
Agent 会加载最近的会话上下文，继续刚才的对话。就好像你们从来没断过。
原理：会话绑定的是 **Session ID**，不是平台。Gateway 把不同平台的消息路由到同一个 Session ID 对应的 `AIAgent` 实例。你的对话历史、记忆、Skill — 全部跨平台共享。
| 你在 Telegram 说 | Agent 记得 | 你在终端继续 |
|-------------------|-----------|-------------|
| "我们项目用 FastAPI" | 存入 MEMORY.md | 自动知道技术栈 |
| "用 httpx 不用 requests" | 存入偏好 | 代码生成用 httpx |
| "部署用 GitHub Actions" | 创建了 deploy Skill | 自动加载 Skill |
### 语音消息支持
Gateway 还支持语音消息。你发一条语音，Agent 会自动转写、理解、回复。
转写提供商（按优先级）：
1. 本地 Whisper（免费，需 ffmpeg）
2. Groq（快，云端）
3. OpenAI Whisper API（准，付费）
### API Server 模式
如果你不想用终端也不想用通讯平台，Hermes 还能暴露为 **OpenAI 兼容的 HTTP 端点**：

```bash
hermes serve --port 8080
```
然后任何支持 OpenAI API 格式的前端 — Open WebUI、LobeChat、LibreChat、NextChat — 都能连上来用。Agent 的全部工具和记忆在 HTTP 模式下同样可用。
> **核心建议**
>
> 第一阶段只接 Telegram 就够了。它的 Bot 创建最简单，API 最稳定，还支持 Topic 隔离（一个 Bot 跑多个独立工作流）。等你在 Telegram 上跑顺了，再加 Discord 和 Slack。不要一上来就接 5 个平台 — 每个 Platform 的权限配置和配对流程都需要时间，逐步添加更稳。
Gateway 跑起来了。Agent 住进了你的 Telegram。接下来的章节，我们让它开始干活 — 用真实场景验证它的能力。
从安装到配置到接入平台，你的"幼犬"已经正式安家了。接下来的章节，我们给它派真正的活儿。
---
# Part 4: 实战场景
## §11 代码审查 Agent：24 小时帮你看 PR
Code Review Agent: Your 24/7 PR Watchdog
你的团队有 5 个开发者，每天产生 3-5 个 PR。作为技术负责人，你每天花 1-2 小时审查代码。有些审查是重复的 — 检查错误处理、确认 API 格式、看有没有硬编码。
这些重复的部分，为什么不交给 Agent？
### 需求分析
不是所有代码审查都适合自动化。先分清：
| 适合 Agent 做 | 必须人做 |
|--------------|----------|
| 检查 API 响应格式是否符合规范 | 评估架构决策是否合理 |
| 发现硬编码的密钥和配置 | 判断业务逻辑是否正确 |
| 检查错误处理是否完整 | 评估用户体验影响 |
| 验证事务边界是否正确 | 代码可读性的主观判断 |
| 发现常见的性能反模式 | 团队共识和沟通 |
Agent 处理的是"标准检查清单"，你处理的是"需要判断力的部分"。分工明确，效率翻倍。
### 方案设计
我们要搭建一个自动审查 PR 的工作流：

```text
Cron 定时触发（每 30 分钟）
→ Agent 拉取最新 PR 列表
→ 对每个新 PR 执行审查 Skill
→ 结果推送到 Telegram
```
需要的组件：
- **Cron 任务**：定时触发
- **Terminal 工具**：执行 git 命令
- **team-code-reviewer Skill**：我们在 §09 创建的审查标准
- **Telegram 推送**：审查结果发到你的聊天
### 逐步实现
**第一步：创建审查 Skill（如果还没有）**
按 §09 的流程创建 `team-code-reviewer` Skill。如果你跳过了那一章，现在创建也行 — 内容可以比 §09 简化，核心是列出你要检查的维度。
**第二步：创建 Cron 任务**
在 Hermes 对话中直接说：

```text
每 30 分钟检查一次 GitHub 仓库的新 PR，
用 team-code-reviewer Skill 审查变更内容，
把结果发到 Telegram。如果没有新 PR 就不通知。
```
Agent 会帮你创建一个 Cron 任务。你也可以用命令行：

```bash
hermes cron create "*/30 * * * *" \
  "检查 GitHub 仓库是否有新的 PR。如果有，\
用 team-code-reviewer Skill 审查变更内容。\
把结果发到 Telegram。如果没有新 PR，以 [SILENT] 开头。" \
  --skill team-code-reviewer \
  --name "PR 审查" \
  --deliver telegram
```
几个关键参数说明：
| 参数 | 值 | 含义 |
|------|-----|------|
| `*/30 * * * *` | Cron 表达式 | 每 30 分钟 |
| `--skill` | team-code-reviewer | 审查时自动加载这个 Skill |
| `--deliver` | telegram | 结果发到 Telegram |
| `[SILENT]` | 特殊标记 | 以这个开头就不推送，静默保存 |
**第三步：验证效果**
手动触发一次，看看输出：

```bash
hermes cron run <任务ID>
```
Agent 会：
1. 执行 `git fetch` 和 `git log` 检查新 PR
2. 对每个新 PR 执行审查流程
3. 按 Skill 定义的格式输出结果
4. 推送到你的 Telegram
**第四步：观察和调整**
运行几天后，你可能需要调整：
- **太吵了？** 把间隔从 30 分钟改成 1 小时，或者只在工作时间运行（`0 9-18 * * 1-5`）
- **误报太多？** 更新 Skill 的审查标准，提高阈值
- **遗漏了？** 给 Skill 添加新的检查维度
### 进阶：用 Subagent 并行审查多个 PR
如果一次有 3 个 PR 要审查，串行太慢。用 Subagent 并行处理：
在 Cron 任务的提示中加入：

```text
如果有多于一个 PR 需要审查，用 delegate_task 并行处理每个 PR。每个Subagent 只负责一个 PR 的审查，最终汇总结果。
```
Agent 会调用 `delegate_task` 工具，为每个 PR 启动一个独立的Subagent。每个Subagent 有自己的终端会话和上下文，互不干扰。所有Subagent 完成后，主 Agent 汇总结果推送给你。
| 维度 | 串行审查 | 并行审查 |
|------|----------|----------|
| 3 个 PR 耗时 | ~15 分钟 | ~5 分钟 |
| Token 成本 | 相同 | 相同（Subagent 用便宜模型） |
| 上下文压力 | 一个会话塞三个 PR | 每个会话一个 PR |
| 最大并发 | 1 | 3（默认上限） |
> **核心建议**
>
> 代码审查 Agent 的价值不在于替代你审查代码，而在于**过滤** — 把明显的格式问题、安全隐患、配置错误先过滤掉，你只需要关注真正需要判断力的部分。从 Cron 间隔 2 小时开始，逐步缩短到你满意的频率。前两周记得每天检查 Agent 的审查结果，及时纠正误判 — 这些纠正信号会让 Agent 的自改进循环启动。
代码审查 Agent 跑起来了。下一章，我们搭一个完全不同类型的 Agent — 信息监控，每天早上给你一份简报。
## §12 信息监控 Agent：每天早上给你一份简报
Information Monitor: Your Daily Briefing Agent
每天早上 9 点，你打开手机，Telegram 里已经有一条消息：今天 Hacker News AI 频道的 Top 10 文章，每篇 3 句话摘要，标注了和你相关的方向。
不是你订阅的 RSS，不是什么新闻聚合 App。是你的 Agent 自己搜索、筛选、总结、推送的。
### 需求拆解
这个 Agent 要做四件事：
1. **搜索**：从指定信息源抓取内容
2. **筛选**：只保留和你相关的
3. **总结**：每篇文章浓缩到 3-5 句话
4. **推送**：发到你的 Telegram
四步串起来，就是一个完整的信息监控流水线。
### 方案设计

```text
每天 9:00 Cron 触发
→ Agent 搜索 Hacker News AI 频道
→ 用 web_extract 提取 Top 文章内容
→ 筛选和你方向相关的（根据 MEMORY.md 中的偏好）
→ 总结每篇 3-5 句话
→ 推送到 Telegram
```
这次我们不写 Skill，直接在 Cron 提示中定义行为。简单场景不需要 Skill 的开销。
### 逐步实现
**第一步：确保 Agent 了解你的关注方向**
在对话中告诉 Agent：

```text
记住我的技术关注方向：
Python 后端开发、AI Agent 框架、
PostgreSQL 性能优化、FastAPI 最佳实践。
其他方向的不用推送给我。
```
Agent 会把这些信息存入 `MEMORY.md`。以后所有信息筛选都基于这些偏好。
**第二步：创建 Cron 任务**

```text
/cron add "0 9 * * *" \
  "搜索 Hacker News 上关于 AI、Python 后端、数据库性能的\
最新讨论。提取 Top 10 文章的标题、链接和关键观点。\
每篇用 3-5 句话总结，标注和我方向相关的内容。\
最后给出一个'今日必读'推荐（最相关的 1-2 篇）。\
格式用 Markdown。结果发到 Telegram。" \
  --name "每日技术简报" --deliver telegram
```
**第三步：手动触发测试**

```bash
hermes cron run <任务ID>
```
检查 Telegram 收到的消息。如果质量不满意，调整提示词。常见调整：
| 问题 | 调整 |
|------|------|
| 摘要太长 | 提示中明确"每篇不超过 3 句话" |
| 信息源不够 | 添加更多搜索关键词或指定网站 |
| 不够精准 | 更新 MEMORY.md 中的偏好描述 |
| 格式混乱 | 提示中给出格式模板 |
**第四步：加入 Silent 模式**
在提示开头加上：

```text
如果没有找到与我的关注方向相关的文章，以 [SILENT] 开头。
```
这样没有好内容的日子，Agent 不会打扰你。只有发现值得看的东西时，才会推送。
### 扩展：多信息源 + Subagent 并行
单靠 Hacker News 太单一了。扩展到多个信息源：

```text
同时搜索以下来源的 AI 和 Python 相关内容：
1. Hacker News
2. Reddit r/Python 和 r/MachineLearning
3. Dev.to 的 Python 和 AI 标签
用 delegate_task 并行搜索这三个来源，每个Subagent 负责一个来源。汇总后去重、排序、总结。
```
Agent 会启动 3 个Subagent 并行搜索，各自独立抓取，主 Agent 汇总去重后输出最终简报。
| 维度 | 单信息源 | 多信息源并行 |
|------|----------|-------------|
| 覆盖面 | 窄 | 广 |
| 耗时 | ~2 分钟 | ~2 分钟（并行） |
| Token 成本 | 低 | 中（Subagent 用便宜模型） |
| 去重压力 | 无 | 需要（同话题多源报道） |
### 推送时间选择
| 时间 | 适合人群 | Cron 表达式 |
|------|----------|-------------|
| 早上 9 点 | 上班路上看 | `0 9 * * 1-5` |
| 中午 12 点 | 午休时扫一眼 | `0 12 * * 1-5` |
| 晚上 8 点 | 下班后学习 | `0 20 * * 1-5` |
| 每天 2 次 | 信息重度用户 | `0 9,20 * * 1-5` |
`1-5` 表示周一到周五。周末不加 `1-5` 就每天都推。
> **核心建议**
>
> 信息监控 Agent 的核心不是"搜得多"，是"筛得准"。刚开始宁可少推，也不要推一堆你不关心的内容。每次 Agent 推了你不感兴趣的东西，告诉它"这个方向我不关注" — 这是最高效的训练信号。一周左右，它的筛选精度会显著提升。
信息监控 Agent 搞定了。下一章，我们把 Cron、Subagent、多平台推送组合起来，搭一个更复杂的自动化场景。
## §13 多平台自动化：Cron + Subagent 组合拳
Multi-Platform Automation: Cron + Subagent Combo
一只训练有素的工作犬，能同时做很多事 — 看门、牧羊、搜索。关键是调度合理、分工明确。
这一章我们把前面学的所有组件组合起来 — Cron 定时、Subagent 并行、多平台推送、Skill 加载 — 搭一个真实的综合自动化场景。
### 场景：每周自动检查服务健康状态
你管理着 3 个线上服务：
- API 服务（api.example.com）
- 管理后台（admin.example.com）
- 文档站（docs.example.com）
每周一早上 8 点，你想要一份健康报告：
- 各服务的可用性和响应时间
- 磁盘使用率
- 最近一周的错误日志摘要
- 如果有问题，高亮标注
报告发到 Slack 的 `#engineering` 频道。如果有严重问题，同时发 Telegram 私信给你。
### 方案设计

```text
每周一 8:00 Cron 触发
→ 主 Agent 创建 3 个 Subagent（每个负责一个服务）
→ Subagent A：检查 API 服务（终端 + Web 工具）
→ Subagent B：检查管理后台
→ Subagent C：检查文档站
→ 主 Agent 汇总报告
→ 正常：发到 Slack #engineering
→ 有严重问题：额外发 Telegram 私信
```
### 逐步实现
**第一步：创建健康检查 Skill**
先创建一个通用的服务健康检查 Skill，确保每次检查的维度一致：

```yaml
---
name: service-health-check
description: 检查服务的健康状态，包括可用性、响应时间、资源使用率和错误日志
metadata:
hermes:
tags: [monitoring, devops]
category: operations
requires_toolsets: [terminal, web]
---
```

```markdown
# Service Health Check
## 检查维度
### 1. 可用性
- HTTP 200, 响应 < 2s, SSL 有效
### 2. 资源使用
- CPU < 80%, 内存 < 85%, 磁盘 < 90%
### 3. 错误日志
- 7 天 5xx 错误数量与趋势
## 输出格式
| 服务 | 可用性 | 响应 | CPU | 状态 |
|------|--------|------|-----|------|
| ... | ✅/❌ | ...ms | ...% | 🟢/🟡/🔴 |
```
**第二步：创建 Cron 任务**

```text
每周一早上 8 点，用 service-health-check Skill 检查以下三个服务：
- api.example.com
- admin.example.com
- docs.example.com
用 delegate_task 并行检查，每个Subagent 负责一个服务。汇总后生成报告。
报告发到 Slack #engineering 频道。
如果任何服务状态为 🔴，额外发一条消息到 Telegram，
包含问题详情和建议的修复步骤。
```
对应的命令：

```bash
hermes cron create "0 8 * * 1" \
  "用 service-health-check Skill 检查 api.example.com、\
admin.example.com、docs.example.com 的健康状态。\
用 delegate_task 并行检查三个服务。汇总报告发到 Slack。\
如果任何服务为红色状态，额外发 Telegram 通知。" \
  --skill service-health-check \
  --name "每周服务健康检查" \
  --deliver slack
```
**第三步：理解执行流程**
Cron 触发后，Agent 的执行流程：
1. **加载 Skill**：`service-health-check` 的审查标准注入上下文
2. **创建Subagent**：3 个 `delegate_task` 调用，各自有独立的终端和上下文
3. **并行检查**：每个Subagent 执行 HTTP 检查、SSH 到服务器看资源、扫描日志
4. **汇总**：主 Agent 收到 3 个Subagent 的结果，生成统一格式报告
5. **推送**：正常报告 → Slack `#engineering`；有问题 → 额外推 Telegram
### Subagent 的安全边界
Subagent 不是无限权力的。有些工具在Subagent 中被禁用：
| 被禁用的工具集 | 原因 |
|---------------|------|
| `delegation` | 防止递归生成（Subagent 不能再生Subagent） |
| `clarify` | Subagent 不能和你互动 |
| `memory` | Subagent 不能写入主 Agent 的记忆 |
| `send_message` | Subagent 不能直接推送消息 |
深度限制为 2 层 — 主 Agent 可以创建Subagent，Subagent 不能再创建Subagent。每个Subagent 最多 50 轮迭代。
### Cron 管理命令速查
| 操作 | 命令 |
|------|------|
| 列出所有任务 | `hermes cron list` |
| 暂停 | `hermes cron pause <id>` |
| 恢复 | `hermes cron resume <id>` |
| 手动触发 | `hermes cron run <id>` |
| 修改计划 | `hermes cron edit <id> --schedule "0 8 * * 1-5"` |
| 删除 | `hermes cron remove <id>` |
| 查看状态 | `hermes cron status` |
### 可选优化：用便宜模型跑Subagent
Subagent 做的是相对简单的检查任务，不需要最强的模型。在 config.yaml 中配置：

```yaml
delegation:
model: "google/gemini-3-flash-preview"
provider: "openrouter"
```
这样主 Agent 用 Claude Sonnet 做汇总和判断，Subagent 用便宜的 Gemini Flash 做执行。成本可以降低 5-10 倍。

![多平台自动化](images/multi-platform-automation.png)
> **核心建议**
>
> 自动化场景的复杂度要逐步增加。先从一个最简单的 Cron 任务开始（比如每天早上检查一个网站），跑通后再加 Subagent 并行、多平台推送、条件判断。不要一上来就搭复杂的流水线 — 复杂度越高，调试成本越高。先让简单的东西稳定运行一周，再逐步叠加。
三个实战场景都搭完了。你的 Agent 现在能审查代码、监控信息、检查服务健康 — 而且全都是自动化的。接下来的章节，我们站高一层，看看 Hermes 在整个 AI Agent 生态中的位置。
---
# Part 5: 深度思考
## §14 Hermes vs OpenClaw：自改进 vs 手动控制，到底谁对？
Hermes vs OpenClaw: Self-Improvement vs Manual Control
"到底选 Hermes 还是 OpenClaw？" — 这是 2026 年 Agent 社区被问得最多的问题之一。
我的回答可能让你意外：这不是一个"谁对"的问题，是一个"你信什么"的问题。
### 核心哲学差异
两个框架的根本分歧在于一句话：**Agent 应该自己学会做事，还是由人来告诉它怎么做？**
Hermes 的答案：Agent 像一只工作犬，通过反复互动和反馈，**自己学会**怎么帮你做事。你不需要写规则手册 — 它自己会提炼。
OpenClaw 的答案：Agent 像一个控制面网关，**人来写规则**，Agent 严格执行。你对它的每个行为都有完全的可见性和控制力。
这不是功能差异，是信仰差异。
### 架构对比
| 维度 | Hermes Agent | OpenClaw |
|------|-------------|----------|
| **核心理念** | Agent as a mind to be developed | Agent as a control plane |
| **记忆架构** | 四层：热记忆 + 冷召回 + Skill + 外部提供商 | 文件式：MEMORY.md + 人工管理的身份文件 |
| **Skill 创建** | 自动提炼 + 手动编写 + 社区安装 | 以人工编写为主，更强调精确控制 |
| **Skill 标准** | agentskills.io 开放标准 | 自己的 Skill 体系 |
| **生态规模** | 643 社区 Skill | 44,000+ 社区 Skill |
| **模型支持** | 200+ 模型 | 模型无关 |
| **多平台** | 15 个平台适配器 | 多平台支持 |
| **部署** | 6 种终端后端（含 Serverless） | 本地/Docker 为主 |
| **定时任务** | 内置 Cron | 有限支持 |
| **安全** | 命令审批 + 容器隔离 + SSRF + 凭据过滤 | 可配置 |
| **开源协议** | MIT | 开源 |
差距最大的两个维度是**生态规模**和**自改进能力**。OpenClaw 的社区生态远大于 Hermes（44,000 vs 643），但 Hermes 的自改进能力是 OpenClaw 完全没有的。
### 一个关键问题：你信任 Agent 自己学习吗？
这个问题的答案决定了你应该选哪个。
**选 Hermes 如果你相信：**
- Agent 可以从错误中自我纠正
- 经验积累比规则编写更有效
- 你愿意在初期花时间"训练"Agent，换取长期的高默契
- 你接受 Agent 有时会学到"不太对"的东西，需要偶尔纠正
**选 OpenClaw 如果你相信：**
- Agent 的每个行为都应该在你的控制之下
- 人工编写的规则比自动提炼的更可靠
- 你需要精确的可审计性和可追溯性
- 你的场景对错误容忍度极低（金融、医疗等）
### 我的判断
两者不是替代关系，是互补关系。
打个比方：Hermes 是一个有自主学习能力的助手，OpenClaw 是一个严格执行流程的执行者。你需要前者来处理"不确定的、需要判断力的"工作，需要后者来处理"必须零差错的、有严格规范的"工作。
实际操作中，很多团队的做法是：
- **开发阶段用 Hermes** — Agent 在反复交互中学习团队的工作方式
- **生产阶段关键流程用 OpenClaw** — 用精确的规则控制部署、监控等关键操作
- **两者可以共存** — Hermes 的 Gateway 和 OpenClaw 的网关可以同时运行，分别负责不同任务
> **核心建议**
>
> 如果你是个人开发者或小团队，从 Hermes 开始。它的自改进循环能让你快速获得一个"懂你"的助手，而且 643 个 Skill 对大多数场景已经够用。如果你是企业用户，或者你的场景对精确控制有硬性要求，OpenClaw 更合适。如果你两边都想要 — 可以，它们不冲突。迁移成本也不高，因为两者的配置格式有相似之处。
选型做完了。最后一章，我们聊聊安全 — 当你的 Agent 比你还了解你的时候，什么该防、什么不该防。
## §15 安全边界与未来：当你的 Agent 比你还了解你
Security Boundaries & the Future
你驯养的工作犬已经能帮你做很多事了 — 审查代码、监控信息、检查服务健康。它记得你的偏好，了解你的工作方式，甚至能独立执行复杂任务。
这时候一个严肃的问题浮上来：**它知道你这么多信息，安全吗？**
这不是杞人忧天。一个 7x24 小时运行、有终端执行权限、了解你偏好、能访问你通讯平台的 Agent，如果安全没做好，后果可以很严重。
好消息是，Hermes 在安全上花了不少心思。
### 安全体系全览
Hermes 的安全不是一个开关，而是多层防御：
| 层级 | 机制 | 保护什么 |
|------|------|----------|
| **命令审批** | 危险终端命令需用户确认 | 防止误操作破坏系统 |
| **容器隔离** | Docker 后端：drop ALL capabilities + pids limit | 隔离 Agent 的执行环境 |
| **SSRF 防护** | 禁止访问内网/云元数据地址 | 防止通过 URL 工具探测内网 |
| **凭据过滤** | 敏感环境变量在执行和日志中自动脱敏 | 防止密钥泄露 |
| **Tirith（一个安全审计框架）扫描** | 命令注入、管道攻击、同形字 URL 检测 | 防止提示注入导致执行恶意命令 |
| **上下文注入防护** | 扫描 AGENTS.md、SOUL.md 等文件 | 防止仓库投毒 |
| **配对授权** | 8 位随机码 + 时效限制 + 失败锁定 | 防止未授权用户使用你的 Agent |
| **Cron 安全** | 禁止递归创建 Cron、扫描提示注入 | 防止定时任务链式攻击 |
### 6 种终端后端的安全等级
不是所有部署方式的安全等级都一样：
| 后端 | 安全等级 | 为什么 |
|------|----------|--------|
| **local** | 低 | 直接跑在你机器上，无隔离 |
| **ssh** | 中 | 远程执行，但远程机器可能被影响 |
| **docker** | 高 | 容器隔离，能力受限 |
| **singularity** | 高 | HPC 级隔离，无 root |
| **modal** | 高 | 云端沙箱，按需启停 |
| **daytona** | 高 | 持久云端沙箱 |
| 后端 | 命令审批 | 容器隔离 | SSRF 防护 |
|------|----------|----------|-----------|
| local | 需要 | 无 | 有 |
| docker | 跳过（容器即边界） | 有 | 有 |
| modal | 跳过 | 有 | 有 |
| ssh | 需要 | 无 | 有 |
**local 后端下**，Agent 执行危险命令（`rm`、`sudo`、`chmod` 等）时会暂停，等你确认。这是最后一道防线。
**Docker 后端下**，每个容器都运行在严格限制下：`--cap-drop ALL`（移除所有 Linux 能力）、`no-new-privileges`（禁止提权）、`--pids-limit 256`（限制进程数）。命令审批被跳过，因为容器本身就是安全边界。
### SSRF 防护：容易被忽略但极重要
SSRF（Server-Side Request Forgery）是 Agent 场景下的高发攻击面。想象一下：你让 Agent 访问一个网页，网页里藏了一个指向 `http://169.254.169.254/latest/meta-data/` 的链接 — 这是 AWS 云实例的元数据接口，能拿到 IAM 凭据。
Hermes 的所有 URL 工具都会验证目标地址，拦截：
- 私有网络（10.0.0.0/8、172.16.0.0/12、192.168.0.0/16）
- 环回地址（127.0.0.0/8）
- 链路本地（169.254.0.0/16 — 云元数据）
- DNS 失败时 fail-closed（宁可拦错不可放过）
- 重定向链的每一跳都会重新验证
这个防护不能关闭。
### 自改进的双刃剑
自改进循环是 Hermes 的核心卖点，但也带来一个独特的安全问题：**Agent 可能学到"坏习惯"。**
假设你在一个项目里用了不规范的代码风格。Agent 观察到后可能创建一个 Skill，把这种不规范的模式当作"正确做法"推广到其他项目。
怎么防范？
1. **定期审查自动创建的 Skill**：`ls ~/.hermes/skills/` 看看 Agent 自己创建了什么
2. **主动纠正**：当你发现 Agent 做错了，明确告诉它"这不是正确做法，正确做法是..."
3. **关键流程用手动 Skill**：对于安全敏感的流程（部署、权限管理），用你手写的 Skill，不依赖自动创建的
4. **MEMORY.md 保持精简**：热记忆空间有限，如果你发现里面有不准确的信息，手动清理
### 记忆主权：你的数据在哪
| 数据 | 存储位置 | 谁能访问 |
|------|----------|----------|
| 热记忆（MEMORY.md/USER.md） | 本地文件 `~/.hermes/memories/` | 只有你 |
| 会话档案（state.db） | 本地 SQLite `~/.hermes/` | 只有你 |
| Skill 文件 | 本地 `~/.hermes/skills/` | 只有你 |
| Cron 任务 | 本地 `~/.hermes/cron/` | 只有你 |
| API Key | 本地 `~/.hermes/.env` | 只有你 |
| 日志 | 本地 `~/.hermes/logs/`（密钥自动脱敏） | 只有你 |
所有数据都在你本地。Hermes 不上传你的对话、记忆或 Skill 到任何服务器。LLM 调用走的是你配置的提供商（OpenRouter、OpenAI 等），这些调用本身遵循各提供商的隐私政策。
如果你想彻底清除所有数据：

```bash
rm -rf ~/.hermes/
```
一个命令，全部清空。你的 Agent 回到出厂状态。
### 未来展望
Hermes Agent 代表了 AI Agent 的一个方向：**Agent 不是工具，是队友。**
工具的特征是稳定 — 锤子今天和明天一样重。队友的特征是成长 — 今天的配合比昨天好，明天比今天更好。
这个方向会带来几个变化：
**1. Agent 从"按次计费"变成"长期投资"**
用 Hermes 的第一个月，你可能觉得它还不如 Claude Code 好用 — 因为它还在学习你的偏好。但到了第三个月，它对你的项目、代码风格、工作习惯的了解，是任何新会话无法比拟的。这种"复利效应"是自改进 Agent 的核心价值。
**2. 记忆系统会成为 Agent 的核心竞争维度**
现在大家比的是"谁的工具多"。未来比的会是"谁记得多"。一个能记住你 3 年工作习惯的 Agent，和一个每次从零开始的 Agent，差距不是一点点。
**3. 安全和信任会成为增长瓶颈**
Agent 知道你越多，你能从它身上获得的价值越大。但你愿意让它知道多少？这个张力会一直存在。未来的 Agent 需要的不只是技术上的安全机制，还有用户能理解和信任的透明度。
**4. 多 Agent 协作是下一站**
Hermes 的 Subagent 是多 Agent 的雏形 — 主 Agent 派Subagent 并行干活。但更远的未来是多 Agent 之间的协作和专业化 — 一个 Agent 专精代码审查，另一个专精部署，第三个专精监控，它们之间通过标准协议通信。
> **核心建议**
>
> 安全不是一个你"做一次就完"的事情，是一个持续的意识。核心原则：**不信任，要验证。** 定期审查 Agent 自动创建的 Skill，用 Docker 后端做隔离，给 Telegram/Discord 配好配对授权，敏感操作用 local 后端的命令审批。做到这四点，你的 Agent 就是一个安全的工作伙伴，而不是一个定时炸弹。
---
全书写到这里。我们从一个问题开始 — "你需要的不是更聪明的 AI，是一个会记住你的 AI" — 到一个能审查代码、监控信息、检查服务健康的 24/7 Agent，再到安全边界的思考。
你的"幼犬"已经可以独立执行任务了。接下来的日子，和它一起工作、一起成长。用得越多，它越懂你。这不是承诺，是机制。