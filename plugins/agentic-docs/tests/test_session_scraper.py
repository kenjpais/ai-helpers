"""
Tests for session scraper functionality.
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from lib.metrics.session_scraper import (
    FileAccess,
    NavigationSequence,
    SessionScraper,
    SessionTelemetry,
)


def create_mock_jsonl_session(session_dir: Path, session_id: str) -> Path:
    """Create a mock session JSONL file."""
    session_file = session_dir / f"{session_id}.jsonl"

    # Mock tool calls with agentic doc accesses
    log_entries = [
        {
            "type": "tool_use",
            "name": "Read",
            "input": {"file_path": "/repo/agentic/AGENTS.md"},
            "timestamp": "2026-05-08T10:00:00Z",
        },
        {
            "type": "tool_use",
            "name": "Read",
            "input": {"file_path": "/repo/agentic/design-docs/components/controller.md"},
            "timestamp": "2026-05-08T10:01:00Z",
        },
        {
            "type": "tool_use",
            "name": "Read",
            "input": {"file_path": "/repo/agentic/domain/concepts/reconciliation.md"},
            "timestamp": "2026-05-08T10:02:00Z",
        },
        {
            "type": "tool_use",
            "name": "Read",
            "input": {"file_path": "/repo/src/main.go"},  # Non-agentic file
            "timestamp": "2026-05-08T10:03:00Z",
        },
        {
            "type": "tool_use",
            "name": "Write",
            "input": {"file_path": "/repo/agentic/ARCHITECTURE.md"},
            "timestamp": "2026-05-08T10:04:00Z",
        },
    ]

    with open(session_file, 'w', encoding='utf-8') as f:
        for entry in log_entries:
            f.write(json.dumps(entry) + '\n')

    return session_file


def test_is_agentic_doc_path():
    """Test agentic doc path detection."""
    scraper = SessionScraper()

    assert scraper.is_agentic_doc_path("/repo/agentic/AGENTS.md")
    assert scraper.is_agentic_doc_path("/repo/agentic/design-docs/components/controller.md")
    assert scraper.is_agentic_doc_path("/repo/ai-docs/DESIGN.md")
    assert scraper.is_agentic_doc_path("/repo/AGENTS.md")

    assert not scraper.is_agentic_doc_path("/repo/src/main.go")
    assert not scraper.is_agentic_doc_path("/repo/README.md")


def test_extract_file_access():
    """Test file access extraction from JSONL line (legacy format)."""
    scraper = SessionScraper()

    # Test legacy format (top-level tool_use)
    line = json.dumps({
        "type": "tool_use",
        "name": "Read",
        "input": {"file_path": "/repo/agentic/AGENTS.md"},
        "timestamp": "2026-05-08T10:00:00Z",
    })

    accesses = scraper.extract_file_accesses_from_log_line(line, "test-session", 1)

    assert len(accesses) == 1
    access = accesses[0]
    assert access.file_path == "/repo/agentic/AGENTS.md"
    assert access.access_type == "read"
    assert access.session_id == "test-session"
    assert access.sequence_number == 1

    # Test Claude Code format (nested in message.content)
    line = json.dumps({
        "type": "assistant",
        "timestamp": "2026-05-08T10:00:00Z",
        "message": {
            "content": [
                {
                    "type": "tool_use",
                    "name": "Read",
                    "input": {"file_path": "/repo/agentic/ARCHITECTURE.md"}
                }
            ]
        }
    })

    accesses = scraper.extract_file_accesses_from_log_line(line, "test-session", 2)

    assert len(accesses) == 1
    access = accesses[0]
    assert access.file_path == "/repo/agentic/ARCHITECTURE.md"
    assert access.access_type == "read"
    assert access.session_id == "test-session"
    assert access.sequence_number == 2


def test_scrape_session_file():
    """Test scraping a single session file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        session_dir = Path(tmpdir)
        session_file = create_mock_jsonl_session(session_dir, "test-session")

        scraper = SessionScraper()
        telemetry = scraper.scrape_session_file(session_file)

        # Should have 4 agentic doc accesses (excluding /repo/src/main.go)
        assert len(telemetry.file_accesses) == 4
        assert telemetry.session_id == "test-session"
        assert len(telemetry.docs_accessed) == 4

        # Check file paths
        file_paths = {access.file_path for access in telemetry.file_accesses}
        assert "/repo/agentic/AGENTS.md" in file_paths
        assert "/repo/agentic/design-docs/components/controller.md" in file_paths
        assert "/repo/agentic/domain/concepts/reconciliation.md" in file_paths
        assert "/repo/agentic/ARCHITECTURE.md" in file_paths


def test_navigation_sequences():
    """Test navigation sequence building."""
    with tempfile.TemporaryDirectory() as tmpdir:
        session_dir = Path(tmpdir)
        session_file = create_mock_jsonl_session(session_dir, "test-session")

        scraper = SessionScraper()
        telemetry = scraper.scrape_session_file(session_file)

        # Should have at least 1 navigation sequence
        assert len(telemetry.navigation_sequences) > 0

        # First sequence should start with AGENTS.md
        first_seq = telemetry.navigation_sequences[0]
        assert first_seq.entry_point == "/repo/agentic/AGENTS.md"

        # Hop count should be number of accesses - 1
        assert first_seq.hop_count >= 0


def test_aggregate_metrics():
    """Test metrics aggregation across sessions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        session_dir = Path(tmpdir)

        # Create multiple mock sessions
        create_mock_jsonl_session(session_dir, "session-1")
        create_mock_jsonl_session(session_dir, "session-2")

        scraper = SessionScraper(claude_dir=Path(tmpdir))
        scraper.projects_dir = session_dir

        telemetry_list = []
        for session_file in session_dir.glob("*.jsonl"):
            telemetry = scraper.scrape_session_file(session_file)
            telemetry_list.append(telemetry)

        metrics = scraper.aggregate_metrics(telemetry_list)

        assert metrics["total_sessions"] == 2
        assert metrics["total_file_accesses"] == 8  # 4 per session
        assert metrics["avg_accesses_per_session"] == 4.0

        # Check most accessed docs
        assert len(metrics["most_accessed_docs"]) > 0
        most_accessed_doc, count = metrics["most_accessed_docs"][0]
        assert count == 2  # Each doc accessed in both sessions


def test_export_to_json():
    """Test JSON export functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        session_dir = Path(tmpdir)
        session_file = create_mock_jsonl_session(session_dir, "test-session")

        scraper = SessionScraper()
        telemetry = scraper.scrape_session_file(session_file)

        output_file = Path(tmpdir) / "output.json"
        scraper.export_to_json([telemetry], output_file)

        # Verify file was created
        assert output_file.exists()

        # Verify JSON is valid
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["session_id"] == "test-session"
        assert len(data[0]["file_accesses"]) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
