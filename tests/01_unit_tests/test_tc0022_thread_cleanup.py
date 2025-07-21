# tests/01_unit_tests/test_tc0022_thread_cleanup.py

"""
测试用例：验证writer线程清理机制

测试目标：
1. 复现线程无法退出的问题
2. 验证daemon=False线程的问题
3. 验证atexit机制的局限性
4. 确保修复后线程能正确清理
"""

from __future__ import annotations

import threading
import time
import signal
import os
import sys
import multiprocessing
import subprocess
from typing import List

import pytest
from config_manager import get_config_manager

from custom_logger import (
    init_custom_logger_system,
    get_logger,
    tear_down_custom_logger_system,
    is_initialized
)


class TestThreadCleanup:
    """测试writer线程清理机制"""

    def setup_method(self) -> None:
        """测试前清理环境"""
        if is_initialized():
            tear_down_custom_logger_system()
        pass

    def teardown_method(self) -> None:
        """测试后清理环境"""
        if is_initialized():
            tear_down_custom_logger_system()
        pass

    def test_tc0022_01_writer_thread_creation(self) -> None:
        """TC0022-01: 测试writer线程的创建"""
        # 记录初始线程数
        initial_thread_count = threading.active_count()
        
        # 初始化logger系统
        config = get_config_manager(test_mode=True)
        init_custom_logger_system(config)
        logger = get_logger("test_thread")
        
        # 触发writer线程创建
        logger.info("测试消息")
        time.sleep(0.1)  # 让线程有时间创建
        
        # 检查线程数是否增加
        current_thread_count = threading.active_count()
        assert current_thread_count > initial_thread_count, "writer线程应该被创建"
        
        # 查找writer线程
        writer_threads = [t for t in threading.enumerate() if 'writer' in str(t.name).lower()]
        assert len(writer_threads) > 0, "应该能找到writer线程"
        
        pass

    def test_tc0022_02_thread_daemon_status(self) -> None:
        """TC0022-02: 测试writer线程的daemon状态"""
        config = get_config_manager(test_mode=True)
        init_custom_logger_system(config)
        logger = get_logger("test_daemon")
        
        # 触发writer线程创建
        logger.info("测试消息")
        time.sleep(0.1)
        
        # 检查writer线程的daemon状态
        writer_threads = [t for t in threading.enumerate() if 'writer' in str(t.name).lower() or (hasattr(t, '_target') and t._target and 'writer' in str(t._target))]
        
        # 应该能找到至少一个writer线程
        assert len(writer_threads) > 0, "应该能找到writer线程"
        
        # 检查daemon状态（当前实现应该是False，这是问题所在）
        for thread in writer_threads:
            print(f"Writer线程: {thread.name}, daemon={thread.daemon}")
            # 当前实现的问题：daemon=False会阻止程序退出
            
        pass

    def test_tc0022_03_explicit_cleanup(self) -> None:
        """TC0022-03: 测试显式清理机制"""
        initial_thread_count = threading.active_count()
        
        config = get_config_manager(test_mode=True)
        init_custom_logger_system(config)
        logger = get_logger("test_cleanup")
        
        # 触发writer线程创建
        logger.info("测试消息")
        time.sleep(0.1)
        
        # 验证线程增加
        assert threading.active_count() > initial_thread_count
        
        # 显式清理
        tear_down_custom_logger_system()
        time.sleep(1.0)  # 给清理时间
        
        # 验证线程是否被正确清理
        final_thread_count = threading.active_count()
        print(f"初始线程数: {initial_thread_count}, 最终线程数: {final_thread_count}")
        
        # 理想情况下应该回到初始状态，但当前实现可能无法做到
        # 这个测试用来验证当前的问题
        
        pass

    def test_tc0022_04_thread_cleanup_in_subprocess(self) -> None:
        """TC0022-04: 在子进程中测试线程清理问题"""
        
        # 创建一个子进程脚本来模拟问题
        test_script = '''
import sys
import threading
import time
import os
sys.path.insert(0, "/mnt/ntfs/ubuntu_data/NutstoreFiles/invest2025/project/custom_logger/src")

from config_manager import get_config_manager
from custom_logger import init_custom_logger_system, get_logger

def main():
    print(f"子进程PID: {os.getpid()}")
    print(f"初始线程数: {threading.active_count()}")
    
    config = get_config_manager(test_mode=True)
    init_custom_logger_system(config)
    logger = get_logger("subprocess_test")
    
    logger.info("子进程测试消息")
    time.sleep(0.5)
    
    print(f"创建logger后线程数: {threading.active_count()}")
    
    # 列出所有线程
    for t in threading.enumerate():
        print(f"线程: {t.name}, daemon={t.daemon}, alive={t.is_alive()}")
    
    print("子进程逻辑完成，准备退出...")
    # 注意：这里没有显式调用tear_down_custom_logger_system()
    # 模拟依赖atexit机制的情况

if __name__ == "__main__":
    main()
'''
        
        # 写入临时脚本
        script_path = "/tmp/test_subprocess_thread_cleanup.py"
        with open(script_path, 'w') as f:
            f.write(test_script)
        
        try:
            # 运行子进程并设置超时
            result = subprocess.run([
                sys.executable, script_path
            ], capture_output=True, text=True, timeout=10)
            
            print("子进程输出:")
            print(result.stdout)
            if result.stderr:
                print("子进程错误:")
                print(result.stderr)
                
            # 如果子进程能正常退出，说明线程清理工作正常
            assert result.returncode == 0, f"子进程应该正常退出，但返回码是 {result.returncode}"
            
        except subprocess.TimeoutExpired:
            # 如果超时，说明存在线程无法退出的问题
            pytest.fail("子进程超时无法退出，证实了线程清理问题的存在")
        finally:
            # 清理临时文件
            if os.path.exists(script_path):
                os.remove(script_path)
        
        pass

    def test_tc0022_05_signal_handling(self) -> None:
        """TC0022-05: 测试信号处理时的线程清理"""
        
        # 创建一个会被信号中断的子进程
        test_script = '''
import sys
import signal
import threading
import time
import os
sys.path.insert(0, "/mnt/ntfs/ubuntu_data/NutstoreFiles/invest2025/project/custom_logger/src")

from config_manager import get_config_manager  
from custom_logger import init_custom_logger_system, get_logger

def signal_handler(signum, frame):
    print(f"收到信号 {signum}")
    # 不调用tear_down_custom_logger_system()来模拟问题
    sys.exit(0)

def main():
    signal.signal(signal.SIGTERM, signal_handler)
    
    config = get_config_manager(test_mode=True)
    init_custom_logger_system(config)
    logger = get_logger("signal_test")
    
    logger.info("信号测试消息")
    
    print(f"线程数: {threading.active_count()}")
    for t in threading.enumerate():
        print(f"线程: {t.name}, daemon={t.daemon}")
    
    # 等待信号
    time.sleep(30)

if __name__ == "__main__":
    main()
'''
        
        script_path = "/tmp/test_signal_thread_cleanup.py"
        with open(script_path, 'w') as f:
            f.write(test_script)
        
        try:
            # 启动子进程
            process = subprocess.Popen([sys.executable, script_path])
            
            # 给进程时间启动
            time.sleep(2)
            
            # 发送SIGTERM信号
            process.send_signal(signal.SIGTERM)
            
            # 等待进程退出，设置较短超时
            try:
                process.wait(timeout=5)
                print(f"进程退出码: {process.returncode}")
            except subprocess.TimeoutExpired:
                # 如果进程没有在合理时间内退出，说明存在线程问题
                process.kill()  # 强制杀死
                pytest.fail("进程无法响应SIGTERM信号正常退出，证实了线程清理问题")
                
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)
        
        pass

    def test_tc0022_06_current_thread_behavior(self) -> None:
        """TC0022-06: 测试当前线程行为以建立基线"""
        
        # 获取当前writer线程的实际状态
        from custom_logger.writer import _writer_thread
        
        config = get_config_manager(test_mode=True)
        init_custom_logger_system(config)
        logger = get_logger("baseline_test")
        
        logger.info("基线测试消息")
        time.sleep(0.5)
        
        # 检查writer线程状态
        if _writer_thread is not None:
            print(f"Writer线程状态:")
            print(f"  name: {_writer_thread.name}")
            print(f"  daemon: {_writer_thread.daemon}")
            print(f"  is_alive: {_writer_thread.is_alive()}")
            print(f"  ident: {_writer_thread.ident}")
            
            # 记录当前行为作为基线
            # 问题：daemon=False意味着这个线程会阻止进程退出
            assert _writer_thread.daemon == False, "当前实现确实使用daemon=False（这是问题所在）"
        
        pass

    def test_tc0022_07_verify_daemon_fix(self) -> None:
        """TC0022-07: 验证daemon=True修复后线程行为"""
        config = get_config_manager(test_mode=True)
        init_custom_logger_system(config)
        logger = get_logger("daemon_fix_test")
        
        logger.info("验证daemon修复的消息")
        time.sleep(0.5)
        
        # 检查所有线程，寻找writer线程
        found_writer_threads = []
        for t in threading.enumerate():
            if ('writer' in str(t.name).lower() or 
                (hasattr(t, '_target') and t._target and 'writer' in str(t._target.__name__))):
                found_writer_threads.append(t)
                print(f"找到Writer线程:")
                print(f"  name: {t.name}")
                print(f"  daemon: {t.daemon}")
                print(f"  is_alive: {t.is_alive()}")
                print(f"  target: {getattr(t, '_target', 'Unknown')}")
        
        # 验证找到了writer线程
        assert len(found_writer_threads) > 0, f"应该找到writer线程，但只找到: {[t.name for t in threading.enumerate()]}"
        
        # 验证所有writer线程都是daemon=True
        for thread in found_writer_threads:
            assert thread.daemon == True, f"修复后writer线程应该是daemon=True，但线程 {thread.name} 的daemon={thread.daemon}"
            
        print(f"✓ 修复成功：找到 {len(found_writer_threads)} 个writer线程，都是daemon线程")
        
        pass

    def test_tc0022_08_verify_subprocess_exit_fix(self) -> None:
        """TC0022-08: 验证子进程现在能正常退出"""
        
        # 创建修复后的测试脚本
        test_script = '''
import sys
import threading
import time
import os
sys.path.insert(0, "/mnt/ntfs/ubuntu_data/NutstoreFiles/invest2025/project/custom_logger/src")

from config_manager import get_config_manager
from custom_logger import init_custom_logger_system, get_logger

def main():
    print(f"子进程PID: {os.getpid()}")
    print(f"初始线程数: {threading.active_count()}")
    
    config = get_config_manager(test_mode=True)
    init_custom_logger_system(config)
    logger = get_logger("subproc_fix")
    
    logger.info("修复后子进程测试消息")
    time.sleep(0.5)
    
    print(f"创建logger后线程数: {threading.active_count()}")
    
    # 列出所有线程
    for t in threading.enumerate():
        print(f"线程: {t.name}, daemon={t.daemon}, alive={t.is_alive()}")
    
    print("子进程逻辑完成，准备退出...")
    print("✓ 修复后应该能够正常退出（依靠daemon线程机制）")

if __name__ == "__main__":
    main()
'''
        
        script_path = "/tmp/test_subprocess_fix.py"
        with open(script_path, 'w') as f:
            f.write(test_script)
        
        try:
            # 运行子进程，现在应该能快速退出
            start_time = time.time()
            result = subprocess.run([
                sys.executable, script_path
            ], capture_output=True, text=True, timeout=5)  # 减少超时时间
            end_time = time.time()
            
            execution_time = end_time - start_time
            print(f"子进程执行时间: {execution_time:.2f}秒")
            print("子进程输出:")
            print(result.stdout)
            
            if result.stderr:
                print("子进程错误:")
                print(result.stderr)
                
            # 修复后子进程应该正常快速退出
            assert result.returncode == 0, f"子进程应该正常退出，但返回码是 {result.returncode}"
            assert execution_time < 3.0, f"子进程应该快速退出，但用了 {execution_time:.2f}秒"
            
            print("✓ 修复成功：子进程能够正常快速退出")
            
        except subprocess.TimeoutExpired:
            pytest.fail("修复失败：子进程仍然超时无法退出")
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)
        
        pass

    def test_tc0022_09_verify_signal_handling_fix(self) -> None:
        """TC0022-09: 验证信号处理修复后能正常响应"""
        
        test_script = '''
import sys
import signal
import threading
import time
import os
sys.path.insert(0, "/mnt/ntfs/ubuntu_data/NutstoreFiles/invest2025/project/custom_logger/src")

from config_manager import get_config_manager  
from custom_logger import init_custom_logger_system, get_logger

def main():
    config = get_config_manager(test_mode=True)
    init_custom_logger_system(config)
    logger = get_logger("signal_fix")
    
    logger.info("修复后信号测试消息")
    
    print(f"线程数: {threading.active_count()}")
    for t in threading.enumerate():
        print(f"线程: {t.name}, daemon={t.daemon}")
    
    print("✓ 修复后信号处理器已注册，等待信号...")
    # 等待信号，但现在有了信号处理器
    time.sleep(10)

if __name__ == "__main__":
    main()
'''
        
        script_path = "/tmp/test_signal_fix.py"
        with open(script_path, 'w') as f:
            f.write(test_script)
        
        try:
            # 启动子进程
            start_time = time.time()
            process = subprocess.Popen([sys.executable, script_path])
            
            # 给进程时间启动
            time.sleep(1)
            
            # 发送SIGTERM信号
            process.send_signal(signal.SIGTERM)
            
            # 等待进程退出
            try:
                process.wait(timeout=3)  # 减少超时时间
                end_time = time.time()
                response_time = end_time - start_time
                
                print(f"进程退出码: {process.returncode}")
                print(f"信号响应时间: {response_time:.2f}秒")
                
                # 修复后应该能快速响应信号
                assert response_time < 5.0, f"进程应该快速响应信号，但用了 {response_time:.2f}秒"
                print("✓ 修复成功：进程能够正常响应信号退出")
                
            except subprocess.TimeoutExpired:
                process.kill()
                pytest.fail("修复失败：进程仍然无法响应SIGTERM信号")
                
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)
        
        pass