# 文字转手写体应用

一个可以将普通文字转换为横版A5大小手写体图片的Python应用。

## 功能特性

- ✅ 支持将普通文字转换为自然的手写体效果
- ✅ 输出A5横版尺寸的高清图片（300dpi）
- ✅ 多种手写体样式可选：默认、紧凑、整洁、随意
- ✅ 支持自定义字体文件
- ✅ 提供两种界面模式：命令行界面(CLI)和图形用户界面(GUI)
- ✅ 支持从文件读取文字内容
- ✅ 交互式文字输入

## 项目结构

```
handwriting-with-AI/
├── src/                # 源代码目录
│   ├── main.py         # 核心转换功能
│   ├── cli.py          # 命令行界面
│   ├── gui.py          # 图形用户界面
│   └── config.py       # 配置和样式管理
├── output/             # 输出图片目录
├── fonts/              # 自定义字体目录
├── LingWaiTC-Medium.otf # 示例字体文件
├── run_app.py          # 应用主入口
├── README.md           # 项目说明文档
├── TODO.md             # 开发计划
├── LICENSE             # 许可证文件
└── .gitignore          # Git忽略文件
```

## 安装说明

### 1. 克隆或下载项目

```bash
git clone https://github.com/yourusername/handwriting-with-AI.git
cd handwriting-with-AI
```

### 2. 安装依赖

本项目需要以下Python库：
- handright: 用于生成手写体效果
- Pillow: 用于图像处理

使用pip安装依赖：

```bash
pip install handright pillow
```

## 使用方法

### 快速开始

运行主入口文件，根据提示选择界面模式：

```bash
python run_app.py
```

### 命令行界面

#### 交互式模式

```bash
python run_app.py --cli
# 或者
python src/cli.py
```

按照提示输入文字内容和选择样式。

#### 直接指定参数

```bash
# 使用指定文字
python src/cli.py --text "这是一段测试文字"

# 使用文本文件
python src/cli.py --file path/to/textfile.txt

# 指定输出路径
python src/cli.py --text "测试文字" --output result.png

# 选择样式
python src/cli.py --text "测试文字" --style neat
```

#### 命令行参数说明

- `-t`, `--text`: 要转换的文字内容
- `-f`, `--file`: 包含要转换文字的文本文件路径
- `-o`, `--output`: 输出图片路径
- `-F`, `--font`: 自定义字体文件路径
- `-s`, `--style`: 预设样式（default/compact/neat/casual）
- `-i`, `--interactive`: 启动交互式模式

### 图形用户界面

```bash
python run_app.py --gui
# 或者
python src/gui.py
```

图形界面提供了直观的操作方式：
- 在文本框中输入要转换的文字
- 选择手写体样式
- 可选：指定自定义字体文件
- 点击"转换为手写体"按钮
- 查看预览并获取生成的图片

## 手写体样式说明

- **default**: 默认样式，平衡的手写效果
- **compact**: 紧凑样式，节省空间，适合长文本
- **neat**: 整洁样式，更加规整，适合正式场合
- **casual**: 随意样式，更加自然，手写感更强

## 常见问题

### 1. 中文字体显示问题

如果中文字体显示不正常，可以尝试指定自定义字体文件。项目根目录提供了一个示例字体文件 `LingWaiTC-Medium.otf`。

### 2. 生成的图片太大

当前配置为A5横版300dpi，这是为了保证打印质量。如果需要更小的图片，可以修改 `config.py` 中的配置。

### 3. GUI界面无法启动

确保你的Python环境中安装了tkinter库。tkinter通常是Python标准库的一部分，但在某些Linux系统中可能需要单独安装：

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install python3-tkinter
```

## 许可证

本项目采用MIT许可证。详情请查看 [LICENSE](LICENSE) 文件。

## 致谢

- 感谢 [handright](https://github.com/Gsllchb/Handright) 库提供的手写体生成功能
- 感谢 [Pillow](https://python-pillow.org/) 库提供的图像处理支持
