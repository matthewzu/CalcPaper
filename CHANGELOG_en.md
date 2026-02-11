# Changelog

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