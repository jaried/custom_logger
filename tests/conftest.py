# tests/conftest.py
from __future__ import annotations
from datetime import datetime
start_time = datetime.now()

import sys
import os
from pathlib import Path

# 确保能找到src目录
project_root = Path(__file__).parent.parent  # 从tests目录向上到项目根目录
src_path = project_root / "src"

# 添加src目录到Python路径的最前面
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

print(f"项目根目录: {project_root}")
print(f"src路径: {src_path}")
print(f"src目录存在: {src_path.exists()}")

# 确保custom_logger目录存在
custom_logger_path = src_path / "custom_logger"
print(f"custom_logger路径: {custom_logger_path}")
print(f"custom_logger目录存在: {custom_logger_path.exists()}")

# 显示Python路径
print("Python路径:")
for i, path in enumerate(sys.path[:5]):  # 只显示前5个
    print(f"  {i}: {path}")

pass
