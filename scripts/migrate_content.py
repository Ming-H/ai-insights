#!/usr/bin/env python3
"""
Migrate Blog, Books, and Gallery content from DevFox Site to AI Insights Hugo site.
"""

import json
import re
import shutil
from pathlib import Path
from datetime import datetime

DEVFOX = Path("/Users/z/Documents/work/my-projects/web-apps/devfox-site/content")
AI_INSIGHTS = Path("/Users/z/Documents/work/my-projects/web-apps/ai-insights/content")

BOOK_TITLES = {
    "agent-design-guide": "智能体设计指南",
    "ai-side-income": "AI 副业与赚钱实战",
    "claude-code-tutorial": "Claude Code 从入门到精通",
    "claude-source-analysis": "Claude 源码解析",
    "hermes-agent-tutorial": "Hermes Agent 实用教程",
    "llm-history": "大模型的前世今生",
    "llm-principles": "大语言模型原理",
    "openclaw-tutorial": "OpenClaw 实用教程",
    "vibe-coding-tutorial": "Vibe Coding 实战教程",
}

BOOK_DESCRIPTIONS = {
    "agent-design-guide": "从原理到实战，构建能干活的 AI Agent",
    "ai-side-income": "13 个互联网从业者靠 AI 创造收入的真实路径",
    "claude-code-tutorial": "Anthropic 官方 AI 编程助手完全指南",
    "claude-source-analysis": "从入口到工具调用，拆解 AI 编程助手的内部架构",
    "hermes-agent-tutorial": "驯养一只会自己变聪明的 AI Agent",
    "llm-history": "从 Transformer 到 DeepSeek，一本书读懂大语言模型",
    "llm-principles": "从 Token 到 Transformer，从预训练到对齐——图解式干练讲解",
    "openclaw-tutorial": "从零搭建你的个人 AI 助手",
    "vibe-coding-tutorial": "从\"听说过\"到\"能交付\"的完整指南",
}


def parse_front_matter(content: str) -> tuple[dict, str]:
    """Parse YAML front matter from markdown content."""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    yaml_str = parts[1].strip()
    body = parts[2].strip()

    metadata = {}
    for line in yaml_str.split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            metadata[key] = value

    # Parse tags if present
    tags_match = re.search(r'tags:\s*\[(.*?)\]', yaml_str)
    if tags_match:
        tags_str = tags_match.group(1)
        metadata['tags'] = [t.strip().strip('"').strip("'") for t in tags_str.split(",")]

    return metadata, body


def migrate_blog():
    """Migrate blog articles from DevFox Site."""
    print("=== Migrating Blog Articles ===")

    blog_src = DEVFOX / "blog"
    blog_dst = AI_INSIGHTS / "blog"

    # Create target directory
    blog_dst.mkdir(parents=True, exist_ok=True)

    # Create _index.md for blog section
    blog_index = """---
title: "博客"
description: "AI 技术深度文章与实战经验分享"
draft: false
---

欢迎来到 **AI Insights 博客**！

这里汇集了关于 AI 编程工具、智能体开发、Vibe Coding 等前沿技术的深度文章与实战经验分享。
"""
    (blog_dst / "_index.md").write_text(blog_index, encoding="utf-8")
    print(f"  Created: blog/_index.md")

    # Migrate each blog article
    count = 0
    for md_file in sorted(blog_src.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        metadata, body = parse_front_matter(content)

        title = metadata.get("title", md_file.stem)
        date = metadata.get("date", "2026-01-01")
        if not date:
            date = "2026-01-01"
        excerpt = metadata.get("excerpt", "")
        tags = metadata.get("tags", [])
        published = metadata.get("published", "true")

        # Build Hugo front matter
        draft = "false" if published == "true" else "true"
        tags_str = json.dumps(tags, ensure_ascii=False)
        categories = '["博客"]'

        hugo_content = f"""---
title: "{title}"
date: {date}
draft: {draft}
tags: {tags_str}
categories: {categories}
description: "{excerpt}"
---

{body}"""

        dst_file = blog_dst / md_file.name
        dst_file.write_text(hugo_content, encoding="utf-8")
        count += 1
        print(f"  Migrated: blog/{md_file.name}")

    print(f"  Total: {count} blog articles migrated\n")


def migrate_books():
    """Migrate books from DevFox Site."""
    print("=== Migrating Books ===")

    books_src = DEVFOX / "books"
    books_dst = AI_INSIGHTS / "books"

    # Create target directory
    books_dst.mkdir(parents=True, exist_ok=True)

    # Create _index.md for books section
    books_index = """---
title: "书籍"
description: "深度技术教程与实战指南，从入门到精通"
draft: false
---

欢迎来到 **AI Insights 书架**！

这里汇集了精心编写的 AI 技术书籍与实战指南，涵盖 Agent 开发、AI 编程工具、大语言模型原理等热门领域。

每本书都是从零开始、循序渐进的完整教程，适合不同层次的开发者阅读。
"""
    (books_dst / "_index.md").write_text(books_index, encoding="utf-8")
    print(f"  Created: books/_index.md")

    # Migrate each book
    count = 0
    for book_dir in sorted(books_src.iterdir()):
        if not book_dir.is_dir():
            continue

        slug = book_dir.name
        if slug not in BOOK_TITLES:
            print(f"  Skipping unknown book: {slug}")
            continue

        manuscript = book_dir / "manuscript.md"
        if not manuscript.exists():
            print(f"  Skipping (no manuscript): {slug}")
            continue

        title = BOOK_TITLES[slug]
        description = BOOK_DESCRIPTIONS.get(slug, "")

        # Create book directory
        book_dst = books_dst / slug
        book_dst.mkdir(parents=True, exist_ok=True)

        # Create _index.md for book
        book_index = f"""---
title: "{title}"
date: 2026-04-15
draft: false
description: "{description}"
type: books
---

# {title}

{description}

[开始阅读](./manuscript/)
"""
        (book_dst / "_index.md").write_text(book_index, encoding="utf-8")
        print(f"  Created: books/{slug}/_index.md")

        # Copy manuscript content with Hugo front matter
        content = manuscript.read_text(encoding="utf-8")

        # Parse original front matter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                body = parts[2].strip()
            else:
                body = content
        else:
            body = content

        # Create manuscript page with front matter
        manuscript_page = f"""---
title: "{title} - 全文"
date: 2026-04-15
draft: false
description: "{description}"
type: books
---

{body}"""

        (book_dst / "manuscript.md").write_text(manuscript_page, encoding="utf-8")
        print(f"  Copied: books/{slug}/manuscript.md")

        count += 1

    print(f"  Total: {count} books migrated\n")


def migrate_gallery():
    """Migrate gallery from DevFox Site."""
    print("=== Migrating Gallery ===")

    gallery_src = DEVFOX / "gallery" / "gallery.json"
    gallery_dst = AI_INSIGHTS / "gallery"

    # Create target directories
    gallery_dst.mkdir(parents=True, exist_ok=True)
    items_dst = gallery_dst / "items"
    items_dst.mkdir(parents=True, exist_ok=True)

    # Create _index.md for gallery section
    gallery_index = """---
title: "画廊"
description: "AI 生成的创意作品展示"
draft: false
---

欢迎来到 **AI Insights 画廊**！

这里展示了各种 AI 创意生成作品，包括 3D 城市微缩地图等。
"""
    (gallery_dst / "_index.md").write_text(gallery_index, encoding="utf-8")
    print(f"  Created: gallery/_index.md")

    # Read gallery data
    if not gallery_src.exists():
        print("  No gallery.json found, skipping gallery migration")
        return

    with open(gallery_src, "r", encoding="utf-8") as f:
        gallery_items = json.load(f)

    count = 0
    for item in gallery_items:
        slug = item.get("slug", f"item-{count}")
        title = item.get("title", "Untitled")
        description = item.get("description", "")
        category = item.get("category", "")
        prompt = item.get("prompt", "")
        tool = item.get("tool", "")
        tags = item.get("tags", [])
        cover_image = item.get("coverImage", "")

        tags_str = json.dumps(tags, ensure_ascii=False)

        # Create item page
        item_content = f"""---
title: "{title}"
date: 2026-04-15
draft: false
description: "{description}"
tags: {tags_str}
category: "{category}"
coverImage: "{cover_image}"
tool: "{tool}"
type: gallery
---

# {title}

**分类**: {category}

**工具**: {tool}

**标签**: {', '.join(tags)}

## 提示词

```
{prompt}
```

## 描述

{description}
"""

        item_file = items_dst / f"{slug}.md"
        item_file.write_text(item_content, encoding="utf-8")
        count += 1
        print(f"  Created: gallery/items/{slug}.md")

    print(f"  Total: {count} gallery items migrated\n")


if __name__ == "__main__":
    print("Starting content migration from DevFox Site to AI Insights...\n")
    migrate_blog()
    migrate_books()
    migrate_gallery()
    print("Migration complete!")
