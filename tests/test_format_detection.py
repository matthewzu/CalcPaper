"""
Unit tests for OutputFormat enum and detect_output_format() function.

Tests the auto-detection of output format based on expression literals.
Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calc_paper import OutputFormat, detect_output_format, CalculatorPaperAdvanced


class TestOutputFormatEnum:
    """Tests for the OutputFormat enum definition."""

    def test_enum_values(self):
        assert OutputFormat.DECIMAL.value == 'decimal'
        assert OutputFormat.HEXADECIMAL.value == 'hex'
        assert OutputFormat.BINARY.value == 'binary'

    def test_enum_members(self):
        members = list(OutputFormat)
        assert len(members) == 3
        assert OutputFormat.DECIMAL in members
        assert OutputFormat.HEXADECIMAL in members
        assert OutputFormat.BINARY in members


class TestDetectOutputFormat:
    """Tests for the detect_output_format() function."""

    # Requirement 11.5: Explicit hex() function takes priority
    def test_explicit_hex_func_priority(self):
        """Explicit hex() function should always return HEXADECIMAL."""
        assert detect_output_format('255', True) == OutputFormat.HEXADECIMAL
        assert detect_output_format('0b1010', True) == OutputFormat.HEXADECIMAL
        assert detect_output_format('100 + 200', True) == OutputFormat.HEXADECIMAL

    # Requirement 11.1: Hex literal → hex output
    def test_hex_literal_detection(self):
        """Expression with hex literal should return HEXADECIMAL."""
        assert detect_output_format('0xFF + 1', False) == OutputFormat.HEXADECIMAL
        assert detect_output_format('0x1A2B', False) == OutputFormat.HEXADECIMAL
        assert detect_output_format('0X00FF', False) == OutputFormat.HEXADECIMAL

    # Requirement 11.2: Binary literal → binary output
    def test_binary_literal_detection(self):
        """Expression with binary literal should return BINARY."""
        assert detect_output_format('0b1010 + 1', False) == OutputFormat.BINARY
        assert detect_output_format('0B11110000', False) == OutputFormat.BINARY
        assert detect_output_format('0b0001', False) == OutputFormat.BINARY

    # Requirement 11.3: Both hex and binary → hex output
    def test_hex_and_binary_returns_hex(self):
        """Expression with both hex and binary should return HEXADECIMAL."""
        assert detect_output_format('0xFF + 0b1010', False) == OutputFormat.HEXADECIMAL
        assert detect_output_format('0b1010 + 0xFF', False) == OutputFormat.HEXADECIMAL

    # Requirement 11.4: No special literals → decimal output
    def test_no_special_literals_returns_decimal(self):
        """Expression without hex/binary literals should return DECIMAL."""
        assert detect_output_format('100 + 200', False) == OutputFormat.DECIMAL
        assert detect_output_format('a + b', False) == OutputFormat.DECIMAL
        assert detect_output_format('3.14 * 2', False) == OutputFormat.DECIMAL


class TestParseLineIntegration:
    """Tests for the integration of detect_output_format into parse_line."""

    def setup_method(self):
        self.calc = CalculatorPaperAdvanced()

    # Requirement 11.1: hex literal → hex output
    def test_hex_literal_produces_hex_output(self):
        result, label, extra, bit_info, use_bitmap, hex_info = self.calc.parse_line('0xFF + 1')
        assert result == 256
        assert hex_info == '0x100'

    # Requirement 11.2: binary literal → binary output
    def test_binary_literal_produces_binary_output(self):
        result, label, extra, bit_info, use_bitmap, hex_info = self.calc.parse_line('0b1010 + 1')
        assert result == 11
        assert hex_info == '0b1011'

    # Requirement 11.3: both hex and binary → hex output
    def test_both_hex_binary_produces_hex_output(self):
        result, label, extra, bit_info, use_bitmap, hex_info = self.calc.parse_line('0xFF + 0b1010')
        assert result == 265
        assert hex_info == '0x109'

    # Requirement 11.4: no special literals → decimal output
    def test_no_literals_produces_decimal_output(self):
        result, label, extra, bit_info, use_bitmap, hex_info = self.calc.parse_line('100 + 200')
        assert hex_info is None

    # Requirement 11.5: explicit hex() takes priority
    def test_explicit_hex_func_takes_priority(self):
        result, label, extra, bit_info, use_bitmap, hex_info = self.calc.parse_line('hex(255)')
        assert result == 255
        assert hex_info == '0xFF'

    def test_variable_assignment_with_hex_literal(self):
        """Variable assignment with hex literal should show hex output."""
        result, label, extra, bit_info, use_bitmap, hex_info = self.calc.parse_line('a = 0xFF')
        assert result == 255
        assert label == 'a'
        assert hex_info == '0xFF'

    def test_bitmap_not_affected(self):
        """bitmap() function should not be affected by auto-detection."""
        result, label, extra, bit_info, use_bitmap, hex_info = self.calc.parse_line('bitmap(0xFF, 1)')
        assert use_bitmap is True
        assert hex_info is None

    def test_comma_not_affected(self):
        """comma() function should not be affected by auto-detection."""
        result, label, extra, bit_info, use_bitmap, hex_info = self.calc.parse_line('comma(59200)')
        assert hex_info == '59,200'

    def test_date_not_affected(self):
        """Date expressions should not be affected by auto-detection."""
        result, label, extra, bit_info, use_bitmap, hex_info = self.calc.parse_line('Y20260410 + D10')
        assert hex_info is None

    def test_format_output_shows_hex(self):
        """format_output should display hex format for hex literal expressions."""
        self.calc.process_text('a = 0xFF + 1')
        output = self.calc.format_output()
        assert '0x100' in output

    def test_format_output_shows_binary(self):
        """format_output should display binary format for binary literal expressions."""
        self.calc.process_text('b = 0b1010 | 0b0101')
        output = self.calc.format_output()
        assert '0b1111' in output
