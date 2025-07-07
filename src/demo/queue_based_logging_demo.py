#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于队列的日志处理演示

展示如何实现：
1. 主程序将日志写入队列
2. Worker进程从队列读取日志并处理
3. 使用新的custom_logger API
"""
from __future__ import annotations

import os
import sys
import tempfile
import multiprocessing as mp
import queue
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from custom_logger import (
    init_custom_logger_system,
    init_custom_logger_system_for_worker,
    get_logger,
    tear_down_custom_logger_system
)


class QueueBasedConfigObject:
    """支持队列的配置对象"""
    
    def __init__(self, log_dir: str, first_start_time: datetime, log_queue: mp.Queue = None):
        self.first_start_time = first_start_time
        self.project_name = "队列日志演示"
        self.experiment_name = "queue_demo"
        
        # 使用paths结构，符合config_manager的格式
        self.paths = {
            'log_dir': log_dir
        }
        
        # 队列信息，用于worker进程
        self.queue_info = {
            "log_queue": log_queue,  # 实际的队列对象
            "queue_type": "multiprocessing.Queue",
            "queue_size": 1000,
            "worker_count": 2,
            "batch_size": 10
        }
        
        # logger配置
        self.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
            "module_levels": {},
            "show_call_chain": True,
            "show_debug_call_stack": False,
        }


class SerializableQueueConfigObject:
    """可序列化的队列配置对象，用于worker进程"""
    
    def __init__(self, config_obj: QueueBasedConfigObject):
        # 复制基本属性
        self.first_start_time = config_obj.first_start_time
        self.project_name = config_obj.project_name
        self.experiment_name = config_obj.experiment_name
        
        # 复制paths结构
        self.paths = config_obj.paths.copy()
        
        # 复制队列信息（注意：实际队列对象会在进程间传递）
        self.queue_info = config_obj.queue_info.copy()
        
        # 复制logger配置
        self.logger = config_obj.logger.copy()
    
    def __getstate__(self):
        """支持pickle序列化"""
        return self.__dict__
    
    def __setstate__(self, state):
        """支持pickle反序列化"""
        self.__dict__.update(state)


def log_queue_worker(serializable_config, worker_id: int):
    """队列日志处理worker"""
    try:
        print(f"Worker {worker_id}: 开始初始化日志系统")
        
        # 使用新的worker初始化函数
        init_custom_logger_system_for_worker(serializable_config)
        
        # 获取logger
        logger = get_logger(f"qwork{worker_id}")
        
        # 获取队列
        log_queue = serializable_config.queue_info.get("log_queue")
        if log_queue is None:
            logger.error(f"Worker {worker_id}: 没有找到日志队列")
            return f"Worker {worker_id} 失败: 没有队列"
        
        logger.info(f"Worker {worker_id} 开始处理队列日志")
        
        processed_count = 0
        while True:
            try:
                # 从队列获取日志消息
                log_message = log_queue.get(timeout=2.0)
                
                # 检查结束标记
                if log_message == "STOP":
                    logger.info(f"Worker {worker_id} 收到停止信号")
                    break
                
                # 处理日志消息
                if isinstance(log_message, dict):
                    level = log_message.get("level", "info")
                    message = log_message.get("message", "")
                    source = log_message.get("source", "unknown")
                    
                    # 根据级别记录日志
                    if level == "debug":
                        logger.debug(f"[来自{source}] {message}")
                    elif level == "info":
                        logger.info(f"[来自{source}] {message}")
                    elif level == "warning":
                        logger.warning(f"[来自{source}] {message}")
                    elif level == "error":
                        logger.error(f"[来自{source}] {message}")
                    else:
                        logger.info(f"[来自{source}] {message}")
                    
                    processed_count += 1
                else:
                    # 简单字符串消息
                    logger.info(f"[队列消息] {log_message}")
                    processed_count += 1
                
            except queue.Empty:
                logger.debug(f"Worker {worker_id} 队列超时，继续等待...")
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} 处理队列消息时出错: {e}")
                break
        
        logger.info(f"Worker {worker_id} 完成，共处理 {processed_count} 条消息")
        
        # 清理
        tear_down_custom_logger_system()
        
        return f"Worker {worker_id} 成功完成，处理了 {processed_count} 条消息"
        
    except Exception as e:
        return f"Worker {worker_id} 失败: {str(e)}"


def main():
    """主程序演示"""
    print("=== 基于队列的日志处理演示开始 ===")
    
    # 创建临时日志目录
    temp_dir = tempfile.mkdtemp(prefix="queue_log_demo_")
    log_dir = os.path.join(temp_dir, "logs")
    
    try:
        # 1. 创建多进程队列
        log_queue = mp.Queue(maxsize=1000)
        
        # 2. 创建配置对象
        first_start_time = datetime.now()
        config_obj = QueueBasedConfigObject(
            log_dir=log_dir,
            first_start_time=first_start_time,
            log_queue=log_queue
        )
        
        print(f"创建配置对象:")
        print(f"  - log_dir: {config_obj.paths['log_dir']}")
        print(f"  - first_start_time: {config_obj.first_start_time}")
        print(f"  - queue_info: {config_obj.queue_info}")
        
        # 3. 主程序初始化日志系统
        print("\n主程序初始化日志系统...")
        init_custom_logger_system(config_obj)
        
        # 4. 主程序记录日志
        main_logger = get_logger("main")
        main_logger.info("主程序日志系统初始化完成")
        main_logger.info("准备启动队列处理worker")
        
        # 5. 创建可序列化的配置对象
        serializable_config = SerializableQueueConfigObject(config_obj)
        
        # 6. 启动worker进程
        worker_count = 2
        print(f"\n启动 {worker_count} 个队列处理worker...")
        
        with mp.Pool(processes=worker_count) as pool:
            # 启动worker进程（异步）
            worker_results = pool.starmap_async(
                log_queue_worker,
                [(serializable_config, i) for i in range(worker_count)]
            )
            
            # 7. 主程序向队列写入日志消息
            print("\n主程序开始向队列写入日志消息...")
            main_logger.info("开始向队列写入消息")
            
            # 模拟不同来源的日志消息
            log_messages = [
                {"level": "info", "message": "系统启动完成", "source": "system"},
                {"level": "debug", "message": "调试信息：内存使用情况", "source": "monitor"},
                {"level": "warning", "message": "磁盘空间不足", "source": "storage"},
                {"level": "info", "message": "用户登录成功", "source": "auth"},
                {"level": "error", "message": "数据库连接失败", "source": "database"},
                {"level": "info", "message": "任务处理完成", "source": "task_manager"},
                "简单的字符串消息",
                {"level": "info", "message": "批处理任务开始", "source": "batch"},
                {"level": "debug", "message": "性能统计数据", "source": "performance"},
                {"level": "info", "message": "系统准备关闭", "source": "system"},
            ]
            
            for i, msg in enumerate(log_messages):
                log_queue.put(msg)
                main_logger.info(f"向队列写入消息 {i+1}: {msg}")
                time.sleep(0.1)  # 模拟消息间隔
            
            # 8. 发送停止信号
            print("\n发送停止信号给worker...")
            for i in range(worker_count):
                log_queue.put("STOP")
            
            main_logger.info("已发送停止信号给所有worker")
            
            # 9. 等待worker完成
            print("\n等待worker完成...")
            results = worker_results.get(timeout=30)
        
        # 10. 处理结果
        main_logger.info("所有worker完成")
        for result in results:
            main_logger.info(f"Worker结果: {result}")
            print(f"Worker结果: {result}")
        
        # 11. 主程序清理
        main_logger.info("主程序准备退出")
        tear_down_custom_logger_system()
        
        print(f"\n日志文件保存在: {config_obj.paths['log_dir']}")
        print("=== 基于队列的日志处理演示完成 ===")
        
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理临时目录（可选）
        try:
            import shutil
            # shutil.rmtree(temp_dir)  # 注释掉以便查看日志文件
            print(f"临时目录: {temp_dir}")
        except:
            pass


if __name__ == "__main__":
    # 设置多进程启动方法
    mp.set_start_method('spawn', force=True)
    main() 