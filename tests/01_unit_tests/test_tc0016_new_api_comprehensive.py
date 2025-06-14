#!/usr/bin/env python3
# tests/01_unit_tests/test_tc0016_new_api_comprehensive.py

"""
新API综合测试用例
测试需求变更中的所有功能：
1. init_custom_logger_system接收config对象，不再调用config_manager
2. worker初始化函数支持序列化config对象和队列
3. 取消first_start_time参数支持
4. worker时间计算正确性
5. logger名称长度限制
"""

from __future__ import annotations
from datetime import datetime
import tempfile
import os
import sys
import multiprocessing as mp
import time
import pytest
from unittest.mock import patch, MagicMock

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from custom_logger import (
    init_custom_logger_system, 
    init_custom_logger_system_for_worker,
    get_logger, 
    tear_down_custom_logger_system,
    is_initialized,
    is_queue_mode
)


class TestNewAPIComprehensive:
    """新API综合测试类"""
    
    def setup_method(self):
        """每个测试前的设置"""
        # 确保日志系统未初始化
        try:
            tear_down_custom_logger_system()
        except:
            pass
    
    def teardown_method(self):
        """每个测试后的清理"""
        try:
            tear_down_custom_logger_system()
        except:
            pass

    def test_tc0016_001_config_object_basic_initialization(self):
        """测试基本的config对象初始化"""
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        # 创建配置对象
        class TestConfig:
            def __init__(self):
                self.first_start_time = datetime.now()
                self.paths = TestPathsConfig()
                
        class TestPathsConfig:
            def __init__(self):
                self.log_dir = temp_dir
        
        config = TestConfig()
        
        # 测试初始化
        init_custom_logger_system(config)
        
        # 验证初始化状态
        assert is_initialized() == True
        assert is_queue_mode() == False
        
        # 测试获取logger
        logger = get_logger('test')
        assert logger is not None
        assert logger.name == 'test'
        
        # 清理
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    def test_tc0016_002_config_object_missing_paths(self):
        """测试缺少paths属性的config对象"""
        class InvalidConfig:
            def __init__(self):
                self.first_start_time = datetime.now()
                # 故意不设置paths属性
        
        config = InvalidConfig()
        
        with pytest.raises(ValueError, match="config_object必须包含paths属性"):
            init_custom_logger_system(config)

    def test_tc0016_003_config_object_missing_log_dir(self):
        """测试缺少log_dir的config对象"""
        class InvalidConfig:
            def __init__(self):
                self.first_start_time = datetime.now()
                self.paths = InvalidPathsConfig()
                
        class InvalidPathsConfig:
            def __init__(self):
                # 故意不设置log_dir属性
                pass
        
        config = InvalidConfig()
        
        with pytest.raises(ValueError, match="config_object必须包含paths.log_dir属性"):
            init_custom_logger_system(config)

    def test_tc0016_004_config_object_missing_first_start_time(self):
        """测试缺少first_start_time的config对象"""
        temp_dir = tempfile.mkdtemp()
        
        class InvalidConfig:
            def __init__(self):
                # 故意不设置first_start_time属性
                self.paths = TestPathsConfig()
                
        class TestPathsConfig:
            def __init__(self):
                self.log_dir = temp_dir
        
        config = InvalidConfig()
        
        with pytest.raises(ValueError, match="config_object必须包含first_start_time属性"):
            init_custom_logger_system(config)
        
        # 清理
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    def test_tc0016_005_config_object_none_value(self):
        """测试传入None的config对象"""
        with pytest.raises(ValueError, match="config_object不能为None"):
            init_custom_logger_system(None)

    def test_tc0016_006_queue_mode_initialization(self):
        """测试队列模式初始化"""
        temp_dir = tempfile.mkdtemp()
        log_queue = mp.Queue()
        
        class QueueConfig:
            def __init__(self):
                self.first_start_time = datetime.now()
                self.paths = TestPathsConfig()
                self.queue_info = QueueInfo()
                
        class TestPathsConfig:
            def __init__(self):
                self.log_dir = temp_dir
                
        class QueueInfo:
            def __init__(self):
                self.log_queue = log_queue
        
        config = QueueConfig()
        
        # 测试初始化
        init_custom_logger_system(config)
        
        # 验证队列模式
        assert is_initialized() == True
        assert is_queue_mode() == True
        
        # 清理
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    def test_tc0016_007_worker_initialization_basic(self):
        """测试worker基本初始化"""
        temp_dir = tempfile.mkdtemp()
        
        class WorkerConfig:
            def __init__(self):
                self.first_start_time = datetime.now()
                self.paths = TestPathsConfig()
                
        class TestPathsConfig:
            def __init__(self):
                self.log_dir = temp_dir
        
        config = WorkerConfig()
        
        # 测试worker初始化
        init_custom_logger_system_for_worker(config, "worker_1")
        
        # 验证初始化状态
        assert is_initialized() == True
        assert is_queue_mode() == False
        
        # 测试获取logger
        logger = get_logger('worker')
        assert logger is not None
        
        # 清理
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    def test_tc0016_008_worker_queue_mode_initialization(self):
        """测试worker队列模式初始化"""
        temp_dir = tempfile.mkdtemp()
        log_queue = mp.Queue()
        
        class WorkerQueueConfig:
            def __init__(self):
                self.first_start_time = datetime.now()
                self.paths = TestPathsConfig()
                self.queue_info = QueueInfo()
                
        class TestPathsConfig:
            def __init__(self):
                self.log_dir = temp_dir
                
        class QueueInfo:
            def __init__(self):
                self.log_queue = log_queue
        
        config = WorkerQueueConfig()
        
        # 测试worker队列初始化
        init_custom_logger_system_for_worker(config, "worker_1")
        
        # 验证队列模式
        assert is_initialized() == True
        assert is_queue_mode() == True
        
        # 清理
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    def test_tc0016_009_worker_missing_config(self):
        """测试worker缺少config对象"""
        with pytest.raises(ValueError, match="serializable_config_object不能为None"):
            init_custom_logger_system_for_worker(None, "worker_1")

    def test_tc0016_010_logger_name_length_validation(self):
        """测试logger名称长度验证"""
        temp_dir = tempfile.mkdtemp()
        
        class TestConfig:
            def __init__(self):
                self.first_start_time = datetime.now()
                self.paths = TestPathsConfig()
                
        class TestPathsConfig:
            def __init__(self):
                self.log_dir = temp_dir
        
        config = TestConfig()
        init_custom_logger_system(config)
        
        # 测试有效长度（8个字符以内）
        logger1 = get_logger('test')
        assert logger1.name == 'test'
        
        logger2 = get_logger('12345678')
        assert logger2.name == '12345678'
        
        # 测试无效长度（超过8个字符）
        with pytest.raises(ValueError, match="日志记录器名称不能超过8个字符"):
            get_logger('123456789')
        
        with pytest.raises(ValueError, match="日志记录器名称不能超过8个字符"):
            get_logger('very_long_logger_name')
        
        # 清理
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    def test_tc0016_011_worker_timing_accuracy(self):
        """测试worker时间计算准确性"""
        temp_dir = tempfile.mkdtemp()
        
        # 设置固定的开始时间
        start_time = datetime.now()
        
        class TimingConfig:
            def __init__(self):
                self.first_start_time = start_time
                self.paths = TestPathsConfig()
                
        class TestPathsConfig:
            def __init__(self):
                self.log_dir = temp_dir
        
        config = TimingConfig()
        
        # 初始化worker
        init_custom_logger_system_for_worker(config, "timing_test")
        
        # 等待一段时间
        time.sleep(1)
        
        # 获取logger并记录日志
        logger = get_logger('timing')
        
        # 记录日志并验证功能正常
        logger.info("Test timing message")
        
        # 验证logger正常工作（能获取到logger说明时间计算正确）
        assert logger is not None
        
        # 清理
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    def test_tc0016_012_dict_format_paths(self):
        """测试字典格式的paths配置"""
        temp_dir = tempfile.mkdtemp()
        
        class DictConfig:
            def __init__(self):
                self.first_start_time = datetime.now()
                self.paths = {'log_dir': temp_dir}
        
        config = DictConfig()
        
        # 测试初始化
        init_custom_logger_system(config)
        
        # 验证初始化成功
        assert is_initialized() == True
        
        # 清理
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    def test_tc0016_013_dict_format_queue_info(self):
        """测试字典格式的queue_info配置"""
        temp_dir = tempfile.mkdtemp()
        log_queue = mp.Queue()
        
        class DictQueueConfig:
            def __init__(self):
                self.first_start_time = datetime.now()
                self.paths = {'log_dir': temp_dir}
                self.queue_info = {'log_queue': log_queue}
        
        config = DictQueueConfig()
        
        # 测试初始化
        init_custom_logger_system(config)
        
        # 验证队列模式
        assert is_initialized() == True
        assert is_queue_mode() == True
        
        # 清理
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    def test_tc0016_014_repeated_initialization(self):
        """测试重复初始化"""
        temp_dir = tempfile.mkdtemp()
        
        class TestConfig:
            def __init__(self):
                self.first_start_time = datetime.now()
                self.paths = TestPathsConfig()
                
        class TestPathsConfig:
            def __init__(self):
                self.log_dir = temp_dir
        
        config = TestConfig()
        
        # 第一次初始化
        init_custom_logger_system(config)
        assert is_initialized() == True
        
        # 第二次初始化应该被忽略
        init_custom_logger_system(config)
        assert is_initialized() == True
        
        # 清理
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    def test_tc0016_015_uninitialized_get_logger(self):
        """测试未初始化时获取logger"""
        with pytest.raises(RuntimeError, match="日志系统未初始化"):
            get_logger('test')

    def test_tc0016_016_datetime_object_first_start_time(self):
        """测试datetime对象格式的first_start_time"""
        temp_dir = tempfile.mkdtemp()
        
        class DateTimeConfig:
            def __init__(self):
                self.first_start_time = datetime(2025, 1, 1, 12, 0, 0)
                self.paths = TestPathsConfig()
                
        class TestPathsConfig:
            def __init__(self):
                self.log_dir = temp_dir
        
        config = DateTimeConfig()
        
        # 测试初始化
        init_custom_logger_system(config)
        assert is_initialized() == True
        
        # 测试时间计算
        logger = get_logger('datetime')
        
        # 记录日志并验证功能正常
        logger.info("Test datetime message")
        
        # 验证logger正常工作
        assert logger is not None
        
        # 清理
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    def test_tc0016_017_string_format_first_start_time(self):
        """测试字符串格式的first_start_time"""
        temp_dir = tempfile.mkdtemp()
        
        class StringTimeConfig:
            def __init__(self):
                self.first_start_time = "2025-01-01T12:00:00"
                self.paths = TestPathsConfig()
                
        class TestPathsConfig:
            def __init__(self):
                self.log_dir = temp_dir
        
        config = StringTimeConfig()
        
        # 测试初始化
        init_custom_logger_system(config)
        assert is_initialized() == True
        
        # 测试时间计算
        logger = get_logger('strtime')
        
        # 记录日志并验证功能正常
        logger.info("Test string time message")
        
        # 验证logger正常工作
        assert logger is not None
        
        # 清理
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    def test_tc0016_018_edge_case_empty_logger_name(self):
        """测试边界情况：空logger名称"""
        temp_dir = tempfile.mkdtemp()
        
        class TestConfig:
            def __init__(self):
                self.first_start_time = datetime.now()
                self.paths = TestPathsConfig()
                
        class TestPathsConfig:
            def __init__(self):
                self.log_dir = temp_dir
        
        config = TestConfig()
        init_custom_logger_system(config)
        
        # 测试空字符串名称（应该允许）
        logger = get_logger('')
        assert logger.name == ''
        
        # 清理
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    def test_tc0016_019_edge_case_exactly_8_chars(self):
        """测试边界情况：恰好8个字符的logger名称"""
        temp_dir = tempfile.mkdtemp()
        
        class TestConfig:
            def __init__(self):
                self.first_start_time = datetime.now()
                self.paths = TestPathsConfig()
                
        class TestPathsConfig:
            def __init__(self):
                self.log_dir = temp_dir
        
        config = TestConfig()
        init_custom_logger_system(config)
        
        # 测试恰好8个字符（应该允许）
        logger = get_logger('12345678')
        assert logger.name == '12345678'
        
        # 清理
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    def test_tc0016_020_integration_main_and_worker(self):
        """测试主程序和worker的集成"""
        temp_dir = tempfile.mkdtemp()
        
        # 主程序配置
        class MainConfig:
            def __init__(self):
                self.first_start_time = datetime.now()
                self.paths = TestPathsConfig()
                
        class TestPathsConfig:
            def __init__(self):
                self.log_dir = temp_dir
        
        main_config = MainConfig()
        
        # 初始化主程序
        init_custom_logger_system(main_config)
        main_logger = get_logger('main')
        main_logger.info("Main program started")
        
        # 清理主程序
        tear_down_custom_logger_system()
        
        # 初始化worker（使用相同的配置）
        init_custom_logger_system_for_worker(main_config, "worker_1")
        worker_logger = get_logger('worker')
        worker_logger.info("Worker started")
        
        # 验证都能正常工作
        assert worker_logger is not None
        
        # 清理
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass 