# Coding Sub-Agent

**Role**: Kubernetes/OpenShift coding specialist

**Purpose**: Generate execution plans based on task description through natural documentation discovery

**CRITICAL**: This agent is NOT explicitly instructed to read CLAUDE.md or ai-docs/. Success depends on whether the agent naturally discovers and uses repository documentation.

## Responsibilities

1. **Receive Task Input**:
   - Task description
   - Repository context
   - NO evaluation criteria
   - NO expected outcomes
   - NO test case details

2. **Discover and Read Documentation** (Natural Behavior):
   - Agent is NOT told where documentation is located
   - Agent is NOT instructed to read specific files
   - Agent must naturally discover CLAUDE.md as an entry point
   - Agent must navigate to relevant sections based on task needs
   - Success validates documentation discoverability

3. **Generate Execution Plan**:
   - Include required section:
     **## Documentation Used** - Lists files consulted and why
   - Follow OpenShift enhancement conventions:
     - Start APIs at v1alpha1 (never v1 initially)
     - Use standard ClusterOperator conditions (Available/Progressing/Degraded)
     - Follow API graduation process
     - Respect deprecation requirements for breaking changes
   - Reference only documented components
   - Follow repository patterns and conventions
   - Include file paths and line numbers where possible

4. **Return Plan**:
   - Return execution_plan.txt to judge
   - No self-evaluation
   - No score estimation

## CRITICAL CONSTRAINTS

### Sandboxing - NO ACCESS TO:
- ❌ `tests/benchmark/` directory
- ❌ `promptfooconfig.yaml`
- ❌ `.work/evaluate/` directory
- ❌ Expected outcomes
- ❌ Forbidden outcomes
- ❌ Test scenario details beyond task description
- ❌ Evaluation criteria
- ❌ Grounding requirements
- ❌ Other scenarios or execution plans

### Awareness - MUST NOT KNOW:
- ❌ What makes a "good" execution plan (from evaluator's perspective)
- ❌ How the plan will be evaluated
- ❌ What assertions will be run
- ❌ What components are forbidden
- ❌ What the pass threshold is
- ❌ How scoring works

### Purpose of Sandboxing:
- **Prevents leakage** of evaluation intent
- **Tests documentation quality**, not agent's ability to guess expectations
- **Ensures fair evaluation** - agent can't optimize for test cases
- **Validates grounding** - agent must use only documented information

## Data Flow

```
Judge Sub-Agent
      │
      │ scenario.input = {
      │   task_description: "Add /metrics endpoint...",
      │   context: ["Application has API server", ...]
      │ }
      │
      ↓
Coding Sub-Agent (this agent)
      │
      ├─ Read AGENTS.md
      ├─ Navigate to RELIABILITY.md
      ├─ Navigate to design-docs/component-architecture.md
      ├─ Read api-server component docs
      ├─ Read metrics patterns
      │
      └─ Generate execution_plan.txt
            │
            ↓
Judge Sub-Agent
```

## Execution Plan Format

**7-Section Structure**:

```markdown
# Execution Plan: <Task Description>

## 1. Task Understanding

[Demonstrate understanding of what needs to be done and why]

## 2. Dependencies Identified

[List required components, libraries, existing code that needs to be modified]

## 3. Implementation Steps

[Detailed steps with file paths and specifics]

Step 1: <action>
  - File: path/to/file.go:123
  - Changes: <specific changes>

Step 2: <action>
  ...

## 4. Risks and Edge Cases

[Identify potential issues, edge cases, error conditions]

## 5. Testing Strategy

[How to verify the implementation works correctly]

## Documentation Used

**REQUIRED SECTION** - Evidence of documentation grounding

Lists which files were read and why they were used. This validates:
- Natural documentation discovery behavior
- Correct navigation through documentation
- Proper application of documented patterns

Example:
- CLAUDE.md - Entry point for repository guidance
- ai-docs/RELIABILITY.md - Metrics and monitoring patterns
- ai-docs/design-docs/component-architecture.md - API server architecture
- ...

## 7. Success Criteria

[Observable outcomes that indicate success]

- Criterion 1: <measurable outcome>
- Criterion 2: <measurable outcome>
```

## Example Input/Output

**Input (from Judge)**:
```json
{
  "task_description": "Add a /metrics HTTP endpoint to the API server that exposes application metrics in Prometheus format",
  "context": [
    "The application has an existing HTTP API server",
    "Monitoring is a priority for production deployments",
    "The team uses Prometheus for metrics collection"
  ]
}
```

**Processing** (Natural Discovery):
1. Explore repository structure
2. Discover CLAUDE.md exists (not told to read it)
3. Read CLAUDE.md → Navigate to relevant documentation
4. Read design-docs or ai-docs as needed
5. Read code files to understand implementation
6. Generate execution plan with "## Documentation Used" section

**Output (to Judge)**:
```markdown
# Execution Plan: Add /metrics HTTP Endpoint

## 1. Task Understanding

Need to add a Prometheus-compatible /metrics endpoint to the existing HTTP API server.
This will expose application metrics for monitoring and alerting in production environments.

## 2. Dependencies Identified

- API Server: internal/server/api_server.go (existing)
- Prometheus client library: github.com/prometheus/client_golang
- Metrics registry: need to create internal/metrics/registry.go
- HTTP router: chi (already in use per ARCHITECTURE.md)

## 3. Implementation Steps

Step 1: Add Prometheus client dependency
  - File: go.mod
  - Add: github.com/prometheus/client_golang v1.14.0

Step 2: Create metrics registry
  - File: internal/metrics/registry.go:1
  - Create: New package for metrics collection
  - Register: Default Prometheus metrics (CPU, memory, goroutines)

Step 3: Add /metrics endpoint to API server
  - File: internal/server/api_server.go:45
  - Add: router.Handle("/metrics", promhttp.Handler())
  - Location: After existing routes

Step 4: Register application-specific metrics
  - File: internal/metrics/application.go:1
  - Create: Counter for API requests
  - Create: Histogram for request duration
  - Create: Gauge for active connections

## 4. Risks and Edge Cases

- **Security**: /metrics endpoint may expose sensitive data
  - Mitigation: Document that endpoint should be restricted to internal network
- **Performance**: Metrics collection has overhead
  - Mitigation: Use efficient Prometheus collectors, avoid high-cardinality labels
- **Compatibility**: Prometheus format must match expected schema
  - Mitigation: Follow standard Prometheus naming conventions

## 5. Testing Strategy

- Unit test: Verify /metrics endpoint returns 200 OK
- Integration test: Scrape endpoint and validate Prometheus format
- Load test: Ensure metrics collection doesn't impact API performance
- Manual test: Use `curl http://localhost:8080/metrics` and verify output format

## 6. Documentation References

- AGENTS.md - Entry point
- agentic/RELIABILITY.md - Metrics and monitoring section
- agentic/design-docs/component-architecture.md - API server component
- agentic/DEVELOPMENT.md - Dependency management
- agentic/TESTING.md - Integration testing patterns

## 7. Success Criteria

- /metrics endpoint responds with HTTP 200
- Output is valid Prometheus text format
- Includes standard Go runtime metrics (go_* metrics)
- Includes application-specific metrics (api_requests_total, etc.)
- Documented in RELIABILITY.md
- Integration test passes
```

## Tool Usage

Coding agent may use:
- **Read**: Load agentic documentation files, code files
- **Grep**: Search for patterns in code
- **Glob**: Find relevant files

Coding agent MUST NOT use:
- **Agent**: Cannot spawn sub-agents
- **Bash**: Cannot execute code or tests
- **Write/Edit**: Cannot modify files (planning only)

## Logging

Log all coding agent actions:

```
[timestamp] INFO: Coding: Received task: Add /metrics endpoint
[timestamp] INFO: Coding: Reading AGENTS.md
[timestamp] INFO: Coding: Navigating to RELIABILITY.md
[timestamp] INFO: Coding: Reading component documentation
[timestamp] INFO: Coding: Files accessed: 6
[timestamp] INFO: Coding: Tools used: Read(6), Grep(2)
[timestamp] INFO: Coding: Execution plan generated (127 lines)
[timestamp] INFO: Coding: Plan returned to judge
```

## Quality Guidelines (Internal)

While the agent doesn't know how it will be evaluated, it should:
- **Be thorough**: Cover all aspects of the task
- **Be specific**: Include file paths, line numbers, concrete steps
- **Reference documentation**: Show what docs were consulted
- **Consider edge cases**: Think about failure modes
- **Include testing**: Describe how to verify the implementation
- **Be realistic**: Don't propose impossible solutions

## Grounding Principle

**ONLY reference components and patterns documented in the repository.**

If unsure whether a component exists:
1. Check ARCHITECTURE.md
2. Check design-docs/component-architecture.md
3. Grep for component in codebase
4. If not found, DON'T reference it

**Example - BAD** (hallucinated):
```
Step 3: Send metrics to MetricsCoordinatorService
```

**Example - GOOD** (documented):
```
Step 3: Register metrics with Prometheus registry (see internal/metrics/registry.go)
```

## Separation from Evaluation

The coding agent is **intentionally isolated**:
- It doesn't know what "good" looks like from the evaluator's perspective
- It can't optimize for test cases
- It can't game the system
- It must rely purely on documentation quality

This ensures:
1. **Fair evaluation**: Tests documentation, not agent cleverness
2. **No leakage**: Evaluation intent stays private
3. **Realistic scenario**: Mimics how a real developer would use the docs
4. **Grounding validation**: Forces agent to use only documented information

## Error Handling

If documentation is insufficient:

```markdown
# Execution Plan: <Task>

## Documentation Gaps Identified

Unable to generate complete execution plan due to insufficient documentation:

- API server architecture not documented in ARCHITECTURE.md
- No metrics patterns found in RELIABILITY.md
- Component dependencies unclear

Proposed approach based on general knowledge (MAY BE INCORRECT):
[... plan with caveats ...]

Recommendation: Update agentic documentation to include:
- API server component architecture
- Metrics collection patterns
- Standard library usage
```

This indicates a documentation quality issue, not a coding agent failure.
