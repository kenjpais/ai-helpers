---
name: generate-data-flow-md
description: "Generate data-flow.md file for agentic documentation"
trigger: /generate-data-flow-md
---

# Generate Data Flow Skill

## Purpose

Generate the `agentic/design-docs/data-flow.md` file documenting how data moves through the system.

## Data Sources

- API definitions (OpenAPI, protobuf)
- Handler code (HTTP handlers, controllers)
- Data models (structs, schemas)
- Queue/messaging code
- Database schemas
- Cache layer code

## Content Sections

1. **Data Flow Overview** - High-level data movement
2. **Request/Response Flow** - HTTP/RPC request handling
3. **Data Transformations** - Format conversions and validations
4. **Data Storage** - Persistence layer interactions
5. **Event Flow** - Asynchronous data movement
6. **Data Pipeline** - Batch processing flows

**Target**: ~220 lines

## Logging

- Skill: generate-data-flow-md
- Data sources: API definitions, handler code, data models
- Lines generated: [count]
