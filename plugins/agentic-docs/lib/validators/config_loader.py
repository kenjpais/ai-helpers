"""
Configuration Loader with Immutability Enforcement

Loads validation.yaml configuration and enforces strict immutability:
- Computes SHA256 hash of configuration at load time
- Provides immutable configuration object
- Verifies hash hasn't changed before critical operations
- Prevents agent from modifying validation parameters

Based on REFACTOR_MAY_8.md requirement for strict immutability enforcement.
"""

import hashlib
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConfigurationTamperError(Exception):
    """Raised when configuration has been modified during validation"""
    pass


class ConfigurationNotFoundError(Exception):
    """Raised when configuration file is not found"""
    pass


@dataclass(frozen=True)
class NavigationConfig:
    """Navigation constraints (immutable)"""
    max_hops: int
    entry_point: str


@dataclass(frozen=True)
class LineBudgetConfig:
    """Line budget constraints (immutable)"""
    agents_md: int
    component_docs: int
    concept_docs: int
    query_responses: int


@dataclass(frozen=True)
class DirectoryStructureConfig:
    """Directory structure requirements (immutable)"""
    required_dirs: List[str]
    required_files: Dict[str, List[str]]


@dataclass(frozen=True)
class QualityScoreConfig:
    """Quality score thresholds (immutable)"""
    minimum_score: int
    coverage_weight: int
    freshness_weight: int
    completeness_weight: int
    linkage_weight: int
    navigation_weight: int


@dataclass(frozen=True)
class ValidationChecksConfig:
    """Validation checks to enable (immutable)"""
    check_directory_structure: bool
    check_navigation_depth: bool
    check_line_budgets: bool
    check_broken_links: bool
    check_coverage: bool
    check_frontmatter: bool
    check_file_naming: bool
    check_quality_score: bool


@dataclass(frozen=True)
class NamingConventionsConfig:
    """File naming conventions (immutable)"""
    format: str
    allowed_extensions: List[str]


@dataclass(frozen=True)
class CoverageConfig:
    """Coverage requirements (immutable)"""
    minimum_component_coverage: float
    minimum_concept_coverage: float


@dataclass(frozen=True)
class FreshnessConfig:
    """Freshness requirements (immutable)"""
    max_age_days: int


@dataclass(frozen=True)
class LoggingConfig:
    """Logging configuration (immutable)"""
    level: str
    output_format: str
    save_logs: bool
    log_directory: str


@dataclass(frozen=True)
class ValidationConfig:
    """
    Complete validation configuration (immutable)

    All fields are immutable (frozen=True) to prevent modification after loading.
    Configuration hash is computed and verified to detect tampering.
    """
    navigation: NavigationConfig
    line_budget: LineBudgetConfig
    directory_structure: DirectoryStructureConfig
    quality_score: QualityScoreConfig
    validation_checks: ValidationChecksConfig
    naming_conventions: NamingConventionsConfig
    coverage: CoverageConfig
    freshness: FreshnessConfig
    logging: LoggingConfig

    # Internal fields for immutability enforcement
    _config_hash: str = field(repr=False)
    _config_path: Path = field(repr=False)
    _raw_config: Dict[str, Any] = field(repr=False)


class ImmutableConfigLoader:
    """
    Loads and enforces immutable validation configuration.

    Usage:
        loader = ImmutableConfigLoader("config/validation.yaml")
        config = loader.load()

        # Later, verify config hasn't been tampered with
        loader.verify_integrity()
    """

    def __init__(self, config_path: Path):
        """
        Initialize config loader

        Args:
            config_path: Path to validation.yaml file
        """
        self.config_path = Path(config_path)
        self._loaded_config: Optional[ValidationConfig] = None
        self._original_hash: Optional[str] = None

    def load(self) -> ValidationConfig:
        """
        Load configuration from YAML file

        Returns:
            Immutable ValidationConfig object

        Raises:
            ConfigurationNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
        """
        if not self.config_path.exists():
            raise ConfigurationNotFoundError(
                f"Configuration file not found: {self.config_path}"
            )

        # Read raw config
        with open(self.config_path, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)

        # Compute hash of config file
        config_hash = self._compute_file_hash(self.config_path)
        self._original_hash = config_hash

        # Parse into immutable dataclasses
        config = ValidationConfig(
            navigation=NavigationConfig(**raw_config['navigation']),
            line_budget=LineBudgetConfig(**raw_config['line_budget']),
            directory_structure=DirectoryStructureConfig(
                required_dirs=tuple(raw_config['directory_structure']['required_dirs']),
                required_files={
                    k: tuple(v) for k, v in raw_config['directory_structure']['required_files'].items()
                }
            ),
            quality_score=QualityScoreConfig(**raw_config['quality_score']),
            validation_checks=ValidationChecksConfig(**raw_config['validation_checks']),
            naming_conventions=NamingConventionsConfig(
                format=raw_config['naming_conventions']['format'],
                allowed_extensions=tuple(raw_config['naming_conventions']['allowed_extensions'])
            ),
            coverage=CoverageConfig(**raw_config['coverage']),
            freshness=FreshnessConfig(**raw_config['freshness']),
            logging=LoggingConfig(**raw_config['logging']),
            _config_hash=config_hash,
            _config_path=self.config_path,
            _raw_config=raw_config,
        )

        self._loaded_config = config
        return config

    def verify_integrity(self) -> None:
        """
        Verify configuration file hasn't been modified since loading

        Raises:
            ConfigurationTamperError: If config hash has changed
        """
        if self._loaded_config is None:
            raise RuntimeError("Configuration not loaded yet. Call load() first.")

        current_hash = self._compute_file_hash(self.config_path)

        if current_hash != self._original_hash:
            raise ConfigurationTamperError(
                f"Configuration file has been modified during validation!\n"
                f"Original hash: {self._original_hash}\n"
                f"Current hash:  {current_hash}\n"
                f"\n"
                f"This violates the immutability constraint. The validation agent\n"
                f"MUST NOT modify config/validation.yaml during execution.\n"
                f"\n"
                f"If you need to change validation parameters:\n"
                f"1. Stop the current validation\n"
                f"2. Edit config/validation.yaml manually\n"
                f"3. Re-run validation with new configuration"
            )

    def get_config(self) -> ValidationConfig:
        """
        Get loaded configuration (must call load() first)

        Returns:
            Immutable ValidationConfig object

        Raises:
            RuntimeError: If configuration not loaded yet
        """
        if self._loaded_config is None:
            raise RuntimeError("Configuration not loaded yet. Call load() first.")
        return self._loaded_config

    def get_config_hash(self) -> str:
        """
        Get SHA256 hash of loaded configuration

        Returns:
            Hex digest of configuration file hash
        """
        if self._original_hash is None:
            raise RuntimeError("Configuration not loaded yet. Call load() first.")
        return self._original_hash

    @staticmethod
    def _compute_file_hash(file_path: Path) -> str:
        """
        Compute SHA256 hash of file contents

        Args:
            file_path: Path to file

        Returns:
            Hex digest of SHA256 hash
        """
        sha256_hash = hashlib.sha256()

        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)

        return sha256_hash.hexdigest()


def load_validation_config(config_path: Optional[Path] = None) -> ValidationConfig:
    """
    Convenience function to load validation configuration

    Args:
        config_path: Path to validation.yaml (defaults to config/validation.yaml)

    Returns:
        Immutable ValidationConfig object
    """
    if config_path is None:
        # Default path relative to plugin root
        plugin_root = Path(__file__).parent.parent.parent
        config_path = plugin_root / "config" / "validation.yaml"

    loader = ImmutableConfigLoader(config_path)
    return loader.load()
