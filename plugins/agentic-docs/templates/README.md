# Agentic Documentation Templates

This directory contains templates for generating agentic documentation files. Templates are based on the structure from [PR #437](https://github.com/openshift-eng/ai-helpers/pull/437) but adapted for generic repositories.

## Template Structure

Templates use placeholder syntax: `{PLACEHOLDER_NAME}`

### Core Templates

| Template | Purpose | Target Lines |
|----------|---------|--------------|
| AGENTS.md.template | Navigation index (entry point) | 80-150 |
| ARCHITECTURE.md.template | Repository structure and code organization | ~200 |
| DESIGN.md.template | Design philosophy and principles | ~350 |
| DEVELOPMENT.md.template | Development setup and workflow | ~280 |
| TESTING.md.template | Test strategy and execution | ~320 |

### Design Principles from PR #437

1. **Concise and scannable**: Use ASCII diagrams, tables, code blocks
2. **Progressive disclosure**: Link to detailed docs, don't duplicate
3. **Retrieval-first**: Emphasize reading docs over relying on training data
4. **Task-oriented**: "Task → Docs Quick Map" sections
5. **AI-optimized**: Compressed documentation index with tree structure

### Placeholder Categories

**Repository Metadata**:
- `{REPOSITORY_NAME}` - Full repository name (e.g., openshift/installer)
- `{PROJECT_NAME}` - Project display name
- `{LAST_UPDATED}` - ISO date

**Metrics**:
- `{TOTAL_FILES}` - Number of documentation files
- `{TOTAL_LINES}` - Total lines of documentation
- `{CURRENT_LINES}` - Current file line count
- `{CURRENT_COVERAGE}` - Test coverage percentage

**Content**:
- `{ARCHITECTURE_SUMMARY}` - Brief architecture overview
- `{BUILD_COMMAND}` - Primary build command from Makefile
- `{TEST_COMMAND}` - Primary test command
- `{REPO_TREE}` - Repository directory tree (ASCII format)
- `{CODE_ORGANIZATION_DETAILS}` - How code is organized

**Languages & Tools**:
- `{LANGUAGE}` - Primary language (Go, Python, etc.)
- `{DEBUGGER}` - Language-appropriate debugger

## Usage in Generation Skills

File-specific generation skills (e.g., `generate-development-md`) should:

1. **Read template**:
   ```bash
   template=$(cat templates/DEVELOPMENT.md.template)
   ```

2. **Extract data from repository**:
   - Parse Makefile for build commands
   - Analyze directory structure
   - Read package files for dependencies

3. **Replace placeholders**:
   ```bash
   content=$(echo "$template" | sed "s/{PROJECT_NAME}/$project_name/g")
   ```

4. **Write output**:
   ```bash
   echo "$content" > agentic/DEVELOPMENT.md
   ```

## Template Formatting

### ASCII Diagrams

Use fenced code blocks with `text` language tag:

```text
[Root]|./agentic|{TOTAL_FILES} files
|
|design-docs:{core-beliefs.md,...}
|domain:{glossary.md,...}
```

### Tables

Use Markdown tables for quick reference:

```markdown
| Task | Read These |
|------|------------|
| Build | DEVELOPMENT.md |
```

### Code Blocks

Include language tags for syntax highlighting:

```bash
make build
```

## Extending Templates

To add a new template:

1. Create `{FILENAME}.template` in this directory
2. Use `{PLACEHOLDER}` syntax for dynamic content
3. Document placeholders in this README
4. Create corresponding generation skill in `skills/generate-{filename}/`
5. Update orchestrator in `skills/create/SKILL.md`

## Reference

Based on templates from:
- https://github.com/openshift-eng/ai-helpers/pull/437
- https://github.com/Prashanth684/agentic-docs-guide/blob/main/AGENTIC_DOCS_FRAMEWORK.md
