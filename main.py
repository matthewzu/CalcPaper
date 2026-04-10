#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CalcPaper - Smart Calculator Paper
Unified entry script: supports both GUI and CLI modes

Usage:
    CalcPaper              # Launch GUI (default)
    CalcPaper --cli        # Launch CLI
    CalcPaper --cli -l zh  # Launch Chinese CLI
    CalcPaper --version    # Show version
"""

import sys
import argparse
from version import VERSION


def main():
    parser = argparse.ArgumentParser(
        description='CalcPaper - Smart Calculator for Programmers / 计算稿纸',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--cli', action='store_true',
                        help='Launch CLI mode / 启动命令行模式')
    parser.add_argument('--lang', '-l', choices=['zh', 'en'], default=None,
                        help='Language / 语言 (zh: 中文, en: English)')
    parser.add_argument('--version', '-v', action='version',
                        version=f'CalcPaper v{VERSION}')

    args = parser.parse_args()

    if args.cli:
        # CLI mode
        from calc_paper import main as cli_main
        sys.argv = ['calc_paper']
        if args.lang:
            sys.argv.extend(['--lang', args.lang])
        cli_main()
    else:
        # GUI mode (default)
        try:
            from calc_paper_gui import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"GUI not available: {e}")
            print("Try: CalcPaper --cli")
            sys.exit(1)


if __name__ == '__main__':
    main()
