# tests/01_unit_tests/test_tc0023_warning_stack_trace.py
"""
OPT-001: 统一warning及以上级别记录调用栈

测试目标：验证warning及以上级别的日志都能记录调用栈
"""
from __future__ import annotations

from datetime import datetime
import tempfile
from unittest.mock import patch

from custom_logger import (
    init_custom_logger_system,
    get_logger,
    tear_down_custom_logger_system,
)

start_time = datetime.now()


class TestWarningStackTrace:
    """测试warning及以上级别记录调用栈"""

    def setup_method(self) -> None:
        """每个测试前的setup"""
        tear_down_custom_logger_system()
        return

    def teardown_method(self) -> None:
        """每个测试后的cleanup"""
        tear_down_custom_logger_system()
        return

    def create_test_config(self) -> object:
        """创建测试配置对象"""

        class TestLoggerConfig:
            def __init__(self) -> None:
                self.global_console_level = "debug"
                self.global_file_level = "debug"
                self.show_call_chain = False
                self.show_debug_call_stack = False
                self.module_levels = {}
                return

        class TestConfig:
            def __init__(self) -> None:
                self.first_start_time = datetime.now()
                self.paths = {"log_dir": tempfile.mkdtemp()}
                self.logger = TestLoggerConfig()
                return

        return TestConfig()

    def test_tc0023_01_warning_should_get_call_stack(self) -> None:
        """验证warning级别应该调用get_call_stack（OPT-001更新）"""
        config = self.create_test_config()
        init_custom_logger_system(config)

        with patch(
            "custom_logger.logger.get_call_stack"
        ) as mock_get_call_stack:
            mock_get_call_stack.return_value = "mock call stack"

            logger = get_logger("test_warn")
            logger.warning("test warning message")

            mock_get_call_stack.assert_called_once()
        return

    def test_tc0023_02_error_should_get_exception_info(self) -> None:
        """验证error级别应该调用get_exception_info（回归测试）"""
        config = self.create_test_config()
        init_custom_logger_system(config)

        with patch(
            "custom_logger.logger.get_exception_info"
        ) as mock_get_exception_info:
            mock_get_exception_info.return_value = "mock stack trace"

            logger = get_logger("test_error")
            logger.error("test error message")

            mock_get_exception_info.assert_called_once()
        return

    def test_tc0023_03_critical_should_get_exception_info(self) -> None:
        """验证critical级别应该调用get_exception_info（回归测试）"""
        config = self.create_test_config()
        init_custom_logger_system(config)

        with patch(
            "custom_logger.logger.get_exception_info"
        ) as mock_get_exception_info:
            mock_get_exception_info.return_value = "mock stack trace"

            logger = get_logger("test_crit")
            logger.critical("test critical message")

            mock_get_exception_info.assert_called_once()
        return

    def test_tc0023_04_exception_should_get_exception_info(self) -> None:
        """验证exception级别应该调用get_exception_info（回归测试）"""
        config = self.create_test_config()
        init_custom_logger_system(config)

        with patch(
            "custom_logger.logger.get_exception_info"
        ) as mock_get_exception_info:
            mock_get_exception_info.return_value = "mock stack trace"

            logger = get_logger("test_exc")
            logger.exception("test exception message")

            mock_get_exception_info.assert_called_once()
        return

    def test_tc0023_05_info_should_not_get_exception_info(self) -> None:
        """验证info级别不应该调用get_exception_info"""
        config = self.create_test_config()
        init_custom_logger_system(config)

        with patch(
            "custom_logger.logger.get_exception_info"
        ) as mock_get_exception_info:
            logger = get_logger("test_info")
            logger.info("test info message")

            mock_get_exception_info.assert_not_called()
        return

    def test_tc0023_06_debug_should_not_get_exception_info(self) -> None:
        """验证debug级别不应该调用get_exception_info"""
        config = self.create_test_config()
        init_custom_logger_system(config)

        with patch(
            "custom_logger.logger.get_exception_info"
        ) as mock_get_exception_info:
            logger = get_logger("test_debug")
            logger.debug("test debug message")

            mock_get_exception_info.assert_not_called()
        return
