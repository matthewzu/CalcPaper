# bitmap Function Guide

Version: 1.0

## Overview

`bitmap()` is a built-in function in CalcPaper used to view detailed bit structure of numeric values, including hexadecimal representation, binary representation, and bit index tables.

## Syntax

```python
bitmap(value)           # Little endian (default)
bitmap(value, 0)        # Little endian (explicit)
bitmap(value, 1)        # Big endian
```

### Parameters

- `value`: The numeric value or variable to view (required)
- `bIsBig`: Endianness flag (optional)
  - `0` or omitted: Little Endian
  - `1`: Big Endian

### Return Value

The `bitmap()` function has no return value, so it can only be used standalone or with variable assignment.

## Basic Usage

### Example 1: Default Little Endian

```python
a = 0xFF
view_a = bitmap(a)
```

Output:
```
a = 0xFF            = 255
view_a = bitmap(a)  = 255  # 255
  Hexadecimal: 0xFF
  Binary: 0b11111111
  Bits: 8 bits (1 bytes)
  Bit indices (Little Endian):
    |0 1 2 3 |4 5 6 7 |
    |1 1 1 1 |1 1 1 1 |
```

### Example 2: Explicit Little Endian

```python
b = 0xAB
view_b = bitmap(b, 0)
```

Output:
```
b = 0xAB               = 171
view_b = bitmap(b, 0)  = 171  # 171
  Hexadecimal: 0xAB
  Binary: 0b10101011
  Bits: 8 bits (1 bytes)
  Bit indices (Little Endian):
    |0 1 2 3 |4 5 6 7 |
    |1 0 1 0 |1 0 1 1 |
```

### Example 3: Big Endian

```python
c = 0xFF8040
view_c = bitmap(c, 1)
```

Output:
```
c = 0xFF8040           = 16744512
view_c = bitmap(c, 1)  = 16744512  # 16744512
  Hexadecimal: 0xFF8040
  Binary: 0b111111111000000001000000
  Bits: 24 bits (3 bytes)
  Bit indices (Big Endian):
    |23 22 21 20 |19 18 17 16 |15 14 13 12 |11 10  9  8 |7 6 5 4 |3 2 1 0 |
    |1  1  1  1  |1  1  1  1  |1  0  0  0  |0  0  0  0  |0 1 0 0 |0 0 0 0 |
```

### Example 4: Standalone Usage

```python
d = 0xABCD
bitmap(d, 1)
```

Output:
```
d = 0xABCD    = 43981
bitmap(d, 1)  = 43981  # 43981
  Hexadecimal: 0xABCD
  Binary: 0b1010101111001101
  Bits: 16 bits (2 bytes)
  Bit indices (Big Endian):
    |15 14 13 12 |11 10  9  8 |7 6 5 4 |3 2 1 0 |
    |1  0  1  0  |1  0  1  1  |1 1 0 0 |1 1 0 1 |
```

## Features

### 1. Multi-Format Display

When using the `bitmap()` function, the following information is displayed:

- Hexadecimal representation
- Binary representation
- Total bits and bytes
- Bit index table (based on endianness parameter)

### 2. Endianness Support

Control endianness through the second parameter:

- `0` or omitted: Little Endian
- `1`: Big Endian

## Endianness Differences

### Little Endian

Bit indices increase from left to right (0→7, 0→15, 0→31):

```python
view = bitmap(0xAB, 0)
```

Output:
```
  Bit indices (Little Endian):
    |0 1 2 3 |4 5 6 7 |
    |1 0 1 0 |1 0 1 1 |
```

- Leftmost is the least significant bit (LSB, bit 0)
- Rightmost is the most significant bit (MSB, bit 7)
- Matches some processor memory layouts

### Big Endian

Bit indices decrease from left to right (7→0, 15→0, 31→0):

```python
view = bitmap(0xAB, 1)
```

Output:
```
  Bit indices (Big Endian):
    |7 6 5 4 |3 2 1 0 |
    |1 0 1 0 |1 0 1 1 |
```

- Leftmost is the most significant bit (MSB, bit 7)
- Rightmost is the least significant bit (LSB, bit 0)
- Matches human reading convention

## Use Cases

### Case 1: View RGB Color Bit Structure

```python
# RGB color
color = 0xFF8040

# View complete bit structure (big endian)
view_color = bitmap(color, 1)
```

Output:
```
color = 0xFF8040            = 16744512
view_color = bitmap(color, 1)  = 16744512  # 16744512
  Hexadecimal: 0xFF8040
  Binary: 0b111111111000000001000000
  Bits: 24 bits (3 bytes)
  Bit indices (Big Endian):
    |23 22 21 20 |19 18 17 16 |15 14 13 12 |11 10  9  8 |7 6 5 4 |3 2 1 0 |
    |1  1  1  1  |1  1  1  1  |1  0  0  0  |0  0  0  0  |0 1 0 0 |0 0 0 0 |
```

From the bit index table, you can clearly see:
- Bits 23-16 (red): 11111111 = 0xFF = 255
- Bits 15-8 (green): 10000000 = 0x80 = 128
- Bits 7-0 (blue): 01000000 = 0x40 = 64

### Case 2: Debug Bitwise Operation Results

```python
# Bitwise operation
a = 0xFF
b = 0x0F
and_result = a & b

# View result bit structure (big endian)
view_and = bitmap(and_result, 1)
```

Output:
```
a = 0xFF                      = 255
b = 0x0F                      = 15
and_result = a & b            = 15  # 0xFF & 0xF
view_and = bitmap(and_result, 1)  = 15  # 15
  Hexadecimal: 0xF
  Binary: 0b00001111
  Bits: 8 bits (1 bytes)
  Bit indices (Big Endian):
    |7 6 5 4 |3 2 1 0 |
    |0 0 0 0 |1 1 1 1 |
```

### Case 3: Understand Shift Operations

```python
# Original value
original = 0b1010

# Left shift 2 bits
shifted = original << 2

# View bit structures (little endian)
view_original = bitmap(original, 0)
view_shifted = bitmap(shifted, 0)
```

Output:
```
original = 0b1010                = 10
shifted = original << 2          = 40
view_original = bitmap(original, 0)  = 10  # 10
  Hexadecimal: 0xA
  Binary: 0b00001010
  Bits: 8 bits (1 bytes)
  Bit indices (Little Endian):
    |0 1 2 3 |4 5 6 7 |
    |0 1 0 1 |0 0 0 0 |

view_shifted = bitmap(shifted, 0)    = 40  # 40
  Hexadecimal: 0x28
  Binary: 0b00101000
  Bits: 8 bits (1 bytes)
  Bit indices (Little Endian):
    |0 1 2 3 |4 5 6 7 |
    |0 0 0 1 |0 1 0 0 |
```

You can clearly see the bits shifted left by 2 positions.

### Case 4: Network Protocol Field Analysis

```python
# Protocol header (big endian)
header = 0x12345678

# View complete structure
view_header = bitmap(header, 1)

# Extract fields
type = (header >> 24) & 0xFF
version = (header >> 16) & 0xFF
length = (header >> 8) & 0xFF
flags = header & 0xFF

# View each field
view_type = bitmap(type, 1)
view_version = bitmap(version, 1)
view_length = bitmap(length, 1)
view_flags = bitmap(flags, 1)
```

## Difference from Normal Calculation

### Without bitmap

Only shows decimal result:

```python
a = 0xFF
b = a & 0x0F
```

Output:
```
a = 0xFF        = 255
b = a & 0x0F    = 15  # 0xFF & 0xF
```

### With bitmap

Shows detailed bit structure:

```python
a = 0xFF
b = bitmap(a & 0x0F, 1)
```

Output:
```
a = 0xFF                    = 255
b = bitmap(a & 0x0F, 1)     = 15  # 15 & 0xF
  Hexadecimal: 0xF
  Binary: 0b00001111
  Bits: 8 bits (1 bytes)
  Bit indices (Big Endian):
    |7 6 5 4 |3 2 1 0 |
    |0 0 0 0 |1 1 1 1 |
```

## Limitations and Notes

### 1. Only Non-Negative Integers

`bitmap()` only works with non-negative integer values:

```python
# Correct
view1 = bitmap(255, 1)

# Not applicable
view2 = bitmap(-10, 1)    # Negative number
view3 = bitmap(3.14, 1)   # Floating-point
```

### 2. Automatic Bit Alignment

Bit count is automatically aligned to multiples of 8 (byte boundaries):

```python
view1 = bitmap(0b1010, 1)  # 4 bits, displayed as 8 bits: 0b00001010
view2 = bitmap(0xFF, 1)    # 8 bits
view3 = bitmap(0xFFFF, 1)  # 16 bits
```

### 3. No Return Value

The `bitmap()` function has no return value, but can be used with variable assignment:

```python
# Correct usage
view = bitmap(0xFF, 1)     # Can assign to variable
bitmap(0xFF, 1)            # Can use standalone

# Incorrect usage
result = bitmap(0xFF, 1) + 10  # Cannot participate in operations
```

## Best Practices

### 1. Use bitmap Wisely

Only use `bitmap()` when you need detailed bit structure view:

```python
# Normal calculation: no bitmap needed
a = 0xFF
b = 0x0F
sum = a + b

# Bitwise operation debugging: use bitmap
and_result = a & b
view_and = bitmap(and_result, 1)
```

### 2. Choose Appropriate Endianness

Select endianness based on actual application:

- Network protocols: Usually big endian (`bitmap(value, 1)`)
- x86/x64 processors: Usually little endian (`bitmap(value, 0)` or `bitmap(value)`)
- ARM processors: May support both

### 3. Step-by-Step Viewing

For complex bitwise operations, use `bitmap()` step by step:

```python
# Step 1
step1 = 0xFF8040 >> 16
view_step1 = bitmap(step1, 1)

# Step 2
step2 = step1 & 0xFF
view_step2 = bitmap(step2, 1)
```

### 4. Use with Comments

Add comments to explain each `bitmap()` purpose:

```python
# Original RGB color
color = 0xFF8040
view_color = bitmap(color, 1)

# Extract red component
red = (color >> 16) & 0xFF
view_red = bitmap(red, 1)  # Should be 0xFF
```

## Practical Tips

### Tip 1: Compare Different Endianness

```python
# Little endian
little = bitmap(0xABCD, 0)

# Big endian
big = bitmap(0xABCD, 1)
```

### Tip 2: Verify Bit Masks

```python
# Create mask
mask = 0xFF00
view_mask = bitmap(mask, 1)

# Apply mask
data = 0xABCD
result = data & mask
view_result = bitmap(result, 1)
```

### Tip 3: Understand Shift Amounts

```python
original = 0b1
view_original = bitmap(original, 1)

shift1 = original << 1
view_shift1 = bitmap(shift1, 1)

shift2 = original << 2
view_shift2 = bitmap(shift2, 1)

shift3 = original << 3
view_shift3 = bitmap(shift3, 1)
```

## Output Format Description

### Bit Index Table Format

```
  Bit indices (Big Endian):
    |7 6 5 4 |3 2 1 0 |
    |1 0 1 0 |1 0 1 1 |
```

- First row: Bit index numbers
- Second row: Corresponding bit values (0 or 1)
- Grouped by 4 bits, separated by spaces
- Vertical bars `|` mark boundaries

### Multi-Byte Display

For multi-byte data, all bytes are displayed:

```
  Bit indices (Big Endian):
    |31 30 29 28 |27 26 25 24 |23 22 21 20 |19 18 17 16 |15 14 13 12 |11 10  9  8 |7 6 5 4 |3 2 1 0 |
    |0  0  0  1  |0  0  1  0  |0  0  1  1  |0  1  0  0  |0  1  0  1  |0  1  1  0  |0 1 1 1 |1 0 0 0 |
```

## Related Documentation

- [User Guide](User-Guide.md)
- [Bitwise Operations Reference](Bitwise-Operations-Reference.md)
- [Hex Comment Format](Hex-Comment-Format.md)
