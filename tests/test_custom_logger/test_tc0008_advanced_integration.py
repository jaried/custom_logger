# tests/test_custom_logger/test_tc0008_advanced_integration.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import threading
from unittest.mock import patch, MagicMock
from custom_logger import get_logger, init_custom_logger_system, tear_down_custom_logger_system
from custom_logger.types import DEBUG, INFO, WARNING, ERROR, EXCEPTION


def test_tc0008_001_custom_config_path_integration():
    """测试自定义配置路径集成"""
    from custom_logger.config import get_config_file_path, set_config_path

    # 创建临时配置文件路径
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as tmp_file:
        custom_config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 直接测试配置路径设置，不mock init_config
        init_custom_logger_system(config_path=custom_config_path)

        # 验证配置路径被正确设置
        assert get_config_file_path() == custom_config_path

        tear_down_custom_logger_system()
    finally:
        # 清理临时文件
        if os.path.exists(custom_config_path):
            os.unlink(custom_config_path)
        set_config_path(None)
    pass


def test_tc0008_002_multiprocess_config_inheritance():
    """测试多进程配置继承"""
    from custom_logger.config import set_config_path, get_config_file_path

    # 创建唯一的测试配置路径
    test_config_path = f"test_multiprocess_{os.getpid()}.yaml"

    def worker_process():
        """Worker进程函数"""
        # worker进程中应该能获取主进程设置的配置路径
        worker_path = get_config_file_path()
        return worker_path

    try:
        # 主进程设置配置路径
        set_config_path(test_config_path)

        # 验证主进程配置路径
        main_path = get_config_file_path()
        assert main_path == test_config_path

        # 模拟子进程通过环境变量获取配置路径
        env_path = os.environ.get('CUSTOM_LOGGER_CONFIG_PATH')
        assert env_path == test_config_path

        # 验证在清理缓存后仍能从环境变量获取
        with patch('custom_logger.config._cached_config_path', None):
            inherited_path = get_config_file_path()
            assert inherited_path == test_config_path

    finally:
        # 清理
        set_config_path(None)
    pass


def test_tc0008_003_worker_logger_with_custom_config():
    """测试worker使用自定义配置的logger"""
    from custom_logger.config import set_config_path

    test_config_path = "worker_test/custom_config.yaml"
    mock_config = {
        "global_console_level": "w_summary",
        "global_file_level": "w_detail",
        "module_levels": {
            "worker_module": {
                "console_level": "w_detail",
                "file_level": "debug"
            }
        },
        "first_start_time": datetime.now().isoformat()
    }

    try:
        # 设置自定义配置路径
        set_config_path(test_config_path)

        with patch('custom_logger.config.get_config', return_value=mock_config):
            with patch('custom_logger.config.get_root_config') as mock_root_config:
                mock_root_config.return_value = MagicMock(first_start_time=mock_config["first_start_time"])

                with patch('custom_logger.manager._initialized', True):
                    # 创建worker logger
                    worker_logger = get_logger("worker_module", console_level="w_summary")

                    # 验证logger创建成功
                    assert worker_logger.name == "worker_module"

                    # 测试worker专用日志方法
                    with patch.object(worker_logger, '_log') as mock_log:
                        worker_logger.worker_summary("Worker task started")
                        worker_logger.worker_detail("Processing data")

                        # 验证worker方法被正确调用
                        assert mock_log.call_count == 2
                        calls = mock_log.call_args_list
                        assert calls[0][0][0] == 5  # W_SUMMARY
                        assert calls[1][0][0] == 3  # W_DETAIL
    finally:
        set_config_path(None)
    pass


def test_tc0008_004_exception_logging_with_custom_config():
    """测试自定义配置下的异常日志记录"""
    from custom_logger.config import set_config_path

    test_config_path = "exception_test/config.yaml"
    mock_config = {
        "global_console_level": "exception",
        "global_file_level": "exception",
        "module_levels": {},
        "first_start_time": datetime.now().isoformat()
    }

    try:
        set_config_path(test_config_path)

        with patch('custom_logger.config.get_config', return_value=mock_config):
            with patch('custom_logger.config.get_root_config') as mock_root_config:
                mock_root_config.return_value = MagicMock(first_start_time=mock_config["first_start_time"])

                with patch('custom_logger.logger.get_console_level', return_value=EXCEPTION):
                    with patch('custom_logger.logger.get_file_level', return_value=EXCEPTION):
                        with patch('custom_logger.manager._initialized', True):
                            logger = get_logger("exception_test")

                            with patch('custom_logger.logger.get_exception_info') as mock_exc:
                                mock_exc.return_value = "Custom exception traceback"

                                with patch.object(logger, '_print_to_console'):
                                    with patch('custom_logger.logger.write_log_async') as mock_file:
                                        logger.exception("Custom config exception")

                                        # 验证异常信息被获取和处理
                                        mock_exc.assert_called_once()
                                        mock_file.assert_called_once()

                                        # 验证异步写入包含异常信息
                                        call_args = mock_file.call_args[0]
                                        assert call_args[1] == EXCEPTION  # level_value
                                        assert call_args[2] == "Custom exception traceback"  # exception_info
    finally:
        set_config_path(None)
    pass


def test_tc0008_005_auto_initialization_with_custom_config():
    """测试自定义配置的自动初始化"""
    from custom_logger.config import set_config_path

    test_config_path = "auto_init/test_config.yaml"
    mock_config = {
        "global_console_level": "info",
        "global_file_level": "debug",
        "module_levels": {}
    }

    try:
        # 预设配置路径（模拟主进程已设置）
        set_config_path(test_config_path)

        # 模拟未初始化状态（worker进程场景）
        with patch('custom_logger.manager._initialized', False):
            with patch('custom_logger.config.get_config', side_effect=[RuntimeError("Not initialized"), mock_config]):
                with patch('custom_logger.manager.init_custom_logger_system') as mock_init:
                    logger = get_logger("auto_init_test")

                    # 验证自动初始化被调用（不传递配置路径，使用环境变量）
                    mock_init.assert_called_once_with()
                    assert isinstance(logger, type(get_logger("test")))
    finally:
        set_config_path(None)
    pass


def test_tc0008_006_caller_identification_fix():
    """测试调用者识别修复"""
    from custom_logger.config import set_config_path

    test_config_path = "caller_test/config.yaml"
    mock_root_config = MagicMock()
    mock_root_config.first_start_time = "2024-01-01T10:00:00"

    try:
        set_config_path(test_config_path)

        # Mock整个配置系统避免实际初始化
        with patch('custom_logger.config.get_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.global_console_level = "info"
            mock_config.global_file_level = "debug"
            mock_config.module_levels = {}
            mock_get_config.return_value = mock_config

            with patch('custom_logger.config.get_root_config', return_value=mock_root_config):
                with patch('custom_logger.manager._initialized', True):
                    logger = get_logger("caller_test")

                    # 直接Mock get_caller_info函数而不是inspect.stack
                    with patch('custom_logger.formatter.get_caller_info') as mock_caller_info:
                        mock_caller_info.return_value = ("demo_cus", 25)

                        with patch.object(logger, '_print_to_console') as mock_console:
                            with patch('custom_logger.logger.write_log_async'):
                                logger.info("Test caller identification")

                                # 验证控制台输出被调用
                                mock_console.assert_called_once()

                                # 验证日志行中包含正确的调用者信息
                                log_line = mock_console.call_args[0][0]
                                assert "demo_cus" in log_line
                                assert "  25" in log_line
                                assert "unknown" not in log_line
    finally:
        set_config_path(None)
    pass


def test_tc0008_007_concurrent_loggers_custom_config():
    """测试自定义配置下的并发logger使用"""
    from custom_logger.config import set_config_path

    test_config_path = "concurrent/test_config.yaml"
    mock_config = {
        "global_console_level": "info",
        "global_file_level": "debug",
        "module_levels": {},
        "first_start_time": datetime.now().isoformat()
    }

    results = []

    def worker_thread(thread_id):
        """线程worker函数"""
        try:
            with patch('custom_logger.config.get_config', return_value=mock_config):
                with patch('custom_logger.config.get_root_config') as mock_root_config:
                    mock_root_config.return_value = MagicMock(first_start_time=mock_config["first_start_time"])

                    with patch('custom_logger.manager._initialized', True):
                        logger = get_logger(f"thread_{thread_id}")

                        with patch.object(logger, '_log') as mock_log:
                            logger.info(f"Message from thread {thread_id}")
                            results.append((thread_id, mock_log.call_count))
        except Exception as e:
            results.append((thread_id, f"Error: {e}"))

    try:
        set_config_path(test_config_path)

        # 创建多个线程并发使用logger
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证所有线程都成功执行
        assert len(results) == 5
        for thread_id, result in results:
            assert result == 1  # 每个线程调用一次_log
    finally:
        set_config_path(None)
    pass


def test_tc0008_008_config_path_inheritance_stress():
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


def test_tc0008_009_mixed_initialization_scenarios():
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


def test_tc0008_010_edge_case_config_paths():
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