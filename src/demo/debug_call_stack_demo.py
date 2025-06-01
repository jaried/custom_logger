# src/demo/debug_call_stack_demo.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


def test_with_debug_on():
    """测试打开调试输出"""
    print("\n=== 测试：调试输出开启 ===")
    
    config_content = """project_name: debug_demo
experiment_name: call_stack_test
first_start_time: null
base_dir: d:/logs/debug

logger:
  global_console_level: info
  global_file_level: debug
  current_session_dir: null
  show_debug_call_stack: true  # 开启调试输出
  module_levels: {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        init_custom_logger_system(config_path=config_path)
        logger = get_logger("debug_test")
        
        print("日志调用 - 应该会显示调用链信息：")
        logger.info("这是一条测试日志消息")
        
    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def test_with_debug_off():
    """测试关闭调试输出"""
    print("\n=== 测试：调试输出关闭 ===")
    
    config_content = """project_name: debug_demo
experiment_name: call_stack_test
first_start_time: null
base_dir: d:/logs/debug

logger:
  global_console_level: info
  global_file_level: debug
  current_session_dir: null
  show_debug_call_stack: false  # 关闭调试输出
  module_levels: {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name

    try:
        init_custom_logger_system(config_path=config_path)
        logger = get_logger("debug_test")
        
        print("日志调用 - 不应该显示调用链信息：")
        logger.info("这是一条测试日志消息")
        
    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    pass


def main():
    """主函数"""
    print("调用链调试输出控制演示")
    print("=" * 50)
    
    # 测试关闭调试输出（默认行为）
    test_with_debug_off()
    
    # 测试开启调试输出
    test_with_debug_on()
    
    print("\n演示完成！")
    pass


if __name__ == "__main__":
    main() 