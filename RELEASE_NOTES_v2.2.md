# CalcPaper v2.2 Release Notes

## 🆕 新功能 / New Features

### 📁 用户数据目录 / User Data Directory
- 配置和会话文件默认存储在 `~/.calcpaper`（如 Windows 上的 `C:\Users\用户名\.calcpaper`）
- 不再存放在可执行文件目录，避免权限问题和数据丢失
- 首次启动自动从旧位置迁移配置和会话文件
- Config and session files now stored in `~/.calcpaper` by default
- Auto-migration from old executable directory on first launch

### 🔄 在线自动更新 / Auto Online Update
- 检查到新版本后弹出确认对话框
- 确认后自动下载对应平台的可执行文件并替换当前版本
- 支持 Windows (.exe)、macOS (.dmg)、Linux 平台
- 下载完成后重启即可生效
- Auto-download and replace executable after user confirmation
- Platform-aware: detects Windows/macOS/Linux assets automatically
- Restart to apply the update
