---
name: generate-core-beliefs-md
description: "Generate core-beliefs.md file for agentic documentation"
trigger: /generate-core-beliefs-md
---

# Generate Core Beliefs Skill

## Purpose

Generate the `agentic/design-docs/core-beliefs.md` file documenting the fundamental operating principles and philosophy of the project.

## Data Sources

- README.md (mission/vision)
- CONTRIBUTING.md (contribution philosophy)
- docs/design/ or docs/architecture/ (design principles)
- Code comments (package-level documentation)
- Commit messages (design rationale)

## Content Sections

1. **Core Principles** - Fundamental beliefs guiding development
2. **Design Values** - What the project optimizes for
3. **Trade-offs** - Explicit choices and their rationale
4. **Non-Goals** - What the project explicitly does NOT do
5. **Philosophy Evolution** - How principles have changed over time

**Target**: ~200 lines

**Critical**: This file is essential for understanding WHY decisions are made.

## Logging

- Skill: generate-core-beliefs-md
- Data sources: README.md, docs/design/, code comments
- Lines generated: [count]
