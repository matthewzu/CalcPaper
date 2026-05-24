# 实现计划：CalcPaper 标签页增强

## 概述

本实现计划覆盖三项核心功能：前向引用（拓扑排序计算引擎）、注释语法确认、撤销/恢复历史标签页隔离。采用增量构建方式，每步在前一步基础上推进，最终集成验证。

## 任务

- [ ] 1. 实现前向引用 — 拓扑排序计算引擎
  - [x] 1.1 在 `calc_paper.py` 中实现 `_collect_definitions()` 方法
    - 第一遍扫描所有行，收集每行定义的变量名（赋值左侧）和引用的变量名（表达式中的标识符）
    - 跳过注释行、空行、函数定义行
    - 返回 `list[dict]`，每个 dict 包含 `defines`, `uses`, `is_comment`, `is_empty`, `is_func_def` 字段
    - _需求: 1.1, 1.8_

  - [x] 1.2 在 `calc_paper.py` 中实现 `_topological_sort()` 方法
    - 基于 `_collect_definitions()` 的结果构建依赖图（邻接表）
    - 使用 Kahn 算法（BFS）进行拓扑排序
    - 检测循环依赖：排序后仍有未处理节点即为循环
    - 返回 `(eval_order: list[int], circular_lines: set[int])`
    - _需求: 1.7, 1.8_

  - [x] 1.3 在 `calc_paper.py` 中实现 `_evaluate_in_order()` 方法
    - 按拓扑序依次调用 `parse_line()` 计算每行
    - 对 `circular_lines` 中的行生成"循环依赖"错误信息
    - 将结果按原始行号存入 `self.results`
    - 处理纯表达式行（非赋值行）：在其依赖的变量全部计算完成后计算
    - _需求: 1.1, 1.6, 1.7_

  - [x] 1.4 重构 `process_text()` 方法使用拓扑排序流程
    - 替换现有逐行顺序计算逻辑为：`_collect_definitions()` → `_topological_sort()` → `_evaluate_in_order()`
    - 保持 `preset_variables` 和 `preset_functions` 参数兼容
    - 确保 `self.lines` 和 `self.results` 按原始行号对齐
    - _需求: 1.1, 1.8_

  - [ ]* 1.5 编写属性测试：前向引用解析正确性
    - **Property 1: 前向引用解析正确性**
    - 验证无环赋值集合在任意行排列下计算结果相同
    - **验证需求: 1.1**

  - [ ]* 1.6 编写属性测试：循环依赖检测
    - **Property 6: 循环依赖检测**
    - 验证包含循环依赖的赋值集合被正确检测并报错，非循环行不受影响
    - **验证需求: 1.7**

  - [ ]* 1.7 编写属性测试：依赖传播完整性
    - **Property 5: 依赖传播完整性**
    - 验证变量值改变后所有直接或间接依赖行反映新结果
    - **验证需求: 1.6**

- [ ] 2. 更新增量计算引擎支持前向引用
  - [x] 2.1 修改 `calc_incremental.py` 中 `DependencyGraph.get_affected_lines()` 方法
    - 移除 `line_idx > current_line` 的限制条件
    - 允许依赖行在定义行之前（前向引用场景）
    - _需求: 1.1, 1.6_

  - [x] 2.2 更新 `IncrementalCalcEngine.process_full()` 适配新的 `process_text()` 接口
    - 确保增量引擎调用新的拓扑排序版 `process_text()`
    - 验证 `LineResult` 的 `variables_defined` 和 `variables_used` 正确反映前向引用关系
    - _需求: 1.1_

- [x] 3. 检查点 — 前向引用功能验证
  - 确保所有测试通过，如有问题请向用户确认。

- [ ] 4. 实现撤销/恢复历史标签页隔离
  - [x] 4.1 扩展 `calc_session.py` 中 `Session` 数据类
    - 新增 `gui_history: list = field(default_factory=list)` 字段
    - 新增 `gui_history_index: int = -1` 字段
    - _需求: 3.1, 3.7_

  - [x] 4.2 重构 `calc_paper_gui.py` 中 `save_gui_state()` 方法
    - 将状态保存到 `session.gui_history` 而非 `self.gui_history`
    - 通过 `self._current_session_id` 获取当前 session 对象
    - 添加 `_current_session_id is None` 的安全检查
    - 保持 50 条历史上限逻辑
    - _需求: 3.1, 3.6, 3.8_

  - [x] 4.3 重构 `calc_paper_gui.py` 中 `undo()` 和 `redo()` 方法
    - 从当前 session 的 `gui_history` 和 `gui_history_index` 读取/写入
    - 移除 GUI 类级别的 `self.gui_history` 和 `self.gui_history_index` 属性
    - _需求: 3.2, 3.4_

  - [x] 4.4 更新标签页切换逻辑
    - 切换标签页时无需额外保存/加载历史（历史已在 session 对象中）
    - 切换后调用 `update_undo_redo_buttons()` 刷新按钮状态
    - _需求: 3.3_

  - [x] 4.5 确保关闭标签页时历史随 session 释放
    - 验证 `close_session()` 删除 session 后 Python GC 自动回收 `gui_history`
    - _需求: 3.5_

  - [ ]* 4.6 编写属性测试：撤销历史标签页隔离
    - **Property 10: 撤销历史标签页隔离**
    - 验证对 Session A 执行 `save_gui_state()` 不影响 Session B 的历史
    - **验证需求: 3.1, 3.2, 3.4, 3.8**

  - [ ]* 4.7 编写属性测试：历史栈容量上限
    - **Property 11: 历史栈容量上限**
    - 验证无论执行多少次保存操作，历史长度不超过 50
    - **验证需求: 3.6**

- [x] 5. 检查点 — 撤销/恢复隔离验证
  - 确保所有测试通过，如有问题请向用户确认。

- [ ] 6. 确认注释语法并补充测试
  - [x] 6.1 验证现有注释处理逻辑正确性
    - 确认 `parse_line()` 对 `#` 开头行返回 `(None, None, None, None, False, None)`
    - 确认行内注释 `line.split('#')[0]` 逻辑正确
    - 确认 `SyntaxHighlighter` 注释高亮逻辑存在
    - _需求: 2.1, 2.2, 2.3_

  - [ ]* 6.2 编写属性测试：注释行不产生计算输出
    - **Property 7: 注释行不产生计算输出**
    - 验证以 `#` 开头的行不产生任何计算结果
    - **验证需求: 2.1, 2.4**

  - [ ]* 6.3 编写属性测试：行内注释被正确剥离
    - **Property 8: 行内注释被正确剥离**
    - 验证 `expr # comment` 的计算结果与单独 `expr` 相同
    - **验证需求: 2.2, 2.5**

  - [ ]* 6.4 编写属性测试：变量隔离与全局变量
    - **Property 2: 标签页间变量隔离**
    - **Property 3: 全局变量跨标签页可用**
    - **Property 4: 局部变量优先于全局变量**
    - **验证需求: 1.2, 1.3, 1.4, 1.5**

- [ ] 7. 更新示例文件
  - [x] 7.1 在 `examples/features_demo.txt` 中添加前向引用演示
    - 在文件末尾新增第 13 节"前向引用 / Forward Reference"
    - 包含基本前向引用示例和多层依赖链示例
    - _需求: 1.1_

- [x] 8. 最终检查点 — 全量验证
  - 确保所有测试通过，如有问题请向用户确认。

## 备注

- 标记 `*` 的子任务为可选属性测试任务，可跳过以加速 MVP
- 每个任务引用具体需求条款以确保可追溯性
- 检查点确保增量验证，避免问题累积
- 属性测试使用 `hypothesis` 库，验证通用正确性属性
- 单元测试验证具体示例和边界条件
