#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新API演示：展示如何使用新的custom_logger API

主要变更：
1. init_custom_logger_system 只接收 config_object 参数
2. 新增 init_custom_logger_system_for_worker 用于worker进程
3. 取消 first_start_time 参数支持，必须从 config.first_start_time 获取
4. 支持队列信息传递给worker
"""
from __future__ import annotations

import os
import sys
import tempfile
import multiprocessing as mp
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


class ConfigObject:
    """模拟config_manager的config对象"""
    
    def __init__(self, log_dir: str, first_start_time: datetime, queue_info: dict = None):
        self.first_start_time = first_start_time
        self.project_name = "新API演示"
        self.experiment_name = "new_api_demo"
        
        # 使用paths结构，符合config_manager的格式
        self.paths = {
            'log_dir': log_dir
        }
        
        # 队列信息，用于worker进程
        self.queue_info = queue_info or {}
        
        # logger配置
        self.logger = {
            "global_console_level": "info",
            "global_file_level": "debug",
            "module_levels": {},
            "show_call_chain": True,
            "show_debug_call_stack": False,
        }


class SerializableConfigObject:
    """可序列化的配置对象，用于worker进程"""
    
    def __init__(self, config_obj: ConfigObject):
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


def worker_function(serializable_config, worker_id: int):
    """Worker进程函数"""
    try:
        print(f"Worker {worker_id}: 开始初始化日志系统")
        
        # 使用新的worker初始化函数
        init_custom_logger_system_for_worker(serializable_config)
        
        # 获取logger
        logger = get_logger(f"work_{worker_id}")
        
        # 检查队列信息
        if hasattr(serializable_config, 'queue_info') and serializable_config.queue_info:
            logger.info(f"Worker {worker_id} 接收到队列信息: {serializable_config.queue_info}")
        
        # 记录一些日志
        logger.info(f"Worker {worker_id} 开始工作")
        logger.debug(f"Worker {worker_id} 调试信息")
        logger.warning(f"Worker {worker_id} 警告信息")
        logger.info(f"Worker {worker_id} 工作完成")
        
        # 清理
        tear_down_custom_logger_system()
        
        return f"Worker {worker_id} 成功完成"
        
    except Exception as e:
        return f"Worker {worker_id} 失败: {str(e)}"


def main():
    """主程序演示"""
    print("=== 新API演示开始 ===")
    
    # 创建临时日志目录
    temp_dir = tempfile.mkdtemp(prefix="new_api_demo_")
    log_dir = os.path.join(temp_dir, "logs")
    
    try:
        # 1. 创建配置对象
        first_start_time = datetime.now()
        queue_info = {
            "queue_type": "multiprocessing.Queue",
            "queue_size": 1000,
            "worker_count": 2,
            "batch_size": 10
        }
        
        config_obj = ConfigObject(
            log_dir=log_dir,
            first_start_time=first_start_time,
            queue_info=queue_info
        )
        
        print(f"创建配置对象:")
        print(f"  - log_dir: {config_obj.paths['log_dir']}")
        print(f"  - first_start_time: {config_obj.first_start_time}")
        print(f"  - queue_info: {config_obj.queue_info}")
        
        # 2. 主程序初始化日志系统（使用新API）
        print("\n主程序初始化日志系统...")
        init_custom_logger_system(config_obj)
        
        # 3. 主程序记录日志
        main_logger = get_logger("main")
        main_logger.info("主程序日志系统初始化完成")
        main_logger.info(f"准备启动 {queue_info['worker_count']} 个worker进程")
        
        # 4. 创建可序列化的配置对象
        serializable_config = SerializableConfigObject(config_obj)
        
        # 5. 启动worker进程
        print(f"\n启动 {queue_info['worker_count']} 个worker进程...")
        with mp.Pool(processes=queue_info['worker_count']) as pool:
            results = pool.starmap(
                worker_function,
                [(serializable_config, i) for i in range(queue_info['worker_count'])]
            )
        
        # 6. 处理结果
        main_logger.info("所有worker进程完成")
        for result in results:
            main_logger.info(f"Worker结果: {result}")
            print(f"Worker结果: {result}")
        
        # 7. 主程序清理
        main_logger.info("主程序准备退出")
        tear_down_custom_logger_system()
        
        print(f"\n日志文件保存在: {config_obj.paths['log_dir']}")
        print("=== 新API演示完成 ===")
        
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