from loguru import logger
from pathlib import Path
from utils.config_manager import ConfigManager


class LogManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not LogManager._initialized:
            self._setup_logger()
            LogManager._initialized = True

    def _setup_logger(self):
        """初始化日志配置"""
        try:
            # 加载配置文件
            config = ConfigManager.load_config()
            logger_config = config.get('logger', {})

            # 获取日志配置参数
            log_path = Path(logger_config.get('file_path', 'logs/cluster_agent.log'))
            log_level = logger_config.get('level', 'INFO')
            log_format = logger_config.get('format', '{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}')
            log_rotation = logger_config.get('rotation', '1 day')
            log_retention = logger_config.get('retention', '7 days')

            # 确保日志目录存在
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # 移除默认的日志处理器
            logger.remove()

            # 添加新的日志处理器
            logger.add(
                log_path,
                level=log_level,
                format=log_format,
                rotation=log_rotation,
                retention=log_retention
            )

            logger.info("Logger initialized successfully")
        except Exception as e:
            # 如果配置失败，使用默认配置
            logger.error(f"Failed to initialize logger from config: {e}")
            logger.add("logs/cluster_agent.log", level="INFO")

    @staticmethod
    def get_logger():
        """获取配置好的logger实例"""
        if not LogManager._initialized:
            LogManager()
        return logger