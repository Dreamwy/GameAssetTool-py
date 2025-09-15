#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片大小修改工具
支持批量修改图片尺寸，保持宽高比或强制指定尺寸
"""

import os
import cv2
from pathlib import Path
from PIL import Image
import numpy as np


class ImageResizer:
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']

    def resize_image(self, input_path, output_path, width=None, height=None,
                    keep_aspect_ratio=True, quality=95, method='LANCZOS'):
        """
        调整单张图片大小

        Args:
            input_path (str): 输入图片路径
            output_path (str): 输出图片路径
            width (int): 目标宽度
            height (int): 目标高度
            keep_aspect_ratio (bool): 是否保持宽高比
            quality (int): JPEG质量 (1-100)
            method (str): 缩放算法 ('LANCZOS', 'BICUBIC', 'BILINEAR', 'NEAREST')

        Returns:
            bool: 是否成功
        """
        try:
            # 检查输入文件
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"输入文件不存在: {input_path}")

            file_ext = Path(input_path).suffix.lower()
            if file_ext not in self.supported_formats:
                raise ValueError(f"不支持的图片格式: {file_ext}")

            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # 使用PIL处理图片
            with Image.open(input_path) as img:
                original_width, original_height = img.size

                # 计算目标尺寸
                target_width, target_height = self._calculate_target_size(
                    original_width, original_height, width, height, keep_aspect_ratio
                )

                # 选择缩放算法
                resample_method = getattr(Image.Resampling, method, Image.Resampling.LANCZOS)

                # 调整大小
                resized_img = img.resize((target_width, target_height), resample_method)

                # 保存图片
                save_kwargs = {}
                output_ext = Path(output_path).suffix.lower()

                if output_ext in ['.jpg', '.jpeg']:
                    save_kwargs['quality'] = quality
                    save_kwargs['optimize'] = True
                    # 如果原图有透明通道，转换为RGB
                    if resized_img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', resized_img.size, (255, 255, 255))
                        if resized_img.mode == 'P':
                            resized_img = resized_img.convert('RGBA')
                        background.paste(resized_img, mask=resized_img.split()[-1] if resized_img.mode == 'RGBA' else None)
                        resized_img = background
                elif output_ext == '.png':
                    save_kwargs['optimize'] = True

                resized_img.save(output_path, **save_kwargs)

            return True

        except Exception as e:
            print(f"调整图片大小失败 {input_path}: {e}")
            return False

    def _calculate_target_size(self, orig_width, orig_height, target_width, target_height, keep_aspect_ratio):
        """计算目标尺寸"""
        if not target_width and not target_height:
            return orig_width, orig_height

        if keep_aspect_ratio:
            if target_width and target_height:
                # 同时指定了宽度和高度，按比例缩放到能完全容纳的尺寸
                width_ratio = target_width / orig_width
                height_ratio = target_height / orig_height
                ratio = min(width_ratio, height_ratio)
                return int(orig_width * ratio), int(orig_height * ratio)
            elif target_width:
                # 只指定宽度
                ratio = target_width / orig_width
                return target_width, int(orig_height * ratio)
            elif target_height:
                # 只指定高度
                ratio = target_height / orig_height
                return int(orig_width * ratio), target_height
        else:
            # 不保持宽高比，强制指定尺寸
            return target_width or orig_width, target_height or orig_height

    def batch_resize(self, input_dir, output_dir, width=None, height=None,
                    keep_aspect_ratio=True, quality=95, method='LANCZOS',
                    output_format=None):
        """
        批量调整图片大小

        Args:
            input_dir (str): 输入目录
            output_dir (str): 输出目录
            width (int): 目标宽度
            height (int): 目标高度
            keep_aspect_ratio (bool): 是否保持宽高比
            quality (int): JPEG质量
            method (str): 缩放算法
            output_format (str): 输出格式 ('jpg', 'png', None=保持原格式)

        Returns:
            int: 成功处理的图片数量
        """
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"输入目录不存在: {input_dir}")

        # 获取所有支持的图片文件
        image_files = []
        for ext in self.supported_formats:
            pattern = f"*{ext}"
            image_files.extend(Path(input_dir).glob(pattern))
            pattern = f"*{ext.upper()}"
            image_files.extend(Path(input_dir).glob(pattern))

        if not image_files:
            print("未找到支持的图片文件")
            return 0

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        success_count = 0
        total_count = len(image_files)

        print(f"开始批量调整 {total_count} 张图片大小...")

        for i, image_file in enumerate(image_files, 1):
            try:
                # 生成输出文件名
                if output_format:
                    output_filename = f"{image_file.stem}.{output_format}"
                else:
                    output_filename = image_file.name

                output_path = os.path.join(output_dir, output_filename)

                # 调整图片大小
                if self.resize_image(
                    str(image_file), output_path, width, height,
                    keep_aspect_ratio, quality, method
                ):
                    success_count += 1
                    print(f"[{i}/{total_count}] ✓ {image_file.name}")
                else:
                    print(f"[{i}/{total_count}] ✗ {image_file.name} - 处理失败")

            except Exception as e:
                print(f"[{i}/{total_count}] ✗ {image_file.name} - 错误: {e}")

        print(f"\n批量调整完成！成功处理 {success_count}/{total_count} 张图片")
        return success_count

    def get_image_info(self, image_path):
        """获取图片信息"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                format_name = img.format
                mode = img.mode

                # 获取文件大小
                file_size = os.path.getsize(image_path)
                size_mb = file_size / (1024 * 1024)

                return {
                    'filename': os.path.basename(image_path),
                    'width': width,
                    'height': height,
                    'format': format_name,
                    'mode': mode,
                    'size_mb': size_mb
                }
        except Exception as e:
            print(f"获取图片信息失败: {e}")
            return None

    def get_preset_sizes(self):
        """获取预设尺寸"""
        return {
            '小图标 (64x64)': (64, 64),
            '头像 (128x128)': (128, 128),
            '缩略图 (256x256)': (256, 256),
            '小图 (512x512)': (512, 512),
            '中图 (800x600)': (800, 600),
            '高清 (1920x1080)': (1920, 1080),
            '4K (3840x2160)': (3840, 2160),
            '宽屏 (1920x800)': (1920, 800),
            'Instagram正方形 (1080x1080)': (1080, 1080),
            'Instagram竖屏 (1080x1350)': (1080, 1350)
        }


def main():
    """命令行版本"""
    import argparse

    parser = argparse.ArgumentParser(description='图片大小调整工具')
    parser.add_argument('input', help='输入图片文件或目录路径')
    parser.add_argument('-o', '--output', help='输出文件或目录路径')
    parser.add_argument('-w', '--width', type=int, help='目标宽度')
    parser.add_argument('-h', '--height', type=int, help='目标高度')
    parser.add_argument('--no-aspect', action='store_true', help='不保持宽高比')
    parser.add_argument('--quality', type=int, default=95, help='JPEG质量 (1-100)')
    parser.add_argument('--method', choices=['LANCZOS', 'BICUBIC', 'BILINEAR', 'NEAREST'],
                       default='LANCZOS', help='缩放算法')
    parser.add_argument('--format', choices=['jpg', 'png'], help='输出格式')
    parser.add_argument('--batch', action='store_true', help='批量处理')

    args = parser.parse_args()

    resizer = ImageResizer()

    try:
        if args.batch or os.path.isdir(args.input):
            # 批量处理
            output_dir = args.output or f"{args.input}_resized"
            success_count = resizer.batch_resize(
                args.input, output_dir, args.width, args.height,
                not args.no_aspect, args.quality, args.method, args.format
            )
            print(f"成功处理 {success_count} 张图片")
        else:
            # 单张处理
            if not args.output:
                input_path = Path(args.input)
                args.output = str(input_path.parent / f"{input_path.stem}_resized{input_path.suffix}")

            success = resizer.resize_image(
                args.input, args.output, args.width, args.height,
                not args.no_aspect, args.quality, args.method
            )

            if success:
                print(f"图片已保存到: {args.output}")
            else:
                print("图片处理失败")

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()