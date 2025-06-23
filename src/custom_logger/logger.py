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


def _check_registry_ansi_support() -> bool:
    """检查注册表中的ANSI支持设置"""
    if os.name != 'nt':
        return True

    try:
        import winreg

        # 检查当前用户的控制台设置
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Console")
            value, _ = winreg.QueryValueEx(key, "VirtualTerminalLevel")
            winreg.CloseKey(key)
            return value == 1
        except FileNotFoundError:
            return False
        except Exception:
            return False
    except ImportError:
        return False


def _enable_registry_ansi_support() -> bool:
    """启用注册表中的ANSI支持设置"""
    if os.name != 'nt':
        return True

    try:
        import winreg

        # 打开或创建Console键
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Console")
            winreg.SetValueEx(key, "VirtualTerminalLevel", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            return True
        except Exception:
            return False
    except ImportError:
        return False


# Windows CMD颜色支持
def _enable_windows_ansi_support() -> bool:
    """启用Windows ANSI颜色支持"""
    if os.name != 'nt':
        return True  # 非Windows系统直接返回True

    # 首先检查注册表设置
    registry_support = _check_registry_ansi_support()
    registry_was_enabled = False

    # 如果注册表未启用，尝试启用
    if not registry_support:
        registry_was_enabled = _enable_registry_ansi_support()
        if registry_was_enabled:
            registry_support = True

    try:
        import ctypes
        from ctypes import wintypes

        # 获取stdout和stderr句柄
        kernel32 = ctypes.windll.kernel32
        stdout_handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        stderr_handle = kernel32.GetStdHandle(-12)  # STD_ERROR_HANDLE

        success = False

        # 启用stdout的ANSI处理
        try:
            stdout_mode = wintypes.DWORD()
            if kernel32.GetConsoleMode(stdout_handle, ctypes.byref(stdout_mode)):
                new_stdout_mode = stdout_mode.value | 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
                if kernel32.SetConsoleMode(stdout_handle, new_stdout_mode):
                    success = True
        except Exception:
            pass

        # 启用stderr的ANSI处理
        try:
            stderr_mode = wintypes.DWORD()
            if kernel32.GetConsoleMode(stderr_handle, ctypes.byref(stderr_mode)):
                new_stderr_mode = stderr_mode.value | 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
                if kernel32.SetConsoleMode(stderr_handle, new_stderr_mode):
                    success = True
        except Exception:
            pass

        # 根据不同情况输出不同的提示信息
        if not success:
            try:
                if registry_was_enabled:
                    # 刚刚启用了注册表，提示重启CMD
                    print("\n[提示] ANSI颜色支持已启用，请重新打开CMD窗口以查看彩色日志。\n", file=sys.stderr)
                elif not registry_support:
                    # 注册表启用失败，提示手动操作
                    print("\n[提示] 无法自动启用CMD颜色支持，请手动在CMD中运行以下命令：", file=sys.stderr)
                    print("reg add HKCU\\Console /v VirtualTerminalLevel /t REG_DWORD /d 1", file=sys.stderr)
                    print("然后重新打开CMD窗口。\n", file=sys.stderr)
                else:
                    # 注册表已设置但API调用失败
                    print("\n[提示] 注册表已配置ANSI支持但当前CMD不支持，请重新打开CMD窗口。\n", file=sys.stderr)
            except Exception:
                pass
        else:
            # API调用成功，但如果刚刚设置了注册表，仍然建议重启以获得更好的支持
            if registry_was_enabled:
                try:
                    print("\n[提示] ANSI颜色支持已启用并生效，重新打开CMD窗口可获得更好的颜色支持。\n", file=sys.stderr)
                except Exception:
                    pass

        # 如果注册表支持或API调用成功，都认为支持颜色
        return success or registry_support
    except Exception:
        return registry_support


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

# 存储ANSI设置提示信息
_ANSI_SETUP_MESSAGE = None


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

    def __init__(self, name: str, config: Optional[Any] = None, console_level: Optional[int] = None, file_level: Optional[int] = None):
        self.name = name
        self.config = config
        self._console_level = console_level
        self._file_level = file_level

        # 如果有ANSI设置提示信息，输出一次
        global _ANSI_SETUP_MESSAGE
        if _ANSI_SETUP_MESSAGE and not hasattr(CustomLogger, '_ansi_message_shown'):
            CustomLogger._ansi_message_shown = True
            # 使用info级别输出提示信息，不添加颜色
            try:
                message = f"[提示] {_ANSI_SETUP_MESSAGE}"
                print(message, file=sys.stderr)
            except Exception:
                pass
        pass

    @property
    def console_level(self) -> int:
        """获取控制台日志级别"""
        # 优先使用构造函数传入的级别（通过get_logger参数设置）
        if self._console_level is not None:
            return self._console_level
        
        # 否则使用全局配置
        level = get_console_level(self.name)
        return level

    @property
    def file_level(self) -> int:
        """获取文件日志级别"""
        # 优先使用构造函数传入的级别（通过get_logger参数设置）
        if self._file_level is not None:
            return self._file_level
        
        # 否则使用全局配置
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

    def _print_to_console(self, log_line: str, level_value: int, countdown: bool = False) -> None:
        """输出到控制台"""
        try:
            # 选择输出流
            if level_value >= WARNING:
                output_stream = sys.stderr
            else:
                output_stream = sys.stdout

            # 只有在颜色支持确实可用时才添加颜色
            if _COLOR_SUPPORT and level_value in LEVEL_COLORS:
                colored_line = f"{LEVEL_COLORS[level_value]}{log_line}{Colors.RESET}"
            else:
                # 如果不支持颜色或该级别没有颜色配置，直接输出原始日志
                colored_line = log_line

            if countdown:
                # 倒计时模式：使用\r在原位更新，不换行
                output_stream.write(f"\r{colored_line}")
                output_stream.flush()
            else:
                # 正常模式：换行输出
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
            countdown: bool = False,
            **kwargs: Any
    ) -> None:
        """底层日志方法
        
        Args:
            level_value: 日志级别数值
            message: 日志消息
            *args: 格式化参数
            do_print: 是否输出到控制台
            countdown: 是否为倒计时模式（使用\r在原位更新，不换行）
            **kwargs: 其他关键字参数
        """
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
            self._print_to_console(log_line, level_value, countdown)
            if exception_info:
                try:
                    # 异常信息也添加颜色（如果该级别有颜色）
                    if _COLOR_SUPPORT and level_value in LEVEL_COLORS:
                        colored_exception = f"{LEVEL_COLORS[level_value]}{exception_info}{Colors.RESET}"
                        print(colored_exception, file=sys.stderr)
                    else:
                        print(exception_info, file=sys.stderr)
                except Exception:
                    pass

        # 文件输出：根据模式选择不同的写入方式
        if should_file:
            # 倒计时模式下不写入文件，避免产生大量重复日志
            if not countdown:
                # 检查是否为队列模式
                try:
                    from .manager import is_queue_mode
                    if is_queue_mode():
                        # 队列模式：发送到队列
                        from .queue_writer import send_log_to_queue
                        send_log_to_queue(log_line, level_value, exception_info)
                    else:
                        # 普通模式：使用异步写入器
                        write_log_async(log_line, level_value, exception_info)
                except ImportError:
                    # 如果导入失败，回退到普通模式
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

    # 倒计时专用方法
    def countdown_info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """倒计时信息级别日志（使用\\r在原位更新，不换行）"""
        self._log(INFO, message, *args, countdown=True, **kwargs)
        return

    def countdown_end(self, final_message: str = None) -> None:
        """结束倒计时，输出换行符和可选的完成信息
        
        Args:
            final_message: 可选的完成信息，如果提供则会在结束倒计时后立即输出
        """
        try:
            if final_message:
                # 清除当前行并输出完成信息
                print(f"\r{' ' * 100}\r", end='')  # 清除当前行
                self.info(final_message)
            else:
                print()  # 输出换行符，结束倒计时行
                sys.stdout.flush()  # 确保立即输出
        except Exception:
            pass
        return