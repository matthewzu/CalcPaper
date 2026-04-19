#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CalcPaper - Advanced Calculator Paper GUI
Supports hex, binary, bitwise operations and byte order display

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
import threading
import urllib.request
import urllib.error
import webbrowser
from calc_paper import CalculatorPaperAdvanced

from version import VERSION

# Config file path
# Default is the executable directory; after PyInstaller packaging, it's the exe directory
GITHUB_REPO = "matthewzu/CalcPaper"

def _get_exe_dir():
    """Get the directory of the executable"""
    if getattr(sys, 'frozen', False):
        # After PyInstaller packaging
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def _get_user_data_dir():
    """Get user data directory: ~/.calcpaper"""
    return os.path.join(os.path.expanduser("~"), ".calcpaper")

DEFAULT_DATA_DIR = _get_user_data_dir()
BOOTSTRAP_CONFIG = os.path.join(DEFAULT_DATA_DIR, 'calcpaper_config.json')

# Get resource file path (compatible with PyInstaller packaging)
def _resource_path(filename):
    """Get absolute path of resource file, compatible with PyInstaller packaging"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

# Default shortcut configuration
DEFAULT_SHORTCUTS = {
    'calculate': '<Control-Return>',
    'calculate_alt': '<F5>',
    'clear': '<Control-d>',
    'undo': '<Control-z>',
    'redo': '<Control-y>',
    'load_example': '<Control-l>',
    'open_file': '<Control-o>',
    'save_file': '<Control-s>',
    'font_increase': '<Control-equal>',
    'font_decrease': '<Control-minus>',
    'help': '<F1>',
}

# Shortcut display names
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
    'help': 'Help',
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
    'help': '帮助',
}


def shortcut_display(key_str):
    """Convert tkinter shortcut string to readable format, e.g. <Control-s> -> Ctrl+S"""
    s = key_str.strip('<>').replace('Control', 'Ctrl').replace('Return', 'Enter')
    parts = s.split('-')
    return '+'.join(p.upper() if len(p) == 1 else p for p in parts)


class UpdateChecker:
    """Background update checker"""

    def __init__(self, current_version, language, callback):
        self.current_version = current_version
        self.language = language
        self.callback = callback  # callback(new_version, download_url, asset_url)

    def check(self):
        """Execute check in background thread"""
        thread = threading.Thread(target=self._do_check, daemon=True)
        thread.start()

    def _do_check(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url, headers={
                "User-Agent": "CalcPaper",
                "Accept": "application/vnd.github.v3+json",
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            # Skip draft or prerelease
            if data.get("draft") or data.get("prerelease"):
                return
            tag = data.get("tag_name", "").lstrip("v")
            if tag and self._compare_versions(self.current_version, tag):
                # Find platform-specific asset URL
                asset_url = None
                asset_size = 0
                platform = sys.platform
                for asset in data.get("assets", []):
                    # Skip assets still being uploaded
                    if asset.get("state") != "uploaded":
                        continue
                    name = asset.get("name", "").lower()
                    matched = False
                    if platform == "win32" and name.endswith(".exe"):
                        matched = True
                    elif platform == "darwin" and name.endswith(".dmg"):
                        matched = True
                    elif platform.startswith("linux") and not name.endswith((".exe", ".dmg")):
                        matched = True
                    if matched:
                        asset_url = asset["browser_download_url"]
                        asset_size = asset.get("size", 0)
                dl_url = data.get("html_url", f"https://github.com/{GITHUB_REPO}/releases")
                self.callback(tag, dl_url, asset_url, asset_size)
        except Exception:
            pass  # Silent ignore all errors

    @staticmethod
    def _compare_versions(current, remote):
        """Compare version strings. Returns True if remote is newer."""
        def parse_ver(v):
            v = v.lstrip('v').strip()
            parts = []
            for p in v.split('.'):
                try:
                    parts.append(int(p))
                except ValueError:
                    parts.append(0)
            return parts

        cur = parse_ver(current)
        rem = parse_ver(remote)
        # Pad to same length
        max_len = max(len(cur), len(rem))
        cur.extend([0] * (max_len - len(cur)))
        rem.extend([0] * (max_len - len(rem)))
        return rem > cur


class AutoCompletePopup:
    """Autocomplete popup widget"""
    def __init__(self, text_widget, root):
        self.text_widget = text_widget
        self.root = root
        self.popup = None
        self.listbox = None
        self.candidates = []
        self.selected_index = 0

    def show(self, candidates, x, y):
        """Show popup at position with candidates list"""
        self.hide()
        if not candidates:
            return
        self.candidates = candidates
        self.selected_index = 0

        self.popup = tk.Toplevel(self.root)
        self.popup.wm_overrideredirect(True)
        self.popup.wm_geometry(f"+{x}+{y}")

        self.listbox = tk.Listbox(self.popup, font=("Consolas", 10),
                                   selectmode=tk.SINGLE, exportselection=False,
                                   width=30, height=min(len(candidates), 8))
        self.listbox.pack()

        for c in candidates:
            self.listbox.insert(tk.END, c)

        self.listbox.selection_set(0)
        self.listbox.bind('<Double-Button-1>', lambda e: self.select_current())

        self.popup.bind('<FocusOut>', lambda e: self.root.after(100, self._check_focus))

    def _check_focus(self):
        try:
            if self.popup and not self.popup.focus_get():
                self.hide()
        except:
            pass

    def hide(self):
        if self.popup:
            try:
                self.popup.destroy()
            except:
                pass
            self.popup = None
            self.listbox = None
            self.candidates = []

    def is_visible(self):
        return self.popup is not None

    def select_current(self):
        if self.candidates and 0 <= self.selected_index < len(self.candidates):
            return self.candidates[self.selected_index]
        return None

    def move_selection(self, direction):
        """direction: -1 up, 1 down"""
        if not self.listbox or not self.candidates:
            return
        self.selected_index = max(0, min(len(self.candidates) - 1, self.selected_index + direction))
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.selected_index)
        self.listbox.see(self.selected_index)


class CalculatorGUIAdvanced:
    def __init__(self, root):
        self.root = root
        self.min_font_size = 8
        self.max_font_size = 32

        # Set window icon
        self._set_icon()

        # Load config (language, font, window size, shortcuts)
        self.load_config()

        self.update_title()

        # Create calculator instance
        self.calculator = CalculatorPaperAdvanced(language=self.language)

        # GUI-specific history (saves input and output text)
        self.gui_history = []
        self.gui_history_index = -1
        self.last_saved_input = ""

        # Create widgets
        self.create_widgets()

        # Bind shortcuts
        self.bind_shortcuts()

        # Bind window resize event
        self.root.bind('<Configure>', self.on_window_configure)

        # Restore last session
        self.root.after(100, self._restore_session_and_init)

        # Restore window position (needs to be after window is shown)
        self.root.after(150, self._apply_saved_position)

        # Autocomplete widget
        self.autocomplete = AutoCompletePopup(self.input_text, self.root)

        # Bind autocomplete key events
        # KeyPress for intercepting Tab/Enter/Up/Down/Escape before text widget processes them
        self.input_text.bind('<KeyPress>', self._on_keypress_for_autocomplete)
        # KeyRelease for updating autocomplete popup after text changes
        self.input_text.bind('<KeyRelease>', self._on_keyrelease_for_autocomplete)

        # Bind input modification event
        self.input_text.bind('<<Modified>>', self.on_input_modified)

        # Save on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start background update check (2 second delay)
        self.root.after(2000, self._start_update_check)

    # ==================== Config Persistence ====================

    def _set_icon(self):
        """Set window icon"""
        try:
            icon_path = _resource_path('calcpaper.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

    def load_config(self):
        """Load configuration file
        
        Data is stored in ~/.calcpaper by default.
        Supports migration from old exe-directory layout.
        """
        defaults = {
            'language': 'en',
            'font_size': 10,
            'window_geometry': '1200x800',
            'window_position': None,
            'data_dir': DEFAULT_DATA_DIR,
            'shortcuts': DEFAULT_SHORTCUTS.copy(),
        }

        # Migration: if old config exists in exe dir, migrate to new location
        exe_dir = _get_exe_dir()
        old_config = os.path.join(exe_dir, 'calcpaper_config.json')
        if old_config != BOOTSTRAP_CONFIG and os.path.exists(old_config) and not os.path.exists(BOOTSTRAP_CONFIG):
            try:
                os.makedirs(DEFAULT_DATA_DIR, exist_ok=True)
                import shutil
                shutil.copy2(old_config, BOOTSTRAP_CONFIG)
                old_session = os.path.join(exe_dir, 'calcpaper_session.json')
                new_session = os.path.join(DEFAULT_DATA_DIR, 'calcpaper_session.json')
                if os.path.exists(old_session) and not os.path.exists(new_session):
                    shutil.copy2(old_session, new_session)
            except Exception:
                pass

        # Read config from default location
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

        # Determine data directory
        self.data_dir = config.get('data_dir', DEFAULT_DATA_DIR)
        os.makedirs(self.data_dir, exist_ok=True)
        self.config_file = os.path.join(self.data_dir, 'calcpaper_config.json')
        self.session_file = os.path.join(self.data_dir, 'calcpaper_session.json')

        # If data_dir differs from default, re-read full config from actual data_dir
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

        # Set window size first
        self.root.geometry(self._saved_geometry)

    def _apply_saved_position(self):
        """Apply saved position after window is shown"""
        if self._saved_position:
            try:
                x, y = self._saved_position.split(',')
                x, y = int(x), int(y)
                # Ensure window doesn't appear off-screen
                screen_w = self.root.winfo_screenwidth()
                screen_h = self.root.winfo_screenheight()
                x = max(0, min(x, screen_w - 100))
                y = max(0, min(y, screen_h - 100))
                self.root.geometry(f"+{x}+{y}")
            except Exception:
                pass

    def save_config(self):
        """Save configuration file"""
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
            # If data_dir is not default, also save a bootstrap config in default dir (containing only data_dir)
            if self.config_file != BOOTSTRAP_CONFIG:
                with open(BOOTSTRAP_CONFIG, 'w', encoding='utf-8') as f:
                    json.dump({'data_dir': self.data_dir}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ==================== Session Persistence ====================

    def save_session(self):
        """Save current session (input and output content)"""
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
        """Load last session"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def _restore_session_and_init(self):
        """Restore session and initialize state"""
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

        # Save initial state
        input_c = self.input_text.get("1.0", "end-1c")
        output_c = self.output_text.get("1.0", "end-1c")
        self.save_gui_state(input_c, output_c)

    def on_close(self):
        """Save config and session on window close"""
        self.save_config()
        self.save_session()
        self.root.destroy()

    def _start_update_check(self):
        """Start background update check"""
        UpdateChecker(VERSION, self.language, self._show_update_notification).check()

    def _show_update_notification(self, new_version, download_url, asset_url=None, asset_size=0):
        """Show update notification and auto-download"""
        def show():
            if not asset_url:
                # No platform-specific asset ready yet
                title = "Update" if self.language == 'en' else "更新检查"
                msg = f"v{new_version} release assets are not ready yet. Please try again later." if self.language == 'en' \
                    else f"v{new_version} 发布资源尚未就绪，请稍后重试。"
                messagebox.showinfo(title, msg)
                return
            title = "Update" if self.language == 'en' else "更新检查"
            msg = f"New version {new_version} available! Download now?" if self.language == 'en' else f"发现新版本 {new_version}！是否立即下载更新？"
            if not messagebox.askyesno(title, msg):
                return
            self.status_bar.config(text="⏳ Downloading update..." if self.language == 'en' else "⏳ 正在下载更新...")
            self.root.update()
            threading.Thread(target=lambda: self._download_update(asset_url, new_version, asset_size), daemon=True).start()
        self.root.after(0, show)

    def _download_update(self, asset_url, new_version, expected_size=0):
        """Download update with progress reporting and integrity checks."""
        try:
            import time
            req = urllib.request.Request(asset_url, headers={"User-Agent": "CalcPaper"})
            with urllib.request.urlopen(req, timeout=300) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                chunks = []
                start_time = time.time()
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    downloaded += len(chunk)
                    elapsed = time.time() - start_time
                    speed = downloaded / elapsed if elapsed > 0 else 0
                    dl_mb = downloaded / 1048576
                    if total > 0:
                        total_mb = total / 1048576
                        pct = downloaded * 100 // total
                        msg = f"⏳ {pct}%  {dl_mb:.1f}/{total_mb:.1f}MB  {speed/1024:.0f}KB/s"
                    else:
                        msg = f"⏳ {dl_mb:.1f}MB  {speed/1024:.0f}KB/s"
                    self.root.after(0, lambda m=msg: self.status_bar.config(text=m))
                data = b"".join(chunks)

            # --- Integrity checks ---
            # 1. Size check against Content-Length
            if total > 0 and len(data) != total:
                raise RuntimeError(
                    f"Size mismatch: expected {total} bytes, got {len(data)}" if self.language == 'en'
                    else f"大小不匹配: 预期 {total} 字节, 实际 {len(data)}")
            # 2. Size check against GitHub asset size
            if expected_size > 0 and len(data) != expected_size:
                raise RuntimeError(
                    f"Size mismatch with release: expected {expected_size} bytes, got {len(data)}" if self.language == 'en'
                    else f"与发布信息不匹配: 预期 {expected_size} 字节, 实际 {len(data)}")
            # 3. Minimum size sanity check (< 100KB is suspicious for an app binary)
            if len(data) < 102400:
                raise RuntimeError(
                    f"Downloaded file too small ({len(data)} bytes), possibly incomplete" if self.language == 'en'
                    else f"下载文件过小 ({len(data)} 字节)，可能不完整")
            # 4. Binary header validation
            if sys.platform == "win32" and data[:2] != b"MZ":
                raise RuntimeError(
                    "Invalid executable (not a valid PE file)" if self.language == 'en'
                    else "无效的可执行文件 (非有效 PE 格式)")
            elif sys.platform == "darwin" and data[:4] not in (b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf", b"\xca\xfe\xba\xbe"):
                raise RuntimeError(
                    "Invalid executable (not a valid Mach-O file)" if self.language == 'en'
                    else "无效的可执行文件 (非有效 Mach-O 格式)")
            elif sys.platform.startswith("linux") and data[:4] != b"\x7fELF":
                raise RuntimeError(
                    "Invalid executable (not a valid ELF file)" if self.language == 'en'
                    else "无效的可执行文件 (非有效 ELF 格式)")

            # Determine exe path
            exe_path = sys.executable
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                ext = ".exe" if sys.platform == "win32" else ""
                exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"CalcPaper{ext}")

            tmp_path = exe_path + ".new"
            with open(tmp_path, "wb") as f:
                f.write(data)

            if sys.platform != "win32":
                os.chmod(tmp_path, 0o755)

            if getattr(sys, 'frozen', False):
                old_path = exe_path + ".old"
                try:
                    os.remove(old_path)
                except OSError:
                    pass
                os.rename(exe_path, old_path)
                os.rename(tmp_path, exe_path)
                msg = f"v{new_version} downloaded. Restart to apply." if self.language == 'en' else f"v{new_version} 已下载，重启生效。"
            else:
                msg = f"v{new_version} downloaded to {exe_path}" if self.language == 'en' else f"v{new_version} 已下载到 {exe_path}"

            self.root.after(0, lambda: self.status_bar.config(text=f"✅ {msg}"))
            self.root.after(0, lambda: messagebox.showinfo(
                "Update" if self.language == 'en' else "更新", msg))
        except Exception as e:
            err_msg = f"Update failed: {e}" if self.language == 'en' else f"更新失败: {e}"
            self.root.after(0, lambda: self.status_bar.config(text=f"❌ {err_msg}"))

    # ==================== Window and Title ====================

    def on_window_configure(self, event):
        if event.widget == self.root:
            self.root.after_idle(self.check_button_scroll_needed)

    def update_title(self):
        if self.language == 'en':
            self.root.title(f"CalcPaper - Advanced v{VERSION}")
        else:
            self.root.title(f"计算稿纸 - 高级版 v{VERSION}")

    # ==================== Language Toggle ====================

    def toggle_language(self):
        self.language = 'zh' if self.language == 'en' else 'en'
        self.calculator.set_language(self.language)
        self.update_title()
        self.update_button_texts()

    def update_button_texts(self):
        """Update button texts (with shortcut display)"""
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
        if hasattr(self, 'help_button'):
            self.help_button.config(text=_btn("Help", "帮助", "help"))

        self.update_initial_font_display()
        self.update_undo_redo_buttons()

    # ==================== Font ====================

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

    # ==================== Widget Creation ====================

    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=0)
        main_frame.grid_rowconfigure(2, weight=0)
        main_frame.grid_columnconfigure(0, weight=1)

        # ========== Input/Output Area ==========
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

        # ========== Button Bar ==========
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

        # Shortcut config button
        shortcut_text = "⌨" 
        self.shortcut_button = tk.Button(self.scrollable_frame, text=shortcut_text,
                                         command=self.open_shortcut_config, font=("Arial", 10), padx=8, pady=3, bg="#607D8B", fg="white")
        self.shortcut_button.pack(side=tk.LEFT, padx=3)

        # Help button
        self.help_button = tk.Button(self.scrollable_frame, text=_btn_text("Help", "帮助", "help"),
                                     command=self.show_help, font=("Arial", 10), padx=8, pady=3, bg="#2196F3", fg="white")
        self.help_button.pack(side=tk.LEFT, padx=3)

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

        # ========== Status Bar ==========
        status_frame = tk.Frame(main_frame, height=25)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        status_frame.grid_propagate(False)

        self.status_bar = tk.Label(status_frame, text="Ready" if self.language == 'en' else "就绪",
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 9))
        self.status_bar.pack(fill=tk.BOTH, expand=True)

        self.root.after(100, self.update_initial_font_display)

    # ==================== Button Scrolling ====================

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

    # ==================== Shortcuts ====================

    def bind_shortcuts(self):
        """Bind shortcuts (from config)"""
        # First unbind all known shortcuts
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
            'help': lambda e: self.show_help(),
        }

        self._bound_keys = []
        # Track which keys are "calculate" actions that need newline suppression
        calc_keys = set()
        for action_name, key_str in sc.items():
            if key_str and action_name in actions:
                try:
                    self.root.bind(key_str, actions[action_name])
                    self._bound_keys.append(key_str)
                    if action_name in ('calculate', 'calculate_alt'):
                        calc_keys.add(key_str)
                    # Also bind uppercase version
                    if 'Control-' in key_str and len(key_str.split('-')[-1].rstrip('>')) == 1:
                        upper_key = key_str[:-2] + key_str[-2].upper() + key_str[-1]
                        if upper_key != key_str:
                            self.root.bind(upper_key, actions[action_name])
                            self._bound_keys.append(upper_key)
                            if action_name in ('calculate', 'calculate_alt'):
                                calc_keys.add(upper_key)
                except Exception:
                    pass

        # Bind calculate shortcuts on input_text to suppress newline insertion
        def _calc_and_break(e):
            self.calculate()
            return "break"
        for key_str in calc_keys:
            try:
                self.input_text.bind(key_str, _calc_and_break)
            except Exception:
                pass

    def _unbind_all_shortcuts(self):
        """Unbind all bound shortcuts"""
        if hasattr(self, '_bound_keys'):
            for key in self._bound_keys:
                try:
                    self.root.unbind(key)
                except Exception:
                    pass
        self._bound_keys = []

    def open_shortcut_config(self):
        """Open settings dialog (shortcuts + data directory)"""
        dialog = tk.Toplevel(self.root)
        title = "Settings" if self.language == 'en' else "设置"
        dialog.title(title)
        dialog.geometry("550x480")
        dialog.transient(self.root)
        dialog.grab_set()

        names = SHORTCUT_NAMES_EN if self.language == 'en' else SHORTCUT_NAMES_ZH

        # ===== Data Directory =====
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

        # ===== Shortcuts =====
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

        # ===== Buttons =====
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        def apply_settings():
            # Save data directory
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
            # Save shortcuts
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

    # ==================== Calculation ====================

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

    # ==================== Clear/Example/File ====================

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

# swap: byte order conversion
net_data = 0x12345678
host_data = swap(net_data)

# hex + swap combined
hex(swap(net_data))

# hex function
hex(255)
hex(color)

# Date/time arithmetic
today = Y20260410
deadline = today + D10
next_month = today + M1
diff = Y20260410 - Y20260101

# Time arithmetic
start = T090000
end = T173000
duration = end - start
lunch = start + h3 + m30

# Workday calculation (auto-skip weekends)
wd = workday(Y20260411, 10)
wd2 = workday(Y20260411, 10, Y20260501/-Y20260412)

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

# swap: 字节序转换
网络数据 = 0x12345678
本地数据 = swap(网络数据)

# hex + swap 组合使用
hex(swap(网络数据))

# hex 函数
hex(255)
hex(颜色)

# 日期运算
今天 = Y20260410
截止日 = 今天 + D10
下个月 = 今天 + M1
天数差 = Y20260410 - Y20260101

# 时间运算
上班 = T090000
下班 = T173000
工时 = 下班 - 上班
午餐 = 上班 + h3 + m30

# 工作日计算（自动跳过周末）
交付日 = workday(Y20260411, 10)
交付日2 = workday(Y20260411, 10, Y20260501/-Y20260412)

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
                # Strip result annotations, extract original expressions
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
        """Strip result annotations, extract original input expressions
        
        Output format examples:
          a = 0xFF        = 255
          bitmap(a, 1)    = 255  # 255
          hex(a)          = 0xFF  # 255
          Bit index lines, hex lines, etc. (bitmap output supplementary lines)
        
        Actions:
        - Remove bitmap/hex output supplementary lines (indented hex/binary/bits/index lines)
        - Remove result portion (extra = result and # comment after expression)
        """
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            stripped = line.strip()
            # Skip bitmap output supplementary lines (indented info lines)
            if stripped and line.startswith('  ') and any(stripped.startswith(kw) for kw in [
                '十六进制:', '二进制:', '位数:', '位索引',
                'Hexadecimal:', 'Binary:', 'Bits:', 'Bit indices',
                '|'
            ]):
                continue
            # Empty lines and comment lines stay unchanged
            if not stripped or stripped.startswith('#'):
                cleaned.append(line)
                continue
            # Process lines with result annotations
            # Format: "original expression    = result  # comment"
            # Need to find the result portion after the last meaningful = in the original expression
            # Strategy: if line has multiple =, first is assignment, rest are results
            if '=' in stripped:
                # Check if it's an assignment expression (e.g. a = 0xFF)
                first_eq = stripped.index('=')
                left = stripped[:first_eq].strip()
                right_part = stripped[first_eq+1:].strip()
                
                # Check if left side is a variable name
                is_assignment = bool(re.match(r'^[a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*$', left))
                
                if is_assignment:
                    # Assignment line: a = 0xFF        = 255  # comment
                    # Need to extract "a = original expression"
                    # Find result separator (multiple spaces followed by =) in right_part
                    # Regex match: value part  spaces+= result
                    match = re.match(r'^(.+?)\s{2,}=\s', right_part)
                    if match:
                        original_expr = match.group(1).strip()
                        cleaned.append(f"{left} = {original_expr}")
                    else:
                        cleaned.append(stripped)
                else:
                    # Non-assignment line (e.g. bitmap(a, 1)    = 255)
                    # Find position of multiple spaces + =
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

    # ==================== Undo/Redo ====================

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

    # ==================== Autocomplete ====================

    def _get_defined_variables(self):
        """Parse defined variable names from input area text in real-time"""
        content = self.input_text.get("1.0", "end-1c")
        variables = []
        pattern = re.compile(r'^([a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*)\s*=', re.MULTILINE)
        reserved_pattern = re.compile(r'^[YTMWDhms]\d+$')
        for match in pattern.finditer(content):
            name = match.group(1)
            if not reserved_pattern.match(name):
                if name not in variables:
                    variables.append(name)
        return variables

    def _get_current_prefix(self):
        """Get the variable name prefix being typed at cursor and its start position"""
        try:
            cursor_pos = self.input_text.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            col = int(col)
            line_text = self.input_text.get(f"{line}.0", f"{line}.{col}")
            # Walk backwards to find start of current word
            i = len(line_text) - 1
            while i >= 0:
                ch = line_text[i]
                if re.match(r'[a-zA-Z0-9_\u4e00-\u9fa5]', ch):
                    i -= 1
                else:
                    break
            word_start = i + 1
            prefix = line_text[word_start:]
            if prefix and re.match(r'[a-zA-Z_\u4e00-\u9fa5]', prefix[0]):
                start_pos = f"{line}.{word_start}"
                return (prefix, start_pos)
            return (None, None)
        except Exception:
            return (None, None)

    def _on_keypress_for_autocomplete(self, event):
        """KeyPress handler: intercept Tab/Enter/Up/Down/Escape when popup is visible"""
        keysym = event.keysym

        if keysym == 'Escape' and self.autocomplete.is_visible():
            self.autocomplete.hide()
            return "break"

        if keysym in ('Up', 'Down') and self.autocomplete.is_visible():
            direction = -1 if keysym == 'Up' else 1
            self.autocomplete.move_selection(direction)
            return "break"

        if keysym == 'Tab' and self.autocomplete.is_visible():
            selected = self.autocomplete.select_current()
            if selected:
                prefix, prefix_start = self._get_current_prefix()
                if prefix_start:
                    self._insert_completion(selected, prefix_start)
            self.autocomplete.hide()
            return "break"

        # Don't intercept other keys
        return None

    def _on_keyrelease_for_autocomplete(self, event):
        """KeyRelease handler: update autocomplete popup after text changes"""
        keysym = event.keysym
        # Skip modifier keys and keys already handled by KeyPress
        if keysym in ('Escape', 'Up', 'Down', 'Tab', 'Return',
                       'Shift_L', 'Shift_R', 'Control_L', 'Control_R',
                       'Alt_L', 'Alt_R', 'Caps_Lock'):
            return
        self._update_autocomplete()

    def _update_autocomplete(self):
        """Update candidate list based on current prefix"""
        prefix, prefix_start = self._get_current_prefix()
        if not prefix or len(prefix) < 1:
            self.autocomplete.hide()
            return

        variables = self._get_defined_variables()
        prefix_lower = prefix.lower()
        matches = [v for v in variables if v.lower().startswith(prefix_lower) and v != prefix]

        if matches:
            try:
                bbox = self.input_text.bbox(tk.INSERT)
                if bbox:
                    x = self.input_text.winfo_rootx() + bbox[0]
                    y = self.input_text.winfo_rooty() + bbox[1] + bbox[3]
                    self.autocomplete.show(matches, x, y)
                else:
                    self.autocomplete.hide()
            except Exception:
                self.autocomplete.hide()
        else:
            self.autocomplete.hide()

    def _insert_completion(self, variable_name, prefix_start):
        """Insert selected variable name into input area, replacing typed prefix"""
        cursor_pos = self.input_text.index(tk.INSERT)
        self.input_text.delete(prefix_start, cursor_pos)
        self.input_text.insert(prefix_start, variable_name)
        self.autocomplete.hide()

    # ==================== Help ====================

    def show_help(self):
        """Show help dialog matching current language"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Help" if self.language == 'en' else "帮助")
        dialog.geometry("700x550")
        dialog.transient(self.root)

        text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, font=("Consolas", 10), state=tk.NORMAL)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        if self.language == 'en':
            content = self._help_text_en()
        else:
            content = self._help_text_zh()

        text.insert("1.0", content)
        text.config(state=tk.DISABLED)

        tk.Button(dialog, text="OK", command=dialog.destroy, padx=20, pady=5).pack(pady=(0, 10))

    def _help_text_en(self):
        return f"""CalcPaper v{VERSION} - Smart Calculator for Programmers

=== Basic Operations ===
  +, -, *, /, ()          Arithmetic
  variable = expression   Variable assignment
  6.5%, 10%               Percentage
  # comment               Comment line

=== Number Formats ===
  0xFF, 0x1A2B            Hexadecimal
  0b1010, 0b11110000      Binary
  255                     Decimal

=== Bitwise Operations ===
  <<   Left shift         e.g. 0b1010 << 2
  >>   Right shift        e.g. 0xFF >> 4
  &    AND                e.g. 0xFF & 0x0F
  |    OR                 e.g. 0xF0 | 0x0F
  ^    XOR                e.g. 0xFF ^ 0xAA
  ~    NOT                e.g. ~0b1010

=== Built-in Functions ===
  bitmap(value)           Bit visualization (little endian, default)
  bitmap(value, 1)        Bit visualization (big endian)
  bitmap(value, 0, 32)    Bit visualization with width
  swap(value)             Byte order swap (can use in expressions)
  hex(value)              Display as hexadecimal

=== Date/Time Arithmetic (NEW in v2.0) ===
  Yyyyymmdd               Date literal      e.g. Y20260410
  Thhmmss                 Time literal      e.g. T143000

  Date durations (UPPERCASE):
    Mxx   months          e.g. M3
    Wxx   weeks           e.g. W2
    Dxx   days            e.g. D10

  Time durations (lowercase):
    hxx   hours           e.g. h2
    mxx   minutes         e.g. m30
    sxx   seconds         e.g. s45

  Operations:
    date + duration  ->  date       Y20260410 + D10 = Y20260420
    date - duration  ->  date       Y20260410 - M1  = Y20260310
    date - date      ->  days       Y20260410 - Y20260101 = 99
    time + duration  ->  time       T090000 + h3 + m30 = T123000
    time - duration  ->  time       T143000 - m30 = T140000
    time - time      ->  seconds    T173000 - T090000 = 30600

=== workday() Working Day Calculation (NEW in v2.0) ===
  workday(start, days)              Count working days (skip weekends)
  workday(start, days, holidays)    With custom holidays

  Holiday format (separated by /):
    Y20260501                       Add as holiday (+ optional)
    -Y20260412                      Remove from holidays (make workday)
    Y20260501/-Y20260412            Combined

  Example:
    workday(Y20260411, 10)                          10 working days
    workday(Y20260411, 20, Y20260501)               add May Day
    workday(Y20260411, 10, -Y20260412)              remove weekend
    workday(Y20260411, 15, Y20260501/-Y20260412)    combined

=== Reserved Keywords ===
  Y, T, M, W, D (uppercase) and h, m, s (lowercase) followed by
  digits are reserved and cannot be used as variable names.
  e.g. M3, h2, Y20260410, T143000 are all reserved.

=== Keyboard Shortcuts ===
  Ctrl+Enter    Calculate
  F5            Calculate (alt)
  Ctrl+D        Clear
  Ctrl+Z        Undo
  Ctrl+Y        Redo
  Ctrl+L        Load example
  Ctrl+O        Open file
  Ctrl+S        Save result
  Ctrl+=/+      Font increase
  Ctrl+-        Font decrease
  F1            Help
  Tab           Autocomplete confirm

=== Autocomplete ===
  Type a variable name prefix -> popup appears
  Tab           Confirm selection
  Up/Down       Navigate candidates
  Escape        Dismiss popup

=== Tips ===
  - Results are auto-saved and restored on next launch
  - Window size, position, language, font are remembered
  - All shortcuts are customizable via Settings button
  - Update check runs in background on startup

=== Related Projects ===
  GanttPilot - Collaborative Project Manager with Gantt Chart
  https://github.com/matthewzu/GanttPilot
"""

    def _help_text_zh(self):
        return f"""CalcPaper v{VERSION} - 程序员的智能计算稿纸

=== 基本运算 ===
  +, -, *, /, ()          四则运算
  变量名 = 表达式          变量赋值
  6.5%, 10%               百分数
  # 注释                   注释行

=== 数值格式 ===
  0xFF, 0x1A2B            16进制
  0b1010, 0b11110000      2进制
  255                     10进制

=== 位运算 ===
  <<   左移               例: 0b1010 << 2
  >>   右移               例: 0xFF >> 4
  &    与                 例: 0xFF & 0x0F
  |    或                 例: 0xF0 | 0x0F
  ^    异或               例: 0xFF ^ 0xAA
  ~    非                 例: ~0b1010

=== 内置函数 ===
  bitmap(数值)            位结构可视化（小端，默认）
  bitmap(数值, 1)         位结构可视化（大端）
  bitmap(数值, 0, 32)     位结构可视化（指定宽度）
  swap(数值)              字节序交换（可用于表达式）
  hex(数值)               显示16进制

=== 日期/时间运算（v2.0 新增）===
  Yyyyymmdd               日期字面量      例: Y20260410
  Thhmmss                 时间字面量      例: T143000

  日期时长（大写）：
    Mxx   月              例: M3
    Wxx   周              例: W2
    Dxx   天              例: D10

  时间时长（小写）：
    hxx   小时            例: h2
    mxx   分钟            例: m30
    sxx   秒              例: s45

  运算规则：
    日期 + 时长  ->  日期       Y20260410 + D10 = Y20260420
    日期 - 时长  ->  日期       Y20260410 - M1  = Y20260310
    日期 - 日期  ->  天数       Y20260410 - Y20260101 = 99
    时间 + 时长  ->  时间       T090000 + h3 + m30 = T123000
    时间 - 时长  ->  时间       T143000 - m30 = T140000
    时间 - 时间  ->  秒数       T173000 - T090000 = 30600

=== workday() 工作日计算（v2.0 新增）===
  workday(起始日期, 天数)           计算工作日（自动跳过周末）
  workday(起始日期, 天数, 节假日)   自定义节假日

  节假日格式（用 / 分隔）：
    Y20260501                       添加为节假日（+号可省略）
    -Y20260412                      移除节假日（变为工作日）
    Y20260501/-Y20260412            组合使用

  示例：
    workday(Y20260411, 10)                          10个工作日
    workday(Y20260411, 20, Y20260501)               添加五一
    workday(Y20260411, 10, -Y20260412)              移除周末
    workday(Y20260411, 15, Y20260501/-Y20260412)    组合

=== 保留关键字 ===
  Y、T、M、W、D（大写）和 h、m、s（小写）后跟数字
  为保留关键字，不可用作变量名。
  例: M3、h2、Y20260410、T143000 均为保留关键字。

=== 快捷键 ===
  Ctrl+Enter    计算
  F5            计算（备选）
  Ctrl+D        清空
  Ctrl+Z        撤销
  Ctrl+Y        恢复
  Ctrl+L        加载示例
  Ctrl+O        打开文件
  Ctrl+S        保存结果
  Ctrl+=/+      放大字体
  Ctrl+-        缩小字体
  F1            帮助
  Tab           自动补全确认

=== 自动补全 ===
  输入已定义的变量名前缀 -> 弹出候选列表
  Tab           确认选择
  上/下方向键    导航候选项
  Escape        关闭弹窗

=== 提示 ===
  - 计算结果自动保存，下次启动自动恢复
  - 窗口大小、位置、语言、字体会被记住
  - 所有快捷键可通过设置按钮自定义
  - 启动时后台自动检查更新

=== 相关项目 ===
  GanttPilot - 基于甘特图的协作式项目管理器
  https://github.com/matthewzu/GanttPilot
"""


def main():
    root = tk.Tk()
    app = CalculatorGUIAdvanced(root)
    root.mainloop()


if __name__ == '__main__':
    main()
