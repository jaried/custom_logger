# 自定义Logger需求文档

## 0. 包结构和安装

### 0.1 包结构

```
项目根目录/
├── src/
│   ├── custom_logger/
│   │   ├── __init__.py
│   │   ├── types.py
│   │   ├── config.py
│   │   ├── formatter.py
│   │   ├── writer.py
│   │   ├── logger.py
│   │   └── manager.py
│   ├── config/
│   │   └── custom_logger.yaml
│   └── demo/
│       └── demo_custom_logger.py
├── tests/
│   └── test_custom_logger/
│       ├── test_tc0001_types.py
│       ├── test_tc0002_config.py
│       ├── test_tc0003_formatter.py
│       ├── test_tc0004_writer.py
│       ├── test_tc0005_logger.py
│       ├── test_tc0006_manager.py
│       ├── test_tc0007_basic_integration.py
│       ├── test_tc0008_advanced_integration.py
│       ├── test_tc0009_performance_integration.py
│       └── test_tc0010_minimal_integration.py
├── setup.py
├── pyproject.toml
├── pytest.ini
├── requirements.txt
├── README.md
└── MANIFEST.in
```

### 0.2 包管理

- **包名**：`custom_logger`
- **导入路径**：`from custom_logger import ...`
- **安装方式**：`pip install -e .`
- **依赖管理**：config_manager（不需要版本号）

### 0.3 配置文件

- **位置**：`src/config/custom_logger.yaml`
- **访问方式**：支持通过不带src的路径导入
- **测试环境**：使用实际配置文件，但隔离测试数据

## 1. 功能需求

### 1.1 日志级别体系

- **标准级别**：DEBUG (10) > INFO (20) > WARNING (30) > ERROR (40) > CRITICAL (50) > EXCEPTION (60)
- **扩展级别**：DEBUG (10) > DETAIL (8) > W_SUMMARY (5) > W_DETAIL (3)
- **使用场景**：
  - 非worker：使用 DEBUG 和 DETAIL
  - worker：使用 W_SUMMARY 和 W_DETAIL
- **方法名称**：
  - 扩展级别对应方法：`detail()`, `worker_summary()`, `worker_detail()`

### 1.2 输出机制

- **控制台输出**：实时输出，支持Windows CMD和PyCharm颜色
  - INFO及以下：无颜色
  - WARNING以上：彩色输出，不同级别使用不同颜色
- **文件输出**：异步批量写入
  - 全量日志文件：记录所有级别
  - 错误日志文件：仅记录ERROR及以上级别

### 1.3 日志格式

```
[{pid:>6} | {模块名:<8} : {行号:>4}] {时间戳} - {运行时长} - {级别:<9} - {消息}
```

### 1.4 颜色方案

- **INFO及以下**：无颜色（普通文本）
- **WARNING**：黄色（CMD）/ 亮黄色（PyCharm）
- **ERROR**：红色（CMD）/ 亮红色（PyCharm）  
- **CRITICAL**：洋红色（CMD）/ 亮洋红色（PyCharm）
- **EXCEPTION**：亮红色（CMD）/ 粗体红色（PyCharm）

### 1.5 文件路径结构

```
d:\logs\{debug模式时加debug层}\{project_name}\{experiment_name}\logs\{启动日期yyyymmdd}\{启动时间hhmmss}\
```

## 2. 配置管理

### 2.1 使用config_manager

- 集成项目统一的配置管理系统
- 配置文件保存到：`src/config/custom_logger.yaml`
- 持久化配置，防止多进程时丢失

### 2.2 配置项

- `project_name`：项目名称
- `experiment_name`：实验名称  
- `global_console_level`：全局控制台日志级别
- `global_file_level`：全局文件日志级别
- `module_levels`：模块特定级别配置（可选）
- `first_start_time`：第一个启动模块的时间戳（自动保存）
- `base_log_dir`：基础日志目录（默认"d:/logs"）

### 2.3 debug模式判断

```python
from is_debug import is_debug
```

使用现有的`is_debug()`函数判断调试模式

### 2.4 系统初始化

- **只有主程序需要调用**：`init_custom_logger_system()`
- 使用config_manager管理配置
- 自动创建必要的目录结构
- 其他进程/worker直接使用`get_logger()`

## 3. 技术要求

### 3.1 多进程支持

- 支持多进程/多线程环境
- 支持worker模式
- 主程序初始化，子进程直接使用

### 3.2 性能要求

- 控制台：实时输出
- 文件：异步写入，避免阻塞主线程
- **早期过滤优化**：被过滤的日志在判断级别后立即返回，不执行格式化等昂贵操作
- 预期负载：最高100条/秒

### 3.3 系统兼容性

- 主要支持Windows环境（CMD和PyCharm）
- **颜色支持**：
  - Windows CMD：自动启用ANSI颜色支持
  - PyCharm：使用专用的更鲜艳颜色
  - 其他环境：标准ANSI颜色或无颜色降级
- 考虑其他操作系统兼容性

## 4. 编码规范

### 4.1 文件规范

- 每个文件≤300行代码
- 文件头格式：
  
  ```python
  # src/custom_logger/filename.py
  from __future__ import annotations
  from datetime import datetime
  start_time = datetime.now()
  ```

### 4.2 函数规范

- 所有函数必须有显式`return`或`pass`
- 禁止返回表达式，先赋值再返回
- `_log`函数必须支持`do_print=True`签名
- 其他级别方法传递`**kwargs`给`_log`

### 4.3 代码质量

- 整数分隔符：配置文件用`_`，打印用`,`
- 行长度≤120字符
- 与系统logging完全隔离

## 5. 文件架构设计

### 5.1 文件拆分（每个≤300行）

1. **`types.py`** (~50行) - 级别常量和类型定义
2. **`config.py`** (~80行) - config_manager集成
3. **`formatter.py`** (~100行) - 日志格式化和行号提取
4. **`writer.py`** (~150行) - 异步文件写入
5. **`logger.py`** (~250行) - 主Logger类，包含Windows颜色支持
6. **`manager.py`** (~100行) - 全局管理器
7. **`__init__.py`** (~30行) - 模块接口

### 5.2 核心接口

```python
# 初始化系统（仅主程序调用）
init_custom_logger_system() -> None

# 获取logger实例（所有进程可用）
get_logger(name: str, console_level: str = None, file_level: str = None) -> CustomLogger

# 清理系统
tear_down_custom_logger_system() -> None

# 检查初始化状态
is_initialized() -> bool
```

### 5.3 Logger方法

```python
# 标准级别
logger.debug(message, *args, **kwargs)
logger.info(message, *args, **kwargs) 
logger.warning(message, *args, **kwargs)
logger.error(message, *args, **kwargs)
logger.critical(message, *args, **kwargs)
logger.exception(message, *args, **kwargs)

# 扩展级别
logger.detail(message, *args, **kwargs)
logger.worker_summary(message, *args, **kwargs)
logger.worker_detail(message, *args, **kwargs)

# 底层方法
logger._log(level, message, *args, do_print=True, **kwargs)
```

### 5.4 包管理文件

- **setup.py**：包安装配置
- **pyproject.toml**：现代Python包配置
- **pytest.ini**：测试配置
- **requirements.txt**：依赖声明
- **MANIFEST.in**：包文件清单

## 6. 配置文件结构

### 6.1 默认配置 (src/config/custom_logger.yaml)

```yaml
# 项目基本信息
project_name: "my_project"
experiment_name: "default"

# 日志级别配置
global_console_level: "info"
global_file_level: "debug"

# 目录配置
base_log_dir: "d:/logs"

# 系统配置（自动生成和维护）
first_start_time: null  # 第一次启动时自动设置
current_session_dir: null  # 当前会话目录

# 模块特定配置（可选）
module_levels: {}
#   module_name:
#     console_level: "debug"
#     file_level: "detail"
```

### 6.2 配置管理流程

1. 主程序调用`init_custom_logger_system()`
2. 检查`src/config/custom_logger.yaml`是否存在
3. 不存在则创建默认配置
4. 加载配置到config_manager
5. 设置`first_start_time`（如果为空）
6. 创建当前会话的日志目录
7. 保存更新后的配置

## 7. 测试要求

### 7.1 测试隔离

- 使用独立的配置空间
- 不影响现有通过的测试
- 支持并行测试
- 使用实际配置文件，但隔离测试数据

### 7.2 测试覆盖

- 所有函数签名和参数组合
- 边界条件和错误处理
- 多进程场景
- 配置管理功能
- **颜色支持功能**：Windows ANSI支持、PyCharm环境检测、颜色输出
- **性能优化**：早期过滤机制、级别判断逻辑

### 7.3 测试文件编号规范

- 测试文件：test_tc0001_types.py 到 test_tc0010_minimal_integration.py
- 测试函数：tc0001_001, tc0001_002 等二级编号
- 先简单测试，再复杂测试

## 8. 依赖关系

### 8.1 外部依赖

- `config_manager` - 配置管理（外部依赖，不需要版本号）
- `is_debug` - 调试模式判断
- 标准库：`threading`, `queue`, `os`, `sys`, `datetime`, `ctypes`（Windows颜色支持）

### 8.2 内部依赖

- 各模块间松耦合设计
- 通过manager统一管理全局状态

### 8.3 依赖文件

```text
# requirements.txt
config_manager
```

## 9. 使用示例

### 9.1 主程序初始化

```python
from custom_logger import init_custom_logger_system, get_logger

# 主程序初始化（仅调用一次）
init_custom_logger_system()

# 获取logger
logger = get_logger("main")
logger.info("程序启动")
```

### 9.2 子进程/Worker使用

```python
from custom_logger import get_logger

# 直接获取logger，无需初始化
logger = get_logger("worker", console_level="w_summary")
logger.worker_summary("Worker开始执行")
logger.worker_detail("详细worker信息")
```

### 9.3 模块特定配置

```python
# 为特定模块设置不同的日志级别
logger = get_logger("data_processor", 
                   console_level="debug", 
                   file_level="detail")
```

### 9.4 包安装和使用

```bash
# 安装包
pip install -e .

# 运行测试
pytest tests/

# 运行演示
python src/demo/demo_custom_logger.py
```

## 10. 新特性说明

### 10.1 颜色支持

- **自动环境检测**：区分Windows CMD、PyCharm、VS Code等环境
- **Windows ANSI支持**：自动启用Windows控制台的ANSI颜色支持
- **PyCharm优化**：为PyCharm环境提供更鲜艳的专用颜色
- **优雅降级**：不支持颜色时自动退回到纯文本输出

### 10.2 性能优化

- **早期过滤**：在`_log`方法开头判断级别，被过滤的日志立即返回
- **避免昂贵操作**：被过滤的日志不执行格式化、异常信息获取等操作
- **高效级别判断**：优化级别比较逻辑

### 10.3 格式改进

- **统一方括号**：`[PID | 模块名 : 行号]` 格式更紧凑
- **完美对齐**：PID(6位右对齐)、模块名(8位左对齐)、行号(4位右对齐)、级别(9位左对齐)
- **视觉友好**：使用分隔符`|`和`:`提供清晰的视觉分组

### 10.4 演示程序

- **完整场景**：覆盖基本用法、多线程、多进程、异常处理等
- **性能测试**：验证早期过滤的性能优化效果
- **颜色演示**：展示不同级别的颜色效果
- **实际应用**：贴近真实使用场景的示例代码