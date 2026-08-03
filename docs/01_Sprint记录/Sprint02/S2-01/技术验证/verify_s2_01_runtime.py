"""Exercise the S2-01 production initialization prompt without real I/O."""

from __future__ import annotations

import argparse
import io
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

import src.custom_logger.log_cleaner as log_cleaner_module
import src.custom_logger.manager as manager_module

CASES = (
    "D:/logs/run-01",
    "D:/logs/run-01/",
    "D:/logs/run-01\\",
    "D:/logs/run-01/\\",
)


class CapturingLogger:
    """Collect the production logger message while manager initialization runs."""

    def __init__(self):
        self.messages = []

    def info(self, message):
        self.messages.append(message)


def build_config(log_dir, *, enable_queue_mode, include_queue_info):
    config = SimpleNamespace(
        paths=SimpleNamespace(log_dir=log_dir),
        first_start_time=object(),
        logger=SimpleNamespace(enable_queue_mode=enable_queue_mode),
    )
    if include_queue_info:
        config.queue_info = SimpleNamespace(log_queue=object())
    return config


def run_initialization(
    log_dir,
    *,
    enable_queue_mode=False,
    include_queue_info=False,
    separator=None,
):
    """Run manager's production function with its I/O collaborators isolated."""
    capture_logger = CapturingLogger()
    config = build_config(
        log_dir,
        enable_queue_mode=enable_queue_mode,
        include_queue_info=include_queue_info,
    )
    error = None
    manager_module._initialized = False
    manager_module._queue_mode = False

    with ExitStack() as stack:
        stack.enter_context(patch.object(manager_module, "init_config_from_object"))
        stack.enter_context(patch.object(manager_module, "init_writer"))
        stack.enter_context(patch.object(manager_module, "init_queue_receiver"))
        stack.enter_context(patch.object(manager_module.atexit, "register"))
        stack.enter_context(
            patch.object(manager_module, "get_logger", return_value=capture_logger)
        )
        stack.enter_context(patch.object(log_cleaner_module, "cleanup_expired_logs"))
        stack.enter_context(patch.object(log_cleaner_module, "reset_cleanup_flag"))
        stack.enter_context(redirect_stdout(io.StringIO()))
        stack.enter_context(redirect_stderr(io.StringIO()))
        if separator is not None:
            stack.enter_context(patch.object(manager_module.os, "sep", separator))
        try:
            manager_module.init_custom_logger_system(config)
        except ValueError as caught_error:
            error = caught_error
        finally:
            manager_module._initialized = False
            manager_module._queue_mode = False

    return capture_logger.messages, config.paths.log_dir, error


def assert_display_predicate(separator=None):
    for original in CASES:
        messages, configured_log_dir, error = run_initialization(
            original, separator=separator
        )
        assert error is None, error
        assert len(messages) == 1, messages
        message = messages[0]
        displayed_log_dir = message.split("日志目录: ", 1)[1].split(", 文件:", 1)[0]
        assert displayed_log_dir.endswith(("/", "\\")), displayed_log_dir
        assert not displayed_log_dir.endswith(("//", "\\\\")), displayed_log_dir
        assert "full.log" in message and "warning.log" in message
        assert configured_log_dir == original


def assert_queue_timing_predicate(failure_messages=None):
    success_messages, _, success_error = run_initialization(
        "D:/logs/queue", enable_queue_mode=True, include_queue_info=True
    )
    actual_failure_messages, _, failure_error = run_initialization(
        "D:/logs/queue", enable_queue_mode=True, include_queue_info=False
    )
    assert success_error is None, success_error
    assert isinstance(failure_error, ValueError), failure_error
    assert len(success_messages) == 1, success_messages
    assert not actual_failure_messages, actual_failure_messages

    failure_messages = (
        actual_failure_messages if failure_messages is None else failure_messages
    )
    assert "日志系统初始化成功" in success_messages[0]
    assert not failure_messages, failure_messages


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("display", "bad-display", "queue", "bad-queue"),
        default="display",
    )
    mode = parser.parse_args().mode

    if mode == "display":
        assert_display_predicate()
        print("runtime_display_cases=4")
    elif mode == "bad-display":
        assert_display_predicate(separator="")
    elif mode == "queue":
        assert_queue_timing_predicate()
        print("runtime_queue_success=1 runtime_queue_failure=1")
    else:
        assert_queue_timing_predicate(failure_messages=["日志系统初始化成功"])


if __name__ == "__main__":
    main()
