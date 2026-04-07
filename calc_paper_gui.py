#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算稿纸 - 高级版GUI
支持16进制、2进制、位运算和字节序显示

Copyright (C) 2026 matthewzu <xiaofeng_zu@163.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, simpledialog
import json
import os
import sys
import re
from calc_paper import CalculatorPaperAdvanced

VERSION = "1.4"

# 配置文件路径
# 默认为可执行文件所在目录；PyInstaller 打包后为 exe 所在目录
def _get_exe_dir():
    """获取可执行文件所在目录"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

DEFAULT_DATA_DIR = _get_exe_dir()
BOOTSTRAP_CONFIG = os.path.join(DEFAULT_DATA_DIR, 'calcpaper_config.json')

# 获取资源文件路径（兼容 PyInstaller 打包）
def _resource_path(filename):
    """获取资源文件的绝对路径，兼容 PyInstaller 打包"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

# 默认快捷键配置
DEFAULT_SHORTCUTS = {
    'calculate': '<F5>',
    'calculate_alt': '<Control-Return>',
    'clear': '<Control-d>',
    'undo': '<Control-z>',
    'redo': '<Control-y>',
    'load_example': '<Control-l>',
    'open_file': '<Control-o>',
    'save_file': '<Control-s>',
    'font_increase': '<Control-equal>',
    'font_decrease': '<Control-minus>',
}

# 快捷键显示名称
SHORTCUT_NAMES_EN = {
    'calculate': 'Calculate',
    'calculate_alt': 'Calculate (Alt)',
    'clear': 'Clear',
    'undo': 'Undo',
    'redo': 'Redo',
    'load_example': 'Load Example',
    'open_file': 'Open File',
    'save_file': 'Save Result',
    'font_increase': 'Font Increase',
    'font_decrease': 'Font Decrease',
}

SHORTCUT_NAMES_ZH = {
    'calculate': '计算',
    'calculate_alt': '计算 (备选)',
    'clear': '清空',
    'undo': '撤销',
    'redo': '恢复',
    'load_example': '加载示例',
    'open_file': '打开文件',
    'save_file': '保存结果',
    'font_increase': '放大字体',
    'font_decrease': '缩小字体',
}


def shortcut_display(key_str):
    """将 tkinter 快捷键字符串转为可读格式，如 <Control-s> -> Ctrl+S"""
    s = key_str.strip('<>').replace('Control', 'Ctrl').replace('Return', 'Enter')
    parts = s.split('-')
    return '+'.join(p.upper() if len(p) == 1 else p for p in parts)


class CalculatorGUIAdvanced:
    def __init__(self, root):
        self.root = root
        self.min_font_size = 8
        self.max_font_size = 32

        # 设置窗口图标
        self._set_icon()

        # 加载配置（语言、字体、窗口大小、快捷键）
        self.load_config()

        self.update_title()

        # 创建计算器实例
        self.calculator = CalculatorPaperAdvanced(language=self.language)

        # GUI专用的历史记录（保存输入和输出文本）
        self.gui_history = []
        self.gui_history_index = -1
        self.last_saved_input = ""

        # 创建界面
        self.create_widgets()

        # 绑定快捷键
        self.bind_shortcuts()

        # 绑定窗口大小变化事件
        self.root.bind('<Configure>', self.on_window_configure)

        # 恢复上次会话
        self.root.after(100, self._restore_session_and_init)

        # 恢复窗口位置（需要在窗口显示后）
        self.root.after(150, self._apply_saved_position)

        # 绑定输入框的修改事件
        self.input_text.bind('<<Modified>>', self.on_input_modified)

        # 窗口关闭时保存
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ==================== 配置持久化 ====================

    def _set_icon(self):
        """设置窗口图标"""
        try:
            icon_path = _resource_path('calcpaper.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

    def load_config(self):
        """加载配置文件
        
        先从默认位置（exe目录）读取配置，其中可能包含用户自定义的 data_dir。
        然后用 data_dir 确定 config 和 session 文件的实际路径。
        """
        defaults = {
            'language': 'en',
            'font_size': 10,
            'window_geometry': '1200x800',
            'window_position': None,
            'data_dir': DEFAULT_DATA_DIR,
            'shortcuts': DEFAULT_SHORTCUTS.copy(),
        }

        # 第一步：从引导配置读取 data_dir
        config = defaults.copy()
        try:
            if os.path.exists(BOOTSTRAP_CONFIG):
                with open(BOOTSTRAP_CONFIG, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                config.update({k: saved[k] for k in saved if k in defaults})
                merged_shortcuts = DEFAULT_SHORTCUTS.copy()
                merged_shortcuts.update(saved.get('shortcuts', {}))
                config['shortcuts'] = merged_shortcuts
        except Exception:
            pass

        # 确定数据目录
        self.data_dir = config.get('data_dir', DEFAULT_DATA_DIR)
        os.makedirs(self.data_dir, exist_ok=True)
        self.config_file = os.path.join(self.data_dir, 'calcpaper_config.json')
        self.session_file = os.path.join(self.data_dir, 'calcpaper_session.json')

        # 第二步：如果 data_dir 不是默认目录，从实际 data_dir 重新读取完整配置
        if self.config_file != BOOTSTRAP_CONFIG:
            try:
                if os.path.exists(self.config_file):
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        saved = json.load(f)
                    config.update({k: saved[k] for k in saved if k in defaults})
                    merged_shortcuts = DEFAULT_SHORTCUTS.copy()
                    merged_shortcuts.update(saved.get('shortcuts', {}))
                    config['shortcuts'] = merged_shortcuts
            except Exception:
                pass

        self.language = config['language']
        self.font_size = config['font_size']
        self._saved_geometry = config['window_geometry']
        self._saved_position = config.get('window_position')
        self.shortcuts = config['shortcuts']

        # 先设置窗口大小
        self.root.geometry(self._saved_geometry)

    def _apply_saved_position(self):
        """在窗口显示后应用保存的位置"""
        if self._saved_position:
            try:
                x, y = self._saved_position.split(',')
                x, y = int(x), int(y)
                # 确保窗口不会出现在屏幕外
                screen_w = self.root.winfo_screenwidth()
                screen_h = self.root.winfo_screenheight()
                x = max(0, min(x, screen_w - 100))
                y = max(0, min(y, screen_h - 100))
                self.root.geometry(f"+{x}+{y}")
            except Exception:
                pass

    def save_config(self):
        """保存配置文件"""
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        geo = f"{w}x{h}"
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        pos = f"{x},{y}"
        config = {
            'language': self.language,
            'font_size': self.font_size,
            'window_geometry': geo,
            'window_position': pos,
            'data_dir': self.data_dir,
            'shortcuts': self.shortcuts,
        }
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            # 如果 data_dir 不是默认目录，在默认目录也保存一份引导配置（只含 data_dir）
            if self.config_file != BOOTSTRAP_CONFIG:
                with open(BOOTSTRAP_CONFIG, 'w', encoding='utf-8') as f:
                    json.dump({'data_dir': self.data_dir}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ==================== 会话持久化 ====================

    def save_session(self):
        """保存当前会话（输入和输出内容）"""
        try:
            input_content = self.input_text.get("1.0", "end-1c")
            output_content = self.output_text.get("1.0", "end-1c")
            session = {
                'input': input_content,
                'output': output_content,
            }
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def load_session(self):
        """加载上次会话"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def _restore_session_and_init(self):
        """恢复会话并初始化状态"""
        session = self.load_session()
        if session:
            input_content = session.get('input', '')
            output_content = session.get('output', '')
            if input_content:
                self.input_text.unbind('<<Modified>>')
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", input_content)
                self.input_text.bind('<<Modified>>', self.on_input_modified)
            if output_content:
                self.output_text.config(state=tk.NORMAL)
                self.output_text.delete("1.0", tk.END)
                self.output_text.insert("1.0", output_content)
                self.apply_syntax_highlighting()
                self.output_text.config(state=tk.DISABLED)
            self.last_saved_input = input_content

        # 保存初始状态
        input_c = self.input_text.get("1.0", "end-1c")
        output_c = self.output_text.get("1.0", "end-1c")
        self.save_gui_state(input_c, output_c)

    def on_close(self):
        """窗口关闭时保存配置和会话"""
        self.save_config()
        self.save_session()
        self.root.destroy()

    # ==================== 窗口和标题 ====================

    def on_window_configure(self, event):
        if event.widget == self.root:
            self.root.after_idle(self.check_button_scroll_needed)

    def update_title(self):
        if self.language == 'en':
            self.root.title(f"CalcPaper - Advanced v{VERSION}")
        else:
            self.root.title(f"计算稿纸 - 高级版 v{VERSION}")

    # ==================== 语言切换 ====================

    def toggle_language(self):
        self.language = 'zh' if self.language == 'en' else 'en'
        self.calculator.set_language(self.language)
        self.update_title()
        self.update_button_texts()

    def update_button_texts(self):
        """更新按钮文本（含快捷键显示）"""
        sc = self.shortcuts

        def _btn(en, zh, key):
            disp = shortcut_display(sc.get(key, ''))
            label = en if self.language == 'en' else zh
            return f"{label} ({disp})" if disp else label

        if hasattr(self, 'calc_button'):
            self.calc_button.config(text=_btn("Calculate", "计算", "calculate"))
        if hasattr(self, 'clear_button'):
            self.clear_button.config(text=_btn("Clear", "清空", "clear"))
        if hasattr(self, 'undo_button'):
            self.undo_button.config(text=_btn("Undo", "撤销", "undo"))
        if hasattr(self, 'redo_button'):
            self.redo_button.config(text=_btn("Redo", "恢复", "redo"))
        if hasattr(self, 'example_button'):
            self.example_button.config(text=_btn("Load Example", "加载示例", "load_example"))
        if hasattr(self, 'open_button'):
            self.open_button.config(text=_btn("Open File", "打开文件", "open_file"))
        if hasattr(self, 'save_button'):
            self.save_button.config(text=_btn("Save Result", "保存结果", "save_file"))
        if hasattr(self, 'lang_button'):
            self.lang_button.config(text="中文" if self.language == 'en' else "EN")

        self.update_initial_font_display()
        self.update_undo_redo_buttons()

    # ==================== 字体 ====================

    def increase_font(self):
        if self.font_size < self.max_font_size:
            self.font_size = min(self.font_size + 2, self.max_font_size)
            self.update_fonts()
            msg = f"Font: {self.font_size}" if self.language == 'en' else f"字体: {self.font_size}"
            self.status_bar.config(text=msg)
            self.root.after(3000, self.restore_normal_status)

    def decrease_font(self):
        if self.font_size > self.min_font_size:
            self.font_size = max(self.font_size - 2, self.min_font_size)
            self.update_fonts()
            msg = f"Font: {self.font_size}" if self.language == 'en' else f"字体: {self.font_size}"
            self.status_bar.config(text=msg)
            self.root.after(3000, self.restore_normal_status)

    def restore_normal_status(self):
        self.status_bar.config(text="Ready" if self.language == 'en' else "就绪")

    def update_initial_font_display(self):
        if hasattr(self, 'font_size_label'):
            self.font_size_label.config(text=f"{self.font_size}")
        self.status_bar.config(text="Ready" if self.language == 'en' else "就绪")

    def update_fonts(self):
        self.input_text.config(font=("Consolas", self.font_size))
        self.output_text.config(font=("Consolas", self.font_size))
        if hasattr(self, 'font_size_label'):
            self.font_size_label.config(text=f"{self.font_size}")

    # ==================== 界面创建 ====================

    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=0)
        main_frame.grid_rowconfigure(2, weight=0)
        main_frame.grid_columnconfigure(0, weight=1)

        # ========== 输入输出区域 ==========
        io_frame = tk.Frame(main_frame)
        io_frame.grid(row=0, column=0, sticky="nsew")
        io_frame.grid_columnconfigure(0, weight=1)
        io_frame.grid_columnconfigure(1, weight=1)
        io_frame.grid_rowconfigure(0, weight=0)
        io_frame.grid_rowconfigure(1, weight=1)

        input_lbl = "Input:" if self.language == 'en' else "输入区域："
        self.input_label = tk.Label(io_frame, text=input_lbl, font=("Arial", 10, "bold"))
        self.input_label.grid(row=0, column=0, sticky="w", padx=(0, 5))

        self.input_text = scrolledtext.ScrolledText(io_frame, wrap=tk.WORD, font=("Consolas", self.font_size))
        self.input_text.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        output_lbl = "Output:" if self.language == 'en' else "输出区域："
        self.output_label = tk.Label(io_frame, text=output_lbl, font=("Arial", 10, "bold"))
        self.output_label.grid(row=0, column=1, sticky="w", padx=(5, 0))

        self.output_text = scrolledtext.ScrolledText(io_frame, wrap=tk.WORD, font=("Consolas", self.font_size), state=tk.DISABLED)
        self.output_text.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

        # ========== 按钮栏 ==========
        button_frame = tk.Frame(main_frame, height=60)
        button_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        button_frame.grid_propagate(False)

        inner_frame = tk.Frame(button_frame)
        inner_frame.pack(fill=tk.BOTH, expand=True)

        self.button_canvas = tk.Canvas(inner_frame, height=50, highlightthickness=0)
        self.button_scrollbar = tk.Scrollbar(inner_frame, orient="horizontal", command=self.button_canvas.xview)
        self.scrollable_frame = tk.Frame(self.button_canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.button_canvas.configure(scrollregion=self.button_canvas.bbox("all")))
        self.button_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.button_canvas.configure(xscrollcommand=self.button_scrollbar.set)
        self.button_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        sc = self.shortcuts

        def _btn_text(en, zh, key):
            disp = shortcut_display(sc.get(key, ''))
            label = en if self.language == 'en' else zh
            return f"{label} ({disp})" if disp else label

        self.calc_button = tk.Button(self.scrollable_frame, text=_btn_text("Calculate", "计算", "calculate"),
                                     command=self.calculate, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=15, pady=3)
        self.calc_button.pack(side=tk.LEFT, padx=(0, 3))

        self.clear_button = tk.Button(self.scrollable_frame, text=_btn_text("Clear", "清空", "clear"),
                                      command=self.clear_all, bg="#f44336", fg="white", font=("Arial", 10), padx=15, pady=3)
        self.clear_button.pack(side=tk.LEFT, padx=3)

        self.undo_button = tk.Button(self.scrollable_frame, text=_btn_text("Undo", "撤销", "undo"),
                                     command=self.undo, bg="#FF9800", fg="white", font=("Arial", 10), padx=15, pady=3)
        self.undo_button.pack(side=tk.LEFT, padx=3)

        self.redo_button = tk.Button(self.scrollable_frame, text=_btn_text("Redo", "恢复", "redo"),
                                     command=self.redo, bg="#FF9800", fg="white", font=("Arial", 10), padx=15, pady=3)
        self.redo_button.pack(side=tk.LEFT, padx=3)

        self.example_button = tk.Button(self.scrollable_frame, text=_btn_text("Load Example", "加载示例", "load_example"),
                                        command=self.load_example, bg="#2196F3", fg="white", font=("Arial", 10), padx=15, pady=3)
        self.example_button.pack(side=tk.LEFT, padx=3)

        self.open_button = tk.Button(self.scrollable_frame, text=_btn_text("Open File", "打开文件", "open_file"),
                                     command=self.open_file, font=("Arial", 10), padx=15, pady=3)
        self.open_button.pack(side=tk.LEFT, padx=3)

        self.save_button = tk.Button(self.scrollable_frame, text=_btn_text("Save Result", "保存结果", "save_file"),
                                     command=self.save_file, font=("Arial", 10), padx=15, pady=3)
        self.save_button.pack(side=tk.LEFT, padx=3)

        self.lang_button = tk.Button(self.scrollable_frame, text="中文" if self.language == 'en' else "EN",
                                     command=self.toggle_language, font=("Arial", 10), padx=12, pady=3, bg="#9C27B0", fg="white")
        self.lang_button.pack(side=tk.LEFT, padx=3)

        # 快捷键配置按钮
        shortcut_text = "⌨" 
        self.shortcut_button = tk.Button(self.scrollable_frame, text=shortcut_text,
                                         command=self.open_shortcut_config, font=("Arial", 10), padx=8, pady=3, bg="#607D8B", fg="white")
        self.shortcut_button.pack(side=tk.LEFT, padx=3)

        self.font_plus_button = tk.Button(self.scrollable_frame, text="A+", command=self.increase_font,
                                          font=("Arial", 10, "bold"), padx=8, pady=3, bg="#4CAF50", fg="white")
        self.font_plus_button.pack(side=tk.LEFT, padx=3)

        self.font_minus_button = tk.Button(self.scrollable_frame, text="A-", command=self.decrease_font,
                                           font=("Arial", 10, "bold"), padx=8, pady=3, bg="#FF9800", fg="white")
        self.font_minus_button.pack(side=tk.LEFT, padx=3)

        self.font_size_label = tk.Label(self.scrollable_frame, text=f"{self.font_size}", font=("Arial", 9),
                                        padx=5, pady=3, relief=tk.SUNKEN, bd=1, bg="white")
        self.font_size_label.pack(side=tk.LEFT, padx=3)

        self.button_canvas.bind("<MouseWheel>", lambda e: self.button_canvas.xview_scroll(int(-1*(e.delta/120)), "units"))
        self.root.after(100, self.setup_button_scrolling)

        # ========== 状态栏 ==========
        status_frame = tk.Frame(main_frame, height=25)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        status_frame.grid_propagate(False)

        self.status_bar = tk.Label(status_frame, text="Ready" if self.language == 'en' else "就绪",
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 9))
        self.status_bar.pack(fill=tk.BOTH, expand=True)

        self.root.after(100, self.update_initial_font_display)

    # ==================== 按钮滚动 ====================

    def setup_button_scrolling(self):
        self.root.update_idletasks()
        self.check_button_scroll_needed()
        self.button_canvas.bind('<Configure>', lambda e: self.root.after_idle(self.check_button_scroll_needed))

    def check_button_scroll_needed(self):
        try:
            self.root.update_idletasks()
            if not hasattr(self, 'button_canvas') or not hasattr(self, 'scrollable_frame'):
                return
            canvas_width = self.button_canvas.winfo_width()
            frame_width = self.scrollable_frame.winfo_reqwidth()
            if canvas_width > 1:
                if frame_width > canvas_width:
                    if not self.button_scrollbar.winfo_viewable():
                        self.button_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
                        self.button_canvas.configure(height=40)
                else:
                    if self.button_scrollbar.winfo_viewable():
                        self.button_scrollbar.pack_forget()
                        self.button_canvas.configure(height=50)
        except (tk.TclError, AttributeError):
            pass

    # ==================== 快捷键 ====================

    def bind_shortcuts(self):
        """绑定快捷键（从配置读取）"""
        # 先解绑所有已知快捷键
        self._unbind_all_shortcuts()

        sc = self.shortcuts
        actions = {
            'calculate': lambda e: self.calculate(),
            'calculate_alt': lambda e: self.calculate(),
            'clear': lambda e: self.clear_all(),
            'undo': lambda e: self.undo(),
            'redo': lambda e: self.redo(),
            'load_example': lambda e: self.load_example(),
            'open_file': lambda e: self.open_file(),
            'save_file': lambda e: self.save_file(),
            'font_increase': lambda e: self.increase_font(),
            'font_decrease': lambda e: self.decrease_font(),
        }

        self._bound_keys = []
        for action_name, key_str in sc.items():
            if key_str and action_name in actions:
                try:
                    self.root.bind(key_str, actions[action_name])
                    self._bound_keys.append(key_str)
                    # 也绑定大写版本
                    if 'Control-' in key_str and len(key_str.split('-')[-1].rstrip('>')) == 1:
                        upper_key = key_str[:-2] + key_str[-2].upper() + key_str[-1]
                        if upper_key != key_str:
                            self.root.bind(upper_key, actions[action_name])
                            self._bound_keys.append(upper_key)
                except Exception:
                    pass

    def _unbind_all_shortcuts(self):
        """解绑所有已绑定的快捷键"""
        if hasattr(self, '_bound_keys'):
            for key in self._bound_keys:
                try:
                    self.root.unbind(key)
                except Exception:
                    pass
        self._bound_keys = []

    def open_shortcut_config(self):
        """打开设置对话框（快捷键 + 数据目录）"""
        dialog = tk.Toplevel(self.root)
        title = "Settings" if self.language == 'en' else "设置"
        dialog.title(title)
        dialog.geometry("550x480")
        dialog.transient(self.root)
        dialog.grab_set()

        names = SHORTCUT_NAMES_EN if self.language == 'en' else SHORTCUT_NAMES_ZH

        # ===== 数据目录 =====
        dir_frame = tk.LabelFrame(dialog,
                                   text="Data Directory" if self.language == 'en' else "数据目录",
                                   font=("Arial", 10, "bold"), padx=10, pady=5)
        dir_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        dir_hint = "Config and session files are stored here." if self.language == 'en' \
            else "配置文件和会话记录保存在此目录。"
        tk.Label(dir_frame, text=dir_hint, font=("Arial", 9), fg="gray").pack(anchor="w")

        dir_row = tk.Frame(dir_frame)
        dir_row.pack(fill=tk.X, pady=3)
        dir_entry = tk.Entry(dir_row, font=("Consolas", 10))
        dir_entry.insert(0, self.data_dir)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        def browse_dir():
            d = filedialog.askdirectory(initialdir=self.data_dir,
                                        title="Select Data Directory" if self.language == 'en' else "选择数据目录")
            if d:
                dir_entry.delete(0, tk.END)
                dir_entry.insert(0, d)

        tk.Button(dir_row, text="...", command=browse_dir, padx=8).pack(side=tk.LEFT)

        # ===== 快捷键 =====
        key_frame = tk.LabelFrame(dialog,
                                   text="Keyboard Shortcuts" if self.language == 'en' else "快捷键",
                                   font=("Arial", 10, "bold"), padx=10, pady=5)
        key_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        hint = "Click a field, then press the new key combination." if self.language == 'en' \
            else "点击输入框，然后按下新的快捷键组合。"
        tk.Label(key_frame, text=hint, font=("Arial", 9), fg="gray").pack(anchor="w")

        canvas = tk.Canvas(key_frame)
        scrollbar = tk.Scrollbar(key_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        entries = {}
        for action_name in DEFAULT_SHORTCUTS:
            row = tk.Frame(scroll_frame)
            row.pack(fill=tk.X, pady=2)

            display_name = names.get(action_name, action_name)
            tk.Label(row, text=display_name, width=20, anchor="w", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

            entry = tk.Entry(row, width=25, font=("Consolas", 10))
            entry.insert(0, self.shortcuts.get(action_name, ''))
            entry.pack(side=tk.LEFT, padx=5)
            entries[action_name] = entry

            def make_capture(e_widget):
                def on_key(event):
                    parts = []
                    if event.state & 0x4:
                        parts.append('Control')
                    if event.state & 0x1:
                        parts.append('Shift')
                    if event.state & 0x8 or event.state & 0x80:
                        parts.append('Alt')
                    keysym = event.keysym
                    if keysym in ('Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R'):
                        return
                    parts.append(keysym)
                    key_str = '<' + '-'.join(parts) + '>'
                    e_widget.delete(0, tk.END)
                    e_widget.insert(0, key_str)
                return on_key

            entry.bind('<Key>', make_capture(entry))

        # ===== 按钮 =====
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        def apply_settings():
            # 保存数据目录
            new_dir = dir_entry.get().strip()
            if new_dir and new_dir != self.data_dir:
                if os.path.isdir(new_dir) or not os.path.exists(new_dir):
                    self.data_dir = new_dir
                    os.makedirs(self.data_dir, exist_ok=True)
                    self.config_file = os.path.join(self.data_dir, 'calcpaper_config.json')
                    self.session_file = os.path.join(self.data_dir, 'calcpaper_session.json')
                else:
                    messagebox.showwarning(
                        "Warning" if self.language == 'en' else "警告",
                        "Invalid directory path" if self.language == 'en' else "无效的目录路径")
                    return
            # 保存快捷键
            for action_name, entry in entries.items():
                self.shortcuts[action_name] = entry.get().strip()
            self.bind_shortcuts()
            self.update_button_texts()
            self.save_config()
            msg = "Settings saved" if self.language == 'en' else "设置已保存"
            self.status_bar.config(text=msg)
            dialog.destroy()

        def reset_shortcuts():
            for action_name, entry in entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, DEFAULT_SHORTCUTS.get(action_name, ''))
            dir_entry.delete(0, tk.END)
            dir_entry.insert(0, DEFAULT_DATA_DIR)

        save_text = "Save" if self.language == 'en' else "保存"
        reset_text = "Reset" if self.language == 'en' else "恢复默认"
        cancel_text = "Cancel" if self.language == 'en' else "取消"

        tk.Button(btn_frame, text=save_text, command=apply_settings, bg="#4CAF50", fg="white",
                  font=("Arial", 10), padx=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=reset_text, command=reset_shortcuts,
                  font=("Arial", 10), padx=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=cancel_text, command=dialog.destroy,
                  font=("Arial", 10), padx=15).pack(side=tk.LEFT, padx=5)

    # ==================== 计算 ====================

    def calculate(self):
        try:
            input_content = self.input_text.get("1.0", tk.END).strip()
            if not input_content:
                self.status_bar.config(text="Please enter calculation content" if self.language == 'en' else "请输入计算内容")
                return

            self.calculator = CalculatorPaperAdvanced(language=self.language)
            self.calculator.process_text(input_content)
            output = self.calculator.format_output()

            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", output)
            self.apply_syntax_highlighting()
            self.output_text.config(state=tk.DISABLED)

            self.status_bar.config(text="Calculation completed" if self.language == 'en' else "计算完成")
            self.save_gui_state(input_content, output)
            self.last_saved_input = input_content
            self.update_undo_redo_buttons()

        except Exception as e:
            title = "Error" if self.language == 'en' else "错误"
            messagebox.showerror(title, str(e))
            self.status_bar.config(text=f"Error: {e}" if self.language == 'en' else f"错误: {e}")

    def apply_syntax_highlighting(self):
        for tag in self.output_text.tag_names():
            self.output_text.tag_remove(tag, "1.0", tk.END)

        self.output_text.tag_config("comment", foreground="gray")
        self.output_text.tag_config("result", foreground="green", font=("Consolas", 10, "bold"))
        self.output_text.tag_config("error", foreground="red")
        self.output_text.tag_config("total", foreground="blue", font=("Consolas", 10, "bold"))
        self.output_text.tag_config("endian", foreground="purple", font=("Consolas", 10, "bold"))
        self.output_text.tag_config("bit_info", foreground="darkblue", font=("Consolas", 9))
        self.output_text.tag_config("hex_result", foreground="#E65100", font=("Consolas", 10, "bold"))

        content = self.output_text.get("1.0", tk.END)
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            line_start = f"{i}.0"
            line_end = f"{i}.end"

            if line.strip().startswith('#'):
                self.output_text.tag_add("comment", line_start, line_end)
            elif '错误:' in line or '变量未定义:' in line:
                self.output_text.tag_add("error", line_start, line_end)
            elif line.strip().startswith('总计:'):
                self.output_text.tag_add("total", line_start, line_end)
            elif line.strip().startswith('-'):
                self.output_text.tag_add("comment", line_start, line_end)
            elif 'endian:' in line.lower():
                self.output_text.tag_add("endian", line_start, line_end)
            elif any(kw in line for kw in ['十六进制:', '二进制:', '位数:', '位索引',
                                            'Hexadecimal:', 'Binary:', 'Bits:', 'Bit indices']):
                self.output_text.tag_add("bit_info", line_start, line_end)
            elif 'hex(' in line.lower() and '=' in line:
                eq_pos = line.find('=')
                if eq_pos > 0:
                    self.output_text.tag_add("hex_result", f"{i}.{eq_pos}", line_end)
            elif '=' in line and not line.strip().startswith('#'):
                eq_pos = line.find('=')
                if eq_pos > 0:
                    self.output_text.tag_add("result", f"{i}.{eq_pos}", line_end)

    # ==================== 清空/示例/文件 ====================

    def clear_all(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.save_gui_state("", "")
        self.last_saved_input = ""
        self.status_bar.config(text="Cleared" if self.language == 'en' else "已清空")

    def load_example(self):
        if self.language == 'en':
            example = """# Advanced CalcPaper Example

# Basic hex operations
a = 0xFF
b = 0x1234
sum = a + b

# Bitwise operations
and_op = a & b
or_op = a | b

# RGB color extraction
color = 0xFF8040
red = (color >> 16) & 0xFF
green = (color >> 8) & 0xFF
blue = color & 0xFF

# View bit structure with bitmap (big endian)
bitmap(color, 1)

# hex function
hex(255)
hex(color)

# Percentage calculation
price = 100
discount = price * 15%
final_price = price - discount
"""
        else:
            example = """# 高级计算稿纸示例

# 基本16进制运算
a = 0xFF
b = 0x1234
和 = a + b

# 位运算
与 = a & b
或 = a | b

# RGB颜色提取
颜色 = 0xFF8040
红色 = (颜色 >> 16) & 0xFF
绿色 = (颜色 >> 8) & 0xFF
蓝色 = 颜色 & 0xFF

# 使用bitmap查看位结构（大端字节序）
bitmap(颜色, 1)

# hex 函数
hex(255)
hex(颜色)

# 百分数计算
价格 = 100
折扣 = 价格 * 15%
实付 = 价格 - 折扣
"""
        self.input_text.unbind('<<Modified>>')
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", example)
        self.save_gui_state(example, "")
        self.last_saved_input = example
        self.input_text.bind('<<Modified>>', self.on_input_modified)
        self.status_bar.config(text="Example loaded" if self.language == 'en' else "已加载示例")

    def open_file(self):
        title = "Open File" if self.language == 'en' else "打开文件"
        filename = filedialog.askopenfilename(title=title, filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                # 清理计算结果标注，提取原始表达式
                content = self._strip_result_annotations(content)
                self.input_text.unbind('<<Modified>>')
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", content)
                self.save_gui_state(content, "")
                self.last_saved_input = content
                self.input_text.bind('<<Modified>>', self.on_input_modified)
                self.status_bar.config(text=f"Opened: {filename}" if self.language == 'en' else f"已打开: {filename}")
            except Exception as e:
                messagebox.showerror("Error" if self.language == 'en' else "错误", str(e))

    def _strip_result_annotations(self, text):
        """清理计算结果标注，提取原始输入表达式
        
        输出格式示例：
          a = 0xFF        = 255
          bitmap(a, 1)    = 255  # 255
          hex(a)          = 0xFF  # 255
          位索引行、十六进制行等（bitmap输出的附加行）
        
        需要：
        - 去掉 bitmap/hex 输出的附加信息行（缩进的十六进制/二进制/位数/位索引行）
        - 去掉结果部分（表达式后面多余的 = result 和 # comment）
        """
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            stripped = line.strip()
            # 跳过 bitmap 输出的附加行（以空格开头的信息行）
            if stripped and line.startswith('  ') and any(stripped.startswith(kw) for kw in [
                '十六进制:', '二进制:', '位数:', '位索引',
                'Hexadecimal:', 'Binary:', 'Bits:', 'Bit indices',
                '|'
            ]):
                continue
            # 空行和注释行保持不变
            if not stripped or stripped.startswith('#'):
                cleaned.append(line)
                continue
            # 处理带结果标注的行
            # 格式: "原始表达式    = 结果  # 注释"
            # 需要找到原始表达式中最后一个有意义的 = 之后的结果部分
            # 策略：如果行中有多个 =，第一个是赋值，后面的是结果
            if '=' in stripped:
                # 检查是否是赋值表达式（如 a = 0xFF）
                first_eq = stripped.index('=')
                left = stripped[:first_eq].strip()
                right_part = stripped[first_eq+1:].strip()
                
                # 检查左边是否是变量名
                is_assignment = bool(re.match(r'^[a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*$', left))
                
                if is_assignment:
                    # 赋值行：a = 0xFF        = 255  # 注释
                    # 需要提取 "a = 原始表达式"
                    # 在 right_part 中找到结果分隔符（多个空格后的 =）
                    # 用正则匹配：值部分  空格+= 结果
                    match = re.match(r'^(.+?)\s{2,}=\s', right_part)
                    if match:
                        original_expr = match.group(1).strip()
                        cleaned.append(f"{left} = {original_expr}")
                    else:
                        cleaned.append(stripped)
                else:
                    # 非赋值行（如 bitmap(a, 1)    = 255）
                    # 找到多空格+= 的位置
                    match = re.match(r'^(.+?)\s{2,}=\s', stripped)
                    if match:
                        original_expr = match.group(1).strip()
                        cleaned.append(original_expr)
                    else:
                        cleaned.append(stripped)
            else:
                cleaned.append(stripped)
        return '\n'.join(cleaned)

    def save_file(self):
        title = "Save File" if self.language == 'en' else "保存文件"
        filename = filedialog.asksaveasfilename(title=title, defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            try:
                content = self.output_text.get("1.0", tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_bar.config(text=f"Saved: {filename}" if self.language == 'en' else f"已保存: {filename}")
            except Exception as e:
                messagebox.showerror("Error" if self.language == 'en' else "错误", str(e))

    # ==================== 撤销/恢复 ====================

    def save_gui_state(self, input_text, output_text):
        if self.gui_history_index < len(self.gui_history) - 1:
            self.gui_history = self.gui_history[:self.gui_history_index + 1]
        self.gui_history.append((input_text, output_text))
        self.gui_history_index = len(self.gui_history) - 1
        if len(self.gui_history) > 50:
            self.gui_history.pop(0)
            self.gui_history_index -= 1
        self.update_undo_redo_buttons()

    def on_input_modified(self, event):
        if self.input_text.edit_modified():
            self.input_text.edit_modified(False)
            if hasattr(self, '_save_timer'):
                self.root.after_cancel(self._save_timer)
            self._save_timer = self.root.after(500, self.auto_save_input)

    def auto_save_input(self):
        current_input = self.input_text.get("1.0", "end-1c")
        if current_input != self.last_saved_input:
            output_content = self.output_text.get("1.0", "end-1c")
            self.save_gui_state(current_input, output_content)
            self.last_saved_input = current_input

    def undo(self):
        if self.gui_history_index > 0:
            self.gui_history_index -= 1
            inp, out = self.gui_history[self.gui_history_index]
            self.input_text.unbind('<<Modified>>')
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", inp)
            self.last_saved_input = inp
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", out)
            self.apply_syntax_highlighting()
            self.output_text.config(state=tk.DISABLED)
            self.input_text.bind('<<Modified>>', self.on_input_modified)
            self.status_bar.config(text="Undo" if self.language == 'en' else "撤销完成")
            self.update_undo_redo_buttons()

    def redo(self):
        if self.gui_history_index < len(self.gui_history) - 1:
            self.gui_history_index += 1
            inp, out = self.gui_history[self.gui_history_index]
            self.input_text.unbind('<<Modified>>')
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", inp)
            self.last_saved_input = inp
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", out)
            self.apply_syntax_highlighting()
            self.output_text.config(state=tk.DISABLED)
            self.input_text.bind('<<Modified>>', self.on_input_modified)
            self.status_bar.config(text="Redo" if self.language == 'en' else "恢复完成")
            self.update_undo_redo_buttons()

    def update_undo_redo_buttons(self):
        if hasattr(self, 'undo_button'):
            self.undo_button.config(state=tk.NORMAL if self.gui_history_index > 0 else tk.DISABLED)
        if hasattr(self, 'redo_button'):
            self.redo_button.config(state=tk.NORMAL if self.gui_history_index < len(self.gui_history) - 1 else tk.DISABLED)


def main():
    root = tk.Tk()
    app = CalculatorGUIAdvanced(root)
    root.mainloop()


if __name__ == '__main__':
    main()
