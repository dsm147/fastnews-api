import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config, MetaData
from sqlalchemy import pool

from alembic import context

# 将项目根目录添加到 Python 路径
sys.path.append(str(Path(__file__).resolve().parents[1]))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 导入所有模型以确保表被注册
from models.news import Base as NewsBase, Category, News
from models.users import Base as UsersBase, User, UserToken
from models.favorite import Base as FavoriteBase, Favorite
from models.history import Base as HistoryBase, History

# 合并所有 Base 的 metadata 到一个统一的 metadata
combined_metadata = MetaData()
for base in [NewsBase, UsersBase, FavoriteBase, HistoryBase]:
    for table_name, table in base.metadata.tables.items():
        table.to_metadata(combined_metadata)

target_metadata = combined_metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
