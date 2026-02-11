#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算稿纸 - 高级版GUI
支持16进制、2进制、位运算和字节序显示
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import re
from calc_paper import CalculatorPaperAdvanced

VERSION = "1.0"

class CalculatorGUIAdvanced:
    def __init__(self, root):
        self.root = root
        self.language = 'en'  # 默认英文，'zh' 或 'en'
        self.font_size = 10  # 默认字体大小
        self.min_font_size = 8  # 最小字体大小
        self.max_font_size = 32  # 最大字体大小（不再限制）
        self.update_title()
        self.root.geometry("1200x800")

        # 创建计算器实例
        self.calculator = CalculatorPaperAdvanced(language=self.language)

        # 创建界面
        self.create_widgets()

        # 绑定快捷键
        self.bind_shortcuts()

        # 绑定窗口大小变化事件
        self.root.bind('<Configure>', self.on_window_configure)

    def on_window_configure(self, event):
        """窗口大小变化时的处理"""
        # 只处理主窗口的配置变化
        if event.widget == self.root:
            # 检查按钮是否需要滚动
            self.root.after_idle(self.check_button_scroll_needed)

    def update_title(self):
        """更新标题栏"""
        if self.language == 'en':
            self.root.title(f"CalcPaper - Advanced v{VERSION}")
        else:
            self.root.title(f"计算稿纸 - 高级版 v{VERSION}")

    def toggle_language(self):
        """切换语言"""
        self.language = 'zh' if self.language == 'en' else 'en'
        self.calculator.set_language(self.language)
        self.update_title()

        # 更新按钮文本
        self.update_button_texts()

    def update_button_texts(self):
        """更新按钮文本"""
        if hasattr(self, 'calc_button'):
            calc_text = "Calculate (F5)" if self.language == 'en' else "计算 (F5)"
            self.calc_button.config(text=calc_text)

        if hasattr(self, 'clear_button'):
            clear_text = "Clear (Ctrl+D)" if self.language == 'en' else "清空 (Ctrl+D)"
            self.clear_button.config(text=clear_text)

        if hasattr(self, 'example_button'):
            example_text = "Load Example (Ctrl+L)" if self.language == 'en' else "加载示例 (Ctrl+L)"
            self.example_button.config(text=example_text)

        if hasattr(self, 'open_button'):
            open_text = "Open File (Ctrl+O)" if self.language == 'en' else "打开文件 (Ctrl+O)"
            self.open_button.config(text=open_text)

        if hasattr(self, 'save_button'):
            save_text = "Save Result (Ctrl+S)" if self.language == 'en' else "保存结果 (Ctrl+S)"
            self.save_button.config(text=save_text)

        if hasattr(self, 'lang_button'):
            lang_text = "中文" if self.language == 'en' else "EN"
            self.lang_button.config(text=lang_text)

        # 更新标签文本
        if hasattr(self, 'input_text') and hasattr(self, 'output_text'):
            # 这里可以更新输入输出区域的标签，但由于我们没有保存标签引用，暂时跳过
            pass

        # 更新状态栏
        self.update_initial_font_display()

    def increase_font(self):
        """放大字体"""
        if self.font_size < self.max_font_size:
            old_size = self.font_size
            self.font_size = min(self.font_size + 2, self.max_font_size)
            self.update_fonts()

            # 只在字体真正改变时显示状态
            if old_size != self.font_size:
                status_text = f"Font increased to {self.font_size}" if self.language == 'en' else f"字体增大到 {self.font_size}"
                self.status_bar.config(text=status_text)
                # 3秒后恢复正常状态显示
                self.root.after(3000, self.restore_normal_status)
        else:
            # 显示提示信息
            status_text = f"Maximum font size ({self.max_font_size})" if self.language == 'en' else f"最大字体大小 ({self.max_font_size})"
            self.status_bar.config(text=status_text)
            # 3秒后恢复正常状态显示
            self.root.after(3000, self.restore_normal_status)

    def decrease_font(self):
        """缩小字体"""
        if self.font_size > self.min_font_size:
            old_size = self.font_size
            self.font_size = max(self.font_size - 2, self.min_font_size)
            self.update_fonts()

            # 只在字体真正改变时显示状态
            if old_size != self.font_size:
                status_text = f"Font decreased to {self.font_size}" if self.language == 'en' else f"字体缩小到 {self.font_size}"
                self.status_bar.config(text=status_text)
                # 3秒后恢复正常状态显示
                self.root.after(3000, self.restore_normal_status)
        else:
            # 显示提示信息
            status_text = f"Minimum font size ({self.min_font_size})" if self.language == 'en' else f"最小字体大小 ({self.min_font_size})"
            self.status_bar.config(text=status_text)
            # 3秒后恢复正常状态显示
            self.root.after(3000, self.restore_normal_status)

    def restore_normal_status(self):
        """恢复正常状态显示"""
        status_text = "Ready" if self.language == 'en' else "就绪"
        self.status_bar.config(text=status_text)

    def update_initial_font_display(self):
        """初始化字体大小显示"""
        if hasattr(self, 'font_size_label'):
            self.font_size_label.config(text=f"{self.font_size}")

        # 只在初始化时显示字体信息，之后保持简洁的状态
        status_text = "Ready" if self.language == 'en' else "就绪"
        self.status_bar.config(text=status_text)

    def update_fonts(self):
        """更新字体大小"""
        self.input_text.config(font=("Consolas", self.font_size))
        self.output_text.config(font=("Consolas", self.font_size))

        # 更新字体大小显示
        if hasattr(self, 'font_size_label'):
            self.font_size_label.config(text=f"{self.font_size}")

        # 不在这里更新状态栏，避免重复显示

    def create_widgets(self):
        """创建界面组件"""
        # 主框架 - 使用固定比例布局
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 配置行权重：输入输出区域占据大部分空间
        main_frame.grid_rowconfigure(0, weight=1)  # 输入输出区域
        main_frame.grid_rowconfigure(1, weight=0)  # 按钮栏（固定高度）
        main_frame.grid_rowconfigure(2, weight=0)  # 状态栏（固定高度）
        main_frame.grid_columnconfigure(0, weight=1)

        # ========== 输入输出区域 ==========
        io_frame = tk.Frame(main_frame)
        io_frame.grid(row=0, column=0, sticky="nsew")

        # 配置列权重：左右各占50%
        io_frame.grid_columnconfigure(0, weight=1)
        io_frame.grid_columnconfigure(1, weight=1)
        io_frame.grid_rowconfigure(0, weight=0)  # 标签行
        io_frame.grid_rowconfigure(1, weight=1)  # 文本框行

        # 左侧：输入区域
        input_text = "Input:" if self.language == 'en' else "输入区域："
        input_label = tk.Label(io_frame, text=input_text, font=("Arial", 10, "bold"))
        input_label.grid(row=0, column=0, sticky="w", padx=(0, 5))

        self.input_text = scrolledtext.ScrolledText(
            io_frame,
            wrap=tk.WORD,
            font=("Consolas", self.font_size)
        )
        self.input_text.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        # 右侧：输出区域
        output_text = "Output:" if self.language == 'en' else "输出区域："
        output_label = tk.Label(io_frame, text=output_text, font=("Arial", 10, "bold"))
        output_label.grid(row=0, column=1, sticky="w", padx=(5, 0))

        self.output_text = scrolledtext.ScrolledText(
            io_frame,
            wrap=tk.WORD,
            font=("Consolas", self.font_size),
            state=tk.DISABLED
        )
        self.output_text.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

        # 保存标签引用以便语言切换
        self.input_label = input_label
        self.output_label = output_label

        # ========== 按钮栏 ==========
        button_frame = tk.Frame(main_frame, height=60)
        button_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        button_frame.grid_propagate(False)  # 防止子组件改变框架大小

        # 创建内部滚动容器
        inner_frame = tk.Frame(button_frame)
        inner_frame.pack(fill=tk.BOTH, expand=True)

        # 创建画布和滚动条
        self.button_canvas = tk.Canvas(inner_frame, height=50, highlightthickness=0)
        self.button_scrollbar = tk.Scrollbar(inner_frame, orient="horizontal", command=self.button_canvas.xview)
        self.scrollable_frame = tk.Frame(self.button_canvas)

        # 配置滚动
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.button_canvas.configure(scrollregion=self.button_canvas.bbox("all"))
        )

        self.button_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.button_canvas.configure(xscrollcommand=self.button_scrollbar.set)

        # 先打包画布
        self.button_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 计算按钮
        calc_text = "Calculate (F5)" if self.language == 'en' else "计算 (F5)"
        self.calc_button = tk.Button(
            self.scrollable_frame,
            text=calc_text,
            command=self.calculate,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=3
        )
        self.calc_button.pack(side=tk.LEFT, padx=(0, 3))

        # 清空按钮
        clear_text = "Clear (Ctrl+D)" if self.language == 'en' else "清空 (Ctrl+D)"
        self.clear_button = tk.Button(
            self.scrollable_frame,
            text=clear_text,
            command=self.clear_all,
            bg="#f44336",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=3
        )
        self.clear_button.pack(side=tk.LEFT, padx=3)

        # 加载示例按钮
        example_text = "Load Example (Ctrl+L)" if self.language == 'en' else "加载示例 (Ctrl+L)"
        self.example_button = tk.Button(
            self.scrollable_frame,
            text=example_text,
            command=self.load_example,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=3
        )
        self.example_button.pack(side=tk.LEFT, padx=3)

        # 打开文件按钮
        open_text = "Open File (Ctrl+O)" if self.language == 'en' else "打开文件 (Ctrl+O)"
        self.open_button = tk.Button(
            self.scrollable_frame,
            text=open_text,
            command=self.open_file,
            font=("Arial", 10),
            padx=15,
            pady=3
        )
        self.open_button.pack(side=tk.LEFT, padx=3)

        # 保存文件按钮
        save_text = "Save Result (Ctrl+S)" if self.language == 'en' else "保存结果 (Ctrl+S)"
        self.save_button = tk.Button(
            self.scrollable_frame,
            text=save_text,
            command=self.save_file,
            font=("Arial", 10),
            padx=15,
            pady=3
        )
        self.save_button.pack(side=tk.LEFT, padx=3)

        # 中英文切换按钮
        lang_text = "中文" if self.language == 'en' else "EN"
        self.lang_button = tk.Button(
            self.scrollable_frame,
            text=lang_text,
            command=self.toggle_language,
            font=("Arial", 10),
            padx=12,
            pady=3,
            bg="#9C27B0",
            fg="white"
        )
        self.lang_button.pack(side=tk.LEFT, padx=3)

        # 字体放大按钮
        self.font_plus_button = tk.Button(
            self.scrollable_frame,
            text="A+",
            command=self.increase_font,
            font=("Arial", 10, "bold"),
            padx=8,
            pady=3,
            bg="#4CAF50",
            fg="white"
        )
        self.font_plus_button.pack(side=tk.LEFT, padx=3)

        # 字体缩小按钮
        self.font_minus_button = tk.Button(
            self.scrollable_frame,
            text="A-",
            command=self.decrease_font,
            font=("Arial", 10, "bold"),
            padx=8,
            pady=3,
            bg="#FF9800",
            fg="white"
        )
        self.font_minus_button.pack(side=tk.LEFT, padx=3)

        # 字体大小显示
        self.font_size_label = tk.Label(
            self.scrollable_frame,
            text=f"{self.font_size}",
            font=("Arial", 9),
            padx=5,
            pady=3,
            relief=tk.SUNKEN,
            bd=1,
            bg="white"
        )
        self.font_size_label.pack(side=tk.LEFT, padx=3)

        # 绑定鼠标滚轮到画布
        def on_mousewheel(event):
            self.button_canvas.xview_scroll(int(-1*(event.delta/120)), "units")

        self.button_canvas.bind("<MouseWheel>", on_mousewheel)

        # 延迟初始化滚动检查
        self.root.after(100, self.setup_button_scrolling)

        # ========== 状态栏 ==========
        status_frame = tk.Frame(main_frame, height=25)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        status_frame.grid_propagate(False)  # 防止子组件改变框架大小

        status_text = "Ready" if self.language == 'en' else "就绪"
        self.status_bar = tk.Label(
            status_frame,
            text=status_text,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9)
        )
        self.status_bar.pack(fill=tk.BOTH, expand=True)

        # 初始化字体大小显示
        self.root.after(100, self.update_initial_font_display)

    def setup_button_scrolling(self):
        """设置按钮滚动功能"""
        # 确保按钮容器正确显示
        self.root.update_idletasks()
        self.check_button_scroll_needed()

        # 绑定窗口大小变化事件
        self.button_canvas.bind('<Configure>', lambda e: self.root.after_idle(self.check_button_scroll_needed))

    def check_button_scroll_needed(self):
        """检查按钮是否需要滚动"""
        try:
            self.root.update_idletasks()

            # 确保画布已经正确初始化
            if not hasattr(self, 'button_canvas') or not hasattr(self, 'scrollable_frame'):
                return

            canvas_width = self.button_canvas.winfo_width()
            frame_width = self.scrollable_frame.winfo_reqwidth()

            # 只有当画布宽度大于1时才进行检查（确保已初始化）
            if canvas_width > 1:
                if frame_width > canvas_width:
                    # 需要滚动条
                    if not self.button_scrollbar.winfo_viewable():
                        self.button_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
                        # 调整画布高度为滚动条留出空间
                        self.button_canvas.configure(height=40)
                else:
                    # 不需要滚动条
                    if self.button_scrollbar.winfo_viewable():
                        self.button_scrollbar.pack_forget()
                        # 恢复画布高度
                        self.button_canvas.configure(height=50)

        except (tk.TclError, AttributeError):
            # 如果组件还没有完全初始化，忽略错误
            pass

    def bind_shortcuts(self):
        """绑定快捷键"""
        self.root.bind('<F5>', lambda e: self.calculate())
        self.root.bind('<Control-Return>', lambda e: self.calculate())
        self.root.bind('<Control-d>', lambda e: self.clear_all())
        self.root.bind('<Control-D>', lambda e: self.clear_all())
        self.root.bind('<Control-l>', lambda e: self.load_example())
        self.root.bind('<Control-L>', lambda e: self.load_example())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-O>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_file())
        self.root.bind('<Control-plus>', lambda e: self.increase_font())
        self.root.bind('<Control-equal>', lambda e: self.increase_font())
        self.root.bind('<Control-minus>', lambda e: self.decrease_font())

    def calculate(self):
        """执行计算"""
        try:
            # 获取输入内容
            input_content = self.input_text.get("1.0", tk.END).strip()

            if not input_content:
                status_text = "Please enter calculation content" if self.language == 'en' else "请输入计算内容"
                self.status_bar.config(text=status_text)
                return

            # 创建新的计算器实例
            self.calculator = CalculatorPaperAdvanced(language=self.language)

            # 处理文本
            self.calculator.process_text(input_content)

            # 获取格式化输出
            output = self.calculator.format_output()

            # 显示结果
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", output)

            # 应用语法高亮
            self.apply_syntax_highlighting()

            self.output_text.config(state=tk.DISABLED)

            status_text = "Calculation completed" if self.language == 'en' else "计算完成"
            self.status_bar.config(text=status_text)

        except Exception as e:
            error_title = "Error" if self.language == 'en' else "错误"
            error_msg = f"Calculation error: {str(e)}" if self.language == 'en' else f"计算出错：{str(e)}"
            messagebox.showerror(error_title, error_msg)
            error_status = f"Error: {str(e)}" if self.language == 'en' else f"错误: {str(e)}"
            self.status_bar.config(text=error_status)

    def apply_syntax_highlighting(self):
        """应用语法高亮"""
        # 清除所有标签
        for tag in self.output_text.tag_names():
            self.output_text.tag_remove(tag, "1.0", tk.END)

        # 定义标签样式
        self.output_text.tag_config("comment", foreground="gray")
        self.output_text.tag_config("result", foreground="green", font=("Consolas", 10, "bold"))
        self.output_text.tag_config("error", foreground="red")
        self.output_text.tag_config("total", foreground="blue", font=("Consolas", 10, "bold"))
        self.output_text.tag_config("endian", foreground="purple", font=("Consolas", 10, "bold"))
        self.output_text.tag_config("bit_info", foreground="darkblue", font=("Consolas", 9))

        content = self.output_text.get("1.0", tk.END)
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            line_start = f"{i}.0"
            line_end = f"{i}.end"

            # 注释行
            if line.strip().startswith('#'):
                self.output_text.tag_add("comment", line_start, line_end)

            # 错误信息
            elif '错误:' in line or '变量未定义:' in line:
                self.output_text.tag_add("error", line_start, line_end)

            # 总计行
            elif line.strip().startswith('总计:'):
                self.output_text.tag_add("total", line_start, line_end)

            # 分隔线
            elif line.strip().startswith('-'):
                self.output_text.tag_add("comment", line_start, line_end)

            # 字节序设置
            elif 'endian:' in line.lower():
                self.output_text.tag_add("endian", line_start, line_end)

            # 位信息行
            elif any(keyword in line for keyword in ['十六进制:', '二进制:', '位数:', '位索引']):
                self.output_text.tag_add("bit_info", line_start, line_end)

            # 结果行（包含 = 的行）
            elif '=' in line and not line.strip().startswith('#'):
                # 找到 = 号的位置
                eq_pos = line.find('=')
                if eq_pos > 0:
                    result_start = f"{i}.{eq_pos}"
                    self.output_text.tag_add("result", result_start, line_end)

    def clear_all(self):
        """清空所有内容"""
        self.input_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        status_text = "Cleared" if self.language == 'en' else "已清空"
        self.status_bar.config(text=status_text)

    def load_example(self):
        """加载示例"""
        if self.language == 'en':
            example = """# Advanced CalcPaper Example

# Set little endian
endian: little

# Basic hex operations
a = 0xFF
b = 0x1234
sum = a + b

# Bitwise operations
and_op = a & b
or_op = a | b
xor_op = a ^ b
left_shift = a << 2
right_shift = b >> 4

# Switch to big endian
endian: big

# RGB color extraction
color = 0xFF8040
red = (color >> 16) & 0xFF
green = (color >> 8) & 0xFF
blue = color & 0xFF

# View bit structure with bitmap
bitmap view_color = color

# Percentage calculation
price = 100
discount = price * 15%
final_price = price - discount
"""
        else:
            example = """# 高级计算稿纸示例

# 设置小端字节序
endian: little

# 基本16进制运算
a = 0xFF
b = 0x1234
和 = a + b

# 位运算
与 = a & b
或 = a | b
异或 = a ^ b
左移 = a << 2
右移 = b >> 4

# 切换到大端字节序
endian: big

# RGB颜色提取
颜色 = 0xFF8040
红色 = (颜色 >> 16) & 0xFF
绿色 = (颜色 >> 8) & 0xFF
蓝色 = 颜色 & 0xFF

# 使用bitmap查看位结构
bitmap 查看颜色 = 颜色

# 百分数计算
价格 = 100
折扣 = 价格 * 15%
实付 = 价格 - 折扣
"""
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", example)
        status_text = "Example loaded" if self.language == 'en' else "已加载示例"
        self.status_bar.config(text=status_text)

    def open_file(self):
        """打开文件"""
        title_text = "Open File" if self.language == 'en' else "打开文件"
        filename = filedialog.askopenfilename(
            title=title_text,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", content)
                status_text = f"Opened: {filename}" if self.language == 'en' else f"已打开: {filename}"
                self.status_bar.config(text=status_text)
            except Exception as e:
                error_title = "Error" if self.language == 'en' else "错误"
                error_msg = f"Cannot open file: {str(e)}" if self.language == 'en' else f"无法打开文件：{str(e)}"
                messagebox.showerror(error_title, error_msg)

    def save_file(self):
        """保存文件"""
        title_text = "Save File" if self.language == 'en' else "保存文件"
        filename = filedialog.asksaveasfilename(
            title=title_text,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            try:
                content = self.output_text.get("1.0", tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)

                status_text = f"Saved: {filename}" if self.language == 'en' else f"已保存: {filename}"
                self.status_bar.config(text=status_text)
            except Exception as e:
                error_title = "Error" if self.language == 'en' else "错误"
                error_msg = f"Cannot save file: {str(e)}" if self.language == 'en' else f"无法保存文件：{str(e)}"
                messagebox.showerror(error_title, error_msg)


def main():
    """主函数"""
    root = tk.Tk()
    app = CalculatorGUIAdvanced(root)
    root.mainloop()


if __name__ == '__main__':
    main()
