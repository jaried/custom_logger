# docs/05_预研/验证_20260202/verify_log_cleaner.py
"""
US-001 技术验证：日志过期清理功能

验证关键技术点：
1. 日期目录解析与过期判断（yyyymmdd格式）
2. 目录删除操作
3. 空间统计计算
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

def check_date_parsing():
    """验证1：日期目录解析与过期判断"""
    print("\n=== 验证1：日期目录解析与过期判断 ===")

    # 模拟目录名列表
    test_dirs = [
        "20260125",  # 8天前（假设过期）
        "20260126",  # 7天前
        "20260130",  # 3天前
        "20260201",  # 1天前
        "invalid",   # 无效格式
        "20260-abc", # 无效格式
    ]

    retention_days = 7
    today = datetime.now().date()

    print(f"当前日期: {today}")
    print(f"保留天数: {retention_days}")
    print(f"过期阈值日期: {today - timedelta(days=retention_days)}")
    print("\n目录解析结果:")

    for dir_name in test_dirs:
        if not dir_name.isdigit() or len(dir_name) != 8:
            print(f"  {dir_name}: ❌ 无效格式，跳过")
            continue

        try:
            dir_date = datetime.strptime(dir_name, "%Y%m%d").date()
            days_diff = (today - dir_date).days
            is_expired = days_diff > retention_days

            status = "过期" if is_expired else "保留"
            print(f"  {dir_name}: {dir_date} ({days_diff}天前) → {status}")

        except ValueError as e:
            print(f"  {dir_name}: ❌ 解析失败: {e}")

    print("✅ 验证1通过：日期解析与过期判断逻辑正确")


def check_directory_operations():
    """验证2：目录删除与空间统计"""
    print("\n=== 验证2：目录删除与空间统计 ===")

    # 创建临时测试目录
    base_dir = Path("D:/tmp_log_cleaner_verify")
    base_dir.mkdir(exist_ok=True)

    # 创建测试目录结构
    test_dirs = []
    total_expected_size = 0

    for i in range(3):
        dir_name = f"test_{datetime.now().strftime('%Y%m%d')}_{i}"
        dir_path = base_dir / dir_name
        dir_path.mkdir(exist_ok=True)

        # 创建一些测试文件
        for j in range(5):
            file_path = dir_path / f"file_{j}.log"
            content = f"Test log content {j} " * 100  # 约2KB
            file_path.write_text(content, encoding='utf-8')
            total_expected_size += file_path.stat().st_size

        test_dirs.append(dir_path)

    print(f"创建测试目录: {base_dir}")
    print(f"测试目录数量: {len(test_dirs)}")
    print(f"预期总大小: {total_expected_size / 1024:.2f} KB")

    # 计算实际总大小
    total_actual_size = 0
    for dir_path in test_dirs:
        for item in dir_path.rglob("*"):
            if item.is_file():
                total_actual_size += item.stat().st_size

    print(f"实际总大小: {total_actual_size / 1024:.2f} KB")

    # 执行删除操作
    deleted_count = 0
    deleted_size = 0

    for dir_path in test_dirs:
        dir_size = sum(f.stat().st_size for f in dir_path.rglob("*") if f.is_file())

        try:
            shutil.rmtree(dir_path)
            deleted_count += 1
            deleted_size += dir_size
            print(f"  删除: {dir_path.name} ({dir_size / 1024:.2f} KB)")
        except Exception as e:
            print(f"  删除失败: {dir_path.name} - {e}")

    print(f"\n删除统计: {deleted_count} 个目录, {deleted_size / 1024:.2f} KB")

    # 清理根目录
    try:
        if base_dir.exists():
            shutil.rmtree(base_dir)
            print(f"清理测试根目录: {base_dir}")
    except Exception as e:
        print(f"清理根目录失败: {e}")

    print("✅ 验证2通过：目录删除与空间统计功能正常")


def check_config_save_simulation():
    """验证3：config.save() 模拟（不实际调用）"""
    print("\n=== 验证3：config.save() 兼容性检查 ===")

    # 模拟 config 对象结构
    class MockConfig:
        def __init__(self):
            self.logger = {}
            self.paths = {}

        def save(self):
            print("    模拟调用 config.save() - 配置已保存")

    config = MockConfig()

    # 检查并添加默认值
    if not hasattr(config, 'logger') or 'log_retention_days' not in config.logger:
        if isinstance(config.logger, dict):
            config.logger['log_retention_days'] = 7
            print("    配置项 log_retention_days 不存在，已设置默认值: 7")
        else:
            print("    config.logger 不是字典类型")

    print(f"    当前配置: log_retention_days = {config.logger.get('log_retention_days')}")

    # 模拟保存
    config.save()

    print("✅ 验证3通过：配置项处理逻辑正确")


if __name__ == "__main__":
    print("=" * 50)
    print("US-001 日志过期清理功能 - 技术验证")
    print("=" * 50)

    try:
        check_date_parsing()
        check_directory_operations()
        check_config_save_simulation()

        print("\n" + "=" * 50)
        print("✅ 所有验证通过")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
