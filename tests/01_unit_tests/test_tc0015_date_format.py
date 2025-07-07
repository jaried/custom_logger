# tests/01_unit_tests/test_tc0015_date_format.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from custom_logger.config import _create_log_dir


class TestDateFormat:
    """测试日期格式变更：从yyyymmdd改为yyyy-mm-dd"""

    def test_tc0015_001_new_date_format_basic(self):
        """测试基本的新日期格式 yyyy-mm-dd"""
        # 创建模拟配置对象
        cfg = MagicMock()
        cfg.base_dir = tempfile.gettempdir()
        cfg.project_name = 'test_proj'
        cfg.experiment_name = 'test_exp'
        cfg.first_start_time = '2025-01-01T12:00:00'
        
        with patch('custom_logger.config.is_debug', return_value=False):
            result = _create_log_dir(cfg)
        
        # 验证新的日期格式 yyyy-mm-dd
        assert '2025-01-01' in result
        assert '120000' in result
        
        # 验证路径结构
        expected_parts = ['test_proj', 'test_exp', '2025-01-01', '120000']
        for part in expected_parts:
            assert part in result

    def test_tc0015_002_multiple_date_formats(self):
        """测试多个不同日期的新格式"""
        test_cases = [
            ('2025-01-01T12:00:00', '2025-01-01', '120000'),
            ('2025-12-31T23:59:59', '2025-12-31', '235959'),
            ('2024-02-29T06:30:15', '2024-02-29', '063015'),  # 闰年
            ('2023-07-15T14:45:30', '2023-07-15', '144530'),
        ]
        
        for time_str, expected_date, expected_time in test_cases:
            cfg = MagicMock()
            cfg.base_dir = tempfile.gettempdir()
            cfg.project_name = 'test_proj'
            cfg.experiment_name = 'test_exp'
            cfg.first_start_time = time_str
            
            with patch('custom_logger.config.is_debug', return_value=False):
                result = _create_log_dir(cfg)
            
            assert expected_date in result, f"日期格式错误，期望 {expected_date} 在路径 {result} 中"
            assert expected_time in result, f"时间格式错误，期望 {expected_time} 在路径 {result} 中"

    def test_tc0015_003_debug_mode_with_new_date_format(self):
        """测试调试模式下的新日期格式"""
        cfg = MagicMock()
        cfg.base_dir = tempfile.gettempdir()
        cfg.project_name = 'debug_proj'
        cfg.experiment_name = 'debug_exp'
        cfg.first_start_time = '2025-06-15T09:30:45'
        
        with patch('custom_logger.config.is_debug', return_value=True):
            result = _create_log_dir(cfg)
        
        # 验证debug模式下的路径包含debug层级
        assert 'debug' in result
        assert '2025-06-15' in result
        assert '093045' in result
        assert 'debug_proj' in result
        assert 'debug_exp' in result

    def test_tc0015_004_date_format_consistency(self):
        """测试日期格式的一致性"""
        # 使用datetime对象
        test_datetime = datetime(2025, 3, 8, 16, 20, 35)
        
        cfg = MagicMock()
        cfg.base_dir = tempfile.gettempdir()
        cfg.project_name = 'consistency_proj'
        cfg.experiment_name = 'consistency_exp'
        cfg.first_start_time = test_datetime.isoformat()
        
        with patch('custom_logger.config.is_debug', return_value=False):
            result = _create_log_dir(cfg)
        
        # 验证格式化结果
        expected_date = test_datetime.strftime("%Y-%m-%d")  # 2025-03-08
        expected_time = test_datetime.strftime("%H%M%S")    # 162035
        
        assert expected_date in result
        assert expected_time in result

    def test_tc0015_005_invalid_date_fallback(self):
        """测试无效日期时的回退机制"""
        cfg = MagicMock()
        cfg.base_dir = tempfile.gettempdir()
        cfg.project_name = 'fallback_proj'
        cfg.experiment_name = 'fallback_exp'
        cfg.first_start_time = 'invalid_date_string'
        
        with patch('custom_logger.config.is_debug', return_value=False):
            # 应该使用当前时间作为回退
            result = _create_log_dir(cfg)
        
        # 验证路径包含项目和实验名称
        assert 'fallback_proj' in result
        assert 'fallback_exp' in result
        
        # 验证日期格式为 yyyy-mm-dd（当前日期）
        current_date = datetime.now().strftime("%Y-%m-%d")
        # 由于时间可能跨越日期边界，我们检查年份格式
        assert '2025-' in result or '2024-' in result or '2026-' in result

    def test_tc0015_006_none_date_fallback(self):
        """测试None日期时的回退机制"""
        cfg = MagicMock()
        cfg.base_dir = tempfile.gettempdir()
        cfg.project_name = 'none_proj'
        cfg.experiment_name = 'none_exp'
        cfg.first_start_time = None
        
        with patch('custom_logger.config.is_debug', return_value=False):
            result = _create_log_dir(cfg)
        
        # 验证路径包含项目和实验名称
        assert 'none_proj' in result
        assert 'none_exp' in result
        
        # 验证使用了当前时间的日期格式
        current_year = datetime.now().year
        assert str(current_year) in result

    def test_tc0015_007_path_separator_handling(self):
        """测试路径分隔符处理"""
        cfg = MagicMock()
        cfg.base_dir = tempfile.gettempdir().replace("\\", "/")
        cfg.project_name = 'path_proj'
        cfg.experiment_name = 'path_exp'
        cfg.first_start_time = '2025-05-20T11:15:25'
        
        with patch('custom_logger.config.is_debug', return_value=False):
            result = _create_log_dir(cfg)
        
        # 验证路径结构正确
        assert 'path_proj' in result
        assert 'path_exp' in result
        assert '2025-05-20' in result
        assert '111525' in result
        
        # 验证路径是有效的
        assert os.path.isabs(result) or result.startswith('d:')

    def test_tc0015_008_edge_case_dates(self):
        """测试边界情况的日期"""
        edge_cases = [
            ('2025-01-01T00:00:00', '2025-01-01', '000000'),  # 年初
            ('2025-12-31T23:59:59', '2025-12-31', '235959'),  # 年末
            ('2024-02-29T12:00:00', '2024-02-29', '120000'),  # 闰年2月29日
            ('2025-02-28T12:00:00', '2025-02-28', '120000'),  # 非闰年2月28日
        ]
        
        for time_str, expected_date, expected_time in edge_cases:
            cfg = MagicMock()
            cfg.base_dir = tempfile.gettempdir()
            cfg.project_name = 'edge_proj'
            cfg.experiment_name = 'edge_exp'
            cfg.first_start_time = time_str
            
            with patch('custom_logger.config.is_debug', return_value=False):
                result = _create_log_dir(cfg)
            
            assert expected_date in result, f"边界日期测试失败: {time_str}"
            assert expected_time in result, f"边界时间测试失败: {time_str}" 