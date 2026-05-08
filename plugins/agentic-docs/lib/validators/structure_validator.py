"""
Structure Validator - Validate agentic documentation structure and quality

Converted from validate.sh to Python for the agentic/ structure.
Based on AGENTIC_DOCS_FRAMEWORK.md requirements.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class StructureValidator:
    """Validate agentic documentation structure and quality"""

    # Required entry point files
    REQUIRED_ENTRY_POINTS = [
        "AGENTS.md",
        "ARCHITECTURE.md",
    ]

    # Required core files in agentic/
    REQUIRED_CORE_FILES = [
        "agentic/DESIGN.md",
        "agentic/DEVELOPMENT.md",
        "agentic/TESTING.md",
        "agentic/RELIABILITY.md",
        "agentic/SECURITY.md",
        "agentic/QUALITY_SCORE.md",
    ]

    # Required design docs
    REQUIRED_DESIGN_DOCS = [
        "agentic/design-docs/index.md",
        "agentic/design-docs/core-beliefs.md",
        "agentic/design-docs/component-architecture.md",
        "agentic/design-docs/data-flow.md",
    ]

    # Required domain docs
    REQUIRED_DOMAIN_DOCS = [
        "agentic/domain/index.md",
        "agentic/domain/glossary.md",
    ]

    # Line budget constraints
    LINE_BUDGETS = {
        "AGENTS.md": (80, 150),  # (min, max)
        "ARCHITECTURE.md": (50, 300),
        "agentic/DESIGN.md": (100, 500),
        "agentic/DEVELOPMENT.md": (100, 400),
        "agentic/TESTING.md": (100, 400),
        "agentic/RELIABILITY.md": (100, 400),
        "agentic/SECURITY.md": (100, 400),
        "component_docs": (50, 100),  # Per component doc
        "concept_docs": (30, 75),  # Per concept doc
    }

    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize validator

        Args:
            repo_path: Repository path (defaults to current directory)
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self, verbose: bool = True) -> Tuple[bool, Dict]:
        """
        Run all validation checks

        Args:
            verbose: Print validation progress

        Returns:
            Tuple of (success, results_dict)
        """
        self.errors = []
        self.warnings = []

        if verbose:
            print("✅ Validating agentic/ documentation")
            print(f"   Repository: {self.repo_path}")
            print()

        results = {}

        # Phase 1: Entry Points
        results["entry_points"] = self._validate_entry_points(verbose)

        # Phase 2: Core Files
        results["core_files"] = self._validate_core_files(verbose)

        # Phase 3: Design Docs
        results["design_docs"] = self._validate_design_docs(verbose)

        # Phase 4: Domain Docs
        results["domain_docs"] = self._validate_domain_docs(verbose)

        # Phase 5: Line Budgets
        results["line_budgets"] = self._validate_line_budgets(verbose)

        # Phase 6: Structural Quality
        results["structural_quality"] = self._validate_structural_quality(verbose)

        # Phase 7: ADR Naming
        results["adr_naming"] = self._validate_adr_naming(verbose)

        if verbose:
            print()
            print("=" * 60)
            if not self.errors:
                print("✅ Validation PASSED - All checks successful")
            else:
                print(f"❌ Validation FAILED - {len(self.errors)} error(s)")
                for error in self.errors:
                    print(f"   • {error}")

            if self.warnings:
                print()
                print(f"⚠️  {len(self.warnings)} warning(s):")
                for warning in self.warnings:
                    print(f"   • {warning}")

        return (len(self.errors) == 0, results)

    def _validate_entry_points(self, verbose: bool) -> bool:
        """Validate entry point files (AGENTS.md, ARCHITECTURE.md)"""
        if verbose:
            print("=== Phase 1: Entry Points ===")
            print()

        all_valid = True

        for file_path in self.REQUIRED_ENTRY_POINTS:
            full_path = self.repo_path / file_path
            if full_path.exists():
                if verbose:
                    print(f"  ✅ {file_path}")

                # Check line count for AGENTS.md
                if file_path == "AGENTS.md":
                    line_count = len(full_path.read_text().splitlines())
                    min_lines, max_lines = self.LINE_BUDGETS["AGENTS.md"]
                    if verbose:
                        print(f"     {line_count} lines", end="")
                    if line_count < min_lines or line_count > max_lines:
                        msg = f"Should be {min_lines}-{max_lines} lines (current: {line_count})"
                        self.warnings.append(f"AGENTS.md: {msg}")
                        if verbose:
                            print(f" ⚠️  WARNING: {msg}")
                    else:
                        if verbose:
                            print(" ✓")
            else:
                all_valid = False
                self.errors.append(f"Missing: {file_path}")
                if verbose:
                    print(f"  ❌ Missing: {file_path}")

        if verbose:
            print()

        return all_valid

    def _validate_core_files(self, verbose: bool) -> bool:
        """Validate core files in agentic/"""
        if verbose:
            print("=== Phase 2: Core Files ===")
            print()

        all_valid = True

        for file_path in self.REQUIRED_CORE_FILES:
            full_path = self.repo_path / file_path
            if full_path.exists():
                if verbose:
                    print(f"  ✅ {file_path}")
            else:
                all_valid = False
                self.errors.append(f"Missing: {file_path}")
                if verbose:
                    print(f"  ❌ Missing: {file_path}")

        if verbose:
            print()

        return all_valid

    def _validate_design_docs(self, verbose: bool) -> bool:
        """Validate design documentation"""
        if verbose:
            print("=== Phase 3: Design Documentation ===")
            print()

        all_valid = True

        for file_path in self.REQUIRED_DESIGN_DOCS:
            full_path = self.repo_path / file_path
            if full_path.exists():
                if verbose:
                    print(f"  ✅ {file_path}")
            else:
                all_valid = False
                self.errors.append(f"Missing: {file_path}")
                if verbose:
                    print(f"  ❌ Missing: {file_path}")

        # Check for component docs
        components_dir = self.repo_path / "agentic/design-docs/components"
        if components_dir.exists():
            component_files = list(components_dir.glob("*.md"))
            if verbose:
                print(f"  ✅ Found {len(component_files)} component doc(s)")
        else:
            self.warnings.append("No component documentation found")
            if verbose:
                print("  ⚠️  No component documentation found")

        if verbose:
            print()

        return all_valid

    def _validate_domain_docs(self, verbose: bool) -> bool:
        """Validate domain documentation"""
        if verbose:
            print("=== Phase 4: Domain Documentation ===")
            print()

        all_valid = True

        for file_path in self.REQUIRED_DOMAIN_DOCS:
            full_path = self.repo_path / file_path
            if full_path.exists():
                if verbose:
                    print(f"  ✅ {file_path}")
            else:
                all_valid = False
                self.errors.append(f"Missing: {file_path}")
                if verbose:
                    print(f"  ❌ Missing: {file_path}")

        # Check for concept docs
        concepts_dir = self.repo_path / "agentic/domain/concepts"
        if concepts_dir.exists():
            concept_files = list(concepts_dir.glob("*.md"))
            if verbose:
                print(f"  ✅ Found {len(concept_files)} concept doc(s)")
        else:
            self.warnings.append("No concept documentation found")
            if verbose:
                print("  ⚠️  No concept documentation found")

        if verbose:
            print()

        return all_valid

    def _validate_line_budgets(self, verbose: bool) -> bool:
        """Validate line count budgets"""
        if verbose:
            print("=== Phase 5: Line Budget Validation ===")
            print()

        # Already checked AGENTS.md in phase 1
        # Check component docs
        components_dir = self.repo_path / "agentic/design-docs/components"
        if components_dir.exists():
            min_lines, max_lines = self.LINE_BUDGETS["component_docs"]
            violations = []

            for component_file in components_dir.glob("*.md"):
                line_count = len(component_file.read_text().splitlines())
                if line_count > max_lines:
                    violations.append(f"{component_file.name}: {line_count} lines (max: {max_lines})")

            if violations:
                for violation in violations:
                    self.warnings.append(f"Component doc exceeds budget: {violation}")
                if verbose:
                    print(f"  ⚠️  {len(violations)} component doc(s) exceed line budget")
            elif verbose:
                print("  ✅ All component docs within line budget")

        # Check concept docs
        concepts_dir = self.repo_path / "agentic/domain/concepts"
        if concepts_dir.exists():
            min_lines, max_lines = self.LINE_BUDGETS["concept_docs"]
            violations = []

            for concept_file in concepts_dir.glob("*.md"):
                line_count = len(concept_file.read_text().splitlines())
                if line_count > max_lines:
                    violations.append(f"{concept_file.name}: {line_count} lines (max: {max_lines})")

            if violations:
                for violation in violations:
                    self.warnings.append(f"Concept doc exceeds budget: {violation}")
                if verbose:
                    print(f"  ⚠️  {len(violations)} concept doc(s) exceed line budget")
            elif verbose:
                print("  ✅ All concept docs within line budget")

        if verbose:
            print()

        return True  # Warnings only, not errors

    def _validate_structural_quality(self, verbose: bool) -> bool:
        """Validate structural quality (index files, etc.)"""
        if verbose:
            print("=== Phase 6: Structural Quality ===")
            print()

        # Check for index files in populated directories
        directories = ["design-docs", "domain", "decisions", "references"]

        for dir_name in directories:
            dir_path = self.repo_path / "agentic" / dir_name
            if dir_path.exists():
                md_files = list(dir_path.rglob("*.md"))
                if len(md_files) > 1:
                    # Has content, should have index
                    index_files = list(dir_path.glob("index.md"))
                    if index_files:
                        if verbose:
                            print(f"  ✅ {dir_name}/ has index.md for navigation")
                    else:
                        self.warnings.append(f"{dir_name}/ has {len(md_files)} files but no index.md")
                        if verbose:
                            print(f"  ⚠️  {dir_name}/ has {len(md_files)} files but no index.md")

        if verbose:
            print()

        return True

    def _validate_adr_naming(self, verbose: bool) -> bool:
        """Validate ADR naming format (adr-NNNN-*)"""
        if verbose:
            print("=== Phase 7: ADR Naming Format ===")
            print()

        decisions_dir = self.repo_path / "agentic/decisions"
        if decisions_dir.exists():
            adr_files = list(decisions_dir.glob("adr-*.md"))

            if adr_files:
                # Check naming format: adr-NNNN-*
                valid_pattern = re.compile(r"^adr-\d{4}-.+\.md$")
                invalid_adrs = [f for f in adr_files if not valid_pattern.match(f.name)]

                if invalid_adrs:
                    for invalid in invalid_adrs:
                        self.warnings.append(f"ADR doesn't use adr-NNNN- format: {invalid.name}")
                    if verbose:
                        print(f"  ⚠️  {len(invalid_adrs)} ADR(s) don't use adr-NNNN- format")
                elif verbose:
                    print(f"  ✅ All {len(adr_files)} ADR(s) use correct format")
            elif verbose:
                print("  ℹ️  No ADRs found")
        elif verbose:
            print("  ℹ️  No decisions/ directory")

        if verbose:
            print()

        return True


def main():
    """CLI entry point for testing"""
    import sys

    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."

    validator = StructureValidator(Path(repo_path))
    success, results = validator.validate_all(verbose=True)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
