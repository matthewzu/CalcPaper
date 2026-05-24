#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CalcPaper - Incremental Calculation Engine and Dependency Graph

This module provides:
- LineResult: Data class representing the result of calculating a single line.
- DependencyGraph: Line-level dependency graph for tracking variable definitions
  and usages across lines, supporting transitive dependency resolution.
- IncrementalCalcEngine: Wraps CalculatorPaperAdvanced to provide incremental
  calculation capabilities, only recalculating changed lines and their dependents.

Copyright (C) 2026 matthewzu <xiaofeng_zu@163.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from __future__ import annotations

import re
import copy
from dataclasses import dataclass, field
from typing import Any, Optional

from calc_paper import CalculatorPaperAdvanced
from calc_session import GlobalVariableStore


@dataclass
class LineResult:
    """行计算结果"""
    line_index: int
    input_line: str
    output_line: str
    result_value: Any
    variables_defined: list[str] = field(default_factory=list)
    variables_used: list[str] = field(default_factory=list)
    is_error: bool = False
    error_message: Optional[str] = None


class DependencyGraph:
    """行级别依赖关系图
    
    Tracks which variables each line defines and uses, enabling efficient
    determination of which lines need recalculation when a line changes.
    Supports transitive dependency resolution: if line A defines x, line B
    uses x and defines y, and line C uses y, then changing A affects B and C.
    """

    def __init__(self):
        self._defines: dict[int, set[str]] = {}      # line_index -> set of defined variable names
        self._uses: dict[int, set[str]] = {}          # line_index -> set of used variable names
        self._var_to_line: dict[str, int] = {}        # variable_name -> line_index that defines it

    def build(self, line_results: list[LineResult]) -> None:
        """从 LineResult 列表构建依赖图
        
        Clears existing graph data and rebuilds from scratch based on
        the provided line results.
        
        Args:
            line_results: List of LineResult objects from a full calculation.
        """
        self._defines.clear()
        self._uses.clear()
        self._var_to_line.clear()

        for result in line_results:
            idx = result.line_index
            self._defines[idx] = set(result.variables_defined)
            self._uses[idx] = set(result.variables_used)
            for var_name in result.variables_defined:
                self._var_to_line[var_name] = idx

    def get_affected_lines(self, changed_lines: list[int]) -> list[int]:
        """给定变化行，返回所有需要重算的行（含传递依赖），按行号排序
        
        Uses BFS to find all transitively affected lines. A line is affected
        if it uses a variable defined by a changed line, or if it uses a
        variable defined by another affected line.
        
        Args:
            changed_lines: List of line indices that have changed.
            
        Returns:
            Sorted list of all line indices that need recalculation,
            including the changed lines themselves.
        """
        affected = set(changed_lines)
        queue = list(changed_lines)

        while queue:
            current_line = queue.pop(0)
            # Find variables defined by this line
            defined_vars = self._defines.get(current_line, set())
            if not defined_vars:
                continue

            # Find all lines that use any of these variables
            for line_idx, used_vars in self._uses.items():
                if line_idx not in affected:
                    if used_vars & defined_vars:
                        affected.add(line_idx)
                        queue.append(line_idx)

        return sorted(affected)

    def update_line(self, line_index: int, result: LineResult) -> None:
        """更新单行的依赖信息
        
        Updates the graph for a single line after recalculation. Removes
        old variable mappings and adds new ones.
        
        Args:
            line_index: The line index to update.
            result: The new LineResult for this line.
        """
        # Remove old variable-to-line mappings for this line
        old_defines = self._defines.get(line_index, set())
        for var_name in old_defines:
            if self._var_to_line.get(var_name) == line_index:
                del self._var_to_line[var_name]

        # Update with new data
        self._defines[line_index] = set(result.variables_defined)
        self._uses[line_index] = set(result.variables_used)
        for var_name in result.variables_defined:
            self._var_to_line[var_name] = line_index

    def get_line_defines(self, line_index: int) -> set[str]:
        """获取指定行定义的变量集合"""
        return self._defines.get(line_index, set())

    def get_line_uses(self, line_index: int) -> set[str]:
        """获取指定行使用的变量集合"""
        return self._uses.get(line_index, set())

    def get_var_definition_line(self, var_name: str) -> Optional[int]:
        """获取定义指定变量的行号"""
        return self._var_to_line.get(var_name)


# Regex patterns for variable detection
_ASSIGNMENT_PATTERN = re.compile(
    r'^([a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*)\s*=\s*(.+)$'
)
_VARIABLE_REF_PATTERN = re.compile(
    r'\b([a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*)\b'
)
# Reserved keywords and function names that should not be treated as variable references
_RESERVED_NAMES = frozenset([
    'swap', 'bitmap', 'hex', 'comma', 'workday', 'global',
    'True', 'False', 'None',
])


def _detect_variables_defined(line: str) -> list[str]:
    """Detect variables defined (assigned) in a line.
    
    Looks for patterns like `variable_name = expression`.
    
    Args:
        line: The input line text (stripped).
        
    Returns:
        List of variable names defined in this line (usually 0 or 1).
    """
    if not line or line.startswith('#'):
        return []

    # Remove inline comments
    if '#' in line:
        line = line.split('#')[0].strip()

    # Skip function-style calls (hex(...), bitmap(...), comma(...), workday(...), global(...))
    func_pattern = r'^(hex|bitmap|comma|workday|global)\s*\('
    if re.match(func_pattern, line, re.IGNORECASE):
        return []

    match = _ASSIGNMENT_PATTERN.match(line.strip())
    if match:
        var_name = match.group(1)
        # Check it's not a reserved keyword
        if var_name not in _RESERVED_NAMES and not re.match(r'^[YTMWDhms]\d+$', var_name):
            return [var_name]
    return []


def _detect_variables_used(line: str, defined_vars: list[str] = None) -> list[str]:
    """Detect variables referenced (used) in a line.
    
    Scans the expression part of the line for variable references,
    excluding the variable being defined (if any) and reserved names.
    
    Args:
        line: The input line text (stripped).
        defined_vars: Variables defined in this line (to exclude from usage).
        
    Returns:
        List of variable names used in this line.
    """
    if not line or line.startswith('#'):
        return []

    if defined_vars is None:
        defined_vars = []

    # Remove inline comments
    if '#' in line:
        line = line.split('#')[0].strip()

    # Get the expression part (right side of assignment, or the whole line)
    expr = line
    match = _ASSIGNMENT_PATTERN.match(line.strip())
    if match:
        expr = match.group(2)

    # Strip function wrappers (hex(...), bitmap(...), comma(...))
    func_pattern = r'^(hex|bitmap|comma)\s*\(\s*(.+?)\s*(?:,\s*[^)]+)?\s*\)$'
    func_match = re.match(func_pattern, expr.strip(), re.IGNORECASE)
    if func_match:
        expr = func_match.group(2)

    # Also handle the case where the whole line is a function call
    if not match:
        func_line_pattern = r'^(hex|bitmap|comma|workday)\s*\(\s*(.+?)\s*(?:,\s*[^)]+)?\s*\)$'
        func_line_match = re.match(func_line_pattern, line.strip(), re.IGNORECASE)
        if func_line_match:
            expr = func_line_match.group(2)

    # Find all variable references in the expression
    used = []
    defined_set = set(defined_vars)
    for m in _VARIABLE_REF_PATTERN.finditer(expr):
        var_name = m.group(1)
        if (var_name not in _RESERVED_NAMES and
                var_name not in defined_set and
                not re.match(r'^[YTMWDhms]\d+$', var_name) and
                not re.match(r'^0[xXbB]', var_name)):
            if var_name not in used:
                used.append(var_name)
    return used


class IncrementalCalcEngine:
    """支持增量计算的引擎包装器
    
    Wraps the existing CalculatorPaperAdvanced engine to provide:
    - Full calculation with dependency graph building
    - Incremental calculation (only recalculate changed lines and dependents)
    - Line preview without modifying state
    - Dependency/dependent queries
    
    Usage:
        calculator = CalculatorPaperAdvanced()
        global_store = GlobalVariableStore()
        engine = IncrementalCalcEngine(calculator, global_store)
        results = engine.process_full("a = 1\\nb = a + 1")
        # After editing line 0:
        new_results = engine.process_incremental(old_text, new_text, [0])
    """

    def __init__(self, calculator: CalculatorPaperAdvanced, global_store: GlobalVariableStore):
        """包装现有计算引擎，添加增量计算能力
        
        Args:
            calculator: The CalculatorPaperAdvanced instance to wrap.
            global_store: The GlobalVariableStore for cross-session variables.
        """
        self._calculator = calculator
        self._global_store = global_store
        self._dep_graph = DependencyGraph()
        self._last_results: list[LineResult] = []
        self._last_text: str = ""

    @property
    def dependency_graph(self) -> DependencyGraph:
        """Access the internal dependency graph."""
        return self._dep_graph

    @property
    def last_results(self) -> list[LineResult]:
        """Access the last calculation results."""
        return self._last_results

    def process_full(self, text: str) -> list[LineResult]:
        """全量计算并建立依赖图
        
        Processes all lines using the wrapped calculator engine, then
        analyzes results to build the dependency graph.
        
        Args:
            text: The full input text (multi-line).
            
        Returns:
            List of LineResult objects for each line.
        """
        self._last_text = text
        
        # Use the existing calculator to process all text
        # Pass global variables as preset so they're available during calculation
        global_vars = self._global_store.get_all()
        self._calculator.process_text(text, preset_variables=global_vars if global_vars else None)
        
        # Build LineResult list from calculator state
        lines = text.strip().split('\n') if text.strip() else []
        line_results = []

        for i, input_line in enumerate(lines):
            input_line_stripped = input_line.strip()
            
            # Detect variables
            vars_defined = _detect_variables_defined(input_line_stripped)
            vars_used = _detect_variables_used(input_line_stripped, vars_defined)

            # Get result from calculator
            result_value = None
            is_error = False
            error_message = None
            output_line = input_line_stripped

            if i < len(self._calculator.results):
                result_info = self._calculator.results[i]
                if result_info is not None:
                    result, label, extra_info, bit_info, use_bitmap, hex_info = result_info
                    result_value = result
                    if result is None and extra_info and ('错误' in str(extra_info) or '变量未定义' in str(extra_info)):
                        is_error = True
                        error_message = extra_info
                        output_line = f"{input_line_stripped}  # {extra_info}"
                    elif result is not None:
                        # Format output line
                        if hex_info:
                            result_str = hex_info
                        elif isinstance(result, int):
                            result_str = str(result)
                        elif isinstance(result, float):
                            if result == int(result):
                                result_str = str(int(result))
                            else:
                                result_str = f"{result:.2f}"
                        else:
                            result_str = str(result)
                        
                        if extra_info and not is_error:
                            output_line = f"{input_line_stripped}  = {result_str}  # {extra_info}"
                        else:
                            output_line = f"{input_line_stripped}  = {result_str}"

            lr = LineResult(
                line_index=i,
                input_line=input_line_stripped,
                output_line=output_line,
                result_value=result_value,
                variables_defined=vars_defined,
                variables_used=vars_used,
                is_error=is_error,
                error_message=error_message,
            )
            line_results.append(lr)

        # Build dependency graph
        self._dep_graph.build(line_results)
        self._last_results = line_results
        return line_results

    def process_incremental(self, old_text: str, new_text: str, changed_lines: list[int]) -> list[LineResult]:
        """增量计算：仅重算变化行及其依赖行
        
        Identifies which lines need recalculation based on the dependency
        graph, then recalculates only those lines. Falls back to full
        calculation if the number of lines changed.
        
        Args:
            old_text: The previous text content.
            new_text: The new text content after editing.
            changed_lines: List of line indices that were directly modified.
            
        Returns:
            Complete list of LineResult objects for all lines in new_text.
        """
        old_lines = old_text.strip().split('\n') if old_text.strip() else []
        new_lines = new_text.strip().split('\n') if new_text.strip() else []

        # If line count changed, fall back to full calculation
        if len(old_lines) != len(new_lines):
            return self.process_full(new_text)

        # Get all affected lines (changed + transitive dependents)
        affected_lines = self._dep_graph.get_affected_lines(changed_lines)

        # Recalculate by processing the full text with the calculator
        # (since the calculator maintains variable state sequentially)
        # We need to re-process from the beginning to maintain correct variable state
        self._calculator.lines = []
        self._calculator.results = []
        # Start with global variables as base (local assignments will override)
        global_vars = self._global_store.get_all()
        self._calculator.variables = dict(global_vars) if global_vars else {}

        all_lines = new_text.strip().split('\n') if new_text.strip() else []
        
        for line in all_lines:
            original_line = line.strip()
            if not original_line:
                self._calculator.lines.append('')
                self._calculator.results.append(None)
                continue
            if original_line.startswith('#'):
                self._calculator.lines.append(original_line)
                self._calculator.results.append(None)
                continue
            result, label, extra_info, bit_info, use_bitmap, hex_info = self._calculator.parse_line(line)
            self._calculator.lines.append(original_line)
            if result is not None:
                self._calculator.results.append((result, label, extra_info, bit_info, use_bitmap, hex_info))
            else:
                self._calculator.results.append((None, label, extra_info, bit_info, use_bitmap, hex_info))

        # Build new LineResult list
        line_results = []
        for i, input_line in enumerate(all_lines):
            input_line_stripped = input_line.strip()
            vars_defined = _detect_variables_defined(input_line_stripped)
            vars_used = _detect_variables_used(input_line_stripped, vars_defined)

            result_value = None
            is_error = False
            error_message = None
            output_line = input_line_stripped

            if i < len(self._calculator.results):
                result_info = self._calculator.results[i]
                if result_info is not None:
                    result, label, extra_info, bit_info, use_bitmap, hex_info = result_info
                    result_value = result
                    if result is None and extra_info and ('错误' in str(extra_info) or '变量未定义' in str(extra_info)):
                        is_error = True
                        error_message = extra_info
                        output_line = f"{input_line_stripped}  # {extra_info}"
                    elif result is not None:
                        if hex_info:
                            result_str = hex_info
                        elif isinstance(result, int):
                            result_str = str(result)
                        elif isinstance(result, float):
                            if result == int(result):
                                result_str = str(int(result))
                            else:
                                result_str = f"{result:.2f}"
                        else:
                            result_str = str(result)
                        
                        if extra_info and not is_error:
                            output_line = f"{input_line_stripped}  = {result_str}  # {extra_info}"
                        else:
                            output_line = f"{input_line_stripped}  = {result_str}"

            lr = LineResult(
                line_index=i,
                input_line=input_line_stripped,
                output_line=output_line,
                result_value=result_value,
                variables_defined=vars_defined,
                variables_used=vars_used,
                is_error=is_error,
                error_message=error_message,
            )
            line_results.append(lr)

        # Update dependency graph
        for line_idx in affected_lines:
            if line_idx < len(line_results):
                self._dep_graph.update_line(line_idx, line_results[line_idx])

        # Also update any newly changed lines that weren't in the old graph
        for line_idx in changed_lines:
            if line_idx < len(line_results) and line_idx not in affected_lines:
                self._dep_graph.update_line(line_idx, line_results[line_idx])

        self._last_results = line_results
        self._last_text = new_text
        return line_results

    def get_dependencies(self, line_index: int) -> set[int]:
        """获取指定行依赖的所有行号
        
        Returns the set of line indices that define variables used by
        the specified line.
        
        Args:
            line_index: The line index to query.
            
        Returns:
            Set of line indices that this line depends on.
        """
        used_vars = self._dep_graph.get_line_uses(line_index)
        dependencies = set()
        for var_name in used_vars:
            def_line = self._dep_graph.get_var_definition_line(var_name)
            if def_line is not None and def_line != line_index:
                dependencies.add(def_line)
        return dependencies

    def get_dependents(self, line_index: int) -> set[int]:
        """获取依赖于指定行的所有行号
        
        Returns the set of line indices that use variables defined by
        the specified line.
        
        Args:
            line_index: The line index to query.
            
        Returns:
            Set of line indices that depend on this line.
        """
        defined_vars = self._dep_graph.get_line_defines(line_index)
        dependents = set()
        for other_line, used_vars in self._dep_graph._uses.items():
            if other_line != line_index and used_vars & defined_vars:
                dependents.add(other_line)
        return dependents

    def preview_line(self, line_text: str) -> Optional[LineResult]:
        """预览单行计算结果（不修改状态）
        
        Creates a temporary calculator state, evaluates the line, and
        returns the result without modifying the main engine state.
        Returns None for incomplete or invalid expressions.
        
        Args:
            line_text: The line text to preview.
            
        Returns:
            A LineResult if the expression is valid and complete, None otherwise.
        """
        line_text = line_text.strip()
        if not line_text:
            return None

        # Skip comments
        if line_text.startswith('#'):
            return None

        # Create a temporary calculator with the current variable state
        temp_calc = CalculatorPaperAdvanced(language=self._calculator.language)
        temp_calc.variables = dict(self._calculator.variables)

        # Also inject global variables (lower priority than local)
        for name, value in self._global_store.get_all().items():
            if name not in temp_calc.variables:
                temp_calc.variables[name] = value

        try:
            result, label, extra_info, bit_info, use_bitmap, hex_info = temp_calc.parse_line(line_text)
        except Exception:
            return None

        # If result is None and there's an error, return None (requirement 10.3)
        if result is None:
            if extra_info and ('错误' in str(extra_info) or '变量未定义' in str(extra_info)):
                return None
            # No result and no error means empty/comment line
            return None

        # Build output line
        if hex_info:
            result_str = hex_info
        elif isinstance(result, int):
            result_str = str(result)
        elif isinstance(result, float):
            if result == int(result):
                result_str = str(int(result))
            else:
                result_str = f"{result:.2f}"
        else:
            result_str = str(result)

        if extra_info and not ('错误' in str(extra_info) or '变量未定义' in str(extra_info)):
            output_line = f"{line_text}  = {result_str}  # {extra_info}"
        else:
            output_line = f"{line_text}  = {result_str}"

        vars_defined = _detect_variables_defined(line_text)
        vars_used = _detect_variables_used(line_text, vars_defined)

        return LineResult(
            line_index=-1,  # Preview doesn't have a real line index
            input_line=line_text,
            output_line=output_line,
            result_value=result,
            variables_defined=vars_defined,
            variables_used=vars_used,
            is_error=False,
            error_message=None,
        )
