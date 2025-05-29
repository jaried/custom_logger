# tests/test_custom_logger/test_tc0008_advanced_integration.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import pytest
from unittest.mock import patch, MagicMock, call
from custom_logger import get_logger
from custom_logger.types import DEBUG, INFO, WARNING, ERROR, EXCEPTION


def test_tc0008_001_logger_output_mocking():
    """测试logger输出的mock"""
    mock_config = {
        "global_console_level": "debug",
        "global_file_level": "debug",
        "module_levels": {},
        "first_start_time": datetime.now().isoformat()
    }

    with patch('custom_logger.config.get_config', return_value=mock_config):
        with patch('custom_logger.formatter.get_config', return_value=mock_config):
            with patch('custom_logger.logger.get_console_level', return_value=DEBUG):
                with patch('custom_logger.logger.get_file_level', return_value=DEBUG):
                    with patch('custom_logger.manager._initialized', True):
                        logger = get_logger("output_test")

                        with patch.object(logger, '_print_to_console') as mock_console:
                            with patch('custom_logger.logger.write_log_async') as mock_file:
                                logger.info("Test message")

                                # 验证控制台输出被调用
                                mock_console.assert_called_once()
                                # 验证文件写入被调用
                                mock_file.assert_called_once()
    pass


def test_tc0008_002_logger_format_testing():
    """测试logger格式化功能"""
    mock_config = {
        "global_console_level": "debug",
        "global_file_level": "debug",
        "module_levels": {},
        "first_start_time": datetime.now().isoformat()
    }

    with patch('custom_logger.config.get_config', return_value=mock_config):
        with patch('custom_logger.formatter.get_config', return_value=mock_config):
            with patch('custom_logger.logger.get_console_level', return_value=DEBUG):
                with patch('custom_logger.logger.get_file_level', return_value=DEBUG):
                    with patch('custom_logger.manager._initialized', True):
                        logger = get_logger("format_test")

                        with patch('custom_logger.logger.create_log_line') as mock_format:
                            mock_format.return_value = "Formatted message"

                            with patch.object(logger, '_print_to_console'):
                                with patch('custom_logger.logger.write_log_async'):
                                    logger.info("Test {}", "message")

                                    # 验证格式化被调用
                                    mock_format.assert_called_once_with(
                                        "info", "Test {}", "format_test", ("message",), {}
                                    )
    pass


def test_tc0008_003_exception_logging():
    """测试异常日志记录"""
    mock_config = {
        "global_console_level": "exception",
        "global_file_level": "exception",
        "module_levels": {},
        "first_start_time": datetime.now().isoformat()
    }

    with patch('custom_logger.config.get_config', return_value=mock_config):
        with patch('custom_logger.formatter.get_config', return_value=mock_config):
            with patch('custom_logger.logger.get_console_level', return_value=EXCEPTION):
                with patch('custom_logger.logger.get_file_level', return_value=EXCEPTION):
                    with patch('custom_logger.manager._initialized', True):
                        logger = get_logger("exception_test")

                        with patch('custom_logger.logger.get_exception_info') as mock_exc:
                            mock_exc.return_value = "Exception traceback"

                            with patch.object(logger, '_print_to_console'):
                                with patch('custom_logger.logger.write_log_async') as mock_file:
                                    logger.exception("An error occurred")

                                    # 验证异常信息被获取
                                    mock_exc.assert_called_once()
                                    # 验证异步写入包含异常信息
                                    mock_file.assert_called_once()
    pass


def test_tc0008_004_worker_logging():
    """测试worker日志功能"""
    mock_config = {
        "global_console_level": "w_detail",
        "global_file_level": "w_detail",
        "module_levels": {}
    }

    with patch('custom_logger.config.get_config', return_value=mock_config):
        with patch('custom_logger.manager._initialized', True):
            logger = get_logger("worker_test", console_level="w_summary")

            with patch.object(logger, '_log') as mock_log:
                logger.worker_summary("Worker started")
                logger.worker_detail("Worker processing")

                # 验证worker方法调用了_log
                assert mock_log.call_count == 2
                calls = mock_log.call_args_list
                assert calls[0][0][0] == 5  # W_SUMMARY
                assert calls[1][0][0] == 3  # W_DETAIL
    pass


def test_tc0008_005_auto_initialization():
    """测试自动初始化"""
    mock_config = {
        "global_console_level": "info",
        "global_file_level": "debug",
        "module_levels": {}
    }

    # 模拟未初始化状态
    with patch('custom_logger.manager._initialized', False):
        with patch('custom_logger.config.get_config', side_effect=[RuntimeError("Not initialized"), mock_config]):
            with patch('custom_logger.manager.init_custom_logger_system') as mock_init:
                logger = get_logger("auto_init_test")

                # 验证自动初始化被调用
                mock_init.assert_called_once()
                assert isinstance(logger, type(get_logger("test")))
    pass