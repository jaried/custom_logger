# tests/test_custom_logger/test_tc0021_error_stack_trace.py
"""
测试ERROR级别及以上自动打印错误栈功能
"""
from __future__ import annotations

import os
import tempfile
import pytest
from datetime import datetime
from unittest.mock import patch

from custom_logger import (
    init_custom_logger_system,
    get_logger,
    tear_down_custom_logger_system,
    ERROR, CRITICAL, EXCEPTION
)


class ConfigObject:
    """测试用配置对象"""
    
    def __init__(self, log_dir: str, first_start_time: datetime):
        self.first_start_time = first_start_time
        self.project_name = "error_stack_test"
        self.experiment_name = "tc0021"
        
        self.paths = {
            'log_dir': log_dir
        }
        
        self.logger = {
            'global_console_level': 'debug',
            'global_file_level': 'debug',
            'show_debug_call_stack': False,
            'module_levels': {}
        }


@pytest.fixture
def temp_log_dir():
    """创建临时日志目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def config_object(temp_log_dir):
    """创建测试配置对象"""
    return ConfigObject(temp_log_dir, datetime.now())


def test_tc0021_exception_method_captures_stack(config_object, temp_log_dir):
    """测试exception()方法自动捕获异常栈"""
    try:
        init_custom_logger_system(config_object)
        logger = get_logger("exception_test")
        
        # 创建一个异常情况
        try:
            result = 1 / 0
        except ZeroDivisionError:
            logger.exception("除零错误发生")
        
        # 刷新确保写入
        from custom_logger.writer import flush_writer
        flush_writer()
        
        # 检查日志文件中是否包含异常栈
        full_log_path = os.path.join(temp_log_dir, "full.log")
        assert os.path.exists(full_log_path), "full.log文件不存在"
        
        with open(full_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        assert "除零错误发生" in log_content, "异常日志消息不存在"
        assert "ZeroDivisionError" in log_content, "异常类型不存在"
        assert "Traceback" in log_content, "异常栈信息不存在"
        assert "division by zero" in log_content, "异常详细信息不存在"
        
    finally:
        tear_down_custom_logger_system()


def test_tc0021_error_method_captures_stack_when_exception_active(config_object, temp_log_dir):
    """测试error()方法在有活动异常时自动捕获异常栈"""
    try:
        init_custom_logger_system(config_object)
        logger = get_logger("error_test")
        
        # 创建一个异常情况，然后在except块中使用error()
        try:
            result = 1 / 0
        except ZeroDivisionError:
            logger.error("处理除零错误")
        
        # 刷新确保写入
        from custom_logger.writer import flush_writer
        flush_writer()
        
        # 检查日志文件
        full_log_path = os.path.join(temp_log_dir, "full.log")
        assert os.path.exists(full_log_path), "full.log文件不存在"
        
        with open(full_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        assert "处理除零错误" in log_content, "错误日志消息不存在"
        assert "ZeroDivisionError" in log_content, "异常类型不存在"
        assert "Traceback" in log_content, "异常栈信息不存在"
        
    finally:
        tear_down_custom_logger_system()


def test_tc0021_critical_method_captures_stack_when_exception_active(config_object, temp_log_dir):
    """测试critical()方法在有活动异常时自动捕获异常栈"""
    try:
        init_custom_logger_system(config_object)
        logger = get_logger("critical_test")
        
        # 创建一个异常情况，然后在except块中使用critical()
        try:
            invalid_list = [1, 2, 3]
            result = invalid_list[10]
        except IndexError:
            logger.critical("严重的索引错误")
        
        # 刷新确保写入
        from custom_logger.writer import flush_writer
        flush_writer()
        
        # 检查日志文件
        full_log_path = os.path.join(temp_log_dir, "full.log")
        assert os.path.exists(full_log_path), "full.log文件不存在"
        
        with open(full_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        assert "严重的索引错误" in log_content, "严重错误日志消息不存在"
        assert "IndexError" in log_content, "异常类型不存在"
        assert "Traceback" in log_content, "异常栈信息不存在"
        
    finally:
        tear_down_custom_logger_system()


def test_tc0021_error_method_no_stack_when_no_exception(config_object, temp_log_dir):
    """测试error()方法在没有活动异常时不打印异常栈"""
    try:
        init_custom_logger_system(config_object)
        logger = get_logger("error_no_stack")
        
        # 在没有异常的情况下使用error()
        logger.error("普通错误消息")
        
        # 刷新确保写入
        from custom_logger.writer import flush_writer
        flush_writer()
        
        # 检查日志文件
        full_log_path = os.path.join(temp_log_dir, "full.log")
        assert os.path.exists(full_log_path), "full.log文件不存在"
        
        with open(full_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        assert "普通错误消息" in log_content, "错误日志消息不存在"
        assert "Traceback" not in log_content, "不应该有异常栈信息"
        
    finally:
        tear_down_custom_logger_system()


def test_tc0021_warning_method_no_stack_even_with_exception(config_object, temp_log_dir):
    """测试warning()方法即使有活动异常也不打印异常栈"""
    try:
        init_custom_logger_system(config_object)
        logger = get_logger("warning_test")
        
        # 创建一个异常情况，然后在except块中使用warning()
        try:
            result = 1 / 0
        except ZeroDivisionError:
            logger.warning("警告消息")
        
        # 刷新确保写入
        from custom_logger.writer import flush_writer
        flush_writer()
        
        # 检查日志文件
        full_log_path = os.path.join(temp_log_dir, "full.log")
        assert os.path.exists(full_log_path), "full.log文件不存在"
        
        with open(full_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        assert "警告消息" in log_content, "警告日志消息不存在"
        assert "Traceback" not in log_content, "WARNING级别不应该有异常栈信息"
        
    finally:
        tear_down_custom_logger_system()


def test_tc0021_console_output_includes_stack_trace(config_object, temp_log_dir):
    """测试控制台输出也包含异常栈信息"""
    try:
        init_custom_logger_system(config_object)
        logger = get_logger("console_test")
        
        # 使用patch来捕获stderr输出
        with patch('sys.stderr.write') as mock_stderr:
            try:
                result = 1 / 0
            except ZeroDivisionError:
                logger.error("控制台错误测试")
        
        # 检查是否有stderr输出调用
        stderr_calls = mock_stderr.call_args_list
        stderr_output = ''.join(call[0][0] for call in stderr_calls if call[0])
        
        assert "控制台错误测试" in stderr_output, "控制台错误消息不存在"
        assert "ZeroDivisionError" in stderr_output, "控制台异常类型不存在"
        
    finally:
        tear_down_custom_logger_system()


def test_tc0021_mixed_levels_stack_behavior(config_object, temp_log_dir):
    """测试混合级别的异常栈行为"""
    try:
        init_custom_logger_system(config_object)
        logger = get_logger("mixed_test")
        
        # 在异常上下文中测试所有级别
        try:
            result = 1 / 0
        except ZeroDivisionError:
            logger.info("信息级别")          # 不应该有栈
            logger.warning("警告级别")       # 不应该有栈  
            logger.error("错误级别")         # 应该有栈
            logger.critical("严重级别")      # 应该有栈
            logger.exception("异常级别")     # 应该有栈
        
        # 刷新确保写入
        from custom_logger.writer import flush_writer
        flush_writer()
        
        # 检查日志文件
        full_log_path = os.path.join(temp_log_dir, "full.log")
        assert os.path.exists(full_log_path), "full.log文件不存在"
        
        with open(full_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # 检查所有消息都存在
        assert "信息级别" in log_content
        assert "警告级别" in log_content
        assert "错误级别" in log_content
        assert "严重级别" in log_content
        assert "异常级别" in log_content
        
        # 检查异常栈出现的次数（应该是3次：error, critical, exception）
        traceback_count = log_content.count("Traceback")
        assert traceback_count == 3, f"异常栈出现次数应该是3，实际是{traceback_count}"
        
    finally:
        tear_down_custom_logger_system()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])