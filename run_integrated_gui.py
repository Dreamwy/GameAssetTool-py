#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多媒体处理工具集 - 整合GUI启动脚本
包含视频转PNG和自动去背景两大功能
"""

import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    try:
        print("启动多媒体处理工具集...")
        print("功能包括：")
        print("  🎬 视频转PNG - 将视频文件转换为PNG图片序列")
        print("  🖼️ 自动去背景 - 智能移除图片背景")
        print()

        from integrated_gui import main as gui_main
        gui_main()

    except ImportError as e:
        print(f"导入错误: {e}")
        print()
        print("请确保已安装所需依赖:")
        print("pip install -r requirements.txt")
        print()
        print("特别注意：")
        print("- 请确保已安装PyQt5: pip install PyQt5")
        print("- 如果rembg安装失败，请尝试: pip install rembg")
        print("- 首次使用AI去背景功能会下载模型文件（约180MB）")

    except Exception as e:
        print(f"启动失败: {e}")
        print("详细错误信息:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()