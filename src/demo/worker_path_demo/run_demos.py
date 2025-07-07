# src/demo/worker_path_demo/run_demos.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import sys
import subprocess


def run_demo(demo_name: str, demo_script: str):
    """运行单个demo"""
    print(f"\n{'=' * 60}")
    print(f"运行 {demo_name}")
    print(f"{'=' * 60}")

    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        demo_path = os.path.join(current_dir, demo_script)

        if not os.path.exists(demo_path):
            print(f"❌ Demo文件不存在: {demo_path}")
            return False

        # 运行demo
        result = subprocess.run([sys.executable, demo_path],
                                capture_output=False,
                                text=True)

        if result.returncode == 0:
            print(f"✓ {demo_name} 运行成功")
            return True
        else:
            print(f"❌ {demo_name} 运行失败 (退出码: {result.returncode})")
            return False

    except Exception as e:
        print(f"❌ 运行 {demo_name} 时出错: {e}")
        return False


def show_menu():
    """显示菜单"""
    print("\nWorker路径Demo运行器")
    print("=" * 40)
    print("1. 简单测试 (推荐先运行)")
    print("2. 路径信息演示")
    print("3. 调用者识别测试")
    print("4. 调用者识别调试")
    print("5. 快速验证Demo")
    print("6. 完整功能Demo")
    print("7. 运行所有Demo")
    print("8. 查看Demo说明")
    print("0. 退出")
    print("=" * 40)


def show_demo_info():
    """显示Demo说明"""
    print("\nDemo说明:")
    print("-" * 40)
    print("1. 快速验证Demo:")
    print("   - 文件: demo_worker_path_quick.py")
    print("   - 功能: 快速验证Worker日志路径功能")
    print("   - 特点: 使用临时配置，运行时间短")
    print("   - 适合: 快速测试和验证")

    print("\n2. 完整功能Demo:")
    print("   - 文件: demo_worker_custom_config.py")
    print("   - 功能: 完整演示所有Worker功能")
    print("   - 特点: 多线程+多进程，详细验证")
    print("   - 适合: 全面了解功能")

    print("\n3. 验证要点:")
    print("   - 使用非默认配置文件")
    print("   - Worker日志保存到正确路径")
    print("   - 多进程配置继承正常")
    print("   - 异步文件写入功能正常")


def run_all_demos():
    """运行所有Demo"""
    print("\n开始运行所有Demo...")

    demos = [
        ("简单测试", "demo_simple_test.py"),
        ("路径信息演示", "demo_path_info.py"),
        ("快速验证Demo", "demo_worker_path_quick.py"),
        ("完整功能Demo", "demo_worker_custom_config.py")
    ]

    results = []
    for demo_name, demo_script in demos:
        success = run_demo(demo_name, demo_script)
        results.append((demo_name, success))

        if success:
            print(f"\n等待3秒后运行下一个Demo...")
            import time
            time.sleep(3)

    # 显示总结
    print(f"\n{'=' * 60}")
    print("Demo运行总结")
    print(f"{'=' * 60}")

    for demo_name, success in results:
        status = "✓ 成功" if success else "❌ 失败"
        print(f"{demo_name}: {status}")

    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    print(f"\n总计: {success_count}/{total_count} 个Demo运行成功")


def main():
    """主函数"""
    print("Worker路径Demo运行器")
    print("本工具用于运行Worker自定义配置演示程序")

    while True:
        show_menu()

        try:
            choice = input("\n请选择 (0-8): ").strip()

            if choice == "0":
                print("退出Demo运行器")
                break

            elif choice == "1":
                run_demo("简单测试", "demo_simple_test.py")

            elif choice == "2":
                run_demo("路径信息演示", "demo_path_info.py")

            elif choice == "3":
                run_demo("调用者识别测试", "demo_caller_test.py")

            elif choice == "4":
                run_demo("调用者识别调试", "demo_debug_caller.py")

            elif choice == "5":
                run_demo("快速验证Demo", "demo_worker_path_quick.py")

            elif choice == "6":
                run_demo("完整功能Demo", "demo_worker_custom_config.py")

            elif choice == "7":
                run_all_demos()

            elif choice == "8":
                show_demo_info()

            else:
                print("无效选择，请输入0-8之间的数字")

        except KeyboardInterrupt:
            print("\n\n用户中断，退出Demo运行器")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")

    print("感谢使用Worker路径Demo运行器！")


if __name__ == "__main__":
    main()