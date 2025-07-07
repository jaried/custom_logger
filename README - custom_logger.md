# Custom Logger 使用手册

高性能自定义日志系统，支持多进程/多线程、异步文件写入、智能调用者识别。

**版本**: 1.2.0  
**作者**: Tony Xiao  
**邮箱**: tony.xiao@gmail.com  
**GitHub**: https://github.com/jaried/custom_logger.git

## 快速开始

### 基本使用

```python
from custom_logger import init_custom_logger_system, get_logger
from config_manager import get_config_manager

# 1. 初始化日志系统
config = get_config_manager()
init_custom_logger_system(config)

# 2. 获取logger实例（名字不能超过16个字符）
logger = get_logger("main")

# 3. 记录日志
logger.info("程序启动成功")
logger.warning("这是一个警告")
logger.error("发生了错误")
```

### Worker进程使用（队列模式）

当需要在独立的Worker进程中使用队列模式时，使用专用的初始化函数：

```python
from custom_logger import init_custom_logger_system_for_worker, get_logger
import pickle

def worker_function(serialized_config):
    # 反序列化配置对象
    config = pickle.loads(serialized_config)
    
    # Worker专用初始化函数（启用队列模式）
    init_custom_logger_system_for_worker(config)
    
    # 获取logger
    logger = get_logger("worker")
    logger.info("Worker进程启动")
    # 日志会通过队列传递给主进程写入文件
```

## 核心函数

### init_custom_logger_system(config_object)

初始化日志系统，必须在使用logger前调用。

**参数**:
- `config_object`: 配置对象，必须包含以下属性：
  - `paths.log_dir`: 日志文件存储目录
  - `first_start_time`: 程序首次启动时间（datetime对象）
  - `logger`: 日志配置（可选），可包含：
    - `enable_queue_mode`: 是否启用队列模式（布尔值，默认False）
    - `global_console_level`: 全局控制台日志级别
    - `global_file_level`: 全局文件日志级别

**示例**:
```python
from config_manager import get_config_manager

config = get_config_manager()
init_custom_logger_system(config)
```

### init_custom_logger_system_for_worker(serializable_config_object, worker_id=None)

Worker进程专用初始化函数，支持队列模式。

**参数**:
- `serializable_config_object`: 序列化的配置对象，包含：
  - `paths.log_dir`: 日志文件存储目录
  - `first_start_time`: 程序首次启动时间
  - `logger.enable_queue_mode`: 是否启用队列模式（可选）
  - `queue_info.log_queue`: 队列对象（队列模式时必需）
- `worker_id`: Worker进程ID（可选，用于标识日志来源）

**队列模式配置**:
```python
# 在主进程中配置队列模式
config = get_config_manager()
config.logger.enable_queue_mode = True  # 启用队列模式
config.queue_info.log_queue = queue_object  # 提供队列对象
```

### get_logger(name, console_level=None, file_level=None)

获取logger实例。

**参数**:
- `name`: logger名称（必须16个字符以内）
- `console_level`: 控制台日志级别（可选，用于设置模块特定级别）
- `file_level`: 文件日志级别（可选，用于设置模块特定级别）

**返回**:
- `CustomLogger`: 自定义日志记录器实例

**异常**:
- `RuntimeError`: 如果日志系统未初始化
- `ValueError`: 如果name超过16个字符

**示例**:
```python
# 使用全局级别
logger = get_logger("main")

# 设置模块特定级别
debug_logger = get_logger("debug", console_level="debug", file_level="detail")
worker_logger = get_logger("worker", console_level="warning", file_level="info")
```

## 日志级别和方法

### CustomLogger方法

#### 标准级别方法
```python
logger.debug(message, *args, **kwargs)      # DEBUG (10) - 调试信息
logger.info(message, *args, **kwargs)       # INFO (20) - 普通信息
logger.warning(message, *args, **kwargs)    # WARNING (30) - 警告信息
logger.error(message, *args, **kwargs)      # ERROR (40) - 错误信息
logger.critical(message, *args, **kwargs)   # CRITICAL (50) - 严重错误
logger.exception(message, *args, **kwargs)  # EXCEPTION (60) - 异常信息（自动包含堆栈）
```

#### 扩展级别方法
```python
logger.detail(message, *args, **kwargs)           # DETAIL (8) - 详细调试信息
logger.worker_summary(message, *args, **kwargs)   # W_SUMMARY (5) - Worker摘要
logger.worker_detail(message, *args, **kwargs)    # W_DETAIL (3) - Worker详细信息
```

#### 属性
```python
logger.console_level  # 获取当前控制台日志级别（数值）
logger.file_level     # 获取当前文件日志级别（数值）
logger.name          # 获取logger名称
```

#### 参数化日志
```python
# 使用位置参数
logger.info("用户 {} 登录成功", username)
logger.info("处理了 {} 条记录", count)

# 使用关键字参数
logger.info("用户 {name} 年龄 {age}", name="张三", age=25)
logger.info("处理 {count:,} 条记录", count=total_records)
```

## 使用场景

### 单线程应用

```python
from custom_logger import init_custom_logger_system, get_logger
from config_manager import get_config_manager

def main():
    # 初始化
    config = get_config_manager()
    init_custom_logger_system(config)
    
    # 使用
    logger = get_logger("main")
    logger.info("应用程序启动")
    
    # 业务逻辑
    logger.info("处理数据...")
    logger.info("应用程序结束")

if __name__ == "__main__":
    main()
```

### 多线程应用

```python
import threading
from custom_logger import init_custom_logger_system, get_logger
from config_manager import get_config_manager

def worker_function(worker_id):
    worker_logger = get_logger("worker")
    worker_logger.info(f"Worker {worker_id} 开始执行")
    # 处理逻辑...
    worker_logger.info(f"Worker {worker_id} 完成")

def main():
    # 主程序初始化
    config = get_config_manager()
    init_custom_logger_system(config)
    
    # 启动多个线程
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker_function, args=(i,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
```

### 多进程应用

#### 方式1：自动继承配置（推荐）
```python
import multiprocessing
from custom_logger import init_custom_logger_system, get_logger
from config_manager import get_config_manager

def process_worker(worker_id):
    # 子进程自动继承主进程配置
    worker_logger = get_logger("worker")
    worker_logger.info(f"进程Worker {worker_id} 启动")
    # 处理逻辑...
    worker_logger.info(f"进程Worker {worker_id} 完成")

def main():
    # 主进程初始化
    config = get_config_manager()
    init_custom_logger_system(config)
    
    # 启动多个进程
    with multiprocessing.Pool(processes=2) as pool:
        pool.map(process_worker, [1, 2])

if __name__ == "__main__":
    main()
```

#### 方式2：队列模式（适用于复杂场景）
```python
import multiprocessing
import pickle
from custom_logger import init_custom_logger_system, init_custom_logger_system_for_worker, get_logger
from config_manager import get_config_manager

def worker_with_queue(serialized_config, worker_id):
    # 反序列化配置对象
    config = pickle.loads(serialized_config)
    
    # 使用Worker专用初始化（启用队列模式）
    init_custom_logger_system_for_worker(config, worker_id=f"worker_{worker_id}")
    
    # 获取logger
    worker_logger = get_logger("worker")
    worker_logger.info(f"队列模式Worker {worker_id} 启动")
    # 处理逻辑...
    worker_logger.info(f"队列模式Worker {worker_id} 完成")

def main():
    # 主进程初始化
    config = get_config_manager()
    
    # 配置队列模式
    log_queue = multiprocessing.Queue()
    config.logger.enable_queue_mode = True  # 启用队列模式
    config.queue_info = type('QueueInfo', (), {})()  # 创建queue_info对象
    config.queue_info.log_queue = log_queue  # 设置队列对象
    
    init_custom_logger_system(config)
    
    # 序列化配置对象传递给子进程
    serialized_config = pickle.dumps(config)
    
    # 启动多个进程
    processes = []
    for i in range(2):
        process = multiprocessing.Process(
            target=worker_with_queue, 
            args=(serialized_config, i)
        )
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()

if __name__ == "__main__":
    main()
```

**队列模式说明**:
- 主进程负责文件写入，Worker进程通过队列发送日志
- 需要设置 `config.logger.enable_queue_mode = True`
- 需要提供 `config.queue_info.log_queue` 队列对象
- Worker进程使用 `init_custom_logger_system_for_worker()` 初始化

### 日志级别配置

#### 全局级别配置
```python
from config_manager import get_config_manager

config = get_config_manager()

# 设置全局日志级别
config.logger.global_console_level = "info"    # 控制台输出级别
config.logger.global_file_level = "debug"      # 文件输出级别

init_custom_logger_system(config)
```

#### 模块特定级别配置
每个模块可以通过`get_logger()`参数设置自己的特定级别：

```python
# 使用全局级别
main_logger = get_logger("main")

# 设置模块特定级别
worker_logger = get_logger("worker", console_level="warning", file_level="info")
db_logger = get_logger("database", console_level="error", file_level="debug")
debug_logger = get_logger("debug", console_level="debug", file_level="detail")

# 各模块使用自己的特定级别设置
worker_logger.info("这条信息不会在控制台显示")  # 因为worker控制台级别是warning
worker_logger.warning("这条警告会在控制台显示")  # 达到warning级别

db_logger.warning("这条警告不会在控制台显示")    # 因为database控制台级别是error
db_logger.error("这条错误会在控制台显示")        # 达到error级别
```

## 常见问题

### 日志不显示
```python
# 检查级别设置
logger = get_logger("debug", console_level="debug")
logger.debug("现在应该能看到这条消息")
```

### Logger名字长度
```python
# ✅ 推荐：使用简短有意义的名称
logger = get_logger("main")      # 简短
logger = get_logger("database")  # 适中
logger = get_logger("very_long_module_name")  # 长名称也可以正常使用
```

### 配置对象检查
```python
from config_manager import get_config_manager

config = get_config_manager()
# 检查必需属性
print(f"日志目录: {config.paths.log_dir}")
print(f"启动时间: {config.first_start_time}")

init_custom_logger_system(config)
```

## 最佳实践

### 推荐做法
```python
# ✅ 主程序初始化一次
def main():
    config = get_config_manager()
    init_custom_logger_system(config)
    logger = get_logger("main")
    logger.info("程序启动")

# ✅ 模块中直接获取logger
def worker_function():
    logger = get_logger("worker")  # 无需重新初始化
    logger.info("Worker启动")

# ✅ 使用简短有意义的名称
main_logger = get_logger("main")
auth_logger = get_logger("auth")
db_logger = get_logger("database")
```

### 避免做法
```python
# ❌ 重复初始化
def worker_function():
    init_custom_logger_system(config)  # 不要这样做

# ✅ 推荐简短名称便于阅读
logger = get_logger("auth")  # 简短清晰

# ❌ 在循环中初始化
for i in range(10):
    init_custom_logger_system(config)  # 不要这样做
```

---

Custom Logger 提供简单易用的日志记录功能，支持多进程/多线程环境，通过合理配置可以满足各种应用场景的日志需求。