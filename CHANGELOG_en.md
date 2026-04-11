# Changelog

# Changelog

## [2.1] - 2026-04-11

### Added
- 📆 **workday() Working Day Calculation**:
  - Syntax: `workday(start_date, working_days[, extra_holidays])`
  - Auto-skip weekends, comments list skipped holidays
  - Extra holidays separated by `/`, `+` to add (optional), `-` to remove
  - Example: `workday(Y20260411, 10, Y20260501/-Y20260412)`
- 📝 **Smart Date/Time Comments**:
  - Date result comments auto-show: YYYY-MM-DD WXX Weekday
  - Time result comments auto-show: HH:MM:SS
  - Date difference auto-convert to: Xy Xmo Xw Xd
  - Time difference auto-convert to: Xh Xm Xs
- 🔗 **hex() supports nested function calls**: e.g. `hex(swap(x))`

### Fixed
- 🛠️ Fix GUI Ctrl+Enter inserting newline while calculating

### Improved
- 📖 All examples and help text updated with swap/workday/hex(swap()) usage
- 📚 Updated all documentation

## [2.0] - 2026-04-11

### Added
- 📅 **Date/Time Arithmetic**:
  - Date literals `Yyyyymmdd`, time literals `Thhmmss`
  - Date durations (uppercase): `Mxx` (months), `Wxx` (weeks), `Dxx` (days)
  - Time durations (lowercase): `hxx` (hours), `mxx` (minutes), `sxx` (seconds)
  - Date result comments auto-show: YYYY-MM-DD WXX Weekday
  - Time result comments auto-show: HH:MM:SS
  - Date difference comments auto-convert to: Xy Xmo Xw Xd
  - Time difference comments auto-convert to: Xh Xm Xs
- 📆 **workday() Working Day Calculation**:
  - Syntax: `workday(start_date, working_days[, extra_holidays])`
  - Auto-skip weekends, comments list skipped holidays
  - Extra holidays separated by `/`, `+` to add (optional), `-` to remove
  - Example: `workday(Y20260411, 10, Y20260501/-Y20260412)`
- ✏️ **Variable Name Autocomplete**: Auto-suggest popup in GUI
- 🔄 **Auto Update Check on Startup**: Background check for latest GitHub release
- 🖥️ **GUI + CLI Dual-mode Packaging**: Unified entry `main.py`
- 📦 **Unified Version Management**: `version.py` as single source

## [1.2] - 2026-03-13

### Added
- ✨ **swap() function**: Byte order swap function
  - Auto-detect byte size (1, 2, 4, 8)
  - Can be used in expressions and assignments: `a = swap(b)`, `c = swap(d) * 2`
  - Works with bitmap: `bitmap(swap(x), 1)`
  - Commonly used for network byte order conversion
- 🔄 **Undo/Redo functionality** (CLI version):
  - CLI: Automatically saves history states
  - Saves up to 50 history states
  - API: `undo()`, `redo()`, `can_undo()`, `can_redo()`

### Improved
- 🎨 **bitmap Display Optimization**:
  - Preserve leading zeros in hexadecimal (e.g., `0x0F` not `0xF`)
  - Big endian: MSB (most significant bit) starts from index 0, goes 0→31 left to right
  - Little endian: LSB (least significant bit) starts from index 0, displays 31→0 left to right
  - Bit values right-aligned with indices
- 📖 Updated help information with swap() function description
- 🎯 Optimized expression parsing to support function nesting

---

## [1.1] - 2026-03-05

### Breaking Changes
- 🔄 **bitmap Syntax Refactoring**: Merged `endian:` command and `bitmap` keyword into function form
  - Old syntax: `endian: big` + `bitmap variable = value`
  - New syntax: `bitmap(value, 1)` or `variable = bitmap(value, 1)`
  - `bitmap(value)` or `bitmap(value, 0)` for little endian (default)
  - `bitmap(value, 1)` for big endian
  - Function has no return value, can only be used standalone or with variable assignment

### Added
- ✨ Added `bitmap()` function with parameterized endianness control
- 📚 Added documentation: `bitmap函数说明.md` and `bitmap-Function-Guide.md`

### Improved
- 🎯 Simplified bit structure viewing syntax, more functional programming style
- 📖 Updated all example code to use new bitmap function syntax
- 🔧 Optimized code structure, removed global endianness state

### Removed
- ❌ Removed `endian:` command (replaced by bitmap function parameter)
- ❌ Removed `bitmap` keyword syntax (changed to function call)

---

## [1.0] - 2026-02-11

### Added

#### General Features

- Version numbering system starting from 1.0
- Bilingual support (Chinese/English)
- Default English mode

#### GUI Interface

- Clear button shortcut Ctrl+D
- Language toggle button (中文/EN)
- Font scaling functionality (A+/A- buttons)
- Keyboard shortcuts Ctrl+Plus and Ctrl+Minus for font scaling
- Version number display in title bar
- All interface elements (buttons, labels, examples) use English in English mode
- Status bar messages support both languages
- Button bar horizontal scrolling to prevent button disappearance when font is enlarged
- Smart font size limiting system that automatically calculates maximum font based on screen size
- Fixed height button container to ensure buttons are always visible
- Real-time font size display label
- Default English interface

#### Command Line Interface

- Language mode selection parameter `--lang` or `-l`
- Examples displayed in help information, including bitmap and endian keyword usage
- Version number display in title
- Full English display in English mode
- `--version` or `-v` parameter to check version
- Default English mode

#### Documentation

##### Chinese Documentation

- [User Guide](docs/使用指南.md) - Complete usage instructions
- [Bitwise Operations Reference](docs/位运算快速参考.md) - Bitwise operators and techniques
- [Hex Comment Format](docs/16进制注释格式说明.md) - Automatic hex comment feature
- [bitmap Keyword Guide](docs/bitmap关键字说明.md) - Bit structure visualization

##### English Documentation

- [User Guide](docs/User-Guide.md) - Complete usage instructions
- [Bitwise Operations Reference](docs/Bitwise-Operations-Reference.md) - Bitwise operators and techniques
- [Hex Comment Format](docs/Hex-Comment-Format.md) - Automatic hex comment feature
- [bitmap Keyword Guide](docs/bitmap-Keyword-Guide.md) - Bit structure visualization

### Fixed

- GUI button disappearance issue when font is enlarged (using grid layout system with fixed component proportions)
- Status bar repeated message issue (removed recursive calls, optimized status update logic)
- Infinite recursion issue during font scaling
- Default language setting to English
- Added detailed usage instructions for bitmap and endian keywords in help information
- Optimized language switching logic to avoid recreating the entire interface
- Button layout uses fixed height container (60px) to ensure always visible
- Status bar uses fixed height (25px) and displays only current information
- Input/output windows occupy fixed proportions, font changes don't affect window size
- Improved scrollbar display logic, only shows when needed
- Added real-time font size display label
- Status bar message auto-restore mechanism (returns to normal after 3 seconds)
- Removed font size limitations, maximum can reach 32

### Improved

- Updated README.md with new feature descriptions
- Optimized code structure to support language switching
- Better user experience

### Technical Details

- Python 3.6+ compatible
- Uses argparse for command line argument processing
- GUI uses tkinter standard library
- No additional dependencies required

---

## Version Notes

Version format: MAJOR.MINOR

- MAJOR: Major feature updates or incompatible API changes
- MINOR: Backward-compatible feature additions