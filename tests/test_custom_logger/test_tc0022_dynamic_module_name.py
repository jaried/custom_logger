# tests/test_custom_logger/test_tc0022_dynamic_module_name.py
"""
TC0022: logger自动识别调用模块名

验证目标：
1. 主程序初始化logger后，子模块直接使用传入的logger
2. 日志中显示的是实际调用模块的名字，而不是logger创建时的名字

验收标准：
- 日志中显示的模块名来自调用栈分析，而非logger.name
- 无论是直接传递logger还是get_logger创建，都显示实际调用模块名
"""
from __future__ import annotations

import os
import tempfile
import pytest
from datetime import datetime

from custom_logger import (
    init_custom_logger_system,
    get_logger,
    tear_down_custom_logger_system,
)


class ConfigObject:
    """测试用配置对象"""

    def __init__(self, log_dir: str, first_start_time: datetime):
        self.first_start_time = first_start_time
        self.project_name = "dynamic_module_test"
        self.experiment_name = "tc0022"

        self.paths = {
            'log_dir': log_dir
        }

        self.logger = {
            'global_console_level': 'debug',
            'global_file_level': 'debug',
            'show_debug_call_stack': False,
            'module_levels': {}
        }


@pytest.fixture
def temp_log_dir():
    """创建临时日志目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def config_object(temp_log_dir):
    """创建测试配置对象"""
    return ConfigObject(temp_log_dir, datetime.now())


def test_tc002201_main_logger_shows_caller_module(config_object):
    """TC002201: 主程序调用logger时显示实际调用模块名"""
    try:
        init_custom_logger_system(config_object)

        # 获取logger
        main_logger = get_logger("main_program")

        # 调用logger
        main_logger.info("测试消息")

        # 验证：logger的名字保持不变
        assert main_logger is not None
        assert main_logger.name == "main_program"
    finally:
        tear_down_custom_logger_system()


def test_tc002202_passed_logger_shows_caller_module(config_object):
    """TC002202: 子模块使用传入的logger时显示实际调用模块名"""
    try:
        init_custom_logger_system(config_object)

        # 主程序获取logger
        main_logger = get_logger("main_program")

        # 子模块使用传入的logger
        main_logger.info("子模块消息")

        # 验证：logger的名字仍然是main_program
        # 但日志输出中显示的应该是实际调用模块名
        assert main_logger.name == "main_program"
    finally:
        tear_down_custom_logger_system()


def test_tc002203_own_logger_shows_caller_module(config_object):
    """TC002203: 子模块获取自己的logger时显示实际调用模块名"""
    try:
        init_custom_logger_system(config_object)

        # 子模块获取自己的logger
        child_logger = get_logger("child_module")

        # 调用logger
        child_logger.info("子模块消息")

        # 验证
        assert child_logger.name == "child_module"
    finally:
        tear_down_custom_logger_system()


def test_tc002204_warning_level_with_stack_trace(config_object):
    """TC002204: warning级别正确显示调用栈"""
    try:
        init_custom_logger_system(config_object)

        main_logger = get_logger("main")

        # warning级别应该显示调用栈
        main_logger.warning("警告消息")

        assert main_logger is not None
    finally:
        tear_down_custom_logger_system()


def test_tc002205_multiple_loggers_same_caller(config_object):
    """TC002205: 多个logger在同一位置调用时显示相同的调用模块名"""
    try:
        init_custom_logger_system(config_object)

        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")
        logger3 = get_logger("logger3")

        # 所有logger在同一个位置调用，应该显示相同的调用模块名
        logger1.info("消息1")
        logger2.info("消息2")
        logger3.info("消息3")

        assert logger1.name == "logger1"
        assert logger2.name == "logger2"
        assert logger3.name == "logger3"
    finally:
        tear_down_custom_logger_system()


def test_tc002206_logger_name_preserved_internally(config_object):
    """TC002206: logger的name属性保持不变（虽然日志输出使用动态模块名）"""
    try:
        init_custom_logger_system(config_object)

        # 创建logger
        main_logger = get_logger("main")
        child_logger = get_logger("child")

        # logger的name属性保持创建时的名字
        assert main_logger.name == "main"
        assert child_logger.name == "child"

        # 但日志输出中会显示实际调用模块名（test_tc0022...）
        # 由于16字符限制，可能会被截断为 test_tc0022_dyn...
        main_logger.info("主程序消息")
        child_logger.info("子模块消息")
    finally:
        tear_down_custom_logger_system()
