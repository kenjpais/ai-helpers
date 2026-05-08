"""
Execution Metrics - Track and display execution metrics for agentic-docs commands

Based on REFACTOR_MAY_8.md requirements for metrics display after execution.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class ExecutionMetrics:
    """Container for execution metrics"""

    command: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

    # Tracking
    tools_used: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    skills_invoked: List[str] = field(default_factory=list)
    files_accessed: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    agents_spawned: List[str] = field(default_factory=list)

    # Results
    files_created: int = 0
    files_modified: int = 0
    errors: List[str] = field(default_factory=list)

    def record_tool_use(self, tool_name: str):
        """Record tool usage"""
        self.tools_used[tool_name] += 1

    def record_skill_invocation(self, skill_name: str):
        """Record skill invocation"""
        if skill_name not in self.skills_invoked:
            self.skills_invoked.append(skill_name)

    def record_file_access(self, file_path: str):
        """Record file access"""
        if file_path not in self.files_accessed:
            self.files_accessed.append(file_path)

    def record_data_source(self, source: str):
        """Record data source"""
        if source not in self.data_sources:
            self.data_sources.append(source)

    def record_agent_spawn(self, agent_name: str):
        """Record agent spawn"""
        self.agents_spawned.append(agent_name)

    def record_file_creation(self):
        """Record file creation"""
        self.files_created += 1

    def record_file_modification(self):
        """Record file modification"""
        self.files_modified += 1

    def record_error(self, error: str):
        """Record error"""
        self.errors.append(error)

    def complete(self):
        """Mark execution as complete"""
        self.end_time = time.time()

    @property
    def duration_seconds(self) -> float:
        """Get execution duration in seconds"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    @property
    def duration_formatted(self) -> str:
        """Get formatted duration (e.g., '2m 34s')"""
        duration = self.duration_seconds
        minutes = int(duration // 60)
        seconds = int(duration % 60)

        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    def display(self):
        """Display execution metrics to CLI"""
        print()
        print("=" * 60)
        print("📊 Execution Metrics")
        print("=" * 60)
        print()
        print(f"Command: /{self.command}")
        print(f"Duration: {self.duration_formatted}")
        print()

        if self.files_created or self.files_modified:
            print("Files:")
            if self.files_created:
                print(f"  • Created: {self.files_created}")
            if self.files_modified:
                print(f"  • Modified: {self.files_modified}")
            print()

        if self.tools_used:
            print("Tools Used:")
            for tool, count in sorted(self.tools_used.items()):
                print(f"  • {tool}: {count} invocation(s)")
            print()

        if self.skills_invoked:
            print("Skills Invoked:")
            for skill in self.skills_invoked:
                print(f"  • {skill}")
            print()

        if self.data_sources:
            print("Data Sources:")
            for source in self.data_sources:
                print(f"  • {source}")
            print()

        if self.agents_spawned:
            print("Agents Spawned:")
            for agent in self.agents_spawned:
                print(f"  • {agent}")
            print()

        if self.errors:
            print("Errors:")
            for error in self.errors:
                print(f"  ❌ {error}")
            print()

        print("=" * 60)
        print()

    def to_dict(self) -> dict:
        """Convert metrics to dictionary for logging"""
        return {
            "command": self.command,
            "timestamp": datetime.fromtimestamp(self.start_time).isoformat(),
            "duration_seconds": self.duration_seconds,
            "duration_formatted": self.duration_formatted,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "tools_used": dict(self.tools_used),
            "skills_invoked": self.skills_invoked,
            "files_accessed": self.files_accessed[:10],  # Limit to first 10
            "data_sources": self.data_sources,
            "agents_spawned": self.agents_spawned,
            "errors": self.errors,
        }


class MetricsTracker:
    """Track metrics across multiple executions"""

    def __init__(self):
        self.executions: List[ExecutionMetrics] = []
        self.current: Optional[ExecutionMetrics] = None

    def start(self, command: str) -> ExecutionMetrics:
        """Start tracking a new execution"""
        self.current = ExecutionMetrics(command=command)
        return self.current

    def complete(self):
        """Complete current execution"""
        if self.current:
            self.current.complete()
            self.executions.append(self.current)
            metrics = self.current
            self.current = None
            return metrics
        return None

    def display_summary(self):
        """Display summary of all executions"""
        if not self.executions:
            print("No executions tracked")
            return

        print()
        print("=" * 60)
        print("📈 Execution Summary")
        print("=" * 60)
        print()
        print(f"Total Executions: {len(self.executions)}")
        print()

        # Aggregate metrics
        total_duration = sum(e.duration_seconds for e in self.executions)
        total_files_created = sum(e.files_created for e in self.executions)
        total_files_modified = sum(e.files_modified for e in self.executions)
        all_tools = defaultdict(int)
        all_skills = set()

        for execution in self.executions:
            for tool, count in execution.tools_used.items():
                all_tools[tool] += count
            all_skills.update(execution.skills_invoked)

        print(f"Total Duration: {int(total_duration // 60)}m {int(total_duration % 60)}s")
        print(f"Files Created: {total_files_created}")
        print(f"Files Modified: {total_files_modified}")
        print()

        print("Most Used Tools:")
        for tool, count in sorted(all_tools.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  • {tool}: {count}")
        print()

        print(f"Unique Skills: {len(all_skills)}")
        print()
        print("=" * 60)
        print()


# Global tracker instance
_tracker = MetricsTracker()


def get_tracker() -> MetricsTracker:
    """Get global metrics tracker instance"""
    return _tracker


def start_tracking(command: str) -> ExecutionMetrics:
    """Start tracking execution metrics"""
    return _tracker.start(command)


def complete_tracking() -> Optional[ExecutionMetrics]:
    """Complete and return current metrics"""
    return _tracker.complete()
