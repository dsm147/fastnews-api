import sys
from loguru import logger
from config.settings import settings


def setup_logging():
    """配置日志系统"""

    # 移除默认的 handler
    logger.remove()

    # 控制台输出（开发模式）
    if settings.debug:
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            level="DEBUG",
            colorize=True
        )
    else:
        # 生产模式：精简格式
        logger.add(
            sys.stdout,
            format="{time} | {level} | {message}",
            level="INFO"
        )

    # 文件输出（所有环境）
    logger.add(
        "logs/app_{time:YYYY-MM-D}.log",
        format="{time} | {level} | {name}:{function}:{line} | {message}",
        level="DEBUG" if settings.debug else "INFO",
        rotation="500 MB",
        retention="10 days",
        compression="zip",
        enqueue=True
    )

    # 错误日志单独存
    logger.add(
        "logs/error_{time:YYYY-MM-D}.log",
        level="ERROR",
        rotation="100 MB",
        retention="30 days",
        compression="zip"
    )
