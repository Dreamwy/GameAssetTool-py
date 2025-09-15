#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频转PNG工具使用示例
"""

from video_to_png import VideoToPNG
import os

def example_usage():
    """演示如何使用VideoToPNG类"""
    
    # 创建转换器实例
    converter = VideoToPNG()
    
    # 示例视频文件路径（请替换为实际的视频文件）
    video_path = "sample_video.mp4"
    
    # 检查视频文件是否存在
    if not os.path.exists(video_path):
        print(f"示例视频文件 '{video_path}' 不存在")
        print("请将您的视频文件重命名为 'sample_video.mp4' 或修改此脚本中的路径")
        return
    
    try:
        # 1. 获取视频信息
        print("=== 获取视频信息 ===")
        info = converter.get_video_info(video_path)
        if info:
            print(f"分辨率: {info['width']}x{info['height']}")
            print(f"总帧数: {info['total_frames']}")
            print(f"帧率: {info['fps']:.2f} FPS")
            print(f"时长: {info['duration']:.2f} 秒")
        
        # 2. 基本转换 - 提取所有帧
        print("\n=== 示例1: 提取所有帧 ===")
        converter.extract_frames(
            video_path=video_path,
            output_dir="example_output_all_frames",
            quality=5  # 中等压缩
        )
        
        # 3. 按帧率提取 - 每秒1帧
        print("\n=== 示例2: 每秒1帧 ===")
        converter.extract_frames(
            video_path=video_path,
            output_dir="example_output_1fps",
            frame_rate=1.0,
            quality=3  # 推荐质量
        )
        
        # 4. 提取时间片段 - 前30秒，每秒2帧
        print("\n=== 示例3: 前30秒，每秒2帧 ===")
        converter.extract_frames(
            video_path=video_path,
            output_dir="example_output_30s_2fps",
            frame_rate=2.0,
            start_time=0,
            end_time=30,
            quality=1  # 高质量
        )
        
        print("\n=== 所有示例完成 ===")
        print("生成的图片保存在以下目录:")
        print("- example_output_all_frames/")
        print("- example_output_1fps/")
        print("- example_output_30s_2fps/")
        
    except Exception as e:
        print(f"转换过程中发生错误: {e}")

if __name__ == "__main__":
    example_usage()
