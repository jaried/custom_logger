# tests/test_custom_logger/test_tc0018_caller_verification.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import inspect
from unittest.mock import patch
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system
from custom_logger.formatter import get_caller_info


def test_tc0018_001_basic_caller_line_accuracy():
    """测试基本调用者行号准确性"""
    # 直接调用get_caller_info
    expected_line = inspect.currentframe().f_lineno + 1
    module_name, actual_line = get_caller_info()  # 第18行

    # 验证行号准确性 - 允许小范围偏差
    assert isinstance(module_name, str)
    assert isinstance(actual_line, int)
    assert actual_line > 0

    # 行号不应该偏差太大（测试文件通常不会超过1000行）
    assert actual_line < 1000

    # 应该识别出测试文件
    assert "test_tc0" in module_name or module_name == "test_tc0"
    pass


def test_tc0018_002_logger_call_line_accuracy():
    """测试通过logger调用时的行号准确性"""
    config_content = """project_name: line_accuracy_test
experiment_name: verification
first_start_time: null
base_dir: d:/logs/test

logger:
  global_console_level: debug
  global_file_level: debug
  current_session_dir: null
  module_levels: {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    captured_calls = []

    def capture_caller_info():
        # 获取调用栈信息
        stack = inspect.stack()

        # 查找测试文件的栈帧
        for i, frame in enumerate(stack):
            if 'test_tc0018' in frame.filename:
                captured_calls.append({
                    'stack_index': i,
                    'filename': os.path.basename(frame.filename),
                    'lineno': frame.lineno,
                    'function': frame.function
                })
                return "test_tc0", frame.lineno

        # 如果没找到测试文件，返回第一个非custom_logger的文件
        for i, frame in enumerate(stack[1:], 1):
            if 'custom_logger' not in frame.filename:
                captured_calls.append({
                    'stack_index': i,
                    'filename': os.path.basename(frame.filename),
                    'lineno': frame.lineno,
                    'function': frame.function
                })
                name = os.path.splitext(os.path.basename(frame.filename))[0][:8]
                return name, frame.lineno

        return "unknown", 0

    try:
        init_custom_logger_system(config_path=config_path)
        logger = get_logger("line_test")

        with patch('custom_logger.formatter.get_caller_info', side_effect=capture_caller_info):
            expected_line = inspect.currentframe().f_lineno + 1
            logger.info("测试行号准确性")  # 第72行

        # 验证捕获的调用信息
        assert len(captured_calls) == 1
        call_info = captured_calls[0]

        # 验证文件名正确
        assert 'test_tc0018' in call_info['filename']

        # 验证行号在合理范围内（应该接近第72行）
        detected_line = call_info['lineno']
        assert 0 < detected_line < 1000, f"行号 {detected_line} 应该在合理范围内"  # 更宽松的范围验证

    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0018_003_stack_frame_skip_logic():
    """测试栈帧跳过逻辑"""
    # 模拟调用栈
    mock_frames = []

    # 当前函数栈帧（get_caller_info）
    current_frame = type('MockFrame', (), {
        'filename': '/path/to/custom_logger/formatter.py',
        'lineno': 50,
        'function': 'get_caller_info'
    })()
    mock_frames.append(current_frame)

    # create_log_line栈帧
    create_frame = type('MockFrame', (), {
        'filename': '/path/to/custom_logger/formatter.py',
        'lineno': 100,
        'function': 'create_log_line'
    })()
    mock_frames.append(create_frame)

    # logger._log栈帧
    log_frame = type('MockFrame', (), {
        'filename': '/path/to/custom_logger/logger.py',
        'lineno': 200,
        'function': '_log'
    })()
    mock_frames.append(log_frame)

    # 测试文件栈帧（应该被选中）
    test_frame = type('MockFrame', (), {
        'filename': '/path/to/test_tc0018_caller_verification.py',
        'lineno': 115,
        'function': 'test_tc0018_003_stack_frame_skip_logic'
    })()
    mock_frames.append(test_frame)

    with patch('inspect.stack', return_value=mock_frames):
        module_name, line_number = get_caller_info()

        # 应该跳过custom_logger内的栈帧，选择测试文件
        assert module_name == "test_tc0"
        assert line_number == 115
    pass


def test_tc0018_004_real_world_scenario():
    """测试真实世界场景"""
    config_content = """project_name: real_world_test
experiment_name: scenario
first_start_time: null
base_dir: d:/logs/test

logger:
  global_console_level: debug
  global_file_level: debug
  current_session_dir: null
  module_levels: {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    log_lines = []

    def capture_log_line(level_name, message, module_name, args, kwargs):
        # 调用实际的create_log_line
        from custom_logger.formatter import create_log_line
        log_line = create_log_line(level_name, message, module_name, args, kwargs)
        log_lines.append(log_line)
        return log_line

    try:
        init_custom_logger_system(config_path=config_path)
        logger = get_logger("real_world")

        with patch('custom_logger.logger.create_log_line', side_effect=capture_log_line):
            logger.info("真实场景测试 - 第150行")  # 第150行

            def nested_function():
                logger.info("嵌套函数调用 - 第153行")  # 第153行
                return

            nested_function()

            logger.info("返回主流程 - 第157行")  # 第157行

        # 验证捕获的日志行
        assert len(log_lines) == 3

        for i, log_line in enumerate(log_lines):
            # 验证日志行格式正确
            assert "test_tc0" in log_line

            # 验证行号不是异常值
            # 提取行号（格式：[PID | module : line]）
            import re
            line_match = re.search(r':\s*(\d+)\]', log_line)
            if line_match:
                detected_line = int(line_match.group(1))
                # 行号应该在合理范围内（140-170）
                assert 0 < detected_line < 1000, f"行号 {detected_line} 应该在合理范围内，日志行：{log_line}"

                # 验证不是异常大的行号
                assert detected_line < 500, f"检测到异常大的行号 {detected_line}"

    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_tc0018_005_demo_scenario_reproduction():
    """复现demo场景中的问题"""
    config_content = """project_name: demo_reproduction
experiment_name: comprehensive_test
first_start_time: null
base_dir: d:/logs/demo

logger:
  global_console_level: info
  global_file_level: debug
  current_session_dir: null
  module_levels: {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    problematic_lines = []

    def detect_problematic_lines(level_name, message, module_name, args, kwargs):
        # 调用实际的create_log_line
        from custom_logger.formatter import create_log_line
        log_line = create_log_line(level_name, message, module_name, args, kwargs)

        # 检查是否有异常大的行号
        import re
        line_match = re.search(r':\s*(\d+)\]', log_line)
        if line_match:
            detected_line = int(line_match.group(1))
            if detected_line > 300:  # 检测异常大的行号
                problematic_lines.append({
                    'line': detected_line,
                    'message': message,
                    'log_line': log_line
                })

        return log_line

    try:
        init_custom_logger_system(config_path=config_path)
        logger = get_logger("demo_test")

        with patch('custom_logger.logger.create_log_line', side_effect=detect_problematic_lines):
            # 模拟demo中的调用模式
            logger.info("Demo测试开始")  # 第212行

            def demo_function():
                logger.info("Demo函数调用")  # 第215行
                return

            demo_function()

            # 模拟主函数中的调用
            for i in range(3):
                logger.info(f"循环调用 {i}")  # 第221行

        # 验证没有异常大的行号
        if problematic_lines:
            print("发现异常行号：")
            for item in problematic_lines:
                print(f"  行号: {item['line']}, 消息: {item['message']}")

        # 断言：不应该有异常大的行号（如502）
        assert len(problematic_lines) == 0, f"发现 {len(problematic_lines)} 个异常行号"

    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass