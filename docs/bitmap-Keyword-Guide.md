# bitmap Keyword Guide

Version: 1.0

## Overview

`bitmap` is a special keyword in CalcPaper used to view detailed bit structure of numeric values, including hexadecimal representation, binary representation, and bit index tables.

## Basic Usage

### Syntax

```python
bitmap variable_name = expression
```

### Example

```python
endian: big
bitmap view = 0xFF
```

Output:
```
bitmap view = 0xFF    = 255 (0xFF, 0b11111111)
  Hexadecimal: 0xFF
  Binary: 0b11111111
  Bits: 8 bits (1 bytes)
  Bit indices (Big Endian):
    |7 6 5 4 |3 2 1 0 |
    |1 1 1 1 |1 1 1 1 |
```

## Features

### 1. Multi-Format Display

When using the `bitmap` keyword, results are displayed in three formats simultaneously:

- Decimal: `255`
- Hexadecimal: `0xFF`
- Binary: `0b11111111`

```python
bitmap a = 0xAB
# Output: 255 (0xFF, 0b11111111)
```

### 2. Bit Structure Information

Displays detailed bit structure information:

- Hexadecimal representation
- Binary representation
- Total bits and bytes
- Bit index table (based on endianness)

### 3. Endianness Support

Endianness must be set before displaying bit index tables:

```python
# Set big endian
endian: big

# Or set little endian
endian: little
```

## Endianness Differences

### Big Endian

Bit indices decrease from left to right (MSB to LSB):

```python
endian: big
bitmap view = 0xAB
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

### Little Endian

Bit indices increase from left to right (LSB to MSB):

```python
endian: little
bitmap view = 0xAB
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

## Use Cases

### Case 1: View RGB Color Bit Structure

```python
endian: big

# RGB color
color = 0xFF8040

# View complete bit structure
bitmap view_color = color
```

Output:
```
bitmap view_color = color    = 16744512 (0xFF8040, 0b111111111000000001000000)
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
endian: big

# Bitwise operation
a = 0xFF
b = 0x0F
and_result = a & b

# View result bit structure
bitmap view_and = and_result
```

Output:
```
and_result = a & b          = 15
bitmap view_and = and_result = 15 (0xF, 0b1111)
  Hexadecimal: 0xF
  Binary: 0b00001111
  Bits: 8 bits (1 bytes)
  Bit indices (Big Endian):
    |7 6 5 4 |3 2 1 0 |
    |0 0 0 0 |1 1 1 1 |
```

### Case 3: Understand Shift Operations

```python
endian: big

# Original value
original = 0b1010

# Left shift 2 bits
shifted = original << 2

# View bit structures
bitmap view_original = original
bitmap view_shifted = shifted
```

Output:
```
original = 0b1010                = 10
bitmap view_original = original  = 10 (0xA, 0b1010)
  Hexadecimal: 0xA
  Binary: 0b00001010
  Bits: 8 bits (1 bytes)
  Bit indices (Big Endian):
    |7 6 5 4 |3 2 1 0 |
    |0 0 0 0 |1 0 1 0 |

shifted = original << 2          = 40
bitmap view_shifted = shifted    = 40 (0x28, 0b101000)
  Hexadecimal: 0x28
  Binary: 0b00101000
  Bits: 8 bits (1 bytes)
  Bit indices (Big Endian):
    |7 6 5 4 |3 2 1 0 |
    |0 0 1 0 |1 0 0 0 |
```

You can clearly see the bits shifted left by 2 positions.

### Case 4: Network Protocol Field Analysis

```python
endian: big

# Protocol header
header = 0x12345678

# View complete structure
bitmap view_header = header

# Extract fields
type = (header >> 24) & 0xFF
version = (header >> 16) & 0xFF
length = (header >> 8) & 0xFF
flags = header & 0xFF

# View each field
bitmap view_type = type
bitmap view_version = version
bitmap view_length = length
bitmap view_flags = flags
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

Shows multiple formats and bit structure:

```python
endian: big
a = 0xFF
bitmap b = a & 0x0F
```

Output:
```
a = 0xFF                = 255
bitmap b = a & 0x0F     = 15 (0xF, 0b1111)
  Hexadecimal: 0xF
  Binary: 0b00001111
  Bits: 8 bits (1 bytes)
  Bit indices (Big Endian):
    |7 6 5 4 |3 2 1 0 |
    |0 0 0 0 |1 1 1 1 |
```

## Limitations and Notes

### 1. Endianness Must Be Set

To display bit index tables, endianness must be set first:

```python
# Wrong: No endianness set
bitmap a = 0xFF  # Won't show bit index table

# Correct: Set endianness first
endian: big
bitmap a = 0xFF  # Will show bit index table
```

### 2. Only Non-Negative Integers

`bitmap` only works with non-negative integer values:

```python
# Correct
bitmap a = 255

# Not applicable
bitmap b = -10    # Negative number
bitmap c = 3.14   # Floating-point
```

### 3. Automatic Bit Alignment

Bit count is automatically aligned to multiples of 8 (byte boundaries):

```python
bitmap a = 0b1010  # 4 bits, displayed as 8 bits: 0b00001010
bitmap b = 0xFF    # 8 bits
bitmap c = 0xFFFF  # 16 bits
```

## Best Practices

### 1. Use bitmap Wisely

Only use `bitmap` when you need detailed bit structure view:

```python
# Normal calculation: no bitmap needed
a = 0xFF
b = 0x0F
sum = a + b

# Bitwise operation debugging: use bitmap
and_result = a & b
bitmap view_and = and_result
```

### 2. Choose Appropriate Endianness

Select endianness based on actual application:

- Network protocols: Usually big endian
- x86/x64 processors: Usually little endian
- ARM processors: May support both

### 3. Step-by-Step Viewing

For complex bitwise operations, use `bitmap` step by step:

```python
endian: big

# Step 1
step1 = 0xFF8040 >> 16
bitmap view_step1 = step1

# Step 2
step2 = step1 & 0xFF
bitmap view_step2 = step2
```

### 4. Use with Comments

Add comments to explain each `bitmap` purpose:

```python
endian: big

# Original RGB color
color = 0xFF8040
bitmap view_color = color

# Extract red component
red = (color >> 16) & 0xFF
bitmap view_red = red  # Should be 0xFF
```

## Practical Tips

### Tip 1: Compare Different Endianness

```python
# Big endian
endian: big
bitmap big_endian = 0xABCD

# Little endian
endian: little
bitmap little_endian = 0xABCD
```

### Tip 2: Verify Bit Masks

```python
endian: big

# Create mask
mask = 0xFF00
bitmap view_mask = mask

# Apply mask
data = 0xABCD
result = data & mask
bitmap view_result = result
```

### Tip 3: Understand Shift Amounts

```python
endian: big

original = 0b1
bitmap original = original

shift1 = original << 1
bitmap shift1 = shift1

shift2 = original << 2
bitmap shift2 = shift2

shift3 = original << 3
bitmap shift3 = shift3
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
