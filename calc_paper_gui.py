#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CalcPaper - Advanced Calculator Paper GUI (CustomTkinter)
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

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import sys
import re
import subprocess
import threading
import urllib.request
import urllib.error
import webbrowser

try:
    import customtkinter as ctk
except ImportError:
    print("customtkinter is required. Install with: pip install customtkinter")
    sys.exit(1)

from calc_paper import CalculatorPaperAdvanced
from calc_session import SessionManager, GlobalVariableStore, Session
from calc_history import GitHistoryStore
from version import VERSION

# Config file path
GITHUB_REPO = "matthewzu/CalcPaper"

def _get_exe_dir():
    """Get the directory of the executable"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def _get_user_data_dir():
    """Get user data directory: ~/.calcpaper"""
    return os.path.join(os.path.expanduser("~"), ".calcpaper")

DEFAULT_DATA_DIR = _get_user_data_dir()
BOOTSTRAP_CONFIG = os.path.join(DEFAULT_DATA_DIR, 'calcpaper_config.json')

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
    """Convert tkinter shortcut string to readable format"""
    s = key_str.strip('<>').replace('Control', 'Ctrl').replace('Return', 'Enter')
    parts = s.split('-')
    return '+'.join(p.upper() if len(p) == 1 else p for p in parts)


def _link_dialog(parent, title, message, link_text, link_url, ask=False, gui=None):
    """Show a dialog with a clickable link (GanttPilot style).

    Args:
        parent: parent window
        title: dialog title
        message: main text
        link_text: link display text
        link_url: link URL
        ask: True returns bool (Yes/No), False shows OK only
        gui: GUI instance for _active_dialog tracking

    Returns:
        bool
    """
    if gui and gui._has_active_dialog():
        return False
    result = [False]
    dlg = ctk.CTkToplevel(parent)
    dlg.title(title)
    dlg.transient(parent)
    dlg.grab_set()
    dlg.resizable(False, False)

    if gui:
        gui._active_dialog = dlg

    frame = ctk.CTkFrame(dlg, fg_color="transparent")
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

    ctk.CTkLabel(frame, text=message, wraplength=380, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 8))

    link_label = ctk.CTkLabel(frame, text=link_text, text_color="#3B8ED0", cursor="hand2")
    link_label.pack(anchor=tk.W, pady=(0, 12))
    link_label.bind("<Button-1>", lambda e: webbrowser.open(link_url))

    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
    btn_frame.pack()
    if ask:
        def _yes():
            result[0] = True
            dlg.destroy()
        def _no():
            result[0] = False
            dlg.destroy()
        ctk.CTkButton(btn_frame, text="Yes", command=_yes, width=80).pack(side=tk.LEFT, padx=8)
        ctk.CTkButton(btn_frame, text="No", command=_no, width=80).pack(side=tk.LEFT, padx=8)
    else:
        ctk.CTkButton(btn_frame, text="OK", command=dlg.destroy, width=80).pack()

    dlg.update_idletasks()
    w = dlg.winfo_reqwidth()
    h = dlg.winfo_reqheight()
    px = parent.winfo_x() + (parent.winfo_width() - w) // 2
    py = parent.winfo_y() + (parent.winfo_height() - h) // 2
    dlg.geometry(f"+{max(0,px)}+{max(0,py)}")
    dlg.focus_set()
    dlg.bind("<Escape>", lambda e: dlg.destroy())
    parent.wait_window(dlg)
    if gui:
        gui._active_dialog = None
    return result[0]


class UpdateChecker:
    """Background update checker with no_update and fail callbacks (GanttPilot style)"""

    def __init__(self, current_version, language, callback,
                 no_update_callback=None, fail_callback=None):
        self.current_version = current_version
        self.language = language
        self.callback = callback
        self.no_update_callback = no_update_callback
        self.fail_callback = fail_callback

    def check(self):
        threading.Thread(target=self._do_check, daemon=True).start()

    def _do_check(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url, headers={
                "User-Agent": "CalcPaper",
                "Accept": "application/vnd.github.v3+json",
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            if data.get("draft") or data.get("prerelease"):
                if self.no_update_callback:
                    self.no_update_callback()
                return
            tag = data.get("tag_name", "").lstrip("v")
            if tag and self._compare_versions(self.current_version, tag):
                asset_url = None
                asset_size = 0
                platform = sys.platform
                for asset in data.get("assets", []):
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
            else:
                if self.no_update_callback:
                    self.no_update_callback()
        except Exception:
            if self.fail_callback:
                self.fail_callback()

    @staticmethod
    def _compare_versions(current, remote):
        """Returns True if remote is newer."""
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
        self._active_dialog = None
        self._focus_restore_id = None

        # Clean up leftover .old file from previous update
        self._cleanup_old_executable()

        # Set window icon
        self._set_icon()

        # Load config
        self.load_config()
        self.update_title()

        # Multi-session management
        self.global_store = GlobalVariableStore()
        self.session_manager = SessionManager(self.global_store)
        self._current_session_id = None

        # Git history store
        self.history_store = GitHistoryStore()

        # Subscribe to global variable changes
        self.global_store.subscribe(self._on_global_variable_changed)

        # Create calculator instance (will be replaced per-session)
        self.calculator = CalculatorPaperAdvanced(language=self.language)

        # GUI-specific state
        self.last_saved_input = ""

        # Create widgets
        self.create_widgets()

        # Bind shortcuts
        self.bind_shortcuts()

        # Bind multi-session shortcuts
        self.root.bind('<Control-t>', lambda e: self._new_session_tab())
        self.root.bind('<Control-T>', lambda e: self._new_session_tab())
        self.root.bind('<Control-w>', lambda e: self._close_current_session_tab())
        self.root.bind('<Control-W>', lambda e: self._close_current_session_tab())
        self.root.bind('<Control-Tab>', lambda e: self._switch_next_session_tab())

        # Bind window resize event
        self.root.bind('<Configure>', self.on_window_configure)

        # Focus restoration
        self.root.bind("<FocusIn>", self._on_main_focus)

        # Restore last session
        self.root.after(100, self._restore_session_and_init)

        # Restore window position
        self.root.after(150, self._apply_saved_position)

        # Autocomplete widget
        self.autocomplete = AutoCompletePopup(self.input_text, self.root)

        # Bind autocomplete key events
        self.input_text.bind('<KeyPress>', self._on_keypress_for_autocomplete)
        self.input_text.bind('<KeyRelease>', self._on_keyrelease_for_autocomplete)

        # Bind input modification event
        self.input_text.bind('<<Modified>>', self.on_input_modified)

        # Save on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start background update check (2 second delay)
        self.root.after(2000, self._start_update_check)

        # Show Git warning if not available
        if self.history_store.warning_message:
            self.root.after(500, lambda: self._toast(
                "⚠ Git 未安装，请安装以启用历史功能: git-scm.com/downloads"
                if self.language == 'zh' else
                "⚠ Git not found. Install Git for history: git-scm.com/downloads",
                duration=8000
            ))

    # ==================== Dialog Focus Management ====================

    def _on_main_focus(self, event=None):
        if self._focus_restore_id is not None:
            self.root.after_cancel(self._focus_restore_id)
        self._focus_restore_id = self.root.after(50, self._restore_dialog_focus)

    def _has_active_dialog(self):
        dlg = self._active_dialog
        if dlg is not None:
            try:
                if dlg.winfo_exists():
                    dlg.lift()
                    dlg.focus_force()
                    return True
            except Exception:
                pass
            self._active_dialog = None
        return False

    def _restore_dialog_focus(self):
        self._focus_restore_id = None
        dlg = self._active_dialog
        if dlg is not None:
            try:
                if dlg.winfo_exists():
                    dlg.deiconify()
                    dlg.lift()
                    dlg.focus_force()
                    try:
                        dlg.grab_set()
                    except Exception:
                        pass
            except Exception:
                pass

    # ==================== Config Persistence ====================

    def _set_icon(self):
        try:
            icon_path = _resource_path('calcpaper.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

    def load_config(self):
        defaults = {
            'language': 'en',
            'font_size': 10,
            'window_geometry': '1200x800',
            'window_position': None,
            'data_dir': DEFAULT_DATA_DIR,
            'shortcuts': DEFAULT_SHORTCUTS.copy(),
            'appearance_mode': 'system',
        }

        # Migration from old exe-directory layout
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

        # Read config from default location (~/.calcpaper)
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

        # Data directory (config + session all in one dir, default ~/.calcpaper)
        self.data_dir = config.get('data_dir', DEFAULT_DATA_DIR)
        os.makedirs(self.data_dir, exist_ok=True)
        self.config_file = os.path.join(self.data_dir, 'calcpaper_config.json')
        self.session_file = os.path.join(self.data_dir, 'calcpaper_session.json')

        # If data_dir differs from default, re-read config from actual location
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
        self.appearance_mode = config.get('appearance_mode', 'system')

        # Apply appearance mode
        ctk.set_appearance_mode(self.appearance_mode)

        # Set window size
        self.root.geometry(self._saved_geometry)

    def _apply_saved_position(self):
        if self._saved_position:
            try:
                x, y = self._saved_position.split(',')
                x, y = int(x), int(y)
                screen_w = self.root.winfo_screenwidth()
                screen_h = self.root.winfo_screenheight()
                x = max(0, min(x, screen_w - 100))
                y = max(0, min(y, screen_h - 100))
                self.root.geometry(f"+{x}+{y}")
            except Exception:
                pass

    def save_config(self):
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
            'appearance_mode': self.appearance_mode,
        }
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            if self.config_file != BOOTSTRAP_CONFIG:
                with open(BOOTSTRAP_CONFIG, 'w', encoding='utf-8') as f:
                    json.dump({'data_dir': self.data_dir}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ==================== Session Persistence ====================

    def save_session(self):
        """Save all sessions using SessionManager (version 2 format)."""
        try:
            # Save current session state before persisting
            self._save_current_session_state()
            self.session_manager.save_all(self.session_file)
        except Exception:
            pass

    def load_session(self):
        """Load sessions using SessionManager. Returns True if sessions were loaded."""
        try:
            self.session_manager.load_all(self.session_file)
            return True
        except Exception:
            return False

    def _save_current_session_state(self):
        """Save the current editor content to the active session object."""
        if self._current_session_id is None:
            return
        try:
            session = self.session_manager.get_session(self._current_session_id)
            session.input_text = self.input_text.get("1.0", "end-1c")
            session.output_text = self.output_text.get("1.0", "end-1c")
            session.variables = dict(session.calculator.variables) if hasattr(session.calculator, 'variables') else {}
        except (KeyError, Exception):
            pass

    def _restore_session_and_init(self):
        """Restore sessions from file and initialize the UI."""
        loaded = self.load_session()

        # Ensure at least one session exists
        sessions = self.session_manager.list_sessions()
        if not sessions:
            self.session_manager.create_session()
            sessions = self.session_manager.list_sessions()

        # Build session tab bar
        self._rebuild_session_tabs()

        # Activate the saved active tab
        active_idx = self.session_manager.active_tab_index
        if active_idx < len(sessions):
            self._activate_session(sessions[active_idx].session_id)
        else:
            self._activate_session(sessions[0].session_id)

        # Save initial GUI state
        input_c = self.input_text.get("1.0", "end-1c")
        output_c = self.output_text.get("1.0", "end-1c")
        self.save_gui_state(input_c, output_c)

    def on_close(self):
        self.save_config()
        # Save current session state and persist all sessions
        self._save_current_session_state()
        # Update active tab index
        sessions = self.session_manager.list_sessions()
        for i, s in enumerate(sessions):
            if s.session_id == self._current_session_id:
                self.session_manager.active_tab_index = i
                break
        self.save_session()
        self.root.destroy()

    # ==================== Update Check (GanttPilot style) ====================

    def _start_update_check(self):
        UpdateChecker(VERSION, self.language, self._show_update_notification).check()

    def manual_update_check(self):
        """Manual update check with button disable and status feedback."""
        self.update_btn.configure(state=tk.DISABLED)
        self.status_var.set("⏳ Checking..." if self.language == 'en' else "⏳ 检查中...")

        def on_result(new_version, download_url, asset_url=None, asset_size=0):
            self.root.after(0, lambda: self.update_btn.configure(state=tk.NORMAL))
            if new_version:
                self.root.after(0, lambda: self._show_update_notification(new_version, download_url, asset_url, asset_size))

        def on_no_update():
            self.root.after(0, lambda: self.update_btn.configure(state=tk.NORMAL))
            msg = "Already latest version" if self.language == 'en' else "已是最新版本"
            self.root.after(0, lambda: self.status_var.set(f"✅ {msg}"))

        def on_fail():
            self.root.after(0, lambda: self.update_btn.configure(state=tk.NORMAL))
            msg = "Check failed" if self.language == 'en' else "检查失败"
            self.root.after(0, lambda: self.status_var.set(f"❌ {msg}"))

        UpdateChecker(VERSION, self.language, on_result,
                      no_update_callback=on_no_update, fail_callback=on_fail).check()

    def _show_update_notification(self, new_version, download_url, asset_url=None, asset_size=0):
        def show():
            if not asset_url:
                title = "Update" if self.language == 'en' else "更新检查"
                msg = f"v{new_version} release assets are not ready yet." if self.language == 'en' \
                    else f"v{new_version} 发布资源尚未就绪，请稍后重试。"
                messagebox.showinfo(title, msg)
                return
            changelog_url = f"https://github.com/{GITHUB_REPO}/blob/master/CHANGELOG.md"
            msg = f"New version {new_version} available! Download now?" if self.language == 'en' \
                else f"发现新版本 {new_version}！是否立即下载更新？"
            link_text = "📋 " + ("View Changelog" if self.language == 'en' else "查看更新日志")
            if not _link_dialog(self.root, "Update" if self.language == 'en' else "更新检查",
                                msg, link_text, changelog_url, ask=True, gui=self):
                return
            self.status_var.set("⏳ Downloading..." if self.language == 'en' else "⏳ 正在下载...")
            self.root.update()
            threading.Thread(target=lambda: self._download_update(asset_url, new_version, asset_size), daemon=True).start()
        self.root.after(0, show)

    def _download_update(self, asset_url, new_version, expected_size=0):
        """Download update with progress and integrity checks, then auto-restart."""
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
                    self.root.after(0, lambda m=msg: self.status_var.set(m))
                data = b"".join(chunks)

            # Integrity checks
            if total > 0 and len(data) != total:
                raise RuntimeError(f"Size mismatch: expected {total}, got {len(data)}")
            if expected_size > 0 and len(data) != expected_size:
                raise RuntimeError(f"Size mismatch with release: expected {expected_size}, got {len(data)}")
            if len(data) < 102400:
                raise RuntimeError(f"File too small ({len(data)} bytes)")
            if sys.platform == "win32" and data[:2] != b"MZ":
                raise RuntimeError("Invalid PE executable")
            elif sys.platform == "darwin" and data[:4] not in (b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf", b"\xca\xfe\xba\xbe"):
                raise RuntimeError("Invalid Mach-O executable")
            elif sys.platform.startswith("linux") and data[:4] != b"\x7fELF":
                raise RuntimeError("Invalid ELF executable")

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

            # Show completion with README link, then auto-restart
            def _post_update():
                readme_url = f"https://github.com/{GITHUB_REPO}#readme"
                msg = f"v{new_version} downloaded. Restarting..." if self.language == 'en' \
                    else f"v{new_version} 已下载，即将重启..."
                link_text = "📖 " + ("View README" if self.language == 'en' else "查看说明")
                _link_dialog(self.root, "Update" if self.language == 'en' else "更新",
                             msg, link_text, readme_url, ask=False, gui=self)
                self._restart_app(exe_path)

            self.root.after(0, _post_update)
        except Exception as e:
            err_msg = f"Update failed: {e}" if self.language == 'en' else f"更新失败: {e}"
            self.root.after(0, lambda: self.status_var.set(f"❌ {err_msg}"))

    def _cleanup_old_executable(self):
        """Remove leftover .old file from a previous update."""
        if getattr(sys, 'frozen', False):
            old_path = sys.executable + ".old"
            try:
                if os.path.exists(old_path):
                    os.remove(old_path)
            except OSError:
                pass

    def _restart_app(self, exe_path=None):
        """Restart the application after update.
        
        Waits for the current process to fully exit before launching the new exe.
        
        Critical: Must clear _MEIPASS2 environment variable to prevent the new
        process from inheriting the old PyInstaller temp directory path, which
        causes "Failed to load Python DLL" errors on Windows or similar issues
        on macOS/Linux.
        """
        if exe_path is None:
            exe_path = sys.executable
        try:
            import subprocess
            # Clear PyInstaller env vars so child process doesn't inherit old _MEI path
            env = os.environ.copy()
            env.pop('_MEIPASS2', None)
            env.pop('_MEIPASS', None)
            
            current_pid = os.getpid()
            
            if sys.platform == "win32":
                # Use PowerShell for a completely silent delay (no window flash).
                # Wait 5 seconds for old process to fully exit and _MEI dir cleanup,
                # then launch the new exe.
                # Critical: Explicitly remove _MEIPASS2 inside PowerShell before
                # launching the new process, to ensure the new exe doesn't inherit
                # the old PyInstaller temp directory path.
                ps_cmd = (
                    f'powershell -WindowStyle Hidden -Command "'
                    f'[Environment]::SetEnvironmentVariable(\'_MEIPASS2\', $null); '
                    f'[Environment]::SetEnvironmentVariable(\'_MEIPASS\', $null); '
                    f'$env:_MEIPASS2 = $null; '
                    f'$env:_MEIPASS = $null; '
                    f'Start-Sleep -Seconds 5; '
                    f'Remove-Item -Force -ErrorAction SilentlyContinue \'{exe_path}.old\'; '
                    f'Start-Process \'{exe_path}\'"'
                )
                subprocess.Popen(
                    ps_cmd,
                    shell=True,
                    env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                    close_fds=True
                )
            elif sys.platform == "darwin":
                # macOS: wait for old process to exit, clean up .old, then open new exe
                subprocess.Popen(
                    f'while kill -0 {current_pid} 2>/dev/null; do sleep 0.5; done; '
                    f'sleep 1; '
                    f'rm -f "{exe_path}.old" 2>/dev/null; '
                    f'open "{exe_path}"',
                    shell=True,
                    env=env,
                    start_new_session=True,
                    close_fds=True
                )
            else:
                # Linux: wait for old process to exit, clean up .old, then launch
                subprocess.Popen(
                    f'while kill -0 {current_pid} 2>/dev/null; do sleep 0.5; done; '
                    f'sleep 1; '
                    f'rm -f "{exe_path}.old" 2>/dev/null; '
                    f'"{exe_path}" &',
                    shell=True,
                    env=env,
                    start_new_session=True,
                    close_fds=True
                )
        except Exception:
            pass
        self.root.destroy()
        sys.exit(0)

    # ==================== Window and Title ====================

    def on_window_configure(self, event):
        pass  # No button scrolling needed with CTk layout

    def update_title(self):
        if self.language == 'en':
            self.root.title(f"CalcPaper v{VERSION}")
        else:
            self.root.title(f"计算稿纸 v{VERSION}")

    # ==================== Language Toggle ====================

    def toggle_language(self):
        self.language = 'zh' if self.language == 'en' else 'en'
        self.calculator.set_language(self.language)
        self.update_title()
        self.update_button_texts()

    def update_button_texts(self):
        sc = self.shortcuts

        def _btn(en, zh, key):
            disp = shortcut_display(sc.get(key, ''))
            label = en if self.language == 'en' else zh
            return f"{label} ({disp})" if disp else label

        if hasattr(self, 'calc_button'):
            self.calc_button.configure(text=_btn("▶ Calculate", "▶ 计算", "calculate"))
        if hasattr(self, 'clear_button'):
            self.clear_button.configure(text=_btn("Clear", "清空", "clear"))
        if hasattr(self, 'undo_button'):
            self.undo_button.configure(text="↩ " + ("Undo" if self.language == 'en' else "撤销"))
        if hasattr(self, 'redo_button'):
            self.redo_button.configure(text="↪ " + ("Redo" if self.language == 'en' else "恢复"))
        if hasattr(self, 'example_button'):
            self.example_button.configure(text="📋 " + ("Example" if self.language == 'en' else "示例"))
        if hasattr(self, 'open_button'):
            self.open_button.configure(text="📂 " + ("Open" if self.language == 'en' else "打开"))
        if hasattr(self, 'save_button'):
            self.save_button.configure(text="💾 " + ("Save" if self.language == 'en' else "保存"))
        if hasattr(self, 'lang_button'):
            self.lang_button.configure(text="🌐 中文" if self.language == 'en' else "🌐 EN")
        if hasattr(self, 'help_button'):
            self.help_button.configure(text="? " + ("Help" if self.language == 'en' else "帮助"))
        if hasattr(self, 'input_label'):
            self.input_label.configure(text="Input:" if self.language == 'en' else "输入:")
        if hasattr(self, 'output_label'):
            self.output_label.configure(text="Output:" if self.language == 'en' else "输出:")
        if hasattr(self, 'update_btn'):
            self.update_btn.configure(text="⟳ " + ("Update" if self.language == 'en' else "更新"))
        if hasattr(self, 'shortcut_button'):
            self.shortcut_button.configure(text="⚙ " + ("Settings" if self.language == 'en' else "设置"))

        self.update_initial_font_display()
        self.update_undo_redo_buttons()

    # ==================== Font ====================

    def increase_font(self):
        if self.font_size < self.max_font_size:
            self.font_size = min(self.font_size + 2, self.max_font_size)
            self.update_fonts()
            msg = f"Font: {self.font_size}" if self.language == 'en' else f"字体: {self.font_size}"
            self._toast(msg)

    def decrease_font(self):
        if self.font_size > self.min_font_size:
            self.font_size = max(self.font_size - 2, self.min_font_size)
            self.update_fonts()
            msg = f"Font: {self.font_size}" if self.language == 'en' else f"字体: {self.font_size}"
            self._toast(msg)

    def restore_normal_status(self):
        self.status_var.set("Ready" if self.language == 'en' else "就绪")

    def _toast(self, message, duration=3000):
        """Show a toast-style status message that auto-clears."""
        self.status_var.set(message)
        if hasattr(self, '_toast_timer'):
            self.root.after_cancel(self._toast_timer)
        self._toast_timer = self.root.after(duration, self.restore_normal_status)

    def _switch_to_editor(self):
        """Switch to the Editor tab."""
        if hasattr(self, 'tabview') and hasattr(self, '_editor_tab_name'):
            try:
                self.tabview.set(self._editor_tab_name)
            except Exception:
                pass

    def _on_tab_changed(self):
        """Called when tab selection changes. Disable editor buttons on non-editor tabs."""
        current = self.tabview.get()
        is_editor = (current == self._editor_tab_name)
        state = tk.NORMAL if is_editor else tk.DISABLED
        for btn in (self.calc_button, self.clear_button, self.open_button,
                    self.save_button, self.example_button):
            btn.configure(state=state)
        # Undo/redo respect both tab state and history state
        if is_editor:
            self.update_undo_redo_buttons()
        else:
            self.undo_button.configure(state=tk.DISABLED)
            self.redo_button.configure(state=tk.DISABLED)

    # ==================== Multi-Session Tab Management ====================

    def _rebuild_session_tabs(self):
        """Rebuild the session tab bar from the SessionManager state."""
        # Clear existing tab buttons
        for widget in self._session_tab_frame.winfo_children():
            widget.destroy()
        self._session_tab_buttons.clear()

        sessions = self.session_manager.list_sessions()
        for session in sessions:
            self._add_session_tab_button(session)

        # Add "+" button for new tab
        add_btn = ctk.CTkButton(
            self._session_tab_frame, text="+", width=28, height=26,
            command=self._new_session_tab,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent", hover_color=("gray80", "gray30"),
            text_color=("gray30", "gray70")
        )
        add_btn.pack(side=tk.LEFT, padx=(4, 0))

    def _add_session_tab_button(self, session):
        """Add a single session tab button to the tab bar."""
        btn_frame = ctk.CTkFrame(self._session_tab_frame, fg_color="transparent", height=28)
        btn_frame.pack(side=tk.LEFT, padx=(0, 1))

        # Tab name button (double-click to rename, drag to reorder)
        is_active = (session.session_id == self._current_session_id)
        fg = ("gray75", "gray35") if is_active else "transparent"
        tab_btn = ctk.CTkButton(
            btn_frame, text=session.name, height=26, width=80,
            command=lambda sid=session.session_id: self._switch_session_tab(sid),
            font=ctk.CTkFont(size=11, weight="bold" if is_active else "normal"),
            fg_color=fg, hover_color=("gray80", "gray30"),
            text_color=("gray10", "gray90"),
            corner_radius=6
        )
        tab_btn.pack(side=tk.LEFT)

        # Bind double-click for rename
        tab_btn.bind("<Double-Button-1>", lambda e, sid=session.session_id: self._rename_session_tab(sid))

        # Bind drag for reorder
        tab_btn.bind("<ButtonPress-1>", lambda e, sid=session.session_id: self._drag_start(e, sid))
        tab_btn.bind("<B1-Motion>", self._drag_motion)
        tab_btn.bind("<ButtonRelease-1>", self._drag_end)

        # Close button (×)
        close_btn = ctk.CTkButton(
            btn_frame, text="×", width=20, height=20,
            command=lambda sid=session.session_id: self._close_session_tab(sid),
            font=ctk.CTkFont(size=12),
            fg_color="transparent", hover_color=("gray80", "gray30"),
            text_color=("gray50", "gray60"),
            corner_radius=4
        )
        close_btn.pack(side=tk.LEFT, padx=(0, 2))

        self._session_tab_buttons[session.session_id] = btn_frame

    def _new_session_tab(self):
        """Create a new session tab."""
        # Save current session state first
        self._save_current_session_state()

        # Create new session
        session = self.session_manager.create_session()

        # Rebuild tabs and activate the new one
        self._rebuild_session_tabs()
        self._activate_session(session.session_id)

        msg = f"New tab: {session.name}" if self.language == 'en' else f"新标签: {session.name}"
        self._toast(msg)

    def _close_session_tab(self, session_id):
        """Close a session tab."""
        # Save current state if closing the active tab
        if session_id == self._current_session_id:
            self._save_current_session_state()

        # Close the session (auto-creates new blank if last)
        self.session_manager.close_session(session_id)

        # Determine which session to activate
        sessions = self.session_manager.list_sessions()
        if sessions:
            # If we closed the active tab, activate the one at the adjusted index
            if session_id == self._current_session_id:
                active_idx = self.session_manager.active_tab_index
                self._current_session_id = None  # Reset before activating
                self._rebuild_session_tabs()
                self._activate_session(sessions[active_idx].session_id)
            else:
                self._rebuild_session_tabs()

    def _close_current_session_tab(self):
        """Close the currently active session tab (Ctrl+W)."""
        if self._current_session_id:
            self._close_session_tab(self._current_session_id)

    def _switch_session_tab(self, session_id):
        """Switch to a specific session tab."""
        if session_id == self._current_session_id:
            return
        self._save_current_session_state()
        self._activate_session(session_id)

    def _switch_next_session_tab(self):
        """Switch to the next session tab (Ctrl+Tab)."""
        sessions = self.session_manager.list_sessions()
        if len(sessions) <= 1:
            return
        current_idx = 0
        for i, s in enumerate(sessions):
            if s.session_id == self._current_session_id:
                current_idx = i
                break
        next_idx = (current_idx + 1) % len(sessions)
        self._switch_session_tab(sessions[next_idx].session_id)

    def _rename_session_tab(self, session_id):
        """Rename a session tab via inline editing (double-click)."""
        try:
            session = self.session_manager.get_session(session_id)
        except KeyError:
            return

        btn_frame = self._session_tab_buttons.get(session_id)
        if not btn_frame:
            return

        # Replace the tab button with an entry widget for inline editing
        for child in btn_frame.winfo_children():
            child.pack_forget()

        entry = ctk.CTkEntry(btn_frame, width=80, height=26,
                             font=ctk.CTkFont(size=11))
        entry.pack(side=tk.LEFT)
        entry.insert(0, session.name)
        entry.select_range(0, tk.END)
        entry.focus_set()

        def _confirm(event=None):
            new_name = entry.get().strip()
            if new_name:
                session.name = new_name
            self._rebuild_session_tabs()

        def _cancel(event=None):
            self._rebuild_session_tabs()

        entry.bind("<Return>", _confirm)
        entry.bind("<Escape>", _cancel)
        entry.bind("<FocusOut>", _confirm)

    def _drag_start(self, event, session_id):
        """Start dragging a session tab."""
        self._drag_session_id = session_id
        self._drag_start_x = event.x_root
        self._drag_moved = False
        self._drag_indicator = None

    def _drag_motion(self, event):
        """Track drag motion and show drop position indicator."""
        if not hasattr(self, '_drag_session_id') or not self._drag_session_id:
            return
        dx = abs(event.x_root - self._drag_start_x)
        if dx > 10:
            self._drag_moved = True
            self._update_drag_indicator(event.x_root)

    def _update_drag_indicator(self, drop_x):
        """Show a visual indicator (vertical line) at the drop position."""
        # Remove old indicator
        if self._drag_indicator:
            try:
                self._drag_indicator.destroy()
            except Exception:
                pass
            self._drag_indicator = None

        insert_x = self._get_drop_indicator_x(drop_x)

        # Draw indicator line
        self._drag_indicator = tk.Frame(
            self._session_tab_frame, width=3, height=24,
            bg="#2563EB", relief=tk.FLAT
        )
        self._drag_indicator.place(x=insert_x - 1, y=2)

    def _drag_end(self, event):
        """End drag and reorder tabs if moved far enough."""
        # Remove indicator
        if hasattr(self, '_drag_indicator') and self._drag_indicator:
            try:
                self._drag_indicator.destroy()
            except Exception:
                pass
            self._drag_indicator = None

        if not hasattr(self, '_drag_session_id') or not self._drag_session_id:
            return
        if not self._drag_moved:
            self._drag_session_id = None
            return

        # Determine drop position
        sessions = self.session_manager.list_sessions()
        source_id = self._drag_session_id
        self._drag_session_id = None

        # Find source index
        source_idx = None
        for i, s in enumerate(sessions):
            if s.session_id == source_id:
                source_idx = i
                break
        if source_idx is None:
            return

        # Find target index using ordered tab positions
        target_idx = self._get_drop_target_index(event.x_root)

        # Perform reorder with proper index adjustment
        if source_idx != target_idx:
            order = self.session_manager._session_order
            sid = order.pop(source_idx)
            # Adjust target if source was before target (removal shifts indices)
            if source_idx < target_idx:
                target_idx = min(target_idx - 1, len(order))
            order.insert(target_idx, sid)
            self._rebuild_session_tabs()

    def _get_drop_target_index(self, drop_x):
        """Calculate the target insertion index based on drop x position.

        Iterates tabs in display order (matching session_order) to find
        where the dragged tab should be inserted.
        """
        sessions = self.session_manager.list_sessions()
        for i, s in enumerate(sessions):
            btn_frame = self._session_tab_buttons.get(s.session_id)
            if btn_frame:
                try:
                    frame_x = btn_frame.winfo_rootx()
                    frame_w = btn_frame.winfo_width()
                    frame_mid = frame_x + frame_w // 2
                    if drop_x < frame_mid:
                        return i
                except Exception:
                    continue
        return len(sessions) - 1

    def _get_drop_indicator_x(self, drop_x):
        """Calculate the x position for the drop indicator line.

        Returns the local x coordinate within _session_tab_frame.
        """
        sessions = self.session_manager.list_sessions()
        frame_root_x = self._session_tab_frame.winfo_rootx()

        for i, s in enumerate(sessions):
            btn_frame = self._session_tab_buttons.get(s.session_id)
            if btn_frame:
                try:
                    bx = btn_frame.winfo_rootx()
                    bw = btn_frame.winfo_width()
                    mid = bx + bw // 2
                    if drop_x < mid:
                        return bx - frame_root_x
                except Exception:
                    continue

        # After last tab
        if sessions:
            btn_frame = self._session_tab_buttons.get(sessions[-1].session_id)
            if btn_frame:
                try:
                    return btn_frame.winfo_rootx() + btn_frame.winfo_width() - frame_root_x
                except Exception:
                    pass
        return 0

    def _activate_session(self, session_id):
        """Activate a session: load its content into the editor."""
        try:
            session = self.session_manager.get_session(session_id)
        except KeyError:
            return

        self._current_session_id = session_id
        self.calculator = session.calculator

        # Update active tab index in session manager
        sessions = self.session_manager.list_sessions()
        for i, s in enumerate(sessions):
            if s.session_id == session_id:
                self.session_manager.active_tab_index = i
                break

        # Load input text
        self.input_text.unbind('<<Modified>>')
        self.input_text.delete("1.0", tk.END)
        if session.input_text:
            self.input_text.insert("1.0", session.input_text)
        self.input_text.bind('<<Modified>>', self.on_input_modified)

        # Load output text
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        if session.output_text:
            self.output_text.insert("1.0", session.output_text)
            self.apply_syntax_highlighting()
        self.output_text.configure(state=tk.DISABLED)

        self.last_saved_input = session.input_text

        # Re-run calculation silently to populate variables if needed
        if session.input_text.strip() and not session.calculator.variables:
            try:
                session.calculator = CalculatorPaperAdvanced(language=self.language)
                # Inject global variables
                for name, value in self.global_store.get_all().items():
                    session.calculator.variables[name] = value
                # Inject global functions
                for fname, (params, body) in self.global_store.get_all_functions().items():
                    session.calculator.functions[fname] = (params, body)
                session.calculator.process_text(session.input_text)
                self.calculator = session.calculator
                session.variables = dict(session.calculator.variables)
            except Exception:
                pass

        # Refresh UI
        self._rebuild_session_tabs()
        self._refresh_variables_tab()
        self._refresh_functions_tab()
        self.update_undo_redo_buttons()

    def _on_global_variable_changed(self, name, value):
        """Callback when a global variable or function changes. Refresh all tabs."""
        self._refresh_variables_tab()
        self._refresh_functions_tab()

    def update_initial_font_display(self):
        if hasattr(self, 'font_size_label'):
            self.font_size_label.configure(text=f"{self.font_size}")
        self.status_var.set("Ready" if self.language == 'en' else "就绪")

    def update_fonts(self):
        self.input_text.configure(font=("Consolas", self.font_size))
        self.output_text.configure(font=("Consolas", self.font_size))
        if hasattr(self, 'vars_text'):
            self.vars_text.configure(font=("Consolas", self.font_size))
        if hasattr(self, 'history_text'):
            self.history_text.configure(font=("Consolas", self.font_size))
        if hasattr(self, 'font_size_label'):
            self.font_size_label.configure(text=f"{self.font_size}")

    def _apply_text_theme(self):
        """Apply theme-appropriate colors to tk.Text widgets based on current appearance mode."""
        mode = ctk.get_appearance_mode()  # "Dark" or "Light"
        if mode == "Dark":
            bg = "#2b2b2b"
            fg = "#dcdcdc"
            insert_bg = "white"
            select_bg = "#264f78"
            output_bg = "#1e1e1e"
        else:
            bg = "#ffffff"
            fg = "#1e1e1e"
            insert_bg = "black"
            select_bg = "#add6ff"
            output_bg = "#f5f5f5"

        self.input_text.configure(bg=bg, fg=fg, insertbackground=insert_bg, selectbackground=select_bg)
        self.output_text.configure(bg=output_bg, fg=fg, insertbackground=insert_bg, selectbackground=select_bg)
        if hasattr(self, 'vars_text'):
            self.vars_text.configure(bg=output_bg, fg=fg, insertbackground=insert_bg, selectbackground=select_bg)
        if hasattr(self, 'funcs_text'):
            self.funcs_text.configure(bg=output_bg, fg=fg, insertbackground=insert_bg, selectbackground=select_bg)
        if hasattr(self, 'history_text'):
            self.history_text.configure(bg=output_bg, fg=fg, insertbackground=insert_bg, selectbackground=select_bg)
        # Re-apply syntax highlighting colors for the current theme
        if self.output_text.get("1.0", "end-1c").strip():
            self.apply_syntax_highlighting()

    def _preview_appearance(self, mode):
        """Live preview appearance mode change from settings dialog."""
        ctk.set_appearance_mode(mode)
        self.root.after(100, self._apply_text_theme)

    def _refresh_variables_tab(self):
        """Update the Variables tab with currently defined variables and their values."""
        if not hasattr(self, 'vars_text'):
            return
        import datetime
        variables = {}
        if hasattr(self, 'calculator') and hasattr(self.calculator, 'variables'):
            variables = self.calculator.variables

        # Get global variables
        global_vars = self.global_store.get_all() if hasattr(self, 'global_store') else {}

        # Get current session name
        session_name = ""
        if self._current_session_id:
            try:
                session = self.session_manager.get_session(self._current_session_id)
                session_name = session.name
            except KeyError:
                pass

        self.vars_text.configure(state=tk.NORMAL)
        self.vars_text.delete("1.0", tk.END)

        has_content = False

        # Show session name header
        if session_name:
            tab_header = f"📄 {session_name}\n" if self.language == 'en' else f"📄 {session_name}\n"
            self.vars_text.insert(tk.END, tab_header)
            self.vars_text.insert(tk.END, "═" * 44 + "\n\n")

        # Local variables section
        if variables:
            has_content = True
            header = "Local Variables\n" if self.language == 'en' else "局部变量\n"
            self.vars_text.insert(tk.END, header)
            self.vars_text.insert(tk.END, "─" * 44 + "\n")
            for name, val in variables.items():
                if isinstance(val, datetime.date) and not isinstance(val, datetime.datetime):
                    display = val.strftime("Y%Y%m%d") + f"  ({val.strftime('%Y-%m-%d')})"
                elif isinstance(val, datetime.time):
                    display = val.strftime("T%H%M%S") + f"  ({val.strftime('%H:%M:%S')})"
                elif isinstance(val, int) and (val > 255 or val < 0):
                    display = f"{val}  (0x{val & 0xFFFFFFFFFFFFFFFF:X})"
                else:
                    display = str(val)
                self.vars_text.insert(tk.END, f"{name:<20}{display}\n")

        # Global variables section
        if global_vars:
            has_content = True
            if variables:
                self.vars_text.insert(tk.END, "\n")
            header = "🌐 Global Variables (全局变量)\n" if self.language == 'en' else "🌐 全局变量\n"
            self.vars_text.insert(tk.END, header)
            self.vars_text.insert(tk.END, "─" * 44 + "\n")
            for name, val in global_vars.items():
                if isinstance(val, datetime.date) and not isinstance(val, datetime.datetime):
                    display = val.strftime("Y%Y%m%d") + f"  ({val.strftime('%Y-%m-%d')})"
                elif isinstance(val, datetime.time):
                    display = val.strftime("T%H%M%S") + f"  ({val.strftime('%H:%M:%S')})"
                elif isinstance(val, int) and (val > 255 or val < 0):
                    display = f"{val}  (0x{val & 0xFFFFFFFFFFFFFFFF:X})"
                else:
                    display = str(val)
                self.vars_text.insert(tk.END, f"🌐 {name:<17}{display}\n")

        if not has_content:
            hint = "No variables defined yet.\nRun a calculation to see variables here." if self.language == 'en' \
                else "暂无变量。\n运行计算后变量会显示在这里。"
            self.vars_text.insert(tk.END, hint)
        self.vars_text.configure(state=tk.DISABLED)

    def _refresh_functions_tab(self):
        """Update the Functions tab with currently defined functions."""
        if not hasattr(self, 'funcs_text'):
            return
        
        local_funcs = {}
        if hasattr(self, 'calculator') and hasattr(self.calculator, 'functions'):
            local_funcs = self.calculator.functions

        global_funcs = self.global_store.get_all_functions() if hasattr(self, 'global_store') else {}

        self.funcs_text.configure(state=tk.NORMAL)
        self.funcs_text.delete("1.0", tk.END)

        has_content = False

        # Local functions section
        if local_funcs:
            has_content = True
            header = "Local Functions\n" if self.language == 'en' else "局部函数\n"
            self.funcs_text.insert(tk.END, header)
            self.funcs_text.insert(tk.END, "─" * 44 + "\n")
            for name, (params, body) in local_funcs.items():
                params_str = ", ".join(params)
                self.funcs_text.insert(tk.END, f"{name}({params_str}) = {body}\n")

        # Global functions section
        if global_funcs:
            has_content = True
            if local_funcs:
                self.funcs_text.insert(tk.END, "\n")
            header = "🌐 Global Functions\n" if self.language == 'en' else "🌐 全局函数\n"
            self.funcs_text.insert(tk.END, header)
            self.funcs_text.insert(tk.END, "─" * 44 + "\n")
            for name, (params, body) in global_funcs.items():
                params_str = ", ".join(params)
                self.funcs_text.insert(tk.END, f"🌐 {name}({params_str}) = {body}\n")

        # Built-in functions section
        self.funcs_text.insert(tk.END, "\n")
        header = "Built-in Functions\n" if self.language == 'en' else "内置函数\n"
        self.funcs_text.insert(tk.END, header)
        self.funcs_text.insert(tk.END, "─" * 44 + "\n")
        builtins_info = [
            ("hex(expr)", "十六进制输出" if self.language != 'en' else "Hexadecimal output"),
            ("swap(expr)", "字节序转换" if self.language != 'en' else "Byte order swap"),
            ("bitmap(expr, endian)", "位图显示" if self.language != 'en' else "Bitmap display"),
            ("comma(expr)", "千分位格式" if self.language != 'en' else "Thousand separators"),
            ("global(name)", "全局化变量/函数" if self.language != 'en' else "Globalize var/func"),
            ("workday(date, n, ...)", "工作日计算" if self.language != 'en' else "Workday calculation"),
        ]
        for sig, desc in builtins_info:
            self.funcs_text.insert(tk.END, f"{sig:<28}{desc}\n")

        if not has_content and not global_funcs:
            # Only show hint if no user functions at all
            pass

        self.funcs_text.configure(state=tk.DISABLED)

    def _refresh_history_tab(self):
        """Update the History tab showing what changed between each calculation."""
        if not hasattr(self, 'history_text'):
            return
        self.history_text.configure(state=tk.NORMAL)
        self.history_text.delete("1.0", tk.END)

        # Configure tags for diff display
        self.history_text.tag_config("added", foreground="#4EC9B0")
        self.history_text.tag_config("removed", foreground="#F44747")
        self.history_text.tag_config("header", foreground="#569CD6", font=("Consolas", self.font_size, "bold"))
        self.history_text.tag_config("result", foreground="#6A9955")
        self.history_text.tag_config("current_marker", foreground="#DCDCAA", font=("Consolas", self.font_size, "bold"))
        self.history_text.tag_config("tab_name", foreground="#C586C0", font=("Consolas", self.font_size, "bold"))

        # Get current session name
        session_name = ""
        if self._current_session_id:
            try:
                session = self.session_manager.get_session(self._current_session_id)
                session_name = session.name
            except KeyError:
                pass

        # Show session name header
        if session_name:
            self.history_text.insert(tk.END, f"📄 {session_name} ", "tab_name")
            label = "History" if self.language == 'en' else "的修改记录"
            self.history_text.insert(tk.END, f"{label}\n")
            self.history_text.insert(tk.END, "═" * 44 + "\n\n")

        # Get gui_history from current session
        gui_history = []
        gui_history_index = -1
        if self._current_session_id is not None:
            try:
                session = self.session_manager.get_session(self._current_session_id)
                gui_history = session.gui_history
                gui_history_index = session.gui_history_index
            except KeyError:
                pass

        if gui_history and len(gui_history) > 1:
            count = 0
            for i in range(len(gui_history) - 1, 0, -1):
                inp, out = gui_history[i]
                if not inp.strip():
                    continue
                count += 1

                # Current position marker
                is_current = (i == gui_history_index)
                at_latest = (gui_history_index == len(gui_history) - 1)

                # Header
                self.history_text.insert(tk.END, f"── #{count} ", "header")
                if is_current and not at_latest:
                    self.history_text.insert(tk.END, "◀ CURRENT ", "current_marker")
                elif is_current and at_latest and count == 1:
                    self.history_text.insert(tk.END, "◀ LATEST ", "current_marker")
                self.history_text.insert(tk.END, "──\n", "header")

                # Show diff: what changed from previous state
                prev_inp = gui_history[i - 1][0] if i > 0 else ""
                cur_lines = set(l.strip() for l in inp.strip().split('\n') if l.strip() and not l.strip().startswith('#'))
                prev_lines = set(l.strip() for l in prev_inp.strip().split('\n') if l.strip() and not l.strip().startswith('#'))

                added = cur_lines - prev_lines
                removed = prev_lines - cur_lines

                if added:
                    for line in list(added)[:4]:
                        self.history_text.insert(tk.END, f"  + {line}\n", "added")
                    if len(added) > 4:
                        self.history_text.insert(tk.END, f"  + ... (+{len(added)-4} more)\n", "added")
                if removed:
                    for line in list(removed)[:2]:
                        self.history_text.insert(tk.END, f"  - {line}\n", "removed")
                    if len(removed) > 2:
                        self.history_text.insert(tk.END, f"  - ... (+{len(removed)-2} more)\n", "removed")

                if not added and not removed:
                    # No code diff (maybe just whitespace change), show input preview
                    lines = [l for l in inp.strip().split('\n') if l.strip() and not l.strip().startswith('#')]
                    for l in lines[:2]:
                        self.history_text.insert(tk.END, f"  {l}\n")

                # Show last result
                if out.strip():
                    out_lines = [l for l in out.strip().split('\n') if l.strip() and '=' in l]
                    if out_lines:
                        last = out_lines[-1].strip()
                        if len(last) > 60:
                            last = last[:57] + "..."
                        self.history_text.insert(tk.END, f"  → {last}\n", "result")

                self.history_text.insert(tk.END, "\n")
                if count >= 20:
                    break
        else:
            hint = "No history yet.\nCalculation history will appear here." if self.language == 'en' \
                else "暂无历史记录。\n计算历史会显示在这里。"
            self.history_text.insert(tk.END, hint)
        self.history_text.configure(state=tk.DISABLED)


    # ==================== Widget Creation ====================

    def create_widgets(self):
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(6, 10))
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # ========== Toolbar (single row, grouped) ==========
        toolbar = ctk.CTkFrame(main_frame, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        sc = self.shortcuts

        def _btn_text(en, zh, key):
            disp = shortcut_display(sc.get(key, ''))
            label = en if self.language == 'en' else zh
            return f"{label} ({disp})" if disp else label

        # Left: Primary actions
        # Group 1: Calculate + Clear
        self.calc_button = ctk.CTkButton(toolbar, text=_btn_text("▶ Calculate", "▶ 计算", "calculate"),
                                          command=self.calculate, fg_color="#2563EB", hover_color="#1D4ED8",
                                          width=120, height=32, font=ctk.CTkFont(size=13, weight="bold"))
        self.calc_button.pack(side=tk.LEFT, padx=(0, 3))

        self.clear_button = ctk.CTkButton(toolbar, text=_btn_text("Clear", "清空", "clear"),
                                           command=self.clear_all, fg_color="#DC2626", hover_color="#B91C1C",
                                           width=70, height=32)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 6))

        # Separator
        ctk.CTkFrame(toolbar, width=1, height=24, fg_color="gray50").pack(side=tk.LEFT, padx=4)

        # Group 2: Undo / Redo
        self.undo_button = ctk.CTkButton(toolbar, text="↩ " + ("Undo" if self.language == 'en' else "撤销"),
                                          command=self.undo, width=70, height=32, state=tk.DISABLED)
        self.undo_button.pack(side=tk.LEFT, padx=2)

        self.redo_button = ctk.CTkButton(toolbar, text="↪ " + ("Redo" if self.language == 'en' else "恢复"),
                                          command=self.redo, width=70, height=32, state=tk.DISABLED)
        self.redo_button.pack(side=tk.LEFT, padx=(2, 6))

        # Separator
        ctk.CTkFrame(toolbar, width=1, height=24, fg_color="gray50").pack(side=tk.LEFT, padx=4)

        # Group 3: File operations
        self.open_button = ctk.CTkButton(toolbar, text="📂 " + ("Open" if self.language == 'en' else "打开"),
                                          command=self.open_file, width=70, height=32)
        self.open_button.pack(side=tk.LEFT, padx=2)

        self.save_button = ctk.CTkButton(toolbar, text="� " + ("Save" if self.language == 'en' else "保存"),
                                          command=self.save_file, width=70, height=32)
        self.save_button.pack(side=tk.LEFT, padx=2)

        self.example_button = ctk.CTkButton(toolbar, text="� " + ("Example" if self.language == 'en' else "示例"),
                                             command=self.load_example, width=80, height=32)
        self.example_button.pack(side=tk.LEFT, padx=2)

        # Right side: secondary actions + font controls
        # (packed from RIGHT, so order is reversed visually)
        self.update_btn = ctk.CTkButton(toolbar, text="⟳ " + ("Update" if self.language == 'en' else "更新"),
                                         command=self.manual_update_check, width=72, height=28)
        self.update_btn.pack(side=tk.RIGHT, padx=2)

        self.help_button = ctk.CTkButton(toolbar, text="? " + ("Help" if self.language == 'en' else "帮助"),
                                          command=self.show_help, width=62, height=28)
        self.help_button.pack(side=tk.RIGHT, padx=2)

        self.shortcut_button = ctk.CTkButton(toolbar, text="⚙ " + ("Settings" if self.language == 'en' else "设置"),
                                              command=self.open_shortcut_config, width=76, height=28)
        self.shortcut_button.pack(side=tk.RIGHT, padx=2)

        self.lang_button = ctk.CTkButton(toolbar, text="🌐 中文" if self.language == 'en' else "🌐 EN",
                                          command=self.toggle_language, width=62, height=28)
        self.lang_button.pack(side=tk.RIGHT, padx=2)

        # Separator before font controls
        ctk.CTkFrame(toolbar, width=1, height=24, fg_color="gray50").pack(side=tk.RIGHT, padx=4)

        self.font_size_label = ctk.CTkLabel(toolbar, text=f"{self.font_size}", width=22,
                                             font=ctk.CTkFont(size=11))
        self.font_size_label.pack(side=tk.RIGHT, padx=1)

        self.font_minus_btn = ctk.CTkButton(toolbar, text="A−", command=self.decrease_font,
                                             width=28, height=28, font=ctk.CTkFont(size=11))
        self.font_minus_btn.pack(side=tk.RIGHT, padx=1)

        self.font_plus_btn = ctk.CTkButton(toolbar, text="A+", command=self.increase_font,
                                            width=28, height=28, font=ctk.CTkFont(size=11))
        self.font_plus_btn.pack(side=tk.RIGHT, padx=1)

        # ========== Main Content: CTkTabview ==========
        self.tabview = ctk.CTkTabview(main_frame, height=400, command=self._on_tab_changed)
        self.tabview.grid(row=1, column=0, sticky="nsew")

        # Tab: Editor (input + output side by side)
        editor_tab_name = "Editor" if self.language == 'en' else "编辑器"
        self._editor_tab_name = editor_tab_name
        self.tabview.add(editor_tab_name)
        editor_tab = self.tabview.tab(editor_tab_name)
        editor_tab.grid_columnconfigure(0, weight=1)
        editor_tab.grid_columnconfigure(1, weight=1)
        editor_tab.grid_rowconfigure(2, weight=1)

        # ===== Session Tab Bar (within Editor tab) =====
        self._session_tab_frame = ctk.CTkFrame(editor_tab, height=32, fg_color="transparent")
        self._session_tab_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 2))
        self._session_tab_buttons = {}  # session_id -> button widget

        self.input_label = ctk.CTkLabel(editor_tab, text="Input:" if self.language == 'en' else "输入:",
                                         font=ctk.CTkFont(size=12, weight="bold"))
        self.input_label.grid(row=1, column=0, sticky="w", padx=(4, 5), pady=(0, 2))

        self.output_label = ctk.CTkLabel(editor_tab, text="Output:" if self.language == 'en' else "输出:",
                                          font=ctk.CTkFont(size=12, weight="bold"))
        self.output_label.grid(row=1, column=1, sticky="w", padx=(5, 4), pady=(0, 2))

        # Input text area
        input_container = ctk.CTkFrame(editor_tab, corner_radius=8)
        input_container.grid(row=2, column=0, sticky="nsew", padx=(4, 4))
        input_container.grid_rowconfigure(0, weight=1)
        input_container.grid_columnconfigure(0, weight=1)

        self.input_text = tk.Text(input_container, wrap=tk.WORD, font=("Consolas", self.font_size),
                                   undo=True, relief=tk.FLAT, padx=8, pady=8, bd=0, highlightthickness=0)
        input_sb = tk.Scrollbar(input_container, orient=tk.VERTICAL, command=self.input_text.yview)
        self.input_text.configure(yscrollcommand=input_sb.set)
        self.input_text.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        input_sb.grid(row=0, column=1, sticky="ns", pady=6)

        # Output text area
        output_container = ctk.CTkFrame(editor_tab, corner_radius=8)
        output_container.grid(row=2, column=1, sticky="nsew", padx=(4, 4))
        output_container.grid_rowconfigure(0, weight=1)
        output_container.grid_columnconfigure(0, weight=1)

        self.output_text = tk.Text(output_container, wrap=tk.WORD, font=("Consolas", self.font_size),
                                    state=tk.DISABLED, relief=tk.FLAT, padx=8, pady=8, bd=0, highlightthickness=0)
        output_sb = tk.Scrollbar(output_container, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=output_sb.set)
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        output_sb.grid(row=0, column=1, sticky="ns", pady=6)

        # Tab: Variables (shows defined variables)
        vars_tab_name = "Variables" if self.language == 'en' else "变量"
        self.tabview.add(vars_tab_name)
        vars_tab = self.tabview.tab(vars_tab_name)
        vars_tab.grid_rowconfigure(0, weight=1)
        vars_tab.grid_columnconfigure(0, weight=1)

        self.vars_text = tk.Text(vars_tab, wrap=tk.WORD, font=("Consolas", self.font_size),
                                  state=tk.DISABLED, relief=tk.FLAT, padx=12, pady=12, bd=0, highlightthickness=0)
        self.vars_text.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        # Tab: Functions (shows defined functions)
        funcs_tab_name = "Functions" if self.language == 'en' else "函数"
        self.tabview.add(funcs_tab_name)
        funcs_tab = self.tabview.tab(funcs_tab_name)
        funcs_tab.grid_rowconfigure(0, weight=1)
        funcs_tab.grid_columnconfigure(0, weight=1)

        self.funcs_text = tk.Text(funcs_tab, wrap=tk.WORD, font=("Consolas", self.font_size),
                                   state=tk.DISABLED, relief=tk.FLAT, padx=12, pady=12, bd=0, highlightthickness=0)
        self.funcs_text.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        # Tab: History (shows calculation history)
        hist_tab_name = "History" if self.language == 'en' else "历史"
        self.tabview.add(hist_tab_name)
        hist_tab = self.tabview.tab(hist_tab_name)
        hist_tab.grid_rowconfigure(0, weight=1)
        hist_tab.grid_columnconfigure(0, weight=1)

        self.history_text = tk.Text(hist_tab, wrap=tk.WORD, font=("Consolas", self.font_size),
                                     state=tk.DISABLED, relief=tk.FLAT, padx=12, pady=12, bd=0, highlightthickness=0)
        self.history_text.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        # Apply theme colors to text areas
        self._apply_text_theme()

        # ========== Status Bar (toast-style) ==========
        self.status_var = tk.StringVar(value="Ready" if self.language == 'en' else "就绪")
        self._status_frame = ctk.CTkFrame(main_frame, corner_radius=6, height=28)
        self._status_frame.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        self._status_frame.grid_propagate(False)
        self._status_frame.grid_columnconfigure(0, weight=1)

        self._status_label = ctk.CTkLabel(self._status_frame, textvariable=self.status_var,
                                           anchor=tk.W, font=ctk.CTkFont(size=11), padx=10)
        self._status_label.grid(row=0, column=0, sticky="ew", pady=2)

    # ==================== Shortcuts ====================

    def bind_shortcuts(self):
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
        calc_keys = set()
        for action_name, key_str in sc.items():
            if key_str and action_name in actions:
                try:
                    self.root.bind(key_str, actions[action_name])
                    self._bound_keys.append(key_str)
                    if action_name in ('calculate', 'calculate_alt'):
                        calc_keys.add(key_str)
                    if 'Control-' in key_str and len(key_str.split('-')[-1].rstrip('>')) == 1:
                        upper_key = key_str[:-2] + key_str[-2].upper() + key_str[-1]
                        if upper_key != key_str:
                            self.root.bind(upper_key, actions[action_name])
                            self._bound_keys.append(upper_key)
                            if action_name in ('calculate', 'calculate_alt'):
                                calc_keys.add(upper_key)
                except Exception:
                    pass

        def _calc_and_break(e):
            self.calculate()
            return "break"
        for key_str in calc_keys:
            try:
                self.input_text.bind(key_str, _calc_and_break)
            except Exception:
                pass

    def _unbind_all_shortcuts(self):
        if hasattr(self, '_bound_keys'):
            for key in self._bound_keys:
                try:
                    self.root.unbind(key)
                except Exception:
                    pass
        self._bound_keys = []

    def open_shortcut_config(self):
        """Open settings dialog (shortcuts + data directory + appearance)"""
        if self._has_active_dialog():
            return
        dialog = ctk.CTkToplevel(self.root)
        title = "Settings" if self.language == 'en' else "设置"
        dialog.title(title)
        dialog.geometry("580x520")
        dialog.transient(self.root)
        dialog.grab_set()
        self._active_dialog = dialog

        names = SHORTCUT_NAMES_EN if self.language == 'en' else SHORTCUT_NAMES_ZH

        # Scrollable content
        scroll = ctk.CTkScrollableFrame(dialog)
        scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ===== Appearance Mode =====
        appear_label = ctk.CTkLabel(scroll, text="Appearance" if self.language == 'en' else "外观模式",
                                     font=ctk.CTkFont(size=13, weight="bold"))
        appear_label.pack(anchor="w", pady=(0, 4))

        appear_hint = "System = follow OS setting" if self.language == 'en' else "System = 跟随系统设置"
        ctk.CTkLabel(scroll, text=appear_hint, text_color="gray").pack(anchor="w", pady=(0, 4))

        appear_var = tk.StringVar(value=self.appearance_mode)
        appear_menu = ctk.CTkSegmentedButton(scroll, values=["system", "light", "dark"], variable=appear_var,
                                              command=lambda val: self._preview_appearance(val))
        appear_menu.pack(anchor="w", pady=(0, 12))

        # ===== Data Directory =====
        dir_label = ctk.CTkLabel(scroll, text="Data Directory" if self.language == 'en' else "数据目录",
                                  font=ctk.CTkFont(size=13, weight="bold"))
        dir_label.pack(anchor="w", pady=(0, 4))

        dir_hint = "Config and session files location. Change requires restart." if self.language == 'en' \
            else "配置和会话文件存储位置，修改后需重启生效。"
        ctk.CTkLabel(scroll, text=dir_hint, text_color="gray").pack(anchor="w", pady=(0, 4))

        dir_row = ctk.CTkFrame(scroll, fg_color="transparent")
        dir_row.pack(fill=tk.X, pady=(0, 12))
        dir_entry = ctk.CTkEntry(dir_row, font=ctk.CTkFont(family="Consolas", size=11), width=400)
        dir_entry.insert(0, self.data_dir)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        def browse_dir():
            d = filedialog.askdirectory(initialdir=self.data_dir)
            if d:
                dir_entry.delete(0, tk.END)
                dir_entry.insert(0, d)

        ctk.CTkButton(dir_row, text="📂", command=browse_dir, width=32).pack(side=tk.LEFT)

        # ===== Shortcuts =====
        key_label = ctk.CTkLabel(scroll, text="Keyboard Shortcuts" if self.language == 'en' else "快捷键",
                                  font=ctk.CTkFont(size=13, weight="bold"))
        key_label.pack(anchor="w", pady=(0, 4))

        hint = "Click a field, then press the new key combination." if self.language == 'en' \
            else "点击输入框，然后按下新的快捷键组合。"
        ctk.CTkLabel(scroll, text=hint, text_color="gray").pack(anchor="w", pady=(0, 6))

        entries = {}
        for action_name in DEFAULT_SHORTCUTS:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill=tk.X, pady=2)

            display_name = names.get(action_name, action_name)
            ctk.CTkLabel(row, text=display_name, width=140, anchor="w").pack(side=tk.LEFT, padx=5)

            entry = ctk.CTkEntry(row, width=200, font=ctk.CTkFont(family="Consolas", size=11))
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
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)

        def apply_settings():
            # Appearance
            new_mode = appear_var.get()
            if new_mode != self.appearance_mode:
                self.appearance_mode = new_mode
                ctk.set_appearance_mode(new_mode)
                self._apply_text_theme()
            # Data directory
            new_dir = dir_entry.get().strip()
            if new_dir and new_dir != self.data_dir:
                if os.path.isdir(new_dir) or not os.path.exists(new_dir):
                    old_dir = self.data_dir
                    self.data_dir = new_dir
                    os.makedirs(self.data_dir, exist_ok=True)
                    self.config_file = os.path.join(self.data_dir, 'calcpaper_config.json')
                    self.session_file = os.path.join(self.data_dir, 'calcpaper_session.json')
                    # Migrate files from old directory
                    import shutil
                    for fname in ('calcpaper_config.json', 'calcpaper_session.json'):
                        src = os.path.join(old_dir, fname)
                        dst = os.path.join(self.data_dir, fname)
                        if os.path.exists(src) and not os.path.exists(dst):
                            try:
                                shutil.copy2(src, dst)
                            except Exception:
                                pass
                else:
                    messagebox.showwarning("Warning", "Invalid directory path")
                    return
            # Shortcuts
            for action_name, entry in entries.items():
                self.shortcuts[action_name] = entry.get().strip()
            self.bind_shortcuts()
            self.update_button_texts()
            self.save_config()
            self.status_var.set("Settings saved" if self.language == 'en' else "设置已保存")
            dialog.destroy()
            self._active_dialog = None

        def reset_all():
            for action_name, entry in entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, DEFAULT_SHORTCUTS.get(action_name, ''))
            appear_var.set("system")

        def _close():
            dialog.destroy()
            self._active_dialog = None

        ctk.CTkButton(btn_frame, text="Save" if self.language == 'en' else "保存",
                       command=apply_settings, fg_color="#4CAF50", hover_color="#388E3C", width=90).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="Reset" if self.language == 'en' else "恢复默认",
                       command=reset_all, width=90).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="Cancel" if self.language == 'en' else "取消",
                       command=_close, width=90).pack(side=tk.LEFT, padx=5)

        dialog.protocol("WM_DELETE_WINDOW", _close)


    # ==================== Calculation ====================

    def calculate(self):
        self._switch_to_editor()
        try:
            input_content = self.input_text.get("1.0", tk.END).strip()
            if not input_content:
                self.status_var.set("Please enter calculation content" if self.language == 'en' else "请输入计算内容")
                return

            # Use the current session's calculator
            self.calculator = CalculatorPaperAdvanced(language=self.language)

            # Pass global variables as preset (lower priority than local assignments)
            global_vars = self.global_store.get_all()
            global_funcs = self.global_store.get_all_functions()
            self.calculator.process_text(input_content, preset_variables=global_vars, preset_functions=global_funcs)
            output = self.calculator.format_output()

            # Check for global() function calls and update global store
            self._process_global_declarations(input_content)

            self.output_text.configure(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", output)
            self.apply_syntax_highlighting()
            self.output_text.configure(state=tk.DISABLED)

            self.status_var.set("Calculation completed" if self.language == 'en' else "计算完成")
            self.save_gui_state(input_content, output)
            self.last_saved_input = input_content
            self.update_undo_redo_buttons()

            # Update current session's calculator reference
            if self._current_session_id:
                try:
                    session = self.session_manager.get_session(self._current_session_id)
                    session.calculator = self.calculator
                    session.variables = dict(self.calculator.variables)
                except KeyError:
                    pass

            self._refresh_variables_tab()
            self._refresh_functions_tab()
            self._refresh_history_tab()

        except Exception as e:
            title = "Error" if self.language == 'en' else "错误"
            messagebox.showerror(title, str(e))
            self.status_var.set(f"Error: {e}" if self.language == 'en' else f"错误: {e}")

    def _process_global_declarations(self, input_content):
        """Process global() function calls and update the global variable store."""
        import re
        # Match global(variable_name) calls
        pattern = re.compile(r'\bglobal\s*\(\s*([a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*)\s*\)')
        matches = pattern.findall(input_content)
        for var_name in matches:
            if var_name in self.calculator.variables:
                self.global_store.set(var_name, self.calculator.variables[var_name])
            elif var_name in self.calculator.functions:
                params, body = self.calculator.functions[var_name]
                self.global_store.set_function(var_name, params, body)

    def apply_syntax_highlighting(self):
        for tag in self.output_text.tag_names():
            self.output_text.tag_remove(tag, "1.0", tk.END)

        mode = ctk.get_appearance_mode()
        if mode == "Dark":
            self.output_text.tag_config("comment", foreground="#6A9955")
            self.output_text.tag_config("result", foreground="#4EC9B0", font=("Consolas", self.font_size, "bold"))
            self.output_text.tag_config("error", foreground="#F44747")
            self.output_text.tag_config("total", foreground="#569CD6", font=("Consolas", self.font_size, "bold"))
            self.output_text.tag_config("endian", foreground="#C586C0", font=("Consolas", self.font_size, "bold"))
            self.output_text.tag_config("bit_info", foreground="#9CDCFE", font=("Consolas", max(self.font_size - 1, 8)))
            self.output_text.tag_config("hex_result", foreground="#CE9178", font=("Consolas", self.font_size, "bold"))
        else:
            self.output_text.tag_config("comment", foreground="#008000")
            self.output_text.tag_config("result", foreground="#098658", font=("Consolas", self.font_size, "bold"))
            self.output_text.tag_config("error", foreground="#CD3131")
            self.output_text.tag_config("total", foreground="#0000FF", font=("Consolas", self.font_size, "bold"))
            self.output_text.tag_config("endian", foreground="#AF00DB", font=("Consolas", self.font_size, "bold"))
            self.output_text.tag_config("bit_info", foreground="#001080", font=("Consolas", max(self.font_size - 1, 8)))
            self.output_text.tag_config("hex_result", foreground="#A31515", font=("Consolas", self.font_size, "bold"))

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
        self._switch_to_editor()
        self.input_text.delete("1.0", tk.END)
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.configure(state=tk.DISABLED)
        self.save_gui_state("", "")
        self.last_saved_input = ""
        self.status_var.set("Cleared" if self.language == 'en' else "已清空")

    def load_example(self):
        self._switch_to_editor()
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

# comma: display with thousand separators
comma(1234567)
59,200 + 1,000

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

# comma: 千分位格式显示
comma(1234567)
59,200 + 1,000

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
        self.status_var.set("Example loaded" if self.language == 'en' else "已加载示例")

    def open_file(self):
        self._switch_to_editor()
        title = "Open File" if self.language == 'en' else "打开文件"
        filename = filedialog.askopenfilename(title=title, filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                content = self._strip_result_annotations(content)
                self.input_text.unbind('<<Modified>>')
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", content)
                self.save_gui_state(content, "")
                self.last_saved_input = content
                self.input_text.bind('<<Modified>>', self.on_input_modified)
                self.status_var.set(f"Opened: {os.path.basename(filename)}" if self.language == 'en' else f"已打开: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _strip_result_annotations(self, text):
        """Strip result annotations from output text to extract original input."""
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            stripped = line.strip()
            if stripped and line.startswith('  ') and any(stripped.startswith(kw) for kw in [
                '十六进制:', '二进制:', '位数:', '位索引',
                'Hexadecimal:', 'Binary:', 'Bits:', 'Bit indices',
                '|'
            ]):
                continue
            if not stripped or stripped.startswith('#'):
                cleaned.append(line)
                continue
            if '=' in stripped:
                first_eq = stripped.index('=')
                left = stripped[:first_eq].strip()
                right_part = stripped[first_eq+1:].strip()
                is_assignment = bool(re.match(r'^[a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*$', left))
                if is_assignment:
                    match = re.match(r'^(.+?)\s{2,}=\s', right_part)
                    if match:
                        original_expr = match.group(1).strip()
                        cleaned.append(f"{left} = {original_expr}")
                    else:
                        cleaned.append(stripped)
                else:
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
                self.status_var.set(f"Saved: {os.path.basename(filename)}" if self.language == 'en' else f"已保存: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ==================== Undo/Redo ====================

    def save_gui_state(self, input_text, output_text):
        if self._current_session_id is None:
            return
        try:
            session = self.session_manager.get_session(self._current_session_id)
        except KeyError:
            return
        if session.gui_history_index < len(session.gui_history) - 1:
            session.gui_history = session.gui_history[:session.gui_history_index + 1]
        session.gui_history.append((input_text, output_text))
        session.gui_history_index = len(session.gui_history) - 1
        if len(session.gui_history) > 50:
            session.gui_history.pop(0)
            session.gui_history_index -= 1
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
        self._switch_to_editor()
        if self._current_session_id is None:
            return
        try:
            session = self.session_manager.get_session(self._current_session_id)
        except KeyError:
            return
        if session.gui_history_index > 0:
            session.gui_history_index -= 1
            inp, out = session.gui_history[session.gui_history_index]
            self.input_text.unbind('<<Modified>>')
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", inp)
            self.last_saved_input = inp
            self.output_text.configure(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", out)
            self.apply_syntax_highlighting()
            self.output_text.configure(state=tk.DISABLED)
            self.input_text.bind('<<Modified>>', self.on_input_modified)
            self._toast("Undo" if self.language == 'en' else "撤销完成")
            self.update_undo_redo_buttons()
            self._refresh_history_tab()

    def redo(self):
        self._switch_to_editor()
        if self._current_session_id is None:
            return
        try:
            session = self.session_manager.get_session(self._current_session_id)
        except KeyError:
            return
        if session.gui_history_index < len(session.gui_history) - 1:
            session.gui_history_index += 1
            inp, out = session.gui_history[session.gui_history_index]
            self.input_text.unbind('<<Modified>>')
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", inp)
            self.last_saved_input = inp
            self.output_text.configure(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", out)
            self.apply_syntax_highlighting()
            self.output_text.configure(state=tk.DISABLED)
            self.input_text.bind('<<Modified>>', self.on_input_modified)
            self._toast("Redo" if self.language == 'en' else "恢复完成")
            self.update_undo_redo_buttons()
            self._refresh_history_tab()

    def update_undo_redo_buttons(self):
        can_undo = False
        can_redo = False
        if self._current_session_id is not None:
            try:
                session = self.session_manager.get_session(self._current_session_id)
                can_undo = session.gui_history_index > 0
                can_redo = session.gui_history_index < len(session.gui_history) - 1
            except KeyError:
                pass
        if hasattr(self, 'undo_button'):
            self.undo_button.configure(state=tk.NORMAL if can_undo else tk.DISABLED)
        if hasattr(self, 'redo_button'):
            self.redo_button.configure(state=tk.NORMAL if can_redo else tk.DISABLED)

    # ==================== Autocomplete ====================

    def _get_defined_variables(self):
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

    def _get_defined_functions(self):
        """Get all user-defined function names from input text and global store."""
        content = self.input_text.get("1.0", "end-1c")
        functions = []
        # Match function definitions: func(x, y) = expr
        pattern = re.compile(r'^([a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*)\s*\([^)]+\)\s*=', re.MULTILINE)
        for match in pattern.finditer(content):
            name = match.group(1)
            if name.lower() not in ('swap', 'bitmap', 'hex', 'comma', 'global', 'workday'):
                if name not in functions:
                    functions.append(name)
        # Add global functions
        if hasattr(self, 'global_store'):
            for fname in self.global_store.get_all_functions():
                if fname not in functions:
                    functions.append(fname)
        # Add built-in function names
        builtins = ['swap', 'bitmap', 'hex', 'comma', 'global', 'workday']
        for b in builtins:
            if b not in functions:
                functions.append(b)
        return functions

    def _get_current_prefix(self):
        try:
            cursor_pos = self.input_text.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            col = int(col)
            line_text = self.input_text.get(f"{line}.0", f"{line}.{col}")
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
        return None

    def _on_keyrelease_for_autocomplete(self, event):
        keysym = event.keysym
        if keysym in ('Escape', 'Up', 'Down', 'Tab', 'Return',
                       'Shift_L', 'Shift_R', 'Control_L', 'Control_R',
                       'Alt_L', 'Alt_R', 'Caps_Lock'):
            return
        self._update_autocomplete()

    def _update_autocomplete(self):
        prefix, prefix_start = self._get_current_prefix()
        if not prefix or len(prefix) < 1:
            self.autocomplete.hide()
            return
        variables = self._get_defined_variables()
        functions = self._get_defined_functions()
        # Combine: functions shown with () suffix for clarity
        all_candidates = []
        prefix_lower = prefix.lower()
        for v in variables:
            if v.lower().startswith(prefix_lower) and v != prefix:
                all_candidates.append(v)
        for f in functions:
            if f.lower().startswith(prefix_lower) and f != prefix:
                display = f + "()"
                if display not in all_candidates and f not in all_candidates:
                    all_candidates.append(display)
        if all_candidates:
            try:
                bbox = self.input_text.bbox(tk.INSERT)
                if bbox:
                    x = self.input_text.winfo_rootx() + bbox[0]
                    y = self.input_text.winfo_rooty() + bbox[1] + bbox[3]
                    self.autocomplete.show(all_candidates, x, y)
                else:
                    self.autocomplete.hide()
            except Exception:
                self.autocomplete.hide()
        else:
            self.autocomplete.hide()

    def _insert_completion(self, variable_name, prefix_start):
        cursor_pos = self.input_text.index(tk.INSERT)
        self.input_text.delete(prefix_start, cursor_pos)
        # If completing a function (ends with "()"), insert and place cursor between parens
        if variable_name.endswith("()"):
            func_name = variable_name[:-2]
            self.input_text.insert(prefix_start, func_name + "()")
            # Move cursor between the parentheses
            insert_pos = self.input_text.index(f"{prefix_start} + {len(func_name) + 1} chars")
            self.input_text.mark_set(tk.INSERT, insert_pos)
        else:
            self.input_text.insert(prefix_start, variable_name)
        self.autocomplete.hide()


    # ==================== Help (GanttPilot style with clickable links) ====================

    def show_help(self):
        """Show help dialog with clickable project links."""
        if self._has_active_dialog():
            return
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Help" if self.language == 'en' else "帮助")
        dialog.geometry("720x580")
        dialog.transient(self.root)
        self._active_dialog = dialog

        # Use tk.Text for rich text display (tags for coloring)
        text_frame = ctk.CTkFrame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10), state=tk.NORMAL,
                       bg="#1e1e1e", fg="#dcdcdc", relief=tk.FLAT, padx=10, pady=10)
        sb = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=sb.set)
        text.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")

        if self.language == 'en':
            content = self._help_text_en()
        else:
            content = self._help_text_zh()

        text.insert("1.0", content)
        text.configure(state=tk.DISABLED)

        # Bottom: clickable links + close button
        bottom = ctk.CTkFrame(dialog, fg_color="transparent")
        bottom.pack(fill=tk.X, padx=10, pady=(0, 10))

        github_url = f"https://github.com/{GITHUB_REPO}"
        link1 = ctk.CTkLabel(bottom, text=f"📦 GitHub: {GITHUB_REPO}", text_color="#3B8ED0", cursor="hand2")
        link1.pack(side=tk.LEFT, padx=(0, 16))
        link1.bind("<Button-1>", lambda e: webbrowser.open(github_url))

        gantt_url = "https://github.com/matthewzu/GanttPilot"
        link2 = ctk.CTkLabel(bottom, text="📊 GanttPilot", text_color="#3B8ED0", cursor="hand2")
        link2.pack(side=tk.LEFT, padx=(0, 16))
        link2.bind("<Button-1>", lambda e: webbrowser.open(gantt_url))

        def _close():
            dialog.destroy()
            self._active_dialog = None

        ctk.CTkButton(bottom, text="OK", command=_close, width=80).pack(side=tk.RIGHT)
        dialog.protocol("WM_DELETE_WINDOW", _close)

    def _help_text_en(self):
        return f"""CalcPaper v{VERSION} - Smart Calculator for Programmers

=== Basic Operations ===
  +, -, *, /, ()          Arithmetic
  variable = expression   Variable assignment
  6.5%, 10%               Percentage
  # comment               Comment line

=== Forward References ===
  Variables can be used before they are defined:
    total = price * qty   (price and qty defined below)
    price = 50
    qty = 20              total = 1000
  Circular dependencies are detected and reported as errors.

=== Number Formats ===
  0xFF, 0x1A2B            Hexadecimal
  0b1010, 0b11110000      Binary
  255                     Decimal
  59,200                  Comma-separated (auto-converted to 59200)

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
  comma(value)            Display with comma separators (e.g. 59,200)
  global(name)            Declare variable/function shared across all tabs

=== User-Defined Functions ===
  name(params) = expr     Define a function
  name(args)              Call a function
  global(func_name)       Share function across all tabs

  Examples:
    func(x, y) = 3*x + 5*y     Define with explicit multiplication
    f(x) = 3x + 1              Implicit multiplication (3x = 3*x)
    double(x) = 2*x            Single parameter
    quad(x) = double(double(x)) Nested function calls
    result = func(2, 3)        Assign function result to variable
    global(double)              Share double() across all tabs

=== Date/Time Arithmetic ===
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

=== workday() Working Day Calculation ===
  workday(start, days)              Count working days (skip weekends)
  workday(start, days, holidays)    With custom holidays

  Holiday format (separated by /):
    Y20260501                       Add as holiday
    -Y20260412                      Remove from holidays (make workday)
    Y20260501/-Y20260412            Combined

=== Reserved Keywords ===
  Y, T, M, W, D (uppercase) and h, m, s (lowercase) followed by
  digits are reserved and cannot be used as variable names.

=== Keyboard Shortcuts ===
  Ctrl+Enter    Calculate
  F5            Calculate (alt)
  Ctrl+D        Clear
  Ctrl+Z        Undo
  Ctrl+Y        Redo
  Ctrl+T        New tab
  Ctrl+W        Close tab
  Ctrl+Tab      Switch tab
  Ctrl+L        Load example
  Ctrl+O        Open file
  Ctrl+S        Save result
  Ctrl+=/+      Font increase
  Ctrl+-        Font decrease
  F1            Help
  Tab           Autocomplete confirm

=== Multi-Session Tabs ===
  - Each tab has its own independent variables and calculator
  - Double-click tab name to rename
  - Drag tabs to reorder
  - global(var_name) declares a variable shared across all tabs
  - global(func_name) declares a function shared across all tabs
  - Variables tab shows current tab name and distinguishes local/global vars
  - Functions tab shows local, global, and built-in functions
  - History tab shows only the current tab's calculation history

=== Auto Output Format ===
  - Expression with 0x literal -> result in hex (e.g. 0xFF + 1 = 0x100)
  - Expression with 0b literal -> result in binary (e.g. 0b1010 + 1 = 0b1011)
  - Both hex and binary -> hex takes priority
  - Explicit hex() function always takes priority

=== Autocomplete ===
  Type a variable or function name prefix -> popup appears
  Functions shown with () suffix, cursor placed between parens on select
  Tab           Confirm selection
  Up/Down       Navigate candidates
  Escape        Dismiss popup

=== Tips ===
  - Results are auto-saved and restored on next launch
  - Window size, position, language, font are remembered
  - All shortcuts are customizable via Settings (gear icon)
  - Update check runs in background; click "Update" button to check manually
  - Supports Light/Dark/System appearance modes (Settings)
  - Data directory defaults to ~/.calcpaper, changeable in Settings
  - Variables tab shows all defined variables after calculation
  - History tab shows colored diff of changes between calculations
"""

    def _help_text_zh(self):
        return f"""CalcPaper v{VERSION} - 程序员的智能计算稿纸

=== 基本运算 ===
  +, -, *, /, ()          四则运算
  变量名 = 表达式          变量赋值
  6.5%, 10%               百分数
  # 注释                   注释行

=== 前向引用 ===
  变量可以在定义之前使用：
    总价 = 单价 * 数量     （单价和数量在下面定义）
    单价 = 50
    数量 = 20              总价 = 1000
  循环依赖会被自动检测并报错。

=== 数值格式 ===
  0xFF, 0x1A2B            16进制
  0b1010, 0b11110000      2进制
  255                     10进制
  59,200                  千分位格式（自动转换为 59200）

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
  comma(数值)             千分位格式显示（如 59,200）
  global(变量名)          声明跨标签页共享的全局变量
  global(函数名)          声明跨标签页共享的全局函数

=== 自定义函数 ===
  函数名(参数) = 表达式    定义函数
  函数名(参数值)           调用函数
  global(函数名)           共享函数到所有标签页

  示例：
    func(x, y) = 3*x + 5*y     显式乘法定义
    f(x) = 3x + 1              隐式乘法（3x = 3*x）
    double(x) = 2*x            单参数函数
    quad(x) = double(double(x)) 嵌套函数调用
    result = func(2, 3)        函数结果赋值给变量

=== 日期/时间运算 ===
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

=== workday() 工作日计算 ===
  workday(起始日期, 天数)           计算工作日（自动跳过周末）
  workday(起始日期, 天数, 节假日)   自定义节假日

  节假日格式（用 / 分隔）：
    Y20260501                       添加为节假日
    -Y20260412                      移除节假日（变为工作日）
    Y20260501/-Y20260412            组合使用

=== 保留关键字 ===
  Y、T、M、W、D（大写）和 h、m、s（小写）后跟数字
  为保留关键字，不可用作变量名。

=== 快捷键 ===
  Ctrl+Enter    计算
  F5            计算（备选）
  Ctrl+D        清空
  Ctrl+Z        撤销
  Ctrl+Y        恢复
  Ctrl+T        新建标签
  Ctrl+W        关闭标签
  Ctrl+Tab      切换标签
  Ctrl+L        加载示例
  Ctrl+O        打开文件
  Ctrl+S        保存结果
  Ctrl+=/+      放大字体
  Ctrl+-        缩小字体
  F1            帮助
  Tab           自动补全确认

=== 多会话标签页 ===
  - 每个标签页拥有独立的变量和计算引擎
  - 双击标签名可重命名
  - 拖动标签可改变顺序
  - global(变量名) 声明跨标签页共享的全局变量
  - global(函数名) 声明跨标签页共享的全局函数
  - 变量面板显示当前标签名，区分局部/全局变量
  - 函数面板显示局部、全局和内置函数
  - 历史面板仅显示当前标签的修改记录

=== 自动输出格式 ===
  - 表达式含 0x 字面量 → 结果以十六进制输出（如 0xFF + 1 = 0x100）
  - 表达式含 0b 字面量 → 结果以二进制输出（如 0b1010 + 1 = 0b1011）
  - 同时含两者 → 十六进制优先
  - 显式 hex() 函数始终优先

=== 自动补全 ===
  输入已定义的变量名或函数名前缀 -> 弹出候选列表
  函数名带 () 后缀，选中后光标定位到括号内
  Tab           确认选择
  上/下方向键    导航候选项
  Escape        关闭弹窗

=== 提示 ===
  - 计算结果自动保存，下次启动自动恢复
  - 窗口大小、位置、语言、字体会被记住
  - 所有快捷键可通过设置按钮（齿轮图标）自定义
  - 启动时后台自动检查更新，点击"更新"按钮可手动检查
  - 支持浅色/深色/跟随系统外观模式（在设置中切换）
  - 数据目录默认为 ~/.calcpaper，可在设置中修改
  - 变量面板显示当前标签页的所有已定义变量
  - 历史面板以彩色 diff 显示当前标签的计算变更
  - 计算历史以 Git 仓库持久化（需安装 Git）
"""


def main():
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = CalculatorGUIAdvanced(root)
    root.mainloop()


if __name__ == "__main__":
    main()
