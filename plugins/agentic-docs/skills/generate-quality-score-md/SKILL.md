---
name: generate-quality-score-md
description: "Generate QUALITY_SCORE.md file for agentic documentation"
trigger: /generate-quality-score-md
---

# Generate QUALITY_SCORE.md Skill

## Purpose

Generate the `agentic/QUALITY_SCORE.md` file that calculates and tracks documentation quality metrics.

## Data Sources

- All agentic/ documentation files
- Repository structure (component count)
- Git metadata (last updated dates)
- Link validation results
- Line count analysis

## Content Sections

1. **Overall Score** - Total quality score (0-100)
2. **Coverage Metrics** - Component coverage percentage (40 points)
3. **Freshness Metrics** - Documentation age (20 points)
4. **Completeness Metrics** - Required files present (20 points)
5. **Linkage Metrics** - Broken links count (10 points)
6. **Navigation Metrics** - Max hop depth (10 points)
7. **Improvement Recommendations** - Actionable next steps

**Target**: ~150 lines

## Logging

- Skill: generate-quality-score-md
- Data sources: agentic/ files, git metadata
- Quality score calculated: [score]/100
- Lines generated: [count]
