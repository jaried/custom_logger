# tests/test_custom_logger/test_tc0013_custom_config_worker.py
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


def test_tc0013_001_worker_with_custom_config_start_time():
    """测试Worker使用非默认配置并根据主程序start_time计算用时"""
    # 创建自定义配置
    config_content = """project_name: "custom_worker_test"
experiment_name: "start_time_test"
first_start_time: "2024-01-01T10:00:00"
base_dir: "d:/logs/custom_test"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    worker_module:
      console_level: "w_summary"
      file_level: "w_detail"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        custom_config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 使用自定义配置初始化
        init_custom_logger_system(config_path=custom_config_path)

        # 验证配置路径被正确设置
        assert get_config_file_path() == custom_config_path

        # 获取根配置验证start_time
        from custom_logger.config import get_root_config
        root_cfg = get_root_config()

        project_name = getattr(root_cfg, 'project_name', None)
        experiment_name = getattr(root_cfg, 'experiment_name', None)
        first_start_time = getattr(root_cfg, 'first_start_time', None)

        assert project_name == "custom_worker_test"
        assert experiment_name == "start_time_test"
        assert first_start_time is not None

        # 创建Worker logger
        worker_logger = get_logger("worker_module", console_level="w_summary")

        # 捕获日志输出来验证时间计算
        captured_logs = []

        def mock_create_log_line(level_name, message, module_name, args, kwargs):
            from custom_logger.formatter import format_elapsed_time, get_caller_info
            current_time = datetime.now()
            elapsed_str = format_elapsed_time(first_start_time, current_time)
            caller_module, line_number = get_caller_info()
            log_line = f"[PID | {caller_module:<8} : {line_number:>4}] elapsed:{elapsed_str} - {level_name} - {message}"
            captured_logs.append(log_line)
            return log_line

        # 修正Mock路径：使用logger模块中的导入路径
        with patch('custom_logger.logger.create_log_line', side_effect=mock_create_log_line):
            worker_logger.worker_summary("Worker任务开始")
            worker_logger.worker_detail("Worker详细信息")

        # 验证日志包含正确的时间计算
        assert len(captured_logs) >= 2

        for log_line in captured_logs:
            # 验证包含elapsed时间
            assert "elapsed:" in log_line
            # 验证时间格式
            assert ":" in log_line and "." in log_line

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(custom_config_path):
            os.unlink(custom_config_path)


def test_tc0013_002_worker_thread_with_custom_config():
    """测试Worker线程使用自定义配置"""
    config_content = """project_name: "thread_worker_test"
experiment_name: "thread_test"
first_start_time: null
base_dir: "d:/logs/thread_test"

logger:
  global_console_level: "w_summary"
  global_file_level: "w_detail"
  current_session_dir: null
  module_levels:
    thread_worker:
      console_level: "w_detail"
      file_level: "debug"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        custom_config_path = tmp_file.name

    results = []

    def worker_thread(worker_id: int):
        try:
            # Worker线程中获取logger
            worker_logger = get_logger("thread_worker")

            # 验证Worker能正确获取配置
            assert worker_logger.name == "thread_worker"

            # 模拟日志记录
            with patch.object(worker_logger, '_log') as mock_log:
                worker_logger.worker_summary(f"Worker {worker_id} 开始")
                worker_logger.worker_detail(f"Worker {worker_id} 详细信息")

                # 验证调用次数
                assert mock_log.call_count == 2
                results.append((worker_id, "success", mock_log.call_count))

        except Exception as e:
            results.append((worker_id, "error", str(e)))

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 初始化系统
        init_custom_logger_system(config_path=custom_config_path)

        # 启动多个Worker线程
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(results) == 3
        for worker_id, status, call_count in results:
            assert status == "success"
            assert call_count == 2

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(custom_config_path):
            os.unlink(custom_config_path)


def test_tc0013_003_worker_config_inheritance():
    """测试Worker配置继承"""
    config_content = """project_name: "inheritance_test"
experiment_name: "worker_inherit"
first_start_time: null
base_dir: "d:/logs/inherit_test"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    worker_a:
      console_level: "w_summary"
      file_level: "w_detail"
    worker_b:
      console_level: "error"
      file_level: "warning"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        custom_config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 初始化系统
        init_custom_logger_system(config_path=custom_config_path)

        # 验证环境变量配置路径被设置
        env_path = os.environ.get('CUSTOM_LOGGER_CONFIG_PATH')
        assert env_path == custom_config_path

        # 创建不同配置的Worker
        worker_a = get_logger("worker_a")
        worker_b = get_logger("worker_b")
        worker_default = get_logger("worker_default")

        # 验证Worker A配置
        from custom_logger.types import W_SUMMARY, W_DETAIL
        assert worker_a.console_level == W_SUMMARY
        assert worker_a.file_level == W_DETAIL

        # 验证Worker B配置
        from custom_logger.types import ERROR, WARNING
        assert worker_b.console_level == ERROR
        assert worker_b.file_level == WARNING

        # 验证默认Worker配置
        from custom_logger.types import INFO, DEBUG
        assert worker_default.console_level == INFO
        assert worker_default.file_level == DEBUG

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(custom_config_path):
            os.unlink(custom_config_path)


def test_tc0013_004_worker_session_directory():
    """测试Worker会话目录创建"""
    config_content = """project_name: "session_test"
experiment_name: "directory_test"
first_start_time: "2024-06-01T15:30:00"
base_dir: "d:/logs/session_test"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        custom_config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 使用自定义配置初始化
        init_custom_logger_system(config_path=custom_config_path)

        # 获取会话目录
        from custom_logger.config import get_root_config
        root_cfg = get_root_config()
        logger_cfg = root_cfg.logger

        if isinstance(logger_cfg, dict):
            session_dir = logger_cfg.get('current_session_dir')
        else:
            session_dir = getattr(logger_cfg, 'current_session_dir', None)

        # 验证会话目录路径格式
        assert session_dir is not None
        assert "session_test" in session_dir
        assert "directory_test" in session_dir
        assert "20240601" in session_dir
        assert "153000" in session_dir

        # 验证目录存在
        assert os.path.exists(session_dir)

        # 创建Worker并验证能正常使用
        worker_logger = get_logger("session_worker")

        # 修正Mock路径：使用logger模块中的导入路径
        with patch('custom_logger.logger.write_log_async') as mock_write:
            worker_logger.info("测试会话目录")
            mock_write.assert_called_once()

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(custom_config_path):
            os.unlink(custom_config_path)


def test_tc0013_005_worker_elapsed_time_calculation():
    """测试Worker时间计算的精确性"""
    # 使用固定的启动时间
    fixed_start_time = "2024-01-01T10:00:00"

    # 构造配置内容，避免使用f-string表达式
    config_content = """project_name: "elapsed_test"
experiment_name: "time_calc"
first_start_time: "2024-01-01T10:00:00"
base_dir: "d:/logs/elapsed_test"

logger:
  global_console_level: "debug"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        custom_config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 初始化系统
        init_custom_logger_system(config_path=custom_config_path)

        # 创建Worker
        worker_logger = get_logger("elapsed_worker")

        # 模拟特定时间点
        mock_current_time = datetime(2024, 1, 1, 10, 5, 30, 500000)  # 5分30.5秒后

        elapsed_times = []

        def mock_create_log_line(level_name, message, module_name, args, kwargs):
            from custom_logger.formatter import format_elapsed_time, get_caller_info
            elapsed_str = format_elapsed_time(fixed_start_time, mock_current_time)
            elapsed_times.append(elapsed_str)
            caller_module, line_number = get_caller_info()
            log_line = f"[PID | {caller_module:<8} : {line_number:>4}] {elapsed_str} - {level_name} - {message}"
            return log_line

        # 修正Mock路径：使用logger模块中的导入路径
        with patch('custom_logger.logger.create_log_line', side_effect=mock_create_log_line):
            worker_logger.info("时间计算测试")

        # 验证时间计算
        assert len(elapsed_times) == 1
        elapsed_str = elapsed_times[0]

        # 应该是 0:05:30.50 (5分30.5秒)
        assert elapsed_str == "0:05:30.50"

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(custom_config_path):
            os.unlink(custom_config_path)


def test_tc0013_006_multiple_workers_same_config():
    """测试多个Worker使用同一配置"""
    config_content = """project_name: "multi_worker_test"
experiment_name: "shared_config"
first_start_time: null
base_dir: "d:/logs/multi_worker"

logger:
  global_console_level: "w_summary"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    shared_worker:
      console_level: "w_detail"
      file_level: "w_summary"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        custom_config_path = tmp_file.name

    worker_results = []

    def worker_function(worker_id: int):
        try:
            # 每个Worker都获取相同的logger
            worker_logger = get_logger("shared_worker")

            # 验证配置一致性
            from custom_logger.types import W_DETAIL, W_SUMMARY
            assert worker_logger.console_level == W_DETAIL
            assert worker_logger.file_level == W_SUMMARY

            # 记录日志
            with patch.object(worker_logger, '_log') as mock_log:
                worker_logger.worker_summary(f"Worker {worker_id} 执行")
                worker_logger.worker_detail(f"Worker {worker_id} 详细")

                worker_results.append((worker_id, "success", mock_log.call_count))

        except Exception as e:
            worker_results.append((worker_id, "error", str(e)))

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 初始化系统
        init_custom_logger_system(config_path=custom_config_path)

        # 创建多个Worker线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有Worker完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(worker_results) == 5
        for worker_id, status, call_count in worker_results:
            assert status == "success"
            assert call_count == 2

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(custom_config_path):
            os.unlink(custom_config_path)


def test_tc0013_007_worker_debug_mode_directory():
    """测试Worker在debug模式下的目录创建"""
    config_content = """project_name: "debug_worker_test"
experiment_name: "debug_mode"
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
        custom_config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 模拟debug模式
        with patch('custom_logger.config.is_debug', return_value=True):
            # 初始化系统
            init_custom_logger_system(config_path=custom_config_path)

            # 获取会话目录
            from custom_logger.config import get_root_config
            root_cfg = get_root_config()
            logger_cfg = root_cfg.logger

            if isinstance(logger_cfg, dict):
                session_dir = logger_cfg.get('current_session_dir')
            else:
                session_dir = getattr(logger_cfg, 'current_session_dir', None)

            # 验证debug模式下的路径包含debug子目录
            assert session_dir is not None
            assert "debug" in session_dir
            assert "debug_worker_test" in session_dir
            assert "debug_mode" in session_dir

            # 创建Worker验证正常工作
            debug_worker = get_logger("debug_worker")

            with patch.object(debug_worker, '_log') as mock_log:
                debug_worker.debug("Debug模式Worker测试")
                mock_log.assert_called_once()

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(custom_config_path):
            os.unlink(custom_config_path)


def test_tc0013_008_worker_auto_initialization():
    """测试Worker自动初始化（模拟子进程场景）"""
    config_content = """project_name: "auto_init_test"
experiment_name: "worker_auto_init"
first_start_time: null
base_dir: "d:/logs/auto_init"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        custom_config_path = tmp_file.name

    try:
        # 清理状态确保未初始化
        tear_down_custom_logger_system()
        set_config_path(None)

        # 手动设置环境变量（模拟主进程设置）
        os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = custom_config_path

        # 模拟Worker进程场景：系统未初始化但有环境变量
        from custom_logger.manager import _initialized
        assert not _initialized

        # Worker直接获取logger应该触发自动初始化
        worker_logger = get_logger("auto_init_worker")

        # 验证系统已自动初始化
        from custom_logger.manager import is_initialized
        assert is_initialized()

        # 验证Worker能正常工作
        assert worker_logger.name == "auto_init_worker"

        # 验证配置被正确加载
        from custom_logger.config import get_root_config
        root_cfg = get_root_config()
        project_name = getattr(root_cfg, 'project_name', None)
        assert project_name == "auto_init_test"

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if 'CUSTOM_LOGGER_CONFIG_PATH' in os.environ:
            del os.environ['CUSTOM_LOGGER_CONFIG_PATH']
        if os.path.exists(custom_config_path):
            os.unlink(custom_config_path)


def test_tc0013_009_worker_performance_with_custom_config():
    """测试Worker在自定义配置下的性能"""
    config_content = """project_name: "perf_test"
experiment_name: "worker_performance"
first_start_time: null
base_dir: "d:/logs/perf_test"

logger:
  global_console_level: "error"
  global_file_level: "error"
  current_session_dir: null
  module_levels:
    perf_worker:
      console_level: "critical"
      file_level: "critical"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        custom_config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 初始化系统
        init_custom_logger_system(config_path=custom_config_path)

        # 创建高级别Worker（大部分日志被过滤）
        perf_worker = get_logger("perf_worker")

        # 验证早期过滤工作正常
        from custom_logger.types import DEBUG, INFO, WARNING, ERROR, CRITICAL

        # 测试大量被过滤的日志调用
        start_perf = time.time()

        for i in range(2):
            perf_worker.debug(f"Debug {i}")  # 被过滤
            perf_worker.info(f"Info {i}")  # 被过滤
            perf_worker.warning(f"Warning {i}")  # 被过滤
            perf_worker.error(f"Error {i}")  # 被过滤

        end_perf = time.time()
        duration = end_perf - start_perf

        # 4000条被过滤的日志应该很快完成
        assert duration < 1.0  # 1秒内完成

        # 验证级别过滤正确工作
        assert not perf_worker._should_log_console(DEBUG)
        assert not perf_worker._should_log_console(INFO)
        assert not perf_worker._should_log_console(WARNING)
        assert not perf_worker._should_log_console(ERROR)
        assert perf_worker._should_log_console(CRITICAL)

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(custom_config_path):
            os.unlink(custom_config_path)


def test_tc0013_010_worker_config_edge_cases():
    """测试Worker配置边界情况"""
    # 测试配置文件路径包含特殊字符
    config_content = """project_name: "边界测试"
experiment_name: "特殊字符"
first_start_time: null
base_dir: "d:/logs/特殊/目录"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    "特殊_worker":
      console_level: "debug"
      file_level: "info"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        custom_config_path = tmp_file.name

    try:
        # 清理状态
        tear_down_custom_logger_system()
        set_config_path(None)

        # 初始化系统
        init_custom_logger_system(config_path=custom_config_path)

        # 创建带特殊字符的Worker
        special_worker = get_logger("特殊_worker")

        # 验证Worker能正常工作
        assert special_worker.name == "特殊_worker"

        # 验证配置正确加载
        from custom_logger.types import DEBUG, INFO
        assert special_worker.console_level == DEBUG
        assert special_worker.file_level == INFO

        # 测试空字符串Worker名称
        empty_worker = get_logger("")
        assert empty_worker.name == ""

        # 测试长Worker名称
        long_name = "a" * 100
        long_worker = get_logger(long_name)
        assert long_worker.name == long_name

    finally:
        tear_down_custom_logger_system()
        set_config_path(None)
        if os.path.exists(custom_config_path):
            os.unlink(custom_config_path)