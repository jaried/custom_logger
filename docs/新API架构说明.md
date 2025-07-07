# Custom Logger 新API架构说明

## 概述

根据需求变更，Custom Logger 现在支持两种模式：
1. **普通模式**：传统的异步文件写入
2. **队列模式**：主程序从队列读取并写文件，Worker进程发送到队列

## 核心变更

### 1. init_custom_logger_system 函数变更

**旧版本**：
```python
init_custom_logger_system(
    config_path: Optional[str] = None,
    first_start_time: Optional[datetime] = None
)
```

**新版本**：
```python
init_custom_logger_system(config_object: Any) -> None
```

**主要变更**：
- 只接收 `config_object` 参数
- 不再调用 config_manager，直接使用传入的 config 对象
- 使用 `config.paths.log_dir` 作为工作路径
- 使用 `config.first_start_time` 用于计时
- 取消对 `first_start_time` 参数的支持

### 2. 新增 init_custom_logger_system_for_worker 函数

```python
init_custom_logger_system_for_worker(
    serializable_config_object: Any,
    worker_id: str = None
) -> None
```

**功能**：
- 专门用于 Worker 进程初始化
- 接收序列化的配置对象
- Worker 自己打印日志到控制台
- 把需要存文件的信息传给队列

### 3. 队列模式支持

当配置对象包含 `queue_info.log_queue` 时，自动启用队列模式：

**主程序**：
- 启动队列接收器
- 从队列读取日志并写入文件
- 自己的日志也正常处理

**Worker进程**：
- 启动队列发送器
- 日志同时输出到控制台和发送到队列
- 主程序负责文件写入

## 配置对象结构

### 基本结构

```python
class ConfigObject:
    def __init__(self):
        # 必需属性
        self.first_start_time = datetime.now()
        self.paths = {
            'log_dir': '/path/to/logs'
        }
        
        # 可选：队列信息（启用队列模式）
        self.queue_info = {
            "log_queue": multiprocessing.Queue(),
            "queue_type": "multiprocessing.Queue",
            "queue_size": 1000,
        }
        
        # 日志配置
        self.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
            "module_levels": {},
            "show_call_chain": True,
            "show_debug_call_stack": False,
        }
```

### 队列模式配置

要启用队列模式，配置对象必须包含：
- `queue_info.log_queue`：实际的队列对象（multiprocessing.Queue）

## 使用示例

### 普通模式

```python
from custom_logger import init_custom_logger_system, get_logger
from datetime import datetime

class SimpleConfig:
    def __init__(self):
        self.first_start_time = datetime.now()
        self.paths = {'log_dir': '/path/to/logs'}
        self.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
        }

config = SimpleConfig()
init_custom_logger_system(config)
logger = get_logger("test")
logger.info("这是普通模式的日志")
```

### 队列模式

**主程序**：
```python
import multiprocessing as mp
from custom_logger import init_custom_logger_system, get_logger

class MainConfig:
    def __init__(self):
        self.first_start_time = datetime.now()
        self.paths = {'log_dir': '/path/to/logs'}
        self.queue_info = {
            "log_queue": mp.Queue(maxsize=1000)
        }
        self.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
        }

# 主程序初始化（启用队列接收器）
config = MainConfig()
init_custom_logger_system(config)
main_logger = get_logger("main")
main_logger.info("主程序日志")

# 启动worker进程...
```

**Worker进程**：
```python
from custom_logger import init_custom_logger_system_for_worker, get_logger

def worker_process(log_queue, log_dir, first_start_time, worker_id):
    class WorkerConfig:
        def __init__(self):
            self.first_start_time = first_start_time
            self.paths = {'log_dir': log_dir}
            self.queue_info = {"log_queue": log_queue}
            self.logger = {
                "global_console_level": "info",
                "global_file_level": "debug",
            }
    
    # Worker初始化（启用队列发送器）
    worker_config = WorkerConfig()
    init_custom_logger_system_for_worker(worker_config, f"worker_{worker_id}")
    
    logger = get_logger(f"w{worker_id}")
    logger.info("Worker日志")  # 同时输出到控制台和发送到队列
```

## 架构优势

### 1. 解耦设计
- Custom Logger 不再依赖 config_manager
- 配置对象由外部程序提供
- 支持任意配置对象结构

### 2. 灵活的多进程支持
- 主程序：统一的文件写入管理
- Worker：独立的日志处理，无文件竞争
- 队列：高效的进程间日志传输

### 3. 向后兼容
- 保留原有的日志级别和格式
- 保留颜色支持和终端适配
- 保留异常处理和错误恢复

## 注意事项

### 1. 配置对象要求
- 必须包含 `paths.log_dir` 属性
- 必须包含 `first_start_time` 属性
- 队列模式需要 `queue_info.log_queue` 属性

### 2. 多进程队列传递
- 在 Windows 上使用 `spawn` 模式时，队列对象不能通过 pickle 序列化
- 建议使用 `multiprocessing.Process` 而不是 `Pool`
- 队列对象通过进程参数直接传递

### 3. 资源清理
- 主程序和 Worker 都需要调用 `tear_down_custom_logger_system()`
- 队列接收器会自动处理停止信号
- 建议使用 `atexit` 注册清理函数

## API 参考

### 函数列表

- `init_custom_logger_system(config_object)` - 主程序初始化
- `init_custom_logger_system_for_worker(config_object, worker_id)` - Worker初始化
- `get_logger(name)` - 获取日志器
- `tear_down_custom_logger_system()` - 清理系统
- `is_initialized()` - 检查初始化状态
- `is_queue_mode()` - 检查队列模式状态

### 配置属性

**必需属性**：
- `first_start_time: datetime` - 启动时间
- `paths.log_dir: str` - 日志目录

**可选属性**：
- `queue_info.log_queue: mp.Queue` - 队列对象（启用队列模式）
- `logger.global_console_level: str` - 全局控制台级别
- `logger.global_file_level: str` - 全局文件级别
- `logger.module_levels: dict` - 模块级别配置

## 完整示例

参考演示文件：
- `src/demo/new_api_demo.py` - 基本API使用
- `src/demo/simple_queue_demo.py` - 队列模式演示 