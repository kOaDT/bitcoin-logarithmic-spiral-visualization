from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logging.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close() 