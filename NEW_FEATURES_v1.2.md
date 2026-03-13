# CalcPaper v1.2 新功能

## 1. swap() 字节序交换函数

### 功能说明

`swap()` 函数用于交换数值的字节序（Endian Swap），常用于网络字节序和本地字节序之间的转换。

### 语法

```python
swap(value)
```

### 参数

- `value`: 要交换字节序的整数值或变量

### 返回值

返回字节序交换后的整数值，可以参与计算和赋值。

### 使用示例

#### 示例1：基本使用

```python
a = 0x1234
b = swap(a)  # 结果: 0x3412 (13330)
```

#### 示例2：用于表达式

```python
x = 0xABCD
y = swap(x) * 2  # swap(x) 的结果参与计算
```

#### 示例3：配合 bitmap 查看

```python
原始 = 0x12345678
bitmap(原始, 1)

交换后 = swap(原始)
bitmap(交换后, 1)
```

#### 示例4：bitmap 内嵌 swap

```python
数据 = 0xAABBCCDD
bitmap(swap(数据), 1)  # 直接查看交换后的位结构
```

#### 示例5：网络字节序转换

```python
# 网络字节序（大端）转本地字节序（小端）
网络数据 = 0x12345678
本地数据 = swap(网络数据)

# 查看转换前后
bitmap(网络数据, 1)   # 大端显示
bitmap(本地数据, 0)   # 小端显示
```

### 工作原理

swap() 函数会自动检测数值的字节数（1, 2, 4, 或 8 字节），然后反转字节顺序：

- 1字节 (8位): 不变
- 2字节 (16位): `0x1234` → `0x3412`
- 4字节 (32位): `0x12345678` → `0x78563412`
- 8字节 (64位): `0x123456789ABCDEF0` → `0xF0DEBC9A78563412`

### 应用场景

1. **网络编程**: 网络字节序（大端）与本地字节序转换
2. **文件格式**: 处理不同字节序的二进制文件
3. **跨平台**: x86（小端）与网络/ARM（大端）数据交换
4. **协议解析**: 解析网络协议中的多字节字段

---

## 2. 撤销/恢复功能

### 功能说明

支持撤销（Undo）和恢复（Redo）操作，可以回退到之前的计算状态。

### 使用方法

#### GUI 版本

- **撤销**: 点击"撤销"按钮或按 `Ctrl+Z`
- **恢复**: 点击"恢复"按钮或按 `Ctrl+Y` 或 `Ctrl+Shift+Z`

#### 命令行版本

- **撤销**: 输入 `undo`
- **恢复**: 输入 `redo`

### 特性

- 自动保存每次计算的状态
- 最多保存 50 个历史状态
- 支持多次撤销和恢复
- 撤销后进行新计算会清除后续历史

### 使用示例

```python
# 第一次计算
a = 100
b = 200
sum = a + b

calc  # 计算

# 第二次计算
c = 300
total = sum + c

calc  # 计算

# 撤销到第一次计算
undo

# 恢复到第二次计算
redo
```

### 历史记录管理

- 每次执行 `calc` 命令后，当前状态会被保存
- 撤销操作会回退到上一个保存的状态
- 恢复操作会前进到下一个保存的状态
- 历史记录超过 50 个时，最早的记录会被删除

---

## 完整示例

### 示例：RGB 颜色处理与字节序转换

```python
# 原始 RGB 颜色（大端格式）
color_be = 0xFF8040

# 提取 RGB 分量
red = (color_be >> 16) & 0xFF
green = (color_be >> 8) & 0xFF
blue = color_be & 0xFF

# 查看原始颜色（大端）
bitmap(color_be, 1)

# 转换为小端格式
color_le = swap(color_be)

# 查看转换后的颜色（小端）
bitmap(color_le, 0)

# 验证：从小端格式提取 RGB（字节顺序相反）
blue2 = (color_le >> 16) & 0xFF
green2 = (color_le >> 8) & 0xFF
red2 = color_le & 0xFF

# 验证结果
bitmap(red2, 1)    # 应该等于 red
bitmap(green2, 1)  # 应该等于 green
bitmap(blue2, 1)   # 应该等于 blue
```

### 示例：网络协议字段处理

```python
# 网络协议头（大端格式）
header_be = 0x12345678

# 查看网络格式
bitmap(header_be, 1)

# 转换为本地格式
header_le = swap(header_be)

# 查看本地格式
bitmap(header_le, 0)

# 提取字段（本地格式）
field1 = header_le & 0xFF
field2 = (header_le >> 8) & 0xFF
field3 = (header_le >> 16) & 0xFF
field4 = (header_le >> 24) & 0xFF

# 查看各字段
bitmap(field1, 1)
bitmap(field2, 1)
bitmap(field3, 1)
bitmap(field4, 1)
```

---

## 版本信息

- **版本**: v1.2
- **发布日期**: 2026-03-05
- **新增功能**:
  1. swap() 字节序交换函数
  2. 撤销/恢复功能（GUI 和命令行）

## 兼容性

- 完全兼容 v1.1 的所有功能
- swap() 函数可以与 bitmap() 函数配合使用
- 撤销/恢复不影响现有功能

## 下一步

- 阅读 [使用指南](docs/使用指南.md)
- 查看 [bitmap 函数说明](docs/bitmap函数说明.md)
- 尝试 [示例文件](examples/)
