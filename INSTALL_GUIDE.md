# 安装指南

## 快速安装

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python run_integrated_gui.py
```

## 依赖说明

### 核心依赖
- **PyQt5** - 现代化GUI界面框架
- **opencv-python** - 视频/图像处理
- **Pillow** - 图像操作
- **numpy** - 数值计算
- **rembg** - AI智能去背景

### PyQt5安装

如果自动安装失败，可手动安装：

```bash
# 通用安装
pip install PyQt5

# macOS使用Homebrew
brew install pyqt5

# Ubuntu/Debian
sudo apt install python3-pyqt5

# CentOS/RHEL
sudo yum install python3-PyQt5
```

## 系统要求

- Python 3.7+
- PyQt5 5.15+
- 足够的磁盘空间（PNG文件通常较大）
- rembg首次使用会下载AI模型（约180MB）

## 常见问题

### 1. PyQt5安装失败
- 确保Python版本兼容（≥3.7）
- 更新pip: `pip install --upgrade pip`
- 尝试不同版本: `pip install PyQt5==5.15.10`

### 2. rembg模型下载慢
- 确保网络连接稳定
- 模型文件约180MB，请耐心等待
- 模型会缓存到本地，只需下载一次

### 3. 应用启动失败
- 检查所有依赖是否正确安装: `pip list`
- 查看详细错误信息进行排查
- 确保Python路径正确

## 开发环境设置

### 使用虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv mytool_env

# 激活虚拟环境
# Windows
mytool_env\Scripts\activate
# macOS/Linux
source mytool_env/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 使用conda

```bash
# 创建conda环境
conda create -n mytool python=3.11 -y
conda activate mytool

# 安装依赖
pip install -r requirements.txt
```

## 验证安装

运行以下命令验证安装：

```python
# 测试PyQt5
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"

# 测试opencv
python -c "import cv2; print('OpenCV OK')"

# 测试rembg
python -c "import rembg; print('rembg OK')"
```

如果所有测试都通过，说明安装成功！