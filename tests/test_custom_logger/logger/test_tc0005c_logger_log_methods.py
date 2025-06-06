# tests/test_custom_logger/logger/test_tc0005c_logger_log_methods.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import sys
import pytest
from unittest.mock import patch, MagicMock

# 使用相对导入避免路径问题
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from custom_logger.logger import (
    CustomLogger, Colors, LEVEL_COLORS, _enable_windows_ansi_support,
    _COLOR_SUPPORT, _detect_terminal_type, _TERMINAL_TYPE
)
from custom_logger.types import (
    DEBUG, INFO, WARNING, ERROR, CRITICAL, EXCEPTION,
    DETAIL, W_SUMMARY, W_DETAIL
)


@patch('custom_logger.logger.create_log_line')
@patch('custom_logger.logger.write_log_async')
def test_tc0005_021_log_method_basic(mock_write_async, mock_create_log_line):
    """测试基本的_log方法"""
    mock_create_log_line.return_value = "Formatted log line"

    logger = CustomLogger("test_logger", console_level=INFO, file_level=DEBUG)

    with patch.object(logger, '_print_to_console') as mock_print:
        logger._log(INFO, "Test message", "arg1", do_print=True, kwarg1="value1")

    mock_create_log_line.assert_called_once_with(
        "info", "Test message", "test_logger", ("arg1",), {"kwarg1": "value1"}
    )
    mock_print.assert_called_once_with("Formatted log line", INFO)
    mock_write_async.assert_called_once_with("Formatted log line", INFO, None)
    pass


@patch('custom_logger.logger.create_log_line')
@patch('custom_logger.logger.write_log_async')
def test_tc0005_022_log_method_do_print_false(mock_write_async, mock_create_log_line):
    """测试_log方法do_print=False"""
    mock_create_log_line.return_value = "Formatted log line"

    logger = CustomLogger("test_logger", console_level=INFO, file_level=DEBUG)

    with patch.object(logger, '_print_to_console') as mock_print:
        logger._log(INFO, "Test message", do_print=False)

    # 不应该调用控制台输出
    mock_print.assert_not_called()
    # 但应该写入文件
    mock_write_async.assert_called_once()
    pass


@patch('custom_logger.logger.create_log_line')
@patch('custom_logger.logger.get_exception_info')
@patch('custom_logger.logger.write_log_async')
def test_tc0005_023_log_method_exception_level(mock_write_async, mock_get_exception, mock_create_log_line):
    """测试EXCEPTION级别的_log方法"""
    mock_create_log_line.return_value = "Exception log line"
    mock_get_exception.return_value = "Stack trace info"

    logger = CustomLogger("test_logger", console_level=EXCEPTION, file_level=DEBUG)

    with patch.object(logger, '_print_to_console') as mock_print:
        with patch('builtins.print') as mock_print_exc:
            logger._log(EXCEPTION, "Exception occurred")

    mock_get_exception.assert_called_once()
    mock_write_async.assert_called_once_with("Exception log line", EXCEPTION, "Stack trace info")
    
    # 验证异常信息输出，考虑可能包含颜色代码
    mock_print_exc.assert_called_once()
    call_args = mock_print_exc.call_args
    
    # 检查调用参数：第一个参数应该包含"Stack trace info"（可能带颜色代码），第二个参数应该是sys.stderr
    assert len(call_args[0]) == 1  # 只有一个位置参数
    assert "Stack trace info" in call_args[0][0]  # 异常信息应该包含在输出中
    assert call_args[1]['file'] == sys.stderr  # 应该输出到stderr
    pass


@patch('custom_logger.logger.get_level_name')
@patch('custom_logger.logger.create_log_line')
def test_tc0005_024_log_method_invalid_level(mock_create_log_line, mock_get_level_name):
    """测试无效级别的处理"""
    mock_get_level_name.side_effect = ValueError("Invalid level")
    mock_create_log_line.return_value = "Log line"

    logger = CustomLogger("test_logger", console_level=DEBUG, file_level=DEBUG)

    with patch.object(logger, '_print_to_console'):
        with patch('custom_logger.logger.write_log_async'):
            logger._log(999, "Invalid level message")

    # 应该使用LEVEL_999格式
    mock_create_log_line.assert_called_once()
    args = mock_create_log_line.call_args[0]
    assert args[0] == "LEVEL_999"
    pass


def test_tc0005_025_debug_method():
    """测试debug方法"""
    logger = CustomLogger("test_logger")

    with patch.object(logger, '_log') as mock_log:
        logger.debug("Debug message", "arg1", kwarg1="value1")

    mock_log.assert_called_once_with(
        DEBUG, "Debug message", "arg1", kwarg1="value1"
    )
    pass


def test_tc0005_026_info_method():
    """测试info方法"""
    logger = CustomLogger("test_logger")

    with patch.object(logger, '_log') as mock_log:
        logger.info("Info message", "arg1", kwarg1="value1")

    mock_log.assert_called_once_with(
        INFO, "Info message", "arg1", kwarg1="value1"
    )
    pass


def test_tc0005_027_warning_method():
    """测试warning方法"""
    logger = CustomLogger("test_logger")

    with patch.object(logger, '_log') as mock_log:
        logger.warning("Warning message", "arg1", kwarg1="value1")

    mock_log.assert_called_once_with(
        WARNING, "Warning message", "arg1", kwarg1="value1"
    )
    pass


def test_tc0005_028_error_method():
    """测试error方法"""
    logger = CustomLogger("test_logger")

    with patch.object(logger, '_log') as mock_log:
        logger.error("Error message", "arg1", kwarg1="value1")

    mock_log.assert_called_once_with(
        ERROR, "Error message", "arg1", kwarg1="value1"
    )
    pass


def test_tc0005_029_critical_method():
    """测试critical方法"""
    logger = CustomLogger("test_logger")

    with patch.object(logger, '_log') as mock_log:
        logger.critical("Critical message", "arg1", kwarg1="value1")

    mock_log.assert_called_once_with(
        CRITICAL, "Critical message", "arg1", kwarg1="value1"
    )
    pass


def test_tc0005_030_exception_method():
    """测试exception方法"""
    logger = CustomLogger("test_logger")

    with patch.object(logger, '_log') as mock_log:
        logger.exception("Exception message", "arg1", kwarg1="value1")

    mock_log.assert_called_once_with(
        EXCEPTION, "Exception message", "arg1", kwarg1="value1"
    )
    pass


def test_tc0005_031_detail_method():
    """测试detail方法"""
    logger = CustomLogger("test_logger")

    with patch.object(logger, '_log') as mock_log:
        logger.detail("Detail message", "arg1", kwarg1="value1")

    mock_log.assert_called_once_with(
        DETAIL, "Detail message", "arg1", kwarg1="value1"
    )
    pass


def test_tc0005_032_worker_summary_method():
    """测试worker_summary方法"""
    logger = CustomLogger("test_logger")

    with patch.object(logger, '_log') as mock_log:
        logger.worker_summary("Worker summary", "arg1", kwarg1="value1")

    mock_log.assert_called_once_with(
        W_SUMMARY, "Worker summary", "arg1", kwarg1="value1"
    )
    pass


def test_tc0005_033_worker_detail_method():
    """测试worker_detail方法"""
    logger = CustomLogger("test_logger")

    with patch.object(logger, '_log') as mock_log:
        logger.worker_detail("Worker detail", "arg1", kwarg1="value1")

    mock_log.assert_called_once_with(
        W_DETAIL, "Worker detail", "arg1", kwarg1="value1"
    )
    pass