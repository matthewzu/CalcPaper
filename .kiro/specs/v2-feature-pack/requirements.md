# 需求文档

## 简介

CalcPaper v2 功能包，包含以下新功能和优化：变量名自动补全、日期加减运算、启动时后台检查更新、打包程序包含命令行接口、README 优化、GitHub Release 页面说明优化、知乎推广文档更新。

## 术语表

- **CalcPaper**: 计算稿纸应用程序，包含 GUI 和 CLI 两种界面
- **GUI**: 基于 tkinter 的图形用户界面（calc_paper_gui.py）
- **CLI**: 命令行界面（calc_paper.py）
- **输入区域**: GUI 中用户编写计算表达式的文本框
- **自动补全弹窗**: 在输入区域中弹出的变量名候选列表窗口
- **日期字面量**: 以 Y 前缀表示的日期值，格式为 Yyyyymmdd（如 Y20260410）
- **时间字面量**: 以 T 前缀表示的时间值，格式为 Thhmmss（如 T143000）
- **日期时长字面量（大写）**: 以 M/W/D 前缀表示的日期时间段，分别代表月（Mxx）、周（Wxx）、天（Dxx）
- **时间时长字面量（小写）**: 以 h/m/s 前缀表示的时间时间段，分别代表小时（hxx）、分钟（mxx）、秒（sxx）
- **保留关键字**: 以 Y、T、M、W、D、h、m、s 开头且后跟数字的标识符为系统保留关键字，不可用作变量名
- **GitHub_Releases_API**: GitHub 提供的用于查询仓库发布版本信息的 REST API
- **更新检查器**: 启动时在后台线程中检查 GitHub 最新版本的模块
- **PyInstaller**: 用于将 Python 应用打包为独立可执行文件的工具
- **打包程序**: 通过 PyInstaller 生成的独立可执行文件（CalcPaper.exe / CalcPaper.dmg / CalcPaper）
- **入口脚本**: 打包程序的统一入口点，根据命令行参数决定启动 GUI 或 CLI 模式

## 需求

### 需求 1：变量名自动补全

**用户故事：** 作为一个 CalcPaper 用户，我希望在 GUI 输入区域输入变量名时能看到自动补全建议，以便快速引用之前定义的变量。

#### 验收标准

1. WHEN 用户在 GUI 输入区域中输入字符, THE 自动补全弹窗 SHALL 显示所有名称前缀匹配当前输入的已定义变量
2. WHEN 用户从自动补全弹窗中选择一个变量名, THE GUI SHALL 将选中的变量名插入到输入区域的当前光标位置，替换已输入的前缀部分
3. WHEN 没有任何已定义变量的名称与当前输入前缀匹配, THE 自动补全弹窗 SHALL 保持隐藏状态
4. WHEN 用户按下 Escape 键或点击自动补全弹窗外部区域, THE 自动补全弹窗 SHALL 关闭
5. THE CalcPaper SHALL 从当前输入区域文本中实时解析已定义的变量名（格式为"变量名 = 表达式"的行）作为补全候选
6. WHEN 用户按下上下方向键, THE 自动补全弹窗 SHALL 在候选列表中移动选中项
7. WHEN 用户按下 Tab 键或 Enter 键, THE 自动补全弹窗 SHALL 确认当前选中的候选项并插入

### 需求 2：日期加减运算

**用户故事：** 作为一个 CalcPaper 用户，我希望能够对日期和时间进行加减运算，以便快速计算日期差值或推算未来/过去的日期。

#### 验收标准

1. WHEN 用户输入格式为 Yyyyymmdd 的日期字面量（如 Y20260410）, THE CalcPaper SHALL 将其解析为对应的日期对象
2. WHEN 用户输入格式为 Thhmmss 的时间字面量（如 T143000）, THE CalcPaper SHALL 将其解析为对应的时间对象
3. WHEN 用户输入格式为 Mxx 的日期时长字面量（如 M3，大写）, THE CalcPaper SHALL 将其解析为 xx 个月的时间段
4. WHEN 用户输入格式为 Wxx 的日期时长字面量（如 W2，大写）, THE CalcPaper SHALL 将其解析为 xx 周的时间段
5. WHEN 用户输入格式为 Dxx 的日期时长字面量（如 D10，大写）, THE CalcPaper SHALL 将其解析为 xx 天的时间段
6. WHEN 用户输入格式为 hxx 的时间时长字面量（如 h2，小写）, THE CalcPaper SHALL 将其解析为 xx 小时的时间段
7. WHEN 用户输入格式为 mxx 的时间时长字面量（如 m30，小写）, THE CalcPaper SHALL 将其解析为 xx 分钟的时间段
8. WHEN 用户输入格式为 sxx 的时间时长字面量（如 s45，小写）, THE CalcPaper SHALL 将其解析为 xx 秒的时间段
9. WHEN 用户对日期字面量和日期时长字面量（M/W/D）执行加法运算, THE CalcPaper SHALL 返回偏移后的日期，并以 Yyyyymmdd 格式显示结果
10. WHEN 用户对日期字面量和日期时长字面量（M/W/D）执行减法运算, THE CalcPaper SHALL 返回偏移后的日期，并以 Yyyyymmdd 格式显示结果
11. WHEN 用户对两个日期字面量执行减法运算, THE CalcPaper SHALL 返回两个日期之间的天数差值
12. WHEN 用户对两个时间字面量执行减法运算（如 T143000 - T120000）, THE CalcPaper SHALL 返回两个时间之间的秒数差值（整数）
13. WHEN 用户对时间字面量和时间时长字面量（h/m/s）执行加法运算（如 T120000 + h2）, THE CalcPaper SHALL 返回偏移后的时间，并以 Thhmmss 格式显示结果
14. WHEN 用户对时间字面量和时间时长字面量（h/m/s）执行减法运算（如 T143000 - m30）, THE CalcPaper SHALL 返回偏移后的时间，并以 Thhmmss 格式显示结果
15. IF 时间运算结果超出 00:00:00-23:59:59 范围（如 T230000 + h3）, THEN THE CalcPaper SHALL 显示错误信息："时间溢出：结果超出一天范围" / "Time overflow: result exceeds 24-hour range"
16. IF 用户输入的日期字面量格式不合法（如月份超过12或日期超过当月天数）, THEN THE CalcPaper SHALL 显示描述性的错误信息
17. THE CalcPaper SHALL 在 GUI 和 CLI 两种界面中均支持日期加减运算
18. WHEN 用户将日期运算结果赋值给变量, THE CalcPaper SHALL 保存该日期值，使其可在后续表达式中引用
19. THE 日期格式化输出 SHALL 将日期结果显示为 Yyyyymmdd 格式，将时间结果显示为 Thhmmss 格式
20. FOR ALL 合法的日期字面量 d 和时长字面量 p，解析(格式化(解析(d) + 解析(p))) SHALL 产生与直接计算等价的结果（往返一致性）
21. THE CalcPaper SHALL 明确区分大小写：M（月）与 m（分钟）、D（天）与 d（不使用）、W（周）与 w（不使用）、h（小时）、s（秒）均为独立的字面量前缀
22. THE 变量名验证 SHALL 排除以保留关键字前缀（Y、T、M、W、D、h、m、s 后跟数字）开头的标识符，防止与字面量语法冲突
23. THE CalcPaper 文档（需求文档、设计文档及用户文档）SHALL 明确说明保留关键字列表及其限制

### 需求 3：启动时后台检查更新

**用户故事：** 作为一个 CalcPaper 用户，我希望程序启动时能自动检查是否有新版本，以便及时获取最新功能和修复。

#### 验收标准

1. WHEN CalcPaper GUI 启动时, THE 更新检查器 SHALL 在后台线程中查询 GitHub_Releases_API 获取最新发布版本号
2. WHEN 更新检查器发现远程版本号高于当前版本号, THE CalcPaper SHALL 显示一个非阻塞的提示信息，包含新版本号和下载链接
3. WHEN 更新检查器发现当前版本已是最新, THE CalcPaper SHALL 不显示任何提示
4. IF 更新检查器无法连接到 GitHub_Releases_API（如网络不可用）, THEN THE CalcPaper SHALL 静默忽略错误，不影响正常使用
5. THE 更新检查器 SHALL 在后台线程中执行网络请求，不阻塞 GUI 主线程的启动和响应
6. WHEN 用户点击更新提示中的下载链接, THE CalcPaper SHALL 使用系统默认浏览器打开 GitHub Releases 页面
7. THE 更新检查器 SHALL 使用 GitHub 仓库地址 matthewzu/CalcPaper 作为查询目标

### 需求 4：打包程序包含命令行接口

**用户故事：** 作为一个 CalcPaper 用户，我希望打包后的可执行文件同时支持 GUI 和 CLI 模式，以便在不同场景下灵活使用。

#### 验收标准

1. WHEN 用户不带任何命令行参数运行打包程序, THE 入口脚本 SHALL 启动 GUI 图形界面
2. WHEN 用户带有 --cli 参数运行打包程序, THE 入口脚本 SHALL 启动 CLI 命令行界面
3. WHEN 用户带有 --version 或 -v 参数运行打包程序, THE 入口脚本 SHALL 显示当前版本号并退出
4. WHEN 用户带有 --lang 参数运行打包程序, THE 入口脚本 SHALL 将指定的语言传递给 GUI 或 CLI
5. THE 打包程序 SHALL 通过一个统一入口脚本（main.py）将 calc_paper.py 和 calc_paper_gui.py 的功能整合到同一个可执行文件中
6. THE GitHub_Actions 自动发布工作流（.github/workflows/auto-release.yml）SHALL 将 PyInstaller 的打包入口点从 calc_paper_gui.py 更改为统一入口脚本（main.py），其余打包流程保持不变
7. WHILE 打包程序以 CLI 模式运行, THE CalcPaper SHALL 提供与直接运行 calc_paper.py 相同的全部功能
8. THE 版本号 SHALL 在单一位置定义（version.py 中的 VERSION 常量），calc_paper.py、calc_paper_gui.py 和 main.py 均从该模块导入版本号，消除版本号重复定义

### 需求 5：优化 README 文档

**用户故事：** 作为一个潜在用户，我希望 README 文档清晰展示功能列表，并优先推荐打包程序的使用方式，以便快速了解和上手 CalcPaper。

#### 验收标准

1. THE README SHALL 将"下载打包程序"作为首选推荐的使用方式，排在"从源码运行"之前
2. THE README SHALL 包含一个结构化的功能列表，涵盖所有已有功能和 v2 新增功能
3. THE README SHALL 在功能列表中明确标注 v2 新增的功能项（日期运算、变量补全、自动更新、CLI 打包）
4. THE README SHALL 在中文和英文两个部分中保持内容一致
5. THE README SHALL 包含从 GitHub Releases 页面下载各平台打包程序的说明和链接
6. THE README SHALL 将 Python 脚本运行方式作为备选方案进行说明

### 需求 6：优化 GitHub Release 页面说明

**用户故事：** 作为一个 GitHub 用户，我希望 Release 页面的说明能准确反映当前版本包含的功能，并突出新功能，以便快速了解版本变化。

#### 验收标准

1. THE GitHub_Actions 自动发布工作流 SHALL 在 Release 说明中列出当前版本的完整功能列表
2. THE GitHub_Actions 自动发布工作流 SHALL 在 Release 说明中单独列出新增功能部分
3. THE GitHub_Actions 自动发布工作流 SHALL 在 Release 说明中包含各平台的下载说明（Windows、macOS、Linux）
4. THE GitHub_Actions 自动发布工作流 SHALL 在 Release 说明中包含打包程序同时支持 GUI 和 CLI 模式的说明
5. THE GitHub_Actions 自动发布工作流 SHALL 在 Release 说明中使用中英文双语描述

### 需求 7：更新知乎推广文档

**用户故事：** 作为项目维护者，我希望知乎推广文档与 README 保持一致的优化方向，并包含 v2 新功能的介绍，以便更好地推广项目。

#### 验收标准

1. THE 知乎推广文档 SHALL 将"下载打包程序"作为首选推荐的使用方式
2. THE 知乎推广文档 SHALL 更新功能列表，包含 v2 新增的所有功能（日期运算、变量补全、自动更新、CLI 打包）
3. THE 知乎推广文档 SHALL 更新版本号为 v2.0
4. THE 知乎推广文档 SHALL 更新"与其他工具的对比"表格，加入 v2 新功能的对比项
5. THE 知乎推广文档 SHALL 包含日期运算功能的使用示例
6. THE 知乎推广文档 SHALL 更新"未来规划"部分，移除已实现的功能项
7. THE 知乎推广文档 SHALL 修正许可证描述为 GPL-3.0（与项目实际一致）
