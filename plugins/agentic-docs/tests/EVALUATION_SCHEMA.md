# Evaluation Framework Schema

**Version**: 2.0  
**Purpose**: Define the complete schema for agentic-docs evaluation scenarios

## Schema Overview

```yaml
scenario:
  id: string                    # Opaque identifier (e.g., "scenario-014")
  description: string           # Human-readable description
  category: string              # Scenario category for stratification
  input:
    task_description: string    # Task given to coding sub-agent
    context: string[]           # Contextual information
  
  expected_outcomes:            # Required behaviors
    - id: string
      description: string
      assertion: string         # Assertion type and definition
      weight: number            # Optional: scoring weight (default: 1)
      critical: boolean         # Optional: auto-fail if violated (default: false)
  
  forbidden_outcomes:           # NEW: Prohibited behaviors
    - id: string
      description: string
      assertion: string         # Must NOT satisfy this
  
  grounding:                    # NEW: Documentation grounding validation
    required_components: string[]    # Components that must be referenced
    forbidden_components: string[]   # Components that must NOT be referenced
    
  evaluation:                   # NEW: Evaluation configuration
    runs_per_scenario: number   # Number of runs for variance testing (default: 1)
    pass_threshold: number      # Required pass rate (default: 1.0)
    evaluator:
      model: string             # LLM model for rubric assertions
      temperature: number       # Temperature setting
      prompt_version: string    # Rubric prompt version
```

## Assertion Types

### Deterministic Assertions

**regex**: Pattern matching
```yaml
assertion: "regex: /metrics.*Prometheus/"
```

**contains**: Substring matching
```yaml
assertion: "contains: implements HTTP handler"
```

**json-schema**: Structured data validation
```yaml
assertion: "json-schema: { required: ['component', 'implementation'] }"
```

**javascript**: Custom scripted validation
```yaml
assertion: "javascript: output.includes('mutex') && output.includes('synchronization')"
```

**python**: Custom Python validation
```yaml
assertion: "python: 'race detector' in output.lower()"
```

### Probabilistic Assertions

**llm-rubric**: Semantic evaluation using LLM
```yaml
assertion: "llm-rubric: The execution plan identifies the API server component"
```

**Characteristics**:
- Non-deterministic (varies across runs)
- Depends on evaluator model/temperature
- May produce different scores for identical input
- Requires calibration and variance testing

## Field Definitions

### scenario.id

**Format**: `scenario-NNN` (opaque numeric identifier)

**Purpose**: Prevent leakage of evaluation intent to coding agents

**Example**:
```yaml
id: "scenario-014"  # Good: opaque
id: "add-monitoring-endpoint"  # Bad: reveals intent
```

### scenario.category

**Purpose**: Enable stratified reporting by capability type

**Categories**:
- `architecture-reasoning` - Architectural analysis and design
- `dependency-resolution` - Understanding and managing dependencies
- `security` - Security considerations and threat modeling
- `migration-planning` - Migration and upgrade strategies
- `retrieval` - Information retrieval from documentation
- `api-integration` - API design and integration
- `concurrency` - Concurrency and synchronization
- `refactoring` - Code refactoring and cleanup
- `testing` - Test strategy and implementation
- `performance` - Performance optimization

**Example**:
```yaml
category: "security"
```

### expected_outcomes.weight

**Purpose**: Allow differential importance scoring

**Default**: 1.0

**Example**:
```yaml
- id: "considers-security"
  weight: 5.0        # 5x more important than weight=1 outcomes
  critical: false
```

**Scoring**:
```
weighted_score = sum(satisfied_weight) / sum(total_weight)
```

### expected_outcomes.critical

**Purpose**: Define outcomes that must pass for scenario success

**Default**: false

**Evaluation Rule**:
- If `critical: true` and outcome FAILS → scenario FAILS (regardless of other outcomes)
- Non-critical outcomes contribute to weighted score

**Example**:
```yaml
- id: "includes-security-validation"
  critical: true     # Scenario fails if this outcome fails
```

### forbidden_outcomes

**Purpose**: Detect hallucinations, contradictions, and unsafe recommendations

**Evaluation Rule**:
- Any forbidden outcome violation → scenario FAILS
- Treated as more severe than missing expected outcomes

**Example**:
```yaml
forbidden_outcomes:
  - id: "invents-nonexistent-service"
    description: "Plan must not reference fabricated MetricsCoordinatorService"
    assertion: "not-contains: MetricsCoordinatorService"
  
  - id: "recommends-unsafe-approach"
    description: "Plan must not recommend disabling security features"
    assertion: "llm-rubric: The plan does NOT recommend disabling authentication or security controls"
```

### grounding.required_components

**Purpose**: Validate that plan references documented architectural components

**Validation**:
- Extract components referenced in execution plan
- Check each against documentation (ARCHITECTURE.md, design-docs/components/)
- Flag undocumented references as hallucinations

**Example**:
```yaml
grounding:
  required_components:
    - "api-server"
    - "metrics-registry"
```

### grounding.forbidden_components

**Purpose**: Detect references to non-existent or deprecated components

**Example**:
```yaml
grounding:
  forbidden_components:
    - "legacy-auth-service"      # Removed in v2.0
    - "MetricsCoordinatorService" # Never existed
```

### evaluation.runs_per_scenario

**Purpose**: Measure consistency and detect flaky assertions

**Default**: 1

**Recommended**: 3-5 for production evaluation

**Metrics Collected**:
- Pass rate: `successful_runs / total_runs`
- Variance: Standard deviation across runs
- Consistency score: `1 - (failed_runs / total_runs)`
- Flaky assertions: Assertions that pass sometimes but not always

**Example**:
```yaml
evaluation:
  runs_per_scenario: 5
  pass_threshold: 0.8  # Require 80% pass rate (4/5 runs)
```

### evaluation.evaluator

**Purpose**: Track evaluator configuration for reproducibility

**Fields**:
- `model`: LLM model used for llm-rubric assertions
- `temperature`: Temperature setting (affects variance)
- `prompt_version`: Version of rubric evaluation prompt

**Logged Metadata**:
```json
{
  "evaluator": {
    "model": "claude-sonnet-4-6",
    "temperature": 0.0,
    "prompt_version": "v2.1",
    "timestamp": "2026-05-09T10:30:00Z"
  }
}
```

## Complete Example

```yaml
scenario:
  id: "scenario-014"
  description: "Add monitoring endpoint with Prometheus format"
  category: "api-integration"
  
  input:
    task_description: "Add a /metrics HTTP endpoint to the API server that exposes application metrics in Prometheus format"
    context:
      - "The application has an existing HTTP API server"
      - "Monitoring is a priority for production deployments"
      - "The team uses Prometheus for metrics collection"
  
  expected_outcomes:
    - id: "identifies-api-server"
      description: "Plan identifies API server component"
      assertion: "llm-rubric: The execution plan identifies the API server component"
      weight: 2.0
      critical: true
    
    - id: "includes-prometheus-library"
      description: "Plan includes Prometheus client library"
      assertion: "llm-rubric: The execution plan includes adding a Prometheus client library"
      weight: 1.0
      critical: false
    
    - id: "considers-security"
      description: "Plan considers security implications"
      assertion: "llm-rubric: The execution plan mentions security considerations"
      weight: 3.0
      critical: false
  
  forbidden_outcomes:
    - id: "invents-metrics-service"
      description: "Plan must not reference non-existent MetricsCoordinatorService"
      assertion: "not-contains: MetricsCoordinatorService"
    
    - id: "recommends-exposing-secrets"
      description: "Plan must not recommend exposing sensitive data in metrics"
      assertion: "llm-rubric: The plan does NOT recommend exposing passwords, tokens, or API keys in metrics"
  
  grounding:
    required_components:
      - "api-server"
    forbidden_components:
      - "MetricsCoordinatorService"
      - "legacy-monitoring-service"
  
  evaluation:
    runs_per_scenario: 3
    pass_threshold: 0.67  # Require 2/3 runs to pass
    evaluator:
      model: "claude-sonnet-4-6"
      temperature: 0.0
      prompt_version: "v2.1"
```

## Evaluation Semantics

### Deterministic vs Probabilistic Assertions

**Deterministic Assertions** (regex, contains, json-schema, scripted):
- Produce identical results across runs
- Binary pass/fail
- Fast evaluation
- No evaluator model required

**Probabilistic Assertions** (llm-rubric):
- May vary across runs (especially with temperature > 0)
- Depend on evaluator model and prompt
- Slower evaluation
- Require calibration

### Evaluation Flow

1. **Load scenario** from YAML
2. **For each run** (1 to `runs_per_scenario`):
   - Spawn isolated coding sub-agent
   - Pass `input.task_description` and `input.context`
   - Capture execution plan output
   - Evaluate all expected outcomes
   - Evaluate all forbidden outcomes
   - Validate grounding
   - Record run result
3. **Aggregate results**:
   - Compute pass rate
   - Check critical failures
   - Calculate weighted score
   - Detect flaky assertions
4. **Determine scenario result**:
   - FAIL if any critical outcome fails
   - FAIL if any forbidden outcome violated
   - FAIL if grounding validation fails
   - FAIL if pass_rate < pass_threshold
   - PASS otherwise

### Scoring Formula

```
# Weighted satisfaction rate
weighted_score = sum(satisfied_outcome.weight) / sum(all_outcomes.weight)

# Scenario pass criteria
scenario_pass = (
  no_critical_failures AND
  no_forbidden_violations AND
  grounding_valid AND
  pass_rate >= pass_threshold
)
```

## Assertion Diversification

**Purpose**: Reduce benchmark memorization and keyword gaming

**Implementation**: For each assertion ID, maintain multiple semantically equivalent phrasings

**Example**:
```yaml
# Assertion pool for "includes-testing-strategy"
assertions:
  - "llm-rubric: The execution plan includes a strategy for testing the endpoint"
  - "llm-rubric: The plan discusses how to validate endpoint behavior"
  - "llm-rubric: The plan proposes endpoint verification approach"
  - "llm-rubric: The plan includes metrics endpoint testing considerations"
```

**Evaluation**: Randomly select one variant per run

## Efficiency Metrics (Telemetry Only)

**Purpose**: Measure execution efficiency without affecting pass/fail

**Metrics**:
- `docs_relevance_ratio`: Relevant files read / Total files read
- `tool_efficiency_score`: Successful tool calls / Total tool calls
- `hallucinated_file_accesses`: File reads for non-existent files
- `context_efficiency`: Unique information accessed / Total information accessed
- `unnecessary_reads`: Files read multiple times or never used

**Logged** but NOT used for scenario pass/fail decisions

## Calibration Set

**Purpose**: Detect evaluator drift and validate scoring consistency

**Location**: `tests/benchmark/calibration/`

**Characteristics**:
- Fixed scenarios with known-good outputs
- Never modified
- Run on every evaluation
- Expected pass rate: ≥95%

**Calibration Metrics**:
```json
{
  "calibration": {
    "scenarios": 10,
    "expected_pass_rate": 0.95,
    "actual_pass_rate": 0.94,
    "drift_detected": false
  }
}
```

## Version History

**v2.0** (2026-05-09):
- Added forbidden_outcomes
- Added grounding validation
- Added multi-run variance testing
- Added weighted scoring and critical outcomes
- Added evaluator versioning
- Added assertion diversification
- Added efficiency telemetry
- Added category stratification
- Renamed scenario IDs to opaque format

**v1.0** (2026-05-08):
- Initial schema with expected_outcomes
- llm-rubric assertions only
