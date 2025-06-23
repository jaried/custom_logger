# Custom Logger 概要设计文档

## 1. 引言

### 1.1 目的
本文档描述了custom_logger项目的概要设计，包括系统的整体设计思路、模块划分、接口定义、数据结构和主要业务流程。

### 1.2 适用范围
本文档适用于custom_logger项目的详细设计、编码实现和测试工作。

### 1.3 设计目标
- **高性能**: 异步日志写入，不阻塞主线程
- **易用性**: 简单的API接口，最小化配置
- **可扩展**: 支持多种配置源和输出目标
- **稳定性**: 多进程环境下的配置隔离和错误处理
- **兼容性**: 与现有config_manager系统无缝集成

**新API设计目标（2025年1月）**：
- **解耦设计**: 不再依赖config_manager，直接接收配置对象
- **Worker友好**: 专门的worker初始化函数，支持序列化配置传递
- **严格验证**: logger名字长度严格限制，防止格式错乱
- **队列支持**: 内置多进程队列模式，优化大规模并发场景
- **时间精确**: 使用外部传入的first_start_time，确保时间计算准确

## 2. 系统概要设计

### 2.1 设计原则

#### 2.1.1 分层架构
- **应用层**: 用户调用接口
- **接口层**: 系统管理和logger工厂
- **核心层**: 日志记录、配置管理、异步写入
- **支撑层**: 类型定义、外部依赖、文件系统

#### 2.1.2 职责分离
- **Manager**: 系统生命周期管理
- **Config**: 配置加载和验证
- **Logger**: 日志记录和格式化
- **Writer**: 异步文件写入
- **Formatter**: 日志格式化和调用者识别

#### 2.1.3 配置优先级
1. 函数参数（最高优先级）
2. 配置对象
3. 配置文件
4. 默认值（最低优先级）

### 2.2 核心模块设计

#### 2.2.1 Manager模块（系统管理器）
**职责**:
- 系统初始化和清理
- Logger实例创建和管理
- 全局状态维护

**主要功能**:
- 初始化日志系统
- 创建和缓存logger实例
- 系统资源清理
- 初始化状态检查

**接口设计**:
- `init_custom_logger_system()`: 系统初始化
- `get_logger()`: 获取logger实例
- `tear_down_custom_logger_system()`: 系统清理
- `is_initialized()`: 状态检查

#### 2.2.2 Config模块（配置管理器）
**职责**:
- 配置文件加载和解析
- 配置对象处理和验证
- 配置冲突检测和解决
- 会话目录管理

**主要功能**:
- 多配置源支持（文件、对象、参数）
- first_start_time冲突检测
- 配置内容验证和默认值填充
- 会话目录自动创建
- config_manager集成和优化

**关键设计**:
- 配置预读机制：防止config_manager覆盖原始配置
- 智能冲突检测：相同值不冲突，不同值抛错
- 多进程配置隔离：确保子进程正确加载配置
- **配置属性自动补充**：
  - 自动检查config对象是否包含完整的logger配置属性
  - 缺少logger属性时自动创建并设置默认值
  - 缺少logger子属性时自动补充默认值
  - 支持的自动补充属性：global_console_level、global_file_level、module_levels、show_call_chain、show_debug_call_stack、enable_queue_mode
  - 优雅处理只读config对象，无法设置属性时不抛出异常
  - 确保下次使用时config对象包含完整配置信息

#### 2.2.3 Logger模块（日志记录器）
**职责**:
- 日志消息记录和处理
- 日志级别控制和过滤
- 消息格式化调度
- 异步写入调度

**主要功能**:
- 多级别日志记录（标准级别+扩展级别）
- 动态级别控制
- 早期过滤优化
- 参数化日志支持
- 异常信息自动捕获
- **倒计时功能**：原位更新显示，避免文件写入膨胀

**级别体系**:
- 标准级别：DEBUG(10) > INFO(20) > WARNING(30) > ERROR(40) > CRITICAL(50) > EXCEPTION(60)
- 扩展级别：W_DETAIL(3) > W_SUMMARY(5) > DETAIL(8)

**倒计时功能设计**:
- `countdown_info()`: 倒计时信息输出
  - 使用`\r`实现原位更新（同一行显示）
  - 保留完整的日志格式（时间戳、PID、模块名等）
  - 不写入文件，仅控制台显示
  - 适用于长时间等待场景（建议20秒以上）
- `countdown_end()`: 结束倒计时
  - 可选显示完成信息
  - 自动换行，为后续日志让出空间
  - 完成信息会正常写入文件

#### 2.2.4 Writer模块（异步写入器）
**职责**:
- 异步日志文件写入
- 文件管理和轮转
- 写入队列管理
- 性能优化

**主要功能**:
- 异步队列处理
- 批量写入优化
- 文件目录自动创建
- 错误日志分离
- 写入状态监控

#### 2.2.5 Formatter模块（格式化器）
**职责**:
- 日志消息格式化
- 调用者信息识别
- 时间戳和运行时长计算
- 颜色支持处理

**主要功能**:
- 统一日志格式：`[PID | 模块名 : 行号] 时间戳 - 运行时长 - 级别 - 消息`
- 智能调用者识别
- 跨平台颜色支持
- 性能优化的格式化

## 3. 数据结构设计

### 3.1 配置数据结构

#### 3.1.1 主配置结构
```
配置对象:
├── project_name: 项目名称
├── experiment_name: 实验名称
├── first_start_time: 首次启动时间
├── base_dir: 日志基础目录
└── logger: 日志配置
    ├── global_console_level: 全局控制台级别
    ├── global_file_level: 全局文件级别
    ├── current_session_dir: 当前会话目录
    ├── show_call_chain: 调用链显示控制
    ├── show_debug_call_stack: 调试堆栈显示控制
    └── module_levels: 模块特定级别配置
        └── [模块名]:
            ├── console_level: 控制台级别
            └── file_level: 文件级别
```

#### 3.1.2 日志级别常量
```
级别定义:
├── W_DETAIL = 3 (Worker详细级别)
├── W_SUMMARY = 5 (Worker摘要级别)
├── DETAIL = 8 (详细调试级别)
├── DEBUG = 10 (调试级别)
├── INFO = 20 (信息级别)
├── WARNING = 30 (警告级别)
├── ERROR = 40 (错误级别)
├── CRITICAL = 50 (严重错误级别)
└── EXCEPTION = 60 (异常级别)
```

### 3.2 日志消息结构

#### 3.2.1 日志记录格式
```
日志记录:
├── 进程ID (6位右对齐)
├── 模块名 (8位左对齐)
├── 行号 (4位右对齐)
├── 时间戳 (YYYY-MM-DD HH:MM:SS)
├── 运行时长 (H:MM:SS.ff)
├── 级别名称 (9位左对齐)
└── 消息内容
```

#### 3.2.2 文件路径结构
```
日志文件路径:
{base_dir}/
└── {debug}/ (debug模式时)
    └── {project_name}/
        └── {experiment_name}/
            └── {YYYY-MM-DD}/
                └── {HHMMSS}/
                    ├── full.log (完整日志)
                    └── error.log (错误日志)
```

## 4. 接口设计

### 4.1 系统管理接口

#### 4.1.1 系统初始化接口（新API）

**主程序初始化**:
```python
def init_custom_logger_system(config_object: Any) -> None:
    """
    初始化自定义日志系统（主程序模式）
    
    Args:
        config_object: 配置对象（必须），主程序传递config_manager的config对象
                      必须包含paths.log_dir和first_start_time属性
                      如果包含queue_info.log_queue，则启用队列模式
    
    Raises:
        ValueError: 如果config_object为None或缺少必要属性
    """
```

**Worker进程初始化**:
```python
def init_custom_logger_system_for_worker(
    serializable_config_object: Any,
    worker_id: str = None
) -> None:
    """
    为worker进程初始化自定义日志系统
    
    Args:
        serializable_config_object: 序列化的配置对象，包含paths.log_dir、
                                   first_start_time、以及队列信息等
        worker_id: worker进程ID，用于标识日志来源
    
    Raises:
        ValueError: 如果serializable_config_object为None或缺少必要属性
    """
```

**API变更说明**:
1. 不再接收`config_path`和`first_start_time`参数
2. 所有配置信息必须通过`config_object`提供
3. Worker进程使用专门的初始化函数
4. 支持队列模式用于多进程日志处理
**接口名称**: `init_custom_logger_system`
**功能描述**: 初始化整个日志系统
**输入参数**:
- `config_path`: 配置文件路径（可选）
- `first_start_time`: 首次启动时间（可选）
- `config_object`: 配置对象（可选）
**输出**: 无
**异常**: 配置冲突时抛出ValueError

#### 4.1.2 Logger获取接口
**接口名称**: `get_logger`
**功能描述**: 获取logger实例
**输入参数**:
- `name`: logger名称（必须，严格限制8字符以内）
- `console_level`: 控制台级别（可选，已废弃，保留用于兼容性）
- `file_level`: 文件级别（可选，已废弃，保留用于兼容性）
**输出**: CustomLogger实例
**异常**: 
- 系统未初始化时抛出RuntimeError
- 名称超过8个字符时抛出ValueError
**新增验证**:
- 严格的名称长度检查，超过8个字符直接抛出异常
- 提示信息明确指出字符数限制

#### 4.1.3 系统清理接口
**接口名称**: `tear_down_custom_logger_system`
**功能描述**: 清理系统资源
**输入参数**: 无
**输出**: 无
**异常**: 无

### 4.2 日志记录接口

#### 4.2.1 标准级别接口
- `debug(message, *args, **kwargs)`: 调试信息
- `info(message, *args, **kwargs)`: 普通信息
- `warning(message, *args, **kwargs)`: 警告信息
- `error(message, *args, **kwargs)`: 错误信息
- `critical(message, *args, **kwargs)`: 严重错误
- `exception(message, *args, **kwargs)`: 异常信息（自动包含堆栈）

#### 4.2.2 扩展级别接口
- `detail(message, *args, **kwargs)`: 详细调试信息
- `worker_summary(message, *args, **kwargs)`: Worker摘要信息
- `worker_detail(message, *args, **kwargs)`: Worker详细信息

#### 4.2.3 倒计时功能接口
- `countdown_info(message, *args, **kwargs)`: 倒计时信息输出
  - 在同一行原位更新，使用`\r`不换行
  - 保留完整日志格式（时间戳、PID、模块名等）
  - 不写入文件，仅控制台显示
  - 适用于长时间等待场景（建议20秒以上）
- `countdown_end(final_message=None)`: 结束倒计时
  - 可选显示完成信息
  - 自动换行，为后续日志让出空间
  - 完成信息会正常写入文件

## 5. 业务流程设计

### 5.1 系统初始化流程

#### 5.1.1 主流程
1. **参数验证**: 检查输入参数的有效性
2. **配置加载**: 根据优先级加载配置
3. **冲突检测**: 检查first_start_time冲突
4. **配置验证**: 验证配置完整性和合法性
5. **目录创建**: 创建会话目录和日志目录
6. **Writer初始化**: 启动异步写入器
7. **状态设置**: 设置系统初始化完成标志

#### 5.1.2 配置加载子流程
1. **原始配置预读**: 读取原始配置文件内容
2. **config_manager初始化**: 初始化外部配置管理器
3. **配置一致性检查**: 比较原始配置和manager配置
4. **配置强制更新**: 必要时强制设置原始配置
5. **配置验证**: 验证最终配置的正确性

### 5.2 日志记录流程

#### 5.2.1 主流程
1. **级别检查**: 早期过滤，不符合级别的直接返回
2. **调用者识别**: 获取调用者模块名和行号
3. **消息格式化**: 格式化日志消息和参数
4. **控制台输出**: 根据级别决定是否输出到控制台
5. **异步写入**: 将日志加入异步写入队列

#### 5.2.2 异步写入子流程
1. **队列接收**: 从异步队列接收日志消息
2. **批量处理**: 批量处理多条日志消息
3. **文件写入**: 写入到相应的日志文件
4. **错误处理**: 处理写入过程中的异常
5. **状态更新**: 更新写入状态和统计信息

#### 5.2.3 倒计时功能流程
1. **倒计时信息处理**:
   - 调用`countdown_info()`时不检查文件级别
   - 格式化倒计时消息（保留完整格式）
   - 使用`\r`输出到控制台（原位更新）
   - 不加入异步写入队列（避免文件膨胀）
2. **倒计时结束处理**:
   - 调用`countdown_end()`时可选显示完成信息
   - 如有完成信息，按正常日志处理（含文件写入）
   - 输出换行符，为后续日志让出空间
   - 清理倒计时状态

### 5.3 多进程配置同步流程

#### 5.3.1 主进程配置设置
1. **配置初始化**: 主进程初始化配置
2. **环境变量设置**: 设置配置路径环境变量
3. **子进程启动**: 启动子进程并传递配置信息

#### 5.3.2 子进程配置继承
1. **环境变量读取**: 读取配置路径环境变量
2. **原始配置保护**: 预读原始配置防止被覆盖
3. **配置管理器初始化**: 初始化config_manager
4. **配置一致性验证**: 验证配置是否正确加载
5. **必要时强制修复**: 检测到不一致时强制设置正确配置

## 6. 异常处理设计

### 6.1 异常分类

#### 6.1.1 配置相关异常
- **配置文件不存在**: 使用默认配置继续运行
- **配置格式错误**: 抛出异常，停止初始化
- **配置冲突**: 抛出ValueError，明确指出冲突内容

#### 6.1.2 运行时异常
- **文件写入失败**: 记录错误，尝试降级处理
- **格式化异常**: 记录原始消息，避免丢失日志
- **调用者识别失败**: 使用默认值，不影响日志记录

### 6.2 异常处理策略

#### 6.2.1 遇错即抛原则
- 对于影响系统正常运行的错误，立即抛出异常
- 最小化try-except的使用，避免隐藏问题
- 提供清晰的错误信息和解决建议

#### 6.2.2 降级处理
- 对于非关键功能的错误，采用降级处理
- 确保核心日志功能不受影响
- 记录降级处理的原因和影响

## 7. 性能设计

### 7.1 性能优化策略

#### 7.1.1 早期过滤
- 在日志记录的最早阶段进行级别检查
- 被过滤的日志不执行任何格式化操作
- 减少不必要的字符串操作和函数调用

#### 7.1.2 异步写入
- 使用异步队列处理文件写入
- 批量写入减少系统调用次数
- 避免I/O操作阻塞主线程

#### 7.1.3 缓存优化
- 缓存logger实例，避免重复创建
- 缓存格式化模板，减少字符串操作
- 缓存调用者信息，减少堆栈分析

### 7.2 性能监控

#### 7.2.1 关键指标
- 日志记录延迟
- 异步队列长度
- 文件写入速度
- 内存使用情况

#### 7.2.2 性能基准
- 支持100条/秒的日志记录
- 控制台输出延迟 < 1ms
- 文件写入延迟 < 10ms
- 内存使用增长 < 1MB/小时

## 8. 安全设计

### 8.1 数据安全

#### 8.1.1 敏感信息保护
- 禁止在日志中记录密码、密钥等敏感信息
- 提供数据脱敏机制
- 配置文件中敏感信息通过环境变量注入

#### 8.1.2 文件权限
- 日志文件设置合理的访问权限
- 防止未授权用户访问日志内容
- 配置文件的安全存储

### 8.2 系统安全

#### 8.2.1 资源限制
- 限制日志文件大小，防止磁盘空间耗尽
- 限制异步队列长度，防止内存溢出
- 监控系统资源使用情况

#### 8.2.2 故障隔离
- 日志系统故障不影响主业务逻辑
- 提供降级模式，确保基本功能可用
- 自动恢复机制，减少人工干预

## 9. 扩展性设计

### 9.1 功能扩展

#### 9.1.1 输出目标扩展
- 支持网络日志传输
- 支持数据库日志存储
- 支持第三方日志服务集成

#### 9.1.2 格式扩展
- 支持JSON格式日志
- 支持结构化日志
- 支持自定义格式化器

### 9.2 配置扩展

#### 9.2.1 配置源扩展
- 支持数据库配置
- 支持远程配置服务
- 支持动态配置更新

#### 9.2.2 配置验证扩展
- 支持配置模式验证
- 支持配置版本管理
- 支持配置变更审计

## 10. 测试设计

### 10.1 测试策略

#### 10.1.1 单元测试
- 每个模块的独立功能测试
- 边界条件和异常情况测试
- 性能基准测试

#### 10.1.2 集成测试
- 模块间接口测试
- 端到端功能测试
- 多进程环境测试

#### 10.1.3 性能测试
- 高并发日志记录测试
- 长时间运行稳定性测试
- 资源使用情况测试

### 10.2 测试环境隔离设计

#### 10.2.1 路径隔离方案
```python
# 标准测试路径配置方案
import tempfile
import os

def setup_test_environment():
    """设置测试环境的标准化路径配置"""
    temp_dir = tempfile.gettempdir()
    test_base_dir = os.path.join(temp_dir, "custom_logger_tests")
    return test_base_dir

# 在所有测试中统一使用
base_dir = setup_test_environment()
```

#### 10.2.2 Mock配置设计模式
- **具体值原则**: 所有Mock对象的关键属性必须设置为具体的字符串值
- **路径一致性**: Mock配置生成的路径必须与实际`_create_log_dir`函数的输出格式一致
- **属性完整性**: Mock配置必须包含`base_dir`、`experiment_name`、`first_start_time`、`logger`、`paths`等必要属性

#### 10.2.3 路径格式标准化设计
- **实际格式**: `{base_dir}/{project_name}/{experiment_name}/{YYYY-MM-DD}/{HHMMSS}`
- **日期处理**: 使用`strftime("%Y-%m-%d")`生成日期部分
- **时间处理**: 使用`strftime("%H%M%S")`生成时间部分
- **调试模式**: 在`is_debug()`为True时，在base_dir后添加"debug"目录

### 10.3 测试配置管理设计

#### 10.3.1 Mock配置创建标准化
```python
def create_mock_config(project_name="test_project", 
                      experiment_name="test_experiment",
                      base_dir=None):
    """创建标准化的Mock配置对象"""
    if base_dir is None:
        base_dir = tempfile.gettempdir()
    
    mock_cfg = MagicMock()
    mock_cfg.base_dir = base_dir
    mock_cfg.project_name = project_name
    mock_cfg.experiment_name = experiment_name
    mock_cfg.first_start_time = "2024-01-01T12:00:00"
    mock_cfg.logger = {
        "global_console_level": "info",
        "global_file_level": "debug",
        "current_session_dir": None,
        "module_levels": {}
    }
    mock_cfg.paths = {"log_dir": base_dir}
    return mock_cfg
```

#### 10.3.2 测试期望值计算
```python
def calculate_expected_path(base_dir, project_name, experiment_name, 
                           first_start_time, is_debug=False):
    """计算期望的路径，与实际实现保持一致"""
    from datetime import datetime
    
    if is_debug:
        base_dir = os.path.join(base_dir, "debug")
    
    start_time = datetime.fromisoformat(first_start_time)
    date_str = start_time.strftime("%Y-%m-%d")
    time_str = start_time.strftime("%H%M%S")
    
    return os.path.join(base_dir, project_name, experiment_name, date_str, time_str)
```

### 10.4 测试覆盖

#### 10.4.1 功能覆盖
- 所有公开接口的测试覆盖
- 所有配置选项的测试覆盖
- 所有异常路径的测试覆盖
- **路径格式一致性测试**: 确保测试期望与实际实现路径格式完全一致

#### 10.4.2 场景覆盖
- 单线程应用场景
- 多线程应用场景
- 多进程应用场景
- 高并发场景
- **Mock配置场景**: 覆盖各种Mock配置组合和边界情况

---

## 文档维护

**创建日期**: 2025-06-06  
**最后更新**: 2025-06-06  
**版本**: v1.1  
**维护者**: 开发团队  

### 更新记录
- v1.2 (2025-06-06): 新增测试环境隔离设计和Mock配置标准化方案
- v1.1 (2025-06-06): 新增多进程配置管理和config_manager集成优化的概要设计
- v1.0 (2025-06-06): 初始版本，包含系统整体概要设计 