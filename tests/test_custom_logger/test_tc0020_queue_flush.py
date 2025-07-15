# tests/test_custom_logger/test_tc0020_queue_flush.py
"""
测试队列刷新功能，确保所有日志都能实时写入文件
"""
from __future__ import annotations

import os
import tempfile
import time
import pytest
from datetime import datetime

from custom_logger import (
    init_custom_logger_system,
    get_logger,
    tear_down_custom_logger_system
)


class ConfigObject:
    """测试用配置对象"""
    
    def __init__(self, log_dir: str, first_start_time: datetime):
        self.first_start_time = first_start_time
        self.project_name = "queue_flush_test"
        self.experiment_name = "tc0020"
        
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


def test_tc0020_queue_flush_basic(config_object, temp_log_dir):
    """测试基本队列刷新功能"""
    try:
        # 初始化日志系统
        init_custom_logger_system(config_object)
        
        # 获取logger
        logger = get_logger("test_flush")
        
        # 输出多条日志
        logger.info("测试消息1")
        logger.warning("测试消息2")
        logger.error("测试消息3")
        
        # 调用flush确保所有数据写入
        from custom_logger.writer import flush_writer
        flush_writer()
        
        # 检查文件内容
        full_log_path = os.path.join(temp_log_dir, "full.log")
        warning_log_path = os.path.join(temp_log_dir, "warning.log")
        
        # 验证文件存在且有内容
        assert os.path.exists(full_log_path), "full.log文件不存在"
        assert os.path.exists(warning_log_path), "warning.log文件不存在"
        
        # 验证文件大小
        full_size = os.path.getsize(full_log_path)
        warning_size = os.path.getsize(warning_log_path)
        
        assert full_size > 0, "full.log文件为空"
        assert warning_size > 0, "warning.log文件为空"
        
        # 验证文件内容
        with open(full_log_path, 'r', encoding='utf-8') as f:
            full_content = f.read()
            
        with open(warning_log_path, 'r', encoding='utf-8') as f:
            warning_content = f.read()
        
        assert "测试消息1" in full_content, "full.log中缺少测试消息1"
        assert "测试消息2" in full_content, "full.log中缺少测试消息2"
        assert "测试消息3" in full_content, "full.log中缺少测试消息3"
        
        assert "测试消息2" in warning_content, "warning.log中缺少测试消息2"
        assert "测试消息3" in warning_content, "warning.log中缺少测试消息3"
        
    finally:
        tear_down_custom_logger_system()


def test_tc0020_queue_flush_module_files(config_object, temp_log_dir):
    """测试模块文件的队列刷新"""
    try:
        # 初始化日志系统
        init_custom_logger_system(config_object)
        
        # 获取多个模块的logger
        logger_main = get_logger("main")
        logger_module1 = get_logger("module1")
        logger_module2 = get_logger("module2")
        
        # 输出不同模块的日志
        logger_main.info("主模块消息")
        logger_main.warning("主模块警告")
        
        logger_module1.info("模块1消息")
        logger_module1.error("模块1错误")
        
        logger_module2.info("模块2消息")
        logger_module2.critical("模块2严重错误")
        
        # 调用flush确保所有数据写入
        from custom_logger.writer import flush_writer
        flush_writer()
        
        # 检查模块文件
        expected_files = [
            ("main_full.log", "主模块消息"),
            ("main_warning.log", "主模块警告"),
            ("module1_full.log", "模块1消息"),
            ("module1_warning.log", "模块1错误"),
            ("module2_full.log", "模块2消息"),
            ("module2_warning.log", "模块2严重错误")
        ]
        
        for filename, expected_content in expected_files:
            filepath = os.path.join(temp_log_dir, filename)
            assert os.path.exists(filepath), f"{filename}文件不存在"
            assert os.path.getsize(filepath) > 0, f"{filename}文件为空"
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                assert expected_content in content, f"{filename}中缺少期望内容: {expected_content}"
        
    finally:
        tear_down_custom_logger_system()


def test_tc0020_auto_flush_on_shutdown(config_object, temp_log_dir):
    """测试系统关闭时自动刷新"""
    try:
        # 初始化日志系统
        init_custom_logger_system(config_object)
        
        # 获取logger
        logger = get_logger("auto_flush")
        
        # 输出日志
        logger.info("关闭前的消息")
        logger.warning("关闭前的警告")
        
        # 系统关闭时应自动刷新
        tear_down_custom_logger_system()
        
        # 检查文件内容
        full_log_path = os.path.join(temp_log_dir, "full.log")
        warning_log_path = os.path.join(temp_log_dir, "warning.log")
        
        assert os.path.exists(full_log_path), "关闭后full.log文件不存在"
        assert os.path.exists(warning_log_path), "关闭后warning.log文件不存在"
        
        full_size = os.path.getsize(full_log_path)
        warning_size = os.path.getsize(warning_log_path)
        
        assert full_size > 0, "关闭后full.log文件为空"
        assert warning_size > 0, "关闭后warning.log文件为空"
        
        # 验证内容
        with open(full_log_path, 'r', encoding='utf-8') as f:
            full_content = f.read()
            
        with open(warning_log_path, 'r', encoding='utf-8') as f:
            warning_content = f.read()
        
        assert "关闭前的消息" in full_content, "关闭后full.log中缺少消息"
        assert "关闭前的警告" in warning_content, "关闭后warning.log中缺少警告"
        
    except Exception:
        # 确保资源清理
        try:
            tear_down_custom_logger_system()
        except:
            pass
        raise


def test_tc0020_flush_with_large_queue(config_object, temp_log_dir):
    """测试大量日志时的刷新功能"""
    try:
        # 初始化日志系统
        init_custom_logger_system(config_object)
        
        # 获取logger
        logger = get_logger("large_queue")
        
        # 快速输出大量日志
        for i in range(100):
            logger.info(f"大量日志消息 {i}")
            if i % 10 == 0:
                logger.warning(f"警告消息 {i}")
        
        # 调用flush确保所有数据写入
        from custom_logger.writer import flush_writer
        flush_writer()
        
        # 检查文件内容
        full_log_path = os.path.join(temp_log_dir, "full.log")
        warning_log_path = os.path.join(temp_log_dir, "warning.log")
        
        assert os.path.exists(full_log_path), "大量日志后full.log文件不存在"
        assert os.path.exists(warning_log_path), "大量日志后warning.log文件不存在"
        
        # 验证文件大小合理
        full_size = os.path.getsize(full_log_path)
        warning_size = os.path.getsize(warning_log_path)
        
        assert full_size > 5000, f"大量日志后full.log文件太小: {full_size} bytes"
        assert warning_size > 500, f"大量日志后warning.log文件太小: {warning_size} bytes"
        
        # 验证内容完整性
        with open(full_log_path, 'r', encoding='utf-8') as f:
            full_content = f.read()
            
        with open(warning_log_path, 'r', encoding='utf-8') as f:
            warning_content = f.read()
        
        # 检查第一条和最后一条消息
        assert "大量日志消息 0" in full_content, "缺少第一条消息"
        assert "大量日志消息 99" in full_content, "缺少最后一条消息"
        
        # 检查警告消息
        assert "警告消息 0" in warning_content, "缺少第一条警告"
        assert "警告消息 90" in warning_content, "缺少最后一条警告"
        
    finally:
        tear_down_custom_logger_system()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])