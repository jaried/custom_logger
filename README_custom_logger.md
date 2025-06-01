# Custom Logger

自定义日志系统，支持多进程和异步文件写入。

**作者**: Tony Xiao  
**邮箱**: tony.xiao@gmail.com

## 特性

- 支持多种日志级别（包括worker专用级别）
- 实时控制台输出（支持Windows CMD颜色）
- 异步文件写入（不阻塞主线程）
- 多进程/多线程安全
- 基于config_manager的配置管理
- 自动日志目录管理

## 安装

```bash
pip install -e .
```

## 快速开始

### 主程序初始化

```python
from custom_logger import init_custom_logger_system, get_logger

# 主程序初始化（仅调用一次）
init_custom_logger_system()

# 获取logger
logger = get_logger("main")
logger.info("程序启动")
```

### Worker使用

```python
from custom_logger import get_logger

# 直接获取logger，无需初始化
logger = get_logger("worker", console_level="w_summary")
logger.worker_summary("Worker开始执行")
logger.worker_detail("详细worker信息")
```

## 日志级别

- **标准级别**：DEBUG > INFO > WARNING > ERROR > CRITICAL > EXCEPTION
- **扩展级别**：DEBUG > DETAIL > W_SUMMARY > W_DETAIL

## 配置

配置文件位置：`src/config/custom_logger.yaml`

主要配置项：

- `project_name`：项目名称
- `experiment_name`：实验名称
- `global_console_level`：全局控制台日志级别
- `global_file_level`：全局文件日志级别

## 测试

```bash
pytest tests/
```

## 依赖

- Python >= 3.12
- config_manager