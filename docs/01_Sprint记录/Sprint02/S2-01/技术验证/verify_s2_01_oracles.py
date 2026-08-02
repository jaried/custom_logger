"""Executable positive and negative controls for the S2-01 acceptance predicates."""

from __future__ import annotations

import argparse
import os
from collections.abc import Callable


CASES = (
    "D:/logs/run-01",
    "D:/logs/run-01/",
    "D:/logs/run-01\\",
    "D:/logs/run-01/\\",
)


def normalize_display(log_dir: str) -> str:
    return str(log_dir).rstrip("/\\") + os.sep


def raw_display(log_dir: str) -> str:
    return str(log_dir)


def assert_display_predicate(normalizer: Callable[[str], str]) -> None:
    for original in CASES:
        display = normalizer(original)
        assert display.endswith(("/", "\\")), display
        assert not display.endswith(("//", "\\\\")), display


def success_prompt_predicate(initialization_succeeded: bool) -> str:
    if initialization_succeeded:
        return (
            "日志系统初始化成功，日志目录: D:/logs/run-01/, 文件: full.log, warning.log"
        )
    return ""


def assert_queue_timing_predicate(prompt_factory: Callable[[bool], str]) -> None:
    success_output = prompt_factory(True)
    failure_output = prompt_factory(False)
    assert "日志系统初始化成功" in success_output
    assert "日志系统初始化成功" not in failure_output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("display", "bad-display", "queue", "bad-queue"),
        default="display",
    )
    mode = parser.parse_args().mode

    if mode == "display":
        assert_display_predicate(normalize_display)
        print("display_cases=4")
    elif mode == "bad-display":
        assert_display_predicate(raw_display)
    elif mode == "queue":
        assert_queue_timing_predicate(success_prompt_predicate)
        print("queue_success=1 queue_failure=1")
    else:
        assert_queue_timing_predicate(
            lambda succeeded: (
                success_prompt_predicate(True)
                if not succeeded
                else success_prompt_predicate(succeeded)
            )
        )


if __name__ == "__main__":
    main()
