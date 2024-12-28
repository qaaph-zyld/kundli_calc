"""
Test suite for the Vimshottari Dasha calculation system
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from app.core.calculations.dasha_system import VimshottariDasha

@pytest.fixture
def dasha_calculator():
    return VimshottariDasha()

def test_birth_nakshatra_calculation(dasha_calculator):
    # Test cases with known nakshatra positions
    nakshatra_span = Decimal('13.333333333333334')  # 13°20'
    test_cases = [
        (0.0, 1, 1.0),                   # Start of first nakshatra
        (float(nakshatra_span - Decimal('0.000001')), 2, 1.0),  # Just before end of first nakshatra
        (float(nakshatra_span + Decimal('0.000001')), 2, 0.999999),  # Just after start of second nakshatra
        (float(nakshatra_span * Decimal('26') + Decimal('0.000001')), 27, 0.999999),  # Just after start of last nakshatra
        (359.99999, 27, 0.0),            # End of last nakshatra
        (float(nakshatra_span * Decimal('9')), 10, 1.0),  # Start of 10th nakshatra
        (13.33333, 2, 1.0)               # Start of second nakshatra
    ]
    
    for moon_long, expected_nak, expected_balance in test_cases:
        nakshatra, balance = dasha_calculator.calculate_birth_nakshatra_balance(moon_long)
        assert nakshatra == expected_nak, f"Failed for moon_long={moon_long}"
        assert abs(balance - expected_balance) < 0.000002, f"Failed for moon_long={moon_long}, expected {expected_balance}, got {balance}"

def test_dasha_sequence(dasha_calculator):
    # Test dasha sequence for different birth nakshatras
    test_cases = [
        (1, ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']),
        (2, ['Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury', 'Ketu']),
        (3, ['Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury', 'Ketu', 'Venus']),
        (13, ['Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury', 'Ketu', 'Venus', 'Sun']),
        (19, ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'])
    ]
    
    for nakshatra, expected_sequence in test_cases:
        sequence = dasha_calculator.get_dasha_sequence(nakshatra)
        assert sequence == expected_sequence
        # Verify total years equals 120
        total_years = sum(dasha_calculator.maha_dasha_periods[planet] for planet in sequence)
        assert total_years == 120

def test_dasha_period_calculation(dasha_calculator):
    test_cases = [
        {
            'birth_date': datetime(2000, 1, 1, 12, 0),
            'moon_long': 0.0,  # Start of first nakshatra (Ketu)
            'expected_first_planet': 'Ketu',
            'expected_first_years': 7.0  # Full Ketu period
        },
        {
            'birth_date': datetime(2000, 1, 1, 12, 0),
            'moon_long': float(Decimal('13.333333333333334')),  # Start of second nakshatra (Venus)
            'expected_first_planet': 'Venus',
            'expected_first_years': 20.0  # Full Venus period
        },
        {
            'birth_date': datetime(2000, 1, 1, 12, 0),
            'moon_long': float(Decimal('26.666666666666668')),  # Start of third nakshatra (Sun)
            'expected_first_planet': 'Sun',
            'expected_first_years': 6.0  # Full Sun period
        }
    ]
    
    for test_case in test_cases:
        result = dasha_calculator.calculate_dasha_periods(
            test_case['birth_date'], 
            test_case['moon_long']
        )
        
        assert 'birth_nakshatra' in result
        assert 'balance' in result
        assert 'periods' in result
        assert len(result['periods']) == 9
        
        first_period = result['periods'][0]
        assert first_period['planet'] == test_case['expected_first_planet']
        assert first_period['start_date'] == test_case['birth_date']
        assert abs(first_period['duration_years'] - test_case['expected_first_years']) < 0.000001
        
        # Verify continuity of periods
        for i in range(len(result['periods']) - 1):
            current = result['periods'][i]
            next_period = result['periods'][i + 1]
            assert current['end_date'] == next_period['start_date']

def test_antardasha_calculation(dasha_calculator):
    main_period = {
        'planet': 'Moon',
        'start_date': datetime(2000, 1, 1),
        'end_date': datetime(2010, 1, 1),  # 10 years (Moon's period)
        'duration_years': 10
    }
    
    sub_periods = dasha_calculator.calculate_antardasha(main_period)
    
    assert len(sub_periods) == 9  # Should have 9 sub-periods
    
    # Verify first sub-period
    first_sub = sub_periods[0]
    assert first_sub['main_planet'] == 'Moon'
    assert first_sub['sub_planet'] == 'Moon'
    assert first_sub['start_date'] == main_period['start_date']
    
    # Verify proportional durations
    total_days = (main_period['end_date'] - main_period['start_date']).days
    moon_period = dasha_calculator.maha_dasha_periods['Moon']
    
    for sub in sub_periods:
        sub_planet = sub['sub_planet']
        expected_days = int((Decimal(str(dasha_calculator.maha_dasha_periods[sub_planet])) / Decimal('120') * Decimal(str(total_days))).to_integral_value())
        if sub == sub_periods[-1]:
            # Last period gets remaining days
            expected_days = total_days - sum(p['duration_days'] for p in sub_periods[:-1])
        assert abs(sub['duration_days'] - expected_days) <= 1  # Allow for rounding difference
    
    # Verify last sub-period
    last_sub = sub_periods[-1]
    assert last_sub['end_date'] == main_period['end_date']
    
    # Verify total duration matches main period
    total_sub_days = sum(sub['duration_days'] for sub in sub_periods)
    expected_total_days = (main_period['end_date'] - main_period['start_date']).days
    assert total_sub_days == expected_total_days

def test_pratyantardasha_calculation(dasha_calculator):
    antardasha_period = {
        'main_planet': 'Moon',
        'sub_planet': 'Mars',
        'start_date': datetime(2000, 1, 1),
        'end_date': datetime(2000, 7, 1),  # 182 days
        'duration_days': 182
    }
    
    prat_periods = dasha_calculator.calculate_pratyantardasha(antardasha_period)
    
    assert len(prat_periods) == 9  # Should have 9 sub-periods
    
    # Verify first sub-period
    first_prat = prat_periods[0]
    assert first_prat['main_planet'] == 'Moon'
    assert first_prat['sub_planet'] == 'Mars'
    assert first_prat['prat_planet'] == 'Mars'
    assert first_prat['start_date'] == antardasha_period['start_date']
    
    # Verify proportional durations
    total_days = antardasha_period['duration_days']
    
    for prat in prat_periods:
        sub_planet = prat['prat_planet']
        expected_days = int((Decimal(str(dasha_calculator.maha_dasha_periods[sub_planet])) / Decimal('120') * Decimal(str(total_days))).to_integral_value())
        if prat == prat_periods[-1]:
            # Last period gets remaining days
            expected_days = total_days - sum(p['duration_days'] for p in prat_periods[:-1])
        assert abs(prat['duration_days'] - expected_days) <= 1  # Allow for rounding difference
    
    # Verify last sub-period
    last_prat = prat_periods[-1]
    assert last_prat['end_date'] == antardasha_period['end_date']
    
    # Verify total duration matches antardasha period
    total_prat_days = sum(prat['duration_days'] for prat in prat_periods)
    expected_total_days = (antardasha_period['end_date'] - antardasha_period['start_date']).days
    assert total_prat_days == expected_total_days

def test_all_dasha_levels(dasha_calculator):
    birth_date = datetime(2000, 1, 1, 12, 0)
    moon_long = 0.0  # Start of first nakshatra
    
    result = dasha_calculator.calculate_all_dasha_levels(birth_date, moon_long)
    
    # Verify structure
    assert 'birth_nakshatra' in result
    assert 'balance' in result
    assert 'periods' in result
    
    # Check main periods
    assert len(result['periods']) == 9
    
    # Check antardasha periods
    for period in result['periods']:
        assert 'antardasha' in period
        assert len(period['antardasha']) == 9
        
        # Check pratyantardasha periods
        for antardasha in period['antardasha']:
            assert 'pratyantardasha' in antardasha
            assert len(antardasha['pratyantardasha']) == 9
            
            # Verify continuity of pratyantardasha periods
            for i in range(len(antardasha['pratyantardasha']) - 1):
                current = antardasha['pratyantardasha'][i]
                next_period = antardasha['pratyantardasha'][i + 1]
                assert current['end_date'] == next_period['start_date']

def test_invalid_antardasha_input(dasha_calculator):
    # Test missing required keys
    invalid_period = {
        'main_planet': 'Moon',
        'sub_planet': 'Mars'
        # Missing start_date, end_date, and duration_days
    }
    
    with pytest.raises(ValueError):
        dasha_calculator.calculate_pratyantardasha(invalid_period)

def test_edge_cases(dasha_calculator):
    # Test invalid moon longitude
    with pytest.raises(ValueError):
        dasha_calculator.calculate_dasha_periods(
            datetime(2000, 1, 1),
            400.0  # Invalid moon longitude
        )
    
    with pytest.raises(ValueError):
        dasha_calculator.calculate_dasha_periods(
            datetime(2000, 1, 1),
            -0.1  # Invalid moon longitude
        )
    
    # Test invalid period calculation
    with pytest.raises(ValueError):
        dasha_calculator.calculate_dasha_periods(
            datetime(2000, 1, 1),
            360.1  # Invalid moon longitude
        )

def test_precision_calculations(dasha_calculator):
    # Test precise nakshatra boundaries
    test_cases = [
        (13.33333333333333, 2, 1.0),  # Start of second nakshatra
        (13.33333333333334, 2, 1.0),  # Also start of second nakshatra
        (346.66666666666663, 27, 1.0),  # Start of last nakshatra
        (346.66666666666664, 27, 1.0),  # Also start of last nakshatra
    ]
    
    for moon_long, expected_nak, expected_balance in test_cases:
        nakshatra, balance = dasha_calculator.calculate_birth_nakshatra_balance(moon_long)
        assert nakshatra == expected_nak, f"Failed for moon_long={moon_long}"
        assert abs(balance - expected_balance) < 0.000001, f"Failed for moon_long={moon_long}"
