---
name: generate-agents-md
description: "Generate AGENTS.md file for agentic documentation"
trigger: /generate-agents-md
---

# Generate AGENTS.md Skill

## Purpose

Generate the `AGENTS.md` file - the entry point navigation table for AI agents.

## Data Sources

- All agentic/ documentation files (to build index)
- Component list (from agentic/design-docs/components/)
- Concept list (from agentic/domain/concepts/)
- Workflow list (from agentic/domain/workflows/)

## Content Sections

1. **Navigation Table** - Quick links to key documents
2. **Getting Started** - First steps for agents
3. **Core Documentation** - Links to DESIGN, DEVELOPMENT, TESTING, etc.
4. **Components** - List of all components with links
5. **Domain Concepts** - List of concepts with links
6. **Workflows** - List of workflows with links

**Target**: 80-150 lines (CRITICAL: Must stay within line budget)

**Critical**: This is the entry point - must be concise and well-organized.

## Line Budget Enforcement

AGENTS.md MUST be 80-150 lines. If generated content exceeds 150 lines:
1. Condense component/concept lists
2. Remove redundant descriptions
3. Use compact table format
4. Prioritize most important links

## Logging

- Skill: generate-agents-md
- Data sources: agentic/ file index
- Components linked: [count]
- Concepts linked: [count]
- Lines generated: [count]
- **Line budget status**: [PASS/FAIL]
