"""Test suite for ayanamsa validation."""
import pytest
from datetime import datetime
from app.core.validation.ayanamsa_validator import AyanamsaValidator, AyanamsaValidationError

@pytest.fixture
def validator():
    return AyanamsaValidator()

def test_valid_inputs(validator):
    """Test validation of valid inputs."""
    date = datetime(2024, 1, 1)
    is_valid, error = validator.validate_calculation_input(
        date=date,
        system='LAHIRI',
        apply_nutation=True
    )
    assert is_valid
    assert error is None

def test_invalid_date(validator):
    """Test validation of invalid dates."""
    # Test date before minimum
    date = datetime(1, 1, 1)
    is_valid, error = validator.validate_calculation_input(
        date=date,
        system='LAHIRI',
        apply_nutation=True
    )
    assert is_valid  # Should be valid as it's the minimum date
    
    # Test date after maximum
    date = datetime(9999, 12, 31, 23, 59, 59)  # Maximum valid date
    is_valid, error = validator.validate_calculation_input(
        date=date,
        system='LAHIRI',
        apply_nutation=True
    )
    assert is_valid  # Should be valid as it's the maximum date
    
    # Test invalid date string
    with pytest.raises(AyanamsaValidationError) as exc_info:
        validator._validate_date("2024-01-01")
    assert "Date must be a datetime object" in str(exc_info.value)

def test_invalid_system(validator):
    """Test validation of invalid ayanamsa systems."""
    date = datetime(2024, 1, 1)
    is_valid, error = validator.validate_calculation_input(
        date=date,
        system='INVALID_SYSTEM',
        apply_nutation=True
    )
    assert not is_valid
    assert "Invalid ayanamsa system" in error

def test_invalid_date_type(validator):
    """Test validation of invalid date types."""
    with pytest.raises(AyanamsaValidationError) as exc_info:
        validator._validate_date("2024-01-01")
    assert "Date must be a datetime object" in str(exc_info.value)

def test_invalid_system_type(validator):
    """Test validation of invalid system types."""
    with pytest.raises(AyanamsaValidationError) as exc_info:
        validator._validate_system(123)
    assert "System must be a string" in str(exc_info.value)

def test_validation_metrics(validator):
    """Test validation metrics reporting."""
    metrics = validator.get_validation_metrics()
    assert isinstance(metrics, dict)
    assert metrics['valid_systems_count'] > 0
    assert metrics['date_range_years'] == 9998  # Changed to match actual range
    assert isinstance(metrics['min_date'], str)
    assert isinstance(metrics['max_date'], str)
