#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算稿纸 - 高级版本
支持：
1. 四则运算、变量引用、百分数
2. 16进制 (0x...) 和 2进制 (0b...) 数值
3. 位运算：左移(<<)、右移(>>)、与(&)、或(|)、非(~)、异或(^)
4. 16进制按2进制显示，支持大小端字节序索引

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

import re
import sys
import argparse

VERSION = "1.4"


class CalculatorPaperAdvanced:
    def __init__(self, language='zh'):
        self.lines = []
        self.results = []
        self.variables = {}
        self.bit_display_mode = None  # 'little' 或 'big' 或 None
        self.language = language  # 'zh' 或 'en'
        
        # 撤销/恢复功能的历史记录
        self.history = []  # 存储历史状态
        self.history_index = -1  # 当前历史位置

    def set_language(self, language):
        """设置语言"""
        self.language = language
    
    def swap_endian(self, value, byte_size=None):
        """字节序交换函数
        
        Args:
            value: 要交换的整数值
            byte_size: 字节数（1, 2, 4, 8），如果为None则自动检测
            
        Returns:
            交换后的整数值
        """
        if not isinstance(value, (int, float)):
            raise ValueError("swap() 只能用于整数")
        
        value = int(value)
        if value < 0:
            raise ValueError("swap() 不支持负数")
        
        # 自动检测字节数
        if byte_size is None:
            if value == 0:
                byte_size = 1
            else:
                # 计算需要的字节数（向上取整到 1, 2, 4, 8）
                bit_len = value.bit_length()
                if bit_len <= 8:
                    byte_size = 1
                elif bit_len <= 16:
                    byte_size = 2
                elif bit_len <= 32:
                    byte_size = 4
                else:
                    byte_size = 8
        
        # 提取各字节并反转
        bytes_list = []
        for i in range(byte_size):
            byte_val = (value >> (i * 8)) & 0xFF
            bytes_list.append(byte_val)
        
        # 反转字节顺序
        bytes_list.reverse()
        
        # 重新组合
        result = 0
        for i, byte_val in enumerate(bytes_list):
            result |= (byte_val << (i * 8))
        
        return result

    def parse_line(self, line):
        """解析单行表达式"""
        line = line.strip()
        if not line or line.startswith('#'):
            return None, None, None, None, False, None

        # 移除行内注释
        original_expr = line
        if '#' in line:
            line = line.split('#')[0].strip()

        # 检查是否使用了 hex 函数（只能单独使用，不能赋值或参与计算）
        use_hex_func = False

        # 检查是否使用了 bitmap 函数（只能单独使用，不能赋值或参与计算）
        use_bitmap = False
        bitmap_endian = None
        bitmap_width = None

        hex_pattern = r'^hex\s*\(\s*(.+?)\s*\)$'
        hex_func_match = re.match(hex_pattern, line, re.IGNORECASE)

        # 支持嵌套括号，如 bitmap(swap(x), 1)
        # 第3个参数为可选的宽度参数
        bitmap_pattern = r'^bitmap\s*\(\s*(.+?)(?:\s*,\s*([01]))?(?:\s*,\s*(\d+))?\s*\)$'
        bitmap_match = re.match(bitmap_pattern, line, re.IGNORECASE)

        if hex_func_match:
            use_hex_func = True
            value_expr = hex_func_match.group(1).strip()
            line = value_expr
            label = None
            is_assignment = False

        elif bitmap_match:
            use_bitmap = True
            value_expr = bitmap_match.group(1).strip()
            endian_param = bitmap_match.group(2)
            width_param = bitmap_match.group(3)
            
            # 设置临时字节序
            if endian_param == '1':
                bitmap_endian = 'big'
            else:  # '0' 或 None
                bitmap_endian = 'little'
            
            # 设置位宽度
            if width_param is not None:
                bitmap_width = int(width_param)
                if bitmap_width <= 0:
                    return None, None, f"错误: bitmap 宽度参数必须是正整数", None, False, None
            
            # 只保留值表达式用于计算
            line = value_expr
            label = None
            is_assignment = False

        else:
            # 检查是否有标签（如：房租 = 1000）
            label = None
            expr = line
            is_assignment = False

            if '=' in line:
                parts = line.split('=', 1)
                left = parts[0].strip()
                right = parts[1].strip()

                # 检查左边是否是变量名（不包含运算符）
                if re.match(r'^[a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*$', left):
                    label = left
                    expr = right
                    is_assignment = True
                    line = expr

        # 检查原始表达式是否包含16进制或2进制（在变量替换之前）
        has_hex_bin = bool(re.search(r'0[xXbB][0-9a-fA-F]+', line))

        try:
            # 检查表达式是否包含位运算符
            has_bitwise = any(op in line for op in ['<<', '>>', '&', '|', '^', '~'])

            # 如果包含位运算或16进制/2进制，使用16进制格式替换变量
            use_hex_in_comment = has_hex_bin or has_bitwise

            # 替换变量
            expr_with_vars, undefined_vars = self._replace_variables(line, use_hex_format=use_hex_in_comment)

            # 如果有未定义的变量，返回错误
            if undefined_vars:
                return None, label, f"变量未定义: {', '.join(undefined_vars)}", None, False, None

            # 计算表达式
            result = self.evaluate(expr_with_vars, has_hex_bin)

            # 保存变量（只有非 bitmap/hex 调用才保存）
            if label and not use_bitmap and not use_hex_func:
                self.variables[label] = result

            # 返回结果和替换后的表达式（如果有变量替换）
            replaced_expr = expr_with_vars if expr_with_vars != line else None

            # 生成位显示信息
            # 只有当使用了 bitmap 函数时才显示位索引
            bit_info = None
            if use_bitmap and bitmap_endian:
                # 如果结果是整数值（可能是float类型），转换为int
                if isinstance(result, (int, float)) and result >= 0:
                    int_result = int(result)
                    if int_result == result:  # 确保是整数值
                        # 检测原始表达式中的前导0位数
                        input_bit_width = self._detect_input_bit_width(value_expr)
                        bit_info = self._generate_bit_display(int_result, bitmap_endian, bitmap_width, input_bit_width)

            # 生成 hex 显示信息
            hex_info = None
            if use_hex_func:
                if isinstance(result, (int, float)) and result >= 0:
                    int_result = int(result)
                    if int_result == result:
                        hex_info = f"0x{int_result:X}"

            # 返回结果，标签，替换表达式，位信息，是否使用bitmap，hex信息
            return result, label, replaced_expr, bit_info, use_bitmap, hex_info

        except Exception as e:
            return None, label, f"错误: {str(e)}", None, False, None

    def _replace_variables(self, expr, use_hex_format=False):
        """替换表达式中的变量

        Args:
            expr: 表达式字符串
            use_hex_format: 是否使用16进制格式显示变量值
        """
        # 先保护16进制和2进制字面量
        # 使用占位符替换它们
        hex_bin_pattern = r'0[xXbB][0-9a-fA-F]+'
        protected = []

        def protect_hex_bin(match):
            protected.append(match.group(0))
            return f'__PROTECTED_{len(protected)-1}__'

        expr_protected = re.sub(hex_bin_pattern, protect_hex_bin, expr)

        # 找出所有可能的变量名（中文、英文、数字、下划线）
        # 但要排除 swap 和 bitmap 函数名
        pattern = r'\b([a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*)\b'

        undefined_vars = []

        def replace_func(match):
            var_name = match.group(1)
            # 跳过占位符和函数名
            if var_name.startswith('__PROTECTED_') or var_name.lower() in ['swap', 'bitmap', 'hex']:
                return var_name

            if var_name in self.variables:
                val = self.variables[var_name]
                # 如果需要16进制格式且值是整数
                if use_hex_format and isinstance(val, (int, float)):
                    int_val = int(val)
                    if int_val == val and int_val >= 0:
                        return f"0x{int_val:X}"

                # 否则使用十进制格式
                if isinstance(val, int):
                    return str(val)
                elif isinstance(val, float) and val == int(val):
                    # 如果是整数值的浮点数，转换为整数
                    return str(int(val))
                return str(val)
            else:
                undefined_vars.append(var_name)
                return var_name

        result = re.sub(pattern, replace_func, expr_protected)

        # 恢复16进制和2进制字面量
        for i, literal in enumerate(protected):
            result = result.replace(f'__PROTECTED_{i}__', literal)

        return result, undefined_vars

    def _convert_percentage(self, expression):
        """将百分数转换为小数"""
        pattern = r'(\d+\.?\d*)%'

        def replace_func(match):
            number = match.group(1)
            return str(float(number) / 100)

        return re.sub(pattern, replace_func, expression)

    def _convert_hex_bin(self, expression):
        """转换16进制和2进制数值"""
        # 16进制: 0x... 或 0X...
        expression = re.sub(r'0[xX]([0-9a-fA-F]+)', lambda m: str(int(m.group(1), 16)), expression)

        # 2进制: 0b... 或 0B...
        expression = re.sub(r'0[bB]([01]+)', lambda m: str(int(m.group(1), 2)), expression)

        return expression

    def evaluate(self, expression, has_hex_bin=False):
        """计算表达式的值"""
        # 移除空格
        expression = expression.replace(' ', '')

        # 检查表达式是否合法
        if not expression:
            raise ValueError("表达式为空")

        # 转换百分数
        expression = self._convert_percentage(expression)

        # 转换16进制和2进制
        expression = self._convert_hex_bin(expression)
        
        # 处理 swap() 函数调用（递归处理，从内到外）
        max_iterations = 10  # 防止无限循环
        iteration = 0
        while 'swap(' in expression.lower() and iteration < max_iterations:
            swap_pattern = r'swap\s*\(\s*([^()]+)\s*\)'
            match = re.search(swap_pattern, expression, flags=re.IGNORECASE)
            if not match:
                break
            
            inner_expr = match.group(1)
            # 计算内部表达式
            try:
                inner_value = eval(inner_expr)
                # 执行字节序交换
                swapped = self.swap_endian(inner_value)
                # 替换整个 swap(...) 为结果
                expression = expression[:match.start()] + str(swapped) + expression[match.end():]
            except Exception as e:
                raise ValueError(f"swap() 函数错误: {str(e)}")
            
            iteration += 1

        # 检查是否包含位运算符
        has_bitwise = any(op in expression for op in ['<<', '>>', '&', '|', '^', '~'])

        # 使用 Python 的 eval 进行计算
        # 允许的字符包括：数字、运算符、括号
        allowed_chars = set('0123456789+-*/(). ')
        if has_bitwise:
            allowed_chars.update(['<', '>', '&', '|', '^', '~'])

        if not all(c in allowed_chars for c in expression):
            raise ValueError("包含非法字符")

        try:
            result = eval(expression)
            # 如果使用了位运算或16/2进制，强制返回整数
            if has_bitwise or has_hex_bin:
                return int(result)
            # 如果结果是整数值，返回整数
            if isinstance(result, float) and result == int(result):
                return int(result)
            return float(result)
        except ZeroDivisionError:
            raise ValueError("除数不能为零")
        except SyntaxError:
            raise ValueError("表达式语法错误")
        except Exception as e:
            raise ValueError(f"计算错误: {str(e)}")

    def _align_to_boundary(self, bits):
        """将位数对齐到最接近的 8/16/32/64 边界
        
        Args:
            bits: 需要的最小位数
            
        Returns:
            对齐后的位数（8, 16, 32 或 64）
        """
        if bits <= 8:
            return 8
        elif bits <= 16:
            return 16
        elif bits <= 32:
            return 32
        elif bits <= 64:
            return 64
        else:
            # 超过64位，按8位对齐
            return ((bits + 7) // 8) * 8

    def _detect_input_bit_width(self, expr):
        """检测输入表达式中的位宽度（基于前导0）
        
        例如：0x00FF → 16位（4个hex字符 × 4位）
              0b00001111 → 8位（8个bin字符）
              0xFF → 8位（2个hex字符 × 4位）
        
        Returns:
            检测到的位宽度，如果无法检测则返回None
        """
        expr = expr.strip()
        
        # 先检查是否是变量引用，如果是则查找变量的原始赋值
        # 这里只处理直接的字面量
        
        # 检查16进制字面量
        hex_match = re.match(r'^0[xX]([0-9a-fA-F]+)$', expr)
        if hex_match:
            hex_digits = hex_match.group(1)
            return len(hex_digits) * 4  # 每个hex字符4位
        
        # 检查2进制字面量
        bin_match = re.match(r'^0[bB]([01]+)$', expr)
        if bin_match:
            bin_digits = bin_match.group(1)
            return len(bin_digits)
        
        return None

    def _generate_bit_display(self, value, endian_mode, user_width=None, input_bit_width=None):
        """生成位显示信息
        
        Args:
            value: 要显示的整数值
            endian_mode: 字节序模式 ('big' 或 'little')
            user_width: 用户指定的位宽度（8, 16, 32, 64），可选
            input_bit_width: 从输入表达式检测到的位宽度（保留前导0），可选
        """
        if not isinstance(value, int) or value < 0:
            return None

        # 确定需要的最小位数
        if value == 0:
            min_bits = 8
        else:
            min_bits = value.bit_length()

        # 确定最终位数
        if user_width is not None:
            # 用户显式指定了宽度
            bit_count = user_width
            if bit_count < min_bits:
                # 宽度不够，自动扩展到能容纳值的最小宽度
                bit_count = self._align_to_boundary(min_bits)
        elif input_bit_width is not None:
            # 使用输入表达式中检测到的位宽度（保留前导0）
            # 对齐到最近的 8/16/32/64 边界
            bit_count = self._align_to_boundary(max(min_bits, input_bit_width))
        else:
            # 缺省：对齐到最接近的 8/16/32/64 边界
            bit_count = self._align_to_boundary(min_bits)

        # 生成二进制字符串（从MSB到LSB，保留前导0）
        bin_str = format(value, f'0{bit_count}b')

        result_lines = []
        
        # 根据语言选择文本
        if self.language == 'en':
            # 保留前导0的16进制表示
            hex_width = bit_count // 4
            result_lines.append(f"  Hexadecimal: 0x{value:0{hex_width}X}")
            result_lines.append(f"  Binary: 0b{bin_str}")
            result_lines.append(f"  Bits: {bit_count} bits ({bit_count // 8} bytes)")
        else:
            # 保留前导0的16进制表示
            hex_width = bit_count // 4
            result_lines.append(f"  十六进制: 0x{value:0{hex_width}X}")
            result_lines.append(f"  二进制: 0b{bin_str}")
            result_lines.append(f"  位数: {bit_count} bits ({bit_count // 8} bytes)")

        # 生成位索引表格
        if endian_mode == 'big':
            # 大端字节序：MSB（最高位）从0开始编码
            # 位索引从左到右：0, 1, 2, ..., 31
            if self.language == 'en':
                result_lines.append("  Bit indices (Big Endian):")
            else:
                result_lines.append("  位索引 (大端字节序):")

            index_parts = []
            bit_parts = []

            # 从MSB到LSB显示（bin_str从左到右）
            for i in range(0, bit_count, 4):
                # 每4位一组
                nibble_bits = bin_str[i:i+4]

                # 大端：MSB从0开始，从左到右 0→31
                indices = [str(i + j) for j in range(4)]
                bits = list(nibble_bits)

                # 计算这组的最大宽度
                max_width = max(len(idx) for idx in indices)

                # 格式化索引（右对齐）
                formatted_indices = [f"{idx:>{max_width}}" for idx in indices]
                # 格式化位值（右对齐，与索引对齐）
                formatted_bits = [f"{bit:>{max_width}}" for bit in bits]

                index_parts.append('|' + ' '.join(formatted_indices) + ' ')
                bit_parts.append('|' + ' '.join(formatted_bits) + ' ')

            # 添加结束符
            index_parts.append('|')
            bit_parts.append('|')

            # 输出
            result_lines.append('    ' + ''.join(index_parts))
            result_lines.append('    ' + ''.join(bit_parts))

        elif endian_mode == 'little':
            # 小端字节序：LSB（最低位）从0开始编码
            # 位索引从右到左：..., 2, 1, 0
            # 但显示时从左到右：31, 30, ..., 1, 0
            if self.language == 'en':
                result_lines.append("  Bit indices (Little Endian):")
            else:
                result_lines.append("  位索引 (小端字节序):")

            index_parts = []
            bit_parts = []

            # 从MSB到LSB显示（bin_str从左到右）
            for i in range(0, bit_count, 4):
                # 每4位一组
                nibble_bits = bin_str[i:i+4]

                # 小端：LSB从0开始，从左到右显示 31→0
                indices = [str(bit_count - 1 - i - j) for j in range(4)]
                bits = list(nibble_bits)

                # 计算这组的最大宽度
                max_width = max(len(idx) for idx in indices)

                # 格式化索引（右对齐）
                formatted_indices = [f"{idx:>{max_width}}" for idx in indices]
                # 格式化位值（右对齐，与索引对齐）
                formatted_bits = [f"{bit:>{max_width}}" for bit in bits]

                index_parts.append('|' + ' '.join(formatted_indices) + ' ')
                bit_parts.append('|' + ' '.join(formatted_bits) + ' ')

            # 添加结束符
            index_parts.append('|')
            bit_parts.append('|')

            # 输出
            result_lines.append('    ' + ''.join(index_parts))
            result_lines.append('    ' + ''.join(bit_parts))

        return '\n'.join(result_lines)

    def process_text(self, text):
        """处理多行文本"""
        self.lines = []
        self.results = []
        self.variables = {}

        lines = text.strip().split('\n')

        for line in lines:
            original_line = line.strip()

            # 空行
            if not original_line:
                self.lines.append('')
                self.results.append(None)
                continue

            # 注释行
            if original_line.startswith('#'):
                self.lines.append(original_line)
                self.results.append(None)
                continue

            # 解析表达式
            result, label, extra_info, bit_info, use_bitmap, hex_info = self.parse_line(line)

            self.lines.append(original_line)

            if result is not None:
                # 成功计算
                self.results.append((result, label, extra_info, bit_info, use_bitmap, hex_info))
            else:
                # 计算失败或特殊命令
                self.results.append((None, label, extra_info, bit_info, use_bitmap, hex_info))
        
        # 保存当前状态到历史记录
        self.save_state()
    
    def save_state(self):
        """保存当前状态到历史记录"""
        # 如果当前不在历史末尾，删除后面的历史
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        # 保存当前状态
        state = {
            'lines': self.lines.copy(),
            'results': self.results.copy(),
            'variables': self.variables.copy()
        }
        self.history.append(state)
        self.history_index = len(self.history) - 1
        
        # 限制历史记录数量（最多保存50个状态）
        if len(self.history) > 50:
            self.history.pop(0)
            self.history_index -= 1
    
    def undo(self):
        """撤销到上一个状态"""
        if self.history_index > 0:
            self.history_index -= 1
            state = self.history[self.history_index]
            self.lines = state['lines'].copy()
            self.results = state['results'].copy()
            self.variables = state['variables'].copy()
            return True
        return False
    
    def redo(self):
        """恢复到下一个状态"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            state = self.history[self.history_index]
            self.lines = state['lines'].copy()
            self.results = state['results'].copy()
            self.variables = state['variables'].copy()
            return True
        return False
    
    def can_undo(self):
        """检查是否可以撤销"""
        return self.history_index > 0
    
    def can_redo(self):
        """检查是否可以恢复"""
        return self.history_index < len(self.history) - 1

    def format_output(self):
        """格式化输出结果"""
        output = []
        max_line_len = max(len(line) for line in self.lines) if self.lines else 0

        for line, result_info in zip(self.lines, self.results):
            # 空行
            if not line:
                output.append('')
                continue

            # 注释行
            if line.startswith('#'):
                output.append(line)
                continue

            # 没有结果信息
            if result_info is None:
                output.append(line)
                continue

            result, label, extra_info, bit_info, use_bitmap, hex_info = result_info

            if result is None:
                # 计算失败或特殊命令，显示信息
                if extra_info:
                    output.append(f"{line}  # {extra_info}")
                else:
                    output.append(line)
            else:
                # 格式化数字
                if hex_info:
                    # hex() 函数：显示16进制
                    result_str = hex_info
                elif isinstance(result, int):
                    # 整数
                    if use_bitmap:
                        # 使用 bitmap 函数：只显示十进制
                        result_str = str(result)
                    else:
                        # 未使用 bitmap：只显示十进制
                        result_str = str(result)
                elif result == int(result):
                    result_str = str(int(result))
                else:
                    result_str = f"{result:.2f}"

                padding = ' ' * (max_line_len - len(line) + 2)

                # bitmap 调用不显示赋值，只显示结果
                if use_bitmap:
                    # 如果有变量替换，显示替换后的表达式
                    if extra_info:
                        output.append(f"{line}{padding}= {result_str}  # {extra_info}")
                    else:
                        output.append(f"{line}{padding}= {result_str}")
                else:
                    # 普通计算，显示赋值
                    if extra_info:
                        output.append(f"{line}{padding}= {result_str}  # {extra_info}")
                    else:
                        output.append(f"{line}{padding}= {result_str}")

                # 如果有位显示信息，添加到输出
                if bit_info:
                    output.append(bit_info)

        return '\n'.join(output)


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='CalcPaper - Advanced Calculator with Bitwise Operations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples (示例):
  # Basic calculation (基本计算)
  a = 100
  b = 200
  sum = a + b

  # Bitwise operations (位运算)
  x = 0xFF
  y = x << 2

  # RGB color extraction (RGB颜色提取)
  color = 0xFF8040
  red = (color >> 16) & 0xFF

  # bitmap function for bit structure (bitmap函数查看位结构)
  bitmap(0xFF)           # Little endian (default) (小端，默认)
  bitmap(0xFF, 0)        # Little endian (小端)
  bitmap(0xFF, 1)        # Big endian (大端)
  bitmap(0xFF, 1, 32)    # Big endian, 32-bit width (大端，32位宽度)
  bitmap(0x00FF)         # Leading zeros preserved (保留前导0)
  
  # Note: bitmap() can only be used standalone (注意：bitmap()只能单独使用)
  # Cannot assign to variable or use in expressions (不能赋值或参与计算)

  # Percentage calculation (百分数计算)
  price = 100
  discount = 15%
  final = price * (1 - discount)
"""
    )

    parser.add_argument('-l', '--lang', choices=['zh', 'en'], default='en',
                        help='Language / 语言 (zh: 中文, en: English)')
    parser.add_argument('-v', '--version', action='version',
                        version=f'CalcPaper v{VERSION}')

    args = parser.parse_args()
    language = args.lang

    # 根据语言显示不同的界面
    if language == 'en':
        print("=" * 80)
        print(f"CalcPaper - Advanced v{VERSION} (Hex, Binary & Bitwise Operations)")
        print("=" * 80)
        print("Usage:")
        print("1. Basic operations: +, -, *, /, ()")
        print("2. Variable reference: variable_name = expression")
        print("3. Percentage: 6.5%, 10%")
        print("4. Hexadecimal: 0xFF, 0x1A2B")
        print("5. Binary: 0b1010, 0b11110000")
        print("6. Bitwise operations:")
        print("   - Left shift: <<  (e.g., 0b1010 << 2)")
        print("   - Right shift: >> (e.g., 0xFF >> 4)")
        print("   - AND: &          (e.g., 0xFF & 0x0F)")
        print("   - OR: |           (e.g., 0xF0 | 0x0F)")
        print("   - XOR: ^          (e.g., 0xFF ^ 0xAA)")
        print("   - NOT: ~          (e.g., ~0b1010)")
        print("7. bitmap function:")
        print("   - bitmap(value)           (Little Endian, default)")
        print("   - bitmap(value, 0)        (Little Endian)")
        print("   - bitmap(value, 1)        (Big Endian)")
        print("   - bitmap(value, 0, 32)    (Little Endian, 32-bit width)")
        print("   - bitmap(value, 1, 64)    (Big Endian, 64-bit width)")
        print("   - Width: any positive integer (auto-align if omitted)")
        print("   - Leading zeros are preserved for alignment")
        print("   - Note: Can only be used standalone")
        print("   - Example: bitmap(0xFF, 1)")
        print("8. swap function:")
        print("   - swap(value)        (Swap byte order)")
        print("   - Can be used in expressions")
        print("   - Example: a = swap(0x1234)  # Result: 0x3412")
        print("   - Example: bitmap(swap(b))")
        print("9. hex function:")
        print("   - hex(value)         (Display as hexadecimal)")
        print("   - Note: Can only be used standalone")
        print("   - Example: hex(255)  # Result: 0xFF")
        print("10. Lines starting with # are comments")
        print("11. Type 'exit' or 'quit' to exit")
        print("12. Type 'calc' to start calculation")
        print("=" * 80)
        print()

        example = """# Bitwise operations example

# Normal calculation (decimal only)
a = 0xFF
b = 0x0F
sum = a + b

# View bit structure with bitmap (little endian)
bitmap(a, 0)
bitmap(b)

# Bitwise operations (decimal only)
and_result = a & b
or_result = a | b

# View bitwise operation results with bitmap (big endian)
bitmap(and_result, 1)
bitmap(or_result, 1)
"""

        print("Example input:")
        print(example)
        print("\nExample output:")
        calculator = CalculatorPaperAdvanced(language=language)
        calculator.process_text(example)
        print(calculator.format_output())
        print("\n" + "=" * 80)
        print("Now enter your calculation content (type 'calc' to calculate):\n")

    else:  # Chinese
        print("=" * 80)
        print(f"计算稿纸 - 高级版 v{VERSION}（支持16进制、2进制和位运算）")
        print("=" * 80)
        print("使用说明:")
        print("1. 基本运算: +、-、*、/、()")
        print("2. 变量引用: 变量名 = 表达式")
        print("3. 百分数: 6.5%、10%")
        print("4. 16进制: 0xFF、0x1A2B")
        print("5. 2进制: 0b1010、0b11110000")
        print("6. 位运算:")
        print("   - 左移: <<  (例: 0b1010 << 2)")
        print("   - 右移: >>  (例: 0xFF >> 4)")
        print("   - 与: &     (例: 0xFF & 0x0F)")
        print("   - 或: |     (例: 0xF0 | 0x0F)")
        print("   - 异或: ^   (例: 0xFF ^ 0xAA)")
        print("   - 非: ~     (例: ~0b1010)")
        print("7. bitmap 函数:")
        print("   - bitmap(数值)            (小端字节序，默认)")
        print("   - bitmap(数值, 0)         (小端字节序)")
        print("   - bitmap(数值, 1)         (大端字节序)")
        print("   - bitmap(数值, 0, 32)     (小端字节序，32位宽度)")
        print("   - bitmap(数值, 1, 64)     (大端字节序，64位宽度)")
        print("   - 宽度: 任意正整数（缺省自动对齐）")
        print("   - 前导0会被保留用于对齐")
        print("   - 注意：只能单独使用")
        print("   - 示例: bitmap(0xFF, 1)")
        print("8. swap 函数:")
        print("   - swap(数值)         (字节序交换)")
        print("   - 可以用于表达式中")
        print("   - 示例: a = swap(0x1234)  # 结果: 0x3412")
        print("   - 示例: bitmap(swap(b))")
        print("9. hex 函数:")
        print("   - hex(数值)          (显示16进制)")
        print("   - 注意：只能单独使用")
        print("   - 示例: hex(255)  # 结果: 0xFF")
        print("10. 以 # 开头的行为注释")
        print("11. 输入 'exit' 或 'quit' 退出")
        print("12. 输入 'calc' 开始计算")
        print("=" * 80)
        print()

        example = """# 位运算示例

# 普通计算（只显示十进制）
a = 0xFF
b = 0x0F
和 = a + b

# 使用 bitmap 查看位结构（小端字节序）
bitmap(a, 0)
bitmap(b)

# 位运算（只显示十进制）
与运算 = a & b
或运算 = a | b

# 使用 bitmap 查看位运算结果（大端字节序）
bitmap(与运算, 1)
bitmap(或运算, 1)
"""

        print("示例输入:")
        print(example)
        print("\n示例输出:")
        calculator = CalculatorPaperAdvanced(language=language)
        calculator.process_text(example)
        print(calculator.format_output())
        print("\n" + "=" * 80)
        print("现在请输入你的计算内容（输入 'calc' 开始计算）:\n")

    calculator = CalculatorPaperAdvanced(language=language)
    lines = []

    while True:
        try:
            line = input()

            if line.lower() in ['exit', 'quit']:
                msg = "Goodbye!" if language == 'en' else "再见！"
                print(msg)
                break

            if line.lower() == 'clear':
                lines = []
                msg = "Input cleared\n" if language == 'en' else "已清空输入内容\n"
                print(msg)
                continue

            if line.lower() == 'calc':
                if lines:
                    text = '\n'.join(lines)
                    calculator = CalculatorPaperAdvanced(language=language)
                    calculator.process_text(text)
                    print("\n" + "=" * 80)
                    result_title = "Calculation Result:" if language == 'en' else "计算结果:"
                    print(result_title)
                    print("=" * 80)
                    print(calculator.format_output())
                    print("\n" + "=" * 80)
                    continue_msg = "Continue or type 'exit' to quit:\n" if language == 'en' else "继续输入或输入 'exit' 退出:\n"
                    print(continue_msg)
                    lines = []
                else:
                    msg = "Please enter calculation content first!\n" if language == 'en' else "请先输入计算内容！\n"
                    print(msg)
            else:
                lines.append(line)

        except KeyboardInterrupt:
            msg = "\n\nGoodbye!" if language == 'en' else "\n\n再见！"
            print(msg)
            break
        except EOFError:
            break


if __name__ == '__main__':
    main()
