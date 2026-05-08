---
name: generate-glossary-md
description: "Generate glossary.md file for agentic documentation"
trigger: /generate-glossary-md
---

# Generate Glossary Skill

## Purpose

Generate the `agentic/domain/glossary.md` file defining domain-specific terminology.

## Data Sources

- Code comments (type/struct documentation)
- API definitions (field descriptions)
- CRD specs (Kubernetes custom resources)
- README.md (terminology sections)
- docs/ (glossary or terminology files)
- Variable/type names (infer common terms)

## Content Sections

1. **Glossary Index** - Alphabetical term list
2. **Core Concepts** - Fundamental domain terms
3. **Technical Terms** - Implementation-specific terminology
4. **Kubernetes Terms** - K8s-specific vocabulary (if applicable)
5. **Acronyms** - Abbreviations and their meanings
6. **Related Concepts** - Cross-references between terms

**Target**: ~150 lines

## Logging

- Skill: generate-glossary-md
- Data sources: code comments, API definitions, CRDs
- Terms extracted: [count]
- Lines generated: [count]
