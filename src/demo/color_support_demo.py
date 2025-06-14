"""
演示custom_logger在不同环境下的颜色支持

这个演示展示了：
1. 在CMD环境下的颜色支持
2. 在PyCharm环境下的颜色支持
3. 在其他IDE环境下的颜色支持
4. 颜色支持的自动检测和配置
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from custom_logger import (
    init_custom_logger_system,
    get_logger,
    tear_down_custom_logger_system
)


def demonstrate_color_support():
    """演示颜色支持功能"""
    print("="*60)
    print("演示custom_logger颜色支持功能")
    print("="*60)
    
    # 显示环境信息
    print(f"操作系统: {os.name}")
    print(f"终端类型检测: {_detect_terminal_type()}")
    print(f"颜色支持状态: {_get_color_support_status()}")
    print(f"环境变量:")
    for key in ['PYCHARM_HOSTED', 'PYCHARM_MATPLOTLIB_BACKEND', 'VSCODE_PID', 'TERM_PROGRAM', 'TERM']:
        value = os.environ.get(key, '未设置')
        print(f"  {key}: {value}")
    print()
    
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp:
        config_path = tmp.name
        tmp.write("""project_name: "颜色支持演示"
experiment_name: "color_demo"
base_dir: "temp/logs"
logger:
  global_console_level: "debug"
  global_file_level: "debug"
""")
    
    try:
        print(f"配置文件路径: {config_path}")
        
        # 初始化日志系统
        print("初始化日志系统...")
        init_custom_logger_system(config_path=config_path)
        
        # 获取logger
        logger = get_logger("color")
        
        print("\n开始测试各级别日志的颜色显示:")
        print("-" * 40)
        
        # 测试各个级别的日志
        logger.debug("这是DEBUG级别的日志 - 通常不显示颜色")
        logger.info("这是INFO级别的日志 - 通常不显示颜色")
        logger.warning("这是WARNING级别的日志 - 应该显示黄色")
        logger.error("这是ERROR级别的日志 - 应该显示红色")
        logger.critical("这是CRITICAL级别的日志 - 应该显示洋红色")
        
        # 测试异常日志
        try:
            raise ValueError("这是一个测试异常")
        except Exception:
            logger.exception("这是EXCEPTION级别的日志 - 应该显示亮红色，并包含异常堆栈")
        
        print("-" * 40)
        print("颜色测试完成")
        
        # 清理
        tear_down_custom_logger_system()
        
    finally:
        # 清理临时文件
        try:
            os.unlink(config_path)
        except:
            pass


def _detect_terminal_type() -> str:
    """检测终端类型（复制自logger.py用于演示）"""
    # 检测PyCharm
    if 'PYCHARM_HOSTED' in os.environ or 'PYCHARM_MATPLOTLIB_BACKEND' in os.environ:
        return 'pycharm'

    # 检测VS Code
    if 'VSCODE_PID' in os.environ or 'TERM_PROGRAM' in os.environ and os.environ['TERM_PROGRAM'] == 'vscode':
        return 'vscode'

    # 检测其他IDE
    if any(ide in os.environ.get('PATH', '').lower() for ide in ['pycharm', 'vscode', 'code']):
        return 'ide'

    # Windows CMD
    if os.name == 'nt' and os.environ.get('TERM') != 'xterm':
        return 'cmd'

    # Unix终端
    return 'terminal'


def _get_color_support_status() -> str:
    """获取颜色支持状态"""
    terminal_type = _detect_terminal_type()
    
    if terminal_type == 'cmd':
        # 对于CMD，需要检查ANSI支持
        if os.name == 'nt':
            try:
                # 检查注册表
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Console")
                value, _ = winreg.QueryValueEx(key, "VirtualTerminalLevel")
                winreg.CloseKey(key)
                if value == 1:
                    return "支持（注册表已配置）"
                else:
                    return "不支持（注册表未配置）"
            except Exception:
                return "不支持（无法检查注册表）"
        else:
            return "支持（非Windows系统）"
    elif terminal_type == 'pycharm':
        return "支持（PyCharm环境）"
    elif terminal_type == 'vscode':
        return "支持（VS Code环境）"
    else:
        return "支持（标准终端）"


def demonstrate_manual_color_test():
    """手动颜色测试（不依赖logger系统）"""
    print("\n" + "="*60)
    print("手动ANSI颜色代码测试")
    print("="*60)
    
    # ANSI颜色代码
    colors = {
        'RED': '\033[31m',
        'YELLOW': '\033[33m',
        'GREEN': '\033[32m',
        'BLUE': '\033[34m',
        'MAGENTA': '\033[35m',
        'CYAN': '\033[36m',
        'WHITE': '\033[37m',
        'BRIGHT_RED': '\033[91m',
        'PYCHARM_YELLOW': '\033[93m',
        'PYCHARM_RED': '\033[91m',
        'PYCHARM_MAGENTA': '\033[95m',
        'PYCHARM_BRIGHT_RED': '\033[1;31m',
        'RESET': '\033[0m'
    }
    
    print("如果您看到以下文本显示为不同颜色，说明您的终端支持ANSI颜色：")
    print()
    
    for color_name, color_code in colors.items():
        if color_name != 'RESET':
            colored_text = f"{color_code}这是{color_name}颜色的文本{colors['RESET']}"
            print(f"{color_name:20}: {colored_text}")
    
    print()
    print("如果上述文本都显示为相同颜色（通常是白色或黑色），说明您的终端不支持ANSI颜色。")


def main():
    """主函数"""
    print("Custom Logger 颜色支持演示程序")
    print("=" * 60)
    
    # 演示颜色支持
    demonstrate_color_support()
    
    # 手动颜色测试
    demonstrate_manual_color_test()
    
    print("\n演示完成！")
    print("\n使用说明：")
    print("1. 在CMD中运行：如果看不到颜色，请按提示配置注册表")
    print("2. 在PyCharm中运行：应该能看到适合PyCharm的颜色方案")
    print("3. 在VS Code中运行：应该能看到标准的ANSI颜色")
    print("4. 在其他终端中运行：通常都支持ANSI颜色")


if __name__ == "__main__":
    main() 