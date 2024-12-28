"""Test planetary position model."""
import pytest
from datetime import datetime
import uuid

from app.models.users import User
from app.models.birth_charts import BirthChart
from app.models.planetary_positions import PlanetaryPosition
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


@pytest.fixture
def test_birth_chart(test_db, test_user):
    """Create test birth chart."""
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
    return chart


def test_create_planetary_position(test_db, test_birth_chart):
    """Test planetary position creation."""
    position_id = str(uuid.uuid4())
    position = PlanetaryPosition(
        id=position_id,
        birth_chart_id=test_birth_chart.id,
        planet_name="Sun",
        longitude=45.5,
        latitude=0.0,
        speed=1.0,
        house=1,
        zodiac_sign="Taurus",
        nakshatra="Rohini",
        nakshatra_pada=2,
    )

    test_db.add(position)
    test_db.commit()
    test_db.refresh(position)

    assert position.id == position_id
    assert position.birth_chart_id == test_birth_chart.id
    assert position.planet_name == "Sun"
    assert abs(position.longitude - 45.5) < 0.0001
    assert abs(position.latitude - 0.0) < 0.0001
    assert abs(position.speed - 1.0) < 0.0001
    assert position.house == 1
    assert position.zodiac_sign == "Taurus"
    assert position.nakshatra == "Rohini"
    assert position.nakshatra_pada == 2
    assert isinstance(position.created_at, datetime)
    assert isinstance(position.updated_at, datetime)


def test_update_planetary_position(test_db, test_birth_chart):
    """Test planetary position update."""
    # Create position
    position = PlanetaryPosition(
        id=str(uuid.uuid4()),
        birth_chart_id=test_birth_chart.id,
        planet_name="Sun",
        longitude=45.5,
        latitude=0.0,
        speed=1.0,
    )
    test_db.add(position)
    test_db.commit()

    # Update position
    new_longitude = 90.0
    position.longitude = new_longitude
    test_db.commit()
    test_db.refresh(position)

    assert abs(position.longitude - new_longitude) < 0.0001
    assert position.updated_at > position.created_at


def test_delete_planetary_position(test_db, test_birth_chart):
    """Test planetary position deletion."""
    # Create position
    position_id = str(uuid.uuid4())
    position = PlanetaryPosition(
        id=position_id,
        birth_chart_id=test_birth_chart.id,
        planet_name="Sun",
        longitude=45.5,
        latitude=0.0,
        speed=1.0,
    )
    test_db.add(position)
    test_db.commit()

    # Delete position
    test_db.delete(position)
    test_db.commit()

    # Try to find the deleted position
    deleted_position = test_db.query(PlanetaryPosition).filter(
        PlanetaryPosition.id == position_id
    ).first()
    assert deleted_position is None


def test_birth_chart_relationship(test_db, test_birth_chart):
    """Test planetary position-birth chart relationship."""
    # Create position
    position = PlanetaryPosition(
        id=str(uuid.uuid4()),
        birth_chart_id=test_birth_chart.id,
        planet_name="Sun",
        longitude=45.5,
        latitude=0.0,
        speed=1.0,
    )
    test_db.add(position)
    test_db.commit()
    test_db.refresh(position)

    # Test relationship
    assert position.birth_chart == test_birth_chart
    assert position in test_birth_chart.planetary_positions


def test_cascade_delete(test_db, test_birth_chart):
    """Test cascade delete when birth chart is deleted."""
    # Create position
    position = PlanetaryPosition(
        id=str(uuid.uuid4()),
        birth_chart_id=test_birth_chart.id,
        planet_name="Sun",
        longitude=45.5,
        latitude=0.0,
        speed=1.0,
    )
    test_db.add(position)
    test_db.commit()

    # Delete birth chart
    test_db.delete(test_birth_chart)
    test_db.commit()

    # Check if planetary position was also deleted
    deleted_position = test_db.query(PlanetaryPosition).filter(
        PlanetaryPosition.id == position.id
    ).first()
    assert deleted_position is None
