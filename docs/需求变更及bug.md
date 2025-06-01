需求变更：
需求变更：

1、配置文件更改为`src/config/config.yaml`，其他配置文件不再使用。

2、配置文件结构需要用到的部分改为如下：

# 默认配置

DEFAULT_CONFIG = {  
    "project_name": "my_project",  
    "experiment_name": "default",  
    "first_start_time": None,  
    "base_dir": "d:/logs",  
    'logger': {  
        "global_console_level": "info",  
        "global_file_level": "debug",  
        "current_session_dir": None,  
        "module_levels": {}, },  
}



bug1：

默认配置：init_custom_logger_system()使用 src/config/config.yaml
自定义配置：init_custom_logger_system(config_path="path/to/not_default.yaml")使用指定配置文件
Worker进程：直接调用 get_logger()，自动从环境变量继承主程序的配置路径
目前不能正确处理

bug2：
[ 21696 | _callers :  103] 2025-06-01 22:20:20 - 12420:20:20.81 - w_summary - Worker任务开始
调用者，行号识别有问题。
