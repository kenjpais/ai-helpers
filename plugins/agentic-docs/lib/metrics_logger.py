#!/usr/bin/env python3
"""
Metrics Logger for Agentic-Docs Commands

Tracks and logs execution metrics for /agentic-docs:create, /agentic-docs:validate,
and /agentic-docs:evaluate commands.

Provides:
- Real-time logging to CLI
- Persistent logging to timestamped log files
- Post-execution metrics summary
- Tool and skill usage tracking
- Agent execution flow tracking
- Data flow transparency
"""

import time
import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class LogLevel(Enum):
    """Log levels for different message types."""
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


@dataclass
class ToolInvocation:
    """Represents a single tool invocation."""
    tool_name: str
    timestamp: str
    description: Optional[str] = None
    duration_ms: Optional[float] = None


@dataclass
class SkillInvocation:
    """Represents a single skill invocation."""
    skill_name: str
    timestamp: str
    duration_ms: Optional[float] = None
    data_sources: List[str] = field(default_factory=list)


@dataclass
class AgentExecution:
    """Represents an agent or sub-agent execution."""
    agent_id: str
    agent_type: str  # "primary", "judge", "coding"
    timestamp: str
    duration_ms: Optional[float] = None
    tools_used: List[str] = field(default_factory=list)
    skills_used: List[str] = field(default_factory=list)
    files_accessed: List[str] = field(default_factory=list)


@dataclass
class DataFlow:
    """Represents data flow between components."""
    source: str
    destination: str
    data_type: str
    timestamp: str


@dataclass
class ExecutionMetrics:
    """Complete execution metrics for a command run."""
    command: str
    repository: str
    timestamp_start: str
    timestamp_end: Optional[str] = None
    duration_ms: Optional[float] = None

    # Agent tracking
    primary_agent: str = "Main Orchestrator"
    sub_agents: List[AgentExecution] = field(default_factory=list)

    # Tool and skill tracking
    tools_used: Dict[str, int] = field(default_factory=dict)
    skills_used: Dict[str, int] = field(default_factory=dict)

    # Data sources
    data_sources: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    files_accessed: List[str] = field(default_factory=list)

    # Data flow
    data_flows: List[DataFlow] = field(default_factory=list)

    # Command-specific results
    result: str = "UNKNOWN"  # "PASS", "FAIL", "COMPLETED", "ERROR"
    details: Dict[str, Any] = field(default_factory=dict)


class MetricsLogger:
    """
    Metrics logger for agentic-docs commands.

    Provides real-time CLI logging and persistent file logging with
    post-execution metrics summary.
    """

    def __init__(self, command: str, repository: str, log_dir: str = "logs"):
        """
        Initialize metrics logger.

        Args:
            command: Command name (e.g., "agentic-docs:create")
            repository: Repository path
            log_dir: Directory for log files (default: "logs")
        """
        self.command = command
        self.repository = repository
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped log file
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        safe_command = command.replace(":", "-").replace("/", "-")
        self.log_file = self.log_dir / f"{safe_command}-{timestamp}.log"

        # Initialize metrics
        self.metrics = ExecutionMetrics(
            command=command,
            repository=repository,
            timestamp_start=datetime.datetime.now().isoformat()
        )

        # Track start time for duration calculation
        self.start_time = time.time()

        # Write initial log entry
        self._log(LogLevel.INFO, f"Command invoked: {command}")
        self._log(LogLevel.INFO, f"Repository: {repository}")
        self._log(LogLevel.INFO, f"Log file: {self.log_file}")

    def _log(self, level: LogLevel, message: str):
        """
        Write log entry to file and optionally to CLI.

        Args:
            level: Log level
            message: Log message
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level.value}: {message}"

        # Write to log file
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")

        # Also print to CLI for real-time visibility
        print(f"  {log_entry}")

    def log_info(self, message: str):
        """Log INFO level message."""
        self._log(LogLevel.INFO, message)

    def log_warn(self, message: str):
        """Log WARN level message."""
        self._log(LogLevel.WARN, message)

    def log_error(self, message: str):
        """Log ERROR level message."""
        self._log(LogLevel.ERROR, message)

    def log_debug(self, message: str):
        """Log DEBUG level message."""
        self._log(LogLevel.DEBUG, message)

    def log_tool_invocation(self, tool_name: str, description: Optional[str] = None):
        """
        Log a tool invocation.

        Args:
            tool_name: Name of the tool (e.g., "Read", "Bash", "Agent")
            description: Optional description of what the tool did
        """
        timestamp = datetime.datetime.now().isoformat()

        # Track in metrics
        if tool_name not in self.metrics.tools_used:
            self.metrics.tools_used[tool_name] = 0
        self.metrics.tools_used[tool_name] += 1

        # Log to file
        msg = f"Tool used: {tool_name}"
        if description:
            msg += f" - {description}"
        self._log(LogLevel.INFO, msg)

    def log_skill_invocation(self, skill_name: str, data_sources: List[str] = None):
        """
        Log a skill invocation.

        Args:
            skill_name: Name of the skill (e.g., "generate-design-md")
            data_sources: Optional list of data sources used by the skill
        """
        timestamp = datetime.datetime.now().isoformat()

        # Track in metrics
        if skill_name not in self.metrics.skills_used:
            self.metrics.skills_used[skill_name] = 0
        self.metrics.skills_used[skill_name] += 1

        # Track data sources
        if data_sources:
            for source in data_sources:
                if source not in self.metrics.data_sources:
                    self.metrics.data_sources.append(source)

        # Log to file
        msg = f"Skill invoked: {skill_name}"
        if data_sources:
            msg += f" (sources: {', '.join(data_sources)})"
        self._log(LogLevel.INFO, msg)

    def log_agent_spawn(self, agent_id: str, agent_type: str):
        """
        Log spawning of a sub-agent.

        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent ("judge", "coding", etc.)
        """
        agent = AgentExecution(
            agent_id=agent_id,
            agent_type=agent_type,
            timestamp=datetime.datetime.now().isoformat()
        )
        self.metrics.sub_agents.append(agent)

        self._log(LogLevel.INFO, f"Spawning {agent_type} sub-agent (ID: {agent_id})")

    def log_data_flow(self, source: str, destination: str, data_type: str):
        """
        Log data flow between components.

        Args:
            source: Source of the data
            destination: Destination of the data
            data_type: Type of data being transferred
        """
        flow = DataFlow(
            source=source,
            destination=destination,
            data_type=data_type,
            timestamp=datetime.datetime.now().isoformat()
        )
        self.metrics.data_flows.append(flow)

        self._log(LogLevel.INFO, f"Data flow: {source} → {destination} ({data_type})")

    def log_file_access(self, file_path: str):
        """
        Log file access.

        Args:
            file_path: Path to the file accessed
        """
        if file_path not in self.metrics.files_accessed:
            self.metrics.files_accessed.append(file_path)

        self._log(LogLevel.DEBUG, f"File accessed: {file_path}")

    def log_file_created(self, file_path: str):
        """
        Log file creation.

        Args:
            file_path: Path to the file created
        """
        if file_path not in self.metrics.files_created:
            self.metrics.files_created.append(file_path)

        self._log(LogLevel.INFO, f"File created: {file_path}")

    def log_key_decision(self, decision: str):
        """
        Log a key decision made during execution.

        Args:
            decision: Description of the decision
        """
        self._log(LogLevel.INFO, f"**Key Decision**: {decision}")

    def finalize(self, result: str, details: Dict[str, Any] = None):
        """
        Finalize metrics and display summary.

        Args:
            result: Overall result ("PASS", "FAIL", "COMPLETED", "ERROR")
            details: Optional command-specific result details
        """
        # Calculate final metrics
        self.metrics.timestamp_end = datetime.datetime.now().isoformat()
        self.metrics.duration_ms = (time.time() - self.start_time) * 1000
        self.metrics.result = result
        if details:
            self.metrics.details = details

        # Log completion
        duration_sec = self.metrics.duration_ms / 1000
        self._log(LogLevel.INFO, f"Command completed: {result}")
        self._log(LogLevel.INFO, f"Total duration: {duration_sec:.1f}s")

        # Display CLI summary
        self._display_metrics_summary()

        # Write metrics to JSON file
        metrics_file = self.log_file.with_suffix(".metrics.json")
        with open(metrics_file, "w") as f:
            json.dump(asdict(self.metrics), f, indent=2)

        print(f"\nMetrics saved: {metrics_file}")

    def _display_metrics_summary(self):
        """Display post-execution metrics summary to CLI."""
        duration_sec = self.metrics.duration_ms / 1000

        print("\n" + "━" * 70)
        print("📊 Execution Metrics")
        print("━" * 70)
        print(f"\nCommand: {self.command}")
        print(f"Duration: {duration_sec:.1f}s")
        print(f"Result: {self.metrics.result}")

        # Agent execution
        if self.metrics.sub_agents:
            print(f"\nAgent Execution:")
            print(f"  Primary Agent: {self.metrics.primary_agent}")
            print(f"  Sub-Agents spawned: {len(self.metrics.sub_agents)}")
            for agent in self.metrics.sub_agents:
                print(f"    • {agent.agent_type} (ID: {agent.agent_id})")

        # Tool usage
        if self.metrics.tools_used:
            print(f"\nTools Used:")
            for tool, count in sorted(self.metrics.tools_used.items(), key=lambda x: -x[1]):
                print(f"  • {tool}: {count} invocations")

        # Skill usage
        if self.metrics.skills_used:
            print(f"\nSkills Used:")
            for skill, count in sorted(self.metrics.skills_used.items(), key=lambda x: -x[1]):
                print(f"  • {skill}: {count} invocations")

        # Data sources
        if self.metrics.data_sources:
            print(f"\nData Sources ({len(self.metrics.data_sources)}):")
            for source in self.metrics.data_sources[:10]:  # Limit to first 10
                print(f"  • {source}")
            if len(self.metrics.data_sources) > 10:
                print(f"  ... and {len(self.metrics.data_sources) - 10} more")

        # Files created
        if self.metrics.files_created:
            print(f"\nFiles Created: {len(self.metrics.files_created)}")

        # Files accessed
        if self.metrics.files_accessed:
            print(f"\nFiles Accessed: {len(self.metrics.files_accessed)}")

        # Command-specific details
        if self.metrics.details:
            print(f"\nDetails:")
            for key, value in self.metrics.details.items():
                print(f"  {key}: {value}")

        print(f"\nLog file: {self.log_file}")
        print("━" * 70)
