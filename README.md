# 文字转手写体应用（集成Ollama AI功能）

一个可以将普通文字转换为横版A5大小手写体图片的Python应用，并集成了Ollama AI功能以增强文字处理能力。

## 功能特性

- ✅ 支持将普通文字转换为自然的手写体效果
- ✅ 输出A5横版尺寸的高清图片（300dpi）
- ✅ 多种手写体样式可选：默认、紧凑、整洁、随意
- ✅ 支持自定义字体文件
- ✅ 提供两种界面模式：命令行界面(CLI)和图形用户界面(GUI)
- ✅ 支持从文件读取文字内容
- ✅ 交互式文字输入
- ✅ 集成Ollama AI功能，支持AI辅助文字生成
- ✅ 流式响应显示，实时查看AI生成内容
- ✅ 支持从AI生成内容中选择片段导入到转换区域

## 项目结构

```
handwriting-with-AI/
├── src/                # 源代码目录
│   ├── main.py         # 核心转换功能
│   ├── cli.py          # 命令行界面
│   ├── gui.py          # 图形用户界面（集成AI功能）
│   ├── config.py       # 配置和样式管理
│   └── ollama_utils.py # Ollama AI功能工具类
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
- ollama: 用于AI功能集成

使用pip安装依赖：

```bash
pip install handright pillow ollama
```

### 3. 安装并配置Ollama

要使用AI功能，您需要安装并运行Ollama本地服务：

1. 从[Ollama官网](https://ollama.com/)下载并安装Ollama
2. 拉取您需要的模型，例如：
   ```bash
   ollama pull llama3.2
   ollama pull deepseek-coder
   ollama pull qwen3:0.6b  # 轻量级中文模型推荐
   ollama pull deepseek-r1:latest  # 适合手写练习和创意生成的模型
   ```
3. 启动Ollama服务：
   ```bash
   ollama serve
   ```
4. 测试Ollama服务是否正常运行：
   ```bash
   # 检查Ollama服务状态
   curl http://localhost:11434/api/tags

   # 或者使用项目提供的测试脚本
   cd src
   python test_ollama.py
   ```

## 使用方法

### 快速开始

运行主入口文件，根据提示选择界面模式：

```bash
python run_app.py
```

### 注意：使用AI功能前的准备

在使用GUI中的AI功能前，请确保：

1. Ollama服务正在运行（通过 `ollama serve`命令启动）
2. 至少已下载一个可用的AI模型（如 `llama3.2`、`qwen3:0.6b`等）
3. 通过GUI界面中的"刷新模型列表"按钮验证应用能否正确检测到模型
4. 如果模型列表为空，请检查Ollama服务和网络连接

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

### 基本转换功能

- 在主页面文本框中输入要转换的文字
- 选择手写体样式
- 可选：指定自定义字体文件
- 点击"转换为手写体"按钮
- 查看预览并获取生成的图片

### AI辅助功能（通过标签页切换）

- **刷新模型列表**：点击按钮获取当前可用的Ollama模型
- **选择模型**：从下拉菜单中选择要使用的AI模型
- **输入提示词**：在输入框中输入您的问题或指令
- **预设提示**：点击预设按钮快速插入常用提示词
- **发送请求**：点击"发送"按钮开始AI生成
- **查看流式响应**：AI回复将实时显示在下方文本区域
- **导入内容**：选择AI生成内容中的片段，点击"导入所选"按钮将内容添加到转换区域
- **停止生成**：在AI生成过程中可以随时点击"停止"按钮终止生成
- **清空输出**：点击"清空"按钮重置AI交互区域

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

### 4. Ollama模型未找到问题

如果应用无法检测到Ollama模型，请按照以下步骤排查：

1. **确认Ollama服务正在运行**：

   ```bash
   # 检查服务状态
   ps aux | grep ollama
   # 或者重启服务
   ollama serve
   ```
2. **验证模型已正确下载**：

   ```bash
   ollama list
   ```

   确认列表中显示了你需要的模型。
3. **检查网络连接**：

   ```bash
   curl http://localhost:11434/api/tags
   ```

   这应该返回包含模型信息的JSON响应。
4. **使用测试脚本诊断问题**：

   ```bash
   cd src
   python test_ollama.py
   ```

   查看详细的连接和模型检测日志。
5. **检查防火墙设置**：
   确保本地防火墙没有阻止11434端口的连接。
6. **重新启动应用程序**：
   有时候需要重新启动应用程序才能识别到新的模型或服务状态变化。

### 5. 推荐使用的Ollama模型

- **中文轻量级模型**：`qwen3:0.6b` - 适合基础文本生成和手写内容建议
- **代码相关模型**：`deepseek-coder` - 适合生成代码示例
- **通用模型**：`llama3.2` - 通用能力强，响应质量高

## 许可证

本项目采用MIT许可证。详情请查看 [LICENSE](LICENSE) 文件。
