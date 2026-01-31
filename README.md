# AI Insights Blog

基于 Hugo 的 GitHub Pages 博客，展示 ContentForge AI 生成的每日 AI 简报和技术文章系列。

## 项目结构

```
ai-insights/
├── content/                    # Hugo 内容目录
│   ├── daily/                  # 每日 AI 简报
│   ├── series/                 # 系列技术文章
│   │   ├── LLM_series/        # LLM 系列（100期）
│   │   └── ML_series/         # ML 系列（100期）
│   ├── about.md               # 关于页面
│   └── _index.md              # 首页
├── scripts/
│   └── sync_content.py        # 内容同步脚本
├── .github/workflows/
│   ├── hugo.yml               # GitHub Pages 部署
│   └── sync-content.yml       # 自动同步内容
├── themes/paper/              # Paper 主题
└── hugo.toml                 # Hugo 配置
```

## 本地开发

### 安装 Hugo

```bash
# macOS
brew install hugo

# 其他平台
# 访问 https://gohugo.io/installation/
```

### 同步内容

```bash
# 同步全部内容
python scripts/sync_content.py --all

# 只同步每日简报
python scripts/sync_content.py --daily

# 只同步系列文章
python scripts/sync_content.py --series
```

### 启动开发服务器

```bash
hugo server --buildDrafts
# 访问 http://localhost:1313
```

### 构建生产版本

```bash
hugo --minify
# 输出到 public/ 目录
```

## 部署到 GitHub Pages

1. 在 GitHub 创建新仓库 `ai-insights`
2. 推送代码到仓库

```bash
git init
git add .
git commit -m "Initial commit"

git remote add origin https://github.com/Ming-H/ai-insights.git
git branch -M main
git push -u origin main
```

3. 在仓库设置中启用 GitHub Pages
   - Settings → Pages
   - Source: GitHub Actions

## 内容来源

- **每日简报**: 由 [ContentForge AI](https://github.com/Ming-H/content-forge-ai) 自动生成
- **系列文章**: LLM 系列和 ML 系列，各 100 期

## 技术栈

- **Hugo**: 静态网站生成器
- **Paper 主题**: 简洁现代的博客主题
- **GitHub Pages**: 网站托管
- **GitHub Actions**: 自动部署和内容同步

## 自定义配置

### 修改主题配置

编辑 `hugo.toml` 中的 `[params]` 部分：

```toml
[params]
  color = 'linen'           # 主题颜色
  avatar = 'avatar-url'     # 头像
  name = 'Your Name'        # 名称
  bio = 'Your Bio'          # 简介
```

### 添加菜单项

在 `hugo.toml` 的 `[[menu.main]]` 部分添加：

```toml
[[menu.main]]
  url = "/your-page/"
  name = "页面名称"
  weight = 5
```

## 许可证

MIT License
