# tests/test_custom_logger/test_tc0001_types.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import pytest
from custom_logger.types import (
    DEBUG, INFO, WARNING, ERROR, CRITICAL, EXCEPTION,
    DETAIL, W_SUMMARY, W_DETAIL,
    LEVEL_NAME_TO_VALUE, VALUE_TO_LEVEL_NAME,
    parse_level_name, get_level_name
)


def test_tc0001_001_level_constants():
    """测试级别常量值是否正确"""
    assert DEBUG == 10
    assert INFO == 20
    assert WARNING == 30
    assert ERROR == 40
    assert CRITICAL == 50
    assert EXCEPTION == 60
    assert DETAIL == 8
    assert W_SUMMARY == 5
    assert W_DETAIL == 3
    pass


def test_tc0001_002_level_name_mapping():
    """测试级别名称映射是否完整"""
    expected_mapping = {
        "debug": 10,
        "info": 20,
        "warning": 30,
        "error": 40,
        "critical": 50,
        "exception": 60,
        "detail": 8,
        "w_summary": 5,
        "w_detail": 3,
    }

    assert LEVEL_NAME_TO_VALUE == expected_mapping

    # 验证反向映射
    for name, value in expected_mapping.items():
        assert VALUE_TO_LEVEL_NAME[value] == name
    pass


def test_tc0001_003_parse_level_name_valid():
    """测试解析有效的级别名称"""
    assert parse_level_name("debug") == 10
    assert parse_level_name("INFO") == 20
    assert parse_level_name(" Warning ") == 30
    assert parse_level_name("ERROR") == 40
    assert parse_level_name("critical") == 50
    assert parse_level_name("exception") == 60
    assert parse_level_name("detail") == 8
    assert parse_level_name("w_summary") == 5
    assert parse_level_name("w_detail") == 3
    pass


def test_tc0001_004_parse_level_name_invalid():
    """测试解析无效的级别名称"""
    with pytest.raises(ValueError, match="无效的日志级别"):
        parse_level_name("invalid_level")

    with pytest.raises(ValueError, match="无效的日志级别"):
        parse_level_name("")

    with pytest.raises(ValueError, match="无效的日志级别"):
        parse_level_name("trace")
    pass


def test_tc0001_005_parse_level_name_non_string():
    """测试解析非字符串参数"""
    with pytest.raises(ValueError, match="级别名称必须是字符串"):
        parse_level_name(123)

    with pytest.raises(ValueError, match="级别名称必须是字符串"):
        parse_level_name(None)

    with pytest.raises(ValueError, match="级别名称必须是字符串"):
        parse_level_name([])
    pass


def test_tc0001_006_get_level_name_valid():
    """测试获取有效级别的名称"""
    assert get_level_name(10) == "debug"
    assert get_level_name(20) == "info"
    assert get_level_name(30) == "warning"
    assert get_level_name(40) == "error"
    assert get_level_name(50) == "critical"
    assert get_level_name(60) == "exception"
    assert get_level_name(8) == "detail"
    assert get_level_name(5) == "w_summary"
    assert get_level_name(3) == "w_detail"
    pass


def test_tc0001_007_get_level_name_invalid():
    """测试获取无效级别值的名称"""
    with pytest.raises(ValueError, match="无效的日志级别数值"):
        get_level_name(999)

    with pytest.raises(ValueError, match="无效的日志级别数值"):
        get_level_name(-1)

    with pytest.raises(ValueError, match="无效的日志级别数值"):
        get_level_name(0)
    pass


def test_tc0001_008_case_insensitive():
    """测试大小写不敏感"""
    test_cases = [
        ("DEBUG", 10),
        ("debug", 10),
        ("Debug", 10),
        ("INFO", 20),
        ("info", 20),
        ("W_SUMMARY", 5),
        ("w_summary", 5),
        ("W_Summary", 5),
    ]

    for level_name, expected_value in test_cases:
        assert parse_level_name(level_name) == expected_value
    pass


def test_tc0001_009_whitespace_handling():
    """测试空白字符处理"""
    assert parse_level_name("  debug  ") == 10
    assert parse_level_name("\tdebug\t") == 10
    assert parse_level_name("\ndebug\n") == 10
    assert parse_level_name("debug ") == 10
    assert parse_level_name(" debug") == 10
    pass


def test_tc0001_010_level_ordering():
    """测试级别顺序是否正确"""
    levels = [W_DETAIL, W_SUMMARY, DETAIL, DEBUG, INFO, WARNING, ERROR, CRITICAL, EXCEPTION]

    # 验证顺序递增
    for i in range(len(levels) - 1):
        assert levels[i] < levels[i + 1], f"Level {levels[i]} should be < {levels[i + 1]}"
    pass