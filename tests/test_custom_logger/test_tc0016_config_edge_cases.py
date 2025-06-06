# tests/test_custom_logger/test_tc0016_config_edge_cases.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
from ruamel.yaml import YAML
from unittest.mock import patch, MagicMock
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system
from custom_logger.config import set_config_path, get_config_file_path, init_config


def test_tc0016_001_yaml_serialization_safety():
    """测试YAML序列化安全性"""
    # 创建包含复杂对象的配置
    config_content = """project_name: "yaml_safety_test"
experiment_name: "serialization"
first_start_time: null
base_dir: "d:/logs/yaml_safety"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    test_module:
      console_level: "debug"
      file_level: "info"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 初始化并修改配置（触发保存）
        init_custom_logger_system(config_path=config_path)

        # 获取logger并修改配置
        logger = get_logger("test_module")

        # 等待配置保存
        import time
        time.sleep(1)

        # 读取保存后的YAML文件，检查是否包含Python对象标签
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证不包含危险的Python对象序列化标签
        assert 'tag:yaml.org,2002:python/object' not in content
        assert 'tag:yaml.org,2002:python/object/apply' not in content
        assert '!!python/object' not in content

        # 验证能正常重新加载
        tear_down_custom_logger_system()
        init_custom_logger_system(config_path=config_path)

        # 验证配置正确
        from custom_logger.config import get_root_config
        root_cfg = get_root_config()
        project_name = getattr(root_cfg, 'project_name', None)
        assert project_name == "yaml_safety_test"

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0016_002_config_corruption_recovery():
    """测试配置文件损坏时的恢复能力"""
    # 创建正常配置
    config_content = """project_name: "corruption_test"
experiment_name: "recovery"
first_start_time: null
base_dir: "d:/logs/corruption"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        # 先用正常配置初始化
        tear_down_custom_logger_system()
        set_config_path(None)
        init_custom_logger_system(config_path=config_path)
        tear_down_custom_logger_system()

        # 故意损坏配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("invalid: yaml: content: [unclosed bracket")

        # 尝试重新初始化（应该能处理错误）
        try:
            init_custom_logger_system(config_path=config_path)
            # 如果没有抛出异常，验证能基本工作
            logger = get_logger("test")
            logger.info("测试消息")
        except Exception:
            # 如果抛出异常，这是预期的行为
            pass

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0016_003_config_manager_object_persistence():
    """测试config_manager对象持久化问题"""
    config_content = """project_name: "persistence_test"
experiment_name: "object_persistence"
first_start_time: null
base_dir: "d:/logs/persistence"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    persistence_module:
      console_level: "debug"
      file_level: "info"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 初始化系统
        init_custom_logger_system(config_path=config_path)

        # 获取配置对象
        from custom_logger.config import get_root_config
        root_cfg1 = get_root_config()

        # 修改配置触发保存
        logger = get_logger("persistence_module")

        # 等待可能的自动保存
        import time
        time.sleep(1)

        # 重新初始化并获取配置
        tear_down_custom_logger_system()
        init_custom_logger_system(config_path=config_path)
        root_cfg2 = get_root_config()

        # 验证配置内容一致
        project1 = getattr(root_cfg1, 'project_name', None)
        project2 = getattr(root_cfg2, 'project_name', None)
        assert project1 == project2 == "persistence_test"

        # 验证logger配置一致
        logger1_cfg = getattr(root_cfg1, 'logger', None)
        logger2_cfg = getattr(root_cfg2, 'logger', None)
        assert logger1_cfg is not None
        assert logger2_cfg is not None

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0016_004_large_config_handling():
    """测试大型配置文件的处理"""
    # 创建包含大量模块配置的配置文件
    module_configs = {}
    for i in range(100):
        module_configs[f"module_{i:03d}"] = {
            "console_level": "debug" if i % 2 == 0 else "info",
            "file_level": "debug" if i % 3 == 0 else "info"
        }

    config_data = {
        "project_name": "large_config_test",
        "experiment_name": "performance",
        "first_start_time": None,
        "base_dir": "d:/logs/large_config",
        "logger": {
            "global_console_level": "info",
            "global_file_level": "debug",
            "current_session_dir": None,
            "module_levels": module_configs
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.default_flow_style = False
        yaml.dump(config_data, tmp_file)
        config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 测试大型配置加载性能
        import time
        start_time_test = time.time()

        init_custom_logger_system(config_path=config_path)

        end_time_test = time.time()
        load_duration = end_time_test - start_time_test

        # 验证加载时间合理（应该在几秒内）
        assert load_duration < 5.0

        # 验证能正确获取特定模块配置
        logger_050 = get_logger("module_050")
        logger_051 = get_logger("module_051")

        # 验证配置正确
        from custom_logger.types import DEBUG, INFO
        assert logger_050.console_level == DEBUG  # 50 % 2 == 0
        assert logger_051.console_level == INFO  # 51 % 2 == 1

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0016_005_concurrent_config_access():
    """测试并发配置访问"""
    config_content = """project_name: "concurrent_config_test"
experiment_name: "concurrent_access"
first_start_time: null
base_dir: "d:/logs/concurrent"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    concurrent_module_1:
      console_level: "debug"
      file_level: "info"
    concurrent_module_2:
      console_level: "warning"
      file_level: "error"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    results = []
    import threading

    def concurrent_config_access(thread_id: int):
        """并发访问配置的函数"""
        try:
            logger1 = get_logger(f"concurrent_module_{thread_id % 2 + 1}")
            logger2 = get_logger(f"thread_{thread_id}_logger")

            # 多次访问配置
            for i in range(10):
                level1 = logger1.console_level
                level2 = logger2.console_level

                # 验证级别获取一致
                assert level1 > 0
                assert level2 > 0

            results.append((thread_id, "success"))
        except Exception as e:
            results.append((thread_id, f"error: {e}"))

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 初始化系统
        init_custom_logger_system(config_path=config_path)

        # 创建多个线程并发访问配置
        threads = []
        for i in range(5):
            thread = threading.Thread(target=concurrent_config_access, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证所有线程都成功
        assert len(results) == 5
        for thread_id, status in results:
            assert status == "success"

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0016_006_config_path_edge_cases():
    """测试配置路径边界情况"""
    edge_cases = [
        "",  # 空字符串
        "   ",  # 空白字符串
        "non_existent_file.yaml",  # 不存在的文件
        "config with spaces.yaml",  # 包含空格的路径
        "unicode_配置文件.yaml",  # Unicode字符
    ]

    for test_path in edge_cases:
        try:
            # 清理状态
            tear_down_custom_logger_system()
            set_config_path(None)

            if test_path.strip() == "":
                # 空字符串应该使用默认路径
                set_config_path(test_path)
                retrieved_path = get_config_file_path()
                expected_default = os.path.join("src", "config", "config.yaml")
                assert retrieved_path == expected_default
            else:
                # 其他情况应该能正确设置和获取
                set_config_path(test_path)
                retrieved_path = get_config_file_path()
                assert retrieved_path == test_path

        finally:
            set_config_path(None)
    pass


def test_tc0016_007_config_conversion_stability():
    """测试配置对象转换的稳定性"""
    config_content = """project_name: "conversion_test"
experiment_name: "stability"
first_start_time: null
base_dir: "d:/logs/conversion"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    conversion_module:
      console_level: "debug"
      file_level: "info"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 初始化系统
        init_custom_logger_system(config_path=config_path)

        # 获取配置并测试转换
        from custom_logger.config import get_config, _convert_confignode_to_dict
        config = get_config()

        # 测试模块级别配置的转换
        module_levels = getattr(config, 'module_levels', {})

        # 如果是ConfigNode对象，测试转换
        if hasattr(module_levels, '__dict__'):
            converted = _convert_confignode_to_dict(module_levels)
            assert isinstance(converted, dict)
            assert 'conversion_module' in converted
            assert isinstance(converted['conversion_module'], dict)
            assert 'console_level' in converted['conversion_module']

        # 多次转换应该保持一致
        for i in range(5):
            logger = get_logger("conversion_module")
            level = logger.console_level
            from custom_logger.types import DEBUG
            assert level == DEBUG

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0016_008_session_directory_creation_edge():
    """测试会话目录创建的边界情况"""
    # 测试特殊字符路径
    config_content = """project_name: "session_边界_test"
experiment_name: "目录_creation"
first_start_time: "2024-01-01T15:30:00"
base_dir: "d:/logs/特殊字符/测试"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 初始化系统
        with patch('os.makedirs') as mock_makedirs:
            init_custom_logger_system(config_path=config_path)

            # 验证目录创建被调用
            mock_makedirs.assert_called()

            # 获取会话目录
            from custom_logger.config import get_root_config
            root_cfg = get_root_config()
            logger_cfg = root_cfg.logger

            if isinstance(logger_cfg, dict):
                session_dir = logger_cfg.get('current_session_dir')
            else:
                session_dir = getattr(logger_cfg, 'current_session_dir', None)

            # 验证会话目录路径
            assert session_dir is not None
            assert "session_边界_test" in session_dir
            assert "目录_creation" in session_dir
            assert "20240101" in session_dir
            assert "153000" in session_dir

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0016_009_debug_mode_directory_edge():
    """测试debug模式目录的边界情况"""
    config_content = """project_name: "debug_edge_test"
experiment_name: "boundary"
first_start_time: "2024-01-01T12:00:00"
base_dir: "d:/logs/debug_base"

logger:
  global_console_level: "debug"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 测试不同的debug模式状态
        debug_states = [True, False]

        for debug_state in debug_states:
            with patch('custom_logger.config.is_debug', return_value=debug_state):
                with patch('os.makedirs') as mock_makedirs:
                    # 重新初始化系统
                    if debug_state != debug_states[0]:  # 第二次需要先清理
                        tear_down_custom_logger_system()

                    init_custom_logger_system(config_path=config_path)

                    # 获取会话目录
                    from custom_logger.config import get_root_config
                    root_cfg = get_root_config()
                    logger_cfg = root_cfg.logger

                    if isinstance(logger_cfg, dict):
                        session_dir = logger_cfg.get('current_session_dir')
                    else:
                        session_dir = getattr(logger_cfg, 'current_session_dir', None)

                    # 验证debug模式下的路径
                    assert session_dir is not None
                    if debug_state:
                        assert "debug" in session_dir
                    # 验证其他路径组件
                    assert "debug_edge_test" in session_dir
                    assert "boundary" in session_dir

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0016_010_config_error_recovery():
    """测试配置错误时的恢复机制"""
    # 创建正常配置
    normal_config = """project_name: "error_recovery_test"
experiment_name: "recovery"
first_start_time: null
base_dir: "d:/logs/recovery"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(normal_config)
        config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 1. 正常初始化
        init_custom_logger_system(config_path=config_path)
        logger1 = get_logger("test1")
        logger1.info("正常配置测试")
        tear_down_custom_logger_system()

        # 2. 模拟config_manager加载失败
        with patch('custom_logger.config.get_config_manager', side_effect=Exception("Config load error")):
            try:
                init_custom_logger_system(config_path=config_path)
                # 如果没有抛出异常，验证系统有基本容错
                logger2 = get_logger("test2")
            except Exception:
                # 抛出异常是预期的
                pass

        # 3. 恢复正常
        init_custom_logger_system(config_path=config_path)
        logger3 = get_logger("test3")
        logger3.info("恢复后测试")

        # 验证恢复后能正常工作
        assert logger3.name == "test3"

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass