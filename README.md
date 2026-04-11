# CalcPaper - 计算稿纸

<div align="center">

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.6+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-orange.svg)

**Smart Calculator with Bitwise & Date Operations | 支持位运算和日期运算的智能计算器**

[中文](#中文) | [English](#english)

</div>

---

## English

### 📖 Introduction

CalcPaper is a smart calculator designed for programmers, supporting variable references, bitwise operations, date/time arithmetic, hexadecimal/binary numbers, byte order swapping, and more — making complex calculations as simple as writing on paper.

Version: 2.0

### 🚀 Quick Start

#### Download Packaged Program (Recommended)

Download the packaged program for your platform from GitHub Releases — no Python installation required:

👉 [Download Latest Version](https://github.com/matthewzu/CalcPaper/releases/latest)

| Platform | File |
| --- | --- |
| Windows | `CalcPaper.exe` |
| macOS | `CalcPaper.dmg` |
| Linux | `CalcPaper` |

Double-click to launch the GUI interface.

CLI mode:

```bash
# Windows
CalcPaper.exe --cli

# macOS / Linux
./CalcPaper --cli
```

#### Run from Source (Alternative)

```bash
# Clone the repository
git clone https://github.com/matthewzu/CalcPaper.git
cd CalcPaper

# No dependencies needed (uses Python standard library)

# GUI interface (default)
python main.py

# CLI mode
python main.py --cli

# Specify language
python main.py --lang en
python main.py --cli --lang zh

# Check version
python main.py --version
```

### ✨ Key Features

- 🧮 **Variable References** - Define variables and use them later
- 🔢 **Multi-base Support** - Hexadecimal (0xFF), Binary (0b1010)
- ⚡ **Bitwise Operations** - Support <<, >>, &, |, ^, ~ operators
- 📊 **bitmap() Bit Visualization** - View each bit's value and index, big/little endian display
- 🔀 **swap() Byte Order Swap** - Network to host byte order conversion
- 🔢 **hex() Hex Display** - Display hexadecimal representation of values
- 📅 🆕 **Date/Time Arithmetic** - Date durations (Y/T/M/W/D) and time durations (h/m/s)
- 📆 🆕 **workday() Working Day Calculation** - Count working days with custom holidays
- ✏️ 🆕 **Variable Name Autocomplete** - Auto-suggest popup when typing variable names in GUI
- 🔄 🆕 **Auto Update Check on Startup** - Background check for latest GitHub release
- 🖥️ 🆕 **GUI + CLI Dual-mode Packaging** - Single executable supports both graphical and command-line interface
- 💯 **Percentage Calculation** - Direct use of 6.5%, 10%, etc.
- 💾 **Session Auto-restore** - Auto save and restore content from last session
- ⚙️ **Config Persistence** - Remember window size, language, and font settings
- ⌨️ **Customizable Shortcuts** - All keyboard shortcuts are configurable
- 🌏 **Bilingual (Chinese/English)** - Both GUI and CLI support language switching
- 🔤 **Font Scaling** - GUI supports font size adjustment
- 🔄 **Undo/Redo** - Support undo and redo operations
- 💡 **Smart Comments** - Auto hex format for bitwise operations

### 🆕 What's New in v2.0

#### Date/Time Arithmetic

Calculate dates and times directly in your expressions using intuitive literal syntax:

- Date literals: `Yyyyymmdd` (e.g., `Y20260410` = April 10, 2026)
- Time literals: `Thhmmss` (e.g., `T143000` = 14:30:00)
- Date durations (uppercase): `Mxx` (months), `Wxx` (weeks), `Dxx` (days)
- Time durations (lowercase): `hxx` (hours), `mxx` (minutes), `sxx` (seconds)

Operations: date ± duration → date, date - date → days, time ± duration → time, time - time → seconds.

Comments auto-show human-readable format: dates show "YYYY年M月D日 第XX周星期X", times show "X时X分X秒", date differences show "X年X月X周X天", time differences show "X小时X分钟X秒".

#### workday() Working Day Calculation 🆕

Calculate the date after a given number of working days, auto-skipping weekends:

```python
deadline = workday(Y20260411, 10)                    # 10 working days
deadline2 = workday(Y20260411, 20, Y20260501)        # add May Day as holiday
deadline3 = workday(Y20260411, 10, -Y20260412)       # remove weekend
deadline4 = workday(Y20260411, 15, Y20260501/-Y20260412)  # combined
```

Extra holidays: `Y20260501` (add), `-Y20260412` (remove), separated by `/`.

#### Variable Name Autocomplete

In the GUI, start typing a previously defined variable name and an autocomplete popup appears. Use Up/Down to navigate, Tab/Enter to confirm, Escape to dismiss.

#### Auto Update Check

On GUI startup, CalcPaper checks GitHub Releases in the background. If a newer version is found, a clickable notification appears in the status bar.

#### GUI + CLI Dual-mode

The packaged executable supports both modes:
- `CalcPaper` — launches GUI (default)
- `CalcPaper --cli` — launches interactive CLI
- `CalcPaper --cli --lang zh` — CLI in Chinese

### 📝 Usage Examples

#### Basic Calculation

```python
# Monthly budget
salary = 8000
rent = 2000
food = 30 * 25
balance = salary - rent - food
```

**Output:**

```
salary = 8000                  = 8000
rent = 2000                    = 2000
food = 30 * 25                 = 750
balance = salary - rent - food = 5250  # 8000 - 2000 - 750
```

#### Bitwise Operations

```python
# RGB color extraction
color = 0xFF8040
R = (color >> 16) & 0xFF
G = (color >> 8) & 0xFF
B = color & 0xFF

# View bit structure with bitmap
bitmap(color, 1)
```

#### Date/Time Arithmetic 🆕

```python
# Date arithmetic (comments auto-show date and weekday)
today = Y20260410
deadline = today + D10      # Y20260420  # 2026年4月20日 第17周星期一
next_month = today + M1     # Y20260510
diff = Y20260410 - Y20260101  # 99  # 3月1周2天

# Time arithmetic (comments auto-show hours/minutes/seconds)
start = T090000
end = T173000
duration = end - start      # 30600  # 8小时30分钟
lunch = start + h3 + m30    # T123000  # 12时30分

# Workday calculation
deadline = workday(Y20260411, 10)  # auto-skip weekends
```

#### Network Programming

```python
# IP address parsing
IP = 0xC0A80001  # 192.168.0.1
seg1 = (IP >> 24) & 0xFF  # 192
seg2 = (IP >> 16) & 0xFF  # 168
seg3 = (IP >> 8) & 0xFF   # 0
seg4 = IP & 0xFF          # 1
```

#### Byte Order Conversion

```python
# Network byte order (big endian) to host byte order (little endian)
net_data = 0x12345678
host_data = swap(net_data)  # 0x78563412

# View before and after
bitmap(net_data, 1)   # Big endian display
bitmap(host_data, 0)  # Little endian display
```

### 📚 Built-in Functions

#### bitmap()

Bit structure visualization function, displaying each bit's value and index.

```python
bitmap(0xFF8040)      # Default little endian display
bitmap(0xFF8040, 1)   # Big endian display
bitmap(0xFF8040, 0)   # Little endian display
```

#### swap()

Byte order swap function for big/little endian conversion.

```python
swap(0x12345678)  # 0x78563412
```

#### hex()

Hexadecimal display function. Supports nested function calls.

```python
hex(255)    # 0xFF
hex(65535)  # 0xFFFF
hex(swap(0x12345678))  # 0x78563412
```

#### workday()

Working day calculation function. Counts working days from a start date, skipping weekends by default.

```python
workday(Y20260411, 10)                     # 10 working days from date
workday(Y20260411, 20, Y20260501)          # add extra holiday
workday(Y20260411, 10, -Y20260412)         # remove weekend day
workday(Y20260411, 15, Y20260501/-Y20260412)  # combined
```

### 🔒 Reserved Keywords

The following prefixes followed by digits are reserved keywords and cannot be used as variable names:

```
Y + digits (date)     T + digits (time)
M + digits (month)    W + digits (week)     D + digits (day)
h + digits (hour)     m + digits (minute)   s + digits (second)
Uppercase M/W/D = date durations, lowercase h/m/s = time durations
```

Examples: `Y20260410`, `T143000`, `M3`, `W2`, `D10`, `h2`, `m30`, `s45` are all reserved keywords.

### 🎯 Use Cases

| Scenario | Examples |
| --- | --- |
| 🔧 **Embedded Development** | Register configuration, bit flag management |
| 🌐 **Network Programming** | IP parsing, protocol field extraction |
| 🎨 **Graphics Processing** | RGB color decomposition, pixel operations |
| 💾 **Data Processing** | Bit masking, data packing/unpacking |
| 📅 **Date Calculation** | Project scheduling, deadline estimation |
| 📊 **Daily Calculations** | Financial budgeting, shopping discounts |

### 📚 Documentation

#### English Documentation

- [User Guide](docs/User-Guide.md) - Complete usage instructions and examples
- [Bitwise Operations Reference](docs/Bitwise-Operations-Reference.md) - Bitwise operators and techniques
- [Hex Comment Format](docs/Hex-Comment-Format.md) - Automatic hex comment feature
- [bitmap Function Guide](docs/bitmap-Function-Guide.md) - Bit structure visualization

#### 中文文档

- [使用指南](docs/使用指南.md) - 完整的使用说明和示例
- [位运算快速参考](docs/位运算快速参考.md) - 位运算操作符和技巧
- [16进制注释格式说明](docs/16进制注释格式说明.md) - 自动16进制注释功能
- [bitmap函数说明](docs/bitmap函数说明.md) - 位结构可视化功能

### 🖥️ Requirements

- **Python**: 3.6+ (only needed when running from source)
- **GUI**: tkinter (included with Python)
- **Platform**: Windows, macOS, Linux

### 🤝 Contributing

Issues and Pull Requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details

### 📮 Contact

- **Issues**: [GitHub Issues](https://github.com/matthewzu/CalcPaper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/matthewzu/CalcPaper/discussions)
- **Email**: xiaofeng_zu@163.com

---

## 中文

### 📖 简介

CalcPaper（计算稿纸）是一款专为程序员设计的智能计算器，支持变量引用、位运算、日期/时间运算、16进制/2进制数值、字节序转换等功能，让复杂计算像在纸上写算式一样简单。

版本：2.0

### 🚀 快速开始

#### 下载打包程序（首选）

从 GitHub Releases 下载适合您平台的打包程序，开箱即用，无需安装 Python：

👉 [下载最新版本](https://github.com/matthewzu/CalcPaper/releases/latest)

| 平台 | 文件 |
| --- | --- |
| Windows | `CalcPaper.exe` |
| macOS | `CalcPaper.dmg` |
| Linux | `CalcPaper` |

下载后双击运行即可启动 GUI 图形界面。

CLI 命令行模式：

```bash
# Windows
CalcPaper.exe --cli

# macOS / Linux
./CalcPaper --cli
```

#### 从源码运行（备选）

```bash
# 克隆仓库
git clone https://github.com/matthewzu/CalcPaper.git
cd CalcPaper

# 无需安装依赖（使用 Python 标准库）

# 图形界面（默认）
python main.py

# 命令行模式
python main.py --cli

# 指定语言
python main.py --lang en
python main.py --cli --lang zh

# 查看版本
python main.py --version
```

### ✨ 核心特性

- 🧮 **变量引用** - 定义变量，后续直接使用
- 🔢 **多进制支持** - 16进制（0xFF）、2进制（0b1010）
- ⚡ **位运算** - 支持 <<、>>、&、|、^、~ 等操作
- 📊 **bitmap() 位结构可视化** - 查看每一位的值和索引，支持大端/小端显示
- 🔀 **swap() 字节序交换** - 网络字节序与本地字节序转换
- 🔢 **hex() 16进制显示** - 显示数值的16进制表示
- 📅 🆕 **日期/时间加减运算** - 支持日期时长（Y/T/M/W/D）和时间时长（h/m/s）
- 📆 🆕 **workday() 工作日计算** - 计算工作日，支持自定义节假日
- ✏️ 🆕 **变量名自动补全** - GUI 中输入变量名时自动弹出候选列表
- 🔄 🆕 **启动时自动检查更新** - 后台检查 GitHub 最新版本
- 🖥️ 🆕 **GUI + CLI 双模式打包** - 一个可执行文件同时支持图形界面和命令行
- 💯 **百分数计算** - 直接使用 6.5%、10% 等
- 💾 **会话自动恢复** - 自动保存和恢复上次退出时的内容
- ⚙️ **配置持久化** - 记住窗口大小、语言和字体设置
- ⌨️ **可自定义快捷键** - 所有快捷键均可配置
- 🌏 **中英文双语** - GUI 和命令行都支持中英文切换
- 🔤 **字体缩放** - GUI 支持字体放大缩小
- 🔄 **撤销/恢复** - 支持撤销和恢复操作
- 💡 **智能注释** - 位运算自动显示16进制格式

### 🆕 v2.0 新功能详解

#### 日期/时间加减运算

直接在表达式中使用日期和时间字面量进行计算：

- 日期字面量：`Yyyyymmdd`（如 `Y20260410` = 2026年4月10日）
- 时间字面量：`Thhmmss`（如 `T143000` = 14:30:00）
- 日期时长（大写）：`Mxx`（月）、`Wxx`（周）、`Dxx`（天）
- 时间时长（小写）：`hxx`（小时）、`mxx`（分钟）、`sxx`（秒）

运算规则：日期 ± 时长 → 日期，日期 - 日期 → 天数，时间 ± 时长 → 时间，时间 - 时间 → 秒数。

注释自动显示人类可读格式：日期显示"X年X月X日 第XX周星期X"，时间显示"X时X分X秒"，日期差显示"X年X月X周X天"，时间差显示"X小时X分钟X秒"。

#### workday() 工作日计算 🆕

计算从指定日期起若干工作日后的日期，自动跳过周末：

```python
deadline = workday(Y20260411, 10)                    # 10个工作日
deadline2 = workday(Y20260411, 20, Y20260501)        # 添加五一为节假日
deadline3 = workday(Y20260411, 10, -Y20260412)       # 移除周末
deadline4 = workday(Y20260411, 15, Y20260501/-Y20260412)  # 组合
```

额外节假日：`Y20260501`（添加）、`-Y20260412`（移除），用 `/` 分隔。

#### 变量名自动补全

在 GUI 输入区域输入已定义的变量名时，自动弹出候选列表。上下方向键导航，Tab/Enter 确认选择，Escape 关闭。

#### 启动时自动检查更新

GUI 启动时后台检查 GitHub Releases 最新版本。发现新版本时在状态栏显示可点击的下载提示。

#### GUI + CLI 双模式

打包后的可执行文件同时支持两种模式：
- `CalcPaper` — 启动 GUI（默认）
- `CalcPaper --cli` — 启动交互式命令行
- `CalcPaper --cli --lang en` — 英文命令行

### 📝 使用示例

#### 基础计算

```python
# 月度预算
工资 = 8000
房租 = 2000
餐费 = 30 * 25
结余 = 工资 - 房租 - 餐费
```

**输出：**

```
工资 = 8000                    = 8000
房租 = 2000                    = 2000
餐费 = 30 * 25                 = 750
结余 = 工资 - 房租 - 餐费      = 5250  # 8000 - 2000 - 750
```

#### 位运算

```python
# RGB 颜色提取
颜色 = 0xFF8040
R = (颜色 >> 16) & 0xFF
G = (颜色 >> 8) & 0xFF
B = 颜色 & 0xFF

# 使用 bitmap 查看位结构
bitmap(颜色, 1)
```

#### 日期/时间运算 🆕

```python
# 日期运算（注释自动显示年月日和星期）
today = Y20260410
deadline = today + D10      # Y20260420  # 2026年4月20日 第17周星期一
next_month = today + M1     # Y20260510
diff = Y20260410 - Y20260101  # 99  # 3月1周2天

# 时间运算（注释自动显示时分秒）
start = T090000
end = T173000
duration = end - start      # 30600  # 8小时30分钟
lunch = start + h3 + m30    # T123000  # 12时30分

# 工作日计算
deadline = workday(Y20260411, 10)  # 自动跳过周末
```

#### 网络编程

```python
# IP 地址解析
IP = 0xC0A80001  # 192.168.0.1
段1 = (IP >> 24) & 0xFF  # 192
段2 = (IP >> 16) & 0xFF  # 168
段3 = (IP >> 8) & 0xFF   # 0
段4 = IP & 0xFF          # 1
```

#### 字节序转换

```python
# 网络字节序（大端）转本地字节序（小端）
网络数据 = 0x12345678
本地数据 = swap(网络数据)  # 0x78563412

# 查看转换前后
bitmap(网络数据, 1)  # 大端显示
bitmap(本地数据, 0)  # 小端显示
```

### 📚 内置函数

#### bitmap()

位结构可视化函数，显示数值的每一位值和索引。

```python
bitmap(0xFF8040)      # 默认小端显示
bitmap(0xFF8040, 1)   # 大端显示
bitmap(0xFF8040, 0)   # 小端显示
```

#### swap()

字节序交换函数，用于大端/小端转换。

```python
swap(0x12345678)  # 0x78563412
```

#### hex()

16进制显示函数。支持嵌套函数调用。

```python
hex(255)    # 0xFF
hex(65535)  # 0xFFFF
hex(swap(0x12345678))  # 0x78563412
```

#### workday()

工作日计算函数。从指定日期起计算若干工作日后的日期，默认跳过周末。

```python
workday(Y20260411, 10)                     # 10个工作日后
workday(Y20260411, 20, Y20260501)          # 添加额外节假日
workday(Y20260411, 10, -Y20260412)         # 移除周末
workday(Y20260411, 15, Y20260501/-Y20260412)  # 组合
```

### 🔒 保留关键字说明

以下前缀后跟数字的标识符为系统保留关键字，不可用作变量名：

```
Y + 数字 (日期)    T + 数字 (时间)
M + 数字 (月)      W + 数字 (周)      D + 数字 (天)
h + 数字 (小时)    m + 数字 (分钟)    s + 数字 (秒)
大写 M/W/D = 日期时长，小写 h/m/s = 时间时长
```

例如：`Y20260410`、`T143000`、`M3`、`W2`、`D10`、`h2`、`m30`、`s45` 均为保留关键字。

### 🎯 适用场景

| 场景 | 示例 |
| --- | --- |
| 🔧 **嵌入式开发** | 寄存器配置、位标志管理 |
| 🌐 **网络编程** | IP地址解析、协议字段提取 |
| 🎨 **图形处理** | RGB颜色分解、像素操作 |
| 💾 **数据处理** | 位掩码、数据打包/解包 |
| 📅 **日期计算** | 项目排期、截止日期推算 |
| 📊 **日常计算** | 财务预算、购物折扣 |

### 📚 文档

#### 中文文档

- [使用指南](docs/使用指南.md) - 完整的使用说明和示例
- [位运算快速参考](docs/位运算快速参考.md) - 位运算操作符和技巧
- [16进制注释格式说明](docs/16进制注释格式说明.md) - 自动16进制注释功能
- [bitmap函数说明](docs/bitmap函数说明.md) - 位结构可视化功能

#### English Documentation

- [User Guide](docs/User-Guide.md) - Complete usage instructions and examples
- [Bitwise Operations Reference](docs/Bitwise-Operations-Reference.md) - Bitwise operators and techniques
- [Hex Comment Format](docs/Hex-Comment-Format.md) - Automatic hex comment feature
- [bitmap Function Guide](docs/bitmap-Function-Guide.md) - Bit structure visualization

### 🖥️ 系统要求

- **Python**: 3.6+（仅从源码运行时需要）
- **GUI**: tkinter（Python 自带）
- **平台**: Windows、macOS、Linux

### 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 📄 许可证

本项目采用 GPL-3.0 许可证 - 详见 [LICENSE](LICENSE) 文件

### 📮 联系方式

- **Issues**: [GitHub Issues](https://github.com/matthewzu/CalcPaper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/matthewzu/CalcPaper/discussions)
- **Email**: xiaofeng_zu@163.com

---

<div align="center">

**⭐ If you like this project, please give it a star! ⭐**

**⭐ 如果这个项目对你有帮助，请给它一个 Star！⭐**

Made with ❤️ by developers, for developers

[Report Bug](https://github.com/matthewzu/CalcPaper/issues) · [Request Feature](https://github.com/matthewzu/CalcPaper/issues) · [Documentation](docs/)

</div>
