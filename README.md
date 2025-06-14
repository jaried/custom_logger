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

# 2. 获取logger实例（名字不能超过8个字符）
logger = get_logger("main")

# 3. 记录日志
logger.info("程序启动成功")
logger.warning("这是一个警告")
logger.error("发生了错误")
```

### Worker进程使用

```python
from custom_logger import init_custom_logger_system_for_worker, get_logger
import pickle

def worker_function(serialized_config):
    # 反序列化配置对象
    config = pickle.loads(serialized_config)
    
    # Worker专用初始化函数
    init_custom_logger_system_for_worker(config)
    
    # 获取logger
    logger = get_logger("worker")
    logger.info("Worker进程启动")
```

## 核心函数

### init_custom_logger_system(config_object)

初始化日志系统，必须在使用logger前调用。

**参数**:
- `config_object`: 配置对象，必须包含 `paths.log_dir` 和 `first_start_time` 属性

**示例**:
```python
from config_manager import get_config_manager

config = get_config_manager()
init_custom_logger_system(config)
```

### get_logger(name, console_level=None, file_level=None)

获取logger实例。

**参数**:
- `name`: logger名称（必须8个字符以内）
- `console_level`: 控制台日志级别（可选）
- `file_level`: 文件日志级别（可选）

**示例**:
```python
# 基本使用
logger = get_logger("main")

# 指定日志级别
debug_logger = get_logger("debug", console_level="debug", file_level="detail")
```

## 日志级别

### 标准级别
```python
logger.debug("调试信息")      # DEBUG
logger.info("普通信息")       # INFO  
logger.warning("警告信息")    # WARNING
logger.error("错误信息")      # ERROR
logger.critical("严重错误")   # CRITICAL
logger.exception("异常信息")  # 自动包含堆栈信息
```

### 扩展级别
```python
logger.detail("详细调试信息")           # DETAIL
logger.worker_summary("Worker摘要")     # W_SUMMARY
logger.worker_detail("Worker详细信息")  # W_DETAIL
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

```python
import multiprocessing
from custom_logger import init_custom_logger_system, get_logger
from config_manager import get_config_manager

def process_worker(worker_id):
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

## 常见问题

### 日志不显示
```python
# 检查级别设置
logger = get_logger("debug", console_level="debug")
logger.debug("现在应该能看到这条消息")
```

### Logger名字长度限制
```python
# ✅ 正确：8字符以内
logger = get_logger("main")      # 4字符
logger = get_logger("database")  # 8字符

# ❌ 错误：超过8字符会抛出异常
logger = get_logger("very_long_module_name")  # 会抛出ValueError
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

# ❌ 名字太长
logger = get_logger("authentication_module")  # 超过8字符

# ❌ 在循环中初始化
for i in range(10):
    init_custom_logger_system(config)  # 不要这样做
```

---

Custom Logger 提供简单易用的日志记录功能，支持多进程/多线程环境，通过合理配置可以满足各种应用场景的日志需求。