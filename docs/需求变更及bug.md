# 需求变更及Bug记录

## 需求变更记录

### 变更001 - config_object初始化优化 (2025-06-06)

**变更类型**: 功能增强  
**优先级**: 高  
**状态**: 已完成  

#### 变更描述
优化`init_custom_logger_system`函数的`config_object`参数处理逻辑，确保当只传入`config_object`时，logger配置能够正确初始化。

#### 具体需求
1. **完整初始化**: 当`init_custom_logger_system`只传入`config_object`对象时，需要对config对象初始化logger的配置
2. **first_start_time处理**: 
   - 传入的`first_start_time`参数应该是最高优先级
   - 如果传入的`config_object.first_start_time`没有值，才能使用自身逻辑
   - 如果两个都有值且值相同，不抛出错误
   - 如果两个都有值但值不同，抛出错误避免歧义
3. **会话目录创建**: 自动创建并设置`current_session_dir`
4. **配置完整性**: 确保所有必要的logger配置项都被正确初始化

#### 优先级规则
1. **最高优先级**: 传入的`first_start_time`参数
2. **次高优先级**: `config_object.first_start_time`
3. **最低优先级**: 当前时间（当两者都没有值时）
4. **冲突检测**: 如果两个都有值但不同，抛出`ValueError`

#### 实现要点
- 修改`_init_from_config_object`函数，添加`first_start_time`参数支持
- 实现智能冲突检测，支持datetime对象与字符串格式的比较
- 确保logger配置的完整复制，包括字典和对象格式支持
- 优化异常处理逻辑，避免配置被意外覆盖

#### 测试覆盖
- 基本config_object传递功能
- first_start_time冲突检测（不同值）
- first_start_time相同值不冲突
- 各种边界情况（缺少属性、None值等）
- logger配置的字典和对象格式支持

#### 影响范围
- `src/custom_logger/config.py`: `_init_from_config_object`函数
- `src/custom_logger/manager.py`: `init_custom_logger_system`函数调用
- `tests/01_unit_tests/test_custom_logger/test_tc0014_config_object_passing.py`: 新增测试用例

#### 向后兼容性
✅ 完全向后兼容，不影响现有的配置文件加载方式

---

### 变更002 - YAML库迁移 (2025-06-06)

**变更类型**: 技术债务优化  
**优先级**: 中等  
**状态**: 已完成  

#### 变更描述
将项目的YAML处理库从PyYAML迁移到ruamel.yaml，以获得更好的YAML格式保持能力和更安全的序列化机制。

#### 具体需求
1. **依赖库替换**: 将所有PyYAML的使用替换为ruamel.yaml
2. **API适配**: 适配ruamel.yaml的API调用方式
3. **格式保持**: 利用ruamel.yaml的格式保持特性，确保配置文件的可读性
4. **安全性提升**: 避免PyYAML的不安全序列化问题

#### 技术要点
- 更新`requirements.txt`和`pyproject.toml`中的依赖声明
- 修改所有`import yaml`为`from ruamel.yaml import YAML`
- 适配YAML对象的实例化和配置方式
- 保持现有的YAML文件格式和内容结构

#### 实现细节
```python
# 旧的PyYAML方式
import yaml
yaml.dump(data, file, default_flow_style=False, allow_unicode=True)

# 新的ruamel.yaml方式
from ruamel.yaml import YAML
yaml = YAML()
yaml.preserve_quotes = True
yaml.default_flow_style = False
yaml.dump(data, file)
```

#### 影响范围
- `requirements.txt`: 依赖声明更新
- `pyproject.toml`: 依赖声明更新
- `tests/test_custom_logger/test_tc0016_config_edge_cases.py`: YAML处理代码更新
- `src/demo/custom_logger_comprehensive/demo_runner.py`: 模块检查更新
- 所有使用YAML处理的代码文件

#### 测试验证
- 验证配置文件的正确加载和保存
- 确保YAML格式的保持性
- 验证序列化安全性（无Python对象标签）
- 回归测试确保功能不受影响

#### 向后兼容性
✅ 完全向后兼容，YAML文件格式和内容保持不变，仅底层处理库发生变化

#### 优势
1. **格式保持**: ruamel.yaml能更好地保持YAML文件的原始格式
2. **安全性**: 避免PyYAML的不安全序列化问题
3. **功能丰富**: 支持更多YAML特性，如注释保持
4. **维护活跃**: ruamel.yaml有更活跃的维护和更新

---

## Bug记录

### Bug001 - 示例Bug记录格式
**发现日期**: 2025-XX-XX  
**修复日期**: 2025-XX-XX  
**严重程度**: 中等  
**状态**: 已修复  

**问题描述**: 
描述具体的bug现象

**复现步骤**:
1. 步骤1
2. 步骤2
3. 步骤3

**根本原因**: 
分析bug的根本原因

**解决方案**: 
描述具体的修复方案

**测试验证**: 
描述如何验证修复效果

---

## 文档说明

本文档记录custom_logger项目的需求变更和bug修复情况，用于跟踪项目演进过程。

### 文档维护规则
1. 每个需求变更都要有唯一编号
2. 记录变更的完整上下文和影响范围
3. 包含测试验证情况
4. 标明向后兼容性影响

需求变更：
需求变更：

1、配置文件更改为`src/config/config.yaml`，其他配置文件不再使用。

2、配置文件结构需要用到的部分改为如下：

# 默认配置

DEFAULT_CONFIG = {  
    "project_name": "my_project",  
    "experiment_name": "default",  
    "first_start_time": None,  
    "base_dir": "d:/logs",  
    'logger': {  
        "global_console_level": "info",  
        "global_file_level": "debug",  
        "current_session_dir": None,  
        "module_levels": {}, },  
}



bug1：

默认配置：init_custom_logger_system()使用 src/config/config.yaml
自定义配置：init_custom_logger_system(config_path="path/to/not_default.yaml")使用指定配置文件
Worker进程：直接调用 get_logger()，自动从环境变量继承主程序的配置路径
目前不能正确处理

bug2：
[ 21696 | _callers :  103] 2025-06-01 22:20:20 - 12420:20:20.81 - w_summary - Worker任务开始
调用者，行号识别有问题。

### Bug002 - 多进程配置加载问题 (2025-06-06)
**发现日期**: 2025-06-06  
**修复日期**: 2025-06-06  
**严重程度**: 高  
**状态**: 已修复  

**问题描述**: 
在多进程环境中，子进程无法正确加载指定的配置文件内容，而是使用了默认配置或缓存的配置。

**复现步骤**:
1. 创建包含特定配置的YAML文件（如project_name: "yaml_test"）
2. 在子进程中通过环境变量传递配置文件路径
3. 子进程初始化custom_logger系统
4. 检查实际加载的配置内容

**根本原因**: 
config_manager在初始化时会自动保存配置，这会覆盖原始的测试配置文件。保存的格式是包装格式（__data__字段），丢失了原始的配置内容。

**解决方案**: 
1. 在初始化config_manager之前预读原始配置文件内容
2. 检测配置不一致时强制设置原始配置到config_manager
3. 处理config_manager的包装格式，正确提取配置内容
4. 添加调试输出帮助诊断配置加载问题

**测试验证**: 
通过test_tc0015_multiprocess_config.py中的多个测试用例验证：
- yaml_serialization_test_function: 验证YAML配置正确加载
- isolation_test_function: 验证配置隔离功能
- config_manager_test_function: 验证config_manager集成

**影响范围**:
- src/custom_logger/config.py: init_config函数的配置加载逻辑
- 多进程测试用例的稳定性
- config_manager集成的可靠性
