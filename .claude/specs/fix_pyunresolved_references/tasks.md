# 修复PyUnresolvedReferences错误任务清单

## 任务概览
修复custom_logger项目中所有PyUnresolvedReferencesInspection检查报告的ERROR和WARNING级别问题。

## 执行计划

### 第一阶段：ERROR级别修复（P0）

- [ ] 1. 修复config.py中的config_manager依赖问题
  - [ ] 1.1 重写_init_from_config_object函数，移除_managers引用（第183、187行）
  - [ ] 1.2 移除_init_from_config_object中的get_config_manager调用（第192行）
  - [ ] 1.3 重写init_config函数中的相关代码，移除_managers引用（第429、433行）
  - [ ] 1.4 移除init_config中的get_config_manager调用（第438行）
  - [ ] 1.5 确保直接使用传入的config_object，符合项目约束

- [ ] 2. 修复demo_comprehensive_custom_logger.py的导入错误
  - [ ] 2.1 移除parse_level_name的导入（第15行）
  - [ ] 2.2 移除get_level_name的导入（第15行）
  - [ ] 2.3 检查并修正相关函数调用

- [ ] 3. 修复demo_comprehensive_custom_logger.py的变量引用错误
  - [ ] 3.1 在第381行前定义error_log_path变量
  - [ ] 3.2 确保error_log_path正确指向错误日志文件

- [ ] 4. 修复worker_params_demo.py的导入错误
  - [ ] 4.1 移除init_custom_logger_system_with_params导入（第25行）
  - [ ] 4.2 移除init_custom_logger_system_from_serializable_config导入（第26行）
  - [ ] 4.3 移除get_logger_init_params导入（第28行）
  - [ ] 4.4 移除get_serializable_config导入（第29行）

- [ ] 5. 修复worker_serializable_config_demo.py的导入错误
  - [ ] 5.1 移除init_custom_logger_system_from_serializable_config导入（第24行）
  - [ ] 5.2 移除get_serializable_config导入（第26行）

- [ ] 6. 修复demo_worker_custom_config.py的变量引用错误
  - [ ] 6.1 在第195行前定义error_log_path变量
  - [ ] 6.2 确保所有error_log_path引用（196、197行）正常

### 第二阶段：WARNING级别修复（P1）

- [ ] 7. 清理未使用的导入
  - [ ] 7.1 删除config.py第7行的Dict导入
  - [ ] 7.2 删除comprehensive_demo.py第11行的multiprocessing导入
  - [ ] 7.3 删除demo_worker_custom_config.py第9行的threading导入
  - [ ] 7.4 删除demo_worker_custom_config.py第10行的multiprocessing导入

- [ ] 8. 修复CustomLogger方法调用
  - [ ] 8.1 修正demo_comprehensive_custom_logger.py第232行的w_summary调用
  - [ ] 8.2 修正demo_comprehensive_custom_logger.py第233行的w_detail调用
  - [ ] 8.3 修正demo_comprehensive_custom_logger.py第345行的w_summary调用

- [ ] 9. 修复其他WARNING问题
  - [ ] 9.1 修正demo_comprehensive_custom_logger.py第749行的invalid_attr访问

### 第三阶段：验证和测试

- [ ] 10. 静态检查验证
  - [ ] 10.1 运行PyCharm检查，确认无ERROR
  - [ ] 10.2 运行ruff检查，确认代码质量
  - [ ] 10.3 确认WARNING数量减少80%以上

- [ ] 11. 功能测试
  - [ ] 11.1 运行所有修改的demo文件
  - [ ] 11.2 执行pytest测试套件
  - [ ] 11.3 验证日志功能正常

- [ ] 12. 回归测试
  - [ ] 12.1 确认现有功能未受影响
  - [ ] 12.2 验证API兼容性

## 完成标准

- 所有ERROR级别问题已修复（7个）
- 所有WARNING级别问题已修复（6个）
- 所有测试通过
- 所有demo可正常运行
- 代码通过ruff检查

## 注意事项

1. 每个修改都要保持最小化原则
2. 保持向后兼容性
3. 遵循项目编码规范
4. 及时提交代码变更