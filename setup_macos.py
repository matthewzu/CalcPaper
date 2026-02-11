"""
macOS应用打包配置
使用 py2app 将计算稿纸打包成 .app 应用

安装依赖:
    pip install py2app

打包命令:
    python setup_macos.py py2app

生成的应用位于: dist/计算稿纸.app
"""

from setuptools import setup

APP = ['calc_paper_gui.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'app_icon.icns',  # 如果有图标文件
    'plist': {
        'CFBundleName': '计算稿纸',
        'CFBundleDisplayName': '计算稿纸 - 高级版',
        'CFBundleGetInfoString': "支持位运算的智能计算器",
        'CFBundleIdentifier': "com.calculator.paper.advanced",
        'CFBundleVersion': "2.1.0",
        'CFBundleShortVersionString': "2.1.0",
        'NSHumanReadableCopyright': "Copyright © 2026, All Rights Reserved"
    }
}

setup(
    name='计算稿纸',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
