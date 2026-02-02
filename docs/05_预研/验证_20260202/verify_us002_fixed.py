# docs/05_预研/验证_20260202/verify_us002_fixed.py
"""
验证 US-002 修复方案：使用 caller_module 替代 module_name

修复方案：修改 formatter.py 第241行
- 原代码：{module_name:^16}
- 修复后：{caller_module:^16}
"""

import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../..", "src"))

from datetime import datetime
from custom_logger import init_custom_logger_system, get_logger
import traceback


def verify_fixed():
    """验证修复后的行为"""
    print("=" * 60)
    print("验证 US-002 修复：使用 caller_module")
    print("=" * 60)

    # 创建临时日志目录
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix="verify_us002_fixed_")
    log_dir = os.path.join(temp_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 模拟配置
    work_dir_val = temp_dir
    log_dir_val = log_dir

    class Config:
        first_start_time = datetime.now()
        class paths:
            work_dir = work_dir_val
            log_dir = log_dir_val
        class logger:
            enable_queue_mode = False
            global_console_level = 'debug'
            global_file_level = 'debug'

    # 初始化logger系统
    init_custom_logger_system(Config())

    # 主程序获取logger
    main_logger = get_logger("main_program")
    print("\n[主程序] 获取logger: main_program")

    # 测试场景
    print("\n" + "=" * 60)
    print("测试场景")
    print("=" * 60)

    # 场景1：主程序调用
    print("\n场景1：主程序调用 main_logger.info()")
    print(f"  期望显示: verify_us002_fixed (或 verify_u)")
    print(f"  实际显示: ", end="")
    main_logger.info("主程序消息")

    # 场景2：子模块直接使用主程序logger
    print("\n场景2：子模块使用 main_logger.info()")
    print(f"  期望显示: verify_us002_fixed (或 verify_u)")
    print(f"  实际显示: ", end="")
    main_logger.info("子模块消息（使用主程序logger）")

    # 场景3：子模块获取自己的logger
    print("\n场景3：子模块 get_logger('child').info()")
    child_logger = get_logger("child")
    print(f"  期望显示: verify_us002_fixed (或 verify_u)")
    print(f"  实际显示: ", end="")
    child_logger.info("子模块消息（自己的logger）")

    # 读取日志文件验证
    print("\n" + "=" * 60)
    print("日志文件验证")
    print("=" * 60)

    log_files = []
    if os.path.exists(log_dir):
        for f in os.listdir(log_dir):
            if f.endswith('.log') and 'info' in f.lower():
                log_files.append(os.path.join(log_dir, f))

    if log_files:
        log_file = log_files[0]
        print(f"\n日志文件: {log_file}")
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
            print("\n日志内容:")
            print("-" * 40)
            for line in log_content.strip().split('\n'):
                print(f"  {line}")
            print("-" * 40)

    # 分析结果
    print("\n" + "=" * 60)
    print("分析结果")
    print("=" * 60)

    print("\n当前实现：create_log_line() 使用 get_caller_info() 获取动态模块名")
    print("需要修改：formatter.py 第241行")
    print("  原代码：log_line = f\"... {module_name:^16} ...\"")
    print("  修复后：log_line = f\"... {caller_module:^16} ...\"")

    print("\n注意事项：")
    print("1. get_caller_info() 返回的 module_name 来自文件 basename")
    print("2. 长文件名会被截断到16字符")
    print("3. 测试文件名 verify_us002_fixed.py 会被处理为 verify_us002_fixed")

    print("\n" + "=" * 60)
    print("验证完成")
    print("=" * 60)


if __name__ == "__main__":
    verify_fixed()
