---
name: generate-component-architecture-md
description: "Generate component-architecture.md file for agentic documentation"
trigger: /generate-component-architecture-md
---

# Generate Component Architecture Skill

## Purpose

Generate the `agentic/design-docs/component-architecture.md` file documenting how the system is decomposed into components.

## Data Sources

- Code structure (pkg/, cmd/, internal/)
- Component interfaces
- Dependency graph
- API definitions
- docs/architecture/ files

## Content Sections

1. **Component Overview** - High-level component breakdown
2. **Component Responsibilities** - What each component does
3. **Component Interactions** - How components communicate
4. **Dependency Graph** - Component dependencies
5. **Extension Points** - How to extend components
6. **Component Lifecycle** - Initialization, runtime, shutdown

**Target**: ~250 lines

## Logging

- Skill: generate-component-architecture-md
- Data sources: code structure, interfaces, dependency graph
- Components identified: [count]
- Lines generated: [count]
