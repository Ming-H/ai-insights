# AI Insights — 内容迁移指南 (Migration Guide)

> 版本: 1.0.0
> 最后更新: 2026-04-21
> 源项目: DevFox Site (devfox.ai) — Next.js 14
> 目标项目: AI Insights (ai-insights.devfox.ai) — Hugo + Congo

---

## 1. 迁移概述

### 1.1 迁移背景

DevFox Site 正在从「个人博客站」改造为「品牌官网」。Blog、Books、Gallery 等内容消费型页面与品牌官网的营销定位不匹配，需要迁移至 AI Insights（Hugo 静态站）统一管理。

### 1.2 迁移范围

| 内容类型 | 当前路径 | 迁移目标 | 优先级 |
|---------|---------|---------|--------|
| Blog 文章 | `/blog` + `/blog/[slug]` | AI Insights `/blog` | P0 |
| Books 读书笔记 | `/books` + `/books/[slug]` | AI Insights `/books` | P0 |
| Gallery 灵感图集 | `/inspiration` | AI Insights `/gallery` | P1 |
| 每日简报 | 已在 AI Insights | — (无变化) | — |
| 系列文章 | 已在 AI Insights | — (无变化) | — |

### 1.3 迁移原则

1. **内容不丢失** — 所有现有内容完整迁移，URL 通过重定向保持可访问
2. **用户体验连续** — 旧 URL 自动重定向到新地址，无死链
3. **SEO 可持续** — 使用 301 重定向传递权重，保持 sitemap 更新
4. **架构独立** — 两个项目独立部署、独立维护，通过导航链接互联

---

## 2. 迁移策略

### 2.1 总体方案

```
DevFox Site (Next.js)                    AI Insights (Hugo)
┌─────────────────────┐                 ┌─────────────────────────┐
│ /                    │                 │ /                       │
│ /services/*          │                 │ /daily/                 │
│ /cases/*             │   Blog/Books    │ /series/                │
│ /about               │ ──────────────→ │ /blog/     [NEW]        │
│ /contact             │   Gallery       │ /books/    [NEW]        │
│                      │ ──────────────→ │ /gallery/  [NEW]        │
│ /blog     → redirect │                 │ /about/                │
│ /books    → redirect │                 └─────────────────────────┘
│ /inspiration → redirect│
└─────────────────────┘
```

### 2.2 迁移步骤

#### Phase 1: AI Insights 准备 (1 周)

1. **扩展 Hugo 内容类型**
   - 新增 `blog` content type
   - 新增 `books` content type
   - 新增 `gallery` content type
   - 配置 hugo.toml 菜单

2. **创建模板**
   - `layouts/blog/list.html` — Blog 列表页
   - `layouts/blog/single.html` — Blog 文章详情页
   - `layouts/books/list.html` — Books 列表页
   - `layouts/books/single.html` — Books 详情页
   - `layouts/gallery/list.html` — Gallery 展示页
   - 创建对应的 partials

3. **样式适配**
   - 确保新内容类型符合 Congo 主题风格
   - 适配深色/浅色模式

#### Phase 2: 内容迁移 (1 周)

1. **Blog 文章迁移**
   - 从 DevFox Site 的 `content/blog/` 提取 Markdown 文件
   - 转换 Front Matter 格式（Next.js → Hugo）
   - 写入 AI Insights `content/blog/`

2. **Books 迁移**
   - 从 DevFox Site 的数据源提取 Books 数据
   - 转换为 Hugo Markdown 格式
   - 写入 AI Insights `content/books/`

3. **Gallery 迁移**
   - 从 DevFox Site 的 `data/inspiration.json` 提取图片数据
   - 创建 Hugo content entries
   - 确保图片资源正确引用（R2 URL）

#### Phase 3: DevFox Site 改造 (1 周)

1. **移除旧页面**
   - 删除 `/blog`、`/books`、`/inspiration` 路由
   - 删除对应的 loader 和组件

2. **添加重定向**
   - 在 `next.config.mjs` 中配置 redirects
   - 或在 `vercel.json` 中配置

3. **更新导航**
   - Navbar 中移除 Blog/Books/Gallery
   - 添加 "AI Insights" 外链

4. **更新首页**
   - 移除 Blog/Books/Gallery 的 preview sections
   - 添加品牌官网内容

---

## 3. 内容映射关系

### 3.1 Blog 文章

#### DevFox Site 格式 (Source)

```markdown
---
title: "文章标题"
date: "2026-01-15"
tags: ["AI", "Agent"]
description: "文章摘要"
---

文章正文 Markdown...
```

#### AI Insights 格式 (Target)

```markdown
---
title: "文章标题"
date: 2026-01-15
draft: false
tags: ["AI", "Agent"]
categories: ["Blog"]
description: "文章摘要"
author: "DevFox"
showDate: true
showReadingTime: true
---

文章正文 Markdown...
```

#### 字段映射

| DevFox Site 字段 | AI Insights 字段 | 转换规则 |
|-----------------|-----------------|---------|
| `title` | `title` | 直接映射 |
| `date` | `date` | 格式统一为 `YYYY-MM-DD` |
| `tags` | `tags` | 直接映射 |
| `description` | `description` | 直接映射 |
| — | `draft` | 默认 `false` |
| — | `categories` | 固定为 `["Blog"]` |
| — | `author` | 固定为 `"DevFox"` |
| `slug` (文件名) | 文件名 | `YYYY-MM-DD-slug.md` |
| 正文 | 正文 | 直接复制，注意图片路径 |

### 3.2 Books 读书笔记

#### DevFox Site 格式 (Source)

```typescript
// 来自 lib/book-loader.ts
{
  title: "书名",
  slug: "book-slug",
  subtitle: "副标题",
  readingTime: "15 分钟",
  content: "Markdown 正文",
  // ... 其他元数据
}
```

#### AI Insights 格式 (Target)

```markdown
---
title: "书名 — 副标题"
date: 2026-01-15
draft: false
tags: ["读书笔记", "AI"]
categories: ["Books"]
description: "书籍摘要和读后感"
author: "DevFox"
bookTitle: "书名"
bookAuthor: "作者"
readingTime: 15
showDate: true
showReadingTime: true
type: books
---

读书笔记正文 Markdown...
```

#### 字段映射

| DevFox Site 字段 | AI Insights 字段 | 转换规则 |
|-----------------|-----------------|---------|
| `title` | `title` | 直接映射 |
| `slug` | 文件名 | `YYYY-MM-DD-slug.md` |
| `subtitle` | `description` | 作为描述 |
| `readingTime` | `readingTime` | 提取数字 |
| `content` | 正文 | 直接复制 |
| — | `type` | 固定为 `books` |
| — | `categories` | 固定为 `["Books"]` |

### 3.3 Gallery 灵感图集

#### DevFox Site 格式 (Source)

```json
// data/inspiration.json
{
  "items": [
    {
      "index": 1,
      "filename": "image_001.jpg",
      "source": "collection",
      "collection_dir": "awesome-collection",
      "prompt": "提示词...",
      "tags": ["landscape", "nature"]
    }
  ]
}
```

#### AI Insights 格式 (Target)

**方案 A: 单页 Gallery（推荐）**

创建 `content/gallery/_index.md`，通过 JavaScript 动态加载 JSON 数据:

```markdown
---
title: "灵感图集"
date: 2026-01-15
draft: false
description: "AI 生成的灵感图片集合"
type: gallery
layout: gallery
---
```

配合自定义模板 `layouts/gallery/list.html`，前端 JS 加载 R2 图片资源。

**方案 B: 每张图片独立 content**

不推荐，因为图片数量可能很大，管理成本高。

---

## 4. URL 重定向规划

### 4.1 重定向规则

| 旧 URL (DevFox Site) | 新 URL (AI Insights) | 类型 |
|---------------------|---------------------|------|
| `/blog` | `https://ai-insights.devfox.ai/blog/` | 301 |
| `/blog/[slug]` | `https://ai-insights.devfox.ai/blog/[slug]/` | 301 |
| `/books` | `https://ai-insights.devfox.ai/books/` | 301 |
| `/books/[slug]` | `https://ai-insights.devfox.ai/books/[slug]/` | 301 |
| `/inspiration` | `https://ai-insights.devfox.ai/gallery/` | 301 |

### 4.2 Next.js Redirects 配置

在 `next.config.mjs` 中添加:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  async redirects() {
    const AI_INSIGHTS_BASE = 'https://ai-insights.devfox.ai';
    
    return [
      // Blog 重定向
      {
        source: '/blog',
        destination: `${AI_INSIGHTS_BASE}/blog/`,
        permanent: true,
      },
      {
        source: '/blog/:slug',
        destination: `${AI_INSIGHTS_BASE}/blog/:slug/`,
        permanent: true,
      },
      // Books 重定向
      {
        source: '/books',
        destination: `${AI_INSIGHTS_BASE}/books/`,
        permanent: true,
      },
      {
        source: '/books/:slug',
        destination: `${AI_INSIGHTS_BASE}/books/:slug/`,
        permanent: true,
      },
      // Gallery 重定向
      {
        source: '/inspiration',
        destination: `${AI_INSIGHTS_BASE}/gallery/`,
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
```

### 4.3 Vercel Redirects 配置 (备选)

如果使用 `vercel.json`:

```json
{
  "redirects": [
    {
      "source": "/blog",
      "destination": "https://ai-insights.devfox.ai/blog/",
      "statusCode": 301
    },
    {
      "source": "/blog/:slug*",
      "destination": "https://ai-insights.devfox.ai/blog/:slug*/",
      "statusCode": 301
    },
    {
      "source": "/books",
      "destination": "https://ai-insights.devfox.ai/books/",
      "statusCode": 301
    },
    {
      "source": "/books/:slug*",
      "destination": "https://ai-insights.devfox.ai/books/:slug*/",
      "statusCode": 301
    },
    {
      "source": "/inspiration",
      "destination": "https://ai-insights.devfox.ai/gallery/",
      "statusCode": 301
    }
  ]
}
```

---

## 5. 模板设计说明

### 5.1 Blog 模板

#### 列表页 (`layouts/blog/list.html`)

```
┌─────────────────────────────────────┐
│ [Header]                            │
├─────────────────────────────────────┤
│                                     │
│  Blog                               │
│  技术文章与思考                        │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 文章标题                      │   │
│  │ 2026-01-15 · 5 min · #AI    │   │
│  │ 文章摘要...                   │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ 文章标题                      │   │
│  │ 2026-01-10 · 8 min · #Agent │   │
│  │ 文章摘要...                   │   │
│  └─────────────────────────────┘   │
│  ...                                │
│                                     │
│  [Pagination]                       │
├─────────────────────────────────────┤
│ [Footer]                            │
└─────────────────────────────────────┘
```

#### 详情页 (`layouts/blog/single.html`)

```
┌─────────────────────────────────────┐
│ [Header]                            │
├─────────────────────────────────────┤
│                                     │
│  ← 返回 Blog                        │
│                                     │
│  文章标题 (h1)                       │
│  2026-01-15 · 5 min · #AI #Agent   │
│                                     │
│  ─────────────────────────          │
│                                     │
│  文章正文...                         │
│                                     │
│  ─────────────────────────          │
│  ← 上一篇        下一篇 →           │
│                                     │
├─────────────────────────────────────┤
│ [Footer]                            │
└─────────────────────────────────────┘
```

### 5.2 Books 模板

#### 列表页 (`layouts/books/list.html`)

```
┌─────────────────────────────────────┐
│ [Header]                            │
├─────────────────────────────────────┤
│                                     │
│  Books                              │
│  读书笔记与知识提炼                    │
│                                     │
│  ┌──────────┐ ┌──────────┐         │
│  │ 书名      │ │ 书名      │         │
│  │ 副标题    │ │ 副标题    │         │
│  │ 15 min   │ │ 20 min   │         │
│  └──────────┘ └──────────┘         │
│  ...                                │
│                                     │
├─────────────────────────────────────┤
│ [Footer]                            │
└─────────────────────────────────────┘
```

### 5.3 Gallery 模板

#### 展示页 (`layouts/gallery/list.html`)

```
┌─────────────────────────────────────┐
│ [Header]                            │
├─────────────────────────────────────┤
│                                     │
│  Gallery                            │
│  AI 生成的灵感图集                    │
│                                     │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐          │
│  │   │ │   │ │   │ │   │          │
│  └───┘ └───┘ └───┘ └───┘          │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐          │
│  │   │ │   │ │   │ │   │          │
│  └───┘ └───┘ └───┘ └───┘          │
│  ...                                │
│                                     │
│  [Load More]                        │
├─────────────────────────────────────┤
│ [Footer]                            │
└─────────────────────────────────────┘
```

- 图片采用瀑布流或网格布局
- 点击图片打开大图（Lightbox）
- 支持懒加载

### 5.4 共享样式

所有新增模板应:
- 使用 Congo 主题的基础布局
- 保持与现有 `daily/` 和 `series/` 模板一致的样式风格
- 响应式设计适配移动端
- 支持深色/浅色模式

---

## 6. 导航结构变化

### 6.1 AI Insights 导航 (更新后)

**当前导航**:
```
首页 | 每日简报 | 系列文章 | 关于
```

**迁移后导航**:
```
首页 | 每日简报 | 系列文章 | Blog | Books | Gallery | 关于
```

### 6.2 hugo.toml 菜单配置

```toml
[[menu.main]]
  name = "首页"
  weight = 1
  url = "/"

[[menu.main]]
  name = "每日简报"
  weight = 2
  url = "/daily/"

[[menu.main]]
  name = "系列文章"
  weight = 3
  url = "/series/"

[[menu.main]]
  name = "Blog"
  weight = 4
  url = "/blog/"

[[menu.main]]
  name = "Books"
  weight = 5
  url = "/books/"

[[menu.main]]
  name = "Gallery"
  weight = 6
  url = "/gallery/"

[[menu.main]]
  name = "关于"
  weight = 7
  url = "/about/"
```

### 6.3 DevFox Site 导航 (更新后)

**当前导航**:
```
DevFox AI | Blog | Books | Gallery | Projects | About
```

**改造后导航**:
```
DevFox Logo | Services ▼ | Cases | About | Contact | [AI Insights →]
```

### 6.4 跨站链接

两个站点之间通过以下方式互联:

**DevFox Site → AI Insights**:
- Navbar 中 "AI Insights" 外链按钮
- Footer 中 "Blog / Books / Gallery" 链接指向 AI Insights
- 首页可选的 "最新文章" 区域链接到 AI Insights

**AI Insights → DevFox Site**:
- About 页面中的个人介绍链接到 devfox.ai
- Header/Foot 中的 "DevFox" 品牌链接
- 导航中可选的 "服务" 外链

---

## 7. 迁移脚本

### 7.1 Blog 迁移脚本示例

```python
#!/usr/bin/env python3
"""将 DevFox Site 的 Blog 文章迁移到 AI Insights Hugo 站点"""

import re
from pathlib import Path
from datetime import datetime

# 路径配置
DEVFOX_BLOG_DIR = Path("../devfox-site/content/blog")
AI_INSIGHTS_BLOG_DIR = Path("content/blog")

def convert_front_matter(source_fm: dict, filename: str) -> dict:
    """转换 Front Matter 格式"""
    target_fm = {
        "title": source_fm.get("title", ""),
        "date": source_fm.get("date", ""),
        "draft": False,
        "tags": source_fm.get("tags", []),
        "categories": ["Blog"],
        "description": source_fm.get("description", ""),
        "author": "DevFox",
        "showDate": True,
        "showReadingTime": True,
    }
    return target_fm

def migrate_blog():
    """执行 Blog 迁移"""
    AI_INSIGHTS_BLOG_DIR.mkdir(parents=True, exist_ok=True)
    
    for md_file in DEVFOX_BLOG_DIR.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        
        # 解析 Front Matter
        fm_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        if not fm_match:
            print(f"⚠️ 跳过无 Front Matter 的文件: {md_file.name}")
            continue
        
        # 转换并写入
        # ... (具体转换逻辑)
        
        target = AI_INSIGHTS_BLOG_DIR / md_file.name
        target.write_text(converted_content, encoding="utf-8")
        print(f"✅ 迁移: {md_file.name}")

if __name__ == "__main__":
    migrate_blog()
```

---

## 8. 注意事项

### 8.1 SEO 相关

1. **301 重定向生效时间** — 搜索引擎需要数周才能完全识别 301 重定向
2. **Sitemap 更新** — DevFox Site 移除旧页面后更新 sitemap.xml；AI Insights 添加新页面后更新 sitemap
3. **robots.txt** — 确保两个站点的 robots.txt 正确配置
4. **Google Search Console** — 在迁移后提交新的 sitemap，监控索引变化

### 8.2 性能相关

1. **图片资源** — Gallery 的图片仍使用 R2 存储，不随 Hugo 站点一起部署
2. **构建时间** — AI Insights 内容增多后注意 Hugo 构建时间
3. **CDN 缓存** — 迁移后清除 Vercel 和 GitHub Pages 的 CDN 缓存

### 8.3 维护相关

1. **内容同步** — 新的 Blog 文章直接在 AI Insights 仓库创建，不再经过 DevFox Site
2. **自动发布** — Blog/Books 可参考现有的 content-sync 机制
3. **评论系统** — 如需要，可在 AI Insights 中集成 Giscus/Disqus

---

## 9. 回滚方案

如果迁移后出现严重问题:

1. **DevFox Site** — 移除 redirects 配置，恢复旧页面路由
2. **AI Insights** — 删除新增的 content types 和模板
3. **DNS** — 无 DNS 变更，不需要回滚

### 回滚检查清单

- [ ] 确认 DevFox Site 旧页面可以正常访问
- [ ] 确认 AI Insights 旧内容（daily/series）未受影响
- [ ] 确认重定向配置已移除
- [ ] 确认导航链接已恢复
