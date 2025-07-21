# src/custom_logger/writer.py
from __future__ import annotations
from datetime import datetime

start_time = datetime.now()

import os
import sys
import threading
import queue
import time
import signal
from typing import Optional, TextIO
from .config import get_config
from .types import WARNING

# 全局队列和线程
_log_queue: Optional[queue.Queue] = None
_writer_thread: Optional[threading.Thread] = None
_stop_event: Optional[threading.Event] = None

# 队列结束标记
QUEUE_SENTINEL = object()


class LogEntry:
    """日志条目"""

    def __init__(self, log_line: str, level_value: int, logger_name: str, exception_info: Optional[str] = None):
        self.log_line = log_line
        self.level_value = level_value
        self.logger_name = logger_name
        self.exception_info = exception_info
        pass


class FileWriter:
    """文件写入器"""

    def __init__(self, session_dir: str):
        self.session_dir = session_dir
        self.full_log_file: Optional[TextIO] = None
        self.warning_log_file: Optional[TextIO] = None
        self.module_files: dict[str, dict[str, TextIO]] = {}  # {logger_name: {"full": file, "warning": file}}
        self._init_files()
        pass

    def _init_files(self) -> None:
        """初始化日志文件"""
        try:
            # 规范化路径，确保使用正确的分隔符
            normalized_session_dir = os.path.normpath(self.session_dir)
            os.makedirs(normalized_session_dir, exist_ok=True)

            full_log_path = os.path.join(normalized_session_dir, "full.log")
            warning_log_path = os.path.join(normalized_session_dir, "warning.log")

            self.full_log_file = open(full_log_path, 'a', encoding='utf-8', buffering=1)
            self.warning_log_file = open(warning_log_path, 'a', encoding='utf-8', buffering=1)

        except Exception as e:
            try:
                print(f"无法创建日志文件: {e}", file=sys.stderr)
            except (ValueError, AttributeError):
                pass

        return

    def _ensure_module_files(self, logger_name: str) -> None:
        """确保指定模块的日志文件已创建"""
        if logger_name in self.module_files:
            return  # 文件已经创建
        
        try:
            # 规范化路径，确保使用正确的分隔符
            normalized_session_dir = os.path.normpath(self.session_dir)
            
            full_log_path = os.path.join(normalized_session_dir, f"{logger_name}_full.log")
            warning_log_path = os.path.join(normalized_session_dir, f"{logger_name}_warning.log")
            
            # 创建文件句柄
            full_file = open(full_log_path, 'a', encoding='utf-8', buffering=1)
            warning_file = open(warning_log_path, 'a', encoding='utf-8', buffering=1)
            
            # 存储到module_files字典
            self.module_files[logger_name] = {
                "full": full_file,
                "warning": warning_file
            }
            
        except Exception as e:
            try:
                print(f"无法创建模块日志文件 {logger_name}: {e}", file=sys.stderr)
            except (ValueError, AttributeError):
                pass
        
        return

    def write_log(self, entry: LogEntry) -> None:
        """写入日志条目"""
        try:
            # 确保模块文件存在
            self._ensure_module_files(entry.logger_name)
            
            # 1. 写入全局完整日志
            if self.full_log_file:
                self.full_log_file.write(entry.log_line + '\n')
                if entry.exception_info:
                    self.full_log_file.write(entry.exception_info + '\n')
                self.full_log_file.flush()

            # 2. 写入全局警告日志（WARNING及以上级别）
            if entry.level_value >= WARNING and self.warning_log_file:
                self.warning_log_file.write(entry.log_line + '\n')
                if entry.exception_info:
                    self.warning_log_file.write(entry.exception_info + '\n')
                self.warning_log_file.flush()
            
            # 3. 写入模块文件
            if entry.logger_name in self.module_files:
                module_file_handles = self.module_files[entry.logger_name]
                
                # 写入模块完整日志
                if "full" in module_file_handles and module_file_handles["full"]:
                    module_file_handles["full"].write(entry.log_line + '\n')
                    if entry.exception_info:
                        module_file_handles["full"].write(entry.exception_info + '\n')
                    module_file_handles["full"].flush()
                
                # 写入模块警告日志（WARNING及以上级别）
                if (entry.level_value >= WARNING and 
                    "warning" in module_file_handles and 
                    module_file_handles["warning"]):
                    module_file_handles["warning"].write(entry.log_line + '\n')
                    if entry.exception_info:
                        module_file_handles["warning"].write(entry.exception_info + '\n')
                    module_file_handles["warning"].flush()

        except Exception as e:
            try:
                print(f"写入日志文件失败: {e}", file=sys.stderr)
            except (ValueError, AttributeError):
                pass

        return

    def close(self) -> None:
        """关闭文件"""
        try:
            # 关闭全局文件
            if self.full_log_file:
                try:
                    self.full_log_file.flush()  # 确保数据写入
                    self.full_log_file.close()
                except Exception:
                    pass
                self.full_log_file = None

            if self.warning_log_file:
                try:
                    self.warning_log_file.flush()  # 确保数据写入
                    self.warning_log_file.close()
                except Exception:
                    pass
                self.warning_log_file = None
            
            # 关闭所有模块文件
            for logger_name, file_handles in self.module_files.items():
                try:
                    if "full" in file_handles and file_handles["full"]:
                        try:
                            file_handles["full"].flush()  # 确保数据写入
                            file_handles["full"].close()
                        except Exception:
                            pass
                    if "warning" in file_handles and file_handles["warning"]:
                        try:
                            file_handles["warning"].flush()  # 确保数据写入
                            file_handles["warning"].close()
                        except Exception:
                            pass
                except Exception as e:
                    try:
                        print(f"关闭模块文件失败 {logger_name}: {e}", file=sys.stderr)
                    except (ValueError, AttributeError):
                        pass
            
            # 清空模块文件字典
            self.module_files.clear()
            
            # 在Windows环境下，额外等待确保文件句柄释放
            if sys.platform.startswith('win'):
                time.sleep(0.1)

        except Exception as e:
            try:
                print(f"关闭日志文件失败: {e}", file=sys.stderr)
            except (ValueError, AttributeError):
                pass

        return


def _writer_thread_func() -> None:
    """写入线程主函数"""
    try:
        from .config import get_root_config
        cfg = get_root_config()
        
        # 优先从paths配置中获取日志目录
        session_dir = None
        
        # 尝试从paths.log_dir获取
        paths_obj = getattr(cfg, 'paths', None)
        if paths_obj is not None:
            if isinstance(paths_obj, dict):
                session_dir = paths_obj.get('log_dir', None)
            else:
                session_dir = getattr(paths_obj, 'log_dir', None)
        
        # 如果paths.log_dir不存在，尝试直接从config.log_dir获取
        if session_dir is None:
            session_dir = getattr(cfg, 'log_dir', None)

        if session_dir is None:
            print("无法获取会话目录", file=sys.stderr)
            raise Exception("无法获取会话目录")

        writer = FileWriter(session_dir)
    except Exception as e:
        try:
            print(f"初始化文件写入器失败: {e}", file=sys.stderr)
        except (ValueError, AttributeError):
            pass
        return

    try:
        while True:
            try:
                # 从队列获取日志条目
                entry = _log_queue.get(timeout=1.0)

                # 检查结束标记
                if entry is QUEUE_SENTINEL:
                    break

                # 写入日志
                writer.write_log(entry)

            except queue.Empty:
                # 检查停止事件
                if _stop_event and _stop_event.is_set():
                    break
                continue
            except Exception as e:
                print(f"写入线程异常: {e}", file=sys.stderr)

    finally:
        writer.close()

    return


def init_writer() -> None:
    """初始化异步写入器"""
    global _log_queue, _writer_thread, _stop_event

    if _log_queue is not None:
        return  # 已经初始化

    try:
        _log_queue = queue.Queue(maxsize=1_000)
        _stop_event = threading.Event()
        _writer_thread = threading.Thread(target=_writer_thread_func, daemon=True)
        _writer_thread.start()

        # 设置信号处理器增强清理机制
        _setup_signal_handlers()

    except Exception as e:
        # 避免在测试环境中输出到可能已关闭的stderr
        try:
            print(f"初始化写入器失败: {e}", file=sys.stderr)
        except (ValueError, AttributeError):
            # 如果stderr不可用，静默处理
            pass

    return


def write_log_async(log_line: str, level_value: int, logger_name: str, exception_info: Optional[str] = None) -> None:
    """异步写入日志"""
    if _log_queue is None:
        return

    try:
        entry = LogEntry(log_line, level_value, logger_name, exception_info)
        _log_queue.put_nowait(entry)

    except queue.Full:
        try:
            print("日志队列已满，丢弃日志", file=sys.stderr)
        except (ValueError, AttributeError):
            pass
    except Exception as e:
        try:
            print(f"日志写入失败: {e}", file=sys.stderr)
        except (ValueError, AttributeError):
            pass

    return


def flush_writer() -> None:
    """刷新写入器，确保所有队列中的数据都被写入文件"""
    global _log_queue, _writer_thread
    
    if _log_queue is None or _writer_thread is None:
        return
    
    try:
        # 等待队列变空
        max_wait_time = 5.0  # 最大等待5秒
        wait_interval = 0.1  # 每次等待0.1秒
        waited_time = 0.0
        
        while waited_time < max_wait_time:
            if _log_queue.empty():
                # 队列为空，再等待一小段时间确保写入线程处理完毕
                time.sleep(0.1)
                if _log_queue.empty():
                    break
            
            time.sleep(wait_interval)
            waited_time += wait_interval
        
        # 如果仍有数据，打印警告
        if not _log_queue.empty():
            try:
                print(f"警告: flush_writer超时，队列中还有 {_log_queue.qsize()} 条数据", file=sys.stderr)
            except (ValueError, AttributeError):
                pass
                
    except Exception as e:
        try:
            print(f"刷新写入器失败: {e}", file=sys.stderr)
        except (ValueError, AttributeError):
            pass
    
    return


def shutdown_writer() -> None:
    """关闭异步写入器"""
    global _log_queue, _writer_thread, _stop_event

    try:
        # 先尝试刷新所有数据
        flush_writer()
        
        if _log_queue is not None:
            _log_queue.put(QUEUE_SENTINEL)

        if _stop_event is not None:
            _stop_event.set()

        if _writer_thread is not None and _writer_thread.is_alive():
            _writer_thread.join(timeout=10.0)  # 增加超时时间
            
            # 如果线程仍在运行，给更多时间
            if _writer_thread.is_alive():
                time.sleep(1.0)
                _writer_thread.join(timeout=5.0)

    except Exception as e:
        try:
            print(f"关闭写入器失败: {e}", file=sys.stderr)
        except (ValueError, AttributeError):
            pass
    finally:
        _log_queue = None
        _writer_thread = None
        _stop_event = None
        
        # 在Windows环境下，额外等待一段时间确保文件句柄释放
        if sys.platform.startswith('win'):
            time.sleep(0.5)

    return


def _setup_signal_handlers() -> None:
    """设置信号处理器增强线程清理机制"""
    def signal_handler(signum: int, frame) -> None:
        """信号处理器：触发writer清理"""
        try:
            shutdown_writer()
        except Exception as e:
            try:
                print(f"信号处理器中清理writer失败: {e}", file=sys.stderr)
            except (ValueError, AttributeError):
                pass
        
        # 重新安装默认信号处理器并重新发送信号
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)

    try:
        # 注册SIGTERM和SIGINT信号处理器
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    except (ValueError, OSError) as e:
        # 在某些环境中信号注册可能失败，静默处理
        try:
            print(f"信号处理器注册失败: {e}", file=sys.stderr)
        except (ValueError, AttributeError):
            pass
    
    return