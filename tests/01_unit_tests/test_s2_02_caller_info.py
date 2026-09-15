# tests/01_unit_tests/test_s2_02_caller_info.py
from __future__ import annotations

from datetime import datetime
import inspect
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from custom_logger import init_custom_logger_system, tear_down_custom_logger_system
from custom_logger.formatter import create_log_line, get_caller_info


@pytest.fixture(autouse=True)
def cleanup_logger_system():
    tear_down_custom_logger_system()
    yield
    tear_down_custom_logger_system()


def _build_config(tmp_path, show_call_chain: bool = False, show_debug: bool = False):
    logger_config = SimpleNamespace(
        global_console_level="debug",
        global_file_level="debug",
        show_call_chain=show_call_chain,
        show_debug_call_stack=show_debug,
        show_warning_stack=False,
        module_levels={},
    )
    config = SimpleNamespace(
        first_start_time=datetime.now(),
        paths={"log_dir": str(tmp_path)},
        logger=logger_config,
    )
    return config


def _probe_caller_info():
    expected_line = inspect.currentframe().f_lineno + 1
    caller = get_caller_info()
    return caller, expected_line


def test_s2_02_direct_caller_location(tmp_path):
    init_custom_logger_system(_build_config(tmp_path))
    expected_line = inspect.currentframe().f_lineno + 1
    module_name, line_number = get_caller_info()
    assert module_name == Path(__file__).stem[:16]
    assert line_number == expected_line


def test_s2_02_nested_probe_location(tmp_path):
    init_custom_logger_system(_build_config(tmp_path))
    (module_name, line_number), expected_line = _probe_caller_info()
    assert module_name == Path(__file__).stem[:16]
    assert line_number == expected_line


def test_s2_02_create_log_line_location(tmp_path):
    init_custom_logger_system(_build_config(tmp_path))
    expected_line = inspect.currentframe().f_lineno + 1
    log_line = create_log_line("INFO", "caller test", "ignored", (), {})
    assert Path(__file__).stem[:16] in log_line
    assert f": {expected_line:>4}]" in log_line


def test_s2_02_plain_path_ignores_inspect_stack_and_getframeinfo(tmp_path):
    init_custom_logger_system(_build_config(tmp_path))
    with patch("custom_logger.formatter.inspect.stack", side_effect=AssertionError("stack called")):
        with patch(
            "custom_logger.formatter.inspect.getframeinfo",
            side_effect=AssertionError("getframeinfo called"),
        ):
            expected_line = inspect.currentframe().f_lineno + 1
            module_name, line_number = get_caller_info()
    assert module_name == Path(__file__).stem[:16]
    assert line_number == expected_line


def test_s2_02_currentframe_none_returns_main():
    with patch("custom_logger.formatter.inspect.currentframe", return_value=None):
        assert get_caller_info() == ("main", 0)


def test_s2_02_currentframe_exception_returns_error(tmp_path, capsys):
    init_custom_logger_system(_build_config(tmp_path, show_call_chain=True))
    with patch(
        "custom_logger.formatter.inspect.currentframe",
        side_effect=RuntimeError("frame failure"),
    ):
        assert get_caller_info() == ("error", 0)
    captured = capsys.readouterr()
    assert "[调用链异常] frame failure" in captured.out


def test_s2_02_module_name_is_truncated_to_16_chars(tmp_path):
    init_custom_logger_system(_build_config(tmp_path))
    module_name, _ = get_caller_info()
    assert module_name == Path(__file__).stem[:16]
    assert len(module_name) == 16


def test_s2_02_diagnostics_disabled_do_not_build_full_stack(tmp_path, capsys):
    init_custom_logger_system(_build_config(tmp_path))
    with patch(
        "custom_logger.formatter._get_call_stack_info",
        side_effect=AssertionError("diagnostic stack called"),
    ):
        module_name, line_number = get_caller_info()
    captured = capsys.readouterr()
    assert module_name == Path(__file__).stem[:16]
    assert line_number > 0
    assert "[调用链]" not in captured.out
    assert "DEBUG: get_caller_info调用链:" not in captured.out
