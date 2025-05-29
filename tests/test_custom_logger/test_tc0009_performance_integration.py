# tests/test_custom_logger/test_tc0009_performance_integration.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import time
import pytest
from unittest.mock import patch, MagicMock
from custom_logger import get_logger
from custom_logger.types import DEBUG, INFO, WARNING, ERROR


def test_tc0009_001_level_filtering_performance():
    """测试级别过滤性能"""
    mock_config = {
        "global_console_level": "error",  # 高级别，大部分日志被过滤
        "global_file_level": "error",
        "module_levels": {},
        "first_start_time": datetime.now().isoformat()
    }

    with patch('custom_logger.config.get_config', return_value=mock_config):
        with patch('custom_logger.formatter.get_config', return_value=mock_config):
            with patch('custom_logger.logger.get_console_level', return_value=ERROR):
                with patch('custom_logger.logger.get_file_level', return_value=ERROR):
                    with patch('custom_logger.manager._initialized', True):
                        logger = get_logger("perf_test")

                        # 测试大量被过滤的日志
                        start_time = time.time()

                        for i in range(1_000):
                            logger.debug(f"Debug message {i}")  # 被过滤
                            logger.info(f"Info message {i}")  # 被过滤

                        end_time = time.time()
                        duration = end_time - start_time

                        # 被过滤的日志应该很快
                        assert duration < 0.5  # 500ms内完成
    pass


def test_tc0009_002_multiple_loggers():
    """测试多个logger的创建"""
    mock_config = {
        "global_console_level": "info",
        "global_file_level": "debug",
        "module_levels": {}
    }

    with patch('custom_logger.config.get_config', return_value=mock_config):
        with patch('custom_logger.logger.get_console_level', return_value=INFO):
            with patch('custom_logger.manager._initialized', True):
                loggers = []

                # 创建多个logger
                for i in range(100):
                    logger = get_logger(f"logger_{i}")
                    loggers.append(logger)

                # 验证所有logger都正确创建
                assert len(loggers) == 100
                for i, logger in enumerate(loggers):
                    assert logger.name == f"logger_{i}"
                    assert logger.console_level == INFO
    pass


def test_tc0009_003_edge_case_messages():
    """测试边界情况消息"""
    mock_config = {
        "global_console_level": "debug",
        "global_file_level": "debug",
        "module_levels": {}
    }

    with patch('custom_logger.config.get_config', return_value=mock_config):
        with patch('custom_logger.manager._initialized', True):
            logger = get_logger("edge_test")

            with patch.object(logger, '_log') as mock_log:
                # 测试各种边界情况
                logger.info("")  # 空消息
                logger.info("x" * 1_000)  # 长消息
                logger.info("测试中文")  # Unicode
                logger.info("Special: \n\t\r")  # 特殊字符

                # 验证所有调用都成功
                assert mock_log.call_count == 4
    pass


def test_tc0009_004_format_edge_cases():
    """测试格式化边界情况"""
    mock_config = {
        "global_console_level": "debug",
        "global_file_level": "debug",
        "module_levels": {}
    }

    with patch('custom_logger.config.get_config', return_value=mock_config):
        with patch('custom_logger.manager._initialized', True):
            logger = get_logger("format_edge_test")

            with patch.object(logger, '_log') as mock_log:
                # 测试格式化边界情况
                logger.info("User {} has {} items", "Alice", 42)  # 正常格式化
                logger.info("Missing arg: {}", )  # 缺少参数（应该优雅处理）
                logger.info("Extra args: {}", "one", "two")  # 多余参数
                logger.info("Named: {name}", name="Bob")  # 命名参数

                # 验证所有调用都成功（即使格式化有问题）
                assert mock_log.call_count == 4
    pass


def test_tc0009_005_stress_test():
    """测试压力情况"""
    mock_config = {
        "global_console_level": "warning",
        "global_file_level": "error",
        "module_levels": {},
        "first_start_time": datetime.now().isoformat()
    }

    with patch('custom_logger.config.get_config', return_value=mock_config):
        with patch('custom_logger.formatter.get_config', return_value=mock_config):
            with patch('custom_logger.logger.get_console_level', return_value=WARNING):
                with patch('custom_logger.logger.get_file_level', return_value=ERROR):
                    with patch('custom_logger.manager._initialized', True):
                        # 创建多个logger并发日志记录
                        loggers = [get_logger(f"stress_{i}") for i in range(10)]

                        with patch('custom_logger.logger.write_log_async') as mock_write:
                            # 每个logger记录不同级别的日志
                            for i, logger in enumerate(loggers):
                                logger.debug(f"Debug from {i}")  # 被过滤
                                logger.info(f"Info from {i}")  # 被过滤
                                logger.warning(f"Warning from {i}")  # 控制台输出
                                logger.error(f"Error from {i}")  # 控制台和文件输出

                            # 只有ERROR级别的日志会写入文件
                            assert mock_write.call_count == 10  # 10个error调用
    pass