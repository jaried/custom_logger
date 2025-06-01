# src/custom_logger/manager.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import atexit
from typing import Optional
from .config import init_config, get_config
from .writer import init_writer, shutdown_writer
from .logger import CustomLogger
from .types import parse_level_name

# 全局状态
_initialized = False


def init_custom_logger_system(config_path: Optional[str] = None) -> None:
    """初始化自定义日志系统（仅主程序调用）

    Args:
        config_path: 配置文件路径（可选），如果不提供则使用默认路径
    """
    global _initialized

    if _initialized:
        return

    try:
        # 初始化配置，传递配置路径
        init_config(config_path)

        # 初始化异步写入器
        init_writer()

        # 注册退出时清理
        atexit.register(tear_down_custom_logger_system)

        _initialized = True

    except Exception as e:
        # 避免在测试环境中输出到可能已关闭的stderr
        try:
            import sys
            print(f"日志系统初始化失败: {e}", file=sys.stderr)
        except (ValueError, AttributeError, ImportError):
            # 如果所有输出都失败，则静默处理
            pass
        raise

    return


def get_logger(
        name: str,
        console_level: Optional[str] = None,
        file_level: Optional[str] = None
) -> CustomLogger:
    """获取logger实例

    Args:
        name: logger名称
        console_level: 控制台日志级别（可选）
        file_level: 文件日志级别（可选）

    Returns:
        CustomLogger实例
    """
    # 检查系统是否已初始化
    if not _initialized:
        try:
            get_config()  # 尝试获取配置，如果失败则未初始化
        except RuntimeError:
            # 如果未初始化，自动初始化（兼容性处理）
            init_custom_logger_system()

    # 解析级别参数
    console_level_value = None
    file_level_value = None

    if console_level is not None:
        console_level_value = parse_level_name(console_level)

    if file_level is not None:
        file_level_value = parse_level_name(file_level)

    # 创建logger实例
    logger = CustomLogger(name, console_level_value, file_level_value)
    return logger


def tear_down_custom_logger_system() -> None:
    """清理自定义日志系统"""
    global _initialized

    try:
        # 关闭异步写入器
        shutdown_writer()
    except Exception as e:
        # 避免在测试环境中输出到可能已关闭的stderr
        try:
            import sys
            print(f"日志系统清理失败: {e}", file=sys.stderr)
        except (ValueError, AttributeError, ImportError):
            # 如果所有输出都失败，则静默处理
            pass
    finally:
        # 无论如何都要重置状态
        _initialized = False

    return


def is_initialized() -> bool:
    """检查日志系统是否已初始化"""
    return _initialized