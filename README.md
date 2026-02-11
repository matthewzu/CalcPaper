# CalcPaper - 计算稿纸

<div align="center">

![Version](https://img.shields.io/badge/version-1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.6+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**支持位运算的智能计算器 | Smart Calculator with Bitwise Operations**

[English](#english) | [中文](#中文)

</div>

---

## 中文

### 📖 简介

CalcPaper（计算稿纸）是一款专为程序员设计的智能计算器，支持变量引用、位运算、16进制/2进制数值，让复杂计算像在纸上写算式一样简单。

版本：1.0

### ✨ 核心特性

- 🧮 **变量引用** - 定义变量，后续直接使用
- 🔢 **多进制支持** - 16进制（0xFF）、2进制（0b1010）
- ⚡ **位运算** - 支持 <<、>>、&、|、^、~ 等操作
- 📊 **位结构显示** - 可视化查看每一位的值和索引
- 🔄 **字节序支持** - 大端/小端字节序切换
- 💯 **百分数计算** - 直接使用 6.5%、10% 等
- 🎨 **图形界面** - 友好的 GUI 界面（可选）
- 🌏 **中英文切换** - GUI和命令行都支持中英文
- 🔤 **字体缩放** - GUI支持字体放大缩小
- ⌨️ **快捷键** - 丰富的快捷键支持
- 💡 **智能注释** - 位运算自动显示16进制格式

### 🚀 快速开始

#### 安装

```bash
# 克隆仓库
git clone https://github.com/matthewzu/CalcPaper.git
cd CalcPaper

# 无需安装依赖（使用 Python 标准库）
```

#### 运行

```bash
# 图形界面版本（推荐）
python calc_paper_gui.py

# 命令行版本（中文）
python calc_paper.py

# 命令行版本（英文）
python calc_paper.py --lang en

# 查看版本
python calc_paper.py --version
```

### 📝 使用示例

#### 示例1: 基础计算

```python
# 月度预算
工资 = 8000
房租 = 2000
餐费 = 30 * 25
结余 = 工资 - 房租 - 餐费
```

**输出：**

```bash
工资 = 8000        = 8000
房租 = 2000        = 2000
餐费 = 30 * 25     = 750
结余 = 工资 - 房租 - 餐费  = 5250  # 8000 - 2000 - 750
```

#### 示例2: 位运算

```python
# 设置字节序
endian: big

# RGB 颜色提取
颜色 = 0xFF8040
R = (颜色 >> 16) & 0xFF
G = (颜色 >> 8) & 0xFF
B = 颜色 & 0xFF

# 使用 bitmap 查看位结构
bitmap 查看颜色 = 颜色
```

**输出：**

```bash
颜色 = 0xFF8040                    = 16744512
R = (颜色 >> 16) & 0xFF            = 255  # 0xFF8040 >> 16 & 0xFF
G = (颜色 >> 8) & 0xFF             = 128  # 0xFF8040 >> 8 & 0xFF
B = 颜色 & 0xFF                    = 64   # 0xFF8040 & 0xFF

bitmap 查看颜色 = 颜色              = 16744512 (0xFF8040, 0b111111111000000001000000)
  十六进制: 0xFF8040
  二进制: 0b111111111000000001000000
  位数: 24 bits (3 bytes)
  位索引 (大端字节序):
    |23 22 21 20 |19 18 17 16 |15 14 13 12 |11 10  9  8 |7 6 5 4 |3 2 1 0 |
    |1  1  1  1  |1  1  1  1  |1  0  0  0  |0  0  0  0  |0 1 0 0 |0 0 0 0 |
```

#### 示例3: 网络编程

```python
# IP 地址解析
IP = 0xC0A80001  # 192.168.0.1
段1 = (IP >> 24) & 0xFF  # 192
段2 = (IP >> 16) & 0xFF  # 168
段3 = (IP >> 8) & 0xFF   # 0
段4 = IP & 0xFF          # 1
```

#### 示例4: 购物折扣

```python
# 双十一购物
原价 = 299
店铺折扣 = 20%
优惠券 = 30

折后价 = 原价 * (1 - 店铺折扣)
最终价 = 折后价 - 优惠券
```

### 🎯 适用场景

| 场景 | 示例 |
|------|------|
| 🔧 **嵌入式开发** | 寄存器配置、位标志管理 |
| 🌐 **网络编程** | IP地址解析、协议字段提取 |
| 🎨 **图形处理** | RGB颜色分解、像素操作 |
| 💾 **数据处理** | 位掩码、数据打包/解包 |
| 📊 **日常计算** | 财务预算、购物折扣 |

### 📚 文档

#### 中文文档

- [使用指南](docs/使用指南.md) - 完整的使用说明和示例
- [位运算快速参考](docs/位运算快速参考.md) - 位运算操作符和技巧
- [16进制注释格式说明](docs/16进制注释格式说明.md) - 自动16进制注释功能
- [bitmap关键字说明](docs/bitmap关键字说明.md) - 位结构可视化功能

#### English Documentation

- [User Guide](docs/User-Guide.md) - Complete usage instructions and examples
- [Bitwise Operations Reference](docs/Bitwise-Operations-Reference.md) - Bitwise operators and techniques
- [Hex Comment Format](docs/Hex-Comment-Format.md) - Automatic hex comment feature
- [bitmap Keyword Guide](docs/bitmap-Keyword-Guide.md) - Bit structure visualization

### 🖥️ 系统要求

- **Python**: 3.6+
- **GUI**: tkinter（Python自带）
- **平台**: Windows、macOS、Linux

### 📦 打包分发

#### macOS 应用

```bash
# 安装打包工具
pip install py2app

# 打包应用
python setup_macos.py py2app

# 运行
open dist/CalcPaper.app
```

#### Windows 应用

```bash
# 安装打包工具
pip install pyinstaller

# 打包应用
pyinstaller --onefile --windowed --name="CalcPaper" calc_paper_gui.py

# 运行
dist\CalcPaper.exe
```

### 🎨 界面预览

#### GUI 版本

- 双栏布局：输入区域 | 输出结果
- 语法高亮显示
- 快捷键支持：
  - F5 或 Ctrl+Enter：计算
  - Ctrl+D：清空
  - Ctrl+L：加载示例
  - Ctrl+O：打开文件
  - Ctrl+S：保存结果
  - Ctrl+Plus：放大字体
  - Ctrl+Minus：缩小字体
- 中英文切换按钮
- 字体缩放按钮（A+/A-）
- 文件操作（打开、保存）

#### 命令行版本

- 交互式输入
- 实时计算
- 中英文模式切换（--lang 参数）
- 示例在 help 信息中显示
- 适合脚本调用

### 🤝 贡献

欢迎提交 Issue 和 Pull Request！

#### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

#### 贡献指南

- 遵循现有代码风格
- 添加必要的测试
- 更新相关文档
- 提供清晰的提交信息

### 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

### 🙏 致谢

- 灵感来源于 uTools 计算稿纸
- 感谢所有贡献者和用户的反馈

### 📮 联系方式

- **Issues**: [GitHub Issues](https://github.com/matthewzu/CalcPaper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/matthewzu/CalcPaper/discussions)
- **Email**: xiaofeng_zu@163.com

### 🌟 Star History

如果这个项目对你有帮助，请给它一个 Star ⭐

---

## English

### 📖 Introduction

CalcPaper is a smart calculator designed for programmers, supporting variable references, bitwise operations, hexadecimal/binary numbers, making complex calculations as simple as writing on paper.

Version: 1.0

### ✨ Key Features

- 🧮 **Variable References** - Define variables and use them later
- 🔢 **Multi-base Support** - Hexadecimal (0xFF), Binary (0b1010)
- ⚡ **Bitwise Operations** - Support <<, >>, &, |, ^, ~ operators
- 📊 **Bit Structure Display** - Visualize each bit's value and index
- 🔄 **Endianness Support** - Big-endian/Little-endian switching
- 💯 **Percentage Calculation** - Direct use of 6.5%, 10%, etc.
- 🎨 **GUI Interface** - User-friendly graphical interface (optional)
- 🌏 **Language Toggle** - Both GUI and CLI support Chinese/English
- 🔤 **Font Scaling** - GUI supports font size adjustment
- ⌨️ **Keyboard Shortcuts** - Rich shortcut support
- 💡 **Smart Comments** - Auto hex format for bitwise operations

### 🚀 Quick Start

#### Installation

```bash
# Clone the repository
git clone https://github.com/matthewzu/CalcPaper.git
cd CalcPaper

# No dependencies needed (uses Python standard library)
```

#### Run

```bash
# GUI version (recommended)
python calc_paper_gui.py

# Command-line version (Chinese)
python calc_paper.py

# Command-line version (English)
python calc_paper.py --lang en

# Check version
python calc_paper.py --version
```

### 📝 Usage Examples

#### Example 1: Basic Calculation

```python
# Monthly budget
salary = 8000
rent = 2000
food = 30 * 25
balance = salary - rent - food
```

#### Example 2: Bitwise Operations

```python
# Set endianness
endian: big

# RGB color extraction
color = 0xFF8040
R = (color >> 16) & 0xFF  # 255
G = (color >> 8) & 0xFF   # 128
B = color & 0xFF          # 64

# View bit structure with bitmap
bitmap view_color = color
```

#### Example 3: Network Programming

```python
# IP address parsing
IP = 0xC0A80001  # 192.168.0.1
seg1 = (IP >> 24) & 0xFF  # 192
seg2 = (IP >> 16) & 0xFF  # 168
seg3 = (IP >> 8) & 0xFF   # 0
seg4 = IP & 0xFF          # 1
```

### 🎯 Use Cases

| Scenario | Examples |
|----------|----------|
| 🔧 **Embedded Development** | Register configuration, bit flag management |
| 🌐 **Network Programming** | IP parsing, protocol field extraction |
| 🎨 **Graphics Processing** | RGB color decomposition, pixel operations |
| 💾 **Data Processing** | Bit masking, data packing/unpacking |
| 📊 **Daily Calculations** | Financial budgeting, shopping discounts |

### 📚 Documentation

- [User Guide](docs/使用指南.md)
- [Bitwise Operations Quick Reference](docs/位运算快速参考.md)
- [Hex Comment Format](docs/16进制注释格式说明.md)
- [Bitmap Keyword](docs/bitmap关键字说明.md)

### 🖥️ Requirements

- **Python**: 3.6+
- **GUI**: tkinter (included with Python)
- **Platform**: Windows, macOS, Linux

### 📦 Distribution

#### macOS App

```bash
pip install py2app
python setup_macos.py py2app
open dist/CalcPaper.app
```

#### Windows App

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="CalcPaper" calc_paper_gui.py
dist\CalcPaper.exe
```

### 🤝 Contributing

Issues and Pull Requests are welcome!

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

### 📄 License

MIT License - see [LICENSE](LICENSE) file

### 🙏 Acknowledgments

- Inspired by uTools Calculator Paper
- Thanks to all contributors

### 📮 Contact

- **Issues**: [GitHub Issues](https://github.com/matthewzu/CalcPaper/issues)
- **Email**: xiaofeng_zu@163.com

---

<div align="center">

**⭐ If you like this project, please give it a star! ⭐**

Made with ❤️ by developers, for developers

[Report Bug](https://github.com/matthewzu/CalcPaper/issues) · [Request Feature](https://github.com/matthewzu/CalcPaper/issues) · [Documentation](docs/)

</div>
