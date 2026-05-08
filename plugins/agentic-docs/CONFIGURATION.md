# Agentic-Docs Plugin Configuration Guide

This guide explains how to configure the agentic-docs plugin validation behavior.

## Configuration File Location

```
plugins/agentic-docs/config/validation.yaml
```

**Important**: The validation agent **CANNOT** modify this file. You must edit it directly to change validation behavior.

## Quick Start

### 1. View Current Configuration

```bash
cat plugins/agentic-docs/config/validation.yaml
```

### 2. Edit Configuration

```bash
# Use your preferred editor
vim plugins/agentic-docs/config/validation.yaml

# Or
code plugins/agentic-docs/config/validation.yaml
```

### 3. Run Validation

```bash
# Validation will use your updated configuration
/agentic-docs:validate
```

## Configuration Parameters

### Navigation Constraints

Controls how agents navigate through documentation.

```yaml
navigation:
  max_hops: 3              # Maximum hops from AGENTS.md to any information
  entry_point: "AGENTS.md" # Primary entry point for navigation
```

**When to change**:
- **Increase `max_hops`** (4-5): For very large repositories with deep component hierarchies
- **Decrease `max_hops`** (2): For small repositories requiring tighter navigation

**Example**:
```yaml
navigation:
  max_hops: 4  # Allow 4 hops for large repository
```

---

### Line Budget Constraints

Enforces line limits on documentation files to keep them concise.

```yaml
line_budget:
  agents_md: 150         # Maximum lines for AGENTS.md
  component_docs: 100    # Maximum lines per component doc
  concept_docs: 75       # Maximum lines per concept doc
  query_responses: 500   # Maximum lines for query responses
```

**When to change**:
- **Increase limits**: If your documentation is legitimately detailed
- **Decrease limits**: To enforce stricter conciseness

**Example - Relax Limits**:
```yaml
line_budget:
  agents_md: 200         # Allow longer navigation file
  component_docs: 150    # Allow longer component docs
  concept_docs: 100      # Allow longer concept docs
```

**Example - Stricter Limits**:
```yaml
line_budget:
  agents_md: 100         # Enforce tighter navigation
  component_docs: 75     # Keep components very concise
  concept_docs: 50       # Keep concepts very short
```

---

### Directory Structure

Defines required directories and files.

```yaml
directory_structure:
  required_dirs:
    - "agentic"
    - "agentic/design-docs"
    - "agentic/design-docs/components"
    # ... (13 total)
  
  required_files:
    root:
      - "AGENTS.md"
      - "ARCHITECTURE.md"
    agentic:
      - "DESIGN.md"
      - "DEVELOPMENT.md"
      # ... (6 core files)
```

**When to change**:
- **Add directories**: For project-specific documentation structure
- **Remove directories**: For minimal repositories
- **Add files**: For additional required documentation

**Example - Add Custom Directory**:
```yaml
directory_structure:
  required_dirs:
    - "agentic"
    - "agentic/design-docs"
    - "agentic/custom-docs"  # Your custom directory
    # ...
```

**Example - Add Required File**:
```yaml
directory_structure:
  required_files:
    root:
      - "AGENTS.md"
      - "ARCHITECTURE.md"
    agentic:
      - "DESIGN.md"
      - "DEVELOPMENT.md"
      - "DEPLOYMENT.md"  # Your custom required file
```

---

### Quality Score Thresholds

Controls quality score calculation and pass/fail threshold.

```yaml
quality_score:
  minimum_score: 70      # Minimum quality score to pass (0-100)
  coverage_weight: 40    # Coverage points (≥80% components documented)
  freshness_weight: 20   # Freshness points (updated <90 days)
  completeness_weight: 20 # Completeness points (all required files)
  linkage_weight: 10     # Linkage points (no broken links)
  navigation_weight: 10  # Navigation points (≤3 hop depth)
```

**When to change**:
- **Lower `minimum_score`**: For work-in-progress documentation
- **Raise `minimum_score`**: For stricter quality requirements
- **Adjust weights**: To prioritize different quality aspects

**Example - Stricter Quality**:
```yaml
quality_score:
  minimum_score: 80      # Require higher quality
  coverage_weight: 50    # Emphasize coverage more
  freshness_weight: 15   # Relax freshness requirement
```

**Example - Relaxed Quality (WIP)**:
```yaml
quality_score:
  minimum_score: 50      # Allow lower quality for WIP
  coverage_weight: 30    # Relax coverage requirement
  completeness_weight: 30 # Still require files
```

---

### Validation Checks

Enable/disable specific validation checks.

```yaml
validation_checks:
  check_directory_structure: true  # Check required dirs/files
  check_navigation_depth: true     # Check ≤3 hops
  check_line_budgets: true         # Check line limits
  check_broken_links: true         # Check for broken links
  check_coverage: true             # Check component coverage
  check_frontmatter: true          # Check frontmatter fields
  check_file_naming: true          # Check naming conventions
  check_quality_score: true        # Calculate quality score
```

**When to change**:
- **Disable checks**: To skip specific validations temporarily
- **Enable all checks**: For comprehensive validation

**Example - Disable Frontmatter Check**:
```yaml
validation_checks:
  check_frontmatter: false  # Skip frontmatter validation
  # ... (other checks remain enabled)
```

**Example - Quick Validation (Structure Only)**:
```yaml
validation_checks:
  check_directory_structure: true  # Only check structure
  check_navigation_depth: false
  check_line_budgets: false
  check_broken_links: false
  check_coverage: false
  check_frontmatter: false
  check_file_naming: false
  check_quality_score: false
```

---

### File Naming Conventions

Controls file naming format validation.

```yaml
naming_conventions:
  format: "kebab-case"  # File naming format
  allowed_extensions:
    - ".md"
    - ".json"
    - ".yaml"
```

**Options for `format`**:
- `kebab-case`: my-file-name.md
- `snake_case`: my_file_name.md
- `camelCase`: myFileName.md
- `PascalCase`: MyFileName.md

**Example - Allow More Extensions**:
```yaml
naming_conventions:
  format: "kebab-case"
  allowed_extensions:
    - ".md"
    - ".json"
    - ".yaml"
    - ".txt"    # Allow .txt files
    - ".adoc"   # Allow AsciiDoc files
```

---

### Coverage Requirements

Controls component/concept coverage thresholds.

```yaml
coverage:
  minimum_component_coverage: 0.8  # 80% of components must be documented
  minimum_concept_coverage: 0.7    # 70% of concepts must be documented
```

**When to change**:
- **Lower coverage**: For partial documentation efforts
- **Raise coverage**: For comprehensive documentation

**Example - Require Full Coverage**:
```yaml
coverage:
  minimum_component_coverage: 1.0  # 100% components documented
  minimum_concept_coverage: 1.0    # 100% concepts documented
```

---

### Freshness Requirements

Controls documentation age validation.

```yaml
freshness:
  max_age_days: 90  # Maximum age for documentation freshness
```

**When to change**:
- **Increase**: For stable projects with infrequent updates
- **Decrease**: For fast-moving projects

**Example - Stable Project**:
```yaml
freshness:
  max_age_days: 180  # Allow 6-month-old docs
```

**Example - Fast-Moving Project**:
```yaml
freshness:
  max_age_days: 30   # Require monthly updates
```

---

### Logging Configuration

Controls validation logging behavior.

```yaml
logging:
  level: "INFO"              # Logging level (DEBUG, INFO, WARNING, ERROR)
  output_format: "structured" # Log format (structured, plain)
  save_logs: true            # Save logs to file
  log_directory: "logs"      # Directory for log files
```

**When to change**:
- **Debug validation issues**: Set `level: "DEBUG"`
- **Reduce log verbosity**: Set `level: "WARNING"`
- **Change log location**: Update `log_directory`

**Example - Debug Mode**:
```yaml
logging:
  level: "DEBUG"             # Verbose logging
  output_format: "structured"
  save_logs: true
  log_directory: "logs"
```

---

## Common Configuration Scenarios

### Scenario 1: Large Repository

For repositories with many components and deep hierarchies:

```yaml
navigation:
  max_hops: 4  # Allow deeper navigation

line_budget:
  agents_md: 200         # Allow longer navigation
  component_docs: 150    # Allow detailed components
  concept_docs: 100      # Allow detailed concepts

quality_score:
  minimum_score: 70      # Standard quality threshold
```

### Scenario 2: Work-in-Progress Documentation

For documentation still being developed:

```yaml
quality_score:
  minimum_score: 50  # Lower threshold for WIP

coverage:
  minimum_component_coverage: 0.5  # 50% coverage OK for now
  minimum_concept_coverage: 0.5    # 50% coverage OK for now

validation_checks:
  check_broken_links: false  # Skip broken link check (many WIP)
  check_freshness: false     # Skip freshness check
```

### Scenario 3: Strict Quality Enforcement

For production-ready documentation:

```yaml
navigation:
  max_hops: 2  # Enforce tight navigation

line_budget:
  agents_md: 100         # Enforce conciseness
  component_docs: 75     # Keep components brief
  concept_docs: 50       # Keep concepts very brief

quality_score:
  minimum_score: 85      # High quality requirement
  coverage_weight: 50    # Emphasize coverage

coverage:
  minimum_component_coverage: 0.95  # 95% coverage required
  minimum_concept_coverage: 0.90    # 90% coverage required

freshness:
  max_age_days: 30  # Require monthly updates
```

### Scenario 4: Minimal Validation

For quick structure checks only:

```yaml
validation_checks:
  check_directory_structure: true  # Only check structure
  check_navigation_depth: false
  check_line_budgets: false
  check_broken_links: false
  check_coverage: false
  check_frontmatter: false
  check_file_naming: false
  check_quality_score: false

quality_score:
  minimum_score: 0  # No quality threshold
```

---

## Configuration Immutability

**CRITICAL**: The validation agent **CANNOT** modify `config/validation.yaml` during execution.

### Immutability Enforcement

The validation process:
1. Loads `config/validation.yaml` at start
2. Computes SHA256 hash of configuration
3. Verifies hash before each validation phase
4. **Fails** if configuration has been modified

### Why Immutability?

- **Prevents agent manipulation**: Agent cannot relax constraints to pass validation
- **Ensures consistency**: Same configuration throughout validation run
- **Audit trail**: Configuration changes are explicit user edits

### How to Change Configuration

```bash
# 1. Stop any running validation
# 2. Edit the configuration file
vim plugins/agentic-docs/config/validation.yaml

# 3. Re-run validation (loads new config)
/agentic-docs:validate
```

**The agent will NEVER**:
- Modify validation.yaml directly
- Suggest changes to configuration values
- Override configuration parameters

**The agent WILL**:
- Load and respect configuration
- Report validation results based on configuration
- Suggest that YOU (the user) edit configuration if needed

---

## Troubleshooting

### Problem: Validation always fails

**Solution**: Check if thresholds are too strict:

```yaml
# Relax quality threshold
quality_score:
  minimum_score: 60  # Lower from 70

# Relax coverage requirements
coverage:
  minimum_component_coverage: 0.6  # Lower from 0.8
```

### Problem: Navigation depth violations

**Solution**: Increase max hops:

```yaml
navigation:
  max_hops: 4  # Increase from 3
```

### Problem: Line budget violations

**Solution**: Increase line limits:

```yaml
line_budget:
  agents_md: 200      # Increase from 150
  component_docs: 150  # Increase from 100
```

### Problem: Configuration not taking effect

**Solution**: Verify you're editing the correct file:

```bash
# Check file path
ls -la plugins/agentic-docs/config/validation.yaml

# Verify your changes are saved
cat plugins/agentic-docs/config/validation.yaml | grep "max_hops"
```

---

## See Also

- [README.md](./README.md) - Plugin overview
- [validate/SKILL.md](./skills/validate/SKILL.md) - Validation skill documentation
- [structure_validator.py](./lib/validators/structure_validator.py) - Validation implementation
