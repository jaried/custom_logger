# docs/05_预研/验证_20260202/verify_us002_worker_process.py
"""
验证 US-002：worker进程场景下的动态模块名

验证目标：
1. worker进程调用logger时，显示worker模块名（不是主进程模块名）
2. 队列模式下的日志正确显示worker模块名
"""

import sys
import os
import multiprocessing as mp
import tempfile
import shutil
from datetime import datetime

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../..", "src"))

from custom_logger import init_custom_logger_system, get_logger


def worker_function(worker_id: int, log_queue: mp.Queue, config_dict: dict):
    """worker进程函数"""
    # 在worker进程中初始化logger
    from custom_logger import init_custom_logger_system_for_worker

    init_custom_logger_system_for_worker(config_dict)

    # 获取logger
    worker_logger = get_logger(f"worker_{worker_id}")

    # 测试1：worker调用自己的logger
    worker_logger.info(f"Worker {worker_id} 消息（自己的logger）")

    # 测试2：worker使用主程序传入的logger（如果支持）
    # 注意：由于logger对象不能直接跨进程传递，这个场景需要特殊处理

    # 测试3：不同函数调用
    worker_sub_function(worker_logger)


def worker_sub_function(logger):
    """worker子函数"""
    logger.info("Worker子函数消息")


def verify_worker_scenario():
    """验证worker进程场景"""
    print("=" * 60)
    print("验证 US-002：worker进程场景")
    print("=" * 60)

    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="verify_us002_worker_")
    log_dir = os.path.join(temp_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 配置对象
    class Config:
        first_start_time = datetime.now()
        class paths:
            work_dir = temp_dir
            log_dir = log_dir
        class logger:
            enable_queue_mode = True
            global_console_level = 'debug'
            global_file_level = 'debug'

    # 创建队列
    log_queue = mp.Queue()

    # 初始化主程序logger系统
    init_custom_logger_system(Config())

    # 设置队列
    from custom_logger.queue_writer import set_queue_sender
    set_queue_sender(log_queue)

    # 启动队列接收器
    from custom_logger.queue_writer import QueueLogReceiver
    receiver = QueueLogReceiver(log_queue, log_dir)
    receiver.start_receiving()

    print("\n[主程序] 启动worker进程...")

    # 准备worker配置
    config_dict = {
        'paths': {'work_dir': temp_dir, 'log_dir': log_dir},
        'logger': {
            'enable_queue_mode': True,
            'global_console_level': 'debug',
            'global_file_level': 'debug'
        },
        'first_start_time': datetime.now().isoformat()
    }

    # 启动worker进程
    processes = []
    for i in range(2):
        p = mp.Process(target=worker_function, args=(i, log_queue, config_dict))
        p.start()
        processes.append(p)

    # 等待worker完成
    for p in processes:
        p.join()

    print("\n[主程序] Worker进程完成")

    # 等待队列处理完成
    import time
    time.sleep(1)

    # 停止接收器
    receiver.stop_receiving()

    # 读取日志文件验证
    print("\n" + "=" * 60)
    print("日志文件验证")
    print("=" * 60)

    log_files = []
    for f in os.listdir(log_dir):
        if f.endswith('.log') and 'info' in f.lower():
            log_files.append(os.path.join(log_dir, f))

    if log_files:
        log_file = log_files[0]
        print(f"\n日志文件: {log_file}")
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print("\n日志内容:")
            print("-" * 40)
            for line in content.strip().split('\n')[-10:]:  # 显示最后10行
                print(f"  {line}")
            print("-" * 40)

    # 分析模块名
    print("\n分析结果:")
    print("期望：日志中应显示 'verify_us002_worker' 而非主程序模块名")

    # 清理
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass

    print("\n" + "=" * 60)
    print("验证完成")
    print("=" * 60)


if __name__ == "__main__":
    # Windows下multiprocessing需要特殊处理
    mp.set_start_method('spawn', force=True)
    verify_worker_scenario()
