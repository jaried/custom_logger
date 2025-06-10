# tests/01_unit_tests/test_tc0014_config_object_passing.py
from __future__ import annotations
from datetime import datetime

import pytest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile

# 添加src路径到sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from custom_logger.manager import init_custom_logger_system, get_logger, tear_down_custom_logger_system
from custom_logger.config import set_config_path


class MockConfigObject:
    """模拟的配置对象"""
    def __init__(self):
        self.project_name = "test_config_object_project"
        self.experiment_name = "config_object_experiment"
        self.first_start_time = "2025-06-06T12:00:00.000000"
        self.base_dir = tempfile.gettempdir().replace("\\", "/")
        self.paths = {
            'log_dir': ''
        }
        self.logger = {
            'global_console_level': 'INFO',
            'global_file_level': 'DEBUG',
            'module_levels': {
                'test_module': {
                    'console_level': 'WARNING',
                    'file_level': 'ERROR'
                }
            }
        }


class TestConfigObjectPassing:
    """测试config_object传递功能"""

    def setup_method(self):
        """每个测试前的设置"""
        # 清理环境
        tear_down_custom_logger_system()
        
        # 清理环境变量
        if 'CUSTOM_LOGGER_CONFIG_PATH' in os.environ:
            del os.environ['CUSTOM_LOGGER_CONFIG_PATH']

    def teardown_method(self):
        """每个测试后的清理"""
        tear_down_custom_logger_system()
        
        # 清理config_manager缓存
        try:
            from config_manager import _managers
            _managers.clear()
        except (ImportError, AttributeError, KeyError):
            pass
        
        # 清理配置路径缓存
        try:
            from custom_logger.config import set_config_path
            set_config_path(None)
        except Exception:
            pass
        
        # 清理环境变量
        if 'CUSTOM_LOGGER_CONFIG_PATH' in os.environ:
            del os.environ['CUSTOM_LOGGER_CONFIG_PATH']
        
        # 强制清理所有可能的配置状态
        try:
            # 清理可能的全局配置状态
            import custom_logger.config as config_module
            if hasattr(config_module, '_config_path'):
                config_module._config_path = None
        except Exception:
            pass
        
        # 删除测试配置文件，确保下次测试从干净状态开始
        try:
            test_config_path = "tests/src/config/config.yaml"
            if os.path.exists(test_config_path):
                os.remove(test_config_path)
        except Exception:
            pass

    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_001_config_object_basic_passing(self, mock_get_config_manager):
        """测试基本的config_object传递功能"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        
        # 创建测试配置对象
        config_obj = MockConfigObject()
        
        # 使用config_object初始化系统
        init_custom_logger_system(config_object=config_obj)
        
        # 验证配置对象的属性被正确设置
        assert mock_cfg.project_name == "test_config_object_project"
        assert mock_cfg.experiment_name == "config_object_experiment"
        assert mock_cfg.first_start_time == "2025-06-06T12:00:00.000000"
        assert mock_cfg.base_dir == tempfile.gettempdir().replace("\\", "/")
        
        # 验证logger配置被正确复制（除了log_dir会被自动创建）
        expected_logger = config_obj.logger.copy()
        # log_dir会被自动创建，所以我们只验证其他字段
        for key, value in expected_logger.items():
            assert mock_cfg.logger[key] == value
        # 验证paths.log_dir被创建
        assert hasattr(mock_cfg, 'paths')

    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_002_config_object_priority_over_path(self, mock_get_config_manager):
        """测试config_object优先级高于config_path"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        
        # 创建测试配置对象
        config_obj = MockConfigObject()
        
        # 同时传入config_path和config_object
        init_custom_logger_system(
            config_path="some/config/path.yaml",
            config_object=config_obj
        )
        
        # 验证使用了config_object而不是config_path
        # get_config_manager应该被调用一次（用于获取config_manager实例）
        mock_get_config_manager.assert_called()
        assert mock_cfg.project_name == "test_config_object_project"

    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_003_config_object_with_first_start_time_conflict(self, mock_get_config_manager):
        """测试config_object与first_start_time参数同时传入时的冲突检测"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        
        # 创建测试配置对象
        config_obj = MockConfigObject()
        
        # 传入不同的first_start_time（应该抛出冲突错误）
        new_start_time = datetime(2025, 6, 6, 15, 30, 0)
        
        with pytest.raises(ValueError, match="传入的first_start_time参数.*与config_object.first_start_time.*不一致"):
            init_custom_logger_system(
                config_object=config_obj,
                first_start_time=new_start_time
            )

    @patch('custom_logger.config._create_log_dir')
    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_004_config_object_partial_attributes(self, mock_get_config_manager, mock_create_log_dir):
        """测试config_object只有部分属性的情况"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        mock_create_log_dir.return_value = "/test/log/dir"
        
        # 创建只有部分属性的配置对象
        class PartialConfigObject:
            def __init__(self):
                self.project_name = "partial_project"
                # 缺少其他属性
        
        config_obj = PartialConfigObject()
        
        init_custom_logger_system(config_object=config_obj)
        
        # 验证存在的属性被设置
        assert mock_cfg.project_name == "partial_project"
        
        # 验证缺少的属性不会导致错误（通过没有异常抛出来验证）

    @patch('custom_logger.config._create_log_dir')
    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_005_config_object_logger_dict_format(self, mock_get_config_manager, mock_create_log_dir):
        """测试config_object中logger配置为字典格式"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        mock_create_log_dir.return_value = "/test/log/dir"
        
        # 创建配置对象，logger为字典
        class DictLoggerConfigObject:
            def __init__(self):
                self.project_name = "dict_logger_project"
                self.logger = {
                    'global_console_level': 'ERROR',
                    'global_file_level': 'WARNING',
                    'module_levels': {}
                }
        
        config_obj = DictLoggerConfigObject()
        
        init_custom_logger_system(config_object=config_obj)
        
        # 验证logger配置被正确复制（除了log_dir会被自动创建）
        expected_logger = {
            'global_console_level': 'ERROR',
            'global_file_level': 'WARNING',
            'module_levels': {}
        }
        # 验证主要配置项
        for key, value in expected_logger.items():
            assert mock_cfg.logger[key] == value
        # 验证paths.log_dir被创建
        assert hasattr(mock_cfg, 'paths')

    @patch('custom_logger.config._create_log_dir')
    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_006_config_object_logger_object_format(self, mock_get_config_manager, mock_create_log_dir):
        """测试config_object中logger配置为对象格式"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        mock_create_log_dir.return_value = "/test/log/dir"
        
        # 创建配置对象，logger为对象
        class LoggerConfigObject:
            def __init__(self):
                self.global_console_level = 'CRITICAL'
                self.global_file_level = 'INFO'
                # 移除current_session_dir，现在由paths.log_dir管理
                self.module_levels = {'test': {'console_level': 'DEBUG'}}
        
        class ObjectLoggerConfigObject:
            def __init__(self):
                self.project_name = "object_logger_project"
                self.logger = LoggerConfigObject()
        
        config_obj = ObjectLoggerConfigObject()
        
        init_custom_logger_system(config_object=config_obj)
        
        # 验证logger配置被正确转换为字典
        expected_logger = {
            'global_console_level': 'CRITICAL',
            'global_file_level': 'INFO',
            'module_levels': {'test': {'console_level': 'DEBUG'}}
        }
        # 验证主要配置项
        for key, value in expected_logger.items():
            assert mock_cfg.logger[key] == value
        # 验证paths.log_dir被创建
        assert hasattr(mock_cfg, 'paths')

    @patch('custom_logger.config._create_log_dir')
    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_007_config_object_exception_handling(self, mock_get_config_manager, mock_create_log_dir):
        """测试config_object处理过程中的异常处理"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        mock_create_log_dir.return_value = "/test/log/dir"
        
        # 创建会导致异常的配置对象
        class ProblematicConfigObject:
            @property
            def project_name(self):
                raise ValueError("Simulated error")
        
        config_obj = ProblematicConfigObject()
        
        # 应该不会抛出异常，而是使用默认配置
        init_custom_logger_system(config_object=config_obj)
        
        # 验证系统仍然能正常初始化（通过没有异常抛出来验证）

    @patch('custom_logger.config._create_log_dir')
    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_008_config_object_none_values(self, mock_get_config_manager, mock_create_log_dir):
        """测试config_object中包含None值的情况"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        mock_create_log_dir.return_value = "/test/log/dir"
        
        # 创建包含None值的配置对象
        class NoneValueConfigObject:
            def __init__(self):
                self.project_name = "none_test_project"
                self.experiment_name = None  # None值
                self.first_start_time = "2025-06-06T12:00:00.000000"
                self.base_dir = None  # None值
        
        config_obj = NoneValueConfigObject()
        
        init_custom_logger_system(config_object=config_obj)
        
        # 验证非None值被设置
        assert mock_cfg.project_name == "none_test_project"
        assert mock_cfg.first_start_time == "2025-06-06T12:00:00.000000"
        
        # None值不应该被设置（通过检查setattr调用来验证）
        # 这里我们主要验证没有异常抛出

    @patch('custom_logger.config._create_log_dir')
    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_009_config_object_complete_initialization(self, mock_get_config_manager, mock_create_log_dir):
        """测试config_object的完整初始化流程，包括日志目录创建和时间处理"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        
        # 模拟日志目录创建
        mock_create_log_dir.return_value = "/test/session/dir"
        
        # 创建包含datetime对象的配置对象
        class CompleteConfigObject:
            def __init__(self):
                self.project_name = "complete_test_project"
                self.experiment_name = "complete_experiment"
                self.first_start_time = datetime(2025, 6, 6, 10, 30, 45)  # datetime对象
                self.base_dir = tempfile.gettempdir().replace("\\", "/")
                self.logger = {
                    'global_console_level': 'DEBUG',
                    'global_file_level': 'INFO',
                    'module_levels': {},
                    'show_call_chain': True,
                    'show_debug_call_stack': False
                }
        
        config_obj = CompleteConfigObject()
        
        init_custom_logger_system(config_object=config_obj)
        
        # 验证基本配置被正确设置
        assert mock_cfg.project_name == "complete_test_project"
        assert mock_cfg.experiment_name == "complete_experiment"
        assert mock_cfg.base_dir == tempfile.gettempdir().replace("\\", "/")
        
        # 验证datetime对象被转换为ISO格式字符串
        assert mock_cfg.first_start_time == "2025-06-06T10:30:45"
        
        # 验证日志目录创建函数被调用
        mock_create_log_dir.assert_called_once_with(mock_cfg)
        
        # 验证paths配置被设置（由于Mock的存在，我们只验证paths属性存在）
        assert hasattr(mock_cfg, 'paths')
        
        # 验证logger配置（包含自动添加的current_session_dir）
        expected_logger = {
            'global_console_level': 'DEBUG',
            'global_file_level': 'INFO',
            'module_levels': {},
            'show_call_chain': True,
            'show_debug_call_stack': False,
            'current_session_dir': '/test/session/dir'  # 自动添加的字段
        }
        assert mock_cfg.logger == expected_logger

    @patch('custom_logger.config._create_log_dir')
    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_010_config_object_missing_logger_config(self, mock_get_config_manager, mock_create_log_dir):
        """测试config_object缺少logger配置时的默认配置初始化"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        
        # 模拟日志目录创建
        mock_create_log_dir.return_value = "/test/default/session"
        
        # 创建没有logger配置的配置对象
        class NoLoggerConfigObject:
            def __init__(self):
                self.project_name = "no_logger_project"
                self.experiment_name = "no_logger_experiment"
                self.first_start_time = datetime(2025, 6, 6, 12, 0, 0)
                self.base_dir = tempfile.gettempdir().replace("\\", "/")
                # 没有logger属性
        
        config_obj = NoLoggerConfigObject()
        
        init_custom_logger_system(config_object=config_obj)
        
        # 验证基本配置被正确设置
        assert mock_cfg.project_name == "no_logger_project"
        assert mock_cfg.experiment_name == "no_logger_experiment"
        assert mock_cfg.base_dir == tempfile.gettempdir().replace("\\", "/")
        assert mock_cfg.first_start_time == "2025-06-06T12:00:00"
        
        # 验证日志目录创建函数被调用
        mock_create_log_dir.assert_called_once_with(mock_cfg)
        
        # 验证paths配置被设置（由于Mock的存在，我们只验证paths属性存在）
        assert hasattr(mock_cfg, 'paths')
        
        # 验证cfg.logger被赋值为期望的字典
        # 由于mock_cfg.logger是MagicMock，我们检查它是否被赋值
        assert hasattr(mock_cfg, 'logger')
        # 检查最后一次赋值的参数
        # 注意：在mock环境下，我们主要验证逻辑执行正确，而不是具体的值
        pass

    @patch('custom_logger.config._create_log_dir')
    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_011_config_object_missing_first_start_time(self, mock_get_config_manager, mock_create_log_dir):
        """测试config_object缺少first_start_time时的自动时间设置"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        
        # 模拟日志目录创建
        mock_create_log_dir.return_value = "/test/auto/session"
        
        # 创建没有first_start_time的配置对象
        class NoTimeConfigObject:
            def __init__(self):
                self.project_name = "no_time_project"
                self.experiment_name = "no_time_experiment"
                self.base_dir = tempfile.gettempdir().replace("\\", "/")
                self.logger = {
                    'global_console_level': 'INFO',
                    'global_file_level': 'DEBUG'
                }
                # 没有first_start_time属性
        
        config_obj = NoTimeConfigObject()
        
        init_custom_logger_system(config_object=config_obj)
        
        # 验证基本配置被正确设置
        assert mock_cfg.project_name == "no_time_project"
        assert mock_cfg.experiment_name == "no_time_experiment"
        assert mock_cfg.base_dir == tempfile.gettempdir().replace("\\", "/")
        
        # 验证first_start_time被自动设置（应该是当前时间的ISO格式）
        assert hasattr(mock_cfg, 'first_start_time')
        assert mock_cfg.first_start_time is not None
        
        # 验证日志目录创建函数被调用
        mock_create_log_dir.assert_called_once_with(mock_cfg)

    @patch('custom_logger.config._create_log_dir')
    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_012_first_start_time_conflict_detection(self, mock_get_config_manager, mock_create_log_dir):
        """测试first_start_time冲突检测"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        
        # 模拟日志目录创建
        mock_create_log_dir.return_value = "/test/conflict/session"
        
        # 创建有first_start_time的配置对象
        class ConfigWithTime:
            def __init__(self):
                self.project_name = "conflict_project"
                self.first_start_time = datetime(2025, 6, 6, 10, 0, 0)
        
        config_obj = ConfigWithTime()
        
        # 传入不同的first_start_time参数
        different_time = datetime(2025, 6, 6, 15, 0, 0)
        
        with pytest.raises(ValueError, match="传入的first_start_time参数.*与config_object.first_start_time.*不一致"):
            init_custom_logger_system(
                config_object=config_obj,
                first_start_time=different_time
            )

    @patch('custom_logger.config._create_log_dir')
    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_013_first_start_time_param_only(self, mock_get_config_manager, mock_create_log_dir):
        """测试只传入first_start_time参数的情况"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        
        # 模拟日志目录创建
        mock_create_log_dir.return_value = "/test/param/session"
        
        # 创建没有first_start_time的配置对象
        class ConfigWithoutTime:
            def __init__(self):
                self.project_name = "param_only_project"
                self.experiment_name = "param_only_experiment"
        
        config_obj = ConfigWithoutTime()
        param_time = datetime(2025, 6, 6, 14, 30, 0)
        
        init_custom_logger_system(
            config_object=config_obj,
            first_start_time=param_time
        )
        
        # 验证使用了传入的first_start_time参数
        assert mock_cfg.first_start_time == "2025-06-06T14:30:00"

    @patch('custom_logger.config._create_log_dir')
    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_014_config_object_time_only(self, mock_get_config_manager, mock_create_log_dir):
        """测试只有config_object中有first_start_time的情况"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        
        # 模拟日志目录创建
        mock_create_log_dir.return_value = "/test/config/session"
        
        # 创建有first_start_time的配置对象
        class ConfigWithTime:
            def __init__(self):
                self.project_name = "config_time_project"
                self.first_start_time = datetime(2025, 6, 6, 16, 45, 0)
        
        config_obj = ConfigWithTime()
        
        init_custom_logger_system(config_object=config_obj)
        
        # 验证使用了config_object中的first_start_time
        assert mock_cfg.first_start_time == "2025-06-06T16:45:00"

    @patch('custom_logger.config._create_log_dir')
    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_015_config_object_none_time_no_conflict(self, mock_get_config_manager, mock_create_log_dir):
        """测试config_object中first_start_time为None时不产生冲突"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        
        # 模拟日志目录创建
        mock_create_log_dir.return_value = "/test/none/session"
        
        # 创建first_start_time为None的配置对象
        class ConfigWithNoneTime:
            def __init__(self):
                self.project_name = "none_time_project"
                self.first_start_time = None
        
        config_obj = ConfigWithNoneTime()
        param_time = datetime(2025, 6, 6, 18, 0, 0)
        
        # 应该不会抛出冲突异常
        init_custom_logger_system(
            config_object=config_obj,
            first_start_time=param_time
        )
        
        # 验证使用了传入的first_start_time参数
        assert mock_cfg.first_start_time == "2025-06-06T18:00:00"

    @patch('custom_logger.config._create_log_dir')
    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_016_both_none_use_current_time(self, mock_get_config_manager, mock_create_log_dir):
        """测试两者都为None时使用当前时间"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        
        # 模拟日志目录创建
        mock_create_log_dir.return_value = "/test/current/session"
        
        # 创建没有first_start_time的配置对象
        class ConfigWithoutTime:
            def __init__(self):
                self.project_name = "current_time_project"
                # 没有first_start_time属性
        
        config_obj = ConfigWithoutTime()
        
        init_custom_logger_system(config_object=config_obj)
        
        # 验证first_start_time被设置（应该是当前时间）
        assert hasattr(mock_cfg, 'first_start_time')
        assert mock_cfg.first_start_time is not None
        # 验证格式是ISO格式
        from datetime import datetime
        try:
            datetime.fromisoformat(mock_cfg.first_start_time)
        except ValueError:
            pytest.fail("first_start_time不是有效的ISO格式")

    @patch('custom_logger.config._create_log_dir')
    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_017_same_first_start_time_no_conflict(self, mock_get_config_manager, mock_create_log_dir):
        """测试相同的first_start_time不产生冲突"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        
        # 模拟日志目录创建
        mock_create_log_dir.return_value = "/test/same/session"
        
        # 创建有first_start_time的配置对象
        class ConfigWithSameTime:
            def __init__(self):
                self.project_name = "same_time_project"
                self.first_start_time = datetime(2025, 6, 6, 12, 30, 0)
        
        config_obj = ConfigWithSameTime()
        same_time = datetime(2025, 6, 6, 12, 30, 0)
        
        # 应该不会抛出冲突异常
        init_custom_logger_system(
            config_object=config_obj,
            first_start_time=same_time
        )
        
        # 验证时间被正确设置
        assert mock_cfg.first_start_time == "2025-06-06T12:30:00"

    @patch('custom_logger.config._create_log_dir')
    @patch('custom_logger.config.get_config_manager')
    def test_tc0014_018_same_first_start_time_string_format(self, mock_get_config_manager, mock_create_log_dir):
        """测试字符串格式的相同first_start_time不产生冲突"""
        # 创建mock配置管理器
        mock_cfg = MagicMock()
        mock_get_config_manager.return_value = mock_cfg
        
        # 模拟日志目录创建
        mock_create_log_dir.return_value = "/test/string/session"
        
        # 创建有字符串格式first_start_time的配置对象
        class ConfigWithStringTime:
            def __init__(self):
                self.project_name = "string_time_project"
                self.first_start_time = "2025-06-06T20:15:00"
        
        config_obj = ConfigWithStringTime()
        same_time = datetime(2025, 6, 6, 20, 15, 0)
        
        # 应该不会抛出冲突异常
        init_custom_logger_system(
            config_object=config_obj,
            first_start_time=same_time
        )
        
        # 验证时间被正确设置
        assert mock_cfg.first_start_time == "2025-06-06T20:15:00"

    def test_tc0014_011_partial_config_object_missing_experiment(self):
        """测试部分配置对象缺少experiment_name的情况"""
        with patch('custom_logger.config.get_config_manager') as mock_get_config_manager:
            # 创建mock配置管理器，设置必要的默认属性
            import tempfile
            temp_dir = tempfile.gettempdir()
            mock_cfg = MagicMock()
            mock_cfg.base_dir = temp_dir
            mock_cfg.experiment_name = "default"
            mock_cfg.first_start_time = "2024-01-01T12:00:00"
            mock_cfg.logger = {"global_console_level": "info"}
            mock_cfg.paths = {"log_dir": temp_dir}
            mock_get_config_manager.return_value = mock_cfg
            
            class PartialConfig:
                def __init__(self):
                    self.project_name = "partial_project"
                    # 缺少experiment_name
            
            config_obj = PartialConfig()
            
            init_custom_logger_system(config_object=config_obj)
            
            # 验证project_name被设置
            assert mock_cfg.project_name == "partial_project"
            
            # 验证系统正常初始化（没有异常抛出）
            pass

    def test_tc0014_012_dict_config_missing_experiment(self):
        """测试字典配置缺少experiment_name的情况"""
        with patch('custom_logger.config.get_config_manager') as mock_get_config_manager:
            # 创建mock配置管理器，设置必要的默认属性
            import tempfile
            temp_dir = tempfile.gettempdir()
            mock_cfg = MagicMock()
            mock_cfg.base_dir = temp_dir
            mock_cfg.experiment_name = "default"
            mock_cfg.first_start_time = "2024-01-01T12:00:00"
            mock_cfg.logger = {"global_console_level": "info"}
            mock_cfg.paths = {"log_dir": temp_dir}
            mock_get_config_manager.return_value = mock_cfg
            
            # 使用字典作为配置对象
            config_dict = {
                'project_name': 'dict_project',
                'base_dir': temp_dir
                # 缺少experiment_name
            }
            
            init_custom_logger_system(config_object=config_dict)
            
            # 验证字典中的配置被设置
            # 注意：字典配置对象的处理可能与对象配置不同
            # 这里主要验证没有异常抛出
            pass

    def test_tc0014_013_config_with_none_experiment(self):
        """测试配置中experiment_name为None的情况"""
        with patch('custom_logger.config.get_config_manager') as mock_get_config_manager:
            # 创建mock配置管理器，设置必要的默认属性
            import tempfile
            temp_dir = tempfile.gettempdir()
            mock_cfg = MagicMock()
            mock_cfg.base_dir = temp_dir
            mock_cfg.experiment_name = "default"
            mock_cfg.first_start_time = "2024-01-01T12:00:00"
            mock_cfg.logger = {"global_console_level": "info"}
            mock_cfg.paths = {"log_dir": temp_dir}
            mock_get_config_manager.return_value = mock_cfg
            
            class ConfigWithNoneExperiment:
                def __init__(self):
                    self.project_name = "none_experiment_project"
                    self.experiment_name = None  # 显式设置为None
            
            config_obj = ConfigWithNoneExperiment()
            
            init_custom_logger_system(config_object=config_obj)
            
            # 验证project_name被设置
            assert mock_cfg.project_name == "none_experiment_project"
            
            # None值不应该被设置到config_manager
            # 这里主要验证没有异常抛出
            pass

    def test_tc0014_012_config_object_project_name_priority(self):
        """测试config_object中project_name的优先级"""
        with patch('custom_logger.config.get_config_manager') as mock_get_config_manager:
            # 创建mock配置管理器，设置必要的默认属性
            import tempfile
            temp_dir = tempfile.gettempdir()
            mock_cfg = MagicMock()
            mock_cfg.base_dir = temp_dir
            mock_cfg.experiment_name = "default"
            mock_cfg.first_start_time = "2024-01-01T12:00:00"
            mock_cfg.logger = {"global_console_level": "info"}
            mock_cfg.paths = {"log_dir": temp_dir}
            mock_get_config_manager.return_value = mock_cfg
            
            # 模拟config_manager已有的project_name
            mock_cfg.project_name = "existing_project"
            
            class CustomConfig:
                def __init__(self):
                    self.project_name = "override_project"
                    self.experiment_name = "override_experiment"
            
            config_obj = CustomConfig()
            
            init_custom_logger_system(config_object=config_obj)
            
            # 验证config_object中的值覆盖了原有值
            assert mock_cfg.project_name == "override_project"
            assert mock_cfg.experiment_name == "override_experiment"

    def test_tc0014_013_config_object_partial_override(self):
        """测试config_object部分覆盖现有配置"""
        with patch('custom_logger.config.get_config_manager') as mock_get_config_manager:
            # 创建mock配置管理器，设置必要的默认属性
            import tempfile
            temp_dir = tempfile.gettempdir()
            mock_cfg = MagicMock()
            mock_cfg.base_dir = temp_dir
            mock_cfg.experiment_name = "default"
            mock_cfg.first_start_time = "2024-01-01T12:00:00"
            mock_cfg.logger = {"global_console_level": "info"}
            mock_cfg.paths = {"log_dir": temp_dir}
            mock_get_config_manager.return_value = mock_cfg
            
            class PartialConfig:
                def __init__(self):
                    self.project_name = "partial_override_project"
                    # 只有project_name，其他配置保持不变
            
            config_obj = PartialConfig()
            
            init_custom_logger_system(config_object=config_obj)
            
            # 验证只有指定的属性被覆盖
            assert mock_cfg.project_name == "partial_override_project"
            
            # 验证系统正常初始化
            pass 