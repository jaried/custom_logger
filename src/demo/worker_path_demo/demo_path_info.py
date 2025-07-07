# src/demo/worker_path_demo/demo_path_info.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import threading
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


def worker_task(worker_id: int):
    """Worker任务函数"""
    worker_logger = get_logger("worker")
    worker_logger.info(f"Worker {worker_id} 开始任务")
    worker_logger.info(f"Worker {worker_id} 执行中...")
    worker_logger.info(f"Worker {worker_id} 完成任务")
    return


def main():
    """主函数 - 演示路径信息和调用者识别"""
    print("=" * 60)
    print("路径信息和调用者识别演示")
    print("=" * 60)

    # 创建测试配置
    config_content = """project_name: "path_info_test"
experiment_name: "caller_demo"
first_start_time: null
base_dir: "d:/logs/path_demo"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels: {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        print(f"📋 配置文件: {config_path}")

        # 初始化日志系统
        init_custom_logger_system(config_path=config_path)
        print("✓ 日志系统初始化完成")

        # 获取主logger
        main_logger = get_logger("main")
        main_logger.info("=== 路径信息演示开始 ===")

        # 显示配置信息
        from custom_logger.config import get_root_config
        root_cfg = get_root_config()

        project_name = getattr(root_cfg, 'project_name', 'unknown')
        experiment_name = getattr(root_cfg, 'experiment_name', 'unknown')
        base_dir = getattr(root_cfg, 'base_dir', 'unknown')

        main_logger.info("📁 配置信息:")
        main_logger.info("  项目名称: {}", project_name)
        main_logger.info("  实验名称: {}", experiment_name)
        main_logger.info("  基础目录: {}", base_dir)

        # 获取会话目录
        logger_cfg = root_cfg.logger
        if isinstance(logger_cfg, dict):
            session_dir = logger_cfg.get('current_session_dir')
        else:
            session_dir = getattr(logger_cfg, 'current_session_dir', None)

        if session_dir:
            main_logger.info("  会话目录: {}", session_dir)
            print(f"\n📂 实际日志保存路径: {session_dir}")

            # 显示路径结构分析
            print("\n📋 路径结构分析:")
            print(f"  基础目录: {base_dir}")
            print(f"  项目名称: {project_name}")
            print(f"  实验名称: {experiment_name}")
            print(f"  完整路径: {session_dir}")

            # 检查路径是否包含预期的组件
            if str(base_dir) in str(session_dir):
                print("  ✓ 基础目录匹配")
            else:
                print("  ❌ 基础目录不匹配")

            if str(project_name) in str(session_dir):
                print("  ✓ 项目名称匹配")
            else:
                print("  ❌ 项目名称不匹配")

            if str(experiment_name) in str(session_dir):
                print("  ✓ 实验名称匹配")
            else:
                print("  ❌ 实验名称不匹配")

        main_logger.info("=== 调用者识别测试 ===")

        # 测试不同来源的调用者识别
        def test_function_a():
            test_logger = get_logger("test")
            test_logger.info("来自 test_function_a 的调用")
            return

        def test_function_b():
            test_logger = get_logger("test")
            test_logger.info("来自 test_function_b 的调用")
            return

        main_logger.info("测试函数调用:")
        test_function_a()
        test_function_b()

        main_logger.info("=== Worker线程测试 ===")

        # 启动Worker线程测试
        threads = []
        for i in range(2):
            thread = threading.Thread(target=worker_task, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        main_logger.info("=== 演示完成 ===")

        print("\n" + "=" * 60)
        print("演示结果总结")
        print("=" * 60)
        print(f"✓ 配置文件: {config_path}")
        print(f"✓ 日志路径: {session_dir}")
        print("✓ 调用者识别: 检查上面的日志输出中模块名是否正确")
        print("✓ Worker线程: 多线程日志记录正常")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
        print("✓ 清理完成")


if __name__ == "__main__":
    main()