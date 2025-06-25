# Custom Logger 使用手册

高性能自定义日志系统，支持多进程/多线程、异步文件写入、智能调用者识别和灵活配置管理。

**版本**: 1.1.0  
**作者**: Tony Xiao  
**邮箱**: tony.xiao@gmail.com  
**GitHub**: https://github.com/jaried/custom_logger.git

## 🚀 最新更新 (v1.1.1)

### 新增功能
- ✅ **config_object初始化支持**: 支持直接传入配置对象进行初始化
- ✅ **智能冲突检测**: first_start_time参数优先级管理和冲突检测
- ✅ **多进程配置隔离**: 解决多进程环境下配置加载问题
- ✅ **config_manager集成优化**: 增强与外部配置管理器的集成稳定性
- ✅ **完整架构文档**: 新增详细的架构设计和需求变更文档
- ✅ **增强测试覆盖**: 18个全面测试用例确保功能稳定性

### 架构优化
- 🏗️ **分层架构设计**: 应用层、接口层、核心层、支撑层清晰分离
- 🔧 **配置管理优化**: 支持多配置源，智能优先级处理
- 🚀 **多进程性能优化**: 配置预读机制，减少重复I/O操作
- 📊 **可视化文档**: 使用Mermaid图表展示系统架构和数据流

### Bug修复
- 🐛 **多进程配置加载**: 修复子进程无法正确加载指定配置文件的问题
- 🐛 **config_manager兼容性**: 解决config_manager自动保存覆盖原始配置的问题
- 🐛 **配置格式处理**: 正确处理config_manager的包装格式（__data__字段）

## 目录

1. [快速开始](#快速开始)
2. [核心函数详解](#核心函数详解)
3. [配置管理](#配置管理)
4. [使用场景](#使用场景)
5. [最佳实践](#最佳实践)
6. [架构设计](#架构设计)
7. [故障排除](#故障排除)
8. [更新日志](#更新日志)

## 快速开始

### 基本使用流程

```python
from custom_logger import init_custom_logger_system, get_logger
from datetime import datetime

# 1. 主程序初始化日志系统（只需调用一次）
start_time = datetime.now()
init_custom_logger_system(first_start_time=start_time)

# 2. 获取logger实例
logger = get_logger("main")

# 3. 记录日志
logger.info("程序启动成功")
logger.warning("这是一个警告")
logger.error("发生了错误")

# 4. 程序结束时会自动清理（也可手动调用）
# tear_down_custom_logger_system()
```

### 30秒快速体验

```python
from custom_logger import init_custom_logger_system, get_logger

# 初始化（使用默认配置）
init_custom_logger_system()

# 获取logger并记录日志
logger = get_logger("demo")
logger.info("Hello, Custom Logger!")
logger.warning("这是一条警告消息")
logger.error("这是一条错误消息")
```

## 核心函数详解

### init_custom_logger_system()

**作用**: 初始化整个日志系统，是使用Custom Logger的必要前提。

**函数签名**:
```python
def init_custom_logger_system(
    config_path: Optional[str] = None,
    first_start_time: Optional[datetime] = None,
    config_object: Optional[Any] = None
) -> None:
```

**参数说明**:
- `config_path`: 配置文件路径（可选）
  - 默认值: `src/config/config.yaml`
  - 支持相对路径和绝对路径
  - 如果文件不存在，会使用默认配置
- `first_start_time`: 首次启动时间（可选）
  - 用于日志目录创建和运行时间计算
  - 主程序建议设置此参数
  - 子进程/其他模块不设置，会从配置文件读取
- `config_object`: 配置对象（可选，v1.1.0新增）
  - 直接传入配置对象，无需配置文件
  - 支持字典或对象格式
  - 与config_path互斥，config_object优先级更高

**使用场景**:

#### 1. 主程序启动（推荐方式）
```python
from datetime import datetime
from custom_logger import init_custom_logger_system

# 设置启动时间，确保所有模块使用统一的时间基准
start_time = datetime.now()
init_custom_logger_system(first_start_time=start_time)
```

#### 2. 使用自定义配置文件
```python
# 使用项目特定的配置文件
init_custom_logger_system(
    config_path="my_project/config/logging.yaml",
    first_start_time=datetime.now()
)
```

#### 3. 子进程/Worker中使用
```python
# 子进程中无需设置first_start_time，会自动从配置继承
init_custom_logger_system()
```

#### 4. 使用配置对象（v1.1.0新增）
```python
# 方式1：使用字典配置
config_dict = {
    'project_name': 'my_project',
    'base_dir': 'd:/logs',
    'logger': {
        'global_console_level': 'debug',
        'global_file_level': 'info'
    }
}
init_custom_logger_system(
    config_object=config_dict,
    first_start_time=datetime.now()
)

# 方式2：使用对象配置
class Config:
    def __init__(self):
        self.project_name = 'my_project'
        self.base_dir = 'd:/logs'
        self.logger = {
            'global_console_level': 'info',
            'global_file_level': 'debug'
        }

config_obj = Config()
init_custom_logger_system(config_object=config_obj)

# 方式3：从外部系统获取配置
external_config = get_config_from_database()  # 假设从数据库获取
init_custom_logger_system(
    config_object=external_config,
    first_start_time=datetime.now()
)
```

#### 5. 测试环境使用
```python
import tempfile

# 使用临时配置文件进行测试
with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp_file:
    tmp_file.write("project_name: test\nlogger:\n  global_console_level: debug")
    tmp_file.flush()
    init_custom_logger_system(config_path=tmp_file.name)

# 或者使用配置对象进行测试（推荐）
test_config = {
    'project_name': 'test_project',
    'base_dir': './test_logs',
    'logger': {'global_console_level': 'debug'}
}
init_custom_logger_system(config_object=test_config)
```

**重要提示**:
- ✅ **主程序中必须调用一次** - 作为整个日志系统的入口点
- ✅ **多进程安全** - 子进程会自动继承主进程的配置
- ✅ **幂等性** - 重复调用不会造成问题
- ❌ **不要在循环中调用** - 这是一次性初始化函数

### get_logger()

**作用**: 获取logger实例，用于实际的日志记录操作。

**函数签名**:
```python
def get_logger(
    name: str,
    console_level: Optional[str] = None,
    file_level: Optional[str] = None
) -> CustomLogger:
```

**参数说明**:
- `name`: logger名称
  - **必须8个字符以内**，因为日志输出时只显示前8位字符
  - 用于标识不同模块或组件
  - 示例: "main", "worker", "db", "api", "auth", "cache"
- `console_level`: 控制台日志级别（可选）
  - **动态覆盖配置文件设置**，仅对当前logger实例生效
  - 可选值: "debug", "info", "warning", "error", "critical"
  - 扩展级别: "detail", "w_summary", "w_detail"
- `file_level`: 文件日志级别（可选）
  - **动态覆盖配置文件设置**，仅对当前logger实例生效
  - 同console_level的可选值

**使用场景**:

#### 1. 基本使用（推荐）
```python
# 使用配置文件中的默认级别
logger = get_logger("main")
logger.info("程序启动")
```

#### 2. 模块化使用
```python
# 不同模块使用不同的logger名称（必须8字符以内）
auth_logger = get_logger("auth")      # 认证模块 (4字符)
db_logger = get_logger("database")    # 数据库模块 (8字符)
api_logger = get_logger("api")        # API模块 (3字符)
cache_logger = get_logger("cache")    # 缓存模块 (5字符)

auth_logger.info("用户登录成功")
db_logger.debug("执行SQL查询")
api_logger.warning("API响应超时")
```

#### 3. 临时调整日志级别（动态覆盖）
```python
# 使用配置文件中的默认级别
default_logger = get_logger("main")

# 临时启用详细日志用于调试（覆盖配置文件设置）
debug_logger = get_logger("debug", console_level="debug", file_level="detail")
debug_logger.debug("这条详细调试信息会显示")

# 只显示重要信息（覆盖配置文件设置）
important_logger = get_logger("critical", console_level="warning", file_level="error")
important_logger.info("这条普通信息不会显示")  # 被过滤
important_logger.warning("这条警告会显示")      # 显示

# 同一模块名，不同级别设置
logger1 = get_logger("module", console_level="debug")    # 显示debug及以上
logger2 = get_logger("module", console_level="error")    # 只显示error及以上
# 注意：这是两个不同的logger实例，有各自的级别设置
```

#### 4. Worker专用级别
```python
# Worker线程使用专门的日志级别
worker_logger = get_logger("worker", console_level="w_summary", file_level="w_detail")
worker_logger.worker_summary("Worker开始执行任务")
worker_logger.worker_detail("Worker详细执行步骤")
```

**logger实例方法**:

#### 标准日志级别
```python
logger.debug("调试信息")      # DEBUG (10)
logger.info("普通信息")       # INFO (20)
logger.warning("警告信息")    # WARNING (30)
logger.error("错误信息")      # ERROR (40)
logger.critical("严重错误")   # CRITICAL (50)
logger.exception("异常信息")  # EXCEPTION (60) - 自动包含堆栈信息
```

#### 扩展日志级别
```python
logger.detail("详细调试信息")           # DETAIL (8)
logger.worker_summary("Worker摘要")     # W_SUMMARY (5)
logger.worker_detail("Worker详细信息")  # W_DETAIL (3)
```

#### 带参数的日志
```python
# 推荐使用{}占位符
logger.info("用户 {} 登录成功", username)
logger.info("处理了 {:,} 条记录", record_count)
logger.info("用户 {name} 年龄 {age}", name="张三", age=25)
```

## 配置管理

### 默认配置文件结构

配置文件位置: `src/config/config.yaml`

```yaml
# 项目基本信息
project_name: "my_project"
experiment_name: "default"
first_start_time: null  # 自动生成

# 日志基础目录
base_dir: "d:/logs"

# 日志配置
logger:
  # 全局默认级别
  global_console_level: "info"
  global_file_level: "debug"
  
  # 当前会话目录（自动生成）
  current_session_dir: null
  
  # 调用链显示控制
  show_call_chain: false
  show_debug_call_stack: false
  
  # 模块特定配置
  module_levels:
    worker:
      console_level: "w_summary"
      file_level: "w_detail"
    debug_module:
      console_level: "debug"
      file_level: "detail"
```

### 日志文件组织结构

```
{base_dir}/
├── {project_name}/
│   ├── {experiment_name}/
│   │   ├── logs/
│   │   │   ├── {YYYYMMDD}/          # 按日期分组
│   │   │   │   ├── {HHMMSS}/        # 按启动时间分组
│   │   │   │   │   ├── full.log     # 完整日志
│   │   │   │   │   └── warning.log  # 警告日志
```

示例: `d:/logs/my_project/default/logs/20241201/143022/full.log`

### 配置文件自动备份

```
src/config/
├── config.yaml                      # 主配置文件
└── backup/
    └── {YYYYMMDD}/
        └── {HHMMSS}/
            └── config_{YYYYMMDD}_{HHMMSS}.yaml  # 备份配置
```

## 使用场景

### 1. 单线程应用

```python
from custom_logger import init_custom_logger_system, get_logger
from datetime import datetime

def main():
    # 初始化日志系统
    init_custom_logger_system(first_start_time=datetime.now())
    
    # 获取logger
    logger = get_logger("main")
    logger.info("应用程序启动")
    
    # 业务逻辑
    process_data(logger)
    
    logger.info("应用程序结束")

def process_data(logger):
    logger.info("开始处理数据")
    # 处理逻辑...
    logger.info("数据处理完成")

if __name__ == "__main__":
    main()
```

### 2. 多线程应用

```python
import threading
from custom_logger import init_custom_logger_system, get_logger
from datetime import datetime

def worker_function(worker_id):
    # Worker中直接获取logger，无需重新初始化
    worker_logger = get_logger("worker", console_level="w_summary")
    
    worker_logger.worker_summary(f"Worker {worker_id} 开始执行")
    
    for i in range(100):
        worker_logger.worker_detail(f"Worker {worker_id} 处理任务 {i+1}/100")
        # 处理逻辑...
    
    worker_logger.worker_summary(f"Worker {worker_id} 完成所有任务")

def main():
    # 主程序初始化
    init_custom_logger_system(first_start_time=datetime.now())
    main_logger = get_logger("main")
    
    main_logger.info("启动多线程任务")
    
    # 启动多个Worker线程
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker_function, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    main_logger.info("所有线程任务完成")

if __name__ == "__main__":
    main()
```

### 3. 多进程应用

```python
import multiprocessing
from custom_logger import init_custom_logger_system, get_logger
from datetime import datetime

def process_worker(worker_id):
    """进程Worker函数 - 必须在模块级别定义"""
    # 进程中获取logger（会自动继承主进程配置）
    worker_logger = get_logger("process_worker")
    
    worker_logger.info(f"进程Worker {worker_id} 启动")
    
    for i in range(50):
        worker_logger.debug(f"Process-{worker_id} 处理步骤 {i+1}")
        # 处理逻辑...
    
    worker_logger.info(f"进程Worker {worker_id} 完成")
    return f"Process-{worker_id} finished"

def main():
    # 主进程初始化
    init_custom_logger_system(first_start_time=datetime.now())
    main_logger = get_logger("main")
    
    main_logger.info("启动多进程任务")
    
    # 启动多个进程
    with multiprocessing.Pool(processes=2) as pool:
        results = pool.map(process_worker, [1, 2])
    
    main_logger.info(f"所有进程完成: {results}")

if __name__ == "__main__":
    main()
```

#### 4. 动态级别调整实战示例

```python
from custom_logger import init_custom_logger_system, get_logger

def main():
    # 初始化日志系统
    init_custom_logger_system()
    
    # 1. 普通模块使用默认配置
    normal_logger = get_logger("normal")
    normal_logger.info("使用配置文件中的默认级别")
    
    # 2. 调试模块需要详细信息
    debug_logger = get_logger("debug", console_level="debug", file_level="detail")
    debug_logger.debug("这是调试信息")  # 会显示
    debug_logger.detail("这是详细信息")  # 会保存到文件
    
    # 3. 生产模块只要重要信息
    prod_logger = get_logger("prod", console_level="warning", file_level="error")
    prod_logger.info("这条不会显示")     # 被过滤
    prod_logger.warning("这条会显示")   # 显示
    prod_logger.error("这条会保存")     # 显示并保存
    
    # 4. Worker模块使用专用级别
    worker_logger = get_logger("worker", console_level="w_summary", file_level="w_detail")
    worker_logger.worker_summary("Worker任务开始")  # 显示
    worker_logger.worker_detail("Worker详细步骤")   # 保存到文件
    
    # 5. 检查当前级别
    print(f"调试模块控制台级别: {debug_logger.console_level}")  # 输出: 10 (DEBUG)
    print(f"生产模块控制台级别: {prod_logger.console_level}")   # 输出: 30 (WARNING)

if __name__ == "__main__":
    main()
```

```python
from custom_logger import init_custom_logger_system, get_logger

def main():
    init_custom_logger_system()
    logger = get_logger("main")
    
    try:
        risky_operation()
    except ValueError as e:
        # 已知异常使用error
        logger.error(f"数值错误: {e}")
    except Exception:
        # 未知异常使用exception（自动包含堆栈信息）
        logger.exception("发生未知错误")

def risky_operation():
    # 可能抛出异常的操作
    result = 10 / 0  # ZeroDivisionError

if __name__ == "__main__":
    main()
```

### 5. 异常处理

```python
from custom_logger import init_custom_logger_system, get_logger

def main():
    init_custom_logger_system()
    
    # 不同级别的logger
    debug_logger = get_logger("debug", console_level="debug", file_level="debug")
    production_logger = get_logger("prod", console_level="warning", file_level="error")
    
    # 测试消息
    debug_logger.debug("这条会显示")      # 显示到控制台
    debug_logger.info("这条会显示")       # 显示到控制台
    debug_logger.warning("这条会显示")    # 显示到控制台
    
    production_logger.debug("这条不会显示")    # 被过滤
    production_logger.info("这条不会显示")     # 被过滤
    production_logger.warning("这条会显示")    # 显示到控制台
    production_logger.error("这条会显示并保存") # 显示到控制台并保存到文件

if __name__ == "__main__":
    main()
```

### 6. 级别过滤示例

## 最佳实践

```python
# ✅ 推荐：主程序初始化
def main():
    from datetime import datetime
    init_custom_logger_system(first_start_time=datetime.now())
    logger = get_logger("main")
    logger.info("程序启动")
    
    # 其他模块直接获取logger
    worker_main()

def worker_main():
    # ✅ Worker中直接获取，无需重新初始化
    logger = get_logger("worker")
    logger.info("Worker启动")

# ❌ 避免：重复初始化
def worker_function():
    init_custom_logger_system()  # 不要这样做
```

### 1. 初始化模式

**重要提示**: 日志输出格式中模块名只显示8位字符，因此logger名称必须控制在8个字符以内。

```python
# ✅ 推荐：8字符以内的简短有意义名称
main_logger = get_logger("main")      # 主程序 (4字符)
auth_logger = get_logger("auth")      # 认证模块 (4字符)
db_logger = get_logger("database")    # 数据库模块 (8字符)
api_logger = get_logger("api")        # API模块 (3字符)
worker_logger = get_logger("worker")  # Worker线程 (6字符)
cache_logger = get_logger("cache")    # 缓存模块 (5字符)
proc_logger = get_logger("proc")      # 处理器 (4字符)
net_logger = get_logger("network")    # 网络模块 (7字符)

# ❌ 避免：超过8字符的名称（会被截断显示）
logger = get_logger("authentication_module")  # 太长，只显示"authenti"
logger = get_logger("data_processing_engine")  # 太长，只显示"data_pro"

# 📋 常用模块名称建议（8字符以内）：
# main     - 主程序
# auth     - 认证
# database - 数据库  
# api      - API接口
# worker   - Worker线程
# cache    - 缓存
# config   - 配置
# network  - 网络
# file     - 文件操作
# timer    - 定时器
# queue    - 队列
# proc     - 处理器
# monitor  - 监控
# sched    - 调度器
```

### 3. 级别选择指南

```python
# 根据用途选择合适级别
logger.debug("变量值: {}", value)           # 开发调试
logger.info("用户登录: {}", username)       # 重要事件
logger.warning("配置缺失，使用默认值")        # 潜在问题
logger.error("数据库连接失败")               # 错误但可恢复
logger.critical("内存不足，程序即将退出")     # 严重错误
logger.exception("未处理的异常")             # 异常（自动包含堆栈）

# Worker专用级别
worker_logger.worker_summary("任务开始")     # Worker重要事件
worker_logger.worker_detail("处理步骤1")     # Worker详细信息
```

### 4. 参数化日志

```python
# ✅ 推荐：使用参数化
logger.info("用户 {} 执行操作 {}", username, action)
logger.info("处理 {count:,} 条记录", count=total_records)

# ❌ 避免：字符串拼接
logger.info("用户 " + username + " 执行操作")  # 性能差
logger.info(f"用户 {username} 执行操作")      # 总是执行格式化
```

### 5. 动态级别设置

`get_logger`支持在运行时动态设置日志级别，提供了三种级别配置方式：

#### 配置优先级（从高到低）：
1. **函数参数级别** - `get_logger(name, console_level="debug")`
2. **配置文件模块级别** - `config.yaml` 中的 `module_levels`
3. **配置文件全局级别** - `config.yaml` 中的 `global_console_level`

```python
# 1. 使用配置文件中的默认设置
logger = get_logger("module")

# 2. 动态覆盖控制台级别
logger = get_logger("module", console_level="debug")

# 3. 动态覆盖文件级别  
logger = get_logger("module", file_level="error")

# 4. 同时覆盖控制台和文件级别
logger = get_logger("module", console_level="warning", file_level="critical")

# 5. 查看当前logger的级别设置
print(f"控制台级别: {logger.console_level}")  # 返回数值
print(f"文件级别: {logger.file_level}")      # 返回数值

# 6. 不同实例可以有不同的级别
debug_instance = get_logger("worker", console_level="debug")
prod_instance = get_logger("worker", console_level="error")
# 这是两个独立的logger实例，级别设置互不影响
```

#### 级别数值对照表：
```
W_DETAIL = 3      # Worker详细级别
W_SUMMARY = 5     # Worker摘要级别  
DETAIL = 8        # 详细调试级别
DEBUG = 10        # 调试级别
INFO = 20         # 信息级别
WARNING = 30      # 警告级别
ERROR = 40        # 错误级别
CRITICAL = 50     # 严重错误级别
EXCEPTION = 60    # 异常级别
```

```python
# ✅ 推荐：使用项目特定配置
init_custom_logger_system(
    config_path="my_project/config/logging.yaml",
    first_start_time=datetime.now()
)

# ✅ 推荐：使用配置对象（v1.1.0新增）
config = {
    'project_name': 'my_project',
    'logger': {
        'global_console_level': 'info',
        'module_levels': {
            'worker': {
                'console_level': 'w_summary',
                'file_level': 'w_detail'
            }
        }
    }
}
init_custom_logger_system(config_object=config)
```

### 6. 配置管理

```python
# ✅ 推荐：使用exception方法记录异常
try:
    risky_operation()
except Exception:
    logger.exception("操作失败")  # 自动包含堆栈信息

# ✅ 推荐：已知异常使用error
try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    logger.error("JSON解析失败: {}", str(e))  # 不需要堆栈
```

### 7. 错误处理

### 常见问题

#### 1. 日志不显示
```python
# 检查级别设置
logger = get_logger("debug")
print(f"控制台级别: {logger.console_level}")
print(f"文件级别: {logger.file_level}")

# 临时启用详细日志
debug_logger = get_logger("debug", console_level="debug", file_level="debug")
debug_logger.debug("现在应该能看到这条消息")
```

#### 2. 找不到配置文件
```python
# 确保配置文件路径正确
init_custom_logger_system(config_path="src/config/config.yaml")

# 或使用绝对路径
import os
config_path = os.path.abspath("src/config/config.yaml")
init_custom_logger_system(config_path=config_path)
```

#### 3. 多进程日志丢失
```python
# 确保进程函数在模块级别定义
def process_worker(worker_id):  # ✅ 模块级别
    logger = get_logger("worker")
    # ...

# ❌ 避免在函数内部定义进程函数
def main():
    def worker(id):  # 这样定义会导致序列化问题
        pass
```

#### 4. 时间基准不一致
```python
# ✅ 主程序设置统一的启动时间
start_time = datetime.now()
init_custom_logger_system(first_start_time=start_time)

# ✅ 子进程无需设置，会自动继承
# 在子进程中：
init_custom_logger_system()  # 不传first_start_time参数
```

#### 5. 多进程配置加载问题 (v1.1.1修复)
```python
# ✅ 问题已修复：子进程现在能正确加载指定的配置文件
# 如果仍遇到问题，可以启用调试模式查看详细信息
import os
os.environ['CUSTOM_LOGGER_DEBUG'] = '1'

# 创建测试配置
test_config = {
    'project_name': 'test_project',
    'logger': {
        'global_console_level': 'debug'
    }
}

# 使用配置对象避免文件相关问题
init_custom_logger_system(config_object=test_config)
```

#### 6. config_manager集成问题
```python
# ✅ 问题已修复：系统现在能正确处理config_manager的包装格式
# 如果遇到配置不一致，系统会自动检测并修复

# 检查配置是否正确加载
from custom_logger.config import get_config_manager
cfg = get_config_manager()
print(f"当前项目名: {getattr(cfg, 'project_name', 'NOT_SET')}")
```

## 架构设计

### 系统架构概览

Custom Logger 采用分层架构设计，确保高性能、可扩展性和易维护性：

```
┌─────────────────────────────────────────────────────────────┐
│                    应用层 (Application Layer)                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   主程序调用     │  │   Worker进程     │  │   测试用例   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    接口层 (Interface Layer)                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              manager.py (系统管理接口)                   │ │
│  │  init_custom_logger_system() / get_logger()            │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    核心层 (Core Layer)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ logger.py    │  │ config.py    │  │ writer.py        │   │
│  │ (日志记录器)  │  │ (配置管理)   │  │ (异步写入器)      │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   支撑层 (Support Layer)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ types.py     │  │ config_mgr   │  │ 文件系统         │   │
│  │ (类型定义)    │  │ (外部依赖)   │  │ (日志存储)        │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件

#### 1. Manager (管理器)
- **职责**: 系统初始化、生命周期管理、logger实例创建
- **关键功能**: 
  - 系统初始化和清理
  - 配置对象处理和验证
  - Logger实例工厂

#### 2. Config (配置管理)
- **职责**: 配置加载、验证、管理
- **关键功能**:
  - 多种配置源支持（文件、对象）
  - 配置冲突检测和解决
  - 会话目录管理

#### 3. Logger (日志记录器)
- **职责**: 日志记录、格式化、级别控制
- **关键功能**:
  - 多级别日志记录
  - 调用链追踪
  - 异步写入调度

#### 4. Writer (异步写入器)
- **职责**: 异步日志写入、文件管理
- **关键功能**:
  - 异步队列处理
  - 文件轮转和管理
  - 性能优化

### 配置对象处理流程 (v1.1.0)

```
传入config_object → 检查first_start_time冲突 → 复制配置属性 → 创建会话目录 → 初始化完成
                                ↓
                    ┌─────────────────────────────┐
                    │     冲突检测逻辑             │
                    │  ┌─────────────────────────┐ │
                    │  │ 两者都有值且不同 → 抛错  │ │
                    │  │ 两者都有值且相同 → 使用  │ │
                    │  │ 只有参数值 → 使用参数    │ │
                    │  │ 只有对象值 → 使用对象    │ │
                    │  │ 都没有值 → 使用当前时间  │ │
                    │  └─────────────────────────┘ │
                    └─────────────────────────────────┘
```

### 关键设计决策

#### 1. 配置优先级管理
- **决策**: 参数 > 配置对象 > 配置文件 > 默认值
- **理由**: 提供灵活的配置覆盖机制
- **实现**: 智能冲突检测，相同值不冲突

#### 2. 异步写入设计
- **决策**: 使用异步队列处理日志写入
- **理由**: 提高性能，避免阻塞主线程
- **实现**: 基于asyncio的队列机制

#### 3. 模块化设计
- **决策**: 每个模块职责单一明确
- **理由**: 提高可维护性和可测试性
- **实现**: 清晰的接口定义和依赖关系

### 性能特性

- **异步写入**: 日志写入不阻塞主线程
- **智能缓存**: 减少重复的格式化操作
- **级别过滤**: 在记录前进行级别检查
- **批量处理**: 优化文件I/O操作

### 扩展性设计

- **插件机制**: 支持自定义日志处理器
- **配置扩展**: 支持新的配置源类型
- **输出扩展**: 支持多种输出目标
- **跨平台**: 支持Windows、Linux、macOS

## 故障排除

```python
# 启用调试输出（仅开发时使用）
import os
os.environ['CUSTOM_LOGGER_DEBUG'] = '1'

# 在配置文件中启用调用链显示
# logger:
#   show_call_chain: true
#   show_debug_call_stack: true
```

### 调试模式

```python
# 1. 使用合适的日志级别避免不必要的格式化
logger = get_logger("performance", console_level="warning")  # 只显示重要信息

# 2. 对于高频日志，考虑使用worker级别
worker_logger = get_logger("worker", console_level="w_summary", file_level="w_detail")

# 3. 避免在循环中进行复杂的字符串格式化
for i in range(1000):
    # ❌ 避免：复杂格式化
    logger.debug(f"处理第 {i:,} 项，数据: {complex_data}")
    
    # ✅ 推荐：简单格式化或条件日志
    if i % 100 == 0:
        logger.info("处理进度: {}/{}", i, 1000)
```

### 性能优化

Custom Logger 是一个功能强大且易用的日志系统，核心使用流程：

1. **初始化**: 使用 `init_custom_logger_system()` 初始化系统
2. **获取Logger**: 使用 `get_logger()` 获取logger实例
3. **记录日志**: 使用logger的各种方法记录日志
4. **自动清理**: 程序结束时自动清理资源

通过合理的配置和最佳实践，可以构建高效、可维护的日志系统，满足从简单脚本到复杂多进程应用的各种需求。

## 更新日志

### v1.1.1 (2025-06-06)

#### 🐛 重要Bug修复
- **多进程配置加载**: 修复子进程无法正确加载指定配置文件的关键问题
- **config_manager兼容性**: 解决config_manager自动保存覆盖原始配置的问题
- **配置格式处理**: 正确处理config_manager的包装格式（__data__字段）

#### 🚀 性能优化
- **配置预读机制**: 在初始化config_manager之前预读原始配置，避免被覆盖
- **智能配置检测**: 自动检测配置不一致并强制修复
- **多进程性能**: 减少重复I/O操作，优化进程间配置传递

#### 🔧 技术改进
- **原始配置保护**: 防止config_manager自动保存覆盖测试配置
- **配置内容比较**: 智能比较配置内容，确保正确性
- **调试输出增强**: 添加详细的调试信息帮助问题诊断

#### 📊 架构文档更新
- **多进程配置流程图**: 新增多进程配置加载的时序图
- **配置隔离设计**: 详细说明多进程环境下的配置隔离机制
- **Bug修复记录**: 完整记录问题发现、分析和解决过程

#### 🧪 测试稳定性
- **多进程测试**: 修复test_tc0015_multiprocess_config.py中的失败测试
- **配置隔离验证**: 确保不同进程间配置正确隔离
- **回归测试**: 验证修复不影响现有功能

### v1.1.0 (2025-06-06)

#### 🚀 新增功能
- **config_object初始化支持**: 新增`config_object`参数，支持直接传入配置对象进行初始化
- **智能冲突检测**: 实现`first_start_time`参数的优先级管理和冲突检测机制
- **完整架构文档**: 新增详细的架构设计文档和需求变更文档
- **增强测试覆盖**: 新增18个全面测试用例，确保功能稳定性

#### 🏗️ 架构优化
- **分层架构设计**: 重新设计为应用层、接口层、核心层、支撑层的清晰分离
- **配置管理优化**: 支持多配置源（文件、对象、参数），智能优先级处理
- **模块化改进**: 优化模块间依赖关系，提高可维护性

#### 🔧 技术改进
- **配置优先级规则**: 参数 > 配置对象 > 配置文件 > 默认值
- **冲突检测逻辑**: 只有当两个`first_start_time`值不同时才抛出错误
- **会话目录管理**: 自动创建和管理会话目录
- **异常处理优化**: 改进异常处理逻辑，避免配置被意外覆盖

#### 📊 可视化文档
- **系统架构图**: 使用Mermaid图表展示系统架构
- **配置处理流程图**: 可视化配置对象处理流程
- **初始化时序图**: 展示系统初始化的完整流程

#### 🧪 测试增强
- **基本功能测试**: config_object传递和初始化功能
- **冲突检测测试**: first_start_time冲突检测（不同值抛错，相同值不冲突）
- **边界情况测试**: 缺少属性、None值等各种边界情况
- **格式支持测试**: logger配置的字典和对象格式支持
- **完整流程测试**: 端到端的初始化流程测试

#### 📝 文档更新
- **README更新**: 新增config_object使用示例和架构设计章节
- **需求变更文档**: 详细记录需求变更的完整信息
- **架构设计文档**: 完整的系统架构设计和技术决策文档

#### ✅ 向后兼容性
- 完全向后兼容，不影响现有的配置文件加载方式
- 现有代码无需修改即可继续使用

### v1.0.0 (2025-06-01)

#### 🎉 初始版本
- **基础日志功能**: 支持多级别日志记录
- **异步写入**: 高性能异步日志写入机制
- **多进程支持**: 完整的多进程/多线程支持
- **配置管理**: 基于YAML的配置文件管理
- **智能调用者识别**: 自动识别日志调用者信息
- **会话管理**: 基于时间的会话目录管理

---

## 项目信息

- **项目名称**: Custom Logger
- **版本**: 1.1.1
- **作者**: Tony Xiao
- **联系方式**: tony.xiao@gmail.com
- **GitHub仓库**: https://github.com/jaried/custom_logger.git
- **许可证**: MIT License

## 贡献与支持

如果您在使用过程中遇到问题或有改进建议，欢迎：

1. **提交Issue**: 在GitHub仓库中提交问题报告
2. **贡献代码**: 提交Pull Request来改进项目
3. **功能建议**: 通过Issue或邮件提出新功能建议
4. **文档完善**: 帮助改进文档和示例

### 快速链接

- 📚 [项目文档](https://github.com/jaried/custom_logger.git)
- 🐛 [问题报告](https://github.com/jaried/custom_logger.git/issues)
- 💡 [功能请求](https://github.com/jaried/custom_logger.git/issues)
- 📧 [联系作者](mailto:tony.xiao@gmail.com)