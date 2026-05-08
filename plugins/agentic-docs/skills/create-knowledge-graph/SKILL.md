---
name: agentic-docs:create-knowledge-graph
description: "Generate NetworkX knowledge graph from existing agentic documentation"
trigger: /agentic-docs:create-knowledge-graph
---

# Agentic-Docs: Create Knowledge Graph

**Trigger**: `/agentic-docs:create-knowledge-graph`  
**Purpose**: Generate a NetworkX knowledge graph from existing agentic documentation

## Overview

This skill reads existing agentic documentation files and generates a knowledge graph that represents the relationships between concepts, components, and architecture elements within the repository.

## Prerequisites

**REQUIRED**: Must be run AFTER `/agentic-docs:create` has successfully generated the agentic documentation.

## Input

**Repository Path** (optional - defaults to current directory)

```
/agentic-docs:create-knowledge-graph [<repo-path>]
```

## Workflow

### Phase 1: Validate Prerequisites

**Actions**:
1. Check that `agentic/` directory exists
2. Verify required documentation files are present
3. Validate documentation structure

**Exit Early**: If prerequisites not met, report error and exit

### Phase 2: Extract Knowledge

**Actions**:
1. Read all documentation files from `agentic/` directory
2. Extract entities (components, concepts, APIs, etc.)
3. Identify relationships between entities
4. Build NetworkX graph structure

### Phase 3: Generate Output

**Actions**:
1. Create `agentic/knowledge-graph/` directory
2. Serialize graph to `graph.json`
3. Generate graph statistics

**Output to CLI**:
```
✅ Knowledge Graph Created
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Output: agentic/knowledge-graph/graph.json
Nodes: <count>
Edges: <count>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Output Format

The generated `graph.json` contains:
- **Nodes**: Entities from the documentation (components, concepts, APIs)
- **Edges**: Relationships between entities (depends-on, implements, calls, etc.)
- **Metadata**: Node and edge attributes

## Error Handling

**Missing Documentation**: If `agentic/` directory doesn't exist or is incomplete, report clear error message directing user to run `/agentic-docs:create` first.

**Invalid Structure**: If documentation exists but has invalid structure, report specific validation errors.
