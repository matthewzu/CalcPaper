#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CalcPaper - Multi-session Management and Global Variable Store

This module provides:
- GlobalVariableStore: Cross-session shared global variable storage with
  observer pattern for change notification.
- SessionManager: Multi-session lifecycle management and persistence.
- Session: Data class representing a single calculator session.

Copyright (C) 2026 matthewzu <xiaofeng_zu@163.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable
from uuid import uuid4

from calc_paper import CalculatorPaperAdvanced


class GlobalVariableStore:
    """跨会话共享的全局变量存储
    
    Provides a centralized store for global variables that are shared
    across all calculator sessions. Supports an observer pattern where
    listeners are notified whenever a variable changes.
    
    Usage:
        store = GlobalVariableStore()
        store.subscribe(lambda name, value: print(f"{name} = {value}"))
        store.set("pi", 3.14159)  # Notifies all listeners
    """

    def __init__(self):
        self._variables: dict[str, Any] = {}
        self._listeners: list[Callable[[str, Any], None]] = []

    def set(self, name: str, value: Any) -> None:
        """设置全局变量并通知所有监听者
        
        Args:
            name: Variable name
            value: Variable value
        """
        self._variables[name] = value
        self._notify_listeners(name, value)

    def get(self, name: str, default: Any = None) -> Any:
        """获取全局变量值
        
        Args:
            name: Variable name
            default: Default value if variable doesn't exist
            
        Returns:
            The variable value, or default if not found
        """
        return self._variables.get(name, default)

    def has(self, name: str) -> bool:
        """检查全局变量是否存在
        
        Args:
            name: Variable name
            
        Returns:
            True if the variable exists in the store
        """
        return name in self._variables

    def get_all(self) -> dict[str, Any]:
        """获取所有全局变量
        
        Returns:
            A copy of all global variables as a dictionary
        """
        return dict(self._variables)

    def remove(self, name: str) -> None:
        """删除一个全局变量
        
        If the variable exists, it is removed and listeners are notified
        with a value of None.
        
        Args:
            name: Variable name to remove
        """
        if name in self._variables:
            del self._variables[name]
            self._notify_listeners(name, None)

    def clear(self) -> None:
        """清除所有全局变量
        
        Removes all variables and notifies listeners for each removed variable
        with a value of None.
        """
        names = list(self._variables.keys())
        self._variables.clear()
        for name in names:
            self._notify_listeners(name, None)

    def subscribe(self, callback: Callable[[str, Any], None]) -> None:
        """注册变量变更监听器
        
        The callback will be called with (name, value) whenever a variable
        is set, removed, or cleared.
        
        Args:
            callback: A callable that accepts (name: str, value: Any)
        """
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unsubscribe(self, callback: Callable[[str, Any], None]) -> None:
        """取消注册变量变更监听器
        
        Args:
            callback: The previously registered callback to remove
        """
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self, name: str, value: Any) -> None:
        """通知所有监听者变量已变更
        
        Args:
            name: The variable name that changed
            value: The new value (None if removed)
        """
        for listener in self._listeners[:]:  # Iterate over a copy for safety
            listener(name, value)


@dataclass
class Session:
    """表示一个独立的计算会话
    
    Each session has its own calculator engine instance, input/output text,
    and local variables. Sessions are identified by a unique UUID.
    """
    session_id: str
    name: str
    input_text: str = ""
    output_text: str = ""
    variables: dict = field(default_factory=dict)
    calculator: CalculatorPaperAdvanced = field(default_factory=CalculatorPaperAdvanced)
    created_at: datetime = field(default_factory=datetime.now)


class SessionManager:
    """管理多个计算会话的生命周期和持久化
    
    Provides creation, retrieval, closure, and persistence of multiple
    independent calculator sessions. Integrates with GlobalVariableStore
    for cross-session variable sharing.
    
    Usage:
        store = GlobalVariableStore()
        manager = SessionManager(store)
        session = manager.create_session("计算1")
        manager.save_all("sessions.json")
    """

    def __init__(self, global_store: GlobalVariableStore):
        self._global_store = global_store
        self._sessions: dict[str, Session] = {}
        self._session_order: list[str] = []  # Maintains tab order
        self._active_tab_index: int = 0

    @property
    def active_tab_index(self) -> int:
        """获取当前活跃标签页索引"""
        return self._active_tab_index

    @active_tab_index.setter
    def active_tab_index(self, value: int) -> None:
        """设置当前活跃标签页索引"""
        if 0 <= value < len(self._session_order):
            self._active_tab_index = value

    def create_session(self, name: str = None) -> Session:
        """创建新会话，分配独立的 CalculatorPaperAdvanced 实例
        
        Args:
            name: Session display name. If None, auto-generates "计算N".
            
        Returns:
            The newly created Session instance.
        """
        session_id = str(uuid4())
        if name is None:
            name = f"计算{len(self._sessions) + 1}"
        
        session = Session(
            session_id=session_id,
            name=name,
            calculator=CalculatorPaperAdvanced(),
            created_at=datetime.now()
        )
        self._sessions[session_id] = session
        self._session_order.append(session_id)
        return session

    def close_session(self, session_id: str) -> None:
        """关闭并释放会话资源
        
        If this is the last session, automatically creates a new blank session.
        
        Args:
            session_id: The UUID of the session to close.
            
        Raises:
            KeyError: If session_id does not exist.
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session not found: {session_id}")
        
        # Remove from order list and sessions dict
        idx = self._session_order.index(session_id)
        self._session_order.remove(session_id)
        del self._sessions[session_id]
        
        # Auto-create new blank session if last one was closed
        if len(self._sessions) == 0:
            self.create_session()
            self._active_tab_index = 0
        else:
            # Adjust active tab index
            if self._active_tab_index >= len(self._session_order):
                self._active_tab_index = len(self._session_order) - 1
            elif self._active_tab_index > idx:
                self._active_tab_index -= 1

    def get_session(self, session_id: str) -> Session:
        """获取指定会话
        
        Args:
            session_id: The UUID of the session to retrieve.
            
        Returns:
            The Session instance.
            
        Raises:
            KeyError: If session_id does not exist.
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session not found: {session_id}")
        return self._sessions[session_id]

    def list_sessions(self) -> list[Session]:
        """列出所有活跃会话（按标签页顺序）
        
        Returns:
            List of all active Session instances in tab order.
        """
        return [self._sessions[sid] for sid in self._session_order]

    def save_all(self, filepath: str) -> None:
        """持久化所有会话状态到 JSON 文件（版本 2 格式）
        
        Serializes all sessions (excluding calculator instances) and global
        variables to a JSON file.
        
        Args:
            filepath: Path to the output JSON file.
        """
        sessions_data = []
        for sid in self._session_order:
            session = self._sessions[sid]
            sessions_data.append({
                "session_id": session.session_id,
                "name": session.name,
                "input": session.input_text,
                "output": session.output_text,
                "variables": self._serialize_variables(session.variables)
            })
        
        data = {
            "version": 2,
            "active_tab_index": self._active_tab_index,
            "global_variables": self._serialize_variables(self._global_store.get_all()),
            "sessions": sessions_data
        }
        
        # Write atomically by writing to temp file first
        dir_path = os.path.dirname(filepath)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        tmp_filepath = filepath + ".tmp"
        with open(tmp_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Replace original file
        if os.path.exists(filepath):
            os.replace(tmp_filepath, filepath)
        else:
            os.rename(tmp_filepath, filepath)

    def load_all(self, filepath: str) -> None:
        """从 JSON 文件恢复所有会话
        
        Deserializes sessions and global variables from a JSON file.
        Recreates calculator instances for each session. If the file
        doesn't exist or is corrupted, creates a single blank session.
        
        Args:
            filepath: Path to the session JSON file.
        """
        if not os.path.exists(filepath):
            # File doesn't exist - start with a blank session
            if len(self._sessions) == 0:
                self.create_session()
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError, OSError):
            # Corrupted file - start with a blank session
            if len(self._sessions) == 0:
                self.create_session()
            return
        
        # Validate version
        version = data.get("version", 1)
        if version == 2:
            self._load_v2(data)
        elif version == 1:
            self._load_v1(data)
        else:
            # Unknown version - start fresh
            if len(self._sessions) == 0:
                self.create_session()

    def _load_v2(self, data: dict) -> None:
        """Load version 2 format session data."""
        # Clear existing sessions
        self._sessions.clear()
        self._session_order.clear()
        
        # Restore global variables
        global_vars = data.get("global_variables", {})
        for name, value in global_vars.items():
            self._global_store.set(name, value)
        
        # Restore sessions
        sessions_data = data.get("sessions", [])
        for session_data in sessions_data:
            session_id = session_data.get("session_id", str(uuid4()))
            name = session_data.get("name", "计算")
            input_text = session_data.get("input", "")
            output_text = session_data.get("output", "")
            variables = session_data.get("variables", {})
            
            # Create calculator and restore variables
            calculator = CalculatorPaperAdvanced()
            calculator.variables = dict(variables)
            
            session = Session(
                session_id=session_id,
                name=name,
                input_text=input_text,
                output_text=output_text,
                variables=dict(variables),
                calculator=calculator,
                created_at=datetime.now()
            )
            self._sessions[session_id] = session
            self._session_order.append(session_id)
        
        # Restore active tab index
        self._active_tab_index = data.get("active_tab_index", 0)
        if self._active_tab_index >= len(self._session_order):
            self._active_tab_index = 0
        
        # Ensure at least one session exists
        if len(self._sessions) == 0:
            self.create_session()

    def _load_v1(self, data: dict) -> None:
        """Load version 1 format (legacy single-session format)."""
        # Clear existing sessions
        self._sessions.clear()
        self._session_order.clear()
        
        # Version 1 has a single session with "input" and "output" keys
        input_text = data.get("input", "")
        output_text = data.get("output", "")
        
        calculator = CalculatorPaperAdvanced()
        session = Session(
            session_id=str(uuid4()),
            name="计算1",
            input_text=input_text,
            output_text=output_text,
            calculator=calculator,
            created_at=datetime.now()
        )
        self._sessions[session.session_id] = session
        self._session_order.append(session.session_id)
        self._active_tab_index = 0

    @staticmethod
    def _serialize_variables(variables: dict) -> dict:
        """Serialize variables dict to JSON-compatible format.
        
        Filters out non-serializable values (e.g., datetime objects)
        and converts numeric types appropriately.
        """
        result = {}
        for key, value in variables.items():
            if isinstance(value, (int, float, str, bool)):
                result[key] = value
            elif isinstance(value, (list, dict)):
                try:
                    json.dumps(value)
                    result[key] = value
                except (TypeError, ValueError):
                    pass
            # Skip non-serializable values (datetime, etc.)
        return result
