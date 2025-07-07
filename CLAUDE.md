# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个高性能的Python自定义日志系统（版本1.0.0），支持：
- 基于队列架构的多进程/多线程日志记录
- 带智能调用者识别的异步文件写入
- 多种日志级别，包括自定义级别（W_DETAIL, W_SUMMARY, DETAIL）
- 智能目录管理和配置隔离
- 长时间运行操作的实时倒计时功能

**重要约束**: 本项目彻底不使用config_manager，只用config_manager创建的对象。

## 开发命令

### 测试
```bash
# 运行所有测试
python -m pytest

# 运行特定测试模块
python -m pytest tests/test_custom_logger/test_new_api.py
python -m pytest tests/01_unit_tests/

# 以详细输出运行
python -m pytest -v --tb=short

# 运行特定测试函数（函数以'tc'开头）
python -m pytest -k "tc0015"
```

### 包管理
```bash
# 以开发模式安装（推荐）
pip install -e .

# 从requirements安装
pip install -r requirements.txt

# 构建包
python setup.py sdist bdist_wheel

# 使用conda环境（如果需要）
conda run -n base_python3.12 pip install -e .
```

### 代码质量检查
```bash
# 使用ruff检查代码风格
ruff check src/
ruff check tests/

# 格式化代码
ruff format src/
ruff format tests/
```

### 演示和测试
```bash
# 运行综合演示
python src/demo/demo_comprehensive_custom_logger.py
python src/demo/new_api_demo.py

# 运行特定功能演示
python src/demo/queue_based_logging_demo.py
python src/demo/color_support_demo.py
python src/demo/worker_path_demo/demo_worker_path_quick.py
```

## 架构概览

### 核心组件

1. **Manager (`manager.py`)**：系统初始化和生命周期管理
   - `init_custom_logger_system()` - 主进程初始化
   - `init_custom_logger_system_for_worker()` - Worker进程初始化
   - `get_logger()` - Logger实例获取

2. **Logger (`logger.py`)**：核心日志功能
   - 包含标准和扩展日志级别的`CustomLogger`类
   - ANSI颜色支持，集成Windows注册表
   - 进度指示的倒计时功能

3. **Writer (`writer.py`)**：文件写入系统
   - 带后台线程的异步文件写入
   - 使用栈检查的智能调用者识别
   - 路径管理和目录创建

4. **Queue Writer (`queue_writer.py`)**：多进程队列支持
   - Worker进程的基于队列的日志记录
   - 独立的发送者/接收者架构

5. **Formatter (`formatter.py`)**：日志消息格式化
   - 彩色控制台输出
   - 带调用者信息的结构化文件输出
   - 异常处理和堆栈跟踪格式化

6. **Config (`config.py`)**：配置管理
   - 与config_manager对象集成（不直接使用）
   - 级别解析和验证
   - 目录路径解析

### 关键设计原则

- **不直接使用config_manager**：仅使用由config_manager创建的config对象
- **16字符logger名称限制**：为保持格式一致性而强制执行
- **Workers的队列模式**：多进程场景的独立初始化路径
- **调用者识别**：自动识别调用的模块/函数
- **异步文件操作**：为性能优化的非阻塞文件写入

### 配置结构

系统期望config对象具有以下属性：
```python
config.paths.log_dir          # 日志目录路径
config.first_start_time       # 程序启动时间（datetime）
config.logger.enable_queue_mode     # 可选：启用队列模式
config.logger.global_console_level  # 可选：全局控制台级别
config.logger.global_file_level     # 可选：全局文件级别
config.queue_info.log_queue         # 可选：worker进程的队列对象
```

### 日志级别（按顺序）
- W_DETAIL (3), W_SUMMARY (5), DETAIL (8), DEBUG (10), INFO (20), WARNING (30), ERROR (40), CRITICAL (50), EXCEPTION (60)

### 使用模式

**单进程：**
```python
from custom_logger import init_custom_logger_system, get_logger
config = get_config_manager()
init_custom_logger_system(config)
logger = get_logger("main")
```

**多进程（推荐方式 - 自动继承）：**
```python
# 主进程
config = get_config_manager()
init_custom_logger_system(config)

# Worker进程（自动继承配置）
def worker_function(worker_id):
    worker_logger = get_logger("worker")
    worker_logger.info(f"Worker {worker_id} 启动")
```

**多进程（队列模式）：**
```python
# 主进程
config.logger.enable_queue_mode = True
config.queue_info.log_queue = queue_object
init_custom_logger_system(config)

# Worker进程
init_custom_logger_system_for_worker(serialized_config)
logger = get_logger("worker")
```

## 重要约束

- Logger名称必须≤16个字符（超过会抛出ValueError）
- 必须在使用get_logger()之前调用初始化函数
- 队列模式需要enable_queue_mode=True和队列对象
- 每个进程只能进行一次logger系统初始化
- Worker进程需要独立的初始化函数

## 测试指南

- 测试函数应以'tc'前缀开头
- 使用pytest标记：unit, integration, slow
- 测试组织在tests/test_custom_logger/和tests/01_unit_tests/中
- 集成测试在test_tc0010_minimal_integration.py中
- API合规性测试在test_new_api_requirements.py中