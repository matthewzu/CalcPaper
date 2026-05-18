#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CalcPaper - Syntax Highlighter
Incremental syntax highlighting engine for CalcPaper expressions.

Supports highlighting: comments, variables, numbers, operators, functions,
datetime literals, global variables, errors, results, and bitmap displays.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Token:
    """A syntax token with type, text content, and position."""
    type: str
    text: str
    start: int
    end: int


# All supported token types
TOKEN_TYPES = [
    'comment', 'variable', 'number', 'operator', 'function',
    'datetime', 'global_var', 'error', 'result', 'bitmap'
]

# Dark theme colors
DARK_THEME = {
    'comment': '#6A9955',
    'variable': '#9CDCFE',
    'number': '#B5CEA8',
    'operator': '#D4D4D4',
    'function': '#DCDCAA',
    'datetime': '#CE9178',
    'global_var': '#4EC9B0',
    'error': '#F44747',
    'result': '#569CD6',
    'bitmap': '#C586C0',
}

# Light theme colors
LIGHT_THEME = {
    'comment': '#008000',
    'variable': '#001080',
    'number': '#098658',
    'operator': '#000000',
    'function': '#795E26',
    'datetime': '#A31515',
    'global_var': '#267F99',
    'error': '#CD3131',
    'result': '#0000FF',
    'bitmap': '#AF00DB',
}

# Regex patterns for tokenization
_FUNCTION_NAMES = r'(?:hex|bitmap|comma|swap|workday|global)'
_FUNCTION_PATTERN = re.compile(
    r'\b(' + _FUNCTION_NAMES + r')\s*\(', re.IGNORECASE
)
_NUMBER_PATTERN = re.compile(
    r'0[xX][0-9a-fA-F]+|0[bB][01]+|\d+\.?\d*'
)
_DATETIME_PATTERN = re.compile(
    r'(?<![a-zA-Z0-9_\u4e00-\u9fa5])([YT]\d+|[MWDhms]\d+)(?![a-zA-Z0-9_\u4e00-\u9fa5])'
)
_OPERATOR_PATTERN = re.compile(
    r'<<|>>|[+\-*/%=&|^~]'
)
_IDENTIFIER_PATTERN = re.compile(
    r'[a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*'
)


class SyntaxHighlighter:
    """Incremental syntax highlighting engine for CalcPaper."""

    TOKEN_TYPES = TOKEN_TYPES

    def __init__(self, text_widget=None, theme: str = 'dark', global_vars: set = None):
        """Initialize the syntax highlighter.

        Args:
            text_widget: A Tkinter Text widget to apply highlighting to.
                         Can be None for tokenize-only usage.
            theme: Color theme, either 'dark' or 'light'.
            global_vars: Set of variable names that are global.
        """
        self._widget = text_widget
        self._theme = theme
        self._colors = DARK_THEME.copy() if theme == 'dark' else LIGHT_THEME.copy()
        self._global_vars = global_vars if global_vars is not None else set()
        if self._widget is not None:
            self._configure_tags()

    def _configure_tags(self):
        """Configure text widget tags with current theme colors."""
        if self._widget is None:
            return
        for token_type, color in self._colors.items():
            self._widget.tag_configure(token_type, foreground=color)

    def set_theme(self, theme: str) -> None:
        """Switch the color theme.

        Args:
            theme: 'dark' or 'light'
        """
        self._theme = theme
        self._colors = DARK_THEME.copy() if theme == 'dark' else LIGHT_THEME.copy()
        if self._widget is not None:
            self._configure_tags()

    def tokenize_line(self, line: str, is_output: bool = False) -> list:
        """Tokenize a single line into a list of Token objects.

        The concatenation of all token texts equals the original line.
        Each token type belongs to TOKEN_TYPES.

        Args:
            line: The line text to tokenize.
            is_output: If True, treat as output line (check for errors/results/bitmap).

        Returns:
            List of Token objects covering the entire line.
        """
        if not line:
            return []

        # Track which character positions have been assigned a token type
        # We'll collect typed spans, then fill gaps with plain text tokens
        spans = []  # list of (start, end, type)

        if is_output:
            spans = self._tokenize_output_line(line)
        else:
            spans = self._tokenize_input_line(line)

        # Sort spans by start position
        spans.sort(key=lambda s: s[0])

        # Remove overlapping spans (first one wins)
        filtered = []
        last_end = 0
        for start, end, ttype in spans:
            if start < last_end:
                continue
            filtered.append((start, end, ttype))
            last_end = end

        # Build token list, filling gaps with None-type tokens
        tokens = []
        pos = 0
        for start, end, ttype in filtered:
            if pos < start:
                # Gap - plain text (no specific type, use 'operator' as default for whitespace/parens)
                gap_text = line[pos:start]
                tokens.append(Token(type='operator', text=gap_text, start=pos, end=start))
            tokens.append(Token(type=ttype, text=line[start:end], start=start, end=end))
            pos = end
        if pos < len(line):
            gap_text = line[pos:]
            tokens.append(Token(type='operator', text=gap_text, start=pos, end=len(line)))

        return tokens

    def _tokenize_input_line(self, line: str) -> list:
        """Tokenize an input line (expression)."""
        spans = []

        # Check for full-line comment
        stripped = line.lstrip()
        if stripped.startswith('#'):
            comment_start = line.index('#')
            spans.append((comment_start, len(line), 'comment'))
            # Leading whitespace
            return spans

        # Check for inline comment
        comment_pos = self._find_comment_pos(line)
        if comment_pos is not None:
            spans.append((comment_pos, len(line), 'comment'))
            # Only tokenize the part before the comment
            active_line = line[:comment_pos]
        else:
            active_line = line

        # Detect assignment target (variable on left side of =)
        assignment_var = None
        assignment_end = 0
        eq_match = re.match(
            r'^(\s*)([a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*)\s*=(?!=)',
            active_line
        )
        if eq_match:
            var_start = eq_match.start(2)
            var_end = eq_match.end(2)
            var_name = eq_match.group(2)
            # Check if it's a global variable
            if var_name in self._global_vars:
                spans.append((var_start, var_end, 'global_var'))
            else:
                spans.append((var_start, var_end, 'variable'))
            assignment_var = var_name
            assignment_end = var_end

        # Find functions
        for m in _FUNCTION_PATTERN.finditer(active_line):
            func_start = m.start(1)
            func_end = m.end(1)
            spans.append((func_start, func_end, 'function'))

        # Find datetime literals
        for m in _DATETIME_PATTERN.finditer(active_line):
            spans.append((m.start(1), m.end(1), 'datetime'))

        # Find numbers
        for m in _NUMBER_PATTERN.finditer(active_line):
            # Skip if inside a datetime literal or function name
            start = m.start()
            # Check if this number is part of a datetime literal
            if self._is_inside_datetime(active_line, start, m.end()):
                continue
            spans.append((start, m.end(), 'number'))

        # Find operators
        for m in _OPERATOR_PATTERN.finditer(active_line):
            spans.append((m.start(), m.end(), 'operator'))

        # Find identifiers (variables referenced in expression, not the assignment target)
        for m in _IDENTIFIER_PATTERN.finditer(active_line):
            ident_start = m.start()
            ident_end = m.end()
            ident = m.group(0)

            # Skip if it's the assignment target variable
            if assignment_var and ident_start == eq_match.start(2):
                continue

            # Skip function names (already handled)
            if ident.lower() in ('hex', 'bitmap', 'comma', 'swap', 'workday', 'global'):
                continue

            # Skip datetime literals
            if re.match(r'^[YTMWDhms]\d+$', ident):
                continue

            # Check if it's a global variable
            if ident in self._global_vars:
                spans.append((ident_start, ident_end, 'global_var'))

        return spans

    def _tokenize_output_line(self, line: str) -> list:
        """Tokenize an output line (result/error/bitmap)."""
        spans = []

        # Check for error lines
        if '错误:' in line or '错误：' in line or 'Error:' in line or '变量未定义' in line:
            spans.append((0, len(line), 'error'))
            return spans

        # Check for bitmap display (lines with bit patterns like "│0│1│0│...")
        if self._is_bitmap_line(line):
            spans.append((0, len(line), 'bitmap'))
            return spans

        # Check for result lines
        # CalcPaper output format: "expression  = result" (double space before =)
        # Find the result = sign (preceded by two or more spaces)
        result_eq = re.search(r'  =\s', line)
        if result_eq:
            result_start = result_eq.start() + 2  # position of the '='
            spans.append((result_start, len(line), 'result'))
            # Tokenize the expression part before the result
            expr_part = line[:result_eq.start()]
            expr_spans = self._tokenize_input_line(expr_part)
            spans.extend(expr_spans)
            return spans

        # Fallback: find any = sign
        eq_pos = line.find('=')
        if eq_pos >= 0:
            result_start = eq_pos
            spans.append((result_start, len(line), 'result'))
            expr_part = line[:eq_pos]
            expr_spans = self._tokenize_input_line(expr_part)
            spans.extend(expr_spans)
            return spans

        return spans

    def _is_bitmap_line(self, line: str) -> bool:
        """Check if a line is a bitmap display line."""
        # Bitmap lines typically contain box-drawing characters and bit values
        if '│' in line or '┌' in line or '└' in line or '├' in line:
            return True
        # Also check for bit index lines like "  7   6   5   4   3   2   1   0"
        if re.match(r'^\s*\d+(\s+\d+)+\s*$', line):
            return True
        return False

    def _find_comment_pos(self, line: str) -> Optional[int]:
        """Find the position of an inline comment (# not inside a string)."""
        # Simple approach: find # that's not part of a hex literal
        for i, ch in enumerate(line):
            if ch == '#':
                # Check if it's part of a hex literal (unlikely in CalcPaper)
                return i
        return None

    def _is_inside_datetime(self, line: str, num_start: int, num_end: int) -> bool:
        """Check if a number match is part of a datetime literal."""
        # Look backwards from num_start for a datetime prefix
        if num_start > 0:
            prefix_char = line[num_start - 1]
            if prefix_char in 'YTMWDhms':
                # Check that the prefix char is the start of a datetime literal
                if num_start >= 2:
                    before_prefix = line[num_start - 2]
                    if not (before_prefix.isalnum() or before_prefix == '_'):
                        return True
                else:
                    return True
        return False

    def highlight_full(self, text: str) -> None:
        """Apply syntax highlighting to the entire text in the widget.

        Args:
            text: The full text content to highlight.
        """
        if self._widget is None:
            return

        # Remove all existing tags
        for tag in TOKEN_TYPES:
            self._widget.tag_remove(tag, '1.0', 'end')

        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_num = i + 1  # Tkinter uses 1-based line numbers
            # Determine if this is an output line (heuristic: check for result patterns)
            is_output = self._is_output_line(line)
            tokens = self.tokenize_line(line, is_output=is_output)
            for token in tokens:
                if token.type in TOKEN_TYPES and token.type != 'operator':
                    start_idx = f"{line_num}.{token.start}"
                    end_idx = f"{line_num}.{token.end}"
                    self._widget.tag_add(token.type, start_idx, end_idx)

    def highlight_lines(self, line_indices: list) -> None:
        """Incrementally re-highlight specific lines.

        Only the specified lines are re-processed, making this efficient
        for incremental updates after text changes.

        Args:
            line_indices: List of 0-based line indices to re-highlight.
        """
        if self._widget is None:
            return

        for line_idx in line_indices:
            line_num = line_idx + 1  # Convert to 1-based
            start = f"{line_num}.0"
            end = f"{line_num}.end"

            # Remove existing tags for this line
            for tag in TOKEN_TYPES:
                self._widget.tag_remove(tag, start, end)

            # Get the line content from the widget
            try:
                line_text = self._widget.get(start, end)
            except Exception:
                continue

            # Tokenize and apply tags
            is_output = self._is_output_line(line_text)
            tokens = self.tokenize_line(line_text, is_output=is_output)
            for token in tokens:
                if token.type in TOKEN_TYPES and token.type != 'operator':
                    start_idx = f"{line_num}.{token.start}"
                    end_idx = f"{line_num}.{token.end}"
                    self._widget.tag_add(token.type, start_idx, end_idx)

    def _is_output_line(self, line: str) -> bool:
        """Heuristic to determine if a line is an output line."""
        if not line:
            return False
        # Output lines typically have "= result" pattern or error messages
        if '错误:' in line or '错误：' in line or 'Error:' in line:
            return True
        if '变量未定义' in line:
            return True
        if self._is_bitmap_line(line):
            return True
        # Check for "expression  = result" pattern (double space before =)
        if '  =' in line or ' = ' in line:
            return True
        return False
