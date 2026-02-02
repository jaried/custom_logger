# docs/05_预研/验证_20260202/verify_us002_dynamic_module_name.py
"""
验证 US-002：logger自动识别调用模块名

验证目标：
1. 主程序初始化logger后，传递给子模块使用
2. 子模块调用logger时，显示子模块的模块名（而不是主程序的模块名）
"""

import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../..", "src"))

from datetime import datetime
from custom_logger import init_custom_logger_system, get_logger

# 模拟配置对象
class MockConfig:
    """模拟配置对象"""
    def __init__(self):
        self.first_start_time = datetime.now()
        self.paths = type('obj', (object,), {
            'work_dir': os.path.join(os.path.dirname(__file__), "temp_verify"),
            'log_dir': os.path.join(os.path.dirname(__file__), "temp_verify/logs")
        })()
        self.logger = type('obj', (object,), {
            'enable_queue_mode': False,
            'global_console_level': 10,  # DEBUG
            'global_file_level': 10
        })()

    def save(self):
        """模拟保存配置"""
        pass


def verify_main():
    """主程序：初始化logger并测试动态模块名"""
    print("=" * 60)
    print("验证 US-002：logger自动识别调用模块名")
    print("=" * 60)

    # 创建临时日志目录
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix="verify_us002_")
    log_dir = os.path.join(temp_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    work_dir_val = temp_dir
    log_dir_val = log_dir

    # 模拟配置
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

    # 主程序调用logger
    print("\n--- 主程序调用 logger.info() ---")
    main_logger.info("这是主程序的日志消息")

    # 模拟子模块调用（在同一个文件中模拟不同模块）
    print("\n--- 模拟子模块调用 logger.info() ---")

    # 场景1：直接使用主程序传入的logger
    print("\n场景1：子模块直接使用主程序传入的logger")
    child_module_logger = main_logger
    child_module_logger.info("这是子模块的日志消息")

    # 场景2：子模块获取自己的logger
    print("\n场景2：子模块通过get_logger获取自己的logger")
    child_own_logger = get_logger("child_module")
    child_own_logger.info("这是子模块自己获取的logger")

    # 测试warning级别（带调用栈）
    print("\n--- 测试warning级别（应该显示调用栈）---")
    main_logger.warning("主程序warning")
    child_module_logger.warning("子模块warning（使用主程序logger）")

    # 读取日志文件验证
    print("\n--- 验证日志文件内容 ---")
    log_files = []
    if os.path.exists(log_dir):
        for f in os.listdir(log_dir):
            if f.endswith('.log'):
                log_files.append(os.path.join(log_dir, f))

    if log_files:
        log_file = log_files[-1]  # 读取最新的日志文件
        print(f"\n日志文件: {log_file}")
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
            print("\n日志内容:")
            print("-" * 40)
            print(log_content)
            print("-" * 40)

            # 分析日志中的模块名
            print("\n分析结果:")
            lines = log_content.strip().split('\n')
            for i, line in enumerate(lines, 1):
                if "main_program" in line or "child_module" in line or "verify_us002" in line:
                    print(f"  第{i}行: 包含模块标识")

    # 清理
    import shutil
    try:
        shutil.rmtree(temp_dir)
        print(f"\n清理临时目录: {temp_dir}")
    except Exception as e:
        print(f"\n清理失败: {e}")

    print("\n" + "=" * 60)
    print("验证完成")
    print("=" * 60)

    # 结论
    print("\n结论:")
    print("1. 当前create_log_line()已经使用get_caller_info()动态获取调用者信息")
    print("2. 日志中显示的模块名来自调用栈分析，不是logger.name")
    print("3. 需要验证的是：是否所有场景都正确显示调用模块名")


if __name__ == "__main__":
    verify_main()
