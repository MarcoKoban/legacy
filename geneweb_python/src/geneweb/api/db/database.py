"""
Database configuration and session management for user authentication.

This module provides:
- SQLAlchemy engine and session management
- Database initialization and migrations
- Connection pooling
- Database utilities
"""

from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ..config import settings
from .models import Base

# Database file path
DB_DIR = Path(__file__).parent.parent.parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "geneweb_users.db"


# Create SQLAlchemy engine
def get_database_url() -> str:
    """Get database URL from settings or use default SQLite."""
    # For now, use SQLite. In production, use PostgreSQL
    return f"sqlite:///{DB_PATH}"


# Create engine with appropriate settings
engine = create_engine(
    get_database_url(),
    # SQLite specific settings
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=settings.debug,  # Log SQL queries in debug mode
)


# Enable foreign key constraints for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraints for SQLite."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in models.py if they don't exist.
    Safe to call multiple times (idempotent).
    """
    import logging

    logger = logging.getLogger("geneweb.api.db")

    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info(
            "Database initialized successfully",
            db_path=str(DB_PATH),
            tables=list(Base.metadata.tables.keys()),
        )
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions.

    Use this in FastAPI route dependencies:
    ```python
    @router.get("/users")
    async def get_users(db: Session = Depends(get_db)):
        users = db.query(UserModel).all()
        return users
    ```

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_default_users(db: Session) -> None:
    """
    Create default admin and demo users if they don't exist.

    Args:
        db: Database session
    """
    import logging
    from datetime import datetime, timezone

    from ..security.auth import UserRole, auth_service
    from .models import UserModel

    logger = logging.getLogger("geneweb.api.db")

    # Check if users already exist
    existing_admin = db.query(UserModel).filter(UserModel.username == "admin").first()
    existing_demo = db.query(UserModel).filter(UserModel.username == "demo").first()

    if not existing_admin:
        admin_user = UserModel(
            username="admin",
            email="admin@geneweb.local",
            full_name="Administrator",
            hashed_password=auth_service.get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            password_changed_at=datetime.now(timezone.utc),
        )
        db.add(admin_user)
        logger.info("Created default admin user")

    if not existing_demo:
        demo_user = UserModel(
            username="demo",
            email="demo@geneweb.local",
            full_name="Demo User",
            hashed_password=auth_service.get_password_hash("demo1234"),
            role=UserRole.USER,
            is_active=True,
            is_verified=True,
            password_changed_at=datetime.now(timezone.utc),
        )
        db.add(demo_user)
        logger.info("Created default demo user")

    db.commit()
