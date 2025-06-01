# src/custom_logger/formatter.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import sys
import traceback
import inspect
from typing import Tuple, Optional
from .config import get_config


def get_caller_info() -> Tuple[str, int]:
    """获取调用者信息（文件名和行号）"""
    frame = None
    try:
        # 获取调用栈
        stack = inspect.stack()

        # 找到第一个不在custom_logger包内的调用者
        for frame_info in stack:
            filename = frame_info.filename
            if 'custom_logger' not in filename:
                # 提取文件名（不含路径和扩展名）
                basename = os.path.basename(filename)
                name_without_ext = os.path.splitext(basename)[0]

                # 限制为8个字符
                if len(name_without_ext) > 8:
                    module_name = name_without_ext[:8]
                else:
                    module_name = name_without_ext

                line_number = frame_info.lineno
                return module_name, line_number

        # 如果没找到，使用默认值
        return "unknown", 0

    except Exception:
        return "error", 0


def format_elapsed_time(start_time_iso: str, current_time: datetime) -> str:
    """格式化运行时长"""
    try:
        start_time_dt = datetime.fromisoformat(start_time_iso)
        elapsed = current_time - start_time_dt
        total_seconds = elapsed.total_seconds()

        hours, remainder = divmod(int(total_seconds), 3_600)
        minutes, seconds_int = divmod(remainder, 60)

        # 计算带小数的秒数
        fractional_seconds = total_seconds - (hours * 3_600 + minutes * 60)

        elapsed_str = f"{hours}:{minutes:02d}:{fractional_seconds:05.2f}"
        return elapsed_str

    except Exception:
        return "0:00:00.00"


def format_pid(pid: int) -> str:
    """格式化进程ID"""
    pid_str = f"{pid:>6}"
    return pid_str


def format_log_message(
        level_name: str,
        message: str,
        module_name: str,
        args: tuple,
        kwargs: dict
) -> str:
    """格式化日志消息内容"""
    try:
        if args or kwargs:
            formatted_message = message.format(*args, **kwargs)
        else:
            formatted_message = message
        return formatted_message
    except Exception as e:
        # 格式化失败时返回原始消息和错误信息
        error_msg = f"{message} [格式化错误: {e}]"
        if args:
            error_msg += f" args={args}"
        if kwargs:
            error_msg += f" kwargs={kwargs}"
        return error_msg


def create_log_line(
        level_name: str,
        message: str,
        module_name: str,
        args: tuple,
        kwargs: dict
) -> str:
    """创建完整的日志行"""
    from .config import get_root_config

    cfg = get_root_config()
    current_time = datetime.now()

    # 获取各个组件
    pid_str = format_pid(os.getpid())
    caller_module, line_number = get_caller_info()
    timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')

    # 获取第一次启动时间
    first_start_time = getattr(cfg, 'first_start_time', None)
    elapsed_str = format_elapsed_time(first_start_time, current_time)
    formatted_message = format_log_message(level_name, message, module_name, args, kwargs)

    # 组装日志行，新格式：[PID | 模块名 : 行号]，模块名8位左对齐，行号4位对齐，级别左对齐9字符
    log_line = f"[{pid_str} | {caller_module:<8} : {line_number:>4}] {timestamp} - {elapsed_str} - {level_name:<9} - {formatted_message}"

    return log_line


def get_exception_info() -> Optional[str]:
    """获取异常信息"""
    try:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_type is not None:
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            tb_str = ''.join(tb_lines)
            return tb_str
        return None
    except Exception:
        return None