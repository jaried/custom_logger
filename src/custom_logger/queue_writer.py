# src/custom_logger/queue_writer.py
"""
队列写入器模块

支持多进程环境下的日志写入：
- Worker进程：将日志信息发送到队列
- 主程序：从队列读取日志信息并写入文件
"""
from __future__ import annotations

import os
import sys
import threading
import queue
import multiprocessing as mp
from typing import Optional, TextIO, Any, Dict
from dataclasses import dataclass
from .types import WARNING


@dataclass
class QueueLogEntry:
    """队列日志条目"""
    log_line: str
    level_value: int
    exception_info: Optional[str] = None
    worker_id: Optional[str] = None
    timestamp: Optional[str] = None


class QueueLogSender:
    """队列日志发送器（用于worker进程）"""
    
    def __init__(self, log_queue: mp.Queue, worker_id: str = None):
        self.log_queue = log_queue
        self.worker_id = worker_id or "unknown"
    
    def send_log(self, log_line: str, level_value: int, exception_info: Optional[str] = None) -> None:
        """发送日志到队列"""
        if self.log_queue is None:
            return
        
        try:
            entry = QueueLogEntry(
                log_line=log_line,
                level_value=level_value,
                exception_info=exception_info,
                worker_id=self.worker_id
            )
            self.log_queue.put_nowait(entry)
        except queue.Full:
            try:
                print(f"Worker {self.worker_id}: 日志队列已满，丢弃日志", file=sys.stderr)
            except (ValueError, AttributeError):
                pass
        except Exception as e:
            try:
                print(f"Worker {self.worker_id}: 发送日志到队列失败: {e}", file=sys.stderr)
            except (ValueError, AttributeError):
                pass


class QueueLogReceiver:
    """队列日志接收器（用于主程序）"""
    
    def __init__(self, log_queue: mp.Queue, session_dir: str):
        self.log_queue = log_queue
        self.session_dir = session_dir
        self.full_log_file: Optional[TextIO] = None
        self.warning_log_file: Optional[TextIO] = None
        self._receiver_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._init_files()
    
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
    
    def start_receiving(self) -> None:
        """开始接收队列日志"""
        if self._receiver_thread is not None:
            return
        
        self._receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._receiver_thread.start()
    
    def stop_receiving(self) -> None:
        """停止接收队列日志"""
        if self._receiver_thread is None:
            return
        
        self._stop_event.set()
        
        # 发送停止信号到队列
        try:
            self.log_queue.put_nowait("STOP_LOGGING")
        except:
            pass
        
        # 等待线程结束
        if self._receiver_thread.is_alive():
            self._receiver_thread.join(timeout=5.0)
        
        self._receiver_thread = None
        self._stop_event.clear()
    
    def _receive_loop(self) -> None:
        """接收循环"""
        try:
            while not self._stop_event.is_set():
                try:
                    # 从队列获取日志条目
                    entry = self.log_queue.get(timeout=1.0)
                    
                    # 检查停止信号
                    if entry == "STOP_LOGGING":
                        break
                    
                    # 处理日志条目
                    if isinstance(entry, QueueLogEntry):
                        self._write_log_entry(entry)
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    try:
                        print(f"处理队列日志时出错: {e}", file=sys.stderr)
                    except (ValueError, AttributeError):
                        pass
        
        finally:
            self._close_files()
    
    def _write_log_entry(self, entry: QueueLogEntry) -> None:
        """写入日志条目"""
        try:
            # 写入完整日志
            if self.full_log_file:
                self.full_log_file.write(entry.log_line + '\n')
                if entry.exception_info:
                    self.full_log_file.write(entry.exception_info + '\n')
                self.full_log_file.flush()

            # 写入警告日志（WARNING及以上级别）
            if entry.level_value >= WARNING and self.warning_log_file:
                self.warning_log_file.write(entry.log_line + '\n')
                if entry.exception_info:
                    self.warning_log_file.write(entry.exception_info + '\n')
                self.warning_log_file.flush()

        except Exception as e:
            try:
                print(f"写入日志文件失败: {e}", file=sys.stderr)
            except (ValueError, AttributeError):
                pass
    
    def _close_files(self) -> None:
        """关闭文件"""
        try:
            if self.full_log_file:
                self.full_log_file.close()
                self.full_log_file = None

            if self.warning_log_file:
                self.warning_log_file.close()
                self.warning_log_file = None

        except Exception as e:
            try:
                print(f"关闭日志文件失败: {e}", file=sys.stderr)
            except (ValueError, AttributeError):
                pass


# 全局队列日志发送器（用于worker进程）
_queue_log_sender: Optional[QueueLogSender] = None

# 全局队列日志接收器（用于主程序）
_queue_log_receiver: Optional[QueueLogReceiver] = None


def init_queue_sender(log_queue: mp.Queue, worker_id: str = None) -> None:
    """初始化队列日志发送器（worker进程调用）"""
    global _queue_log_sender
    
    if _queue_log_sender is not None:
        return
    
    _queue_log_sender = QueueLogSender(log_queue, worker_id)


def init_queue_receiver(log_queue: mp.Queue, session_dir: str) -> None:
    """初始化队列日志接收器（主程序调用）"""
    global _queue_log_receiver
    
    if _queue_log_receiver is not None:
        return
    
    _queue_log_receiver = QueueLogReceiver(log_queue, session_dir)
    _queue_log_receiver.start_receiving()


def send_log_to_queue(log_line: str, level_value: int, exception_info: Optional[str] = None) -> None:
    """发送日志到队列（worker进程调用）"""
    if _queue_log_sender is not None:
        _queue_log_sender.send_log(log_line, level_value, exception_info)


def shutdown_queue_writer() -> None:
    """关闭队列写入器"""
    global _queue_log_sender, _queue_log_receiver
    
    if _queue_log_receiver is not None:
        _queue_log_receiver.stop_receiving()
        _queue_log_receiver = None
    
    _queue_log_sender = None 