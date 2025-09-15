# 多媒体处理工具集

一个功能强大的Python工具集，包含视频转PNG和自动去背景两大功能模块。支持命令行和图形界面两种使用方式。

## 🎬 视频转PNG工具
将视频文件转换为PNG图片序列

## 🖼️ 自动去背景工具
自动移除图片背景，生成透明PNG文件

## 功能特性

### 🎬 视频转PNG功能
- 支持多种视频格式：MP4, AVI, MOV, MKV, WMV, FLV, WebM
- 高质量PNG输出，可调节压缩级别
- 灵活的帧率控制，可提取所有帧或指定帧率
- 时间范围选择，支持提取视频片段
- 实时进度显示和详细的视频信息显示

### 🖼️ 自动去背景功能
- 🤖 AI智能去背景（rembg模型）
- 🎯 多种算法选择：GrabCut、分水岭、K-means、阈值
- 📁 批量处理支持
- 🖼️ 实时预览效果
- 🎨 透明背景PNG输出
- ⚙️ 可调参数设置

### 🖥️ 通用特性
- 🎯 **整合界面** - 所有功能集成在一个窗口中
- 🖥️ **现代GUI** - 基于PyQt5的专业界面
- 💻 **命令行支持** - 支持脚本自动化
- 🌐 **跨平台兼容** - Windows/macOS/Linux通用

## 安装依赖

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
# 基础依赖
pip install opencv-python Pillow numpy PyQt5

# 去背景功能依赖
pip install rembg
```

## 使用方法

### 🚀 推荐：整合图形界面

启动整合界面（包含所有功能）：
```bash
python run_integrated_gui.py
```

**整合界面功能：**
- **第一个选项卡：🎬 视频转PNG**
  - 输入原视频路径选择
  - 输出目录路径设置
  - 帧率、时间范围、质量等参数调节
  - 视频信息查看和实时转换

- **第二个选项卡：🖼️ 去背景**
  - 单张图片去背景（带预览功能）
  - 批量图片处理
  - 多种算法选择和参数调节

---

## 🎬 视频转PNG工具使用

### 1. 命令行版本

基本使用：
```bash
python video_to_png.py input_video.mp4
```

高级选项：
```bash
python video_to_png.py input_video.mp4 \
    --output my_frames \
    --rate 2.0 \
    --start 10 \
    --end 60 \
    --quality 1
```

#### 命令行参数说明

- `input`: 输入视频文件路径（必需）
- `-o, --output`: 输出目录（默认：output_frames）
- `-r, --rate`: 提取帧率，例如1.0表示每秒1帧（可选）
- `-s, --start`: 开始时间，单位秒（默认：0）
- `-e, --end`: 结束时间，单位秒（默认：视频结尾）
- `-q, --quality`: PNG压缩级别，0-9（0=最高质量，默认：3）
- `--info`: 只显示视频信息，不进行转换

#### 示例

查看视频信息：
```bash
python video_to_png.py my_video.mp4 --info
```

提取前30秒，每秒1帧：
```bash
python video_to_png.py my_video.mp4 -o frames_1fps -r 1.0 -e 30
```

提取1分钟到2分钟的片段，最高质量：
```bash
python video_to_png.py my_video.mp4 -s 60 -e 120 -q 0
```

### 2. 图形界面版本

使用整合GUI（推荐）：
```bash
python run_integrated_gui.py
```

GUI功能：
- 📁 可视化文件选择
- ⚙️ 直观的参数设置
- 📊 实时进度显示
- 📝 视频信息预览
- 🎛️ 现代化PyQt5界面

## 输出说明

### 文件命名格式

生成的PNG文件按以下格式命名：
```
frame_000001_0.033s.png
frame_000002_0.067s.png
frame_000003_0.100s.png
...
```

格式说明：
- `frame_`: 固定前缀
- `000001`: 帧序号（6位数字，补零）
- `0.033s`: 时间戳（秒）
- `.png`: 文件扩展名

### 输出目录结构

```
output_frames/
├── frame_000001_0.033s.png
├── frame_000002_0.067s.png
├── frame_000003_0.100s.png
└── ...
```

## 性能优化建议

### PNG压缩级别选择

| 级别 | 说明 | 适用场景 |
|------|------|----------|
| 0-1  | 最高质量，文件较大 | 专业用途，后期处理 |
| 2-4  | 平衡质量与大小（推荐） | 一般用途 |
| 5-7  | 较高压缩，质量良好 | 存储空间有限 |
| 8-9  | 最高压缩，质量下降 | 预览或临时使用 |

### 帧率选择建议

| 帧率 | 说明 | 适用场景 |
|------|------|----------|
| 原始帧率 | 提取所有帧 | 完整分析，动画制作 |
| 10-15 FPS | 高频采样 | 动作分析 |
| 1-5 FPS | 中频采样 | 内容分析 |
| 0.1-1 FPS | 低频采样 | 关键帧提取 |

## 故障排除

### 常见问题

1. **"无法打开视频文件"**
   - 检查文件路径是否正确
   - 确认视频文件未损坏
   - 验证文件格式是否支持

2. **"内存不足"**
   - 降低提取帧率
   - 提高PNG压缩级别
   - 分段处理长视频

3. **"转换速度慢"**
   - 提高PNG压缩级别
   - 降低提取帧率
   - 使用SSD存储

### 支持的视频格式

✅ 支持的格式：
- MP4 (推荐)
- AVI
- MOV
- MKV
- WMV
- FLV
- WebM

❌ 不支持的格式：
- 受DRM保护的视频
- 某些专有格式

## 系统要求

- Python 3.7+
- OpenCV 4.0+
- 足够的磁盘空间（PNG文件通常较大）

## 许可证

MIT License

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的视频转PNG功能
- 提供命令行和GUI两种界面
- 支持多种视频格式
- 可调节输出质量和帧率

## 贡献

欢迎提交Issue和Pull Request！

## 🖼️ 自动去背景工具使用

### 1. 命令行版本

基本使用（推荐AI方法）：
```bash
python remove_background.py input_image.jpg
```

指定输出文件：
```bash
python remove_background.py input_image.jpg -o output_no_bg.png
```

使用不同算法：
```bash
# 使用GrabCut算法
python remove_background.py input_image.jpg -m grabcut --iterations 10

# 使用K-means聚类
python remove_background.py input_image.jpg -m kmeans --k 4

# 使用阈值方法（适用于纯色背景）
python remove_background.py input_image.jpg -m threshold --threshold 200
```

批量处理：
```bash
python remove_background.py /path/to/images/ --batch -o output_directory -m rembg
```

### 2. 图形界面版本

使用整合GUI（推荐）：
```bash
python run_integrated_gui.py
```

GUI功能：
- 📁 可视化文件选择
- 🔍 实时预览效果
- ⚙️ 多种算法选择
- 📊 批量处理支持
- 🎛️ 现代化PyQt5界面

### 去背景算法说明

| 算法 | 特点 | 适用场景 | 处理速度 |
|------|------|----------|----------|
| **rembg** | AI智能识别，效果最佳 | 通用场景，复杂背景 | 中等 |
| **grabcut** | 交互式分割，可调参数 | 主体明确的图片 | 快 |
| **watershed** | 基于梯度的分割 | 边界清晰的图片 | 快 |
| **kmeans** | 颜色聚类分割 | 颜色差异明显 | 快 |
| **threshold** | 简单阈值分割 | 纯色背景 | 最快 |

### 推荐使用流程

1. **首选rembg**：对于大多数场景，AI算法效果最佳
2. **纯色背景**：使用threshold方法，速度最快
3. **批量处理**：根据图片类型选择合适算法
4. **预览调试**：使用GUI实时预览不同算法效果

### 注意事项

- rembg首次使用会下载AI模型（约180MB）
- 处理大图片时建议使用较快的算法
- 批量处理时建议先用少量图片测试效果

### 常见问题解决

#### 1. scikit-image版本兼容问题
如果遇到类似错误：
```
The `skimage.future.graph` submodule was moved to `skimage.graph` in v0.20
```
解决方案：当前版本已移除对scikit-image的依赖，请重新安装：
```bash
pip install -r requirements.txt
```

#### 2. rembg安装问题
如果rembg安装失败，请尝试：
```bash
pip install --upgrade pip
pip install rembg
```

#### 3. 模型下载慢
rembg首次使用需要下载AI模型，如果下载慢：
- 请确保网络连接稳定
- 模型文件约180MB，请耐心等待
- 模型会缓存到本地，只需下载一次

#### 4. PyQt5界面问题
如果GUI界面显示异常：
- 确保PyQt5正确安装: `pip install PyQt5`
- 检查显示环境变量设置
- 尝试重新安装: `pip install --upgrade PyQt5`

## 快速启动

### 🚀 推荐：使用整合界面

```bash
# 启动整合工具（推荐）
python run_integrated_gui.py
```

整合界面特色：
- 📱 **统一界面**：所有功能集中在一个窗口
- 🎯 **选项卡设计**：视频转PNG和去背景功能分别在不同选项卡
- 💾 **便捷操作**：文件路径自动关联，操作更流畅
- 🎨 **现代界面**：基于PyQt5的专业UI设计

## 联系方式

如有问题或建议，请通过GitHub Issues联系。
