#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试视频时间范围提取的问题
"""

import cv2
import numpy as np
import os
from video_to_png import VideoToPNG

def create_test_video():
    """创建一个10秒的测试视频，带有时间戳"""
    # 创建视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 2  # 使用较低帧率便于观察
    duration_seconds = 10
    total_frames = fps * duration_seconds

    out = cv2.VideoWriter('test_time_video.mp4', fourcc, fps, (640, 480))

    print(f"创建测试视频: {duration_seconds}秒, {fps} FPS, {total_frames} 帧")

    for frame_num in range(total_frames):
        # 创建带时间戳的帧
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # 计算当前时间
        current_time = frame_num / fps

        # 添加大号时间戳
        cv2.putText(frame, f'{current_time:.1f}s',
                   (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 4)
        cv2.putText(frame, f'Frame {frame_num}',
                   (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)

        out.write(frame)

    out.release()
    print("✓ 测试视频创建完成")

def test_time_range_extraction():
    """测试时间范围提取"""
    if not os.path.exists('test_time_video.mp4'):
        create_test_video()

    converter = VideoToPNG()

    print("\n=== 测试视频信息 ===")
    info = converter.get_video_info('test_time_video.mp4')
    print(f"总时长: {info['duration']:.2f}秒")
    print(f"总帧数: {info['total_frames']}")
    print(f"帧率: {info['fps']:.2f} FPS")

    print("\n=== 测试时间范围提取 ===")
    print("提取 0-5 秒的帧...")

    # 清理之前的输出
    output_dir = "test_time_output"
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)

    # 提取0-5秒的帧
    result = converter.extract_frames(
        'test_time_video.mp4',
        output_dir,
        frame_rate=None,  # 提取所有帧
        start_time=0,
        end_time=5,
        quality=3
    )

    print(f"\n提取结果: {result} 张图片")

    # 检查输出的文件
    if os.path.exists(output_dir):
        files = sorted([f for f in os.listdir(output_dir) if f.endswith('.png')])
        print(f"\n输出文件数量: {len(files)}")

        if files:
            print("前几个文件:")
            for f in files[:5]:
                print(f"  {f}")

            if len(files) > 5:
                print("...")
                print("最后几个文件:")
                for f in files[-3:]:
                    print(f"  {f}")

            # 分析时间戳
            timestamps = []
            for f in files:
                if '_' in f and 's.png' in f:
                    time_part = f.split('_')[-1].replace('s.png', '')
                    try:
                        timestamp = float(time_part)
                        timestamps.append(timestamp)
                    except ValueError:
                        pass

            if timestamps:
                print(f"\n时间戳范围: {min(timestamps):.3f}s - {max(timestamps):.3f}s")
                print(f"应该的范围: 0.000s - 5.000s")

                if max(timestamps) < 4.5:
                    print("⚠ 警告: 提取结束时间过早！")
                elif max(timestamps) > 5.5:
                    print("⚠ 警告: 提取结束时间过晚！")
                else:
                    print("✓ 时间范围正确")

    # 清理
    if os.path.exists('test_time_video.mp4'):
        os.remove('test_time_video.mp4')
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)

    print("\n✓ 测试完成，文件已清理")

if __name__ == "__main__":
    test_time_range_extraction()