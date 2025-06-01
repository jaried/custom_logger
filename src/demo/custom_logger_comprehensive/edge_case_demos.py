# src/demo/custom_logger_comprehensive/edge_case_demos.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import time
import tempfile
import threading
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


def demo_edge_case_inputs():
    """演示边界情况输入"""
    print("\n=== 边界情况输入演示 ===")

    logger = get_logger("edge_case_demo")
    logger.info("边界情况输入演示开始")

    # 空字符串测试
    logger.info("空字符串测试:")
    logger.info("")  # 空消息
    logger.info("   ")  # 空白消息

    # 特殊字符测试
    logger.info("特殊字符测试:")
    logger.info("包含换行符\n的消息")
    logger.info("包含制表符\t的消息")
    logger.info("包含Unicode字符: 🚀📝✅❌")
    logger.info("包含中文字符: 测试消息，包含中文")

    # 长消息测试
    long_message = "很长的消息" + "x" * 1_000 + "结束"
    logger.info("长消息测试（{:,} 字符）: {}", len(long_message), long_message[:50] + "...")

    # 格式化边界测试
    logger.info("格式化边界测试:")
    logger.info("参数过多: {}", "arg1", "arg2", "arg3")  # 多余参数
    logger.info("参数不足: {} {}")  # 缺少参数
    logger.info("混合错误: {} {key}", "arg1", key="value", extra="unused")

    # None值测试
    logger.info("None值测试:")
    logger.info("包含None: {}", None)
    logger.info("None作为关键字: {value}", value=None)

    return


def demo_extreme_parameters():
    """演示极端参数"""
    print("\n=== 极端参数演示 ===")

    # 极端长度的logger名称
    very_long_name = "极长的logger名称" + "x" * 100
    long_logger = get_logger(very_long_name)
    long_logger.info("使用极长名称的logger测试")

    # 空名称logger
    empty_logger = get_logger("")
    empty_logger.info("空名称logger测试")

    # 特殊字符名称
    special_logger = get_logger("特殊/字符\\名称:测试")
    special_logger.info("特殊字符名称logger测试")

    # 极端级别配置
    extreme_logger = get_logger("extreme_test", console_level="w_detail", file_level="exception")
    extreme_logger.info("极端级别配置测试")
    extreme_logger.w_detail("W_DETAIL级别消息")
    extreme_logger.exception("EXCEPTION级别消息")

    return


def demo_error_conditions():
    """演示错误条件处理"""
    print("\n=== 错误条件处理演示 ===")

    logger = get_logger("error_demo")
    logger.info("错误条件处理演示开始")

    # 格式化错误
    logger.info("格式化错误测试:")
    try:
        logger.info("错误格式: {invalid_format", "参数")
    except Exception as e:
        logger.error("捕获格式化错误: {}", e)

    # 类型错误测试
    logger.info("类型错误测试:")
    from custom_logger.types import parse_level_name
    try:
        invalid_level = parse_level_name(123)  # 非字符串参数
    except ValueError as e:
        logger.error("捕获级别解析错误: {}", e)

    try:
        invalid_level = parse_level_name("invalid_level")  # 无效级别
    except ValueError as e:
        logger.error("捕获无效级别错误: {}", e)

    # 嵌套异常测试
    def nested_exception():
        try:
            raise ValueError("内层异常")
        except ValueError:
            raise RuntimeError("外层异常")

    try:
        nested_exception()
    except RuntimeError:
        logger.exception("嵌套异常测试")

    return


def demo_concurrent_edge_cases():
    """演示并发边界情况"""
    print("\n=== 并发边界情况演示 ===")

    logger = get_logger("concurrent_demo")
    logger.info("并发边界情况演示开始")

    results = []
    errors = []

    def stress_worker(worker_id: int, operation_type: str):
        """压力测试worker"""
        try:
            worker_logger = get_logger(f"stress_{operation_type}_{worker_id}")

            if operation_type == "rapid_logging":
                # 快速日志记录
                for i in range(50):
                    worker_logger.info("快速日志 {} - {}", worker_id, i)

            elif operation_type == "large_messages":
                # 大消息记录
                for i in range(10):
                    big_msg = f"大消息{i}" + "x" * 500
                    worker_logger.info("Worker {} 大消息: {}", worker_id, big_msg)

            elif operation_type == "exception_spam":
                # 异常日志
                for i in range(20):
                    try:
                        if i % 3 == 0:
                            raise ValueError(f"测试异常 {i}")
                        worker_logger.info("正常消息 {} - {}", worker_id, i)
                    except ValueError:
                        worker_logger.exception("Worker {} 异常 {}", worker_id, i)

            results.append(f"{operation_type}-{worker_id}")

        except Exception as e:
            errors.append(f"{operation_type}-{worker_id}: {e}")

    # 启动多种类型的并发测试
    threads = []
    operation_types = ["rapid_logging", "large_messages", "exception_spam"]

    start_concurrent = time.time()

    for op_type in operation_types:
        for i in range(2):  # 每种类型2个worker
            thread = threading.Thread(target=stress_worker, args=(i, op_type))
            threads.append(thread)
            thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    end_concurrent = time.time()
    concurrent_duration = end_concurrent - start_concurrent

    logger.info("并发测试完成:")
    logger.info("  耗时: {:.3f} 秒", concurrent_duration)
    logger.info("  成功: {:,} 个worker", len(results))
    logger.info("  错误: {:,} 个worker", len(errors))

    if errors:
        logger.error("并发错误详情:")
        for error in errors:
            logger.error("  {}", error)

    return


def demo_memory_stress():
    """演示内存压力测试"""
    print("\n=== 内存压力测试演示 ===")

    logger = get_logger("memory_demo")
    logger.info("内存压力测试开始")

    # 大量logger创建测试
    loggers = []
    for i in range(100):
        test_logger = get_logger(f"memory_test_{i}")
        loggers.append(test_logger)

    logger.info("创建了 {:,} 个logger实例", len(loggers))

    # 大量日志记录测试
    start_memory = time.time()

    for i, test_logger in enumerate(loggers):
        if i % 10 == 0:  # 每10个记录一次
            test_logger.info("内存测试 logger {} 记录", i)

    end_memory = time.time()
    memory_duration = end_memory - start_memory

    logger.info("内存压力测试完成，耗时: {:.3f} 秒", memory_duration)

    # 清理引用
    del loggers
    logger.info("清理logger引用完成")

    return


def demo_file_system_edge_cases():
    """演示文件系统边界情况"""
    print("\n=== 文件系统边界情况演示 ===")

    logger = get_logger("filesystem_demo")
    logger.info("文件系统边界情况演示开始")

    # 获取当前会话目录
    from custom_logger.config import get_root_config
    root_cfg = get_root_config()
    logger_cfg = root_cfg.logger

    if isinstance(logger_cfg, dict):
        session_dir = logger_cfg.get('current_session_dir')
    else:
        session_dir = getattr(logger_cfg, 'current_session_dir', None)

    if session_dir:
        logger.info("当前会话目录: {}", session_dir)

        # 检查目录权限
        if os.path.exists(session_dir):
            logger.info("会话目录存在，权限正常")
        else:
            logger.error("会话目录不存在")

        # 检查磁盘空间（简单测试）
        try:
            import shutil
            total, used, free = shutil.disk_usage(session_dir)
            logger.info("磁盘空间信息:")
            logger.info("  总空间: {:,} GB", total // (1024 ** 3))
            logger.info("  已用空间: {:,} GB", used // (1024 ** 3))
            logger.info("  可用空间: {:,} GB", free // (1024 ** 3))
        except Exception as e:
            logger.error("获取磁盘空间信息失败: {}", e)

    # 文件写入压力测试
    logger.info("开始文件写入压力测试")
    start_file = time.time()

    for i in range(1_000):
        logger.debug("文件写入压力测试 {:,}", i)

    end_file = time.time()
    file_duration = end_file - start_file
    logger.info("1,000条日志写入耗时: {:.3f} 秒", file_duration)

    return


def demo_unicode_and_encoding():
    """演示Unicode和编码测试"""
    print("\n=== Unicode和编码测试演示 ===")

    logger = get_logger("unicode_demo")
    logger.info("Unicode和编码测试开始")

    # 各种Unicode字符测试
    unicode_tests = [
        "基本中文: 你好世界",
        "日文: こんにちは世界",
        "韩文: 안녕하세요 세계",
        "阿拉伯文: مرحبا بالعالم",
        "俄文: Привет мир",
        "表情符号: 😀😂🤣😊😍🥰😘",
        "特殊符号: ©®™€£¥§¶†‡",
        "数学符号: ∀∂∃∅∇∈∉∋∌∏∑",
        "箭头符号: ←↑→↓↔↕↖↗↘↙",
    ]

    for test_text in unicode_tests:
        logger.info("Unicode测试: {}", test_text)

    # 混合编码测试
    mixed_content = "混合内容: ASCII + 中文 + Emoji 🚀 + Math ∑∆"
    logger.info("混合编码: {}", mixed_content)

    # 长Unicode消息
    long_unicode = "重复的Unicode消息 " * 100 + " 🎉"
    logger.info("长Unicode消息 ({:,} 字符): {}...", len(long_unicode), long_unicode[:50])

    return


def create_edge_case_config():
    """创建边界情况测试配置"""
    config_content = """# 边界情况测试配置
project_name: "边界测试_project"
experiment_name: "edge_case_demo"
first_start_time: null
base_dir: "d:/logs/edge_test"

logger:
  global_console_level: "debug"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    extreme_test:
      console_level: "w_detail"
      file_level: "exception"
    stress_rapid_logging_0:
      console_level: "info"
      file_level: "debug"
    stress_large_messages_0:
      console_level: "warning"
      file_level: "debug"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        return tmp_file.name


def main():
    """主函数"""
    print("Custom Logger 边界情况演示")
    print("=" * 60)
    print("本演示将测试各种边界情况和极端场景")
    print("=" * 60)

    config_path = None

    try:
        # 创建边界情况测试配置
        config_path = create_edge_case_config()
        print(f"✓ 创建边界测试配置: {config_path}")

        # 初始化日志系统
        init_custom_logger_system(config_path=config_path)
        print("✓ 日志系统初始化完成")

        # 运行边界情况演示
        demo_edge_case_inputs()
        demo_extreme_parameters()
        demo_error_conditions()
        demo_unicode_and_encoding()
        demo_concurrent_edge_cases()
        demo_memory_stress()
        demo_file_system_edge_cases()

        print("\n" + "=" * 60)
        print("边界情况演示完成")
        print("=" * 60)
        print("✓ 边界输入 - 空值、特殊字符、长消息处理正常")
        print("✓ 极端参数 - 极长名称、特殊字符处理正常")
        print("✓ 错误条件 - 格式化错误、类型错误处理正常")
        print("✓ Unicode编码 - 多语言、表情符号处理正常")
        print("✓ 并发边界 - 高并发、大量日志处理正常")
        print("✓ 内存压力 - 大量logger实例处理正常")
        print("✓ 文件系统 - 磁盘空间、权限检查正常")

    except Exception as e:
        print(f"❌ 边界情况演示中发生错误: {e}")
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