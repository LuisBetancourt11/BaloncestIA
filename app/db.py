"""Database configuration and session factory.

By default this uses a local SQLite file `app.db`. In production set the
`DATABASE_URL` environment variable to a proper database URI (e.g. Postgres).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Use DATABASE_URL env var if present, otherwise fall back to local sqlite
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./app.db')

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
