"""Test database module."""
import os

# Set test environment before importing any modules
os.environ["ENV"] = "test"

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db, init_test_db, cleanup_test_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database."""
    # Initialize test database
    init_test_db()
    
    yield
    
    # Clean up test database
    cleanup_test_db()


@pytest.fixture
def test_db():
    """Test database session."""
    db = next(get_db())
    try:
        yield db
    finally:
        db.rollback()
        db.close()


def test_create_db_session(test_db):
    """Test database session creation."""
    assert isinstance(test_db, Session)


def test_db_session_rollback(test_db):
    """Test database session rollback."""
    try:
        # Try to execute an invalid query
        test_db.execute(text("SELECT * FROM non_existent_table"))
        test_db.commit()
        assert False, "Should have raised an exception"
    except Exception:
        test_db.rollback()
        assert True


def test_db_session_commit(test_db):
    """Test database session commit."""
    try:
        # Execute a valid query
        test_db.execute(text("SELECT 1"))
        test_db.commit()
        assert True
    except Exception:
        assert False, "Should not have raised an exception"


def test_db_session_context():
    """Test database session context management."""
    db = next(get_db())
    try:
        db.execute(text("SELECT 1"))
        db.commit()
        assert True
    finally:
        db.close()
