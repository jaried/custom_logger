# src/demo/demo_quick_start.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


def quick_start_demo():
    """快速入门演示"""
    print("Custom Logger 快速入门演示")
    print("="*50)
    
    # 创建简单配置
    config_content = """project_name: "quick_start"
experiment_name: "demo"
first_start_time: null
base_dir: "d:/logs/quick_start"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  show_debug_call_stack: false
  module_levels: {}
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name
    
    try:
        print(f"\n1. 初始化日志系统:")
        print(f"   配置文件: {config_path}")
        init_custom_logger_system(config_path=config_path)
        print("   ✓ 日志系统初始化完成")
        
        print(f"\n2. 创建logger并记录日志:")
        logger = get_logger("quick_demo")
        
        logger.info("欢迎使用 Custom Logger!")
        logger.debug("这是调试信息")
        logger.warning("这是警告信息")
        logger.error("这是错误信息")
        
        print("   ✓ 各级别日志已记录")
        
        print(f"\n3. 带参数的日志:")
        user_name = "张三"
        action = "登录"
        logger.info("用户 {} 执行了 {} 操作", user_name, action)
        logger.info("系统状态: {status}, 用户数: {count}", status="正常", count=100)
        
        print("   ✓ 参数化日志已记录")
        
        print(f"\n4. 异常日志:")
        try:
            result = 10 / 0
        except ZeroDivisionError:
            logger.exception("除零错误演示")
        
        print("   ✓ 异常日志已记录")
        
        print(f"\n5. 获取日志文件位置:")
        from custom_logger.config import get_root_config
        root_cfg = get_root_config()
        logger_cfg = getattr(root_cfg, 'logger', None)
        if logger_cfg:
            if isinstance(logger_cfg, dict):
                session_dir = logger_cfg.get('current_session_dir', 'N/A')
            else:
                session_dir = getattr(logger_cfg, 'current_session_dir', 'N/A')
            print(f"   日志文件目录: {session_dir}")
        
    finally:
        print(f"\n6. 清理:")
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
        print("   ✓ 系统清理完成")
    
    print("\n快速入门演示完成!")
    print("="*50)
    return


if __name__ == "__main__":
    quick_start_demo() 