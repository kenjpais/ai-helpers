"""
Metrics Validator - Ensures metrics are derived from actual execution outputs

Implements PR #450 approach:
- Only verified and fully accurate metrics are stored and displayed
- Metrics derived directly from execution outputs
- Consistently reproducible
- No speculative or partially computed values

This prevents the issue where metrics shown to users are partially incorrect
or inconsistent with actual execution results.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional


class MetricsValidator:
    """Validates metrics JSON for integrity and accuracy"""

    # Placeholder patterns that indicate metrics weren't properly filled
    PLACEHOLDER_PATTERNS = [
        r'<ACTUAL_',
        r'<COUNT',
        r'<TOTAL',
        r'<PERCENT',
        r'<SCORE',
        r'<TIMESTAMP',
        r'<REPO',
        r'<LOG',
        r'<.*_FROM_JSON>',
        r'\{.*\}',  # Template variables
        r'\$\{.*\}',  # Environment variables
    ]

    @classmethod
    def validate_metrics_json(cls, metrics: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that all metrics have valid sources and no placeholder values

        Args:
            metrics: Metrics dictionary to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        required_fields = [
            'command',
            'repository',
            'timestamp_start',
            'timestamp_end',
            'duration_ms',
            'result'
        ]

        for field in required_fields:
            if field not in metrics:
                errors.append(f"Missing required field: {field}")
            elif metrics[field] is None:
                errors.append(f"Required field is null: {field}")

        # Validate timestamps
        if 'timestamp_start' in metrics and metrics['timestamp_start']:
            if not cls._is_valid_timestamp(metrics['timestamp_start']):
                errors.append(f"Invalid timestamp_start: {metrics['timestamp_start']}")

        if 'timestamp_end' in metrics and metrics['timestamp_end']:
            if not cls._is_valid_timestamp(metrics['timestamp_end']):
                errors.append(f"Invalid timestamp_end: {metrics['timestamp_end']}")

        # Validate duration matches timestamps
        if all(f in metrics and metrics[f] for f in ['timestamp_start', 'timestamp_end', 'duration_ms']):
            try:
                start = datetime.fromisoformat(metrics['timestamp_start'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(metrics['timestamp_end'].replace('Z', '+00:00'))
                expected_duration = (end - start).total_seconds() * 1000
                actual_duration = metrics['duration_ms']

                # Allow 1 second tolerance for rounding
                if abs(expected_duration - actual_duration) > 1000:
                    errors.append(
                        f"Duration mismatch: duration_ms={actual_duration}ms but "
                        f"timestamps indicate {expected_duration}ms"
                    )
            except Exception as e:
                errors.append(f"Error validating duration consistency: {e}")

        # Validate result enum
        valid_results = ['PASS', 'FAIL', 'COMPLETED', 'ERROR', 'UNKNOWN']
        if 'result' in metrics and metrics['result'] not in valid_results:
            errors.append(f"Invalid result value: {metrics['result']} (must be one of {valid_results})")

        # Check for placeholder values recursively
        placeholder_errors = cls._check_for_placeholders(metrics, path="")
        errors.extend(placeholder_errors)

        # Validate numeric fields are actual numbers
        numeric_fields = ['duration_ms']
        for field in numeric_fields:
            if field in metrics and metrics[field] is not None:
                if not isinstance(metrics[field], (int, float)):
                    errors.append(f"{field} must be a number, got {type(metrics[field]).__name__}")

        # Validate tool and skill countsif 'tools_used' in metrics and isinstance(metrics['tools_used'], dict):
            for tool, count in metrics['tools_used'].items():
                if not isinstance(count, int) or count < 0:
                    errors.append(f"tools_used['{tool}'] must be a non-negative integer, got {count}")

        if 'skills_used' in metrics and isinstance(metrics['skills_used'], dict):
            for skill, count in metrics['skills_used'].items():
                if not isinstance(count, int) or count < 0:
                    errors.append(f"skills_used['{skill}'] must be a non-negative integer, got {count}")

        return len(errors) == 0, errors

    @classmethod
    def _is_valid_timestamp(cls, timestamp_str: str) -> bool:
        """Check if timestamp is valid ISO format"""
        try:
            datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return True
        except Exception:
            return False

    @classmethod
    def _check_for_placeholders(cls, obj: Any, path: str = "") -> List[str]:
        """
        Recursively check for placeholder values in metrics

        Args:
            obj: Object to check (dict, list, str, etc.)
            path: Current path in object tree (for error messages)

        Returns:
            List of error messages for found placeholders
        """
        errors = []

        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                errors.extend(cls._check_for_placeholders(value, new_path))

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                errors.extend(cls._check_for_placeholders(item, new_path))

        elif isinstance(obj, str):
            # Check for placeholder patterns
            for pattern in cls.PLACEHOLDER_PATTERNS:
                if re.search(pattern, obj):
                    errors.append(
                        f"Placeholder value detected at {path}: '{obj}' "
                        f"(matches pattern {pattern})"
                    )
                    break  # One error per field is enough

        return errors

    @classmethod
    def validate_metrics_file(cls, metrics_file: Path) -> Tuple[bool, List[str]]:
        """
        Validate a metrics JSON file

        Args:
            metrics_file: Path to metrics JSON file

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not metrics_file.exists():
            return False, [f"Metrics file not found: {metrics_file}"]

        try:
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON in metrics file: {e}"]
        except Exception as e:
            return False, [f"Error reading metrics file: {e}"]

        return cls.validate_metrics_json(metrics)

    @classmethod
    def load_and_validate(cls, metrics_file: Path) -> Tuple[Optional[Dict], List[str]]:
        """
        Load and validate metrics file

        Args:
            metrics_file: Path to metrics JSON file

        Returns:
            Tuple of (metrics_dict or None, list_of_errors)
        """
        is_valid, errors = cls.validate_metrics_file(metrics_file)

        if not is_valid:
            return None, errors

        with open(metrics_file, 'r') as f:
            metrics = json.load(f)

        return metrics, []


def validate_before_display(metrics_file: Path, strict: bool = True) -> bool:
    """
    Validate metrics before displaying to user

    Args:
        metrics_file: Path to metrics JSON file
        strict: If True, fail on any validation error. If False, warn but continue.

    Returns:
        True if valid, False otherwise

    Raises:
        ValueError: If strict=True and validation fails
    """
    is_valid, errors = MetricsValidator.validate_metrics_file(metrics_file)

    if not is_valid:
        error_msg = "❌ Metrics Validation Failed\n\n"
        error_msg += f"Metrics file: {metrics_file}\n\n"
        error_msg += "Errors:\n"
        for error in errors:
            error_msg += f"  • {error}\n"
        error_msg += "\n"
        error_msg += "CRITICAL: Metrics contain invalid or placeholder values.\n"
        error_msg += "This indicates metrics were not properly derived from actual execution.\n"
        error_msg += "\n"
        error_msg += "Metrics MUST be:\n"
        error_msg += "  • Derived directly from execution outputs\n"
        error_msg += "  • Consistently reproducible\n"
        error_msg += "  • Fully verified and accurate\n"
        error_msg += "\n"
        error_msg += "Do NOT display potentially incorrect metrics to users."

        if strict:
            raise ValueError(error_msg)
        else:
            print(f"\n⚠️  WARNING: {error_msg}\n")
            return False

    return True
