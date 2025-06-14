# tests/test_custom_logger/test_new_api_requirements.py
from __future__ import annotations

import os
import tempfile
import shutil
import multiprocessing as mp
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import pytest

from custom_logger import (
    init_custom_logger_system,
    init_custom_logger_system_for_worker,
    get_logger,
    tear_down_custom_logger_system,
    is_initialized
)


class TestNewAPIRequirements:
    """测试新API需求的所有情况"""

    def setup_method(self):
        """每个测试前的设置"""
        # 清理系统状态
        tear_down_custom_logger_system()
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = os.path.join(self.temp_dir, "logs")
        
        # 创建基础配置对象
        self.base_config = Mock()
        self.base_config.first_start_time = datetime.now()
        self.base_config.paths = Mock()
        self.base_config.paths.log_dir = self.log_dir
        self.base_config.logger = Mock()
        self.base_config.logger.global_console_level = "info"
        self.base_config.logger.global_file_level = "debug"
        self.base_config.logger.module_levels = {}

    def teardown_method(self):
        """每个测试后的清理"""
        tear_down_custom_logger_system()
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_custom_logger_system_requires_config_object(self):
        """测试init_custom_logger_system必须传入config_object"""
        # 测试传入None会抛出异常
        with pytest.raises(ValueError, match="config_object不能为None"):
            init_custom_logger_system(None)

    def test_init_custom_logger_system_requires_paths_log_dir(self):
        """测试init_custom_logger_system必须包含paths.log_dir"""
        # 测试缺少paths属性
        config = Mock()
        config.first_start_time = datetime.now()
        # 删除paths属性，确保getattr返回None
        del config.paths
        
        with pytest.raises(ValueError, match="config_object必须包含paths属性"):
            init_custom_logger_system(config)

        # 测试paths为None
        config = Mock()
        config.first_start_time = datetime.now()
        config.paths = None
        with pytest.raises(ValueError, match="config_object必须包含paths属性"):
            init_custom_logger_system(config)

        # 测试paths.log_dir为None（字典格式）
        config = Mock()
        config.first_start_time = datetime.now()
        config.paths = {"other_key": "value"}
        with pytest.raises(ValueError, match="config_object必须包含paths.log_dir属性"):
            init_custom_logger_system(config)

        # 测试paths.log_dir为None（对象格式）
        config = Mock()
        config.first_start_time = datetime.now()
        config.paths = Mock()
        config.paths.log_dir = None
        with pytest.raises(ValueError, match="config_object必须包含paths.log_dir属性"):
            init_custom_logger_system(config)

    def test_init_custom_logger_system_requires_first_start_time(self):
        """测试init_custom_logger_system必须包含first_start_time"""
        config = Mock()
        config.paths = Mock()
        config.paths.log_dir = self.log_dir
        # 删除first_start_time属性，确保hasattr返回False
        del config.first_start_time
        
        with pytest.raises(ValueError, match="config_object必须包含first_start_time属性"):
            init_custom_logger_system(config)

    def test_init_custom_logger_system_success_with_valid_config(self):
        """测试使用有效配置成功初始化"""
        # 测试成功初始化
        init_custom_logger_system(self.base_config)
        
        assert is_initialized() == True
        
        # 测试重复初始化不会出错
        init_custom_logger_system(self.base_config)
        assert is_initialized() == True

    def test_init_custom_logger_system_creates_log_directory(self):
        """测试初始化时会创建日志目录"""
        # 确保目录不存在
        if os.path.exists(self.log_dir):
            shutil.rmtree(self.log_dir)
        
        assert not os.path.exists(self.log_dir)
        
        # 初始化系统
        init_custom_logger_system(self.base_config)
        
        # 验证目录被创建
        assert os.path.exists(self.log_dir)

    def test_init_custom_logger_system_with_queue_mode(self):
        """测试队列模式初始化"""
        # 创建带队列信息的配置
        config = Mock()
        config.first_start_time = datetime.now()
        config.paths = Mock()
        config.paths.log_dir = self.log_dir
        config.logger = Mock()
        config.logger.global_console_level = "info"
        config.logger.global_file_level = "debug"
        config.logger.module_levels = {}
        
        # 添加队列信息
        config.queue_info = Mock()
        config.queue_info.log_queue = mp.Queue()
        
        # 模拟队列接收器初始化
        with patch('custom_logger.manager.init_queue_receiver') as mock_init_receiver:
            init_custom_logger_system(config)
            mock_init_receiver.assert_called_once_with(config.queue_info.log_queue, self.log_dir)

    def test_get_logger_name_length_validation(self):
        """测试get_logger名字长度验证"""
        # 先初始化系统
        init_custom_logger_system(self.base_config)
        
        # 测试有效长度的名字
        valid_names = ["a", "ab", "abc", "abcd", "abcde", "abcdef", "abcdefg", "abcdefgh"]
        for name in valid_names:
            logger = get_logger(name)
            assert logger is not None
            assert logger.name == name
        
        # 测试超过8个字符的名字
        invalid_names = ["abcdefghi", "very_long_name", "超过八个字符的名字"]
        for name in invalid_names:
            with pytest.raises(ValueError, match=f"日志记录器名称不能超过8个字符，当前长度: {len(name)}"):
                get_logger(name)

    def test_get_logger_requires_initialization(self):
        """测试get_logger需要先初始化系统"""
        # 确保系统未初始化
        tear_down_custom_logger_system()
        
        with pytest.raises(RuntimeError, match="日志系统未初始化"):
            get_logger("test")

    def test_worker_initialization_function(self):
        """测试worker初始化函数"""
        # 测试传入None会抛出异常
        with pytest.raises(ValueError, match="serializable_config_object不能为None"):
            init_custom_logger_system_for_worker(None)

        # 测试缺少必要属性
        config = Mock()
        config.first_start_time = datetime.now()
        # 删除paths属性，确保getattr返回None
        del config.paths
        
        with pytest.raises(ValueError, match="serializable_config_object必须包含paths属性"):
            init_custom_logger_system_for_worker(config)

        # 测试成功初始化
        config = Mock()
        config.first_start_time = datetime.now()
        config.paths = Mock()
        config.paths.log_dir = self.log_dir
        config.logger = Mock()
        config.logger.global_console_level = "info"
        config.logger.global_file_level = "debug"
        config.logger.module_levels = {}
        
        init_custom_logger_system_for_worker(config, "worker_001")
        assert is_initialized() == True

    def test_worker_initialization_with_queue_mode(self):
        """测试worker队列模式初始化"""
        config = Mock()
        config.first_start_time = datetime.now()
        config.paths = Mock()
        config.paths.log_dir = self.log_dir
        config.logger = Mock()
        config.logger.global_console_level = "info"
        config.logger.global_file_level = "debug"
        config.logger.module_levels = {}
        
        # 添加队列信息
        config.queue_info = Mock()
        config.queue_info.log_queue = mp.Queue()
        
        # 模拟队列发送器初始化
        with patch('custom_logger.manager.init_queue_sender') as mock_init_sender:
            init_custom_logger_system_for_worker(config, "worker_001")
            mock_init_sender.assert_called_once_with(config.queue_info.log_queue, "worker_001")

    def test_worker_timing_calculation(self):
        """测试worker的用时计算正确"""
        # 设置一个固定的开始时间
        start_time = datetime(2025, 1, 1, 10, 0, 0)
        
        config = Mock()
        config.first_start_time = start_time
        config.paths = Mock()
        config.paths.log_dir = self.log_dir
        config.logger = Mock()
        config.logger.global_console_level = "info"
        config.logger.global_file_level = "debug"
        config.logger.module_levels = {}
        
        # 初始化worker
        init_custom_logger_system_for_worker(config, "worker_001")
        
        # 获取logger并测试时间计算
        logger = get_logger("test")
        
        # 模拟当前时间为开始时间后1小时2分钟3.45秒
        current_time = start_time + timedelta(hours=1, minutes=2, seconds=3, microseconds=450000)
        
        # 捕获输出来验证时间计算
        import io
        import sys
        from unittest.mock import patch
        
        captured_output = io.StringIO()
        
        with patch('custom_logger.formatter.datetime') as mock_datetime:
            mock_datetime.now.return_value = current_time
            mock_datetime.fromisoformat = datetime.fromisoformat
            
            # 捕获print输出
            with patch('sys.stdout', captured_output):
                logger.info("test message")
        
        # 验证输出包含正确的时间计算
        output = captured_output.getvalue()
        # 应该包含 "1:02:03.45" 这样的时间格式
        assert "1:02:03.45" in output or "1:02:03" in output, f"时间计算不正确，输出: {output}"

    def test_config_object_with_dict_paths(self):
        """测试配置对象的paths为字典格式"""
        config = Mock()
        config.first_start_time = datetime.now()
        config.paths = {"log_dir": self.log_dir}  # 字典格式
        config.logger = Mock()
        config.logger.global_console_level = "info"
        config.logger.global_file_level = "debug"
        config.logger.module_levels = {}
        
        # 应该成功初始化
        init_custom_logger_system(config)
        assert is_initialized() == True

    def test_config_object_with_object_paths(self):
        """测试配置对象的paths为对象格式"""
        config = Mock()
        config.first_start_time = datetime.now()
        config.paths = Mock()
        config.paths.log_dir = self.log_dir  # 对象格式
        config.logger = Mock()
        config.logger.global_console_level = "info"
        config.logger.global_file_level = "debug"
        config.logger.module_levels = {}
        
        # 应该成功初始化
        init_custom_logger_system(config)
        assert is_initialized() == True

    def test_logger_uses_config_first_start_time(self):
        """测试logger使用config.first_start_time进行计时"""
        # 设置一个特定的开始时间
        specific_start_time = datetime(2025, 1, 1, 12, 0, 0)
        
        config = Mock()
        config.first_start_time = specific_start_time
        config.paths = Mock()
        config.paths.log_dir = self.log_dir
        config.logger = Mock()
        config.logger.global_console_level = "info"
        config.logger.global_file_level = "debug"
        config.logger.module_levels = {}
        
        init_custom_logger_system(config)
        logger = get_logger("test")
        
        # 验证配置中的first_start_time被正确使用
        from custom_logger.config import get_root_config
        root_config = get_root_config()
        assert root_config.first_start_time == specific_start_time

    def test_multiple_loggers_with_different_names(self):
        """测试创建多个不同名字的logger"""
        init_custom_logger_system(self.base_config)
        
        # 创建多个logger
        logger1 = get_logger("app")
        logger2 = get_logger("db")
        logger3 = get_logger("api")
        
        # 验证它们是不同的实例但都有效
        assert logger1.name == "app"
        assert logger2.name == "db"
        assert logger3.name == "api"
        
        # 验证它们都能正常工作
        logger1.info("App message")
        logger2.info("DB message")
        logger3.info("API message")

    def test_edge_case_empty_string_name(self):
        """测试边界情况：空字符串名字"""
        init_custom_logger_system(self.base_config)
        
        # 空字符串应该是有效的（长度为0，小于8）
        logger = get_logger("")
        assert logger.name == ""

    def test_edge_case_exactly_8_characters(self):
        """测试边界情况：恰好8个字符的名字"""
        init_custom_logger_system(self.base_config)
        
        # 恰好8个字符应该是有效的
        logger = get_logger("12345678")
        assert logger.name == "12345678"

    def test_edge_case_9_characters(self):
        """测试边界情况：9个字符的名字"""
        init_custom_logger_system(self.base_config)
        
        # 9个字符应该抛出异常
        with pytest.raises(ValueError, match="日志记录器名称不能超过8个字符，当前长度: 9"):
            get_logger("123456789")

    def test_config_object_missing_logger_attribute(self):
        """测试配置对象缺少logger属性的情况"""
        config = Mock()
        config.first_start_time = datetime.now()
        config.paths = Mock()
        config.paths.log_dir = self.log_dir
        # 没有logger属性
        
        # 应该能够初始化（使用默认配置）
        init_custom_logger_system(config)
        assert is_initialized() == True
        
        # 应该能够获取logger
        logger = get_logger("test")
        assert logger is not None

    def test_config_attributes_auto_supplement(self):
        """测试config属性自动补充功能"""
        # 创建一个缺少logger属性的config对象
        config = Mock()
        config.first_start_time = datetime.now()
        config.paths = Mock()
        config.paths.log_dir = self.log_dir
        # 确保没有logger属性
        if hasattr(config, 'logger'):
            delattr(config, 'logger')
        
        # 验证初始化前没有logger属性
        assert not hasattr(config, 'logger')
        
        # 初始化系统
        init_custom_logger_system(config)
        
        # 验证logger属性被自动添加
        assert hasattr(config, 'logger')
        assert config.logger is not None
        
        # 验证logger的各个子属性都被正确设置
        assert hasattr(config.logger, 'global_console_level')
        assert config.logger.global_console_level == "info"
        
        assert hasattr(config.logger, 'global_file_level')
        assert config.logger.global_file_level == "debug"
        
        assert hasattr(config.logger, 'module_levels')
        assert config.logger.module_levels == {}
        
        assert hasattr(config.logger, 'show_call_chain')
        assert config.logger.show_call_chain == True
        
        assert hasattr(config.logger, 'show_debug_call_stack')
        assert config.logger.show_debug_call_stack == False
        
        assert hasattr(config.logger, 'enable_queue_mode')
        assert config.logger.enable_queue_mode == False

    def test_config_partial_logger_attributes_supplement(self):
        """测试config部分logger属性自动补充功能"""
        # 创建一个有logger但缺少部分属性的config对象
        config = Mock()
        config.first_start_time = datetime.now()
        config.paths = Mock()
        config.paths.log_dir = self.log_dir
        
        # 创建一个不完整的logger对象，明确设置一些属性，删除其他属性
        config.logger = Mock()
        config.logger.global_console_level = "warning"  # 已有属性
        config.logger.global_file_level = "error"  # 已有属性
        # 删除其他属性，确保它们不存在
        if hasattr(config.logger, 'module_levels'):
            delattr(config.logger, 'module_levels')
        if hasattr(config.logger, 'show_call_chain'):
            delattr(config.logger, 'show_call_chain')
        if hasattr(config.logger, 'show_debug_call_stack'):
            delattr(config.logger, 'show_debug_call_stack')
        if hasattr(config.logger, 'enable_queue_mode'):
            delattr(config.logger, 'enable_queue_mode')
        
        # 初始化系统
        init_custom_logger_system(config)
        
        # 验证已有属性保持不变
        assert config.logger.global_console_level == "warning"
        assert config.logger.global_file_level == "error"
        
        # 验证缺失的属性被自动补充
        assert hasattr(config.logger, 'module_levels')
        assert config.logger.module_levels == {}
        
        assert hasattr(config.logger, 'show_call_chain')
        assert config.logger.show_call_chain == True
        
        assert hasattr(config.logger, 'show_debug_call_stack')
        assert config.logger.show_debug_call_stack == False
        
        assert hasattr(config.logger, 'enable_queue_mode')
        assert config.logger.enable_queue_mode == False

    def test_config_none_attributes_supplement(self):
        """测试config中None值属性的自动补充功能"""
        # 创建一个有logger但属性值为None的config对象
        config = Mock()
        config.first_start_time = datetime.now()
        config.paths = Mock()
        config.paths.log_dir = self.log_dir
        
        # 创建一个属性值为None的logger对象
        config.logger = Mock()
        config.logger.global_console_level = None
        config.logger.global_file_level = None
        config.logger.module_levels = None
        config.logger.show_call_chain = None
        config.logger.show_debug_call_stack = None
        config.logger.enable_queue_mode = None
        
        # 初始化系统
        init_custom_logger_system(config)
        
        # 验证None值属性被自动补充为默认值
        assert config.logger.global_console_level == "info"
        assert config.logger.global_file_level == "debug"
        assert config.logger.module_levels == {}
        assert config.logger.show_call_chain == True
        assert config.logger.show_debug_call_stack == False
        assert config.logger.enable_queue_mode == False

    def test_config_readonly_object_attributes_supplement(self):
        """测试只读config对象的属性补充处理"""
        # 创建一个模拟的只读对象
        class ReadOnlyConfig:
            def __init__(self, log_dir):
                self.first_start_time = datetime.now()
                self.paths = Mock()
                self.paths.log_dir = log_dir
            
            def __setattr__(self, name, value):
                if name in ['first_start_time', 'paths']:
                    super().__setattr__(name, value)
                else:
                    raise AttributeError(f"Cannot set attribute '{name}' on readonly object")
        
        config = ReadOnlyConfig(self.log_dir)
        
        # 初始化系统应该不会因为无法设置属性而失败
        init_custom_logger_system(config)
        assert is_initialized() == True
        
        # 应该能够获取logger（使用默认配置）
        logger = get_logger("test")
        assert logger is not None

    def test_invalid_log_directory_creation(self):
        """测试无效日志目录创建的错误处理"""
        config = Mock()
        config.first_start_time = datetime.now()
        config.paths = Mock()
        # 使用一个无效的路径（比如在只读位置）
        config.paths.log_dir = "/root/invalid_path_that_cannot_be_created"
        config.logger = Mock()
        config.logger.global_console_level = "info"
        config.logger.global_file_level = "debug"
        config.logger.module_levels = {}
        
        # 在Windows上，这个测试可能不会失败，所以我们用一个更可靠的方法
        # 使用一个包含无效字符的路径
        if os.name == 'nt':  # Windows
            config.paths.log_dir = "C:\\invalid<>path"
        else:  # Unix-like
            config.paths.log_dir = "/root/invalid_path"
        
        # 应该抛出ValueError
        with pytest.raises(ValueError, match="无法创建日志目录"):
            init_custom_logger_system(config)

    def test_system_cleanup_and_reinitialization(self):
        """测试系统清理和重新初始化"""
        # 初始化系统
        init_custom_logger_system(self.base_config)
        assert is_initialized() == True
        
        # 清理系统
        tear_down_custom_logger_system()
        assert is_initialized() == False
        
        # 重新初始化
        init_custom_logger_system(self.base_config)
        assert is_initialized() == True
        
        # 应该能够获取新的logger
        logger = get_logger("test")
        assert logger is not None 