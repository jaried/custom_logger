# debug_log_test.py
from __future__ import annotations
from datetime import datetime
import os
import tempfile
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from custom_logger import (
    init_custom_logger_system,
    get_logger,
    tear_down_custom_logger_system,
    DEBUG, INFO, WARNING, ERROR, CRITICAL, EXCEPTION,
    DETAIL, W_SUMMARY, W_DETAIL
)


class ConfigObject:
    """模拟config_manager的config对象"""
    
    def __init__(self, log_dir: str, first_start_time: datetime):
        self.first_start_time = first_start_time
        self.project_name = "debug_test"
        self.experiment_name = "log_output_test"
        
        # 使用paths结构，符合config_manager的格式
        self.paths = {
            'log_dir': log_dir
        }
        
        # logger配置
        self.logger = {
            'global_console_level': 'debug',
            'global_file_level': 'debug',
            'show_debug_call_stack': False,
            'module_levels': {}
        }


def main():
    """简单的日志测试"""
    print("开始测试日志输出...")
    
    # 创建日志目录
    log_dir = os.path.join(tempfile.gettempdir(), "debug_test_logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建配置对象
    config_object = ConfigObject(log_dir, datetime.now())
    
    try:
        # 初始化日志系统
        init_custom_logger_system(config_object)
        
        # 获取多个不同名称的logger
        logger1 = get_logger("test_main")
        logger2 = get_logger("test_module")
        logger3 = get_logger("test_worker")
        
        print("开始输出各种级别的日志...")
        
        # 测试各种日志级别
        logger1.debug("这是DEBUG级别消息")
        logger1.info("这是INFO级别消息")
        logger1.warning("这是WARNING级别消息")
        logger1.error("这是ERROR级别消息")
        logger1.critical("这是CRITICAL级别消息")
        
        # 测试不同模块
        logger2.info("模块2的信息消息")
        logger2.warning("模块2的警告消息")
        logger2.error("模块2的错误消息")
        
        logger3.info("模块3的信息消息")
        logger3.warning("模块3的警告消息")
        logger3.error("模块3的错误消息")
        
        # 测试特殊级别
        logger1.worker_detail("这是W_DETAIL级别消息")
        logger1.worker_summary("这是W_SUMMARY级别消息")
        logger1.detail("这是DETAIL级别消息")
        
        # 测试异常日志
        try:
            result = 1 / 0
        except ZeroDivisionError:
            logger1.exception("测试异常日志")
        
        print("日志输出完成！")
        
        # 检查日志文件
        if os.path.exists(log_dir):
            print(f"\\n日志目录: {log_dir}")
            print("日志文件:")
            for file in os.listdir(log_dir):
                file_path = os.path.join(log_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"  {file}: {size} bytes")
        
    finally:
        tear_down_custom_logger_system()
    
    return


if __name__ == "__main__":
    main()