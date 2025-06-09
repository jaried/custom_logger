# tests/test_custom_logger/test_tc0002_config.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from custom_logger.config import (
    get_config_file_path, init_config, get_config, get_root_config,
    get_console_level, get_file_level, DEFAULT_CONFIG,
    set_config_path, _cached_config_path
)
from custom_logger.types import DEBUG, INFO


def test_tc0002_001_get_config_file_path_default():
    """测试获取默认配置文件路径"""
    # 清理缓存和环境变量
    set_config_path(None)

    path = get_config_file_path()
    expected_path = os.path.join("src", "config", "config.yaml")  # 修正期望路径
    assert path == expected_path
    pass


def test_tc0002_002_default_config_structure():
    """测试默认配置结构"""
    assert DEFAULT_CONFIG["project_name"] == "my_project"
    assert DEFAULT_CONFIG["experiment_name"] == "default"
    assert DEFAULT_CONFIG['logger']["global_console_level"] == "info"
    assert DEFAULT_CONFIG['logger']["global_file_level"] == "debug"
    assert DEFAULT_CONFIG["base_dir"] == "d:/logs"
    assert DEFAULT_CONFIG["first_start_time"] is None
    assert DEFAULT_CONFIG['paths']["log_dir"] is None
    assert DEFAULT_CONFIG['logger']["module_levels"] == {}
    pass


def test_tc0002_003_set_config_path():
    """测试设置配置路径"""
    from custom_logger.config import get_cached_config_path

    test_path = "test/custom_config.yaml"

    set_config_path(test_path)

    # 验证缓存路径被设置
    assert get_cached_config_path() == test_path
    # 验证环境变量被设置
    assert os.environ.get('CUSTOM_LOGGER_CONFIG_PATH') == test_path

    # 清理
    set_config_path(None)
    assert 'CUSTOM_LOGGER_CONFIG_PATH' not in os.environ
    pass


def test_tc0002_004_get_config_file_path_with_cache():
    """测试从缓存获取配置路径"""
    test_path = "cached/config.yaml"

    set_config_path(test_path)
    path = get_config_file_path()

    assert path == test_path

    # 清理
    set_config_path(None)
    pass


def test_tc0002_005_get_config_file_path_from_env():
    """测试从环境变量获取配置路径"""
    test_path = "env/config.yaml"

    # 清理缓存但设置环境变量
    set_config_path(None)
    os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = test_path

    path = get_config_file_path()
    assert path == test_path

    # 清理
    del os.environ['CUSTOM_LOGGER_CONFIG_PATH']
    pass


@patch('os.makedirs')
@patch('custom_logger.config.is_debug')
@patch('custom_logger.config.get_config_manager')
def test_tc0002_006_init_config_with_custom_path(mock_get_config_manager, mock_is_debug, mock_makedirs):
    """测试使用自定义路径初始化配置"""
    from custom_logger.config import get_cached_config_path

    mock_is_debug.return_value = False
    mock_cfg = MagicMock()
    mock_get_config_manager.return_value = mock_cfg

    custom_path = "custom/test_config.yaml"

    # 模拟hasattr返回False（新配置）
    with patch('builtins.hasattr', return_value=False):
        init_config(custom_path)

    # 验证配置路径被设置
    assert get_cached_config_path() == custom_path
    # 验证config_manager使用了正确的路径
    mock_get_config_manager.assert_called_with(config_path=custom_path)
    mock_makedirs.assert_called()

    # 清理
    set_config_path(None)
    pass


@patch('os.makedirs')
@patch('custom_logger.config.is_debug')
@patch('custom_logger.config.get_config_manager')
def test_tc0002_007_init_config_existing(mock_get_config_manager, mock_is_debug, mock_makedirs):
    """测试初始化已有配置"""
    mock_is_debug.return_value = False
    mock_cfg = MagicMock()
    mock_cfg.first_start_time = "2024-01-01T10:00:00"
    mock_get_config_manager.return_value = mock_cfg

    with patch('builtins.hasattr', return_value=True):
        init_config()

    # 验证已有的first_start_time不被覆盖
    assert mock_cfg.first_start_time == "2024-01-01T10:00:00"
    mock_makedirs.assert_called()
    pass


@patch('custom_logger.config.get_config_manager')
def test_tc0002_008_get_config_initialized(mock_get_config_manager):
    """测试获取已初始化的配置"""
    mock_cfg = MagicMock()
    mock_logger_config = MagicMock()
    mock_cfg.logger = mock_logger_config
    mock_get_config_manager.return_value = mock_cfg

    with patch('builtins.hasattr', return_value=True):
        config = get_config()
        assert config == mock_logger_config
    pass


@patch('custom_logger.config.get_config_manager')
def test_tc0002_009_get_root_config_initialized(mock_get_config_manager):
    """测试获取根配置对象"""
    mock_cfg = MagicMock()
    mock_cfg.logger = MagicMock()
    mock_get_config_manager.return_value = mock_cfg

    with patch('builtins.hasattr', return_value=True):
        config = get_root_config()
        assert config == mock_cfg
    pass


@patch('custom_logger.config.get_config_manager')
def test_tc0002_010_get_root_config_not_initialized(mock_get_config_manager):
    """测试获取未初始化的根配置"""
    mock_cfg = MagicMock()
    mock_get_config_manager.return_value = mock_cfg

    with patch('builtins.hasattr', return_value=False):
        with pytest.raises(RuntimeError, match="日志系统未初始化"):
            get_root_config()
    pass


@patch('custom_logger.config.get_config')
def test_tc0002_011_get_console_level_global(mock_get_config):
    """测试获取全局控制台级别"""
    mock_config = MagicMock()
    mock_config.global_console_level = "info"
    mock_config.module_levels = {}
    mock_get_config.return_value = mock_config

    level = get_console_level("test_module")
    assert level == INFO
    pass


@patch('custom_logger.config.get_config')
def test_tc0002_012_get_console_level_module_specific(mock_get_config):
    """测试获取模块特定控制台级别"""
    mock_config = MagicMock()
    mock_config.global_console_level = "info"
    mock_config.module_levels = {"test_module": {"console_level": "debug"}}
    mock_get_config.return_value = mock_config

    level = get_console_level("test_module")
    assert level == DEBUG
    pass


@patch('custom_logger.config.get_config')
def test_tc0002_013_get_file_level_global(mock_get_config):
    """测试获取全局文件级别"""
    mock_config = MagicMock()
    mock_config.global_file_level = "debug"
    mock_config.module_levels = {}
    mock_get_config.return_value = mock_config

    level = get_file_level("test_module")
    assert level == DEBUG
    pass


@patch('custom_logger.config.get_config')
def test_tc0002_014_get_file_level_module_specific(mock_get_config):
    """测试获取模块特定文件级别"""
    mock_config = MagicMock()
    mock_config.global_file_level = "debug"
    mock_config.module_levels = {"test_module": {"file_level": "info"}}
    mock_get_config.return_value = mock_config

    level = get_file_level("test_module")
    assert level == INFO
    pass


def test_tc0002_015_config_path_priority():
    """测试配置路径优先级"""
    # 清理初始状态
    set_config_path(None)

    try:
        # 设置环境变量
        os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = "env/config.yaml"

        # 缓存路径应该优先于环境变量
        set_config_path("cache/config.yaml")
        assert get_config_file_path() == "cache/config.yaml"

        # 清理缓存，应该使用环境变量
        set_config_path(None)
        # 手动重新设置环境变量，因为set_config_path(None)会清理它
        os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = "env/config.yaml"
        assert get_config_file_path() == "env/config.yaml"

        # 清理环境变量，应该使用默认路径
        if 'CUSTOM_LOGGER_CONFIG_PATH' in os.environ:
            del os.environ['CUSTOM_LOGGER_CONFIG_PATH']
        expected_default = os.path.join("src", "config", "config.yaml")  # 修正期望路径
        assert get_config_file_path() == expected_default

    finally:
        # 确保清理
        set_config_path(None)
        if 'CUSTOM_LOGGER_CONFIG_PATH' in os.environ:
            del os.environ['CUSTOM_LOGGER_CONFIG_PATH']
    pass


def test_tc0002_016_worker_config_path_inheritance():
    """测试worker进程配置路径继承"""
    from custom_logger.config import get_cached_config_path

    test_path = "worker/test_config.yaml"

    # 模拟主进程设置配置路径
    set_config_path(test_path)

    # 模拟worker进程（清理缓存，只保留环境变量）
    original_cache = get_cached_config_path()
    set_config_path(None)  # 清理缓存但保留环境变量
    os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = test_path  # 手动设置环境变量

    try:
        # worker进程应该能从环境变量读取配置路径
        worker_path = get_config_file_path()
        assert worker_path == test_path
    finally:
        # 恢复和清理
        set_config_path(None)
    pass


@patch('os.makedirs')
@patch('custom_logger.config.is_debug')
@patch('custom_logger.config.get_config_manager')
def test_tc0002_017_init_config_debug_mode(mock_get_config_manager, mock_is_debug, mock_makedirs):
    """测试调试模式下的配置初始化"""
    mock_is_debug.return_value = True
    mock_cfg = MagicMock()
    mock_cfg.base_dir = "d:/logs"
    mock_cfg.project_name = "test_project"
    mock_cfg.experiment_name = "test_exp"
    mock_cfg.first_start_time = None
    mock_cfg.logger = MagicMock()
    mock_get_config_manager.return_value = mock_cfg

    with patch('builtins.hasattr', return_value=True):
        init_config()

    # 验证debug目录被创建
    mock_makedirs.assert_called()
    pass


def test_tc0002_018_set_config_path_none():
    """测试设置配置路径为None"""
    from custom_logger.config import get_cached_config_path

    # 先设置一个路径
    set_config_path("test/path.yaml")
    assert get_cached_config_path() == "test/path.yaml"
    assert os.environ.get('CUSTOM_LOGGER_CONFIG_PATH') == "test/path.yaml"

    # 设置为None应该清理
    set_config_path(None)
    assert get_cached_config_path() is None
    assert 'CUSTOM_LOGGER_CONFIG_PATH' not in os.environ
    pass


def test_tc0002_019_empty_module_levels():
    """测试模块级别配置为空的情况"""
    mock_config = MagicMock()
    mock_config.global_console_level = "warning"
    mock_config.global_file_level = "error"
    mock_config.module_levels = {"other_module": {"console_level": "debug"}}

    with patch('custom_logger.config.get_config', return_value=mock_config):
        console_level = get_console_level("non_existing_module")
        file_level = get_file_level("non_existing_module")

        # 应该使用全局配置
        assert console_level == 30  # WARNING
        assert file_level == 40  # ERROR
    pass


def test_tc0002_020_is_debug_integration():
    """测试is_debug函数集成"""
    from is_debug import is_debug
    result = is_debug()
    assert isinstance(result, bool)
    pass