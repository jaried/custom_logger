# src/demo/worker_path_demo/demo_caller_test.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import threading
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


def function_a():
    """测试函数A"""
    logger = get_logger("test")
    logger.info("这是来自 function_a 的调用")  # 这行应该显示正确的行号
    return


def function_b():
    """测试函数B"""
    logger = get_logger("test")
    logger.info("这是来自 function_b 的调用")  # 这行应该显示正确的行号
    return


def worker_thread(worker_id: int):
    """Worker线程函数"""
    logger = get_logger("worker")
    logger.info(f"Worker {worker_id} 开始")  # 这行应该显示正确的行号
    logger.info(f"Worker {worker_id} 工作中")  # 这行应该显示正确的行号
    logger.info(f"Worker {worker_id} 完成")  # 这行应该显示正确的行号
    return


def main():
    """主函数"""
    print("调用者识别测试")
    print("=" * 40)

    # 创建简单配置
    config_content = """project_name: caller_test
experiment_name: line_number_test
first_start_time: null
base_dir: d:/logs/caller_test

logger:
  global_console_level: info
  global_file_level: debug
  current_session_dir: null
  module_levels: {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        # 初始化日志系统
        init_custom_logger_system(config_path=config_path)
        print("✓ 日志系统初始化完成")

        # 主函数调用测试
        main_logger = get_logger("main")
        main_logger.info("=== 主函数调用测试 ===")  # 第51行
        main_logger.info("这是主函数的第一条日志")  # 第52行
        main_logger.info("这是主函数的第二条日志")  # 第53行

        print("\n--- 测试函数调用 ---")
        function_a()  # 应该显示function_a内部的行号
        function_b()  # 应该显示function_b内部的行号

        print("\n--- 测试线程调用 ---")
        threads = []
        for i in range(2):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        main_logger.info("=== 测试完成 ===")  # 第67行

        print("\n调用者识别测试完成!")
        print("请检查上面的日志输出：")
        print("1. 主函数的日志应该显示 'demo_cal' 模块名和正确的行号")
        print("2. function_a 和 function_b 应该显示正确的行号")
        print("3. worker线程应该显示 'threadin' 模块名和正确的行号")

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