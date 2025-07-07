# src/demo/worker_path_demo/demo_worker_path_quick.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import threading
import time
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


def create_quick_test_config():
    """创建快速测试配置文件"""
    config_content = f"""# 快速测试配置
project_name: "quick_test"
experiment_name: "worker_path_demo"
first_start_time: null
base_dir: "{os.path.join(os.getcwd(), 'demo_logs').replace(os.sep, '/')}"

paths:
  log_dir: null

logger:
  global_console_level: "info"
  global_file_level: "debug"
  module_levels:
    main:
      console_level: "info"
      file_level: "debug"
    worker:
      console_level: "w_summary"
      file_level: "w_detail"
"""

    # 创建临时配置文件，确保UTF-8编码无BOM
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        return tmp_file.name


def worker_function(worker_id: int):
    """Worker函数"""
    # Worker获取logger（自动继承配置）
    worker_logger = get_logger("worker", console_level="w_summary")

    worker_logger.worker_summary(f"Worker {worker_id} 开始执行任务")

    for i in range(10):
        worker_logger.worker_detail(f"Worker {worker_id} 执行步骤 {i + 1}/10")
        time.sleep(0.1)

    worker_logger.worker_summary(f"Worker {worker_id} 任务完成")
    return f"Worker-{worker_id} finished"


def main():
    """主函数"""
    print("Worker路径快速验证Demo")
    print("=" * 50)

    config_path = None

    try:
        # 创建测试配置
        config_path = create_quick_test_config()
        print(f"✓ 创建测试配置: {config_path}")

        # 初始化日志系统
        init_custom_logger_system(config_path=config_path)
        print("✓ 日志系统初始化完成")

        # 获取主logger
        main_logger = get_logger("main")
        main_logger.info("Demo程序启动")

        # 显示配置信息
        from custom_logger.config import get_root_config
        root_cfg = get_root_config()

        # 安全获取配置属性
        project_name = getattr(root_cfg, 'project_name', 'unknown')
        experiment_name = getattr(root_cfg, 'experiment_name', 'unknown')
        base_dir = getattr(root_cfg, 'base_dir', 'unknown')

        main_logger.info("项目: {}", project_name)
        main_logger.info("实验: {}", experiment_name)
        main_logger.info("基础目录: {}", base_dir)

        # 获取日志目录
        paths_cfg = getattr(root_cfg, 'paths', None)
        if paths_cfg:
            if isinstance(paths_cfg, dict):
                session_dir = paths_cfg.get('log_dir')
            else:
                session_dir = getattr(paths_cfg, 'log_dir', None)
        else:
            session_dir = None

        if session_dir:
            main_logger.info("会话目录: {}", session_dir)
            print(f"📁 日志保存到: {session_dir}")

        # 启动Worker线程
        print("\n启动Worker线程...")
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待Worker完成
        for thread in threads:
            thread.join()

        main_logger.info("所有Worker完成")

        # 等待文件写入
        time.sleep(1)

        # 验证日志文件
        print("\n验证日志文件...")
        if session_dir and os.path.exists(session_dir):
            full_log = os.path.join(session_dir, "full.log")
            if os.path.exists(full_log):
                size = os.path.getsize(full_log)
                print(f"✓ 日志文件存在: {full_log}")
                print(f"✓ 文件大小: {size:,} 字节")

                # 读取并显示部分日志内容
                with open(full_log, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"✓ 总行数: {len(lines):,}")

                    # 显示Worker相关的日志行
                    worker_lines = [line for line in lines if 'worker' in line.lower()]
                    print(f"✓ Worker日志行数: {len(worker_lines)}")

                    if worker_lines:
                        print("\nWorker日志示例:")
                        for line in worker_lines[:5]:  # 显示前5行
                            print(f"  {line.strip()}")
            else:
                print(f"❌ 日志文件不存在: {full_log}")
        else:
            print(f"❌ 会话目录不存在: {session_dir}")

        # 验证环境变量
        env_path = os.environ.get('CUSTOM_LOGGER_CONFIG_PATH')
        if env_path:
            print(f"✓ 环境变量配置路径: {env_path}")
        else:
            print("❌ 环境变量未设置")

        print("\n" + "=" * 50)
        print("验证完成！")
        if session_dir:
            print(f"Worker日志已成功保存到: {session_dir}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理
        tear_down_custom_logger_system()
        if config_path and os.path.exists(config_path):
            os.unlink(config_path)
        print("✓ 清理完成")


if __name__ == "__main__":
    main()