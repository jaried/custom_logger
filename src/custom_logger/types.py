# src/custom_logger/types.py
from __future__ import annotations
from datetime import datetime
from typing import Dict

start_time = datetime.now()

# 日志级别常量定义
DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50
EXCEPTION = 60

# 扩展级别常量
DETAIL = 8
W_SUMMARY = 5
W_DETAIL = 3

# 级别名称到数值的映射
LEVEL_NAME_TO_VALUE: Dict[str, int] = {
    "debug": DEBUG,
    "info": INFO,
    "warning": WARNING,
    "error": ERROR,
    "critical": CRITICAL,
    "exception": EXCEPTION,
    "detail": DETAIL,
    "w_summary": W_SUMMARY,
    "w_detail": W_DETAIL,
}

# 数值到级别名称的映射
VALUE_TO_LEVEL_NAME: Dict[int, str] = {v: k for k, v in LEVEL_NAME_TO_VALUE.items()}


def parse_level_name(level_name: str) -> int:
    """解析级别名称为数值"""
    if not isinstance(level_name, str):
        raise ValueError(f"级别名称必须是字符串，得到: {type(level_name)}")

    name = level_name.strip().lower()
    if name not in LEVEL_NAME_TO_VALUE:
        valid_levels = ", ".join(LEVEL_NAME_TO_VALUE.keys())
        raise ValueError(f"无效的日志级别: {level_name}，有效级别: {valid_levels}")

    result = LEVEL_NAME_TO_VALUE[name]
    return result


def get_level_name(level_value: int) -> str:
    """获取级别数值对应的名称"""
    if level_value not in VALUE_TO_LEVEL_NAME:
        raise ValueError(f"无效的日志级别数值: {level_value}")

    result = VALUE_TO_LEVEL_NAME[level_value]
    return result