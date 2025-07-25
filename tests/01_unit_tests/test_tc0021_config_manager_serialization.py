# tests/01_unit_tests/test_tc0021_config_manager_serialization.py
from __future__ import annotations
from datetime import datetime

import os
import tempfile
import pytest
from config_manager import get_config_manager

from custom_logger import (
    init_custom_logger_system,
    init_custom_logger_system_for_worker,
    get_logger,
    tear_down_custom_logger_system,
    is_initialized
)


class TestConfigManagerSerialization:
    """测试使用config_manager序列化功能初始化worker logger
    
    测试内容：
    1. 使用config_manager.create_serializable_snapshot()初始化worker
    2. 使用config_manager.to_dict()初始化worker
    3. 使用config_manager.get_serializable_data()初始化worker
    4. 验证序列化的config包含正确的默认logger配置
    5. 验证worker可以正常使用序列化的config初始化logger
    """
    
    def setup_method(self):
        """每个测试方法前的设置"""
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
    
    def test_tc0021_001_create_serializable_snapshot_worker_init(self):
        """测试使用create_serializable_snapshot初始化worker"""
        # 创建config_manager配置
        config = get_config_manager(test_mode=True)
        config.project_name = "test_snapshot"
        config.experiment_name = "worker_test"
        config.paths.log_dir = self.log_dir
        config.first_start_time = datetime.now()
        
        # 初始化主进程logger系统（确保logger配置被创建）
        init_custom_logger_system(config)
        
        # 创建可序列化快照
        serializable_snapshot = config.create_serializable_snapshot()
        
        # 验证快照包含必要属性
        assert hasattr(serializable_snapshot, 'paths')
        assert hasattr(serializable_snapshot.paths, 'log_dir')
        assert hasattr(serializable_snapshot, 'first_start_time')
        assert hasattr(serializable_snapshot, 'logger')
        
        # 验证logger配置的默认值
        logger_config = serializable_snapshot.logger
        if hasattr(logger_config, 'show_call_chain'):
            assert logger_config.show_call_chain is False
        elif isinstance(logger_config, dict):
            assert logger_config.get('show_call_chain', True) is False
        
        # 清理主进程
        tear_down_custom_logger_system()
        
        # 使用快照初始化worker
        worker_id = "snapshot_worker"
        init_custom_logger_system_for_worker(serializable_snapshot, worker_id)
        
        # 验证worker初始化成功
        assert is_initialized()
        
        # 获取logger并测试
        logger = get_logger("snap_test")
        logger.info("使用快照初始化的worker logger正常工作")
    
    def test_tc0021_002_to_dict_worker_init(self):
        """测试使用to_dict()初始化worker"""
        # 创建config_manager配置
        config = get_config_manager(test_mode=True)
        config.project_name = "test_to_dict"
        config.experiment_name = "worker_test"
        config.paths.log_dir = self.log_dir
        config.first_start_time = datetime.now()
        
        # 初始化主进程logger系统
        init_custom_logger_system(config)
        
        # 转换为字典
        config_dict = config.to_dict()
        
        # 验证字典包含必要键
        assert 'paths' in config_dict
        assert 'log_dir' in config_dict['paths']
        assert 'first_start_time' in config_dict
        assert 'logger' in config_dict
        
        # 验证logger配置的默认值
        logger_config = config_dict['logger']
        assert isinstance(logger_config, dict)
        assert logger_config.get('show_call_chain', True) is False
        assert logger_config.get('show_debug_call_stack', True) is False
        
        # 清理主进程
        tear_down_custom_logger_system()
        
        # 使用config_dict重建配置对象
        worker_config = get_config_manager(test_mode=True)
        worker_config.from_dict(config_dict)
        
        # 使用重建的配置初始化worker
        worker_id = "dict_worker"
        init_custom_logger_system_for_worker(worker_config, worker_id)
        
        # 验证worker初始化成功
        assert is_initialized()
        
        # 获取logger并测试
        logger = get_logger("dict_test")
        logger.info("使用to_dict重建配置的worker logger正常工作")
    
    def test_tc0021_003_get_serializable_data_worker_init(self):
        """测试使用get_serializable_data()初始化worker"""
        # 创建config_manager配置
        config = get_config_manager(test_mode=True)
        config.project_name = "test_serializable_data"
        config.experiment_name = "worker_test"
        config.paths.log_dir = self.log_dir
        config.first_start_time = datetime.now()
        
        # 初始化主进程logger系统
        init_custom_logger_system(config)
        
        # 获取可序列化数据（返回SerializableConfigData对象）
        serializable_data = config.get_serializable_data()
        
        # 验证数据类型和内容（SerializableConfigData对象具有类似字典的访问方式）
        assert hasattr(serializable_data, 'paths')
        assert hasattr(serializable_data, 'first_start_time')
        assert hasattr(serializable_data, 'logger')
        
        # 验证logger配置的默认值
        logger_config = serializable_data.logger
        # logger_config也可能是SerializableConfigData对象
        if isinstance(logger_config, dict):
            assert logger_config.get('show_call_chain', True) is False
        else:
            # SerializableConfigData对象具有属性访问
            assert hasattr(logger_config, 'show_call_chain')
            assert logger_config.show_call_chain is False
        
        # 清理主进程
        tear_down_custom_logger_system()
        
        # 直接使用SerializableConfigData对象初始化worker（它应该可以直接使用）
        worker_id = "serializable_worker"
        init_custom_logger_system_for_worker(serializable_data, worker_id)
        
        # 验证worker初始化成功
        assert is_initialized()
        
        # 获取logger并测试
        logger = get_logger("serial_test")
        logger.info("使用get_serializable_data的worker logger正常工作")
    
    def test_tc0021_004_serialization_preserves_logger_defaults(self):
        """测试序列化过程保持logger默认配置"""
        # 创建config_manager配置（不手动设置logger）
        config = get_config_manager(test_mode=True)
        config.project_name = "test_defaults"
        config.experiment_name = "preserve_test"
        config.paths.log_dir = self.log_dir
        config.first_start_time = datetime.now()
        
        # 初始化主进程（会自动创建logger配置）
        init_custom_logger_system(config)
        
        # 测试所有序列化方法都保持正确的默认值
        serialization_methods = [
            ("snapshot", lambda c: c.create_serializable_snapshot()),
            ("to_dict", lambda c: c.to_dict()),
            ("serializable_data", lambda c: c.get_serializable_data())
        ]
        
        for method_name, serialize_func in serialization_methods:
            serialized_config = serialize_func(config)
            
            # 根据返回类型获取logger配置
            if hasattr(serialized_config, 'logger'):
                logger_config = serialized_config.logger
            elif isinstance(serialized_config, dict) and 'logger' in serialized_config:
                logger_config = serialized_config['logger']
            else:
                pytest.fail(f"{method_name}序列化结果中没有logger配置")
            
            # 验证关键默认值
            if isinstance(logger_config, dict):
                assert logger_config.get('show_call_chain', True) is False, f"{method_name}方法未保持show_call_chain=False"
                assert logger_config.get('show_debug_call_stack', True) is False, f"{method_name}方法未保持show_debug_call_stack=False"
                assert logger_config.get('global_console_level', '') == 'info', f"{method_name}方法未保持global_console_level=info"
                assert logger_config.get('global_file_level', '') == 'debug', f"{method_name}方法未保持global_file_level=debug"
            else:
                assert hasattr(logger_config, 'show_call_chain'), f"{method_name}方法logger配置缺少show_call_chain属性"
                assert logger_config.show_call_chain is False, f"{method_name}方法未保持show_call_chain=False"
    
    def test_tc0021_005_multiprocess_serialization_flow(self):
        """测试完整的多进程序列化流程"""
        # 模拟主进程：创建配置并序列化
        main_config = get_config_manager(test_mode=True)
        main_config.project_name = "multiprocess_test"
        main_config.experiment_name = "full_flow"
        main_config.paths.log_dir = self.log_dir
        main_config.first_start_time = datetime.now()
        
        # 主进程初始化logger系统
        init_custom_logger_system(main_config)
        main_logger = get_logger("main_proc")
        main_logger.info("主进程logger初始化完成")
        
        # 主进程序列化配置（模拟发送给worker）
        serialized_for_worker = main_config.create_serializable_snapshot()
        
        # 模拟主进程关闭
        tear_down_custom_logger_system()
        
        # 模拟worker进程：接收序列化配置并初始化
        worker_id = "multiprocess_worker"
        init_custom_logger_system_for_worker(serialized_for_worker, worker_id)
        
        # worker进程使用logger
        worker_logger = get_logger("worker_proc")
        worker_logger.info("Worker进程logger初始化完成")
        
        # 验证worker正常工作
        assert is_initialized()
        
        # 验证worker正常运行即可（说明序列化配置正确传递）
        # 主要目标是验证config_manager的序列化功能可以正常用于worker初始化
        # worker能够正常获取logger并写入日志说明序列化配置传递成功
    
    def test_tc0021_006_serialization_error_handling(self):
        """测试序列化过程的错误处理"""
        # 测试None配置对象的错误处理
        with pytest.raises(ValueError, match="不能为None"):
            init_custom_logger_system_for_worker(None, "error_worker")
        
        # 测试缺少必要属性的配置
        # 创建一个简单的对象而不是Mock（避免Mock属性访问问题）
        class IncompleteConfig:
            pass
        
        incomplete_config = IncompleteConfig()
        # 完全没有任何属性
        with pytest.raises(ValueError, match="必须包含paths属性"):
            init_custom_logger_system_for_worker(incomplete_config, "error_worker")
        
        # 测试config_manager序列化的配置包含所有必要属性
        # 即使初始配置不完整，序列化过程应该补充必要的默认值
        config = get_config_manager(test_mode=True)
        config.project_name = "auto_complete_test"
        # config_manager应该自动补充paths.log_dir
        snapshot = config.create_serializable_snapshot()
        
        # 验证序列化后包含必要属性
        assert hasattr(snapshot, 'paths')
        assert hasattr(snapshot.paths, 'log_dir')
        assert hasattr(snapshot, 'first_start_time')
        
        # 这样的配置应该能正常初始化worker
        init_custom_logger_system_for_worker(snapshot, "auto_complete_worker")
        assert is_initialized()