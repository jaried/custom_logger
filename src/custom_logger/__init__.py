# src/custom_logger/__init__.py

"""
Custom Logger 模块

提供自定义日志功能，支持多进程环境和配置管理。
"""
from __future__ import annotations

from .manager import (
    init_custom_logger_system,
    init_custom_logger_system_for_worker,
    get_logger,
    tear_down_custom_logger_system,
    is_initialized,
    is_queue_mode
)

from .logger import CustomLogger

from .types import (
    DEBUG, INFO, WARNING, ERROR, CRITICAL, EXCEPTION,
    DETAIL, W_SUMMARY, W_DETAIL
)

__all__ = [
    # 初始化函数
    'init_custom_logger_system',
    'init_custom_logger_system_for_worker',
    
    # 日志器获取
    'get_logger',
    'CustomLogger',
    
    # 系统管理
    'tear_down_custom_logger_system',
    'is_initialized',
    'is_queue_mode',
    
    # 日志级别常量
    'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'EXCEPTION',
    'DETAIL', 'W_SUMMARY', 'W_DETAIL'
]