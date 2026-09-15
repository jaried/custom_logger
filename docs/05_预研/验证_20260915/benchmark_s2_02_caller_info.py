#!/usr/bin/env python3
"""S2-02 caller 定位固定性能对照脚本。"""

from __future__ import annotations

import argparse
import importlib
import json
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Callable

WARMUP = 10_000
ROUNDS = 7
ITERATIONS = 100_000


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--git-ref", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def _load_get_caller_info(source_root: Path):
    src_dir = source_root.resolve() / "src"
    sys.path.insert(0, str(src_dir))
    try:
        module = importlib.import_module("custom_logger.formatter")
    finally:
        sys.path.pop(0)
    return module.get_caller_info


def _build_cases(get_caller_info):
    def case_a():
        return get_caller_info()

    def case_b_inner():
        return get_caller_info()

    def case_b():
        return case_b_inner()

    expected_module = Path(__file__).stem[:16]
    case_a_line = case_a.__code__.co_firstlineno + 1
    case_b_line = case_b_inner.__code__.co_firstlineno + 1

    case_a_result = case_a()
    case_b_result = case_b()
    assert case_a_result == (expected_module, case_a_line)
    assert case_b_result == (expected_module, case_b_line)

    return {
        "case_a": (case_a, case_a_result),
        "case_b": (case_b, case_b_result),
    }


def _measure(probe: Callable[[], tuple[str, int]]) -> dict:
    for _ in range(WARMUP):
        probe()

    round_values = []
    for _ in range(ROUNDS):
        started = time.perf_counter_ns()
        for _ in range(ITERATIONS):
            probe()
        elapsed = time.perf_counter_ns() - started
        round_values.append(elapsed / ITERATIONS)

    return {
        "round_ns_per_call": round_values,
        "median_ns_per_call": statistics.median(round_values),
        "min_ns_per_call": min(round_values),
        "max_ns_per_call": max(round_values),
    }


def main() -> int:
    args = _parse_args()
    source_root = Path(args.source_root).resolve()
    output = Path(args.output).resolve()

    get_caller_info = _load_get_caller_info(source_root)
    cases = _build_cases(get_caller_info)

    result = {
        "git_ref": args.git_ref,
        "source_root": str(source_root),
        "sys_version": sys.version,
        "platform": platform.platform(),
        "config": {
            "show_call_chain": False,
            "show_debug_call_stack": False,
            "show_warning_stack": False,
        },
        "warmup": WARMUP,
        "rounds": ROUNDS,
        "iterations": ITERATIONS,
        "correctness": "pass",
        "cases": {},
    }

    for case_name, (probe, caller_result) in cases.items():
        measured = _measure(probe)
        measured["caller_result"] = [caller_result[0], caller_result[1]]
        result["cases"][case_name] = measured

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
