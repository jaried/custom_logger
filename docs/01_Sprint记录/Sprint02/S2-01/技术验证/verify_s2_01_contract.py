"""Static contract oracle for the S2-01 initialization success message."""

from __future__ import annotations

import argparse
from pathlib import Path


PATTERNS = (
    'get_logger("manager")',
    "full.log",
    "warning.log",
    "日志系统初始化失败",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("contract", "bad-contract"), default="contract")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    source = (args.root / "src/custom_logger/manager.py").read_text(encoding="utf-8")
    patterns = PATTERNS if args.mode == "contract" else ("S2-01-missing-contract-pattern",)
    missing = [pattern for pattern in patterns if pattern not in source]
    if missing:
        raise SystemExit(f"missing contract patterns: {missing}")
    print(f"contract_patterns={len(PATTERNS)}")


if __name__ == "__main__":
    main()
