# src/demo/unified_demo_system.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import sys
import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system

from config_manager import get_config_manager

config_manager = get_config_manager(
    config_path="src/config/config.yaml",
    auto_create=True,
    first_start_time=start_time
)

def worker_process(worker_id: int):
    """多进程工作函数 - 必须在模块级别定义以支持序列化"""
    try:
        from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system
        init_custom_logger_system(config_path="src/config/config.yaml")
        
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


class UnifiedDemoSystem:
    """统一的Custom Logger演示系统"""
    
    def __init__(self):
        self.config_path = "src/config/config.yaml"
        self.demo_categories = {
            "1": ("基础功能演示", self._basic_demos),
            "2": ("高级功能演示", self._advanced_demos),
            "3": ("多线程/多进程演示", self._concurrent_demos),
            "4": ("配置管理演示", self._config_demos),
            "5": ("调用者识别演示", self._caller_demos),
            "6": ("边界测试演示", self._edge_case_demos),
            "7": ("性能测试演示", self._performance_demos),
            "8": ("错误处理演示", self._error_handling_demos),
            "9": ("完整功能覆盖", self._comprehensive_demo),
        }
        return
    
    def show_main_menu(self):
        """显示主菜单"""
        print("\n" + "="*80)
        print("Custom Logger 统一演示系统")
        print("="*80)
        print("请选择演示类别:")
        print()
        
        for key, (name, _) in self.demo_categories.items():
            print(f"  {key}. {name}")
        
        print()
        print("  0. 退出")
        print("="*80)
        return
    
    def run_demo_category(self, choice: str):
        """运行指定类别的演示"""
        if choice not in self.demo_categories:
            print("无效的选择!")
            return False
        
        category_name, demo_func = self.demo_categories[choice]
        
        try:
            print(f"\n开始 {category_name}...")
            print("-" * 60)
            demo_func()
            print("-" * 60)
            print(f"{category_name} 完成")
            return True
            
        except Exception as e:
            print(f"演示过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _basic_demos(self):
        """基础功能演示"""
        print("1. 基础日志记录")
        
        try:
            init_custom_logger_system(config_path=self.config_path)
            logger = get_logger("basic_demo")
            
            # 基本日志级别测试
            logger.debug("这是调试信息")
            logger.info("这是普通信息")
            logger.warning("这是警告信息")
            logger.error("这是错误信息")
            logger.critical("这是严重错误信息")
            
            # 格式化消息测试
            user_name = "张三"
            user_id = 12_345
            logger.info(f"用户登录: {user_name} (ID: {user_id:,})")
            
            # 异常日志测试
            try:
                result = 10 / 0
            except ZeroDivisionError as e:
                logger.error(f"计算错误: {e}", exc_info=True)
            
            print("基础功能演示完成")
            
        finally:
            tear_down_custom_logger_system()
        
        return
    
    def _advanced_demos(self):
        """高级功能演示"""
        print("2. 高级功能演示")
        
        try:
            init_custom_logger_system(config_path=self.config_path)
            
            # 多模块日志测试
            modules = ["auth", "database", "api", "cache"]
            loggers = {name: get_logger(name) for name in modules}
            
            for name, logger in loggers.items():
                logger.info(f"{name} 模块初始化完成")
                logger.debug(f"{name} 模块详细信息")
            
            # 嵌套函数调用测试
            def level_1():
                logger = get_logger("level1")
                logger.info("第一层函数调用")
                
                def level_2():
                    logger = get_logger("level2")
                    logger.info("第二层嵌套函数调用")
                    return
                
                level_2()
                return
            
            level_1()
            
            # 类方法调用测试
            class DemoService:
                def __init__(self):
                    self.logger = get_logger("service")
                    return
                
                def process_data(self, data_size: int):
                    self.logger.info(f"开始处理数据，大小: {data_size:,} 字节")
                    time.sleep(0.1)
                    self.logger.info("数据处理完成")
                    return
            
            service = DemoService()
            service.process_data(1_024_000)
            
            print("高级功能演示完成")
            
        finally:
            tear_down_custom_logger_system()
        
        return
    
    def _concurrent_demos(self):
        """多线程/多进程演示"""
        print("3. 并发处理演示")
        
        # 多线程演示
        print("\n3.1 多线程日志演示")
        try:
            init_custom_logger_system(config_path=self.config_path)
            
            def worker_thread(worker_id: int):
                logger = get_logger("thread_worker")
                logger.info(f"线程 {worker_id} 开始工作")
                
                for i in range(3):
                    logger.debug(f"线程 {worker_id} 执行步骤 {i+1}")
                    time.sleep(0.1)
                
                logger.info(f"线程 {worker_id} 完成工作")
                return f"thread_{worker_id}_done"
            
            main_logger = get_logger("main")
            main_logger.info("启动多线程测试")
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(worker_thread, i+1) for i in range(3)]
                results = [future.result() for future in futures]
            
            main_logger.info(f"所有线程完成: {results}")
            
        finally:
            tear_down_custom_logger_system()
        
        # 多进程演示
        print("\n3.2 多进程日志演示")
        try:
            init_custom_logger_system(config_path=self.config_path)
            
            main_logger = get_logger("main")
            main_logger.info("启动多进程测试")
            
            with ProcessPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(worker_process, i+1) for i in range(2)]
                results = [future.result(timeout=10) for future in futures]
            
            main_logger.info(f"所有进程完成: {results}")
            
        finally:
            tear_down_custom_logger_system()
        
        print("并发处理演示完成")
        return
    
    def _config_demos(self):
        """配置管理演示"""
        print("4. 配置管理演示")
        
        try:
            init_custom_logger_system(config_path=self.config_path)
            
            # 显示当前配置 - 使用根配置对象
            from custom_logger.config import get_root_config
            root_cfg = get_root_config()
            
            # 安全获取配置属性
            project_name = getattr(root_cfg, 'project_name', 'unknown')
            experiment_name = getattr(root_cfg, 'experiment_name', 'unknown')
            base_dir = getattr(root_cfg, 'base_dir', 'unknown')
            
            print(f"项目名称: {project_name}")
            print(f"实验名称: {experiment_name}")
            print(f"基础目录: {base_dir}")
            
            # 获取logger配置
            logger_cfg = getattr(root_cfg, 'logger', None)
            if logger_cfg:
                if isinstance(logger_cfg, dict):
                    console_level = logger_cfg.get('global_console_level', 'unknown')
                    file_level = logger_cfg.get('global_file_level', 'unknown')
                    show_call_chain = logger_cfg.get('show_call_chain', False)
                else:
                    console_level = getattr(logger_cfg, 'global_console_level', 'unknown')
                    file_level = getattr(logger_cfg, 'global_file_level', 'unknown')
                    show_call_chain = getattr(logger_cfg, 'show_call_chain', False)
                
                print(f"控制台级别: {console_level}")
                print(f"文件级别: {file_level}")
                print(f"调用链显示: {show_call_chain}")
            else:
                print("控制台级别: unknown")
                print("文件级别: unknown")
                print("调用链显示: unknown")
            
            # 测试不同模块的日志级别
            logger = get_logger("config_test")
            logger.info("配置管理测试")
            logger.debug("调试级别信息")
            
            print("配置管理演示完成")
            
        finally:
            tear_down_custom_logger_system()
        
        return
    
    def _caller_demos(self):
        """调用者识别演示"""
        print("5. 调用者识别演示")
        
        try:
            init_custom_logger_system(config_path=self.config_path)
            
            # 直接调用
            logger = get_logger("caller_test")
            logger.info("主函数直接调用")
            
            # 函数调用
            def test_function():
                logger = get_logger("func_test")
                logger.info("函数内部调用")
                return
            
            test_function()
            
            # 嵌套调用
            def outer_function():
                def inner_function():
                    logger = get_logger("nested_test")
                    logger.info("嵌套函数调用")
                    return
                inner_function()
                return
            
            outer_function()
            
            # 类方法调用
            class TestClass:
                def __init__(self):
                    self.logger = get_logger("class_test")
                    return
                
                def test_method(self):
                    self.logger.info("类方法调用")
                    return
            
            test_obj = TestClass()
            test_obj.test_method()
            
            print("调用者识别演示完成")
            
        finally:
            tear_down_custom_logger_system()
        
        return
    
    def _edge_case_demos(self):
        """边界测试演示"""
        print("6. 边界测试演示")
        
        try:
            init_custom_logger_system(config_path=self.config_path)
            logger = get_logger("edge_test")
            
            # 空消息测试
            logger.info("")
            
            # 长消息测试
            long_message = "这是一个很长的消息 " * 50
            logger.info(long_message)
            
            # 特殊字符测试
            special_chars = "测试特殊字符: !@#$%^&*()_+-=[]{}|;':\",./<>?"
            logger.info(special_chars)
            
            # Unicode测试
            unicode_message = "Unicode测试: 🚀 🎉 ✅ ❌ 中文 English 日本語"
            logger.info(unicode_message)
            
            # 数字格式测试
            large_number = 1_234_567_890
            float_number = 3.14159265359
            logger.info(f"大数字: {large_number:,}, 浮点数: {float_number:.6f}")
            
            # None值测试
            none_value = None
            logger.info(f"None值测试: {none_value}")
            
            print("边界测试演示完成")
            
        finally:
            tear_down_custom_logger_system()
        
        return
    
    def _performance_demos(self):
        """性能测试演示"""
        print("7. 性能测试演示")
        
        try:
            init_custom_logger_system(config_path=self.config_path)
            logger = get_logger("perf_test")
            
            # 大量日志测试
            test_counts = [100, 500, 1_000]
            
            for count in test_counts:
                start_time = time.time()
                
                for i in range(count):
                    logger.info(f"性能测试消息 {i+1:,}")
                
                end_time = time.time()
                elapsed = end_time - start_time
                rate = count / elapsed if elapsed > 0 else float('inf')
                
                print(f"  {count:>5,} 条消息: {elapsed:.3f}秒, {rate:,.1f} 消息/秒")
            
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
            
            print("性能测试演示完成")
            
        finally:
            tear_down_custom_logger_system()
        
        return
    
    def _error_handling_demos(self):
        """错误处理演示"""
        print("8. 错误处理演示")
        
        try:
            init_custom_logger_system(config_path=self.config_path)
            logger = get_logger("error_test")
            
            # 异常捕获测试
            try:
                result = 10 / 0
            except ZeroDivisionError as e:
                logger.error(f"除零错误: {e}", exc_info=True)
            
            # 文件操作错误
            try:
                with open("不存在的文件.txt", "r") as f:
                    content = f.read()
            except FileNotFoundError as e:
                logger.error(f"文件未找到: {e}")
            
            # 类型错误
            try:
                result = "字符串" + 123
            except TypeError as e:
                logger.error(f"类型错误: {e}")
            
            # 自定义异常
            class CustomError(Exception):
                pass
            
            try:
                raise CustomError("这是一个自定义异常")
            except CustomError as e:
                logger.critical(f"自定义异常: {e}", exc_info=True)
            
            print("错误处理演示完成")
            
        finally:
            tear_down_custom_logger_system()
        
        return
    
    def _comprehensive_demo(self):
        """完整功能覆盖演示"""
        print("9. 完整功能覆盖演示")
        print("将依次自动执行所有演示功能 (1-8)...")
        print("="*60)
        
        # 获取所有演示功能（除了演示9本身）
        demo_list = [
            ("1", "基础功能演示", self._basic_demos),
            ("2", "高级功能演示", self._advanced_demos),
            ("3", "多线程/多进程演示", self._concurrent_demos),
            ("4", "配置管理演示", self._config_demos),
            ("5", "调用者识别演示", self._caller_demos),
            ("6", "边界测试演示", self._edge_case_demos),
            ("7", "性能测试演示", self._performance_demos),
            ("8", "错误处理演示", self._error_handling_demos),
        ]
        
        success_count = 0
        total_count = len(demo_list)
        
        for demo_num, demo_name, demo_func in demo_list:
            print(f"\n{'='*60}")
            print(f"正在执行: {demo_num}. {demo_name}")
            print(f"进度: {success_count + 1}/{total_count}")
            print(f"{'='*60}")
            
            try:
                # 执行演示
                demo_func()
                success_count += 1
                print(f"✅ {demo_name} 执行成功")
                
                # 等待用户按回车继续下一个演示
                if success_count < total_count:  # 不是最后一个演示
                    try:
                        input(f"\n按回车键继续下一个演示 ({success_count + 1}/{total_count})...")
                    except (KeyboardInterrupt, EOFError):
                        print("\n用户中断执行")
                        break
                
            except Exception as e:
                print(f"❌ {demo_name} 执行失败: {e}")
                import traceback
                traceback.print_exc()
                
                # 询问是否继续
                try:
                    continue_choice = input(f"\n{demo_name} 执行失败，是否继续执行剩余演示？(y/n): ").strip().lower()
                    if continue_choice not in ['y', 'yes', '']:
                        print("用户选择停止执行")
                        break
                except (KeyboardInterrupt, EOFError):
                    print("\n用户中断执行")
                    break
        
        # 显示总结
        print(f"\n{'='*60}")
        print("完整功能覆盖演示总结")
        print(f"{'='*60}")
        print(f"总演示数量: {total_count}")
        print(f"成功执行: {success_count}")
        print(f"失败数量: {total_count - success_count}")
        print(f"成功率: {success_count/total_count*100:.1f}%")
        
        if success_count == total_count:
            print("🎉 所有演示都执行成功！")
        elif success_count > 0:
            print("⚠️  部分演示执行成功")
        else:
            print("❌ 所有演示都执行失败")
        
        print("完整功能覆盖演示完成")
        return
    
    def run(self):
        """运行演示系统"""
        print("Custom Logger 统一演示系统")
        print("初始化演示环境...")
        
        try:
            while True:
                self.show_main_menu()
                
                try:
                    choice = input("\n请输入您的选择 (0-9): ").strip()
                except (KeyboardInterrupt, EOFError):
                    print("\n\n程序被用户中断")
                    break
                
                if choice == '0':
                    print("\n感谢使用 Custom Logger 演示系统!")
                    break
                
                if choice in self.demo_categories:
                    success = self.run_demo_category(choice)
                    if success:
                        print("\n按回车键返回主菜单...")
                        try:
                            input()
                        except (KeyboardInterrupt, EOFError):
                            print("\n返回主菜单")
                    else:
                        print("\n演示运行失败，按回车键返回主菜单...")
                        try:
                            input()
                        except (KeyboardInterrupt, EOFError):
                            print("\n返回主菜单")
                else:
                    print(f"\n无效的选择: '{choice}'，请输入 0-9")
                    print("按回车键继续...")
                    try:
                        input()
                    except (KeyboardInterrupt, EOFError):
                        pass
        
        except Exception as e:
            print(f"\n程序发生意外错误: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n演示系统退出")
        return


def main():
    """主函数"""
    demo_system = UnifiedDemoSystem()
    demo_system.run()
    return


if __name__ == "__main__":
    main() 