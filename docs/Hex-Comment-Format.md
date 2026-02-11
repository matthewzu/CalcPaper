# Hexadecimal Comment Format

Version: 1.0

## Overview

CalcPaper automatically displays variable values in hexadecimal format in comments when processing expressions containing bitwise operations or hexadecimal/binary numbers, making bitwise operation processes clearer and easier to understand.

## Automatic Hexadecimal Comments

### Trigger Conditions

Variable values are displayed in hexadecimal format in comments when the expression meets any of the following conditions:

1. Expression contains hexadecimal numbers (0x...)
2. Expression contains binary numbers (0b...)
3. Expression contains bitwise operators (<<, >>, &, |, ^, ~)

### Examples

#### Example 1: Contains Hexadecimal Numbers

```python
# Input
a = 0xFF
b = 0x10
sum = a + b
```

```python
# Output
a = 0xFF        = 255
b = 0x10        = 16
sum = a + b     = 271  # 0xFF + 0x10
```

#### Example 2: Contains Bitwise Operations

```python
# Input
x = 255
y = 15
and_result = x & y
```

```python
# Output
x = 255                  = 255
y = 15                   = 15
and_result = x & y       = 15  # 0xFF & 0xF
```

#### Example 3: Mixed Operations

```python
# Input
color = 0xFF8040
red = (color >> 16) & 0xFF
green = (color >> 8) & 0xFF
blue = color & 0xFF
```

```python
# Output
color = 0xFF8040                = 16744512
red = (color >> 16) & 0xFF      = 255  # 0xFF8040 >> 16 & 0xFF
green = (color >> 8) & 0xFF     = 128  # 0xFF8040 >> 8 & 0xFF
blue = color & 0xFF             = 64   # 0xFF8040 & 0xFF
```

## Comment Format Rules

### 1. Variable Substitution

When variables are referenced in expressions, comments show the complete expression after substitution:

```python
# Input
a = 0xFF
b = 0x0F
result = a & b
```

```python
# Output
a = 0xFF           = 255
b = 0x0F           = 15
result = a & b     = 15  # 0xFF & 0xF
```

### 2. Hexadecimal Format

- Positive integers: Uppercase hexadecimal format (0xFF)
- Negative integers: Decimal format
- Floating-point: Decimal format

```python
# Input
positive = 255
negative = -10
decimal = 3.14
bitwise = positive >> 4
```

```python
# Output
positive = 255           = 255
negative = -10           = -10
decimal = 3.14           = 3.14
bitwise = positive >> 4  = 15  # 0xFF >> 4
```

### 3. Complex Expressions

For complex expressions, comments show the complete result after all variable substitutions:

```python
# Input
a = 0xFF
b = 0x0F
c = 0xF0
complex = (a & b) | (a & c)
```

```python
# Output
a = 0xFF                     = 255
b = 0x0F                     = 15
c = 0xF0                     = 240
complex = (a & b) | (a & c)  = 255  # (0xFF & 0xF) | (0xFF & 0xF0)
```

## Cases Without Hexadecimal Comments

### 1. Pure Arithmetic Operations

Expressions without hexadecimal, binary, or bitwise operations won't show hexadecimal comments:

```python
# Input
a = 100
b = 200
sum = a + b
```

```python
# Output
a = 100        = 100
b = 200        = 200
sum = a + b    = 300  # 100 + 200 (decimal)
```

### 2. Percentage Calculations

```python
# Input
price = 100
discount = 15%
final = price * (1 - discount)
```

```python
# Output
price = 100                  = 100
discount = 15%               = 0.15
final = price * (1 - discount) = 85.00  # 100 * (1 - 0.15)
```

## Difference from bitmap Keyword

### Hexadecimal Comments

- Automatically triggered
- Displayed in end-of-line comments
- Only shows substituted expression
- No bit structure display

```python
a = 0xFF
b = a & 0x0F  # Automatically shows: 0xFF & 0xF
```

### bitmap Keyword

- Requires explicit use
- Displayed in separate multi-line output
- Shows detailed bit structure information
- Includes hexadecimal, binary, and bit indices

```python
endian: big
bitmap view = 0xFF
# Output:
# Hexadecimal: 0xFF
# Binary: 0b11111111
# Bits: 8 bits (1 bytes)
# Bit index table...
```

## Practical Scenarios

### Scenario 1: Debugging Bitwise Operations

```python
# Input
mask = 0xFF00
data = 0xABCD
extract_high = data & mask
```

```python
# Output
mask = 0xFF00                = 65280
data = 0xABCD                = 43981
extract_high = data & mask   = 43776  # 0xABCD & 0xFF00
```

From the comment, you can clearly see: 0xABCD & 0xFF00 = 0xAB00 (43776)

### Scenario 2: RGB Color Calculation

```python
# Input
R = 0xFF
G = 0x80
B = 0x40
color = (R << 16) | (G << 8) | B
```

```python
# Output
R = 0xFF                        = 255
G = 0x80                        = 128
B = 0x40                        = 64
color = (R << 16) | (G << 8) | B = 16744512  # (0xFF << 16) | (0x80 << 8) | 0x40
```

### Scenario 3: Network Protocol Parsing

```python
# Input
packet = 0x12345678
type = (packet >> 24) & 0xFF
version = (packet >> 16) & 0xFF
length = (packet >> 8) & 0xFF
flags = packet & 0xFF
```

```python
# Output
packet = 0x12345678              = 305419896
type = (packet >> 24) & 0xFF     = 18   # 0x12345678 >> 24 & 0xFF
version = (packet >> 16) & 0xFF  = 52   # 0x12345678 >> 16 & 0xFF
length = (packet >> 8) & 0xFF    = 86   # 0x12345678 >> 8 & 0xFF
flags = packet & 0xFF            = 120  # 0x12345678 & 0xFF
```

## Configuration Options

Currently, hexadecimal comment format is automatic and requires no configuration. Future versions may add options such as:

- Force all variables to use hexadecimal format
- Custom hexadecimal format (uppercase/lowercase)
- Control comment detail level

## Best Practices

1. **Use hexadecimal literals**: When working with bitwise operations, use hexadecimal literals (0xFF) instead of decimal (255) for clearer comments

2. **Meaningful variable names**: Use descriptive variable names combined with hexadecimal comments for better readability

3. **Step-by-step calculations**: Break complex bitwise operations into multiple steps, each with clear comments

4. **Combine with bitmap**: For cases requiring detailed bit structure view, use the bitmap keyword

## Related Documentation

- [User Guide](User-Guide.md)
- [Bitwise Operations Reference](Bitwise-Operations-Reference.md)
- [bitmap Keyword Guide](bitmap-Keyword-Guide.md)
