---
name: agentic-docs:validate
description: "Validate agentic documentation against quality standards with user-configurable parameters"
trigger: /agentic-docs:validate
---

# Agentic-Docs: Validate

**Trigger**: `/agentic-docs:validate`  
**Purpose**: Validate existing agentic documentation against quality standards

## Overview

Validates agentic documentation using configuration-driven parameters. The agent **cannot** modify validation parameters - they are loaded from `config/validation.yaml` and enforced immutably.

## Input

**Repository Path** (optional - defaults to current directory)

```
/agentic-docs:validate [<repo-path>]
```

## Configuration

All validation parameters are defined in `config/validation.yaml`:

- **Navigation depth**: Maximum hops from AGENTS.md (default: 3)
- **Line budgets**: Maximum lines per file type
- **Directory structure**: Required directories and files
- **Quality score**: Thresholds and weights
- **Validation checks**: Which checks to enable

**Agent Constraint**: The agent MUST NOT modify these parameters during execution. Configuration is loaded at start and enforced immutably throughout validation.

## Workflow

### Phase 1: Load Configuration (Immutable)

**Action**: Load validation.yaml configuration

**Tool**: `lib/validators/config_loader.py`

**Logged**:
- Configuration file: `config/validation.yaml`
- Parameters loaded: 45
- Configuration hash: `<sha256>` (for immutability verification)

**Output to CLI**:
```
🔍 Agentic-Docs: Validate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Repository: /path/to/repo
Timestamp: 2026-05-08 14:35:20
Configuration: config/validation.yaml (immutable)
Log file: logs/agentic-docs-validate-2026-05-08-14-35-20.log
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 2: Validate Directory Structure

**Tool**: `lib/validators/structure_validator.py`

**Checks**:
- Required directories exist
- Required files present
- File naming conventions

**Logged**:
- Directories checked: 13
- Files checked: 19
- Issues found: 0

**Output to CLI**:
```
Phase 1: Directory Structure Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ All 13 required directories exist
✓ All 19 required files present
✓ File naming conventions correct
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 3: Validate Navigation Depth

**Tool**: `lib/validators/navigation_validator.py`

**Checks**:
- Maximum hops from AGENTS.md ≤ configured limit
- No orphaned documents
- All links reachable

**Logged**:
- Maximum hops configured: 3
- Actual maximum hops: 2
- Orphaned documents: 0

**Output to CLI**:
```
Phase 2: Navigation Depth Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Maximum hops: 2/3 (within limit)
✓ No orphaned documents
✓ All documents reachable from AGENTS.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 4: Validate Line Budgets

**Tool**: `lib/validators/line_budget_validator.py`

**Checks**:
- AGENTS.md ≤ configured limit
- Component docs ≤ configured limit
- Concept docs ≤ configured limit

**Logged**:
- AGENTS.md: 145/150 lines ✓
- Component docs: 12 files, max 98 lines ✓
- Concept docs: 8 files, max 72 lines ✓

**Output to CLI**:
```
Phase 3: Line Budget Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ AGENTS.md: 145/150 lines
✓ Component docs: 12 files (max 98/100 lines)
✓ Concept docs: 8 files (max 72/75 lines)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 5: Validate Links

**Tool**: `lib/validators/link_validator.py`

**Checks**:
- No broken internal links
- All cross-references valid

**Logged**:
- Links checked: 127
- Broken links: 0

**Output to CLI**:
```
Phase 4: Link Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Checked 127 links
✓ No broken links found
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 6: Calculate Quality Score

**Tool**: `lib/validators/quality_score_calculator.py`

**Calculation** (based on config weights):
- Coverage: 40 points (≥80% components documented)
- Freshness: 20 points (updated <90 days)
- Completeness: 20 points (all required files)
- Linkage: 10 points (no broken links)
- Navigation: 10 points (≤3 hop depth)

**Logged**:
- Coverage score: 38/40
- Freshness score: 18/20
- Completeness score: 20/20
- Linkage score: 10/10
- Navigation score: 10/10
- Total: 96/100

**Output to CLI**:
```
Phase 5: Quality Score Calculation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Coverage:     38/40 (95% components documented)
Freshness:    18/20 (updated 45 days ago)
Completeness: 20/20 (all files present)
Linkage:      10/10 (no broken links)
Navigation:   10/10 (max 2 hops)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Score: 96/100 ✓ PASS (threshold: 70)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Validation Summary Report

**Output to CLI**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Validation Summary Report

Repository: openshift/installer
Timestamp: 2026-05-08 14:35:45
Duration: 18.7s

Validation Results:
  ✓ Directory Structure: PASS
  ✓ Navigation Depth: PASS (2/3 hops)
  ✓ Line Budgets: PASS
  ✓ Link Integrity: PASS (0 broken links)
  ✓ Quality Score: PASS (96/100)

Overall: ✅ PASS

Tools Used:
  • config_loader.py (load configuration)
  • structure_validator.py (directory structure)
  • navigation_validator.py (navigation depth)
  • line_budget_validator.py (line budgets)
  • link_validator.py (broken links)
  • quality_score_calculator.py (quality score)

Configuration: config/validation.yaml (immutable)
Log file: logs/agentic-docs-validate-2026-05-08-14-35-20.log
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Configuration Immutability

**Critical Constraint**: The agent MUST NOT modify validation parameters during execution.

**Enforcement**:
1. Configuration loaded at start with SHA256 hash
2. Hash verified before each validation phase
3. Any tampering causes immediate failure

**Error if modified**:
```
❌ Configuration Tampering Detected

Configuration hash mismatch!
Expected: sha256:abc123...
Actual:   sha256:def456...

Validation parameters MUST NOT be modified during execution.
Please restart validation to reload configuration.

Aborting validation.
```

## Logging Format

### Log File
```
[2026-05-08 14:35:20] INFO: Command invoked: /agentic-docs:validate
[2026-05-08 14:35:20] INFO: Repository: /path/to/repo
[2026-05-08 14:35:20] INFO: Configuration loaded: config/validation.yaml
[2026-05-08 14:35:20] INFO: Configuration hash: sha256:abc123...
[2026-05-08 14:35:20] INFO: Phase 1: Directory Structure Validation - STARTED
[2026-05-08 14:35:22] INFO: Tool: structure_validator.py
[2026-05-08 14:35:22] INFO: Directories checked: 13/13 ✓
[2026-05-08 14:35:22] INFO: Files checked: 19/19 ✓
[2026-05-08 14:35:22] INFO: Phase 1: Directory Structure Validation - COMPLETED
[2026-05-08 14:35:22] INFO: Phase 2: Navigation Depth Validation - STARTED
[2026-05-08 14:35:25] INFO: Tool: navigation_validator.py
[2026-05-08 14:35:25] INFO: Maximum hops: 2 (limit: 3) ✓
...
[2026-05-08 14:35:45] INFO: Overall result: PASS
[2026-05-08 14:35:45] INFO: Quality score: 96/100
```

## Customizing Validation

Users can modify `config/validation.yaml` to customize validation behavior:

```yaml
# Example: Change navigation depth limit
navigation:
  max_hops: 4  # Changed from default 3

# Example: Adjust line budgets
line_budget:
  agents_md: 200  # Increased from 150
  component_docs: 150  # Increased from 100
```

Then re-run `/agentic-docs:validate` to apply new configuration.
