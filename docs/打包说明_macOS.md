# macOS 应用打包说明

## 📦 方法1: 使用 py2app（推荐）

### 1. 安装依赖

```bash
pip install py2app
```

### 2. 打包应用

```bash
# 开发模式（快速测试）
python setup_macos.py py2app -A

# 发布模式（独立应用）
python setup_macos.py py2app
```

### 3. 运行应用

```bash
# 打开应用
open dist/计算稿纸.app

# 或双击 dist/计算稿纸.app
```

### 4. 分发应用

生成的 `dist/计算稿纸.app` 可以：
- 直接拷贝到 `/Applications` 文件夹
- 压缩成 .zip 分发给其他用户
- 制作 .dmg 安装包（见下文）

---

## 📦 方法2: 使用 PyInstaller

### 1. 安装依赖

```bash
pip install pyinstaller
```

### 2. 打包应用

```bash
# 单文件模式
pyinstaller --onefile --windowed --name="计算稿纸" calc_paper_gui.py

# 带图标
pyinstaller --onefile --windowed --name="计算稿纸" --icon=app_icon.icns calc_paper_gui.py
```

### 3. 运行应用

```bash
open dist/计算稿纸.app
```

---

## 🎨 创建应用图标

### 1. 准备图标文件

需要一个 1024x1024 的 PNG 图片

### 2. 转换为 .icns 格式

```bash
# 使用 macOS 自带工具
mkdir MyIcon.iconset
sips -z 16 16     icon.png --out MyIcon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out MyIcon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out MyIcon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out MyIcon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out MyIcon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out MyIcon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out MyIcon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out MyIcon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out MyIcon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out MyIcon.iconset/icon_512x512@2x.png

iconutil -c icns MyIcon.iconset
mv MyIcon.icns app_icon.icns
```

---

## 📀 创建 DMG 安装包

### 方法1: 使用 create-dmg

```bash
# 安装工具
brew install create-dmg

# 创建 DMG
create-dmg \
  --volname "计算稿纸" \
  --volicon "app_icon.icns" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "计算稿纸.app" 200 190 \
  --hide-extension "计算稿纸.app" \
  --app-drop-link 600 185 \
  "计算稿纸-v2.1.dmg" \
  "dist/"
```

### 方法2: 手动创建

1. 打开"磁盘工具"
2. 文件 → 新建映像 → 空白映像
3. 将 `计算稿纸.app` 拖入
4. 创建 Applications 文件夹的快捷方式
5. 转换为压缩映像

---

## 🔐 代码签名（可选）

如果要在 App Store 或给其他用户使用，需要签名：

```bash
# 查看可用证书
security find-identity -v -p codesigning

# 签名应用
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/计算稿纸.app

# 验证签名
codesign --verify --deep --strict --verbose=2 dist/计算稿纸.app
spctl -a -t exec -vv dist/计算稿纸.app
```

---

## 📋 完整打包流程

### 快速版本（开发测试）

```bash
# 1. 安装依赖
pip install py2app

# 2. 打包
python setup_macos.py py2app -A

# 3. 测试
open dist/计算稿纸.app
```

### 发布版本（分发给用户）

```bash
# 1. 安装依赖
pip install py2app

# 2. 清理旧文件
rm -rf build dist

# 3. 打包
python setup_macos.py py2app

# 4. 测试
open dist/计算稿纸.app

# 5. 创建 DMG（可选）
brew install create-dmg
create-dmg \
  --volname "计算稿纸" \
  --window-size 800 400 \
  --icon-size 100 \
  --app-drop-link 600 185 \
  "计算稿纸-v2.1.dmg" \
  "dist/"

# 6. 分发
# 将 计算稿纸-v2.1.dmg 分发给用户
```

---

## ⚠️ 常见问题

### 1. 应用无法打开

**问题**: "计算稿纸.app 已损坏，无法打开"

**解决**:
```bash
# 移除隔离属性
xattr -cr dist/计算稿纸.app

# 或允许任何来源
sudo spctl --master-disable
```

### 2. 缺少依赖

**问题**: 应用运行时提示缺少模块

**解决**: 在 `setup_macos.py` 中添加：
```python
OPTIONS = {
    'packages': ['tkinter', 're', 'sys'],
    'includes': ['calc_paper'],
}
```

### 3. 应用体积过大

**问题**: .app 文件太大

**解决**:
```python
OPTIONS = {
    'excludes': ['matplotlib', 'numpy', 'scipy'],  # 排除不需要的包
    'optimize': 2,  # 优化字节码
}
```

---

## 📊 打包结果

### 文件结构

```
dist/
└── 计算稿纸.app/
    └── Contents/
        ├── Info.plist          # 应用信息
        ├── MacOS/
        │   └── 计算稿纸         # 可执行文件
        ├── Resources/          # 资源文件
        │   ├── app_icon.icns
        │   └── ...
        └── Frameworks/         # Python 运行时
```

### 应用大小

- **开发模式** (-A): ~10 MB（链接到系统Python）
- **发布模式**: ~50-100 MB（包含完整Python运行时）
- **优化后**: ~30-50 MB

---

## 🎯 推荐配置

### 最小配置（快速测试）

```bash
pip install py2app
python setup_macos.py py2app -A
```

### 标准配置（日常使用）

```bash
pip install py2app
python setup_macos.py py2app
```

### 完整配置（专业分发）

```bash
pip install py2app create-dmg
python setup_macos.py py2app
# 添加图标、签名、创建DMG
```

---

## 📚 参考资源

- [py2app 官方文档](https://py2app.readthedocs.io/)
- [PyInstaller 文档](https://pyinstaller.org/)
- [macOS 应用打包指南](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
