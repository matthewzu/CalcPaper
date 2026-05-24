"""
Tests for comment syntax handling in CalcPaper.

Verifies:
- parse_line() returns (None, None, None, None, False, None) for # comment lines
- Inline comments are correctly stripped via line.split('#')[0]
- SyntaxHighlighter has comment highlighting logic
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calc_paper import CalculatorPaperAdvanced
from calc_syntax import SyntaxHighlighter


class TestCommentLineHandling:
    """Verify parse_line() correctly handles lines starting with #."""

    def test_comment_line_returns_none_tuple(self):
        """A line starting with # should return all-None result."""
        calc = CalculatorPaperAdvanced()
        result = calc.parse_line("# this is a comment")
        assert result == (None, None, None, None, False, None)

    def test_comment_line_with_leading_whitespace(self):
        """A line with leading whitespace then # should also be treated as comment."""
        calc = CalculatorPaperAdvanced()
        # parse_line strips the line first, so "  # comment" becomes "# comment"
        result = calc.parse_line("  # this is a comment")
        assert result == (None, None, None, None, False, None)

    def test_empty_comment_line(self):
        """A line with just # should be treated as comment."""
        calc = CalculatorPaperAdvanced()
        result = calc.parse_line("#")
        assert result == (None, None, None, None, False, None)

    def test_comment_with_expression_content(self):
        """A comment line containing expression-like text should still be a comment."""
        calc = CalculatorPaperAdvanced()
        result = calc.parse_line("# x = 5 + 3")
        assert result == (None, None, None, None, False, None)

    def test_empty_line_returns_none_tuple(self):
        """An empty line should also return all-None result."""
        calc = CalculatorPaperAdvanced()
        result = calc.parse_line("")
        assert result == (None, None, None, None, False, None)


class TestInlineCommentStripping:
    """Verify inline comments are correctly stripped before calculation."""

    def test_expression_with_inline_comment(self):
        """'5 + 3 # add numbers' should compute as '5 + 3' = 8."""
        calc = CalculatorPaperAdvanced()
        result, label, *_ = calc.parse_line("5 + 3 # add numbers")
        assert result == 8

    def test_assignment_with_inline_comment(self):
        """'x = 10 # set x' should assign x = 10."""
        calc = CalculatorPaperAdvanced()
        result, label, *_ = calc.parse_line("x = 10 # set x to ten")
        assert result == 10
        assert label == "x"
        assert calc.variables["x"] == 10

    def test_inline_comment_does_not_affect_result(self):
        """The result of 'expr # comment' should equal the result of 'expr'."""
        calc = CalculatorPaperAdvanced()
        result_with_comment, *_ = calc.parse_line("2 * 7 # multiply")
        
        calc2 = CalculatorPaperAdvanced()
        result_without_comment, *_ = calc2.parse_line("2 * 7")
        
        assert result_with_comment == result_without_comment == 14

    def test_inline_comment_with_hash_in_expression(self):
        """Hex literals don't contain #, so no ambiguity with comments."""
        calc = CalculatorPaperAdvanced()
        result, *_ = calc.parse_line("0xFF # max byte value")
        assert result == 255


class TestSyntaxHighlighterComments:
    """Verify SyntaxHighlighter has comment highlighting logic."""

    def test_full_line_comment_tokenized_as_comment(self):
        """A line starting with # should produce a 'comment' token."""
        highlighter = SyntaxHighlighter(text_widget=None)
        tokens = highlighter.tokenize_line("# this is a comment")
        
        comment_tokens = [t for t in tokens if t.type == 'comment']
        assert len(comment_tokens) >= 1
        # The comment token should cover from # to end of line
        assert comment_tokens[0].text.startswith('#')

    def test_full_line_comment_with_leading_whitespace(self):
        """A line with leading whitespace then # should highlight the comment part."""
        highlighter = SyntaxHighlighter(text_widget=None)
        tokens = highlighter.tokenize_line("  # indented comment")
        
        comment_tokens = [t for t in tokens if t.type == 'comment']
        assert len(comment_tokens) >= 1
        # Comment should start at the # character
        assert '#' in comment_tokens[0].text

    def test_inline_comment_tokenized(self):
        """'x = 5 # comment' should have a comment token for the # part."""
        highlighter = SyntaxHighlighter(text_widget=None)
        tokens = highlighter.tokenize_line("x = 5 # comment")
        
        comment_tokens = [t for t in tokens if t.type == 'comment']
        assert len(comment_tokens) >= 1
        assert '# comment' in comment_tokens[0].text

    def test_comment_token_type_exists(self):
        """The 'comment' type should be in TOKEN_TYPES."""
        assert 'comment' in SyntaxHighlighter.TOKEN_TYPES

    def test_comment_color_defined_in_themes(self):
        """Both dark and light themes should define a color for comments."""
        from calc_syntax import DARK_THEME, LIGHT_THEME
        assert 'comment' in DARK_THEME
        assert 'comment' in LIGHT_THEME
