# src/demo/worker_path_demo/demo_debug_caller.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import threading
import inspect
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


def debug_caller_info():
    """调试调用者信息获取"""
    print("\n=== 调用栈分析 ===")
    stack = inspect.stack()
    for i, frame_info in enumerate(stack[:10]):
        filename = os.path.basename(frame_info.filename)
        print(f"Frame {i}: {filename}:{frame_info.lineno} - {frame_info.function}")
    print("=" * 30)
    return


def test_function():
    """测试函数"""
    print(f"\n--- 在 test_function 中调试 (第{inspect.currentframe().f_lineno}行) ---")
    debug_caller_info()

    logger = get_logger("test")
    print(f"即将调用 logger.info (第{inspect.currentframe().f_lineno + 1}行)")
    logger.info("测试消息 - 这应该显示正确的行号")
    return


def worker_function(worker_id: int):
    """Worker函数"""
    print(f"\n--- Worker {worker_id} 调试 ---")
    debug_caller_info()

    logger = get_logger("worker")
    print(f"Worker {worker_id} 即将调用 logger.info (第{inspect.currentframe().f_lineno + 1}行)")
    logger.info(f"Worker {worker_id} 消息")
    return


def main():
    """主函数"""
    print("调用者识别调试")
    print("=" * 40)

    # 创建配置
    config_content = """project_name: debug_test
experiment_name: caller_debug
first_start_time: null
base_dir: d:/logs/debug

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
        init_custom_logger_system(config_path=config_path)

        print(f"\n--- 主函数调试 (第{inspect.currentframe().f_lineno}行) ---")
        debug_caller_info()

        main_logger = get_logger("main")
        print(f"主函数即将调用 logger.info (第{inspect.currentframe().f_lineno + 1}行)")
        main_logger.info("主函数测试消息")

        print("\n=== 测试函数调用 ===")
        test_function()

        print("\n=== 测试线程调用 ===")
        thread = threading.Thread(target=worker_function, args=(1,))
        thread.start()
        thread.join()

        print("\n调试完成！")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)


if __name__ == "__main__":
    main()