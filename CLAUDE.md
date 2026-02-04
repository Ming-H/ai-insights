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

Content is synced from `devfoxaicn/content-forge-ai` via Python scripts. The paths in `scripts/sync_content.py` are hardcoded for local development and are automatically patched by GitHub Actions in CI.

```bash
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
│ daily-digest.yml    │──────────▶│ sync-content.yml    │
│ Runs: 6/12/18 Beijing│  sync    │ Runs: 7:30/13/19    │
│ repository_dispatch │──(instant)│ or on push          │
│ Generates:          │──────────▶│ Converts + commits  │
│ - Daily digests     │           │ - Hugo front matter │
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
- 07:30: ai-insights syncs and builds
- 12:00: content-forge-ai generates midday digest
- 13:00: ai-insights syncs and builds
- 18:00: content-forge-ai generates evening digest
- 19:00: ai-insights syncs and builds

## Directory Structure

```
ai-insights/
├── content/                    # Hugo content (Markdown)
│   ├── _index.md              # Homepage content
│   ├── about.md               # About page
│   ├── daily/                 # Daily AI digests (YYYY-MM-DD-index.md)
│   └── series/                # Technical article series
│       ├── LLM_series/        # LLM series articles
│       └── ML_series/         # ML series articles
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
```yaml
---
title: "Article Title"
date: YYYY-MM-DD
draft: false
tags: ['tag1', 'tag2']
categories: ['category']
description: "Description"
---
```

**Series articles have additional fields**:
```yaml
series: "series_name"
episode: 1
difficulty: "中级"
estimatedWords: 2000
```

## Git Workflow

- Main branch: `main`
- Push to main triggers GitHub Actions build/deploy via `hugo.yml`
- Content sync runs automatically via cron in `sync-content.yml`
- Commits from sync workflow use `[skip ci]` to avoid build loops

## Important Notes

- **Congo theme is a git submodule** - run `git submodule update --init --recursive` if missing
- **Content paths in sync script** are hardcoded for local development; GitHub Actions patches them via sed
  - **Critical**: When editing `.github/workflows/sync-content.yml`, sed commands MUST use double quotes for variable expansion: `sed -i "s|...|$GITHUB_WORKSPACE/...|g"` (single quotes will not expand the variable)
- **No automated tests** - manual verification via `hugo server --buildDrafts`
- **Content language** is Chinese (zh-cn); preserve technical terms in English
