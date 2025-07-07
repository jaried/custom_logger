# src/demo/worker_path_demo/demo_simple_test.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import threading
import time
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


def worker_function(worker_id: int):
    """简单的Worker函数"""
    worker_logger = get_logger("worker")

    worker_logger.info(f"Worker {worker_id} 开始执行")

    for i in range(5):
        worker_logger.info(f"Worker {worker_id} 步骤 {i + 1}")
        time.sleep(0.1)

    worker_logger.info(f"Worker {worker_id} 完成")
    return


def main():
    """主函数"""
    print("简单Worker测试")
    print("=" * 40)

    # 创建临时目录和配置
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建简单配置
        config_content = f"""project_name: simple_test
experiment_name: worker_demo  
first_start_time: null
base_dir: {temp_dir.replace(os.sep, '/')}

logger:
  global_console_level: info
  global_file_level: debug
  current_session_dir: null
  module_levels: {{}}
"""

        config_file = os.path.join(temp_dir, "config.yaml")
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)

        print(f"✓ 创建配置: {config_file}")
        print(f"✓ 日志目录: {temp_dir}")

        try:
            # 初始化日志系统
            init_custom_logger_system(config_path=config_file)
            print("✓ 日志系统初始化成功")

            # 创建主logger
            main_logger = get_logger("main")
            main_logger.info("简单测试开始")

            # 启动几个Worker线程
            print("\n启动Worker线程...")
            threads = []
            for i in range(2):
                thread = threading.Thread(target=worker_function, args=(i,))
                threads.append(thread)
                thread.start()

            # 等待完成
            for thread in threads:
                thread.join()

            main_logger.info("测试完成")

            # 等待文件写入
            time.sleep(1)

            # 检查日志文件
            print("\n检查日志文件...")
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.log'):
                        file_path = os.path.join(root, file)
                        size = os.path.getsize(file_path)
                        print(f"✓ 日志文件: {file_path}")
                        print(f"  大小: {size:,} 字节")

                        # 读取内容
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            print(f"  行数: {len(lines)}")

                            if lines:
                                print("  最后3行:")
                                for line in lines[-3:]:
                                    print(f"    {line.strip()}")

            print("\n✓ 简单测试完成！")

        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()

        finally:
            tear_down_custom_logger_system()
            print("✓ 清理完成")


if __name__ == "__main__":
    main()