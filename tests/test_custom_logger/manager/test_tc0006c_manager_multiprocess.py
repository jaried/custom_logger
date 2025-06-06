# tests/test_custom_logger/manager/test_tc0006c_manager_multiprocess.py
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


def test_tc0006_024_config_path_environment_inheritance():
    """测试配置路径环境变量继承"""
    from custom_logger.config import set_config_path, get_config_file_path, get_cached_config_path

    test_path = "worker/inherited_config.yaml"

    # 模拟主进程设置配置路径
    set_config_path(test_path)

    # 验证环境变量被设置
    assert os.environ.get('CUSTOM_LOGGER_CONFIG_PATH') == test_path

    # 模拟worker进程获取配置路径（清理缓存）
    set_config_path(None)  # 清理缓存
    os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = test_path  # 确保环境变量存在

    worker_path = get_config_file_path()
    assert worker_path == test_path

    # 清理
    set_config_path(None)
    pass


@patch('custom_logger.manager.init_writer')
def test_tc0006_025_multiprocess_config_sharing(mock_init_writer):
    """测试多进程配置共享"""
    from custom_logger.config import get_config_file_path, set_config_path
    import os

    # 确保清理状态
    tear_down_custom_logger_system()
    set_config_path(None)

    custom_path = "multiprocess/shared_config.yaml"

    # 只mock init_writer，让init_config正常运行以设置配置路径
    with patch('custom_logger.manager.init_config') as mock_init_config:
        # 让init_config执行实际的set_config_path逻辑
        def mock_init_config_impl(config_path, first_start_time=None, config_object=None):
            if config_path is not None:
                set_config_path(config_path)

        mock_init_config.side_effect = mock_init_config_impl

        # 主进程初始化
        init_custom_logger_system(config_path=custom_path)

        # 验证初始化被调用时传递了正确的配置路径
        mock_init_config.assert_called_with(custom_path, None, None)

        # 验证主进程配置路径被正确设置
        main_path = get_config_file_path()
        assert main_path == custom_path

        # 验证环境变量被设置
        assert os.environ.get('CUSTOM_LOGGER_CONFIG_PATH') == custom_path

        # 模拟worker进程启动（清理缓存但保留环境变量）
        # 注意：不调用set_config_path(None)，而是手动清理缓存
        from custom_logger.config import _cached_config_path
        with patch('custom_logger.config._cached_config_path', None):
            # 确保环境变量仍然存在
            assert os.environ.get('CUSTOM_LOGGER_CONFIG_PATH') == custom_path

            # 由于环境变量存在，worker进程应该能继承
            worker_path = get_config_file_path()
            assert worker_path == custom_path

    # 清理
    set_config_path(None)
    pass


def test_tc0006_026_worker_logger_creation():
    """测试worker进程中logger创建"""
    from custom_logger.config import set_config_path

    # 设置测试配置路径
    test_path = "worker/test_config.yaml"
    set_config_path(test_path)

    try:
        # 模拟worker进程（未初始化状态）
        with patch('custom_logger.manager._initialized', False):
            with patch('custom_logger.manager.get_config') as mock_get_config:
                with patch('custom_logger.manager.init_custom_logger_system') as mock_init:
                    # 第一次get_config失败触发自动初始化
                    mock_get_config.side_effect = [RuntimeError("Not initialized"), None]

                    logger = get_logger("worker_logger", console_level="w_summary")

                    # 验证自动初始化被调用
                    mock_init.assert_called_once_with()
                    assert isinstance(logger, CustomLogger)
                    assert logger.name == "worker_logger"
    finally:
        # 清理
        set_config_path(None)
    pass


def test_tc0006_027_worker_config_path_inheritance():
    """测试worker进程配置路径继承"""
    from custom_logger.config import get_cached_config_path, set_config_path

    test_path = "worker/test_config.yaml"

    # 模拟主进程设置配置路径
    set_config_path(test_path)

    # 模拟worker进程（清理缓存，只保留环境变量）
    original_cache = get_cached_config_path()
    set_config_path(None)  # 清理缓存但保留环境变量
    os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = test_path  # 手动设置环境变量

    try:
        # worker进程应该能从环境变量读取配置路径
        from custom_logger.config import get_config_file_path
        worker_path = get_config_file_path()
        assert worker_path == test_path
    finally:
        # 恢复和清理
        set_config_path(None)
    pass


def test_tc0006_028_config_path_inheritance_stress():
    """测试配置路径继承的压力测试"""
    from custom_logger.config import set_config_path, get_config_file_path

    base_path = "stress_test/config"

    # 测试快速切换配置路径
    for i in range(100):
        test_path = f"{base_path}_{i}.yaml"
        set_config_path(test_path)

        # 验证路径正确设置
        assert get_config_file_path() == test_path
        assert os.environ.get('CUSTOM_LOGGER_CONFIG_PATH') == test_path

        # 模拟worker进程获取配置
        with patch('custom_logger.config._cached_config_path', None):
            worker_path = get_config_file_path()
            assert worker_path == test_path

    # 清理
    set_config_path(None)
    pass


def test_tc0006_029_mixed_initialization_scenarios():
    """测试混合初始化场景"""
    from custom_logger.config import set_config_path

    try:
        # 场景1：主进程显式初始化
        tear_down_custom_logger_system()
        with patch('custom_logger.manager.init_config') as mock_init_config:
            with patch('custom_logger.manager.init_writer'):
                init_custom_logger_system("explicit/config.yaml")
                mock_init_config.assert_called_with("explicit/config.yaml", None, None)

        tear_down_custom_logger_system()

        # 场景2：worker进程自动初始化（使用环境变量配置）
        set_config_path("worker/inherited.yaml")

        with patch('custom_logger.manager._initialized', False):
            with patch('custom_logger.config.get_config', side_effect=[RuntimeError(), {}]):
                with patch('custom_logger.manager.init_custom_logger_system') as mock_auto_init:
                    get_logger("worker_logger")
                    mock_auto_init.assert_called_once_with()

        # 场景3：混合使用默认和自定义配置
        tear_down_custom_logger_system()
        set_config_path(None)

        with patch('custom_logger.manager.init_config') as mock_default_init:
            with patch('custom_logger.manager.init_writer'):
                init_custom_logger_system()  # 不传配置路径
                mock_default_init.assert_called_with(None, None, None)

    finally:
        set_config_path(None)
        tear_down_custom_logger_system()
    pass


def test_tc0006_030_edge_case_config_paths():
    """测试边界情况的配置路径"""
    from custom_logger.config import set_config_path, get_config_file_path

    edge_cases = [
        "single_file.yaml",  # 单个文件名
        "very/deep/nested/path/config.yaml",  # 深层嵌套
        "path with spaces/config.yaml",  # 包含空格
        "unicode_路径/配置.yaml",  # Unicode字符
    ]

    # 单独测试空字符串情况
    try:
        set_config_path("")
        # 空字符串应该被当作无效，返回默认路径
        retrieved_path = get_config_file_path()
        expected_default = os.path.join("config", "config.yaml")
        assert retrieved_path == expected_default
    finally:
        set_config_path(None)

    # 测试其他边界情况
    for test_path in edge_cases:
        try:
            set_config_path(test_path)

            # 验证路径被正确处理
            retrieved_path = get_config_file_path()
            assert retrieved_path == test_path

            # 验证环境变量传递
            env_path = os.environ.get('CUSTOM_LOGGER_CONFIG_PATH')
            assert env_path == test_path

        finally:
            set_config_path(None)
    pass