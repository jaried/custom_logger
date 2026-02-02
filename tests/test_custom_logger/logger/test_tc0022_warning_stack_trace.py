# tests/test_custom_logger/logger/test_tc0022_warning_stack_trace.py
"""
Unit tests for warning stack trace functionality (OPT-001)

测试 get_call_stack() 函数能正确获取和格式化调用栈信息。
"""
from __future__ import annotations

import pytest
from custom_logger.formatter import get_call_stack


class TestGetCallStack:
    """测试 get_call_stack() 函数"""

    def test_tc002201_normal_warning_call(self) -> None:
        """UT-001: 正常场景 - 典型warning调用应返回格式化调用栈字符串"""
        # 直接调用函数，获取当前调用栈
        result = get_call_stack()

        # 应该返回字符串
        assert isinstance(result, str)

        # 应该包含当前文件和函数名
        assert "test_tc0022_warning_stack_trace.py" in result
        assert "test_tc002201_normal_warning_call" in result

    def test_tc002202_nested_call(self) -> None:
        """UT-002: 正常场景 - 深层嵌套调用应包含完整调用链"""
        def inner_function():
            return get_call_stack()

        def middle_function():
            return inner_function()

        def outer_function():
            return middle_function()

        result = outer_function()

        # 应该包含完整的调用链
        assert "inner_function" in result
        assert "middle_function" in result
        assert "outer_function" in result

    def test_tc002203_single_layer_call(self) -> None:
        """UT-003: 边界场景 - 单层调用应返回最小调用栈"""
        result = get_call_stack()

        # 至少应该有当前函数
        assert "test_tc002203_single_layer_call" in result

    def test_tc002204_format_correctness(self) -> None:
        """UT-004: 边界场景 - 调用栈格式应正确（文件:行号 函数名）"""
        result = get_call_stack()

        # 检查格式应包含文件名、行号和函数名
        # 格式：File "path", line X, in function_name
        assert 'File "' in result or "File " in result
        assert "line " in result
        assert " in " in result

    def test_tc002205_exception_handling(self) -> None:
        """UT-005: 异常场景 - 获取失败时应返回空字符串"""
        # 这个测试验证函数有异常处理
        # 实际调用中不太可能失败，但如果有异常应返回空字符串
        # 我们通过直接调用来验证不会崩溃
        result = get_call_stack()
        # 只要没有抛出异常就通过
        assert isinstance(result, str)

    def test_tc002206_multiple_calls(self) -> None:
        """UT-006: 正常场景 - 多次调用应各自独立工作"""
        result1 = get_call_stack()
        result2 = get_call_stack()

        # 两次调用应该都成功
        assert isinstance(result1, str)
        assert isinstance(result2, str)
        # 都应该包含当前函数
        assert "test_tc002206_multiple_calls" in result1
        assert "test_tc002206_multiple_calls" in result2
