from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# We'll point DATABASE_URL to Postgres later via env var
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./receipts.db"  # use sqlite for local dev first (simpler)
)

# For sqlite, need check_same_thread=False
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()