"""Test aspect calculations."""
import pytest
from app.core.calculations.aspects import EnhancedAspectCalculator


@pytest.fixture
def calculator():
    """Get aspect calculator instance."""
    return EnhancedAspectCalculator()


def test_calculate_aspect_angle(calculator):
    """Test aspect angle calculation."""
    # Test conjunction (0°)
    assert calculator.calculate_aspect_angle(0.0, 0.0) == 0.0
    # Test opposition (180°)
    assert calculator.calculate_aspect_angle(0.0, 180.0) == 180.0
    # Test trine (120°)
    assert calculator.calculate_aspect_angle(0.0, 120.0) == 120.0
    # Test across 0°
    assert abs(calculator.calculate_aspect_angle(350.0, 10.0) - 20.0) < 0.001


def test_is_aspect_within_orb(calculator):
    """Test aspect orb calculation."""
    # Test exact aspect
    assert calculator.is_aspect_within_orb(120.0, 120.0, 8.0) is True
    # Test within orb
    assert calculator.is_aspect_within_orb(118.0, 120.0, 8.0) is True
    # Test outside orb
    assert calculator.is_aspect_within_orb(111.0, 120.0, 8.0) is False


def test_get_aspect_type(calculator):
    """Test aspect type determination."""
    # Test conjunction
    assert calculator.get_aspect_type(0.0, 8.0) == "conjunction"
    # Test opposition
    assert calculator.get_aspect_type(180.0, 8.0) == "opposition"
    # Test trine
    assert calculator.get_aspect_type(120.0, 8.0) == "trine"
    # Test no aspect
    assert calculator.get_aspect_type(45.0, 8.0) is None


def test_calculate_planet_aspects(calculator):
    """Test planet aspects calculation."""
    # Test case: Two planets in trine
    planet_positions = {
        "Sun": 0.0,
        "Moon": 120.0,
        "Mars": 90.0
    }
    orb = 8.0
    
    aspects = calculator.calculate_planet_aspects(planet_positions, orb)
    assert isinstance(aspects, list)
    
    # Check for Sun-Moon trine
    sun_moon_aspect = next(
        (a for a in aspects if 
         (a["planet1"] == "Sun" and a["planet2"] == "Moon") or
         (a["planet1"] == "Moon" and a["planet2"] == "Sun")),
        None
    )
    assert sun_moon_aspect is not None
    assert sun_moon_aspect["aspect"] == "trine"


def test_calculate_orb_strength(calculator):
    """Test orb strength calculation."""
    aspect = calculator.ASPECTS["Conjunction"]
    
    # Test exact aspect (0° orb)
    assert calculator._calculate_orb_strength(aspect, 0.0) == 100.0
    
    # Test half orb
    half_strength = calculator._calculate_orb_strength(aspect, aspect.orb / 2)
    assert 45 < half_strength < 55
    
    # Test full orb
    assert calculator._calculate_orb_strength(aspect, aspect.orb) == 0.0


def test_calculate_speed_strength(calculator):
    """Test speed strength calculation."""
    # Test same speed
    assert calculator._calculate_speed_strength(1.0, 1.0) == 100.0
    
    # Test moderate speed difference
    assert 40 < calculator._calculate_speed_strength(1.0, 2.0) < 60
    
    # Test large speed difference
    assert calculator._calculate_speed_strength(1.0, 11.0) == 0.0


def test_calculate_dignity_strength(calculator):
    """Test dignity strength calculation."""
    # Test exalted planets
    assert calculator._calculate_dignity_strength("exalted", "exalted") == 100.0
    
    # Test debilitated planets
    assert calculator._calculate_dignity_strength("debilitated", "debilitated") == 5.0
    
    # Test mixed dignities
    mixed_strength = calculator._calculate_dignity_strength("exalted", "debilitated")
    assert 0 < mixed_strength < 100
