#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多媒体处理工具集 - PyQt5整合GUI
包含视频转PNG和自动去背景两大功能
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QTabWidget, QLabel, QLineEdit, QPushButton,
                            QFileDialog, QMessageBox, QProgressBar, QTextEdit,
                            QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
                            QGroupBox, QGridLayout, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap
from pathlib import Path
import threading
import time

# 导入工具类
from video_to_png import VideoToPNG
from remove_background import BackgroundRemover
from image_resizer import ImageResizer


class WorkerThread(QThread):
    """工作线程类"""
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(True, "操作完成！")
        except Exception as e:
            self.finished.emit(False, f"操作失败: {str(e)}")


class IntegratedGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("多媒体处理工具集")
        self.setGeometry(100, 100, 900, 700)

        # 初始化工具类
        self.video_converter = VideoToPNG()
        self.bg_remover = BackgroundRemover()
        self.image_resizer = ImageResizer()

        # 设置UI
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 标题
        title_label = QLabel("多媒体处理工具集")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)

        # 创建选项卡
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # 视频转PNG选项卡
        video_tab = self.create_video_tab()
        tab_widget.addTab(video_tab, "🎬 视频转PNG")

        # 去背景选项卡
        bg_tab = self.create_background_tab()
        tab_widget.addTab(bg_tab, "🖼️ 去背景")

        # 图片大小调整选项卡
        resize_tab = self.create_resize_tab()
        tab_widget.addTab(resize_tab, "📏 调整大小")

    def create_video_tab(self):
        """创建视频转PNG选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 文件选择组
        file_group = QGroupBox("文件选择")
        file_layout = QGridLayout(file_group)

        # 输入视频文件
        file_layout.addWidget(QLabel("输入视频:"), 0, 0)
        self.video_input_line = QLineEdit()
        file_layout.addWidget(self.video_input_line, 0, 1)
        video_browse_btn = QPushButton("浏览")
        video_browse_btn.clicked.connect(self.browse_video_file)
        file_layout.addWidget(video_browse_btn, 0, 2)

        # 输出目录
        file_layout.addWidget(QLabel("输出目录:"), 1, 0)
        self.video_output_line = QLineEdit("output_frames")
        file_layout.addWidget(self.video_output_line, 1, 1)
        output_browse_btn = QPushButton("浏览")
        output_browse_btn.clicked.connect(self.browse_output_dir)
        file_layout.addWidget(output_browse_btn, 1, 2)

        layout.addWidget(file_group)

        # 参数设置组
        param_group = QGroupBox("参数设置")
        param_layout = QGridLayout(param_group)

        # 帧率
        param_layout.addWidget(QLabel("帧率 (FPS):"), 0, 0)
        self.fps_spin = QDoubleSpinBox()
        self.fps_spin.setRange(0.1, 60.0)
        self.fps_spin.setValue(1.0)
        self.fps_spin.setSingleStep(0.1)
        param_layout.addWidget(self.fps_spin, 0, 1)

        # 开始时间
        param_layout.addWidget(QLabel("开始时间 (秒):"), 0, 2)
        self.start_spin = QSpinBox()
        self.start_spin.setRange(0, 99999)
        self.start_spin.setValue(0)
        param_layout.addWidget(self.start_spin, 0, 3)

        # 结束时间
        param_layout.addWidget(QLabel("结束时间 (秒):"), 1, 0)
        self.end_spin = QSpinBox()
        self.end_spin.setRange(0, 99999)
        self.end_spin.setValue(0)
        param_layout.addWidget(self.end_spin, 1, 1)

        # 质量
        param_layout.addWidget(QLabel("质量 (0-9):"), 1, 2)
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(0, 9)
        self.quality_spin.setValue(3)
        param_layout.addWidget(self.quality_spin, 1, 3)

        layout.addWidget(param_group)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.video_info_btn = QPushButton("查看视频信息")
        self.video_info_btn.clicked.connect(self.show_video_info)
        btn_layout.addWidget(self.video_info_btn)

        self.video_convert_btn = QPushButton("开始转换")
        self.video_convert_btn.clicked.connect(self.convert_video)
        btn_layout.addWidget(self.video_convert_btn)

        layout.addLayout(btn_layout)

        # 进度条
        self.video_progress = QProgressBar()
        layout.addWidget(self.video_progress)

        # 状态显示
        self.video_status = QTextEdit()
        self.video_status.setMaximumHeight(150)
        layout.addWidget(self.video_status)

        return widget

    def create_background_tab(self):
        """创建去背景选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 文件选择组
        file_group = QGroupBox("文件/目录选择")
        file_layout = QGridLayout(file_group)

        # 输入选择
        file_layout.addWidget(QLabel("输入:"), 0, 0)
        self.bg_input_line = QLineEdit()
        self.bg_input_line.setPlaceholderText("选择单个图片文件或包含图片的目录")
        file_layout.addWidget(self.bg_input_line, 0, 1)

        # 输入选择按钮
        bg_file_btn = QPushButton("选择文件")
        bg_file_btn.clicked.connect(self.browse_image_file)
        file_layout.addWidget(bg_file_btn, 0, 2)

        bg_dir_btn = QPushButton("选择目录")
        bg_dir_btn.clicked.connect(self.browse_image_directory)
        file_layout.addWidget(bg_dir_btn, 0, 3)

        # 输出选择
        file_layout.addWidget(QLabel("输出:"), 1, 0)
        self.bg_output_line = QLineEdit()
        self.bg_output_line.setPlaceholderText("单个文件输出路径或批量输出目录")
        file_layout.addWidget(self.bg_output_line, 1, 1)

        # 输出选择按钮
        bg_output_file_btn = QPushButton("输出文件")
        bg_output_file_btn.clicked.connect(self.browse_output_file)
        file_layout.addWidget(bg_output_file_btn, 1, 2)

        bg_output_dir_btn = QPushButton("输出目录")
        bg_output_dir_btn.clicked.connect(self.browse_output_directory)
        file_layout.addWidget(bg_output_dir_btn, 1, 3)

        # 处理模式指示
        self.bg_mode_label = QLabel("💡 选择文件进行单张处理，选择目录进行批量处理")
        self.bg_mode_label.setStyleSheet("color: #666; font-size: 11px; margin-top: 5px;")
        file_layout.addWidget(self.bg_mode_label, 2, 0, 1, 4)

        layout.addWidget(file_group)

        # 算法选择组
        method_group = QGroupBox("算法选择")
        method_layout = QGridLayout(method_group)

        method_layout.addWidget(QLabel("去背景算法:"), 0, 0)
        self.method_combo = QComboBox()

        # 添加带详细说明的算法选项
        algorithms = [
            ("rembg", "AI智能识别，效果最佳 - 适用于通用场景、复杂背景"),
            ("grabcut", "交互式分割，可调参数 - 适用于主体明确的图片"),
            ("watershed", "基于梯度的分割 - 适用于边界清晰的图片"),
            ("kmeans", "颜色聚类分割 - 适用于颜色差异明显的图片"),
            ("threshold", "简单阈值分割，速度最快 - 适用于纯色背景")
        ]

        for algo_name, description in algorithms:
            self.method_combo.addItem(f"{algo_name} - {description}", algo_name)

        method_layout.addWidget(self.method_combo, 0, 1, 1, 2)

        # 算法说明标签
        info_label = QLabel("💡 选择适合您图片特点的算法以获得最佳效果")
        info_label.setStyleSheet("color: #666; font-size: 11px; margin-top: 5px;")
        method_layout.addWidget(info_label, 1, 0, 1, 3)

        # 处理模式显示
        self.processing_mode_label = QLabel("处理模式: 未选择")
        self.processing_mode_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        method_layout.addWidget(self.processing_mode_label, 2, 0, 1, 3)

        layout.addWidget(method_group)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.bg_process_btn = QPushButton("开始处理")
        self.bg_process_btn.clicked.connect(self.process_background)
        btn_layout.addWidget(self.bg_process_btn)

        self.bg_open_folder_btn = QPushButton("打开输出文件夹")
        self.bg_open_folder_btn.clicked.connect(self.open_bg_output_folder)
        self.bg_open_folder_btn.setEnabled(False)
        btn_layout.addWidget(self.bg_open_folder_btn)

        layout.addLayout(btn_layout)

        # 进度条
        self.bg_progress = QProgressBar()
        layout.addWidget(self.bg_progress)

        # 状态显示
        self.bg_status = QTextEdit()
        self.bg_status.setMaximumHeight(150)
        layout.addWidget(self.bg_status)

        return widget

    def create_resize_tab(self):
        """创建图片大小调整选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 文件/目录选择组
        file_group = QGroupBox("文件/目录选择")
        file_layout = QGridLayout(file_group)

        # 输入选择
        file_layout.addWidget(QLabel("输入:"), 0, 0)
        self.resize_input_line = QLineEdit()
        self.resize_input_line.setPlaceholderText("选择单个图片文件或包含图片的目录")
        file_layout.addWidget(self.resize_input_line, 0, 1)

        # 输入选择按钮
        resize_file_btn = QPushButton("选择文件")
        resize_file_btn.clicked.connect(self.browse_resize_file)
        file_layout.addWidget(resize_file_btn, 0, 2)

        resize_dir_btn = QPushButton("选择目录")
        resize_dir_btn.clicked.connect(self.browse_resize_directory)
        file_layout.addWidget(resize_dir_btn, 0, 3)

        # 输出选择
        file_layout.addWidget(QLabel("输出:"), 1, 0)
        self.resize_output_line = QLineEdit()
        self.resize_output_line.setPlaceholderText("调整大小后的输出路径")
        file_layout.addWidget(self.resize_output_line, 1, 1)

        # 输出选择按钮
        resize_output_file_btn = QPushButton("输出文件")
        resize_output_file_btn.clicked.connect(self.browse_resize_output_file)
        file_layout.addWidget(resize_output_file_btn, 1, 2)

        resize_output_dir_btn = QPushButton("输出目录")
        resize_output_dir_btn.clicked.connect(self.browse_resize_output_directory)
        file_layout.addWidget(resize_output_dir_btn, 1, 3)

        # 处理模式指示
        self.resize_mode_label = QLabel("💡 选择文件进行单张处理，选择目录进行批量处理")
        self.resize_mode_label.setStyleSheet("color: #666; font-size: 11px; margin-top: 5px;")
        file_layout.addWidget(self.resize_mode_label, 2, 0, 1, 4)

        layout.addWidget(file_group)

        # 尺寸设置组
        size_group = QGroupBox("尺寸设置")
        size_layout = QGridLayout(size_group)

        # 预设尺寸
        size_layout.addWidget(QLabel("预设尺寸:"), 0, 0)
        self.size_preset_combo = QComboBox()
        self.size_preset_combo.addItem("自定义尺寸", None)

        # 添加预设尺寸
        presets = self.image_resizer.get_preset_sizes()
        for name, (width, height) in presets.items():
            self.size_preset_combo.addItem(name, (width, height))

        self.size_preset_combo.currentTextChanged.connect(self.on_preset_changed)
        size_layout.addWidget(self.size_preset_combo, 0, 1, 1, 3)

        # 自定义宽度
        size_layout.addWidget(QLabel("宽度:"), 1, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(800)
        self.width_spin.setSuffix(" px")
        size_layout.addWidget(self.width_spin, 1, 1)

        # 自定义高度
        size_layout.addWidget(QLabel("高度:"), 1, 2)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(600)
        self.height_spin.setSuffix(" px")
        size_layout.addWidget(self.height_spin, 1, 3)

        # 保持宽高比
        self.keep_aspect_check = QCheckBox("保持宽高比")
        self.keep_aspect_check.setChecked(True)
        size_layout.addWidget(self.keep_aspect_check, 2, 0, 1, 2)

        # 缩放算法
        size_layout.addWidget(QLabel("缩放算法:"), 2, 2)
        self.resize_method_combo = QComboBox()
        methods = [
            ("LANCZOS", "高质量缩放（推荐）"),
            ("BICUBIC", "双三次插值"),
            ("BILINEAR", "双线性插值"),
            ("NEAREST", "最近邻插值（快速）")
        ]
        for method, desc in methods:
            self.resize_method_combo.addItem(f"{method} - {desc}", method)
        size_layout.addWidget(self.resize_method_combo, 2, 3)

        layout.addWidget(size_group)

        # 输出设置组
        output_group = QGroupBox("输出设置")
        output_layout = QGridLayout(output_group)

        # JPEG质量
        output_layout.addWidget(QLabel("JPEG质量:"), 0, 0)
        self.resize_quality_spin = QSpinBox()
        self.resize_quality_spin.setRange(1, 100)
        self.resize_quality_spin.setValue(95)
        self.resize_quality_spin.setSuffix("%")
        output_layout.addWidget(self.resize_quality_spin, 0, 1)

        # 输出格式
        output_layout.addWidget(QLabel("输出格式:"), 0, 2)
        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(["保持原格式", "JPG", "PNG"])
        output_layout.addWidget(self.output_format_combo, 0, 3)

        layout.addWidget(output_group)

        # 操作按钮
        btn_layout = QHBoxLayout()

        self.resize_info_btn = QPushButton("查看图片信息")
        self.resize_info_btn.clicked.connect(self.show_resize_info)
        btn_layout.addWidget(self.resize_info_btn)

        self.resize_process_btn = QPushButton("开始处理")
        self.resize_process_btn.clicked.connect(self.process_resize)
        btn_layout.addWidget(self.resize_process_btn)

        self.resize_open_folder_btn = QPushButton("打开输出文件夹")
        self.resize_open_folder_btn.clicked.connect(self.open_resize_output_folder)
        self.resize_open_folder_btn.setEnabled(False)
        btn_layout.addWidget(self.resize_open_folder_btn)

        layout.addLayout(btn_layout)

        # 进度条
        self.resize_progress = QProgressBar()
        layout.addWidget(self.resize_progress)

        # 状态显示
        self.resize_status = QTextEdit()
        self.resize_status.setMaximumHeight(150)
        layout.addWidget(self.resize_status)

        return widget

    def browse_video_file(self):
        """浏览视频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "",
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm);;所有文件 (*)"
        )
        if file_path:
            self.video_input_line.setText(file_path)

    def browse_output_dir(self):
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.video_output_line.setText(dir_path)

    def browse_image_file(self):
        """浏览单个图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片文件", "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff *.webp);;所有文件 (*)"
        )
        if file_path:
            self.bg_input_line.setText(file_path)
            # 自动设置输出文件名
            input_path = Path(file_path)
            output_path = input_path.parent / f"{input_path.stem}_no_bg.png"
            self.bg_output_line.setText(str(output_path))
            # 更新处理模式
            self.processing_mode_label.setText("处理模式: 单文件处理")
            self.bg_mode_label.setText("💡 已选择单个文件，将进行单张图片处理")

    def browse_image_directory(self):
        """浏览包含图片的目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择包含图片的目录")
        if dir_path:
            self.bg_input_line.setText(dir_path)
            # 自动设置输出目录
            input_path = Path(dir_path)
            output_path = input_path.parent / f"{input_path.name}_no_bg"
            self.bg_output_line.setText(str(output_path))
            # 更新处理模式
            self.processing_mode_label.setText("处理模式: 批量处理")
            # 统计图片数量
            image_count = self.count_images_in_directory(dir_path)
            self.bg_mode_label.setText(f"💡 已选择目录，将批量处理 {image_count} 张图片")

    def browse_output_file(self):
        """浏览单个输出文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存输出文件", "",
            "PNG文件 (*.png);;所有文件 (*)"
        )
        if file_path:
            self.bg_output_line.setText(file_path)

    def browse_output_directory(self):
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.bg_output_line.setText(dir_path)

    def count_images_in_directory(self, dir_path):
        """统计目录中的图片文件数量"""
        try:
            from pathlib import Path
            supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
            count = 0
            dir_obj = Path(dir_path)
            for ext in supported_formats:
                count += len(list(dir_obj.glob(f'*{ext}')))
                count += len(list(dir_obj.glob(f'*{ext.upper()}')))
            return count
        except Exception:
            return 0

    def show_video_info(self):
        """显示视频信息"""
        video_path = self.video_input_line.text()
        if not video_path:
            QMessageBox.warning(self, "警告", "请先选择视频文件！")
            return

        try:
            info = self.video_converter.get_video_info(video_path)

            # 基本信息
            info_text = f"""视频信息：
文件: {info.get('filename', 'N/A')}
时长: {info.get('duration', 'N/A'):.2f}秒
帧率: {info.get('fps', 'N/A'):.2f} FPS
总帧数: {info.get('total_frames', 'N/A')}
分辨率: {info.get('width', 'N/A')}x{info.get('height', 'N/A')}
文件大小: {info.get('size_mb', 'N/A'):.2f} MB"""

            # 显示帧率调试信息
            fps_methods = info.get('fps_methods', [])
            fps_reported = info.get('fps_reported', 0)
            
            if fps_methods:
                info_text += f"""

帧率检测调试信息：
• OpenCV原始报告: {fps_reported:.2f} FPS
• 检测到 {len(fps_methods)} 种计算方法："""
                
                for method, value in fps_methods:
                    status = "✓ 已采用" if abs(value - info.get('fps', 0)) < 0.01 else ""
                    info_text += f"""
  - {method}: {value:.2f} FPS {status}"""
                
                info_text += f"""
• 最终选择: {info.get('fps', 'N/A'):.2f} FPS"""

            # 如果有多种时长计算方法，显示调试信息
            duration_methods = info.get('duration_methods', [])
            if len(duration_methods) > 1:
                info_text += f"""

时长计算调试信息：
• 检测到 {len(duration_methods)} 种计算方法
• 计算结果: {', '.join([f'{d:.2f}s' for d in duration_methods])}
• 选择最大值: {max(duration_methods):.2f}s (通常最准确)"""

            self.video_status.setPlainText(info_text)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取视频信息失败：{str(e)}")

    def convert_video(self):
        """转换视频"""
        video_path = self.video_input_line.text()
        output_dir = self.video_output_line.text()

        if not video_path:
            QMessageBox.warning(self, "警告", "请先选择视频文件！")
            return

        # 获取参数
        fps = self.fps_spin.value()
        start_time = self.start_spin.value()
        end_time = self.end_spin.value() if self.end_spin.value() > 0 else None
        quality = self.quality_spin.value()

        # 禁用按钮
        self.video_convert_btn.setEnabled(False)
        self.video_progress.setValue(0)
        self.video_status.append("开始转换...")

        # 创建工作线程
        def convert_func():
            return self.video_converter.convert(
                video_path, output_dir, fps, start_time, end_time, quality
            )

        self.worker = WorkerThread(convert_func)
        self.worker.finished.connect(self.on_video_finished)
        self.worker.start()

        # 模拟进度更新
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_video_progress)
        self.video_timer.start(100)

    def update_video_progress(self):
        """更新视频转换进度"""
        current = self.video_progress.value()
        if current < 90:
            self.video_progress.setValue(current + 1)
        else:
            self.video_timer.stop()

    def on_video_finished(self, success, message):
        """视频转换完成"""
        self.video_timer.stop()
        self.video_progress.setValue(100)
        self.video_convert_btn.setEnabled(True)
        self.video_status.append(message)

        if success:
            QMessageBox.information(self, "完成", "视频转换完成！")
        else:
            QMessageBox.critical(self, "错误", message)

    def process_background(self):
        """处理背景"""
        input_path = self.bg_input_line.text()
        output_path = self.bg_output_line.text()
        # 获取选中算法的实际名称，而不是显示文本
        method = self.method_combo.currentData() or self.method_combo.currentText().split(' - ')[0]

        if not input_path:
            QMessageBox.warning(self, "警告", "请先选择输入文件或目录！")
            return

        # 判断是单文件还是批量处理
        import os
        is_batch = os.path.isdir(input_path)

        if not is_batch and not output_path:
            QMessageBox.warning(self, "警告", "请设置输出文件路径！")
            return

        if is_batch and not output_path:
            # 为批量处理自动生成输出目录
            input_path_obj = Path(input_path)
            output_path = str(input_path_obj.parent / f"{input_path_obj.name}_no_bg")
            self.bg_output_line.setText(output_path)

        # 禁用按钮
        self.bg_process_btn.setEnabled(False)
        self.bg_progress.setValue(0)

        # 获取算法的友好名称用于显示
        algo_display = self.method_combo.currentText().split(' - ')[0]
        mode_str = "批量处理" if is_batch else "单文件处理"
        self.bg_status.append(f"开始{mode_str}... 算法: {algo_display}")

        # 创建工作线程
        def process_func():
            if is_batch:
                # 批量处理：输入目录，输出目录
                return self.bg_remover.batch_process(input_path, output_path, method=method)
            else:
                # 单文件处理：输入文件，输出文件
                return self.bg_remover.process_image(input_path, output_path, method=method)

        self.bg_worker = WorkerThread(process_func)
        self.bg_worker.finished.connect(self.on_bg_finished)
        self.bg_worker.start()

        # 模拟进度更新
        self.bg_timer = QTimer()
        self.bg_timer.timeout.connect(self.update_bg_progress)
        self.bg_timer.start(200)

    def update_bg_progress(self):
        """更新背景处理进度"""
        current = self.bg_progress.value()
        if current < 90:
            self.bg_progress.setValue(current + 2)
        else:
            self.bg_timer.stop()

    def on_bg_finished(self, success, message):
        """背景处理完成"""
        self.bg_timer.stop()
        self.bg_progress.setValue(100)
        self.bg_process_btn.setEnabled(True)
        self.bg_status.append(message)

        if success:
            # 显示更详细的完成信息
            input_path = self.bg_input_line.text()
            output_path = self.bg_output_line.text()
            # 重新判断是否为批量处理
            import os
            is_batch = os.path.isdir(input_path)

            if is_batch:
                success_msg = f"批量处理完成！\n\n文件已保存到目录:\n{output_path}"
                # 添加状态信息
                self.bg_status.append(f"✓ 输出目录: {output_path}")
                # 统计输出文件数量
                try:
                    output_count = len([f for f in os.listdir(output_path) if f.endswith('.png')])
                    self.bg_status.append(f"✓ 成功处理 {output_count} 张图片")
                except Exception:
                    pass
            else:
                success_msg = f"单文件处理完成！\n\n文件已保存为:\n{output_path}"

                # 检查文件是否真实存在
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path) / 1024  # KB
                    self.bg_status.append(f"✓ 文件已保存: {output_path} ({file_size:.1f} KB)")
                else:
                    self.bg_status.append(f"⚠ 警告: 无法确认文件是否保存成功")

            QMessageBox.information(self, "处理完成", success_msg)

            # 启用打开文件夹按钮
            self.bg_open_folder_btn.setEnabled(True)
        else:
            QMessageBox.critical(self, "处理错误", message)

    def open_bg_output_folder(self):
        """打开背景处理输出文件夹"""
        import subprocess
        import platform

        try:
            input_path = self.bg_input_line.text()
            output_path = self.bg_output_line.text()
            import os
            is_batch = os.path.isdir(input_path)

            if is_batch:
                # 批量处理：打开输出目录
                folder_path = output_path
            else:
                # 单文件处理：打开输出文件所在目录
                folder_path = str(Path(output_path).parent)

            folder_path = str(folder_path)

            # 根据操作系统打开文件夹
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            elif system == "Windows":
                subprocess.run(["explorer", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])

            self.bg_status.append(f"已打开文件夹: {folder_path}")

        except Exception as e:
            QMessageBox.warning(self, "警告", f"无法打开文件夹: {e}")

    # === 图片大小调整相关方法 ===
    def browse_resize_file(self):
        """浏览单个图片文件进行大小调整"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片文件", "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff *.webp);;所有文件 (*)"
        )
        if file_path:
            self.resize_input_line.setText(file_path)
            # 自动设置输出文件名
            input_path = Path(file_path)
            output_path = input_path.parent / f"{input_path.stem}_resized{input_path.suffix}"
            self.resize_output_line.setText(str(output_path))
            # 更新模式提示
            self.resize_mode_label.setText("💡 已选择单个文件，将进行单张图片大小调整")

    def browse_resize_directory(self):
        """浏览包含图片的目录进行批量大小调整"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择包含图片的目录")
        if dir_path:
            self.resize_input_line.setText(dir_path)
            # 自动设置输出目录
            input_path = Path(dir_path)
            output_path = input_path.parent / f"{input_path.name}_resized"
            self.resize_output_line.setText(str(output_path))
            # 统计图片数量
            image_count = self.count_images_in_directory(dir_path)
            self.resize_mode_label.setText(f"💡 已选择目录，将批量调整 {image_count} 张图片大小")

    def browse_resize_output_file(self):
        """浏览单个输出文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存调整后的图片", "",
            "图片文件 (*.jpg *.png);;所有文件 (*)"
        )
        if file_path:
            self.resize_output_line.setText(file_path)

    def browse_resize_output_directory(self):
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.resize_output_line.setText(dir_path)

    def on_preset_changed(self):
        """预设尺寸改变时的处理"""
        current_data = self.size_preset_combo.currentData()
        if current_data:
            width, height = current_data
            self.width_spin.setValue(width)
            self.height_spin.setValue(height)

    def show_resize_info(self):
        """显示图片信息"""
        input_path = self.resize_input_line.text()
        if not input_path:
            QMessageBox.warning(self, "警告", "请先选择图片文件！")
            return

        if os.path.isfile(input_path):
            try:
                info = self.image_resizer.get_image_info(input_path)
                if info:
                    info_text = f"""图片信息：
文件: {info.get('filename', 'N/A')}
尺寸: {info.get('width', 'N/A')} x {info.get('height', 'N/A')} 像素
格式: {info.get('format', 'N/A')}
颜色模式: {info.get('mode', 'N/A')}
文件大小: {info.get('size_mb', 'N/A'):.2f} MB"""
                    self.resize_status.setPlainText(info_text)
                else:
                    self.resize_status.setPlainText("无法获取图片信息")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"获取图片信息失败：{str(e)}")
        else:
            # 显示目录统计信息
            if os.path.isdir(input_path):
                image_count = self.count_images_in_directory(input_path)
                info_text = f"""目录信息：
路径: {input_path}
图片文件数量: {image_count} 张
支持的格式: jpg, jpeg, png, bmp, tiff, webp"""
                self.resize_status.setPlainText(info_text)
            else:
                QMessageBox.warning(self, "警告", "请选择有效的图片文件或目录！")

    def process_resize(self):
        """处理图片大小调整"""
        input_path = self.resize_input_line.text()
        output_path = self.resize_output_line.text()

        if not input_path:
            QMessageBox.warning(self, "警告", "请先选择输入文件或目录！")
            return

        # 判断是单文件还是批量处理
        is_batch = os.path.isdir(input_path)

        if not is_batch and not output_path:
            QMessageBox.warning(self, "警告", "请设置输出文件路径！")
            return

        if is_batch and not output_path:
            # 为批量处理自动生成输出目录
            input_path_obj = Path(input_path)
            output_path = str(input_path_obj.parent / f"{input_path_obj.name}_resized")
            self.resize_output_line.setText(output_path)

        # 获取参数
        width = self.width_spin.value()
        height = self.height_spin.value()
        keep_aspect = self.keep_aspect_check.isChecked()
        quality = self.resize_quality_spin.value()
        method = self.resize_method_combo.currentData() or "LANCZOS"

        # 获取输出格式
        format_text = self.output_format_combo.currentText()
        output_format = None
        if format_text == "JPG":
            output_format = "jpg"
        elif format_text == "PNG":
            output_format = "png"

        # 禁用按钮
        self.resize_process_btn.setEnabled(False)
        self.resize_progress.setValue(0)

        mode_str = "批量处理" if is_batch else "单文件处理"
        self.resize_status.append(f"开始{mode_str}... 目标尺寸: {width}x{height}")

        # 创建工作线程
        def process_func():
            if is_batch:
                # 批量处理
                return self.image_resizer.batch_resize(
                    input_path, output_path, width, height,
                    keep_aspect, quality, method, output_format
                )
            else:
                # 单文件处理
                return self.image_resizer.resize_image(
                    input_path, output_path, width, height,
                    keep_aspect, quality, method
                )

        self.resize_worker = WorkerThread(process_func)
        self.resize_worker.finished.connect(self.on_resize_finished)
        self.resize_worker.start()

        # 模拟进度更新
        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self.update_resize_progress)
        self.resize_timer.start(200)

    def update_resize_progress(self):
        """更新图片大小调整进度"""
        current = self.resize_progress.value()
        if current < 90:
            self.resize_progress.setValue(current + 2)
        else:
            self.resize_timer.stop()

    def on_resize_finished(self, success, message):
        """图片大小调整完成"""
        self.resize_timer.stop()
        self.resize_progress.setValue(100)
        self.resize_process_btn.setEnabled(True)
        self.resize_status.append(message)

        if success:
            # 显示更详细的完成信息
            input_path = self.resize_input_line.text()
            output_path = self.resize_output_line.text()
            is_batch = os.path.isdir(input_path)

            if is_batch:
                success_msg = f"批量大小调整完成！\n\n文件已保存到目录:\n{output_path}"
                # 添加状态信息
                self.resize_status.append(f"✓ 输出目录: {output_path}")
                # 统计输出文件数量
                try:
                    output_files = [f for f in os.listdir(output_path)
                                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'))]
                    self.resize_status.append(f"✓ 成功调整 {len(output_files)} 张图片大小")
                except Exception:
                    pass
            else:
                success_msg = f"图片大小调整完成！\n\n文件已保存为:\n{output_path}"

                # 检查文件是否真实存在
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path) / 1024  # KB
                    self.resize_status.append(f"✓ 文件已保存: {output_path} ({file_size:.1f} KB)")

                    # 显示调整后的尺寸信息
                    try:
                        info = self.image_resizer.get_image_info(output_path)
                        if info:
                            self.resize_status.append(f"✓ 调整后尺寸: {info['width']} x {info['height']} 像素")
                    except Exception:
                        pass
                else:
                    self.resize_status.append(f"⚠ 警告: 无法确认文件是否保存成功")

            QMessageBox.information(self, "处理完成", success_msg)

            # 启用打开文件夹按钮
            self.resize_open_folder_btn.setEnabled(True)
        else:
            QMessageBox.critical(self, "处理错误", message)

    def open_resize_output_folder(self):
        """打开图片大小调整输出文件夹"""
        import subprocess
        import platform

        try:
            input_path = self.resize_input_line.text()
            output_path = self.resize_output_line.text()
            is_batch = os.path.isdir(input_path)

            if is_batch:
                # 批量处理：打开输出目录
                folder_path = output_path
            else:
                # 单文件处理：打开输出文件所在目录
                folder_path = str(Path(output_path).parent)

            folder_path = str(folder_path)

            # 根据操作系统打开文件夹
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            elif system == "Windows":
                subprocess.run(["explorer", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])

            self.resize_status.append(f"已打开文件夹: {folder_path}")

        except Exception as e:
            QMessageBox.warning(self, "警告", f"无法打开文件夹: {e}")


def main():
    """主函数"""
    app = QApplication(sys.argv)

    # 设置应用信息
    app.setApplicationName("多媒体处理工具集")
    app.setOrganizationName("MyTool")

    # 创建主窗口
    window = IntegratedGUI()
    window.show()

    # 运行应用
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()