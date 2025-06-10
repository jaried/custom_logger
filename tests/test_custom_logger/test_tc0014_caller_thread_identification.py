# tests/test_custom_logger/test_tc0014_caller_thread_identification.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import threading
import time
from unittest.mock import patch, MagicMock
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system
from custom_logger.formatter import get_caller_info


def test_tc0014_001_caller_info_from_thread():
    """测试线程中调用者识别"""
    results = []

    def thread_function():
        """线程函数"""
        module_name, line_number = get_caller_info()
        results.append((module_name, line_number))
        return

    # 创建并启动线程
    thread = threading.Thread(target=thread_function)
    thread.start()
    thread.join()

    # 验证结果
    assert len(results) == 1
    module_name, line_number = results[0]

    # 应该识别出当前测试文件，而不是threading相关的模块
    assert isinstance(module_name, str)
    assert len(module_name) <= 8
    assert module_name != "threadin"  # 不应该是threading的内部标识
    assert module_name != "unknown"
    assert line_number > 0
    pass


def test_tc0014_002_caller_info_skip_threading():
    """测试跳过线程相关调用栈"""
    import inspect

    # Mock调用栈，包含threading相关文件
    mock_frames = []

    # 添加threading.py相关的栈帧（应该被跳过）
    threading_frame = MagicMock()
    threading_frame.filename = "/usr/lib/python3.12/threading.py"
    threading_frame.lineno = 1012
    mock_frames.append(threading_frame)

    # 添加_bootstrap相关的栈帧（应该被跳过）
    bootstrap_frame = MagicMock()
    bootstrap_frame.filename = "/usr/lib/python3.12/threading.py"
    bootstrap_frame.lineno = 1075
    mock_frames.append(bootstrap_frame)

    # 添加用户代码栈帧（应该被识别）
    user_frame = MagicMock()
    user_frame.filename = "/path/to/demo_worker_test.py"
    user_frame.lineno = 50
    mock_frames.append(user_frame)

    with patch('inspect.stack', return_value=mock_frames):
        module_name, line_number = get_caller_info()

        # 应该跳过threading相关文件，识别用户代码
        assert module_name == "demo_wor"  # demo_worker_test的前8位
        assert line_number == 50
    pass


def test_tc0014_003_logger_caller_in_thread():
    """测试线程中logger调用的调用者识别"""
    config_content = f"""project_name: "thread_caller_test"
experiment_name: "test"
first_start_time: null
base_dir: "{temp_dir}/test"

logger:
  global_console_level: "w_detail"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {{}}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        import tempfile
        temp_dir = tempfile.gettempdir().replace("\\", "/")
        tmp_file.write(config_content)
        config_path = tmp_file.name

    captured_callers = []

    def mock_get_caller_info():
        """Mock get_caller_info来验证被正确调用"""
        # 应该被调用并返回正确的调用者信息
        captured_callers.append("called")
        return "test_tc0", 25  # 返回测试文件标识

    results = []

    def thread_worker():
        """线程worker函数"""
        try:
            logger = get_logger("thread_test")

            # Mock get_caller_info函数
            with patch('custom_logger.formatter.get_caller_info', side_effect=mock_get_caller_info):
                logger.info("线程中的日志消息")
                results.append("success")
        except Exception as e:
            results.append(f"error: {e}")

    try:
        # 初始化日志系统
        init_custom_logger_system(config_path=config_path)

        # 在线程中执行logger调用
        thread = threading.Thread(target=thread_worker)
        thread.start()
        thread.join()

        # 验证结果
        assert len(results) == 1
        assert results[0] == "success"
        assert len(captured_callers) >= 1  # get_caller_info被调用

    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0014_004_complex_call_stack():
    """测试复杂调用栈的处理"""
    import inspect

    # 创建复杂的调用栈
    mock_frames = []

    # 当前函数栈帧
    current_frame = MagicMock()
    current_frame.filename = "/path/to/formatter.py"
    current_frame.lineno = 20
    mock_frames.append(current_frame)

    # custom_logger内部栈帧（应该被跳过）
    logger_frame = MagicMock()
    logger_frame.filename = "/path/to/custom_logger/logger.py"
    logger_frame.lineno = 100
    mock_frames.append(logger_frame)

    # threading相关栈帧（应该被跳过）
    thread_frame = MagicMock()
    thread_frame.filename = "/usr/lib/python3.12/threading.py"
    thread_frame.lineno = 1012
    mock_frames.append(thread_frame)

    # 用户代码栈帧（应该被识别）
    user_frame = MagicMock()
    user_frame.filename = "/path/to/user_code.py"
    user_frame.lineno = 42
    mock_frames.append(user_frame)

    with patch('inspect.stack', return_value=mock_frames):
        module_name, line_number = get_caller_info()

        # 应该识别出用户代码
        assert module_name == "user_cod"  # user_code的前8位
        assert line_number == 42
    pass


def test_tc0014_005_threading_bootstrap_skip():
    """测试跳过threading._bootstrap相关调用"""
    import inspect

    mock_frames = []

    # 添加_bootstrap_inner栈帧（应该被跳过）
    bootstrap_frame = MagicMock()
    bootstrap_frame.filename = "/usr/lib/python3.12/threading.py"
    bootstrap_frame.lineno = 1075
    mock_frames.append(bootstrap_frame)

    # 添加run方法栈帧（应该被跳过）
    run_frame = MagicMock()
    run_frame.filename = "/usr/lib/python3.12/threading.py"
    run_frame.lineno = 1012
    mock_frames.append(run_frame)

    # 添加实际的用户函数栈帧
    user_frame = MagicMock()
    user_frame.filename = "/path/to/worker_function.py"
    user_frame.lineno = 30
    mock_frames.append(user_frame)

    with patch('inspect.stack', return_value=mock_frames):
        module_name, line_number = get_caller_info()

        # 应该正确识别用户函数
        assert module_name == "worker_f"  # worker_function的前8位
        assert line_number == 30
    pass


def test_tc0014_006_multiple_threads_caller():
    """测试多线程环境下的调用者识别"""
    config_content = f"""project_name: "multi_thread_test"
experiment_name: "caller_test"
first_start_time: null
base_dir: "{temp_dir}/test"

logger:
  global_console_level: "info"  
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {{}}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        import tempfile
        temp_dir = tempfile.gettempdir().replace("\\", "/")
        tmp_file.write(config_content)
        config_path = tmp_file.name

    results = []
    call_counts = []

    def mock_get_caller_info():
        """Mock函数来验证调用"""
        call_counts.append(1)
        return "test_tc0", len(call_counts)  # 返回不同的行号

    def worker_thread(thread_id):
        """Worker线程函数"""
        try:
            logger = get_logger(f"thread_{thread_id}")

            with patch('custom_logger.formatter.get_caller_info', side_effect=mock_get_caller_info):
                logger.info(f"线程 {thread_id} 消息")
                results.append((thread_id, "success"))
        except Exception as e:
            results.append((thread_id, f"error: {e}"))

    try:
        # 初始化日志系统
        init_custom_logger_system(config_path=config_path)

        # 创建多个线程
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(results) == 3
        for thread_id, status in results:
            assert status == "success"

        # 验证get_caller_info被正确调用
        assert len(call_counts) >= 3

    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0014_007_real_threading_identification():
    """测试真实threading环境下的识别"""
    config_content = f"""project_name: "real_thread_test"
experiment_name: "identification"
first_start_time: null
base_dir: "{temp_dir}/test"

logger:
  global_console_level: "debug"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {{}}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        import tempfile
        temp_dir = tempfile.gettempdir().replace("\\", "/")
        tmp_file.write(config_content)
        config_path = tmp_file.name

    captured_lines = []

    def capture_log_line(level_name, message, module_name, args, kwargs):
        """捕获日志行"""
        from custom_logger.formatter import get_caller_info
        caller_module, line_number = get_caller_info()
        log_line = f"[{caller_module:<8} : {line_number:>4}] {level_name} - {message}"
        captured_lines.append(log_line)
        return log_line

    results = []

    def real_worker_function():
        """真实的worker函数，不使用Mock"""
        try:
            logger = get_logger("real_worker")

            # 不使用Mock，让系统自然调用get_caller_info
            with patch('custom_logger.logger.create_log_line', side_effect=capture_log_line):
                logger.info("真实线程测试消息")
                results.append("logged")
        except Exception as e:
            results.append(f"error: {e}")

    try:
        # 初始化日志系统
        init_custom_logger_system(config_path=config_path)

        # 在真实线程中执行
        thread = threading.Thread(target=real_worker_function)
        thread.start()
        thread.join()

        # 验证结果
        assert len(results) == 1
        assert results[0] == "logged"
        assert len(captured_lines) == 1

        # 验证日志行不包含threading内部标识
        log_line = captured_lines[0]
        assert "threadin" not in log_line  # 不应该显示threading内部标识
        assert ": " in log_line  # 应该有正确的格式

    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0014_008_custom_logger_only_stack():
    """测试只有custom_logger调用栈的情况"""
    import inspect

    # 创建只包含custom_logger文件的调用栈
    mock_frames = []

    for i in range(3):
        frame = MagicMock()
        frame.filename = f"/path/to/custom_logger/module{i}.py"
        frame.lineno = 100 + i
        mock_frames.append(frame)

    with patch('inspect.stack', return_value=mock_frames):
        module_name, line_number = get_caller_info()

        # 应该返回最后一个custom_logger栈帧的信息
        assert module_name == "module2"  # 最后一个文件
        assert line_number == 102  # 最后一个行号
    pass


def test_tc0014_009_skip_pattern_effectiveness():
    """测试跳过模式的有效性"""
    import inspect

    # 测试所有跳过模式
    skip_cases = [
        ("/path/to/custom_logger/logger.py", 100),
        ("/usr/lib/python3.12/threading.py", 200),
        ("/path/to/_bootstrap_module.py", 300),
    ]

    for skip_file, skip_line in skip_cases:
        mock_frames = []

        # 添加应该被跳过的栈帧
        skip_frame = MagicMock()
        skip_frame.filename = skip_file
        skip_frame.lineno = skip_line
        mock_frames.append(skip_frame)

        # 添加用户代码栈帧
        user_frame = MagicMock()
        user_frame.filename = "/path/to/user_code.py"
        user_frame.lineno = 50
        mock_frames.append(user_frame)

        with patch('inspect.stack', return_value=mock_frames):
            module_name, line_number = get_caller_info()

            # 应该跳过第一个，识别用户代码
            assert module_name == "user_cod"
            assert line_number == 50
    pass


def test_tc0014_010_concurrent_caller_identification():
    """测试并发调用者识别"""
    config_content = f"""project_name: "concurrent_test"
experiment_name: "caller_test"
first_start_time: null
base_dir: "{temp_dir}/test"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {{}}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        import tempfile
        temp_dir = tempfile.gettempdir().replace("\\", "/")
        tmp_file.write(config_content)
        config_path = tmp_file.name

    results = []
    lock = threading.Lock()

    def concurrent_worker(worker_id):
        """并发worker函数"""
        try:
            logger = get_logger(f"worker_{worker_id}")

            # 使用真实的调用者识别，不Mock
            for i in range(5):
                logger.info(f"Worker {worker_id} 消息 {i}")
                time.sleep(0.01)  # 小延迟模拟真实工作

            with lock:
                results.append((worker_id, "success"))
        except Exception as e:
            with lock:
                results.append((worker_id, f"error: {e}"))

    try:
        # 初始化日志系统
        init_custom_logger_system(config_path=config_path)

        # 创建多个并发线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=concurrent_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(results) == 5
        for worker_id, status in results:
            assert status == "success"

    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass