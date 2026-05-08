---
name: agentic-docs:create-knowledge-graph
description: "Generate knowledge graph from existing agentic documentation"
trigger: /agentic-docs:create-knowledge-graph
---

# Agentic-Docs: Create Knowledge Graph

**Trigger**: `/agentic-docs:create-knowledge-graph`  
**Purpose**: Generate NetworkX knowledge graph from existing agentic documentation

## Overview

Generates a knowledge graph from agentic documentation that has already been created. This command is **completely decoupled** from `/agentic-docs:create` and must be run separately.

**Important**: This command requires that `/agentic-docs:create` has already been run successfully.

## Input

**Repository Path** (optional - defaults to current directory)

```
/agentic-docs:create-knowledge-graph [<repo-path>]
```

## Prerequisites

The following directory must exist:
```
<repo>/
└── agentic/
    ├── DESIGN.md
    ├── DEVELOPMENT.md
    ├── TESTING.md
    ├── RELIABILITY.md
    ├── SECURITY.md
    ├── design-docs/
    ├── domain/
    └── ... (complete agentic structure)
```

If agentic documentation doesn't exist:
```
❌ Error: Agentic Documentation Not Found

Directory agentic/ does not exist in this repository.

Please run /agentic-docs:create first to generate documentation.

Aborting knowledge graph generation.
```

## Workflow

### Phase 0: Initialize

**Output to CLI**:
```
📊 Agentic-Docs: Create Knowledge Graph
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Repository: /path/to/repo
Timestamp: 2026-05-08 15:00:12
Source: agentic/ directory
Log file: logs/agentic-docs-kg-2026-05-08-15-00-12.log
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 1: Verify Agentic Documentation

**Action**: Check that agentic documentation exists

**Validation**:
- `agentic/` directory exists
- Required files present (DESIGN.md, DEVELOPMENT.md, etc.)
- AGENTS.md exists

**Output to CLI**:
```
Phase 1: Verify Agentic Documentation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ agentic/ directory found
✓ 6 required files present
✓ AGENTS.md entry point found
✓ 25 documentation files discovered
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 2: Read Documentation Files

**Action**: Read all agentic documentation files

**Data Sources**:
- AGENTS.md
- ARCHITECTURE.md
- agentic/DESIGN.md
- agentic/DEVELOPMENT.md
- agentic/TESTING.md
- agentic/RELIABILITY.md
- agentic/SECURITY.md
- agentic/QUALITY_SCORE.md
- agentic/design-docs/**/*.md
- agentic/domain/**/*.md
- All markdown files in agentic/

**Tools Used**:
- `read` - Read markdown files
- `bash` - Find all .md files

**Output to CLI**:
```
Phase 2: Read Documentation Files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Read 25 markdown files
✓ Total content: 12,450 lines
✓ Files by type:
  • Core docs: 6 files
  • Component docs: 12 files
  • Concept docs: 5 files
  • Index files: 2 files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 3: Extract Links and Relationships

**Action**: Parse markdown to extract links between documents

**What is extracted**:
- Markdown links: `[text](path.md)`
- Cross-references between components
- Concept → Component relationships
- Navigation paths

**Output to CLI**:
```
Phase 3: Extract Links and Relationships
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Extracted 147 links
✓ Identified 45 relationships
✓ Cross-references:
  • Component → Component: 23
  • Component → Concept: 18
  • Concept → Concept: 4
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 4: Build NetworkX Graph

**Action**: Create NetworkX graph with embedded content

**Graph Structure**:
```python
{
  "directed": true,
  "multigraph": false,
  "graph": {},
  "nodes": [
    {
      "id": "AGENTS.md",
      "type": "entry_point",
      "content": "... (full markdown content embedded) ...",
      "path": "AGENTS.md",
      "lines": 145
    },
    {
      "id": "agentic/DESIGN.md",
      "type": "core_doc",
      "content": "... (full markdown content embedded) ...",
      "path": "agentic/DESIGN.md",
      "lines": 350
    },
    {
      "id": "component:api-server",
      "type": "component",
      "content": "... (full markdown content embedded) ...",
      "path": "agentic/design-docs/components/api-server.md",
      "lines": 98
    },
    ...
  ],
  "links": [
    {
      "source": "AGENTS.md",
      "target": "agentic/DESIGN.md",
      "rel": "links_to"
    },
    {
      "source": "agentic/DESIGN.md",
      "target": "component:api-server",
      "rel": "references"
    },
    ...
  ]
}
```

**Critical Requirement**: All document content must be **embedded in graph nodes** (no file I/O during retrieval).

**Output to CLI**:
```
Phase 4: Build NetworkX Graph
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Created graph with 25 nodes
✓ Added 147 edges
✓ Embedded content in all nodes
✓ Graph properties:
  • Entry points: 1 (AGENTS.md)
  • Core docs: 6 nodes
  • Component docs: 12 nodes
  • Concept docs: 5 nodes
  • Index docs: 2 nodes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 5: Validate Graph

**Action**: Validate graph structure and properties

**Validations**:
- Graph is connected (all nodes reachable from AGENTS.md)
- All content embedded (no missing content)
- No broken links
- Maximum navigation depth ≤ 3 hops

**Output to CLI**:
```
Phase 5: Validate Graph
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Graph is connected (all nodes reachable)
✓ All content embedded (no missing data)
✓ No broken links
✓ Maximum depth: 2 hops (within limit)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 6: Save Graph

**Action**: Save graph to JSON file

**Output Location**:
```
<repo>/
└── agentic/
    └── knowledge-graph/
        └── graph.json
```

**File Format**: NetworkX node-link JSON format

**Output to CLI**:
```
Phase 6: Save Graph
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Created agentic/knowledge-graph/ directory
✓ Saved graph to agentic/knowledge-graph/graph.json
✓ File size: 2.4 MB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Final Summary

**Output to CLI**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Knowledge Graph Generated Successfully

Repository: /path/to/repo
Duration: 15.3s

Graph Statistics:
  Nodes: 25
  Edges: 147
  Entry points: 1
  Maximum depth: 2 hops
  Content embedded: 12,450 lines

Output: agentic/knowledge-graph/graph.json (2.4 MB)

Tools Used:
  • read (25 invocations)
  • bash (3 invocations)
  • write (1 invocation)

Data Sources:
  • agentic/ directory (25 files)

Log file: logs/agentic-docs-kg-2026-05-08-15-00-12.log
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next steps:
  • Use /ask skill for graph-based queries
  • Knowledge graph enables faster retrieval
  • Graph supports ≤3 hop navigation
```

## Decoupling from /agentic-docs:create

**Key Design Principle**: This command is completely independent of `/agentic-docs:create`.

**Reasons for Separation**:
1. **Modularity**: Knowledge graph generation is optional
2. **Performance**: Some users may not need graph-based retrieval
3. **Flexibility**: Users can regenerate graph without regenerating docs
4. **Testing**: Easier to test graph generation independently

**Usage Pattern**:
```bash
# First, generate documentation
/agentic-docs:create

# Later, optionally generate knowledge graph
/agentic-docs:create-knowledge-graph

# Regenerate graph without regenerating docs
/agentic-docs:create-knowledge-graph
```

## Error Handling

If documentation doesn't exist:
```
❌ Error: Missing Agentic Documentation

Required: agentic/ directory with complete documentation
Found: Directory does not exist

Please run /agentic-docs:create first.
```

If graph already exists:
```
⚠️  Warning: Knowledge Graph Exists

Existing: agentic/knowledge-graph/graph.json
Action: Will be overwritten

Continue? (y/n)
```
