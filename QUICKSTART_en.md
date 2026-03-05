# Quick Start

## Get Started with CalcPaper in 5 Minutes

### 1. Run the Program

```bash
# GUI version (recommended for beginners)
python calc_paper_gui.py

# Command-line version
python calc_paper.py --lang en
```

### 2. Basic Usage

Enter in the input area:

```python
# Simple calculation
a = 100
b = 200
sum = a + b
```

Click "Calculate" button (or press F5) to see results.

### 3. Bitwise Operations

```python
# Hexadecimal operations
x = 0xFF
y = 0x0F
and_result = x & y
```

### 4. View Bit Structure

```python
# Use bitmap function (big endian)
view = bitmap(0xFF, 1)
```

### 5. Keyboard Shortcuts

- F5: Calculate
- Ctrl+D: Clear
- Ctrl+L: Load example
- Ctrl+Plus: Increase font
- Ctrl+Minus: Decrease font

### 6. Toggle Language

Click the "中文" button on the interface to switch to Chinese.

## More Resources

- [User Guide](docs/User-Guide.md)
- [Bitwise Operations Reference](docs/Bitwise-Operations-Reference.md)
- [Hex Comment Format](docs/Hex-Comment-Format.md)
- [bitmap Function Guide](docs/bitmap-Function-Guide.md)
- [Example Files](examples/)

## FAQ

### Q: How to check version?

```bash
python calc_paper.py --version
```

### Q: How to switch language?

**GUI**: Click "EN" or "中文" button

**Command Line**: Use `--lang` parameter

```bash
python calc_paper.py --lang en
```

### Q: How to save results?

**GUI**: Click "Save Result" button or press Ctrl+S

### Q: What number formats are supported?

- Decimal: `123`, `456.78`
- Hexadecimal: `0xFF`, `0x1A2B`
- Binary: `0b1010`, `0b11110000`
- Percentage: `15%`, `6.5%`

### Q: How to view detailed bit structure?

Use `bitmap()` function:

```python
# Little endian (default)
view = bitmap(0xFF)

# Big endian
view = bitmap(0xFF, 1)
```

### Q: How to use bitmap function?

```python
# Syntax
bitmap(value)        # Little endian (default)
bitmap(value, 0)     # Little endian (explicit)
bitmap(value, 1)     # Big endian

# Example
a = 0xFF
view_a = bitmap(a, 1)
```

### Q: What operators are supported?

**Arithmetic Operators**:
- `+` Addition
- `-` Subtraction
- `*` Multiplication
- `/` Division
- `%` Modulo

**Bitwise Operators**:
- `&` Bitwise AND
- `|` Bitwise OR
- `^` Bitwise XOR
- `<<` Left shift
- `>>` Right shift

## Example Demonstrations

### Basic Calculation Example

```python
# Salary calculation
salary = 8000
rent = 2000
food = 30 * 25
balance = salary - rent - food
```

### Bitwise Operation Example

```python
# RGB color extraction
color = 0xFF8040
red = (color >> 16) & 0xFF
green = (color >> 8) & 0xFF
blue = color & 0xFF

# View bit structure (big endian)
view_color = bitmap(color, 1)
```

### Percentage Calculation Example

```python
# Discount calculation
original_price = 100
discount_rate = 15%
discount_amount = original_price * discount_rate
final_price = original_price - discount_amount
```

## Next Steps

1. Read the [complete User Guide](docs/User-Guide.md)
2. Try more examples in [example files](examples/)
3. Explore advanced features like bitmap visualization
4. Learn bitwise operation techniques

Enjoy using CalcPaper!