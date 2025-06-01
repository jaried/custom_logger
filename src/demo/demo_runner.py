# src/demo/demo_runner.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import sys


def show_menu():
    """显示demo菜单"""
    print("\n" + "="*80)
    print("Custom Logger 演示程序")
    print("="*80)
    print("请选择要运行的演示:")
    print()
    print("  1. 快速入门演示 (demo_quick_start.py)")
    print("     - 基本使用方法")
    print("     - 简单配置")
    print("     - 常用功能")
    print()
    print("  2. 高级功能演示 (demo_advanced_features.py)")
    print("     - 多线程日志")
    print("     - 多进程日志") 
    print("     - 自定义配置")
    print("     - 调用者识别")
    print("     - 性能测试")
    print()
    print("  3. 综合功能演示 (demo_comprehensive_custom_logger.py)")
    print("     - 类型系统")
    print("     - 配置管理")
    print("     - 格式化功能")
    print("     - 错误处理")
    print("     - 完整功能覆盖")
    print()
    print("  4. 调用链调试演示 (debug_call_stack_demo.py)")
    print("     - 调试输出控制")
    print("     - 调用链显示")
    print()
    print("  0. 退出")
    print("="*80)
    return


def run_demo(choice: str):
    """运行指定的demo"""
    demo_map = {
        '1': ('demo_quick_start', 'quick_start_demo'),
        '2': ('demo_advanced_features', 'main'),
        '3': ('demo_comprehensive_custom_logger', 'main'),
        '4': ('debug_call_stack_demo', 'main')
    }
    
    if choice not in demo_map:
        print("无效的选择!")
        return False
    
    module_name, function_name = demo_map[choice]
    
    try:
        print(f"\n启动 {module_name} 演示...")
        print("-" * 60)
        
        # 动态导入并执行
        module = __import__(module_name, fromlist=[function_name])
        demo_function = getattr(module, function_name)
        demo_function()
        
        print("-" * 60)
        print(f"{module_name} 演示完成")
        return True
        
    except ImportError as e:
        print(f"无法导入演示模块 {module_name}: {e}")
        print("请确保演示文件存在于当前目录")
        return False
    
    except AttributeError as e:
        print(f"演示模块 {module_name} 中没有找到函数 {function_name}: {e}")
        return False
    
    except Exception as e:
        print(f"运行演示时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_demo_files():
    """检查demo文件是否存在"""
    required_files = [
        'demo_quick_start.py',
        'demo_advanced_features.py', 
        'demo_comprehensive_custom_logger.py',
        'debug_call_stack_demo.py'
    ]
    
    missing_files = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    for file_name in required_files:
        file_path = os.path.join(current_dir, file_name)
        if not os.path.exists(file_path):
            missing_files.append(file_name)
    
    if missing_files:
        print(f"警告: 以下demo文件缺失:")
        for file_name in missing_files:
            print(f"  - {file_name}")
        print()
    
    return len(missing_files) == 0


def main():
    """主函数"""
    print("Custom Logger Demo Runner")
    print("初始化演示环境...")
    
    # 检查demo文件
    if not check_demo_files():
        print("部分demo文件缺失，某些演示可能无法运行")
        print()
    
    # 添加当前目录到Python路径，以便导入demo模块
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    try:
        while True:
            show_menu()
            
            try:
                choice = input("\n请输入您的选择 (0-4): ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n\n程序被用户中断")
                break
            
            if choice == '0':
                print("\n感谢使用 Custom Logger Demo!")
                break
            
            if choice in ['1', '2', '3', '4']:
                success = run_demo(choice)
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
                print(f"\n无效的选择: '{choice}'，请输入 0-4")
                print("按回车键继续...")
                try:
                    input()
                except (KeyboardInterrupt, EOFError):
                    pass
    
    except Exception as e:
        print(f"\n程序发生意外错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nDemo Runner 退出")
    return


def show_info():
    """显示演示信息"""
    print("\n" + "="*80)
    print("Custom Logger 演示说明")
    print("="*80)
    print()
    print("本演示程序涵盖了 custom_logger 的所有主要功能，包括:")
    print()
    print("• 类型系统和日志级别管理")
    print("• 配置文件管理和模块特定配置") 
    print("• 多线程和多进程环境下的日志记录")
    print("• 调用者识别和日志格式化")
    print("• 异常处理和错误日志记录")
    print("• 性能测试和优化验证")
    print("• 调试输出控制和问题排查")
    print()
    print("每个演示都是独立的，可以单独运行，也可以通过本程序统一管理。")
    print("演示过程中生成的日志文件会保存在 d:/logs/ 目录下对应的子目录中。")
    print()
    print("这些演示完全覆盖了现有测试用例的功能范围，可以作为:")
    print("• 学习 custom_logger 使用方法的教程")
    print("• 验证系统功能正确性的工具")
    print("• 性能基准测试的参考")
    print("• 问题排查和调试的辅助工具")
    print("="*80)
    return


if __name__ == "__main__":
    # 如果有命令行参数 --info，显示说明信息
    if len(sys.argv) > 1 and sys.argv[1] == '--info':
        show_info()
    else:
        main() 