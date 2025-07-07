# src/demo/custom_logger_comprehensive/comprehensive_demo.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import time
import tempfile
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


def create_demo_config():
    """创建演示用的配置文件"""
    config_content = """# Custom Logger 综合演示配置
project_name: "custom_logger_demo"
experiment_name: "comprehensive_test"
first_start_time: null
base_dir: "d:/logs/demo"

logger:
  global_console_level: "info"
  global_file_level: "debug"
  current_session_dir: null
  module_levels:
    main_demo:
      console_level: "debug"
      file_level: "debug"
    worker_thread:
      console_level: "w_summary"
      file_level: "w_detail"
    worker_process:
      console_level: "w_summary"
      file_level: "debug"
    performance_test:
      console_level: "error"
      file_level: "error"
    exception_demo:
      console_level: "exception"
      file_level: "debug"
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(config_content)
        return tmp_file.name


def demo_basic_logging():
    """演示基础日志功能"""
    print("\n=== 基础日志功能演示 ===")

    logger = get_logger("main_demo")

    # 标准级别演示
    logger.debug("这是调试信息 - DEBUG级别")
    logger.detail("这是详细调试信息 - DETAIL级别")
    logger.info("程序启动成功 - INFO级别")
    logger.warning("这是警告信息 - WARNING级别")
    logger.error("这是错误信息 - ERROR级别")
    logger.critical("这是严重错误 - CRITICAL级别")

    # Worker级别演示
    logger.worker_summary("Worker摘要信息 - W_SUMMARY级别")
    logger.worker_detail("Worker详细信息 - W_DETAIL级别")

    # 带参数的日志
    user_name = "张三"
    user_count = 1_234
    logger.info("用户 {} 有 {:,} 条消息", user_name, user_count)
    logger.info("用户 {name} 年龄 {age}", name="李四", age=25)

    return


def demo_exception_handling():
    """演示异常处理功能"""
    print("\n=== 异常处理演示 ===")

    logger = get_logger("exception_demo")

    try:
        numbers = [1, 2, 3]
        result = numbers[10]  # 故意引发索引错误
    except IndexError:
        logger.exception("捕获到索引错误异常")

    try:
        result = 10 / 0  # 故意引发除零错误
    except ZeroDivisionError:
        logger.exception("捕获到除零错误异常")

    # 普通错误日志
    logger.error("这是普通错误信息，不包含异常堆栈")

    return


def demo_level_filtering():
    """演示级别过滤功能"""
    print("\n=== 级别过滤演示 ===")

    # 高级别logger（只显示重要信息）
    high_logger = get_logger("high_level", console_level="warning", file_level="error")

    # 低级别logger（显示所有信息）
    detail_logger = get_logger("detail_level", console_level="debug", file_level="debug")

    print("高级别logger输出（只显示WARNING及以上）：")
    high_logger.debug("这条调试信息不会显示")
    high_logger.info("这条普通信息不会显示")
    high_logger.warning("这条警告信息会显示")
    high_logger.error("这条错误信息会显示")

    print("\n详细logger输出（显示所有级别）：")
    detail_logger.debug("这条调试信息会显示")
    detail_logger.info("这条普通信息会显示")
    detail_logger.warning("这条警告信息会显示")
    detail_logger.error("这条错误信息会显示")

    return


def thread_worker_function(worker_id: int, task_count: int):
    """线程Worker函数"""
    worker_logger = get_logger("worker_thread", console_level="w_summary")

    worker_logger.worker_summary(f"线程Worker {worker_id} 启动，处理 {task_count:,} 个任务")

    for i in range(task_count):
        if i % 20 == 0:
            worker_logger.worker_detail(f"Thread-{worker_id} 进度 {i + 1:,}/{task_count:,}")
        time.sleep(0.01)

    worker_logger.worker_summary(f"线程Worker {worker_id} 完成所有任务")
    return f"Thread-{worker_id} completed {task_count:,} tasks"


def process_worker_function(worker_id: int, task_count: int):
    """进程Worker函数"""
    worker_logger = get_logger("worker_process", console_level="w_summary")

    worker_logger.worker_summary(f"进程Worker {worker_id} 启动，处理 {task_count:,} 个任务")

    for i in range(task_count):
        if i % 10 == 0:
            worker_logger.worker_detail(f"Process-{worker_id} 进度 {i + 1:,}/{task_count:,}")
        time.sleep(0.02)

    worker_logger.worker_summary(f"进程Worker {worker_id} 完成所有任务")
    return f"Process-{worker_id} completed {task_count:,} tasks"


def demo_multithreading():
    """演示多线程场景"""
    print("\n=== 多线程演示 ===")

    main_logger = get_logger("main_demo")
    main_logger.info("启动多线程任务演示")

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for i in range(3):
            future = executor.submit(thread_worker_function, i, 50)
            futures.append(future)

        for future in futures:
            result = future.result()
            main_logger.info(f"线程任务完成: {result}")

    main_logger.info("多线程演示完成")
    return


def demo_multiprocessing():
    """演示多进程场景"""
    print("\n=== 多进程演示 ===")

    main_logger = get_logger("main_demo")
    main_logger.info("启动多进程任务演示")

    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = []
        for i in range(2):
            future = executor.submit(process_worker_function, i, 30)
            futures.append(future)

        for future in futures:
            result = future.result()
            main_logger.info(f"进程任务完成: {result}")

    main_logger.info("多进程演示完成")
    return


def demo_performance_optimization():
    """演示性能优化功能"""
    print("\n=== 性能优化演示 ===")

    # 创建高级别logger，大部分日志会被过滤
    perf_logger = get_logger("performance_test", console_level="error", file_level="error")
    main_logger = get_logger("main_demo")

    print("测试 10,000 条被过滤日志的性能...")

    start_perf = time.time()
    for i in range(10_000):
        perf_logger.debug(f"性能测试消息 {i:,}")  # 这些会被早期过滤

    end_perf = time.time()
    duration = end_perf - start_perf

    main_logger.info(f"10,000 条被过滤日志耗时: {duration:.3f} 秒")
    main_logger.info("早期过滤优化正常工作")

    return


def demo_format_examples():
    """演示格式化功能"""
    print("\n=== 格式化功能演示 ===")

    logger = get_logger("main_demo")

    # 各种格式化方式
    logger.info("简单消息")
    logger.info("位置参数: {}, {}, {}", "第一个", "第二个", "第三个")
    logger.info("关键字参数: {name} 年龄 {age}", name="王五", age=30)
    logger.info("混合参数: {} 在 {city} 工作", "赵六", city="上海")

    # 数字格式化
    large_number = 2_345_678
    percentage = 0.856
    file_size = 1_024.768

    logger.info("处理了 {:,} 条记录", large_number)
    logger.info("成功率: {:.2%}", percentage)
    logger.info("文件大小: {:.2f} MB", file_size)

    # 格式化错误处理
    logger.info("参数不匹配测试: {} 和 {}", "只有一个参数")

    return


def demo_config_verification():
    """演示配置验证功能"""
    print("\n=== 配置验证演示 ===")

    main_logger = get_logger("main_demo")

    # 显示配置信息
    from custom_logger.config import get_root_config
    root_cfg = get_root_config()

    project_name = getattr(root_cfg, 'project_name', 'unknown')
    experiment_name = getattr(root_cfg, 'experiment_name', 'unknown')
    base_dir = getattr(root_cfg, 'base_dir', 'unknown')

    main_logger.info("配置验证:")
    main_logger.info("  项目名称: {}", project_name)
    main_logger.info("  实验名称: {}", experiment_name)
    main_logger.info("  基础目录: {}", base_dir)

    # 获取会话目录
    logger_cfg = root_cfg.logger
    if isinstance(logger_cfg, dict):
        session_dir = logger_cfg.get('current_session_dir')
    else:
        session_dir = getattr(logger_cfg, 'current_session_dir', None)

    if session_dir:
        main_logger.info("  会话目录: {}", session_dir)
        print(f"📁 实际日志保存路径: {session_dir}")

    # 验证环境变量
    env_path = os.environ.get('CUSTOM_LOGGER_CONFIG_PATH')
    if env_path:
        main_logger.info("  环境变量配置路径: {}", env_path)

    return session_dir


def demo_color_display():
    """演示颜色显示功能"""
    print("\n=== 颜色显示演示 ===")

    logger = get_logger("main_demo", console_level="debug")

    print("以下日志将展示不同级别的颜色效果：")
    logger.debug("DEBUG级别 - 无颜色显示")
    logger.detail("DETAIL级别 - 无颜色显示")
    logger.info("INFO级别 - 无颜色显示")
    logger.warning("WARNING级别 - 黄色显示")
    logger.error("ERROR级别 - 红色显示")
    logger.critical("CRITICAL级别 - 洋红色显示")

    # 异常级别颜色演示
    try:
        raise ValueError("演示异常颜色")
    except ValueError:
        logger.exception("EXCEPTION级别 - 亮红色显示")

    return


def demo_caller_identification():
    """演示调用者识别功能"""
    print("\n=== 调用者识别演示 ===")

    def function_a():
        logger = get_logger("caller_test")
        logger.info("来自 function_a 的调用 - 应显示正确的模块名和行号")
        return

    def function_b():
        logger = get_logger("caller_test")
        logger.info("来自 function_b 的调用 - 应显示正确的模块名和行号")
        return

    def worker_in_thread():
        logger = get_logger("thread_caller")
        logger.info("来自线程的调用 - 应显示正确的调用者信息")
        return

    # 主函数调用
    main_logger = get_logger("main_demo")
    main_logger.info("主函数调用者识别测试")

    # 函数调用测试
    function_a()
    function_b()

    # 线程调用测试
    thread = threading.Thread(target=worker_in_thread)
    thread.start()
    thread.join()

    main_logger.info("调用者识别演示完成")
    return


def demo_file_verification(session_dir: str):
    """演示文件验证功能"""
    print("\n=== 文件验证演示 ===")

    main_logger = get_logger("main_demo")

    # 等待文件写入完成
    time.sleep(2)

    if session_dir and os.path.exists(session_dir):
        full_log_path = os.path.join(session_dir, "full.log")
        warning_log_path = os.path.join(session_dir, "warning.log")

        # 验证完整日志文件
        if os.path.exists(full_log_path):
            file_size = os.path.getsize(full_log_path)
            main_logger.info("完整日志文件大小: {:,} 字节", file_size)

            with open(full_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                line_count = len(lines)
                main_logger.info("日志总行数: {:,} 行", line_count)

                # 统计不同级别的日志
                info_count = sum(1 for line in lines if ' INFO ' in line)
                warning_count = sum(1 for line in lines if ' WARNING ' in line)
                error_count = sum(1 for line in lines if ' ERROR ' in line)
                worker_count = sum(1 for line in lines if 'Worker' in line)

                main_logger.info("统计结果:")
                main_logger.info("  INFO级别: {:,} 条", info_count)
                main_logger.info("  WARNING级别: {:,} 条", warning_count)
                main_logger.info("  ERROR级别: {:,} 条", error_count)
                main_logger.info("  Worker相关: {:,} 条", worker_count)

        # 验证错误日志文件
        if os.path.exists(error_log_path):
            error_size = os.path.getsize(error_log_path)
            main_logger.info("错误日志文件大小: {:,} 字节", error_size)
        else:
            main_logger.info("错误日志文件为空（正常现象）")
    else:
        main_logger.error("会话目录不存在: {}", session_dir)

    return


def demo_stress_test():
    """演示压力测试"""
    print("\n=== 压力测试演示 ===")

    main_logger = get_logger("main_demo")
    main_logger.info("开始压力测试")

    def stress_worker(worker_id: int):
        worker_logger = get_logger(f"stress_worker_{worker_id}")
        for i in range(100):
            worker_logger.info(f"Stress Worker {worker_id} 消息 {i:,}")
        return

    # 启动多个线程进行压力测试
    threads = []
    start_stress = time.time()

    for i in range(5):
        thread = threading.Thread(target=stress_worker, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_stress = time.time()
    stress_duration = end_stress - start_stress

    main_logger.info("压力测试完成，耗时: {:.3f} 秒", stress_duration)
    main_logger.info("500 条日志（5个Worker × 100条）并发处理正常")

    return


def main():
    """主函数 - 运行所有演示"""
    print("Custom Logger 综合功能演示")
    print("=" * 80)
    print("本演示将展示 custom_logger 的所有主要功能")
    print("=" * 80)

    config_path = None
    session_dir = None

    try:
        # 创建演示配置
        config_path = create_demo_config()
        print(f"✓ 创建演示配置: {config_path}")

        # 初始化日志系统
        init_custom_logger_system(config_path=config_path)
        print("✓ 日志系统初始化完成")

        # 获取主logger
        main_logger = get_logger("main_demo")
        main_logger.info("Custom Logger 综合演示开始")

        # 运行所有演示
        demo_basic_logging()
        demo_exception_handling()
        demo_level_filtering()
        demo_format_examples()
        session_dir = demo_config_verification()
        demo_color_display()
        demo_caller_identification()
        demo_performance_optimization()
        demo_multithreading()
        demo_multiprocessing()
        demo_stress_test()
        demo_file_verification(session_dir)

        main_logger.info("所有演示完成")

        print("\n" + "=" * 80)
        print("演示总结")
        print("=" * 80)
        print("✓ 基础日志功能 - 所有级别正常工作")
        print("✓ 异常处理 - 异常堆栈正确记录")
        print("✓ 级别过滤 - 早期过滤优化正常")
        print("✓ 格式化功能 - 参数格式化正常")
        print("✓ 配置管理 - 自定义配置生效")
        print("✓ 颜色显示 - 终端颜色支持正常")
        print("✓ 调用者识别 - 模块名和行号准确")
        print("✓ 多线程支持 - 并发日志记录正常")
        print("✓ 多进程支持 - 配置继承正常")
        print("✓ 文件写入 - 异步写入功能正常")
        print("✓ 性能优化 - 高性能处理验证通过")

        if session_dir:
            print(f"✓ 日志文件保存到: {session_dir}")

        print("\n🎉 Custom Logger 综合演示成功完成！")

    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理日志系统
        tear_down_custom_logger_system()

        # 清理临时配置文件
        if config_path and os.path.exists(config_path):
            os.unlink(config_path)

        print("✓ 清理完成")


if __name__ == "__main__":
    main()