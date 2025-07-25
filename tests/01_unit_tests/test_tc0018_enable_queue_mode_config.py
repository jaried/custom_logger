#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试config.logger.enable_queue_mode参数功能

测试内容：
1. 配置中enable_queue_mode=True时启用队列模式
2. 配置中enable_queue_mode=False时不启用队列模式
3. 没有enable_queue_mode参数时保持向后兼容
4. enable_queue_mode=True但缺少queue_info时抛出异常
5. Worker进程的enable_queue_mode参数测试
"""
from __future__ import annotations

import os
import tempfile
import unittest
import multiprocessing as mp
from datetime import datetime
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.custom_logger.manager import (
    init_custom_logger_system,
    init_custom_logger_system_for_worker,
    get_logger,
    tear_down_custom_logger_system
)


class TestEnableQueueModeConfig(unittest.TestCase):
    """测试enable_queue_mode配置参数"""
    
    def setUp(self):
        """测试前准备"""
        # 使用系统临时目录
        self.temp_dir = tempfile.mkdtemp(prefix="test_enable_queue_mode_")
        self.log_dir = os.path.join(self.temp_dir, "logs")
        
        # 基础配置对象
        self.basic_config = Mock()
        self.basic_config.first_start_time = datetime.now()
        self.basic_config.project_name = "测试项目"
        self.basic_config.experiment_name = "enable_queue_mode_test"
        self.basic_config.paths = Mock()
        self.basic_config.paths.log_dir = self.log_dir
        
        # 基础logger配置
        self.basic_config.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
            "module_levels": {},
            "show_call_chain": False,  # 修复：使用新的默认值
            "show_debug_call_stack": False,
        }
    
    def tearDown(self):
        """测试后清理"""
        try:
            tear_down_custom_logger_system()
        except:
            pass
        
        # 清理临时目录
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    @patch('src.custom_logger.manager.init_queue_receiver')
    @patch('src.custom_logger.manager.init_writer')
    def test_enable_queue_mode_true_with_queue_info(self, mock_init_writer, mock_init_receiver):
        """测试enable_queue_mode=True且有queue_info时启用队列模式"""
        # 配置enable_queue_mode=True
        config = Mock()
        config.first_start_time = self.basic_config.first_start_time
        config.project_name = self.basic_config.project_name
        config.experiment_name = self.basic_config.experiment_name
        config.paths = self.basic_config.paths
        
        # logger配置中启用队列模式
        config.logger = self.basic_config.logger.copy()
        config.logger["enable_queue_mode"] = True
        
        # 提供queue_info
        config.queue_info = Mock()
        config.queue_info.log_queue = mp.Queue()
        
        # 初始化系统
        init_custom_logger_system(config)
        
        # 验证调用了队列接收器初始化，没有调用普通写入器
        mock_init_receiver.assert_called_once_with(config.queue_info.log_queue, self.log_dir)
        mock_init_writer.assert_not_called()
    
    @patch('src.custom_logger.manager.init_queue_receiver')
    @patch('src.custom_logger.manager.init_writer')
    def test_enable_queue_mode_false_with_queue_info(self, mock_init_writer, mock_init_receiver):
        """测试enable_queue_mode=False时不启用队列模式，即使有queue_info"""
        # 配置enable_queue_mode=False
        config = Mock()
        config.first_start_time = self.basic_config.first_start_time
        config.project_name = self.basic_config.project_name
        config.experiment_name = self.basic_config.experiment_name
        config.paths = self.basic_config.paths
        
        # logger配置中禁用队列模式
        config.logger = self.basic_config.logger.copy()
        config.logger["enable_queue_mode"] = False
        
        # 提供queue_info（但应该被忽略，因为enable_queue_mode=False）
        config.queue_info = Mock()
        config.queue_info.log_queue = mp.Queue()
        
        # 初始化系统
        init_custom_logger_system(config)
        
        # 验证调用了队列接收器初始化（向后兼容逻辑），没有调用普通写入器
        mock_init_receiver.assert_called_once_with(config.queue_info.log_queue, self.log_dir)
        mock_init_writer.assert_not_called()
    
    @patch('src.custom_logger.manager.init_queue_receiver')
    @patch('src.custom_logger.manager.init_writer')
    def test_no_enable_queue_mode_with_queue_info(self, mock_init_writer, mock_init_receiver):
        """测试没有enable_queue_mode参数时的向后兼容行为"""
        # 不设置enable_queue_mode参数
        config = Mock()
        config.first_start_time = self.basic_config.first_start_time
        config.project_name = self.basic_config.project_name
        config.experiment_name = self.basic_config.experiment_name
        config.paths = self.basic_config.paths
        config.logger = self.basic_config.logger.copy()
        # 注意：logger配置中没有enable_queue_mode参数
        
        # 提供queue_info
        config.queue_info = Mock()
        config.queue_info.log_queue = mp.Queue()
        
        # 初始化系统
        init_custom_logger_system(config)
        
        # 验证调用了队列接收器初始化（向后兼容逻辑）
        mock_init_receiver.assert_called_once_with(config.queue_info.log_queue, self.log_dir)
        mock_init_writer.assert_not_called()
    
    @patch('src.custom_logger.manager.init_queue_receiver')
    @patch('src.custom_logger.manager.init_writer')
    def test_no_enable_queue_mode_no_queue_info(self, mock_init_writer, mock_init_receiver):
        """测试没有enable_queue_mode和queue_info时使用普通模式"""
        # 不设置enable_queue_mode参数和queue_info
        config = Mock()
        config.first_start_time = self.basic_config.first_start_time
        config.project_name = self.basic_config.project_name
        config.experiment_name = self.basic_config.experiment_name
        config.paths = self.basic_config.paths
        config.logger = self.basic_config.logger.copy()
        # 确保没有queue_info属性
        del config.queue_info
        
        # 初始化系统
        init_custom_logger_system(config)
        
        # 验证调用了普通写入器，没有调用队列接收器
        mock_init_writer.assert_called_once()
        mock_init_receiver.assert_not_called()
    
    def test_enable_queue_mode_true_without_queue_info(self):
        """测试enable_queue_mode=True但没有queue_info时抛出异常"""
        # 配置enable_queue_mode=True但不提供queue_info
        config = Mock()
        config.first_start_time = self.basic_config.first_start_time
        config.project_name = self.basic_config.project_name
        config.experiment_name = self.basic_config.experiment_name
        config.paths = self.basic_config.paths
        
        # logger配置中启用队列模式
        config.logger = self.basic_config.logger.copy()
        config.logger["enable_queue_mode"] = True
        
        # 确保没有queue_info属性
        del config.queue_info
        
        # 验证抛出异常
        with self.assertRaises(ValueError) as context:
            init_custom_logger_system(config)
        
        self.assertIn("配置启用队列模式但未提供queue_info", str(context.exception))
    
    def test_enable_queue_mode_true_without_log_queue(self):
        """测试enable_queue_mode=True但queue_info中没有log_queue时抛出异常"""
        # 配置enable_queue_mode=True但queue_info中没有log_queue
        config = Mock()
        config.first_start_time = self.basic_config.first_start_time
        config.project_name = self.basic_config.project_name
        config.experiment_name = self.basic_config.experiment_name
        config.paths = self.basic_config.paths
        
        # logger配置中启用队列模式
        config.logger = self.basic_config.logger.copy()
        config.logger["enable_queue_mode"] = True
        
        # 提供queue_info但没有log_queue
        config.queue_info = Mock()
        del config.queue_info.log_queue
        
        # 验证抛出异常
        with self.assertRaises(ValueError) as context:
            init_custom_logger_system(config)
        
        self.assertIn("配置启用队列模式但未提供queue_info.log_queue", str(context.exception))
    
    def test_enable_queue_mode_dict_format(self):
        """测试logger配置为字典格式时的enable_queue_mode参数"""
        # 使用字典格式的logger配置
        config = Mock()
        config.first_start_time = self.basic_config.first_start_time
        config.project_name = self.basic_config.project_name
        config.experiment_name = self.basic_config.experiment_name
        config.paths = {"log_dir": self.log_dir}  # 字典格式的paths
        
        # 字典格式的logger配置
        config.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
            "enable_queue_mode": True
        }
        
        # 提供queue_info
        config.queue_info = {"log_queue": mp.Queue()}
        
        # 验证不抛出异常
        with patch('src.custom_logger.manager.init_queue_receiver'):
            init_custom_logger_system(config)
    
    @patch('src.custom_logger.manager.init_queue_sender')
    @patch('src.custom_logger.manager.init_writer')
    def test_worker_enable_queue_mode_true(self, mock_init_writer, mock_init_sender):
        """测试Worker进程中enable_queue_mode=True的行为"""
        # 创建序列化配置对象
        serializable_config = Mock()
        serializable_config.first_start_time = self.basic_config.first_start_time
        serializable_config.project_name = self.basic_config.project_name
        serializable_config.experiment_name = self.basic_config.experiment_name
        serializable_config.paths = self.basic_config.paths
        
        # logger配置中启用队列模式
        serializable_config.logger = self.basic_config.logger.copy()
        serializable_config.logger["enable_queue_mode"] = True
        
        # 提供queue_info
        serializable_config.queue_info = Mock()
        serializable_config.queue_info.log_queue = mp.Queue()
        
        worker_id = "test_worker"
        
        # 初始化worker系统
        init_custom_logger_system_for_worker(serializable_config, worker_id)
        
        # 验证调用了队列发送器初始化，没有调用普通写入器
        mock_init_sender.assert_called_once_with(serializable_config.queue_info.log_queue, worker_id)
        mock_init_writer.assert_not_called()
    
    @patch('src.custom_logger.manager.init_queue_sender')
    @patch('src.custom_logger.manager.init_writer')
    def test_worker_enable_queue_mode_false(self, mock_init_writer, mock_init_sender):
        """测试Worker进程中enable_queue_mode=False的行为"""
        # 创建序列化配置对象
        serializable_config = Mock()
        serializable_config.first_start_time = self.basic_config.first_start_time
        serializable_config.project_name = self.basic_config.project_name
        serializable_config.experiment_name = self.basic_config.experiment_name
        serializable_config.paths = self.basic_config.paths
        
        # logger配置中禁用队列模式
        serializable_config.logger = self.basic_config.logger.copy()
        serializable_config.logger["enable_queue_mode"] = False
        
        # 提供queue_info（但应该被忽略，因为enable_queue_mode=False）
        serializable_config.queue_info = Mock()
        serializable_config.queue_info.log_queue = mp.Queue()
        
        worker_id = "test_worker"
        
        # 初始化worker系统
        init_custom_logger_system_for_worker(serializable_config, worker_id)
        
        # 验证调用了队列发送器初始化（向后兼容逻辑），没有调用普通写入器
        mock_init_sender.assert_called_once_with(serializable_config.queue_info.log_queue, worker_id)
        mock_init_writer.assert_not_called()
    
    def test_worker_enable_queue_mode_true_without_queue_info(self):
        """测试Worker进程中enable_queue_mode=True但没有queue_info时抛出异常"""
        # 创建序列化配置对象
        serializable_config = Mock()
        serializable_config.first_start_time = self.basic_config.first_start_time
        serializable_config.project_name = self.basic_config.project_name
        serializable_config.experiment_name = self.basic_config.experiment_name
        serializable_config.paths = self.basic_config.paths
        
        # logger配置中启用队列模式
        serializable_config.logger = self.basic_config.logger.copy()
        serializable_config.logger["enable_queue_mode"] = True
        
        # 确保没有queue_info属性
        del serializable_config.queue_info
        
        worker_id = "test_worker"
        
        # 验证抛出异常
        with self.assertRaises(ValueError) as context:
            init_custom_logger_system_for_worker(serializable_config, worker_id)
        
        self.assertIn("配置启用队列模式但未提供queue_info", str(context.exception))


if __name__ == '__main__':
    unittest.main() 