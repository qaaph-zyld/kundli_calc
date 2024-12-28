"""Test birth chart model."""
import pytest
from datetime import datetime
import uuid

from app.models.birth_charts import BirthChart
from app.models.users import User
from app.core.security import get_password_hash


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


def test_create_birth_chart(test_db, test_user):
    """Test birth chart creation."""
    chart_id = str(uuid.uuid4())
    birth_time = datetime.utcnow()

    chart = BirthChart(
        id=chart_id,
        user_id=test_user.id,
        name="Test Chart",
        date_of_birth=birth_time.date(),
        time_of_birth=birth_time.time(),
        place_of_birth="New Delhi",
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
    )

    test_db.add(chart)
    test_db.commit()
    test_db.refresh(chart)

    assert chart.id == chart_id
    assert chart.user_id == test_user.id
    assert chart.name == "Test Chart"
    assert chart.place_of_birth == "New Delhi"
    assert abs(chart.latitude - 28.6139) < 0.0001
    assert abs(chart.longitude - 77.2090) < 0.0001
    assert chart.timezone == "Asia/Kolkata"
    assert isinstance(chart.created_at, datetime)
    assert isinstance(chart.updated_at, datetime)


def test_update_birth_chart(test_db, test_user):
    """Test birth chart update."""
    # Create birth chart
    chart = BirthChart(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        name="Test Chart",
        date_of_birth=datetime.utcnow().date(),
        time_of_birth=datetime.utcnow().time(),
        place_of_birth="New Delhi",
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
    )
    test_db.add(chart)
    test_db.commit()

    # Update birth chart
    new_name = "Updated Chart"
    chart.name = new_name
    test_db.commit()
    test_db.refresh(chart)

    assert chart.name == new_name
    assert chart.updated_at > chart.created_at


def test_delete_birth_chart(test_db, test_user):
    """Test birth chart deletion."""
    # Create birth chart
    chart_id = str(uuid.uuid4())
    chart = BirthChart(
        id=chart_id,
        user_id=test_user.id,
        name="Test Chart",
        date_of_birth=datetime.utcnow().date(),
        time_of_birth=datetime.utcnow().time(),
        place_of_birth="New Delhi",
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
    )
    test_db.add(chart)
    test_db.commit()

    # Delete birth chart
    test_db.delete(chart)
    test_db.commit()

    # Try to find the deleted chart
    deleted_chart = test_db.query(BirthChart).filter(BirthChart.id == chart_id).first()
    assert deleted_chart is None


def test_birth_chart_user_relationship(test_db, test_user):
    """Test birth chart-user relationship."""
    # Create birth chart
    chart = BirthChart(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        name="Test Chart",
        date_of_birth=datetime.utcnow().date(),
        time_of_birth=datetime.utcnow().time(),
        place_of_birth="New Delhi",
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
    )
    test_db.add(chart)
    test_db.commit()
    test_db.refresh(chart)

    # Test relationship
    assert chart.user == test_user
    assert chart in test_user.birth_charts


def test_cascade_delete(test_db, test_user):
    """Test cascade delete when user is deleted."""
    # Create birth chart
    chart = BirthChart(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        name="Test Chart",
        date_of_birth=datetime.utcnow().date(),
        time_of_birth=datetime.utcnow().time(),
        place_of_birth="New Delhi",
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
    )
    test_db.add(chart)
    test_db.commit()

    # Delete user
    test_db.delete(test_user)
    test_db.commit()

    # Check if birth chart was also deleted
    deleted_chart = test_db.query(BirthChart).filter(BirthChart.id == chart.id).first()
    assert deleted_chart is None
