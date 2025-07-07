# tests/01_unit_tests/test_tc0017_new_api_requirements.py
"""
测试新API需求的全面测试用例

测试内容：
1. init_custom_logger_system只接收config_object参数，不再支持first_start_time参数
2. config_object必须包含paths.log_dir和first_start_time属性
3. worker初始化函数正确处理序列化config对象和队列模式
4. get_logger名字超过8个字符直接抛出异常
5. worker用时计算正确
6. 队列模式的正确工作
"""
from __future__ import annotations

import os
import sys
import tempfile
import shutil
import multiprocessing as mp
from datetime import datetime
from unittest.mock import Mock, patch
import pytest

# 添加src路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from custom_logger import (
    init_custom_logger_system,
    init_custom_logger_system_for_worker,
    get_logger,
    tear_down_custom_logger_system,
    is_initialized,
    is_queue_mode
)


class TestNewAPIRequirements:
    """新API需求测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 确保日志系统未初始化
        tear_down_custom_logger_system()
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = os.path.join(self.temp_dir, "logs")
        
        # 创建基本的config对象
        self.basic_config = Mock()
        self.basic_config.paths = Mock()
        self.basic_config.paths.log_dir = self.log_dir
        self.basic_config.first_start_time = datetime.now()
        # 使用字典而不是Mock对象，避免enable_queue_mode被误认为存在
        self.basic_config.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
            "module_levels": {}
        }
        # 确保没有queue_info属性
        del self.basic_config.queue_info
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        tear_down_custom_logger_system()
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_config_object_only(self):
        """测试只使用config_object参数初始化"""
        # 测试正常初始化
        init_custom_logger_system(self.basic_config)
        assert is_initialized()
        assert not is_queue_mode()
        
        # 测试重复初始化不报错
        init_custom_logger_system(self.basic_config)
        assert is_initialized()
    
    def test_init_config_object_none(self):
        """测试config_object为None时抛出异常"""
        with pytest.raises(ValueError, match="config_object不能为None"):
            init_custom_logger_system(None)
    
    def test_init_missing_paths_attribute(self):
        """测试缺少paths属性时抛出异常"""
        config = Mock()
        config.first_start_time = datetime.now()
        # 删除paths属性，让getattr返回None
        del config.paths
        
        with pytest.raises(ValueError, match="config_object必须包含paths属性"):
            init_custom_logger_system(config)
    
    def test_init_missing_log_dir_attribute(self):
        """测试缺少paths.log_dir属性时抛出异常"""
        config = Mock()
        config.paths = Mock()
        # paths.log_dir为None
        config.paths.log_dir = None
        config.first_start_time = datetime.now()
        
        with pytest.raises(ValueError, match="config_object必须包含paths.log_dir属性"):
            init_custom_logger_system(config)
    
    def test_init_missing_first_start_time(self):
        """测试缺少first_start_time属性时抛出异常"""
        config = Mock()
        config.paths = Mock()
        config.paths.log_dir = self.log_dir
        # 删除first_start_time属性
        del config.first_start_time
        
        with pytest.raises(ValueError, match="config_object必须包含first_start_time属性"):
            init_custom_logger_system(config)
    
    def test_init_with_dict_paths(self):
        """测试paths为字典格式的config对象"""
        config = Mock()
        config.paths = {"log_dir": self.log_dir}
        config.first_start_time = datetime.now()
        config.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
            "module_levels": {}
        }
        # 确保没有queue_info属性
        del config.queue_info
        
        init_custom_logger_system(config)
        assert is_initialized()
    
    def test_init_with_queue_mode(self):
        """测试启用队列模式"""
        config = Mock()
        config.paths = Mock()
        config.paths.log_dir = self.log_dir
        config.first_start_time = datetime.now()
        config.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
            "module_levels": {}
        }
        
        # 添加队列信息
        config.queue_info = Mock()
        config.queue_info.log_queue = mp.Queue()
        
        with patch('custom_logger.manager.init_queue_receiver') as mock_init_receiver:
            init_custom_logger_system(config)
            assert is_initialized()
            assert is_queue_mode()
            mock_init_receiver.assert_called_once_with(config.queue_info.log_queue, self.log_dir)
    
    def test_init_with_dict_queue_info(self):
        """测试queue_info为字典格式"""
        config = Mock()
        config.paths = Mock()
        config.paths.log_dir = self.log_dir
        config.first_start_time = datetime.now()
        config.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
            "module_levels": {}
        }
        
        # queue_info为字典格式
        config.queue_info = {"log_queue": mp.Queue()}
        
        with patch('custom_logger.manager.init_queue_receiver') as mock_init_receiver:
            init_custom_logger_system(config)
            assert is_initialized()
            assert is_queue_mode()
            mock_init_receiver.assert_called_once()
    
    def test_worker_init_with_serializable_config(self):
        """测试worker初始化函数"""
        serializable_config = Mock()
        serializable_config.paths = Mock()
        serializable_config.paths.log_dir = self.log_dir
        serializable_config.first_start_time = datetime.now()
        serializable_config.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
            "module_levels": {}
        }
        # 确保没有queue_info属性
        del serializable_config.queue_info
        
        worker_id = "worker_001"
        
        init_custom_logger_system_for_worker(serializable_config, worker_id)
        assert is_initialized()
        assert not is_queue_mode()  # 没有队列信息时为普通模式
    
    def test_worker_init_with_queue_mode(self):
        """测试worker初始化启用队列模式"""
        serializable_config = Mock()
        serializable_config.paths = Mock()
        serializable_config.paths.log_dir = self.log_dir
        serializable_config.first_start_time = datetime.now()
        serializable_config.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
            "module_levels": {}
        }
        
        # 添加队列信息
        serializable_config.queue_info = Mock()
        serializable_config.queue_info.log_queue = mp.Queue()
        
        worker_id = "worker_001"
        
        with patch('custom_logger.manager.init_queue_sender') as mock_init_sender:
            init_custom_logger_system_for_worker(serializable_config, worker_id)
            assert is_initialized()
            assert is_queue_mode()
            mock_init_sender.assert_called_once_with(serializable_config.queue_info.log_queue, worker_id)
    
    def test_worker_init_none_config(self):
        """测试worker初始化时config为None"""
        with pytest.raises(ValueError, match="serializable_config_object不能为None"):
            init_custom_logger_system_for_worker(None)
    
    def test_worker_init_missing_paths(self):
        """测试worker初始化时缺少paths属性"""
        config = Mock()
        config.first_start_time = datetime.now()
        # 删除paths属性
        del config.paths
        
        with pytest.raises(ValueError, match="serializable_config_object必须包含paths属性"):
            init_custom_logger_system_for_worker(config)
    
    def test_worker_init_missing_log_dir(self):
        """测试worker初始化时缺少log_dir属性"""
        config = Mock()
        config.paths = Mock()
        config.paths.log_dir = None
        config.first_start_time = datetime.now()
        
        with pytest.raises(ValueError, match="serializable_config_object必须包含paths.log_dir属性"):
            init_custom_logger_system_for_worker(config)
    
    def test_worker_init_missing_first_start_time(self):
        """测试worker初始化时缺少first_start_time属性"""
        config = Mock()
        config.paths = Mock()
        config.paths.log_dir = self.log_dir
        # 删除first_start_time属性
        del config.first_start_time
        
        with pytest.raises(ValueError, match="serializable_config_object必须包含first_start_time属性"):
            init_custom_logger_system_for_worker(config)
    
    def test_get_logger_name_length_check(self):
        """测试get_logger名字长度检查"""
        init_custom_logger_system(self.basic_config)
        
        # 正常长度的名字
        logger1 = get_logger("test")
        assert logger1 is not None
        
        logger2 = get_logger("1234567890123456")  # 16个字符，边界情况
        assert logger2 is not None
        
        # 超过16个字符的名字
        with pytest.raises(ValueError, match=r"日志记录器名称.*不能超过16个字符，当前长度: \d+"):
            get_logger("12345678901234567")  # 17个字符
    
    def test_get_logger_without_init(self):
        """测试未初始化时调用get_logger"""
        with pytest.raises(RuntimeError, match="日志系统未初始化"):
            get_logger("test")
    
    def test_worker_time_calculation(self):
        """测试worker用时计算正确"""
        # 设置一个固定的first_start_time
        fixed_start_time = datetime(2025, 1, 1, 10, 0, 0)
        
        serializable_config = Mock()
        serializable_config.paths = Mock()
        serializable_config.paths.log_dir = self.log_dir
        serializable_config.first_start_time = fixed_start_time
        serializable_config.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
            "module_levels": {}
        }
        # 确保没有queue_info属性
        del serializable_config.queue_info
        
        init_custom_logger_system_for_worker(serializable_config, "worker_001")
        
        # 获取logger并测试时间计算
        logger = get_logger("worker01")
        
        # Mock当前时间为start_time + 5秒
        current_time = datetime(2025, 1, 1, 10, 0, 5)
        
        # 需要Mock多个地方的datetime
        with patch('custom_logger.logger.datetime') as mock_logger_datetime, \
             patch('custom_logger.formatter.datetime') as mock_formatter_datetime:
            
            mock_logger_datetime.now.return_value = current_time
            mock_formatter_datetime.now.return_value = current_time
            
            # 测试日志输出包含正确的运行时长
            with patch('builtins.print') as mock_print:
                logger.info("测试消息")
                
                # 检查print调用的参数
                assert mock_print.called
                printed_message = mock_print.call_args[0][0]
                
                # 应该包含运行时长信息（5秒）
                # 由于时间格式可能不同，我们检查是否包含5秒的表示
                assert "0:00:05" in printed_message or "00:05" in printed_message or "5.0" in printed_message
    
    def test_queue_mode_integration(self):
        """测试队列模式的集成"""
        # 创建队列
        log_queue = mp.Queue()
        
        # 主程序配置（接收器）
        main_config = Mock()
        main_config.paths = Mock()
        main_config.paths.log_dir = self.log_dir
        main_config.first_start_time = datetime.now()
        main_config.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
            "module_levels": {}
        }
        main_config.queue_info = Mock()
        main_config.queue_info.log_queue = log_queue
        
        # Worker配置（发送器）
        worker_config = Mock()
        worker_config.paths = Mock()
        worker_config.paths.log_dir = self.log_dir
        worker_config.first_start_time = datetime.now()
        worker_config.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
            "module_levels": {}
        }
        worker_config.queue_info = Mock()
        worker_config.queue_info.log_queue = log_queue
        
        # 测试主程序初始化
        with patch('custom_logger.manager.init_queue_receiver') as mock_init_receiver:
            init_custom_logger_system(main_config)
            assert is_queue_mode()
            mock_init_receiver.assert_called_once()
        
        # 清理并测试worker初始化
        tear_down_custom_logger_system()
        
        with patch('custom_logger.manager.init_queue_sender') as mock_init_sender:
            init_custom_logger_system_for_worker(worker_config, "worker_001")
            assert is_queue_mode()
            mock_init_sender.assert_called_once()
    
    def test_config_object_attribute_validation(self):
        """测试config对象属性验证的边界情况"""
        # 测试paths为空字典
        config = Mock()
        config.paths = {}  # 空字典
        config.first_start_time = datetime.now()
        
        with pytest.raises(ValueError, match="config_object必须包含paths.log_dir属性"):
            init_custom_logger_system(config)
        
        # 测试paths字典中log_dir为None
        config.paths = {"log_dir": None}
        
        with pytest.raises(ValueError, match="config_object必须包含paths.log_dir属性"):
            init_custom_logger_system(config)
        
        # 测试paths对象中log_dir属性不存在
        config.paths = Mock()
        # 删除log_dir属性，让getattr返回None
        del config.paths.log_dir
        
        with pytest.raises(ValueError, match="config_object必须包含paths.log_dir属性"):
            init_custom_logger_system(config)
    
    def test_multiple_logger_instances(self):
        """测试创建多个logger实例"""
        init_custom_logger_system(self.basic_config)
        
        # 创建多个不同名字的logger
        logger1 = get_logger("test1")
        logger2 = get_logger("test2")
        logger3 = get_logger("12345678")  # 8个字符的边界情况
        
        assert logger1 is not None
        assert logger2 is not None
        assert logger3 is not None
        
        # 确保它们是不同的实例
        assert logger1 != logger2
        assert logger2 != logger3
    
    def test_system_cleanup(self):
        """测试系统清理功能"""
        init_custom_logger_system(self.basic_config)
        assert is_initialized()
        
        tear_down_custom_logger_system()
        assert not is_initialized()
        assert not is_queue_mode()
        
        # 重复清理不应该出错
        tear_down_custom_logger_system()
        assert not is_initialized()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 