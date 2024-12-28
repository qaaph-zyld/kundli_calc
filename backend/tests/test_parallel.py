"""Tests for parallel processing functionality"""
import pytest
from datetime import datetime, timedelta
from app.core.parallel import batch_processor
from app.api.models import Location

@pytest.fixture
def test_location():
    return Location(latitude=28.6139, longitude=77.2090, altitude=0)

@pytest.fixture
def date_range():
    start_date = datetime(2024, 1, 1, 0, 0)
    end_date = datetime(2024, 1, 10, 0, 0)
    return start_date, end_date

def test_batch_processor_initialization():
    """Test batch processor initialization"""
    assert batch_processor is not None
    assert batch_processor.calculator is not None

def test_date_range_generation(date_range):
    """Test date range generation"""
    start_date, end_date = date_range
    dates = batch_processor._generate_date_range(start_date, end_date)
    
    assert len(dates) == 10
    assert dates[0] == start_date
    assert dates[-1] == end_date
    
    # Check consecutive dates
    for i in range(len(dates) - 1):
        diff = dates[i + 1] - dates[i]
        assert diff == timedelta(days=1)

def test_planetary_positions_batch(test_location, date_range, mocker):
    """Test parallel planetary positions calculation"""
    start_date, end_date = date_range
    
    # Mock swisseph calls
    mocker.patch('swisseph.calc_ut', return_value=((120.5, 23.4, 0.9, 0.1), 0))
    mocker.patch('swisseph.get_ayanamsa_ut', return_value=24.13)
    mocker.patch('swisseph.set_topo')
    
    results = batch_processor.process_date_range(
        start_date,
        end_date,
        test_location,
        "planetary_positions"
    )
    
    assert len(results) == 10
    for result in results:
        assert isinstance(result, dict)
        assert len(result) > 0

def test_house_cusps_batch(test_location, date_range, mocker):
    """Test parallel house cusps calculation"""
    start_date, end_date = date_range
    
    # Mock swisseph house calculations
    mock_cusps = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]
    mock_ascmc = [83.5, 173.2, 263.1, 353.0]
    mocker.patch('swisseph.houses_ex', return_value=(mock_cusps, mock_ascmc))
    
    results = batch_processor.process_date_range(
        start_date,
        end_date,
        test_location,
        "house_cusps"
    )
    
    assert len(results) == 10
    for result in results:
        assert isinstance(result, dict)
        assert 'cusps' in result
        assert 'ascmc' in result
        assert len(result['cusps']) == 12
        assert len(result['ascmc']) == 4

def test_invalid_calculation_type(test_location, date_range):
    """Test invalid calculation type handling"""
    start_date, end_date = date_range
    
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        batch_processor.process_date_range(
            start_date,
            end_date,
            test_location,
            "invalid_type"
        )

def test_error_handling(test_location, date_range, mocker):
    """Test error handling in parallel processing"""
    start_date, end_date = date_range
    
    def mock_calc_ut(*args, **kwargs):
        raise Exception("Test error")
    
    # Mock calculation to raise exception
    mocker.patch('app.core.calculations.astronomical.AstronomicalCalculator.calculate_planetary_positions',
                side_effect=mock_calc_ut)
    
    results = batch_processor.process_date_range(
        start_date,
        end_date,
        test_location,
        "planetary_positions"
    )
    
    assert len(results) == 10
    for result in results:
        assert result == {}
