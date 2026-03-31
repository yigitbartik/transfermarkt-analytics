"""Database connection and session management"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from config import DATABASE_URL
from database.models import Base
import logging

logger = logging.getLogger(__name__)

# Create engine with connection pooling
db_engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=db_engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"Error getting database session: {e}")
        db.close()
        raise

def close_db(db):
    """Close database session"""
    if db:
        db.close()

def reset_db():
    """Reset database (drop all tables and recreate)"""
    try:
        Base.metadata.drop_all(bind=db_engine)
        Base.metadata.create_all(bind=db_engine)
        logger.info("Database reset successfully")
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise
