#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for CalculatorPaperAdvanced._topological_sort() method.

Validates:
- Simple linear dependency chain (a→b→c)
- Forward reference resolution
- Circular dependency detection (a→b→a)
- Self-reference detection (a = a + 1)
- Independent lines (no dependencies)
- Mixed: some circular, some not
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calc_paper import CalculatorPaperAdvanced


class TestTopologicalSortLinearChain:
    """Tests for simple linear dependency chains."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    def test_simple_chain_a_depends_on_b_depends_on_c(self):
        """a = b * 3, b = c + 1, c = 10 → eval order: c, b, a."""
        lines = ['a = b * 3', 'b = c + 1', 'c = 10']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == set()
        # c (index 2) must come before b (index 1), b before a (index 0)
        assert eval_order.index(2) < eval_order.index(1)
        assert eval_order.index(1) < eval_order.index(0)

    def test_two_line_chain(self):
        """a = b + 1, b = 5 → b evaluated before a."""
        lines = ['a = b + 1', 'b = 5']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == set()
        assert eval_order.index(1) < eval_order.index(0)

    def test_already_in_order(self):
        """c = 10, b = c + 1, a = b * 3 → already in dependency order."""
        lines = ['c = 10', 'b = c + 1', 'a = b * 3']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == set()
        assert eval_order.index(0) < eval_order.index(1)
        assert eval_order.index(1) < eval_order.index(2)


class TestTopologicalSortForwardReference:
    """Tests for forward reference resolution."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    def test_forward_reference_basic(self):
        """a = b * 3 references b defined on a later line."""
        lines = ['a = b * 3', 'b = 1']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == set()
        # b (index 1) must be evaluated before a (index 0)
        assert eval_order.index(1) < eval_order.index(0)

    def test_multi_level_forward_reference(self):
        """Multiple levels of forward references."""
        lines = ['result = a + b', 'a = b * 3', 'b = c + 1', 'c = 10']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == set()
        # c before b, b before a, a before result
        assert eval_order.index(3) < eval_order.index(2)
        assert eval_order.index(2) < eval_order.index(1)
        assert eval_order.index(1) < eval_order.index(0)


class TestTopologicalSortCircularDependency:
    """Tests for circular dependency detection."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    def test_simple_cycle_two_lines(self):
        """a = b + 1, b = a + 1 → both lines are circular."""
        lines = ['a = b + 1', 'b = a + 1']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == {0, 1}
        assert 0 not in eval_order
        assert 1 not in eval_order

    def test_three_line_cycle(self):
        """a = b, b = c, c = a → all three are circular."""
        lines = ['a = b + 1', 'b = c + 1', 'c = a + 1']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == {0, 1, 2}

    def test_self_reference(self):
        """a = a + 1 → self-reference is circular."""
        lines = ['a = a + 1']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == {0}
        assert 0 not in eval_order


class TestTopologicalSortIndependentLines:
    """Tests for independent lines with no dependencies."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    def test_all_independent(self):
        """Lines with no inter-dependencies are all in eval_order."""
        lines = ['a = 1', 'b = 2', 'c = 3']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == set()
        assert set(eval_order) == {0, 1, 2}

    def test_pure_expression_no_deps(self):
        """Pure expression with no variable references."""
        lines = ['1 + 2']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == set()
        assert 0 in eval_order

    def test_pure_expression_with_dependency(self):
        """Pure expression referencing a variable defined elsewhere."""
        lines = ['a * 3', 'a = 10']
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == set()
        # a (index 1) must be evaluated before the expression (index 0)
        assert eval_order.index(1) < eval_order.index(0)


class TestTopologicalSortMixed:
    """Tests for mixed scenarios: some circular, some not."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    def test_mixed_circular_and_non_circular(self):
        """Some lines are circular, others are not."""
        lines = [
            'a = b + 1',   # 0: circular (a→b→a)
            'b = a + 1',   # 1: circular (b→a→b)
            'c = 10',      # 2: independent
            'd = c * 2',   # 3: depends on c only
        ]
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == {0, 1}
        assert 2 in eval_order
        assert 3 in eval_order
        assert eval_order.index(2) < eval_order.index(3)

    def test_comment_and_empty_lines_excluded(self):
        """Comment and empty lines are not in eval_order or circular_lines."""
        lines = [
            '# comment',   # 0: comment
            'a = 1',       # 1: assignment
            '',            # 2: empty
            'b = a + 1',   # 3: depends on a
        ]
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == set()
        # Only lines 1 and 3 should be in eval_order
        assert set(eval_order) == {1, 3}
        assert eval_order.index(1) < eval_order.index(3)

    def test_function_definition_excluded(self):
        """Function definition lines are excluded from the graph."""
        lines = [
            'f(x) = x * 2',  # 0: func def
            'a = 5',          # 1: assignment
            'b = a + 1',      # 2: depends on a
        ]
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == set()
        assert 0 not in eval_order  # func def excluded
        assert set(eval_order) == {1, 2}
        assert eval_order.index(1) < eval_order.index(2)

    def test_diamond_dependency(self):
        """Diamond-shaped dependency: d depends on b and c, both depend on a."""
        lines = [
            'd = b + c',   # 0: depends on b, c
            'b = a * 2',   # 1: depends on a
            'c = a + 1',   # 2: depends on a
            'a = 5',       # 3: no deps
        ]
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == set()
        # a (3) must come before b (1) and c (2)
        # b (1) and c (2) must come before d (0)
        assert eval_order.index(3) < eval_order.index(1)
        assert eval_order.index(3) < eval_order.index(2)
        assert eval_order.index(1) < eval_order.index(0)
        assert eval_order.index(2) < eval_order.index(0)

    def test_partial_cycle_with_independent_chain(self):
        """Cycle in one part, valid chain in another."""
        lines = [
            'x = y + 1',   # 0: circular with y
            'y = x + 1',   # 1: circular with x
            'a = 10',      # 2: independent
            'b = a * 2',   # 3: depends on a
            'c = b + 1',   # 4: depends on b
        ]
        line_infos = self.calc._collect_definitions(lines)
        eval_order, circular_lines = self.calc._topological_sort(line_infos)

        assert circular_lines == {0, 1}
        assert {2, 3, 4}.issubset(set(eval_order))
        assert eval_order.index(2) < eval_order.index(3)
        assert eval_order.index(3) < eval_order.index(4)
