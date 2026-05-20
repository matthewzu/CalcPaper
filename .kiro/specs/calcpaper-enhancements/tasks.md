# 实施计划：CalcPaper 增强功能

## 概述

基于需求文档和设计文档，将 CalcPaper 增强功能分解为增量实施步骤。每个任务构建在前一个任务之上，最终将所有组件集成到 GUI 中。实施语言为 Python，测试框架使用 Hypothesis 进行属性测试，pytest 进行单元测试。

## 任务

- [x] 1. 搭建测试基础设施和项目结构
  - 创建 `tests/` 目录和 `tests/__init__.py`
  - 创建 `tests/conftest.py`，配置 Hypothesis 设置（min 100 iterations）
  - 在项目根目录添加 `pytest.ini` 或 `pyproject.toml` 中配置 pytest
  - 确保 `hypothesis` 和 `pytest` 依赖可用
  - _需求: 全部_

- [x] 2. 实现自动输出格式检测模块
  - [x] 2.1 在 `calc_paper.py` 中实现 `OutputFormat` 枚举和 `detect_output_format()` 函数
    - 定义 `OutputFormat` 枚举（DECIMAL, HEXADECIMAL, BINARY）
    - 实现 `detect_output_format(expression, has_explicit_hex_func)` 函数
    - 按优先级检测：显式 hex() > 0x 字面量 > 0b 字面量 > 十进制
    - 集成到现有 `parse_line()` 方法中，替换硬编码的格式逻辑
    - _需求: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [ ]* 2.2 编写格式检测属性测试
    - **Property 18: 输出格式自动检测**
    - **验证: 需求 11.1, 11.2, 11.3, 11.4, 11.5**
    - 测试文件: `tests/test_format_detection.py`

- [x] 3. 实现 Git 历史存储模块
  - [x] 3.1 创建 `calc_history.py`，实现 `GitHistoryStore` 类
    - 实现 `__init__`：初始化或打开 Git 仓库（默认路径 `~/.calcpaper/history`）
    - 实现 `is_available()`：检查 Git 是否可用
    - 实现 `commit()`：将 input/output 保存为 `session.txt`/`output.txt` 并提交
    - 实现 `has_changes()`：检查内容是否与最近提交不同
    - 实现 `get_history()`：获取历史记录列表（时间倒序）
    - 实现 `get_diff()`：获取指定提交的 diff
    - 实现 `restore()`：恢复指定提交的内容
    - 实现 `HistoryEntry` 和 `DiffResult` 数据类
    - 实现 Git 不可用时的回退逻辑（内存历史模式）
    - _需求: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 3.1, 3.4_

  - [ ]* 3.2 编写 Git 历史存储属性测试
    - **Property 1: 提交内容往返一致性**
    - **验证: 需求 2.1, 2.3, 3.4**
    - 测试文件: `tests/test_history_store.py`

  - [ ]* 3.3 编写提交消息格式属性测试
    - **Property 2: 提交消息格式正确性**
    - **验证: 需求 2.2**
    - 测试文件: `tests/test_history_store.py`

  - [ ]* 3.4 编写重复提交幂等性属性测试
    - **Property 3: 重复内容提交幂等性**
    - **验证: 需求 2.4**
    - 测试文件: `tests/test_history_store.py`

  - [ ]* 3.5 编写历史记录排序属性测试
    - **Property 4: 历史记录时间倒序**
    - **验证: 需求 3.1**
    - 测试文件: `tests/test_history_store.py`

- [x] 4. 检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [x] 5. 实现全局变量存储模块
  - [x] 5.1 在 `calc_session.py` 中实现 `GlobalVariableStore` 类
    - 实现 `set()`/`get()`/`has()`/`get_all()` 方法
    - 实现 `subscribe()` 监听器机制，变量变更时通知所有监听者
    - _需求: 5.1, 5.2, 5.3_

  - [ ]* 5.2 编写全局变量跨会话同步属性测试
    - **Property 7: 全局变量跨会话同步**
    - **验证: 需求 5.1, 5.2, 5.3**
    - 测试文件: `tests/test_global_variables.py`

  - [ ]* 5.3 编写局部变量优先级属性测试
    - **Property 8: 局部变量优先于全局变量**
    - **验证: 需求 5.5**
    - 测试文件: `tests/test_global_variables.py`

- [x] 6. 实现多会话管理模块
  - [x] 6.1 在 `calc_session.py` 中实现 `Session` 数据类和 `SessionManager` 类
    - 实现 `Session` 数据类（session_id, name, input_text, output_text, variables, calculator, created_at）
    - 实现 `create_session()`：创建新会话，分配独立的 CalculatorPaperAdvanced 实例
    - 实现 `close_session()`：关闭并释放会话资源
    - 实现 `get_session()`/`list_sessions()`
    - 实现 `save_all()`/`load_all()`：JSON 格式持久化（版本 2 格式）
    - 关闭最后一个标签页时自动创建新空白会话
    - _需求: 4.1, 4.2, 4.3, 4.5, 4.6, 6.1, 6.2, 6.3, 6.4_

  - [ ]* 6.2 编写会话变量隔离性属性测试
    - **Property 5: 会话变量隔离性**
    - **验证: 需求 4.2, 4.3**
    - 测试文件: `tests/test_session_manager.py`

  - [ ]* 6.3 编写标签切换状态保持属性测试
    - **Property 6: 标签切换状态保持**
    - **验证: 需求 4.4**
    - 测试文件: `tests/test_session_manager.py`

  - [ ]* 6.4 编写多会话持久化往返一致性属性测试
    - **Property 9: 多会话持久化往返一致性**
    - **验证: 需求 6.1, 6.2, 6.3, 6.4**
    - 测试文件: `tests/test_session_manager.py`

- [x] 7. 检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [x] 8. 实现增量计算引擎
  - [x] 8.1 创建 `calc_incremental.py`，实现 `DependencyGraph` 类
    - 实现 `build()`：从 LineResult 列表构建依赖图
    - 实现 `get_affected_lines()`：给定变化行，返回所有需要重算的行（含传递依赖）
    - 实现 `update_line()`：更新单行依赖信息
    - 定义 `LineResult` 数据类
    - _需求: 8.3_

  - [x] 8.2 实现 `IncrementalCalcEngine` 类
    - 实现 `process_full()`：全量计算并建立依赖图
    - 实现 `process_incremental()`：增量计算（仅重算变化行及其依赖行）
    - 实现 `get_dependencies()`/`get_dependents()`
    - 实现 `preview_line()`：预览单行计算结果（不修改状态）
    - 包装现有 `CalculatorPaperAdvanced` 引擎
    - _需求: 8.1, 8.2, 8.4, 10.4_

  - [ ]* 8.3 编写增量计算等价性属性测试
    - **Property 12: 增量计算等价于全量计算**
    - **验证: 需求 8.1, 8.2**
    - 测试文件: `tests/test_incremental_calc.py`

  - [ ]* 8.4 编写依赖图正确性属性测试
    - **Property 13: 依赖图正确性**
    - **验证: 需求 8.3**
    - 测试文件: `tests/test_incremental_calc.py`

  - [ ]* 8.5 编写预览无效表达式属性测试
    - **Property 16: 无效表达式预览返回空**
    - **验证: 需求 10.3**
    - 测试文件: `tests/test_preview.py`

  - [ ]* 8.6 编写预览结果一致性属性测试
    - **Property 17: 预览结果与正式计算一致**
    - **验证: 需求 10.4**
    - 测试文件: `tests/test_preview.py`

- [x] 9. 实现虚拟化文本渲染组件
  - [x] 9.1 创建 `calc_virtual_text.py`，实现 `VirtualTextWidget` 类
    - 继承 `ctk.CTkFrame`，实现虚拟化渲染逻辑
    - 实现 `set_content()`/`get_content()`：设置和获取全部内容
    - 实现 `get_visible_range()`：获取当前可视行范围
    - 实现 `scroll_to_line()`/`render_visible()`：滚动和渲染
    - 实现兼容 Tkinter Text 的接口：`insert()`/`delete()`/`get()`
    - 支持超过 10000 行文本
    - _需求: 7.1, 7.2, 7.3, 7.4_

  - [ ]* 9.2 编写虚拟文本可视范围属性测试
    - **Property 10: 虚拟文本可视范围正确性**
    - **验证: 需求 7.1**
    - 测试文件: `tests/test_virtual_text.py`

  - [ ]* 9.3 编写虚拟文本光标往返属性测试
    - **Property 11: 虚拟文本光标往返一致性**
    - **验证: 需求 7.4**
    - 测试文件: `tests/test_virtual_text.py`

- [x] 10. 实现语法高亮引擎
  - [x] 10.1 创建 `calc_syntax.py`，实现 `SyntaxHighlighter` 类
    - 定义 `Token` 数据类和 `TOKEN_TYPES` 列表
    - 实现 `tokenize_line()`：将一行文本分词为 Token 列表
    - 实现 `highlight_full()`：全量高亮
    - 实现 `highlight_lines()`：增量高亮指定行
    - 实现 `set_theme()`：切换主题配色
    - 支持高亮类型：comment, variable, number, operator, function, datetime, global_var, error, result, bitmap
    - _需求: 9.1, 9.2, 9.3, 9.4_

  - [ ]* 10.2 编写语法分词正确性属性测试
    - **Property 14: 语法分词正确性**
    - **验证: 需求 9.1, 9.2, 9.4**
    - 测试文件: `tests/test_syntax.py`

  - [ ]* 10.3 编写增量高亮等价性属性测试
    - **Property 15: 增量高亮等价于全量高亮**
    - **验证: 需求 9.3**
    - 测试文件: `tests/test_syntax.py`

- [x] 11. 检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [x] 12. 集成多标签页 UI 到 GUI
  - [x] 12.1 在 `calc_paper_gui.py` 中实现标签栏和多会话 UI
    - 在编辑器区域顶部添加标签栏（TabBar）
    - 实现新建标签、关闭标签、切换标签的 UI 交互
    - 绑定快捷键：Ctrl+T 新建、Ctrl+W 关闭、Ctrl+Tab 切换
    - 每个标签页关联独立的 Session 和 CalcEngine 实例
    - 标签切换时保存/恢复完整状态（输入、输出、变量）
    - 关闭最后一个标签时自动创建新空白标签
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [x] 12.2 集成全局变量到 GUI
    - 在 Variables_Tab 中区分显示全局变量（带"全局"标识）和局部变量
    - 实现 `global()` 函数调用的 UI 反馈
    - 全局变量变更时刷新所有标签页的变量面板
    - _需求: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 12.3 集成会话持久化
    - 关闭应用时调用 `SessionManager.save_all()` 保存所有标签状态
    - 启动时调用 `SessionManager.load_all()` 恢复所有标签
    - 使用版本 2 的 JSON 格式（含 global_variables 和 sessions 数组）
    - _需求: 6.1, 6.2, 6.3, 6.4_

- [x] 13. 集成 Git 历史和 Diff 视图到 GUI
  - [x] 13.1 在 History_Tab 中集成 GitHistoryStore
    - 以时间倒序列表展示历史提交记录
    - 选择历史记录时显示 diff 视图（绿色新增、红色删除、灰色上下文）
    - 双击历史记录恢复内容到编辑器
    - 计算操作后自动提交到 Git 历史
    - Git 不可用时显示状态栏警告
    - _需求: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4_

- [x] 14. 集成增量计算和实时预览到 GUI
  - [x] 14.1 替换现有计算逻辑为增量计算引擎
    - 使用 `IncrementalCalcEngine` 包装现有 `CalculatorPaperAdvanced`
    - 文本修改时触发增量计算而非全量计算
    - 增量计算结果与全量不一致时自动回退
    - _需求: 8.1, 8.2, 8.3, 8.4_

  - [x] 14.2 实现实时计算预览 UI
    - 在当前行右侧以淡色文本显示预览结果
    - 用户停止输入 300ms 后触发预览计算
    - 表达式不完整时不显示预览
    - 按计算快捷键时将预览转为正式输出
    - _需求: 10.1, 10.2, 10.3, 10.4_

- [x] 15. 集成虚拟文本和语法高亮到 GUI
  - [x] 15.1 将 VirtualTextWidget 集成到编辑器
    - 替换标准 Tkinter Text 为 VirtualTextWidget（大文件时）
    - 确保光标定位和选择功能兼容
    - 渲染异常时回退到标准 Text 组件
    - _需求: 7.1, 7.2, 7.3, 7.4_

  - [x] 15.2 集成 SyntaxHighlighter 到输入/输出区域
    - 输入区域高亮：注释、变量名、数字、运算符、函数、日期时间、全局变量
    - 输出区域高亮：计算结果、错误信息、位图显示
    - 文本修改时增量更新高亮
    - _需求: 9.1, 9.2, 9.3, 9.4_

- [x] 16. 最终检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

## 备注

- 标记 `*` 的任务为可选任务，可跳过以加速 MVP 开发
- 每个任务引用了具体的需求编号以确保可追溯性
- 检查点确保增量验证
- 属性测试验证通用正确性属性（使用 Hypothesis 库）
- 单元测试验证具体示例和边界情况
