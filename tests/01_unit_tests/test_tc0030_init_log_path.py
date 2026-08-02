# tests/01_unit_tests/test_tc0030_init_log_path.py

from __future__ import annotations

from datetime import datetime
import os
import pytest


class TestInitLogPath:
    """测试初始化成功后打印日志路径功能"""

    def test_tc0030_init_success_prints_log_path(self, capsys):
        """测试：初始化成功后自动打印日志路径"""
        # 清理之前的初始化状态
        import src.custom_logger.manager as manager_module

        manager_module._initialized = False

        # 创建临时配置
        class TempConfig:
            def __init__(self):
                self.paths = type(
                    "obj",
                    (object,),
                    {
                        "log_dir": "D:/Tony/Documents/invest2025/project/custom_logger/test_logs"
                    },
                )()
                self.first_start_time = datetime.now()
                self.logger = type("obj", (object,), {})()

        config = TempConfig()

        # 初始化logger系统
        from src.custom_logger import init_custom_logger_system

        init_custom_logger_system(config)

        # 捕获输出
        captured = capsys.readouterr()

        # 验证输出包含日志路径信息
        assert "日志系统初始化成功" in captured.out or "日志目录" in captured.out, (
            f"初始化成功后应打印日志路径信息，实际输出: {captured.out}"
        )

        # 清理
        manager_module.tear_down_custom_logger_system()
        manager_module._initialized = False

    def test_tc0031_init_prints_log_dir(self, capsys):
        """测试：打印信息包含日志目录"""
        # 清理之前的初始化状态
        import src.custom_logger.manager as manager_module

        manager_module._initialized = False

        test_log_dir = "D:/Tony/Documents/invest2025/project/custom_logger/test_logs"

        class TempConfig:
            def __init__(self):
                self.paths = type("obj", (object,), {"log_dir": test_log_dir})()
                self.first_start_time = datetime.now()
                self.logger = type("obj", (object,), {})()

        config = TempConfig()

        from src.custom_logger import init_custom_logger_system

        init_custom_logger_system(config)

        captured = capsys.readouterr()

        # 验证包含日志目录
        assert test_log_dir in captured.out, (
            f"打印信息应包含日志目录 {test_log_dir}，实际输出: {captured.out}"
        )

        # 清理
        manager_module.tear_down_custom_logger_system()
        manager_module._initialized = False

    def test_tc0032_init_prints_file_names(self, capsys):
        """测试：打印信息包含日志文件名"""
        # 清理之前的初始化状态
        import src.custom_logger.manager as manager_module

        manager_module._initialized = False

        class TempConfig:
            def __init__(self):
                self.paths = type(
                    "obj",
                    (object,),
                    {
                        "log_dir": "D:/Tony/Documents/invest2025/project/custom_logger/test_logs"
                    },
                )()
                self.first_start_time = datetime.now()
                self.logger = type("obj", (object,), {})()

        config = TempConfig()

        from src.custom_logger import init_custom_logger_system

        init_custom_logger_system(config)

        captured = capsys.readouterr()

        # 验证包含文件名
        assert "full.log" in captured.out or "warning.log" in captured.out, (
            f"打印信息应包含日志文件名，实际输出: {captured.out}"
        )

        # 清理
        manager_module.tear_down_custom_logger_system()
        manager_module._initialized = False

    @pytest.mark.parametrize(
        "log_dir",
        [
            "D:/Tony/Documents/invest2025/project/custom_logger/test_logs",
            "D:/Tony/Documents/invest2025/project/custom_logger/test_logs/",
            "D:/Tony/Documents/invest2025/project/custom_logger/test_logs\\",
            "D:/Tony/Documents/invest2025/project/custom_logger/test_logs/\\",
        ],
    )
    def test_s2_01_init_prints_single_trailing_separator_without_mutating_config(
        self, capsys, log_dir
    ):
        """Initialization displays one separator while preserving the configured path."""
        import src.custom_logger.manager as manager_module

        manager_module._initialized = False

        class TempConfig:
            def __init__(self):
                self.paths = type("obj", (object,), {"log_dir": log_dir})()
                self.first_start_time = datetime.now()
                self.logger = type("obj", (object,), {})()

        config = TempConfig()

        try:
            from src.custom_logger import init_custom_logger_system

            init_custom_logger_system(config)
            captured = capsys.readouterr()
            expected_display = str(log_dir).rstrip("/\\") + os.sep

            assert f"日志目录: {expected_display}" in captured.out
            assert not expected_display.endswith(("//", "\\\\"))
            assert config.paths.log_dir == log_dir
        finally:
            manager_module.tear_down_custom_logger_system()
            manager_module._initialized = False
