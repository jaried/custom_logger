# src/demo/worker_path_demo/demo_verify_caller_fix.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import threading
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


def test_main_function():
    """测试主函数调用者识别"""
    logger = get_logger("main")
    print("=== 主函数测试 ===")
    logger.info("主函数第26行 - 应该显示demo_ver模块名和行号26")  # 第26行
    logger.info("主函数第27行 - 应该显示demo_ver模块名和行号27")  # 第27行
    return


def test_function_calls():
    """测试函数调用者识别"""
    print("\n=== 函数调用测试 ===")

    def function_a():
        logger = get_logger("func_a")
        logger.info("function_a第35行 - 应该显示demo_ver和行号35")  # 第35行
        return

    def function_b():
        logger = get_logger("func_b")
        logger.info("function_b第39行 - 应该显示demo_ver和行号39")  # 第39行
        return

    function_a()
    function_b()
    return


def worker_thread_function(worker_id: int):
    """Worker线程函数"""
    logger = get_logger("worker")
    logger.info(f"Worker线程第48行 - Worker {worker_id} 应该显示demo_ver和行号48")  # 第48行
    logger.info(f"Worker线程第49行 - Worker {worker_id} 应该显示demo_ver和行号49")  # 第49行
    return


def test_thread_calls():
    """测试线程调用者识别"""
    print("\n=== 线程调用测试 ===")

    threads = []
    for i in range(2):
        thread = threading.Thread(target=worker_thread_function, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    return


def main():
    """主函数"""
    print("调用者识别修复验证")
    print("=" * 50)

    # 创建测试配置
    config_content = """project_name: verify_caller_fix
experiment_name: test
first_start_time: null
base_dir: d:/logs/verify

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

        # 运行各种测试
        test_main_function()
        test_function_calls()
        test_thread_calls()

        print("\n" + "=" * 50)
        print("验证完成！")
        print("请检查上面的日志输出：")
        print("1. 模块名应该是 'demo_ver' (而不是 'unknown' 或 'threadin')")
        print("2. 行号应该匹配注释中标注的行号")
        print("3. Worker线程应该显示正确的文件名和行号")

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
