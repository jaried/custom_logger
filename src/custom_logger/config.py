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
    "global_console_level": "info",
    "global_file_level": "debug",
    "base_log_dir": "d:/logs",
    "first_start_time": None,
    "current_session_dir": None,
    "module_levels": {}
}


def get_config_file_path() -> str:
    """获取配置文件路径"""
    config_path = os.path.join("config", "custom_logger.yaml")
    return config_path


def init_config() -> None:
    """初始化配置"""
    config_path = get_config_file_path()
    cfg = get_config_manager(config_path=config_path)

    # 检查配置是否已存在
    if not hasattr(cfg, 'custom_logger'):
        # 创建默认配置
        cfg.custom_logger = DEFAULT_CONFIG.copy()

    # 获取配置对象（可能是字典或DotDict）
    config_obj = cfg.custom_logger

    # 设置第一次启动时间
    if isinstance(config_obj, dict):
        # 字典方式访问
        if config_obj.get('first_start_time') is None:
            config_obj['first_start_time'] = datetime.now().isoformat()
    else:
        # DotDict方式访问
        if config_obj.first_start_time is None:
            config_obj.first_start_time = datetime.now().isoformat()

    # 创建当前会话目录
    session_dir = _create_session_dir(cfg)
    if isinstance(config_obj, dict):
        # 字典方式访问
        config_obj['current_session_dir'] = session_dir
    else:
        # DotDict方式访问
        config_obj.current_session_dir = session_dir

    return


def _create_session_dir(cfg) -> str:
    """创建当前会话的日志目录"""
    config_obj = cfg.custom_logger

    # 获取配置值（兼容字典和DotDict）
    if isinstance(config_obj, dict):
        base_dir = config_obj.get('base_log_dir', 'd:/logs')
        project_name = config_obj.get('project_name', 'my_project')
        experiment_name = config_obj.get('experiment_name', 'default')
        first_start_time_str = config_obj.get('first_start_time')
    else:
        base_dir = getattr(config_obj, 'base_log_dir', 'd:/logs')
        project_name = getattr(config_obj, 'project_name', 'my_project')
        experiment_name = getattr(config_obj, 'experiment_name', 'default')
        first_start_time_str = getattr(config_obj, 'first_start_time', None)

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
    if not hasattr(cfg, 'custom_logger'):
        raise RuntimeError("日志系统未初始化，请先调用 init_custom_logger_system()")

    return cfg.custom_logger


def get_console_level(module_name: str) -> int:
    """获取模块的控制台日志级别"""
    cfg = get_config()

    # 获取模块级别配置（兼容字典和DotDict）
    if isinstance(cfg, dict):
        module_levels = cfg.get('module_levels', {})
        global_level = cfg.get('global_console_level', 'info')
    else:
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

    # 获取模块级别配置（兼容字典和DotDict）
    if isinstance(cfg, dict):
        module_levels = cfg.get('module_levels', {})
        global_level = cfg.get('global_file_level', 'debug')
    else:
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
