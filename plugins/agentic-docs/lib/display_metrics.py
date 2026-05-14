#!/usr/bin/env python3
"""
Display Metrics Summary

Reads a metrics JSON file and displays a formatted summary to stdout.
This script is the SINGLE SOURCE OF TRUTH for metrics display - prevents
hallucinated numbers in CLI output.

CRITICAL: Validates metrics before display to ensure no incorrect or placeholder
values are shown to users (PR #450 approach).

Usage:
    python lib/display_metrics.py <metrics-json-file>
    python lib/display_metrics.py logs/agentic-docs-create-2026-05-09.metrics.json
    python lib/display_metrics.py <metrics-json-file> --strict  # Fail on validation errors
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Import metrics validator
try:
    from .metrics.metrics_validator import MetricsValidator
except ImportError:
    # Try relative import if running as script
    import os
    sys.path.insert(0, str(Path(__file__).parent))
    from metrics.metrics_validator import MetricsValidator


def format_duration(duration_ms: Optional[float]) -> str:
    """Format duration in milliseconds to human-readable string."""
    if duration_ms is None:
        return "<DURATION_NOT_RECORDED>"

    seconds = duration_ms / 1000
    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"


def display_summary(metrics: Dict[str, Any]) -> None:
    """
    Display formatted metrics summary.

    All values come from the metrics dict - NO INVENTED NUMBERS.
    """
    command = metrics.get("command", "<COMMAND_NOT_RECORDED>")
    result = metrics.get("result", "<RESULT_NOT_RECORDED>")
    duration_ms = metrics.get("duration_ms")
    duration = format_duration(duration_ms)

    print("\n" + "━" * 70)
    print(f"✅ {command.title().replace('-', ' ')} Complete" if result == "COMPLETED" or result == "PASS" else f"❌ {command.title().replace('-', ' ')} Failed")
    print("━" * 70)

    # Duration
    print(f"\nDuration: {duration}")

    # Files created
    files_created = metrics.get("files_created", [])
    if files_created:
        print(f"\nFiles Created: {len(files_created)}")
        # Group by category if we can infer from paths
        core_docs = [f for f in files_created if "/agentic/" in f and "/" not in f.split("/agentic/")[1]]
        design_docs = [f for f in files_created if "/design-docs/" in f]
        domain_docs = [f for f in files_created if "/domain/" in f]
        root_docs = [f for f in files_created if f.endswith(".md") and "/" not in f]

        if core_docs or design_docs or domain_docs or root_docs:
            if core_docs:
                print(f"  • Core docs: {len(core_docs)} files")
            if design_docs:
                print(f"  • Design docs: {len(design_docs)} files")
            if domain_docs:
                print(f"  • Domain docs: {len(domain_docs)} files")
            if root_docs:
                print(f"  • Entry points: {len(root_docs)} files")
            print(f"  • Total: {len(files_created)} files")

    # Skills invoked
    skills_used = metrics.get("skills_used", {})
    if skills_used:
        print(f"\nSkills Invoked:")
        for skill in sorted(skills_used.keys()):
            print(f"  • {skill}")

    # Data sources
    data_sources = metrics.get("data_sources", [])
    if data_sources:
        print(f"\nData Sources:")
        for source in data_sources[:10]:
            print(f"  • {source}")
        if len(data_sources) > 10:
            print(f"  • ... and {len(data_sources) - 10} more")

    # Tools used
    tools_used = metrics.get("tools_used", {})
    if tools_used:
        print(f"\nTools Used:")
        for tool, count in sorted(tools_used.items(), key=lambda x: -x[1]):
            print(f"  • {tool}: {count} invocations")

    # Details (command-specific)
    details = metrics.get("details", {})
    if details:
        # Validation result
        if "validation" in details:
            print(f"\nValidation: {details['validation']}")

        # Quality score
        if "quality_score" in details:
            print(f"Quality Score: {details['quality_score']}")

        # Other details
        for key, value in details.items():
            if key not in ["validation", "quality_score"]:
                print(f"{key}: {value}")

    # Log file path
    log_file = metrics.get("_log_file")  # Internal field
    if not log_file:
        # Try to infer from command
        repository = metrics.get("repository", "unknown")
        timestamp_start = metrics.get("timestamp_start", "unknown")
        if timestamp_start != "unknown":
            # Format: 2026-05-09T10:30:15.123456 -> 2026-05-09-10-30-15
            timestamp_clean = timestamp_start.split(".")[0].replace(":", "-").replace("T", "-")
            log_file = f"logs/{command}-{timestamp_clean}.log"
        else:
            log_file = f"logs/{command}-<TIMESTAMP>.log"

    print(f"\nLog file: {log_file}")
    print("━" * 70)


def main():
    # Parse arguments
    strict_mode = "--strict" in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if len(args) != 1:
        print("Usage: python lib/display_metrics.py <metrics-json-file> [--strict]", file=sys.stderr)
        print("\nOptions:", file=sys.stderr)
        print("  --strict    Fail on any validation error (default: warn only)", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print("  python lib/display_metrics.py logs/agentic-docs-create-2026-05-09.metrics.json", file=sys.stderr)
        print("  python lib/display_metrics.py logs/agentic-docs-create-2026-05-09.metrics.json --strict", file=sys.stderr)
        sys.exit(1)

    metrics_file = Path(args[0])

    if not metrics_file.exists():
        print(f"Error: Metrics file not found: {metrics_file}", file=sys.stderr)
        sys.exit(1)

    # CRITICAL: Validate metrics before loading and displaying (PR #450)
    print("🔍 Validating metrics integrity...", file=sys.stderr)
    is_valid, errors = MetricsValidator.validate_metrics_file(metrics_file)

    if not is_valid:
        print("\n❌ Metrics Validation Failed\n", file=sys.stderr)
        print(f"Metrics file: {metrics_file}\n", file=sys.stderr)
        print("Validation errors:", file=sys.stderr)
        for error in errors:
            print(f"  • {error}", file=sys.stderr)
        print("\n" + "="*70, file=sys.stderr)
        print("CRITICAL: Metrics contain invalid or placeholder values.", file=sys.stderr)
        print("This indicates metrics were not properly derived from actual execution.", file=sys.stderr)
        print("\nMetrics MUST be:", file=sys.stderr)
        print("  • Derived directly from execution outputs", file=sys.stderr)
        print("  • Consistently reproducible", file=sys.stderr)
        print("  • Fully verified and accurate", file=sys.stderr)
        print("\nDo NOT display potentially incorrect metrics to users.", file=sys.stderr)
        print("="*70 + "\n", file=sys.stderr)

        if strict_mode:
            sys.exit(1)
        else:
            print("⚠️  WARNING: Continuing in non-strict mode, but metrics may be incorrect.\n", file=sys.stderr)

    try:
        with open(metrics_file) as f:
            metrics = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {metrics_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # Store log file path for display
    metrics["_log_file"] = str(metrics_file).replace(".metrics.json", ".log")

    if is_valid:
        print("✅ Metrics validation passed\n", file=sys.stderr)

    display_summary(metrics)


if __name__ == "__main__":
    main()
