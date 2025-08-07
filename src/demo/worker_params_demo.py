"""
演示如何在worker进程中使用参数化初始化避免config_manager重复初始化

这个演示展示了三种方式：
1. 传统方式：每个worker都会初始化config_manager（会造成重复初始化）
2. 参数化方式：主进程提取参数，worker使用参数初始化（推荐方式）
3. 序列化配置方式：主进程获取序列化配置，worker使用序列化配置初始化
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
    init_custom_logger_system_with_params,  # 占位函数，抛出NotImplementedError
    init_custom_logger_system_from_serializable_config,  # 占位函数，抛出NotImplementedError
    get_logger,
    get_logger_init_params,  # 占位函数，抛出NotImplementedError
    get_serializable_config,  # 占位函数，抛出NotImplementedError
    tear_down_custom_logger_system
)

# 注意：此demo依赖于尚未实现的函数，暂时无法正常运行
DEMO_DISABLED = True

def traditional_worker(worker_id: int, config_path: str, first_start_time: datetime = None):
    """传统的worker函数 - 每个worker都会初始化config_manager"""
    print(f"传统Worker {worker_id}: 开始初始化日志系统")
    
    # 设置环境变量
    os.environ['CUSTOM_LOGGER_CONFIG_PATH'] = config_path
    
    # 每个worker都会调用init_custom_logger_system，导致config_manager重复初始化
    # 但现在可以传入外部的first_start_time
    init_custom_logger_system(first_start_time=first_start_time)
    
    # 获取logger并记录日志
    logger = get_logger(f"trad_{worker_id}")
    logger.info(f"传统Worker {worker_id} 开始工作")
    
    # 模拟一些工作
    for i in range(3):
        logger.info(f"传统Worker {worker_id} 处理任务 {i+1}")
    
    logger.info(f"传统Worker {worker_id} 工作完成")
    
    # 清理
    tear_down_custom_logger_system()
    
    return f"传统Worker-{worker_id} 完成"


def params_worker(worker_id: int, params: dict):
    """使用参数的worker函数 - 避免config_manager重复初始化（推荐方式）"""
    print(f"参数Worker {worker_id}: 开始使用参数初始化日志系统")
    
    # 使用参数初始化，避免config_manager重复初始化
    init_custom_logger_system_with_params(**params)
    
    # 获取logger并记录日志
    logger = get_logger(f"param_{worker_id}")
    logger.info(f"参数Worker {worker_id} 开始工作")
    
    # 模拟一些工作
    for i in range(3):
        logger.info(f"参数Worker {worker_id} 处理任务 {i+1}")
    
    logger.info(f"参数Worker {worker_id} 工作完成")
    
    # 清理
    tear_down_custom_logger_system()
    
    return f"参数Worker-{worker_id} 完成"


def serializable_config_worker(worker_id: int, serializable_config):
    """使用序列化配置的worker函数 - 避免config_manager重复初始化"""
    print(f"序列化配置Worker {worker_id}: 开始使用序列化配置初始化日志系统")
    
    # 使用序列化配置初始化，避免config_manager重复初始化
    init_custom_logger_system_from_serializable_config(
        serializable_config=serializable_config
    )
    
    # 获取logger并记录日志
    logger = get_logger(f"ser_{worker_id}")
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
        
        # 外部主程序设置统一的启动时间
        external_start_time = datetime.now()
        print(f"外部主程序设置的启动时间: {external_start_time}")
        
        # 使用多进程执行传统worker，传入外部启动时间
        print("启动传统worker进程（传入外部启动时间）...")
        with mp.Pool(processes=2) as pool:
            results = pool.starmap(
                traditional_worker,
                [(1, config_path, external_start_time), (2, config_path, external_start_time)]
            )
        
        print("传统worker结果:")
        for result in results:
            print(f"  - {result}")
            
    finally:
        # 清理临时文件
        try:
            os.unlink(config_path)
        except Exception:
            pass


def demonstrate_params_approach():
    """演示参数化方式 - 避免config_manager重复初始化（推荐方式）"""
    print("\n" + "="*60)
    print("演示参数化方式（避免config_manager重复初始化，推荐方式）")
    print("="*60)
    
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp:
        config_path = tmp.name
        tmp.write("""project_name: "参数化演示"
experiment_name: "params_demo"
base_dir: "temp/logs"
logger:
  global_console_level: "info"
  global_file_level: "debug"
""")
    
    try:
        print(f"配置文件路径: {config_path}")
        
        # 外部主程序设置统一的启动时间
        external_start_time = datetime.now()
        print(f"外部主程序设置的启动时间: {external_start_time}")
        
        # 主进程初始化日志系统，传入外部启动时间
        print("主进程初始化日志系统（使用外部启动时间）...")
        init_custom_logger_system(config_path=config_path, first_start_time=external_start_time)
        
        # 获取初始化参数
        print("主进程获取初始化参数...")
        params = get_logger_init_params()
        print(f"参数: {params}")
        
        # 验证first_start_time是否正确传递
        if 'first_start_time' in params:
            print(f"✓ first_start_time已包含在参数中: {params['first_start_time']}")
        else:
            print("⚠ first_start_time未包含在参数中")
        
        # 主进程记录一些日志
        main_logger = get_logger("main")
        main_logger.info("主进程开始启动worker")
        
        # 清理主进程的日志系统（worker会重新初始化）
        tear_down_custom_logger_system()
        
        # 使用多进程执行参数化worker
        print("启动参数化worker进程...")
        with mp.Pool(processes=2) as pool:
            results = pool.starmap(
                params_worker,
                [(1, params), (2, params)]
            )
        
        print("参数化worker结果:")
        for result in results:
            print(f"  - {result}")
            
    finally:
        # 清理临时文件
        try:
            os.unlink(config_path)
        except Exception:
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
        
        # 外部主程序设置统一的启动时间
        external_start_time = datetime.now()
        print(f"外部主程序设置的启动时间: {external_start_time}")
        
        # 主进程初始化日志系统，传入外部启动时间
        print("主进程初始化日志系统（使用外部启动时间）...")
        init_custom_logger_system(config_path=config_path, first_start_time=external_start_time)
        
        # 获取序列化配置
        print("主进程获取序列化配置...")
        serializable_config = get_serializable_config()
        print(f"序列化配置类型: {type(serializable_config)}")
        
        # 验证first_start_time是否包含在序列化配置中
        if hasattr(serializable_config, 'first_start_time'):
            print(f"✓ first_start_time已包含在序列化配置中: {serializable_config.first_start_time}")
        else:
            print("⚠ first_start_time未包含在序列化配置中")
        
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
                [(1, serializable_config), 
                 (2, serializable_config)]
            )
        
        print("序列化配置worker结果:")
        for result in results:
            print(f"  - {result}")
            
    finally:
        # 清理临时文件
        try:
            os.unlink(config_path)
        except Exception:
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
            pool.starmap(
                traditional_worker,
                [(i, config_path) for i in range(1, 4)]
            )
        traditional_time = time.time() - start_time
        print(f"传统方式耗时: {traditional_time:.2f}秒")
        
        # 测试参数化方式
        print("测试参数化方式性能...")
        start_time = time.time()
        
        # 主进程初始化
        init_custom_logger_system(config_path=config_path)
        params = get_logger_init_params()
        tear_down_custom_logger_system()
        
        # worker执行
        with mp.Pool(processes=3) as pool:
            pool.starmap(
                params_worker,
                [(i, params) for i in range(1, 4)]
            )
        params_time = time.time() - start_time
        print(f"参数化方式耗时: {params_time:.2f}秒")
        
        # 测试序列化配置方式
        print("测试序列化配置方式性能...")
        start_time = time.time()
        
        # 主进程初始化
        init_custom_logger_system(config_path=config_path)
        serializable_config = get_serializable_config()
        tear_down_custom_logger_system()
        
        # worker执行
        with mp.Pool(processes=3) as pool:
            pool.starmap(
                serializable_config_worker,
                [(i, serializable_config) for i in range(1, 4)]
            )
        serializable_time = time.time() - start_time
        print(f"序列化配置方式耗时: {serializable_time:.2f}秒")
        
        # 性能对比
        print("\n性能对比结果:")
        if traditional_time > 0:
            params_improvement = ((traditional_time - params_time) / traditional_time) * 100
            serializable_improvement = ((traditional_time - serializable_time) / traditional_time) * 100
            print(f"参数化方式性能提升: {params_improvement:.1f}%")
            print(f"序列化配置方式性能提升: {serializable_improvement:.1f}%")
        
    finally:
        # 清理临时文件
        try:
            os.unlink(config_path)
        except Exception:
            pass


def main():
    """主函数"""
    if DEMO_DISABLED:
        print("警告：此demo依赖于尚未实现的函数，暂时无法运行")
        print("需要实现以下函数：")
        print("  - init_custom_logger_system_with_params")
        print("  - init_custom_logger_system_from_serializable_config")
        print("  - get_logger_init_params")
        print("  - get_serializable_config")
        return
    
    print("Worker参数化初始化演示")
    print("="*60)
    print("这个演示展示了如何在worker进程中使用参数化初始化")
    print("来避免config_manager重复初始化的问题。")
    
    # 确保temp目录存在
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # 演示传统方式
        demonstrate_traditional_approach()
        
        # 演示参数化方式（推荐）
        demonstrate_params_approach()
        
        # 演示序列化配置方式
        demonstrate_serializable_config_approach()
        
        # 演示性能对比
        demonstrate_performance_comparison()
        
        print("\n" + "="*60)
        print("演示完成！")
        print("="*60)
        print("总结:")
        print("1. 传统方式：每个worker都会初始化config_manager，造成重复初始化")
        print("2. 参数化方式：主进程提取参数，worker直接使用参数，避免重复初始化（推荐）")
        print("3. 序列化配置方式：主进程获取序列化配置，worker直接使用，避免重复初始化")
        print("4. 参数化方式是最轻量级和高效的解决方案")
        print("5. 推荐在多进程环境中优先使用参数化方式")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 