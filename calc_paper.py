#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算稿纸 - 高级版本
支持：
1. 四则运算、变量引用、百分数
2. 16进制 (0x...) 和 2进制 (0b...) 数值
3. 位运算：左移(<<)、右移(>>)、与(&)、或(|)、非(~)、异或(^)
4. 16进制按2进制显示，支持大小端字节序索引
"""

import re
import sys
import argparse

VERSION = "1.0"


class CalculatorPaperAdvanced:
    def __init__(self, language='zh'):
        self.lines = []
        self.results = []
        self.variables = {}
        self.bit_display_mode = None  # 'little' 或 'big' 或 None
        self.language = language  # 'zh' 或 'en'

    def set_language(self, language):
        """设置语言"""
        self.language = language

    def parse_line(self, line):
        """解析单行表达式"""
        line = line.strip()
        if not line or line.startswith('#'):
            return None, None, None, None, False

        # 检查是否是字节序设置命令
        if line.lower().startswith('endian:'):
            endian = line.split(':', 1)[1].strip().lower()
            if endian in ['little', 'small', '小端', '小字节序']:
                self.bit_display_mode = 'little'
                msg = "已设置为小端字节序 (Little Endian)" if self.language == 'zh' else "Set to Little Endian"
                return None, None, msg, 'endian', False
            elif endian in ['big', 'large', '大端', '大字节序']:
                self.bit_display_mode = 'big'
                msg = "已设置为大端字节序 (Big Endian)" if self.language == 'zh' else "Set to Big Endian"
                return None, None, msg, 'endian', False
            elif endian in ['none', 'off', '关闭']:
                self.bit_display_mode = None
                msg = "已关闭字节序显示" if self.language == 'zh' else "Endian display disabled"
                return None, None, msg, 'endian', False
            else:
                msg = f"错误: 未知的字节序类型: {endian}" if self.language == 'zh' else f"Error: Unknown endian type: {endian}"
                return None, None, msg, 'endian', False

        # 移除行内注释
        original_expr = line
        if '#' in line:
            line = line.split('#')[0].strip()

        # 检查是否使用了 bitmap 关键字
        use_bitmap = False
        if line.lower().startswith('bitmap'):
            use_bitmap = True
            # 移除 bitmap 关键字
            line = line[6:].strip()

        # 检查原始表达式是否包含16进制或2进制（在变量替换之前）
        has_hex_bin = bool(re.search(r'0[xXbB][0-9a-fA-F]+', line))

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

        try:
            # 检查表达式是否包含位运算符
            has_bitwise = any(op in expr for op in ['<<', '>>', '&', '|', '^', '~'])

            # 如果包含位运算或16进制/2进制，使用16进制格式替换变量
            use_hex_in_comment = has_hex_bin or has_bitwise

            # 替换变量
            expr_with_vars, undefined_vars = self._replace_variables(expr, use_hex_format=use_hex_in_comment)

            # 如果有未定义的变量，返回错误
            if undefined_vars:
                return None, label, f"变量未定义: {', '.join(undefined_vars)}", None, False

            # 计算表达式
            result = self.evaluate(expr_with_vars, has_hex_bin)

            # 保存变量
            if label:
                self.variables[label] = result

            # 返回结果和替换后的表达式（如果有变量替换）
            replaced_expr = expr_with_vars if expr_with_vars != expr else None

            # 生成位显示信息
            # 只有当使用了 bitmap 关键字时才显示位索引
            bit_info = None
            if use_bitmap and self.bit_display_mode:
                # 如果结果是整数值（可能是float类型），转换为int
                if isinstance(result, (int, float)) and result >= 0:
                    int_result = int(result)
                    if int_result == result:  # 确保是整数值
                        bit_info = self._generate_bit_display(int_result)

            # 返回结果，标签，替换表达式，位信息，是否使用bitmap
            return result, label, replaced_expr, bit_info, use_bitmap

        except Exception as e:
            return None, label, f"错误: {str(e)}", None, False

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
        pattern = r'\b([a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*)\b'

        undefined_vars = []

        def replace_func(match):
            var_name = match.group(1)
            # 跳过占位符
            if var_name.startswith('__PROTECTED_'):
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

    def _generate_bit_display(self, value):
        """生成位显示信息"""
        if not isinstance(value, int) or value < 0:
            return None

        # 确定需要的位数（至少8位，按8位对齐）
        if value == 0:
            bit_count = 8
        else:
            bit_count = ((value.bit_length() + 7) // 8) * 8

        # 生成二进制字符串（从MSB到LSB）
        bin_str = format(value, f'0{bit_count}b')

        result_lines = []
        result_lines.append(f"  十六进制: 0x{value:X}")
        result_lines.append(f"  二进制: 0b{bin_str}")
        result_lines.append(f"  位数: {bit_count} bits ({bit_count // 8} bytes)")

        # 生成位索引表格
        # 不管大端小端，二进制位都从MSB到LSB显示（从左到右）
        # 位索引的含义：位0是LSB，位31是MSB

        if self.bit_display_mode == 'little':
            # 小端字节序：位索引从左到右递增 0→31
            result_lines.append("  位索引 (小端字节序):")

            index_parts = []
            bit_parts = []

            # 从MSB到LSB显示（bin_str从左到右）
            for i in range(0, bit_count, 4):
                # 每4位一组
                nibble_bits = bin_str[i:i+4]

                # 小端：从左到右 0→31
                indices = [str(i + j) for j in range(4)]
                bits = [nibble_bits[j] for j in range(4)]

                # 计算这组的最大宽度
                max_width = max(len(idx) for idx in indices)

                # 格式化索引（右对齐）
                formatted_indices = [f"{idx:>{max_width}}" for idx in indices]
                # 格式化位值（居中对齐到索引宽度）
                formatted_bits = [f"{bit:^{max_width}}" for bit in bits]

                index_parts.append('|' + ' '.join(formatted_indices) + ' ')
                bit_parts.append('|' + ' '.join(formatted_bits) + ' ')

            # 添加结束符
            index_parts.append('|')
            bit_parts.append('|')

            # 输出
            result_lines.append('    ' + ''.join(index_parts))
            result_lines.append('    ' + ''.join(bit_parts))

        elif self.bit_display_mode == 'big':
            # 大端字节序：位索引从左到右递减 31→0
            result_lines.append("  位索引 (大端字节序):")

            index_parts = []
            bit_parts = []

            # 从MSB到LSB显示（bin_str从左到右）
            for i in range(0, bit_count, 4):
                # 每4位一组
                nibble_bits = bin_str[i:i+4]

                # 大端：从左到右 31→0
                indices = [str(bit_count - 1 - i - j) for j in range(4)]
                bits = [nibble_bits[j] for j in range(4)]

                # 计算这组的最大宽度
                max_width = max(len(idx) for idx in indices)

                # 格式化索引（右对齐）
                formatted_indices = [f"{idx:>{max_width}}" for idx in indices]
                # 格式化位值（居中对齐到索引宽度）
                formatted_bits = [f"{bit:^{max_width}}" for bit in bits]

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
            result, label, extra_info, bit_info, use_bitmap = self.parse_line(line)

            self.lines.append(original_line)

            if result is not None:
                # 成功计算
                self.results.append((result, label, extra_info, bit_info, use_bitmap))
            else:
                # 计算失败或特殊命令
                self.results.append((None, label, extra_info, bit_info, use_bitmap))

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

            result, label, extra_info, bit_info, use_bitmap = result_info

            if result is None:
                # 计算失败或特殊命令，显示信息
                if extra_info:
                    output.append(f"{line}  # {extra_info}")
                else:
                    output.append(line)
            else:
                # 格式化数字
                if isinstance(result, int):
                    # 整数
                    if use_bitmap:
                        # 使用 bitmap 关键字：显示十进制、十六进制和二进制
                        result_str = str(result)
                        if result >= 0:
                            hex_str = f"0x{result:X}"
                            bin_str = f"0b{result:b}"
                            result_str = f"{result} ({hex_str}, {bin_str})"
                    else:
                        # 未使用 bitmap：只显示十进制
                        result_str = str(result)
                elif result == int(result):
                    result_str = str(int(result))
                else:
                    result_str = f"{result:.2f}"

                padding = ' ' * (max_line_len - len(line) + 2)

                # 如果有变量替换，显示替换后的表达式
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

  # Endianness setting (字节序设置)
  endian: big     # Big endian (大端)
  endian: little  # Little endian (小端)
  endian: none    # Disable (关闭)

  # Bitmap keyword for bit structure (bitmap关键字查看位结构)
  endian: big
  bitmap view = 0xFF  # Shows hex, binary, and bit indices
                      # 显示16进制、2进制和位索引

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
        print("7. Endianness display:")
        print("   - endian: little  (Little Endian)")
        print("   - endian: big     (Big Endian)")
        print("   - endian: none    (Disable)")
        print("8. bitmap keyword:")
        print("   - Without bitmap: Show decimal only")
        print("   - With bitmap: Show decimal, hex, binary and bit indices")
        print("   - Example: bitmap a = 0xFF")
        print("9. Lines starting with # are comments")
        print("10. Type 'exit' or 'quit' to exit")
        print("11. Type 'calc' to start calculation")
        print("=" * 80)
        print()

        example = """# Bitwise operations example

# Set little endian display
endian: little

# Normal calculation (decimal only)
a = 0xFF
b = 0x0F
sum = a + b

# View bit structure with bitmap
bitmap view_a = a
bitmap view_b = b

# Bitwise operations (decimal only)
and_result = a & b
or_result = a | b

# View bitwise operation results with bitmap
bitmap view_and = and_result
bitmap view_or = or_result
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
        print("7. 字节序显示:")
        print("   - endian: little  (小端字节序)")
        print("   - endian: big     (大端字节序)")
        print("   - endian: none    (关闭)")
        print("8. bitmap 关键字:")
        print("   - 不使用 bitmap: 只显示十进制")
        print("   - 使用 bitmap: 显示十进制、16进制、2进制和位索引")
        print("   - 示例: bitmap a = 0xFF")
        print("9. 以 # 开头的行为注释")
        print("10. 输入 'exit' 或 'quit' 退出")
        print("11. 输入 'calc' 开始计算")
        print("=" * 80)
        print()

        example = """# 位运算示例

# 设置小端字节序显示
endian: little

# 普通计算（只显示十进制）
a = 0xFF
b = 0x0F
和 = a + b

# 使用 bitmap 查看位结构
bitmap 查看a = a
bitmap 查看b = b

# 位运算（只显示十进制）
与运算 = a & b
或运算 = a | b

# 使用 bitmap 查看位运算结果
bitmap 查看与运算 = 与运算
bitmap 查看或运算 = 或运算
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
