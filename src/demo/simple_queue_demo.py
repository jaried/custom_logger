#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的队列日志演示

展示新的架构：
1. 主程序：从队列读取日志信息并写入文件
2. Worker进程：自己打印日志到控制台，把需要存文件的信息传给队列
3. 使用Process而不是Pool来避免序列化问题
"""
from __future__ import annotations

import os
import sys
import tempfile
import multiprocessing as mp
import time
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from custom_logger import (
    init_custom_logger_system,
    init_custom_logger_system_for_worker,
    get_logger,
    tear_down_custom_logger_system
)


def worker_process(log_queue, log_dir: str, first_start_time: datetime, worker_id: int):
    """Worker进程函数"""
    try:
        print(f"Worker {worker_id}: 开始初始化")
        
        # 创建worker的配置对象
        class WorkerConfig:
            def __init__(self):
                self.first_start_time = first_start_time
                self.project_name = "简化队列演示"
                self.experiment_name = "simple_queue_demo"
                self.paths = {'log_dir': log_dir}
                self.queue_info = {
                    "log_queue": log_queue,
                    "queue_type": "multiprocessing.Queue",
                    "queue_size": 1000,
                }
                self.logger = {
                    "global_console_level": "info",
                    "global_file_level": "debug",
                    "module_levels": {},
                    "show_call_chain": True,
                    "show_debug_call_stack": False,
                }
        
        worker_config = WorkerConfig()
        
        # 初始化worker的日志系统
        init_custom_logger_system_for_worker(worker_config, f"worker_{worker_id}")
        
        # 获取logger
        logger = get_logger(f"w{worker_id}")
        
        # Worker开始工作
        logger.info(f"Worker {worker_id} 开始工作")
        
        # 执行一些任务
        for i in range(3):
            logger.info(f"Worker {worker_id} 执行任务 {i+1}")
            time.sleep(0.2)
            
            if i == 1:
                logger.warning(f"Worker {worker_id} 任务 {i+1} 有警告")
        
        logger.info(f"Worker {worker_id} 工作完成")
        
        # 清理
        tear_down_custom_logger_system()
        print(f"Worker {worker_id}: 完成")
        
    except Exception as e:
        print(f"Worker {worker_id} 异常: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主程序"""
    print("=== 简化队列日志演示开始 ===")
    
    # 创建临时日志目录
    temp_dir = tempfile.mkdtemp(prefix="simple_queue_demo_")
    log_dir = os.path.join(temp_dir, "logs")
    
    try:
        # 1. 创建多进程队列
        log_queue = mp.Queue(maxsize=1000)
        print(f"创建日志队列")
        
        # 2. 创建配置对象
        first_start_time = datetime.now()
        
        class MainConfig:
            def __init__(self):
                self.first_start_time = first_start_time
                self.project_name = "简化队列演示"
                self.experiment_name = "simple_queue_demo"
                self.paths = {'log_dir': log_dir}
                self.queue_info = {
                    "log_queue": log_queue,
                    "queue_type": "multiprocessing.Queue",
                    "queue_size": 1000,
                }
                self.logger = {
                    "global_console_level": "info",
                    "global_file_level": "debug",
                    "module_levels": {},
                    "show_call_chain": True,
                    "show_debug_call_stack": False,
                }
        
        config_obj = MainConfig()
        
        print(f"配置信息:")
        print(f"  - 日志目录: {config_obj.paths['log_dir']}")
        print(f"  - 启动时间: {config_obj.first_start_time}")
        
        # 3. 主程序初始化日志系统（启用队列接收器）
        print(f"\n主程序初始化日志系统...")
        init_custom_logger_system(config_obj)
        
        # 4. 主程序记录日志
        main_logger = get_logger("main")
        main_logger.info("主程序日志系统初始化完成")
        main_logger.info("队列模式已启用")
        
        # 5. 启动worker进程
        worker_count = 2
        processes = []
        
        main_logger.info(f"启动 {worker_count} 个worker进程")
        print(f"\n启动 {worker_count} 个worker进程...")
        
        for i in range(worker_count):
            p = mp.Process(
                target=worker_process,
                args=(log_queue, log_dir, first_start_time, i)
            )
            p.start()
            processes.append(p)
            main_logger.info(f"Worker {i} 进程已启动")
        
        # 6. 等待所有进程完成
        print(f"\n等待所有worker完成...")
        for i, p in enumerate(processes):
            p.join()
            main_logger.info(f"Worker {i} 进程已完成")
        
        # 7. 等待队列处理完成
        print(f"\n等待队列日志处理完成...")
        time.sleep(1.0)
        
        # 8. 主程序清理
        main_logger.info("所有worker进程已完成")
        main_logger.info("主程序准备退出")
        
        tear_down_custom_logger_system()
        
        print(f"\n=== 演示完成 ===")
        print(f"日志文件保存在: {config_obj.paths['log_dir']}")
        print(f"临时目录: {temp_dir}")
        
        # 显示日志文件内容
        full_log_path = os.path.join(config_obj.paths['log_dir'], "full.log")
        if os.path.exists(full_log_path):
            print(f"\n=== 日志文件内容 ===")
            try:
                with open(full_log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"日志文件共 {len(lines)} 行:")
                    for i, line in enumerate(lines, 1):
                        print(f"{i:2d}: {line.rstrip()}")
            except Exception as e:
                print(f"读取日志文件失败: {e}")
        
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理临时目录（可选）
        try:
            import shutil
            # shutil.rmtree(temp_dir)  # 注释掉以便查看日志文件
            pass
        except:
            pass


if __name__ == "__main__":
    # 设置多进程启动方法
    mp.set_start_method('spawn', force=True)
    main() 