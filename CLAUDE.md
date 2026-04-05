# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Insights is a Hugo-based static site blog (Chinese language) that showcases AI daily digests and technical article series. It is part of a two-repository automated content system:

- **Content Generation**: `Ming-H/content-forge-ai` - generates AI content via scheduled workflows
- **Content Presentation**: This repository (`Ming-H/ai-insights`) - displays content via Hugo + Congo theme

The system uses Python scripts to pull content from the source repo and convert it to Hugo front matter format.

## Development Commands

```bash
# Local development server
hugo server --buildDrafts

# Build production site
hugo --minify

# Build with custom base URL
hugo --baseURL "https://Ming-H.github.io/ai-insights/"
```

## Content Sync Commands

Content is synced from `Ming-H/content-forge-ai` via Python scripts. The script uses environment variables for path configuration:

```bash
# For local development, set these environment variables if paths differ
export CONTENT_FORGE_AI_PATH="/path/to/content-forge-ai"
export HUGO_CONTENT_PATH="./content"

# Sync all content from content-forge-ai
python scripts/sync_content.py --all

# Sync only daily digests
python scripts/sync_content.py --daily

# Sync only series articles
python scripts/sync_content.py --series

# Create/update basic pages (index, about)
python scripts/sync_content.py --pages
```

**Important**: Do not manually edit content in `content/daily/` or `content/series/` as it will be overwritten on sync.

## High-Level Architecture

The system consists of two repositories with automated workflows:

```
content-forge-ai (source)          ai-insights (this repo)
┌─────────────────────┐           ┌─────────────────────┐
│ GitHub Actions      │           │ GitHub Actions      │
│ digest generation   │──────────▶│ sync-content.yml    │
│ Runs: 6/12/18 Beijing│  sync    │ Runs: 6:45/12:45/18:45
│ repository_dispatch │──(instant)│ repository_dispatch │
│ Generates:          │           │ Converts + commits  │
│ - Daily digests     │──────────▶│ - Hugo front matter │
│ - Series articles   │           │ - Triggers hugo.yml │
└─────────────────────┘           └─────────────────────┘
                                          │
                                          ▼
                                   ┌─────────────────────┐
                                   │ GitHub Actions      │
                                   │ hugo.yml            │
                                   │ Builds + deploys to │
                                   │ GitHub Pages        │
                                   └─────────────────────┘
```

**Schedule** (Beijing Time):
- 06:00: content-forge-ai generates morning digest
- 06:45: ai-insights syncs (45min guard for digest completion)
- 12:00: content-forge-ai generates midday digest
- 12:45: ai-insights syncs
- 18:00: content-forge-ai generates evening digest
- 18:45: ai-insights syncs

**Sync Workflow Behavior**:
- The `sync-content.yml` workflow includes a guard step that waits up to 10 minutes for the daily digest to exist
- If the digest is not found after 10 minutes, the sync is skipped (no error)
- Syncs can also be triggered instantly via `repository_dispatch` from content-forge-ai
- Manual trigger available via `workflow_dispatch`

## Directory Structure

```
ai-insights/
├── content/                    # Hugo content (Markdown)
│   ├── _index.md              # Homepage content
│   ├── about.md               # About page
│   ├── daily/                 # Daily AI digests (YYYY-MM-DD-index.md)
│   └── series/                # Technical article series
│       ├── series_1_llm_foundation/      # LLM foundation series
│       ├── series_2_rag_technique/       # RAG technique series
│       ├── series_3_agent_development/   # Agent development series
│       └── ... (multiple series)
├── layouts/                   # Custom Hugo templates (override theme)
│   ├── _default/
│   ├── daily/                 # Custom daily digest templates
│   ├── series/                # Custom series templates
│   └── partials/              # Template partials
├── scripts/
│   └── sync_content.py        # Content sync script (Python 3.10+)
├── .github/workflows/
│   ├── hugo.yml               # Hugo build/deploy to GitHub Pages
│   └── sync-content.yml       # Automated content sync (cron)
├── themes/congo/              # Congo theme (git submodule)
└── hugo.toml                  # Hugo configuration
```

## Key Configuration

**Hugo config** (`hugo.toml`):
- Language: `zh-cn` (Chinese)
- Theme: Congo (`congo`)
- Base URL: `https://Ming-H.github.io/ai-insights/`
- `summaryLength = 0` (full content in summaries)

**Content front matter format** (YAML):

**Daily Digests**:
```yaml
---
title: "AI每日热点 · YYYY年MM月DD日"
date: YYYY-MM-DD
draft: false
tags: ['AI简报', '洞察: insight1', '洞察: insight2']
categories: ['每日热点', 'category1', 'category2']
description: "AI每日热点 · YYYY年MM月DD日"
---
```

**Series Articles**:
```yaml
---
title: "Article Title"
date: YYYY-MM-DD
draft: false
tags: ['keyword1', 'keyword2']
categories: ["series_name", "difficulty"]
description: "Article description"
series: "series_name"
episode: 1
difficulty: "中级"
estimatedWords: 2000
---
```

## Git Workflow

- Main branch: `main`
- Push to main triggers GitHub Actions build/deploy via `hugo.yml`
- Content sync runs automatically via cron in `sync-content.yml`
- Commits from sync workflow use `[skip ci]` to avoid build loops

## Important Notes

- **Congo theme is a git submodule** - run `git submodule update --init --recursive` if missing
- **Content paths in sync script** use environment variables (`CONTENT_FORGE_AI_PATH`, `HUGO_CONTENT_PATH`) for flexibility
- **No automated tests** - manual verification via `hugo server --buildDrafts`
- **Content language** is Chinese (zh-cn); preserve technical terms in English
- **Sync workflow uses guard mechanism** - if daily digest doesn't exist after 10 minutes of polling, sync is skipped (this is expected behavior, not an error)
- **Series article naming**: Files use episode number prefix (e.g., `001-title.md`)
- **Daily digest naming**: Files use date format `YYYY-MM-DD-index.md`
