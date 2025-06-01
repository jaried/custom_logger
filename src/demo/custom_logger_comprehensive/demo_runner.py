# src/demo/custom_logger_comprehensive/demo_runner.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import sys
import subprocess
import time


def get_demo_directory():
    """获取demo目录路径"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return current_dir


def run_demo_script(script_name: str, description: str):
    """运行单个demo脚本"""
    demo_dir = get_demo_directory()
    script_path = os.path.join(demo_dir, script_name)

    if not os.path.exists(script_path):
        print(f"❌ Demo脚本不存在: {script_path}")
        return False

    print(f"\n{'=' * 80}")
    print(f"运行: {description}")
    print(f"脚本: {script_name}")
    print(f"{'=' * 80}")

    try:
        # 运行demo脚本
        start_run = time.time()
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=demo_dir,
            capture_output=False,
            text=True
        )
        end_run = time.time()

        duration = end_run - start_run

        if result.returncode == 0:
            print(f"\n✅ {description} 运行成功 (耗时: {duration:.2f}秒)")
            return True
        else:
            print(f"\n❌ {description} 运行失败 (退出码: {result.returncode})")
            return False

    except Exception as e:
        print(f"\n❌ 运行 {description} 时发生异常: {e}")
        return False


def show_demo_menu():
    """显示demo菜单"""
    print("\nCustom Logger 演示程序运行器")
    print("=" * 50)
    print("1. 综合功能演示 (推荐)")
    print("2. 特定功能演示")
    print("3. 边界情况演示")
    print("4. 运行所有演示")
    print("5. 查看演示说明")
    print("0. 退出")
    print("=" * 50)


def show_demo_descriptions():
    """显示演示说明"""
    print("\n演示程序说明:")
    print("-" * 50)

    print("\n1. 综合功能演示 (comprehensive_demo.py):")
    print("   - 覆盖所有主要功能的完整演示")
    print("   - 包括基础日志、多线程、多进程、异常处理")
    print("   - 展示性能优化、颜色显示、配置管理")
    print("   - 推荐首次使用时运行")

    print("\n2. 特定功能演示 (feature_specific_demos.py):")
    print("   - 详细展示各个模块的具体功能")
    print("   - Types、Config、Formatter、Writer、Logger、Manager")
    print("   - 适合深入了解每个模块的工作原理")

    print("\n3. 边界情况演示 (edge_case_demos.py):")
    print("   - 测试各种边界情况和极端场景")
    print("   - 包括空值、特殊字符、大量数据、并发压力")
    print("   - 验证系统的健壮性和错误处理能力")

    print("\n演示特点:")
    print("✓ 使用临时配置文件，不影响生产环境")
    print("✓ 自动清理临时文件和日志系统")
    print("✓ 详细的输出说明和结果验证")
    print("✓ 覆盖所有测试用例中的功能场景")


def run_all_demos():
    """运行所有演示"""
    demos = [
        ("comprehensive_demo.py", "综合功能演示"),
        ("feature_specific_demos.py", "特定功能演示"),
        ("edge_case_demos.py", "边界情况演示"),
    ]

    print(f"\n{'=' * 80}")
    print("开始运行所有演示程序")
    print(f"{'=' * 80}")

    results = []
    total_start = time.time()

    for script_name, description in demos:
        print(f"\n等待3秒后运行下一个演示...")
        time.sleep(3)

        success = run_demo_script(script_name, description)
        results.append((description, success))

    total_end = time.time()
    total_duration = total_end - total_start

    # 显示总结
    print(f"\n{'=' * 80}")
    print("所有演示运行完成")
    print(f"{'=' * 80}")

    success_count = 0
    for description, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{description}: {status}")
        if success:
            success_count += 1

    print(f"\n总计: {success_count}/{len(results)} 个演示成功")
    print(f"总耗时: {total_duration:.2f} 秒")

    return success_count == len(results)


def validate_demo_environment():
    """验证演示运行环境"""
    print("验证演示运行环境...")

    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print(f"❌ Python版本过低: {python_version.major}.{python_version.minor}")
        print("   需要Python 3.7或更高版本")
        return False

    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")

    # 检查必要的模块
    required_modules = ['custom_logger', 'config_manager', 'yaml', 'threading', 'multiprocessing']
    missing_modules = []

    for module in required_modules:
        try:
            if module == 'yaml':
                import yaml
            elif module == 'threading':
                import threading
            elif module == 'multiprocessing':
                import multiprocessing
            elif module == 'custom_logger':
                import custom_logger
            elif module == 'config_manager':
                import config_manager
            print(f"✅ 模块 {module} 可用")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ 模块 {module} 不可用")

    if missing_modules:
        print(f"\n缺少必要模块: {', '.join(missing_modules)}")
        return False

    # 检查demo脚本
    demo_dir = get_demo_directory()
    required_scripts = [
        "comprehensive_demo.py",
        "feature_specific_demos.py",
        "edge_case_demos.py"
    ]

    missing_scripts = []
    for script in required_scripts:
        script_path = os.path.join(demo_dir, script)
        if os.path.exists(script_path):
            print(f"✅ 演示脚本 {script} 存在")
        else:
            missing_scripts.append(script)
            print(f"❌ 演示脚本 {script} 不存在")

    if missing_scripts:
        print(f"\n缺少演示脚本: {', '.join(missing_scripts)}")
        return False

    print("✅ 演示环境验证通过")
    return True


def show_system_info():
    """显示系统信息"""
    print("\n系统信息:")
    print("-" * 30)
    print(f"Python版本: {sys.version}")
    print(f"操作系统: {os.name}")
    print(f"当前目录: {os.getcwd()}")
    print(f"Demo目录: {get_demo_directory()}")

    # 检查日志系统状态
    try:
        from custom_logger.manager import is_initialized
        init_status = is_initialized()
        print(f"日志系统状态: {'已初始化' if init_status else '未初始化'}")
    except Exception as e:
        print(f"日志系统状态: 检查失败 ({e})")


def interactive_demo_selection():
    """交互式演示选择"""
    while True:
        show_demo_menu()

        try:
            choice = input("\n请选择要运行的演示 (0-5): ").strip()

            if choice == "0":
                print("退出演示程序")
                break

            elif choice == "1":
                run_demo_script("comprehensive_demo.py", "综合功能演示")

            elif choice == "2":
                run_demo_script("feature_specific_demos.py", "特定功能演示")

            elif choice == "3":
                run_demo_script("edge_case_demos.py", "边界情况演示")

            elif choice == "4":
                run_all_demos()

            elif choice == "5":
                show_demo_descriptions()

            else:
                print("无效选择，请输入0-5之间的数字")

        except KeyboardInterrupt:
            print("\n\n用户中断，退出演示程序")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")


def main():
    """主函数"""
    print("Custom Logger 演示程序运行器")
    print("=" * 50)
    print("这个工具用于运行 Custom Logger 的各种演示程序")

    # 显示系统信息
    show_system_info()

    # 验证环境
    if not validate_demo_environment():
        print("\n❌ 环境验证失败，无法运行演示")
        print("请检查以上错误信息并修复后重试")
        return 1

    # 处理命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg in ["--all", "-a"]:
            print("\n运行所有演示...")
            success = run_all_demos()
            return 0 if success else 1

        elif arg in ["--comprehensive", "-c"]:
            success = run_demo_script("comprehensive_demo.py", "综合功能演示")
            return 0 if success else 1

        elif arg in ["--features", "-f"]:
            success = run_demo_script("feature_specific_demos.py", "特定功能演示")
            return 0 if success else 1

        elif arg in ["--edge", "-e"]:
            success = run_demo_script("edge_case_demos.py", "边界情况演示")
            return 0 if success else 1

        elif arg in ["--help", "-h"]:
            print("\n使用方法:")
            print("  python demo_runner.py                  # 交互式菜单")
            print("  python demo_runner.py --all            # 运行所有演示")
            print("  python demo_runner.py --comprehensive  # 综合功能演示")
            print("  python demo_runner.py --features       # 特定功能演示")
            print("  python demo_runner.py --edge           # 边界情况演示")
            print("  python demo_runner.py --help           # 显示帮助")
            return 0

        else:
            print(f"\n未知参数: {arg}")
            print("使用 --help 查看可用参数")
            return 1

    # 交互式模式
    try:
        interactive_demo_selection()
        return 0
    except Exception as e:
        print(f"\n运行过程中发生错误: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)