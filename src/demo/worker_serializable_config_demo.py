"""
演示如何在worker进程中使用序列化配置对象避免config_manager重复初始化

这个演示展示了两种方式：
1. 传统方式：每个worker都会初始化config_manager（会造成重复初始化）
2. 序列化配置方式：主进程获取序列化配置，worker使用序列化配置初始化（避免重复初始化）
"""
from __future__ import annotations

import os
import sys
import tempfile
import multiprocessing as mp
from datetime import datetime
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from custom_logger import (
    init_custom_logger_system,
    init_custom_logger_system_from_serializable_config,
    get_logger,
    get_serializable_config,
    tear_down_custom_logger_system
)


def traditional_worker(worker_id: int, config_path: str):
    """传统的worker函数 - 每个worker都会初始化config_manager"""
    print(f"传统Worker {worker_id}: 开始初始化日志系统")
    
    # 设置环境变量
    os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = config_path
    
    # 每个worker都会调用init_custom_logger_system，导致config_manager重复初始化
    init_custom_logger_system()
    
    # 获取logger并记录日志
    logger = get_logger(f"worker_{worker_id}")
    logger.info(f"传统Worker {worker_id} 开始工作")
    
    # 模拟一些工作
    for i in range(3):
        logger.info(f"传统Worker {worker_id} 处理任务 {i+1}")
    
    logger.info(f"传统Worker {worker_id} 工作完成")
    
    # 清理
    tear_down_custom_logger_system()
    
    return f"传统Worker-{worker_id} 完成"


def serializable_config_worker(worker_id: int, serializable_config, first_start_time: datetime):
    """使用序列化配置的worker函数 - 避免config_manager重复初始化"""
    print(f"序列化配置Worker {worker_id}: 开始使用序列化配置初始化日志系统")
    
    # 使用序列化配置初始化，避免config_manager重复初始化
    init_custom_logger_system_from_serializable_config(
        serializable_config=serializable_config,
        first_start_time=first_start_time
    )
    
    # 获取logger并记录日志
    logger = get_logger(f"ser_wkr_{worker_id}")
    logger.info(f"序列化配置Worker {worker_id} 开始工作")
    
    # 模拟一些工作
    for i in range(3):
        logger.info(f"序列化配置Worker {worker_id} 处理任务 {i+1}")
    
    logger.info(f"序列化配置Worker {worker_id} 工作完成")
    
    # 清理
    tear_down_custom_logger_system()
    
    return f"序列化配置Worker-{worker_id} 完成"


def demonstrate_traditional_approach():
    """演示传统方式 - 每个worker都会初始化config_manager"""
    print("\n" + "="*60)
    print("演示传统方式（会造成config_manager重复初始化）")
    print("="*60)
    
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp:
        config_path = tmp.name
        tmp.write("""project_name: "传统方式演示"
experiment_name: "traditional_demo"
base_dir: "temp/logs"
logger:
  global_console_level: "info"
  global_file_level: "debug"
""")
    
    try:
        print(f"配置文件路径: {config_path}")
        
        # 使用多进程执行传统worker
        print("启动传统worker进程...")
        with mp.Pool(processes=2) as pool:
            results = pool.starmap(
                traditional_worker,
                [(1, config_path), (2, config_path)]
            )
        
        print("传统worker结果:")
        for result in results:
            print(f"  - {result}")
            
    finally:
        # 清理临时文件
        try:
            os.unlink(config_path)
        except:
            pass


def demonstrate_serializable_config_approach():
    """演示序列化配置方式 - 避免config_manager重复初始化"""
    print("\n" + "="*60)
    print("演示序列化配置方式（避免config_manager重复初始化）")
    print("="*60)
    
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp:
        config_path = tmp.name
        tmp.write("""project_name: "序列化配置演示"
experiment_name: "serializable_demo"
base_dir: "temp/logs"
logger:
  global_console_level: "info"
  global_file_level: "debug"
""")
    
    try:
        print(f"配置文件路径: {config_path}")
        
        # 主进程初始化日志系统
        print("主进程初始化日志系统...")
        first_start_time = datetime.now()
        init_custom_logger_system(
            config_path=config_path,
            first_start_time=first_start_time
        )
        
        # 获取序列化配置
        print("主进程获取序列化配置...")
        serializable_config = get_serializable_config()
        print(f"序列化配置类型: {type(serializable_config)}")
        
        # 主进程记录一些日志
        main_logger = get_logger("main")
        main_logger.info("主进程开始启动worker")
        
        # 清理主进程的日志系统（worker会重新初始化）
        tear_down_custom_logger_system()
        
        # 使用多进程执行序列化配置worker
        print("启动序列化配置worker进程...")
        with mp.Pool(processes=2) as pool:
            results = pool.starmap(
                serializable_config_worker,
                [(1, serializable_config, first_start_time), 
                 (2, serializable_config, first_start_time)]
            )
        
        print("序列化配置worker结果:")
        for result in results:
            print(f"  - {result}")
            
    finally:
        # 清理临时文件
        try:
            os.unlink(config_path)
        except:
            pass


def demonstrate_performance_comparison():
    """演示性能对比"""
    print("\n" + "="*60)
    print("性能对比演示")
    print("="*60)
    
    import time
    
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp:
        config_path = tmp.name
        tmp.write("""project_name: "性能对比演示"
experiment_name: "performance_demo"
base_dir: "temp/logs"
logger:
  global_console_level: "warning"
  global_file_level: "error"
""")
    
    try:
        # 测试传统方式
        print("测试传统方式性能...")
        start_time = time.time()
        with mp.Pool(processes=3) as pool:
            results = pool.starmap(
                traditional_worker,
                [(i, config_path) for i in range(1, 4)]
            )
        traditional_time = time.time() - start_time
        print(f"传统方式耗时: {traditional_time:.2f}秒")
        
        # 测试序列化配置方式
        print("测试序列化配置方式性能...")
        start_time = time.time()
        
        # 主进程初始化
        first_start_time = datetime.now()
        init_custom_logger_system(
            config_path=config_path,
            first_start_time=first_start_time
        )
        serializable_config = get_serializable_config()
        tear_down_custom_logger_system()
        
        # worker执行
        with mp.Pool(processes=3) as pool:
            results = pool.starmap(
                serializable_config_worker,
                [(i, serializable_config, first_start_time) for i in range(1, 4)]
            )
        serializable_time = time.time() - start_time
        print(f"序列化配置方式耗时: {serializable_time:.2f}秒")
        
        # 性能对比
        if traditional_time > 0:
            improvement = ((traditional_time - serializable_time) / traditional_time) * 100
            print(f"性能提升: {improvement:.1f}%")
        
    finally:
        # 清理临时文件
        try:
            os.unlink(config_path)
        except:
            pass


def main():
    """主函数"""
    print("Worker序列化配置演示")
    print("="*60)
    print("这个演示展示了如何在worker进程中使用序列化配置对象")
    print("来避免config_manager重复初始化的问题。")
    
    # 确保temp目录存在
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # 演示传统方式
        demonstrate_traditional_approach()
        
        # 演示序列化配置方式
        demonstrate_serializable_config_approach()
        
        # 演示性能对比
        demonstrate_performance_comparison()
        
        print("\n" + "="*60)
        print("演示完成！")
        print("="*60)
        print("总结:")
        print("1. 传统方式：每个worker都会初始化config_manager，造成重复初始化")
        print("2. 序列化配置方式：主进程获取序列化配置，worker直接使用，避免重复初始化")
        print("3. 序列化配置方式通常有更好的性能表现")
        print("4. 推荐在多进程环境中使用序列化配置方式")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 