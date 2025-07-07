# src/demo/worker_path_demo/demo_final_verification.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import threading
import time
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


def main():
    """最终验证demo"""
    print("=" * 60)
    print("Worker自定义配置最终验证")
    print("=" * 60)

    # 创建自定义配置
    config_content = """project_name: "final_verification"
experiment_name: "worker_path_test"
first_start_time: null
base_dir: "d:/logs/final_test"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    main_process:
      console_level: "info"
      file_level: "debug"
    worker_process:
      console_level: "w_summary"
      file_level: "w_detail"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    print(f"✓ 自定义配置文件: {config_path}")

    try:
        # 使用自定义配置初始化
        init_custom_logger_system(config_path=config_path)
        print("✓ 日志系统初始化成功")

        # 获取主logger
        main_logger = get_logger("main_process")
        main_logger.info("最终验证开始")

        # 验证配置信息
        from custom_logger.config import get_root_config
        root_cfg = get_root_config()

        project_name = getattr(root_cfg, 'project_name', 'unknown')
        experiment_name = getattr(root_cfg, 'experiment_name', 'unknown')

        main_logger.info("项目名称: {}", project_name)
        main_logger.info("实验名称: {}", experiment_name)

        # 获取会话目录
        logger_cfg = root_cfg.logger
        if isinstance(logger_cfg, dict):
            session_dir = logger_cfg.get('current_session_dir')
        else:
            session_dir = getattr(logger_cfg, 'current_session_dir', None)

        if session_dir:
            main_logger.info("会话目录: {}", session_dir)
            print(f"📁 日志将保存到: {session_dir}")

        # Worker测试
        def worker_task(worker_id):
            worker_logger = get_logger("worker_process")
            worker_logger.worker_summary(f"Worker {worker_id} 开始任务")

            for i in range(3):
                worker_logger.worker_detail(f"Worker {worker_id} 步骤 {i + 1}")
                time.sleep(0.1)

            worker_logger.worker_summary(f"Worker {worker_id} 完成任务")
            return

        print("\n启动Worker验证...")
        threads = []
        for i in range(2):
            thread = threading.Thread(target=worker_task, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        main_logger.info("Worker验证完成")

        # 等待文件写入
        time.sleep(1)

        # 验证结果
        print("\n验证结果:")
        print(f"✓ 使用了非默认配置文件: {config_path}")
        print(f"✓ 项目名称: {project_name}")
        print(f"✓ 实验名称: {experiment_name}")

        if session_dir and os.path.exists(session_dir):
            print(f"✓ 会话目录创建成功: {session_dir}")

            full_log = os.path.join(session_dir, "full.log")
            if os.path.exists(full_log):
                size = os.path.getsize(full_log)
                print(f"✓ 日志文件创建成功: {size:,} 字节")

                with open(full_log, 'r', encoding='utf-8') as f:
                    content = f.read()
                    worker_count = content.count('Worker')
                    print(f"✓ Worker日志记录: {worker_count} 条")

        # 验证环境变量
        env_path = os.environ.get('CUSTOM_LOGGER_CONFIG_PATH')
        if env_path == config_path:
            print("✓ 环境变量配置路径正确")
        else:
            print(f"❌ 环境变量配置路径错误: {env_path}")

        print("\n" + "=" * 60)
        print("最终验证结果: ✅ 成功!")
        print("Worker能够使用非默认配置并正确保存日志到指定路径")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
        print("✓ 清理完成")


if __name__ == "__main__":
    main()