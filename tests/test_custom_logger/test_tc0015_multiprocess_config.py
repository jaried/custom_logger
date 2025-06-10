# tests/test_custom_logger/test_tc0015_multiprocess_config.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor
from unittest.mock import patch, MagicMock
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system
from custom_logger.config import set_config_path, get_config_file_path


def worker_process_function(worker_id: int, config_path: str):
    """进程worker函数，用于测试多进程配置继承"""
    try:
        # 设置环境变量（模拟主进程设置）
        os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = config_path

        # 在子进程中初始化日志系统
        from custom_logger import init_custom_logger_system, get_logger
        init_custom_logger_system()

        # 获取logger并记录日志
        logger = get_logger(f"process_worker_{worker_id}")
        logger.info(f"进程Worker {worker_id} 启动")
        logger.info(f"进程Worker {worker_id} 完成")

        return f"Process-{worker_id} success"
    except Exception as e:
        return f"Process-{worker_id} error: {str(e)}"


def simple_process_function(config_path: str):
    """简单的进程函数，测试配置加载"""
    try:
        # 模拟从环境变量获取配置
        os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = config_path

        # 检查配置路径获取
        from custom_logger.config import get_config_file_path
        retrieved_path = get_config_file_path()

        if retrieved_path == config_path:
            return "config_path_correct"
        else:
            return f"config_path_wrong: expected={config_path}, got={retrieved_path}"
    except Exception as e:
        return f"error: {str(e)}"


def process_init_test_function(should_init: bool, config_path: str):
    """测试进程初始化的函数"""
    try:
        if should_init:
            # 设置环境变量
            os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = config_path

            # 显式初始化
            from custom_logger import init_custom_logger_system
            init_custom_logger_system()

        # 尝试获取logger
        from custom_logger import get_logger
        logger = get_logger("process_test")
        logger.info("进程测试消息")

        return "init_success"
    except Exception as e:
        return f"init_error: {str(e)}"


def yaml_serialization_test_function(config_path: str):
    """测试YAML配置序列化的函数"""
    try:
        # 设置环境变量
        os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = config_path

        # 初始化并使用配置
        from custom_logger import init_custom_logger_system, get_logger
        init_custom_logger_system()

        # 获取配置信息
        from custom_logger.config import get_root_config
        root_cfg = get_root_config()

        project_name = getattr(root_cfg, 'project_name', None)
        experiment_name = getattr(root_cfg, 'experiment_name', None)

        if project_name == "yaml_test" and experiment_name == "serialization":
            return "yaml_load_success"
        else:
            return f"yaml_load_wrong: project={project_name}, exp={experiment_name}"
    except Exception as e:
        return f"yaml_error: {str(e)}"


def auto_init_test_function(config_path: str):
    """测试自动初始化的函数"""
    try:
        # 设置环境变量但不显式初始化
        os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = config_path

        # 直接获取logger，应该触发自动初始化
        from custom_logger import get_logger
        logger = get_logger("auto_init_test")
        logger.info("自动初始化测试")

        return "auto_init_success"
    except Exception as e:
        return f"auto_init_error: {str(e)}"


def stress_test_function(worker_id: int, config_path: str, message_count: int):
    """压力测试函数"""
    try:
        # 设置环境变量
        os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = config_path

        # 初始化
        from custom_logger import init_custom_logger_system, get_logger
        init_custom_logger_system()

        # 获取logger
        logger = get_logger(f"stress_worker_{worker_id}")

        # 记录大量日志
        for i in range(message_count):
            logger.info(f"Worker {worker_id} 消息 {i}")

        return f"Worker-{worker_id} logged {message_count} messages"
    except Exception as e:
        return f"Worker-{worker_id} error: {str(e)}"


def complex_config_test_function(config_path: str):
    """测试复杂配置的函数"""
    try:
        # 设置环境变量
        os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = config_path

        # 初始化
        from custom_logger import init_custom_logger_system, get_logger
        init_custom_logger_system()

        # 测试不同模块的配置
        logger1 = get_logger("complex_module_a")
        logger2 = get_logger("complex_module_b")
        logger_default = get_logger("default_module")

        # 记录日志
        logger1.debug("模块A调试信息")
        logger1.info("模块A信息")
        logger2.warning("模块B警告")
        logger_default.info("默认模块信息")

        return "complex_config_success"
    except Exception as e:
        return f"complex_config_error: {str(e)}"


def env_cleanup_test_function():
    """测试环境变量清理的函数"""
    try:
        # 不设置环境变量，直接尝试获取配置路径
        from custom_logger.config import get_config_file_path
        path = get_config_file_path()

        # 应该返回默认路径
        expected_default = os.path.join("src", "config", "config.yaml")
        if path == expected_default:
            return "default_path_correct"
        else:
            return f"default_path_wrong: {path}"
    except Exception as e:
        return f"env_cleanup_error: {str(e)}"


def isolation_test_function(config_path: str, expected_project: str):
    """隔离测试函数"""
    try:
        os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = config_path

        from custom_logger import init_custom_logger_system
        from custom_logger.config import get_root_config

        init_custom_logger_system()
        root_cfg = get_root_config()
        project_name = getattr(root_cfg, 'project_name', None)

        if project_name == expected_project:
            return f"isolation_success: {project_name}"
        else:
            return f"isolation_failed: expected={expected_project}, got={project_name}"
    except Exception as e:
        return f"isolation_error: {str(e)}"


def config_manager_test_function(config_path: str):
    """测试config_manager集成的函数"""
    try:
        os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = config_path

        from custom_logger import init_custom_logger_system, get_logger
        from custom_logger.config import get_root_config

        # 初始化并获取配置
        init_custom_logger_system()
        root_cfg = get_root_config()

        # 验证config_manager能正确工作
        project_name = getattr(root_cfg, 'project_name', None)
        logger_cfg = getattr(root_cfg, 'logger', None)

        if project_name != "config_manager_test":
            return f"project_name_wrong: {project_name}"

        if not logger_cfg:
            return "logger_config_missing"

        # 测试模块特定配置
        logger = get_logger("integration_test")

        # 验证级别配置正确
        from custom_logger.types import DEBUG, INFO
        if logger.console_level != DEBUG:
            return f"console_level_wrong: {logger.console_level}"

        if logger.file_level != INFO:
            return f"file_level_wrong: {logger.file_level}"

        return "config_manager_integration_success"
    except Exception as e:
        return f"config_manager_error: {str(e)}"


def test_tc0015_001_multiprocess_config_inheritance():
    """测试多进程配置继承"""
    import tempfile
    temp_dir = tempfile.gettempdir().replace("\\", "/")
    config_content = f"""project_name: "multiprocess_test"
experiment_name: "config_inheritance"
first_start_time: null
base_dir: "{temp_dir}/multiprocess"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    process_worker_0:
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

        # 主进程初始化
        init_custom_logger_system(config_path=config_path)

        # 验证环境变量被设置
        env_path = os.environ.get('CUSTOM_LOGGER_CONFIG_PATH')
        assert env_path == config_path

        # 启动子进程
        with ProcessPoolExecutor(max_workers=2) as executor:
            futures = []
            for i in range(2):
                future = executor.submit(worker_process_function, i, config_path)
                futures.append(future)

            # 收集结果
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=10)
                    results.append(result)
                except Exception as e:
                    results.append(f"Future error: {e}")

        # 验证结果
        assert len(results) == 2
        for result in results:
            assert "success" in result

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0015_002_config_path_inheritance():
    """测试配置路径在进程间的继承"""
    import tempfile
    temp_dir = tempfile.gettempdir().replace("\\", "/")
    config_content = f"""project_name: "path_inheritance_test"
experiment_name: "test"
first_start_time: null
base_dir: "{temp_dir}/test"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {{}}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 主进程设置配置路径
        set_config_path(config_path)

        # 验证主进程配置路径
        main_path = get_config_file_path()
        assert main_path == config_path

        # 在子进程中测试配置路径获取
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(simple_process_function, config_path)
            result = future.result(timeout=5)

        # 验证子进程能正确获取配置路径
        assert result == "config_path_correct"

    finally:
        set_config_path(None)
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0015_003_process_initialization():
    """测试进程中的日志系统初始化"""
    import tempfile
    temp_dir = tempfile.gettempdir().replace("\\", "/")
    config_content = f"""project_name: "process_init_test"
experiment_name: "initialization"
first_start_time: null
base_dir: "{temp_dir}/process_init"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {{}}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        # 测试1: 进程中显式初始化
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(process_init_test_function, True, config_path)
            result1 = future.result(timeout=10)

        assert result1 == "init_success"

        # 测试2: 进程中自动初始化（因为有环境变量配置路径）
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(process_init_test_function, False, config_path)
            result2 = future.result(timeout=10)

        # 由于有环境变量配置路径，自动初始化也会成功
        assert result2 == "init_success"

    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0015_004_yaml_serialization_compatibility():
    """测试YAML配置的序列化兼容性"""
    import tempfile
    temp_dir = tempfile.gettempdir().replace("\\", "/")
    config_content = f"""project_name: "yaml_test"
experiment_name: "serialization"
first_start_time: "2024-01-01T10:00:00"
base_dir: "{temp_dir}/yaml_test"

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
        # 在子进程中测试YAML配置加载
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(yaml_serialization_test_function, config_path)
            result = future.result(timeout=10)

        # 验证YAML配置能在子进程中正确加载
        assert result == "yaml_load_success"

    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0015_005_auto_initialization():
    """测试子进程中的自动初始化"""
    import tempfile
    temp_dir = tempfile.gettempdir().replace("\\", "/")
    config_content = f"""project_name: "auto_init_test"
experiment_name: "process_auto_init"
first_start_time: null
base_dir: "{temp_dir}/auto_init"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {{}}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        # 在子进程中测试自动初始化
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(auto_init_test_function, config_path)
            result = future.result(timeout=10)

        # 验证自动初始化成功
        assert result == "auto_init_success"

    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0015_006_multiprocess_stress():
    """测试多进程压力场景"""
    import tempfile
    temp_dir = tempfile.gettempdir().replace("\\", "/")
    config_content = f"""project_name: "stress_test"
experiment_name: "multiprocess_stress"
first_start_time: null
base_dir: "{temp_dir}/stress"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {{}}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        # 启动多个进程，每个进程记录多条日志
        with ProcessPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(3):
                future = executor.submit(stress_test_function, i, config_path, 10)
                futures.append(future)

            # 收集结果
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=15)
                    results.append(result)
                except Exception as e:
                    results.append(f"Future error: {e}")

        # 验证所有进程都成功
        assert len(results) == 3
        for result in results:
            assert "logged 10 messages" in result

    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0015_007_complex_config_inheritance():
    """测试复杂配置的继承"""
    config_content = f"""project_name: "complex_config_test"
experiment_name: "inheritance"
first_start_time: null
base_dir: "{temp_dir}/complex"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    complex_module_a:
      console_level: "debug"
      file_level: "detail"
    complex_module_b:
      console_level: "warning"
      file_level: "error"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        # 在子进程中测试复杂配置
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(complex_config_test_function, config_path)
            result = future.result(timeout=10)

        # 验证复杂配置正确加载
        assert result == "complex_config_success"

    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0015_008_environment_cleanup():
    """测试环境变量清理"""
    try:
        # 清理环境变量
        if 'CUSTOM_LOGGER_CONFIG_PATH' in os.environ:
            del os.environ['CUSTOM_LOGGER_CONFIG_PATH']

        # 在子进程中测试默认路径
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(env_cleanup_test_function)
            result = future.result(timeout=5)

        # 验证返回默认路径
        assert result == "default_path_correct"

    finally:
        # 确保清理
        if 'CUSTOM_LOGGER_CONFIG_PATH' in os.environ:
            del os.environ['CUSTOM_LOGGER_CONFIG_PATH']
    pass


def test_tc0015_009_process_isolation():
    """测试进程间的配置隔离"""
    # 创建两个不同的配置文件
    config1_content = """project_name: "isolation_test_1"
experiment_name: "process_1"
first_start_time: null
base_dir: "{temp_dir}/isolation1"

logger:
  global_console_level: "debug"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {{}}
"""

    config2_content = """project_name: "isolation_test_2"
experiment_name: "process_2"
first_start_time: null
base_dir: "{temp_dir}/isolation2"

logger:
  global_console_level: "error"
  global_file_level: "error"
  current_session_dir: null
  module_levels: {{}}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp1:
        tmp1.write(config1_content)
        config1_path = tmp1.name

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp2:
        tmp2.write(config2_content)
        config2_path = tmp2.name

    try:
        # 测试两个进程使用不同配置
        with ProcessPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(isolation_test_function, config1_path, "isolation_test_1")
            future2 = executor.submit(isolation_test_function, config2_path, "isolation_test_2")

            result1 = future1.result(timeout=10)
            result2 = future2.result(timeout=10)

        # 验证两个进程正确加载了各自的配置
        assert "isolation_success: isolation_test_1" in result1
        assert "isolation_success: isolation_test_2" in result2

    finally:
        if os.path.exists(config1_path):
            os.unlink(config1_path)
        if os.path.exists(config2_path):
            os.unlink(config2_path)
    pass


def test_tc0015_010_config_manager_integration():
    """测试config_manager集成的多进程兼容性"""
    config_content = f"""project_name: "config_manager_test"
experiment_name: "multiprocess_integration"
first_start_time: null
base_dir: "{temp_dir}/config_manager"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    integration_test:
      console_level: "debug"
      file_level: "info"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        # 在子进程中测试config_manager集成
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(config_manager_test_function, config_path)
            result = future.result(timeout=10)

        # 验证config_manager集成正确
        assert result == "config_manager_integration_success"

    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass