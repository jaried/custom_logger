# src/demo/demo_comprehensive_custom_logger.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from custom_logger import (
    init_custom_logger_system, get_logger, tear_down_custom_logger_system,
    DEBUG, INFO, WARNING, ERROR, CRITICAL, EXCEPTION, DETAIL, W_SUMMARY, W_DETAIL,
    parse_level_name, get_level_name
)
from custom_logger.formatter import get_caller_info, format_elapsed_time, create_log_line


def demo_01_types_system():
    """演示类型系统功能"""
    print("\n" + "="*60)
    print("Demo 01: 类型系统演示")
    print("="*60)
    
    print("\n1. 日志级别常量:")
    levels = [
        ("DEBUG", DEBUG),
        ("INFO", INFO), 
        ("WARNING", WARNING),
        ("ERROR", ERROR),
        ("CRITICAL", CRITICAL),
        ("EXCEPTION", EXCEPTION),
        ("DETAIL", DETAIL),
        ("W_SUMMARY", W_SUMMARY),
        ("W_DETAIL", W_DETAIL)
    ]
    
    for name, value in levels:
        print(f"  {name:<12} = {value:>2}")
    
    print("\n2. 级别名称解析:")
    test_names = ["debug", "INFO", " Warning ", "ERROR", "w_summary"]
    for name in test_names:
        try:
            value = parse_level_name(name)
            reverse_name = get_level_name(value)
            print(f"  '{name}' -> {value} -> '{reverse_name}'")
        except ValueError as e:
            print(f"  '{name}' -> ERROR: {e}")
    
    print("\n3. 无效级别处理:")
    invalid_cases = ["invalid", "", 999, None]
    for case in invalid_cases:
        try:
            if isinstance(case, str):
                result = parse_level_name(case)
            else:
                result = get_level_name(case) if isinstance(case, int) else "类型错误"
            print(f"  {case} -> {result}")
        except (ValueError, TypeError) as e:
            print(f"  {case} -> ERROR: {type(e).__name__}")
    
    return


def demo_02_config_management():
    """演示配置管理功能"""
    print("\n" + "="*60)
    print("Demo 02: 配置管理演示")
    print("="*60)
    
    # 创建测试配置
    config_content = """project_name: "demo_project"
experiment_name: "comprehensive_test"
first_start_time: null
base_dir: "d:/logs/demo"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  show_debug_call_stack: false
  module_levels:
    special_module:
      console_level: "debug"
      file_level: "detail"
    worker_module:
      console_level: "w_summary"
      file_level: "w_detail"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name
    
    try:
        print(f"\n1. 初始化配置文件: {config_path}")
        init_custom_logger_system(config_path=config_path)
        
        print("\n2. 测试不同模块的级别配置:")
        modules = ["default_module", "special_module", "worker_module"]
        
        for module_name in modules:
            logger = get_logger(module_name)
            print(f"  {module_name}:")
            print(f"    控制台级别: {logger.console_level} ({get_level_name(logger.console_level)})")
            print(f"    文件级别: {logger.file_level} ({get_level_name(logger.file_level)})")
        
        print("\n3. 测试配置继承:")
        from custom_logger.config import get_root_config
        root_cfg = get_root_config()
        print(f"  项目名称: {getattr(root_cfg, 'project_name', 'N/A')}")
        print(f"  实验名称: {getattr(root_cfg, 'experiment_name', 'N/A')}")
        print(f"  基础目录: {getattr(root_cfg, 'base_dir', 'N/A')}")
        
        # 获取会话目录
        logger_cfg = getattr(root_cfg, 'logger', None)
        if logger_cfg:
            if isinstance(logger_cfg, dict):
                session_dir = logger_cfg.get('current_session_dir', 'N/A')
            else:
                session_dir = getattr(logger_cfg, 'current_session_dir', 'N/A')
            print(f"  会话目录: {session_dir}")
        
    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    
    return


def demo_03_formatter_functions():
    """演示格式化功能"""
    print("\n" + "="*60)
    print("Demo 03: 格式化功能演示")
    print("="*60)
    
    print("\n1. 调用者信息获取:")
    
    def test_function_1():
        return get_caller_info()
    
    def test_function_2():
        def nested_function():
            return get_caller_info()
        return nested_function()
    
    # 直接调用
    module_name, line_number = get_caller_info()
    print(f"  直接调用: {module_name}:{line_number}")
    
    # 函数调用
    module_name, line_number = test_function_1()
    print(f"  函数调用: {module_name}:{line_number}")
    
    # 嵌套调用
    module_name, line_number = test_function_2()
    print(f"  嵌套调用: {module_name}:{line_number}")
    
    print("\n2. 时间格式化:")
    start_times = [
        "2024-01-01T10:00:00",
        "2024-06-15T14:30:15.123"
    ]
    
    current_time = datetime.now()
    
    for start_time_iso in start_times:
        elapsed_str = format_elapsed_time(start_time_iso, current_time)
        print(f"  从 {start_time_iso} 到现在: {elapsed_str}")
    
    print("\n3. 日志行创建:")
    try:
        log_line = create_log_line("info", "测试消息 {}", "demo_module", ("参数值",), {"key": "value"})
        print(f"  完整日志行: {log_line}")
    except Exception as e:
        print(f"  日志行创建错误: {e}")
    
    return


def demo_04_basic_logging():
    """演示基础日志功能"""
    print("\n" + "="*60)
    print("Demo 04: 基础日志功能演示")
    print("="*60)
    
    config_content = """project_name: "basic_logging_demo"
experiment_name: "logging_test"
first_start_time: null
base_dir: "d:/logs/basic"

logger:
  global_console_level: "debug"
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
        logger = get_logger("basic_demo")
        
        print("\n1. 所有级别的日志消息:")
        logger.debug("这是DEBUG级别消息")
        logger.info("这是INFO级别消息")
        logger.warning("这是WARNING级别消息") 
        logger.error("这是ERROR级别消息")
        logger.critical("这是CRITICAL级别消息")
        
        print("\n2. 带参数的日志消息:")
        user_name = "张三"
        user_count = 42
        logger.info("用户 {} 有 {} 条消息", user_name, user_count)
        logger.info("用户 {name} 状态为 {status}", name="李四", status="活跃")
        
        print("\n3. 异常日志:")
        try:
            result = 1 / 0
        except ZeroDivisionError:
            logger.exception("发生除零错误")
        
        print("\n4. 特殊级别:")
        logger.detail("详细信息级别消息")
        logger.w_summary("警告摘要级别消息")
        logger.w_detail("警告详情级别消息")
        
    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    
    return


def demo_05_caller_identification():
    """演示调用者识别功能"""
    print("\n" + "="*60)
    print("Demo 05: 调用者识别演示")
    print("="*60)
    
    config_content = """project_name: "caller_demo"
experiment_name: "identification_test"
first_start_time: null
base_dir: "d:/logs/caller"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  show_debug_call_stack: true  # 开启调试输出查看调用链
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
        
        print("\n1. 不同层级的函数调用:")
        logger = get_logger("main")
        logger.info("主函数直接调用")
        
        level_1_function()
        level_2_function()
        
        print("\n2. 类方法调用:")
        test_obj = TestClass()
        test_obj.method_call()
        
        print("\n3. 循环中的调用:")
        for i in range(3):
            logger.info(f"循环第 {i+1} 次调用")
        
    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    
    return


def demo_06_multithread_logging():
    """演示多线程日志功能"""
    print("\n" + "="*60)
    print("Demo 06: 多线程日志演示")
    print("="*60)
    
    config_content = """project_name: "multithread_demo"
experiment_name: "thread_test"
first_start_time: null
base_dir: "d:/logs/multithread"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  show_debug_call_stack: false
  module_levels:
    worker_thread:
      console_level: "w_summary"
      file_level: "w_detail"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name
    
    def worker_function(worker_id: int, task_count: int):
        """Worker线程函数"""
        logger = get_logger("worker_thread")
        
        for i in range(task_count):
            logger.info(f"Worker {worker_id} 执行任务 {i+1}")
            time.sleep(0.1)  # 模拟工作
        
        logger.w_summary(f"Worker {worker_id} 完成所有任务")
        return f"worker_{worker_id}_completed"
    
    try:
        init_custom_logger_system(config_path=config_path)
        main_logger = get_logger("main_thread")
        
        print("\n1. 启动多个线程:")
        main_logger.info("开始多线程测试")
        
        # 使用ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(3):
                future = executor.submit(worker_function, i+1, 2)
                futures.append(future)
            
            # 等待所有线程完成
            results = []
            for future in futures:
                result = future.result()
                results.append(result)
                main_logger.info(f"线程完成: {result}")
        
        main_logger.info("所有线程执行完成")
        
        print("\n2. 使用传统Threading:")
        
        def simple_thread_function(thread_id: int):
            logger = get_logger("simple_thread")
            logger.info(f"简单线程 {thread_id} 开始")
            time.sleep(0.2)
            logger.info(f"简单线程 {thread_id} 结束")
            return
        
        threads = []
        for i in range(2):
            thread = threading.Thread(target=simple_thread_function, args=(i+1,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        main_logger.info("传统线程测试完成")
        
    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    
    return


def simple_process_function(worker_id: int):
    """简单的进程函数，用于演示"""
    try:
        # 进程中需要重新初始化日志系统
        from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system
        from custom_logger.config import get_config_file_path
        
        # 从环境变量获取配置路径
        config_path = get_config_file_path()
        init_custom_logger_system(config_path=config_path)
        
        logger = get_logger("process_worker")
        logger.info(f"进程 {worker_id} 开始工作")
        
        # 模拟一些工作
        for i in range(3):
            logger.debug(f"进程 {worker_id} 步骤 {i+1}")
            time.sleep(0.1)
        
        logger.info(f"进程 {worker_id} 工作完成")
        
        tear_down_custom_logger_system()
        return f"process_{worker_id}_success"
        
    except Exception as e:
        return f"process_{worker_id}_error: {str(e)}"


def demo_07_multiprocess_logging():
    """演示多进程日志功能"""
    print("\n" + "="*60)
    print("Demo 07: 多进程日志演示")
    print("="*60)
    
    config_content = """project_name: "multiprocess_demo"
experiment_name: "process_test"
first_start_time: null
base_dir: "d:/logs/multiprocess"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  show_debug_call_stack: false
  module_levels:
    process_worker:
      console_level: "debug"
      file_level: "detail"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        config_path = tmp_file.name
    
    try:
        # 主进程初始化
        init_custom_logger_system(config_path=config_path)
        main_logger = get_logger("main_process")
        
        print("\n1. 启动多个进程:")
        main_logger.info("开始多进程测试")
        
        # 使用ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=2) as executor:
            futures = []
            for i in range(2):
                future = executor.submit(simple_process_function, i+1)
                futures.append(future)
            
            # 等待所有进程完成
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=10)
                    results.append(result)
                    main_logger.info(f"进程完成: {result}")
                except Exception as e:
                    main_logger.error(f"进程执行错误: {e}")
        
        main_logger.info("多进程测试完成")
        
        print("\n2. 进程配置继承验证:")
        main_logger.info("验证子进程能正确继承配置")
        
    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    
    return


def demo_08_custom_config_scenarios():
    """演示自定义配置场景"""
    print("\n" + "="*60)
    print("Demo 08: 自定义配置场景演示")
    print("="*60)
    
    scenarios = [
        {
            "name": "高性能场景",
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
        },
        {
            "name": "调试开发场景",
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
            "name": "生产监控场景",
            "config": {
                "global_console_level": "info",
                "global_file_level": "info",
                "show_debug_call_stack": False,
                "module_levels": {
                    "monitor_module": {
                        "console_level": "w_summary",
                        "file_level": "w_detail"
                    }
                }
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        
        # 构建配置内容
        config_dict = {
            "project_name": f"scenario_{i}",
            "experiment_name": scenario['name'].replace(' ', '_'),
            "first_start_time": None,
            "base_dir": f"d:/logs/scenario_{i}",
            "logger": scenario['config']
        }
        
        # 转换为YAML格式字符串
        from ruamel.yaml import YAML
        from io import StringIO
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.default_flow_style = False
        stream = StringIO()
        yaml.dump(config_dict, stream)
        config_content = stream.getvalue()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(config_content)
            config_path = tmp_file.name
        
        try:
            init_custom_logger_system(config_path=config_path)
            
            # 测试不同模块
            modules_to_test = ["default_module"]
            if "module_levels" in scenario['config']:
                modules_to_test.extend(scenario['config']['module_levels'].keys())
            
            for module_name in modules_to_test:
                logger = get_logger(module_name)
                console_level_name = get_level_name(logger.console_level)
                file_level_name = get_level_name(logger.file_level)
                
                print(f"  {module_name}: 控制台={console_level_name}, 文件={file_level_name}")
                logger.info(f"{scenario['name']} - 模块 {module_name} 测试消息")
        
        finally:
            tear_down_custom_logger_system()
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    return


def demo_09_performance_test():
    """演示性能测试"""
    print("\n" + "="*60)
    print("Demo 09: 性能测试演示")
    print("="*60)
    
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
        
        print("\n1. 大量日志消息性能测试:")
        
        # 测试不同数量的日志消息
        test_counts = [100, 500, 1000]
        
        for count in test_counts:
            start_time = time.time()
            
            for i in range(count):
                logger.info(f"性能测试消息 {i+1}/{count}")
            
            end_time = time.time()
            elapsed = end_time - start_time
            rate = count / elapsed if elapsed > 0 else float('inf')
            
            print(f"  {count:>4} 条消息: {elapsed:.3f}秒, {rate:.1f} 消息/秒")
        
        print("\n2. 不同级别消息混合测试:")
        start_time = time.time()
        
        for i in range(200):
            logger.debug(f"Debug 消息 {i}")
            logger.info(f"Info 消息 {i}")
            logger.warning(f"Warning 消息 {i}")
            if i % 10 == 0:
                logger.error(f"Error 消息 {i}")
        
        end_time = time.time()
        elapsed = end_time - start_time
        total_messages = 200 * 4  # debug, info, warning 各200条, error 20条
        rate = total_messages / elapsed if elapsed > 0 else float('inf')
        
        print(f"  {total_messages} 条混合消息: {elapsed:.3f}秒, {rate:.1f} 消息/秒")
        
        print("\n3. 带格式化参数的消息性能:")
        start_time = time.time()
        
        for i in range(300):
            logger.info("用户 {} 在 {} 执行了 {} 操作", 
                       f"user_{i}", datetime.now().strftime("%H:%M:%S"), "test")
        
        end_time = time.time()
        elapsed = end_time - start_time
        rate = 300 / elapsed if elapsed > 0 else float('inf')
        
        print(f"  300 条格式化消息: {elapsed:.3f}秒, {rate:.1f} 消息/秒")
        
    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    
    return


def demo_10_error_scenarios():
    """演示错误场景处理"""
    print("\n" + "="*60)
    print("Demo 10: 错误场景处理演示")
    print("="*60)
    
    print("\n1. 配置文件错误:")
    
    # 测试不存在的配置文件
    try:
        init_custom_logger_system(config_path="non_existent_config.yaml")
        print("  不存在的配置文件: 初始化成功 (使用默认配置)")
    except Exception as e:
        print(f"  不存在的配置文件: 错误 - {e}")
    finally:
        tear_down_custom_logger_system()
    
    # 测试无效的配置内容
    invalid_config = "invalid: yaml: content: ["
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(invalid_config)
        invalid_config_path = tmp_file.name
    
    try:
        init_custom_logger_system(config_path=invalid_config_path)
        print("  无效YAML配置: 初始化成功 (使用默认配置)")
    except Exception as e:
        print(f"  无效YAML配置: 错误 - {e}")
    finally:
        tear_down_custom_logger_system()
        if os.path.exists(invalid_config_path):
            os.unlink(invalid_config_path)
    
    print("\n2. 级别解析错误:")
    
    invalid_levels = ["invalid_level", "", "trace", 999]
    for level in invalid_levels:
        try:
            if isinstance(level, str):
                result = parse_level_name(level)
                print(f"  '{level}': 解析成功 -> {result}")
            else:
                result = get_level_name(level)
                print(f"  {level}: 解析成功 -> '{result}'")
        except (ValueError, TypeError) as e:
            print(f"  {level}: 错误 - {type(e).__name__}: {e}")
    
    print("\n3. 异常日志记录:")
    
    config_content = """project_name: "error_demo"
experiment_name: "error_test"
first_start_time: null
base_dir: "d:/logs/error"

logger:
  global_console_level: "debug"
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
        logger = get_logger("error_test")
        
        # 测试各种异常
        exceptions_to_test = [
            ("ZeroDivisionError", lambda: 1/0),
            ("ValueError", lambda: int("invalid")),
            ("KeyError", lambda: {"a": 1}["b"]),
            ("AttributeError", lambda: None.invalid_attr),
            ("IndexError", lambda: [1, 2, 3][5])
        ]
        
        for error_name, error_func in exceptions_to_test:
            try:
                error_func()
            except Exception:
                logger.exception(f"捕获到 {error_name}")
        
        print("  各种异常已记录到日志")
        
    finally:
        tear_down_custom_logger_system()
        if os.path.exists(config_path):
            os.unlink(config_path)
    
    return


def main():
    """主演示函数"""
    print("Custom Logger 综合演示")
    print("="*80)
    print("本演示将展示custom_logger的所有主要功能，涵盖现有测试用例的功能范围")
    print("="*80)
    
    demos = [
        ("类型系统", demo_01_types_system),
        ("配置管理", demo_02_config_management), 
        ("格式化功能", demo_03_formatter_functions),
        ("基础日志", demo_04_basic_logging),
        ("调用者识别", demo_05_caller_identification),
        ("多线程日志", demo_06_multithread_logging),
        ("多进程日志", demo_07_multiprocess_logging),
        ("自定义配置", demo_08_custom_config_scenarios),
        ("性能测试", demo_09_performance_test),
        ("错误处理", demo_10_error_scenarios)
    ]
    
    try:
        for i, (name, demo_func) in enumerate(demos, 1):
            print(f"\n执行演示 {i}: {name}")
            demo_func()
            
            if i < len(demos):
                print(f"\n{'-'*60}")
                print("按回车键继续下一个演示...")
                input()
    
    except KeyboardInterrupt:
        print("\n\n演示被用户中断")
    
    except Exception as e:
        print(f"\n\n演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 确保清理
        try:
            tear_down_custom_logger_system()
        except:
            pass
    
    print("\n" + "="*80)
    print("演示完成！感谢使用 Custom Logger")
    print("="*80)
    return


if __name__ == "__main__":
    main() 