# 需求文档

## 简介

本功能增强针对 CalcPaper 多标签页计算器的三个核心改进：局部变量在当前标签页内全局可用、支持 `#` 注释语法、以及撤销/恢复历史记录按标签页隔离。这些改进旨在提升多标签页场景下的使用体验和数据隔离性。

## 术语表

- **CalcPaper**: 基于 Python 的桌面多标签页计算器应用
- **标签页 (Tab)**: 一个独立的计算会话，拥有独立的输入区、输出区和计算引擎实例
- **局部变量 (Local_Variable)**: 在某个标签页内通过赋值语句定义的变量，仅在该标签页内可见
- **全局变量 (Global_Variable)**: 通过 `global()` 函数声明的跨标签页共享变量
- **注释 (Comment)**: 以 `#` 开头的文本行或行内 `#` 后的文本，不参与计算
- **撤销历史 (Undo_History)**: 记录用户在编辑器中的操作状态，支持撤销和恢复
- **计算引擎 (Calculator_Engine)**: `CalculatorPaperAdvanced` 实例，负责解析和计算表达式
- **会话管理器 (Session_Manager)**: `SessionManager` 类，管理多个标签页的生命周期和持久化
- **语法高亮器 (Syntax_Highlighter)**: `SyntaxHighlighter` 类，负责对输入文本进行语法着色

## 需求

### 需求 1：局部变量在当前标签页内全局可用（含前向引用）

**用户故事：** 作为一个用户，我希望在标签页内定义的变量可以在该标签页的任意位置引用（包括定义行之前的行），这样我可以自由组织计算逻辑而不受行顺序限制。

**示例：**
```
a = b * 3    # b 在下面才定义，但这里也能用
b = 1        # 结果：a = 3
```

#### 验收标准

1. WHEN 用户在标签页内的某一行定义变量（如 `b = 1`），THE Calculator_Engine SHALL 使该变量在同一标签页内的所有行中可用，包括定义行之前的行（前向引用）
2. WHEN 用户切换到另一个标签页，THE Calculator_Engine SHALL 仅加载该目标标签页自身定义的局部变量，不包含其他标签页的局部变量
3. WHEN 用户在标签页 A 中定义变量 `x = 5`，THE Calculator_Engine SHALL 确保标签页 B 中引用 `x` 时报告"变量未定义"错误（除非标签页 B 自身也定义了 `x`）
4. WHEN 用户通过 `global()` 声明全局变量，THE Calculator_Engine SHALL 使该变量在所有标签页中可用
5. WHEN 局部变量与全局变量同名，THE Calculator_Engine SHALL 优先使用当前标签页的局部变量值
6. WHEN 用户修改某行的变量赋值，THE Calculator_Engine SHALL 重新计算所有依赖该变量的行（无论在其前方还是后方）
7. WHEN 存在循环依赖（如 `a = b`, `b = a`），THE Calculator_Engine SHALL 检测循环并对涉及循环的行报告"循环依赖"错误
8. WHEN 计算引擎处理标签页内容时，THE Calculator_Engine SHALL 通过多遍扫描或拓扑排序解决变量依赖关系，而非逐行顺序计算

### 需求 2：支持注释语法

**用户故事：** 作为一个用户，我希望能在计算文本中添加注释来记录思路或标注说明，这样我的计算过程更易于理解和维护。

#### 验收标准

1. WHEN 一行以 `#` 字符开头（允许前导空格），THE Calculator_Engine SHALL 将该行视为注释行，不进行计算，不产生输出
2. WHEN 一行中包含 `#` 字符，THE Calculator_Engine SHALL 忽略 `#` 及其后的所有文本，仅计算 `#` 之前的表达式
3. WHEN 注释行存在于输入中，THE Syntax_Highlighter SHALL 将注释文本以注释颜色（深色主题绿色 `#6A9955`，浅色主题绿色 `#008000`）高亮显示
4. WHEN 注释行存在于输入中，THE Calculator_Engine SHALL 在输出中对应位置不产生任何结果行（保持空行或跳过）
5. THE Calculator_Engine SHALL 支持在变量赋值行中使用行内注释（如 `rent = 1000 # 月租金`），仅计算 `#` 之前的部分
6. WHEN 表达式中包含十六进制字面量（如 `0xFF`），THE Calculator_Engine SHALL 正确区分十六进制中的字符与注释标记 `#`

### 需求 3：撤销/恢复历史按标签页隔离

**用户故事：** 作为一个用户，我希望每个标签页有独立的撤销/恢复历史，这样在一个标签页中撤销操作不会影响其他标签页的内容。

#### 验收标准

1. THE CalcPaper SHALL 为每个标签页维护独立的撤销/恢复历史栈
2. WHEN 用户在标签页 A 中执行撤销操作，THE CalcPaper SHALL 仅回退标签页 A 的内容，标签页 B 的内容保持不变
3. WHEN 用户切换标签页，THE CalcPaper SHALL 保存当前标签页的历史状态，并加载目标标签页的历史状态
4. WHEN 用户切换到目标标签页后执行撤销，THE CalcPaper SHALL 使用目标标签页自身的历史记录进行回退
5. WHEN 用户关闭标签页，THE CalcPaper SHALL 释放该标签页对应的撤销历史内存
6. THE CalcPaper SHALL 为每个标签页独立维护最多 50 条历史记录
7. WHEN 用户新建标签页，THE CalcPaper SHALL 为该标签页初始化一个空的撤销历史栈
8. WHEN 用户在标签页中编辑内容，THE CalcPaper SHALL 仅将状态变更记录到当前活跃标签页的历史栈中
