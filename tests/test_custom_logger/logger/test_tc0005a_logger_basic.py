# tests/test_custom_logger/logger/test_tc0005a_logger_basic.py
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


def test_tc0005_001_logger_creation():
    """测试logger创建"""
    logger = CustomLogger("test_logger")

    assert logger.name == "test_logger"
    assert logger._console_level is None
    assert logger._file_level is None
    pass


def test_tc0005_002_logger_creation_with_levels():
    """测试带级别的logger创建"""
    logger = CustomLogger("test_logger", console_level=DEBUG, file_level=ERROR)

    assert logger.name == "test_logger"
    assert logger._console_level == DEBUG
    assert logger._file_level == ERROR
    pass


@patch('custom_logger.logger.get_console_level')
def test_tc0005_003_console_level_property_default(mock_get_console_level):
    """测试控制台级别属性（使用默认配置）"""
    mock_get_console_level.return_value = INFO

    logger = CustomLogger("test_logger")
    level = logger.console_level

    assert level == INFO
    mock_get_console_level.assert_called_once_with("test_logger")
    pass


def test_tc0005_004_console_level_property_custom():
    """测试控制台级别属性（使用自定义级别）"""
    logger = CustomLogger("test_logger", console_level=WARNING)
    level = logger.console_level

    assert level == WARNING
    pass


@patch('custom_logger.logger.get_file_level')
def test_tc0005_005_file_level_property_default(mock_get_file_level):
    """测试文件级别属性（使用默认配置）"""
    mock_get_file_level.return_value = DEBUG

    logger = CustomLogger("test_logger")
    level = logger.file_level

    assert level == DEBUG
    mock_get_file_level.assert_called_once_with("test_logger")
    pass


def test_tc0005_006_file_level_property_custom():
    """测试文件级别属性（使用自定义级别）"""
    logger = CustomLogger("test_logger", file_level=ERROR)
    level = logger.file_level

    assert level == ERROR
    pass


def test_tc0005_007_should_log_console():
    """测试是否应该输出到控制台的判断"""
    logger = CustomLogger("test_logger", console_level=WARNING)

    assert not logger._should_log_console(DEBUG)
    assert not logger._should_log_console(INFO)
    assert logger._should_log_console(WARNING)
    assert logger._should_log_console(ERROR)
    assert logger._should_log_console(CRITICAL)
    pass


def test_tc0005_008_should_log_file():
    """测试是否应该输出到文件的判断"""
    logger = CustomLogger("test_logger", file_level=ERROR)

    assert not logger._should_log_file(DEBUG)
    assert not logger._should_log_file(INFO)
    assert not logger._should_log_file(WARNING)
    assert logger._should_log_file(ERROR)
    assert logger._should_log_file(CRITICAL)
    pass


def test_tc0005_009_level_colors_constant():
    """测试级别颜色常量"""
    # 由于颜色会根据终端类型变化，我们测试结构而不是具体值
    assert isinstance(LEVEL_COLORS, dict)
    assert WARNING in LEVEL_COLORS
    assert ERROR in LEVEL_COLORS
    assert CRITICAL in LEVEL_COLORS
    assert EXCEPTION in LEVEL_COLORS

    # 确保所有颜色都不相同
    colors = list(LEVEL_COLORS.values())
    assert len(colors) == len(set(colors)), "所有级别应该有不同的颜色"
    pass


def test_tc0005_010_colors_constant():
    """测试颜色常量"""
    assert Colors.RED == '\033[31m'
    assert Colors.YELLOW == '\033[33m'
    assert Colors.MAGENTA == '\033[35m'
    assert Colors.RESET == '\033[0m'
    assert Colors.BRIGHT_RED == '\033[91m'

    # 测试PyCharm专用颜色
    assert Colors.PYCHARM_YELLOW == '\033[93m'
    assert Colors.PYCHARM_RED == '\033[91m'
    assert Colors.PYCHARM_MAGENTA == '\033[95m'
    assert Colors.PYCHARM_BRIGHT_RED == '\033[1;31m'
    pass