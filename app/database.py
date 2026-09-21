import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


password = os.environ["SIGNALDESK_DB_PASSWORD"]
DATABASE_URL = f"postgresql+psycopg://signaldesk_user:{password}@localhost:5432/signaldesk"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()