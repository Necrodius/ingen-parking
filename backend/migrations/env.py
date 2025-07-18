# This file is part of the Alembic migration environment.
# It configures the Alembic context and runs migrations against the database.
# It loads the database URL from environment variables and sets up the SQLAlchemy engine.
# It also imports the application's models to ensure they are included in the migration context.
# It is typically used to manage database schema changes in a Flask application.

import os, sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db
import models

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)


database_url = os.environ["DATABASE_URL"]
config.set_main_option("sqlalchemy.url", database_url)

target_metadata = db.metadata

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    raise SystemExit("Offline mode not supported; use 'alembic upgrade' normally.")
else:
    run_migrations_online()
