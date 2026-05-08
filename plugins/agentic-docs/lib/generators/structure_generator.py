"""
Structure Generator - Create agentic documentation directory structure

Converted from shell script to Python for the agentic/ structure.
Based on AGENTIC_DOCS_FRAMEWORK.md requirements.
"""

import os
from pathlib import Path
from typing import Optional


class StructureGenerator:
    """Generate agentic documentation directory structure"""

    # Directory structure based on AGENTIC_DOCS_FRAMEWORK.md
    REQUIRED_DIRS = [
        "agentic",
        "agentic/design-docs",
        "agentic/design-docs/components",
        "agentic/domain",
        "agentic/domain/concepts",
        "agentic/domain/workflows",
        "agentic/exec-plans",
        "agentic/exec-plans/active",
        "agentic/exec-plans/completed",
        "agentic/product-specs",
        "agentic/decisions",
        "agentic/references",
        "agentic/generated",
    ]

    # Required files (created as empty/template)
    REQUIRED_FILES = {
        "AGENTS.md": "# AI Agents\n\nEntry point for agentic documentation.\n",
        "ARCHITECTURE.md": "# Architecture\n\nNavigation map with file paths.\n",
        "agentic/DESIGN.md": "# Design Philosophy\n\nSystem design principles.\n",
        "agentic/DEVELOPMENT.md": "# Development\n\nDevelopment setup and workflow.\n",
        "agentic/TESTING.md": "# Testing\n\nTest strategy and coverage.\n",
        "agentic/RELIABILITY.md": "# Reliability\n\nSLOs and observability.\n",
        "agentic/SECURITY.md": "# Security\n\nSecurity model and controls.\n",
        "agentic/QUALITY_SCORE.md": "# Quality Score\n\nDocumentation quality metrics.\n",
        "agentic/design-docs/index.md": "# Design Documentation\n\nArchitecture and design decisions.\n",
        "agentic/design-docs/core-beliefs.md": "# Core Beliefs\n\nOperating principles.\n",
        "agentic/design-docs/component-architecture.md": "# Component Architecture\n\nComponent organization.\n",
        "agentic/design-docs/data-flow.md": "# Data Flow\n\nData pipelines and flows.\n",
        "agentic/domain/index.md": "# Domain\n\nDomain concepts and glossary.\n",
        "agentic/domain/glossary.md": "# Glossary\n\nTerm definitions.\n",
        "agentic/exec-plans/template.md": "# Execution Plan Template\n\n7-section template.\n",
        "agentic/product-specs/index.md": "# Product Specifications\n\nFeature specs.\n",
        "agentic/decisions/index.md": "# Decisions\n\nArchitecture decision records.\n",
        "agentic/decisions/adr-template.md": "# ADR Template\n\nDecision record template.\n",
    }

    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize structure generator

        Args:
            repo_path: Repository path (defaults to current directory)
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()

    def create_structure(self, verbose: bool = True) -> dict:
        """
        Create complete agentic documentation structure

        Args:
            verbose: Print progress messages

        Returns:
            dict with 'dirs_created', 'files_created', 'errors'
        """
        if verbose:
            print(f"📁 Creating agentic/ directory structure in: {self.repo_path}")
            print()

        dirs_created = []
        files_created = []
        errors = []

        # Create directories
        for dir_path in self.REQUIRED_DIRS:
            full_path = self.repo_path / dir_path
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                dirs_created.append(str(dir_path))
                if verbose:
                    print(f"  ✅ Created: {dir_path}/")
            except Exception as e:
                errors.append(f"Failed to create {dir_path}: {e}")
                if verbose:
                    print(f"  ❌ Failed: {dir_path}/ - {e}")

        if verbose:
            print()

        # Create files with templates
        for file_path, content in self.REQUIRED_FILES.items():
            full_path = self.repo_path / file_path
            try:
                # Only create if doesn't exist (don't overwrite)
                if not full_path.exists():
                    full_path.write_text(content)
                    files_created.append(str(file_path))
                    if verbose:
                        print(f"  ✅ Created: {file_path}")
                else:
                    if verbose:
                        print(f"  ⏭️  Exists: {file_path} (skipped)")
            except Exception as e:
                errors.append(f"Failed to create {file_path}: {e}")
                if verbose:
                    print(f"  ❌ Failed: {file_path} - {e}")

        if verbose:
            print()
            print("✅ Directory structure created successfully")
            print(f"   Directories: {len(dirs_created)}")
            print(f"   Files: {len(files_created)}")
            if errors:
                print(f"   Errors: {len(errors)}")

        return {
            "dirs_created": dirs_created,
            "files_created": files_created,
            "errors": errors,
        }

    def validate_structure(self, verbose: bool = True) -> bool:
        """
        Validate that structure was created correctly

        Args:
            verbose: Print validation results

        Returns:
            True if valid, False otherwise
        """
        if verbose:
            print("🔍 Validating structure...")
            print()

        all_valid = True

        # Check directories
        for dir_path in self.REQUIRED_DIRS:
            full_path = self.repo_path / dir_path
            if full_path.exists() and full_path.is_dir():
                if verbose:
                    print(f"  ✅ {dir_path}/")
            else:
                all_valid = False
                if verbose:
                    print(f"  ❌ Missing: {dir_path}/")

        # Check files
        for file_path in self.REQUIRED_FILES.keys():
            full_path = self.repo_path / file_path
            if full_path.exists() and full_path.is_file():
                if verbose:
                    print(f"  ✅ {file_path}")
            else:
                all_valid = False
                if verbose:
                    print(f"  ❌ Missing: {file_path}")

        if verbose:
            print()
            if all_valid:
                print("✅ Structure validation PASSED")
            else:
                print("❌ Structure validation FAILED")

        return all_valid


def main():
    """CLI entry point for testing"""
    import sys

    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."

    generator = StructureGenerator(Path(repo_path))
    result = generator.create_structure(verbose=True)

    print()
    print("Validating...")
    print()

    valid = generator.validate_structure(verbose=True)

    sys.exit(0 if valid and not result["errors"] else 1)


if __name__ == "__main__":
    main()
