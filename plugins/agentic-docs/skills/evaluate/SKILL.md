---
name: agentic-docs:evaluate
description: "Test documentation quality with coding scenarios using transparent multi-agent execution"
trigger: /agentic-docs:evaluate
---

# Agentic-Docs: Evaluate

**Trigger**: `/agentic-docs:evaluate`  
**Purpose**: Test documentation quality using coding scenarios with full execution transparency

## Overview

Tests agentic documentation by spawning coding sub-agents with benchmark tasks. Displays complete execution flow, agent interactions, and data flow between components.

## Input

**Repository Path** (optional - defaults to current directory)

```
/agentic-docs:evaluate [<repo-path>]
```

## Workflow

### Phase 0: Initialize Evaluation

**Output to CLI**:
```
🧪 Agentic-Docs: Evaluate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Repository: /path/to/repo
Timestamp: 2026-05-08 14:40:15
Benchmark tasks: 16
Log file: logs/agentic-docs-evaluate-2026-05-08-14-40-15.log
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Agent Architecture:
  Primary Agent: Main Orchestrator
  Sub-Agents:
    • Coding Sub-Agent (generates execution plans)
    • Judge Sub-Agent (evaluates plans)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 1: Execute Benchmark Tasks

For each benchmark task (16 total):

**Step 1: Display Task**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Task 1/16: Add Monitoring Endpoint
Category: feature-development
Difficulty: medium
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Step 2: Spawn Coding Sub-Agent**
```
→ Spawning Coding Sub-Agent
  Agent ID: coding-agent-001
  Task: Generate execution plan for "Add Monitoring Endpoint"
  Input: task.md, agentic documentation
  Expected Output: 7-section execution plan
```

**Step 3: Show Execution Flow**
```
Coding Sub-Agent Execution Flow:
  1. Read task.md → "Add /metrics endpoint with Prometheus format"
  2. Navigate to AGENTS.md → Entry point loaded
  3. Follow link to RELIABILITY.md → Monitoring section found
  4. Follow link to component-architecture.md → API server identified
  5. Retrieve design-docs/components/api-server.md → Implementation details
  6. Generate execution plan → 7 sections completed
```

**Step 4: Log Data Flow**
```
Data Flow:
  task.md ─────────────────────────> Coding Sub-Agent
  AGENTS.md ────────────────────────> Coding Sub-Agent
  RELIABILITY.md ───────────────────> Coding Sub-Agent
  component-architecture.md ────────> Coding Sub-Agent
  design-docs/components/api-server.md > Coding Sub-Agent
                                          │
                                          ↓
                                    execution_plan.md
                                          │
                                          ↓
                                    Judge Sub-Agent
```

**Step 5: Spawn Judge Sub-Agent**
```
→ Spawning Judge Sub-Agent
  Agent ID: judge-agent-001
  Task: Evaluate execution plan quality
  Input: execution_plan.md, expected_plan.md
  Expected Output: Score (0-35)
```

**Step 6: Show Judge Evaluation**
```
Judge Sub-Agent Evaluation:
  1. Task Understanding: 5/5 ✓
  2. Dependencies Identified: 4/5
  3. Implementation Steps: 5/5 ✓
  4. Risks and Edge Cases: 4/5
  5. Testing Strategy: 5/5 ✓
  6. Documentation References: 5/5 ✓
  7. Success Criteria: 4/5
  
  Total Score: 32/35 ✓ PASS (threshold: 25)
```

**Step 7: Task Results**
```
✅ Task 1/16: PASS (32/35)
Duration: 45.3s
Tools Used:
  • read (5 files)
  • Agent spawn (2 sub-agents)
Skills Used:
  • generate-execution-plan
  • evaluate-execution-plan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 2: Aggregate Results

**Output to CLI**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Evaluation Complete

Results by Category:
  Feature Development: 4/4 tasks PASS
  Bug Fixes: 3/4 tasks PASS
  Refactoring: 4/4 tasks PASS
  Reliability: 4/4 tasks PASS

Overall: 15/16 tasks PASS (93.75%)

Average Score: 30.2/35 (86.3%)

Agent Execution Summary:
  Primary Agent: 1 instance
  Coding Sub-Agents spawned: 16 instances
  Judge Sub-Agents spawned: 16 instances
  Total agent interactions: 48

Tools Used Across All Tasks:
  • read: 247 invocations
  • Agent spawn: 32 invocations
  • bash: 12 invocations

Skills Used Across All Tasks:
  • generate-execution-plan: 16 invocations
  • evaluate-execution-plan: 16 invocations
  • retrieve-from-docs: 85 invocations

Total Duration: 12m 18s
Log file: logs/agentic-docs-evaluate-2026-05-08-14-40-15.log
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Agent Interaction Diagram

For each task, display the interaction flow:

```
Main Orchestrator
      │
      ├─> Spawn Coding Sub-Agent
      │        │
      │        ├─> Read task.md
      │        ├─> Navigate AGENTS.md
      │        ├─> Retrieve docs (3 files)
      │        ├─> Generate plan
      │        │
      │        └─> Return: execution_plan.md
      │
      ├─> Receive execution_plan.md
      │
      ├─> Spawn Judge Sub-Agent
      │        │
      │        ├─> Read execution_plan.md
      │        ├─> Read expected_plan.md
      │        ├─> Compare & score
      │        │
      │        └─> Return: score (32/35)
      │
      └─> Aggregate results
```

## Logging Requirements

### Timestamped Log File

```
[2026-05-08 14:40:15] INFO: Command invoked: /agentic-docs:evaluate
[2026-05-08 14:40:15] INFO: Repository: /path/to/repo
[2026-05-08 14:40:15] INFO: Benchmark tasks: 16
[2026-05-08 14:40:15] INFO: Primary Agent: Main Orchestrator
[2026-05-08 14:40:15] INFO: Sub-Agent Types: Coding, Judge
[2026-05-08 14:40:16] INFO: Task 1/16: Add Monitoring Endpoint - STARTED
[2026-05-08 14:40:16] INFO: Spawning Coding Sub-Agent (ID: coding-agent-001)
[2026-05-08 14:40:18] INFO: Data flow: task.md → Coding Sub-Agent
[2026-05-08 14:40:20] INFO: Data flow: AGENTS.md → Coding Sub-Agent
[2026-05-08 14:40:25] INFO: Data flow: RELIABILITY.md → Coding Sub-Agent
[2026-05-08 14:40:30] INFO: Coding Sub-Agent completed: execution_plan.md
[2026-05-08 14:40:30] INFO: Data flow: execution_plan.md → Judge Sub-Agent
[2026-05-08 14:40:30] INFO: Spawning Judge Sub-Agent (ID: judge-agent-001)
[2026-05-08 14:40:55] INFO: Judge Sub-Agent score: 32/35
[2026-05-08 14:40:55] INFO: Task 1/16: PASS (32/35) - Duration: 45.3s
[2026-05-08 14:40:55] INFO: Tools used: read (5), Agent (2)
[2026-05-08 14:40:55] INFO: Skills used: generate-execution-plan, evaluate-execution-plan
...
[2026-05-08 14:52:33] INFO: Evaluation completed
[2026-05-08 14:52:33] INFO: Overall result: 15/16 PASS (93.75%)
[2026-05-08 14:52:33] INFO: Total duration: 12m 18s
```

## Transparent Execution

**Key Principle**: Full visibility into agent execution and data flow

**For each task, explicitly display**:
1. Primary agent role
2. Sub-agents spawned (with IDs)
3. Execution flow (step-by-step)
4. Data flow (what data moves where)
5. Tools invoked
6. Skills used
7. Agent interactions
8. Results and scores

**No hidden agent operations** - All agent activities logged and displayed.
