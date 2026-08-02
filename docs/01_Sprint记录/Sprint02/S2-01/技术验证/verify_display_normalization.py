"""Validate the display-only directory normalization selected for S2-01."""

import os


def normalize_display_path(log_dir: object) -> str:
    """Return one native directory separator without mutating the input value."""
    return str(log_dir).rstrip("/\\") + os.sep


def check_display_normalization() -> None:
    samples = (
        "D:/logs/run-01",
        "D:/logs/run-01/",
        "D:/logs/run-01\\",
        "D:/logs/run-01/\\",
    )
    originals = samples

    for original in samples:
        displayed = normalize_display_path(original)
        assert displayed.endswith(os.sep), displayed
        assert not displayed.endswith(("//", "\\\\")), displayed
        print(f"input={original!r} output={displayed!r}")

    assert samples == originals, "normalization must not mutate configuration values"
    print(f"native_separator={os.sep!r}")
    print("display_normalization=PASS")


if __name__ == "__main__":
    check_display_normalization()
