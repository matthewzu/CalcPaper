#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for CalculatorPaperAdvanced._evaluate_in_order() method.

Validates:
- Basic evaluation in topological order
- Forward reference resolution (variable used before definition)
- Circular dependency error messages
- Comment/empty/function-definition lines produce None results
- Pure expression lines evaluated after their dependencies
- Results indexed by original line number
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calc_paper import CalculatorPaperAdvanced


class TestEvaluateInOrderBasic:
    """Tests for basic evaluation in topological order."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    def test_single_assignment(self):
        """Single assignment line evaluates correctly."""
        lines = ['a = 5']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.results[0] is not None
        result, label, extra_info, bit_info, use_bitmap, hex_info = self.calc.results[0]
        assert result == 5
        assert label == 'a'

    def test_two_independent_assignments(self):
        """Two independent assignments both evaluate correctly."""
        lines = ['a = 5', 'b = 10']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        r0 = self.calc.results[0]
        r1 = self.calc.results[1]
        assert r0[0] == 5
        assert r0[1] == 'a'
        assert r1[0] == 10
        assert r1[1] == 'b'

    def test_sequential_dependency(self):
        """b depends on a, both evaluate correctly in order."""
        lines = ['a = 5', 'b = a + 1']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.results[0][0] == 5
        assert self.calc.results[1][0] == 6


class TestEvaluateInOrderForwardReference:
    """Tests for forward reference resolution."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    def test_simple_forward_reference(self):
        """a = b * 3 where b is defined on a later line."""
        lines = ['a = b * 3', 'b = 2']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.results[0][0] == 6  # a = 2 * 3 = 6
        assert self.calc.results[0][1] == 'a'
        assert self.calc.results[1][0] == 2
        assert self.calc.results[1][1] == 'b'

    def test_multi_level_forward_reference(self):
        """Chain: a depends on b, b depends on c, all forward references."""
        lines = ['a = b * 3', 'b = c + 1', 'c = 10']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.results[2][0] == 10  # c = 10
        assert self.calc.results[1][0] == 11  # b = c + 1 = 11
        assert self.calc.results[0][0] == 33  # a = b * 3 = 33

    def test_diamond_dependency(self):
        """d depends on b and c, both depend on a."""
        lines = ['d = b + c', 'b = a * 2', 'c = a + 1', 'a = 5']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.results[3][0] == 5   # a = 5
        assert self.calc.results[1][0] == 10  # b = 5 * 2 = 10
        assert self.calc.results[2][0] == 6   # c = 5 + 1 = 6
        assert self.calc.results[0][0] == 16  # d = 10 + 6 = 16


class TestEvaluateInOrderCircularDependency:
    """Tests for circular dependency error messages."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    def test_simple_cycle(self):
        """a = b + 1, b = a + 1 → both get circular dependency error."""
        lines = ['a = b + 1', 'b = a + 1']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        # Both lines should have error results
        assert self.calc.results[0][0] is None
        assert '循环依赖' in self.calc.results[0][2]
        assert self.calc.results[0][1] == 'a'

        assert self.calc.results[1][0] is None
        assert '循环依赖' in self.calc.results[1][2]
        assert self.calc.results[1][1] == 'b'

    def test_self_reference(self):
        """a = a + 1 → self-reference is circular."""
        lines = ['a = a + 1']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.results[0][0] is None
        assert '循环依赖' in self.calc.results[0][2]

    def test_mixed_circular_and_valid(self):
        """Some lines circular, others valid."""
        lines = [
            'a = b + 1',   # 0: circular
            'b = a + 1',   # 1: circular
            'c = 10',      # 2: valid
            'd = c * 2',   # 3: valid, depends on c
        ]
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        # Circular lines get error
        assert self.calc.results[0][0] is None
        assert '循环依赖' in self.calc.results[0][2]
        assert self.calc.results[1][0] is None
        assert '循环依赖' in self.calc.results[1][2]

        # Valid lines compute correctly
        assert self.calc.results[2][0] == 10
        assert self.calc.results[3][0] == 20


class TestEvaluateInOrderSpecialLines:
    """Tests for comment, empty, and function definition lines."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    def test_comment_line_produces_none(self):
        """Comment lines produce None results."""
        lines = ['# this is a comment', 'a = 5']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.results[0] is None
        assert self.calc.results[1][0] == 5

    def test_empty_line_produces_none(self):
        """Empty lines produce None results."""
        lines = ['a = 5', '', 'b = a + 1']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.results[0][0] == 5
        assert self.calc.results[1] is None
        assert self.calc.results[2][0] == 6

    def test_function_definition_produces_none(self):
        """Function definition lines produce None results."""
        lines = ['f(x) = x * 2', 'a = 5']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.results[0] is None
        assert self.calc.results[1][0] == 5

    def test_mixed_special_lines(self):
        """Mix of comment, empty, func def, and assignment lines."""
        lines = [
            '# header comment',   # 0: comment
            'f(x) = x + 1',       # 1: func def
            '',                    # 2: empty
            'a = 10',             # 3: assignment
            'b = a * 2',          # 4: depends on a
        ]
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.results[0] is None
        assert self.calc.results[1] is None
        assert self.calc.results[2] is None
        assert self.calc.results[3][0] == 10
        assert self.calc.results[4][0] == 20


class TestEvaluateInOrderPureExpressions:
    """Tests for pure expression lines (non-assignment)."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    def test_pure_expression_no_deps(self):
        """Pure expression with no variable references."""
        lines = ['1 + 2']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.results[0][0] == 3

    def test_pure_expression_with_forward_ref(self):
        """Pure expression referencing a variable defined later."""
        lines = ['a * 3', 'a = 10']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.results[1][0] == 10  # a = 10
        assert self.calc.results[0][0] == 30  # a * 3 = 30

    def test_pure_expression_after_multiple_deps(self):
        """Pure expression depending on multiple variables."""
        lines = ['a + b', 'a = 5', 'b = 3']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.results[1][0] == 5
        assert self.calc.results[2][0] == 3
        assert self.calc.results[0][0] == 8


class TestEvaluateInOrderResultsIndexing:
    """Tests that results are indexed by original line number."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    def test_results_length_matches_lines(self):
        """self.results has same length as input lines."""
        lines = ['a = 1', 'b = 2', 'c = 3']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert len(self.calc.results) == 3

    def test_lines_stored_correctly(self):
        """self.lines stores stripped original lines."""
        lines = ['  a = 5  ', 'b = a + 1']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.lines[0] == 'a = 5'
        assert self.calc.lines[1] == 'b = a + 1'

    def test_variables_available_after_evaluation(self):
        """Variables are stored in self.variables after evaluation."""
        lines = ['b = 2', 'a = b * 3']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.variables['a'] == 6
        assert self.calc.variables['b'] == 2


class TestEvaluateInOrderWithPresetVariables:
    """Tests for evaluation with preset variables."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    def test_preset_variable_used_in_expression(self):
        """Preset variables are available for expressions."""
        self.calc.variables = {'x': 10}
        lines = ['a = x + 5']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.results[0][0] == 15

    def test_inline_comment_stripped(self):
        """Inline comments are stripped before evaluation."""
        lines = ['a = 5 # this is a comment']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)
        self.calc._evaluate_in_order(lines, line_infos, eval_order, circular_lines)

        assert self.calc.results[0][0] == 5
