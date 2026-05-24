#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for CalculatorPaperAdvanced._collect_definitions() method.

Validates that the first-pass scan correctly identifies:
- Variable definitions (assignment left-hand side)
- Variable references (identifiers in expressions)
- Comment lines, empty lines, and function definitions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calc_paper import CalculatorPaperAdvanced


class TestCollectDefinitionsBasic:
    """Basic functionality tests for _collect_definitions."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    def test_simple_assignment(self):
        """Assignment line defines a variable with no uses."""
        result = self.calc._collect_definitions(['a = 1'])
        assert result[0]['defines'] == 'a'
        assert result[0]['uses'] == set()
        assert not result[0]['is_comment']
        assert not result[0]['is_empty']
        assert not result[0]['is_func_def']

    def test_assignment_with_variable_reference(self):
        """Assignment referencing another variable."""
        result = self.calc._collect_definitions(['a = b * 3'])
        assert result[0]['defines'] == 'a'
        assert result[0]['uses'] == {'b'}

    def test_multiple_references(self):
        """Assignment referencing multiple variables."""
        result = self.calc._collect_definitions(['total = price * qty + tax'])
        assert result[0]['defines'] == 'total'
        assert result[0]['uses'] == {'price', 'qty', 'tax'}

    def test_empty_line(self):
        """Empty line is correctly identified."""
        result = self.calc._collect_definitions([''])
        assert result[0]['defines'] is None
        assert result[0]['uses'] == set()
        assert result[0]['is_empty'] is True
        assert result[0]['is_comment'] is False

    def test_comment_line(self):
        """Comment line starting with # is correctly identified."""
        result = self.calc._collect_definitions(['# this is a comment'])
        assert result[0]['defines'] is None
        assert result[0]['uses'] == set()
        assert result[0]['is_comment'] is True
        assert result[0]['is_empty'] is False

    def test_indented_comment(self):
        """Comment with leading whitespace is correctly identified."""
        result = self.calc._collect_definitions(['  # indented comment'])
        assert result[0]['is_comment'] is True

    def test_function_definition(self):
        """Function definition is correctly identified."""
        result = self.calc._collect_definitions(['func(x, y) = x + y'])
        assert result[0]['defines'] is None
        assert result[0]['uses'] == set()
        assert result[0]['is_func_def'] is True

    def test_inline_comment_stripped(self):
        """Inline comments are stripped before analysis."""
        result = self.calc._collect_definitions(['total = price * qty # cost calculation'])
        assert result[0]['defines'] == 'total'
        assert result[0]['uses'] == {'price', 'qty'}

    def test_self_reference(self):
        """Self-referencing assignment includes the variable in uses."""
        result = self.calc._collect_definitions(['a = a + 1'])
        assert result[0]['defines'] == 'a'
        assert 'a' in result[0]['uses']


class TestCollectDefinitionsBuiltins:
    """Tests for built-in function handling."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    def test_hex_builtin_call(self):
        """hex() builtin call doesn't define a variable but references inner vars."""
        result = self.calc._collect_definitions(['hex(a)'])
        assert result[0]['defines'] is None
        assert 'a' in result[0]['uses']
        assert result[0]['is_func_def'] is False

    def test_bitmap_builtin_call(self):
        """bitmap() builtin call doesn't define a variable."""
        result = self.calc._collect_definitions(['bitmap(x, 1)'])
        assert result[0]['defines'] is None
        assert 'x' in result[0]['uses']

    def test_workday_builtin_call(self):
        """workday() builtin call doesn't define a variable."""
        result = self.calc._collect_definitions(['workday(Y20250101, D5)'])
        assert result[0]['defines'] is None
        # Y20250101 and D5 are reserved keywords, not variable references
        assert result[0]['uses'] == set()

    def test_global_builtin_call(self):
        """global() builtin call doesn't define a variable."""
        result = self.calc._collect_definitions(['global(myvar)'])
        assert result[0]['defines'] is None


class TestCollectDefinitionsEdgeCases:
    """Edge case tests."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    def test_hex_literal_not_treated_as_variable(self):
        """Hex literals like 0xFF should not appear in uses."""
        result = self.calc._collect_definitions(['x = 0xFF + y'])
        assert result[0]['defines'] == 'x'
        assert 'y' in result[0]['uses']
        # 0xFF should not be in uses (it starts with 0x)
        assert 'xFF' not in result[0]['uses']

    def test_reserved_keyword_not_in_uses(self):
        """Reserved keywords (date/time literals) should not appear in uses."""
        result = self.calc._collect_definitions(['Y20250101'])
        assert result[0]['defines'] is None
        assert result[0]['uses'] == set()

    def test_chinese_variable_names(self):
        """Chinese variable names are supported."""
        result = self.calc._collect_definitions(['总价 = 单价 * 数量'])
        assert result[0]['defines'] == '总价'
        assert result[0]['uses'] == {'单价', '数量'}

    def test_pure_expression_line(self):
        """Pure expression line (no assignment) has no defines but has uses."""
        result = self.calc._collect_definitions(['a + b * 3'])
        assert result[0]['defines'] is None
        assert result[0]['uses'] == {'a', 'b'}

    def test_multiple_lines(self):
        """Multiple lines are processed correctly."""
        lines = [
            'a = b * 3',
            'b = c + 1',
            'c = 10',
            '# comment',
            '',
            'result = a + b',
        ]
        result = self.calc._collect_definitions(lines)
        assert len(result) == 6
        assert result[0]['defines'] == 'a'
        assert result[0]['uses'] == {'b'}
        assert result[1]['defines'] == 'b'
        assert result[1]['uses'] == {'c'}
        assert result[2]['defines'] == 'c'
        assert result[2]['uses'] == set()
        assert result[3]['is_comment'] is True
        assert result[4]['is_empty'] is True
        assert result[5]['defines'] == 'result'
        assert result[5]['uses'] == {'a', 'b'}

    def test_swap_function_references_variable(self):
        """swap() is a builtin but its argument variables should be detected."""
        result = self.calc._collect_definitions(['swap(x)'])
        assert result[0]['defines'] is None
        assert 'x' in result[0]['uses']
        assert 'swap' not in result[0]['uses']
