# src/demo/custom_logger_comprehensive/feature_specific_demos.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import time
import tempfile
import threading
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


def demo_types_functionality():
    """演示types模块功能"""
    print("\n=== Types模块功能演示 ===")

    from custom_logger.types import (
        DEBUG, INFO, WARNING, ERROR, CRITICAL, EXCEPTION,
        DETAIL, W_SUMMARY, W_DETAIL,
        parse_level_name, get_level_name,
        LEVEL_NAME_TO_VALUE, VALUE_TO_LEVEL_NAME
    )

    logger = get_logger("types_demo")
    logger.info("Types模块功能演示开始")

    # 展示所有级别常量
    logger.info("级别常量值:")
    logger.info("  DEBUG = {}", DEBUG)
    logger.info("  INFO = {}", INFO)
    logger.info("  WARNING = {}", WARNING)
    logger.info("  ERROR = {}", ERROR)
    logger.info("  CRITICAL = {}", CRITICAL)
    logger.info("  EXCEPTION = {}", EXCEPTION)
    logger.info("  DETAIL = {}", DETAIL)
    logger.info("  W_SUMMARY = {}", W_SUMMARY)
    logger.info("  W_DETAIL = {}", W_DETAIL)

    # 展示级别解析功能
    logger.info("级别名称解析:")
    test_levels = ["debug", "INFO", " Warning ", "error", "w_summary"]
    for level_name in test_levels:
        try:
            level_value = parse_level_name(level_name)
            logger.info("  '{}' -> {}", level_name, level_value)
        except ValueError as e:
            logger.error("  '{}' -> 错误: {}", level_name, e)

    # 展示级别名称获取
    logger.info("级别值转名称:")
    test_values = [DEBUG, INFO, WARNING, ERROR, W_SUMMARY]
    for level_value in test_values:
        try:
            level_name = get_level_name(level_value)
            logger.info("  {} -> '{}'", level_value, level_name)
        except ValueError as e:
            logger.error("  {} -> 错误: {}", level_value, e)

    return


def demo_config_functionality():
    """演示config模块功能"""
    print("\n=== Config模块功能演示 ===")

    logger = get_logger("config_demo")
    logger.info("Config模块功能演示开始")

    # 展示配置信息
    from custom_logger.config import get_root_config, get_config, get_config_file_path

    # 显示配置文件路径
    config_path = get_config_file_path()
    logger.info("当前配置文件路径: {}", config_path)

    # 显示根配置信息
    root_cfg = get_root_config()
    logger.info("根配置信息:")
    logger.info("  项目名称: {}", getattr(root_cfg, 'project_name', 'unknown'))
    logger.info("  实验名称: {}", getattr(root_cfg, 'experiment_name', 'unknown'))
    logger.info("  基础目录: {}", getattr(root_cfg, 'base_dir', 'unknown'))
    logger.info("  启动时间: {}", getattr(root_cfg, 'first_start_time', 'unknown'))

    # 显示logger配置信息
    logger_cfg = get_config()
    logger.info("Logger配置信息:")
    logger.info("  全局控制台级别: {}", getattr(logger_cfg, 'global_console_level', 'unknown'))
    logger.info("  全局文件级别: {}", getattr(logger_cfg, 'global_file_level', 'unknown'))
    logger.info("  当前会话目录: {}", getattr(logger_cfg, 'current_session_dir', 'unknown'))

    # 测试模块级别配置
    from custom_logger.config import get_console_level, get_file_level
    console_level = get_console_level("config_demo")
    file_level = get_file_level("config_demo")
    logger.info("当前模块级别:")
    logger.info("  控制台级别: {}", console_level)
    logger.info("  文件级别: {}", file_level)

    return


def demo_formatter_functionality():
    """演示formatter模块功能"""
    print("\n=== Formatter模块功能演示 ===")

    logger = get_logger("formatter_demo")
    logger.info("Formatter模块功能演示开始")

    from custom_logger.formatter import (
        get_caller_info, format_elapsed_time, format_pid,
        format_log_message, get_exception_info
    )

    # 展示调用者信息获取
    module_name, line_number = get_caller_info()
    logger.info("当前调用者信息: {} 行号 {}", module_name, line_number)

    # 展示时间格式化
    start_time_iso = "2024-01-01T10:00:00"
    current_time = datetime(2024, 1, 1, 11, 30, 45, 500000)
    elapsed_str = format_elapsed_time(start_time_iso, current_time)
    logger.info("时间格式化示例: {}", elapsed_str)

    # 展示PID格式化
    import os
    current_pid = os.getpid()
    formatted_pid = format_pid(current_pid)
    logger.info("PID格式化: '{}'", formatted_pid)

    # 展示消息格式化
    message = "用户 {} 有 {count} 条消息"
    args = ("测试用户",)
    kwargs = {"count": 42}
    formatted_msg = format_log_message("INFO", message, "test", args, kwargs)
    logger.info("消息格式化结果: {}", formatted_msg)

    # 展示异常信息获取
    try:
        raise ValueError("演示异常")
    except ValueError:
        exc_info = get_exception_info()
        logger.info("异常信息获取成功，长度: {} 字符", len(exc_info) if exc_info else 0)

    return


def demo_writer_functionality():
    """演示writer模块功能"""
    print("\n=== Writer模块功能演示 ===")

    logger = get_logger("writer_demo")
    logger.info("Writer模块功能演示开始")

    # 展示异步写入功能
    logger.info("测试异步文件写入功能")

    # 记录大量日志测试异步写入
    start_write = time.time()
    for i in range(100):
        logger.info("异步写入测试消息 {:,}", i + 1)

    end_write = time.time()
    write_duration = end_write - start_write
    logger.info("100条日志记录耗时: {:.3f}秒", write_duration)

    # 测试不同级别的文件写入
    logger.debug("DEBUG级别 - 应写入完整日志")
    logger.info("INFO级别 - 应写入完整日志")
    logger.warning("WARNING级别 - 应写入完整日志")
    logger.error("ERROR级别 - 应写入完整和错误日志")
    logger.critical("CRITICAL级别 - 应写入完整和错误日志")

    return


def demo_logger_functionality():
    """演示logger模块功能"""
    print("\n=== Logger模块功能演示 ===")

    # 测试不同配置的logger
    debug_logger = get_logger("debug_test", console_level="debug", file_level="debug")
    warning_logger = get_logger("warning_test", console_level="warning", file_level="error")
    worker_logger = get_logger("worker_test", console_level="w_summary", file_level="w_detail")

    debug_logger.info("Debug Logger测试开始")

    # 测试级别属性
    debug_logger.info("Debug Logger级别:")
    debug_logger.info("  控制台级别: {}", debug_logger.console_level)
    debug_logger.info("  文件级别: {}", debug_logger.file_level)

    # 测试级别判断功能
    from custom_logger.types import DEBUG, INFO, WARNING, ERROR
    debug_logger.info("级别判断测试:")
    debug_logger.info("  应记录DEBUG到控制台: {}", debug_logger._should_log_console(DEBUG))
    debug_logger.info("  应记录INFO到控制台: {}", debug_logger._should_log_console(INFO))
    debug_logger.info("  应记录WARNING到文件: {}", debug_logger._should_log_file(WARNING))
    debug_logger.info("  应记录ERROR到文件: {}", debug_logger._should_log_file(ERROR))

    # 测试颜色显示功能
    debug_logger.info("颜色显示测试（不同级别）:")
    debug_logger.info("INFO级别消息 - 无颜色")
    debug_logger.warning("WARNING级别消息 - 黄色")
    debug_logger.error("ERROR级别消息 - 红色")
    debug_logger.critical("CRITICAL级别消息 - 洋红色")

    # 测试Worker级别
    worker_logger.info("Worker Logger测试:")
    worker_logger.worker_summary("Worker摘要级别测试")
    worker_logger.worker_detail("Worker详细级别测试")

    return


def demo_manager_functionality():
    """演示manager模块功能"""
    print("\n=== Manager模块功能演示 ===")

    logger = get_logger("manager_demo")
    logger.info("Manager模块功能演示开始")

    # 测试初始化状态检查
    from custom_logger.manager import is_initialized
    init_status = is_initialized()
    logger.info("日志系统初始化状态: {}", init_status)

    # 测试多个logger创建
    logger.info("创建多个不同配置的logger:")

    loggers = []
    configs = [
        ("logger1", "debug", "debug"),
        ("logger2", "info", "warning"),
        ("logger3", "warning", "error"),
        ("worker1", "w_summary", "w_detail"),
        ("worker2", "w_detail", "debug"),
    ]

    for name, console_level, file_level in configs:
        test_logger = get_logger(name, console_level=console_level, file_level=file_level)
        loggers.append(test_logger)
        logger.info("  {} - 控制台:{} 文件:{}", name, console_level, file_level)

    # 测试logger独立性
    logger.info("测试logger独立性:")
    for test_logger in loggers[:3]:  # 只测试前3个避免输出过多
        test_logger.info(f"{test_logger.name} 独立测试消息")

    return


def demo_integration_scenarios():
    """演示集成场景"""
    print("\n=== 集成场景演示 ===")

    logger = get_logger("integration_demo")
    logger.info("集成场景演示开始")

    # 场景1：多层函数调用
    def level3_function():
        l3_logger = get_logger("level3")
        l3_logger.info("第3层函数调用")
        return

    def level2_function():
        l2_logger = get_logger("level2")
        l2_logger.info("第2层函数调用")
        level3_function()
        return

    def level1_function():
        l1_logger = get_logger("level1")
        l1_logger.info("第1层函数调用")
        level2_function()
        return

    logger.info("场景1: 多层函数调用测试")
    level1_function()

    # 场景2：异常传播
    def exception_function():
        exc_logger = get_logger("exception_test")
        try:
            result = 1 / 0
        except ZeroDivisionError:
            exc_logger.exception("在exception_function中捕获异常")
            raise
        return

    logger.info("场景2: 异常传播测试")
    try:
        exception_function()
    except ZeroDivisionError:
        logger.exception("在主函数中捕获传播的异常")

    # 场景3：线程间日志记录
    results = []

    def thread_logger_test(thread_id: int):
        t_logger = get_logger(f"thread_{thread_id}")
        t_logger.info("线程 {} 开始执行", thread_id)

        for i in range(5):
            t_logger.debug("线程 {} 步骤 {}", thread_id, i + 1)
            time.sleep(0.1)

        t_logger.info("线程 {} 执行完成", thread_id)
        results.append(f"Thread-{thread_id}")
        return

    logger.info("场景3: 线程间日志记录测试")
    threads = []
    for i in range(3):
        thread = threading.Thread(target=thread_logger_test, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    logger.info("线程测试完成，结果: {}", results)

    return


def create_feature_test_config():
    """创建功能测试配置"""
    config_content = """# 功能测试配置
project_name: "feature_test"
experiment_name: "specific_demos"
first_start_time: null
base_dir: "d:/logs/feature_test"

logger:
  global_console_level: "debug"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    debug_test:
      console_level: "debug"
      file_level: "debug"
    warning_test:
      console_level: "warning"
      file_level: "error"
    worker_test:
      console_level: "w_summary"
      file_level: "w_detail"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        return tmp_file.name


def main():
    """主函数"""
    print("Custom Logger 特定功能演示")
    print("=" * 60)
    print("本演示将详细展示各模块的具体功能")
    print("=" * 60)

    config_path = None

    try:
        # 创建功能测试配置
        config_path = create_feature_test_config()
        print(f"✓ 创建功能测试配置: {config_path}")

        # 初始化日志系统
        init_custom_logger_system(config_path=config_path)
        print("✓ 日志系统初始化完成")

        # 运行各模块功能演示
        demo_types_functionality()
        demo_config_functionality()
        demo_formatter_functionality()
        demo_writer_functionality()
        demo_logger_functionality()
        demo_manager_functionality()
        demo_integration_scenarios()

        print("\n" + "=" * 60)
        print("特定功能演示完成")
        print("=" * 60)
        print("✓ Types模块 - 级别定义和解析功能正常")
        print("✓ Config模块 - 配置管理功能正常")
        print("✓ Formatter模块 - 日志格式化功能正常")
        print("✓ Writer模块 - 异步文件写入功能正常")
        print("✓ Logger模块 - 日志记录核心功能正常")
        print("✓ Manager模块 - 系统管理功能正常")
        print("✓ 集成场景 - 复杂使用场景功能正常")

    except Exception as e:
        print(f"❌ 功能演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理日志系统
        tear_down_custom_logger_system()

        # 清理临时配置文件
        if config_path and os.path.exists(config_path):
            os.unlink(config_path)

        print("✓ 清理完成")


if __name__ == "__main__":
    main()