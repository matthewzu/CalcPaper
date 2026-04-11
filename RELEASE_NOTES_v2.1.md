# CalcPaper v2.1 Release Notes

## 🆕 新功能 / New Features

### 📆 workday() 工作日计算 / Working Day Calculation
- 语法：`workday(起始日期, 工作日天数[, 额外节假日])`
- 默认跳过周末，注释中列出跳过的节假日
- 额外节假日用 `/` 分隔
- `Y20260501` 或 `+Y20260501`：添加为节假日（`+` 可省略）
- `-Y20260412`：从默认节假日中移除
- 示例：`workday(Y20260411, 10, Y20260501/-Y20260412)`

### 📝 智能日期/时间注释 / Smart Date/Time Comments
- 日期结果注释自动显示：X年X月X日 第XX周星期X / YYYY-MM-DD WXX Weekday
- 时间结果注释自动显示：X时X分X秒 / HH:MM:SS
- 日期差注释自动转换为：X年X月X周X天 / Xy Xmo Xw Xd
- 时间差注释自动转换为：X小时X分钟X秒 / Xh Xm Xs

### 🔗 hex() 嵌套函数支持 / Nested Function Support
- `hex(swap(x))` 等嵌套调用现在正常工作

## 🛠️ 修复 / Fixes
- 修复 GUI 中 Ctrl+Enter 同时触发换行和计算的问题

## 📖 改进 / Improvements
- 所有示例和帮助文档添加 swap/workday/hex(swap()) 用法
- 更新全部文档（README、使用指南、QUICKSTART、CHANGELOG 等）
