"""
虚拟化文本渲染组件 - VirtualTextWidget

仅渲染可视区域内容，支持超过 10000 行文本而不产生明显性能下降。
提供与标准 Tkinter Text 组件兼容的接口。
"""

import tkinter as tk
import customtkinter as ctk


class VirtualTextWidget(ctk.CTkFrame):
    """虚拟化渲染的文本组件，仅渲染可视区域内容。

    核心优化策略：
    - 在内存中维护完整的行列表（self._lines）
    - 内部 Text 组件仅加载可视窗口 + 缓冲区的行
    - 滚动时动态更新 Text 组件内容
    - 对外提供与 tk.Text 兼容的 insert/delete/get 接口

    适用于输出显示（只读模式）和大文件编辑场景。
    小文件（< VIRTUAL_THRESHOLD 行）直接使用标准模式。
    """

    # 超过此行数时启用虚拟化模式
    VIRTUAL_THRESHOLD = 500
    # 可视区域上下各额外渲染的缓冲行数
    BUFFER_LINES = 20
    # 默认可视行数估算
    DEFAULT_VISIBLE_LINES = 50

    def __init__(self, parent, **kwargs):
        """初始化虚拟文本组件。

        Args:
            parent: 父组件
            **kwargs: 支持的关键字参数：
                - font: 字体设置
                - wrap: 换行模式 (tk.WORD, tk.CHAR, tk.NONE)
                - state: 状态 (tk.NORMAL, tk.DISABLED)
                - relief: 边框样式
                - padx, pady: 内边距
                - bd: 边框宽度
                - highlightthickness: 高亮边框厚度
                - undo: 是否启用撤销
        """
        # Extract text widget kwargs
        text_kwargs = {}
        text_keys = ['font', 'wrap', 'state', 'relief', 'padx', 'pady',
                     'bd', 'highlightthickness', 'undo']
        for key in text_keys:
            if key in kwargs:
                text_kwargs[key] = kwargs.pop(key)

        # Initialize CTkFrame
        super().__init__(parent, **kwargs)

        # Internal state
        self._lines: list[str] = ['']  # All content lines (always at least one empty line)
        self._virtual_mode = False  # Whether virtualization is active
        self._scroll_offset = 0  # First visible line index (0-based)
        self._visible_lines_count = self.DEFAULT_VISIBLE_LINES
        self._cursor_line = 0  # Virtual cursor line (0-based)
        self._cursor_col = 0  # Virtual cursor column (0-based)
        self._font = text_kwargs.get('font', ('Consolas', 12))
        self._state = text_kwargs.get('state', tk.NORMAL)

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Internal Text widget - renders only visible portion in virtual mode
        self._text = tk.Text(self, **text_kwargs)
        self._text.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        self._scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self._scrollbar.grid(row=0, column=1, sticky="ns")

        # Connect scrollbar
        self._scrollbar.configure(command=self._on_scrollbar)
        self._text.configure(yscrollcommand=self._on_text_scroll)

        # Bind mouse wheel for scrolling
        self._text.bind('<MouseWheel>', self._on_mousewheel)
        self._text.bind('<Button-4>', self._on_mousewheel_linux)
        self._text.bind('<Button-5>', self._on_mousewheel_linux)

        # Bind resize to recalculate visible lines
        self._text.bind('<Configure>', self._on_configure)

        # Track if we need to update visible area
        self._render_scheduled = False

    # ========== Public API: Content Management ==========

    def set_content(self, lines: list[str]) -> None:
        """设置全部内容（不立即全量渲染，仅在虚拟模式下渲染可视区域）。

        Args:
            lines: 文本行列表，每行不含换行符
        """
        if not lines:
            lines = ['']
        self._lines = list(lines)

        # Decide whether to use virtual mode
        self._virtual_mode = len(self._lines) > self.VIRTUAL_THRESHOLD

        # Reset scroll position
        self._scroll_offset = 0
        self._cursor_line = 0
        self._cursor_col = 0

        # Render
        self.render_visible()

    def get_content(self) -> str:
        """获取全部文本内容。

        Returns:
            完整文本内容，行之间以换行符连接
        """
        if not self._virtual_mode:
            # In standard mode, read directly from text widget
            return self._text.get("1.0", "end-1c")
        return '\n'.join(self._lines)

    def get_visible_range(self) -> tuple[int, int]:
        """获取当前可视行范围。

        Returns:
            (start_line, end_line) 元组，start_line 为 0-indexed，
            end_line 为不包含的上界（即可视范围为 [start, end)）
        """
        if not self._virtual_mode:
            # In standard mode, query the text widget directly
            try:
                top = self._text.index("@0,0")
                top_line = int(top.split('.')[0]) - 1  # Convert to 0-based
                # Estimate bottom based on widget height
                bottom = self._text.index(f"@0,{self._text.winfo_height()}")
                bottom_line = int(bottom.split('.')[0])  # Already exclusive
                return (max(0, top_line), min(bottom_line, len(self._lines)))
            except (tk.TclError, ValueError):
                return (0, min(self._visible_lines_count, len(self._lines)))

        start = self._scroll_offset
        end = min(start + self._visible_lines_count, len(self._lines))
        return (start, end)

    def scroll_to_line(self, line_index: int) -> None:
        """滚动到指定行。

        Args:
            line_index: 目标行号（0-based）
        """
        if not self._virtual_mode:
            # Standard mode: use text widget's built-in scrolling
            tk_line = line_index + 1  # Convert to 1-based
            self._text.see(f"{tk_line}.0")
            return

        # Clamp to valid range
        max_offset = max(0, len(self._lines) - self._visible_lines_count)
        self._scroll_offset = max(0, min(line_index, max_offset))
        self.render_visible()

    def render_visible(self) -> None:
        """渲染可视区域内容。

        在虚拟模式下，仅将可视窗口 + 缓冲区的行加载到 Text 组件中。
        在标准模式下，加载全部内容。
        """
        # Save current state and temporarily enable editing
        was_disabled = self._state == tk.DISABLED
        if was_disabled:
            self._text.configure(state=tk.NORMAL)

        self._text.delete("1.0", tk.END)

        if not self._virtual_mode:
            # Standard mode: load all content
            content = '\n'.join(self._lines)
            if content:
                self._text.insert("1.0", content)
        else:
            # Virtual mode: load only visible + buffer
            start = max(0, self._scroll_offset - self.BUFFER_LINES)
            end = min(len(self._lines),
                      self._scroll_offset + self._visible_lines_count + self.BUFFER_LINES)

            visible_content = '\n'.join(self._lines[start:end])
            if visible_content:
                self._text.insert("1.0", visible_content)

            # Scroll internal text to show the correct portion
            if self._scroll_offset > start:
                offset_in_widget = self._scroll_offset - start
                self._text.yview_moveto(0)
                self._text.see(f"{offset_in_widget + 1}.0")

            # Update scrollbar position
            self._update_scrollbar()

        if was_disabled:
            self._text.configure(state=tk.DISABLED)

    # ========== Public API: Tkinter Text Compatible Interface ==========

    def insert(self, index: str, text: str) -> None:
        """兼容 Tkinter Text 的插入接口。

        Args:
            index: Tkinter Text 索引格式 (如 "1.0", "end", "insert")
            text: 要插入的文本
        """
        if not self._virtual_mode:
            # Standard mode: delegate directly
            was_disabled = self._state == tk.DISABLED
            if was_disabled:
                self._text.configure(state=tk.NORMAL)
            self._text.insert(index, text)
            if was_disabled:
                self._text.configure(state=tk.DISABLED)
            # Sync internal lines from widget
            self._sync_lines_from_widget()
            return

        # Virtual mode: update internal buffer
        line_idx, col_idx = self._parse_index(index)

        # Split the text to insert into lines
        new_lines = text.split('\n')

        if len(new_lines) == 1:
            # Single line insert
            if line_idx < len(self._lines):
                line = self._lines[line_idx]
                self._lines[line_idx] = line[:col_idx] + new_lines[0] + line[col_idx:]
            else:
                self._lines.append(new_lines[0])
        else:
            # Multi-line insert
            if line_idx < len(self._lines):
                current_line = self._lines[line_idx]
                before = current_line[:col_idx]
                after = current_line[col_idx:]

                # First fragment
                first_line = before + new_lines[0]
                # Last fragment
                last_line = new_lines[-1] + after
                # Middle lines
                middle_lines = new_lines[1:-1]

                # Replace current line with split result
                self._lines[line_idx:line_idx + 1] = [first_line] + middle_lines + [last_line]
            else:
                self._lines.extend(new_lines)

        # Check if we should switch to virtual mode
        if len(self._lines) > self.VIRTUAL_THRESHOLD and not self._virtual_mode:
            self._virtual_mode = True

        self.render_visible()

    def delete(self, start: str, end: str = None) -> None:
        """兼容 Tkinter Text 的删除接口。

        Args:
            start: 起始索引
            end: 结束索引（如果为 None，删除单个字符）
        """
        if not self._virtual_mode:
            # Standard mode: delegate directly
            was_disabled = self._state == tk.DISABLED
            if was_disabled:
                self._text.configure(state=tk.NORMAL)
            if end is None:
                self._text.delete(start)
            else:
                self._text.delete(start, end)
            if was_disabled:
                self._text.configure(state=tk.DISABLED)
            self._sync_lines_from_widget()
            return

        # Virtual mode: update internal buffer
        start_line, start_col = self._parse_index(start)

        if end is None:
            # Delete single character
            if start_line < len(self._lines):
                line = self._lines[start_line]
                if start_col < len(line):
                    self._lines[start_line] = line[:start_col] + line[start_col + 1:]
                elif start_line + 1 < len(self._lines):
                    # Join with next line
                    self._lines[start_line] = line + self._lines[start_line + 1]
                    del self._lines[start_line + 1]
        else:
            end_line, end_col = self._parse_index(end)

            if start_line == end_line:
                # Same line deletion
                if start_line < len(self._lines):
                    line = self._lines[start_line]
                    self._lines[start_line] = line[:start_col] + line[end_col:]
            else:
                # Multi-line deletion
                if start_line < len(self._lines):
                    before = self._lines[start_line][:start_col]
                    after = ''
                    if end_line < len(self._lines):
                        after = self._lines[end_line][end_col:]

                    self._lines[start_line:end_line + 1] = [before + after]

        # Ensure at least one line
        if not self._lines:
            self._lines = ['']

        # Check if we can switch back to standard mode
        if len(self._lines) <= self.VIRTUAL_THRESHOLD and self._virtual_mode:
            self._virtual_mode = False

        self.render_visible()

    def get(self, start: str, end: str = None) -> str:
        """兼容 Tkinter Text 的获取接口。

        Args:
            start: 起始索引
            end: 结束索引

        Returns:
            指定范围内的文本
        """
        if not self._virtual_mode:
            # Standard mode: delegate directly
            if end is None:
                return self._text.get(start)
            return self._text.get(start, end)

        # Virtual mode: read from internal buffer
        start_line, start_col = self._parse_index(start)

        if end is None:
            # Get single character
            if start_line < len(self._lines):
                line = self._lines[start_line]
                if start_col < len(line):
                    return line[start_col]
                elif start_line + 1 < len(self._lines):
                    return '\n'
            return ''

        end_line, end_col = self._parse_index(end)

        if start_line == end_line:
            # Same line
            if start_line < len(self._lines):
                return self._lines[start_line][start_col:end_col]
            return ''

        # Multi-line
        result_parts = []
        for i in range(start_line, min(end_line + 1, len(self._lines))):
            if i == start_line:
                result_parts.append(self._lines[i][start_col:])
            elif i == end_line:
                result_parts.append(self._lines[i][:end_col])
            else:
                result_parts.append(self._lines[i])

        return '\n'.join(result_parts)

    # ========== Public API: Cursor and Selection ==========

    def get_cursor_position(self) -> tuple[int, int]:
        """获取虚拟光标位置。

        Returns:
            (line, col) 元组，均为 0-based
        """
        if not self._virtual_mode:
            try:
                pos = self._text.index(tk.INSERT)
                parts = pos.split('.')
                return (int(parts[0]) - 1, int(parts[1]))
            except tk.TclError:
                return (self._cursor_line, self._cursor_col)
        return (self._cursor_line, self._cursor_col)

    def set_cursor_position(self, line: int, col: int) -> None:
        """设置虚拟光标位置。

        Args:
            line: 行号（0-based）
            col: 列号（0-based）
        """
        # Clamp values
        line = max(0, min(line, len(self._lines) - 1))
        col = max(0, min(col, len(self._lines[line]) if line < len(self._lines) else 0))

        self._cursor_line = line
        self._cursor_col = col

        if not self._virtual_mode:
            try:
                tk_line = line + 1
                self._text.mark_set(tk.INSERT, f"{tk_line}.{col}")
            except tk.TclError:
                pass
        else:
            # Ensure cursor is visible
            start, end = self.get_visible_range()
            if line < start or line >= end:
                self.scroll_to_line(max(0, line - self._visible_lines_count // 2))

    # ========== Public API: Configuration ==========

    def configure(self, **kwargs) -> None:
        """配置组件属性，支持字体变更等。

        Args:
            **kwargs: 配置参数，支持 font, state, wrap 等
        """
        text_keys = ['font', 'wrap', 'state', 'relief', 'padx', 'pady',
                     'bd', 'highlightthickness']

        text_kwargs = {}
        frame_kwargs = {}

        for key, value in kwargs.items():
            if key in text_keys:
                text_kwargs[key] = value
            else:
                frame_kwargs[key] = value

        if 'font' in text_kwargs:
            self._font = text_kwargs['font']
            # Recalculate visible lines after font change
            self._recalculate_visible_lines()

        if 'state' in text_kwargs:
            self._state = text_kwargs['state']

        if text_kwargs:
            self._text.configure(**text_kwargs)

        if frame_kwargs:
            super().configure(**frame_kwargs)

    def cget(self, key: str):
        """获取配置值。"""
        if key == 'font':
            return self._font
        if key == 'state':
            return self._state
        try:
            return self._text.cget(key)
        except tk.TclError:
            return super().cget(key)

    # ========== Public API: Additional Text Widget Compatibility ==========

    def index(self, index: str) -> str:
        """将索引转换为规范化的 'line.col' 格式。"""
        if not self._virtual_mode:
            return self._text.index(index)

        line, col = self._parse_index(index)
        return f"{line + 1}.{col}"

    def see(self, index: str) -> None:
        """确保指定索引可见。"""
        line, _ = self._parse_index(index)
        start, end = self.get_visible_range()
        if line < start or line >= end:
            self.scroll_to_line(max(0, line - self._visible_lines_count // 2))

    def mark_set(self, mark_name: str, index: str) -> None:
        """设置标记位置。"""
        if mark_name == tk.INSERT:
            line, col = self._parse_index(index)
            self.set_cursor_position(line, col)
        elif not self._virtual_mode:
            self._text.mark_set(mark_name, index)

    def tag_add(self, tag_name: str, start: str, end: str = None) -> None:
        """添加标签（用于语法高亮等）。"""
        if not self._virtual_mode:
            if end is None:
                self._text.tag_add(tag_name, start)
            else:
                self._text.tag_add(tag_name, start, end)

    def tag_remove(self, tag_name: str, start: str, end: str = None) -> None:
        """移除标签。"""
        if not self._virtual_mode:
            if end is None:
                self._text.tag_remove(tag_name, start)
            else:
                self._text.tag_remove(tag_name, start, end)

    def tag_configure(self, tag_name: str, **kwargs) -> None:
        """配置标签样式。"""
        self._text.tag_configure(tag_name, **kwargs)

    def yview(self, *args) -> None:
        """Y 轴视图控制。"""
        if not self._virtual_mode:
            self._text.yview(*args)
        else:
            if args:
                if args[0] == 'moveto':
                    fraction = float(args[1])
                    total = len(self._lines)
                    self._scroll_offset = int(fraction * total)
                    self._scroll_offset = max(0, min(self._scroll_offset,
                                                     total - self._visible_lines_count))
                    self.render_visible()
                elif args[0] == 'scroll':
                    amount = int(args[1])
                    unit = args[2] if len(args) > 2 else 'units'
                    if unit == 'pages':
                        amount *= self._visible_lines_count
                    self._scroll_offset += amount
                    self._scroll_offset = max(0, min(self._scroll_offset,
                                                     len(self._lines) - self._visible_lines_count))
                    self.render_visible()

    def xview(self, *args) -> None:
        """X 轴视图控制（委托给内部 Text）。"""
        self._text.xview(*args)

    @property
    def text_widget(self) -> tk.Text:
        """获取内部 Text 组件的引用（用于直接操作，如绑定事件）。"""
        return self._text

    def bind(self, sequence: str, func=None, add: str = None):
        """绑定事件到内部 Text 组件。"""
        return self._text.bind(sequence, func, add)

    def unbind(self, sequence: str, funcid=None):
        """解绑事件。"""
        return self._text.unbind(sequence, funcid)

    def focus_set(self):
        """设置焦点到内部 Text 组件。"""
        self._text.focus_set()

    def focus_get(self):
        """获取当前焦点组件。"""
        return self._text.focus_get()

    # ========== Internal Methods ==========

    def _parse_index(self, index: str) -> tuple[int, int]:
        """解析 Tkinter Text 索引为 (line, col) 元组（0-based）。

        支持的格式：
        - "line.col" (如 "1.0")
        - "end" / "end-1c"
        - "insert"
        - "line.end"

        Args:
            index: Tkinter Text 索引字符串

        Returns:
            (line, col) 元组，均为 0-based
        """
        if index == "end" or index == tk.END:
            return (len(self._lines) - 1, len(self._lines[-1]) if self._lines else 0)

        if index == "end-1c":
            if self._lines:
                last_line = len(self._lines) - 1
                last_col = len(self._lines[last_line])
                if last_col > 0:
                    return (last_line, last_col - 1)
                elif last_line > 0:
                    return (last_line - 1, len(self._lines[last_line - 1]))
            return (0, 0)

        if index == "insert" or index == tk.INSERT:
            return (self._cursor_line, self._cursor_col)

        # Handle "line.col" format
        if '.' in index:
            parts = index.split('.')
            try:
                line = int(parts[0]) - 1  # Convert from 1-based to 0-based
                line = max(0, min(line, len(self._lines) - 1))

                col_str = parts[1]
                if col_str == "end":
                    col = len(self._lines[line]) if line < len(self._lines) else 0
                else:
                    col = int(col_str)
                    if line < len(self._lines):
                        col = max(0, min(col, len(self._lines[line])))
                    else:
                        col = 0

                return (line, col)
            except (ValueError, IndexError):
                return (0, 0)

        return (0, 0)

    def _sync_lines_from_widget(self) -> None:
        """从内部 Text 组件同步内容到 _lines 缓冲区（标准模式使用）。"""
        content = self._text.get("1.0", "end-1c")
        self._lines = content.split('\n') if content else ['']

    def _on_scrollbar(self, *args) -> None:
        """处理滚动条事件。"""
        if not self._virtual_mode:
            self._text.yview(*args)
        else:
            self.yview(*args)

    def _on_text_scroll(self, first, last) -> None:
        """处理 Text 组件滚动事件（更新滚动条位置）。"""
        if not self._virtual_mode:
            self._scrollbar.set(first, last)
        else:
            # In virtual mode, calculate scrollbar position from offset
            self._update_scrollbar()

    def _update_scrollbar(self) -> None:
        """更新滚动条位置以反映虚拟滚动状态。"""
        if not self._lines:
            self._scrollbar.set(0, 1)
            return

        total = len(self._lines)
        if total <= self._visible_lines_count:
            self._scrollbar.set(0, 1)
        else:
            first = self._scroll_offset / total
            last = min(1.0, (self._scroll_offset + self._visible_lines_count) / total)
            self._scrollbar.set(first, last)

    def _on_mousewheel(self, event) -> None:
        """处理鼠标滚轮事件（Windows/macOS）。"""
        if not self._virtual_mode:
            # Let the text widget handle it normally
            return

        # Windows: event.delta is typically ±120
        delta = -1 * (event.delta // 120)
        scroll_amount = delta * 3  # Scroll 3 lines per wheel notch

        self._scroll_offset += scroll_amount
        self._scroll_offset = max(0, min(self._scroll_offset,
                                         max(0, len(self._lines) - self._visible_lines_count)))
        self.render_visible()
        return "break"

    def _on_mousewheel_linux(self, event) -> None:
        """处理鼠标滚轮事件（Linux）。"""
        if not self._virtual_mode:
            return

        if event.num == 4:
            delta = -3
        else:
            delta = 3

        self._scroll_offset += delta
        self._scroll_offset = max(0, min(self._scroll_offset,
                                         max(0, len(self._lines) - self._visible_lines_count)))
        self.render_visible()
        return "break"

    def _on_configure(self, event) -> None:
        """处理组件大小变化事件。"""
        self._recalculate_visible_lines()

    def _recalculate_visible_lines(self) -> None:
        """根据组件高度和字体大小重新计算可视行数。"""
        try:
            widget_height = self._text.winfo_height()
            if widget_height <= 1:
                return

            # Estimate line height from font
            font = self._font
            if isinstance(font, tuple):
                font_size = font[1] if len(font) > 1 else 12
            elif isinstance(font, str):
                font_size = 12
            else:
                font_size = 12

            # Approximate line height (font size + padding)
            line_height = int(font_size * 1.5) + 2
            if line_height <= 0:
                line_height = 20

            self._visible_lines_count = max(10, widget_height // line_height)
        except (tk.TclError, ValueError):
            self._visible_lines_count = self.DEFAULT_VISIBLE_LINES

    @property
    def total_lines(self) -> int:
        """获取总行数。"""
        return len(self._lines)

    @property
    def is_virtual_mode(self) -> bool:
        """是否处于虚拟化模式。"""
        return self._virtual_mode
