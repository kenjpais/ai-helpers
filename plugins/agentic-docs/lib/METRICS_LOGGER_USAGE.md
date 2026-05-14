# Metrics Logger Usage Guide

The `metrics_logger.py` module provides comprehensive logging and metrics tracking for all agentic-docs commands.

## Purpose

Implements the requirements from FIX_MAY_8.md:
- Real-time logging to CLI
- Persistent logging to timestamped log files
- Post-execution metrics display
- Tool and skill usage tracking
- Agent execution transparency
- Data flow tracking

## Quick Start

```python
from lib.metrics_logger import MetricsLogger

# Initialize logger
logger = MetricsLogger(
    command="agentic-docs:create",
    repository="/path/to/repo"
)

# Log tools and skills
logger.log_tool_invocation("Read", "Read AGENTS.md")
logger.log_skill_invocation("generate-design-md", ["README.md", "docs/architecture.md"])

# Log agent spawns and data flows
logger.log_agent_spawn("coding-agent-001", "coding")
logger.log_data_flow("task.md", "Coding Sub-Agent", "task description")

# Log key decisions
logger.log_key_decision("Using immutable configuration - parameters cannot be modified")

# Finalize and display metrics
logger.finalize("PASS", {"quality_score": "96/100", "files_created": 30})
```

## API Reference

### Initialization

```python
MetricsLogger(command: str, repository: str, log_dir: str = "logs")
```

Creates a new metrics logger with timestamped log file.

**Parameters:**
- `command`: Command name (e.g., "agentic-docs:create")
- `repository`: Repository path
- `log_dir`: Directory for log files (default: "logs")

**Creates:**
- Timestamped log file: `logs/{command}-{timestamp}.log`
- Metrics JSON file: `logs/{command}-{timestamp}.metrics.json`

### Logging Methods

#### Basic Logging

```python
logger.log_info("Phase 1: Directory Structure Validation - STARTED")
logger.log_warn("Line budget approaching limit: 145/150")
logger.log_error("Validation failed: broken link detected")
logger.log_debug("Checking file: agentic/AGENTS.md")
```

#### Tool Invocations

```python
logger.log_tool_invocation("Read", "Read AGENTS.md")
logger.log_tool_invocation("Bash", "Run structure_generator.py")
logger.log_tool_invocation("Agent", "Spawn coding sub-agent")
```

**Tracked:**
- Tool name
- Invocation count (auto-incremented)
- Description (optional)
- Timestamp

#### Skill Invocations

```python
logger.log_skill_invocation(
    "generate-design-md",
    data_sources=["README.md", "docs/architecture.md", "pkg/"]
)
```

**Tracked:**
- Skill name
- Invocation count (auto-incremented)
- Data sources used
- Timestamp

#### Agent Execution

```python
# Spawn sub-agent
logger.log_agent_spawn("coding-agent-001", "coding")
logger.log_agent_spawn("judge-agent-001", "judge")

# Data flow between agents
logger.log_data_flow(
    source="scenario.input",
    destination="Coding Sub-Agent",
    data_type="task description"
)
```

**Tracked:**
- Agent ID and type
- Spawn timestamp
- Data flows between components

#### File Operations

```python
# Track file access
logger.log_file_access("agentic/AGENTS.md")
logger.log_file_access("agentic/RELIABILITY.md")

# Track file creation
logger.log_file_created("agentic/DESIGN.md")
logger.log_file_created("agentic/TESTING.md")
```

**Tracked:**
- Files accessed (deduplicated)
- Files created (deduplicated)

#### Key Decisions

```python
logger.log_key_decision("All required directories and files present - proceeding with validation")
logger.log_key_decision("Quality score 96/100 exceeds threshold (70) - documentation meets quality standards")
```

**Purpose:**
- Documents important decision points during execution
- Required for validation skill per FIX_MAY_8.md

### Finalization

```python
logger.finalize(
    result="PASS",  # "PASS", "FAIL", "COMPLETED", "ERROR"
    details={
        "quality_score": "96/100",
        "files_created": 30,
        "scenarios_passed": "15/16"
    }
)
```

**Actions:**
1. Calculates total duration
2. Logs completion
3. Displays metrics summary to CLI
4. Writes metrics JSON file

## Example: /agentic-docs:create

```python
from lib.metrics_logger import MetricsLogger

def create_documentation(repo_path: str):
    # Initialize logger
    logger = MetricsLogger("agentic-docs:create", repo_path)
    
    try:
        # Phase 1: Create directory structure
        logger.log_info("Phase 1: Create Directory Structure - STARTED")
        logger.log_tool_invocation("Bash", "python lib/generators/structure_generator.py")
        logger.log_file_created("agentic/")
        logger.log_file_created("agentic/design-docs/")
        logger.log_info("Phase 1: Create Directory Structure - COMPLETED")
        
        # Phase 2: Generate core documentation
        logger.log_info("Phase 2: Generate Core Documentation - STARTED")
        
        # Invoke skill for each file
        logger.log_skill_invocation(
            "generate-design-md",
            data_sources=["README.md", "docs/architecture.md", "pkg/"]
        )
        logger.log_file_created("agentic/DESIGN.md")
        
        logger.log_skill_invocation(
            "generate-development-md",
            data_sources=["README.md", "Makefile", "go.mod"]
        )
        logger.log_file_created("agentic/DEVELOPMENT.md")
        
        # ... more skills ...
        
        logger.log_info("Phase 2: Generate Core Documentation - COMPLETED")
        
        # Phase 3: Validate output
        logger.log_info("Phase 3: Validate Output - STARTED")
        logger.log_skill_invocation("agentic-docs:validate")
        logger.log_key_decision("Validation passed - all quality checks satisfied")
        logger.log_info("Phase 3: Validate Output - COMPLETED")
        
        # Finalize with success
        logger.finalize("COMPLETED", {
            "files_created": 30,
            "quality_score": "96/100",
            "validation": "PASSED"
        })
        
    except Exception as e:
        logger.log_error(f"Command failed: {e}")
        logger.finalize("ERROR", {"error": str(e)})
        raise
```

## Example: /agentic-docs:validate

```python
from lib.metrics_logger import MetricsLogger

def validate_documentation(repo_path: str):
    logger = MetricsLogger("agentic-docs:validate", repo_path)
    
    try:
        # Load configuration
        logger.log_info("Loading configuration: config/validation.yaml")
        logger.log_tool_invocation("Read", "config/validation.yaml")
        logger.log_key_decision("Using immutable configuration - parameters cannot be modified during execution")
        
        # Validate directory structure
        logger.log_info("Phase 1: Directory Structure Validation - STARTED")
        logger.log_tool_invocation("Bash", "python lib/validators/structure_validator.py")
        logger.log_key_decision("All required directories and files present - proceeding with validation")
        logger.log_info("Phase 1: Directory Structure Validation - COMPLETED")
        
        # Validate navigation depth
        logger.log_info("Phase 2: Navigation Depth Validation - STARTED")
        logger.log_tool_invocation("Bash", "python lib/validators/navigation_validator.py")
        logger.log_key_decision("Navigation depth within acceptable limits - no remediation needed")
        logger.log_info("Phase 2: Navigation Depth Validation - COMPLETED")
        
        # ... more validation phases ...
        
        # Calculate quality score
        logger.log_info("Phase 5: Quality Score Calculation - STARTED")
        logger.log_tool_invocation("Bash", "python lib/validators/quality_score_calculator.py")
        logger.log_key_decision("Quality score 96/100 exceeds threshold (70) - documentation meets quality standards")
        logger.log_info("Phase 5: Quality Score Calculation - COMPLETED")
        
        # Finalize
        logger.finalize("PASS", {
            "quality_score": "96/100",
            "validation_phases": 5,
            "issues_found": 0
        })
        
    except Exception as e:
        logger.log_error(f"Validation failed: {e}")
        logger.finalize("FAIL", {"error": str(e)})
        raise
```

## Example: /agentic-docs:evaluate

```python
from lib.metrics_logger import MetricsLogger

def evaluate_documentation(repo_path: str):
    logger = MetricsLogger("agentic-docs:evaluate", repo_path)
    
    try:
        # Load test scenarios
        logger.log_info("Loading test scenarios from tests/benchmark/")
        logger.log_tool_invocation("Read", "tests/benchmark/*.yaml")
        scenarios_loaded = 16
        logger.log_info(f"Test scenarios loaded: {scenarios_loaded}")
        
        # Execute scenarios
        scenarios_passed = 0
        total_outcomes = 0
        outcomes_satisfied = 0
        
        for i in range(1, scenarios_loaded + 1):
            logger.log_info(f"Scenario {i}/{scenarios_loaded}: STARTED")
            
            # Judge spawns coding sub-agent
            agent_id = f"coding-agent-{i:03d}"
            logger.log_agent_spawn(agent_id, "coding")
            logger.log_data_flow("scenario.input", "Coding Sub-Agent", "task description")
            
            # Coding sub-agent reads documentation
            logger.log_file_access("agentic/AGENTS.md")
            logger.log_file_access("agentic/RELIABILITY.md")
            logger.log_file_access("agentic/design-docs/component-architecture.md")
            
            # Coding sub-agent generates plan
            logger.log_data_flow("Coding Sub-Agent", "execution_plan.txt", "execution plan")
            
            # Judge evaluates with Promptfoo
            judge_id = f"judge-agent-{i:03d}"
            logger.log_agent_spawn(judge_id, "judge")
            logger.log_data_flow("execution_plan.txt", "Judge Sub-Agent", "execution plan")
            logger.log_tool_invocation("Promptfoo", "Run assertions on execution plan")
            
            # Track results
            outcomes_in_scenario = 6
            outcomes_passed = 6  # All passed in this example
            total_outcomes += outcomes_in_scenario
            outcomes_satisfied += outcomes_passed
            
            if outcomes_passed == outcomes_in_scenario:
                scenarios_passed += 1
                logger.log_info(f"Scenario {i}/{scenarios_loaded}: PASS ({outcomes_passed}/{outcomes_in_scenario} outcomes)")
            else:
                logger.log_warn(f"Scenario {i}/{scenarios_loaded}: FAIL ({outcomes_passed}/{outcomes_in_scenario} outcomes)")
        
        # Finalize
        success_rate = (scenarios_passed / scenarios_loaded) * 100
        logger.finalize("PASS" if scenarios_passed == scenarios_loaded else "FAIL", {
            "scenarios_executed": scenarios_loaded,
            "scenarios_passed": scenarios_passed,
            "success_rate": f"{success_rate:.2f}%",
            "total_outcomes": total_outcomes,
            "outcomes_satisfied": outcomes_satisfied,
            "outcome_satisfaction_rate": f"{(outcomes_satisfied/total_outcomes)*100:.2f}%"
        })
        
    except Exception as e:
        logger.log_error(f"Evaluation failed: {e}")
        logger.finalize("ERROR", {"error": str(e)})
        raise
```

## Output Format

### CLI Output (Real-Time)

```
  [2026-05-09 10:30:15] INFO: Command invoked: agentic-docs:create
  [2026-05-09 10:30:15] INFO: Repository: /path/to/repo
  [2026-05-09 10:30:15] INFO: Log file: logs/agentic-docs-create-2026-05-09-10-30-15.log
  [2026-05-09 10:30:16] INFO: Phase 1: Create Directory Structure - STARTED
  [2026-05-09 10:30:16] INFO: Tool used: Bash - python lib/generators/structure_generator.py
  [2026-05-09 10:30:18] INFO: File created: agentic/
  ...
  [2026-05-09 10:32:49] INFO: Command completed: COMPLETED
  [2026-05-09 10:32:49] INFO: Total duration: 154.3s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Execution Metrics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Command: agentic-docs:create
Duration: 154.3s
Result: COMPLETED

Tools Used:
  • Bash: 12 invocations
  • Read: 5 invocations

Skills Used:
  • generate-design-md: 1 invocations
  • generate-development-md: 1 invocations
  • generate-testing-md: 1 invocations
  ... and 9 more

Data Sources (15):
  • README.md
  • Makefile
  • docs/architecture.md
  ... and 12 more

Files Created: 30

Details:
  files_created: 30
  quality_score: 96/100
  validation: PASSED

Log file: logs/agentic-docs-create-2026-05-09-10-30-15.log
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Metrics saved: logs/agentic-docs-create-2026-05-09-10-30-15.metrics.json
```

### Metrics JSON File

```json
{
  "command": "agentic-docs:create",
  "repository": "/path/to/repo",
  "timestamp_start": "2026-05-09T10:30:15.123456",
  "timestamp_end": "2026-05-09T10:32:49.456789",
  "duration_ms": 154333.333,
  "primary_agent": "Main Orchestrator",
  "sub_agents": [],
  "tools_used": {
    "Bash": 12,
    "Read": 5
  },
  "skills_used": {
    "generate-design-md": 1,
    "generate-development-md": 1,
    "generate-testing-md": 1
  },
  "data_sources": [
    "README.md",
    "Makefile",
    "docs/architecture.md"
  ],
  "files_created": [
    "agentic/DESIGN.md",
    "agentic/DEVELOPMENT.md",
    "agentic/TESTING.md"
  ],
  "files_accessed": [
    "README.md",
    "Makefile"
  ],
  "data_flows": [],
  "result": "COMPLETED",
  "details": {
    "files_created": 30,
    "quality_score": "96/100",
    "validation": "PASSED"
  }
}
```

## Integration Notes

### Skills (SKILL.md files)

Skills should document the metrics logger usage:

```markdown
## Logging Requirements

This skill uses `lib/metrics_logger.py` to provide:
- Real-time logging to CLI
- Persistent logging to timestamped log files
- Post-execution metrics summary
- Tool and skill usage tracking

All executions are logged to `logs/agentic-docs-{command}-{timestamp}.log`.
```

### Implementation Scripts

Python scripts should import and use the logger:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from metrics_logger import MetricsLogger

def main():
    logger = MetricsLogger("agentic-docs:create", "/path/to/repo")
    # ... implementation ...
    logger.finalize("COMPLETED", {"files_created": 30})

if __name__ == "__main__":
    main()
```

## Requirements Satisfied

This implementation satisfies all requirements from FIX_MAY_8.md:

✅ **Section 1**: `/agentic-docs:create` logging
- Logs all data sources, tools used, skills invoked
- Prints logs to CLI in real time
- Persists logs to timestamped log file
- Complete, structured, reproducible logs

✅ **Section 2**: `/agentic-docs:validate` logging
- Logs validation phases step-by-step
- Logs key decisions made during validation
- Logs tools and skills used
- Outputs validation summary with repository name and timestamp

✅ **Section 3**: `/agentic-docs:evaluate` logging
- Logs agent execution flow
- Logs sub-agent interactions
- Logs data flow between components
- Complete execution transparency

✅ **Section 4**: Execution transparency
- Displays primary agent and all sub-agents
- Transparent logs of execution flow and data flow
- Logs all tools used, skills invoked, full execution trace
- Timestamped log files for each execution

✅ **Section 5**: Post-execution metrics
- Displays execution duration
- Shows tool usage breakdown
- Shows skill usage breakdown
- Shows complete workflow analytics
