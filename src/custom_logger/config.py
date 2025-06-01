# src/custom_logger/config.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
from typing import Dict, Any, Optional
from config_manager import get_config_manager
from is_debug import is_debug
from .types import parse_level_name

# 默认配置
DEFAULT_CONFIG = {
    "project_name": "my_project",
    "experiment_name": "default",
    "first_start_time": None,
    "base_dir": "d:/logs",
    'logger': {
        "global_console_level": "info",
        "global_file_level": "debug",
        "current_session_dir": None,
        "module_levels": {},
    },
}

# 全局配置路径缓存
_cached_config_path: Optional[str] = None


def get_cached_config_path() -> Optional[str]:
    """获取缓存的配置路径（用于测试）"""
    return _cached_config_path


def set_config_path(config_path: Optional[str]) -> None:
    """设置配置文件路径"""
    global _cached_config_path
    _cached_config_path = config_path

    # 同时设置环境变量供子进程使用
    if config_path is not None and config_path != "":
        os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = config_path
    else:
        # 当设置为None或空字符串时，完全清理环境变量
        if 'CUSTOM_LOGGER_CONFIG_PATH' in os.environ:
            del os.environ['CUSTOM_LOGGER_CONFIG_PATH']
    return


def get_config_file_path() -> str:
    """获取配置文件路径"""
    # 优先级：缓存路径 > 环境变量 > 默认路径
    if _cached_config_path is not None and _cached_config_path != "":
        return _cached_config_path

    env_path = os.environ.get('CUSTOM_LOGGER_CONFIG_PATH')
    if env_path and env_path.strip() != "":
        return env_path

    default_path = os.path.join("config", "config.yaml")
    return default_path


def init_config(config_path: Optional[str] = None) -> None:
    """初始化配置"""
    # 设置配置路径
    if config_path is not None:
        set_config_path(config_path)

    actual_config_path = get_config_file_path()
    cfg = get_config_manager(config_path=actual_config_path)

    # 检查配置是否已存在，使用新的结构
    if not hasattr(cfg, 'logger'):
        # 创建默认配置结构
        for key, value in DEFAULT_CONFIG.items():
            if key == 'logger':
                # 为logger创建对象而不是字典
                logger_obj = type('LoggerConfig', (), {})()
                for sub_key, sub_value in value.items():
                    setattr(logger_obj, sub_key, sub_value)
                setattr(cfg, key, logger_obj)
            else:
                setattr(cfg, key, value)

    # 设置第一次启动时间
    if cfg.first_start_time is None:
        cfg.first_start_time = start_time.isoformat()

    # 创建当前会话目录
    session_dir = _create_session_dir(cfg)
    cfg.logger.current_session_dir = session_dir

    return


def _create_session_dir(cfg) -> str:
    """创建当前会话的日志目录"""
    # 获取配置值
    base_dir = getattr(cfg, 'base_dir', 'd:/logs')
    project_name = getattr(cfg, 'project_name', 'my_project')
    experiment_name = getattr(cfg, 'experiment_name', 'default')
    first_start_time_str = getattr(cfg, 'first_start_time', None)

    # debug模式添加debug层
    if is_debug():
        base_dir = os.path.join(str(base_dir), "debug")

    # 解析第一次启动时间
    first_start = datetime.fromisoformat(first_start_time_str)
    date_str = first_start.strftime("%Y%m%d")
    time_str = first_start.strftime("%H%M%S")

    # 构建完整路径
    session_dir = os.path.join(str(base_dir), str(project_name), str(experiment_name), "logs", date_str, time_str)

    # 创建目录
    os.makedirs(session_dir, exist_ok=True)

    return session_dir


def get_config() -> Any:
    """获取配置"""
    config_path = get_config_file_path()
    cfg = get_config_manager(config_path=config_path)
    if not hasattr(cfg, 'logger'):
        raise RuntimeError("日志系统未初始化，请先调用 init_custom_logger_system()")

    return cfg.logger


def get_root_config() -> Any:
    """获取根配置对象（用于formatter访问first_start_time）"""
    config_path = get_config_file_path()
    cfg = get_config_manager(config_path=config_path)
    if not hasattr(cfg, 'logger'):
        raise RuntimeError("日志系统未初始化，请先调用 init_custom_logger_system()")
    return cfg


def get_console_level(module_name: str) -> int:
    """获取模块的控制台日志级别"""
    cfg = get_config()

    # 获取模块级别配置
    module_levels = getattr(cfg, 'module_levels', {})
    global_level = getattr(cfg, 'global_console_level', 'info')

    module_config = module_levels.get(module_name, {}) if hasattr(module_levels, 'get') else module_levels.get(
        module_name, {})

    # 优先使用模块特定配置
    if 'console_level' in module_config:
        level_name = module_config['console_level']
    else:
        level_name = global_level

    level_value = parse_level_name(level_name)
    return level_value


def get_file_level(module_name: str) -> int:
    """获取模块的文件日志级别"""
    cfg = get_config()

    # 获取模块级别配置
    module_levels = getattr(cfg, 'module_levels', {})
    global_level = getattr(cfg, 'global_file_level', 'debug')

    module_config = module_levels.get(module_name, {}) if hasattr(module_levels, 'get') else module_levels.get(
        module_name, {})

    # 优先使用模块特定配置
    if 'file_level' in module_config:
        level_name = module_config['file_level']
    else:
        level_name = global_level

    level_value = parse_level_name(level_name)
    return level_value