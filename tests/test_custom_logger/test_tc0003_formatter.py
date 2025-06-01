# tests/test_custom_logger/test_tc0003_formatter.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from custom_logger.formatter import (
    get_caller_info, format_elapsed_time, format_pid,
    format_log_message, create_log_line, get_exception_info
)


def test_tc0003_001_get_caller_info():
    """测试获取调用者信息"""
    # 由于这个函数依赖于调用栈，我们测试它的基本功能
    module_name, line_number = get_caller_info()

    # 应该返回当前测试文件的信息
    assert isinstance(module_name, str)
    assert isinstance(line_number, int)
    assert len(module_name) <= 8
    assert line_number > 0
    pass


def test_tc0003_002_get_caller_info_long_filename():
    """测试长文件名被截断"""
    # 模拟一个长文件名的情况
    with patch('inspect.stack') as mock_stack:
        frame_info = MagicMock()
        frame_info.filename = "/path/to/very_long_filename_that_exceeds_eight_chars.py"
        frame_info.lineno = 42
        mock_stack.return_value = [None, frame_info]  # None for current frame

        module_name, line_number = get_caller_info()

        assert len(module_name) <= 8
        # 修正期望值：当只有一个有效栈帧时，应该使用该栈帧的信息
        assert module_name == "very_lon"  # 长文件名截断
        assert line_number == 42
    pass


def test_tc0003_003_get_caller_info_exception():
    """测试获取调用者信息时发生异常"""
    with patch('inspect.stack', side_effect=Exception("Test error")):
        module_name, line_number = get_caller_info()

        assert module_name == "error"
        assert line_number == 0
    pass


def test_tc0003_004_format_elapsed_time():
    """测试格式化运行时长"""
    start_time_iso = "2024-01-01T10:00:00"
    current_time = datetime(2024, 1, 1, 11, 23, 45, 500000)

    elapsed_str = format_elapsed_time(start_time_iso, current_time)

    # 1小时23分45.5秒
    assert elapsed_str == "1:23:45.50"
    pass


def test_tc0003_005_format_elapsed_time_short():
    """测试格式化短时长"""
    start_time_iso = "2024-01-01T10:00:00"
    current_time = datetime(2024, 1, 1, 10, 2, 3, 123000)

    elapsed_str = format_elapsed_time(start_time_iso, current_time)

    # 2分3.123秒
    assert elapsed_str == "0:02:03.12"
    pass


def test_tc0003_006_format_elapsed_time_invalid():
    """测试无效时间格式"""
    elapsed_str = format_elapsed_time("invalid_time", datetime.now())

    assert elapsed_str == "0:00:00.00"
    pass


def test_tc0003_007_format_pid():
    """测试格式化进程ID"""
    # 测试不同的PID值
    assert format_pid(123) == "   123"
    assert format_pid(999999) == "999999"
    assert format_pid(1) == "     1"
    pass


def test_tc0003_008_format_log_message_simple():
    """测试简单日志消息格式化"""
    message = "Hello world"
    result = format_log_message("INFO", message, "test", (), {})

    assert result == "Hello world"
    pass


def test_tc0003_009_format_log_message_with_args():
    """测试带参数的日志消息格式化"""
    message = "User {} logged in from {}"
    args = ("alice", "127.0.0.1")
    result = format_log_message("INFO", message, "test", args, {})

    assert result == "User alice logged in from 127.0.0.1"
    pass


def test_tc0003_010_format_log_message_with_kwargs():
    """测试带关键字参数的日志消息格式化"""
    message = "User {user} has {count} messages"
    kwargs = {"user": "bob", "count": 5}
    result = format_log_message("INFO", message, "test", (), kwargs)

    assert result == "User bob has 5 messages"
    pass


def test_tc0003_011_format_log_message_format_error():
    """测试格式化错误的处理"""
    message = "User {} has {} messages"
    args = ("alice",)  # 缺少一个参数
    result = format_log_message("INFO", message, "test", args, {})

    assert "格式化错误" in result
    assert "alice" in result
    pass


@patch('custom_logger.config.get_root_config')
@patch('custom_logger.formatter.get_caller_info')
@patch('os.getpid')
def test_tc0003_012_create_log_line(mock_getpid, mock_get_caller_info, mock_get_root_config):
    """测试创建完整日志行"""
    # 设置mock
    mock_getpid.return_value = 12345
    mock_get_caller_info.return_value = ("testfile", 42)

    mock_config = MagicMock()
    mock_config.first_start_time = "2024-01-01T10:00:00"
    mock_get_root_config.return_value = mock_config

    # 固定当前时间用于测试
    with patch('custom_logger.formatter.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 1, 30, 500000)
        mock_datetime.fromisoformat = datetime.fromisoformat

        log_line = create_log_line("INFO", "Test message", "test_module", (), {})

        # 验证日志行格式
        assert "[" in log_line and "12345" in log_line
        assert "testfile" in log_line
        assert "42" in log_line
        assert "2024-01-01 10:01:30" in log_line
        assert "0:01:30.50" in log_line
        assert "INFO" in log_line
        assert "Test message" in log_line
    pass


@patch('custom_logger.config.get_root_config')
def test_tc0003_013_create_log_line_with_custom_config_path(mock_get_root_config):
    """测试使用自定义配置路径创建日志行"""
    mock_config = MagicMock()
    mock_config.first_start_time = "2024-01-01T12:00:00"
    mock_get_root_config.return_value = mock_config

    with patch('custom_logger.formatter.get_caller_info', return_value=("demo_cus", 100)):
        with patch('os.getpid', return_value=99999):
            with patch('custom_logger.formatter.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 5, 15)
                mock_datetime.fromisoformat = datetime.fromisoformat

                log_line = create_log_line("INFO", "Demo message", "demo", (), {})

                # 验证调用者正确识别
                assert "demo_cus" in log_line
                assert "  100" in log_line
                assert "Demo message" in log_line
    pass


def test_tc0003_014_get_exception_info_no_exception():
    """测试没有异常时获取异常信息"""
    result = get_exception_info()
    assert result is None
    pass


def test_tc0003_015_get_exception_info_with_exception():
    """测试有异常时获取异常信息"""
    try:
        raise ValueError("Test exception")
    except ValueError:
        result = get_exception_info()

        assert result is not None
        assert "ValueError" in result
        assert "Test exception" in result
        assert "Traceback" in result
    pass


def test_tc0003_016_get_exception_info_exception_in_function():
    """测试函数内部异常处理"""
    with patch('sys.exc_info', side_effect=Exception("Internal error")):
        result = get_exception_info()
        assert result is None
    pass


def test_tc0003_017_format_log_message_mixed_args():
    """测试混合参数的日志消息格式化"""
    message = "User {} has {count} messages and {status} status"
    args = ("charlie",)
    kwargs = {"count": 10, "status": "active"}

    result = format_log_message("INFO", message, "test", args, kwargs)
    assert result == "User charlie has 10 messages and active status"
    pass


def test_tc0003_018_format_elapsed_time_zero():
    """测试零时长格式化"""
    start_time_iso = "2024-01-01T10:00:00"
    current_time = datetime(2024, 1, 1, 10, 0, 0)

    elapsed_str = format_elapsed_time(start_time_iso, current_time)
    assert elapsed_str == "0:00:00.00"
    pass


def test_tc0003_019_caller_info_custom_logger_filter():
    """测试过滤custom_logger包内的调用"""
    with patch('inspect.stack') as mock_stack:
        # 模拟调用栈，包含custom_logger文件
        frame1 = MagicMock()
        frame1.filename = "/path/to/custom_logger/logger.py"
        frame1.lineno = 100

        frame2 = MagicMock()
        frame2.filename = "/path/to/user_code.py"
        frame2.lineno = 50

        mock_stack.return_value = [frame1, frame2]

        module_name, line_number = get_caller_info()

        # 应该跳过custom_logger包内的文件
        assert module_name == "user_cod"
        assert line_number == 50
    pass


def test_tc0003_020_create_log_line_caller_identification():
    """测试日志行中调用者识别修复"""
    with patch('custom_logger.config.get_root_config') as mock_get_root_config:
        mock_config = MagicMock()
        mock_config.first_start_time = "2024-01-01T10:00:00"
        mock_get_root_config.return_value = mock_config

        # 模拟真实的调用栈，应该能正确识别外部调用者
        with patch('custom_logger.formatter.get_caller_info') as mock_get_caller_info:
            # 直接mock get_caller_info的返回值
            mock_get_caller_info.return_value = ("demo_cus", 25)

            with patch('os.getpid', return_value=12345):
                with patch('custom_logger.formatter.datetime') as mock_datetime:
                    mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 1, 30)
                    mock_datetime.fromisoformat = datetime.fromisoformat

                    log_line = create_log_line("INFO", "Test message", "demo", (), {})

                    # 应该识别出demo_cus而不是unknown
                    assert "demo_cus" in log_line
                    assert "25" in log_line
                    assert "unknown" not in log_line
    pass