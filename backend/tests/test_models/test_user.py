"""Test user model module."""
import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from app.core.security import get_password_hash
from app.models.users import User


@pytest.fixture
def test_user(test_db):
    """Create test user."""
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


def test_create_user(test_db):
    """Test user creation."""
    user = User(
        id=str(uuid.uuid4()),
        email="test1@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User 1",
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    assert user.id is not None
    assert user.email == "test1@example.com"
    assert user.full_name == "Test User 1"
    assert user.is_active
    assert not user.is_superuser


def test_update_user(test_user, test_db):
    """Test user update."""
    test_user.full_name = "Updated Name"
    test_db.commit()
    test_db.refresh(test_user)
    
    assert test_user.full_name == "Updated Name"


def test_delete_user(test_user, test_db):
    """Test user deletion."""
    user_id = test_user.id
    test_db.delete(test_user)
    test_db.commit()
    
    deleted_user = test_db.query(User).filter(User.id == user_id).first()
    assert deleted_user is None


def test_unique_email_constraint(test_user, test_db):
    """Test unique email constraint."""
    with pytest.raises(IntegrityError):
        user = User(
            id=str(uuid.uuid4()),
            email=test_user.email,  # Same email as test_user
            hashed_password=get_password_hash("testpassword"),
            full_name="Another User",
        )
        test_db.add(user)
        test_db.commit()
