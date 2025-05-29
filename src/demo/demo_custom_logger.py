# src/demo/demo_custom_logger.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


def demo_basic_usage():
    """演示基本用法"""
    print("\n=== 基本用法演示 ===")

    # 获取logger
    logger = get_logger("main")

    # 记录不同级别的日志
    logger.debug("这是调试信息")
    logger.detail("这是详细调试信息")
    logger.info("程序启动成功")
    logger.warning("这是一个警告")
    logger.error("这是一个错误")
    logger.critical("这是严重错误")

    # 带参数的日志
    user = "Alice"
    count = 42
    logger.info("用户 {} 有 {} 条消息", user, count)
    logger.info("用户 {user} 有 {count} 条消息", user=user, count=count)

    pass


def demo_worker_usage():
    """演示Worker用法"""
    print("\n=== Worker用法演示 ===")

    # Worker logger使用特殊级别
    worker_logger = get_logger("worker", console_level="w_summary")

    worker_logger.worker_summary("Worker开始处理任务")
    worker_logger.worker_detail("正在处理数据...")
    worker_logger.worker_detail("处理进度: 50%")
    worker_logger.worker_summary("Worker任务完成")

    pass


def demo_exception_handling():
    """演示异常处理"""
    print("\n=== 异常处理演示 ===")

    logger = get_logger("exception_demo")

    try:
        # 故意引发异常
        numbers = [1, 2, 3]
        result = numbers[10]  # 索引错误
    except IndexError:
        logger.exception("发生索引错误")

    try:
        # 另一种异常
        result = 10 / 0
    except ZeroDivisionError:
        logger.exception("发生除零错误")

    pass


def demo_different_levels():
    """演示不同级别设置"""
    print("\n=== 不同级别设置演示 ===")

    # 高级别logger（只显示重要信息）
    high_level_logger = get_logger("important", console_level="warning", file_level="error")

    # 低级别logger（显示所有信息）
    detailed_logger = get_logger("detailed", console_level="debug", file_level="debug")

    print("高级别logger输出：")
    high_level_logger.debug("这条不会显示")
    high_level_logger.info("这条也不会显示")
    high_level_logger.warning("这条会显示")
    high_level_logger.error("这条也会显示")

    print("\n详细logger输出：")
    detailed_logger.debug("调试信息会显示")
    detailed_logger.info("普通信息会显示")
    detailed_logger.warning("警告信息会显示")

    pass


def worker_thread_function(worker_id: int, task_count: int):
    """线程worker函数"""
    worker_logger = get_logger(f"thread_worker_{worker_id}", console_level="w_summary")

    worker_logger.worker_summary(f"线程Worker {worker_id} 启动，处理 {task_count} 个任务")

    for i in range(task_count):
        worker_logger.worker_detail(f"Thread-{worker_id} 处理任务 {i + 1}/{task_count}")
        time.sleep(0.1)  # 模拟工作

    worker_logger.worker_summary(f"线程Worker {worker_id} 完成所有任务")
    return f"Thread-{worker_id} completed {task_count} tasks"


def worker_process_function(worker_id: int, task_count: int):
    """进程worker函数"""
    # 进程中需要重新获取logger
    worker_logger = get_logger(f"process_worker_{worker_id}", console_level="w_summary")

    worker_logger.worker_summary(f"进程Worker {worker_id} 启动，处理 {task_count} 个任务")

    for i in range(task_count):
        worker_logger.worker_detail(f"Process-{worker_id} 处理任务 {i + 1}/{task_count}")
        time.sleep(0.05)  # 模拟工作

    worker_logger.worker_summary(f"进程Worker {worker_id} 完成所有任务")
    return f"Process-{worker_id} completed {task_count} tasks"


def demo_multithreading():
    """演示多线程场景"""
    print("\n=== 多线程演示 ===")

    main_logger = get_logger("main")
    main_logger.info("启动多线程任务")

    # 使用ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for i in range(3):
            future = executor.submit(worker_thread_function, i, 3)
            futures.append(future)

        # 等待所有任务完成
        for future in futures:
            result = future.result()
            main_logger.info(f"线程任务完成: {result}")

    main_logger.info("所有线程任务完成")
    pass


def demo_multiprocessing():
    """演示多进程场景"""
    print("\n=== 多进程演示 ===")

    main_logger = get_logger("main")
    main_logger.info("启动多进程任务")

    # 使用ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = []
        for i in range(2):
            future = executor.submit(worker_process_function, i, 2)
            futures.append(future)

        # 等待所有任务完成
        for future in futures:
            result = future.result()
            main_logger.info(f"进程任务完成: {result}")

    main_logger.info("所有进程任务完成")
    pass


def demo_format_examples():
    """演示格式化示例"""
    print("\n=== 格式化示例演示 ===")

    logger = get_logger("format_demo")

    # 各种格式化方式
    logger.info("简单消息")
    logger.info("位置参数: {}, {}, {}", "第一个", "第二个", "第三个")
    logger.info("关键字参数: {name} 年龄 {age}", name="张三", age=25)
    logger.info("混合参数: {} 在 {city} 工作", "李四", city="北京")

    # 数字格式化
    logger.info("处理了 {:,} 条记录", 1_234_567)
    logger.info("成功率: {:.2%}", 0.95)
    logger.info("文件大小: {:.2f} MB", 1024.5)

    # 格式化错误处理
    logger.info("参数不匹配: {} 和 {}", "只有一个参数")

    pass


def demo_performance_test():
    """演示性能测试"""
    print("\n=== 性能测试演示 ===")

    # 创建高级别logger，大部分日志会被过滤
    perf_logger = get_logger("performance", console_level="error", file_level="error")

    print("测试10,000条被过滤的日志性能...")
    start_time = time.time()

    for i in range(10_000):
        perf_logger.debug(f"性能测试消息 {i}")  # 这些会被过滤

    end_time = time.time()
    duration = end_time - start_time

    main_logger = get_logger("main")
    main_logger.info(f"10,000条被过滤日志耗时: {duration:.3f}秒")

    pass


def demo_color_levels():
    """演示颜色级别"""
    print("\n=== 颜色级别演示 ===")

    logger = get_logger("color_demo", console_level="debug")

    logger.debug("DEBUG级别 - 无颜色")
    logger.detail("DETAIL级别 - 无颜色")
    logger.info("INFO级别 - 无颜色")
    logger.warning("WARNING级别 - 黄色")
    logger.error("ERROR级别 - 红色")
    logger.critical("CRITICAL级别 - 洋红色")

    # 异常级别演示
    try:
        raise ValueError("演示异常")
    except ValueError:
        logger.exception("EXCEPTION级别 - 亮红色")

    pass


def main():
    """主函数"""
    print("自定义Logger完整演示程序")
    print("=" * 60)

    try:
        # 初始化日志系统（仅主程序需要）
        init_custom_logger_system()

        # 运行各种演示
        demo_basic_usage()
        demo_worker_usage()
        demo_exception_handling()
        demo_different_levels()
        demo_multithreading()
        demo_multiprocessing()
        demo_format_examples()
        demo_performance_test()
        demo_color_levels()

        print("\n=== 演示完成 ===")
        print("日志文件已保存到配置的目录中")
        print("请检查控制台颜色显示和文件输出")

    except Exception as e:
        print(f"演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理日志系统
        tear_down_custom_logger_system()
        print("日志系统已清理")


if __name__ == "__main__":
    main()