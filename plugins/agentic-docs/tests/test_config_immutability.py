"""
Tests for configuration immutability enforcement

Verifies that configuration cannot be modified during validation execution.
"""

import pytest
import tempfile
import yaml
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.validators.config_loader import (
    ImmutableConfigLoader,
    ConfigurationTamperError,
    ConfigurationNotFoundError,
    load_validation_config,
)


@pytest.fixture
def sample_config():
    """Sample validation configuration"""
    return {
        'navigation': {
            'max_hops': 3,
            'entry_point': 'AGENTS.md'
        },
        'line_budget': {
            'agents_md': 150,
            'component_docs': 100,
            'concept_docs': 75,
            'query_responses': 500
        },
        'directory_structure': {
            'required_dirs': ['agentic', 'agentic/design-docs'],
            'required_files': {
                'root': ['AGENTS.md'],
                'agentic': ['DESIGN.md']
            }
        },
        'quality_score': {
            'minimum_score': 70,
            'coverage_weight': 40,
            'freshness_weight': 20,
            'completeness_weight': 20,
            'linkage_weight': 10,
            'navigation_weight': 10
        },
        'validation_checks': {
            'check_directory_structure': True,
            'check_navigation_depth': True,
            'check_line_budgets': True,
            'check_broken_links': True,
            'check_coverage': True,
            'check_frontmatter': True,
            'check_file_naming': True,
            'check_quality_score': True
        },
        'naming_conventions': {
            'format': 'kebab-case',
            'allowed_extensions': ['.md', '.json', '.yaml']
        },
        'coverage': {
            'minimum_component_coverage': 0.8,
            'minimum_concept_coverage': 0.7
        },
        'freshness': {
            'max_age_days': 90
        },
        'logging': {
            'level': 'INFO',
            'output_format': 'structured',
            'save_logs': True,
            'log_directory': 'logs'
        }
    }


@pytest.fixture
def config_file(sample_config):
    """Create temporary config file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_config, f)
        config_path = Path(f.name)

    yield config_path

    # Cleanup
    config_path.unlink()


def test_load_configuration(config_file):
    """Test loading configuration successfully"""
    loader = ImmutableConfigLoader(config_file)
    config = loader.load()

    assert config.navigation.max_hops == 3
    assert config.line_budget.agents_md == 150
    assert config.quality_score.minimum_score == 70
    assert config.validation_checks.check_directory_structure is True


def test_configuration_immutable(config_file):
    """Test that loaded configuration is immutable"""
    loader = ImmutableConfigLoader(config_file)
    config = loader.load()

    # Attempt to modify configuration (should fail)
    with pytest.raises(Exception):  # FrozenInstanceError in Python 3.10+
        config.navigation.max_hops = 5

    with pytest.raises(Exception):
        config.line_budget.agents_md = 200


def test_compute_hash(config_file):
    """Test that hash is computed correctly"""
    loader = ImmutableConfigLoader(config_file)
    config = loader.load()

    config_hash = loader.get_config_hash()

    # Hash should be 64-char hex string (SHA256)
    assert len(config_hash) == 64
    assert all(c in '0123456789abcdef' for c in config_hash)


def test_verify_integrity_unchanged(config_file):
    """Test integrity verification when file unchanged"""
    loader = ImmutableConfigLoader(config_file)
    config = loader.load()

    # Verify integrity (should pass)
    loader.verify_integrity()  # Should not raise


def test_detect_tampering(config_file, sample_config):
    """Test that tampering is detected"""
    loader = ImmutableConfigLoader(config_file)
    config = loader.load()

    original_hash = loader.get_config_hash()

    # Modify the config file
    sample_config['navigation']['max_hops'] = 5
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)

    # Verify integrity (should fail)
    with pytest.raises(ConfigurationTamperError) as exc_info:
        loader.verify_integrity()

    assert "has been modified during validation" in str(exc_info.value)
    assert original_hash in str(exc_info.value)


def test_missing_config_file():
    """Test error when config file doesn't exist"""
    loader = ImmutableConfigLoader(Path("/nonexistent/config.yaml"))

    with pytest.raises(ConfigurationNotFoundError) as exc_info:
        loader.load()

    assert "Configuration file not found" in str(exc_info.value)


def test_get_config_before_load():
    """Test error when getting config before loading"""
    with tempfile.NamedTemporaryFile(suffix='.yaml') as f:
        loader = ImmutableConfigLoader(Path(f.name))

        with pytest.raises(RuntimeError) as exc_info:
            loader.get_config()

        assert "Configuration not loaded yet" in str(exc_info.value)


def test_verify_before_load():
    """Test error when verifying before loading"""
    with tempfile.NamedTemporaryFile(suffix='.yaml') as f:
        loader = ImmutableConfigLoader(Path(f.name))

        with pytest.raises(RuntimeError) as exc_info:
            loader.verify_integrity()

        assert "Configuration not loaded yet" in str(exc_info.value)


def test_hash_deterministic(config_file):
    """Test that hash is deterministic (same file = same hash)"""
    loader1 = ImmutableConfigLoader(config_file)
    config1 = loader1.load()
    hash1 = loader1.get_config_hash()

    loader2 = ImmutableConfigLoader(config_file)
    config2 = loader2.load()
    hash2 = loader2.get_config_hash()

    assert hash1 == hash2


def test_hash_sensitive_to_changes(config_file, sample_config):
    """Test that hash changes when config changes"""
    loader1 = ImmutableConfigLoader(config_file)
    config1 = loader1.load()
    hash1 = loader1.get_config_hash()

    # Modify config (even slightly)
    sample_config['navigation']['max_hops'] = 4
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)

    loader2 = ImmutableConfigLoader(config_file)
    config2 = loader2.load()
    hash2 = loader2.get_config_hash()

    assert hash1 != hash2


def test_configuration_dataclasses_frozen(config_file):
    """Test that all configuration dataclasses are frozen"""
    loader = ImmutableConfigLoader(config_file)
    config = loader.load()

    # All nested configs should be immutable
    with pytest.raises(Exception):
        config.navigation.max_hops = 999

    with pytest.raises(Exception):
        config.line_budget.agents_md = 999

    with pytest.raises(Exception):
        config.quality_score.minimum_score = 999

    with pytest.raises(Exception):
        config.validation_checks.check_directory_structure = False


def test_lists_converted_to_tuples(config_file):
    """Test that mutable lists are converted to immutable tuples"""
    loader = ImmutableConfigLoader(config_file)
    config = loader.load()

    # Lists should be converted to tuples (immutable)
    assert isinstance(config.directory_structure.required_dirs, tuple)
    assert isinstance(config.naming_conventions.allowed_extensions, tuple)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
