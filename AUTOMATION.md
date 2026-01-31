# AI Insights 自动化流程说明

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI 内容自动化生产系统                         │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────────────┐         ┌──────────────────────┐
    │  content-forge-ai    │         │     ai-insights      │
    │  (内容生成源)         │         │    (网站展示)         │
    └──────────────────────┘         └──────────────────────┘
              │                               │
              │                               │
    ┌─────────▼─────────┐         ┌──────────▼──────────┐
    │  每日 3 次 (6/12/18  │         │   每天 1 次 (8:00)  │
    │  北京时间)          │         │    北京时间          │
    └────────────────────┘         └─────────────────────┘
              │                               │
    ┌─────────▼─────────┐         ┌──────────▼──────────┐
    │ GitHub Actions:    │         │ GitHub Actions:      │
    │ daily-digest.yml   │────────▶│ sync-content.yml     │
    │                    │ 同步    │                      │
    │ 生成 AI 每日简报   │────────▶│ 转换 + 同步到 Hugo   │
    └────────────────────┘         └─────────────────────┘
                                             │
                                   ┌─────────▼─────────┐
                                   │ GitHub Actions:    │
                                   │ hugo.yml           │
                                   │                    │
                                   │ 构建 + 部署到       │
                                   │ GitHub Pages       │
                                   └───────────────────┘
```

## 工作流程

### 1. 内容生成 (content-forge-ai)

**仓库**: `devfoxaicn/content-forge-ai`

**GitHub Actions**: `.github/workflows/daily-digest.yml`

**触发条件**:
- 每天 3 次: 6:00, 12:00, 18:00 (北京时间)
- 手动触发

**功能**:
- 自动抓取 AI 领域最新资讯
- 生成每日简报 Markdown 文件
- 保存到 `data/daily/YYYYMMDD/digest/`

**需要配置的 Secrets**:
```yaml
ZHIPUAI_API_KEY: xxx  # 智谱 AI 密钥
NEWSAPI_KEY: xxx      # NewsAPI 密钥
TAVILY_API_KEY: xxx   # Tavily 搜索密钥
```

### 2. 内容同步 (ai-insights)

**仓库**: `Ming-H/ai-insights`

**GitHub Actions**: `.github/workflows/sync-content.yml`

**触发条件**:
- 每天 3 次 (对应 content-forge-ai 更新时间):
  - 07:30 (北京时间) - 同步早间内容
  - 13:00 (北京时间) - 同步中午内容
  - 19:00 (北京时间) - 同步晚间内容
- 手动触发

**功能**:
- 从 content-forge-ai 拉取最新内容
- 使用 `scripts/sync_content.py` 转换为 Hugo 格式
- 提交到 content/ 目录
- 触发构建流程

**需要配置**:
- 确保 `devfoxaicn/content-forge-ai` 仓库可访问
  - 如果是公开仓库: 使用默认 GITHUB_TOKEN
  - 如果是私有仓库: 需要配置 PAT Token

### 3. 网站构建部署 (ai-insights)

**GitHub Actions**: `.github/workflows/hugo.yml`

**触发条件**:
- 代码推送到 main 分支
- 手动触发

**功能**:
- 使用 Hugo 构建静态网站
- 部署到 GitHub Pages

## 本地开发

### 同步最新内容

```bash
# 同步所有内容
python scripts/sync_content.py --all

# 只同步每日简报
python scripts/sync_content.py --daily

# 只同步系列文章
python scripts/sync_content.py --series
```

### 本地预览

```bash
# 启动本地服务器
hugo server --buildDrafts

# 访问 http://localhost:1313
```

### 生产构建

```bash
# 构建网站
hugo --minify

# 构建输出在 public/ 目录
```

## 故障排查

### 1. 内容同步失败

**检查点**:
```bash
# 检查 content-forge-ai 仓库是否可访问
curl -I https://api.github.com/repos/devfoxaicn/content-forge-ai

# 检查数据目录是否存在
ls -la /path/to/content-forge-ai/data/daily/

# 手动运行同步脚本测试
python scripts/sync_content.py --daily
```

### 2. GitHub Actions 失败

**检查点**:
- GitHub Actions 日志
- Secrets 是否正确配置
- 仓库权限设置

### 3. 网站构建失败

**检查点**:
```bash
# 本地测试构建
hugo --minify

# 检查主题是否正确初始化
git submodule update --init --recursive
```

## 时间线

| 时间 (北京时间) | 事件 |
|----------------|------|
| 06:00 | content-forge-ai 生成早间简报 |
| 07:30 | ai-insights 同步早间内容 |
| 07:35 | ai-insights 构建部署 |
| 12:00 | content-forge-ai 生成午间简报 |
| 13:00 | ai-insights 同步午间内容 |
| 13:05 | ai-insights 构建部署 |
| 18:00 | content-forge-ai 生成晚间简报 |
| 19:00 | ai-insights 同步晚间内容 |
| 19:05 | ai-insights 构建部署 |

## 需要确保的配置

### GitHub Secrets

**content-forge-ai**:
- `ZHIPUAI_API_KEY`
- `NEWSAPI_KEY`
- `TAVILY_API_KEY`

**ai-insights** (如果 content-forge-ai 是私有的):
- `CONTENT_FORGE_AI_TOKEN` (PAT with repo access)

### 仓库权限

- ai-insights 需要读取 content-forge-ai 的权限
- 如果是私有仓库，需要配置协作关系或 PAT Token

### GitHub Pages 设置

- Source: GitHub Actions
- Branch: main
