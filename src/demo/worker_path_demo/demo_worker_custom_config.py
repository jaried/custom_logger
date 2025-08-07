# src/demo/worker_path_demo/demo_worker_custom_config.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


def create_custom_config_file():
    """创建自定义配置文件"""
    # 创建demo专用的配置目录
    demo_config_dir = os.path.join("src", "demo", "worker_path_demo", "config")
    os.makedirs(demo_config_dir, exist_ok=True)

    # 创建自定义配置文件
    custom_config_path = os.path.join(demo_config_dir, "worker_demo_config.yaml")

    config_content = """# Worker Demo自定义配置文件
project_name: "worker_demo_project"
experiment_name: "custom_worker_test"
first_start_time: null
base_dir: "d:/logs/demo"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    main_process:
      console_level: "info"
      file_level: "debug"
    thread_worker:
      console_level: "w_summary"
      file_level: "w_detail"
    process_worker:
      console_level: "w_summary" 
      file_level: "debug"
"""

    with open(custom_config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)

    return custom_config_path


def thread_worker_function(worker_id: int, task_count: int):
    """线程Worker函数"""
    # Worker直接获取logger，无需重新初始化
    worker_logger = get_logger("thread_worker", console_level="w_summary")

    worker_logger.worker_summary(f"线程Worker {worker_id} 启动，处理 {task_count:,} 个任务")

    for i in range(task_count):
        if i % 50 == 0:  # 每50个任务记录一次详细日志
            worker_logger.worker_detail(f"Thread-{worker_id} 处理任务 {i + 1:,}/{task_count:,}")
        time.sleep(0.01)  # 模拟工作

    worker_logger.worker_summary(f"线程Worker {worker_id} 完成所有任务")
    return f"Thread-{worker_id} completed {task_count:,} tasks"


def process_worker_function(worker_id: int, task_count: int):
    """进程Worker函数"""
    # 进程中获取logger（会自动继承配置）
    worker_logger = get_logger("process_worker", console_level="w_summary")

    worker_logger.worker_summary(f"进程Worker {worker_id} 启动，处理 {task_count:,} 个任务")

    for i in range(task_count):
        if i % 25 == 0:  # 每25个任务记录一次详细日志
            worker_logger.worker_detail(f"Process-{worker_id} 处理任务 {i + 1:,}/{task_count:,}")
        time.sleep(0.02)  # 模拟工作

    worker_logger.worker_summary(f"进程Worker {worker_id} 完成所有任务")
    return f"Process-{worker_id} completed {task_count:,} tasks"


def demo_custom_config_workers():
    """演示使用自定义配置的Workers"""
    print("\n" + "=" * 80)
    print("Worker自定义配置演示")
    print("=" * 80)

    # 创建自定义配置文件
    custom_config_path = create_custom_config_file()
    print(f"✓ 创建自定义配置文件: {custom_config_path}")

    try:
        # 使用自定义配置初始化日志系统
        init_custom_logger_system(config_path=custom_config_path)
        print("✓ 日志系统初始化完成（使用自定义配置）")

        # 获取主进程logger
        main_logger = get_logger("main_process")
        main_logger.info("Worker演示程序启动")
        main_logger.info("配置文件路径: {}", custom_config_path)

        # 显示配置信息
        from custom_logger.config import get_root_config
        root_cfg = get_root_config()
        main_logger.info("项目名称: {}", getattr(root_cfg, 'project_name', 'unknown'))
        main_logger.info("实验名称: {}", getattr(root_cfg, 'experiment_name', 'unknown'))
        main_logger.info("日志基础目录: {}", getattr(root_cfg, 'base_dir', 'unknown'))

        # 显示会话目录
        logger_cfg = root_cfg.logger
        if isinstance(logger_cfg, dict):
            session_dir = logger_cfg.get('current_session_dir')
        else:
            session_dir = getattr(logger_cfg, 'current_session_dir', None)

        if session_dir:
            main_logger.info("当前会话目录: {}", session_dir)
            print(f"📁 日志将保存到: {session_dir}")

            # 验证目录是否存在
            if os.path.exists(session_dir):
                print("✓ 会话目录已创建")
            else:
                print("❌ 会话目录不存在")

        print("\n" + "-" * 60)
        print("开始多线程Worker演示")
        print("-" * 60)

        # 多线程Worker演示
        main_logger.info("启动多线程Worker任务")
        with ThreadPoolExecutor(max_workers=3) as executor:
            thread_futures = []
            for i in range(3):
                future = executor.submit(thread_worker_function, i, 100)
                thread_futures.append(future)

            # 等待线程完成
            for future in thread_futures:
                result = future.result()
                main_logger.info("线程任务完成: {}", result)

        print("\n" + "-" * 60)
        print("开始多进程Worker演示")
        print("-" * 60)

        # 多进程Worker演示
        main_logger.info("启动多进程Worker任务")
        with ProcessPoolExecutor(max_workers=2) as executor:
            process_futures = []
            for i in range(2):
                future = executor.submit(process_worker_function, i, 50)
                process_futures.append(future)

            # 等待进程完成
            for future in process_futures:
                result = future.result()
                main_logger.info("进程任务完成: {}", result)

        main_logger.info("所有Worker任务完成")

        # 等待文件写入完成
        time.sleep(2)

        print("\n" + "=" * 80)
        print("验证日志文件")
        print("=" * 80)

        # 验证日志文件
        if session_dir and os.path.exists(session_dir):
            full_log_path = os.path.join(session_dir, "full.log")
            warning_log_path = os.path.join(session_dir, "warning.log")
            error_log_path = os.path.join(session_dir, "error.log")

            if os.path.exists(full_log_path):
                file_size = os.path.getsize(full_log_path)
                print(f"✓ 完整日志文件: {full_log_path}")
                print(f"  文件大小: {file_size:,} 字节")

                # 显示日志文件的最后几行
                try:
                    with open(full_log_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"  总行数: {len(lines):,} 行")
                            print("  最后5行日志:")
                            for line in lines[-5:]:
                                print(f"    {line.strip()}")
                except Exception as e:
                    print(f"  读取日志文件时出错: {e}")
            else:
                print(f"❌ 完整日志文件不存在: {full_log_path}")

            if os.path.exists(error_log_path):
                error_size = os.path.getsize(error_log_path)
                print(f"✓ 错误日志文件: {error_log_path}")
                print(f"  文件大小: {error_size:,} 字节")
            else:
                print(f"✓ 错误日志文件为空（正常，因为没有错误日志）")

        print("\n" + "=" * 80)
        print("Worker配置继承验证")
        print("=" * 80)

        # 验证Worker是否正确继承了配置
        main_logger.info("验证Worker配置继承...")

        # 创建测试Worker验证配置
        test_worker = get_logger("thread_worker")
        main_logger.info("测试Worker控制台级别: {}", test_worker.console_level)
        main_logger.info("测试Worker文件级别: {}", test_worker.file_level)

        # 显示环境变量（用于多进程配置继承）
        env_config_path = os.environ.get('CUSTOM_LOGGER_CONFIG_PATH')
        if env_config_path:
            main_logger.info("环境变量配置路径: {}", env_config_path)
            print(f"✓ 环境变量已设置，支持多进程配置继承")
        else:
            print("❌ 环境变量未设置")

    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理日志系统
        tear_down_custom_logger_system()
        print("\n✓ 日志系统已清理")

        # 清理临时配置文件（可选）
        # os.unlink(custom_config_path)
        print(f"✓ 自定义配置文件保留: {custom_config_path}")


def demo_config_comparison():
    """演示配置对比"""
    print("\n" + "=" * 80)
    print("配置对比演示")
    print("=" * 80)

    # 显示默认配置路径
    from custom_logger.config import get_config_file_path, set_config_path

    # 清理状态
    set_config_path(None)
    default_path = get_config_file_path()
    print(f"默认配置路径: {default_path}")

    # 显示自定义配置路径
    custom_path = create_custom_config_file()
    set_config_path(custom_path)
    current_path = get_config_file_path()
    print(f"自定义配置路径: {current_path}")

    # 清理
    set_config_path(None)


def main():
    """主函数"""
    print("Worker自定义配置演示程序")
    print("本演示将展示:")
    print("1. 使用自定义配置文件初始化日志系统")
    print("2. 多线程Worker日志记录")
    print("3. 多进程Worker日志记录")
    print("4. Worker配置继承验证")
    print("5. 日志文件验证")

    try:
        # 配置对比演示
        demo_config_comparison()

        # 主要演示
        demo_custom_config_workers()

        print("\n" + "=" * 80)
        print("演示完成！")
        print("=" * 80)
        print("请检查生成的日志文件以验证Worker日志是否正确保存。")
        print("日志文件位置: d:/logs/demo/worker_demo_project/custom_worker_test/logs/")

    except KeyboardInterrupt:
        print("\n用户中断演示")
    except Exception as e:
        print(f"\n演示失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()