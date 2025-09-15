#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动去背景转PNG工具
支持多种背景去除算法，将图片背景移除并保存为透明PNG
"""

import cv2
import numpy as np
from PIL import Image, ImageFilter
import os
import argparse
from pathlib import Path
import sys
# 注意：如果需要使用更高级的分割算法，可以添加以下导入：
# from skimage import segmentation, color
# import matplotlib.pyplot as plt

try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("警告: rembg库未安装，AI背景去除功能将不可用")


class BackgroundRemover:
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        self.methods = ['rembg', 'grabcut', 'watershed', 'kmeans', 'threshold']
        
        # 初始化rembg会话（如果可用）
        if REMBG_AVAILABLE:
            try:
                self.rembg_session = new_session('u2net')  # 默认使用u2net模型
            except Exception as e:
                print(f"rembg初始化失败: {e}")
                self.rembg_session = None
        else:
            self.rembg_session = None
    
    def remove_background_rembg(self, image_path, output_path):
        """
        使用rembg AI模型去除背景（推荐方法）
        """
        if not REMBG_AVAILABLE or self.rembg_session is None:
            raise ValueError("rembg库不可用，请安装: pip install rembg")
        
        try:
            # 读取图片
            with open(image_path, 'rb') as input_file:
                input_data = input_file.read()
            
            # 使用rembg去除背景
            output_data = remove(input_data, session=self.rembg_session)
            
            # 保存结果
            with open(output_path, 'wb') as output_file:
                output_file.write(output_data)
            
            return True
        except Exception as e:
            print(f"rembg处理失败: {e}")
            return False
    
    def remove_background_grabcut(self, image_path, output_path, iterations=5):
        """
        使用OpenCV GrabCut算法去除背景
        """
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法读取图片: {image_path}")
        
        height, width = img.shape[:2]
        
        # 创建掩码
        mask = np.zeros((height, width), np.uint8)
        
        # 定义前景和背景模型
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        # 定义矩形区域（假设主体在图片中央）
        margin = min(width, height) // 10
        rect = (margin, margin, width - 2*margin, height - 2*margin)
        
        # 应用GrabCut算法
        cv2.grabCut(img, mask, rect, bgd_model, fgd_model, iterations, cv2.GC_INIT_WITH_RECT)
        
        # 创建最终掩码
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        
        # 应用掩码
        result = img * mask2[:, :, np.newaxis]
        
        # 创建透明背景
        result_rgba = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
        result_rgba[:, :, 3] = mask2 * 255
        
        # 保存结果
        cv2.imwrite(output_path, result_rgba)
        return True
    
    def remove_background_watershed(self, image_path, output_path):
        """
        使用分水岭算法去除背景
        """
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法读取图片: {image_path}")
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 应用阈值
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 形态学操作
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        
        # 确定背景区域
        sure_bg = cv2.dilate(opening, kernel, iterations=3)
        
        # 确定前景区域
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
        
        # 不确定区域
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)
        
        # 标记连通组件
        _, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        
        # 应用分水岭算法
        markers = cv2.watershed(img, markers)
        
        # 创建掩码
        mask = np.zeros(gray.shape, dtype=np.uint8)
        mask[markers > 1] = 255
        
        # 应用掩码
        result = img.copy()
        result_rgba = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
        result_rgba[:, :, 3] = mask
        
        # 保存结果
        cv2.imwrite(output_path, result_rgba)
        return True
    
    def remove_background_kmeans(self, image_path, output_path, k=3):
        """
        使用K-means聚类去除背景
        """
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法读取图片: {image_path}")
        
        # 重塑数据
        data = img.reshape((-1, 3))
        data = np.float32(data)
        
        # 定义停止条件
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        
        # 应用K-means
        _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # 转换回uint8并重塑
        centers = np.uint8(centers)
        segmented_data = centers[labels.flatten()]
        segmented_image = segmented_data.reshape(img.shape)
        
        # 假设最大的聚类是背景，创建掩码
        unique, counts = np.unique(labels, return_counts=True)
        background_label = unique[np.argmax(counts)]
        
        mask = np.where(labels.flatten() == background_label, 0, 255).astype(np.uint8)
        mask = mask.reshape(img.shape[:2])
        
        # 应用掩码
        result_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        result_rgba[:, :, 3] = mask
        
        # 保存结果
        cv2.imwrite(output_path, result_rgba)
        return True
    
    def remove_background_threshold(self, image_path, output_path, threshold_value=None):
        """
        使用简单阈值方法去除背景（适用于纯色背景）
        """
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法读取图片: {image_path}")
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 自动确定阈值或使用指定值
        if threshold_value is None:
            threshold_value, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            threshold_value = int(threshold_value)
        
        # 应用阈值
        _, mask = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
        
        # 假设背景是较亮的区域，反转掩码
        mask = cv2.bitwise_not(mask)
        
        # 形态学操作清理掩码
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # 应用掩码
        result_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        result_rgba[:, :, 3] = mask
        
        # 保存结果
        cv2.imwrite(output_path, result_rgba)
        return True
    
    def process_image(self, image_path, output_path, method='rembg', **kwargs):
        """
        处理单张图片
        
        Args:
            image_path (str): 输入图片路径
            output_path (str): 输出图片路径
            method (str): 去背景方法
            **kwargs: 方法特定参数
        """
        # 检查输入文件
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        file_ext = Path(image_path).suffix.lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"不支持的图片格式: {file_ext}")
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:  # 只有当输出路径包含目录时才创建目录
            os.makedirs(output_dir, exist_ok=True)
        
        # 根据方法选择处理函数
        if method == 'rembg':
            return self.remove_background_rembg(image_path, output_path)
        elif method == 'grabcut':
            return self.remove_background_grabcut(image_path, output_path, 
                                                kwargs.get('iterations', 5))
        elif method == 'watershed':
            return self.remove_background_watershed(image_path, output_path)
        elif method == 'kmeans':
            return self.remove_background_kmeans(image_path, output_path, 
                                               kwargs.get('k', 3))
        elif method == 'threshold':
            return self.remove_background_threshold(image_path, output_path,
                                                  kwargs.get('threshold_value', None))
        else:
            raise ValueError(f"不支持的方法: {method}")
    
    def batch_process(self, input_dir, output_dir, method='rembg', **kwargs):
        """
        批量处理图片
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
        
        print(f"开始批量处理 {total_count} 张图片...")
        
        for i, image_file in enumerate(image_files, 1):
            try:
                # 生成输出文件名
                output_filename = f"{image_file.stem}_no_bg.png"
                output_path = os.path.join(output_dir, output_filename)
                
                # 处理图片
                if self.process_image(str(image_file), output_path, method, **kwargs):
                    success_count += 1
                    print(f"[{i}/{total_count}] ✓ {image_file.name}")
                else:
                    print(f"[{i}/{total_count}] ✗ {image_file.name} - 处理失败")
                
            except Exception as e:
                print(f"[{i}/{total_count}] ✗ {image_file.name} - 错误: {e}")
        
        print(f"\n批量处理完成！成功处理 {success_count}/{total_count} 张图片")
        return success_count

    def process_batch(self, input_path, method='rembg', **kwargs):
        """
        批量处理接口（GUI专用）

        Args:
            input_path (str): 输入目录路径
            method (str): 处理方法
            **kwargs: 其他参数

        Returns:
            int: 成功处理的图片数量
        """
        # 生成输出目录名
        input_dir = Path(input_path)
        output_dir = input_dir.parent / f"{input_dir.name}_no_bg"

        return self.batch_process(input_path, str(output_dir), method, **kwargs)


def main():
    parser = argparse.ArgumentParser(description='自动去背景转PNG工具')
    parser.add_argument('input', help='输入图片文件或目录路径')
    parser.add_argument('-o', '--output', help='输出文件或目录路径')
    parser.add_argument('-m', '--method', choices=['rembg', 'grabcut', 'watershed', 'kmeans', 'threshold'],
                       default='rembg', help='去背景方法 (默认: rembg)')
    parser.add_argument('--batch', action='store_true', help='批量处理目录中的所有图片')
    
    # 方法特定参数
    parser.add_argument('--iterations', type=int, default=5, help='GrabCut迭代次数')
    parser.add_argument('--k', type=int, default=3, help='K-means聚类数量')
    parser.add_argument('--threshold', type=int, help='阈值方法的阈值')
    
    args = parser.parse_args()
    
    remover = BackgroundRemover()
    
    try:
        if args.batch:
            # 批量处理
            if not args.output:
                args.output = "output_no_bg"
            
            success_count = remover.batch_process(
                input_dir=args.input,
                output_dir=args.output,
                method=args.method,
                iterations=args.iterations,
                k=args.k,
                threshold_value=args.threshold
            )
            
            if success_count > 0:
                print(f"\n处理完成的图片保存在: {args.output}")
        else:
            # 单张图片处理
            if not args.output:
                input_path = Path(args.input)
                args.output = f"{input_path.stem}_no_bg.png"
            
            print(f"正在处理图片: {args.input}")
            print(f"使用方法: {args.method}")
            
            success = remover.process_image(
                image_path=args.input,
                output_path=args.output,
                method=args.method,
                iterations=args.iterations,
                k=args.k,
                threshold_value=args.threshold
            )
            
            if success:
                print(f"✓ 处理完成，结果保存为: {args.output}")
            else:
                print("✗ 处理失败")
                sys.exit(1)
                
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
