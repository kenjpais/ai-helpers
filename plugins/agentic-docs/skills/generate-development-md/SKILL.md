---
name: generate-development-md
description: "Generate DEVELOPMENT.md file for agentic documentation"
trigger: /generate-development-md
---

# Generate DEVELOPMENT.md Skill

## Purpose

Generate the `agentic/DEVELOPMENT.md` file that documents the development environment setup, build process, and workflow.

## Input

- Repository path (required)
- Existing agentic/ directory structure (must exist)

## Output

- `agentic/DEVELOPMENT.md` file
- Logging of data sources used
- Line count verification

## Data Sources

This skill reads from the following repository files:
- README.md (setup instructions)
- Makefile (build commands)
- CONTRIBUTING.md (development workflow)
- .devcontainer/ or .github/codespaces/ (container configs)
- Package files (go.mod, package.json, requirements.txt, Cargo.toml)
- Build scripts (build.sh, scripts/build/)
- Environment files (.env.example)

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

**Log**: "Reading development-related files..."

Read the following files:
- README.md
- Makefile
- CONTRIBUTING.md
- Package management files (go.mod, package.json, etc.)
- Build scripts
- Container configs

### 3. Generate DEVELOPMENT.md Content

**Prompt**:
```
Based on the repository build and development setup:

Generate agentic/DEVELOPMENT.md covering:

1. **Prerequisites**
   - Required tools and versions (Go, Node.js, Python, etc.)
   - System dependencies
   - Environment requirements

2. **Local Setup**
   - Clone and initial setup steps
   - Dependency installation
   - Configuration files
   - Environment variables

3. **Build Commands**
   - Local binary build
   - Container image build
   - Cross-compilation (if applicable)
   - Build flags and options

4. **Development Workflow**
   - Code → Test → Lint → Commit cycle
   - Hot reload/watch mode (if available)
   - Development server
   - Debugging setup

5. **Common Tasks**
   - Adding new dependencies
   - Updating dependencies
   - Running linters
   - Code formatting

6. **Troubleshooting**
   - Common build errors
   - Dependency issues
   - Environment problems

Use clear, actionable instructions. Target ~280 lines.

Data sources: README.md, Makefile, package files
```

### 4. Write File

Write generated content to `agentic/DEVELOPMENT.md`

**Log**:
- File created: `agentic/DEVELOPMENT.md`
- Lines generated: [count]
- Data sources used: [list]

### 5. Validate Output

Check that:
- File was created successfully
- Content is not empty
- Build commands are present
- Prerequisites section exists

## Logging

Every run must log:
- **Timestamp**: ISO 8601 format
- **Data sources**: List of files read
- **Lines generated**: Final line count
- **Tools used**: read, write
- **Skill invoked**: generate-development-md
- **Duration**: Time taken in seconds

## Error Handling

- If agentic/ directory doesn't exist: Fail with clear error message
- If Makefile is missing: Warn and infer from package files
- If no build instructions found: Generate minimal template

## Success Criteria

- ✅ agentic/DEVELOPMENT.md created
- ✅ File contains 100-400 lines
- ✅ All sections present (Prerequisites, Setup, Build, Workflow, Tasks, Troubleshooting)
- ✅ Build commands extracted from Makefile
- ✅ Dependencies listed from package files
- ✅ Data sources logged
