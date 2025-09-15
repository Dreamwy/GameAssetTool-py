#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频转PNG工具
支持将视频文件转换为PNG图片序列
"""

import cv2
import os
import argparse
from pathlib import Path
import sys


class VideoToPNG:
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    
    def extract_frames(self, video_path, output_dir, frame_rate=None, start_time=0, end_time=None, quality=95):
        """
        从视频中提取帧并保存为PNG图片
        
        Args:
            video_path (str): 视频文件路径
            output_dir (str): 输出目录
            frame_rate (float): 提取帧率，None表示提取所有帧
            start_time (float): 开始时间（秒）
            end_time (float): 结束时间（秒），None表示到视频结尾
            quality (int): PNG压缩质量 (0-9, 0最高质量)
        """
        # 检查视频文件是否存在
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        # 检查文件格式
        file_ext = Path(video_path).suffix.lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"不支持的视频格式: {file_ext}")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 打开视频文件
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        # 获取视频信息
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        video_duration = total_frames / video_fps
        
        print(f"视频信息:")
        print(f"  文件: {video_path}")
        print(f"  总帧数: {total_frames}")
        print(f"  帧率: {video_fps:.2f} FPS")
        print(f"  时长: {video_duration:.2f} 秒")
        
        # 计算起始和结束帧
        start_frame = int(start_time * video_fps)
        if end_time:
            # 确保包含结束时间的那一帧
            end_frame = min(int(end_time * video_fps) + 1, total_frames)
        else:
            end_frame = total_frames
        
        # 设置起始位置
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        # 计算帧间隔
        if frame_rate:
            frame_interval = max(1, int(video_fps / frame_rate))
        else:
            frame_interval = 1
        
        frame_count = 0
        saved_count = 0
        
        print(f"\n开始提取帧...")
        print(f"  提取范围: 第{start_frame}帧 到 第{end_frame}帧")
        print(f"  帧间隔: {frame_interval}")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret or cap.get(cv2.CAP_PROP_POS_FRAMES) - 1 >= end_frame:
                    break
                
                current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
                
                # 按间隔保存帧
                if (current_frame - start_frame) % frame_interval == 0:
                    # 生成文件名
                    timestamp = current_frame / video_fps
                    filename = f"frame_{current_frame:06d}_{timestamp:.3f}s.png"
                    output_path = os.path.join(output_dir, filename)
                    
                    # 保存PNG文件，设置压缩级别
                    cv2.imwrite(output_path, frame, [cv2.IMWRITE_PNG_COMPRESSION, quality])
                    saved_count += 1
                    
                    # 显示进度
                    progress = (current_frame - start_frame) / (end_frame - start_frame) * 100
                    print(f"\r  进度: {progress:.1f}% - 已保存 {saved_count} 张图片", end="", flush=True)
                
                frame_count += 1
        
        except KeyboardInterrupt:
            print(f"\n\n用户中断操作，已保存 {saved_count} 张图片")
        except Exception as e:
            print(f"\n\n错误: {str(e)}")
        finally:
            cap.release()
        
        print(f"\n\n完成! 总共保存了 {saved_count} 张PNG图片到: {output_dir}")
        return saved_count
    
    def get_video_info(self, video_path):
        """获取视频基本信息"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None

        # 获取基本信息
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 多种方法计算时长，选择最准确的
        duration_methods = []

        # 方法1: 直接从属性获取（毫秒）
        cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1.0)  # 设置到视频结尾
        duration_ms_end = cap.get(cv2.CAP_PROP_POS_MSEC)
        if duration_ms_end > 0:
            duration_methods.append(duration_ms_end / 1000.0)

        # 方法2: 使用帧数/帧率
        if fps > 0 and total_frames > 0:
            duration_frames = total_frames / fps
            duration_methods.append(duration_frames)

        # 方法3: 尝试获取视频总时长（某些OpenCV版本支持）
        try:
            # 跳转到最后一帧来获取准确时长
            cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
            ret, _ = cap.read()
            if ret:
                last_frame_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                if last_frame_time > 0:
                    duration_methods.append(last_frame_time)
        except Exception:
            pass

        # 重置视频到开始
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # 选择最大的时长值（通常更准确）
        duration = max(duration_methods) if duration_methods else 0

        # 如果所有方法都失败，尝试手动计算
        if duration <= 0 and fps > 0:
            # 通过实际读取帧来估算
            frame_count = 0
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            # 采样计算，避免读取全部帧
            sample_frames = min(300, total_frames)  # 最多采样300帧
            step = max(1, total_frames // sample_frames)

            last_timestamp = 0
            for i in range(0, total_frames, step):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, _ = cap.read()
                if ret:
                    timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                    if timestamp > last_timestamp:
                        last_timestamp = timestamp
                        frame_count += 1
                else:
                    break

                # 限制采样数量
                if frame_count >= sample_frames:
                    break

            if last_timestamp > 0:
                duration = last_timestamp

        # 获取文件大小
        file_size = os.path.getsize(video_path)
        size_mb = file_size / (1024 * 1024)

        info = {
            'filename': os.path.basename(video_path),
            'total_frames': total_frames,
            'fps': fps,
            'width': width,
            'height': height,
            'duration': duration,
            'size_mb': size_mb,
            'duration_methods': duration_methods,  # 调试信息
        }

        cap.release()
        return info

    def convert(self, video_path, output_dir, frame_rate=None, start_time=0, end_time=None, quality=3):
        """
        转换视频为PNG图片序列（GUI专用接口）

        Args:
            video_path (str): 视频文件路径
            output_dir (str): 输出目录
            frame_rate (float): 提取帧率
            start_time (int): 开始时间（秒）
            end_time (int): 结束时间（秒），0或None表示到结尾
            quality (int): PNG压缩级别 (0-9)

        Returns:
            int: 保存的图片数量
        """
        # 转换参数
        end_time = None if end_time == 0 else end_time

        # 调用核心转换方法
        return self.extract_frames(
            video_path=video_path,
            output_dir=output_dir,
            frame_rate=frame_rate,
            start_time=start_time,
            end_time=end_time,
            quality=quality
        )


def main():
    parser = argparse.ArgumentParser(description='视频转PNG工具')
    parser.add_argument('input', help='输入视频文件路径')
    parser.add_argument('-o', '--output', default='output_frames', help='输出目录 (默认: output_frames)')
    parser.add_argument('-r', '--rate', type=float, help='提取帧率 (例如: 1.0 表示每秒1帧)')
    parser.add_argument('-s', '--start', type=float, default=0, help='开始时间(秒) (默认: 0)')
    parser.add_argument('-e', '--end', type=float, help='结束时间(秒) (默认: 视频结尾)')
    parser.add_argument('-q', '--quality', type=int, default=3, choices=range(10), 
                       help='PNG压缩级别 0-9 (0=最高质量, 默认: 3)')
    parser.add_argument('--info', action='store_true', help='只显示视频信息，不进行转换')
    
    args = parser.parse_args()
    
    converter = VideoToPNG()
    
    try:
        # 如果只是查看信息
        if args.info:
            info = converter.get_video_info(args.input)
            if info:
                print(f"视频信息:")
                print(f"  分辨率: {info['width']}x{info['height']}")
                print(f"  总帧数: {info['total_frames']}")
                print(f"  帧率: {info['fps']:.2f} FPS")
                print(f"  时长: {info['duration']:.2f} 秒")
            else:
                print("无法读取视频信息")
            return
        
        # 执行转换
        converter.extract_frames(
            video_path=args.input,
            output_dir=args.output,
            frame_rate=args.rate,
            start_time=args.start,
            end_time=args.end,
            quality=args.quality
        )
        
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
