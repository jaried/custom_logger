# tests/test_custom_logger/test_tc0010_minimal_integration.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import pytest
from unittest.mock import patch, MagicMock


def test_tc0010_001_import_test():
    """测试模块导入"""
    try:
        from custom_logger import get_logger, CustomLogger
        from custom_logger.types import DEBUG, INFO, WARNING, ERROR
        from custom_logger.manager import is_initialized
        assert True  # 如果能导入就成功
    except ImportError as e:
        pytest.fail(f"导入失败: {e}")
    pass


def test_tc0010_002_basic_logger_creation():
    """测试基本logger创建"""
    from custom_logger.logger import CustomLogger

    logger = CustomLogger("test")
    assert logger.name == "test"
    assert logger._console_level is None
    assert logger._file_level is None
    pass


def test_tc0010_003_mock_logger_usage():
    """测试带mock的logger使用"""
    from custom_logger.logger import CustomLogger
    from custom_logger.types import INFO

    logger = CustomLogger("mock_test", console_level=INFO, file_level=INFO)

    # Mock配置
    mock_config = {
        "first_start_time": datetime.now().isoformat()
    }

    # Mock所有外部依赖
    with patch.object(logger, '_print_to_console') as mock_console:
        with patch('custom_logger.writer.write_log_async') as mock_file:
            with patch('custom_logger.config.get_root_config') as mock_get_root_config:
                mock_get_root_config.return_value = MagicMock(first_start_time=mock_config["first_start_time"])
                # 模拟_should_log方法返回True
                with patch.object(logger, '_should_log_console', return_value=True):
                    with patch.object(logger, '_should_log_file', return_value=True):
                        logger.info("Test message")

                        # 基本验证：方法被调用
                        assert mock_console.called or mock_file.called
    pass


def test_tc0010_004_types_constants():
    """测试类型常量"""
    from custom_logger.types import DEBUG, INFO, WARNING, ERROR, CRITICAL, EXCEPTION
    from custom_logger.types import DETAIL, W_SUMMARY, W_DETAIL

    # 验证常量值
    assert DEBUG == 10
    assert INFO == 20
    assert WARNING == 30
    assert ERROR == 40
    assert CRITICAL == 50
    assert EXCEPTION == 60
    assert DETAIL == 8
    assert W_SUMMARY == 5
    assert W_DETAIL == 3
    pass


def test_tc0010_005_manager_state():
    """测试管理器状态"""
    from custom_logger.manager import is_initialized, _initialized

    # 测试状态检查函数
    result = is_initialized()
    assert isinstance(result, bool)

    # 状态应该与内部变量一致
    assert result == _initialized
    pass