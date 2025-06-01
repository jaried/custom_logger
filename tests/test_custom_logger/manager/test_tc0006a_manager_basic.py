# tests/test_custom_logger/manager/test_tc0006a_manager_basic.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
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
def test_tc0006_002_init_custom_logger_system_default(mock_atexit, mock_init_writer, mock_init_config):
    """测试初始化自定义日志系统（默认配置）"""
    # 确保未初始化
    tear_down_custom_logger_system()

    init_custom_logger_system()

    # 验证调用了必要的初始化函数
    mock_init_config.assert_called_once_with(None)
    mock_init_writer.assert_called_once()
    mock_atexit.assert_called_once()

    # 验证状态
    assert is_initialized()

    # 清理
    tear_down_custom_logger_system()
    pass


@patch('custom_logger.manager.init_config')
@patch('custom_logger.manager.init_writer')
@patch('atexit.register')
def test_tc0006_003_init_custom_logger_system_custom_path(mock_atexit, mock_init_writer, mock_init_config):
    """测试使用自定义配置路径初始化系统"""
    # 确保未初始化
    tear_down_custom_logger_system()

    custom_path = "test/custom_config.yaml"
    init_custom_logger_system(config_path=custom_path)

    # 验证调用了必要的初始化函数，并传递了配置路径
    mock_init_config.assert_called_once_with(custom_path)
    mock_init_writer.assert_called_once()
    mock_atexit.assert_called_once()

    # 验证状态
    assert is_initialized()

    # 清理
    tear_down_custom_logger_system()
    pass


@patch('custom_logger.manager.init_config')
@patch('custom_logger.manager.init_writer')
def test_tc0006_004_init_custom_logger_system_already_initialized(mock_init_writer, mock_init_config):
    """测试重复初始化系统"""
    # 确保未初始化
    tear_down_custom_logger_system()

    # 第一次初始化
    init_custom_logger_system()

    # 第二次初始化
    init_custom_logger_system("another/path.yaml")

    # 应该只调用一次，且忽略第二次的参数
    mock_init_config.assert_called_once()
    mock_init_writer.assert_called_once()

    # 清理
    tear_down_custom_logger_system()
    pass


@patch('custom_logger.manager.init_config', side_effect=Exception("Init error"))
def test_tc0006_005_init_custom_logger_system_failure(mock_init_config):
    """测试初始化失败"""
    # 确保未初始化
    tear_down_custom_logger_system()

    with pytest.raises(Exception, match="Init error"):
        init_custom_logger_system()

    # 失败后应该仍未初始化
    assert not is_initialized()
    pass


@patch('custom_logger.manager.shutdown_writer')
def test_tc0006_006_tear_down_custom_logger_system(mock_shutdown_writer):
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


def test_tc0006_007_tear_down_not_initialized():
    """测试清理未初始化的系统"""
    # 确保未初始化
    tear_down_custom_logger_system()

    # 再次清理应该不报错
    tear_down_custom_logger_system()

    assert not is_initialized()
    pass


@patch('custom_logger.manager.shutdown_writer', side_effect=Exception("Shutdown error"))
def test_tc0006_008_tear_down_failure(mock_shutdown_writer):
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


def test_tc0006_009_initialization_state_consistency():
    """测试初始化状态一致性"""
    # 确保开始时未初始化
    tear_down_custom_logger_system()
    assert not is_initialized()

    # 使用自定义路径初始化
    with patch('custom_logger.manager.init_config'):
        with patch('custom_logger.manager.init_writer'):
            init_custom_logger_system("custom/test.yaml")
            assert is_initialized()

    # 清理
    tear_down_custom_logger_system()
    assert not is_initialized()

    # 再次初始化（默认路径）
    with patch('custom_logger.manager.init_config'):
        with patch('custom_logger.manager.init_writer'):
            init_custom_logger_system()
            assert is_initialized()

    # 最终清理
    tear_down_custom_logger_system()
    pass


def test_tc0006_010_config_path_parameter_validation():
    """测试配置路径参数验证"""
    tear_down_custom_logger_system()

    with patch('custom_logger.manager.init_config') as mock_init_config:
        with patch('custom_logger.manager.init_writer'):
            # 测试None参数
            init_custom_logger_system(config_path=None)
            mock_init_config.assert_called_with(None)

            tear_down_custom_logger_system()

            # 测试空字符串
            init_custom_logger_system(config_path="")
            mock_init_config.assert_called_with("")

            tear_down_custom_logger_system()

            # 测试正常路径
            init_custom_logger_system(config_path="valid/path.yaml")
            mock_init_config.assert_called_with("valid/path.yaml")

            tear_down_custom_logger_system()
    pass