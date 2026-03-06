# src/custom_logger/log_cleaner.py
"""
日志过期清理模块

根据配置的保留天数，自动删除过期的日志目录。
目录名格式为 yyyymmdd，超过保留天数的整个目录将被删除。
"""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from typing import Any, Optional, Tuple, List


# 全局标记：确保清理只执行一次
_cleanup_done: bool = False


def parse_directory_date(dir_name: str) -> Optional[datetime]:
    """解析目录名为日期对象

    Args:
        dir_name: yyyymmdd格式的目录名

    Returns:
        Optional[datetime]: 解析成功返回日期对象，失败返回None
    """
    # 检查是否为8位数字
    if not dir_name or len(dir_name) != 8 or not dir_name.isdigit():
        return None

    try:
        return datetime.strptime(dir_name, "%Y%m%d")
    except ValueError:
        # 无效日期（如20260230）
        return None


def is_expired(dir_date: datetime, retention_days: int) -> bool:
    """判断目录是否过期

    Args:
        dir_date: 目录日期
        retention_days: 保留天数

    Returns:
        bool: True表示过期
    """
    if retention_days < 0:
        return True

    today = datetime.now().date()
    dir_day = dir_date.date()
    days_diff = (today - dir_day).days

    return days_diff > retention_days


def get_retention_days(config: Any) -> int:
    """获取日志保留天数

    Args:
        config: 配置对象

    Returns:
        int: 保留天数

    Raises:
        ValueError: 如果config为None
    """
    if config is None:
        raise ValueError("config不能为None")

    logger_obj = getattr(config, "logger", None)
    if logger_obj is None:
        return 7

    if isinstance(logger_obj, dict):
        return logger_obj.get("log_retention_days", 7)

    value = getattr(logger_obj, "log_retention_days", 7)
    return value if value is not None else 7


def _ensure_retention_config(config: Any) -> int:
    """确保配置中存在log_retention_days项

    Args:
        config: 配置对象

    Returns:
        int: 保留天数
    """
    logger_obj = getattr(config, "logger", None)
    if logger_obj is None:
        # 创建logger配置
        if isinstance(config, dict):
            config["logger"] = {"log_retention_days": 7}
        else:
            config.logger = {"log_retention_days": 7}
        return 7

    if isinstance(logger_obj, dict):
        if "log_retention_days" not in logger_obj:
            logger_obj["log_retention_days"] = 7
        return logger_obj["log_retention_days"]
    else:
        value = getattr(logger_obj, "log_retention_days", None)
        if value is None:
            setattr(logger_obj, "log_retention_days", 7)
            return 7
        return value


def _calculate_directory_size(dir_path: str) -> int:
    """计算目录大小（字节）

    Args:
        dir_path: 目录路径

    Returns:
        int: 目录大小（字节）
    """
    total_size: int = 0
    try:
        for item in os.walk(dir_path):
            for file in item[2]:
                file_path = os.path.join(item[0], file)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
    except (OSError, PermissionError):
        pass
    return total_size


def scan_log_directories(log_dir: str) -> List[Tuple[str, datetime]]:
    """扫描日志目录，返回有效日期目录列表

    Args:
        log_dir: 日志根目录路径

    Returns:
        List[Tuple[str, datetime]]: (目录路径, 日期) 列表
    """
    if not os.path.exists(log_dir):
        return []

    result: List[Tuple[str, datetime]] = []
    try:
        for item in os.listdir(log_dir):
            item_path = os.path.join(log_dir, item)
            if not os.path.isdir(item_path):
                continue

            dir_date = parse_directory_date(item)
            if dir_date is not None:
                result.append((item_path, dir_date))
    except (OSError, PermissionError):
        pass

    return result


def _format_released_space(freed_bytes: int) -> str:
    """格式化释放空间显示"""
    if freed_bytes < 0:
        raise ValueError("freed_bytes不能为负数")

    if freed_bytes >= 1024 * 1024:
        freed_mb = freed_bytes / (1024 * 1024)
        return f"{freed_mb:.2f} MB"

    freed_kb = freed_bytes / 1024 if freed_bytes > 0 else 0
    return f"{freed_kb:.2f} KB"


def delete_expired_directories(
    expired_dirs: List[str], logger_instance: Any = None
) -> Tuple[int, int]:
    """删除过期的目录

    Args:
        expired_dirs: 过期目录路径列表
        logger_instance: 日志记录器（可选）

    Returns:
        Tuple[int, int]: (删除目录数, 释放字节数)
    """
    deleted_count: int = 0
    freed_bytes: int = 0

    for dir_path in expired_dirs:
        try:
            # 计算目录大小
            dir_size = _calculate_directory_size(dir_path)

            # 删除目录
            shutil.rmtree(dir_path)
            deleted_count += 1
            freed_bytes += dir_size

        except (OSError, PermissionError) as e:
            if logger_instance is not None:
                try:
                    logger_instance.warning(f"删除目录失败: {dir_path}, 错误: {e}")
                except Exception:
                    pass

    return deleted_count, freed_bytes


def cleanup_expired_logs(config: Any, logger_instance: Any = None) -> Tuple[int, int]:
    """清理过期的日志目录

    Args:
        config: 配置对象，必须包含paths.work_dir和logger属性
        logger_instance: 日志记录器，用于输出清理结果

    Returns:
        Tuple[int, int]: (删除目录数, 释放字节数)
    """
    global _cleanup_done

    # 确保只执行一次
    if _cleanup_done:
        return 0, 0

    # 获取日志目录
    paths_obj = getattr(config, "paths", None)
    if paths_obj is None:
        return 0, 0

    if isinstance(paths_obj, dict):
        log_dir = paths_obj.get("work_dir")
    else:
        log_dir = getattr(paths_obj, "work_dir", None)

    if log_dir is None:
        return 0, 0

    # 添加 /logs 后缀
    log_dir = os.path.join(log_dir, "logs")

    # 确保配置存在
    retention_days = _ensure_retention_config(config)

    # 扫描目录
    directories = scan_log_directories(log_dir)

    # 筛选过期目录
    expired_dirs: List[str] = []
    for dir_path, dir_date in directories:
        if is_expired(dir_date, retention_days):
            expired_dirs.append(dir_path)

    # 删除过期目录
    deleted_count, freed_bytes = delete_expired_directories(
        expired_dirs, logger_instance
    )

    # 标记已完成
    _cleanup_done = True

    # 输出日志
    if logger_instance is not None:
        released_space = _format_released_space(freed_bytes)
        try:
            logger_instance.info(
                f"日志过期清理完成: 删除 {deleted_count} 个目录, "
                f"释放 {released_space} 空间"
            )
        except Exception:
            pass

    return deleted_count, freed_bytes


def reset_cleanup_flag() -> None:
    """重置清理标记（主要用于测试）"""
    global _cleanup_done
    _cleanup_done = False
    return
