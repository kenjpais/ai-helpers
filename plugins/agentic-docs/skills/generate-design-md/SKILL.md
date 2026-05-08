---
name: generate-design-md
description: "Generate DESIGN.md file for agentic documentation"
trigger: /generate-design-md
---

# Generate DESIGN.md Skill

## Purpose

Generate the `agentic/DESIGN.md` file that documents the design philosophy and architectural patterns of the repository.

## Input

- Repository path (required)
- Existing agentic/ directory structure (must exist)

## Output

- `agentic/DESIGN.md` file
- Logging of data sources used
- Line count verification

## Data Sources

This skill reads from the following repository files:
- README.md (design overview)
- docs/architecture.md or docs/design.md (if exists)
- CONTRIBUTING.md (design principles)
- Top-level architecture files
- Code structure analysis

## Workflow

### 1. Verify Prerequisites

```bash
# Check that agentic/ directory exists
if [ ! -d "agentic/" ]; then
  echo "ERROR: agentic/ directory not found. Run structure generator first."
  exit 1
fi
```

### 2. Read Data Sources

**Log**: "Reading design-related files..."

Read the following files:
- README.md
- docs/architecture.md (if exists)
- docs/design.md (if exists)
- CONTRIBUTING.md
- High-level code structure (pkg/, cmd/, internal/)

### 3. Generate DESIGN.md Content

**Prompt**:
```
Based on the repository structure and documentation:

Generate agentic/DESIGN.md covering:

1. **Design Philosophy**
   - Core design principles
   - Key architectural decisions
   - Trade-offs and rationale

2. **Architecture Overview**
   - High-level component structure
   - Design patterns used
   - Separation of concerns

3. **Key Abstractions**
   - Main interfaces and contracts
   - Data models
   - Extension points

4. **Design Constraints**
   - Technical constraints
   - Business constraints
   - Scalability considerations

5. **Design Evolution**
   - How the design has evolved
   - Deprecated patterns
   - Future direction

Use clear, concise language. Target ~350 lines.

Data sources: README.md, docs/architecture.md, code structure
```

### 4. Write File

Write generated content to `agentic/DESIGN.md`

**Log**:
- File created: `agentic/DESIGN.md`
- Lines generated: [count]
- Data sources used: [list]

### 5. Validate Output

Check that:
- File was created successfully
- Content is not empty
- File is readable
- Line count is reasonable (100-500 lines)

## Logging

Every run must log:
- **Timestamp**: ISO 8601 format
- **Data sources**: List of files read
- **Lines generated**: Final line count
- **Tools used**: read, write
- **Skill invoked**: generate-design-md
- **Duration**: Time taken in seconds

## Error Handling

- If agentic/ directory doesn't exist: Fail with clear error message
- If README.md is missing: Warn and generate from code analysis only
- If generation fails: Log error and exit with non-zero status

## Success Criteria

- ✅ agentic/DESIGN.md created
- ✅ File contains 100-500 lines
- ✅ All sections present (Design Philosophy, Architecture, Abstractions, Constraints, Evolution)
- ✅ Data sources logged
- ✅ No broken links or references
