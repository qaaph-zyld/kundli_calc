import pytest
from unittest.mock import Mock, patch
import sys
from datetime import datetime
from decimal import Decimal

# Mock dependencies that require C extensions
mock_swe = Mock()
mock_swe.calc_ut.return_value = ((45.5, 0, 1.0), 0)  # longitude, latitude, speed
mock_swe.julday.return_value = 2460000.5
mock_swe.sidtime.return_value = 0.0

mock_pd = Mock()
mock_pd.DataFrame = Mock()
mock_pd.DataFrame.return_value = Mock()

mock_np = Mock()
mock_np.array = Mock(return_value=Mock())
mock_np.mean = Mock(return_value=0.5)

# Patch modules before any imports
sys.modules['swisseph'] = mock_swe
sys.modules['pandas'] = mock_pd
sys.modules['numpy'] = mock_np

# Now we can import our app modules
from app.core.database import Base
from app.main import app
from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.core.database import get_db
from app.core.models.chart import Location

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def test_location():
    return Location(latitude=Decimal('28.6139'), longitude=Decimal('77.2090'), altitude=Decimal('0'))

@pytest.fixture
def test_date():
    return datetime(2024, 1, 1, 12, 0, 0)
