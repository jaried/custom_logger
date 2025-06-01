# tests/test_custom_logger/logger/test_tc0005d_logger_advanced.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# 使用相对导入避免路径问题
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from custom_logger.logger import (
    CustomLogger, Colors, LEVEL_COLORS, _enable_windows_ansi_support,
    _COLOR_SUPPORT, _detect_terminal_type, _TERMINAL_TYPE
)
from custom_logger.types import (
    DEBUG, INFO, WARNING, ERROR, CRITICAL, EXCEPTION,
    DETAIL, W_SUMMARY, W_DETAIL
)


def test_tc0005_034_log_level_filtering():
    """测试日志级别过滤"""
    logger = CustomLogger("test_logger", console_level=WARNING, file_level=ERROR)

    with patch.object(logger, '_print_to_console') as mock_print:
        with patch('custom_logger.logger.write_log_async') as mock_write:
            with patch('custom_logger.logger.create_log_line', return_value="log line"):
                # DEBUG级别：不应输出到控制台和文件
                logger._log(DEBUG, "Debug message")
                mock_print.assert_not_called()
                mock_write.assert_not_called()

                # WARNING级别：应输出到控制台，不输出到文件
                logger._log(WARNING, "Warning message")
                assert mock_print.call_count == 1
                mock_write.assert_not_called()

                # ERROR级别：应输出到控制台和文件
                logger._log(ERROR, "Error message")
                assert mock_print.call_count == 2
                assert mock_write.call_count == 1
    pass


def test_tc0005_035_log_with_no_args():
    """测试无参数的日志记录"""
    logger = CustomLogger("test_logger", console_level=DEBUG, file_level=DEBUG)

    with patch.object(logger, '_log') as mock_log:
        logger.info("Simple message")

    mock_log.assert_called_once_with(INFO, "Simple message")
    pass


def test_tc0005_036_log_with_mixed_args():
    """测试混合参数的日志记录"""
    logger = CustomLogger("test_logger", console_level=DEBUG, file_level=DEBUG)

    with patch.object(logger, '_log') as mock_log:
        logger.error("Error: {} in {}", "ValueError", "module.py", context="test", severity="high")

    mock_log.assert_called_once_with(
        ERROR, "Error: {} in {}", "ValueError", "module.py",
        context="test", severity="high"
    )
    pass


def test_tc0005_037_early_filtering():
    """测试早期过滤功能"""
    logger = CustomLogger("test_logger", console_level=ERROR, file_level=ERROR)

    # Mock所有可能被调用的函数
    with patch('custom_logger.logger.create_log_line') as mock_format:
        with patch('custom_logger.logger.get_level_name') as mock_get_name:
            with patch('custom_logger.logger.write_log_async') as mock_write:
                with patch.object(logger, '_print_to_console') as mock_print:
                    # 调用被过滤的级别
                    logger._log(DEBUG, "Debug message")

                    # 验证格式化等昂贵操作没有被调用
                    mock_format.assert_not_called()
                    mock_get_name.assert_not_called()
                    mock_write.assert_not_called()
                    mock_print.assert_not_called()
    pass


def test_tc0005_038_log_early_return_both_filtered():
    """测试控制台和文件都被过滤时的早期返回"""
    logger = CustomLogger("test_logger", console_level=ERROR, file_level=CRITICAL)

    with patch('custom_logger.logger.get_level_name') as mock_get_name:
        # WARNING级别被两个都过滤
        logger._log(WARNING, "Warning message", do_print=True)

        # 验证get_level_name没有被调用（早期返回）
        mock_get_name.assert_not_called()
    pass


def test_tc0005_039_log_early_return_console_only():
    """测试只有控制台被过滤时不会早期返回"""
    logger = CustomLogger("test_logger", console_level=ERROR, file_level=DEBUG)

    with patch('custom_logger.logger.get_level_name', return_value="warning"):
        with patch('custom_logger.logger.create_log_line', return_value="log line"):
            with patch('custom_logger.logger.write_log_async') as mock_write:
                with patch.object(logger, '_print_to_console') as mock_print:
                    # WARNING级别：控制台过滤，文件不过滤
                    logger._log(WARNING, "Warning message", do_print=True)

                    # 验证文件写入被调用，控制台输出没被调用
                    mock_write.assert_called_once()
                    mock_print.assert_not_called()
    pass


def test_tc0005_040_detect_terminal_type():
    """测试终端类型检测"""
    result = _detect_terminal_type()
    assert isinstance(result, str)
    assert result in ['pycharm', 'vscode', 'ide', 'cmd', 'terminal']
    pass


def test_tc0005_041_detect_pycharm():
    """测试PyCharm环境检测"""
    # 创建只包含PyCharm变量的环境
    clean_env = {'PYCHARM_HOSTED': '1'}

    with patch.dict(os.environ, clean_env, clear=True):
        from custom_logger.logger import _detect_terminal_type
        result = _detect_terminal_type()
        assert result == 'pycharm'
    pass


def test_tc0005_042_detect_vscode():
    """测试VS Code环境检测"""
    # 清除PyCharm环境变量，只设置VS Code
    env_vars = dict(os.environ)
    # 移除PyCharm相关变量
    for key in list(env_vars.keys()):
        if 'PYCHARM' in key:
            del env_vars[key]

    # 设置VS Code变量
    env_vars['VSCODE_PID'] = '12345'

    with patch.dict(os.environ, env_vars, clear=True):
        from custom_logger.logger import _detect_terminal_type
        result = _detect_terminal_type()
        assert result == 'vscode'
    pass


def test_tc0005_043_terminal_specific_colors():
    """测试特定终端的颜色配置"""
    # 创建干净的PyCharm环境
    pycharm_env = {'PYCHARM_HOSTED': '1'}

    with patch.dict(os.environ, pycharm_env, clear=True):
        # 重新导入以应用新的终端类型
        import importlib
        import custom_logger.logger
        importlib.reload(custom_logger.logger)

        from custom_logger.logger import LEVEL_COLORS, Colors, WARNING

        # PyCharm应该使用更鲜艳的颜色
        assert WARNING in LEVEL_COLORS
        # 验证使用的是PyCharm专用颜色
        warning_color = LEVEL_COLORS[WARNING]
        assert warning_color == Colors.PYCHARM_YELLOW
    pass


def test_tc0005_044_color_support_detection():
    """测试颜色支持检测"""
    assert isinstance(_COLOR_SUPPORT, bool)
    assert isinstance(_TERMINAL_TYPE, str)
    pass