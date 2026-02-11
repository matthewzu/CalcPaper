# Bitwise Operations Quick Reference

Version: 1.0

## Table of Contents

- [Basic Concepts](#basic-concepts)
- [Bitwise Operators](#bitwise-operators)
- [Common Techniques](#common-techniques)
- [Practical Examples](#practical-examples)

## Basic Concepts

### Binary Representation

```
Decimal   Binary      Hexadecimal
0         0b0000      0x0
1         0b0001      0x1
2         0b0010      0x2
3         0b0011      0x3
4         0b0100      0x4
5         0b0101      0x5
6         0b0110      0x6
7         0b0111      0x7
8         0b1000      0x8
9         0b1001      0x9
10        0b1010      0xA
11        0b1011      0xB
12        0b1100      0xC
13        0b1101      0xD
14        0b1110      0xE
15        0b1111      0xF
```

### Bit Indexing

```
Big Endian (left to right, decreasing):
|7 6 5 4 |3 2 1 0 |
|1 0 1 0 |1 1 0 0 |

Little Endian (left to right, increasing):
|0 1 2 3 |4 5 6 7 |
|1 0 1 0 |1 1 0 0 |
```

## Bitwise Operators

### 1. Bitwise AND - &

**Rule**: Result is 1 only when both bits are 1

```
  1010
& 1100
------
  1000
```

**Uses**:
- Extract specific bits
- Clear specific bits
- Check odd/even

**Examples**:
```python
# Extract lower 4 bits
a = 0xFF
lower_4 = a & 0x0F  # Result: 0x0F (15)

# Check odd/even
number = 7
is_odd = number & 1  # Result: 1 (odd)

# Clear upper 4 bits
b = 0xFF
clear_upper = b & 0x0F  # Result: 0x0F (15)
```

### 2. Bitwise OR - |

**Rule**: Result is 1 when at least one bit is 1

```
  1010
| 1100
------
  1110
```

**Uses**:
- Set specific bits to 1
- Combine bit flags

**Examples**:
```python
# Set bit 3 to 1
a = 0b1010
set_bit3 = a | 0b1000  # Result: 0b1010 (10)

# Combine permissions
read_perm = 0b0001
write_perm = 0b0010
rw_perm = read_perm | write_perm  # Result: 0b0011 (3)
```

### 3. Bitwise XOR - ^

**Rule**: Result is 1 when bits are different

```
  1010
^ 1100
------
  0110
```

**Uses**:
- Toggle specific bits
- Simple encryption
- Swap variables (not recommended)

**Examples**:
```python
# Toggle all bits
a = 0b1010
toggled = a ^ 0b1111  # Result: 0b0101 (5)

# Simple encryption
plaintext = 0x42
key = 0xFF
ciphertext = plaintext ^ key  # Encrypt
decrypted = ciphertext ^ key  # Decrypt, equals plaintext
```

### 4. Bitwise NOT - ~

**Rule**: 0 becomes 1, 1 becomes 0

```
~ 1010
------
  0101 (actually two's complement, displays as negative)
```

**Note**: In Python, `~x` equals `-(x+1)`

**Examples**:
```python
# NOT (need mask to limit bits)
a = 0b1010
not_8bit = ~a & 0xFF  # Result: 0b11110101 (245)

# Create mask
bits = 4
mask = ~(~0 << bits)  # Result: 0b1111 (15)
```

### 5. Left Shift - <<

**Rule**: Shift left n bits, fill right with 0

```
  1010 << 2
= 101000
```

**Uses**:
- Multiply by power of 2
- Construct bit masks
- Combine bit fields

**Examples**:
```python
# Multiply by power of 2
a = 5
times_4 = a << 2  # Result: 20 (5 * 2^2)

# Construct mask
bit_pos = 3
mask = 1 << bit_pos  # Result: 0b1000 (8)

# RGB combination
R = 0xFF
G = 0x80
B = 0x40
color = (R << 16) | (G << 8) | B  # Result: 0xFF8040
```

### 6. Right Shift - >>

**Rule**: Shift right n bits, fill left with 0 (logical shift)

```
  1010 >> 2
= 0010
```

**Uses**:
- Divide by power of 2
- Extract high bits
- Decompose bit fields

**Examples**:
```python
# Divide by power of 2
a = 20
div_4 = a >> 2  # Result: 5 (20 / 2^2)

# Extract RGB components
color = 0xFF8040
R = (color >> 16) & 0xFF  # Result: 0xFF (255)
G = (color >> 8) & 0xFF   # Result: 0x80 (128)
B = color & 0xFF          # Result: 0x40 (64)
```

## Common Techniques

### 1. Check if bit n is set

```python
number = 0b1010
bit_pos = 3
is_set = (number >> bit_pos) & 1  # Result: 1
```

### 2. Set bit n to 1

```python
number = 0b1010
bit_pos = 2
set_bit = number | (1 << bit_pos)  # Result: 0b1110
```

### 3. Clear bit n (set to 0)

```python
number = 0b1010
bit_pos = 3
clear_bit = number & ~(1 << bit_pos)  # Result: 0b0010
```

### 4. Toggle bit n

```python
number = 0b1010
bit_pos = 2
toggle = number ^ (1 << bit_pos)  # Result: 0b1110
```

### 5. Extract n consecutive bits

```python
number = 0b11010110
start_bit = 2
num_bits = 3
extract = (number >> start_bit) & ((1 << num_bits) - 1)  # Result: 0b101
```

### 6. Check if power of 2

```python
number = 8
is_power_of_2 = (number & (number - 1)) == 0  # Result: True
```

### 7. Count number of 1s in binary

```python
# Using loop
number = 0b1010
count = 0
temp = number
# Loop: temp = temp & (temp - 1), count++
# Result: 2
```

### 8. Swap two numbers (not recommended, demo only)

```python
a = 5
b = 7
a = a ^ b
b = a ^ b  # b = 5
a = a ^ b  # a = 7
```

### 9. Get lowest set bit

```python
number = 0b1010
lowest_bit = number & (-number)  # Result: 0b0010
```

### 10. Clear lowest set bit

```python
number = 0b1010
clear_lowest = number & (number - 1)  # Result: 0b1000
```

## Practical Examples

### Example 1: Permission Management

```python
# Define permission bits
READ = 0b0001      # Read permission
WRITE = 0b0010     # Write permission
EXECUTE = 0b0100   # Execute permission
DELETE = 0b1000    # Delete permission

# Set permissions
user_perm = READ | WRITE  # Read-write permission

# Check permissions
has_read = (user_perm & READ) != 0      # True
has_execute = (user_perm & EXECUTE) != 0  # False

# Add permission
user_perm = user_perm | EXECUTE  # Add execute permission

# Remove permission
user_perm = user_perm & ~WRITE  # Remove write permission
```

### Example 2: RGB Color Processing

```python
endian: big

# Create color
R = 255
G = 128
B = 64
color = (R << 16) | (G << 8) | B  # 0xFF8040

# Extract color components
red = (color >> 16) & 0xFF  # 255
green = (color >> 8) & 0xFF   # 128
blue = color & 0xFF          # 64

# Modify color component (change green to 200)
new_green = 200
color = (color & 0xFF00FF) | (new_green << 8)  # 0xFFC840
```

### Example 3: IP Address Processing

```python
# Construct IP address 192.168.1.1
seg1 = 192
seg2 = 168
seg3 = 1
seg4 = 1
IP = (seg1 << 24) | (seg2 << 16) | (seg3 << 8) | seg4  # 0xC0A80101

# Parse IP address
A = (IP >> 24) & 0xFF  # 192
B = (IP >> 16) & 0xFF  # 168
C = (IP >> 8) & 0xFF   # 1
D = IP & 0xFF          # 1

# Subnet mask 255.255.255.0
mask = 0xFFFFFF00

# Network address
network = IP & mask  # 0xC0A80100 (192.168.1.0)

# Host address
host = IP & ~mask  # 0x00000001 (0.0.0.1)
```

### Example 4: Bit Flag States

```python
# State flags
FLAG_ACTIVE = 0b00000001
FLAG_VISIBLE = 0b00000010
FLAG_ENABLED = 0b00000100
FLAG_SELECTED = 0b00001000

# Initial state
state = FLAG_ACTIVE | FLAG_VISIBLE  # Active and visible

# Check state
is_active = (state & FLAG_ACTIVE) != 0      # True
is_enabled = (state & FLAG_ENABLED) != 0     # False

# Toggle state
state = state ^ FLAG_VISIBLE  # Toggle visibility

# Set multiple flags
state = state | (FLAG_ENABLED | FLAG_SELECTED)

# Clear multiple flags
state = state & ~(FLAG_SELECTED | FLAG_ENABLED)
```

### Example 5: Data Packing and Unpacking

```python
# Pack: combine multiple small data into one large data
# Format: [type:4bits][version:4bits][length:8bits][flags:8bits]
type_val = 0x5
version = 0x2
length = 0x40
flags = 0xFF

packet = (type_val << 20) | (version << 16) | (length << 8) | flags

# Unpack
unpack_type = (packet >> 20) & 0xF   # 5
unpack_version = (packet >> 16) & 0xF   # 2
unpack_length = (packet >> 8) & 0xFF   # 64
unpack_flags = packet & 0xFF          # 255
```

### Example 6: Bit Mask Application

```python
# Create masks
# Lower 4 bits mask
lower_4_mask = 0x0F  # 0b00001111

# Upper 4 bits mask
upper_4_mask = 0xF0  # 0b11110000

# Apply masks
data = 0xAB
lower_4 = data & lower_4_mask  # 0x0B
upper_4 = data & upper_4_mask  # 0xA0

# Swap upper and lower 4 bits
swapped = ((data & lower_4_mask) << 4) | ((data & upper_4_mask) >> 4)  # 0xBA
```

## Performance Tips

1. **Bitwise operations are faster than arithmetic**
   - `x * 2` → `x << 1`
   - `x / 2` → `x >> 1`
   - `x % 2` → `x & 1`

2. **Use bitwise operations for optimized checks**
   - Check odd/even: `x & 1`
   - Check power of 2: `(x & (x-1)) == 0`

3. **Avoid over-optimization**
   - Modern compilers optimize automatically
   - Readability over minor performance gains

## Debugging Tips

### Use bitmap to view bit structure

```python
endian: big

# View bit structure of data
data = 0xAB
bitmap view_data = data
```

### Verify step by step

```python
# Complex bitwise operations step by step
color = 0xFF8040

# Step 1: Right shift
step1 = color >> 16  # 0xFF

# Step 2: Mask
step2 = step1 & 0xFF  # 0xFF

# Final result
red = (color >> 16) & 0xFF  # 0xFF
```

## Common Mistakes

### 1. Forgetting parentheses

```python
# Wrong
result = number & 0xFF == 0  # Compare first, then AND

# Correct
result = (number & 0xFF) == 0  # AND first, then compare
```

### 2. Bitwise operations on negative numbers

```python
# In Python, negative numbers use two's complement
a = -1
result = a >> 1  # Still -1 (arithmetic right shift)

# For logical right shift, convert to unsigned first
unsigned = a & 0xFFFFFFFF
result = unsigned >> 1
```

### 3. Shift beyond range

```python
# Shift amount should not exceed data type bit width
a = 1
result = a << 100  # May produce unexpected results
```

## References

- [User Guide](User-Guide.md)
- [Hex Comment Format](Hex-Comment-Format.md)
- [bitmap Keyword Guide](bitmap-Keyword-Guide.md)
