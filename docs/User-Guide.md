# CalcPaper User Guide

Version: 1.0

## Table of Contents

- [Introduction](#introduction)
- [Installation & Running](#installation--running)
- [Basic Features](#basic-features)
- [Advanced Features](#advanced-features)
- [GUI Usage](#gui-usage)
- [Command Line Usage](#command-line-usage)
- [FAQ](#faq)

## Introduction

CalcPaper is a smart calculator designed for programmers, supporting variable references, bitwise operations, hexadecimal/binary numbers, making complex calculations as simple as writing on paper.

## Installation & Running

### System Requirements

- Python 3.6+
- tkinter (included with Python, required for GUI)

### How to Run

```bash
# GUI version (recommended)
python calc_paper_gui.py

# Command-line version (Chinese)
python calc_paper.py

# Command-line version (English)
python calc_paper.py --lang en

# Check version
python calc_paper.py --version

# Show help
python calc_paper.py --help
```

## Basic Features

### 1. Arithmetic Operations

```python
# Basic operations
a = 100
b = 200
sum = a + b
diff = b - a
product = a * b
quotient = b / a
```

### 2. Variable References

```python
# Use variables after definition
salary = 8000
rent = 2000
food = 30 * 25
balance = salary - rent - food
```

### 3. Percentage Calculations

```python
# Use percentage directly
price = 299
discount = 20%
final_price = price * (1 - discount)

# Or
discount_amount = price * discount
pay = price - discount_amount
```

### 4. Comments

```python
# This is a comment, won't be calculated
price = 100  # Inline comments are also supported
```

## Advanced Features

### 1. Hexadecimal Numbers

```python
# Use 0x prefix
a = 0xFF        # 255
b = 0x1A2B      # 6699
c = 0xDEADBEEF  # 3735928559
```

### 2. Binary Numbers

```python
# Use 0b prefix
flag1 = 0b1010      # 10
flag2 = 0b11110000  # 240
```

### 3. Bitwise Operations

```python
# Left shift <<
a = 0b1010
left_shift_2 = a << 2  # 0b101000 = 40

# Right shift >>
b = 0xFF
right_shift_4 = b >> 4  # 0x0F = 15

# Bitwise AND &
and_result = 0xFF & 0x0F  # 0x0F = 15

# Bitwise OR |
or_result = 0xF0 | 0x0F  # 0xFF = 255

# Bitwise XOR ^
xor_result = 0xFF ^ 0xAA  # 0x55 = 85

# Bitwise NOT ~
not_result = ~0b1010  # -11 (two's complement)
```

### 4. Endianness Display

```python
# Set little endian
endian: little

# Set big endian
endian: big

# Disable endianness display
endian: none
```

### 5. bitmap Keyword

Use `bitmap` keyword to view detailed bit structure:

```python
# Set endianness
endian: big

# Normal calculation (decimal only)
a = 0xFF

# View bit structure with bitmap
bitmap view_a = a
```

Output:
```
a = 0xFF                    = 255
bitmap view_a = a           = 255 (0xFF, 0b11111111)
  Hexadecimal: 0xFF
  Binary: 0b11111111
  Bits: 8 bits (1 bytes)
  Bit indices (Big Endian):
    |7 6 5 4 |3 2 1 0 |
    |1 1 1 1 |1 1 1 1 |
```

## GUI Usage

### Interface Layout

- Left: Input area
- Right: Output area (with syntax highlighting)
- Bottom: Function buttons and status bar

### Keyboard Shortcuts

- `F5` or `Ctrl+Enter`: Calculate
- `Ctrl+D`: Clear
- `Ctrl+L`: Load example
- `Ctrl+O`: Open file
- `Ctrl+S`: Save result
- `Ctrl+Plus` or `Ctrl+=`: Increase font size
- `Ctrl+Minus` or `Ctrl+-`: Decrease font size

### Function Buttons

- **Calculate**: Execute calculation and display results
- **Clear**: Clear input and output areas
- **Load Example**: Load preset example
- **Open File**: Load calculation content from file
- **Save Result**: Save results to file
- **EN/中文**: Toggle language
- **A+**: Increase font size
- **A-**: Decrease font size

### Syntax Highlighting

Output area automatically applies syntax highlighting:

- Green: Calculation results
- Gray: Comments
- Red: Error messages
- Blue: Totals
- Purple: Endianness settings
- Dark blue: Bit information

## Command Line Usage

### Interactive Mode

```bash
# Start program
python calc_paper.py

# Enter calculation content (multiple lines)
a = 100
b = 200
sum = a + b

# Type calc to start calculation
calc

# Continue or type exit to quit
```

### Command Line Arguments

```bash
# Use English interface
python calc_paper.py --lang en

# Check version
python calc_paper.py --version

# Show help
python calc_paper.py --help
```

### Special Commands

- `calc`: Start calculation
- `clear`: Clear input
- `exit` or `quit`: Exit program

## FAQ

### 1. How to view bit structure of a variable?

Use `bitmap` keyword:

```python
endian: big
bitmap variable_name = expression
```

### 2. Why does bitwise NOT result in negative numbers?

Bitwise NOT `~` produces negative numbers (two's complement). For positive results, use a mask:

```python
a = 0b1010
not_result = ~a & 0xFF  # Limit to 8-bit range
```

### 3. How to switch endianness?

Use `endian` command:

```python
endian: little  # Little endian
endian: big     # Big endian
endian: none    # Disable
```

### 4. What number formats are supported?

- Decimal: `123`, `456.78`
- Hexadecimal: `0xFF`, `0x1A2B`
- Binary: `0b1010`, `0b11110000`
- Percentage: `15%`, `6.5%`

### 5. Can I use Unicode in variable names?

Yes! Supports combinations of Unicode characters, English, numbers, and underscores:

```python
price = 100
discount = 15%
final = price * (1 - discount)
```

### 6. How to save calculation results?

GUI version: Click "Save Result" button or press `Ctrl+S`

Command-line version: Use redirection
```bash
python calc_paper.py < input.txt > output.txt
```

### 7. How to increase/decrease font size?

GUI version:
- Click A+ / A- buttons
- Or use shortcuts `Ctrl+Plus` / `Ctrl+Minus`

### 8. How to switch language?

GUI version: Click "EN" or "中文" button

Command-line version: Use `--lang` parameter
```bash
python calc_paper.py --lang en
```

## Practical Examples

### RGB Color Processing

```python
endian: big

# Color value
color = 0xFF8040

# Extract RGB components
red = (color >> 16) & 0xFF
green = (color >> 8) & 0xFF
blue = color & 0xFF

# View bit structure
bitmap view_color = color
```

### IP Address Parsing

```python
# IP address 192.168.0.1
IP = 0xC0A80001

# Extract segments
seg1 = (IP >> 24) & 0xFF  # 192
seg2 = (IP >> 16) & 0xFF  # 168
seg3 = (IP >> 8) & 0xFF   # 0
seg4 = IP & 0xFF          # 1
```

### Bit Flag Management

```python
# Define flags
FLAG_READ = 0b0001
FLAG_WRITE = 0b0010
FLAG_EXECUTE = 0b0100
FLAG_DELETE = 0b1000

# Combine permissions
permission = FLAG_READ | FLAG_WRITE

# Check permissions
has_read = permission & FLAG_READ
has_execute = permission & FLAG_EXECUTE
```

### Financial Calculations

```python
# Monthly budget
salary = 8000
rent = 2000
utilities = 300
food = 30 * 25
transport = 200

# Total expenses
total_expenses = rent + utilities + food + transport

# Balance
balance = salary - total_expenses

# Savings rate
savings_rate = balance / salary * 100%
```

## Tips & Best Practices

1. **Use meaningful variable names**: Make calculations clearer
2. **Add comments**: Explain calculation purpose and logic
3. **Use bitmap wisely**: Only when you need to view bit structure
4. **Choose appropriate endianness**: Based on actual application
5. **Save common calculations**: Save frequently used calculations as files

## More Resources

- [Bitwise Operations Quick Reference](Bitwise-Operations-Reference.md)
- [Hex Comment Format](Hex-Comment-Format.md)
- [bitmap Keyword Guide](bitmap-Keyword-Guide.md)
