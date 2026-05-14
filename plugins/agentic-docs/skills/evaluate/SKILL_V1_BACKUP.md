---
name: agentic-docs:evaluate
description: "Evaluate documentation quality using behavioral validation with strict agent separation and Promptfoo assertions"
trigger: /agentic-docs:evaluate
---

# Agentic-Docs: Evaluate

**Trigger**: `/agentic-docs:evaluate`  
**Purpose**: Evaluate documentation quality by testing whether execution plans produced from documentation exhibit correct observable behavior

## Core Principle

This system evaluates:

> Whether the generated execution plan produces or implies the correct observable behavior

NOT:

> Whether it matches a reference plan or predefined structure

**Behavioral correctness via observable outcomes**, not structural similarity.

## System Architecture

### Strict Separation of Concerns

```
┌──────────────────────────────────────────────────────────────┐
│ Judge Sub-Agent (Orchestrator + Evaluator)                   │
│                                                               │
│  • Loads test scenarios from /tests/benchmark                │
│  • Extracts scenario.input                                   │
│  • Sends ONLY input to coding sub-agent                      │
│  • Receives execution plan                                   │
│  • Runs Promptfoo assertions                                 │
│  • Aggregates results                                        │
│  • Determines pass/fail                                      │
│                                                               │
│  HAS ACCESS TO: test scenarios, expected outcomes            │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ scenario.input ONLY
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Coding Sub-Agent (Plan Generator)                            │
│                                                               │
│  • Receives scenario input                                   │
│  • Reads agentic documentation                               │
│  • Generates execution plan                                  │
│  • Returns plan as output                                    │
│                                                               │
│  NO ACCESS TO: expected outcomes, test cases, evaluation     │
│                logic, Promptfoo configuration                │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ execution_plan output
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Promptfoo (Assertion Engine)                                 │
│                                                               │
│  • Receives execution plan as variable                       │
│  • Evaluates scenario-defined assertions                     │
│  • Returns pass/fail per assertion                           │
│  • Operates purely as deterministic assertion engine         │
│                                                               │
│  DOES NOT: perform semantic reasoning, interpret quality,    │
│            infer missing context                             │
└──────────────────────────────────────────────────────────────┘
```

**Critical Constraint**: The coding sub-agent is **intentionally unaware** of evaluation criteria. Only the judge sub-agent has access to test scenarios and expected outcomes.

## Input

**Repository Path** (optional - defaults to current directory)

```
/agentic-docs:evaluate [<repo-path>]
```

## Workflow

### Phase 0: Initialize Evaluation

**Actions**:
1. Create timestamped log file: `logs/agentic-docs-evaluate-<timestamp>.log`
2. Load test scenarios from `tests/benchmark/*.yaml`
3. Initialize Promptfoo configuration
4. Display agent architecture

**Output to CLI**:
```
🧪 Agentic-Docs: Evaluate (Behavioral Validation)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Repository: <ACTUAL_REPOSITORY_PATH>
Timestamp: <ACTUAL_TIMESTAMP>
Test scenarios: <ACTUAL_COUNT> loaded from tests/benchmark/
Log file: <ACTUAL_LOG_PATH>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

System Architecture:
  Primary Agent: Main Orchestrator
  Judge Sub-Agent: Test scenario loader + Promptfoo orchestrator
  Coding Sub-Agent: Execution plan generator (no eval access)
  Assertion Engine: Promptfoo (deterministic validation only)

Isolation:
  ✓ Coding sub-agent has NO access to expected outcomes
  ✓ Coding sub-agent has NO access to evaluation logic
  ✓ Promptfoo operates as pure assertion engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Metrics grounding**: This output block shows layout only. All placeholders MUST be replaced with real values from the current run. Never copy example values from this documentation.

**Logged**:
```
[2026-05-08 14:40:15] INFO: Command invoked: /agentic-docs:evaluate
[2026-05-08 14:40:15] INFO: Repository: /path/to/repo
[2026-05-08 14:40:15] INFO: Loading test scenarios from tests/benchmark/
[2026-05-08 14:40:15] INFO: Test scenarios loaded: 16
[2026-05-08 14:40:15] INFO: Primary Agent: Main Orchestrator
[2026-05-08 14:40:15] INFO: Judge Sub-Agent: Orchestrator + Evaluator
[2026-05-08 14:40:15] INFO: Coding Sub-Agent: Plan Generator (isolated)
[2026-05-08 14:40:15] INFO: Assertion Engine: Promptfoo
```

### Phase 1: Execute Test Scenarios

For each test scenario (e.g., 16 total):

#### Step 1: Judge Loads Scenario

**Judge Sub-Agent Actions**:
1. Read test scenario file: `tests/benchmark/{scenario-id}.yaml`
2. Extract `scenario.input`
3. Extract `scenario.expected_outcomes` (NOT shared with coding sub-agent)

**Output to CLI**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test Scenario <N>/<TOTAL>: <SCENARIO_ID>
Description: <SCENARIO_DESCRIPTION>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Logged**:
```
[2026-05-08 14:40:16] INFO: Scenario <SCENARIO_NUM>/<TOTAL>: add-monitoring-endpoint - STARTED
[2026-05-08 14:40:16] INFO: Judge Sub-Agent: Loading scenario from tests/benchmark/01-add-monitoring-endpoint.yaml
[2026-05-08 14:40:16] INFO: Judge Sub-Agent: Scenario loaded - 6 expected outcomes defined
```

#### Step 2: Judge Spawns Coding Sub-Agent

**Judge Sub-Agent Actions**:
1. Spawn coding sub-agent in isolated environment
2. Send ONLY `scenario.input` (NO expected outcomes)
3. Coding sub-agent reads agentic documentation
4. Coding sub-agent generates execution plan
5. Receive execution plan output

**Output to CLI**:
```
→ Judge Sub-Agent: Spawning Coding Sub-Agent
  Agent ID: coding-agent-001
  Input: scenario.input (task description and context)
  NO ACCESS TO: expected outcomes, assertions, test criteria
  
  Expected Output: Execution plan as raw text artifact
```

**Data Flow**:
```
Judge Sub-Agent:
  tests/benchmark/01-add-monitoring-endpoint.yaml
    └─> Extract scenario.input ──────┐
                                      │
                                      ↓
                            Coding Sub-Agent:
                              scenario.input
                              agentic/AGENTS.md
                              agentic/RELIABILITY.md
                              agentic/design-docs/component-architecture.md
                              agentic/design-docs/components/api-server.md
                                      │
                                      ↓
                              execution_plan.txt (raw output)
                                      │
                                      ↓
Judge Sub-Agent:                      │
  Receives execution_plan.txt ←───────┘
  Treats as raw observable artifact
```

**Logged**:
```
[2026-05-08 14:40:16] INFO: Judge Sub-Agent: Spawning Coding Sub-Agent (ID: coding-agent-001)
[2026-05-08 14:40:16] INFO: Data flow: scenario.input → Coding Sub-Agent
[2026-05-08 14:40:18] INFO: Coding Sub-Agent: Read agentic/AGENTS.md
[2026-05-08 14:40:20] INFO: Coding Sub-Agent: Read agentic/RELIABILITY.md
[2026-05-08 14:40:22] INFO: Coding Sub-Agent: Read agentic/design-docs/component-architecture.md
[2026-05-08 14:40:25] INFO: Coding Sub-Agent: Read agentic/design-docs/components/api-server.md
[2026-05-08 14:40:30] INFO: Coding Sub-Agent: Generated execution_plan.txt (342 lines)
[2026-05-08 14:40:30] INFO: Data flow: execution_plan.txt → Judge Sub-Agent
[2026-05-08 14:40:30] INFO: Tools used by Coding Sub-Agent: Read (<COUNT> files), Grep (<COUNT> invocations)
[2026-05-08 14:40:30] INFO: Skills used by Coding Sub-Agent: None
```

#### Step 3: Judge Runs Promptfoo Assertions

**Judge Sub-Agent Actions**:
1. For each `expected_outcomes[].assertion`:
   - Pass execution_plan.txt as Promptfoo variable `{{output}}`
   - Run assertion through Promptfoo
   - Receive pass/fail result
2. Aggregate results: PASS if all outcomes satisfied, FAIL if any outcome fails

**Output to CLI**:
```
→ Judge Sub-Agent: Running Promptfoo Assertions
  Assertion Engine: Promptfoo (deterministic validation)
  Input Variable: {{output}} = execution_plan.txt
  
  Expected Outcomes to Validate:
    1. identifies-api-server-component
    2. includes-prometheus-library
    3. defines-metrics-registration
    4. addresses-endpoint-implementation
    5. includes-testing-strategy
    6. considers-security

  Running assertions...
  
  ✓ identifies-api-server-component: PASS
  ✓ includes-prometheus-library: PASS
  ✓ defines-metrics-registration: PASS
  ✓ addresses-endpoint-implementation: PASS
  ✓ includes-testing-strategy: PASS
  ✓ considers-security: PASS
  
  Result: <SATISFIED>/<TOTAL> outcomes satisfied ✓ PASS
```

**Logged**:
```
[2026-05-08 14:40:30] INFO: Judge Sub-Agent: Running Promptfoo assertions on execution_plan.txt
[2026-05-08 14:40:32] INFO: Promptfoo: Assertion 'identifies-api-server-component' - PASS
[2026-05-08 14:40:34] INFO: Promptfoo: Assertion 'includes-prometheus-library' - PASS
[2026-05-08 14:40:36] INFO: Promptfoo: Assertion 'defines-metrics-registration' - PASS
[2026-05-08 14:40:38] INFO: Promptfoo: Assertion 'addresses-endpoint-implementation' - PASS
[2026-05-08 14:40:40] INFO: Promptfoo: Assertion 'includes-testing-strategy' - PASS
[2026-05-08 14:40:42] INFO: Promptfoo: Assertion 'considers-security' - PASS
[2026-05-08 14:40:42] INFO: Judge Sub-Agent: All <TOTAL> expected outcomes satisfied
```

#### Step 4: Display Scenario Results

**Output to CLI**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Test Scenario <SCENARIO_NUM>/<TOTAL>: PASS (<SATISFIED>/<TOTAL> outcomes)

Duration: <DURATION>

Coding Sub-Agent Execution:
  Documentation Files Read: 4
    • agentic/AGENTS.md
    • agentic/RELIABILITY.md
    • agentic/design-docs/component-architecture.md
    • agentic/design-docs/components/api-server.md
  
  Tools Used: Read (4), Grep (2)
  Skills Used: None
  
  Execution Plan Generated: 342 lines

Judge Sub-Agent Evaluation:
  Expected Outcomes: 6
  Promptfoo Assertions Run: 6
  Outcomes Satisfied: <SATISFIED>/<TOTAL> ✓
  
  Assertion Details:
    ✓ identifies-api-server-component
    ✓ includes-prometheus-library
    ✓ defines-metrics-registration
    ✓ addresses-endpoint-implementation
    ✓ includes-testing-strategy
    ✓ considers-security

Raw Execution Plan Saved: .work/evaluate/01-execution-plan.txt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Logged**:
```
[2026-05-08 14:40:42] INFO: Scenario <SCENARIO_NUM>/<TOTAL>: PASS (<SATISFIED>/<TOTAL> outcomes) - Duration: <DURATION>
[2026-05-08 14:40:42] INFO: Execution plan saved: .work/evaluate/01-execution-plan.txt
[2026-05-08 14:40:42] INFO: Scenario <SCENARIO_NUM>/<TOTAL>: COMPLETED
```

### Phase 2: Aggregate Results

**CRITICAL**: Use the display_metrics.py script to show actual results. DO NOT invent metrics.

**Run this command** to display the evaluation summary:
```bash
python lib/display_metrics.py <ACTUAL_METRICS_JSON_PATH>
```

**Example format** (all values from JSON, NO invented numbers):
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Evaluation Complete

Repository: <REPOSITORY_FROM_JSON>
Timestamp: <TIMESTAMP_FROM_JSON>
Duration: <DURATION_FROM_JSON>

Test Results:
  Scenarios Executed: <COUNT_FROM_JSON>
  Scenarios Passed: <COUNT_FROM_JSON> (<PERCENT_FROM_JSON>%)
  Scenarios Failed: <COUNT_FROM_JSON> (<PERCENT_FROM_JSON>%)
  
  Total Expected Outcomes: <COUNT_FROM_JSON>
  Outcomes Satisfied: <COUNT_FROM_JSON> (<PERCENT_FROM_JSON>%)
  Outcomes Failed: <COUNT_FROM_JSON> (<PERCENT_FROM_JSON>%)

Agent Execution Summary:
  Primary Agent: <COUNT_FROM_JSON> instance(s)
  Judge Sub-Agents spawned: <COUNT_FROM_JSON> instances
  Coding Sub-Agents spawned: <COUNT_FROM_JSON> instances
  Total agent interactions: <COUNT_FROM_JSON>

Documentation Access Patterns:
  <FILES_AND_COUNTS_FROM_JSON>
  
  Total file reads: <COUNT_FROM_JSON>

Tools Used Across All Scenarios:
  <TOOLS_FROM_JSON>

Skills Used Across All Scenarios:
  <SKILLS_FROM_JSON>

Promptfoo Assertion Engine:
  Total assertions evaluated: <COUNT_FROM_JSON>
  Assertions passed: <COUNT_FROM_JSON>
  Assertions failed: <COUNT_FROM_JSON>
  Assertion success rate: <PERCENT_FROM_JSON>%

Failed Scenarios:
  <LIST_FROM_JSON_OR_NONE>

Log file: <LOG_PATH_FROM_JSON>
Raw execution plans: <WORK_DIR_FROM_JSON>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Metrics grounding**: The example above shows layout ONLY. All placeholders (`<*_FROM_JSON>`) MUST be filled from the actual metrics JSON file. If a field is missing, print `<NOT_RECORDED>`, NEVER invent a value.

### Metrics Source Table

| Field | Source | Location |
|-------|--------|----------|
| Duration | MetricsLogger.duration_ms | `*.metrics.json`: `duration_ms` field |
| Scenarios Executed | MetricsLogger.details.scenarios_executed | `*.metrics.json`: `details.scenarios_executed` |
| Scenarios Passed | MetricsLogger.details.scenarios_passed | `*.metrics.json`: `details.scenarios_passed` |
| Success Rate | Calculate from passed/total | `(scenarios_passed / scenarios_executed) * 100` |
| Total Outcomes | MetricsLogger.details.total_outcomes | `*.metrics.json`: `details.total_outcomes` |
| Outcomes Satisfied | MetricsLogger.details.outcomes_satisfied | `*.metrics.json`: `details.outcomes_satisfied` |
| Agent Interactions | Count sub_agents | `len(sub_agents)` from JSON |
| Files Accessed | MetricsLogger.files_accessed | `*.metrics.json`: `files_accessed` array |
| Tools Used | MetricsLogger.tools_used | `*.metrics.json`: `tools_used` object |
| Skills Used | MetricsLogger.skills_used | `*.metrics.json`: `skills_used` object |
| Assertion Counts | MetricsLogger.details | `*.metrics.json`: `details.assertions_*` |
| Failed Scenarios | MetricsLogger.details.failed_scenarios | `*.metrics.json`: `details.failed_scenarios` array |
| Log Path | Metrics JSON filename | Replace `.metrics.json` with `.log` |

**Logged**:
```
[2026-05-08 14:52:33] INFO: Evaluation completed
[2026-05-08 14:52:33] INFO: Overall result: <PASS_COUNT>/<TOTAL> scenarios PASS (<PERCENT>%)
[2026-05-08 14:52:33] INFO: Total expected outcomes: <TOTAL>
[2026-05-08 14:52:33] INFO: Outcomes satisfied: <SATISFIED>/<TOTAL> (<PERCENT>%)
[2026-05-08 14:52:33] INFO: Total duration: <DURATION>
[2026-05-08 14:52:33] INFO: Primary agent instances: <COUNT>
[2026-05-08 14:52:33] INFO: Judge sub-agent instances: <COUNT>
[2026-05-08 14:52:33] INFO: Coding sub-agent instances: <COUNT>
[2026-05-08 14:52:33] INFO: Total agent interactions: <COUNT>
[2026-05-08 14:52:33] INFO: Tools used: <TOOL_USAGE>
[2026-05-08 14:52:33] INFO: Skills used: None
[2026-05-08 14:52:33] INFO: Promptfoo assertions evaluated: <COUNT>
[2026-05-08 14:52:33] INFO: Promptfoo assertions passed: 92
[2026-05-08 14:52:33] INFO: Promptfoo assertions failed: 4
```

## Test Scenario Structure

Each scenario is defined in `tests/benchmark/{scenario-id}.yaml`:

```yaml
scenario:
  id: string                    # Unique identifier
  description: string           # Human-readable description
  input:                        # Input sent to coding sub-agent
    task_description: string    # The coding task
    context:                    # Additional context (list)
      - string
      - string
  expected_outcomes:            # Observable behaviors to validate
    - id: string                # Outcome identifier
      description: string       # What this outcome validates
      assertion: string         # Promptfoo-compatible assertion
```

## Expected Outcomes Design Rules

Each expected outcome MUST be:

1. **Observable** from execution plan output
2. **Atomic** (one condition per outcome)
3. **Deterministic** (same input → same result)
4. **Independently verifiable**
5. **Expressible as a Promptfoo assertion**

### Critical Constraint

Expected outcomes MUST NOT describe internal plan structure.

**They must describe observable behavior**:
- Actions performed
- Artifacts produced
- Dependencies resolved
- Constraints satisfied

**They must NOT include**:
- Step ordering
- Internal formatting
- Hidden implementation details

### Good vs Bad Examples

**Good** (Observable Behavior):
```yaml
- id: "identifies-api-server-component"
  description: "Plan identifies the API server as the component to modify"
  assertion: "llm-rubric: The execution plan identifies the API server component"
```

**Bad** (Structural Bias):
```yaml
- id: "has-seven-sections"
  description: "Plan has exactly 7 sections"
  assertion: "llm-rubric: The execution plan contains exactly 7 top-level sections"
```

**Good** (Functional Requirement):
```yaml
- id: "includes-testing-strategy"
  description: "Plan includes testing the metrics endpoint"
  assertion: "llm-rubric: The execution plan includes a testing strategy"
```

**Bad** (Implementation Detail):
```yaml
- id: "testing-section-third"
  description: "Testing section appears as third section"
  assertion: "llm-rubric: The testing section is the third section in the plan"
```

## Evaluation Flow (Strict Pipeline)

```
1. Judge loads test scenario
      ↓
2. Extracts scenario.input
      ↓
3. Sends input to coding sub-agent (NO expected outcomes)
      ↓
4. Receives execution plan (raw text artifact)
      ↓
5. Treats plan as observable artifact
      ↓
6. For each expected_outcomes[].assertion:
     - Pass execution plan as Promptfoo variable {{output}}
     - Run assertion via Promptfoo
     - Receive pass/fail
      ↓
7. Aggregate results:
     - PASS → all outcomes satisfied
     - FAIL → any outcome fails
```

## Promptfoo Usage Constraints

Promptfoo MUST:
- Evaluate ONLY execution plan output
- Use only scenario-defined assertions
- NOT receive expected outcomes as hidden ground truth
- Operate purely as a runtime assertion engine

Promptfoo MUST NOT:
- Perform semantic reasoning beyond assertions
- Interpret plan quality holistically
- Infer missing context or intent

Execution plan is passed as variable: `{{output}}`

## Isolation & Security Rules

To ensure evaluation integrity:

**Only judge sub-agent can access**:
- Test scenarios (`tests/benchmark/*.yaml`)
- Expected outcomes
- Promptfoo configuration
- Evaluation logic

**Coding sub-agent MUST NOT access**:
- Expected outcomes
- Test scenario files
- Evaluation logic
- Promptfoo configuration

**No cross-agent leakage** of evaluation criteria is allowed.

## Debugging & Observability

For every evaluation run, the system MUST output:

1. **Raw execution plan** (saved to `.work/evaluate/{scenario-id}-execution-plan.txt`)
2. **Evaluated expected outcomes** (displayed in CLI)
3. **Per-outcome pass/fail results** (logged and displayed)
4. **Promptfoo assertion outputs** (logged)
5. **Final aggregated score** (displayed and logged)

## Key Design Principle

> Generate freely → Evaluate strictly

- **Generation is flexible and unconstrained** (coding sub-agent explores documentation freely)
- **Evaluation is deterministic and outcome-driven** (Promptfoo validates observable behaviors)

## Success Criteria

A test scenario **passes** if and only if:
- ALL expected outcomes are satisfied
- Promptfoo assertions return PASS for all outcomes

A test scenario **fails** if:
- ANY expected outcome is not satisfied
- ANY Promptfoo assertion returns FAIL

Overall evaluation:
- **Success rate**: (scenarios passed / total scenarios)
- **Outcome satisfaction rate**: (outcomes satisfied / total outcomes)

## Error Handling

If coding sub-agent fails:
1. Log the failure
2. Record scenario as FAILED
3. Continue with remaining scenarios
4. Report failure in final summary

If Promptfoo evaluation fails:
1. Log the Promptfoo error
2. Record specific assertion as FAILED
3. Continue with remaining assertions
4. Report failure in final summary

## Logging Requirements

Every run must log to timestamped file (`logs/agentic-docs-evaluate-<timestamp>.log`):
- Command invoked
- Repository path
- Timestamp
- Test scenarios loaded
- For each scenario:
  - Scenario ID and description
  - Coding sub-agent execution (files read, tools used, duration)
  - Execution plan generated (line count)
  - Judge sub-agent evaluation
  - Promptfoo assertions (each assertion result)
  - Scenario result (PASS/FAIL)
  - Duration
- Final aggregate metrics
- Total duration

## Post-Execution Metrics

Display in CLI after evaluation completes:
- **Execution duration**: Total time
- **Scenario statistics**: Total, passed, failed, success rate
- **Outcome statistics**: Total outcomes, satisfied, failed, satisfaction rate
- **Agent execution**: Primary agent, sub-agents spawned, total interactions
- **Documentation access**: Files read, access frequency
- **Tool usage breakdown**: Each tool and invocation count
- **Skill usage breakdown**: Each skill and invocation count (if any)
- **Promptfoo statistics**: Assertions evaluated, passed, failed, success rate

## Logging Implementation

This skill uses **`lib/metrics_logger.py`** for comprehensive logging and metrics:
- Real-time logging to CLI (all agent spawns, tool invocations, data flows logged as they happen)
- Persistent logging to timestamped log file (`logs/agentic-docs-evaluate-{timestamp}.log`)
- Agent execution transparency (primary agent + all sub-agents displayed)
- Data flow tracking (what data moves where between components)
- Post-execution metrics summary (duration, scenarios passed/failed, outcome satisfaction rate, tool usage)
- Metrics JSON export (`logs/agentic-docs-evaluate-{timestamp}.metrics.json`)

See [lib/METRICS_LOGGER_USAGE.md](../../lib/METRICS_LOGGER_USAGE.md) for complete usage guide.

## Final Summary

This evaluation system ensures:
- **No plan-to-plan structural comparison**
- **No structural bias in evaluation**
- **Strict separation of generation vs evaluation**
- **Deterministic validation via Promptfoo**
- **Outcome-based correctness grounded in observable behavior**
- **Complete execution transparency** (all agent interactions visible)
- **Comprehensive logging** (all tools, skills, data flows tracked)
