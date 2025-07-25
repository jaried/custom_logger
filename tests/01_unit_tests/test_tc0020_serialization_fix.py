# tests/01_unit_tests/test_tc0020_serialization_fix.py
from __future__ import annotations
from datetime import datetime

import os
import tempfile
import pytest
from unittest.mock import Mock, patch
from config_manager import get_config_manager

from custom_logger import (
    init_custom_logger_system,
    init_custom_logger_system_for_worker,
    get_logger,
    tear_down_custom_logger_system,
    is_initialized
)
from src.custom_logger.config import init_config_from_object, _ensure_logger_attributes


class TestSerializationFix:
    """测试序列化修复和调用链默认配置
    
    测试内容：
    1. 验证_ensure_logger_attributes使用字典而非动态类
    2. 验证调用链默认不显示（show_call_chain: False）
    3. 验证序列化config对象能正常初始化worker
    4. 验证缺失logger配置时自动补充默认值
    """
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 使用test_mode=True进行测试隔离
        self.config = get_config_manager(test_mode=True)
        self.config.project_name = "test_serialization"
        self.config.experiment_name = "fix_test"
        
        # 创建临时日志目录
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = os.path.join(self.temp_dir, "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 确保测试开始时系统未初始化
        if is_initialized():
            tear_down_custom_logger_system()
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        if is_initialized():
            tear_down_custom_logger_system()
    
    def test_tc0020_001_ensure_logger_attributes_creates_dict(self):
        """测试_ensure_logger_attributes创建字典类型而非动态类"""
        # 创建没有logger属性的配置对象
        config_obj = Mock()
        config_obj.paths = Mock()
        config_obj.paths.log_dir = self.log_dir
        config_obj.first_start_time = datetime.now()
        # 确保没有logger属性
        del config_obj.logger
        
        # 调用_ensure_logger_attributes
        _ensure_logger_attributes(config_obj)
        
        # 验证logger属性被创建且为字典类型
        assert hasattr(config_obj, 'logger')
        assert isinstance(config_obj.logger, dict)
        
        # 验证默认值
        assert config_obj.logger['global_console_level'] == 'info'
        assert config_obj.logger['global_file_level'] == 'debug'
        assert config_obj.logger['show_call_chain'] is False  # 关键验证
        assert config_obj.logger['show_debug_call_stack'] is False
        assert config_obj.logger['enable_queue_mode'] is False
        assert isinstance(config_obj.logger['module_levels'], dict)
    
    def test_tc0020_002_call_chain_default_false(self):
        """测试调用链默认配置为False，日志中不显示调用链"""
        # 创建配置但不设置show_call_chain
        config_obj = Mock()
        config_obj.paths = Mock()
        config_obj.paths.log_dir = self.log_dir
        config_obj.first_start_time = datetime.now()
        # 不设置logger配置，让_ensure_logger_attributes自动创建
        del config_obj.logger
        
        # 初始化系统（会调用_ensure_logger_attributes）
        init_custom_logger_system(config_obj)
        
        # 获取logger并写入日志
        logger = get_logger("test_chain")
        
        # 捕获输出以验证调用链不显示
        with patch('builtins.print') as mock_print:
            logger.info("测试调用链不显示")
            
            # 验证没有调用print输出调用链信息
            # 检查是否有包含"[调用链]"的调用
            call_chain_prints = [
                call for call in mock_print.call_args_list
                if len(call[0]) > 0 and "[调用链]" in str(call[0][0])
            ]
            assert len(call_chain_prints) == 0, "调用链信息不应该显示"
    
    def test_tc0020_003_worker_init_with_dict_logger_config(self):
        """测试使用字典类型logger配置初始化worker"""
        # 创建序列化配置对象，使用字典类型logger配置
        serializable_config = Mock()
        serializable_config.paths = Mock()
        serializable_config.paths.log_dir = self.log_dir
        serializable_config.first_start_time = datetime.now()
        
        # 使用字典类型的logger配置（模拟序列化后的状态）
        serializable_config.logger = {
            'global_console_level': 'info',
            'global_file_level': 'debug',
            'module_levels': {},
            'show_call_chain': False,
            'show_debug_call_stack': False,
            'enable_queue_mode': False
        }
        
        worker_id = "test_worker_001"
        
        # 初始化worker（应该不会出现序列化错误）
        init_custom_logger_system_for_worker(serializable_config, worker_id)
        
        # 验证初始化成功
        assert is_initialized()
        
        # 获取logger并验证工作正常
        logger = get_logger("worker_test")
        logger.info("Worker logger正常工作")
    
    def test_tc0020_004_missing_logger_config_auto_supplement(self):
        """测试缺失logger配置时自动补充默认值"""
        # 创建完全没有logger配置的对象
        config_obj = Mock()
        config_obj.paths = Mock()
        config_obj.paths.log_dir = self.log_dir
        config_obj.first_start_time = datetime.now()
        # 完全没有logger属性
        del config_obj.logger
        
        # 使用init_config_from_object应该自动补充logger配置
        init_config_from_object(config_obj)
        
        # 验证logger配置被自动创建且为正确的默认值
        assert hasattr(config_obj, 'logger')
        logger_config = config_obj.logger
        
        # 如果是字典类型
        if isinstance(logger_config, dict):
            assert logger_config['show_call_chain'] is False
            assert logger_config['show_debug_call_stack'] is False
            assert logger_config['global_console_level'] == 'info'
            assert logger_config['global_file_level'] == 'debug'
        else:
            # 如果是对象类型
            assert hasattr(logger_config, 'show_call_chain')
            assert logger_config.show_call_chain is False
            assert logger_config.show_debug_call_stack is False
    
    def test_tc0020_005_serialization_compatibility(self):
        """测试配置对象的序列化兼容性"""
        # 创建配置对象并初始化
        config_obj = Mock()
        config_obj.paths = Mock()
        config_obj.paths.log_dir = self.log_dir
        config_obj.first_start_time = datetime.now()
        del config_obj.logger  # 让系统自动创建
        
        # 初始化配置（会创建字典类型的logger配置）
        init_config_from_object(config_obj)
        
        # 验证logger配置是字典类型（可序列化）
        assert isinstance(config_obj.logger, dict) or hasattr(config_obj.logger, '__dict__')
        
        # 模拟序列化过程（应该不会失败）
        try:
            import json
            # 如果是字典，应该可以序列化
            if isinstance(config_obj.logger, dict):
                serialized = json.dumps(config_obj.logger)
                deserialized = json.loads(serialized)
                assert deserialized['show_call_chain'] is False
        except Exception as e:
            pytest.fail(f"序列化测试失败: {e}")
    
    def test_tc0020_006_ensure_attribute_dict_support(self):
        """测试_ensure_attribute函数对字典类型的支持"""
        from src.custom_logger.config import _ensure_attribute
        
        # 测试字典类型
        dict_obj = {}
        _ensure_attribute(dict_obj, 'test_key', 'test_value')
        assert dict_obj['test_key'] == 'test_value'
        
        # 测试对象类型
        obj = Mock()
        del obj.test_attr  # 确保属性不存在
        _ensure_attribute(obj, 'test_attr', 'test_value')
        assert obj.test_attr == 'test_value'
        
        # 测试覆盖None值
        dict_obj['none_key'] = None
        _ensure_attribute(dict_obj, 'none_key', 'new_value')
        assert dict_obj['none_key'] == 'new_value'
        
        # 测试不覆盖现有值
        dict_obj['existing_key'] = 'existing_value'
        _ensure_attribute(dict_obj, 'existing_key', 'new_value')
        assert dict_obj['existing_key'] == 'existing_value'