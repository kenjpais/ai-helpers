---
name: generate-architecture-md
description: "Generate ARCHITECTURE.md file for agentic documentation"
trigger: /generate-architecture-md
---

# Generate ARCHITECTURE.md Skill

## Purpose

Generate the `ARCHITECTURE.md` file documenting the system structure with file paths and code organization.

## Data Sources

- Repository directory structure
- Main code directories (pkg/, cmd/, internal/, src/)
- Configuration directories (config/, manifests/, deploy/)
- Documentation structure (docs/, agentic/)
- Build configuration (Makefile, build scripts)

## Content Sections

1. **Repository Structure** - Directory tree with descriptions
2. **Code Organization** - How code is organized by layer/domain
3. **Configuration Files** - Config locations and purposes
4. **Build Artifacts** - Generated files and build outputs
5. **Documentation** - Where to find different doc types
6. **Key Files** - Important entry points and their locations

**Target**: ~200 lines

**Purpose**: Help agents understand WHERE things are in the codebase.

## Logging

- Skill: generate-architecture-md
- Data sources: repository structure, directory analysis
- Directories documented: [count]
- Lines generated: [count]
