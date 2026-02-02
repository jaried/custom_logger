# docs/05_预研/验证_20260202/verify_stack_in_logger.py
"""
验证调用栈在logger中调用的技术点

验证点：
1. traceback.extract_stack()在logger中调用时能正确获取用户代码位置
2. 调用栈格式化后能正确显示
3. 性能影响可接受
"""
import traceback
import time


class MockLogger:
    """模拟logger，验证内部调用traceback.extract_stack()的效果"""

    def __init__(self, name: str):
        self.name = name

    def get_call_stack_info(self) -> str:
        """获取调用栈信息（模拟logger内部方法）"""
        import os

        # 使用traceback.extract_stack()获取完整调用栈
        stack = traceback.extract_stack()

        # 过滤掉本文件的内部调用，保留用户代码
        user_frames = []
        for frame in stack:
            # 跳过本文件中的get_call_stack_info方法
            basename = os.path.basename(frame.filename)
            if basename == "verify_stack_in_logger.py" and frame.name == "get_call_stack_info":
                continue
            # 跳过本文件中的warning方法（logger内部）
            if basename == "verify_stack_in_logger.py" and frame.name == "warning":
                continue
            user_frames.append(frame)

        # 格式化调用栈
        if user_frames:
            formatted = traceback.format_list(user_frames)
            return ''.join(formatted)
        return "无法获取调用栈"

    def warning(self, message: str) -> None:
        """模拟warning级别日志"""
        stack_info = self.get_call_stack_info()
        print(f"[WARNING] {message}")
        print("调用栈：")
        print(stack_info)


def user_function_a():
    """用户代码A层"""
    logger = MockLogger("test_logger")
    logger.warning("这是一条警告信息")
    return


def user_function_b():
    """用户代码B层"""
    return user_function_a()


def user_function_c():
    """用户代码C层"""
    return user_function_b()


def verify_performance():
    """验证性能影响"""
    print("\n=== 性能验证 ===")

    # 测试100次调用的总时间
    iterations = 100
    start = time.perf_counter()

    logger = MockLogger("perf_test")
    for _ in range(iterations):
        stack = traceback.extract_stack()
        formatted = traceback.format_list(stack)

    end = time.perf_counter()
    total_ms = (end - start) * 1000
    avg_us = total_ms / iterations * 1000

    print(f"总耗时（{iterations}次）: {total_ms:.2f} ms")
    print(f"平均耗时: {avg_us:.2f} µs")
    print(f"结论: {'性能可接受' if avg_us < 1000 else '性能需优化'}")
    return


if __name__ == "__main__":
    print("=== 验证1: 在logger中调用traceback.extract_stack() ===")
    user_function_c()

    verify_performance()

    print("\n=== 验证完成 ===")
