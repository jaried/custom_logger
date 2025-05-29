# src/custom_logger/__init__.py

from .manager import (
    init_custom_logger_system,
    get_logger,
    tear_down_custom_logger_system,
    is_initialized,
)

from .logger import CustomLogger

from .types import (
    DEBUG, INFO, WARNING, ERROR, CRITICAL, EXCEPTION,
    DETAIL, W_SUMMARY, W_DETAIL,
    parse_level_name, get_level_name,
)

__all__ = [
    # 主要接口
    'init_custom_logger_system',
    'get_logger',
    'tear_down_custom_logger_system',
    'is_initialized',

    # 类
    'CustomLogger',

    # 常量和工具
    'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'EXCEPTION',
    'DETAIL', 'W_SUMMARY', 'W_DETAIL',
    'parse_level_name', 'get_level_name',
]