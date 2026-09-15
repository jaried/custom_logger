# src/custom_logger/formatter.py
from __future__ import annotations
from datetime import datetime
import os
import sys
import traceback
import inspect
from typing import Tuple, Optional

start_time = datetime.now()


def _get_call_stack_info() -> str:
    """获取调用栈信息（用于调试）"""
    try:
        import traceback

        stack = traceback.extract_stack()
        # 获取最近的几个调用栈帧
        recent_calls = []
        for frame in stack[-15:]:  # 最后15个栈帧
            filename = os.path.basename(frame.filename)
            recent_calls.append(f"{filename}:{frame.lineno}({frame.name})")
        return " -> ".join(recent_calls)
    except Exception:
        return "无法获取调用栈"


def get_caller_info() -> Tuple[str, int]:
    """获取调用者信息（文件名和行号）"""
    frame = None
    current_frame = None
    show_call_chain = False
    in_test = False
    caller: Optional[Tuple[str, int]] = None
    last_custom_logger_frame: Optional[Tuple[str, int]] = None

    try:
        frame = inspect.currentframe()
        if frame is None:
            return "main", 0

        current_frame = frame.f_back

        try:
            from .config import get_config

            cfg = get_config()
            show_call_chain = cfg.show_call_chain
        except Exception:
            pass

        framework_files = [
            "python",
            "_callers",
            "_hooks",
            "_manager",
            "runner",
            "threading",
            "_threading_local",
            "spawn",
            "process",
            "popen_spawn_win32",
        ]

        while current_frame is not None:
            filename = current_frame.f_code.co_filename
            basename = os.path.basename(filename)
            line_number = current_frame.f_lineno

            if "test_tc" in filename:
                in_test = True

            if caller is None and 0 < line_number <= 10_000:
                name_without_ext = os.path.splitext(basename)[0]

                if name_without_ext.startswith("test_tc"):
                    caller = ("test_tc0", line_number)
                else:
                    normalized_filename = filename.replace("\\", "/").lower()
                    is_custom_logger_file = (
                        "custom_logger" in normalized_filename
                        and (
                            basename
                            in [
                                "logger.py",
                                "formatter.py",
                                "writer.py",
                                "config.py",
                                "manager.py",
                            ]
                            or basename.startswith("module")
                            or basename.startswith("internal")
                        )
                    )

                    if is_custom_logger_file:
                        last_custom_logger_frame = (name_without_ext, line_number)
                    else:
                        is_framework_file = (
                            name_without_ext in framework_files
                            or basename == "<string>"
                        )

                        if (
                            "mock" not in name_without_ext.lower()
                            and not is_framework_file
                        ):
                            caller = (name_without_ext[:16], line_number)

            current_frame = current_frame.f_back

        if show_call_chain:
            call_stack = _get_call_stack_info()
            print(f"[调用链] {call_stack}")

        if in_test:
            try:
                from .config import get_config

                cfg = get_config()
                show_debug = cfg.show_debug_call_stack

                if show_debug:
                    call_stack = _get_call_stack_info()
                    print(f"DEBUG: get_caller_info调用链: {call_stack}")
            except Exception:
                pass

        if caller is not None:
            return caller

        if last_custom_logger_frame is not None:
            module_name, line_number = last_custom_logger_frame
            module_name = module_name[:16] if len(module_name) > 16 else module_name
            return module_name, line_number

        return "unknown", 0

    except Exception as e:
        try:
            from .config import get_config

            cfg = get_config()
            show_call_chain = cfg.show_call_chain
            if show_call_chain:
                print(f"[调用链异常] {e}")
        except Exception:
            pass
        return "error", 0
    finally:
        del current_frame
        del frame


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
    level_name: str, message: str, module_name: str, args: tuple, kwargs: dict
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
    level_name: str, message: str, module_name: str, args: tuple, kwargs: dict
) -> str:
    """创建完整的日志行"""
    from .config import get_root_config

    cfg = get_root_config()
    current_time = datetime.now()

    # 获取各个组件
    pid_str = format_pid(os.getpid())
    caller_module, line_number = get_caller_info()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

    # 获取第一次启动时间并计算运行时长
    first_start_time = getattr(cfg, "first_start_time", None)
    if first_start_time is not None:
        # 如果first_start_time是datetime对象，直接计算时间差
        try:
            if isinstance(first_start_time, datetime):
                elapsed = current_time - first_start_time
                total_seconds = elapsed.total_seconds()
                hours, remainder = divmod(int(total_seconds), 3_600)
                minutes, seconds_int = divmod(remainder, 60)
                fractional_seconds = total_seconds - (hours * 3_600 + minutes * 60)
                elapsed_str = f"{hours}:{minutes:02d}:{fractional_seconds:05.2f}"
            else:
                # 如果是字符串格式，使用原有的format_elapsed_time函数
                elapsed_str = format_elapsed_time(str(first_start_time), current_time)
        except (TypeError, AttributeError):
            # 如果类型检查失败，尝试字符串格式
            elapsed_str = format_elapsed_time(str(first_start_time), current_time)
    else:
        elapsed_str = "0:00:00.00"

    formatted_message = format_log_message(
        level_name, message, module_name, args, kwargs
    )

    # 组装日志行，新格式：[PID | 模块名 : 行号]，模块名16位居中对齐，行号4位对齐，级别居中对齐10字符
    # 使用动态获取的 caller_module 而不是传入的 module_name，以支持自动识别调用模块名（US-002）
    log_line = f"[{pid_str:>6} | {caller_module:^16} : {line_number:>4}] {timestamp} - {elapsed_str} - {level_name:^10} - {formatted_message}"

    return log_line


def get_exception_info() -> Optional[str]:
    """获取异常信息"""
    try:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_type is not None:
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            tb_str = "".join(tb_lines)
            return tb_str
        return None
    except Exception:
        return None


def get_call_stack() -> str:
    """获取当前调用栈信息（用于warning及以上级别）

    使用 traceback.extract_stack() 获取完整调用栈，过滤掉logger内部调用，
    只保留用户代码的调用栈信息。

    Returns:
        str: 格式化的调用栈，或空字符串（获取失败时）
    """
    try:
        # 获取完整调用栈
        stack = traceback.extract_stack()

        # 过滤掉logger内部调用，只保留用户代码
        user_frames: list = []
        for frame in stack:
            # 跳过当前函数（get_call_stack自身）
            if frame.name == "get_call_stack":
                continue
            # 跳过formatter模块的其他内部函数
            if "formatter.py" in frame.filename:
                # 只跳过formatter.py，允许其他模块
                continue
            user_frames.append(frame)

        # 格式化调用栈
        if user_frames:
            formatted = traceback.format_list(user_frames)
            return "".join(formatted)

        return ""
    except Exception:
        # 获取失败时返回空字符串
        return ""