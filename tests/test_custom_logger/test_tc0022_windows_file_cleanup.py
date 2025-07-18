# tests/test_custom_logger/test_tc0022_windows_file_cleanup.py
"""
Windows环境下文件清理测试，解决文件锁定问题
"""
from __future__ import annotations

import os
import tempfile
import time
import shutil
import pytest
from datetime import datetime
from pathlib import Path

from custom_logger import (
    init_custom_logger_system,
    get_logger,
    tear_down_custom_logger_system
)


class MockConfig:
    """模拟配置对象"""
    
    def __init__(self, log_dir: str, first_start_time: datetime):
        self.first_start_time = first_start_time
        self.project_name = "windows_cleanup_test"
        self.experiment_name = "tc0022"
        
        # 使用paths结构，符合config_manager的格式
        self.paths = {
            'log_dir': log_dir
        }
        
        # logger配置
        self.logger = {
            'global_console_level': 'debug',
            'global_file_level': 'debug',
            'show_debug_call_stack': False,
            'module_levels': {}
        }


def force_close_files_in_directory(directory: str, max_retries: int = 3, delay: float = 0.5):
    """强制关闭目录中的文件句柄（Windows专用）"""
    if not os.path.exists(directory):
        return
    
    for retry in range(max_retries):
        try:
            # 遍历目录中的所有文件
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # 尝试打开并立即关闭文件以释放句柄
                        with open(file_path, 'r', encoding='utf-8') as f:
                            pass
                    except (OSError, IOError, PermissionError):
                        # 如果无法打开，可能已经被锁定，跳过
                        continue
            
            # 如果成功遍历完所有文件，退出重试循环
            break
        except Exception:
            if retry < max_retries - 1:
                time.sleep(delay)
            else:
                # 最后一次重试失败，继续执行
                pass


def safe_rmtree(path: str, max_retries: int = 5, delay: float = 0.5):
    """安全地删除目录树，处理Windows文件锁定"""
    if not os.path.exists(path):
        return
    
    for retry in range(max_retries):
        try:
            # 首先尝试强制关闭文件句柄
            force_close_files_in_directory(path)
            
            # 尝试删除目录
            shutil.rmtree(path)
            return
        except (OSError, PermissionError) as e:
            if retry < max_retries - 1:
                print(f"删除目录重试 {retry + 1}/{max_retries}: {e}")
                time.sleep(delay)
            else:
                print(f"无法删除目录 {path}: {e}")
                # 尝试重置权限并再次删除
                try:
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                os.chmod(file_path, 0o777)
                            except (OSError, PermissionError):
                                pass
                        for dir in dirs:
                            dir_path = os.path.join(root, dir)
                            try:
                                os.chmod(dir_path, 0o777)
                            except (OSError, PermissionError):
                                pass
                    shutil.rmtree(path)
                except Exception as final_error:
                    print(f"最终删除失败: {final_error}")


@pytest.fixture
def safe_temp_log_dir():
    """创建安全的临时日志目录，解决Windows文件锁定问题"""
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
        
        # 使用安全删除
        safe_rmtree(temp_dir)


def test_tc0022_windows_file_cleanup_basic(safe_temp_log_dir):
    """测试基本的Windows文件清理"""
    try:
        # 创建config对象
        config = MockConfig(
            log_dir=safe_temp_log_dir,
            first_start_time=datetime.now()
        )
        
        # 初始化日志系统
        init_custom_logger_system(config)
        
        # 创建logger并写入日志
        logger = get_logger("cleanup_test")
        logger.info("测试消息1")
        logger.warning("测试警告")
        logger.error("测试错误")
        
        # 刷新以确保数据写入
        from custom_logger.writer import flush_writer
        flush_writer()
        
        # 验证文件存在
        full_log_path = os.path.join(safe_temp_log_dir, "full.log")
        assert os.path.exists(full_log_path), "日志文件应该存在"
        
        # 验证文件有内容
        with open(full_log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "测试消息1" in content
            assert "测试警告" in content
            assert "测试错误" in content
        
    finally:
        # 确保清理
        tear_down_custom_logger_system()


def test_tc0022_windows_file_cleanup_multiple_loggers(safe_temp_log_dir):
    """测试多个logger的Windows文件清理"""
    try:
        # 创建config对象
        config = MockConfig(
            log_dir=safe_temp_log_dir,
            first_start_time=datetime.now()
        )
        
        # 初始化日志系统
        init_custom_logger_system(config)
        
        # 创建多个logger
        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")
        logger3 = get_logger("logger3")
        
        # 写入日志
        logger1.info("Logger1消息")
        logger2.warning("Logger2警告")
        logger3.error("Logger3错误")
        
        # 刷新以确保数据写入
        from custom_logger.writer import flush_writer
        flush_writer()
        
        # 验证所有文件存在
        expected_files = [
            "full.log",
            "warning.log",
            "logger1_full.log",
            "logger2_full.log",
            "logger2_warning.log",
            "logger3_full.log",
            "logger3_warning.log"
        ]
        
        for filename in expected_files:
            filepath = os.path.join(safe_temp_log_dir, filename)
            assert os.path.exists(filepath), f"文件 {filename} 应该存在"
        
    finally:
        # 确保清理
        tear_down_custom_logger_system()


def test_tc0022_windows_file_cleanup_with_exception(safe_temp_log_dir):
    """测试异常情况下的Windows文件清理"""
    try:
        # 创建config对象
        config = MockConfig(
            log_dir=safe_temp_log_dir,
            first_start_time=datetime.now()
        )
        
        # 初始化日志系统
        init_custom_logger_system(config)
        
        # 创建logger
        logger = get_logger("exception_test")
        
        # 测试异常日志
        try:
            result = 1 / 0
        except ZeroDivisionError:
            logger.error("除零错误")
            logger.critical("严重错误")
            logger.exception("异常详情")
        
        # 刷新以确保数据写入
        from custom_logger.writer import flush_writer
        flush_writer()
        
        # 验证异常栈在文件中
        full_log_path = os.path.join(safe_temp_log_dir, "full.log")
        with open(full_log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "ZeroDivisionError" in content
            assert "Traceback" in content
        
    finally:
        # 确保清理
        tear_down_custom_logger_system()


def test_tc0022_windows_file_cleanup_stress_test(safe_temp_log_dir):
    """Windows文件清理压力测试"""
    try:
        # 创建config对象
        config = MockConfig(
            log_dir=safe_temp_log_dir,
            first_start_time=datetime.now()
        )
        
        # 初始化日志系统
        init_custom_logger_system(config)
        
        # 创建logger
        logger = get_logger("stress_test")
        
        # 大量写入日志
        for i in range(100):
            logger.info(f"压力测试消息 {i}")
            if i % 10 == 0:
                logger.warning(f"警告消息 {i}")
            if i % 20 == 0:
                logger.error(f"错误消息 {i}")
        
        # 刷新以确保数据写入
        from custom_logger.writer import flush_writer
        flush_writer()
        
        # 验证文件大小合理
        full_log_path = os.path.join(safe_temp_log_dir, "full.log")
        file_size = os.path.getsize(full_log_path)
        assert file_size > 5000, f"日志文件大小应该合理: {file_size} bytes"
        
    finally:
        # 确保清理
        tear_down_custom_logger_system()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])