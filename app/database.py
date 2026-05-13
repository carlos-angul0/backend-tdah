from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL
import os

DATABASE_URL = os.getenv("DATABASE_URL")
#DATABASE_URL = "postgresql://admin_tdah:admin@localhost:5432/tdah_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()