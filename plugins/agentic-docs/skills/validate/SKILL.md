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
- **Key Decision**: Using immutable configuration - parameters cannot be modified during execution

**Output to CLI**:
```
🔍 Agentic-Docs: Validate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Repository: <ACTUAL_REPOSITORY_PATH>
Timestamp: <ACTUAL_TIMESTAMP>
Configuration: config/validation.yaml (immutable)
Log file: <ACTUAL_LOG_PATH>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Metrics grounding**: This output block shows layout only. All placeholders MUST be replaced with real values from the current run. Never copy example values.

### Phase 2: Validate Directory Structure

**Tool**: `lib/validators/structure_validator.py`

**Checks**:
- Required directories exist
- Required files present
- File naming conventions

**Logged** (via MetricsLogger):
- Directories checked: <ACTUAL_COUNT>
- Files checked: <ACTUAL_COUNT>
- Issues found: <ACTUAL_COUNT>
- **Key Decision**: All required directories and files present - proceeding with validation

**Output to CLI**:
```
Phase 1: Directory Structure Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ All <COUNT> required directories exist
✓ All <COUNT> required files present
✓ File naming conventions correct
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 3: Validate Navigation Depth

**Tool**: `lib/validators/navigation_validator.py`

**Checks**:
- Maximum hops from AGENTS.md ≤ configured limit
- No orphaned documents
- All links reachable

**Logged** (via MetricsLogger):
- Maximum hops configured: <CONFIG_VALUE>
- Actual maximum hops: <MEASURED_VALUE>
- Orphaned documents: <ACTUAL_COUNT>
- **Key Decision**: Navigation depth within acceptable limits - no remediation needed

**Output to CLI**:
```
Phase 2: Navigation Depth Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Maximum hops: <ACTUAL>/<CONFIGURED> (within limit)
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

**Logged** (via MetricsLogger):
- AGENTS.md: <ACTUAL_LINES>/<CONFIGURED_LIMIT> lines
- Component docs: <FILE_COUNT> files, max <MAX_LINES> lines
- Concept docs: <FILE_COUNT> files, max <MAX_LINES> lines
- **Key Decision**: All line budgets within configured limits - no budget violations

**Output to CLI**:
```
Phase 3: Line Budget Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ AGENTS.md: <ACTUAL>/<LIMIT> lines
✓ Component docs: <COUNT> files (max <MAX_LINES>/<LIMIT> lines)
✓ Concept docs: <COUNT> files (max <MAX_LINES>/<LIMIT> lines)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 5: Validate Links

**Tool**: `lib/validators/link_validator.py`

**Checks**:
- No broken internal links
- All cross-references valid

**Logged** (via MetricsLogger):
- Links checked: <ACTUAL_COUNT>
- Broken links: <ACTUAL_COUNT>
- **Key Decision**: All links valid - documentation navigation integrity confirmed

**Output to CLI**:
```
Phase 4: Link Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Checked <COUNT> links
✓ No broken links found
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 6: Calculate Quality Score

**Tool**: `lib/validators/quality_score_calculator.py`

**Calculation** (based on config weights):
- Coverage: <POINTS> points (≥<THRESHOLD>% components documented)
- Freshness: 20 points (updated <90 days)
- Completeness: 20 points (all required files)
- Linkage: 10 points (no broken links)
- Navigation: 10 points (≤3 hop depth)

**Logged** (via MetricsLogger):
- Coverage score: <ACTUAL_SCORE>/<MAX_SCORE>
- Freshness score: <ACTUAL_SCORE>/<MAX_SCORE>
- Completeness score: <ACTUAL_SCORE>/<MAX_SCORE>
- Linkage score: <ACTUAL_SCORE>/<MAX_SCORE>
- Navigation score: <ACTUAL_SCORE>/<MAX_SCORE>
- Total: <TOTAL_SCORE>/<MAX_SCORE>
- **Key Decision**: Quality score <TOTAL>/<MAX> exceeds threshold (<THRESHOLD>) - documentation meets quality standards

**Output to CLI**:
```
Phase 5: Quality Score Calculation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Coverage:     <SCORE>/<MAX> (<PERCENT>% components documented)
Freshness:    <SCORE>/<MAX> (updated <DAYS> days ago)
Completeness: <SCORE>/<MAX> (all files present)
Linkage:      <SCORE>/<MAX> (no broken links)
Navigation:   <SCORE>/<MAX> (max <HOPS> hops)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Score: <TOTAL>/<MAX> ✓ PASS (threshold: <THRESHOLD>)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Validation Summary Report

**CRITICAL**: Use the display_metrics.py script to show actual results. DO NOT invent metrics.

**Run this command** to display the validation summary:
```bash
python lib/display_metrics.py <ACTUAL_METRICS_JSON_PATH>
```

**Example format** (all values from JSON, NO invented numbers):
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Validation Summary Report

Repository: <REPOSITORY_FROM_JSON>
Timestamp: <TIMESTAMP_FROM_JSON>
Duration: <DURATION_FROM_JSON>

Validation Results:
  <RESULTS_FROM_JSON>

Overall: <PASS_OR_FAIL_FROM_JSON>

Tools Used:
  <LIST_FROM_JSON>

Configuration: config/validation.yaml (immutable)
Log file: <LOG_PATH_FROM_JSON>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Metrics grounding**: The example above shows layout ONLY. All placeholders (`<*_FROM_JSON>`) MUST be filled from the actual metrics JSON file. If a field is missing, print `<NOT_RECORDED>`, NEVER invent a value.

### Metrics Source Table

| Field | Source | Location |
|-------|--------|----------|
| Repository | MetricsLogger.repository | `*.metrics.json`: `repository` field |
| Timestamp | MetricsLogger.timestamp_end | `*.metrics.json`: `timestamp_end` field |
| Duration | MetricsLogger.duration_ms | `*.metrics.json`: `duration_ms` field |
| Validation Results | MetricsLogger.details | `*.metrics.json`: `details` object |
| Overall Result | MetricsLogger.result | `*.metrics.json`: `result` field |
| Tools Used | MetricsLogger.tools_used | `*.metrics.json`: `tools_used` object |
| Quality Score | MetricsLogger.details.quality_score | `*.metrics.json`: `details.quality_score` |
| Log Path | Metrics JSON filename | Replace `.metrics.json` with `.log` |

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
[2026-05-08 14:35:22] INFO: Directories checked: <COUNT>/<TOTAL> ✓
[2026-05-08 14:35:22] INFO: Files checked: <COUNT>/<TOTAL> ✓
[2026-05-08 14:35:22] INFO: Phase 1: Directory Structure Validation - COMPLETED
[2026-05-08 14:35:22] INFO: Phase 2: Navigation Depth Validation - STARTED
[2026-05-08 14:35:25] INFO: Tool: navigation_validator.py
[2026-05-08 14:35:25] INFO: Maximum hops: <ACTUAL> (limit: <LIMIT>) ✓
...
[2026-05-08 14:35:45] INFO: Overall result: PASS
[2026-05-08 14:35:45] INFO: Quality score: <SCORE>/<MAX>
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

## Logging Implementation

This skill uses **`lib/metrics_logger.py`** for comprehensive logging and metrics:
- Real-time logging to CLI (all validation phases logged as they occur)
- Persistent logging to timestamped log file (`logs/agentic-docs-validate-{timestamp}.log`)
- Key decision logging at each validation phase
- Post-execution metrics summary (duration, tool usage, validation results)
- Metrics JSON export (`logs/agentic-docs-validate-{timestamp}.metrics.json`)

See [lib/METRICS_LOGGER_USAGE.md](../../lib/METRICS_LOGGER_USAGE.md) for complete usage guide.
