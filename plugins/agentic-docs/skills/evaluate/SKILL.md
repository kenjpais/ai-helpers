---
name: agentic-docs:evaluate
description: "Evaluate documentation quality using behavioral validation with multi-run variance testing, grounding validation, and weighted scoring"
trigger: /agentic-docs:evaluate
---

# Agentic-Docs: Evaluate (v2.0)

**Trigger**: `/agentic-docs:evaluate`  
**Purpose**: Evaluate documentation quality by testing whether execution plans produced from documentation exhibit correct, grounded, and consistent observable behavior

## Core Principle

This system evaluates:

> Would a competent engineer successfully execute this plan?

Validation criteria:
- **Correctness**: Plan produces correct observable outcomes
- **Grounding**: Plan references only documented components (no hallucinations)
- **Feasibility**: Plan is executable and practical
- **Consistency**: Plan produces consistent results across runs
- **Safety**: Plan avoids prohibited behaviors and unsafe recommendations
- **Robustness**: Plan handles edge cases and error conditions
- **Efficiency**: Plan uses documentation effectively
- **Reproducibility**: Results are stable and evaluator drift is monitored

NOT evaluated:
- Structural similarity to reference plans
- Keyword matching
- Length or verbosity
- Stylistic preferences

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
│  • Validates grounding (documented components only)          │
│  • Runs Promptfoo assertions (expected + forbidden)          │
│  • Collects efficiency telemetry                             │
│  • Repeats for multi-run variance testing                    │
│  • Aggregates weighted scores                                │
│  • Determines pass/fail with critical outcome enforcement    │
│                                                               │
│  HAS ACCESS TO: test scenarios, expected outcomes,           │
│                 forbidden outcomes, documentation index      │
│                                                               │
│  NO ACCESS TO: tests/benchmark/ paths (sandboxed)            │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ scenario.input ONLY
                              │ (NO evaluation hints)
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
│                logic, Promptfoo config, tests/benchmark/     │
│                                                               │
│  SANDBOXED: Cannot access filesystem paths containing        │
│             evaluation artifacts                             │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ execution_plan output
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Grounding Validator                                           │
│                                                               │
│  • Extracts component references from execution plan         │
│  • Validates against documented components                   │
│  • Detects hallucinated/fabricated components                │
│  • Detects forbidden component references                    │
│  • Returns grounding validation result                       │
│                                                               │
│  DATA SOURCES: ARCHITECTURE.md, design-docs/components/      │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ grounding_result
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Promptfoo (Assertion Engine)                                 │
│                                                               │
│  DETERMINISTIC ASSERTIONS:                                   │
│    • regex - Pattern matching (100% reproducible)            │
│    • contains - Substring matching (100% reproducible)       │
│    • json-schema - Structure validation (100% reproducible)  │
│    • javascript - Scripted validation (100% reproducible)    │
│    • python - Custom logic (100% reproducible)               │
│                                                               │
│  PROBABILISTIC ASSERTIONS:                                   │
│    • llm-rubric - Semantic evaluation (variance expected)    │
│                                                               │
│  • Evaluates expected_outcomes (must satisfy)                │
│  • Evaluates forbidden_outcomes (must NOT satisfy)           │
│  • Uses assertion diversification (random variants)          │
│  • Returns pass/fail per assertion                           │
│                                                               │
│  LOGS: evaluator model, temperature, prompt version          │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ assertion_results
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Aggregation Engine                                            │
│                                                               │
│  • Calculates weighted score from outcomes                   │
│  • Enforces critical outcome failures                        │
│  • Computes multi-run statistics (pass rate, variance)       │
│  • Detects flaky assertions                                  │
│  • Collects efficiency telemetry (docs relevance, etc.)      │
│  • Stratifies results by category                            │
│  • Validates against calibration set                         │
│  • Determines final scenario result                          │
└──────────────────────────────────────────────────────────────┘
```

**Critical Constraints**:
1. Coding sub-agent is **intentionally unaware** of evaluation criteria
2. Coding sub-agent is **sandboxed** from tests/benchmark/ directory
3. Only judge sub-agent has access to test scenarios and expected outcomes
4. Scenario IDs are opaque (`scenario-NNN`) to prevent intent leakage

## Input

**Repository Path** (optional - defaults to current directory)

```
/agentic-docs:evaluate [<repo-path>]
```

**Optional Flags**:
```
--runs N              # Override runs_per_scenario (default: from scenario config)
--category CATEGORY   # Evaluate only scenarios in category
--calibration-only    # Run only calibration set
```

## Evaluation Schema

See [tests/EVALUATION_SCHEMA.md](../../tests/EVALUATION_SCHEMA.md) for complete schema documentation.

**Key Fields**:
- `expected_outcomes` - Required behaviors (with weight and critical flags)
- `forbidden_outcomes` - Prohibited behaviors (any violation = FAIL)
- `grounding` - Documentation grounding requirements
- `evaluation` - Multi-run config, evaluator settings
- `category` - Scenario category for stratification

## Workflow

### Phase 0: Initialize Evaluation

**Actions**:
1. Create timestamped log file: `logs/agentic-docs-evaluate-<timestamp>.log`
2. Load test scenarios from `tests/benchmark/*.yaml`
3. Load calibration set from `tests/benchmark/calibration/*.yaml`
4. Initialize Promptfoo configuration
5. Load evaluator configuration (model, temperature, prompt version)
6. Display agent architecture and evaluation mode

**Output to CLI**:
```
🧪 Agentic-Docs: Evaluate (Behavioral Validation v2.0)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Repository: <ACTUAL_REPOSITORY_PATH>
Timestamp: <ACTUAL_TIMESTAMP>
Evaluation Mode: Multi-run variance testing
Runs per scenario: <RUNS_PER_SCENARIO>
Test scenarios: <SCENARIO_COUNT> loaded from tests/benchmark/
Calibration set: <CALIBRATION_COUNT> scenarios
Evaluator: <MODEL> (temp=<TEMP>, prompt=<PROMPT_VERSION>)
Log file: <ACTUAL_LOG_PATH>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Assertion Types:
  Deterministic: regex, contains, json-schema, javascript, python
  Probabilistic: llm-rubric (variance expected)

Leakage Resistance:
  ✓ Opaque scenario IDs (scenario-NNN)
  ✓ Coding sub-agent sandboxed from tests/benchmark/
  ✓ No evaluation hints in scenario.input

Enhancements:
  ✓ Multi-run variance testing
  ✓ Grounding validation (hallucination detection)
  ✓ Weighted scoring with critical outcomes
  ✓ Forbidden outcomes
  ✓ Assertion diversification
  ✓ Efficiency telemetry
  ✓ Category stratification
  ✓ Evaluator calibration tracking
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Metrics grounding**: All placeholders MUST be replaced with actual values from current run.

**Logged**:
```
[<TIMESTAMP>] INFO: Command invoked: /agentic-docs:evaluate
[<TIMESTAMP>] INFO: Repository: <REPO_PATH>
[<TIMESTAMP>] INFO: Evaluation mode: multi-run variance testing
[<TIMESTAMP>] INFO: Scenarios loaded: <COUNT> from tests/benchmark/
[<TIMESTAMP>] INFO: Calibration set: <COUNT> scenarios
[<TIMESTAMP>] INFO: Evaluator: model=<MODEL>, temperature=<TEMP>, prompt_version=<VERSION>
```

### Phase 1: Run Calibration Set

**Purpose**: Validate evaluator is functioning correctly before main evaluation

**Actions**:
1. Run calibration scenarios (known-good outputs)
2. Compute calibration accuracy
3. Detect evaluator drift
4. Fail evaluation if calibration fails

**Expected Calibration Pass Rate**: ≥95%

**Output to CLI**:
```
Phase 1: Evaluator Calibration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Calibration set: <COUNT> scenarios
✓ Pass rate: <PASS_RATE>% (expected ≥95%)
✓ Drift detected: <YES/NO>
✓ Evaluator: <MODEL> validated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Logged**:
```
[<TIMESTAMP>] INFO: Calibration started: <COUNT> scenarios
[<TIMESTAMP>] INFO: Calibration complete: pass_rate=<RATE>, expected=0.95
[<TIMESTAMP>] INFO: Drift detected: <YES/NO>
```

**If calibration fails**:
```
❌ Calibration Failed

Pass rate: <RATE>% (expected ≥95%)
Drift detected: YES

The evaluator is not producing consistent results.
This may indicate:
  - Evaluator model changed
  - Prompt version mismatch
  - Temperature setting incorrect

Aborting evaluation until calibration is resolved.
```

### Phase 2: Evaluate Scenarios (Multi-Run)

For each scenario:

#### Step 1: Load Scenario and Select Assertions

**Judge Sub-Agent Actions**:
1. Load scenario from `tests/benchmark/<scenario-id>.yaml`
2. Parse scenario schema (expected_outcomes, forbidden_outcomes, grounding, evaluation config)
3. Select assertion variants (if assertion_variants defined)
4. Prepare scenario.input for coding sub-agent

**Assertion Diversification**:
- If `assertion_variants` defined for outcome, randomly select one variant
- Purpose: Reduce benchmark memorization and keyword gaming

**Example**:
```yaml
# Scenario defines multiple equivalent assertions
assertion_variants:
  includes-testing-strategy:
    - "llm-rubric: The plan includes a testing strategy"
    - "llm-rubric: The plan discusses endpoint validation"
    - "llm-rubric: The plan proposes verification approach"

# Random selection per run:
Run 1: Uses "The plan includes a testing strategy"
Run 2: Uses "The plan discusses endpoint validation"
Run 3: Uses "The plan proposes verification approach"
```

**Output to CLI**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scenario <SCENARIO_ID>/<TOTAL>: <DESCRIPTION>
Category: <CATEGORY>
Runs: <RUNS_PER_SCENARIO>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Logged**:
```
[<TIMESTAMP>] INFO: Scenario <SCENARIO_ID>: <DESCRIPTION> - STARTED
[<TIMESTAMP>] INFO: Judge Sub-Agent: Loading scenario from tests/benchmark/<SCENARIO_ID>.yaml
[<TIMESTAMP>] INFO: Judge Sub-Agent: Scenario loaded - <COUNT> expected outcomes, <COUNT> forbidden outcomes
[<TIMESTAMP>] INFO: Judge Sub-Agent: Runs configured: <RUNS_PER_SCENARIO>
[<TIMESTAMP>] INFO: Judge Sub-Agent: Assertion diversification: <COUNT> variants selected
```

#### Step 2: Execute Runs

**For each run** (1 to `runs_per_scenario`):

**Judge Sub-Agent Actions**:
1. Spawn coding sub-agent in sandboxed environment
2. Send ONLY `scenario.input` (task_description + context)
3. Coding sub-agent generates execution plan
4. Judge receives execution_plan.txt output
5. Save execution plan to `.work/evaluate/<scenario-id>-run-<N>-execution-plan.txt`

**Sandboxing**:
- Coding sub-agent CANNOT access: `tests/benchmark/`, `promptfooconfig.yaml`, `.work/evaluate/`
- Prevents leakage of evaluation intent

**Output to CLI** (per run):
```
Run <RUN_NUM>/<TOTAL>:
  ↳ Spawning coding sub-agent (sandboxed)
  ↳ Generating execution plan...
  ↳ Plan generated (<LINES> lines)
```

**Logged** (per run):
```
[<TIMESTAMP>] INFO: Run <RUN_NUM>/<RUNS_PER_SCENARIO>: Spawning coding sub-agent
[<TIMESTAMP>] INFO: Coding Sub-Agent: Received task: <TASK_DESCRIPTION>
[<TIMESTAMP>] INFO: Coding Sub-Agent: Reading documentation...
[<TIMESTAMP>] INFO: Coding Sub-Agent: Tools used: Read (<COUNT> files), Grep (<COUNT> invocations)
[<TIMESTAMP>] INFO: Coding Sub-Agent: Execution plan generated (<LINES> lines)
[<TIMESTAMP>] INFO: Judge Sub-Agent: Plan saved to .work/evaluate/<SCENARIO_ID>-run-<N>-execution-plan.txt
```

#### Step 3: Validate Grounding

**Judge Sub-Agent Actions**:
1. Extract component references from execution plan
2. Load documented components from ARCHITECTURE.md, design-docs/components/
3. Validate required_components are referenced
4. Validate forbidden_components are NOT referenced
5. Detect hallucinated (undocumented) components
6. Compute grounding metrics

**Output to CLI** (per run):
```
  ↳ Grounding validation...
    • Required components: <SATISFIED>/<TOTAL> ✓
    • Forbidden components: <VIOLATIONS> violations
    • Hallucinated components: <COUNT>
    • Grounding score: <SCORE>%
```

**Grounding FAIL conditions**:
- Required component missing
- Forbidden component referenced
- Hallucinated component detected

**Logged** (per run):
```
[<TIMESTAMP>] INFO: Grounding Validator: Extracting component references from plan
[<TIMESTAMP>] INFO: Grounding Validator: Referenced components: [<LIST>]
[<TIMESTAMP>] INFO: Grounding Validator: Documented components: [<LIST>]
[<TIMESTAMP>] INFO: Grounding Validator: Required components satisfied: <COUNT>/<TOTAL>
[<TIMESTAMP>] INFO: Grounding Validator: Forbidden components violated: <COUNT>
[<TIMESTAMP>] INFO: Grounding Validator: Hallucinated components: [<LIST>]
[<TIMESTAMP>] INFO: Grounding Validator: Result: <PASS/FAIL>
```

#### Step 4: Run Assertions

**Judge Sub-Agent Actions**:
1. Run Promptfoo with execution_plan as variable
2. Evaluate all expected_outcomes assertions
3. Evaluate all forbidden_outcomes assertions
4. Collect pass/fail per assertion
5. Log evaluator responses for llm-rubric assertions

**Deterministic Assertions** (regex, contains, etc):
- Produce identical results across runs
- Binary pass/fail
- No evaluator variance

**Probabilistic Assertions** (llm-rubric):
- May vary across runs (especially with temperature > 0)
- Logged with evaluator model, temperature, raw response
- Variance expected and measured

**Output to CLI** (per run):
```
  ↳ Expected outcomes (<COUNT>):
    ✓ identifies-api-server (weight: 2.0, critical: true)
    ✓ includes-prometheus-library (weight: 1.0)
    ✗ includes-testing-strategy (weight: 1.0)
    ✓ considers-security (weight: 3.0)
    
  ↳ Forbidden outcomes (<COUNT>):
    ✓ invents-metrics-coordinator (PASS - not violated)
    ✗ recommends-exposing-secrets (FAIL - violated!)
```

**Logged** (per run):
```
[<TIMESTAMP>] INFO: Promptfoo: Evaluating <COUNT> expected outcomes
[<TIMESTAMP>] INFO: Promptfoo: Assertion 'identifies-api-server' (llm-rubric) - PASS
[<TIMESTAMP>] INFO: Promptfoo: Evaluator response: "The plan clearly identifies the API server component..."
[<TIMESTAMP>] INFO: Promptfoo: Assertion 'includes-prometheus-library' (llm-rubric) - PASS
[<TIMESTAMP>] INFO: Promptfoo: Assertion 'includes-testing-strategy' (llm-rubric) - FAIL
[<TIMESTAMP>] INFO: Promptfoo: Evaluating <COUNT> forbidden outcomes
[<TIMESTAMP>] INFO: Promptfoo: Forbidden 'invents-metrics-coordinator' (not-contains) - PASS (not violated)
[<TIMESTAMP>] INFO: Promptfoo: Forbidden 'recommends-exposing-secrets' (llm-rubric) - FAIL (violated!)
```

#### Step 5: Collect Efficiency Telemetry

**Purpose**: Measure execution efficiency (telemetry only, not pass/fail)

**Metrics Collected**:
- `docs_relevance_ratio`: Relevant files read / Total files read
- `tool_efficiency_score`: Successful tool calls / Total tool calls
- `hallucinated_file_accesses`: Attempts to read non-existent files
- `context_efficiency`: Unique information / Total information accessed
- `unnecessary_reads`: Files read multiple times or never used

**Logged** (per run):
```
[<TIMESTAMP>] INFO: Efficiency Telemetry:
[<TIMESTAMP>] INFO:   docs_relevance_ratio: <RATIO>
[<TIMESTAMP>] INFO:   tool_efficiency_score: <SCORE>
[<TIMESTAMP>] INFO:   hallucinated_file_accesses: <COUNT>
[<TIMESTAMP>] INFO:   context_efficiency: <RATIO>
[<TIMESTAMP>] INFO:   unnecessary_reads: <COUNT>
```

**Not displayed in CLI** (telemetry only)

#### Step 6: Compute Run Result

**Weighted Score Calculation**:
```
satisfied_weight = sum(weight for outcome in expected_outcomes if outcome.passed)
total_weight = sum(weight for outcome in expected_outcomes)
weighted_score = satisfied_weight / total_weight
```

**Run FAIL Conditions**:
- Any critical outcome failed
- Any forbidden outcome violated
- Grounding validation failed

**Run Result**:
```
if critical_failure or forbidden_violation or grounding_failure:
    run_result = FAIL
elif weighted_score >= pass_threshold:
    run_result = PASS
else:
    run_result = FAIL
```

**Output to CLI** (per run):
```
Run <RUN_NUM> Result:
  Expected outcomes: <SATISFIED>/<TOTAL>
  Weighted score: <SCORE>/<MAX> (<PERCENT>%)
  Critical failures: <COUNT>
  Forbidden violations: <COUNT>
  Grounding: <PASS/FAIL>
  Result: <PASS/FAIL>
```

**Logged** (per run):
```
[<TIMESTAMP>] INFO: Run <RUN_NUM> result: weighted_score=<SCORE>, critical_failures=<COUNT>, forbidden_violations=<COUNT>, grounding=<PASS/FAIL>
[<TIMESTAMP>] INFO: Run <RUN_NUM>: <PASS/FAIL>
```

#### Step 7: Aggregate Multi-Run Results

**After all runs complete**:

**Compute Aggregate Metrics**:
- `pass_rate`: successful_runs / total_runs
- `variance`: Standard deviation of weighted_scores across runs
- `consistency_score`: 1 - (failed_runs / total_runs)
- `flaky_assertions`: Assertions that pass sometimes but not always

**Scenario PASS Criteria**:
```
pass_rate >= scenario.evaluation.pass_threshold
AND
no_critical_failures_in_all_runs
```

**Output to CLI**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scenario <SCENARIO_ID> Aggregate Results:
  Runs: <TOTAL>
  Pass rate: <PASS_COUNT>/<TOTAL> (<PERCENT>%)
  Pass threshold: <THRESHOLD>%
  Weighted score: <AVG_SCORE> ± <VARIANCE>
  Consistency: <CONSISTENCY_SCORE>
  
  Flaky assertions (<COUNT>):
    • includes-testing-strategy (2/3 runs passed)
  
  Scenario result: <PASS/FAIL> ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Logged**:
```
[<TIMESTAMP>] INFO: Scenario <SCENARIO_ID>: Aggregating <COUNT> runs
[<TIMESTAMP>] INFO: Pass rate: <PASS_COUNT>/<TOTAL> (<PERCENT>%)
[<TIMESTAMP>] INFO: Weighted score: avg=<AVG>, variance=<VAR>
[<TIMESTAMP>] INFO: Consistency score: <SCORE>
[<TIMESTAMP>] INFO: Flaky assertions: <COUNT>
[<TIMESTAMP>] INFO: Scenario result: <PASS/FAIL>
[<TIMESTAMP>] INFO: Scenario <SCENARIO_ID>: COMPLETED
```

### Phase 3: Aggregate All Results

**CRITICAL**: Use the display_metrics.py script to show actual results. DO NOT invent metrics.

**Run this command** to display the evaluation summary:
```bash
python lib/display_metrics.py <ACTUAL_METRICS_JSON_PATH>
```

**Stratified Reporting** (by category):
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Evaluation Complete

Duration: <DURATION>

Overall Results:
  Scenarios: <TOTAL>
  Passed: <PASS_COUNT> (<PERCENT>%)
  Failed: <FAIL_COUNT>
  
Category Breakdown:
  api-integration: <PASS>/<TOTAL> (<PERCENT>%)
  concurrency: <PASS>/<TOTAL> (<PERCENT>%)
  security: <PASS>/<TOTAL> (<PERCENT>%)
  refactoring: <PASS>/<TOTAL> (<PERCENT>%)
  
Multi-Run Statistics:
  Average runs per scenario: <AVG_RUNS>
  Average pass rate: <AVG_PASS_RATE>%
  Average consistency: <AVG_CONSISTENCY>%
  Flaky scenarios: <COUNT>

Assertion Statistics:
  Deterministic: <COUNT> assertions (<PASS>/<TOTAL> passed)
  Probabilistic (llm-rubric): <COUNT> assertions (<PASS>/<TOTAL> passed)
  
Grounding Validation:
  Scenarios with grounding checks: <COUNT>
  Grounding failures: <COUNT>
  Hallucinated components detected: <COUNT>

Forbidden Outcomes:
  Scenarios with forbidden checks: <COUNT>
  Forbidden violations: <COUNT>

Efficiency Telemetry (avg):
  docs_relevance_ratio: <RATIO>
  tool_efficiency_score: <SCORE>
  hallucinated_file_accesses: <COUNT>

Evaluator:
  Model: <MODEL>
  Temperature: <TEMP>
  Prompt version: <PROMPT_VERSION>
  Calibration accuracy: <PERCENT>%

Log file: <LOG_PATH>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Metrics grounding**: All values come from actual metrics JSON file. NO INVENTED NUMBERS.

## Leakage Resistance

### Opaque Scenario IDs

**Problem**: Descriptive IDs like `add-monitoring-endpoint` leak evaluation intent

**Solution**: Use opaque IDs like `scenario-014`

**Example**:
```yaml
# Bad: reveals intent
id: "add-monitoring-endpoint"

# Good: opaque
id: "scenario-014"
```

### Sandbox Isolation

**Problem**: Coding sub-agent could access test scenarios

**Solution**: Sandbox coding sub-agent to prevent filesystem access to:
- `tests/benchmark/`
- `promptfooconfig.yaml`
- `.work/evaluate/`

**Implementation**: Judge sub-agent spawns coding sub-agent with restricted filesystem permissions

### Adversarial Scenarios

**Purpose**: Test leakage resistance

**Characteristics**:
- Misleading scenario IDs
- Decoy documentation
- Irrelevant context
- Intentionally ambiguous wording

**Example**:
```yaml
scenario:
  id: "scenario-099"  # Opaque, no hint
  description: "Adversarial leakage resistance test"
  input:
    task_description: "Improve system performance"
    context:
      - "The system uses a message queue"  # Decoy: actually needs caching
      - "Latency is a concern"  # Ambiguous
```

## Assertion Diversification

**Purpose**: Reduce benchmark memorization and keyword gaming

**Implementation**: For each assertion, maintain multiple semantically equivalent phrasings

**Example**:
```yaml
assertion_variants:
  includes-testing-strategy:
    - "llm-rubric: The plan includes a testing strategy"
    - "llm-rubric: The plan discusses endpoint validation"
    - "llm-rubric: The plan proposes verification approach"
    - "llm-rubric: The plan addresses testing considerations"
```

**Evaluation**: Randomly select one variant per run

**Benefits**:
- Prevents overfitting to specific phrasing
- Tests semantic understanding, not keyword matching
- Improves robustness

## Efficiency Telemetry

**Purpose**: Measure execution efficiency without affecting pass/fail

**Metrics**:

### docs_relevance_ratio
```
relevant_files_read / total_files_read
```
- Measures how targeted documentation access is
- Low score indicates excessive exploration
- High score indicates efficient retrieval

### tool_efficiency_score
```
successful_tool_calls / total_tool_calls
```
- Measures tool usage effectiveness
- Low score indicates trial-and-error behavior
- High score indicates precise tool usage

### hallucinated_file_accesses
```
count(read_attempts for non-existent files)
```
- Detects attempts to access fabricated files
- Indicates hallucination or poor documentation understanding

### context_efficiency
```
unique_information_accessed / total_information_accessed
```
- Measures redundancy in information access
- Low score indicates repeated reads of same content
- High score indicates efficient context building

### unnecessary_reads
```
count(files read but not referenced in plan)
```
- Detects irrelevant documentation access
- High count indicates poor retrieval strategy

**Important**: These are telemetry only, NOT pass/fail criteria

## Evaluator Calibration

**Purpose**: Detect evaluator drift and validate scoring consistency

**Calibration Set**: `tests/benchmark/calibration/*.yaml`

**Characteristics**:
- Fixed scenarios with known-good outputs
- Never modified
- Run on every evaluation
- Expected pass rate: ≥95%

**If Calibration Fails**:
```
❌ Calibration Failed

Pass rate: <RATE>% (expected ≥95%)

Possible causes:
  - Evaluator model changed
  - Prompt version mismatch
  - Temperature setting incorrect
  - Evaluator drift detected

Aborting evaluation.
```

**Logged Calibration Metadata**:
```json
{
  "calibration": {
    "scenarios": 10,
    "expected_pass_rate": 0.95,
    "actual_pass_rate": 0.94,
    "drift_detected": false,
    "evaluator": {
      "model": "claude-sonnet-4-6",
      "temperature": 0.0,
      "prompt_version": "v2.1"
    }
  }
}
```

## Error Handling

### Calibration Failure

If calibration pass rate < 95%:
```
❌ Calibration Failed

Pass rate: <RATE>% (expected ≥95%)

Aborting evaluation until calibration is resolved.
```

### Grounding Failure

If grounding validation fails:
```
❌ Grounding Failure: Scenario <SCENARIO_ID>

Hallucinated components:
  • MetricsCoordinatorService (not documented)
  • LegacyMonitoringService (deprecated)

Required components missing:
  • api-server

Scenario result: FAIL
```

### Forbidden Outcome Violation

If forbidden outcome violated:
```
❌ Forbidden Outcome Violated: Scenario <SCENARIO_ID>

Violation: recommends-exposing-secrets
Description: Plan must not recommend exposing sensitive data

Scenario result: FAIL
```

## Success Criteria

Scenario PASS requires:
- ✅ Pass rate ≥ pass_threshold
- ✅ No critical outcome failures
- ✅ No forbidden outcome violations
- ✅ Grounding validation passed
- ✅ No hallucinated components

Evaluation PASS requires:
- ✅ Calibration pass rate ≥95%
- ✅ Overall scenario pass rate ≥70%
- ✅ All categories have ≥50% pass rate

## Metrics Source Table

| Field | Source | Location |
|-------|--------|----------|
| Duration | MetricsLogger.duration_ms | `*.metrics.json`: `duration_ms` field |
| Scenarios | MetricsLogger.details.scenarios | `*.metrics.json`: `details.scenarios` |
| Pass/Fail Counts | MetricsLogger.details.results | `*.metrics.json`: `details.results` |
| Category Breakdown | MetricsLogger.details.categories | `*.metrics.json`: `details.categories` |
| Multi-Run Stats | MetricsLogger.details.multi_run | `*.metrics.json`: `details.multi_run` |
| Grounding Stats | MetricsLogger.details.grounding | `*.metrics.json`: `details.grounding` |
| Evaluator Config | MetricsLogger.details.evaluator | `*.metrics.json`: `details.evaluator` |

## Logging Implementation

Uses **`lib/metrics_logger.py`** for comprehensive logging:
- Real-time logging to CLI
- Persistent logging to `logs/agentic-docs-evaluate-{timestamp}.log`
- Metrics JSON export to `logs/agentic-docs-evaluate-{timestamp}.metrics.json`
- Key decision logging at each phase
- Evaluator metadata logging
- Calibration results logging

See [lib/METRICS_LOGGER_USAGE.md](../../lib/METRICS_LOGGER_USAGE.md) for usage guide.

## Version History

**v2.0** (2026-05-09):
- Added forbidden_outcomes support
- Added grounding validation (hallucination detection)
- Added multi-run variance testing
- Added weighted scoring and critical outcomes
- Added assertion diversification
- Added efficiency telemetry
- Added category stratification
- Added evaluator calibration
- Distinguished deterministic vs probabilistic assertions
- Implemented sandbox isolation
- Implemented opaque scenario IDs
- Enhanced leakage resistance

**v1.0** (2026-05-08):
- Initial behavioral validation framework
- Strict agent separation
- Promptfoo integration
- Expected outcomes only
