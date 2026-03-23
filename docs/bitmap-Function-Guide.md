# bitmap Function Guide

Version: 1.1

## Overview

`bitmap()` is a built-in function in CalcPaper used to view detailed bit structure of numeric values, including hexadecimal representation, binary representation, and bit index tables.

## Syntax

```python
bitmap(value)              # Little endian (default), auto-align to 8/16/32/64 boundary
bitmap(value, 0)           # Little endian (explicit)
bitmap(value, 1)           # Big endian
bitmap(value, 0, 32)       # Little endian, 32-bit width
bitmap(value, 1, 64)       # Big endian, 64-bit width
```

### Parameters

- `value`: The numeric value or variable to view (required)
- `bIsBig`: Endianness flag (optional)
  - `0` or omitted: Little Endian
  - `1`: Big Endian
- `width`: Bit width (optional, 3rd parameter)
  - Any positive integer
  - When omitted, auto-aligns to the nearest 8/16/32/64 boundary

### Leading Zero Preservation

When the input value contains leading zeros, bitmap preserves them to determine display width:

```python
bitmap(0xFF)         # 8 bits (2 hex digits × 4 bits)
bitmap(0x00FF)       # 16 bits (4 hex digits × 4 bits, leading zeros preserved)
bitmap(0x0000FFFF)   # 32 bits (8 hex digits × 4 bits)
bitmap(0b00001111)   # 8 bits (8 binary digits)
```

### Important Restrictions

**`bitmap()` can only be used standalone:**
- ❌ Assign to variable: `view = bitmap(0xFF, 1)`  # Error
- ❌ Use in expressions: `result = bitmap(0xFF) + 10`  # Error
- ✅ Standalone: `bitmap(0xFF, 1)`  # Correct
- ✅ With width: `bitmap(0xFF, 1, 32)`  # Correct

## Basic Usage

### Example 1: Default Little Endian

```python
a = 0xFF
bitmap(a)
```

Output:
```
a = 0xFF   = 255
bitmap(a)  = 255  # 255
  Hexadecimal: 0xFF
  Binary: 0b11111111
  Bits: 8 bits (1 bytes)
  Bit indices (Little Endian):
    |0 1 2 3 |4 5 6 7 |
    |1 1 1 1 |1 1 1 1 |
```

### Example 2: Leading Zero Preservation

```python
bitmap(0x00FF, 1)
```

Output:
```
bitmap(0x00FF, 1)  = 255
  Hexadecimal: 0x00FF
  Binary: 0b0000000011111111
  Bits: 16 bits (2 bytes)
  Bit indices (Big Endian):
    |0 1 2 3 |4 5 6 7 | 8  9 10 11 |12 13 14 15 |
    |0 0 0 0 |0 0 0 0 | 1  1  1  1 | 1  1  1  1 |
```

### Example 3: Explicit Width Parameter

```python
bitmap(0xFF, 1, 32)
```

Output:
```
bitmap(0xFF, 1, 32)  = 255
  Hexadecimal: 0x000000FF
  Binary: 0b00000000000000000000000011111111
  Bits: 32 bits (4 bytes)
  Bit indices (Big Endian):
    |0 1 2 3 |4 5 6 7 | 8  9 10 11 |12 13 14 15 |16 17 18 19 |20 21 22 23 |24 25 26 27 |28 29 30 31 |
    |0 0 0 0 |0 0 0 0 | 0  0  0  0 | 0  0  0  0 | 0  0  0  0 | 0  0  0  0 | 1  1  1  1 | 1  1  1  1 |
```

### Example 4: Auto-Alignment to Boundary

```python
bitmap(0x1FF, 1)
```

Value is 0x1FF (9 bits), auto-aligns to 16-bit boundary:

Output:
```
bitmap(0x1FF, 1)  = 511
  Hexadecimal: 0x01FF
  Binary: 0b0000000111111111
  Bits: 16 bits (2 bytes)
  Bit indices (Big Endian):
    |0 1 2 3 |4 5 6 7 | 8  9 10 11 |12 13 14 15 |
    |0 0 0 0 |0 0 0 1 | 1  1  1  1 | 1  1  1  1 |
```

## Width Alignment Rules

### Default Alignment (No Width Parameter)

When no width parameter is specified, bit count auto-aligns to the nearest 8/16/32/64 boundary:

| Value Bits | Aligns To |
|-----------|-----------|
| 1-8 bits  | 8 bits    |
| 9-16 bits | 16 bits   |
| 17-32 bits| 32 bits   |
| 33-64 bits| 64 bits   |

### Leading Zeros Affect Alignment

Leading zeros in the input affect the final alignment width:

```python
bitmap(0xFF)         # Value 8 bits → aligns to 8 bits
bitmap(0x00FF)       # Input 16 bits → aligns to 16 bits
bitmap(0x000000FF)   # Input 32 bits → aligns to 32 bits
```

### Explicit Width Parameter

The 3rd parameter forces a specific width:

```python
bitmap(0xFF, 0, 8)    # Force 8-bit
bitmap(0xFF, 0, 16)   # Force 16-bit
bitmap(0xFF, 0, 32)   # Force 32-bit
bitmap(0xFF, 0, 64)   # Force 64-bit
bitmap(0xFF, 0, 12)   # Force 12-bit (any positive integer)
```

If the specified width is smaller than the actual bits needed, it auto-expands to the minimum boundary that can hold the value.

## Features

### 1. Multi-Format Display

When using `bitmap()`, the following information is displayed:

- Hexadecimal representation (with leading zero alignment)
- Binary representation (with leading zero alignment)
- Total bits and bytes
- Bit index table (based on endianness parameter)

### 2. Endianness Support

Control endianness through the second parameter:

- `0` or omitted: Little Endian
- `1`: Big Endian

## Use Cases

### Case 1: View Register Bit Structure

```python
# 32-bit register value
reg = 0x00FF8040
bitmap(reg, 1)           # Auto-detect leading zeros, show 32 bits
bitmap(0xFF8040, 1, 32)  # Explicitly specify 32-bit width
```

### Case 2: Debug Bitwise Operation Results

```python
a = 0xFF
b = 0x0F
and_result = a & b
bitmap(and_result, 1)
```

### Case 3: Network Protocol Field Analysis

```python
# Protocol header (big endian, 32-bit)
header = 0x12345678
bitmap(header, 1, 32)

# Extract fields
type = (header >> 24) & 0xFF
bitmap(type, 1, 8)
```

## Limitations and Notes

### 1. Only Non-Negative Integers

`bitmap()` only works with non-negative integer values.

### 2. Width Parameter

Width parameter must be a positive integer. If the specified width is smaller than the actual bits needed, it auto-expands to the minimum boundary that can hold the value.

### 3. Variable References Lose Leading Zeros

When using variable references, leading zero information is lost (since variables store numeric values). Use the width parameter to specify explicitly:

```python
a = 0x00FF
bitmap(a, 1)       # Shows as 8 bits (variable loses leading zero info)
bitmap(a, 1, 16)   # Explicitly specify 16-bit width
```

### 4. Standalone Use Only

`bitmap()` can only be used standalone, not assigned to variables or used in expressions.

## Related Documentation

- [User Guide](User-Guide.md)
- [Bitwise Operations Reference](Bitwise-Operations-Reference.md)
- [Hex Comment Format](Hex-Comment-Format.md)
