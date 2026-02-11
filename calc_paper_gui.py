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


class CalculatorGUIAdvanced:
    def __init__(self, root):
        self.root = root
        self.root.title("计算稿纸 - 高级版")
        self.root.geometry("1200x800")
        
        # 创建计算器实例
        self.calculator = CalculatorPaperAdvanced()
        
        # 创建界面
        self.create_widgets()
        
        # 绑定快捷键
        self.bind_shortcuts()
        
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧：输入区域
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 输入标签
        input_label = tk.Label(left_frame, text="输入区域：", font=("Arial", 10, "bold"))
        input_label.pack(anchor=tk.W)
        
        # 输入文本框
        self.input_text = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.WORD,
            width=50,
            height=30,
            font=("Consolas", 10)
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 右侧：输出区域
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # 输出标签
        output_label = tk.Label(right_frame, text="输出区域：", font=("Arial", 10, "bold"))
        output_label.pack(anchor=tk.W)
        
        # 输出文本框
        self.output_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            width=50,
            height=30,
            font=("Consolas", 10),
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 计算按钮
        calc_button = tk.Button(
            button_frame,
            text="计算 (F5)",
            command=self.calculate,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        calc_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 清空按钮
        clear_button = tk.Button(
            button_frame,
            text="清空",
            command=self.clear_all,
            bg="#f44336",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=5
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # 加载示例按钮
        example_button = tk.Button(
            button_frame,
            text="加载示例 (Ctrl+L)",
            command=self.load_example,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=5
        )
        example_button.pack(side=tk.LEFT, padx=5)
        
        # 打开文件按钮
        open_button = tk.Button(
            button_frame,
            text="打开文件 (Ctrl+O)",
            command=self.open_file,
            font=("Arial", 10),
            padx=20,
            pady=5
        )
        open_button.pack(side=tk.LEFT, padx=5)
        
        # 保存文件按钮
        save_button = tk.Button(
            button_frame,
            text="保存结果 (Ctrl+S)",
            command=self.save_file,
            font=("Arial", 10),
            padx=20,
            pady=5
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        # 状态栏
        self.status_bar = tk.Label(
            self.root,
            text="就绪",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def bind_shortcuts(self):
        """绑定快捷键"""
        self.root.bind('<F5>', lambda e: self.calculate())
        self.root.bind('<Control-Return>', lambda e: self.calculate())
        self.root.bind('<Control-l>', lambda e: self.load_example())
        self.root.bind('<Control-L>', lambda e: self.load_example())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-O>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_file())
        
    def calculate(self):
        """执行计算"""
        try:
            # 获取输入内容
            input_content = self.input_text.get("1.0", tk.END).strip()
            
            if not input_content:
                self.status_bar.config(text="请输入计算内容")
                return
            
            # 创建新的计算器实例
            self.calculator = CalculatorPaperAdvanced()
            
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
            
            self.status_bar.config(text="计算完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"计算出错：{str(e)}")
            self.status_bar.config(text=f"错误: {str(e)}")
    
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
        self.status_bar.config(text="已清空")
    
    def load_example(self):
        """加载示例"""
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

# 百分数计算
价格 = 100
折扣 = 价格 * 15%
实付 = 价格 - 折扣
"""
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", example)
        self.status_bar.config(text="已加载示例")
    
    def open_file(self):
        """打开文件"""
        filename = filedialog.askopenfilename(
            title="打开文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", content)
                self.status_bar.config(text=f"已打开: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件：{str(e)}")
    
    def save_file(self):
        """保存文件"""
        filename = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                content = self.output_text.get("1.0", tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.status_bar.config(text=f"已保存: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存文件：{str(e)}")


def main():
    """主函数"""
    root = tk.Tk()
    app = CalculatorGUIAdvanced(root)
    root.mainloop()


if __name__ == '__main__':
    main()
