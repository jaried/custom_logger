#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的队列日志演示

展示新的架构：
1. 主程序：从队列读取日志信息并写入文件
2. Worker进程：自己打印日志到控制台，把需要存文件的信息传给队列
3. 使用config.paths.log_dir作为工作路径
4. 使用config.first_start_time用于计时
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


class QueueConfigObject:
    """支持队列的配置对象"""
    
    def __init__(self, log_dir: str, first_start_time: datetime, log_queue: mp.Queue):
        self.first_start_time = first_start_time
        self.project_name = "完整队列演示"
        self.experiment_name = "complete_queue_demo"
        
        # 使用paths结构，符合config_manager的格式
        self.paths = {
            'log_dir': log_dir
        }
        
        # 队列信息，包含实际的队列对象
        self.queue_info = {
            "log_queue": log_queue,
            "queue_type": "multiprocessing.Queue",
            "queue_size": 1000,
            "description": "主程序从队列读取并写文件，worker发送到队列"
        }
        
        # logger配置
        self.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
            "module_levels": {},
            "show_call_chain": True,
            "show_debug_call_stack": False,
        }


class SerializableQueueConfig:
    """可序列化的队列配置对象"""
    
    def __init__(self, config_obj: QueueConfigObject):
        # 复制基本属性
        self.first_start_time = config_obj.first_start_time
        self.project_name = config_obj.project_name
        self.experiment_name = config_obj.experiment_name
        
        # 复制paths结构
        self.paths = config_obj.paths.copy()
        
        # 复制队列信息
        self.queue_info = config_obj.queue_info.copy()
        
        # 复制logger配置
        self.logger = config_obj.logger.copy()
    
    def __getstate__(self):
        """支持pickle序列化"""
        return self.__dict__
    
    def __setstate__(self, state):
        """支持pickle反序列化"""
        self.__dict__.update(state)


def worker_task(log_queue, log_dir: str, first_start_time: datetime, worker_id: int, task_count: int):
    """Worker任务函数"""
    try:
        print(f"\n=== Worker {worker_id} 开始 ===")
        
        # 创建worker的配置对象
        class WorkerConfig:
            def __init__(self):
                self.first_start_time = first_start_time
                self.project_name = "完整队列演示"
                self.experiment_name = "complete_queue_demo"
                self.paths = {'log_dir': log_dir}
                self.queue_info = {
                    "log_queue": log_queue,
                    "queue_type": "multiprocessing.Queue",
                    "queue_size": 1000,
                    "description": "worker发送到队列"
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
        logger.info(f"Worker {worker_id} 开始执行 {task_count} 个任务")
        
        # 模拟执行多个任务
        for task_id in range(task_count):
            logger.debug(f"Worker {worker_id} 开始任务 {task_id + 1}")
            
            # 模拟任务处理
            time.sleep(0.1)
            
            # 根据任务ID模拟不同的日志级别
            if task_id % 5 == 0:
                logger.warning(f"Worker {worker_id} 任务 {task_id + 1} 遇到警告")
            elif task_id % 7 == 0:
                logger.error(f"Worker {worker_id} 任务 {task_id + 1} 遇到错误")
            else:
                logger.info(f"Worker {worker_id} 任务 {task_id + 1} 完成")
        
        logger.info(f"Worker {worker_id} 所有任务完成")
        
        # 清理worker的日志系统
        tear_down_custom_logger_system()
        
        print(f"=== Worker {worker_id} 结束 ===\n")
        return f"Worker {worker_id} 成功完成 {task_count} 个任务"
        
    except Exception as e:
        print(f"Worker {worker_id} 发生异常: {e}")
        import traceback
        traceback.print_exc()
        return f"Worker {worker_id} 失败: {str(e)}"


def main():
    """主程序"""
    print("=== 完整队列日志演示开始 ===")
    
    # 创建临时日志目录
    temp_dir = tempfile.mkdtemp(prefix="complete_queue_demo_")
    log_dir = os.path.join(temp_dir, "logs")
    
    try:
        # 1. 创建多进程队列
        log_queue = mp.Queue(maxsize=1000)
        print(f"创建日志队列，最大容量: 1000")
        
        # 2. 创建配置对象
        first_start_time = datetime.now()
        config_obj = QueueConfigObject(
            log_dir=log_dir,
            first_start_time=first_start_time,
            log_queue=log_queue
        )
        
        print(f"\n配置信息:")
        print(f"  - 项目名: {config_obj.project_name}")
        print(f"  - 实验名: {config_obj.experiment_name}")
        print(f"  - 日志目录: {config_obj.paths['log_dir']}")
        print(f"  - 启动时间: {config_obj.first_start_time}")
        print(f"  - 队列信息: {config_obj.queue_info['description']}")
        
        # 3. 主程序初始化日志系统（启用队列接收器）
        print(f"\n主程序初始化日志系统...")
        init_custom_logger_system(config_obj)
        
        # 4. 主程序记录日志
        main_logger = get_logger("main")
        main_logger.info("主程序日志系统初始化完成")
        main_logger.info("队列模式已启用：主程序接收队列日志并写入文件")
        
        # 5. 启动多个worker进程
        worker_count = 3
        tasks_per_worker = 5
        
        main_logger.info(f"准备启动 {worker_count} 个worker进程，每个执行 {tasks_per_worker} 个任务")
        print(f"\n启动 {worker_count} 个worker进程...")
        
        # 使用进程池启动worker，直接传递队列对象
        with mp.Pool(processes=worker_count) as pool:
            # 启动所有worker（异步）
            worker_results = pool.starmap_async(
                worker_task,
                [(log_queue, log_dir, first_start_time, i, tasks_per_worker) for i in range(worker_count)]
            )
            
            # 主程序继续记录日志
            main_logger.info("所有worker进程已启动")
            
            # 等待一段时间，让worker开始工作
            time.sleep(0.5)
            main_logger.info("Worker进程正在执行任务...")
            
            # 等待所有worker完成
            print(f"\n等待所有worker完成...")
            results = worker_results.get(timeout=60)
        
        # 6. 处理结果
        main_logger.info("所有worker进程已完成")
        for result in results:
            main_logger.info(f"结果: {result}")
            print(f"结果: {result}")
        
        # 7. 等待一下，确保所有队列日志都被处理
        print(f"\n等待队列日志处理完成...")
        time.sleep(1.0)
        
        # 8. 主程序清理
        main_logger.info("主程序准备退出")
        main_logger.info("演示完成，正在清理资源")
        
        tear_down_custom_logger_system()
        
        print(f"\n=== 演示完成 ===")
        print(f"日志文件保存在: {config_obj.paths['log_dir']}")
        print(f"临时目录: {temp_dir}")
        
        # 显示日志文件内容
        full_log_path = os.path.join(config_obj.paths['log_dir'], "full.log")
        if os.path.exists(full_log_path):
            print(f"\n=== 日志文件内容预览 ===")
            try:
                with open(full_log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"日志文件共 {len(lines)} 行")
                    if len(lines) > 10:
                        print("前10行:")
                        for i, line in enumerate(lines[:10]):
                            print(f"{i+1:2d}: {line.rstrip()}")
                        print("...")
                        print("后5行:")
                        for i, line in enumerate(lines[-5:], len(lines)-4):
                            print(f"{i:2d}: {line.rstrip()}")
                    else:
                        for i, line in enumerate(lines):
                            print(f"{i+1:2d}: {line.rstrip()}")
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