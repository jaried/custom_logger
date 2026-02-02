# 验证调用栈获取
import traceback
import inspect


def inner_function():
    """最内层函数"""
    # 方法1: traceback.extract_stack()
    stack1 = traceback.extract_stack()
    print("=== 方法1: traceback.extract_stack() ===")
    for frame in stack1:
        print(f"  {frame.filename}:{frame.lineno} in {frame.name}")

    # 方法2: inspect.stack()
    print("\n=== 方法2: inspect.stack() ===")
    stack2 = inspect.stack()
    for frame_info in stack2:
        print(f"  {frame_info.filename}:{frame_info.lineno} in {frame_info.function}")

    return "done"


def middle_function():
    """中间层函数"""
    return inner_function()


def outer_function():
    """最外层函数"""
    return middle_function()


if __name__ == "__main__":
    print("验证调用栈获取能力...")
    result = outer_function()
    print(f"\n结果: {result}")
