# tests/test_custom_logger/test_tc0006_manager.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import pytest
from unittest.mock import patch, MagicMock
from custom_logger.manager import (
    init_custom_logger_system, get_logger, tear_down_custom_logger_system,
    is_initialized, _initialized
)
from custom_logger.logger import CustomLogger
from custom_logger.types import DEBUG, INFO, ERROR


def test_tc0006_001_is_initialized_false():
    """测试未初始化时的状态检查"""
    # 确保未初始化
    tear_down_custom_logger_system()

    assert not is_initialized()
    pass


@patch('custom_logger.manager.init_config')
@patch('custom_logger.manager.init_writer')
@patch('atexit.register')
def test_tc0006_002_init_custom_logger_system(mock_atexit, mock_init_writer, mock_init_config):
    """测试初始化自定义日志系统"""
    # 确保未初始化
    tear_down_custom_logger_system()

    init_custom_logger_system()

    # 验证调用了必要的初始化函数
    mock_init_config.assert_called_once()
    mock_init_writer.assert_called_once()
    mock_atexit.assert_called_once()

    # 验证状态
    assert is_initialized()

    # 清理
    tear_down_custom_logger_system()
    pass


@patch('custom_logger.manager.init_config')
@patch('custom_logger.manager.init_writer')
def test_tc0006_003_init_custom_logger_system_already_initialized(mock_init_writer, mock_init_config):
    """测试重复初始化系统"""
    # 确保未初始化
    tear_down_custom_logger_system()

    # 第一次初始化
    init_custom_logger_system()

    # 第二次初始化
    init_custom_logger_system()

    # 应该只调用一次
    mock_init_config.assert_called_once()
    mock_init_writer.assert_called_once()

    # 清理
    tear_down_custom_logger_system()
    pass


@patch('custom_logger.manager.init_config', side_effect=Exception("Init error"))
def test_tc0006_004_init_custom_logger_system_failure(mock_init_config):
    """测试初始化失败"""
    # 确保未初始化
    tear_down_custom_logger_system()

    with pytest.raises(Exception, match="Init error"):
        init_custom_logger_system()

    # 失败后应该仍未初始化
    assert not is_initialized()
    pass


@patch('custom_logger.manager.shutdown_writer')
def test_tc0006_005_tear_down_custom_logger_system(mock_shutdown_writer):
    """测试清理自定义日志系统"""
    # 先初始化
    with patch('custom_logger.manager.init_config'):
        with patch('custom_logger.manager.init_writer'):
            init_custom_logger_system()

    assert is_initialized()

    # 清理
    tear_down_custom_logger_system()

    mock_shutdown_writer.assert_called_once()
    assert not is_initialized()
    pass


def test_tc0006_006_tear_down_not_initialized():
    """测试清理未初始化的系统"""
    # 确保未初始化
    tear_down_custom_logger_system()

    # 再次清理应该不报错
    tear_down_custom_logger_system()

    assert not is_initialized()
    pass


@patch('custom_logger.manager.shutdown_writer', side_effect=Exception("Shutdown error"))
def test_tc0006_007_tear_down_failure(mock_shutdown_writer):
    """测试清理失败处理"""
    # 先初始化
    with patch('custom_logger.manager.init_config'):
        with patch('custom_logger.manager.init_writer'):
            init_custom_logger_system()

    # 清理（应该不抛出异常）
    tear_down_custom_logger_system()

    # 状态应该被重置
    assert not is_initialized()
    pass


@patch('custom_logger.manager.get_config')
@patch('custom_logger.manager.parse_level_name')
def test_tc0006_008_get_logger_basic(mock_parse_level, mock_get_config):
    """测试获取基本logger"""
    # 模拟已初始化
    with patch('custom_logger.manager._initialized', True):
        mock_parse_level.side_effect = lambda x: {"debug": DEBUG, "info": INFO}[x]

        logger = get_logger("test_logger", console_level="debug", file_level="info")

        assert isinstance(logger, CustomLogger)
        assert logger.name == "test_logger"
        assert logger._console_level == DEBUG
        assert logger._file_level == INFO
    pass


@patch('custom_logger.manager.get_config')
def test_tc0006_009_get_logger_no_levels(mock_get_config):
    """测试获取不指定级别的logger"""
    # 模拟已初始化
    with patch('custom_logger.manager._initialized', True):
        logger = get_logger("test_logger")

        assert isinstance(logger, CustomLogger)
        assert logger.name == "test_logger"
        assert logger._console_level is None
        assert logger._file_level is None
    pass


@patch('custom_logger.manager.get_config', side_effect=RuntimeError("Not initialized"))
@patch('custom_logger.manager.init_custom_logger_system')
def test_tc0006_010_get_logger_auto_init(mock_init, mock_get_config):
    """测试自动初始化logger系统"""
    # 模拟未初始化
    with patch('custom_logger.manager._initialized', False):
        # 第一次调用get_config失败，第二次成功
        mock_get_config.side_effect = [RuntimeError("Not initialized"), None]

        logger = get_logger("test_logger")

        # 应该自动初始化
        mock_init.assert_called_once()
        assert isinstance(logger, CustomLogger)
    pass


@patch('custom_logger.manager.get_config')
@patch('custom_logger.manager.parse_level_name', side_effect=ValueError("Invalid level"))
def test_tc0006_011_get_logger_invalid_level(mock_parse_level, mock_get_config):
    """测试无效级别参数"""
    # 模拟已初始化
    with patch('custom_logger.manager._initialized', True):
        with pytest.raises(ValueError, match="Invalid level"):
            get_logger("test_logger", console_level="invalid")
    pass


@patch('custom_logger.manager.get_config')
@patch('custom_logger.manager.parse_level_name')
def test_tc0006_012_get_logger_console_level_only(mock_parse_level, mock_get_config):
    """测试只指定控制台级别"""
    # 模拟已初始化
    with patch('custom_logger.manager._initialized', True):
        mock_parse_level.return_value = ERROR

        logger = get_logger("test_logger", console_level="error")

        assert logger._console_level == ERROR
        assert logger._file_level is None
        mock_parse_level.assert_called_once_with("error")
    pass


@patch('custom_logger.manager.get_config')
@patch('custom_logger.manager.parse_level_name')
def test_tc0006_013_get_logger_file_level_only(mock_parse_level, mock_get_config):
    """测试只指定文件级别"""
    # 模拟已初始化
    with patch('custom_logger.manager._initialized', True):
        mock_parse_level.return_value = DEBUG

        logger = get_logger("test_logger", file_level="debug")

        assert logger._console_level is None
        assert logger._file_level == DEBUG
        mock_parse_level.assert_called_once_with("debug")
    pass


@patch('custom_logger.manager.get_config')
@patch('custom_logger.manager.parse_level_name')
def test_tc0006_014_get_logger_both_levels(mock_parse_level, mock_get_config):
    """测试指定两个级别"""
    # 模拟已初始化
    with patch('custom_logger.manager._initialized', True):
        mock_parse_level.side_effect = [INFO, ERROR]  # 按调用顺序返回

        logger = get_logger("test_logger", console_level="info", file_level="error")

        assert logger._console_level == INFO
        assert logger._file_level == ERROR
        assert mock_parse_level.call_count == 2
    pass


def test_tc0006_015_get_logger_empty_name():
    """测试空名称logger"""
    # 模拟已初始化
    with patch('custom_logger.manager._initialized', True):
        with patch('custom_logger.manager.get_config'):
            logger = get_logger("")

            assert logger.name == ""
    pass


def test_tc0006_016_get_logger_unicode_name():
    """测试Unicode名称logger"""
    # 模拟已初始化
    with patch('custom_logger.manager._initialized', True):
        with patch('custom_logger.manager.get_config'):
            logger = get_logger("测试模块")

            assert logger.name == "测试模块"
    pass


def test_tc0006_017_get_logger_long_name():
    """测试长名称logger"""
    long_name = "a" * 100

    # 模拟已初始化
    with patch('custom_logger.manager._initialized', True):
        with patch('custom_logger.manager.get_config'):
            logger = get_logger(long_name)

            assert logger.name == long_name
    pass


@patch('custom_logger.manager.get_config')
@patch('custom_logger.manager.parse_level_name')
def test_tc0006_018_get_logger_case_sensitive_levels(mock_parse_level, mock_get_config):
    """测试级别名称大小写处理"""
    # 模拟已初始化
    with patch('custom_logger.manager._initialized', True):
        mock_parse_level.return_value = INFO

        # 测试不同大小写
        logger = get_logger("test", console_level="INFO")

        mock_parse_level.assert_called_with("INFO")
        assert logger._console_level == INFO
    pass


def test_tc0006_019_multiple_loggers():
    """测试创建多个logger"""
    # 模拟已初始化
    with patch('custom_logger.manager._initialized', True):
        with patch('custom_logger.manager.get_config'):
            logger1 = get_logger("module1")
            logger2 = get_logger("module2")
            logger3 = get_logger("module1")  # 同名

            assert logger1.name == "module1"
            assert logger2.name == "module2"
            assert logger3.name == "module1"

            # 应该是不同的实例
            assert logger1 is not logger3
    pass


@patch('custom_logger.manager.init_config')
@patch('custom_logger.manager.init_writer')
def test_tc0006_020_initialization_state_consistency(mock_init_writer, mock_init_config):
    """测试初始化状态一致性"""
    # 确保开始时未初始化
    tear_down_custom_logger_system()
    assert not is_initialized()

    # 初始化
    init_custom_logger_system()
    assert is_initialized()

    # 清理
    tear_down_custom_logger_system()
    assert not is_initialized()

    # 再次初始化
    init_custom_logger_system()
    assert is_initialized()

    # 最终清理
    tear_down_custom_logger_system()
    pass