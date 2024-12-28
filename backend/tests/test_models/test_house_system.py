"""Test house system model."""
import pytest
from datetime import datetime
import uuid

from app.models.users import User
from app.models.birth_charts import BirthChart
from app.models.house_systems import HouseSystem
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


def test_create_house_system(test_db, test_birth_chart):
    """Test house system creation."""
    house_id = str(uuid.uuid4())
    house = HouseSystem(
        id=house_id,
        birth_chart_id=test_birth_chart.id,
        system_name="Placidus",
        house_number=1,
        cusp_longitude=45.5,
        sign="Taurus",
        degree=15.5,
    )

    test_db.add(house)
    test_db.commit()
    test_db.refresh(house)

    assert house.id == house_id
    assert house.birth_chart_id == test_birth_chart.id
    assert house.system_name == "Placidus"
    assert house.house_number == 1
    assert abs(house.cusp_longitude - 45.5) < 0.0001
    assert house.sign == "Taurus"
    assert abs(house.degree - 15.5) < 0.0001
    assert isinstance(house.created_at, datetime)
    assert isinstance(house.updated_at, datetime)


def test_update_house_system(test_db, test_birth_chart):
    """Test house system update."""
    # Create house
    house = HouseSystem(
        id=str(uuid.uuid4()),
        birth_chart_id=test_birth_chart.id,
        system_name="Placidus",
        house_number=1,
        cusp_longitude=45.5,
    )
    test_db.add(house)
    test_db.commit()

    # Update house
    new_longitude = 90.0
    house.cusp_longitude = new_longitude
    test_db.commit()
    test_db.refresh(house)

    assert abs(house.cusp_longitude - new_longitude) < 0.0001
    assert house.updated_at > house.created_at


def test_delete_house_system(test_db, test_birth_chart):
    """Test house system deletion."""
    # Create house
    house_id = str(uuid.uuid4())
    house = HouseSystem(
        id=house_id,
        birth_chart_id=test_birth_chart.id,
        system_name="Placidus",
        house_number=1,
        cusp_longitude=45.5,
    )
    test_db.add(house)
    test_db.commit()

    # Delete house
    test_db.delete(house)
    test_db.commit()

    # Try to find the deleted house
    deleted_house = test_db.query(HouseSystem).filter(
        HouseSystem.id == house_id
    ).first()
    assert deleted_house is None


def test_birth_chart_relationship(test_db, test_birth_chart):
    """Test house system-birth chart relationship."""
    # Create house
    house = HouseSystem(
        id=str(uuid.uuid4()),
        birth_chart_id=test_birth_chart.id,
        system_name="Placidus",
        house_number=1,
        cusp_longitude=45.5,
    )
    test_db.add(house)
    test_db.commit()
    test_db.refresh(house)

    # Test relationship
    assert house.birth_chart == test_birth_chart
    assert house in test_birth_chart.house_systems


def test_cascade_delete(test_db, test_birth_chart):
    """Test cascade delete when birth chart is deleted."""
    # Create house
    house = HouseSystem(
        id=str(uuid.uuid4()),
        birth_chart_id=test_birth_chart.id,
        system_name="Placidus",
        house_number=1,
        cusp_longitude=45.5,
    )
    test_db.add(house)
    test_db.commit()

    # Delete birth chart
    test_db.delete(test_birth_chart)
    test_db.commit()

    # Check if house system was also deleted
    deleted_house = test_db.query(HouseSystem).filter(
        HouseSystem.id == house.id
    ).first()
    assert deleted_house is None


def test_house_number_range(test_db, test_birth_chart):
    """Test house number range validation."""
    # Create house with invalid house number
    house = HouseSystem(
        id=str(uuid.uuid4()),
        birth_chart_id=test_birth_chart.id,
        system_name="Placidus",
        house_number=13,  # Invalid house number (should be 1-12)
        cusp_longitude=45.5,
    )
    test_db.add(house)

    # Expect an error when committing
    with pytest.raises(Exception):  # SQLite will raise IntegrityError
        test_db.commit()
    test_db.rollback()
