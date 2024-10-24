import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool
from config import DB_NAME, DB_USER, DB_HOSTNAME, DB_PASSWORD, DB_PORT

from alembic import context

from src.auth.models import metadata
from src.database import Base
target_metadata = metadata
# Alembic Config object
config = context.config
section = config.config_ini_section

config.set_section_option(section, "DB_HOSTNAME", DB_HOSTNAME)
config.set_section_option(section, "DB_NAME", DB_NAME )
config.set_section_option(section, "DB_USER", DB_USER )
config.set_section_option(section, "DB_PASSWORD", DB_PASSWORD )
config.set_section_option(section, "DB_PORT", DB_PORT)
# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object

from src.database import SQLALCHEMY_DATABASE_URL

config.set_main_option('sqlalchemy.url', SQLALCHEMY_DATABASE_URL)


async def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def do_run_migrations(connection):
    # Используем run_sync для выполнения инспекции
    await connection.run_sync(do_migrations)


def do_migrations(connection):
    # Конфигурация для миграций
    context.configure(connection=connection, target_metadata=Base.metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable: AsyncEngine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        poolclass=NullPool
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_migrations)  # Используем run_sync


if context.is_offline_mode():
    asyncio.run(run_migrations_offline())
else:
    asyncio.run(run_migrations_online())