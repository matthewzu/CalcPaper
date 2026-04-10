#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CalcPaper - Advanced Calculator Paper
Features:
1. Arithmetic, variable references, percentages
2. Hexadecimal (0x...) and binary (0b...) numbers
3. Bitwise operations: left shift(<<), right shift(>>), AND(&), OR(|), NOT(~), XOR(^)
4. Hex/binary bit display with big/little endian byte order indexing

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
import datetime
import calendar

from version import VERSION


class CalculatorPaperAdvanced:
    def __init__(self, language='zh'):
        self.lines = []
        self.results = []
        self.variables = {}
        self.bit_display_mode = None  # 'little' or 'big' or None
        self.language = language  # 'zh' or 'en'
        
        # Undo/redo history
        self.history = []  # History states
        self.history_index = -1  # Current history position

    def set_language(self, language):
        """Set the display language"""
        self.language = language
    
    def swap_endian(self, value, byte_size=None):
        """Byte order swap function
        
        Args:
            value: Integer value to swap
            byte_size: Number of bytes (1, 2, 4, 8); auto-detected if None
            
        Returns:
            Swapped integer value
        """
        if not isinstance(value, (int, float)):
            raise ValueError("swap() 只能用于整数")
        
        value = int(value)
        if value < 0:
            raise ValueError("swap() 不支持负数")
        
        # Auto-detect byte count
        if byte_size is None:
            if value == 0:
                byte_size = 1
            else:
                # Calculate required bytes (round up to 1, 2, 4, 8)
                bit_len = value.bit_length()
                if bit_len <= 8:
                    byte_size = 1
                elif bit_len <= 16:
                    byte_size = 2
                elif bit_len <= 32:
                    byte_size = 4
                else:
                    byte_size = 8
        
        # Extract bytes and reverse
        bytes_list = []
        for i in range(byte_size):
            byte_val = (value >> (i * 8)) & 0xFF
            bytes_list.append(byte_val)
        
        # Reverse byte order
        bytes_list.reverse()
        
        # Reassemble
        result = 0
        for i, byte_val in enumerate(bytes_list):
            result |= (byte_val << (i * 8))
        
        return result

    def parse_line(self, line):
        """Parse a single line expression"""
        line = line.strip()
        if not line or line.startswith('#'):
            return None, None, None, None, False, None

        # Remove inline comments
        original_expr = line
        if '#' in line:
            line = line.split('#')[0].strip()

        # Check if hex function is used (standalone only, cannot be assigned or used in expressions)
        use_hex_func = False

        # Check if bitmap function is used (standalone only, cannot be assigned or used in expressions)
        use_bitmap = False
        bitmap_endian = None
        bitmap_width = None

        hex_pattern = r'^hex\s*\(\s*(.+?)\s*\)$'
        hex_func_match = re.match(hex_pattern, line, re.IGNORECASE)

        # Support nested parentheses, e.g. bitmap(swap(x), 1)
        # 3rd parameter is optional width
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
            
            # Set temporary byte order
            if endian_param == '1':
                bitmap_endian = 'big'
            else:  # '0' or None
                bitmap_endian = 'little'
            
            # Set bit width
            if width_param is not None:
                bitmap_width = int(width_param)
                if bitmap_width <= 0:
                    return None, None, f"错误: bitmap 宽度参数必须是正整数", None, False, None
            
            # Keep only the value expression for evaluation
            line = value_expr
            label = None
            is_assignment = False

        else:
            # Check if there is a label (e.g.: rent = 1000)
            label = None
            expr = line
            is_assignment = False

            if '=' in line:
                parts = line.split('=', 1)
                left = parts[0].strip()
                right = parts[1].strip()

                # Check if left side is a variable name (no operators)
                if re.match(r'^[a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*$', left):
                    label = left
                    expr = right
                    is_assignment = True
                    line = expr

        # Reserved keyword check (during variable assignment)
        if label and self._is_reserved_keyword(label):
            err_msg = "变量名与保留关键字冲突" if self.language == 'zh' else "Variable name conflicts with reserved keyword"
            return None, None, f"错误: {err_msg}", None, False, None

        # Detect if expression contains date/time/duration literals
        date_time_pattern = r'(?:^|(?<=[\s+\-]))(?:Y\d{8}|T\d{6}|[MWD]\d+|[hms]\d+)(?:$|(?=[\s+\-]))'
        has_date_time = bool(re.search(r'Y\d{8}|T\d{6}|(?<![a-zA-Z0-9_\u4e00-\u9fa5])[MWD]\d+(?![a-zA-Z0-9_\u4e00-\u9fa5])|(?<![a-zA-Z0-9_\u4e00-\u9fa5])[hms]\d+(?![a-zA-Z0-9_\u4e00-\u9fa5])', line))
        # Also check if any variable holds a date/time value
        has_date_time_var = False
        if not has_date_time:
            # Check if any referenced variable holds a date/time value
            var_pattern = r'\b([a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*)\b'
            for m in re.finditer(var_pattern, line):
                var_name = m.group(1)
                if var_name.lower() not in ['swap', 'bitmap', 'hex'] and var_name in self.variables:
                    val = self.variables[var_name]
                    if isinstance(val, (datetime.date, datetime.time)):
                        has_date_time = True
                        has_date_time_var = True
                        break

        if has_date_time and not use_bitmap and not use_hex_func:
            try:
                result = self._evaluate_date_time_line(line)
                # Save variable
                if label:
                    self.variables[label] = result
                return result, label, None, None, False, None
            except Exception as e:
                return None, label, f"错误: {str(e)}", None, False, None

        # Check if original expression contains hex or binary (before variable substitution)
        has_hex_bin = bool(re.search(r'0[xXbB][0-9a-fA-F]+', line))

        try:
            # Check if expression contains bitwise operators
            has_bitwise = any(op in line for op in ['<<', '>>', '&', '|', '^', '~'])

            # If expression contains bitwise ops or hex/binary, use hex format for variable substitution
            use_hex_in_comment = has_hex_bin or has_bitwise

            # Substitute variables
            expr_with_vars, undefined_vars = self._replace_variables(line, use_hex_format=use_hex_in_comment)

            # If there are undefined variables, return error
            if undefined_vars:
                return None, label, f"变量未定义: {', '.join(undefined_vars)}", None, False, None

            # Evaluate expression
            result = self.evaluate(expr_with_vars, has_hex_bin)

            # Save variable (only for non-bitmap/hex calls)
            if label and not use_bitmap and not use_hex_func:
                self.variables[label] = result

            # Return result and substituted expression (if variables were replaced)
            replaced_expr = expr_with_vars if expr_with_vars != line else None

            # Generate bit display info
            # Only show bit indices when bitmap function is used
            bit_info = None
            if use_bitmap and bitmap_endian:
                # If result is an integer value (may be float type), convert to int
                if isinstance(result, (int, float)) and result >= 0:
                    int_result = int(result)
                    if int_result == result:  # Ensure it's an integer value
                        # Detect leading zero bit width from original expression
                        input_bit_width = self._detect_input_bit_width(value_expr)
                        bit_info = self._generate_bit_display(int_result, bitmap_endian, bitmap_width, input_bit_width)

            # Generate hex display info
            hex_info = None
            if use_hex_func:
                if isinstance(result, (int, float)) and result >= 0:
                    int_result = int(result)
                    if int_result == result:
                        hex_info = f"0x{int_result:X}"

            # Return result, label, substituted expression, bit info, bitmap flag, hex info
            return result, label, replaced_expr, bit_info, use_bitmap, hex_info

        except Exception as e:
            return None, label, f"错误: {str(e)}", None, False, None

    def _replace_variables(self, expr, use_hex_format=False):
        """Replace variables in the expression

        Args:
            expr: Expression string
            use_hex_format: Whether to display variable values in hex format
        """
        # First protect hex and binary literals
        # Replace them with placeholders
        hex_bin_pattern = r'0[xXbB][0-9a-fA-F]+'
        protected = []

        def protect_hex_bin(match):
            protected.append(match.group(0))
            return f'__PROTECTED_{len(protected)-1}__'

        expr_protected = re.sub(hex_bin_pattern, protect_hex_bin, expr)

        # Find all possible variable names (Chinese, English, digits, underscores)
        # But exclude swap and bitmap function names
        pattern = r'\b([a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*)\b'

        undefined_vars = []

        def replace_func(match):
            var_name = match.group(1)
            # Skip placeholders and function names
            if var_name.startswith('__PROTECTED_') or var_name.lower() in ['swap', 'bitmap', 'hex']:
                return var_name
            # Skip date/time/duration literals (reserved keyword pattern)
            if self._is_reserved_keyword(var_name):
                return var_name

            if var_name in self.variables:
                val = self.variables[var_name]
                # If variable is date/time type, format as literal
                if isinstance(val, datetime.date) and not isinstance(val, datetime.datetime):
                    return self._format_date_result(val)
                if isinstance(val, datetime.time):
                    return self._format_date_result(val)
                # If hex format needed and value is integer
                if use_hex_format and isinstance(val, (int, float)):
                    int_val = int(val)
                    if int_val == val and int_val >= 0:
                        return f"0x{int_val:X}"

                # Otherwise use decimal format
                if isinstance(val, int):
                    return str(val)
                elif isinstance(val, float) and val == int(val):
                    # If float with integer value, convert to int
                    return str(int(val))
                return str(val)
            else:
                undefined_vars.append(var_name)
                return var_name

        result = re.sub(pattern, replace_func, expr_protected)

        # Restore hex and binary literals
        for i, literal in enumerate(protected):
            result = result.replace(f'__PROTECTED_{i}__', literal)

        return result, undefined_vars

    def _convert_percentage(self, expression):
        """Convert percentages to decimals"""
        pattern = r'(\d+\.?\d*)%'

        def replace_func(match):
            number = match.group(1)
            return str(float(number) / 100)

        return re.sub(pattern, replace_func, expression)

    def _convert_hex_bin(self, expression):
        """Convert hex and binary numbers"""
        # Hex: 0x... or 0X...
        expression = re.sub(r'0[xX]([0-9a-fA-F]+)', lambda m: str(int(m.group(1), 16)), expression)

        # Binary: 0b... or 0B...
        expression = re.sub(r'0[bB]([01]+)', lambda m: str(int(m.group(1), 2)), expression)

        return expression

    def evaluate(self, expression, has_hex_bin=False):
        """Evaluate the expression"""
        # Remove spaces
        expression = expression.replace(' ', '')

        # Check if expression is valid
        if not expression:
            raise ValueError("表达式为空")

        # Convert percentages
        expression = self._convert_percentage(expression)

        # Convert hex and binary
        expression = self._convert_hex_bin(expression)
        
        # Process swap() function calls (recursive, from inside out)
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        while 'swap(' in expression.lower() and iteration < max_iterations:
            swap_pattern = r'swap\s*\(\s*([^()]+)\s*\)'
            match = re.search(swap_pattern, expression, flags=re.IGNORECASE)
            if not match:
                break
            
            inner_expr = match.group(1)
            # Evaluate inner expression
            try:
                inner_value = eval(inner_expr)
                # Perform byte order swap
                swapped = self.swap_endian(inner_value)
                # Replace entire swap(...) with result
                expression = expression[:match.start()] + str(swapped) + expression[match.end():]
            except Exception as e:
                raise ValueError(f"swap() 函数错误: {str(e)}")
            
            iteration += 1

        # Check if expression contains bitwise operators
        has_bitwise = any(op in expression for op in ['<<', '>>', '&', '|', '^', '~'])

        # Use Python's eval for calculation
        # Allowed characters: digits, operators, parentheses
        allowed_chars = set('0123456789+-*/(). ')
        if has_bitwise:
            allowed_chars.update(['<', '>', '&', '|', '^', '~'])

        if not all(c in allowed_chars for c in expression):
            raise ValueError("包含非法字符")

        try:
            result = eval(expression)
            # If bitwise ops or hex/binary used, force integer return
            if has_bitwise or has_hex_bin:
                return int(result)
            # If result is an integer value, return integer
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
        """Align bit count to the nearest 8/16/32/64 boundary
        
        Args:
            bits: Minimum number of bits needed
            
        Returns:
            Aligned bit count (8, 16, 32, or 64)
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
            # Beyond 64 bits, align to 8-bit boundary
            return ((bits + 7) // 8) * 8

    def _parse_date_literal(self, token):
        """Parse Yyyyymmdd date literal, e.g. Y20260410 -> datetime.date(2026, 4, 10)"""
        if not isinstance(token, str):
            return None
        match = re.match(r'^Y(\d{8})$', token)
        if not match:
            return None
        digits = match.group(1)
        year = int(digits[0:4])
        month = int(digits[4:6])
        day = int(digits[6:8])
        if month < 1 or month > 12:
            return None
        max_day = calendar.monthrange(year, month)[1]
        if day < 1 or day > max_day:
            return None
        return datetime.date(year, month, day)

    def _parse_time_literal(self, token):
        """Parse Thhmmss time literal, e.g. T143000 -> datetime.time(14, 30, 0)"""
        if not isinstance(token, str):
            return None
        match = re.match(r'^T(\d{6})$', token)
        if not match:
            return None
        digits = match.group(1)
        hour = int(digits[0:2])
        minute = int(digits[2:4])
        second = int(digits[4:6])
        if hour < 0 or hour > 23:
            return None
        if minute < 0 or minute > 59:
            return None
        if second < 0 or second > 59:
            return None
        return datetime.time(hour, minute, second)

    def _parse_duration_literal(self, token):
        """Parse uppercase date duration literal Mxx/Wxx/Dxx, returns {'type': ..., 'value': int} or None"""
        if not isinstance(token, str):
            return None
        match = re.match(r'^([MWD])(\d+)$', token)
        if not match:
            return None
        prefix = match.group(1)
        value = int(match.group(2))
        if value <= 0:
            return None
        type_map = {'M': 'months', 'W': 'weeks', 'D': 'days'}
        return {'type': type_map[prefix], 'value': value}

    def _parse_time_duration_literal(self, token):
        """Parse lowercase time duration literal hxx/mxx/sxx, returns {'type': ..., 'value': int} or None"""
        if not isinstance(token, str):
            return None
        match = re.match(r'^([hms])(\d+)$', token)
        if not match:
            return None
        prefix = match.group(1)
        value = int(match.group(2))
        if value <= 0:
            return None
        type_map = {'h': 'hours', 'm': 'minutes', 's': 'seconds'}
        return {'type': type_map[prefix], 'value': value}

    def _format_date_result(self, result):
        """Format date as Yyyyymmdd, time as Thhmmss"""
        if isinstance(result, datetime.date) and not isinstance(result, datetime.datetime):
            return f"Y{result.year:04d}{result.month:02d}{result.day:02d}"
        if isinstance(result, datetime.time):
            return f"T{result.hour:02d}{result.minute:02d}{result.second:02d}"
        return str(result)

    def _is_reserved_keyword(self, name):
        """Check if identifier is a reserved keyword (Y/T/M/W/D/h/m/s followed by digits)"""
        if not isinstance(name, str):
            return False
        return bool(re.match(r'^[YTMWDhms]\d+$', name))

    def _evaluate_date_expr(self, left, op, right):
        """Evaluate date expression: date+duration, date-duration, date-date"""
        if isinstance(left, datetime.date) and isinstance(right, dict):
            # Date +/- date duration
            dur_type = right['type']
            dur_val = right['value']
            if op == '+':
                if dur_type == 'days':
                    return left + datetime.timedelta(days=dur_val)
                elif dur_type == 'weeks':
                    return left + datetime.timedelta(weeks=dur_val)
                elif dur_type == 'months':
                    month = left.month - 1 + dur_val
                    year = left.year + month // 12
                    month = month % 12 + 1
                    max_day = calendar.monthrange(year, month)[1]
                    day = min(left.day, max_day)
                    return datetime.date(year, month, day)
            elif op == '-':
                if dur_type == 'days':
                    return left - datetime.timedelta(days=dur_val)
                elif dur_type == 'weeks':
                    return left - datetime.timedelta(weeks=dur_val)
                elif dur_type == 'months':
                    month = left.month - 1 - dur_val
                    year = left.year + month // 12
                    month = month % 12 + 1
                    max_day = calendar.monthrange(year, month)[1]
                    day = min(left.day, max_day)
                    return datetime.date(year, month, day)
            raise ValueError("不支持的日期运算" if self.language == 'zh' else "Unsupported date operation")
        elif isinstance(left, datetime.date) and isinstance(right, datetime.date):
            # Date - date
            if op == '-':
                return (left - right).days
            raise ValueError("不支持的日期运算" if self.language == 'zh' else "Unsupported date operation")
        raise ValueError("不支持的日期运算" if self.language == 'zh' else "Unsupported date operation")

    def _evaluate_time_expr(self, left, op, right):
        """Evaluate time expression: time+duration, time-duration, time-time"""
        if isinstance(left, datetime.time) and isinstance(right, dict):
            # Time +/- time duration
            dur_type = right['type']
            dur_val = right['value']
            total_seconds = left.hour * 3600 + left.minute * 60 + left.second
            if dur_type == 'hours':
                delta = dur_val * 3600
            elif dur_type == 'minutes':
                delta = dur_val * 60
            elif dur_type == 'seconds':
                delta = dur_val
            else:
                raise ValueError("不支持的时间运算" if self.language == 'zh' else "Unsupported time operation")
            if op == '+':
                total_seconds += delta
            elif op == '-':
                total_seconds -= delta
            else:
                raise ValueError("不支持的时间运算" if self.language == 'zh' else "Unsupported time operation")
            if total_seconds < 0 or total_seconds > 86399:
                raise ValueError("时间溢出：结果超出一天范围" if self.language == 'zh' else "Time overflow: result exceeds 24-hour range")
            h = total_seconds // 3600
            m = (total_seconds % 3600) // 60
            s = total_seconds % 60
            return datetime.time(h, m, s)
        elif isinstance(left, datetime.time) and isinstance(right, datetime.time):
            # Time - time
            if op == '-':
                left_sec = left.hour * 3600 + left.minute * 60 + left.second
                right_sec = right.hour * 3600 + right.minute * 60 + right.second
                return left_sec - right_sec
            raise ValueError("不支持的时间运算" if self.language == 'zh' else "Unsupported time operation")
        raise ValueError("不支持的时间运算" if self.language == 'zh' else "Unsupported time operation")

    def _resolve_date_time_token(self, token):
        """Resolve a token to a date/time/duration value or variable reference.
        Returns the parsed value or raises ValueError."""
        token = token.strip()
        # Try date literal
        d = self._parse_date_literal(token)
        if d is not None:
            return d
        # Try time literal
        t = self._parse_time_literal(token)
        if t is not None:
            return t
        # Try date duration (uppercase M/W/D)
        dur = self._parse_duration_literal(token)
        if dur is not None:
            return dur
        # Try time duration (lowercase h/m/s)
        tdur = self._parse_time_duration_literal(token)
        if tdur is not None:
            return tdur
        # Try variable reference
        if re.match(r'^[a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*$', token):
            if token in self.variables:
                return self.variables[token]
            raise ValueError(f"变量未定义: {token}" if self.language == 'zh' else f"Undefined variable: {token}")
        # Try numeric literal - return as number (will be caught by type checking)
        if re.match(r'^\d+(\.\d+)?$', token):
            val = float(token) if '.' in token else int(token)
            return val
        raise ValueError(f"无法解析: {token}" if self.language == 'zh' else f"Cannot parse: {token}")

    def _evaluate_date_time_line(self, expr):
        """Parse and evaluate a date/time expression like 'Y20260410 + D10' or 'start + h3 + m30'."""
        expr = expr.strip()
        # Tokenize: split by + and - while keeping the operators
        # We need to handle chained operations like: start + h3 + m30
        tokens = re.split(r'\s*(\+|\-)\s*', expr)
        # tokens is like ['Y20260410', '+', 'D10'] or ['start', '+', 'h3', '+', 'm30']
        
        if not tokens:
            raise ValueError("表达式为空" if self.language == 'zh' else "Empty expression")
        
        # Resolve the first token
        result = self._resolve_date_time_token(tokens[0])
        
        # If it's just a single token (no operator), return it
        if len(tokens) == 1:
            return result
        
        # Process operator-operand pairs
        i = 1
        while i < len(tokens):
            if i + 1 >= len(tokens):
                raise ValueError("表达式语法错误" if self.language == 'zh' else "Expression syntax error")
            op = tokens[i]
            right = self._resolve_date_time_token(tokens[i + 1])
            
            # Type checking and dispatch
            if isinstance(result, datetime.date):
                if isinstance(right, (int, float)) and not isinstance(right, bool):
                    raise ValueError("日期不能与数值直接运算" if self.language == 'zh' else "Cannot mix date and numeric operations")
                if isinstance(right, dict) and right['type'] in ('hours', 'minutes', 'seconds'):
                    raise ValueError("时间时长不能与日期运算" if self.language == 'zh' else "Cannot use time duration with date")
                if isinstance(right, datetime.time):
                    raise ValueError("不支持的日期运算" if self.language == 'zh' else "Unsupported date operation")
                if isinstance(right, datetime.date):
                    if op == '+':
                        raise ValueError("不支持的日期运算" if self.language == 'zh' else "Unsupported date operation")
                    result = self._evaluate_date_expr(result, op, right)
                elif isinstance(right, dict):
                    result = self._evaluate_date_expr(result, op, right)
                else:
                    raise ValueError("不支持的日期运算" if self.language == 'zh' else "Unsupported date operation")
            elif isinstance(result, datetime.time):
                if isinstance(right, (int, float)) and not isinstance(right, bool):
                    raise ValueError("日期不能与数值直接运算" if self.language == 'zh' else "Cannot mix date and numeric operations")
                if isinstance(right, dict) and right['type'] in ('months', 'weeks', 'days'):
                    raise ValueError("日期时长不能与时间运算" if self.language == 'zh' else "Cannot use date duration with time")
                if isinstance(right, datetime.date):
                    raise ValueError("不支持的时间运算" if self.language == 'zh' else "Unsupported time operation")
                if isinstance(right, datetime.time):
                    if op == '+':
                        raise ValueError("不支持的时间运算" if self.language == 'zh' else "Unsupported time operation")
                    result = self._evaluate_time_expr(result, op, right)
                elif isinstance(right, dict):
                    result = self._evaluate_time_expr(result, op, right)
                else:
                    raise ValueError("不支持的时间运算" if self.language == 'zh' else "Unsupported time operation")
            elif isinstance(result, (int, float)):
                # Numeric result from previous operation (e.g., date-date=days), can't do more date ops
                raise ValueError("不支持的运算" if self.language == 'zh' else "Unsupported operation")
            else:
                raise ValueError("不支持的运算" if self.language == 'zh' else "Unsupported operation")
            
            i += 2
        
        return result

    def _detect_input_bit_width(self, expr):
        """Detect bit width from input expression (based on leading zeros)
        
        Examples: 0x00FF -> 16 bits (4 hex chars x 4 bits)
                  0b00001111 -> 8 bits (8 bin chars)
                  0xFF -> 8 bits (2 hex chars x 4 bits)
        
        Returns:
            Detected bit width, or None if not detectable
        """
        expr = expr.strip()
        
        # First check if it's a variable reference; if so, look up original assignment
        # Here we only handle direct literals
        
        # Check hex literal
        hex_match = re.match(r'^0[xX]([0-9a-fA-F]+)$', expr)
        if hex_match:
            hex_digits = hex_match.group(1)
            return len(hex_digits) * 4  # 4 bits per hex char
        
        # Check binary literal
        bin_match = re.match(r'^0[bB]([01]+)$', expr)
        if bin_match:
            bin_digits = bin_match.group(1)
            return len(bin_digits)
        
        return None

    def _generate_bit_display(self, value, endian_mode, user_width=None, input_bit_width=None):
        """Generate bit display information
        
        Args:
            value: Integer value to display
            endian_mode: Byte order mode ('big' or 'little')
            user_width: User-specified bit width (8, 16, 32, 64), optional
            input_bit_width: Bit width detected from input expression (preserving leading zeros), optional
        """
        if not isinstance(value, int) or value < 0:
            return None

        # Determine minimum bits needed
        if value == 0:
            min_bits = 8
        else:
            min_bits = value.bit_length()

        # Determine final bit count
        if user_width is not None:
            # User explicitly specified width
            bit_count = user_width
            if bit_count < min_bits:
                # Width insufficient, auto-expand to minimum width that fits the value
                bit_count = self._align_to_boundary(min_bits)
        elif input_bit_width is not None:
            # Use bit width detected from input expression (preserving leading zeros)
            # Align to nearest 8/16/32/64 boundary
            bit_count = self._align_to_boundary(max(min_bits, input_bit_width))
        else:
            # Default: align to nearest 8/16/32/64 boundary
            bit_count = self._align_to_boundary(min_bits)

        # Generate binary string (MSB to LSB, preserving leading zeros)
        bin_str = format(value, f'0{bit_count}b')

        result_lines = []
        
        # Select text based on language
        if self.language == 'en':
            # Hex representation with leading zeros
            hex_width = bit_count // 4
            result_lines.append(f"  Hexadecimal: 0x{value:0{hex_width}X}")
            result_lines.append(f"  Binary: 0b{bin_str}")
            result_lines.append(f"  Bits: {bit_count} bits ({bit_count // 8} bytes)")
        else:
            # Hex representation with leading zeros
            hex_width = bit_count // 4
            result_lines.append(f"  十六进制: 0x{value:0{hex_width}X}")
            result_lines.append(f"  二进制: 0b{bin_str}")
            result_lines.append(f"  位数: {bit_count} bits ({bit_count // 8} bytes)")

        # Generate bit index table
        if endian_mode == 'big':
            # Big endian: MSB (most significant bit) indexed from 0
            # Bit indices left to right: 0, 1, 2, ..., 31
            if self.language == 'en':
                result_lines.append("  Bit indices (Big Endian):")
            else:
                result_lines.append("  位索引 (大端字节序):")

            index_parts = []
            bit_parts = []

            # Display MSB to LSB (bin_str left to right)
            for i in range(0, bit_count, 4):
                # 4 bits per group
                nibble_bits = bin_str[i:i+4]

                # Big endian: MSB starts at 0, left to right 0->31
                indices = [str(i + j) for j in range(4)]
                bits = list(nibble_bits)

                # Calculate max width for this group
                max_width = max(len(idx) for idx in indices)

                # Format indices (right-aligned)
                formatted_indices = [f"{idx:>{max_width}}" for idx in indices]
                # Format bit values (right-aligned, matching index width)
                formatted_bits = [f"{bit:>{max_width}}" for bit in bits]

                index_parts.append('|' + ' '.join(formatted_indices) + ' ')
                bit_parts.append('|' + ' '.join(formatted_bits) + ' ')

            # Add closing delimiter
            index_parts.append('|')
            bit_parts.append('|')

            # Output
            result_lines.append('    ' + ''.join(index_parts))
            result_lines.append('    ' + ''.join(bit_parts))

        elif endian_mode == 'little':
            # Little endian: LSB (least significant bit) indexed from 0
            # Bit indices right to left: ..., 2, 1, 0
            # But displayed left to right: 31, 30, ..., 1, 0
            if self.language == 'en':
                result_lines.append("  Bit indices (Little Endian):")
            else:
                result_lines.append("  位索引 (小端字节序):")

            index_parts = []
            bit_parts = []

            # Display MSB to LSB (bin_str left to right)
            for i in range(0, bit_count, 4):
                # 4 bits per group
                nibble_bits = bin_str[i:i+4]

                # Little endian: LSB starts at 0, displayed left to right 31->0
                indices = [str(bit_count - 1 - i - j) for j in range(4)]
                bits = list(nibble_bits)

                # Calculate max width for this group
                max_width = max(len(idx) for idx in indices)

                # Format indices (right-aligned)
                formatted_indices = [f"{idx:>{max_width}}" for idx in indices]
                # Format bit values (right-aligned, matching index width)
                formatted_bits = [f"{bit:>{max_width}}" for bit in bits]

                index_parts.append('|' + ' '.join(formatted_indices) + ' ')
                bit_parts.append('|' + ' '.join(formatted_bits) + ' ')

            # Add closing delimiter
            index_parts.append('|')
            bit_parts.append('|')

            # Output
            result_lines.append('    ' + ''.join(index_parts))
            result_lines.append('    ' + ''.join(bit_parts))

        return '\n'.join(result_lines)

    def process_text(self, text):
        """Process multi-line text"""
        self.lines = []
        self.results = []
        self.variables = {}

        lines = text.strip().split('\n')

        for line in lines:
            original_line = line.strip()

            # Empty line
            if not original_line:
                self.lines.append('')
                self.results.append(None)
                continue

            # Comment line
            if original_line.startswith('#'):
                self.lines.append(original_line)
                self.results.append(None)
                continue

            # Parse expression
            result, label, extra_info, bit_info, use_bitmap, hex_info = self.parse_line(line)

            self.lines.append(original_line)

            if result is not None:
                # Calculation succeeded
                self.results.append((result, label, extra_info, bit_info, use_bitmap, hex_info))
            else:
                # Calculation failed or special command
                self.results.append((None, label, extra_info, bit_info, use_bitmap, hex_info))
        
        # Save current state to history
        self.save_state()
    
    def save_state(self):
        """Save current state to history"""
        # If not at end of history, truncate future states
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        # Save current state
        state = {
            'lines': self.lines.copy(),
            'results': self.results.copy(),
            'variables': self.variables.copy()
        }
        self.history.append(state)
        self.history_index = len(self.history) - 1
        
        # Limit history size (max 50 states)
        if len(self.history) > 50:
            self.history.pop(0)
            self.history_index -= 1
    
    def undo(self):
        """Undo to previous state"""
        if self.history_index > 0:
            self.history_index -= 1
            state = self.history[self.history_index]
            self.lines = state['lines'].copy()
            self.results = state['results'].copy()
            self.variables = state['variables'].copy()
            return True
        return False
    
    def redo(self):
        """Redo to next state"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            state = self.history[self.history_index]
            self.lines = state['lines'].copy()
            self.results = state['results'].copy()
            self.variables = state['variables'].copy()
            return True
        return False
    
    def can_undo(self):
        """Check if undo is available"""
        return self.history_index > 0
    
    def can_redo(self):
        """Check if redo is available"""
        return self.history_index < len(self.history) - 1

    def format_output(self):
        """Format the output results"""
        output = []
        max_line_len = max(len(line) for line in self.lines) if self.lines else 0

        for line, result_info in zip(self.lines, self.results):
            # Empty line
            if not line:
                output.append('')
                continue

            # Comment line
            if line.startswith('#'):
                output.append(line)
                continue

            # No result info
            if result_info is None:
                output.append(line)
                continue

            result, label, extra_info, bit_info, use_bitmap, hex_info = result_info

            if result is None:
                # Calculation failed or special command, show info
                if extra_info:
                    output.append(f"{line}  # {extra_info}")
                else:
                    output.append(line)
            else:
                # Format number
                if hex_info:
                    # hex() function: display hex
                    result_str = hex_info
                elif isinstance(result, datetime.date) and not isinstance(result, datetime.datetime):
                    result_str = self._format_date_result(result)
                elif isinstance(result, datetime.time):
                    result_str = self._format_date_result(result)
                elif isinstance(result, int):
                    # Integer
                    if use_bitmap:
                        # bitmap function: show decimal only
                        result_str = str(result)
                    else:
                        # No bitmap: show decimal only
                        result_str = str(result)
                elif result == int(result):
                    result_str = str(int(result))
                else:
                    result_str = f"{result:.2f}"

                padding = ' ' * (max_line_len - len(line) + 2)

                # bitmap call: don't show assignment, only result
                if use_bitmap:
                    # If variable substitution occurred, show substituted expression
                    if extra_info:
                        output.append(f"{line}{padding}= {result_str}  # {extra_info}")
                    else:
                        output.append(f"{line}{padding}= {result_str}")
                else:
                    # Normal calculation, show assignment
                    if extra_info:
                        output.append(f"{line}{padding}= {result_str}  # {extra_info}")
                    else:
                        output.append(f"{line}{padding}= {result_str}")

                # If bit display info exists, append to output
                if bit_info:
                    output.append(bit_info)

        return '\n'.join(output)


def main():
    """Main function"""
    # Parse command line arguments
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

    # Display different interface based on language
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
