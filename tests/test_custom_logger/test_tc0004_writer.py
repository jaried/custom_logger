# tests/test_custom_logger/test_tc0004_writer.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import threading
import time
import pytest
from unittest.mock import patch, MagicMock, mock_open
from custom_logger.writer import (
    LogEntry, FileWriter, init_writer, write_log_async,
    shutdown_writer, QUEUE_SENTINEL, _log_queue, _writer_thread, _stop_event
)
from custom_logger.types import ERROR, WARNING, INFO


def test_tc0004_001_log_entry_creation():
    """测试日志条目创建"""
    entry = LogEntry("Test log line", INFO, "test_logger", "Exception info")

    assert entry.log_line == "Test log line"
    assert entry.level_value == INFO
    assert entry.logger_name == "test_logger"
    assert entry.exception_info == "Exception info"
    pass


def test_tc0004_002_log_entry_no_exception():
    """测试无异常信息的日志条目"""
    entry = LogEntry("Test log line", ERROR, "test_logger")

    assert entry.log_line == "Test log line"
    assert entry.level_value == ERROR
    assert entry.logger_name == "test_logger"
    assert entry.exception_info is None
    pass


def test_tc0004_003_file_writer_init():
    """测试文件写入器初始化"""
    with tempfile.TemporaryDirectory() as temp_dir:
        writer = FileWriter(temp_dir)

        # 验证文件被创建
        full_log_path = os.path.join(temp_dir, "full.log")
        warning_log_path = os.path.join(temp_dir, "warning.log")

        assert os.path.exists(full_log_path)
        assert os.path.exists(warning_log_path)

        writer.close()
    pass


def test_tc0004_004_file_writer_init_failure():
    """测试文件写入器初始化失败"""
    # 使用一个无效路径
    invalid_path = "/invalid/path/that/does/not/exist"

    with patch('sys.stderr'):
        writer = FileWriter(invalid_path)

        # 即使失败，对象也应该被创建
        assert writer.session_dir == invalid_path
        writer.close()
    pass


def test_tc0004_005_file_writer_write_info_log():
    """测试写入INFO级别日志"""
    with tempfile.TemporaryDirectory() as temp_dir:
        writer = FileWriter(temp_dir)
        entry = LogEntry("Info message", INFO, "test_logger")

        writer.write_log(entry)
        writer.close()

        # 检查full.log有内容，warning.log为空
        full_log_path = os.path.join(temp_dir, "full.log")
        warning_log_path = os.path.join(temp_dir, "warning.log")

        with open(full_log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Info message" in content

        # INFO级别不应写入warning.log
        with open(warning_log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert content.strip() == ""
    pass


def test_tc0004_006_file_writer_write_warning_log():
    """测试写入WARNING级别日志"""
    with tempfile.TemporaryDirectory() as temp_dir:
        writer = FileWriter(temp_dir)
        entry = LogEntry("Warning message", WARNING, "test_logger", "Stack trace")

        writer.write_log(entry)
        writer.close()

        # 检查两个文件都有内容
        full_log_path = os.path.join(temp_dir, "full.log")
        warning_log_path = os.path.join(temp_dir, "warning.log")

        with open(full_log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Warning message" in content
            assert "Stack trace" in content

        with open(warning_log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Warning message" in content
            assert "Stack trace" in content
    pass


def test_tc0004_006b_file_writer_write_error_log():
    """测试写入ERROR级别日志也会写入warning.log"""
    with tempfile.TemporaryDirectory() as temp_dir:
        writer = FileWriter(temp_dir)
        entry = LogEntry("Error message", ERROR, "test_logger", "Stack trace")

        writer.write_log(entry)
        writer.close()

        # 检查两个文件都有内容
        full_log_path = os.path.join(temp_dir, "full.log")
        warning_log_path = os.path.join(temp_dir, "warning.log")

        with open(full_log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Error message" in content
            assert "Stack trace" in content

        # ERROR级别应该写入warning.log
        with open(warning_log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Error message" in content
            assert "Stack trace" in content
    pass


def test_tc0004_007_file_writer_write_failure():
    """测试文件写入失败处理"""
    with tempfile.TemporaryDirectory() as temp_dir:
        writer = FileWriter(temp_dir)

        # 关闭文件句柄模拟写入失败
        writer.full_log_file.close()
        writer.warning_log_file.close()

        entry = LogEntry("Test message", ERROR, "test_logger")

        with patch('sys.stderr'):
            writer.write_log(entry)  # 应该不抛出异常

        writer.close()
    pass


def test_tc0004_008_file_writer_close():
    """测试文件写入器关闭"""
    with tempfile.TemporaryDirectory() as temp_dir:
        writer = FileWriter(temp_dir)

        # 验证文件被打开
        assert writer.full_log_file is not None
        assert writer.warning_log_file is not None

        writer.close()

        # 验证文件被关闭
        assert writer.full_log_file is None
        assert writer.warning_log_file is None
    pass


def test_tc0004_009_file_writer_close_failure():
    """测试文件关闭失败处理"""
    with tempfile.TemporaryDirectory() as temp_dir:
        writer = FileWriter(temp_dir)

        # 确保文件被正确创建
        assert writer.full_log_file is not None
        assert writer.warning_log_file is not None

        # 先正常关闭一次以释放文件句柄
        writer.close()

        # 然后模拟关闭失败
        writer.full_log_file = MagicMock()
        writer.warning_log_file = MagicMock()
        writer.full_log_file.close = MagicMock(side_effect=Exception("Close error"))
        writer.warning_log_file.close = MagicMock(side_effect=Exception("Close error"))

        with patch('sys.stderr'):
            writer.close()  # 应该不抛出异常
    pass

@patch('custom_logger.writer.get_config')
def test_tc0004_010_init_writer(mock_get_config):
    """测试初始化异步写入器"""
    mock_config = MagicMock()
    mock_config.current_session_dir = "/tmp/test"
    mock_get_config.return_value = mock_config

    # 清理全局状态
    shutdown_writer()

    with patch('os.makedirs'):
        init_writer()

    # 验证全局变量被设置
    from custom_logger.writer import _log_queue, _writer_thread, _stop_event
    assert _log_queue is not None
    assert _writer_thread is not None
    assert _stop_event is not None

    shutdown_writer()
    pass


def test_tc0004_011_init_writer_already_initialized():
    """测试重复初始化异步写入器"""
    # 清理全局状态
    shutdown_writer()

    with patch('custom_logger.writer.get_config') as mock_get_config:
        mock_config = MagicMock()
        mock_config.current_session_dir = "/tmp/test"
        mock_get_config.return_value = mock_config

        with patch('os.makedirs'):
            init_writer()

            # 获取第一次初始化的队列引用
            from custom_logger.writer import _log_queue
            first_queue = _log_queue

            # 再次初始化
            init_writer()

            # 应该是同一个队列（没有重新初始化）
            from custom_logger.writer import _log_queue as second_queue
            assert first_queue is second_queue

    shutdown_writer()
    pass


@patch('custom_logger.writer.get_config')
def test_tc0004_012_write_log_async(mock_get_config):
    """测试异步写入日志"""
    mock_config = MagicMock()
    mock_config.current_session_dir = "/tmp/test"
    mock_get_config.return_value = mock_config

    # 清理并初始化
    shutdown_writer()

    with patch('os.makedirs'):
        init_writer()

    # 写入日志
    write_log_async("Test log line", INFO, "test_logger")

    # 等待一小段时间让队列处理
    time.sleep(0.1)

    # 验证队列不为空（或已处理）
    from custom_logger.writer import _log_queue
    assert _log_queue is not None

    shutdown_writer()
    pass


def test_tc0004_013_write_log_async_not_initialized():
    """测试未初始化时异步写入"""
    # 清理全局状态
    shutdown_writer()

    # 直接写入（应该不报错）
    write_log_async("Test log line", INFO, "test_logger")
    pass


def test_tc0004_014_write_log_async_queue_full():
    """测试队列满时的处理"""
    # 使用一个很小的队列来测试
    with patch('queue.Queue') as mock_queue_class:
        mock_queue = MagicMock()
        mock_queue.put_nowait.side_effect = Exception("Queue full")
        mock_queue_class.return_value = mock_queue

        with patch('custom_logger.writer._log_queue', mock_queue):
            with patch('sys.stderr'):
                write_log_async("Test log line", INFO, "test_logger")  # 应该不抛出异常
    pass


def test_tc0004_015_shutdown_writer():
    """测试关闭异步写入器"""
    # 先初始化
    with patch('custom_logger.writer.get_config') as mock_get_config:
        mock_config = MagicMock()
        mock_config.current_session_dir = "/tmp/test"
        mock_get_config.return_value = mock_config

        shutdown_writer()  # 清理

        with patch('os.makedirs'):
            init_writer()

        # 验证已初始化
        from custom_logger.writer import _log_queue, _writer_thread
        assert _log_queue is not None
        assert _writer_thread is not None

        # 关闭
        shutdown_writer()

        # 验证已清理
        from custom_logger.writer import _log_queue as final_queue
        from custom_logger.writer import _writer_thread as final_thread
        assert final_queue is None
        assert final_thread is None
    pass


def test_tc0004_016_shutdown_writer_not_initialized():
    """测试未初始化时关闭写入器"""
    # 确保未初始化
    shutdown_writer()

    # 再次关闭应该不报错
    shutdown_writer()
    pass


def test_tc0004_017_queue_sentinel():
    """测试队列结束标记"""
    assert QUEUE_SENTINEL is not None

    # 验证是唯一对象
    assert QUEUE_SENTINEL is not QUEUE_SENTINEL.__class__()
    pass


def test_tc0004_018_log_entry_edge_cases():
    """测试日志条目的边界情况"""
    # 空字符串
    entry1 = LogEntry("", 0, "test_logger")
    assert entry1.log_line == ""
    assert entry1.level_value == 0
    assert entry1.logger_name == "test_logger"

    # 很长的日志行
    long_message = "x" * 10000
    entry2 = LogEntry(long_message, ERROR, "test_logger")
    assert entry2.log_line == long_message
    assert entry2.logger_name == "test_logger"

    # 特殊字符
    special_message = "日志\t消息\n换行"
    entry3 = LogEntry(special_message, WARNING, "test_logger")
    assert entry3.log_line == special_message
    assert entry3.logger_name == "test_logger"
    pass


def test_tc0004_019_writer_thread_timeout():
    """测试写入线程超时处理"""
    with patch('custom_logger.writer.get_config') as mock_get_config:
        mock_config = MagicMock()
        mock_config.current_session_dir = "/tmp/test"
        mock_get_config.return_value = mock_config

        shutdown_writer()

        with patch('os.makedirs'):
            init_writer()

        # 让线程运行一小段时间
        time.sleep(0.1)

        # 正常关闭
        shutdown_writer()
    pass


def test_tc0004_020_concurrent_write():
    """测试并发写入"""
    with patch('custom_logger.writer.get_config') as mock_get_config:
        mock_config = MagicMock()
        mock_config.current_session_dir = "/tmp/test"
        mock_get_config.return_value = mock_config

        shutdown_writer()

        with patch('os.makedirs'):
            init_writer()

        # 并发写入多条日志
        threads = []
        for i in range(10):
            thread = threading.Thread(
                target=write_log_async,
                args=(f"Message {i}", INFO, "test_logger")
            )
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        time.sleep(0.2)  # 等待处理

        shutdown_writer()
    pass