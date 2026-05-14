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

### 3. Load Template

Read the DEVELOPMENT.md template:

```bash
template_path="templates/DEVELOPMENT.md.template"
```

**Template Structure** (from PR #437):
- Prerequisites section
- Repository structure with ASCII tree
- Development workflow
- Common tasks
- Build & release process
- Project-specific notes

### 4. Extract Repository Data

**From Makefile**:
- Build commands (`make build`, `make test`, `make lint`)
- Test commands
- Format commands
- Install/update dependency commands

**From Package Files**:
- Language version (go.mod, package.json, pyproject.toml)
- Dependencies list
- Build tools

**From README.md**:
- Setup instructions
- Prerequisites

**From Build Scripts**:
- Container build commands
- Local build steps

**From CI Configuration**:
- CI build description
- Release process

### 5. Replace Template Placeholders

Replace placeholders in template:

| Placeholder | Source |
|-------------|--------|
| `{PROJECT_NAME}` | Repository name |
| `{REPOSITORY_NAME}` | Full repo path |
| `{PREREQUISITES_LIST}` | Extract from README, package files |
| `{BUILD_COMMAND}` | From Makefile (primary build target) |
| `{BUILD_OUTPUT_PATH}` | Detect from Makefile or infer |
| `{REPO_TREE}` | Generate ASCII tree of repository |
| `{LOCAL_BUILD_COMMAND}` | From Makefile |
| `{TEST_COMMAND}` | From Makefile (test target) |
| `{LOCAL_RUN_INSTRUCTIONS}` | Infer from binary location |
| `{LOG_COMMAND}` | Language-specific log command |
| `{DEBUGGER}` | Language-appropriate debugger |
| `{DEBUG_COMMAND}` | Debugger command |
| `{CODE_ORGANIZATION_DETAILS}` | Analyze directory structure |
| `{ADD_DEPENDENCY_COMMAND}` | Language-specific (go get, npm install, pip install) |
| `{UPDATE_DEPS_COMMAND}` | Language-specific update command |
| `{LINT_COMMAND}` | From Makefile or infer |
| `{FORMAT_COMMAND}` | From Makefile or infer |
| `{LOCAL_BUILD_FULL}` | From Makefile |
| `{CI_BUILD_DESCRIPTION}` | From CI config |
| `{RELEASE_PROCESS}` | From README or CONTRIBUTING |
| `{PROJECT_SPECIFIC_NOTES}` | Repository-specific quirks |

**Template Processing**:
```
1. Read template file
2. Extract all repository data
3. Replace each {PLACEHOLDER} with actual value
4. Generate final DEVELOPMENT.md content
```

**Target**: ~280 lines (as per template)

### 6. Write File

Write generated content to `agentic/DEVELOPMENT.md`

**Log**:
- File created: `agentic/DEVELOPMENT.md`
- Lines generated: [count]
- Data sources used: [list]

### 7. Validate Output

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
