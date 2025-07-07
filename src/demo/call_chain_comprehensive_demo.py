# src/demo/call_chain_comprehensive_demo.py
from __future__ import annotations
from datetime import datetime

import os
import tempfile
import time
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system


class CallChainDemo:
    """调用链功能综合演示"""

    def __init__(self):
        self.demo_count = 0

    def create_config(self, show_call_chain: bool = False, show_debug_call_stack: bool = False):
        """创建演示配置"""
        class DemoConfig:
            def __init__(self):
                self.first_start_time = datetime.now()
                self.paths = {'log_dir': tempfile.mkdtemp()}
                self.logger = DemoLoggerConfig(show_call_chain, show_debug_call_stack)

        class DemoLoggerConfig:
            def __init__(self, show_call_chain: bool, show_debug_call_stack: bool):
                self.global_console_level = "debug"
                self.global_file_level = "debug"
                self.show_call_chain = show_call_chain
                self.show_debug_call_stack = show_debug_call_stack
                self.module_levels = {}

        return DemoConfig()

    def print_demo_header(self, title: str):
        """打印演示标题"""
        self.demo_count += 1
        print(f"\n{'='*80}")
        print(f"演示 {self.demo_count}: {title}")
        print(f"{'='*80}")

    def demo_01_basic_call_chain_on(self):
        """演示1：基本调用链显示开启"""
        self.print_demo_header("基本调用链显示开启")
        
        config = self.create_config(show_call_chain=True)
        init_custom_logger_system(config)
        
        logger = get_logger("demo")
        print("期望看到: [调用链] 信息")
        logger.info("这是一条测试日志 - 调用链开启")
        logger.warning("这是一条警告日志 - 调用链开启")
        
        tear_down_custom_logger_system()
        pass

    def demo_02_basic_call_chain_off(self):
        """演示2：基本调用链显示关闭"""
        self.print_demo_header("基本调用链显示关闭")
        
        config = self.create_config(show_call_chain=False)
        init_custom_logger_system(config)
        
        logger = get_logger("demo")
        print("期望看到: 不应该有 [调用链] 信息")
        logger.info("这是一条测试日志 - 调用链关闭")
        logger.warning("这是一条警告日志 - 调用链关闭")
        
        tear_down_custom_logger_system()
        pass

    def demo_03_debug_call_stack_on(self):
        """演示3：调试调用链显示开启"""
        self.print_demo_header("调试调用链显示开启")
        
        config = self.create_config(show_debug_call_stack=True)
        init_custom_logger_system(config)
        
        logger = get_logger("demo")
        print("期望看到: DEBUG: get_caller_info调用链 信息（因为在测试环境中）")
        logger.debug("这是一条调试日志 - 调试调用链开启")
        logger.info("这是一条信息日志 - 调试调用链开启")
        
        tear_down_custom_logger_system()
        pass

    def demo_04_both_switches_on(self):
        """演示4：两个开关都开启"""
        self.print_demo_header("两个调用链开关都开启")
        
        config = self.create_config(show_call_chain=True, show_debug_call_stack=True)
        init_custom_logger_system(config)
        
        logger = get_logger("demo")
        print("期望看到: 既有 [调用链] 又有 DEBUG: get_caller_info调用链")
        logger.info("这是一条测试日志 - 两个开关都开启")
        logger.error("这是一条错误日志 - 两个开关都开启")
        
        tear_down_custom_logger_system()
        pass

    def demo_05_multilevel_calls(self):
        """演示5：多层调用的调用链跟踪"""
        self.print_demo_header("多层调用的调用链跟踪")
        
        def level3_business_logic():
            """第三级：业务逻辑"""
            logger = get_logger("business")
            logger.info("执行核心业务逻辑")

        def level2_service_layer():
            """第二级：服务层"""
            logger = get_logger("service")
            logger.info("服务层处理")
            level3_business_logic()

        def level1_controller():
            """第一级：控制器"""
            logger = get_logger("ctrl")
            logger.info("控制器接收请求")
            level2_service_layer()

        config = self.create_config(show_call_chain=True)
        init_custom_logger_system(config)
        
        print("期望看到: 调用链显示完整的函数调用路径")
        level1_controller()
        
        tear_down_custom_logger_system()
        pass

    def demo_06_exception_handling(self):
        """演示6：异常处理中的调用链"""
        self.print_demo_header("异常处理中的调用链")
        
        def problematic_function():
            """有问题的函数"""
            try:
                # 故意引发异常来测试异常处理中的调用链
                result = 1 / 0
            except ZeroDivisionError:
                logger = get_logger("error")
                logger.exception("捕获到除零异常")

        config = self.create_config(show_call_chain=True)
        init_custom_logger_system(config)
        
        print("期望看到: 异常处理时的调用链信息")
        problematic_function()
        
        tear_down_custom_logger_system()
        pass

    def demo_07_concurrent_logging(self):
        """演示7：并发日志中的调用链"""
        self.print_demo_header("并发日志中的调用链")
        
        import threading
        
        def worker_task(worker_id: int):
            """工作任务"""
            logger = get_logger(f"worker{worker_id}")
            for i in range(2):
                logger.info(f"Worker {worker_id} 执行任务 {i}")
                time.sleep(0.1)

        config = self.create_config(show_call_chain=True)
        init_custom_logger_system(config)
        
        print("期望看到: 多个线程的调用链信息，应该互不干扰")
        
        # 创建多个线程
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_task, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        tear_down_custom_logger_system()
        pass

    def demo_08_call_chain_format_showcase(self):
        """演示8：调用链格式展示"""
        self.print_demo_header("调用链格式展示")
        
        def demo_function_a():
            demo_function_b()

        def demo_function_b():  
            demo_function_c()

        def demo_function_c():
            logger = get_logger("format")
            logger.info("展示调用链格式")

        config = self.create_config(show_call_chain=True)
        init_custom_logger_system(config)
        
        print("期望看到: 格式为 文件名:行号(函数名) -> 文件名:行号(函数名) ...")
        demo_function_a()
        
        tear_down_custom_logger_system()
        pass

    def demo_09_performance_impact_test(self):
        """演示9：性能影响测试"""
        self.print_demo_header("性能影响测试")
        
        import time
        
        def performance_test(config_desc: str, config):
            """性能测试函数"""
            init_custom_logger_system(config)
            logger = get_logger("perf")
            
            start_time = time.time()
            for i in range(100):
                logger.info(f"性能测试消息 {i}")
            end_time = time.time()
            
            elapsed = end_time - start_time
            print(f"{config_desc}: 100条日志耗时 {elapsed:.4f} 秒")
            
            tear_down_custom_logger_system()

        print("测试调用链开关对性能的影响:")
        
        # 测试关闭调用链
        config_off = self.create_config(show_call_chain=False)
        performance_test("调用链关闭", config_off)
        
        # 测试开启调用链  
        config_on = self.create_config(show_call_chain=True)
        performance_test("调用链开启", config_on)
        pass

    def run_all_demos(self):
        """运行所有演示"""
        print("调用链功能综合演示开始")
        print("本演示将展示调用链功能的各种使用场景")
        
        try:
            self.demo_01_basic_call_chain_on()
            self.demo_02_basic_call_chain_off()
            self.demo_03_debug_call_stack_on()
            self.demo_04_both_switches_on()
            self.demo_05_multilevel_calls()
            self.demo_06_exception_handling()
            self.demo_07_concurrent_logging()
            self.demo_08_call_chain_format_showcase()
            self.demo_09_performance_impact_test()
            
        except Exception as e:
            print(f"演示过程中出现异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 确保清理
            tear_down_custom_logger_system()
        
        print(f"\n{'='*80}")
        print(f"调用链功能综合演示完成！共运行了 {self.demo_count} 个演示")
        print(f"{'='*80}")
        pass


def main():
    """主函数"""
    demo = CallChainDemo()
    demo.run_all_demos()
    pass


if __name__ == "__main__":
    main()