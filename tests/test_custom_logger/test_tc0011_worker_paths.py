# tests/test_custom_logger/test_tc0011_worker_paths.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import threading
import time
from unittest.mock import patch, MagicMock
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system, is_initialized
from custom_logger.config import set_config_path, get_config_file_path


def test_tc0011_001_worker_with_default_config():
    """测试使用默认config.yaml的worker日志路径"""
    # 清理状态
    tear_down_custom_logger_system()
    set_config_path(None)

    try:
        # 使用临时配置文件进行测试
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write("""
project_name: "test_project"
experiment_name: "default"
first_start_time: null
base_dir: "d:/logs"
logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {}
""")
            test_config_path = tmp_file.name

        # 使用测试配置路径初始化
        init_custom_logger_system(config_path=test_config_path)

        # 验证系统初始化成功
        assert is_initialized()

        # 创建worker logger
        worker_logger = get_logger("test_worker", console_level="w_summary")

        # 验证logger创建成功
        assert worker_logger.name == "test_worker"

        # 清理临时文件
        if os.path.exists(test_config_path):
            os.unlink(test_config_path)

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
    pass


def test_tc0011_002_worker_with_custom_config():
    """测试使用自定义配置文件的worker日志路径"""
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
        tmp_file.write("""
project_name: "custom_project"
experiment_name: "test_exp"
first_start_time: null
base_dir: "d:/custom_logs"
logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {}
""")
        custom_config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 使用自定义配置初始化
        with patch('os.makedirs') as mock_makedirs:
            with patch('custom_logger.writer.init_writer'):
                init_custom_logger_system(config_path=custom_config_path)

                # 验证使用了自定义配置路径
                assert get_config_file_path() == custom_config_path

                # 模拟worker进程环境
                worker_config_path = os.environ.get('CUSTOM_LOGGER_CONFIG_PATH')
                assert worker_config_path == custom_config_path

                # 创建worker logger
                with patch('custom_logger.config.get_config_manager') as mock_get_config:
                    mock_cfg = MagicMock()
                    mock_cfg.base_dir = "d:/custom_logs"
                    mock_cfg.project_name = "custom_project"
                    mock_cfg.experiment_name = "test_exp"
                    mock_cfg.first_start_time = "2024-01-01T15:30:00"
                    mock_cfg.logger = MagicMock()
                    mock_cfg.logger.current_session_dir = "d:/custom_logs/custom_project/test_exp/logs/20240101/153000"
                    mock_cfg.logger.global_console_level = "info"
                    mock_cfg.logger.global_file_level = "debug"
                    mock_cfg.logger.module_levels = {}
                    mock_get_config.return_value = mock_cfg

                    worker_logger = get_logger("custom_worker", console_level="w_detail")
                    assert worker_logger.name == "custom_worker"

    finally:
        # 清理临时文件
        if os.path.exists(custom_config_path):
            os.unlink(custom_config_path)
        tear_down_custom_logger_system()
        set_config_path(None)
    pass


def test_tc0011_003_worker_multiprocess_config_inheritance():
    """测试多进程worker配置继承"""
    test_config_path = "test_multiprocess/config.yaml"

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 主进程设置配置路径
        set_config_path(test_config_path)

        # 验证环境变量被设置
        assert os.environ.get('CUSTOM_LOGGER_CONFIG_PATH') == test_config_path

        # 模拟worker进程（清理缓存但保留环境变量）
        with patch('custom_logger.config._cached_config_path', None):
            worker_config_path = get_config_file_path()
            assert worker_config_path == test_config_path

        # 模拟worker进程中的logger创建
        results = []

        def worker_thread():
            """模拟worker线程"""
            try:
                # worker应该能从环境变量获取配置路径
                thread_config_path = get_config_file_path()
                results.append(("config_path", thread_config_path))

                # 创建worker logger
                with patch('custom_logger.manager._initialized', True):
                    with patch('custom_logger.config.get_config') as mock_get_config:
                        mock_config = MagicMock()
                        mock_config.global_console_level = "w_summary"
                        mock_config.global_file_level = "w_detail"
                        mock_config.module_levels = {}
                        mock_get_config.return_value = mock_config

                        worker_logger = get_logger("thread_worker", console_level="w_summary")
                        results.append(("logger_name", worker_logger.name))

            except Exception as e:
                results.append(("error", str(e)))

        # 启动worker线程
        thread = threading.Thread(target=worker_thread)
        thread.start()
        thread.join()

        # 验证结果
        assert len(results) == 2
        assert ("config_path", test_config_path) in results
        assert ("logger_name", "thread_worker") in results

    finally:
        set_config_path(None)
    pass


def test_tc0011_004_worker_session_directory_creation():
    """测试worker会话目录创建"""
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_config = {
            "project_name": "worker_test",
            "experiment_name": "session_test",
            "base_dir": temp_dir,
            "first_start_time": "2024-06-01T12:00:00",
            "logger": {
                "global_console_level": "info",
                "global_file_level": "debug",
                "current_session_dir": None,
                "module_levels": {}
            }
        }

        try:
            # 清理状态
            tear_down_custom_logger_system()
            set_config_path(None)

            # 模拟配置初始化
            with patch('custom_logger.config.get_config_manager') as mock_get_config:
                mock_cfg = MagicMock()
                for key, value in custom_config.items():
                    if key == 'logger':
                        logger_obj = MagicMock()
                        for sub_key, sub_value in value.items():
                            setattr(logger_obj, sub_key, sub_value)
                        setattr(mock_cfg, key, logger_obj)
                    else:
                        setattr(mock_cfg, key, value)

                mock_get_config.return_value = mock_cfg

                # 验证会话目录路径构建
                from custom_logger.config import _create_session_dir
                session_dir = _create_session_dir(mock_cfg)

                expected_session_dir = os.path.join(
                    temp_dir, "worker_test", "session_test", "logs", "20240601", "120000"
                )
                assert session_dir == expected_session_dir

                # 验证目录被创建
                assert os.path.exists(session_dir)

        finally:
            tear_down_custom_logger_system()
    pass


def test_tc0011_005_worker_debug_mode_directory():
    """测试debug模式下的worker目录创建"""
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_config = {
            "project_name": "debug_worker",
            "experiment_name": "debug_test",
            "base_dir": temp_dir,
            "first_start_time": "2024-06-01T14:30:00",
            "logger": {
                "global_console_level": "debug",
                "global_file_level": "debug",
                "current_session_dir": None,
                "module_levels": {}
            }
        }

        try:
            # 清理状态
            tear_down_custom_logger_system()
            set_config_path(None)

            # 模拟debug模式
            with patch('custom_logger.config.is_debug', return_value=True):
                with patch('custom_logger.config.get_config_manager') as mock_get_config:
                    mock_cfg = MagicMock()
                    for key, value in custom_config.items():
                        if key == 'logger':
                            logger_obj = MagicMock()
                            for sub_key, sub_value in value.items():
                                setattr(logger_obj, sub_key, sub_value)
                            setattr(mock_cfg, key, logger_obj)
                        else:
                            setattr(mock_cfg, key, value)

                    mock_get_config.return_value = mock_cfg

                    # 验证debug模式下的会话目录路径
                    from custom_logger.config import _create_session_dir
                    session_dir = _create_session_dir(mock_cfg)

                    # debug模式应该添加debug子目录
                    expected_session_dir = os.path.join(
                        temp_dir, "debug", "debug_worker", "debug_test", "logs", "20240601", "143000"
                    )
                    assert session_dir == expected_session_dir

                    # 验证目录被创建
                    assert os.path.exists(session_dir)

        finally:
            tear_down_custom_logger_system()
    pass


def test_tc0011_006_worker_config_validation():
    """测试worker配置验证"""
    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 测试未初始化状态下的配置获取
        from custom_logger.config import get_config
        from custom_logger.manager import _initialized

        with patch('custom_logger.manager._initialized', False):
            with patch('custom_logger.config.get_config_manager') as mock_get_config:
                mock_cfg = MagicMock()
                # 模拟未初始化状态（没有logger属性）
                delattr(mock_cfg, 'logger') if hasattr(mock_cfg, 'logger') else None
                with patch('builtins.hasattr', return_value=False):
                    mock_get_config.return_value = mock_cfg

                    try:
                        get_config()
                        assert False, "应该抛出RuntimeError"
                    except RuntimeError as e:
                        assert "日志系统未初始化" in str(e)

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
    pass


def test_tc0011_007_worker_concurrent_config_access():
    """测试并发worker配置访问"""
    test_config_path = "concurrent_test/config.yaml"
    results = []

    def worker_func(worker_id):
        """并发worker函数"""
        try:
            # 每个worker都应该能获取相同的配置路径
            config_path = get_config_file_path()
            results.append((worker_id, "config_path", config_path))

            # 模拟logger创建
            with patch('custom_logger.manager._initialized', True):
                with patch('custom_logger.config.get_config') as mock_get_config:
                    mock_config = MagicMock()
                    mock_config.global_console_level = "info"
                    mock_config.global_file_level = "debug"
                    mock_config.module_levels = {}
                    mock_get_config.return_value = mock_config

                    logger = get_logger(f"worker_{worker_id}")
                    results.append((worker_id, "logger_name", logger.name))

        except Exception as e:
            results.append((worker_id, "error", str(e)))

    try:
        # 设置配置路径
        set_config_path(test_config_path)

        # 启动多个并发worker
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_func, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(results) == 10  # 5个worker，每个2个结果

        # 验证所有worker获取了相同的配置路径
        config_results = [r for r in results if r[1] == "config_path"]
        assert len(config_results) == 5
        for _, _, config_path in config_results:
            assert config_path == test_config_path

        # 验证所有logger创建成功
        logger_results = [r for r in results if r[1] == "logger_name"]
        assert len(logger_results) == 5

    finally:
        set_config_path(None)
    pass


def test_tc0011_008_worker_config_path_priority():
    """测试worker配置路径优先级"""
    try:
        # 清理状态
        set_config_path(None)

        # 测试优先级：缓存 > 环境变量 > 默认
        # 1. 只有默认路径
        default_path = get_config_file_path()
        expected_default = os.path.join("src", "config", "config.yaml")
        assert default_path == expected_default

        # 2. 设置环境变量
        env_path = "env/test_config.yaml"
        os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = env_path
        assert get_config_file_path() == env_path

        # 3. 设置缓存路径（应该优先于环境变量）
        cache_path = "cache/test_config.yaml"
        set_config_path(cache_path)
        assert get_config_file_path() == cache_path

        # 4. 清理缓存，应该回到环境变量
        set_config_path(None)
        os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = env_path  # 重新设置环境变量
        assert get_config_file_path() == env_path

        # 5. 清理环境变量，应该回到默认
        if 'CUSTOM_LOGGER_CONFIG_PATH' in os.environ:
            del os.environ['CUSTOM_LOGGER_CONFIG_PATH']
        assert get_config_file_path() == expected_default

    finally:
        set_config_path(None)
        if 'CUSTOM_LOGGER_CONFIG_PATH' in os.environ:
            del os.environ['CUSTOM_LOGGER_CONFIG_PATH']
    pass


def test_tc0011_009_worker_config_edge_cases():
    """测试worker配置边界情况"""
    try:
        # 测试空字符串配置路径
        set_config_path("")
        default_path = get_config_file_path()
        expected_default = os.path.join("src", "config", "config.yaml")
        assert default_path == expected_default

        # 测试空白字符串环境变量
        set_config_path(None)
        os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = "   "
        assert get_config_file_path() == expected_default

        # 测试Unicode路径
        unicode_path = "测试/配置.yaml"
        set_config_path(unicode_path)
        assert get_config_file_path() == unicode_path

    finally:
        set_config_path(None)
        if 'CUSTOM_LOGGER_CONFIG_PATH' in os.environ:
            del os.environ['CUSTOM_LOGGER_CONFIG_PATH']
    pass


def test_tc0011_010_worker_session_directory_isolation():
    """测试worker会话目录隔离"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建两个不同的配置
        config1 = {
            "project_name": "project1",
            "experiment_name": "exp1",
            "base_dir": temp_dir,
            "first_start_time": "2024-06-01T10:00:00"
        }

        config2 = {
            "project_name": "project2",
            "experiment_name": "exp2",
            "base_dir": temp_dir,
            "first_start_time": "2024-06-01T11:00:00"
        }

        # 验证不同配置生成不同的会话目录
        from custom_logger.config import _create_session_dir

        mock_cfg1 = MagicMock()
        for key, value in config1.items():
            setattr(mock_cfg1, key, value)

        mock_cfg2 = MagicMock()
        for key, value in config2.items():
            setattr(mock_cfg2, key, value)

        session_dir1 = _create_session_dir(mock_cfg1)
        session_dir2 = _create_session_dir(mock_cfg2)

        # 验证目录不同
        assert session_dir1 != session_dir2

        # 验证目录结构正确
        expected_path1 = os.path.join("project1", "exp1", "logs", "20240601", "100000")
        expected_path2 = os.path.join("project2", "exp2", "logs", "20240601", "110000")
        assert expected_path1 in session_dir1
        assert expected_path2 in session_dir2

        # 验证目录都被创建
        assert os.path.exists(session_dir1)
        assert os.path.exists(session_dir2)
    pass