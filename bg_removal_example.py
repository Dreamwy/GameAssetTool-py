#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动去背景工具使用示例
"""

from remove_background import BackgroundRemover
import os

def example_usage():
    """演示如何使用BackgroundRemover类"""
    
    # 创建去背景器实例
    remover = BackgroundRemover()
    
    # 示例图片文件路径（请替换为实际的图片文件）
    sample_image = "sample_image.jpg"
    
    # 检查示例图片是否存在
    if not os.path.exists(sample_image):
        print(f"示例图片文件 '{sample_image}' 不存在")
        print("请将您的图片文件重命名为 'sample_image.jpg' 或修改此脚本中的路径")
        print("支持的格式：JPG, JPEG, PNG, BMP, TIFF, WebP")
        return
    
    try:
        print("=== 自动去背景工具使用示例 ===\n")
        
        # 1. 使用AI方法（推荐）
        print("1. 使用rembg AI算法去背景（推荐方法）")
        if remover.process_image(
            image_path=sample_image,
            output_path="example_output_rembg.png",
            method='rembg'
        ):
            print("✓ AI去背景完成，输出文件: example_output_rembg.png")
        else:
            print("✗ AI去背景失败（可能是rembg库未正确安装）")
        
        print()
        
        # 2. 使用GrabCut算法
        print("2. 使用GrabCut算法去背景")
        if remover.process_image(
            image_path=sample_image,
            output_path="example_output_grabcut.png",
            method='grabcut',
            iterations=8
        ):
            print("✓ GrabCut去背景完成，输出文件: example_output_grabcut.png")
        else:
            print("✗ GrabCut去背景失败")
        
        print()
        
        # 3. 使用K-means聚类
        print("3. 使用K-means聚类去背景")
        if remover.process_image(
            image_path=sample_image,
            output_path="example_output_kmeans.png",
            method='kmeans',
            k=4
        ):
            print("✓ K-means去背景完成，输出文件: example_output_kmeans.png")
        else:
            print("✗ K-means去背景失败")
        
        print()
        
        # 4. 使用阈值方法
        print("4. 使用阈值方法去背景（适用于纯色背景）")
        if remover.process_image(
            image_path=sample_image,
            output_path="example_output_threshold.png",
            method='threshold'
        ):
            print("✓ 阈值去背景完成，输出文件: example_output_threshold.png")
        else:
            print("✗ 阈值去背景失败")
        
        print()
        
        # 5. 批量处理示例（如果有图片目录）
        sample_dir = "sample_images"
        if os.path.exists(sample_dir) and os.path.isdir(sample_dir):
            print(f"5. 批量处理目录 '{sample_dir}' 中的图片")
            success_count = remover.batch_process(
                input_dir=sample_dir,
                output_dir="example_batch_output",
                method='rembg'
            )
            print(f"✓ 批量处理完成，成功处理 {success_count} 张图片")
        else:
            print(f"5. 跳过批量处理（目录 '{sample_dir}' 不存在）")
            print(f"   如需测试批量处理，请创建 '{sample_dir}' 目录并放入图片文件")
        
        print("\n=== 所有示例完成 ===")
        print("生成的去背景图片:")
        output_files = [
            "example_output_rembg.png",
            "example_output_grabcut.png", 
            "example_output_kmeans.png",
            "example_output_threshold.png"
        ]
        
        for file in output_files:
            if os.path.exists(file):
                print(f"- ✓ {file}")
            else:
                print(f"- ✗ {file} (处理失败)")
        
        print("\n推荐使用顺序:")
        print("1. rembg (AI算法) - 效果最佳，适用于大多数场景")
        print("2. grabcut - 速度快，适用于主体明确的图片")
        print("3. threshold - 最快，适用于纯色背景")
        
    except Exception as e:
        print(f"示例运行过程中发生错误: {e}")

def create_sample_structure():
    """创建示例目录结构"""
    print("创建示例目录结构...")
    
    # 创建示例图片目录
    sample_dir = "sample_images"
    if not os.path.exists(sample_dir):
        os.makedirs(sample_dir)
        print(f"✓ 创建目录: {sample_dir}")
        print(f"  请将测试图片放入此目录进行批量处理测试")
    else:
        print(f"✓ 目录已存在: {sample_dir}")
    
    # 创建输出目录
    output_dirs = ["example_batch_output"]
    for dir_name in output_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✓ 创建输出目录: {dir_name}")

if __name__ == "__main__":
    print("自动去背景工具使用示例\n")
    
    # 创建示例目录结构
    create_sample_structure()
    print()
    
    # 运行示例
    example_usage()
