# CalcPaper - 计算稿纸

<div align="center">

![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.6+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-orange.svg)

**Smart Calculator with Bitwise & Date Operations | 支持位运算和日期运算的智能计算器**

[中文](#中文) | [English](#english)

</div>

---

## English

### 📖 Introduction

CalcPaper is a smart calculator designed for programmers, supporting variable references, bitwise operations, date/time arithmetic, hexadecimal/binary numbers, byte order swapping, multi-session tabs, global variables, and more — making complex calculations as simple as writing on paper.

Version: 3.2

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

# Install dependency
pip install customtkinter

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
- 🧮 🆕 **User-Defined Functions** - Define `f(x,y) = expr` and call `f(1,2)` with implicit multiplication
- 🔧 🆕 **Function Autocomplete** - Auto-suggest functions when typing, with cursor placed between parens
- 🌐 🆕 **Global Functions** - `global(func)` shares functions across all tabs
- 📑 🆕 **Functions Tab** - View all local, global, and built-in functions in one panel
- 🔢 **Multi-base Support** - Hexadecimal (0xFF), Binary (0b1010)
- ⚡ **Bitwise Operations** - Support <<, >>, &, |, ^, ~ operators
- 📊 **bitmap() Bit Visualization** - View each bit's value and index, big/little endian display
- 🔀 **swap() Byte Order Swap** - Network to host byte order conversion
- 🔢 **hex() Hex Display** - Display hexadecimal representation of values
- 📅 **Date/Time Arithmetic** - Date durations (Y/T/M/W/D) and time durations (h/m/s)
- 📆 **workday() Working Day Calculation** - Count working days with custom holidays
- 📑 🆕 **Multi-Session Tabs** - Independent calculator sessions with Ctrl+T/W/Tab shortcuts
- 🌐 🆕 **Global Variables** - `global(var)` shares variables across all tabs
- 📜 🆕 **Git History Storage** - Persistent calculation history in `~/.calcpaper/history`
- 🔢 🆕 **Auto Output Format** - Hex/binary literals auto-detect output format
- ⚡ 🆕 **Incremental Calculation** - Only recalculates changed lines and dependencies
- 👁️ 🆕 **Real-time Preview** - Live results shown while typing (300ms delay)
- 📝 🆕 **Enhanced Syntax Highlighting** - Multi-token type highlighting (comments, variables, functions, etc.)
- 🖥️ 🆕 **Virtual Text Rendering** - 10000+ lines without performance loss
- ✏️ **Variable & Function Autocomplete** - Auto-suggest popup when typing variable/function names in GUI
- 🔄 **Auto Update Check** - Background check for latest GitHub release, auto-download
- 📁 **User Data Directory** - Config and session stored in `~/.calcpaper`
- 🎨 **Modern UI (CustomTkinter)** - Rounded buttons, hover animations, flat modern design
- 🌗 **Appearance Mode** - System / Light / Dark theme switching with live preview
- 🖥️ **GUI + CLI Dual-mode Packaging** - Single executable supports both graphical and command-line interface
- 💯 **Percentage Calculation** - Direct use of 6.5%, 10%, etc.
- 💾 **Session Auto-restore** - Auto save and restore content from last session
- ⚙️ **Config Persistence** - Remember window size, language, and font settings
- ⌨️ **Customizable Shortcuts** - All keyboard shortcuts are configurable
- 🌏 **Bilingual (Chinese/English)** - Both GUI and CLI support language switching
- 🔤 **Font Scaling** - GUI supports font size adjustment
- 🔄 **Undo/Redo** - Support undo and redo operations
- 💡 **Smart Comments** - Auto hex format for bitwise operations

### 🆕 What's New in v3.2

#### Function Name Autocomplete

When typing in the editor, function names are now included in autocomplete suggestions:

- User-defined functions (local and global) shown with `()` suffix
- Built-in functions (swap, bitmap, hex, comma, global, workday) included
- Selecting a function places cursor between parentheses for immediate argument input

#### Global Function Sharing

`global()` now supports globalizing user-defined functions across all tabs:

```python
# Tab 1: define and share a function
double(x) = 2*x
global(double)

# Tab 2: use the shared function directly
result = double(5)    # = 10
```

- Global functions persist across sessions (saved to session file)
- `global(funcName)` displays the function definition in output

#### Functions Tab

New "Functions" tab in the side panel showing:

- Local functions defined in current session
- 🌐 Global functions shared across tabs
- Built-in functions with brief descriptions

### 🆕 What's New in v3.1

#### User-Defined Functions

Define reusable functions with parameters and call them in expressions:

```python
# Define a function
func(x, y) = 3*x + 5*y * 2
func(1, 2)                    # = 23

# Implicit multiplication supported
f(x) = 3x + 1
f(5)                          # = 16

# Functions can reference variables
offset = 100
g(x) = x + offset
g(5)                          # = 105

# Nested function calls
double(x) = 2*x
quad(x) = double(double(x))
quad(3)                       # = 12

# Assign function result to variable
area(r) = 3.14 * r * r
circle = area(5)              # = 78.5
```

### 🆕 What's New in v3.0

#### Multi-Session Tabs

Create multiple independent calculator sessions, each with its own variables and calculator engine:

- `Ctrl+T` new tab, `Ctrl+W` close tab, `Ctrl+Tab` switch tabs
- Double-click tab name to rename, drag tabs to reorder
- All tab states auto-saved on close, restored on next launch

#### Global Variables

Share variables across tabs using the `global()` function:

```python
# In Tab 1: define and share a variable
base = 0x40000000
global(base)

# In Tab 2: use the shared variable directly
offset = base + 0x100
```

- Local variables take priority over global variables with the same name
- Variables panel shows 🌐 icon for global variables

#### Git History Storage

Calculation history is persisted as a Git repository in `~/.calcpaper/history`:

- Each calculation auto-commits with timestamp and change summary
- History panel shows changes in Git diff style (green added / red deleted)
- Double-click history entry to restore content
- Falls back to memory mode if Git is not installed

#### Auto Output Format Detection

- Expression with `0x` literal → result in hex (e.g. `0xFF + 1 = 0x100`)
- Expression with `0b` literal → result in binary (e.g. `0b1010 + 1 = 0b1011`)
- Explicit `hex()` function always takes priority

#### Incremental Calculation Engine

Only recalculates changed lines and their dependencies, maintaining a line-level dependency graph for optimal performance.

#### Real-time Preview

Live calculation results shown as faded text to the right of the current line while typing (300ms delay trigger).

#### Enhanced Syntax Highlighting

Supports differentiated highlighting for comments, variables, numbers, operators, functions, datetime literals, global variables, errors, and results.

#### Virtual Text Rendering

Large files (>500 lines) only render the visible area, supporting 10000+ lines without performance degradation.

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

#### Global Variables (Multi-Tab)

```python
# Tab 1: define and share variables
base = 0x40000000
global(base)
page_size = 4096
global(page_size)

# Tab 2: use shared variables directly
offset = base + page_size  # 0x40001000
```

### 📚 Built-in Functions

#### User-Defined Functions

Define custom functions with parameters and use them in expressions.

```python
# Syntax: name(param1, param2, ...) = expression
func(x, y) = 3*x + 5*y
func(2, 3)                    # = 21

# Implicit multiplication: 3x means 3*x
f(x) = 3x + 1
f(5)                          # = 16

# Nested calls
double(x) = 2*x
quad(x) = double(double(x))
quad(3)                       # = 12
```

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

#### global()

Declares a variable or function as global, sharing it across all tabs.

```python
# Define variable first, then declare it global
base = 0x40000000
global(base)

page_size = 4096
global(page_size)

# Define function first, then declare it global
double(x) = 2*x
global(double)
# Other tabs can now use base, page_size, and double() directly
# Local variables/functions take priority over globals with the same name
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
- **GUI**: customtkinter (`pip install customtkinter`)
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

### 🔗 Related Projects

- [GanttPilot](https://github.com/matthewzu/GanttPilot) - Collaborative Project Manager with Gantt Chart

---

## 中文

### 📖 简介

CalcPaper（计算稿纸）是一款专为程序员设计的智能计算器，支持变量引用、位运算、日期/时间运算、16进制/2进制数值、字节序转换、多会话标签页、全局变量共享等功能，让复杂计算像在纸上写算式一样简单。

版本：3.2

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

# 安装依赖
pip install customtkinter

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
- 🧮 🆕 **自定义函数** - 定义 `f(x,y) = 表达式` 并调用 `f(1,2)`，支持隐式乘法
- 🔧 🆕 **函数名自动补齐** - 输入时自动补全函数名，选中后光标定位到括号内
- 🌐 🆕 **全局函数共享** - `global(函数名)` 跨标签页共享函数
- 📑 🆕 **函数列表标签页** - 在一个面板中查看所有局部、全局和内置函数
- 🔢 **多进制支持** - 16进制（0xFF）、2进制（0b1010）
- ⚡ **位运算** - 支持 <<、>>、&、|、^、~ 等操作
- 📊 **bitmap() 位结构可视化** - 查看每一位的值和索引，支持大端/小端显示
- 🔀 **swap() 字节序交换** - 网络字节序与本地字节序转换
- 🔢 **hex() 16进制显示** - 显示数值的16进制表示
- 📅 **日期/时间加减运算** - 支持日期时长（Y/T/M/W/D）和时间时长（h/m/s）
- 📆 **workday() 工作日计算** - 计算工作日，支持自定义节假日
- 📑 🆕 **多会话标签页** - 独立计算会话，Ctrl+T/W/Tab 快捷操作
- 🌐 🆕 **全局变量共享** - `global(变量名)` 跨标签页共享变量
- 📜 🆕 **Git 历史存储** - 计算历史持久化保存在 `~/.calcpaper/history`
- 🔢 🆕 **自动输出格式检测** - 含 0x/0b 字面量时自动以对应格式输出
- ⚡ 🆕 **增量计算引擎** - 仅重新计算变化行及其依赖行
- 👁️ 🆕 **实时计算预览** - 输入时在当前行右侧显示预览结果
- 📝 🆕 **增强语法高亮** - 多种 Token 类型差异化高亮
- 🖥️ 🆕 **虚拟化文本渲染** - 支持 10000+ 行无性能下降
- ✏️ **变量和函数自动补全** - GUI 中输入变量名或函数名时自动弹出候选列表
- 🔄 **自动检查更新** - 后台检查 GitHub 最新版本，确认后自动下载
- 📁 **用户数据目录** - 配置和会话存储在 `~/.calcpaper`
- 🎨 **现代化界面 (CustomTkinter)** - 圆角按钮、hover 动画、扁平化设计
- 🌗 **外观模式切换** - 支持 System / Light / Dark 主题，实时预览
- 🖥️ **GUI + CLI 双模式打包** - 一个可执行文件同时支持图形界面和命令行
- 💯 **百分数计算** - 直接使用 6.5%、10% 等
- 💾 **会话自动恢复** - 自动保存和恢复上次退出时的内容
- ⚙️ **配置持久化** - 记住窗口大小、语言和字体设置
- ⌨️ **可自定义快捷键** - 所有快捷键均可配置
- 🌏 **中英文双语** - GUI 和命令行都支持中英文切换
- 🔤 **字体缩放** - GUI 支持字体放大缩小
- 🔄 **撤销/恢复** - 支持撤销和恢复操作
- 💡 **智能注释** - 位运算自动显示16进制格式

### 🆕 v3.2 新功能详解

#### 函数名自动补齐

在编辑器中输入时，函数名现在也会出现在自动补全候选列表中：

- 用户定义的函数（局部和全局）带 `()` 后缀显示
- 内置函数（swap、bitmap、hex、comma、global、workday）也包含在内
- 选中函数后光标自动定位到括号内，方便立即输入参数

#### global() 支持函数全局化

`global()` 现在支持将用户定义的函数跨标签页共享：

```python
# 标签1：定义并共享函数
double(x) = 2*x
global(double)

# 标签2：直接使用共享函数
result = double(5)    # = 10
```

- 全局函数跨会话持久化保存
- `global(函数名)` 在输出中显示函数定义

#### 函数列表标签页

侧边栏新增"函数"Tab，分三个区域展示：

- 局部函数：当前会话中定义的函数
- 🌐 全局函数：跨标签页共享的函数
- 内置函数：所有内置函数及简要说明

### 🆕 v3.1 新功能详解

#### 自定义函数

定义带参数的可复用函数，并在表达式中调用：

```python
# 定义函数
func(x, y) = 3*x + 5*y * 2
func(1, 2)                    # = 23

# 支持隐式乘法（3x 等价于 3*x）
f(x) = 3x + 1
f(5)                          # = 16

# 函数体可引用已定义的变量
offset = 100
g(x) = x + offset
g(5)                          # = 105

# 嵌套函数调用
double(x) = 2*x
quad(x) = double(double(x))
quad(3)                       # = 12

# 函数结果赋值给变量
面积(r) = 3.14 * r * r
圆 = 面积(5)                  # = 78.5
```

### 🆕 v3.0 新功能详解

#### 多会话标签页

创建多个独立的计算会话，每个标签页拥有独立的变量和计算引擎：

- `Ctrl+T` 新建标签、`Ctrl+W` 关闭标签、`Ctrl+Tab` 切换标签
- 双击标签名重命名、拖动标签改变顺序
- 关闭应用时所有标签状态自动保存，下次启动恢复

#### 全局变量共享

使用 `global()` 函数跨标签页共享变量：

```python
# 在标签1中：定义并共享变量
base = 0x40000000
global(base)

# 在标签2中：直接使用共享变量
offset = base + 0x100
```

- 局部变量优先于同名全局变量
- 变量面板以 🌐 标识全局变量

#### Git 历史存储

计算历史以 Git 仓库形式持久化保存在 `~/.calcpaper/history`：

- 每次计算自动提交，提交消息含时间戳和变更摘要
- 历史面板以 Git diff 风格展示变更（绿色新增/红色删除）
- 双击历史记录恢复内容到编辑器
- Git 未安装时回退到内存模式

#### 自动输出格式检测

- 表达式含 `0x` 字面量 → 结果以十六进制输出（如 `0xFF + 1 = 0x100`）
- 表达式含 `0b` 字面量 → 结果以二进制输出（如 `0b1010 + 1 = 0b1011`）
- 显式 `hex()` 函数始终优先

#### 增量计算引擎

仅重新计算变化行及其依赖行，维护行级依赖图，大幅提升性能。

#### 实时计算预览

输入时在当前行右侧以淡色文本显示预览结果（300ms 延迟触发）。

#### 增强语法高亮

支持注释、变量、数字、运算符、函数、日期时间、全局变量、错误、结果等多种 Token 类型的差异化高亮。

#### 虚拟化文本渲染

大文件（>500行）仅渲染可视区域，支持 10000+ 行无性能下降。

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

#### 全局变量（多标签页）

```python
# 标签1：定义并共享变量
base = 0x40000000
global(base)
page_size = 4096
global(page_size)

# 标签2：直接使用共享变量
offset = base + page_size  # 0x40001000
```

### 📚 内置函数

#### 自定义函数

定义带参数的自定义函数，并在表达式中调用。

```python
# 语法：函数名(参数1, 参数2, ...) = 表达式
func(x, y) = 3*x + 5*y
func(2, 3)                    # = 21

# 隐式乘法：3x 等价于 3*x
f(x) = 3x + 1
f(5)                          # = 16

# 嵌套调用
double(x) = 2*x
quad(x) = double(double(x))
quad(3)                       # = 12
```

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

#### global()

全局变量/函数声明函数。将变量或函数声明为跨标签页共享。

```python
# 先定义变量，再用 global() 声明为全局
base = 0x40000000
global(base)

page_size = 4096
global(page_size)

# 先定义函数，再用 global() 声明为全局
double(x) = 2*x
global(double)
# 其他标签页可直接使用 base、page_size 和 double()
# 局部变量/函数优先于同名全局变量/函数
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
- **GUI**: customtkinter（`pip install customtkinter`）
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

### 🔗 相关项目

- [GanttPilot](https://github.com/matthewzu/GanttPilot) - 基于甘特图的协作式项目管理器

---

<div align="center">

**⭐ If you like this project, please give it a star! ⭐**

**⭐ 如果这个项目对你有帮助，请给它一个 Star！⭐**

Made with ❤️ by developers, for developers

[Report Bug](https://github.com/matthewzu/CalcPaper/issues) · [Request Feature](https://github.com/matthewzu/CalcPaper/issues) · [Documentation](docs/)

</div>
