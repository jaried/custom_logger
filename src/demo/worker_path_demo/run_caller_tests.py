# tests/test_custom_logger/run_caller_tests.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import sys
import os

# 确保能找到src目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import pytest


def run_caller_identification_tests():
    """运行调用者识别相关的测试"""
    print("运行调用者识别测试")
    print("=" * 50)

    # 运行特定的测试文件
    test_file = os.path.join(os.path.dirname(__file__), "test_tc0012_caller_identification.py")

    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return False

    try:
        # 使用pytest运行测试
        result = pytest.main([
            test_file,
            "-v",  # 详细输出
            "--tb=short",  # 简短的错误信息
            "--no-header",  # 不显示header
        ])

        if result == 0:
            print("✅ 所有调用者识别测试通过")
            return True
        else:
            print("❌ 部分测试失败")
            return False

    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
        return False


def run_specific_tests():
    """运行特定的调用者识别测试"""
    print("\n运行关键测试用例")
    print("-" * 30)

    test_cases = [
        "test_tc0012_001_get_caller_info_basic",
        "test_tc0012_005_thread_caller_identification",
        "test_tc0012_013_worker_thread_file_identification",
        "test_tc0012_014_main_function_line_number",
    ]

    test_file = os.path.join(os.path.dirname(__file__), "test_tc0012_caller_identification.py")

    for test_case in test_cases:
        print(f"\n运行: {test_case}")
        result = pytest.main([
            f"{test_file}::{test_case}",
            "-v",
            "--tb=line",
        ])

        if result == 0:
            print(f"✅ {test_case} 通过")
        else:
            print(f"❌ {test_case} 失败")


if __name__ == "__main__":
    print("调用者识别测试运行器")
    print("=" * 50)

    # 运行所有测试
    success = run_caller_identification_tests()

    # 运行关键测试
    run_specific_tests()

    if success:
        print("\n🎉 调用者识别功能测试完成")
    else:
        print("\n⚠️  存在测试失败，需要进一步修复")
        sys.exit(1)