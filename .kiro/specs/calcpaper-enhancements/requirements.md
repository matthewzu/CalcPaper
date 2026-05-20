# 需求文档

## 简介

CalcPaper 增强功能：为计算稿纸应用添加三项重大改进——基于 Git 的历史存储、多会话编辑器（标签页）、以及面向性能与表达力的 UI 优化。

## 术语表

- **CalcPaper**: 计算稿纸应用程序，包含计算引擎和 GUI 界面
- **Calculator_Engine**: 核心计算引擎（`CalculatorPaperAdvanced` 类），负责解析和计算表达式
- **GUI**: 基于 Tkinter + CustomTkinter 的图形用户界面（`CalculatorGUIAdvanced` 类）
- **Session**: 一个独立的计算会话，包含输入文本、输出结果和变量上下文
- **History_Store**: 基于 Git 仓库的历史存储系统，用于持久化计算历史
- **Session_Tab**: 编辑器中的标签页，每个标签页对应一个独立的 Session
- **Global_Variable**: 通过 `global()` 函数声明的跨会话共享变量
- **Variables_Tab**: GUI 中显示当前变量列表的面板
- **History_Tab**: GUI 中显示计算历史的面板
- **Diff_View**: 以 Git diff 风格展示历史变更的视图
- **Virtual_Text_Widget**: 基于虚拟化渲染的文本组件，仅渲染可视区域内容

## 需求

### 需求 1：Git 历史仓库初始化

**用户故事：** 作为用户，我希望计算历史以 Git 仓库形式存储，以便获得可靠的版本化历史记录。

#### 验收标准

1. WHEN CalcPaper 首次启动且历史仓库不存在时, THE History_Store SHALL 在用户数据目录下创建一个新的 Git 仓库
2. WHEN CalcPaper 启动且历史仓库已存在时, THE History_Store SHALL 从 Git 提交记录中加载历史数据
3. THE History_Store SHALL 使用 `~/.calcpaper/history` 作为默认仓库路径
4. IF Git 不可用或仓库初始化失败, THEN THE History_Store SHALL 回退到内存历史模式并在状态栏显示警告信息

### 需求 2：计算会话提交

**用户故事：** 作为用户，我希望每次计算操作自动保存为 Git 提交，以便追踪每一步计算变更。

#### 验收标准

1. WHEN 用户执行一次计算操作, THE History_Store SHALL 将当前输入和输出保存为一个 Git 提交
2. THE History_Store SHALL 在提交消息中包含时间戳和变更摘要
3. THE History_Store SHALL 将输入内容存储为 `session.txt` 文件，输出内容存储为 `output.txt` 文件
4. IF 当前内容与上一次提交内容相同, THEN THE History_Store SHALL 跳过提交操作

### 需求 3：Git Diff 风格历史展示

**用户故事：** 作为用户，我希望在历史标签页中以 Git diff 风格查看计算变更，以便清晰了解每次修改的内容。

#### 验收标准

1. THE History_Tab SHALL 以时间倒序列表展示所有历史提交记录
2. WHEN 用户选择一条历史记录, THE History_Tab SHALL 以 diff 视图展示该提交相对于前一次提交的变更内容
3. THE Diff_View SHALL 使用绿色标记新增行、红色标记删除行、灰色标记上下文行
4. WHEN 用户双击一条历史记录, THE GUI SHALL 将该提交的内容恢复到编辑器中

### 需求 4：多会话标签页

**用户故事：** 作为用户，我希望能创建多个计算标签页，以便同时处理不同的计算任务而互不干扰。

#### 验收标准

1. THE GUI SHALL 在编辑器区域顶部显示标签栏，支持多个 Session_Tab
2. WHEN 用户点击"新建标签"按钮, THE GUI SHALL 创建一个新的 Session_Tab，包含独立的 Calculator_Engine 实例
3. THE GUI SHALL 为每个 Session_Tab 维护独立的输入文本、输出结果和变量上下文
4. WHEN 用户切换标签页, THE GUI SHALL 保存当前标签状态并恢复目标标签的完整状态
5. WHEN 用户关闭一个标签页, THE GUI SHALL 释放该标签对应的 Calculator_Engine 资源
6. IF 用户关闭最后一个标签页, THEN THE GUI SHALL 自动创建一个新的空白标签页
7. THE GUI SHALL 支持通过键盘快捷键 Ctrl+T 新建标签、Ctrl+W 关闭当前标签、Ctrl+Tab 切换标签

### 需求 5：全局变量共享

**用户故事：** 作为用户，我希望能声明跨标签页共享的全局变量，以便在不同计算会话间传递数据。

#### 验收标准

1. WHEN 用户在表达式中使用 `global(variable_name)` 函数, THE Calculator_Engine SHALL 将该变量标记为全局变量
2. THE Calculator_Engine SHALL 在所有 Session_Tab 之间同步全局变量的值
3. WHEN 一个 Session_Tab 中的全局变量值被修改, THE Calculator_Engine SHALL 将新值传播到所有其他 Session_Tab
4. THE Variables_Tab SHALL 在全局变量旁显示"全局"标识以区分局部变量
5. IF 全局变量名与某个 Session_Tab 的局部变量名冲突, THEN THE Calculator_Engine SHALL 优先使用局部变量的值

### 需求 6：多会话持久化

**用户故事：** 作为用户，我希望多标签页状态在关闭应用后能被保存和恢复。

#### 验收标准

1. WHEN 用户关闭 CalcPaper, THE GUI SHALL 将所有 Session_Tab 的状态保存到会话文件中
2. WHEN CalcPaper 启动, THE GUI SHALL 从会话文件恢复所有之前打开的 Session_Tab
3. THE GUI SHALL 在会话文件中保存每个标签的名称、输入内容、输出内容和变量状态
4. THE GUI SHALL 在会话文件中保存全局变量的完整状态

### 需求 7：虚拟化文本渲染

**用户故事：** 作为用户，我希望编辑器在处理大量文本时保持流畅，以便高效处理复杂计算。

#### 验收标准

1. THE Virtual_Text_Widget SHALL 仅渲染当前可视区域内的文本行
2. WHEN 用户滚动编辑器, THE Virtual_Text_Widget SHALL 在 16ms 内完成可视区域的重新渲染
3. THE Virtual_Text_Widget SHALL 支持超过 10000 行文本而不产生明显的性能下降
4. THE Virtual_Text_Widget SHALL 维护与标准 Tkinter Text 组件兼容的光标定位和选择功能

### 需求 8：增量计算引擎

**用户故事：** 作为用户，我希望编辑器只重新计算发生变化的行，以便获得即时的计算反馈。

#### 验收标准

1. WHEN 用户修改输入文本, THE Calculator_Engine SHALL 识别发生变化的行及其依赖行
2. THE Calculator_Engine SHALL 仅重新计算变化行和依赖于变化行变量的后续行
3. THE Calculator_Engine SHALL 维护行级别的依赖关系图以支持增量计算
4. WHEN 单行修改不影响其他行的变量时, THE Calculator_Engine SHALL 在 10ms 内完成增量计算

### 需求 9：语法高亮优化

**用户故事：** 作为用户，我希望语法高亮更加丰富和精确，以便更好地阅读和理解计算表达式。

#### 验收标准

1. THE GUI SHALL 对输入区域的以下元素应用不同的语法高亮颜色：注释、变量名、数字字面量、运算符、函数调用、日期时间字面量
2. THE GUI SHALL 对输出区域的计算结果、错误信息、位图显示分别应用不同的高亮样式
3. WHEN 用户输入文本时, THE GUI SHALL 以增量方式更新语法高亮，仅处理变化的行
4. THE GUI SHALL 对全局变量使用特殊的高亮样式以区分局部变量

### 需求 10：实时计算预览

**用户故事：** 作为用户，我希望在输入时即时看到计算结果预览，以便快速验证表达式的正确性。

#### 验收标准

1. WHILE 用户正在输入表达式, THE GUI SHALL 在当前行右侧以淡色文本显示实时计算预览
2. THE GUI SHALL 在用户停止输入 300ms 后触发预览计算
3. IF 表达式不完整或包含语法错误, THEN THE GUI SHALL 不显示预览结果
4. WHEN 用户按下计算快捷键, THE GUI SHALL 将预览结果转换为正式输出

### 需求 11：根据输入字面量自动检测输出格式

**用户故事：** 作为用户，我希望当表达式中包含十六进制或二进制字面量时，计算结果自动以对应格式显示，以便无需手动调用 `hex()` 函数即可获得直观的输出。

#### 验收标准

1. WHEN 表达式中包含十六进制字面量（0x 前缀）, THE Calculator_Engine SHALL 将计算结果以十六进制格式（0x 前缀大写字母）输出
2. WHEN 表达式中包含二进制字面量（0b 前缀）, THE Calculator_Engine SHALL 将计算结果以二进制格式（0b 前缀）输出
3. WHEN 表达式中同时包含十六进制和二进制字面量, THE Calculator_Engine SHALL 将计算结果以十六进制格式输出
4. WHEN 表达式中不包含任何十六进制或二进制字面量, THE Calculator_Engine SHALL 将计算结果以十进制格式输出
5. WHEN 用户显式使用 `hex()` 函数包裹表达式, THE Calculator_Engine SHALL 优先使用 `hex()` 函数指定的格式，忽略自动检测逻辑
