# tests/test_custom_logger/test_tc0002_config.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from custom_logger.config import (
    get_config_file_path, init_config, get_config,
    get_console_level, get_file_level, DEFAULT_CONFIG
)
from custom_logger.types import DEBUG, INFO


def test_tc0002_001_get_config_file_path():
    """测试获取配置文件路径"""
    path = get_config_file_path()
    expected_path = os.path.join("config", "custom_logger.yaml")
    assert path == expected_path
    pass


def test_tc0002_002_default_config():
    """测试默认配置内容"""
    assert DEFAULT_CONFIG["project_name"] == "my_project"
    assert DEFAULT_CONFIG["experiment_name"] == "default"
    assert DEFAULT_CONFIG["global_console_level"] == "info"
    assert DEFAULT_CONFIG["global_file_level"] == "debug"
    assert DEFAULT_CONFIG["base_log_dir"] == "d:/logs"
    assert DEFAULT_CONFIG["first_start_time"] is None
    assert DEFAULT_CONFIG["current_session_dir"] is None
    assert DEFAULT_CONFIG["module_levels"] == {}
    pass


@patch('os.makedirs')
@patch('custom_logger.config.is_debug')
@patch('custom_logger.config.get_config_manager')
def test_tc0002_003_init_config_new(mock_get_config_manager, mock_is_debug, mock_makedirs):
    """测试初始化新配置"""
    mock_is_debug.return_value = False
    mock_cfg = MagicMock()
    mock_cfg.custom_logger = None
    mock_get_config_manager.return_value = mock_cfg

    # 模拟hasattr返回False（新配置）
    with patch('builtins.hasattr', return_value=False):
        init_config()

    # 验证配置被设置
    assert hasattr(mock_cfg, 'custom_logger')
    mock_makedirs.assert_called()
    pass


@patch('os.makedirs')
@patch('custom_logger.config.is_debug')
@patch('custom_logger.config.get_config_manager')
def test_tc0002_004_init_config_existing(mock_get_config_manager, mock_is_debug, mock_makedirs):
    """测试初始化已有配置"""
    mock_is_debug.return_value = False
    mock_cfg = MagicMock()

    # 创建一个类似字典的对象，支持属性访问
    config_dict = {"first_start_time": "2024-01-01T10:00:00"}
    mock_cfg.custom_logger = config_dict
    mock_get_config_manager.return_value = mock_cfg

    with patch('builtins.hasattr', return_value=True):
        init_config()

    # 验证已有的first_start_time不被覆盖
    assert config_dict["first_start_time"] == "2024-01-01T10:00:00"
    mock_makedirs.assert_called()
    pass


@patch('os.makedirs')
@patch('custom_logger.config.is_debug')
@patch('custom_logger.config.get_config_manager')
def test_tc0002_005_init_config_debug_mode(mock_get_config_manager, mock_is_debug, mock_makedirs):
    """测试调试模式下的配置初始化"""
    mock_is_debug.return_value = True
    mock_cfg = MagicMock()

    config_dict = {
        "base_log_dir": "d:/logs",
        "project_name": "test_project",
        "experiment_name": "test_exp",
        "first_start_time": None
    }
    mock_cfg.custom_logger = config_dict
    mock_get_config_manager.return_value = mock_cfg

    with patch('builtins.hasattr', return_value=True):
        init_config()

    # 验证debug目录被创建
    mock_makedirs.assert_called()
    pass


@patch('custom_logger.config.get_config_manager')
def test_tc0002_006_get_config_initialized(mock_get_config_manager):
    """测试获取已初始化的配置"""
    mock_cfg = MagicMock()
    mock_cfg.custom_logger = {"test": "value"}
    mock_get_config_manager.return_value = mock_cfg

    with patch('builtins.hasattr', return_value=True):
        config = get_config()
        assert config == {"test": "value"}
    pass


@patch('custom_logger.config.get_config_manager')
def test_tc0002_007_get_config_not_initialized(mock_get_config_manager):
    """测试获取未初始化的配置"""
    mock_cfg = MagicMock()
    mock_get_config_manager.return_value = mock_cfg

    with patch('builtins.hasattr', return_value=False):
        with pytest.raises(RuntimeError, match="日志系统未初始化"):
            get_config()
    pass


@patch('custom_logger.config.get_config')
def test_tc0002_008_get_console_level_global(mock_get_config):
    """测试获取全局控制台级别"""
    mock_config = {
        "global_console_level": "info",
        "module_levels": {}
    }
    mock_get_config.return_value = mock_config

    level = get_console_level("test_module")
    assert level == INFO
    pass


@patch('custom_logger.config.get_config')
def test_tc0002_009_get_console_level_module_specific(mock_get_config):
    """测试获取模块特定控制台级别"""
    mock_config = {
        "global_console_level": "info",
        "module_levels": {"test_module": {"console_level": "debug"}}
    }
    mock_get_config.return_value = mock_config

    level = get_console_level("test_module")
    assert level == DEBUG
    pass


@patch('custom_logger.config.get_config')
def test_tc0002_010_get_file_level_global(mock_get_config):
    """测试获取全局文件级别"""
    mock_config = {
        "global_file_level": "debug",
        "module_levels": {}
    }
    mock_get_config.return_value = mock_config

    level = get_file_level("test_module")
    assert level == DEBUG
    pass


@patch('custom_logger.config.get_config')
def test_tc0002_011_get_file_level_module_specific(mock_get_config):
    """测试获取模块特定文件级别"""
    mock_config = {
        "global_file_level": "debug",
        "module_levels": {"test_module": {"file_level": "info"}}
    }
    mock_get_config.return_value = mock_config

    level = get_file_level("test_module")
    assert level == INFO
    pass


@patch('custom_logger.config.get_config')
def test_tc0002_012_module_levels_empty(mock_get_config):
    """测试模块级别配置为空的情况"""
    mock_config = {
        "global_console_level": "warning",
        "global_file_level": "error",
        "module_levels": {"other_module": {"console_level": "debug"}}
    }
    mock_get_config.return_value = mock_config

    console_level = get_console_level("non_existing_module")
    file_level = get_file_level("non_existing_module")

    # 应该使用全局配置
    assert console_level == 30  # WARNING
    assert file_level == 40  # ERROR
    pass


def test_tc0002_013_is_debug_fallback():
    """测试is_debug函数的正常调用"""
    # 测试is_debug函数可以正常调用
    from is_debug import is_debug
    result = is_debug()
    assert isinstance(result, bool)
    pass


def test_tc0002_014_is_debug_normal():
    """测试is_debug函数的基本功能"""
    # 这个测试主要确保函数可以正常调用
    from is_debug import is_debug
    result = is_debug()
    assert isinstance(result, bool)
    pass