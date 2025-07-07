# Custom Logger Demo 使用指南

## 概述

本目录包含了 custom_logger 系统的完整演示程序，涵盖了所有主要功能和使用场景。这些演示完全覆盖了现有测试用例的功能范围，可以作为学习、验证和调试的工具。

## Demo 文件结构

```
src/demo/
├── README_demo_guide.md              # 本文档
├── demo_runner.py                     # 统一的演示程序入口
├── demo_quick_start.py               # 快速入门演示
├── demo_advanced_features.py         # 高级功能演示  
├── demo_comprehensive_custom_logger.py # 综合功能演示
├── debug_call_stack_demo.py          # 调用链调试演示
└── [其他旧demo目录...]              # 保留的旧演示文件
```

## 演示程序说明

### 1. 统一入口 (demo_runner.py)

**功能**: 提供菜单界面，统一管理所有演示程序

**使用方法**:
```bash
cd src/demo
python demo_runner.py
```

**特性**:
- 交互式菜单选择
- 自动检查demo文件完整性
- 错误处理和异常捕获
- 用户友好的操作界面

### 2. 快速入门演示 (demo_quick_start.py)

**涵盖功能**:
- 日志系统初始化
- 基本日志记录
- 参数化日志消息
- 异常日志记录
- 系统清理

**对应测试用例**: 
- test_tc0007_basic_integration.py
- test_tc0010_minimal_integration.py

**运行方法**:
```bash
python demo_quick_start.py
```

### 3. 高级功能演示 (demo_advanced_features.py)

**涵盖功能**:
- 多线程日志记录
- 多进程日志记录
- 自定义配置场景
- 调用者识别测试
- 性能基准测试

**对应测试用例**:
- test_tc0013_custom_config_worker.py
- test_tc0014_caller_thread_identification.py
- test_tc0015_multiprocess_config.py
- test_tc0009_performance_integration.py

**运行方法**:
```bash
python demo_advanced_features.py
```

### 4. 综合功能演示 (demo_comprehensive_custom_logger.py)

**涵盖功能**:
- 类型系统演示 (对应 test_tc0001_types.py)
- 配置管理演示 (对应 test_tc0002_config.py)
- 格式化功能演示 (对应 test_tc0003_formatter.py)
- 基础日志演示 (对应 test_tc0004_writer.py)
- 调用者识别演示 (对应 test_tc0012_caller_identification.py)
- 多线程演示 (对应 test_tc0006_manager.py)
- 多进程演示 (对应 test_tc0015_multiprocess_config.py)
- 自定义配置演示 (对应 test_tc0016_config_edge_cases.py)
- 性能测试演示 (对应 test_tc0009_performance_integration.py)
- 错误处理演示 (对应各种异常测试)

**运行方法**:
```bash
python demo_comprehensive_custom_logger.py
```

### 5. 调用链调试演示 (debug_call_stack_demo.py)

**涵盖功能**:
- 调试输出开启/关闭
- 调用链信息显示
- 配置参数控制

**对应测试用例**:
- test_tc0017_caller_identification_comprehensive.py
- test_tc0018_caller_verification.py

**运行方法**:
```bash
python debug_call_stack_demo.py
```

## 测试用例覆盖映射

| 测试文件 | 对应Demo | 涵盖功能 |
|---------|---------|---------|
| test_tc0001_types.py | comprehensive | 类型系统、级别解析 |
| test_tc0002_config.py | comprehensive | 配置管理、路径处理 |
| test_tc0003_formatter.py | comprehensive | 格式化、调用者识别 |
| test_tc0004_writer.py | comprehensive | 异步写入、日志条目 |
| test_tc0007_basic_integration.py | quick_start | 基础集成测试 |
| test_tc0008_advanced_integration.py | advanced | 高级集成功能 |
| test_tc0009_performance_integration.py | advanced/comprehensive | 性能测试 |
| test_tc0010_minimal_integration.py | quick_start | 最小化集成 |
| test_tc0011_worker_paths.py | advanced | Worker路径管理 |
| test_tc0012_caller_identification.py | comprehensive | 调用者识别 |
| test_tc0013_custom_config_worker.py | advanced | 自定义配置Worker |
| test_tc0014_caller_thread_identification.py | advanced | 线程调用者识别 |
| test_tc0015_multiprocess_config.py | advanced | 多进程配置 |
| test_tc0016_config_edge_cases.py | comprehensive | 配置边界情况 |
| test_tc0017_caller_identification_comprehensive.py | debug_call_stack | 调用者识别综合测试 |
| test_tc0018_caller_verification.py | debug_call_stack | 调用者验证 |

## 使用建议

### 学习路径

1. **新用户**: 从 `demo_quick_start.py` 开始
2. **进阶用户**: 运行 `demo_advanced_features.py`
3. **完整了解**: 执行 `demo_comprehensive_custom_logger.py`
4. **问题调试**: 使用 `debug_call_stack_demo.py`

### 开发验证

1. **功能验证**: 运行对应的demo程序验证特定功能
2. **性能基准**: 使用性能测试部分建立基准
3. **配置测试**: 通过自定义配置演示测试不同配置场景
4. **调试支持**: 使用调试演示定位问题

### 教学和培训

1. **概念讲解**: 使用demo程序进行现场演示
2. **实践练习**: 让学员修改demo配置和参数
3. **问题排查**: 通过demo演示常见问题和解决方法

## 输出和日志

### 日志文件位置

演示程序会在以下位置创建日志文件：
```
d:/logs/
├── quick_start/          # 快速入门演示日志
├── advanced/            # 高级功能演示日志
├── demo/               # 综合演示日志
├── caller/             # 调用者识别演示日志
├── debug/              # 调试演示日志
└── [其他场景目录]/     # 各种测试场景日志
```

### 控制台输出

- **信息提示**: 演示步骤说明和状态信息
- **日志内容**: 实时显示的日志消息
- **性能数据**: 性能测试的统计结果
- **错误信息**: 异常和错误的详细信息

## 故障排除

### 常见问题

1. **导入错误**: 确保在正确的目录下运行，且custom_logger包可访问
2. **配置错误**: 检查临时配置文件是否正确创建
3. **权限问题**: 确保有权限创建日志目录和文件
4. **多进程问题**: 在某些环境下多进程演示可能需要特殊配置

### 调试建议

1. **开启调试输出**: 在配置中设置 `show_debug_call_stack: true`
2. **查看日志文件**: 检查生成的日志文件内容
3. **单步执行**: 逐个运行演示部分定位问题
4. **环境检查**: 确认Python版本和依赖库版本

## 扩展和定制

### 添加新演示

1. 创建新的演示文件 `demo_your_feature.py`
2. 遵循现有的文件头格式
3. 在 `demo_runner.py` 中添加菜单项
4. 更新本README文档

### 修改现有演示

1. 直接编辑对应的演示文件
2. 保持函数签名和接口不变
3. 确保错误处理和资源清理正确
4. 测试修改后的功能

### 配置定制

1. 修改演示中的配置内容
2. 调整日志级别和输出路径
3. 添加自定义模块配置
4. 测试不同配置场景

## 总结

这套demo系统提供了 custom_logger 的完整功能展示，可以用于：

- **学习和教学**: 系统性了解custom_logger的使用方法
- **功能验证**: 验证系统功能的正确性和完整性
- **性能评估**: 评估系统在不同场景下的性能表现
- **问题诊断**: 快速定位和解决使用中的问题
- **开发支持**: 为新功能开发提供测试和验证平台

通过运行这些演示，用户可以全面了解custom_logger的能力，并在实际项目中正确使用它。 