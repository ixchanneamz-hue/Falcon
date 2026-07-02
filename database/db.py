from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_URL, require_config

engine = create_engine(
    require_config(DATABASE_URL, "DATABASE_URL"),
    echo=False,
    pool_pre_ping=True,
    pool_recycle=280
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
