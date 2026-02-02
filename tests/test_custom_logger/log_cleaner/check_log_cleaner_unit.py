# tests/test_custom_logger/log_cleaner/check_log_cleaner_unit.py
"""
US-001 单元测试：日志过期清理模块

测试覆盖：
- 日期解析 (parse_directory_date)
- 过期判断 (is_expired)
- 配置读取 (get_retention_days)
"""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from custom_logger.log_cleaner import (
    parse_directory_date,
    is_expired,
    get_retention_days,
    _ensure_retention_config,
)


class TestParseDirectoryDate:
    """测试日期解析函数"""

    def test_tc001_valid_date_format(self):
        """UT-101: 正常 - 有效日期格式"""
        result = parse_directory_date("20260101")
        assert result == datetime(2026, 1, 1)

    def test_tc002_leap_year_date(self):
        """UT-102: 正常 - 闰年日期"""
        result = parse_directory_date("20240229")
        assert result == datetime(2024, 2, 29)

    def test_tc003_non_digit_string(self):
        """UT-103: 边界 - 非数字字符串"""
        result = parse_directory_date("invalid")
        assert result is None

    def test_tc004_length_too_short(self):
        """UT-104: 边界 - 长度不足"""
        result = parse_directory_date("202601")
        assert result is None

    def test_tc005_length_too_long(self):
        """UT-105: 边界 - 长度过长"""
        result = parse_directory_date("20260101123")
        assert result is None

    def test_tc006_invalid_date(self):
        """UT-106: 异常 - 无效日期（2月30日）"""
        result = parse_directory_date("20260230")
        assert result is None


class TestIsExpired:
    """测试过期判断函数"""

    def test_tc101_not_expired(self):
        """UT-201: 正常 - 未过期"""
        dir_date = datetime.now() - timedelta(days=3)
        result = is_expired(dir_date, 7)
        assert result is False

    def test_tc102_exactly_expired(self):
        """UT-202: 正常 - 刚好过期"""
        dir_date = datetime.now() - timedelta(days=8)
        result = is_expired(dir_date, 7)
        assert result is True

    def test_tc103_zero_days_diff(self):
        """UT-203: 边界 - 零天差（今天）"""
        dir_date = datetime.now()
        result = is_expired(dir_date, 7)
        assert result is False

    def test_tc104_negative_days_diff(self):
        """UT-204: 边界 - 负天数差（未来日期）"""
        dir_date = datetime.now() + timedelta(days=1)
        result = is_expired(dir_date, 7)
        assert result is False

    def test_tc105_zero_retention_days(self):
        """UT-205: 异常 - 保留天数为0"""
        dir_date = datetime.now() - timedelta(days=1)
        result = is_expired(dir_date, 0)
        assert result is True

    def test_tc106_negative_retention_days(self):
        """UT-206: 异常 - 保留天数为负"""
        dir_date = datetime.now()
        result = is_expired(dir_date, -1)
        assert result is True


class TestGetRetentionDays:
    """测试配置读取函数"""

    def test_tc201_config_exists(self):
        """UT-001: 正常 - 配置项存在"""
        config = Mock()
        config.logger = {"log_retention_days": 7}
        result = get_retention_days(config)
        assert result == 7

    def test_tc202_config_other_value(self):
        """UT-002: 正常 - 配置项为其他值"""
        config = Mock()
        config.logger = {"log_retention_days": 30}
        result = get_retention_days(config)
        assert result == 30

    def test_tc203_config_zero(self):
        """UT-003: 边界 - 配置项为0"""
        config = Mock()
        config.logger = {"log_retention_days": 0}
        result = get_retention_days(config)
        assert result == 0

    def test_tc204_config_negative(self):
        """UT-004: 边界 - 配置项为负数"""
        config = Mock()
        config.logger = {"log_retention_days": -1}
        result = get_retention_days(config)
        assert result == -1

    def test_tc205_config_missing(self):
        """UT-005: 异常 - 配置项不存在，使用默认值"""
        config = Mock()
        config.logger = {}
        result = get_retention_days(config)
        assert result == 7

    def test_tc206_config_none(self):
        """UT-006: 异常 - config对象为None"""
        with pytest.raises(ValueError, match="config不能为None"):
            get_retention_days(None)


class TestEnsureRetentionConfig:
    """测试配置初始化函数"""

    def test_tc301_config_missing_attr(self):
        """测试：配置对象没有logger属性"""
        config = Mock()
        config.logger = {}
        result = _ensure_retention_config(config)
        assert result == 7
        assert config.logger["log_retention_days"] == 7

    def test_tc302_config_exists(self):
        """测试：配置项已存在"""
        config = Mock()
        config.logger = {"log_retention_days": 14}
        result = _ensure_retention_config(config)
        assert result == 14
        assert config.logger["log_retention_days"] == 14
