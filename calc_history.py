#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CalcPaper - Git History Store Module

Provides Git-based history storage for calculation sessions.
Falls back to in-memory history when Git is unavailable.

Copyright (C) 2026 matthewzu <xiaofeng_zu@163.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from __future__ import annotations

import os
import sys
import subprocess
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Hide console window on Windows when calling git
_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


@dataclass
class HistoryEntry:
    """A single history entry representing a Git commit."""
    commit_hash: str
    timestamp: datetime
    message: str
    session_id: str


@dataclass
class DiffLine:
    """A single line in a diff result."""
    type: str  # 'add', 'delete', 'context'
    content: str
    old_line_no: Optional[int]
    new_line_no: Optional[int]


@dataclass
class DiffResult:
    """The diff between a commit and its parent."""
    commit_hash: str
    parent_hash: Optional[str]
    lines: list[DiffLine] = field(default_factory=list)


class GitHistoryStore:
    """Git-based calculation history storage.

    Stores input/output snapshots as Git commits, enabling version history,
    diff viewing, and content restoration. Falls back to in-memory mode
    when Git is unavailable.
    """

    def __init__(self, repo_path: str = "~/.calcpaper/history"):
        """Initialize or open a Git repository for history storage.

        Args:
            repo_path: Path to the Git repository. Defaults to ~/.calcpaper/history.
        """
        self._repo_path = Path(os.path.expanduser(repo_path))
        self._git_available = False
        self._git_ready = False  # True once async init completes
        self._warning_message: Optional[str] = None
        self._memory_history: list[HistoryEntry] = []
        self._memory_snapshots: dict[str, tuple[str, str]] = {}  # commit_hash -> (input, output)
        self._memory_counter = 0

        # Start git check and init in background thread to avoid blocking UI
        import threading
        self._init_thread = threading.Thread(target=self._async_init, daemon=True)
        self._init_thread.start()

    def _async_init(self):
        """Background initialization: check git and init repo."""
        self._git_available = self._check_git_available()
        if self._git_available:
            self._init_repo()
            self._git_ready = True
        else:
            self._warning_message = (
                "⚠ Git 未安装，历史记录仅保存在内存中。\n"
                "请安装 Git 以启用持久化历史功能：https://git-scm.com/downloads"
            )

    def is_available(self) -> bool:
        """Check if Git is available and the repository is functional.

        Returns:
            True if Git is available and repo is initialized, False otherwise.
        """
        return self._git_available and self._git_ready

    @property
    def warning_message(self) -> Optional[str]:
        """Get the warning message if Git is not available.

        Returns:
            Warning message string, or None if Git is available.
        """
        return self._warning_message

    def commit(self, session_id: str, input_text: str, output_text: str,
               message: str = None) -> Optional[str]:
        """Commit a calculation snapshot.

        Saves input as session.txt and output as output.txt in a session
        subdirectory, then creates a Git commit.

        Args:
            session_id: Identifier for the session.
            input_text: The input text content.
            output_text: The output/result text content.
            message: Optional commit message. Auto-generated if not provided.

        Returns:
            The commit hash string, or None if content is unchanged.
        """
        if not self.has_changes(session_id, input_text, output_text):
            return None

        timestamp = datetime.now()
        if message is None:
            message = self._generate_commit_message(timestamp, input_text)

        if self._git_available and self._git_ready:
            return self._git_commit(session_id, input_text, output_text, message, timestamp)
        else:
            return self._memory_commit(session_id, input_text, output_text, message, timestamp)

    def has_changes(self, session_id: str, input_text: str, output_text: str) -> bool:
        """Check if content differs from the last commit for this session.

        Args:
            session_id: Identifier for the session.
            input_text: The current input text.
            output_text: The current output text.

        Returns:
            True if content has changed, False if identical to last commit.
        """
        if self._git_available and self._git_ready:
            return self._git_has_changes(session_id, input_text, output_text)
        else:
            return self._memory_has_changes(session_id, input_text, output_text)

    def get_history(self, session_id: str, limit: int = 100) -> list[HistoryEntry]:
        """Get history entries for a session in reverse chronological order.

        Args:
            session_id: Identifier for the session.
            limit: Maximum number of entries to return.

        Returns:
            List of HistoryEntry objects, newest first.
        """
        if self._git_available and self._git_ready:
            return self._git_get_history(session_id, limit)
        else:
            return self._memory_get_history(session_id, limit)

    def get_diff(self, commit_hash: str) -> DiffResult:
        """Get the diff for a specific commit relative to its parent.

        Args:
            commit_hash: The commit hash to get diff for.

        Returns:
            DiffResult containing the diff lines.
        """
        if self._git_available and self._git_ready:
            return self._git_get_diff(commit_hash)
        else:
            return self._memory_get_diff(commit_hash)

    def restore(self, commit_hash: str) -> tuple[str, str]:
        """Restore content from a specific commit.

        Args:
            commit_hash: The commit hash to restore from.

        Returns:
            Tuple of (input_text, output_text) from the commit.
        """
        if self._git_available and self._git_ready:
            return self._git_restore(commit_hash)
        else:
            return self._memory_restore(commit_hash)

    # -------------------------------------------------------------------------
    # Private: Git availability and initialization
    # -------------------------------------------------------------------------

    def _check_git_available(self) -> bool:
        """Check if git command is available on the system."""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=_SUBPROCESS_FLAGS,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return False

    def _init_repo(self) -> None:
        """Initialize the Git repository if it doesn't exist."""
        try:
            self._repo_path.mkdir(parents=True, exist_ok=True)

            # Check if already a git repo
            result = self._run_git(["rev-parse", "--is-inside-work-tree"])
            if result.returncode == 0:
                return

            # Initialize new repo
            result = self._run_git(["init"])
            if result.returncode != 0:
                logger.warning("Failed to initialize git repo: %s", result.stderr)
                self._git_available = False
                return

            # Configure user for commits (local to this repo)
            self._run_git(["config", "user.email", "calcpaper@local"])
            self._run_git(["config", "user.name", "CalcPaper"])

        except OSError as e:
            logger.warning("Failed to create repo directory: %s", e)
            self._git_available = False

    def _run_git(self, args: list[str], input_text: str = None) -> subprocess.CompletedProcess:
        """Run a git command in the repository directory.

        Args:
            args: Git command arguments (without 'git' prefix).
            input_text: Optional stdin input.

        Returns:
            CompletedProcess result.
        """
        return subprocess.run(
            ["git"] + args,
            cwd=str(self._repo_path),
            capture_output=True,
            text=True,
            input=input_text,
            timeout=30,
            creationflags=_SUBPROCESS_FLAGS,
        )

    # -------------------------------------------------------------------------
    # Private: Git-based operations
    # -------------------------------------------------------------------------

    def _git_commit(self, session_id: str, input_text: str, output_text: str,
                    message: str, timestamp: datetime) -> Optional[str]:
        """Create a Git commit with the session content."""
        try:
            # Create session subdirectory
            session_dir = self._repo_path / session_id
            session_dir.mkdir(parents=True, exist_ok=True)

            # Write files
            session_file = session_dir / "session.txt"
            output_file = session_dir / "output.txt"
            session_file.write_text(input_text, encoding="utf-8")
            output_file.write_text(output_text, encoding="utf-8")

            # Stage files
            self._run_git(["add", str(session_dir / "session.txt"),
                          str(session_dir / "output.txt")])

            # Commit with timestamp in environment for reproducibility
            env_date = timestamp.isoformat()
            result = subprocess.run(
                ["git", "commit", "-m", message,
                 "--allow-empty-message"],
                cwd=str(self._repo_path),
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=_SUBPROCESS_FLAGS,
                env={**os.environ,
                     "GIT_AUTHOR_DATE": env_date,
                     "GIT_COMMITTER_DATE": env_date},
            )

            if result.returncode != 0:
                logger.warning("Git commit failed: %s", result.stderr)
                return None

            # Get the commit hash
            hash_result = self._run_git(["rev-parse", "HEAD"])
            if hash_result.returncode == 0:
                return hash_result.stdout.strip()
            return None

        except (OSError, subprocess.TimeoutExpired) as e:
            logger.warning("Git commit error: %s", e)
            return None

    def _git_has_changes(self, session_id: str, input_text: str, output_text: str) -> bool:
        """Check if content differs from last commit using Git."""
        session_dir = self._repo_path / session_id
        session_file = session_dir / "session.txt"
        output_file = session_dir / "output.txt"

        # If files don't exist yet, there are changes
        if not session_file.exists() or not output_file.exists():
            return True

        try:
            existing_input = session_file.read_text(encoding="utf-8")
            existing_output = output_file.read_text(encoding="utf-8")
            return existing_input != input_text or existing_output != output_text
        except OSError:
            return True

    def _git_get_history(self, session_id: str, limit: int) -> list[HistoryEntry]:
        """Get commit history for a session from Git log."""
        try:
            # Use git log with format to get commit info, filtered by path
            session_dir = session_id
            result = self._run_git([
                "log",
                f"--max-count={limit}",
                "--format=%H|%aI|%s",
                "--",
                session_dir,
            ])

            if result.returncode != 0:
                return []

            entries = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|", 2)
                if len(parts) < 3:
                    continue
                commit_hash, timestamp_str, message = parts
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                except ValueError:
                    timestamp = datetime.now()

                entries.append(HistoryEntry(
                    commit_hash=commit_hash,
                    timestamp=timestamp,
                    message=message,
                    session_id=session_id,
                ))

            return entries

        except (subprocess.TimeoutExpired, OSError):
            return []

    def _git_get_diff(self, commit_hash: str) -> DiffResult:
        """Get diff for a commit relative to its parent."""
        try:
            # Get parent hash
            parent_result = self._run_git(["rev-parse", f"{commit_hash}^"])
            parent_hash = None
            if parent_result.returncode == 0:
                parent_hash = parent_result.stdout.strip()

            # Get diff
            if parent_hash:
                diff_result = self._run_git([
                    "diff", "--unified=3", parent_hash, commit_hash
                ])
            else:
                # First commit - diff against empty tree
                diff_result = self._run_git([
                    "diff", "--unified=3",
                    "4b825dc642cb6eb9a060e54bf899d69f82cf7256",  # empty tree hash
                    commit_hash,
                ])

            if diff_result.returncode != 0:
                return DiffResult(commit_hash=commit_hash, parent_hash=parent_hash)

            lines = self._parse_diff_output(diff_result.stdout)
            return DiffResult(
                commit_hash=commit_hash,
                parent_hash=parent_hash,
                lines=lines,
            )

        except (subprocess.TimeoutExpired, OSError):
            return DiffResult(commit_hash=commit_hash, parent_hash=None)

    def _git_restore(self, commit_hash: str) -> tuple[str, str]:
        """Restore content from a specific Git commit."""
        try:
            # Find session files in the commit
            # List files in the commit
            ls_result = self._run_git(["ls-tree", "--name-only", "-r", commit_hash])
            if ls_result.returncode != 0:
                return ("", "")

            files = ls_result.stdout.strip().split("\n")
            input_text = ""
            output_text = ""

            for file_path in files:
                if file_path.endswith("/session.txt") or file_path == "session.txt":
                    show_result = self._run_git(["show", f"{commit_hash}:{file_path}"])
                    if show_result.returncode == 0:
                        input_text = show_result.stdout
                elif file_path.endswith("/output.txt") or file_path == "output.txt":
                    show_result = self._run_git(["show", f"{commit_hash}:{file_path}"])
                    if show_result.returncode == 0:
                        output_text = show_result.stdout

            return (input_text, output_text)

        except (subprocess.TimeoutExpired, OSError):
            return ("", "")

    # -------------------------------------------------------------------------
    # Private: In-memory fallback operations
    # -------------------------------------------------------------------------

    def _memory_commit(self, session_id: str, input_text: str, output_text: str,
                       message: str, timestamp: datetime) -> str:
        """Create an in-memory history entry."""
        self._memory_counter += 1
        commit_hash = f"mem_{self._memory_counter:08d}"

        entry = HistoryEntry(
            commit_hash=commit_hash,
            timestamp=timestamp,
            message=message,
            session_id=session_id,
        )
        self._memory_history.append(entry)
        self._memory_snapshots[commit_hash] = (input_text, output_text)

        return commit_hash

    def _memory_has_changes(self, session_id: str, input_text: str, output_text: str) -> bool:
        """Check if content differs from last in-memory entry."""
        # Find the most recent entry for this session
        for entry in reversed(self._memory_history):
            if entry.session_id == session_id:
                snapshot = self._memory_snapshots.get(entry.commit_hash)
                if snapshot:
                    return snapshot != (input_text, output_text)
                return True
        # No previous entry means there are changes
        return True

    def _memory_get_history(self, session_id: str, limit: int) -> list[HistoryEntry]:
        """Get in-memory history entries in reverse chronological order."""
        entries = [e for e in self._memory_history if e.session_id == session_id]
        # Reverse for newest-first order
        entries = list(reversed(entries))
        return entries[:limit]

    def _memory_get_diff(self, commit_hash: str) -> DiffResult:
        """Get diff for an in-memory commit."""
        current_snapshot = self._memory_snapshots.get(commit_hash)
        if not current_snapshot:
            return DiffResult(commit_hash=commit_hash, parent_hash=None)

        current_input, current_output = current_snapshot

        # Find the entry and its predecessor
        entry_index = None
        session_id = None
        for i, entry in enumerate(self._memory_history):
            if entry.commit_hash == commit_hash:
                entry_index = i
                session_id = entry.session_id
                break

        if entry_index is None:
            return DiffResult(commit_hash=commit_hash, parent_hash=None)

        # Find previous entry for same session
        parent_hash = None
        prev_input = ""
        prev_output = ""
        for i in range(entry_index - 1, -1, -1):
            if self._memory_history[i].session_id == session_id:
                parent_hash = self._memory_history[i].commit_hash
                prev_snapshot = self._memory_snapshots.get(parent_hash, ("", ""))
                prev_input, prev_output = prev_snapshot
                break

        # Generate diff lines for session.txt
        lines = self._compute_diff_lines(prev_input, current_input)

        return DiffResult(
            commit_hash=commit_hash,
            parent_hash=parent_hash,
            lines=lines,
        )

    def _memory_restore(self, commit_hash: str) -> tuple[str, str]:
        """Restore content from an in-memory snapshot."""
        snapshot = self._memory_snapshots.get(commit_hash)
        if snapshot:
            return snapshot
        return ("", "")

    # -------------------------------------------------------------------------
    # Private: Utility methods
    # -------------------------------------------------------------------------

    def _generate_commit_message(self, timestamp: datetime, input_text: str) -> str:
        """Generate a commit message with ISO timestamp and change summary.

        Args:
            timestamp: The commit timestamp.
            input_text: The input text for generating a summary.

        Returns:
            Formatted commit message string.
        """
        iso_time = timestamp.isoformat()
        # Generate a brief summary from the input
        lines = [l.strip() for l in input_text.strip().split("\n") if l.strip()]
        if lines:
            summary = lines[-1][:50]
            if len(lines[-1]) > 50:
                summary += "..."
        else:
            summary = "empty"

        return f"[{iso_time}] {summary}"

    def _parse_diff_output(self, diff_text: str) -> list[DiffLine]:
        """Parse unified diff output into DiffLine objects."""
        lines = []
        old_line = 0
        new_line = 0

        for raw_line in diff_text.split("\n"):
            # Skip diff headers
            if raw_line.startswith("diff ") or raw_line.startswith("index "):
                continue
            if raw_line.startswith("--- ") or raw_line.startswith("+++ "):
                continue
            if raw_line.startswith("@@"):
                # Parse hunk header for line numbers
                import re
                match = re.match(r"@@ -(\d+)", raw_line)
                if match:
                    old_line = int(match.group(1))
                match2 = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", raw_line)
                if match2:
                    new_line = int(match2.group(1))
                continue

            if raw_line.startswith("+"):
                lines.append(DiffLine(
                    type="add",
                    content=raw_line[1:],
                    old_line_no=None,
                    new_line_no=new_line,
                ))
                new_line += 1
            elif raw_line.startswith("-"):
                lines.append(DiffLine(
                    type="delete",
                    content=raw_line[1:],
                    old_line_no=old_line,
                    new_line_no=None,
                ))
                old_line += 1
            elif raw_line.startswith(" "):
                lines.append(DiffLine(
                    type="context",
                    content=raw_line[1:],
                    old_line_no=old_line,
                    new_line_no=new_line,
                ))
                old_line += 1
                new_line += 1

        return lines

    def _compute_diff_lines(self, old_text: str, new_text: str) -> list[DiffLine]:
        """Compute diff lines between two text strings (for in-memory mode)."""
        old_lines = old_text.split("\n") if old_text else []
        new_lines = new_text.split("\n") if new_text else []

        # Simple line-by-line diff using difflib
        import difflib
        differ = difflib.unified_diff(old_lines, new_lines, lineterm="", n=3)

        lines = []
        old_line = 0
        new_line = 0

        for raw_line in differ:
            # Skip headers
            if raw_line.startswith("---") or raw_line.startswith("+++"):
                continue
            if raw_line.startswith("@@"):
                import re
                match = re.match(r"@@ -(\d+)", raw_line)
                if match:
                    old_line = int(match.group(1))
                match2 = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", raw_line)
                if match2:
                    new_line = int(match2.group(1))
                continue

            if raw_line.startswith("+"):
                lines.append(DiffLine(
                    type="add",
                    content=raw_line[1:],
                    old_line_no=None,
                    new_line_no=new_line,
                ))
                new_line += 1
            elif raw_line.startswith("-"):
                lines.append(DiffLine(
                    type="delete",
                    content=raw_line[1:],
                    old_line_no=old_line,
                    new_line_no=None,
                ))
                old_line += 1
            else:
                lines.append(DiffLine(
                    type="context",
                    content=raw_line[1:] if raw_line.startswith(" ") else raw_line,
                    old_line_no=old_line,
                    new_line_no=new_line,
                ))
                old_line += 1
                new_line += 1

        return lines
