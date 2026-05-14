# Agentic-Docs Skills Structure

This document explains the skill organization, template usage, and when to keep skills separate vs consolidate them.

## Skill Directory Structure

```
skills/
├── create/                          # Orchestrator: /agentic-docs:create
│   └── SKILL.md
├── create-knowledge-graph/          # Specialized: /agentic-docs:create-knowledge-graph
│   └── SKILL.md
├── evaluate/                        # Testing: /agentic-docs:evaluate
│   └── SKILL.md
├── validate/                        # Validation: /agentic-docs:validate
│   └── SKILL.md
│
├── generate-agents-md/              # Single artifact: AGENTS.md
│   └── SKILL.md
├── generate-architecture-md/        # Single artifact: ARCHITECTURE.md
│   └── SKILL.md
├── generate-design-md/              # Single artifact: DESIGN.md
│   └── SKILL.md
├── generate-development-md/         # Single artifact: DEVELOPMENT.md
│   └── SKILL.md
├── generate-testing-md/             # Single artifact: TESTING.md
│   └── SKILL.md
├── generate-reliability-md/         # Single artifact: RELIABILITY.md
│   └── SKILL.md
├── generate-security-md/            # Single artifact: SECURITY.md
│   └── SKILL.md
├── generate-quality-score-md/       # Single artifact: QUALITY_SCORE.md
│   └── SKILL.md
├── generate-core-beliefs-md/        # Single artifact: design-docs/core-beliefs.md
│   └── SKILL.md
├── generate-component-architecture-md/  # Single artifact: design-docs/component-architecture.md
│   └── SKILL.md
├── generate-data-flow-md/           # Single artifact: design-docs/data-flow.md
│   └── SKILL.md
└── generate-glossary-md/            # Single artifact: domain/glossary.md
    └── SKILL.md
```

**Total**: 16 skills (4 orchestrators/utilities + 12 file generators)

## Skill Categories

### 1. Orchestrators & Utilities

These skills coordinate multiple sub-tasks:

- **create** - Main orchestrator that calls all 12 generate-*-md skills
- **create-knowledge-graph** - Specialized knowledge graph generation
- **evaluate** - Behavioral testing system with judge/coding sub-agents
- **validate** - Documentation quality validation

**Why separate**: Each has distinct purpose and can be used independently.

### 2. File-Specific Generation Skills

Each `generate-*-md` skill:
- Maps to **one artifact** (clear ownership)
- Has **line budget constraints** (prevents over-generation)
- Can be triggered **individually** (e.g., `/generate-design-md`)
- **Composable** by orchestrator (`/agentic-docs:create` calls all 12)

**Why separate**:
- **Individual triggers**: Users can regenerate just DESIGN.md without touching other files
- **Clear ownership**: Each skill owns one file's generation logic
- **Line budgets**: AGENTS.md has different budget (80-150) than DESIGN.md (~350)
- **Separate data sources**: DEVELOPMENT.md reads Makefile, TESTING.md reads test/, etc.
- **CI composition**: Can selectively regenerate files based on changes

**When to consolidate**: Only if two skills:
- Always run together (never independently)
- Share the same owner
- Differ only in trivial parameters

**Current status**: All 12 generate-*-md skills remain separate because:
- `/agentic-docs:create` orchestrator composes them (CI use case)
- Each has unique data sources and line budgets
- Users may want to regenerate individual files

## Template Usage

### Skills That Use Templates

5 skills use templates from `templates/` directory:

| Skill | Template | Lines | Based On |
|-------|----------|-------|----------|
| generate-agents-md | AGENTS.md.template | 80-150 | PR #437 |
| generate-architecture-md | ARCHITECTURE.md.template | ~200 | PR #437 |
| generate-design-md | DESIGN.md.template | ~350 | PR #437 |
| generate-development-md | DEVELOPMENT.md.template | ~280 | PR #437 |
| generate-testing-md | TESTING.md.template | ~320 | PR #437 |

**How templates are used**:
1. Read template file: `cat templates/DEVELOPMENT.md.template`
2. Extract repository data (Makefile, package files, etc.)
3. Replace placeholders: `{PROJECT_NAME}`, `{BUILD_COMMAND}`, etc.
4. Write output: `agentic/DEVELOPMENT.md`

### Skills That Generate From Scratch

7 skills generate content using AI without templates:

- generate-reliability-md
- generate-security-md
- generate-quality-score-md
- generate-core-beliefs-md
- generate-component-architecture-md
- generate-data-flow-md
- generate-glossary-md

**Why no templates**:
- Content is more dynamic and repository-specific
- Requires deeper code analysis and inference
- Structure varies significantly across repositories

## File Organization Rule

**Every skill directory MUST have SKILL.md** (Claude Code loads skills from SKILL.md files).

**No extra markdown files** unless:
- They're **linked from SKILL.md** as internal documentation
- Or they should be **removed** (dead weight)

Previously removed dead weight:
- `documentation-generation/` (3 unused .md files)
- `inference/` (2 unused .md files)
- `linking/` (1 unused .md file)
- `parsing/` (3 unused .md files)
- `repo/` (4 unused .md files)
- `synthesis/` (2 unused .md files)
- `validation/` (14 unused .md files - validation logic should be in `lib/validators/*.py`)

## Skill Composition Example

```bash
# Individual skill invocation
/generate-design-md /path/to/repo

# Orchestrator invocation (calls all 12 generate-*-md skills)
/agentic-docs:create /path/to/repo
```

The orchestrator skill (`create`) is documented in `skills/create/SKILL.md` and lists all skills it invokes in sequence.

## Adding New Skills

### When to add a new skill:
- New documentation artifact to generate (e.g., `generate-observability-md`)
- New utility (e.g., `analyze-documentation-gaps`)
- New validation category (e.g., `validate-code-examples`)

### When NOT to add a new skill:
- Logic that should be in existing skill
- Helper function (put in `lib/` directory)
- Validation check (put in `lib/validators/` as Python)

### Steps to add:
1. Create directory: `skills/generate-{filename}/`
2. Create `SKILL.md` with frontmatter:
   ```yaml
   ---
   name: generate-{filename}
   description: "Generate {FILENAME}.md file for agentic documentation"
   trigger: /generate-{filename}
   ---
   ```
3. If using template: create `templates/{FILENAME}.md.template`
4. Update orchestrator: `skills/create/SKILL.md` (add to workflow)
5. Test individually: `/generate-{filename} /path/to/repo`

## Skills vs Library Code

**Skills** (in `skills/*/SKILL.md`):
- User-invocable via `/skill-name`
- Coordinate high-level workflows
- Call library code to do work

**Library Code** (in `lib/`):
- Python modules/functions
- Reusable utilities
- Deterministic operations (parsing, validation, metrics)

**Example**:
- **Skill**: `generate-development-md` (SKILL.md)
- **Library**: `lib/generators/development_generator.py` (Python implementation)
- **Validators**: `lib/validators/line_budget_validator.py` (Python validation)
- **Metrics**: `lib/metrics_logger.py` (Python logging)

## Validation Logic

Validation checks should be **Python code in `lib/validators/`**, NOT markdown files in skills directory.

**Bad** (removed):
```
skills/validation/check-navigation-depth.md
skills/validation/check-line-budgets.md
skills/validation/semantic-validate-adr.md
```

**Good** (current):
```
lib/validators/navigation_validator.py
lib/validators/line_budget_validator.py
lib/validators/semantic_validator.py
```

The `validate` skill (SKILL.md) orchestrates these validators but doesn't contain validation logic itself.

## Summary

✅ **Keep separate when**:
- Each skill maps to one artifact
- Can be triggered individually
- Has distinct data sources or line budgets
- Used in composition (orchestrator)

❌ **Consolidate when**:
- Always run together
- Share same owner
- Differ only in trivial parameters

✅ **Current structure is correct**:
- 12 generate-*-md skills stay separate (composable, individual triggers)
- 4 orchestrator/utility skills provide coordination
- Templates used for 5 core files (based on PR #437)
- Library code in `lib/` for implementation
- No dead weight markdown files
