# src/demo/demo_advanced_features.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


def demo_multithread():
    """多线程演示"""
    print("\n" + "="*50)
    print("多线程日志演示")
    print("="*50)
    
    # 使用全局配置文件
    config_path = "src/config/config.yaml"
    
    def worker_function(worker_id: int):
        logger = get_logger("worker")
        logger.info(f"Worker {worker_id} 开始工作")
        
        for i in range(3):
            logger.debug(f"Worker {worker_id} 执行步骤 {i+1}")
            time.sleep(0.1)
        
        logger.info(f"Worker {worker_id} 完成工作")
        return f"worker_{worker_id}_done"
    
    try:
        init_custom_logger_system(config_path=config_path)
        main_logger = get_logger("main")
        
        print("启动多个线程...")
        main_logger.info("开始多线程测试")
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(worker_function, i+1) for i in range(3)]
            results = [future.result() for future in futures]
        
        main_logger.info(f"所有线程完成: {results}")
        print("多线程测试完成")
        
    finally:
        tear_down_custom_logger_system()
    return


def process_worker_function(worker_id: int):
    """进程工作函数"""
    try:
        from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system
        from custom_logger.config import get_config_file_path
        
        config_path = get_config_file_path()
        init_custom_logger_system(config_path=config_path)
        
        logger = get_logger("process_worker")
        logger.info(f"进程 {worker_id} 开始工作")
        
        for i in range(2):
            logger.debug(f"进程 {worker_id} 执行步骤 {i+1}")
            time.sleep(0.1)
        
        logger.info(f"进程 {worker_id} 完成工作")
        tear_down_custom_logger_system()
        return f"process_{worker_id}_success"
        
    except Exception as e:
        return f"process_{worker_id}_error: {str(e)}"


def demo_multiprocess():
    """多进程演示"""
    print("\n" + "="*50)
    print("多进程日志演示")
    print("="*50)
    
    # 使用全局配置文件
    config_path = "src/config/config.yaml"
    
    try:
        init_custom_logger_system(config_path=config_path)
        main_logger = get_logger("main")
        
        print("启动多个进程...")
        main_logger.info("开始多进程测试")
        
        with ProcessPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(process_worker_function, i+1) for i in range(2)]
            results = [future.result(timeout=10) for future in futures]
        
        main_logger.info(f"所有进程完成: {results}")
        print("多进程测试完成")
        
    finally:
        tear_down_custom_logger_system()
    return


def demo_custom_config():
    """自定义配置演示"""
    print("\n" + "="*50)
    print("自定义配置演示")
    print("="*50)
    
    scenarios = [
        {
            "name": "调试模式",
            "config": {
                "global_console_level": "debug",
                "global_file_level": "detail",
                "show_debug_call_stack": True,
                "module_levels": {
                    "debug_module": {
                        "console_level": "detail",
                        "file_level": "debug"
                    }
                }
            }
        },
        {
            "name": "生产模式",
            "config": {
                "global_console_level": "warning",
                "global_file_level": "error",
                "show_debug_call_stack": False,
                "module_levels": {
                    "critical_module": {
                        "console_level": "error",
                        "file_level": "critical"
                    }
                }
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n测试 {scenario['name']} 配置:")
        
        # 构建配置内容
        config_dict = {
            "project_name": f"{scenario['name']}_demo",
            "experiment_name": "config_test",
            "first_start_time": None,
            "base_dir": f"d:/logs/{scenario['name']}",
            "logger": scenario['config']
        }
        
        import yaml
        config_content = yaml.dump(config_dict, default_flow_style=False, allow_unicode=True)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(config_content)
            config_path = tmp_file.name
        
        try:
            init_custom_logger_system(config_path=config_path)
            
            # 测试不同模块
            default_logger = get_logger("default_module")
            if "module_levels" in scenario['config']:
                special_module = list(scenario['config']['module_levels'].keys())[0]
                special_logger = get_logger(special_module)
                
                print(f"  默认模块级别: 控制台={default_logger.console_level}, 文件={default_logger.file_level}")
                print(f"  特殊模块级别: 控制台={special_logger.console_level}, 文件={special_logger.file_level}")
                
                default_logger.info(f"{scenario['name']} - 默认模块测试")
                special_logger.info(f"{scenario['name']} - 特殊模块测试")
            
        finally:
            tear_down_custom_logger_system()
            if os.path.exists(config_path):
                os.unlink(config_path)
    return


def demo_caller_identification():
    """调用者识别演示"""
    print("\n" + "="*50)
    print("调用者识别演示")
    print("="*50)
    
    config_content = """project_name: "caller_demo"
experiment_name: "identification_test"
first_start_time: null
base_dir: "d:/logs/caller"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  show_debug_call_stack: true  # 开启调试模式查看调用链
  module_levels: {}
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name
    
    def level_1_function():
        logger = get_logger("level1")
        logger.info("第一层函数调用")
        return
    
    def level_2_function():
        def nested_function():
            logger = get_logger("level2")
            logger.info("嵌套函数调用")
            return
        nested_function()
        return
    
    class TestClass:
        def method_call(self):
            logger = get_logger("class_method")
            logger.info("类方法调用")
            return
    
    try:
        init_custom_logger_system(config_path=config_path)
        
        print("测试不同层级的调用者识别...")
        
        # 直接调用
        logger = get_logger("main")
        logger.info("主函数直接调用")
        
        # 函数调用
        level_1_function()
        level_2_function()
        
        # 类方法调用
        test_obj = TestClass()
        test_obj.method_call()
        
        print("调用者识别测试完成")
        
    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    return


def demo_performance_test():
    """性能测试演示"""
    print("\n" + "="*50)
    print("性能测试演示")
    print("="*50)
    
    config_content = """project_name: "performance_demo"
experiment_name: "perf_test"
first_start_time: null
base_dir: "d:/logs/performance"

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
        init_custom_logger_system(config_path=config_path)
        logger = get_logger("performance")
        
        print("进行性能测试...")
        
        # 大量日志测试
        test_counts = [500, 1000]
        
        for count in test_counts:
            start_time = time.time()
            
            for i in range(count):
                logger.info(f"性能测试消息 {i+1}")
            
            end_time = time.time()
            elapsed = end_time - start_time
            rate = count / elapsed if elapsed > 0 else float('inf')
            
            print(f"  {count:>4} 条消息: {elapsed:.3f}秒, {rate:.1f} 消息/秒")
        
        # 混合级别测试
        print("  混合级别消息测试...")
        start_time = time.time()
        
        for i in range(100):
            logger.debug(f"Debug {i}")
            logger.info(f"Info {i}")
            logger.warning(f"Warning {i}")
            if i % 10 == 0:
                logger.error(f"Error {i}")
        
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"  混合测试: {elapsed:.3f}秒")
        
    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    return


def main():
    """高级功能演示主函数"""
    print("Custom Logger 高级功能演示")
    print("="*80)
    
    demos = [
        ("多线程日志", demo_multithread),
        ("多进程日志", demo_multiprocess),
        ("自定义配置", demo_custom_config),
        ("调用者识别", demo_caller_identification),
        ("性能测试", demo_performance_test)
    ]
    
    try:
        for name, demo_func in demos:
            print(f"\n开始 {name} 演示...")
            demo_func()
            print(f"{name} 演示完成")
            
            print("\n按回车键继续下一个演示...")
            input()
    
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    
    except Exception as e:
        print(f"\n演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            tear_down_custom_logger_system()
        except:
            pass
    
    print("\n高级功能演示完成!")
    return


if __name__ == "__main__":
    main() 