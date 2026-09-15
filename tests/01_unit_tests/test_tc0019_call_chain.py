# tests/01_unit_tests/test_tc0019_call_chain.py
from __future__ import annotations
from datetime import datetime

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from custom_logger import (
    init_custom_logger_system, 
    get_logger, 
    tear_down_custom_logger_system
)


class TestCallChainDisplay:
    """调用链显示功能测试"""

    def setup_method(self):
        """每个测试前的setup"""
        tear_down_custom_logger_system()

    def teardown_method(self):
        """每个测试后的cleanup"""
        tear_down_custom_logger_system()

    def create_test_config(self, show_call_chain: bool = False, show_debug_call_stack: bool = False):
        """创建测试配置对象"""
        class TestConfig:
            def __init__(self):
                self.first_start_time = datetime.now()
                self.paths = {'log_dir': tempfile.mkdtemp()}
                self.logger = TestLoggerConfig(show_call_chain, show_debug_call_stack)

        class TestLoggerConfig:
            def __init__(self, show_call_chain: bool, show_debug_call_stack: bool):
                self.global_console_level = "debug"
                self.global_file_level = "debug"
                self.show_call_chain = show_call_chain
                self.show_debug_call_stack = show_debug_call_stack
                self.module_levels = {}

        return TestConfig()

    def test_tc0019_01_basic_call_chain_enabled(self, capsys):
        """测试基本调用链显示开启"""
        config = self.create_test_config(show_call_chain=True)
        init_custom_logger_system(config)
        logger = get_logger("test_chain")
        logger.info("测试调用链显示")
        captured = capsys.readouterr()
        assert "[调用链]" in captured.out
        assert "test_tc0019_call_chain.py" in captured.out

    def test_tc0019_02_basic_call_chain_disabled(self, capsys):
        """测试基本调用链显示关闭"""
        config = self.create_test_config(show_call_chain=False)
        init_custom_logger_system(config)
        logger = get_logger("test_chain")
        logger.info("测试调用链显示")
        captured = capsys.readouterr()
        assert "[调用链]" not in captured.out

    def test_tc0019_03_debug_call_stack_in_test_env(self, capsys):
        """测试在测试环境中的调试调用链显示"""
        config = self.create_test_config(show_debug_call_stack=True)
        init_custom_logger_system(config)
        logger = get_logger("test_debug")
        logger.debug("测试调试调用链")
        captured = capsys.readouterr()
        assert "DEBUG: get_caller_info调用链:" in captured.out

    def test_tc0019_04_debug_call_stack_disabled(self, capsys):
        """测试调试调用链显示关闭"""
        config = self.create_test_config(show_debug_call_stack=False)
        init_custom_logger_system(config)
        logger = get_logger("test_debug")
        logger.debug("测试调试调用链")
        captured = capsys.readouterr()
        assert "DEBUG: get_caller_info调用链:" not in captured.out

    def test_tc0019_05_both_switches_enabled(self, capsys):
        """测试两个开关都开启"""
        config = self.create_test_config(show_call_chain=True, show_debug_call_stack=True)
        init_custom_logger_system(config)
        logger = get_logger("test_both")
        logger.info("测试两个开关都开启")
        captured = capsys.readouterr()
        assert "[调用链]" in captured.out
        assert "DEBUG: get_caller_info调用链:" in captured.out

    def test_tc0019_06_exception_call_chain(self, capsys):
        """测试异常情况下的调用链显示"""
        config = self.create_test_config(show_call_chain=True)
        init_custom_logger_system(config)

        with patch('custom_logger.formatter.inspect.currentframe') as mock_frame:
            mock_frame.side_effect = Exception("模拟异常")
            logger = get_logger("test_exc")
            logger.info("测试异常调用链")
            captured = capsys.readouterr()
            assert "[调用链异常]" in captured.out

    def test_tc0019_07_multilevel_call_chain_tracking(self, capsys):
        """测试多层调用的调用链跟踪"""
        def level3_function():
            """第三级函数"""
            logger = get_logger("level3")
            logger.info("第三级调用")

        def level2_function():
            """第二级函数"""
            level3_function()

        def level1_function():
            """第一级函数"""
            level2_function()

        config = self.create_test_config(show_call_chain=True)
        init_custom_logger_system(config)
        level1_function()
        captured = capsys.readouterr()
        assert "[调用链]" in captured.out
        call_chain_lines = [line for line in captured.out.split('\n') if '[调用链]' in line]
        assert len(call_chain_lines) > 0
        call_chain_content = ' '.join(call_chain_lines)
        assert "level3_function" in call_chain_content or "level2_function" in call_chain_content

    def test_tc0019_08_call_chain_format_validation(self, capsys):
        """测试调用链输出格式验证"""
        config = self.create_test_config(show_call_chain=True)
        init_custom_logger_system(config)
        logger = get_logger("format_test")
        logger.warning("测试格式")
        captured = capsys.readouterr()
        call_chain_lines = [line for line in captured.out.split('\n') if '[调用链]' in line]
        assert len(call_chain_lines) > 0
        call_chain_line = call_chain_lines[0]
        assert ".py:" in call_chain_line
        assert "(" in call_chain_line and ")" in call_chain_line
        assert " -> " in call_chain_line

    def test_tc0019_09_config_object_compatibility(self, capsys):
        """测试不同配置对象类型的兼容性"""
        dict_config = {
            'first_start_time': datetime.now(),
            'paths': {'log_dir': tempfile.mkdtemp()},
            'logger': {
                'global_console_level': "debug",
                'global_file_level': "debug", 
                'show_call_chain': True,
                'show_debug_call_stack': False,
                'module_levels': {}
            }
        }

        class DictConfig:
            def __init__(self, config_dict):
                for key, value in config_dict.items():
                    if isinstance(value, dict):
                        setattr(self, key, type('Config', (), value))
                    else:
                        setattr(self, key, value)

        config = DictConfig(dict_config)
        init_custom_logger_system(config)
        logger = get_logger("compat_test")
        logger.info("兼容性测试")
        captured = capsys.readouterr()
        assert "[调用链]" in captured.out

    def test_tc0019_10_concurrent_call_chain_safety(self, capsys):
        """测试并发环境下调用链的安全性"""
        import threading
        import time

        config = self.create_test_config(show_call_chain=True)
        init_custom_logger_system(config)
        results = []

        def worker_function(worker_id: int):
            """worker函数"""
            logger = get_logger(f"worker{worker_id}")
            for i in range(3):
                logger.info(f"Worker {worker_id} - 消息 {i}")
                time.sleep(0.01)

        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        captured = capsys.readouterr()
        call_chain_lines = [line for line in captured.out.split('\n') if '[调用链]' in line]
        assert len(call_chain_lines) >= 9
        call_chain_content = ' '.join(call_chain_lines)
        assert "worker_function" in call_chain_content


def run_call_chain_tests():
    """运行所有调用链测试"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_call_chain_tests()