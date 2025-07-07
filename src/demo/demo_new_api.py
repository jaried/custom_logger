# src/demo/demo_new_api.py
"""
新API演示程序

演示如何使用新的API接口：
1. 主程序使用config对象初始化
2. Worker进程使用序列化配置初始化
3. Logger名字长度验证
4. 时间计算准确性
"""
from __future__ import annotations

import os
import tempfile
import multiprocessing as mp
from datetime import datetime
from unittest.mock import Mock

from custom_logger import (
    init_custom_logger_system,
    init_custom_logger_system_for_worker,
    get_logger,
    tear_down_custom_logger_system
)


class SimpleConfig:
    """简单的配置类，支持序列化"""
    def __init__(self, log_dir: str, start_time: datetime):
        self.first_start_time = start_time
        self.paths = SimplePaths(log_dir)
        self.logger = SimpleLogger()


class SimplePaths:
    """简单的路径配置类"""
    def __init__(self, log_dir: str):
        self.log_dir = log_dir


class SimpleLogger:
    """简单的logger配置类"""
    def __init__(self):
        self.global_console_level = "info"
        self.global_file_level = "debug"
        self.module_levels = {}


def create_config_object(log_dir: str, start_time: datetime) -> SimpleConfig:
    """创建配置对象"""
    return SimpleConfig(log_dir, start_time)


def demo_main_process():
    """演示主程序使用新API"""
    print("=== 主程序新API演示 ===")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    log_dir = os.path.join(temp_dir, "logs")
    start_time = datetime.now()
    
    # 创建配置对象
    config = create_config_object(log_dir, start_time)
    
    try:
        # 使用新API初始化
        print(f"1. 使用config对象初始化系统")
        print(f"   log_dir: {log_dir}")
        print(f"   start_time: {start_time}")
        
        init_custom_logger_system(config)
        print("   ✓ 初始化成功")
        
        # 测试logger名字长度验证
        print("\n2. 测试logger名字长度验证")
        
        # 有效名字
        valid_names = ["app", "db", "api", "worker01", "12345678"]
        for name in valid_names:
            logger = get_logger(name)
            print(f"   ✓ '{name}' (长度: {len(name)}) - 成功")
        
        # 无效名字
        invalid_names = ["very_long_name", "123456789"]
        for name in invalid_names:
            try:
                get_logger(name)
                print(f"   ✗ '{name}' (长度: {len(name)}) - 应该失败但成功了")
            except ValueError as e:
                print(f"   ✓ '{name}' (长度: {len(name)}) - 正确抛出异常: {e}")
        
        # 测试日志输出
        print("\n3. 测试日志输出")
        logger = get_logger("main")
        logger.info("主程序日志消息")
        logger.debug("调试信息")
        logger.warning("警告信息")
        
        print("   ✓ 日志输出完成")
        
    finally:
        tear_down_custom_logger_system()
        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def worker_function(serializable_config, worker_id: str):
    """Worker进程函数"""
    try:
        print(f"\n=== Worker {worker_id} 演示 ===")
        
        # 使用worker专用API初始化
        print(f"1. Worker {worker_id} 初始化")
        init_custom_logger_system_for_worker(serializable_config, worker_id)
        print(f"   ✓ Worker {worker_id} 初始化成功")
        
        # 获取logger并输出日志
        logger = get_logger("worker")
        logger.info(f"Worker {worker_id} 开始工作")
        logger.worker_summary(f"Worker {worker_id} 摘要信息")
        logger.worker_detail(f"Worker {worker_id} 详细信息")
        
        print(f"   ✓ Worker {worker_id} 日志输出完成")
        
    except Exception as e:
        print(f"   ✗ Worker {worker_id} 出错: {e}")
    finally:
        tear_down_custom_logger_system()


def demo_worker_process():
    """演示Worker进程使用新API"""
    print("\n=== Worker进程新API演示 ===")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    log_dir = os.path.join(temp_dir, "logs")
    start_time = datetime.now()
    
    # 创建配置对象
    config = create_config_object(log_dir, start_time)
    
    try:
        # 启动多个worker进程
        processes = []
        for i in range(2):
            worker_id = f"worker_{i+1:03d}"
            p = mp.Process(target=worker_function, args=(config, worker_id))
            p.start()
            processes.append(p)
        
        # 等待所有进程完成
        for p in processes:
            p.join()
        
        print("\n   ✓ 所有Worker进程完成")
        
    finally:
        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def demo_timing_accuracy():
    """演示时间计算准确性"""
    print("\n=== 时间计算准确性演示 ===")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    log_dir = os.path.join(temp_dir, "logs")
    
    # 设置一个固定的开始时间
    start_time = datetime(2025, 1, 1, 10, 0, 0)
    
    # 创建配置对象
    config = create_config_object(log_dir, start_time)
    
    try:
        print(f"1. 设置固定开始时间: {start_time}")
        
        # 初始化系统
        init_custom_logger_system(config)
        
        # 获取logger
        logger = get_logger("timing")
        
        print("2. 输出日志查看时间计算")
        logger.info("这是一条测试时间计算的日志")
        
        print("   ✓ 检查日志中的运行时长是否正确")
        
    finally:
        tear_down_custom_logger_system()
        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def demo_error_handling():
    """演示错误处理"""
    print("\n=== 错误处理演示 ===")
    
    print("1. 测试传入None配置")
    try:
        init_custom_logger_system(None)
        print("   ✗ 应该抛出异常但没有")
    except ValueError as e:
        print(f"   ✓ 正确抛出异常: {e}")
    
    print("\n2. 测试缺少paths属性")
    try:
        class ConfigWithoutPaths:
            def __init__(self):
                self.first_start_time = datetime.now()
                # 没有paths属性
        
        config = ConfigWithoutPaths()
        init_custom_logger_system(config)
        print("   ✗ 应该抛出异常但没有")
    except ValueError as e:
        print(f"   ✓ 正确抛出异常: {e}")
    
    print("\n3. 测试缺少first_start_time属性")
    try:
        class ConfigWithoutStartTime:
            def __init__(self):
                self.paths = SimplePaths("/tmp/test")
                # 没有first_start_time属性
        
        config = ConfigWithoutStartTime()
        init_custom_logger_system(config)
        print("   ✗ 应该抛出异常但没有")
    except ValueError as e:
        print(f"   ✓ 正确抛出异常: {e}")
    
    print("\n4. 测试未初始化时获取logger")
    try:
        tear_down_custom_logger_system()  # 确保未初始化
        get_logger("test")
        print("   ✗ 应该抛出异常但没有")
    except RuntimeError as e:
        print(f"   ✓ 正确抛出异常: {e}")


def main():
    """主函数"""
    print("Custom Logger 新API演示程序")
    print("=" * 50)
    
    # 演示主程序API
    demo_main_process()
    
    # 演示Worker进程API
    demo_worker_process()
    
    # 演示时间计算准确性
    demo_timing_accuracy()
    
    # 演示错误处理
    demo_error_handling()
    
    print("\n" + "=" * 50)
    print("新API演示完成！")
    print("\n主要特性：")
    print("✓ 直接接收config对象，不再调用config_manager")
    print("✓ Worker专用初始化函数")
    print("✓ Logger名字长度严格验证（≤8字符）")
    print("✓ 使用外部传入的first_start_time确保时间准确")
    print("✓ 完善的错误处理和验证")


if __name__ == "__main__":
    main() 