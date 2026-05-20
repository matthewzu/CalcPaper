# 实施计划：CalcPaper v2 功能包

## 概述

基于现有 CalcPaper 架构，按依赖顺序实施 v2 功能包：先建立版本号单一来源，再实现核心引擎扩展（日期/时间运算 + 保留关键字），然后实现 GUI 功能（自动补全、更新检查器），接着创建统一入口脚本和更新打包流程，最后更新文档。

## 任务

- [x] 1. 创建 version.py 并统一版本号来源
  - 创建 `version.py` 文件，定义 `VERSION = "2.0"`
  - 将 `calc_paper.py` 中的 `VERSION = "1.4"` 替换为 `from version import VERSION`
  - 将 `calc_paper_gui.py` 中的 `VERSION = "1.4"` 替换为 `from version import VERSION`
  - 确保现有功能不受影响（导入路径正确）
  - _需求: 4.8_

- [-] 2. 实现日期/时间运算核心引擎
  - [x] 2.1 在 calc_paper.py 中实现日期/时间/时长字面量解析
    - 新增 `_parse_date_literal()`：解析 `Yyyyymmdd` 格式日期
    - 新增 `_parse_time_literal()`：解析 `Thhmmss` 格式时间
    - 新增 `_parse_duration_literal()`：解析大写日期时长 `Mxx`/`Wxx`/`Dxx`
    - 新增 `_parse_time_duration_literal()`：解析小写时间时长 `hxx`/`mxx`/`sxx`
    - 新增 `_format_date_result()`：将日期格式化为 `Yyyyymmdd`，时间格式化为 `Thhmmss`
    - 大小写严格区分：M（月）vs m（分钟），D（天）vs d（不使用），W（周）vs w（不使用）
    - _需求: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.19, 2.21_

  - [x] 2.2 在 calc_paper.py 中实现日期/时间运算逻辑
    - 新增 `_evaluate_date_expr()`：日期+日期时长、日期-日期时长、日期-日期（返回天数差）
    - 新增 `_evaluate_time_expr()`：时间+时间时长、时间-时间时长、时间-时间（返回秒数差）
    - 修改 `parse_line()` 方法，检测日期/时间字面量并走日期运算分支
    - 日期运算结果可赋值给变量，后续引用
    - 时间运算结果可赋值给变量，后续引用
    - 月份加减边界处理（如 1月31日 + M1 → 2月28日/29日）
    - 时间溢出检测（超出 00:00:00-23:59:59 范围时报错）
    - 混合运算类型检查（日期时长不能与时间运算，反之亦然）
    - 修改 `format_output()` 方法，支持日期/时间结果的格式化显示
    - _需求: 2.9, 2.10, 2.11, 2.12, 2.13, 2.14, 2.15, 2.16, 2.17, 2.18, 2.20_

  - [x] 2.3 实现保留关键字验证
    - 新增 `_is_reserved_keyword()` 方法，检查 `^[YTMWDhms]\d+$` 模式
    - 在变量赋值时调用验证，拒绝保留关键字作为变量名
    - 返回双语错误信息："变量名与保留关键字冲突" / "Variable name conflicts with reserved keyword"
    - _需求: 2.22, 2.23_

  - [ ] 2.4 编写日期/时间字面量往返一致性属性测试
    - **Property 4: 日期/时间字面量往返一致性**
    - 使用 hypothesis 生成随机日期和时间，验证 格式化→解析 往返一致
    - **验证: 需求 2.1, 2.2, 2.19**

  - [ ] 2.5 编写时长字面量解析属性测试
    - **Property 5: 时长字面量解析**
    - 使用 hypothesis 生成随机正整数和时长类型（M/W/D/h/m/s），验证解析正确性
    - **验证: 需求 2.3, 2.4, 2.5, 2.6, 2.7, 2.8**

  - [ ] 2.6 编写日期运算正确性属性测试
    - **Property 6: 日期运算正确性**
    - 使用 hypothesis 生成随机日期和日期时长，验证运算结果与 Python datetime 一致
    - **验证: 需求 2.9, 2.10, 2.11**

  - [ ] 2.7 编写日期运算往返一致性属性测试
    - **Property 7: 日期运算往返一致性**
    - 验证 `parse(format(parse(d) + parse(p)))` 与 `parse(d) + parse(p)` 等价
    - **验证: 需求 2.20**

  - [ ] 2.8 编写时间运算正确性属性测试
    - **Property 8: 时间运算正确性**
    - 使用 hypothesis 生成随机时间和时间时长，过滤溢出情况，验证运算结果正确
    - **验证: 需求 2.12, 2.13, 2.14**

  - [ ] 2.9 编写大小写区分属性测试
    - **Property 9: 大小写区分**
    - 验证大写 M 解析为月、小写 m 解析为分钟，类型不同
    - **验证: 需求 2.21**

  - [ ] 2.10 编写保留关键字排除属性测试
    - **Property 10: 保留关键字排除**
    - 使用 hypothesis 生成匹配 `^[YTMWDhms]\d+$` 的字符串，验证均被拒绝
    - **验证: 需求 2.22**

  - [ ] 2.11 编写日期/时间运算单元测试
    - 测试非法日期（月份>12、日期>31）、闰年2月29日、月末边界
    - 测试时间溢出报错（T230000+h3、T000000-s1）
    - 测试时间相减（T143000-T120000=9000）
    - 测试混合运算报错（日期时长+时间、时间时长+日期）
    - 测试保留关键字不可用作变量名
    - _需求: 2.1-2.23_

- [x] 3. 检查点 - 核心引擎测试
  - 确保所有测试通过，如有问题请向用户确认。

- [-] 4. 实现 GUI 变量名自动补全
  - [x] 4.1 在 calc_paper_gui.py 中实现 AutoCompletePopup 类
    - 创建 `AutoCompletePopup` 类，管理补全弹窗的显示/隐藏/选择
    - 实现 `show()`、`hide()`、`select_current()`、`move_selection()` 方法
    - 弹窗使用 `tk.Toplevel` 或 `tk.Listbox` 实现
    - _需求: 1.1, 1.3, 1.4, 1.6_

  - [x] 4.2 在 CalculatorGUIAdvanced 中集成自动补全逻辑
    - 新增 `_get_defined_variables()`：从输入区域实时解析已定义变量名
    - 新增 `_get_current_prefix()`：获取光标处正在输入的前缀
    - 新增 `_on_key_for_autocomplete()`：按键事件处理（触发补全、导航、确认）
    - 新增 `_update_autocomplete()`：根据前缀过滤候选列表
    - 新增 `_insert_completion()`：将选中变量名插入输入区域，替换前缀
    - 绑定 `<KeyRelease>` 事件触发补全
    - Tab/Enter 确认选择，Escape/点击外部关闭弹窗，上下方向键导航
    - 排除保留关键字模式的变量名
    - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

  - [ ] 4.3 编写自动补全前缀过滤属性测试
    - **Property 1: 自动补全前缀过滤**
    - 使用 hypothesis 生成随机变量名列表和前缀，验证过滤结果正确
    - **验证: 需求 1.1**

  - [ ] 4.4 编写自动补全文本插入属性测试
    - **Property 2: 自动补全文本插入**
    - 验证插入操作正确替换前缀，不影响其余文本
    - **验证: 需求 1.2**

  - [ ] 4.5 编写变量名解析属性测试
    - **Property 3: 变量名解析**
    - 使用 hypothesis 生成包含赋值行的文本，验证解析出的变量名集合正确
    - **验证: 需求 1.5**

- [-] 5. 实现 GUI 启动时后台检查更新
  - [x] 5.1 在 calc_paper_gui.py 中实现 UpdateChecker 类
    - 创建 `UpdateChecker` 类，包含 `check()`、`_fetch_latest_version()`、`_compare_versions()` 方法
    - 使用 `urllib.request` 查询 `https://api.github.com/repos/matthewzu/CalcPaper/releases/latest`
    - 设置 5 秒超时，所有网络错误静默忽略
    - 版本号比较：去除 `v` 前缀，按 `.` 分割逐段比较
    - 使用 `from version import VERSION` 获取当前版本号
    - _需求: 3.1, 3.4, 3.5, 3.7_

  - [x] 5.2 在 CalculatorGUIAdvanced 中集成更新检查器
    - 在 `__init__()` 中使用 `root.after(2000, ...)` 延迟启动检查
    - 检查在 `threading.Thread(daemon=True)` 中执行
    - 发现新版本时通过 `root.after(0, callback)` 回到主线程显示提示
    - 提示包含新版本号和下载链接，点击链接用系统浏览器打开 GitHub Releases 页面
    - 当前版本已是最新时不显示任何提示
    - _需求: 3.1, 3.2, 3.3, 3.5, 3.6_

  - [ ] 5.3 编写版本号比较属性测试
    - **Property 11: 版本号比较**
    - 使用 hypothesis 生成随机版本号对，验证比较逻辑正确
    - **验证: 需求 3.2**

  - [ ] 5.4 编写更新检查器单元测试
    - 测试网络超时模拟、JSON 格式异常、版本号格式异常
    - 测试版本号比较边界情况
    - _需求: 3.1-3.7_

- [x] 6. 检查点 - GUI 功能测试
  - 确保所有测试通过，如有问题请向用户确认。

- [-] 7. 创建统一入口脚本 main.py
  - 创建 `main.py`，使用 `argparse` 解析命令行参数
  - 无参数默认启动 GUI（`from calc_paper_gui import main as gui_main`）
  - `--cli` 参数启动 CLI（`from calc_paper import main as cli_main`）
  - `--version` / `-v` 显示版本号并退出
  - `--lang` / `-l` 传递语言参数给 GUI 或 CLI
  - GUI 模式下 tkinter 不可用时捕获 ImportError，提示使用 `--cli`
  - 使用 `from version import VERSION` 获取版本号
  - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.7, 4.8_

- [ ] 7.1 编写 main.py 单元测试
  - 测试 `--cli` 参数、`--lang zh`、无参数默认 GUI、`--version`
  - 验证 version.py 中 VERSION 可被正确导入
  - _需求: 4.1-4.8_

- [x] 8. 更新 GitHub Actions 工作流
  - [x] 8.1 修改 auto-release.yml 打包入口点
    - 将三个平台（Windows/macOS/Linux）的 PyInstaller 入口从 `calc_paper_gui.py` 改为 `main.py`
    - 确保 `version.py` 作为依赖会被自动包含
    - _需求: 4.5, 4.6_

  - [x] 8.2 更新 auto-release.yml 中的 Release 说明模板
    - 更新完整功能列表，加入 v2 新功能（日期运算、时间运算、变量补全、自动更新、CLI 打包）
    - 新增"新增功能"部分，突出 v2 新功能
    - 新增各平台下载说明（Windows/macOS/Linux）
    - 新增 GUI + CLI 双模式说明
    - 使用中英文双语描述
    - _需求: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 9. 更新 README 文档
  - 版本号更新为 2.0
  - 将"下载打包程序"提升为首选推荐使用方式，排在"从源码运行"之前
  - 新增结构化功能列表，涵盖所有已有功能和 v2 新增功能
  - v2 新功能标注 `🆕` 标记（日期运算、时间运算、变量补全、自动更新检查、CLI 打包）
  - 新增 CLI 模式使用说明（`CalcPaper --cli`）
  - 新增保留关键字说明
  - 包含从 GitHub Releases 下载各平台打包程序的说明和链接
  - Python 脚本运行方式作为备选方案
  - 中文和英文两部分内容保持一致
  - _需求: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 10. 更新知乎推广文档
  - 文件位置：`temp/知乎推广文档.md`（已存在于 dev 分支）
  - 将"下载打包程序"提升为首选推荐使用方式
  - 更新功能列表，包含 v2 新增功能（日期运算、时间运算、变量补全、自动更新、CLI 打包）
  - 版本号更新为 v2.0
  - 更新"与其他工具的对比"表格，加入 v2 新功能对比项
  - 新增日期运算功能使用示例
  - 更新"未来规划"部分，移除已实现的功能项
  - 修正许可证描述为 GPL-3.0
  - _需求: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

- [x] 11. 创建 RELEASE_NOTES_v2.0.md
  - 创建版本发布说明文档，列出 v2.0 所有新功能和改进
  - 中英文双语
  - _需求: 6.1, 6.2_

- [x] 12. 最终检查点 - 全部测试通过
  - 确保所有测试通过，如有问题请向用户确认。

## 说明

- 标记 `*` 的任务为可选任务，可跳过以加快 MVP 进度
- 每个任务引用了对应的需求编号，确保可追溯性
- 检查点任务用于阶段性验证，确保增量开发的正确性
- 属性测试验证通用正确性属性，单元测试验证具体示例和边界情况
