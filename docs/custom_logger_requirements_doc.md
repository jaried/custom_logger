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

### 1.2 倒计时功能

- **用途**：用于在同一行显示倒计时进度，适用于等待时间较长的场景（建议20秒以上）
- **特点**：
  - **原位更新**：使用`\r`在同一行更新，不产生多行日志
  - **完整格式**：保留logger的完整格式（时间戳、PID、模块名、用时等）
  - **自动换行**：倒计时结束后自动换行，不影响后续日志
  - **文件优化**：倒计时过程不写入文件，避免日志文件膨胀
  - **一行显示**：整个倒计时过程只占用一行，结束时可直接显示完成信息
- **方法**：
  - `countdown_info()`: 倒计时信息（原位更新，不换行）
  - `countdown_end()`: 结束倒计时，可选显示完成信息
- **适用场景**：
  - 长时间等待操作（建议20秒以上）
  - 需要实时显示进度的场景
  - 避免日志文件中出现大量重复的等待信息

### 1.3 输出机制

- **控制台输出**：实时输出，支持Windows CMD和PyCharm颜色
  - INFO及以下：无颜色
  - WARNING以上：彩色输出，不同级别使用不同颜色
- **文件输出**：异步批量写入
  - **全局日志文件**：
    - `full.log`：记录所有模块的所有级别日志
    - `warning.log`：记录所有模块的WARNING及以上级别日志
  - **模块日志文件**：
    - `{logger_name}_full.log`：记录指定模块的所有级别日志
    - `{logger_name}_warning.log`：记录指定模块的WARNING及以上级别日志
  - **写入策略**：
    - 每条日志根据级别和配置决定写入哪些文件
    - `full.log`和`{logger_name}_full.log`：写入所有级别日志（受文件级别配置限制）
    - `warning.log`和`{logger_name}_warning.log`：仅写入WARNING及以上级别日志
    - 级别控制：遵循现有的console_level和file_level配置机制

### 1.4 日志格式

```
[{pid:>6} | {模块名:<8} : {行号:>4}] {时间戳} - {运行时长} - {级别:<9} - {消息}
```

### 1.5 颜色方案

- **INFO及以下**：无颜色（普通文本）
- **WARNING**：黄色（CMD）/ 亮黄色（PyCharm）
- **ERROR**：红色（CMD）/ 亮红色（PyCharm）  
- **CRITICAL**：洋红色（CMD）/ 亮洋红色（PyCharm）
- **EXCEPTION**：亮红色（CMD）/ 粗体红色（PyCharm）

### 1.6 文件路径结构

```
config.base_dir/{如果是debug模式，加'debug'}/config.project_name/{实验名}/{config.first_start_time,yyyy-mm-dd格式}/{config.first_start_time,HHMMSS格式}/
```

## 2. 配置管理

### 2.1 使用config_manager

- 集成项目统一的配置管理系统
- 配置文件保存到：`src/config/custom_logger.yaml`
- 持久化配置，防止多进程时丢失

### 2.2 新API设计（2025年1月变更）

**主要变更**：
1. `init_custom_logger_system`不再调用config_manager，而是接收config对象
2. 取消对传入`first_start_time`参数的支持，必须使用`config.first_start_time`
3. 使用`config.paths.log_dir`作为工作路径
4. `get_logger`名字超过16个字符直接抛出异常
5. Worker进程使用专门的初始化函数`init_custom_logger_system_for_worker`

**新API接口**：
```python
# 主程序初始化（只接收config对象）
init_custom_logger_system(config_object: Any) -> None

# Worker进程初始化
init_custom_logger_system_for_worker(
    serializable_config_object: Any,
    worker_id: str = None
) -> None

# 获取logger（名字长度验证）
get_logger(name: str, console_level: Optional[str] = None, 
          file_level: Optional[str] = None) -> CustomLogger
```

**API变更说明**：
1. `init_custom_logger_system`不再接收`config_path`和`first_start_time`参数，只接收`config_object`
2. 所有配置信息（包括`first_start_time`、日志级别等）必须通过`config_object`提供
3. `get_logger`名字长度限制为16个字符，超过会抛出`ValueError`异常
4. Worker进程使用专门的`init_custom_logger_system_for_worker`函数
5. 支持队列模式用于多进程日志处理

**配置对象要求**：
- 必须包含`paths.log_dir`属性（字符串路径）
- 必须包含`first_start_time`属性（datetime对象或ISO字符串）
- 可选包含`logger`配置对象
- 可选包含`queue_info.log_queue`用于多进程队列模式
- 可选在`logger`配置中包含`enable_queue_mode`布尔参数来显式控制队列模式

**配置属性自动补充**：
- 如果config对象缺少`logger`属性，系统会自动创建并设置默认值
- 如果`logger`对象缺少必要的子属性，系统会自动补充默认值
- 自动补充的属性包括：
  - `global_console_level`: "info"
  - `global_file_level`: "debug"
  - `module_levels`: {}
  - `show_call_chain`: True
  - `show_debug_call_stack`: False
  - `enable_queue_mode`: False
- 对于只读config对象，系统会优雅处理无法设置属性的情况，不会抛出异常
- 属性补充确保下次使用时config对象包含完整的logger配置信息

**队列模式控制**：
- 优先检查`config.logger.enable_queue_mode`参数
- 如果`enable_queue_mode=True`，则必须提供`queue_info.log_queue`
- 如果`enable_queue_mode=False`，则不启用队列模式（但仍会检查`queue_info`以保持向后兼容）
- 如果没有`enable_queue_mode`参数，则根据是否存在`queue_info.log_queue`自动判断（向后兼容）

### 2.3 YAML处理库选择

- **使用ruamel.yaml替代PyYAML**：提供更好的格式保持能力
- **安全性考虑**：避免PyYAML的不安全序列化问题
- **格式保持**：保持配置文件的原始格式、注释和缩进
- **功能丰富**：支持更多YAML 1.2规范特性

### 2.4 配置项

- `project_name`：项目名称
- `experiment_name`：实验名称  
- `global_console_level`：全局控制台日志级别
- `global_file_level`：全局文件日志级别
- `module_levels`：模块特定级别配置（可选）
- `first_start_time`：第一个启动模块的时间戳（必须由外部传入）
- `base_log_dir`：基础日志目录（默认"d:/logs"）

### 2.5 debug模式判断

```python
from is_debug import is_debug
```

使用现有的`is_debug()`函数判断调试模式

### 2.6 系统初始化

- **主程序调用**：`init_custom_logger_system(config_object)`
- **Worker进程调用**：`init_custom_logger_system_for_worker(serializable_config_object, worker_id)`
- 不再调用config_manager，直接使用传入的配置对象
- 自动创建必要的目录结构
- 支持队列模式用于多进程日志处理

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

# 倒计时功能
logger.countdown_info(message, *args, **kwargs)    # 倒计时信息（原位更新，不换行）
logger.countdown_end(final_message=None)           # 结束倒计时，可选显示完成信息

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
- **路径隔离要求**：所有测试必须使用系统临时路径，禁止使用生产环境路径（如d:\根目录）

### 7.2 测试覆盖

- 所有函数签名和参数组合
- 边界条件和错误处理
- 多进程场景
- 配置管理功能
- **颜色支持功能**：Windows ANSI支持、PyCharm环境检测、颜色输出
- **性能优化**：早期过滤机制、级别判断逻辑

### 7.3 Mock配置规范

- **Mock对象必须设置具体值**：base_dir、experiment_name等属性必须返回字符串而非Mock对象
- **路径格式一致性**：测试期望值必须与实际实现的路径格式保持一致（YYYY-MM-DD格式）
- **临时路径使用**：所有测试路径必须使用tempfile.gettempdir()获取系统临时目录

### 7.4 测试文件编号规范

- 测试文件：test_tc0001_types.py 到 test_tc0010_minimal_integration.py
- 测试函数：tc0001_001, tc0001_002 等二级编号
- 先简单测试，再复杂测试

## 8. 依赖关系

### 8.1 外部依赖

- `config_manager` - 配置管理（外部依赖，不需要版本号）
- `ruamel.yaml` - YAML处理库（>=0.17.0）
- `is_debug` - 调试模式判断
- 标准库：`threading`, `queue`, `os`, `sys`, `datetime`, `ctypes`（Windows颜色支持）

### 8.2 内部依赖

- 各模块间松耦合设计
- 通过manager统一管理全局状态

### 8.3 依赖文件

```text
# requirements.txt
ruamel.yaml>=0.17.0
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

### 9.4 倒计时功能使用

```python
import asyncio
from custom_logger import get_logger

async def countdown_example():
    logger = get_logger("main")
    
    # 倒计时循环（在同一行原位更新）
    for remaining in range(10, 0, -1):
        logger.countdown_info(f"等待 {remaining} 秒后继续...")
        await asyncio.sleep(1)
    
    # 结束倒计时并显示完成信息（合并到一行）
    logger.countdown_end("等待完成，开始执行下一步")
    
    # 或者只结束倒计时不显示额外信息
    # logger.countdown_end()

# 适用场景：长时间等待操作
async def process_with_delay():
    logger = get_logger("process")
    
    # 对于较长的等待时间（建议20秒以上）使用倒计时
    wait_time = 30
    if wait_time > 20:
        for remaining in range(wait_time, 0, -1):
            logger.countdown_info(f"等待 {remaining} 秒后处理下一项...")
            await asyncio.sleep(1)
        logger.countdown_end("等待完成，开始处理")
    else:
        # 短时间等待直接使用普通日志
        logger.info(f"等待 {wait_time} 秒...")
        await asyncio.sleep(wait_time)
```

### 9.5 包安装和使用

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