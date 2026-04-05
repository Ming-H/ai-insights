---
title: "系列文章"
date: 2024-01-01
description: "系统化的 AI 学习资源，从基础到前沿，构建完整知识体系"
---

<style>
.series-landing {
  max-width: 100%;
}

/* Hero Section */
.series-hero-section {
  margin-bottom: 4rem;
  padding-bottom: 2.5rem;
  border-bottom: 1px solid var(--color-border);
}
.series-hero-section h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  letter-spacing: -0.02em;
  line-height: 1.15;
}
.series-hero-subtitle {
  font-size: 1.125rem;
  color: var(--color-text-secondary);
  line-height: 1.7;
  max-width: 600px;
}
.series-hero-stats {
  display: flex;
  gap: 2rem;
  margin-top: 1.5rem;
}
.series-hero-stat {
  display: flex;
  flex-direction: column;
}
.series-hero-stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.2;
}
.series-hero-stat-label {
  font-size: 0.8125rem;
  color: var(--color-text-tertiary);
  margin-top: 0.125rem;
}

/* Series Block */
.series-block {
  margin-bottom: 3.5rem;
}
.series-block-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}
.series-block-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  flex-shrink: 0;
}
.series-block-title {
  font-size: 1.375rem;
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
}
.series-block-desc {
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
  margin-bottom: 1.25rem;
  line-height: 1.6;
}

/* Card Grid */
.series-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.875rem;
}
.series-card {
  display: block;
  position: relative;
  padding: 1.25rem 1.375rem;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-bg-primary);
  transition: all 200ms ease;
  text-decoration: none;
  overflow: hidden;
}
.series-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  border-radius: 12px 12px 0 0;
  opacity: 0;
  transition: opacity 200ms ease;
}
.series-card:hover {
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}
.series-card:hover::before {
  opacity: 1;
}

/* Accent colors per series */
.series-block--llm .series-block-icon { background: #FEF3C7; }
.series-block--llm .series-block-icon { color: #D97706; }
.series-block--llm .series-card::before { background: linear-gradient(90deg, #F59E0B, #D97706); }
.series-block--llm .series-card:hover { border-color: #FDE68A; }

.series-block--ml .series-block-icon { background: #D1FAE5; color: #059669; }
.series-block--ml .series-card::before { background: linear-gradient(90deg, #10B981, #059669); }
.series-block--ml .series-card:hover { border-color: #A7F3D0; }

.series-block--va .series-block-icon { background: #EDE9FE; color: #7C3AED; }
.series-block--va .series-card::before { background: linear-gradient(90deg, #8B5CF6, #7C3AED); }
.series-block--va .series-card:hover { border-color: #C4B5FD; }

.series-block--ae .series-block-icon { background: #DBEAFE; color: #2563EB; }
.series-block--ae .series-card::before { background: linear-gradient(90deg, #3B82F6, #1D4ED8); }
.series-block--ae .series-card:hover { border-color: #93C5FD; }

/* Dark mode adjustments */
[data-theme="dark"] .series-block--llm .series-block-icon { background: #78350F; color: #FCD34D; }
[data-theme="dark"] .series-block--llm .series-card:hover { border-color: #92400E; }
[data-theme="dark"] .series-block--ml .series-block-icon { background: #064E3B; color: #6EE7B7; }
[data-theme="dark"] .series-block--ml .series-card:hover { border-color: #065F46; }
[data-theme="dark"] .series-block--va .series-block-icon { background: #4C1D95; color: #C4B5FD; }
[data-theme="dark"] .series-block--va .series-card:hover { border-color: #5B21B6; }
[data-theme="dark"] .series-block--ae .series-block-icon { background: #1E3A8A; color: #93C5FD; }
[data-theme="dark"] .series-block--ae .series-card:hover { border-color: #1E40AF; }

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    /* inherits dark vars */
  }
  :root:not([data-theme="light"]) .series-block--llm .series-block-icon { background: #78350F; color: #FCD34D; }
  :root:not([data-theme="light"]) .series-block--llm .series-card:hover { border-color: #92400E; }
  :root:not([data-theme="light"]) .series-block--ml .series-block-icon { background: #064E3B; color: #6EE7B7; }
  :root:not([data-theme="light"]) .series-block--ml .series-card:hover { border-color: #065F46; }
  :root:not([data-theme="light"]) .series-block--va .series-block-icon { background: #4C1D95; color: #C4B5FD; }
  :root:not([data-theme="light"]) .series-block--va .series-card:hover { border-color: #5B21B6; }
  :root:not([data-theme="light"]) .series-block--ae .series-block-icon { background: #1E3A8A; color: #93C5FD; }
  :root:not([data-theme="light"]) .series-block--ae .series-card:hover { border-color: #1E40AF; }
}

.series-card-num {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-tertiary);
  margin-bottom: 0.375rem;
  letter-spacing: 0.02em;
}
.series-card-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.375rem;
  line-height: 1.35;
}
.series-card-tags {
  font-size: 0.8125rem;
  color: var(--color-text-tertiary);
  line-height: 1.4;
}

/* Responsive */
@media (max-width: 768px) {
  .series-hero-section h1 { font-size: 1.875rem; }
  .series-hero-stats { gap: 1.25rem; flex-wrap: wrap; }
  .series-card-grid { grid-template-columns: 1fr; }
}
</style>

<div class="series-landing">

<!-- Hero -->
<div class="series-hero-section">
  <h1>系列文章</h1>
  <p class="series-hero-subtitle">系统化的 AI 学习资源，从基础到前沿，构建完整知识体系。每个系列覆盖一个核心领域，由浅入深。</p>
  <div class="series-hero-stats">
    <div class="series-hero-stat">
      <span class="series-hero-stat-value">4</span>
      <span class="series-hero-stat-label">大系列</span>
    </div>
    <div class="series-hero-stat">
      <span class="series-hero-stat-value">290+</span>
      <span class="series-hero-stat-label">计划篇数</span>
    </div>
    <div class="series-hero-stat">
      <span class="series-hero-stat-value">206</span>
      <span class="series-hero-stat-label">已发布</span>
    </div>
  </div>
</div>

<!-- LLM Series -->
<div class="series-block series-block--llm">
  <div class="series-block-header">
    <div class="series-block-icon">⚡</div>
    <h2 class="series-block-title">LLM 系列</h2>
  </div>
  <p class="series-block-desc">大语言模型原理与应用，100 期从架构到应用的全链路深度解读。85 篇已发布。</p>
  <div class="series-card-grid">
    <a href="series_1_llm_foundation/" class="series-card">
      <div class="series-card-num">01</div>
      <div class="series-card-title">LLM 基础</div>
      <div class="series-card-tags">Transformers · Tokenizer · Pre-training</div>
    </a>
    <a href="series_2_rag_technique/" class="series-card">
      <div class="series-card-num">02</div>
      <div class="series-card-title">RAG 实战</div>
      <div class="series-card-tags">检索增强生成 · 向量数据库 · Knowledge Graph</div>
    </a>
    <a href="series_3_agent_development/" class="series-card">
      <div class="series-card-num">03</div>
      <div class="series-card-title">Agent 开发</div>
      <div class="series-card-tags">AI 智能体 · 多Agent协作 · AutoGPT</div>
    </a>
    <a href="series_4_prompt_engineering/" class="series-card">
      <div class="series-card-num">04</div>
      <div class="series-card-title">Prompt 工程</div>
      <div class="series-card-tags">提示词优化 · CoT · Few-shot Learning</div>
    </a>
    <a href="series_5_model_deployment/" class="series-card">
      <div class="series-card-num">05</div>
      <div class="series-card-title">模型部署</div>
      <div class="series-card-tags">推理优化 · 量化 · vLLM · TensorRT</div>
    </a>
    <a href="series_6_multimodal_frontier/" class="series-card">
      <div class="series-card-num">06</div>
      <div class="series-card-title">多模态前沿</div>
      <div class="series-card-tags">视觉理解 · CLIP · DALL-E · Stable Diffusion</div>
    </a>
    <a href="series_7_ai_coding_tools/" class="series-card">
      <div class="series-card-num">07</div>
      <div class="series-card-title">AI 编程工具</div>
      <div class="series-card-tags">Cursor · Copilot · Code Interpreter</div>
    </a>
    <a href="series_8_ai_data_engineering/" class="series-card">
      <div class="series-card-num">08</div>
      <div class="series-card-title">AI 数据工程</div>
      <div class="series-card-tags">数据处理 · RAG数据构建 · 质量控制</div>
    </a>
    <a href="series_9_ai_applications/" class="series-card">
      <div class="series-card-num">09</div>
      <div class="series-card-title">AI 应用场景</div>
      <div class="series-card-tags">行业落地 · 最佳实践 · Case Study</div>
    </a>
    <a href="series_10_ai_infrastructure/" class="series-card">
      <div class="series-card-num">10</div>
      <div class="series-card-title">AI 基础设施</div>
      <div class="series-card-tags">大规模部署 · GPU集群 · 监控运维</div>
    </a>
  </div>
</div>

<!-- ML Series -->
<div class="series-block series-block--ml">
  <div class="series-block-header">
    <div class="series-block-icon">🧠</div>
    <h2 class="series-block-title">ML 系列</h2>
  </div>
  <p class="series-block-desc">机器学习与深度学习，100 期从理论到实践的系统教程。31 篇已发布。</p>
  <div class="series-card-grid">
    <a href="ml_series_1_ml_foundation/" class="series-card">
      <div class="series-card-num">01</div>
      <div class="series-card-title">ML 基础</div>
      <div class="series-card-tags">学习范式 · 模型评估 · 交叉验证</div>
    </a>
    <a href="ml_series_2_deep_learning_foundation/" class="series-card">
      <div class="series-card-num">02</div>
      <div class="series-card-title">深度学习</div>
      <div class="series-card-tags">神经网络 · 反向传播 · 激活函数</div>
    </a>
    <a href="ml_series_3_computer_vision/" class="series-card">
      <div class="series-card-num">03</div>
      <div class="series-card-title">计算机视觉</div>
      <div class="series-card-tags">CNNs · ResNet · YOLO · 图像分割</div>
    </a>
    <a href="ml_series_4_natural_language_processing/" class="series-card">
      <div class="series-card-num">04</div>
      <div class="series-card-title">自然语言处理</div>
      <div class="series-card-tags">Word2Vec · Seq2Seq · Attention机制</div>
    </a>
    <a href="ml_series_5_reinforcement_learning/" class="series-card">
      <div class="series-card-num">05</div>
      <div class="series-card-title">强化学习</div>
      <div class="series-card-tags">RL agents · Q-Learning · Policy Gradient</div>
    </a>
    <a href="ml_series_6_recommender_systems/" class="series-card">
      <div class="series-card-num">06</div>
      <div class="series-card-title">推荐系统</div>
      <div class="series-card-tags">协同过滤 · 矩阵分解 · 深度推荐</div>
    </a>
    <a href="ml_series_7_model_optimization/" class="series-card">
      <div class="series-card-num">07</div>
      <div class="series-card-title">模型优化</div>
      <div class="series-card-tags">超参数调优 · 贝叶斯优化 · AutoML</div>
    </a>
    <a href="ml_series_8_traditional_ml/" class="series-card">
      <div class="series-card-num">08</div>
      <div class="series-card-title">传统 ML</div>
      <div class="series-card-tags">SVM · 决策树 · 随机森林 · XGBoost</div>
    </a>
    <a href="ml_series_9_feature_engineering/" class="series-card">
      <div class="series-card-num">09</div>
      <div class="series-card-title">特征工程</div>
      <div class="series-card-tags">特征选择 · 降维 · 特征交叉</div>
    </a>
    <a href="ml_series_10_advanced_topics/" class="series-card">
      <div class="series-card-num">10</div>
      <div class="series-card-title">高级主题</div>
      <div class="series-card-tags">集成学习 · 模型可解释性 · 迁移学习</div>
    </a>
  </div>
</div>

<!-- Voice Assistant Series -->
<div class="series-block series-block--va">
  <div class="series-block-header">
    <div class="series-block-icon">🎙️</div>
    <h2 class="series-block-title">智能语音助手</h2>
  </div>
  <p class="series-block-desc">语音技术全栈指南，40 期涵盖语音识别、语音合成、对话系统与全栈开发实战。40 篇已发布。</p>
  <div class="series-card-grid">
    <a href="va_series_voice_assistant/" class="series-card">
      <div class="series-card-num">全系列</div>
      <div class="series-card-title">智能语音助手技术全栈指南</div>
      <div class="series-card-tags">语音识别 · 语音合成 · 对话系统 · 全栈开发</div>
    </a>
  </div>
</div>

<!-- Agent Engineering Series -->
<div class="series-block series-block--ae">
  <div class="series-block-header">
    <div class="series-block-icon">🤖</div>
    <h2 class="series-block-title">Agent Engineering</h2>
  </div>
  <p class="series-block-desc">从基础概念到生产部署的 Agent 工程全栈指南，50 期覆盖六大主流框架深度实战。50 篇已发布。</p>
  <div class="series-card-grid">
    <a href="ae_series_1_agent_foundation/" class="series-card">
      <div class="series-card-num">01</div>
      <div class="series-card-title">Agent 工程基础</div>
      <div class="series-card-tags">ReAct · Prompt Chaining · Routing · 并行与分工</div>
    </a>
    <a href="ae_series_2_agent_architecture/" class="series-card">
      <div class="series-card-num">02</div>
      <div class="series-card-title">Agent 架构与工具链</div>
      <div class="series-card-tags">记忆系统 · MCP 协议 · 代码 Agent · 浏览器 Agent</div>
    </a>
    <a href="ae_series_3_multi_agent_systems/" class="series-card">
      <div class="series-card-num">03</div>
      <div class="series-card-title">多 Agent 系统</div>
      <div class="series-card-tags">LangGraph · CrewAI · AutoGen · OpenAI Agents SDK</div>
    </a>
    <a href="ae_series_4_agent_safety_eval/" class="series-card">
      <div class="series-card-num">04</div>
      <div class="series-card-title">评估、安全与可观测</div>
      <div class="series-card-tags">AgentBench · SWE-bench · Prompt Injection 防御</div>
    </a>
    <a href="ae_series_5_agent_production/" class="series-card">
      <div class="series-card-num">05</div>
      <div class="series-card-title">生产化与前沿</div>
      <div class="series-card-tags">部署架构 · CI/CD · 自适应 Agent · 框架对比</div>
    </a>
  </div>
</div>

</div>
