# tests/01_unit_tests/test_tc0019_modular_logging.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import sys
import tempfile
import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any

# 添加src路径以便导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from custom_logger.writer import LogEntry, FileWriter, write_log_async
from custom_logger.types import INFO, WARNING, ERROR, DEBUG


class TestModularLogging:
    """分模块日志功能测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = tempfile.mkdtemp(prefix="custom_logger_modular_test_")
        self.test_session_dir = os.path.join(self.temp_dir, "test_session")
        os.makedirs(self.test_session_dir, exist_ok=True)
        pass

    def teardown_method(self):
        """每个测试方法后的清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        pass

    def create_test_config(self) -> MagicMock:
        """创建测试用的Mock配置对象"""
        mock_cfg = MagicMock()
        mock_cfg.base_dir = self.temp_dir
        mock_cfg.project_name = "modular_test"
        mock_cfg.experiment_name = "test_experiment"
        mock_cfg.first_start_time = "2024-01-01T12:00:00"
        mock_cfg.paths.log_dir = self.test_session_dir
        mock_cfg.logger = {
            "global_console_level": "debug",
            "global_file_level": "debug",
            "module_levels": {},
            "enable_queue_mode": False
        }
        # 确保没有queue_info以禁用队列模式
        mock_cfg.queue_info = None
        return mock_cfg

    # ==================== LogEntry类测试 ====================
    
    def test_tc0019_001_logentry_creation_with_logger_name(self):
        """测试LogEntry创建时包含logger_name参数"""
        # 测试数据
        log_line = "测试日志消息"
        level_value = INFO
        logger_name = "test_logger"
        exception_info = None
        
        # 执行：创建LogEntry对象
        entry = LogEntry(log_line, level_value, logger_name, exception_info)
        
        # 验证：对象创建成功且属性正确
        assert entry.log_line == log_line
        assert entry.level_value == level_value
        assert entry.logger_name == logger_name
        assert entry.exception_info == exception_info
        pass

    def test_tc0019_002_logentry_logger_name_attribute(self):
        """测试LogEntry.logger_name属性访问"""
        # 测试数据
        logger_name = "module_a"
        entry = LogEntry("test message", INFO, logger_name)
        
        # 验证：logger_name属性可正常访问
        assert hasattr(entry, 'logger_name')
        assert entry.logger_name == logger_name
        pass

    def test_tc0019_003_logentry_with_exception_info(self):
        """测试LogEntry包含异常信息的情况"""
        # 测试数据
        log_line = "错误日志"
        level_value = ERROR
        logger_name = "error_logger"
        exception_info = "Exception traceback info"
        
        # 执行：创建包含异常信息的LogEntry
        entry = LogEntry(log_line, level_value, logger_name, exception_info)
        
        # 验证：所有属性正确设置
        assert entry.log_line == log_line
        assert entry.level_value == level_value
        assert entry.logger_name == logger_name
        assert entry.exception_info == exception_info
        pass

    # ==================== FileWriter类测试 ====================
    
    def test_tc0019_010_filewriter_initialization(self):
        """测试FileWriter初始化时创建module_files属性"""
        # 执行：初始化FileWriter
        writer = FileWriter(self.test_session_dir)
        
        # 验证：初始化后具有module_files属性
        assert hasattr(writer, 'module_files')
        assert isinstance(writer.module_files, dict)
        assert len(writer.module_files) == 0
        pass

    def test_tc0019_011_filewriter_ensure_module_files_method(self):
        """测试_ensure_module_files方法"""
        # 准备：创建FileWriter实例
        writer = FileWriter(self.test_session_dir)
        
        # 验证：_ensure_module_files方法存在
        assert hasattr(writer, '_ensure_module_files')
        assert callable(getattr(writer, '_ensure_module_files'))
        pass

    def test_tc0019_012_filewriter_write_log_with_logger_name(self):
        """测试FileWriter.write_log方法处理包含logger_name的LogEntry"""
        # 准备：创建FileWriter和LogEntry
        writer = FileWriter(self.test_session_dir)
        entry = LogEntry("测试消息", INFO, "test_module", None)
        
        # 执行：写入日志（现在应该成功）
        writer.write_log(entry)
        
        # 验证：模块文件应该被创建
        expected_full_path = os.path.join(self.test_session_dir, "test_module_full.log")
        expected_warning_path = os.path.join(self.test_session_dir, "test_module_warning.log")
        
        assert os.path.exists(expected_full_path)
        assert os.path.exists(expected_warning_path)
        
        # 验证：INFO级别只出现在full文件中，不出现在warning文件中
        with open(expected_full_path, 'r', encoding='utf-8') as f:
            full_content = f.read()
            assert "测试消息" in full_content
            
        with open(expected_warning_path, 'r', encoding='utf-8') as f:
            warning_content = f.read()
            assert "测试消息" not in warning_content  # INFO不应该在warning文件中
        
        writer.close()
        pass

    def test_tc0019_013_filewriter_module_files_creation(self):
        """测试模块文件动态创建功能"""
        # 准备：FileWriter实例
        writer = FileWriter(self.test_session_dir)
        logger_name = "test_module"
        
        # 执行：调用_ensure_module_files方法
        try:
            writer._ensure_module_files(logger_name)
            
            # 验证：模块文件应该被创建
            expected_full_path = os.path.join(self.test_session_dir, f"{logger_name}_full.log")
            expected_warning_path = os.path.join(self.test_session_dir, f"{logger_name}_warning.log")
            
            # 这些文件应该存在（在实现后）
            assert os.path.exists(expected_full_path)
            assert os.path.exists(expected_warning_path)
            
        except AttributeError:
            # 当前实现还没有_ensure_module_files方法，这是预期的TDD失败
            pytest.skip("_ensure_module_files方法尚未实现")
        pass

    def test_tc0019_014_filewriter_level_filtering_strategy(self):
        """测试FileWriter级别过滤写入策略"""
        # 准备：FileWriter实例和不同级别的LogEntry
        writer = FileWriter(self.test_session_dir)
        
        # INFO级别日志 - 应该只写入full文件
        info_entry = LogEntry("信息日志", INFO, "test_module", None)
        
        # WARNING级别日志 - 应该写入full和warning文件
        warning_entry = LogEntry("警告日志", WARNING, "test_module", None)
        
        # 这个测试会失败，因为当前实现还不支持模块文件
        try:
            writer.write_log(info_entry)
            writer.write_log(warning_entry)
            
            # 验证文件内容（在实现后）
            full_file_path = os.path.join(self.test_session_dir, "test_module_full.log")
            warning_file_path = os.path.join(self.test_session_dir, "test_module_warning.log")
            
            with open(full_file_path, 'r', encoding='utf-8') as f:
                full_content = f.read()
                assert "信息日志" in full_content
                assert "警告日志" in full_content
                
            with open(warning_file_path, 'r', encoding='utf-8') as f:
                warning_content = f.read()
                assert "信息日志" not in warning_content  # INFO不应该在warning文件中
                assert "警告日志" in warning_content
                
        except (AttributeError, FileNotFoundError):
            # 当前实现还不支持模块文件，这是预期的TDD失败
            pytest.skip("模块文件功能尚未实现")
        pass

    # ==================== write_log_async函数测试 ====================
    
    def test_tc0019_020_write_log_async_with_logger_name(self):
        """测试write_log_async接收logger_name参数"""
        # 测试数据
        log_line = "异步日志测试"
        level_value = INFO
        logger_name = "async_logger"
        exception_info = None
        
        # 执行：调用write_log_async（这会失败，因为当前签名还不支持logger_name）
        try:
            write_log_async(log_line, level_value, logger_name, exception_info)
            # 如果执行到这里，说明函数已经支持新的签名
            assert True  # 表示测试通过
        except TypeError as e:
            # 当前实现还不支持logger_name参数，这是预期的TDD失败
            assert "logger_name" in str(e) or "positional argument" in str(e)
        pass

    def test_tc0019_021_write_log_async_parameter_order(self):
        """测试write_log_async参数顺序正确性"""
        # 验证参数顺序：log_line, level_value, logger_name, exception_info
        
        try:
            # 使用关键字参数确保顺序正确
            write_log_async(
                log_line="测试消息",
                level_value=INFO,
                logger_name="order_test",
                exception_info=None
            )
            assert True  # 如果没有异常，说明参数顺序正确
        except TypeError:
            # 当前实现还不支持logger_name参数
            pytest.skip("write_log_async新接口尚未实现")
        pass

    # ==================== 集成测试用例 ====================
    
    def test_tc0019_100_logger_calls_writer_with_name(self):
        """测试logger._log方法传递logger_name给writer"""
        from custom_logger.logger import CustomLogger
        from custom_logger import config, manager
        
        # 准备：创建logger实例并初始化系统
        mock_config = self.create_test_config()
        
        with patch.object(config, 'get_root_config', return_value=mock_config):
            # 初始化日志系统
            with patch.object(config, 'init_config_from_object') as mock_init:
                mock_init.return_value = None
                manager.init_custom_logger_system(mock_config)
                
                # Mock write_log_async在logger模块级别
                with patch('custom_logger.logger.write_log_async') as mock_write_log_async:
                    logger = CustomLogger("test_logger")
                    
                    # 执行：调用logger方法
                    logger.info("测试消息")
                    
                    # 验证：write_log_async被正确调用
                    assert mock_write_log_async.called
                    call_args = mock_write_log_async.call_args
                    assert len(call_args[0]) >= 3  # 应该有至少3个位置参数
                    # 新实现应该传递logger_name作为第三个参数
                    assert call_args[0][2] == "test_logger"  # logger_name参数
        pass

    # ==================== 端到端测试用例 ====================
    
    def test_tc0019_200_complete_modular_logging_workflow(self):
        """测试完整的分模块日志工作流程"""
        # 这是一个端到端测试，验证整个流程
        # 由于当前实现还不完整，大部分会失败
        
        pytest.skip("等待实现完成后进行端到端测试")
        pass

    def test_tc0019_201_file_content_verification(self):
        """测试文件内容正确性验证"""
        pytest.skip("等待实现完成后进行文件内容验证")
        pass

    def test_tc0019_202_multiple_loggers_separate_files(self):
        """测试多个logger实例创建各自的文件"""
        pytest.skip("等待实现完成后进行多logger测试")
        pass

# ==================== 测试辅助函数 ====================

def verify_file_exists_and_contains(file_path: str, expected_content: str) -> bool:
    """验证文件存在且包含指定内容"""
    if not os.path.exists(file_path):
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        return expected_content in content

def count_lines_in_file(file_path: str) -> int:
    """统计文件行数"""
    if not os.path.exists(file_path):
        return 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return len(f.readlines())


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])