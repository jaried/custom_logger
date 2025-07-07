from custom_logger import init_custom_logger_system, get_logger, tear_down_custom_logger_system
from unittest.mock import Mock
from datetime import datetime
import os, tempfile


def main():
    temp_dir = tempfile.mkdtemp()
    log_dir = os.path.join(temp_dir, 'logs')
    cfg = Mock()
    cfg.first_start_time = datetime.now()
    cfg.paths = Mock()
    cfg.paths.log_dir = log_dir
    cfg.logger = Mock()
    cfg.logger.global_console_level = 'debug'
    cfg.logger.global_file_level = 'debug'
    cfg.logger.module_levels = {}
    cfg.logger.enable_queue_mode = False
    cfg.queue_info = None
    init_custom_logger_system(cfg)
    logger = get_logger('longname12345678')
    logger.info('test message')
    tear_down_custom_logger_system()

if __name__ == '__main__':
    main() 