#!/usr/bin/env python3
"""
内容同步脚本 - 从 content-forge-ai 同步内容到 Hugo 博客

用法:
    python scripts/sync_content.py --daily    # 同步每日简报
    python scripts/sync_content.py --series   # 同步系列文章
    python scripts/sync_content.py --all      # 同步全部内容
"""

# 配置路径（支持通过环境变量覆盖，方便 GitHub Actions / 不同环境）
# 注意：必须在最前面导入并设置环境变量，确保在导入其他模块前生效
import os
from pathlib import Path

# 从环境变量获取路径
CONTENT_FORGE_AI_PATH = Path(os.getenv("CONTENT_FORGE_AI_PATH", "/Users/z/Documents/work/content-forge-ai"))
HUGO_CONTENT_PATH = Path(os.getenv("HUGO_CONTENT_PATH", "/Users/z/Documents/work/ai-insights/content"))

import sys
import json
import shutil
import argparse
import re
from datetime import datetime


def parse_date_from_digest_filename(filename):
    """从 digest 文件名解析日期"""
    match = re.search(r'(\d{8})', filename)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, "%Y%m%d")
    return None


def sync_daily_digest():
    """同步每日简报到 Hugo"""
    print("🔄 开始同步每日简报...")

    daily_path = CONTENT_FORGE_AI_PATH / "data" / "daily"
    hugo_daily_path = HUGO_CONTENT_PATH / "daily"

    # 创建 Hugo daily 目录
    hugo_daily_path.mkdir(parents=True, exist_ok=True)

    # 遍历所有日期目录
    for date_dir in sorted(daily_path.iterdir()):
        if not date_dir.is_dir() or date_dir.name.startswith('.'):
            continue

        digest_dir = date_dir / "digest"
        if not digest_dir.exists():
            continue

        # 查找最新的 digest 文件
        md_files = sorted(digest_dir.glob("digest_*.md"), reverse=True)
        if not md_files:
            continue

        latest_md = md_files[0]
        json_file = latest_md.with_suffix('.json')

        # 解析日期
        pub_date = parse_date_from_digest_filename(latest_md.name)
        if not pub_date:
            print(f"⚠️  无法解析日期: {latest_md.name}")
            continue

        # 读取 Markdown 内容
        with open(latest_md, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # 提取标题（第一行）
        lines = md_content.split('\n')
        title = lines[0].replace('#', '').strip()
        content = '\n'.join(lines[1:]).strip()

        # 读取 JSON 元数据（如果存在）
        tags = ["AI简报"]
        categories = ["每日热点"]
        description = ""

        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                digest_data = json.load(f)

            # 提取核心洞察作为标签
            if 'core_insights' in digest_data:
                tags.extend([f"洞察: {insight[:20]}" for insight in digest_data['core_insights'][:3]])

            # 提取分类
            if 'categories' in digest_data:
                def _cat_to_str(cat):
                    if isinstance(cat, dict):
                        # 优先 name，其次 id，最后转字符串
                        return cat.get('name') or cat.get('id') or str(cat)
                    return str(cat)

                categories.extend([_cat_to_str(c) for c in digest_data['categories']])

        # 生成 Hugo front matter
        front_matter = f"""---
title: "{title}"
date: {pub_date.strftime('%Y-%m-%d')}
draft: false
tags: {tags}
categories: {categories}
description: "AI每日热点 · {pub_date.strftime('%Y年%m月%d日')}"
---

"""

        # 写入 Hugo 文件
        hugo_filename = hugo_daily_path / f"{pub_date.strftime('%Y-%m-%d')}-index.md"
        with open(hugo_filename, 'w', encoding='utf-8') as f:
            f.write(front_matter + content)

        print(f"✅ 已同步: {hugo_filename.name}")

    print("✨ 每日简报同步完成!")


def sync_series_articles():
    """同步系列文章到 Hugo"""
    print("🔄 开始同步系列文章...")

    series_path = CONTENT_FORGE_AI_PATH / "data" / "series"
    hugo_series_path = HUGO_CONTENT_PATH / "series"

    # 创建 Hugo series 目录
    hugo_series_path.mkdir(parents=True, exist_ok=True)

    # 遍历所有系列 (LLM_series, ML_series)
    for category_dir in sorted(series_path.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith('.'):
            continue

        category_name = category_dir.name
        print(f"📚 处理分类: {category_name}")

        # 遍历该分类下的所有 series (series_1_llm_foundation, ml_series_1_ml_foundation, etc.)
        for series_dir in sorted(category_dir.iterdir()):
            if not series_dir.is_dir():
                continue
            if not (series_dir.name.startswith('series_') or series_dir.name.startswith('ml_series_')
                    or series_dir.name.startswith('va_series_') or series_dir.name.startswith('ae_series_')):
                continue

            # 获取系列名称
            series_name = series_dir.name
            print(f"  📖 处理系列: {series_name}")

            # 遍历该系列的所有 episode
            for episode_dir in sorted(series_dir.iterdir()):
                if not episode_dir.is_dir() or not episode_dir.name.startswith('episode_'):
                    continue

                # 查找文章和元数据
                md_files = list(episode_dir.glob("*_article.md"))
                metadata_file = episode_dir / "episode_metadata.json"

                if not md_files or not metadata_file.exists():
                    continue

                article_file = md_files[0]

                # 读取元数据
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

                # 跳过未完成的文章
                if metadata.get('status') != 'completed':
                    continue

                # 读取文章内容
                with open(article_file, 'r', encoding='utf-8') as f:
                    article_content = f.read()

                # 提取标题
                lines = article_content.split('\n')
                title = lines[0].replace('#', '').strip() if lines[0].startswith('#') else metadata['title']
                content = '\n'.join(lines[1:]).strip() if lines[0].startswith('#') else article_content

                # 解析日期
                pub_date = datetime.strptime(metadata['completed_at'], "%Y-%m-%d")

                # 获取 episode 编号
                episode_num = metadata['episode']
                episode_str = f"{episode_num:03d}"

                # 生成 Hugo front matter
                front_matter = f"""---
title: "{metadata['title']}"
date: {pub_date.strftime('%Y-%m-%d')}
draft: false
tags: {metadata['keywords']}
categories: ["{series_name}", "{metadata.get('difficulty', '中级')}"]
description: "{metadata.get('description', metadata['title'])}"
series: "{series_name}"
episode: {episode_num}
difficulty: "{metadata.get('difficulty', '中级')}"
estimatedWords: {metadata.get('estimated_words', 0)}
---

"""

                # 创建系列子目录
                series_subdir = hugo_series_path / series_name
                series_subdir.mkdir(exist_ok=True)

                # 写入 Hugo 文件
                hugo_filename = series_subdir / f"{episode_str}-{metadata['title'].replace(' ', '-').replace('/', '-')}.md"
                with open(hugo_filename, 'w', encoding='utf-8') as f:
                    f.write(front_matter + content)

                print(f"  ✅ 已同步: Episode {episode_num} - {metadata['title']}")

    print("✨ 系列文章同步完成!")


def create_about_page():
    """创建关于页面"""
    about_content = """---
title: "关于 AI Insights"
date: 2024-01-01
draft: false
---

# AI Insights

欢迎来到 **AI Insights** - 一个由 AI 驱动的多平台内容自动化生产工厂。

## 我们提供什么

### 📰 每日 AI 简报

每天更新，汇集全球 AI 领域最新动态，包括：
- 产业动态
- 学术前沿
- 技术创新
- 产品工具
- 行业应用

### 📚 系列技术文章

系统化的 AI 技术学习资源，涵盖：
- **LLM 系列** - 大语言模型原理与应用（100期）
- **ML 系列** - 机器学习与深度学习（100期）

## 技术栈

本博客基于以下技术构建：

- **Hugo** - 静态网站生成器
- **Paper 主题** - 简洁现代的博客主题
- **ContentForge AI** - 内容自动化生产系统
- **GitHub Pages** - 网站托管

## 联系我们

- GitHub: [Ming-H/content-forge-ai](https://github.com/Ming-H/content-forge-ai)
- 官网: [DevFox AI](https://www.devfoxai.cn/)

---

*由 ContentForge AI 自动生成与维护*
"""

    about_path = HUGO_CONTENT_PATH / "about.md"
    with open(about_path, 'w', encoding='utf-8') as f:
        f.write(about_content)

    print("✅ 关于页面已创建")


def create_index_page():
    """创建首页"""
    index_content = """---
title: "AI Insights"
---

欢迎来到 **AI Insights**!

这里汇集了最新的 AI 行业动态和深度的技术文章。

## 最新内容

### 📰 每日简报

每天更新，汇集全球 AI 领域最新动态。

[查看全部简报](/daily/)

### 📚 系列文章

系统化的 AI 技术学习资源。

- **[LLM 系列](/series/llm_series/)** - 大语言模型原理与应用（100期）
- **[ML 系列](/series/ml_series/)** - 机器学习与深度学习（100期）

## 关于

本博客由 [ContentForge AI](https://github.com/Ming-H/content-forge-ai) 自动生成与维护。
"""

    index_path = HUGO_CONTENT_PATH / "_index.md"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)

    print("✅ 首页已创建")


def main():
    parser = argparse.ArgumentParser(description='同步 content-forge-ai 内容到 Hugo 博客')
    parser.add_argument('--daily', action='store_true', help='同步每日简报')
    parser.add_argument('--series', action='store_true', help='同步系列文章')
    parser.add_argument('--all', action='store_true', help='同步全部内容')
    parser.add_argument('--pages', action='store_true', help='创建基础页面')

    args = parser.parse_args()

    if args.pages or args.all:
        create_index_page()
        create_about_page()

    if args.daily or args.all:
        sync_daily_digest()

    if args.series or args.all:
        sync_series_articles()

    if not any([args.daily, args.series, args.all, args.pages]):
        parser.print_help()


if __name__ == "__main__":
    main()
