# src/custom_logger/manager.py
from __future__ import annotations
from datetime import datetime

import atexit
from typing import Optional, Any
from .config import init_config, get_config, set_config_path
from .writer import init_writer, shutdown_writer
from .logger import CustomLogger
from .types import parse_level_name

# 全局状态
_initialized = False


def init_custom_logger_system(
    config_path: Optional[str] = None,
    first_start_time: Optional[datetime] = None,
    config_object: Optional[Any] = None
) -> None:
    """初始化自定义日志系统

    Args:
        config_path: 配置文件路径（可选），如果不提供则使用默认路径 src/config/config.yaml
        first_start_time: 首次启动时间（可选），主程序可以设置，其他程序从配置文件读取
        config_object: 配置对象（可选），主程序可以直接传递config对象给worker
    """
    global _initialized

    if _initialized:
        return

    try:
        # 初始化配置，传递配置路径、启动时间和配置对象
        init_config(config_path, first_start_time, config_object)

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
    
    try:
        # 清理config_manager缓存
        from config_manager import _managers
        _managers.clear()
    except (ImportError, AttributeError, KeyError):
        pass
    
    try:
        # 清理配置路径缓存
        set_config_path(None)
    except Exception:
        pass
    
    finally:
        # 无论如何都要重置状态
        _initialized = False

    return


def is_initialized() -> bool:
    """检查日志系统是否已初始化"""
    return _initialized