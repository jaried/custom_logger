# docs/05_预研/验证_20260307/verify_s1_07_size_unit_display.py
from __future__ import annotations

ONE_KB: int = 1024
ONE_MB: int = 1024 * 1024


def format_released_space(freed_bytes: int) -> str:
    if freed_bytes < 0:
        raise ValueError("freed_bytes 不能为负数")
    if freed_bytes >= ONE_MB:
        return f"{freed_bytes / ONE_MB:.2f} MB"
    return f"{freed_bytes / ONE_KB:.2f} KB"


def main() -> None:
    print('=== S1-07 技术验证：日志清理空间单位显示 ===')

    checks = [
        (0, '0.00 KB'),
        (1024, '1.00 KB'),
        (ONE_MB - 1, '1024.00 KB'),
        (ONE_MB, '1.00 MB'),
        (round(98890.11 * ONE_KB), '96.57 MB'),
    ]

    for freed_bytes, expected in checks:
        actual = format_released_space(freed_bytes)
        print(f'输入: {freed_bytes} bytes -> 输出: {actual}')
        if actual != expected:
            raise AssertionError(f'期望 {expected}，实际 {actual}')

    try:
        format_released_space(-1)
    except ValueError as exc:
        print(f'负数保护: {exc}')
    else:
        raise AssertionError('负数输入未抛出 ValueError')

    print('=== 验证通过 ===')


if __name__ == '__main__':
    main()
