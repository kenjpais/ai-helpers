"""
Session metrics scraper for Claude Code JSONL logs.

Extracts file access patterns, navigation sequences, and timing data
from Claude Code session logs (~/.claude/projects/**/*.jsonl).

Follows the approach from https://github.com/openshift-eng/ai-helpers/pull/450
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class FileAccess:
    """Represents a single file access event."""

    file_path: str
    timestamp: datetime
    sequence_number: int
    access_type: str  # "read", "write", "edit"
    session_id: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "timestamp": self.timestamp.isoformat(),
            "sequence_number": self.sequence_number,
            "access_type": self.access_type,
            "session_id": self.session_id,
        }


@dataclass
class NavigationSequence:
    """Represents a sequence of documentation accesses."""

    session_id: str
    entry_point: Optional[str]  # First doc accessed (e.g., "AGENTS.md")
    accesses: List[FileAccess] = field(default_factory=list)
    hop_count: int = 0
    duration_ms: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "entry_point": self.entry_point,
            "accesses": [a.to_dict() for a in self.accesses],
            "hop_count": self.hop_count,
            "duration_ms": self.duration_ms,
        }


@dataclass
class SessionTelemetry:
    """Aggregated telemetry from a session."""

    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    file_accesses: List[FileAccess] = field(default_factory=list)
    navigation_sequences: List[NavigationSequence] = field(default_factory=list)
    docs_accessed: Set[str] = field(default_factory=set)
    total_hops: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "file_accesses": [a.to_dict() for a in self.file_accesses],
            "navigation_sequences": [n.to_dict() for n in self.navigation_sequences],
            "docs_accessed": sorted(list(self.docs_accessed)),
            "total_hops": self.total_hops,
        }


class SessionScraper:
    """
    Scrapes Claude Code session JSONL logs to extract file access metrics.

    Follows the pattern from PR #450:
    1. Scan session logs in ~/.claude/projects/**/*.jsonl
    2. Filter for Read/Write/Edit tool calls to agentic docs paths
    3. Track sequence numbers and timestamps
    4. Emit structured JSON with FileAccess dataclasses
    5. Aggregate into SessionTelemetry for analysis
    """

    # Patterns for agentic documentation paths
    AGENTIC_DOC_PATTERNS = [
        r"agentic/",
        r"ai-docs/",
        r"AGENTS\.md",
        r"ARCHITECTURE\.md",
        r"DESIGN\.md",
        r"DEVELOPMENT\.md",
        r"TESTING\.md",
        r"RELIABILITY\.md",
        r"SECURITY\.md",
        r"QUALITY_SCORE\.md",
    ]

    def __init__(self, claude_dir: Optional[Path] = None):
        """
        Initialize session scraper.

        Args:
            claude_dir: Path to .claude directory (default: ~/.claude)
        """
        self.claude_dir = claude_dir or Path.home() / ".claude"
        self.projects_dir = self.claude_dir / "projects"

    def is_agentic_doc_path(self, file_path: str) -> bool:
        """Check if a file path is an agentic documentation file."""
        return any(re.search(pattern, file_path) for pattern in self.AGENTIC_DOC_PATTERNS)

    def extract_file_accesses_from_log_line(
        self,
        line: str,
        session_id: str,
        sequence_number: int
    ) -> Optional[FileAccess]:
        """
        Extract file access from a JSONL log line.

        Args:
            line: JSONL log line
            session_id: Session identifier
            sequence_number: Sequence number in session

        Returns:
            FileAccess object if line contains agentic doc access, None otherwise
        """
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            return None

        # Check if this is a tool call
        if entry.get("type") != "tool_use":
            return None

        # Extract tool name and parameters
        tool_name = entry.get("name", "")
        if tool_name not in ["Read", "Write", "Edit"]:
            return None

        # Extract file path from parameters
        params = entry.get("input", {})
        file_path = params.get("file_path")

        if not file_path or not self.is_agentic_doc_path(file_path):
            return None

        # Extract timestamp
        timestamp_str = entry.get("timestamp")
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        else:
            timestamp = datetime.now()

        return FileAccess(
            file_path=file_path,
            timestamp=timestamp,
            sequence_number=sequence_number,
            access_type=tool_name.lower(),
            session_id=session_id,
        )

    def scrape_session_file(self, session_file: Path) -> SessionTelemetry:
        """
        Scrape a single session JSONL file.

        Args:
            session_file: Path to session JSONL file

        Returns:
            SessionTelemetry object with extracted metrics
        """
        session_id = session_file.stem
        file_accesses: List[FileAccess] = []
        sequence_number = 0

        start_time = None
        end_time = None

        with open(session_file, 'r', encoding='utf-8') as f:
            for line in f:
                sequence_number += 1
                access = self.extract_file_accesses_from_log_line(
                    line,
                    session_id,
                    sequence_number
                )

                if access:
                    file_accesses.append(access)

                    if start_time is None:
                        start_time = access.timestamp
                    end_time = access.timestamp

        # Build navigation sequences
        navigation_sequences = self._build_navigation_sequences(file_accesses)

        # Calculate total hops
        total_hops = sum(seq.hop_count for seq in navigation_sequences)

        # Extract unique docs accessed
        docs_accessed = {access.file_path for access in file_accesses}

        return SessionTelemetry(
            session_id=session_id,
            start_time=start_time or datetime.now(),
            end_time=end_time,
            file_accesses=file_accesses,
            navigation_sequences=navigation_sequences,
            docs_accessed=docs_accessed,
            total_hops=total_hops,
        )

    def _build_navigation_sequences(
        self,
        file_accesses: List[FileAccess]
    ) -> List[NavigationSequence]:
        """
        Build navigation sequences from file accesses.

        A navigation sequence is a series of consecutive doc accesses
        within a short time window (e.g., 5 minutes).
        """
        if not file_accesses:
            return []

        sequences: List[NavigationSequence] = []
        current_sequence: Optional[NavigationSequence] = None
        max_gap_seconds = 300  # 5 minutes

        for access in sorted(file_accesses, key=lambda a: a.timestamp):
            if current_sequence is None:
                # Start new sequence
                current_sequence = NavigationSequence(
                    session_id=access.session_id,
                    entry_point=access.file_path,
                    accesses=[access],
                    hop_count=0,
                )
            else:
                # Check time gap
                time_gap = (access.timestamp - current_sequence.accesses[-1].timestamp).total_seconds()

                if time_gap > max_gap_seconds:
                    # Finalize current sequence
                    current_sequence.hop_count = len(current_sequence.accesses) - 1
                    if current_sequence.accesses:
                        duration = (
                            current_sequence.accesses[-1].timestamp -
                            current_sequence.accesses[0].timestamp
                        ).total_seconds() * 1000
                        current_sequence.duration_ms = duration
                    sequences.append(current_sequence)

                    # Start new sequence
                    current_sequence = NavigationSequence(
                        session_id=access.session_id,
                        entry_point=access.file_path,
                        accesses=[access],
                        hop_count=0,
                    )
                else:
                    # Continue current sequence
                    current_sequence.accesses.append(access)

        # Finalize last sequence
        if current_sequence:
            current_sequence.hop_count = len(current_sequence.accesses) - 1
            if current_sequence.accesses:
                duration = (
                    current_sequence.accesses[-1].timestamp -
                    current_sequence.accesses[0].timestamp
                ).total_seconds() * 1000
                current_sequence.duration_ms = duration
            sequences.append(current_sequence)

        return sequences

    def scrape_all_sessions(self, project_name: Optional[str] = None) -> List[SessionTelemetry]:
        """
        Scrape all session files in ~/.claude/projects/.

        Args:
            project_name: Optional project name to filter sessions

        Returns:
            List of SessionTelemetry objects
        """
        if not self.projects_dir.exists():
            return []

        telemetry_list: List[SessionTelemetry] = []

        # Find all JSONL files
        if project_name:
            session_files = self.projects_dir.glob(f"{project_name}/*.jsonl")
        else:
            session_files = self.projects_dir.glob("**/*.jsonl")

        for session_file in session_files:
            try:
                telemetry = self.scrape_session_file(session_file)
                if telemetry.file_accesses:  # Only include sessions with agentic doc accesses
                    telemetry_list.append(telemetry)
            except Exception as e:
                # Log error but continue processing other files
                print(f"Error scraping {session_file}: {e}")

        return telemetry_list

    def export_to_json(self, telemetry_list: List[SessionTelemetry], output_file: Path) -> None:
        """
        Export telemetry to JSON file.

        Args:
            telemetry_list: List of SessionTelemetry objects
            output_file: Path to output JSON file
        """
        data = [t.to_dict() for t in telemetry_list]

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def aggregate_metrics(self, telemetry_list: List[SessionTelemetry]) -> Dict:
        """
        Aggregate metrics across multiple sessions.

        Args:
            telemetry_list: List of SessionTelemetry objects

        Returns:
            Dictionary of aggregated metrics
        """
        total_sessions = len(telemetry_list)
        total_accesses = sum(len(t.file_accesses) for t in telemetry_list)
        total_hops = sum(t.total_hops for t in telemetry_list)

        # Most accessed docs
        doc_access_counts: Dict[str, int] = {}
        for telemetry in telemetry_list:
            for doc in telemetry.docs_accessed:
                doc_access_counts[doc] = doc_access_counts.get(doc, 0) + 1

        most_accessed = sorted(
            doc_access_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Entry points
        entry_points: Dict[str, int] = {}
        for telemetry in telemetry_list:
            for seq in telemetry.navigation_sequences:
                if seq.entry_point:
                    entry_points[seq.entry_point] = entry_points.get(seq.entry_point, 0) + 1

        return {
            "total_sessions": total_sessions,
            "total_file_accesses": total_accesses,
            "total_navigation_hops": total_hops,
            "avg_accesses_per_session": total_accesses / total_sessions if total_sessions > 0 else 0,
            "avg_hops_per_session": total_hops / total_sessions if total_sessions > 0 else 0,
            "most_accessed_docs": most_accessed,
            "entry_points": sorted(entry_points.items(), key=lambda x: x[1], reverse=True),
        }


def main():
    """CLI entry point for session scraping."""
    import sys

    scraper = SessionScraper()

    # Scrape all sessions
    print("Scraping Claude Code session logs...")
    telemetry_list = scraper.scrape_all_sessions()

    print(f"Found {len(telemetry_list)} sessions with agentic doc accesses")

    if not telemetry_list:
        print("No agentic documentation accesses found in session logs.")
        return

    # Export to JSON
    output_file = Path("session_telemetry.json")
    scraper.export_to_json(telemetry_list, output_file)
    print(f"Exported telemetry to {output_file}")

    # Print aggregate metrics
    metrics = scraper.aggregate_metrics(telemetry_list)
    print("\nAggregate Metrics:")
    print(f"  Total sessions: {metrics['total_sessions']}")
    print(f"  Total file accesses: {metrics['total_file_accesses']}")
    print(f"  Total navigation hops: {metrics['total_navigation_hops']}")
    print(f"  Avg accesses/session: {metrics['avg_accesses_per_session']:.1f}")
    print(f"  Avg hops/session: {metrics['avg_hops_per_session']:.1f}")

    print("\nMost Accessed Docs:")
    for doc, count in metrics['most_accessed_docs']:
        print(f"  {doc}: {count}")

    print("\nEntry Points:")
    for entry_point, count in metrics['entry_points']:
        print(f"  {entry_point}: {count}")


if __name__ == "__main__":
    main()
