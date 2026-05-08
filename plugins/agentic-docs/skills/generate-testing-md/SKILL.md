---
name: generate-testing-md
description: "Generate TESTING.md file for agentic documentation"
trigger: /generate-testing-md
---

# Generate TESTING.md Skill

## Purpose

Generate the `agentic/TESTING.md` file that documents the test strategy, test types, and how to run tests.

## Template

Uses `templates/TESTING.md.template` as the base structure (based on PR #437).

## Input

- Repository path (required)
- Existing agentic/ directory structure (must exist)

## Output

- `agentic/TESTING.md` file
- Logging of data sources used
- Line count verification

## Data Sources

This skill reads from the following repository files:
- `templates/TESTING.md.template` (template file)
- test/ or tests/ directories
- Makefile (test targets)
- CI configuration (.github/workflows/, .gitlab-ci.yml, Jenkinsfile)
- Test files (*_test.go, test_*.py, *.test.ts, *_spec.rb)
- Coverage configuration (.coveragerc, jest.config.js)
- Test fixtures (testdata/, fixtures/)
- E2E test directories

## Workflow

### 1. Verify Prerequisites

```bash
# Check that agentic/ directory exists
if [ ! -d "agentic/" ]; then
  echo "ERROR: agentic/ directory not found. Run structure generator first."
  exit 1
fi
```

### 2. Read Data Sources

**Log**: "Reading test-related files..."

Read the following:
- test/ or tests/ directory structure
- Makefile test targets
- CI/CD workflow files
- Sample test files (to identify test frameworks)
- Coverage configuration

### 3. Generate TESTING.md Content

**Prompt**:
```
Based on the repository test structure and CI configuration:

Generate agentic/TESTING.md covering:

1. **Test Strategy**
   - Test pyramid (unit, integration, e2e breakdown)
   - Test coverage goals
   - Testing philosophy

2. **Test Types**
   - Unit tests (scope, frameworks, location)
   - Integration tests (what they cover)
   - End-to-end tests (scenarios covered)
   - Performance tests (if applicable)

3. **Running Tests**
   - Run all tests: make test command
   - Run specific test suite
   - Run single test file or function
   - Parallel test execution
   - Test output interpretation

4. **Test Coverage**
   - Coverage by component/package
   - How to generate coverage reports
   - Coverage thresholds
   - Coverage gaps

5. **Test Fixtures and Mocks**
   - Test data location (testdata/, fixtures/)
   - Mock patterns used
   - Fixture setup and teardown

6. **CI/CD Test Pipeline**
   - Tests run on PR
   - Tests run on merge
   - Nightly/scheduled tests
   - Test failure handling

7. **Writing Tests**
   - Test file naming conventions
   - Test structure patterns
   - Assertion libraries used
   - Best practices

8. **Debugging Test Failures**
   - Common failure modes
   - Viewing test logs
   - Running tests in debug mode

Use clear examples. Target ~320 lines.

Data sources: test/, Makefile, CI configs
```

### 4. Write File

Write generated content to `agentic/TESTING.md`

**Log**:
- File created: `agentic/TESTING.md`
- Lines generated: [count]
- Data sources used: [list]
- Test frameworks detected: [list]

### 5. Validate Output

Check that:
- File was created successfully
- Test strategy section present
- Test running commands included
- Coverage information present

## Logging

Every run must log:
- **Timestamp**: ISO 8601 format
- **Data sources**: List of files read
- **Lines generated**: Final line count
- **Tools used**: read, write, bash (for analyzing test structure)
- **Skill invoked**: generate-testing-md
- **Test frameworks detected**: e.g., pytest, go test, jest
- **Duration**: Time taken in seconds

## Error Handling

- If agentic/ directory doesn't exist: Fail with clear error message
- If no test/ directory found: Generate minimal template with TODO placeholders
- If Makefile has no test target: Infer from CI configuration

## Success Criteria

- ✅ agentic/TESTING.md created
- ✅ File contains 150-500 lines
- ✅ All sections present (Strategy, Types, Running, Coverage, Fixtures, CI, Writing, Debugging)
- ✅ Test commands extracted from Makefile
- ✅ Test frameworks identified
- ✅ Data sources logged
