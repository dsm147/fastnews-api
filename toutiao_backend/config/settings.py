from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，从环境变量或 .env 文件加载"""

    # 数据库
    database_url: str = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # 应用
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"

    # Token 过期时间（天）
    token_expire_days: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# 创建全局配置实例
settings = Settings()
