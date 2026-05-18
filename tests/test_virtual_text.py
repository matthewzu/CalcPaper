"""
Tests for VirtualTextWidget - 虚拟化文本渲染组件

Tests the core logic: buffer management, index parsing, content operations,
and visible range calculations.

Note: GUI-dependent tests (rendering, scrollbar) require a Tk root and are
tested separately. These tests focus on the data layer logic.
"""

from __future__ import annotations

import sys
import os
import tkinter as tk

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="module")
def tk_root():
    """Create a Tk root for testing (hidden)."""
    try:
        root = tk.Tk()
        root.withdraw()
        yield root
        root.destroy()
    except tk.TclError:
        pytest.skip("No display available for Tk tests")


@pytest.fixture
def widget(tk_root):
    """Create a VirtualTextWidget instance for testing."""
    from calc_virtual_text import VirtualTextWidget
    w = VirtualTextWidget(tk_root, font=("Consolas", 12))
    w.pack()
    tk_root.update_idletasks()
    return w


class TestSetAndGetContent:
    """Test set_content and get_content."""

    def test_empty_content(self, widget):
        widget.set_content([])
        assert widget.get_content() == ''

    def test_single_line(self, widget):
        widget.set_content(['hello world'])
        assert widget.get_content() == 'hello world'

    def test_multiple_lines(self, widget):
        lines = ['line 1', 'line 2', 'line 3']
        widget.set_content(lines)
        assert widget.get_content() == 'line 1\nline 2\nline 3'

    def test_large_content_enables_virtual_mode(self, widget):
        lines = [f'line {i}' for i in range(1000)]
        widget.set_content(lines)
        assert widget.is_virtual_mode is True
        assert widget.total_lines == 1000

    def test_small_content_standard_mode(self, widget):
        lines = [f'line {i}' for i in range(10)]
        widget.set_content(lines)
        assert widget.is_virtual_mode is False


class TestGetVisibleRange:
    """Test get_visible_range."""

    def test_small_content_range(self, widget):
        widget.set_content(['a', 'b', 'c'])
        start, end = widget.get_visible_range()
        assert start >= 0
        assert end <= 3

    def test_large_content_range_bounded(self, widget):
        lines = [f'line {i}' for i in range(10000)]
        widget.set_content(lines)
        start, end = widget.get_visible_range()
        assert start >= 0
        assert end <= 10000
        assert end - start <= widget._visible_lines_count


class TestScrollToLine:
    """Test scroll_to_line."""

    def test_scroll_to_beginning(self, widget):
        lines = [f'line {i}' for i in range(10000)]
        widget.set_content(lines)
        widget.scroll_to_line(0)
        start, end = widget.get_visible_range()
        assert start == 0

    def test_scroll_to_middle(self, widget):
        lines = [f'line {i}' for i in range(10000)]
        widget.set_content(lines)
        widget.scroll_to_line(5000)
        start, end = widget.get_visible_range()
        assert start == 5000

    def test_scroll_clamps_to_max(self, widget):
        lines = [f'line {i}' for i in range(10000)]
        widget.set_content(lines)
        widget.scroll_to_line(99999)
        start, end = widget.get_visible_range()
        assert end <= 10000


class TestInsert:
    """Test insert (Tkinter Text compatible interface)."""

    def test_insert_at_beginning(self, widget):
        widget.set_content(['hello'])
        widget.insert("1.0", "world ")
        assert widget.get_content() == 'world hello'

    def test_insert_at_end(self, widget):
        widget.set_content(['hello'])
        widget.insert("1.5", " world")
        assert widget.get_content() == 'hello world'

    def test_insert_newline(self, widget):
        widget.set_content(['hello world'])
        widget.insert("1.5", "\n")
        content = widget.get_content()
        assert content == 'hello\n world'

    def test_insert_multiline(self, widget):
        widget.set_content(['ab'])
        widget.insert("1.1", "x\ny\nz")
        content = widget.get_content()
        assert content == 'ax\ny\nzb'


class TestDelete:
    """Test delete (Tkinter Text compatible interface)."""

    def test_delete_single_char(self, widget):
        widget.set_content(['hello'])
        widget.delete("1.0", "1.1")
        assert widget.get_content() == 'ello'

    def test_delete_range_same_line(self, widget):
        widget.set_content(['hello world'])
        widget.delete("1.0", "1.6")
        assert widget.get_content() == 'world'

    def test_delete_across_lines(self, widget):
        widget.set_content(['hello', 'world'])
        widget.delete("1.3", "2.2")
        assert widget.get_content() == 'helrld'


class TestGet:
    """Test get (Tkinter Text compatible interface)."""

    def test_get_single_char(self, widget):
        widget.set_content(['hello'])
        assert widget.get("1.0", "1.1") == 'h'

    def test_get_range_same_line(self, widget):
        widget.set_content(['hello world'])
        assert widget.get("1.0", "1.5") == 'hello'

    def test_get_multiline(self, widget):
        widget.set_content(['hello', 'world'])
        result = widget.get("1.0", "2.5")
        assert result == 'hello\nworld'


class TestCursorPosition:
    """Test cursor position tracking."""

    def test_set_and_get_cursor(self, widget):
        widget.set_content(['hello', 'world', 'test'])
        widget.set_cursor_position(1, 3)
        line, col = widget.get_cursor_position()
        assert line == 1
        assert col == 3

    def test_cursor_clamped_to_bounds(self, widget):
        widget.set_content(['hi'])
        widget.set_cursor_position(100, 100)
        line, col = widget.get_cursor_position()
        # Should be clamped to last line
        assert line == 0
        assert col <= 2


class TestLargeContent:
    """Test performance with large content (10000+ lines)."""

    def test_set_10000_lines(self, widget):
        lines = [f'line {i}: some content here' for i in range(10000)]
        widget.set_content(lines)
        assert widget.total_lines == 10000
        assert widget.is_virtual_mode is True

    def test_get_content_large(self, widget):
        lines = [f'line {i}' for i in range(10000)]
        widget.set_content(lines)
        content = widget.get_content()
        result_lines = content.split('\n')
        assert len(result_lines) == 10000
        assert result_lines[0] == 'line 0'
        assert result_lines[9999] == 'line 9999'

    def test_visible_range_large(self, widget):
        lines = [f'line {i}' for i in range(10000)]
        widget.set_content(lines)
        start, end = widget.get_visible_range()
        # Should only show a window, not all 10000 lines
        assert end - start <= widget._visible_lines_count

    def test_scroll_large_content(self, widget):
        lines = [f'line {i}' for i in range(10000)]
        widget.set_content(lines)
        widget.scroll_to_line(5000)
        start, end = widget.get_visible_range()
        assert start == 5000

    def test_insert_in_virtual_mode(self, widget):
        lines = [f'line {i}' for i in range(1000)]
        widget.set_content(lines)
        widget.insert("500.0", "inserted: ")
        # Verify the line was modified
        content = widget.get_content()
        assert 'inserted: line 499' in content

    def test_get_in_virtual_mode(self, widget):
        lines = [f'line {i}' for i in range(1000)]
        widget.set_content(lines)
        result = widget.get("500.0", "500.8")
        assert result == 'line 499'
