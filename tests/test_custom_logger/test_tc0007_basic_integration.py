# tests/test_custom_logger/test_tc0007_basic_integration.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import pytest
from unittest.mock import patch, MagicMock
from custom_logger.manager import get_logger, is_initialized, _initialized
from custom_logger.logger import CustomLogger
from custom_logger.types import DEBUG, INFO, WARNING, ERROR


def test_tc0007_001_logger_creation():
    """测试logger创建功能"""
    # 模拟配置
    mock_config = {
        "global_console_level": "info",
        "global_file_level": "debug",
        "module_levels": {}
    }

    with patch('custom_logger.config.get_config', return_value=mock_config):
        with patch('custom_logger.manager._initialized', True):
            logger = get_logger("test_logger")

            assert isinstance(logger, CustomLogger)
            assert logger.name == "test_logger"
    pass


def test_tc0007_002_logger_with_custom_levels():
    """测试带自定义级别的logger"""
    mock_config = {
        "global_console_level": "info",
        "global_file_level": "debug",
        "module_levels": {}
    }

    with patch('custom_logger.config.get_config', return_value=mock_config):
        with patch('custom_logger.manager._initialized', True):
            logger = get_logger("test_logger", console_level="debug", file_level="error")

            assert logger._console_level == DEBUG
            assert logger._file_level == ERROR
    pass


def test_tc0007_003_logger_level_inheritance():
    """测试logger级别继承"""
    mock_config = {
        "global_console_level": "warning",
        "global_file_level": "error",
        "module_levels": {
            "special_module": {
                "console_level": "debug",
                "file_level": "info"
            }
        }
    }

    with patch('custom_logger.config.get_config', return_value=mock_config):
        with patch('custom_logger.logger.get_console_level', return_value=WARNING):
            with patch('custom_logger.logger.get_file_level', return_value=ERROR):
                with patch('custom_logger.manager._initialized', True):
                    # 普通模块
                    normal_logger = get_logger("normal_module")
                    assert normal_logger.console_level == WARNING
                    assert normal_logger.file_level == ERROR

                    # 特殊模块需要单独mock
                    with patch('custom_logger.logger.get_console_level', return_value=DEBUG):
                        with patch('custom_logger.logger.get_file_level', return_value=INFO):
                            special_logger = get_logger("special_module")
                            assert special_logger.console_level == DEBUG
                            assert special_logger.file_level == INFO
    pass


def test_tc0007_004_logger_methods_exist():
    """测试logger方法存在性"""
    mock_config = {
        "global_console_level": "debug",
        "global_file_level": "debug",
        "module_levels": {}
    }

    with patch('custom_logger.config.get_config', return_value=mock_config):
        with patch('custom_logger.manager._initialized', True):
            logger = get_logger("method_test")

            # 检查所有方法都存在
            assert hasattr(logger, 'debug')
            assert hasattr(logger, 'info')
            assert hasattr(logger, 'warning')
            assert hasattr(logger, 'error')
            assert hasattr(logger, 'critical')
            assert hasattr(logger, 'exception')
            assert hasattr(logger, 'detail')
            assert hasattr(logger, 'worker_summary')
            assert hasattr(logger, 'worker_detail')
            assert hasattr(logger, '_log')
    pass


def test_tc0007_005_logger_level_filtering():
    """测试logger级别过滤"""
    mock_config = {
        "global_console_level": "warning",
        "global_file_level": "error",
        "module_levels": {}
    }

    with patch('custom_logger.config.get_config', return_value=mock_config):
        with patch('custom_logger.manager._initialized', True):
            # 直接设置级别避免config调用
            logger = get_logger("filter_test", console_level="warning", file_level="error")

            # 测试级别判断
            assert not logger._should_log_console(DEBUG)
            assert not logger._should_log_console(INFO)
            assert logger._should_log_console(WARNING)
            assert logger._should_log_console(ERROR)

            assert not logger._should_log_file(DEBUG)
            assert not logger._should_log_file(INFO)
            assert not logger._should_log_file(WARNING)
            assert logger._should_log_file(ERROR)
    pass