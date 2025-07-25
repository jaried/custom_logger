# tests/test_custom_logger/test_new_api.py
"""
测试新API功能

测试用例：
- 测试config_object初始化
- 测试worker初始化
- 测试队列模式
"""
from __future__ import annotations

import os
import tempfile
import multiprocessing as mp
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from custom_logger import (
    init_custom_logger_system,
    init_custom_logger_system_for_worker,
    get_logger,
    tear_down_custom_logger_system,
    is_queue_mode
)


class MockConfig:
    """模拟config对象"""
    def __init__(self, log_dir: str, first_start_time: datetime, queue_info=None):
        self.paths = MagicMock()
        self.paths.log_dir = log_dir
        self.first_start_time = first_start_time
        self.logger = {
            'global_console_level': 'info',
            'global_file_level': 'debug'
        }
        if queue_info:
            self.queue_info = queue_info


@pytest.fixture
def temp_log_dir():
    """创建临时日志目录，解决Windows文件锁定问题"""
    import shutil
    import time
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="custom_logger_test_")
    log_dir = os.path.join(temp_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    try:
        yield log_dir
    finally:
        # 确保清理日志系统
        try:
            tear_down_custom_logger_system()
        except Exception:
            pass
        
        # 等待一段时间确保所有文件句柄释放
        time.sleep(0.5)
        
        # 安全删除临时目录
        max_retries = 5
        for retry in range(max_retries):
            try:
                shutil.rmtree(temp_dir)
                break
            except (OSError, PermissionError) as e:
                if retry < max_retries - 1:
                    time.sleep(0.5)
                else:
                    # 最后一次重试失败，尝试重置权限
                    try:
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                try:
                                    os.chmod(file_path, 0o777)
                                except (OSError, PermissionError):
                                    pass
                        shutil.rmtree(temp_dir)
                    except Exception:
                        print(f"警告：无法完全清理临时目录 {temp_dir}")
                        pass


def test_new_api_basic_config_object(temp_log_dir):
    """测试基本的config_object初始化"""
    try:
        # 创建config对象
        config = MockConfig(
            log_dir=temp_log_dir,
            first_start_time=datetime.now()
        )
        
        # 初始化日志系统
        init_custom_logger_system(config_object=config)
        
        # 验证可以获取logger
        logger = get_logger("test")
        assert logger is not None
        assert logger.name == "test"
        
        # 验证可以记录日志
        logger.info("测试新API")
        
        # 验证不是队列模式
        assert not is_queue_mode()
        
    finally:
        tear_down_custom_logger_system()


def test_new_api_worker_initialization(temp_log_dir):
    """测试worker初始化"""
    try:
        # 创建config对象
        config = MockConfig(
            log_dir=temp_log_dir,
            first_start_time=datetime.now()
        )
        
        # 使用worker初始化
        init_custom_logger_system_for_worker(serializable_config_object=config, worker_id="test_worker")
        
        # 验证可以获取logger
        logger = get_logger("worker")
        assert logger is not None
        assert logger.name == "worker"
        
        # 验证可以记录日志
        logger.info("Worker测试")
        
    finally:
        tear_down_custom_logger_system()


def test_new_api_queue_mode(temp_log_dir):
    """测试队列模式"""
    try:
        # 创建队列
        log_queue = mp.Queue()
        
        # 创建带队列的config对象
        queue_info = MagicMock()
        queue_info.log_queue = log_queue
        
        config = MockConfig(
            log_dir=temp_log_dir,
            first_start_time=datetime.now(),
            queue_info=queue_info
        )
        
        # 初始化日志系统
        init_custom_logger_system(config_object=config)
        
        # 验证是队列模式
        assert is_queue_mode()
        
        # 验证可以获取logger
        logger = get_logger("queue")
        assert logger is not None
        
        # 验证可以记录日志
        logger.info("队列模式测试")
        
    finally:
        tear_down_custom_logger_system()


def test_new_api_missing_paths():
    """测试缺少paths属性的错误处理"""
    # 使用普通对象而不是MagicMock，这样getattr会返回None
    class ConfigWithoutPaths:
        def __init__(self):
            self.first_start_time = datetime.now()
    
    config = ConfigWithoutPaths()
    
    with pytest.raises(ValueError, match="config_object必须包含paths属性"):
        init_custom_logger_system(config_object=config)


def test_new_api_missing_first_start_time(temp_log_dir):
    """测试缺少first_start_time的错误处理"""
    # 使用普通对象而不是MagicMock
    class ConfigWithoutFirstStartTime:
        def __init__(self, log_dir):
            self.paths = MagicMock()
            self.paths.log_dir = log_dir
            # 故意不设置first_start_time属性
    
    config = ConfigWithoutFirstStartTime(temp_log_dir)
    
    with pytest.raises(ValueError, match="config_object必须包含first_start_time属性"):
        init_custom_logger_system(config_object=config)


def test_new_api_logger_name_length(temp_log_dir):
    """测试logger名称长度限制"""
    try:
        # 先初始化系统
        config = MockConfig(
            log_dir=temp_log_dir,
            first_start_time=datetime.now()
        )
        init_custom_logger_system(config_object=config)

        # 测试超长名称
        with pytest.raises(ValueError, match=r"日志记录器名称.*不能超过16个字符，当前长度: \d+"):
            get_logger("very_very_long_logger_name")  # 超过16个字符
    except Exception as e:
        raise e


def test_new_api_system_not_initialized():
    """测试系统未初始化时的错误处理"""
    # 确保系统未初始化
    tear_down_custom_logger_system()
    
    with pytest.raises(RuntimeError, match="日志系统未初始化"):
        get_logger("test") 