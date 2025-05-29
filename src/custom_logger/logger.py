# src/custom_logger/logger.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import sys
import os
from typing import Optional, Any
from .types import (
    DEBUG, INFO, WARNING, ERROR, CRITICAL, EXCEPTION,
    DETAIL, W_SUMMARY, W_DETAIL, get_level_name
)
from .config import get_console_level, get_file_level
from .formatter import create_log_line, get_exception_info
from .writer import write_log_async


# Windows CMD颜色支持
def _enable_windows_ansi_support() -> bool:
    """启用Windows ANSI颜色支持"""
    if os.name != 'nt':
        return True  # 非Windows系统直接返回True

    try:
        import ctypes
        from ctypes import wintypes

        # 获取stdout句柄
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE

        # 获取当前控制台模式
        mode = wintypes.DWORD()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False

        # 启用ANSI处理 (ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004)
        new_mode = mode.value | 0x0004
        if not kernel32.SetConsoleMode(handle, new_mode):
            return False

        return True
    except Exception:
        return False


def _detect_terminal_type() -> str:
    """检测终端类型"""
    # 检测PyCharm
    if 'PYCHARM_HOSTED' in os.environ or 'PYCHARM_MATPLOTLIB_BACKEND' in os.environ:
        return 'pycharm'

    # 检测VS Code
    if 'VSCODE_PID' in os.environ or 'TERM_PROGRAM' in os.environ and os.environ['TERM_PROGRAM'] == 'vscode':
        return 'vscode'

    # 检测其他IDE
    if any(ide in os.environ.get('PATH', '').lower() for ide in ['pycharm', 'vscode', 'code']):
        return 'ide'

    # Windows CMD
    if os.name == 'nt' and os.environ.get('TERM') != 'xterm':
        return 'cmd'

    # Unix终端
    return 'terminal'


# 颜色代码类
class Colors:
    RED = '\033[31m'
    YELLOW = '\033[33m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'
    BRIGHT_RED = '\033[91m'

    # PyCharm专用颜色（更鲜艳但不刺眼）
    PYCHARM_YELLOW = '\033[93m'
    PYCHARM_RED = '\033[91m'
    PYCHARM_MAGENTA = '\033[95m'
    PYCHARM_BRIGHT_RED = '\033[1;31m'  # 粗体红色，不用背景色


# 检测终端类型和颜色支持
_TERMINAL_TYPE = _detect_terminal_type()
_COLOR_SUPPORT = _enable_windows_ansi_support() if _TERMINAL_TYPE == 'cmd' else True


# 根据终端类型选择颜色方案
def _get_level_colors():
    """根据终端类型获取级别颜色映射"""
    if _TERMINAL_TYPE == 'pycharm':
        return {
            WARNING: Colors.PYCHARM_YELLOW,
            ERROR: Colors.PYCHARM_RED,
            CRITICAL: Colors.PYCHARM_MAGENTA,
            EXCEPTION: Colors.PYCHARM_BRIGHT_RED,
        }
    else:
        return {
            WARNING: Colors.YELLOW,
            ERROR: Colors.RED,
            CRITICAL: Colors.MAGENTA,
            EXCEPTION: Colors.BRIGHT_RED,
        }


# 级别对应的颜色
LEVEL_COLORS = _get_level_colors()


class CustomLogger:
    """自定义日志器"""

    def __init__(self, name: str, console_level: Optional[int] = None, file_level: Optional[int] = None):
        self.name = name
        self._console_level = console_level
        self._file_level = file_level
        pass

    @property
    def console_level(self) -> int:
        """获取控制台日志级别"""
        if self._console_level is not None:
            return self._console_level

        level = get_console_level(self.name)
        return level

    @property
    def file_level(self) -> int:
        """获取文件日志级别"""
        if self._file_level is not None:
            return self._file_level

        level = get_file_level(self.name)
        return level

    def _should_log_console(self, level_value: int) -> bool:
        """判断是否应该输出到控制台"""
        result = level_value >= self.console_level
        return result

    def _should_log_file(self, level_value: int) -> bool:
        """判断是否应该输出到文件"""
        result = level_value >= self.file_level
        return result

    def _print_to_console(self, log_line: str, level_value: int) -> None:
        """输出到控制台"""
        try:
            # 选择输出流
            if level_value >= WARNING:
                output_stream = sys.stderr
            else:
                output_stream = sys.stdout

            # 添加颜色（如果支持）
            if _COLOR_SUPPORT and level_value in LEVEL_COLORS:
                colored_line = f"{LEVEL_COLORS[level_value]}{log_line}{Colors.RESET}"
            else:
                colored_line = log_line

            print(colored_line, file=output_stream, flush=True)

        except Exception as e:
            # 如果主要的print失败，尝试备用输出方式
            try:
                backup_message = f"控制台输出失败: {e}"
                print(backup_message, file=sys.stderr)
            except Exception:
                # 如果连备用输出都失败，则静默忽略
                pass

        return

    def _log(
            self,
            level_value: int,
            message: str,
            *args: Any,
            do_print: bool = True,
            **kwargs: Any
    ) -> None:
        """底层日志方法"""
        # 早期过滤：如果都不需要输出，直接返回
        should_console = do_print and self._should_log_console(level_value)
        should_file = self._should_log_file(level_value)

        if not should_console and not should_file:
            return

        try:
            level_name = get_level_name(level_value)
        except ValueError:
            level_name = f"LEVEL_{level_value}"

        # 创建日志行
        log_line = create_log_line(level_name, message, self.name, args, kwargs)

        # 获取异常信息（如果是exception级别）
        exception_info = None
        if level_value == EXCEPTION:
            exception_info = get_exception_info()

        # 控制台输出
        if should_console:
            self._print_to_console(log_line, level_value)
            if exception_info:
                try:
                    print(exception_info, file=sys.stderr)
                except Exception:
                    pass

        # 文件输出
        if should_file:
            write_log_async(log_line, level_value, exception_info)

        return

    # 标准级别方法
    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """调试级别日志"""
        self._log(DEBUG, message, *args, **kwargs)
        return

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """信息级别日志"""
        self._log(INFO, message, *args, **kwargs)
        return

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """警告级别日志"""
        self._log(WARNING, message, *args, **kwargs)
        return

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """错误级别日志"""
        self._log(ERROR, message, *args, **kwargs)
        return

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """严重错误级别日志"""
        self._log(CRITICAL, message, *args, **kwargs)
        return

    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        """异常级别日志"""
        self._log(EXCEPTION, message, *args, **kwargs)
        return

    # 扩展级别方法
    def detail(self, message: str, *args: Any, **kwargs: Any) -> None:
        """详细调试级别日志"""
        self._log(DETAIL, message, *args, **kwargs)
        return

    def worker_summary(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Worker摘要级别日志"""
        self._log(W_SUMMARY, message, *args, **kwargs)
        return

    def worker_detail(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Worker详细级别日志"""
        self._log(W_DETAIL, message, *args, **kwargs)
        return