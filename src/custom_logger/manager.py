# src/custom_logger/manager.py
from __future__ import annotations

import atexit
import multiprocessing as mp
from typing import Optional, Any, Dict
from .config import init_config_from_object, get_config, set_config_path, get_root_config
from .writer import init_writer, shutdown_writer
from .queue_writer import init_queue_sender, init_queue_receiver, shutdown_queue_writer
from .logger import CustomLogger
from .types import parse_level_name

# 全局状态
_initialized = False
_queue_mode = False  # 标记是否为队列模式


def init_custom_logger_system(
    config_object: Any
) -> None:
    """初始化自定义日志系统（主程序模式）

    Args:
        config_object: 配置对象（必须），主程序传递config_manager的config对象或序列化的config对象
                      必须包含paths.log_dir和first_start_time属性
                      如果包含queue_info.log_queue，则启用队列模式
                      不再支持first_start_time参数，必须使用config.first_start_time
    
    Raises:
        ValueError: 如果config_object为None或缺少必要属性
    """
    global _initialized, _queue_mode

    if _initialized:
        return

    if config_object is None:
        raise ValueError("config_object不能为None，必须传入config_manager的config对象")
    
    # 验证必要属性
    # 检查paths.log_dir
    paths_obj = getattr(config_object, 'paths', None)
    if paths_obj is None:
        raise ValueError("config_object必须包含paths属性")
    
    if isinstance(paths_obj, dict):
        log_dir = paths_obj.get('log_dir')
    else:
        log_dir = getattr(paths_obj, 'log_dir', None)
    
    if log_dir is None:
        raise ValueError("config_object必须包含paths.log_dir属性")
    
    if not hasattr(config_object, 'first_start_time'):
        raise ValueError("config_object必须包含first_start_time属性")

    try:
        # 直接使用传入的config对象，不再调用config_manager
        init_config_from_object(config_object)

        # 检查是否启用队列模式
        queue_info = getattr(config_object, 'queue_info', None)
        if queue_info is not None:
            log_queue = None
            if isinstance(queue_info, dict):
                log_queue = queue_info.get('log_queue')
            else:
                log_queue = getattr(queue_info, 'log_queue', None)
            
            if log_queue is not None:
                # 启用队列模式：主程序作为日志接收器
                init_queue_receiver(log_queue, log_dir)
                _queue_mode = True
                print(f"主程序启用队列模式，日志接收器已初始化")
            else:
                # 普通模式：使用异步写入器
                init_writer()
                _queue_mode = False
        else:
            # 普通模式：使用异步写入器
            init_writer()
            _queue_mode = False

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


def init_custom_logger_system_for_worker(
    serializable_config_object: Any,
    worker_id: str = None
) -> None:
    """为worker进程初始化自定义日志系统
    
    这个函数专门用于worker进程，接收主程序传过来的包含队列信息的
    config_manager的config对象(序列化后的)。
    
    Worker进程：
    - 自己打印日志到控制台
    - 把需要存文件的信息传给队列
    - 主程序从队列读取并写入文件

    Args:
        serializable_config_object: 序列化的配置对象，包含paths.log_dir、first_start_time、
                                   以及队列信息等
        worker_id: worker进程ID，用于标识日志来源
    
    Raises:
        ValueError: 如果serializable_config_object为None或缺少必要属性
    """
    global _initialized, _queue_mode

    if _initialized:
        return

    if serializable_config_object is None:
        raise ValueError("serializable_config_object不能为None，必须传入序列化的config对象")
    
    # 验证必要属性
    # 检查paths.log_dir
    paths_obj = getattr(serializable_config_object, 'paths', None)
    if paths_obj is None:
        raise ValueError("serializable_config_object必须包含paths属性")
    
    if isinstance(paths_obj, dict):
        log_dir = paths_obj.get('log_dir')
    else:
        log_dir = getattr(paths_obj, 'log_dir', None)
    
    if log_dir is None:
        raise ValueError("serializable_config_object必须包含paths.log_dir属性")
    
    if not hasattr(serializable_config_object, 'first_start_time'):
        raise ValueError("serializable_config_object必须包含first_start_time属性")

    try:
        # 直接使用传入的序列化config对象，不再调用config_manager
        init_config_from_object(serializable_config_object)

        # 检查队列信息
        queue_info = getattr(serializable_config_object, 'queue_info', None)
        if queue_info is not None:
            log_queue = None
            if isinstance(queue_info, dict):
                log_queue = queue_info.get('log_queue')
            else:
                log_queue = getattr(queue_info, 'log_queue', None)
            
            if log_queue is not None:
                # Worker模式：初始化队列发送器
                init_queue_sender(log_queue, worker_id)
                _queue_mode = True
                print(f"Worker {worker_id}: 启用队列模式，日志发送器已初始化")
            else:
                # 如果没有队列，使用普通异步写入器
                init_writer()
                _queue_mode = False
                print(f"Worker {worker_id}: 使用普通写入模式")
        else:
            # 如果没有队列信息，使用普通异步写入器
            init_writer()
            _queue_mode = False
            print(f"Worker {worker_id}: 使用普通写入模式")

        # 注册退出时清理
        atexit.register(tear_down_custom_logger_system)

        _initialized = True

    except Exception as e:
        # 避免在测试环境中输出到可能已关闭的stderr
        try:
            import sys
            print(f"Worker日志系统初始化失败: {e}", file=sys.stderr)
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
    """获取指定名称的日志记录器

    Args:
        name: 日志记录器名称，不超过8个字符
        console_level: 控制台日志级别（可选，已废弃，保留用于兼容性）
        file_level: 文件日志级别（可选，已废弃，保留用于兼容性）

    Returns:
        CustomLogger: 自定义日志记录器实例

    Raises:
        RuntimeError: 如果日志系统未初始化
        ValueError: 如果name超过8个字符
    """
    global _initialized

    if not _initialized:
        raise RuntimeError("日志系统未初始化，请先调用 init_custom_logger_system() 或 init_custom_logger_system_for_worker()")

    if len(name) > 8:
        raise ValueError(f"日志记录器名称不能超过8个字符，当前长度: {len(name)}")

    # 获取配置
    config = get_config()

    # 创建并返回日志记录器
    # 注意：console_level和file_level参数已废弃，CustomLogger会从配置中获取级别
    return CustomLogger(name, config)


def tear_down_custom_logger_system() -> None:
    """清理自定义日志系统"""
    global _initialized, _queue_mode

    if not _initialized:
        return

    try:
        if _queue_mode:
            # 关闭队列写入器
            shutdown_queue_writer()
        else:
            # 关闭异步写入器
            shutdown_writer()
        
        _initialized = False
        _queue_mode = False
    except Exception as e:
        # 避免在测试环境中输出到可能已关闭的stderr
        try:
            import sys
            print(f"日志系统清理失败: {e}", file=sys.stderr)
        except (ValueError, AttributeError, ImportError):
            # 如果所有输出都失败，则静默处理
            pass

    return


def is_initialized() -> bool:
    """检查日志系统是否已初始化

    Returns:
        bool: 如果已初始化返回True，否则返回False
    """
    return _initialized


def is_queue_mode() -> bool:
    """检查是否为队列模式

    Returns:
        bool: 如果为队列模式返回True，否则返回False
    """
    return _queue_mode