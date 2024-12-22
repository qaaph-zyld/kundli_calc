from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import math
from datetime import datetime

@dataclass
class Planet:
    name: str
    longitude: float
    latitude: float
    speed: Dict[str, float]
    house: int
    sign: int
    is_retrograde: bool
    nakshatra: int
    nakshatra_pada: int

@dataclass
class Chart:
    ascendant: float
    planets: Dict[str, Planet]
    houses: Dict[int, float]
    aspects: List[Dict[str, Any]]

class EnhancedPlanetaryStrengthEngine:
    def __init__(self):
        # Natural strengths of planets
        self.natural_strengths = {
            'Sun': 60,
            'Moon': 51,
            'Mars': 28,
            'Mercury': 34,
            'Jupiter': 20,
            'Venus': 50,
            'Saturn': 40
        }
        
        # Directional strengths (dig bala)
        self.directional_strengths = {
            'Sun': {10: 100},      # 10th house (Midheaven)
            'Moon': {4: 100},      # 4th house
            'Mars': {10: 100},     # 10th house
            'Mercury': {1: 100},   # 1st house (Ascendant)
            'Jupiter': {1: 100},   # 1st house
            'Venus': {4: 100},     # 4th house
            'Saturn': {7: 100}     # 7th house
        }
        
        # Motional strengths
        self.motional_strength_rules = {
            'fast': 60,
            'normal': 30,
            'slow': 15,
            'retrograde': 45
        }
        
        # Aspect strengths
        self.aspect_strengths = {
            'conjunction': 100,
            'opposition': 50,
            'trine': 75,
            'square': 25,
            'sextile': 37.5
        }
    
    def _calculate_shadbala_components(
        self,
        planet: Planet,
        chart: Chart
    ) -> Dict[str, float]:
        """
        Calculate detailed Shadbala components
        
        Components:
        1. Sthana Bala (Positional Strength)
        2. Dig Bala (Directional Strength)
        3. Kala Bala (Temporal Strength)
        4. Chesta Bala (Motional Strength)
        5. Naisargika Bala (Natural Strength)
        6. Drik Bala (Aspectual Strength)
        """
        return {
            'sthana_bala': self._calculate_sthana_bala(planet, chart),
            'dig_bala': self._calculate_dig_bala(planet, chart),
            'kala_bala': self._calculate_kala_bala(planet, chart),
            'chesta_bala': self._calculate_chesta_bala(planet),
            'naisargika_bala': self._calculate_naisargika_bala(planet),
            'drik_bala': self._calculate_drik_bala(planet, chart)
        }
    
    def _calculate_sthana_bala(self, planet: Planet, chart: Chart) -> float:
        """Calculate positional strength"""
        # Base strength in sign
        sign_strength = self._calculate_sign_strength(planet)
        
        # Exaltation/Debilitation
        exalt_strength = self._calculate_exaltation_strength(planet)
        
        # Moolatrikona
        moola_strength = self._calculate_moolatrikona_strength(planet)
        
        # Own sign strength
        own_sign_strength = self._calculate_own_sign_strength(planet)
        
        return sign_strength + exalt_strength + moola_strength + own_sign_strength
    
    def _calculate_dig_bala(self, planet: Dict[str, Any], chart: Dict[str, Any]) -> float:
        """Calculate directional strength"""
        # Define directional strengths for each planet
        directional_strengths = {
            "Sun": {"best": 10, "worst": 4},      # Best in 10th, worst in 4th
            "Moon": {"best": 4, "worst": 10},      # Best in 4th, worst in 10th
            "Mars": {"best": 10, "worst": 4},      # Best in 10th, worst in 4th
            "Mercury": {"best": 1, "worst": 7},    # Best in 1st, worst in 7th
            "Jupiter": {"best": 1, "worst": 7},    # Best in 1st, worst in 7th
            "Venus": {"best": 4, "worst": 10},     # Best in 4th, worst in 10th
            "Saturn": {"best": 7, "worst": 1}      # Best in 7th, worst in 1st
        }
        
        # Get planet's house placement
        house = planet.get("house", 1)  # Default to 1st house
        
        # Default to Sun if planet type is not specified
        planet_type = planet.get("name", "Sun")
        planet_dirs = directional_strengths.get(planet_type, directional_strengths["Sun"])
        
        # Calculate distance from best and worst houses
        best_distance = min(
            abs(house - planet_dirs["best"]),
            abs(house - (planet_dirs["best"] + 12)),
            abs(house - (planet_dirs["best"] - 12))
        )
        
        worst_distance = min(
            abs(house - planet_dirs["worst"]),
            abs(house - (planet_dirs["worst"] + 12)),
            abs(house - (planet_dirs["worst"] - 12))
        )
        
        # Convert to strength (100 at best house, 0 at worst house)
        if best_distance < worst_distance:
            # Closer to best house
            strength = 100 - (best_distance / 6) * 50  # Linear falloff
        else:
            # Closer to worst house
            strength = 50 - (worst_distance / 6) * 50  # Linear falloff
        
        return max(0, min(100, strength))  # Clamp between 0 and 100
    
    def _calculate_kala_bala(self, planet: Dict[str, Any], chart: Dict[str, Any]) -> float:
        """Calculate temporal strength"""
        # Get planet's longitude and speed
        longitude = planet["longitude"]
        speed = planet.get("speed", 0)
        
        # Calculate basic temporal strength based on speed
        # Positive speed (direct motion) is stronger than negative (retrograde)
        speed_strength = 50 + (min(abs(speed), 1) * 50 * (1 if speed >= 0 else -0.5))
        
        # Calculate diurnal/nocturnal strength
        # Divide zodiac into day (0-180) and night (180-360) portions
        is_day = 0 <= longitude < 180
        
        # Define diurnal/nocturnal preferences for planets
        day_night_preferences = {
            "Sun": "day",
            "Moon": "night",
            "Mars": "night",
            "Mercury": "neutral",
            "Jupiter": "day",
            "Venus": "night",
            "Saturn": "night"
        }
        
        # Get planet's preference
        planet_type = planet.get("name", "Sun")
        preference = day_night_preferences.get(planet_type, "neutral")
        
        # Calculate day/night strength
        if preference == "neutral":
            day_night_strength = 75  # Neutral planets have good strength regardless
        elif (preference == "day" and is_day) or (preference == "night" and not is_day):
            day_night_strength = 100  # Planet is in preferred time
        else:
            day_night_strength = 50  # Planet is in non-preferred time
        
        # Combine speed and day/night strength
        # Weight speed more heavily as it's a more dynamic factor
        strength = (speed_strength * 0.6) + (day_night_strength * 0.4)
        
        return max(0, min(100, strength))  # Clamp between 0 and 100
    
    def _calculate_chesta_bala(self, planet: Dict[str, Any]) -> float:
        """Calculate motional strength"""
        # Get planet's speed
        speed = planet.get("speed", 0)
        
        # Define typical speeds for each planet
        typical_speeds = {
            "Sun": 1.0,          # Roughly 1° per day
            "Moon": 13.0,        # Roughly 13° per day
            "Mars": 0.5,         # About 0.5° per day
            "Mercury": 1.2,      # Variable, around 1.2° per day
            "Jupiter": 0.1,      # About 0.1° per day
            "Venus": 1.0,        # About 1° per day
            "Saturn": 0.03       # About 0.03° per day
        }
        
        # Get planet's typical speed
        planet_type = planet.get("name", "Sun")
        typical_speed = typical_speeds.get(planet_type, 1.0)
        
        # Calculate ratio of current speed to typical speed
        speed_ratio = abs(speed) / typical_speed if typical_speed != 0 else 0
        
        # Calculate base strength
        if speed >= 0:
            # Direct motion
            if speed_ratio > 1:
                # Faster than typical - very strong
                strength = 100
            else:
                # Slower than typical - moderately strong
                strength = 50 + (speed_ratio * 50)
        else:
            # Retrograde motion - weaker
            if speed_ratio > 1:
                # Fast retrograde - very weak
                strength = 0
            else:
                # Slow retrograde - moderately weak
                strength = 50 - (speed_ratio * 50)
        
        return max(0, min(100, strength))  # Clamp between 0 and 100
    
    def _calculate_naisargika_bala(self, planet: Dict[str, Any]) -> float:
        """Calculate natural strength"""
        # Define natural strengths for each planet
        natural_strengths = {
            "Sun": 100,      # Strongest natural strength
            "Moon": 85,      # Very strong
            "Mars": 70,      # Strong
            "Mercury": 60,   # Moderate to strong
            "Jupiter": 75,   # Strong
            "Venus": 65,     # Moderate to strong
            "Saturn": 50     # Moderate
        }
        
        # Get planet's natural strength
        planet_type = planet.get("name", "Sun")
        strength = natural_strengths.get(planet_type, 50)  # Default to moderate strength
        
        return strength

    def _calculate_drik_bala(self, planet: Planet, chart: Chart) -> float:
        """Calculate aspectual strength"""
        aspect_strength = 0
        for aspect in chart.aspects:
            if aspect['planet1'] == planet.name:
                aspect_strength += self.aspect_strengths.get(
                    aspect['aspect'], 0
                )
        return aspect_strength
    
    def _calculate_vimshopaka_components(
        self,
        planet: Planet,
        chart: Chart
    ) -> Dict[str, float]:
        """
        Calculate Vimshopaka strength components based on:
        - Position in sign
        - Position in nakshatra
        - Position in navamsa
        - Aspects received
        - Dignity
        """
        return {
            'sign_position': self._calculate_sign_position_strength(planet),
            'nakshatra_position': self._calculate_nakshatra_strength(planet),
            'navamsa_position': self._calculate_navamsa_strength(planet),
            'aspect_strength': self._calculate_aspect_strength(planet, chart),
            'dignity_strength': self._calculate_dignity_strength(planet)
        }
    
    def _calculate_special_strengths(
        self,
        planet: Planet,
        chart: Chart
    ) -> Dict[str, float]:
        """
        Calculate special strength factors:
        - Yuddha Bala (War strength)
        - Kendradi Bala (Angular house strength)
        - Drekkana Bala (Decanate strength)
        - Saptavargaja Bala (Seven division strength)
        """
        return {
            'yuddha_bala': self._calculate_yuddha_bala(planet, chart),
            'kendradi_bala': self._calculate_kendradi_bala(planet),
            'drekkana_bala': self._calculate_drekkana_bala(planet),
            'saptavargaja_bala': self._calculate_saptavargaja_bala(planet)
        }
    
    def _calculate_sign_strength(self, planet: Dict[str, Any]) -> float:
        """Calculate strength based on zodiac sign placement"""
        longitude = planet["longitude"]
        sign = int(longitude / 30)  # Get zodiac sign (0-11)
        
        # Define sign strengths for each planet type
        sign_strengths = {
            "Sun": {
                0: 60,   # Aries
                1: 70,   # Taurus
                2: 50,   # Gemini
                3: 40,   # Cancer
                4: 100,  # Leo (exaltation)
                5: 50,   # Virgo
                6: 20,   # Libra (debilitation)
                7: 40,   # Scorpio
                8: 80,   # Sagittarius
                9: 30,   # Capricorn
                10: 70,  # Aquarius
                11: 60   # Pisces
            },
            "Moon": {
                0: 50,   # Aries
                1: 100,  # Taurus (exaltation)
                2: 60,   # Gemini
                3: 90,   # Cancer (own sign)
                4: 50,   # Leo
                5: 40,   # Virgo
                6: 50,   # Libra
                7: 20,   # Scorpio (debilitation)
                8: 70,   # Sagittarius
                9: 40,   # Capricorn
                10: 60,  # Aquarius
                11: 70   # Pisces
            },
            "Mars": {
                0: 90,   # Aries (own sign)
                1: 50,   # Taurus
                2: 40,   # Gemini
                3: 30,   # Cancer (debilitation)
                4: 70,   # Leo
                5: 50,   # Virgo
                6: 40,   # Libra
                7: 90,   # Scorpio (own sign)
                8: 100,  # Sagittarius
                9: 100,  # Capricorn (exaltation)
                10: 60,  # Aquarius
                11: 40   # Pisces
            },
            "Mercury": {
                0: 40,   # Aries
                1: 70,   # Taurus
                2: 90,   # Gemini (own sign)
                3: 60,   # Cancer
                4: 50,   # Leo
                5: 90,   # Virgo (own sign)
                6: 100,  # Libra (exaltation)
                7: 40,   # Scorpio
                8: 50,   # Sagittarius
                9: 20,   # Capricorn (debilitation)
                10: 70,  # Aquarius
                11: 60   # Pisces
            },
            "Jupiter": {
                0: 70,   # Aries
                1: 60,   # Taurus
                2: 20,   # Gemini (debilitation)
                3: 100,  # Cancer (exaltation)
                4: 60,   # Leo
                5: 40,   # Virgo
                6: 50,   # Libra
                7: 50,   # Scorpio
                8: 90,   # Sagittarius (own sign)
                9: 40,   # Capricorn
                10: 40,  # Aquarius
                11: 90   # Pisces (own sign)
            },
            "Venus": {
                0: 20,   # Aries (debilitation)
                1: 90,   # Taurus (own sign)
                2: 70,   # Gemini
                3: 60,   # Cancer
                4: 40,   # Leo
                5: 100,  # Virgo (exaltation)
                6: 90,   # Libra (own sign)
                7: 50,   # Scorpio
                8: 40,   # Sagittarius
                9: 60,   # Capricorn
                10: 50,  # Aquarius
                11: 70   # Pisces
            },
            "Saturn": {
                0: 20,   # Aries (debilitation)
                1: 40,   # Taurus
                2: 60,   # Gemini
                3: 50,   # Cancer
                4: 30,   # Leo
                5: 70,   # Virgo
                6: 100,  # Libra (exaltation)
                7: 50,   # Scorpio
                8: 40,   # Sagittarius
                9: 90,   # Capricorn (own sign)
                10: 90,  # Aquarius (own sign)
                11: 40   # Pisces
            }
        }
        
        # Default to Sun's values if planet type is not specified
        planet_type = planet.get("name", "Sun")
        planet_sign_strengths = sign_strengths.get(planet_type, sign_strengths["Sun"])
        
        return planet_sign_strengths[sign]

    def _calculate_exaltation_strength(self, planet: Dict[str, Any]) -> float:
        """Calculate strength based on exaltation/debilitation"""
        longitude = planet["longitude"]
        sign = int(longitude / 30)  # Get zodiac sign (0-11)
        
        # Define exaltation points for each planet
        exaltation_points = {
            "Sun": {
                "sign": 0,  # Aries
                "degree": 10,
                "debilitation_sign": 6  # Libra
            },
            "Moon": {
                "sign": 1,  # Taurus
                "degree": 3,
                "debilitation_sign": 7  # Scorpio
            },
            "Mars": {
                "sign": 9,  # Capricorn
                "degree": 28,
                "debilitation_sign": 3  # Cancer
            },
            "Mercury": {
                "sign": 5,  # Virgo
                "degree": 15,
                "debilitation_sign": 11  # Pisces
            },
            "Jupiter": {
                "sign": 3,  # Cancer
                "degree": 5,
                "debilitation_sign": 2  # Gemini
            },
            "Venus": {
                "sign": 11,  # Pisces
                "degree": 27,
                "debilitation_sign": 5  # Virgo
            },
            "Saturn": {
                "sign": 6,  # Libra
                "degree": 20,
                "debilitation_sign": 0  # Aries
            }
        }
        
        # Default to Sun if planet type is not specified
        planet_type = planet.get("name", "Sun")
        exalt_data = exaltation_points.get(planet_type, exaltation_points["Sun"])
        
        # Calculate distance from exaltation point
        exalt_sign = exalt_data["sign"]
        exalt_degree = exalt_data["degree"]
        debil_sign = exalt_data["debilitation_sign"]
        
        # Convert planet position to degrees from start of zodiac
        planet_degree = longitude % 30
        total_degrees = sign * 30 + planet_degree
        
        # Calculate distance from exaltation point
        exalt_total = exalt_sign * 30 + exalt_degree
        distance = min(
            abs(total_degrees - exalt_total),
            abs(total_degrees - (exalt_total + 360)),
            abs(total_degrees - (exalt_total - 360))
        )
        
        # Maximum distance is 180 degrees
        normalized_distance = min(distance, 180)
        
        # Convert to strength (100 at exaltation, 0 at debilitation)
        strength = 100 - (normalized_distance / 180) * 100
        
        return strength

    def _calculate_moolatrikona_strength(self, planet: Dict[str, Any]) -> float:
        """Calculate strength based on Moolatrikona positions"""
        longitude = planet["longitude"]
        sign = int(longitude / 30)  # Get zodiac sign (0-11)
        degree = longitude % 30  # Get degree within sign
        
        # Define Moolatrikona ranges for each planet
        moolatrikona_ranges = {
            "Sun": {
                "sign": 4,  # Leo
                "start": 0,
                "end": 20
            },
            "Moon": {
                "sign": 1,  # Taurus
                "start": 3,
                "end": 30
            },
            "Mars": {
                "sign": 0,  # Aries
                "start": 0,
                "end": 12
            },
            "Mercury": {
                "sign": 5,  # Virgo
                "start": 15,
                "end": 20
            },
            "Jupiter": {
                "sign": 8,  # Sagittarius
                "start": 0,
                "end": 10
            },
            "Venus": {
                "sign": 6,  # Libra
                "start": 0,
                "end": 15
            },
            "Saturn": {
                "sign": 10,  # Aquarius
                "start": 0,
                "end": 20
            }
        }
        
        # Default to Sun if planet type is not specified
        planet_type = planet.get("name", "Sun")
        moola_data = moolatrikona_ranges.get(planet_type, moolatrikona_ranges["Sun"])
        
        # Check if planet is in Moolatrikona range
        if sign == moola_data["sign"] and moola_data["start"] <= degree <= moola_data["end"]:
            # Calculate how deep into the range the planet is
            range_size = moola_data["end"] - moola_data["start"]
            position = degree - moola_data["start"]
            
            # Full strength at center of range
            center_distance = abs(position - (range_size / 2))
            max_distance = range_size / 2
            
            # Scale strength from 75 to 100 based on distance from center
            strength = 100 - (center_distance / max_distance) * 25
        else:
            # Base strength of 50 outside Moolatrikona
            strength = 50
        
        return strength

    def _calculate_own_sign_strength(self, planet: Dict[str, Any]) -> float:
        """Calculate strength based on own sign placement"""
        longitude = planet["longitude"]
        sign = int(longitude / 30)  # Get zodiac sign (0-11)
        
        # Define own signs for each planet
        own_signs = {
            "Sun": [4],          # Leo
            "Moon": [3],         # Cancer
            "Mars": [0, 7],      # Aries, Scorpio
            "Mercury": [2, 5],   # Gemini, Virgo
            "Jupiter": [8, 11],  # Sagittarius, Pisces
            "Venus": [1, 6],     # Taurus, Libra
            "Saturn": [9, 10]    # Capricorn, Aquarius
        }
        
        # Default to Sun if planet type is not specified
        planet_type = planet.get("name", "Sun")
        planet_own_signs = own_signs.get(planet_type, own_signs["Sun"])
        
        # Check if planet is in own sign
        if sign in planet_own_signs:
            # Calculate position within sign
            degree = longitude % 30
            
            # Higher strength near the middle of the sign
            center_distance = abs(degree - 15)  # Distance from center (15°)
            
            # Scale strength from 80 to 100 based on distance from center
            strength = 100 - (center_distance / 15) * 20
        else:
            # Base strength of 50 outside own sign
            strength = 50
        
        return strength

    def _calculate_sign_position_strength(self, planet: Dict[str, Any]) -> float:
        """Calculate strength based on position within sign"""
        # Get planet's longitude
        longitude = planet["longitude"]
        
        # Calculate position within sign (0-30 degrees)
        sign_position = longitude % 30
        
        # Define strength zones within sign
        # First 5° (0-5): Strong start
        # Middle 20° (5-25): Variable
        # Last 5° (25-30): Weakening
        if sign_position <= 5:
            strength = 75 + (sign_position / 5) * 25  # 75-100
        elif sign_position >= 25:
            strength = 50 - ((sign_position - 25) / 5) * 25  # 50-25
        else:
            # Parabolic strength curve in middle section
            x = (sign_position - 15) / 10  # -1 to 1
            strength = 75 - (x * x * 25)  # Parabola with peak at 15°
            
        return max(0, min(100, strength))

    def _calculate_nakshatra_strength(self, planet: Dict[str, Any]) -> float:
        """Calculate strength based on nakshatra position"""
        # Get planet's longitude
        longitude = planet["longitude"]
        
        # Calculate nakshatra (27 divisions)
        nakshatra_num = (longitude * 27 / 360) % 27
        position_in_nakshatra = (nakshatra_num % 1) * 100
        
        # Define benefic and malefic nakshatras
        benefic_nakshatras = [0, 3, 5, 7, 10, 12, 15, 17, 20, 22, 25]  # Example list
        malefic_nakshatras = [1, 4, 6, 9, 11, 14, 16, 19, 21, 24, 26]  # Example list
        
        base_nakshatra = int(nakshatra_num)
        
        # Determine base strength from nakshatra type
        if base_nakshatra in benefic_nakshatras:
            base_strength = 75
        elif base_nakshatra in malefic_nakshatras:
            base_strength = 25
        else:
            base_strength = 50
            
        # Adjust strength based on position within nakshatra
        if position_in_nakshatra < 25:
            strength = base_strength + 25
        elif position_in_nakshatra > 75:
            strength = base_strength - 25
        else:
            strength = base_strength
            
        return max(0, min(100, strength))

    def _calculate_navamsa_strength(self, planet: Dict[str, Any]) -> float:
        """Calculate strength based on navamsa position"""
        # Get planet's longitude
        longitude = planet["longitude"]
        
        # Calculate navamsa position (108 divisions)
        navamsa_position = (longitude * 9 / 30) % 9
        
        # Define strength based on navamsa position
        # First third (0-3): Strong
        # Middle third (3-6): Moderate
        # Last third (6-9): Weak
        if navamsa_position < 3:
            strength = 100 - (navamsa_position / 3) * 25
        elif navamsa_position < 6:
            strength = 75 - ((navamsa_position - 3) / 3) * 25
        else:
            strength = 50 - ((navamsa_position - 6) / 3) * 25
            
        return max(0, min(100, strength))

    def _calculate_aspect_strength(self, planet: Dict[str, Any], chart: Dict[str, Any]) -> float:
        """Calculate strength based on aspects received"""
        # This is similar to drik bala but focuses on beneficial aspects
        aspect_strengths = {
            0: 100,    # Conjunction with benefic
            60: 75,    # Sextile
            120: 100,  # Trine
            180: 25    # Opposition
        }
        
        # Define benefic and malefic planets
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]
        malefics = ["Saturn", "Mars", "Sun"]  # Sun can be both
        
        # Get planet's longitude
        planet_long = planet["longitude"]
        
        # Initialize total aspect strength
        total_strength = 50  # Start with neutral strength
        num_aspects = 0
        
        # Check aspects from other planets
        for planet_name, other_planet in chart.get("planets", {}).items():
            if other_planet == planet:  # Skip self
                continue
                
            other_long = other_planet["longitude"]
            
            # Calculate angular distance
            distance = abs(planet_long - other_long)
            if distance > 180:
                distance = 360 - distance
                
            # Check for aspects
            for aspect_angle, base_strength in aspect_strengths.items():
                orb = 6  # Tighter orb for Vimshopaka
                if abs(distance - aspect_angle) <= orb:
                    # Modify strength based on aspecting planet
                    if planet_name in benefics:
                        aspect_strength = base_strength
                    elif planet_name in malefics:
                        aspect_strength = base_strength * 0.5  # Reduce strength for malefics
                    else:
                        aspect_strength = base_strength * 0.75
                        
                    # Add to total
                    total_strength = (total_strength + aspect_strength) / 2
                    num_aspects += 1
                    
        return max(0, min(100, total_strength))

    def _calculate_dignity_strength(self, planet: Dict[str, Any]) -> float:
        """Calculate strength based on planetary dignity"""
        # Get planet's longitude
        longitude = planet["longitude"]
        planet_name = planet.get("name", "Sun")  # Default to Sun
        
        # Calculate sign (0-11)
        sign = int(longitude / 30)
        
        # Define dignities for each planet
        dignities = {
            "Sun": {
                "exaltation": 0,      # Aries
                "debilitation": 6,    # Libra
                "own_sign": [4],      # Leo
                "friend_signs": [0, 8],  # Aries, Sagittarius
                "enemy_signs": [10, 11]  # Aquarius, Pisces
            },
            "Moon": {
                "exaltation": 1,      # Taurus
                "debilitation": 7,    # Scorpio
                "own_sign": [3],      # Cancer
                "friend_signs": [2, 4],  # Gemini, Leo
                "enemy_signs": [5, 6]    # Virgo, Libra
            },
            "Mars": {
                "exaltation": 9,      # Capricorn
                "debilitation": 3,    # Cancer
                "own_sign": [0, 7],   # Aries, Scorpio
                "friend_signs": [4, 8],  # Leo, Sagittarius
                "enemy_signs": [1, 2]    # Taurus, Gemini
            },
            "Mercury": {
                "exaltation": 5,      # Virgo
                "debilitation": 11,   # Pisces
                "own_sign": [2, 5],   # Gemini, Virgo
                "friend_signs": [1, 4],  # Taurus, Leo
                "enemy_signs": [7, 8]    # Scorpio, Sagittarius
            },
            "Jupiter": {
                "exaltation": 3,      # Cancer
                "debilitation": 9,    # Capricorn
                "own_sign": [8, 11],  # Sagittarius, Pisces
                "friend_signs": [0, 4],  # Aries, Leo
                "enemy_signs": [5, 6]    # Virgo, Libra
            },
            "Venus": {
                "exaltation": 11,     # Pisces
                "debilitation": 5,    # Virgo
                "own_sign": [1, 6],   # Taurus, Libra
                "friend_signs": [3, 9],  # Cancer, Capricorn
                "enemy_signs": [7, 8]    # Scorpio, Sagittarius
            },
            "Saturn": {
                "exaltation": 6,      # Libra
                "debilitation": 0,    # Aries
                "own_sign": [9, 10],  # Capricorn, Aquarius
                "friend_signs": [2, 5],  # Gemini, Virgo
                "enemy_signs": [3, 4]    # Cancer, Leo
            }
        }
        
        # Get planet's dignity info
        dignity = dignities.get(planet_name, {})
        
        # Calculate position within sign (0-30 degrees)
        sign_position = longitude % 30
        
        # Calculate base strength
        if sign == dignity.get("exaltation"):
            # Exaltation - strength varies from 90-100 based on position
            strength = 90 + (sign_position / 3)
        elif sign == dignity.get("debilitation"):
            # Debilitation - strength varies from 0-10 based on position
            strength = sign_position / 3
        elif sign in dignity.get("own_sign", []):
            # Own sign - strength varies from 70-80
            strength = 70 + (sign_position / 3)
        elif sign in dignity.get("friend_signs", []):
            # Friendly sign - strength varies from 50-60
            strength = 50 + (sign_position / 3)
        elif sign in dignity.get("enemy_signs", []):
            # Enemy sign - strength varies from 20-30
            strength = 20 + (sign_position / 3)
        else:
            # Neutral sign - strength varies from 40-50
            strength = 40 + (sign_position / 3)
            
        return max(0, min(100, strength))

    def _apply_strength_aggregation(
        self,
        strength_components: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Aggregate and normalize strength components
        
        Returns:
            Dict containing:
            - total_strength: Overall strength (0-100)
            - relative_strength: Strength relative to max possible (0-1)
            - component_strengths: Individual component contributions
        """
        # Calculate total strength
        total = 0
        max_possible = 0
        component_strengths = {}
        
        for category, components in strength_components.items():
            category_total = sum(components.values())
            total += category_total
            component_strengths[category] = category_total
            
            # Calculate theoretical maximum for this category
            if category == 'shadbala':
                max_possible += 600  # Maximum shadbala points
            elif category == 'vimshopaka':
                max_possible += 20   # Maximum vimshopaka points
            elif category == 'special_strength':
                max_possible += 100  # Maximum special strength points
        
        # Normalize to 0-100 scale
        normalized_total = (total / max_possible) * 100
        
        return {
            'total_strength': normalized_total,
            'relative_strength': total / max_possible,
            'component_strengths': component_strengths
        }
    
    def calculate_complete_strengths(
        self,
        planet: Planet,
        chart: Chart
    ) -> Dict[str, Any]:
        """Calculate complete strength profile for a planet"""
        # Calculate all strength components
        shadbala_components = self._calculate_shadbala_components(planet, chart)
        vimshopaka_components = self._calculate_vimshopaka_components(planet, chart)
        special_strength = self._calculate_special_strengths(planet, chart)
        
        # Calculate component totals with weights
        shadbala_total = sum(shadbala_components.values()) * 0.4  # 40% weight
        vimshopaka_total = sum(vimshopaka_components.values()) * 0.3  # 30% weight
        special_total = sum(special_strength.values()) * 0.3  # 30% weight
        
        # Calculate relative strength (compared to baseline)
        baseline_strength = 600  # Theoretical maximum
        relative_strength = (shadbala_total + vimshopaka_total + special_total) / baseline_strength
        
        # Get dignity strength for total calculation
        dignity_strength = self._calculate_dignity_strength(planet)
        
        # Calculate total strength (0-100 scale) with dignity influence
        # For debilitated planets (dignity < 10), we reduce the total strength significantly
        if dignity_strength < 10:
            total_strength = dignity_strength * 2  # Max 20% strength for debilitated planets
        else:
            total_strength = min(100, ((relative_strength * 0.6 + dignity_strength * 0.4) * 100))
        
        return {
            'shadbala': shadbala_components,
            'vimshopaka': vimshopaka_components,
            'special_strength': special_strength,
            'component_strengths': {
                'shadbala': shadbala_total,
                'vimshopaka': vimshopaka_total,
                'special_strength': special_total,
                'dignity': dignity_strength
            },
            'relative_strength': relative_strength,
            'total': total_strength
        }

    def _calculate_yuddha_bala(self, planet: Dict[str, Any], chart: Dict[str, Any]) -> float:
        """Calculate war strength (planetary combat)"""
        # Get planet's longitude
        planet_long = planet["longitude"]
        
        # Initialize combat strength
        combat_strength = 50  # Neutral starting point
        
        # Check combative aspects with other planets
        for other_planet in chart.get("planets", {}).values():
            if other_planet == planet:  # Skip self
                continue
                
            other_long = other_planet["longitude"]
            
            # Calculate angular distance
            distance = abs(planet_long - other_long)
            if distance > 180:
                distance = 360 - distance
                
            # Define combat zones and their effects
            if distance < 1:  # Exact conjunction
                combat_strength -= 25  # Weakened by close combat
            elif distance < 3:  # Very close
                combat_strength -= 15
            elif distance < 10:  # Nearby
                combat_strength -= 5
            elif 170 < distance < 190:  # Opposition
                combat_strength += 10  # Strengthened by opposition
                
        return max(0, min(100, combat_strength))

    def _calculate_kendradi_bala(self, planet: Dict[str, Any]) -> float:
        """Calculate angular house strength"""
        # Get planet's house placement
        house = planet.get("house", 1)
        
        # Define strength for different house positions
        # Kendras (angles): 1, 4, 7, 10
        # Panapharas (succedent): 2, 5, 8, 11
        # Apoklimas (cadent): 3, 6, 9, 12
        if house in [1, 4, 7, 10]:  # Kendras
            strength = 100
        elif house in [2, 5, 8, 11]:  # Panapharas
            strength = 75
        else:  # Apoklimas
            strength = 50
            
        return strength

    def _calculate_drekkana_bala(self, planet: Dict[str, Any]) -> float:
        """Calculate decanate strength"""
        # Get planet's longitude
        longitude = planet["longitude"]
        
        # Calculate decanate (10° divisions within sign)
        sign_pos = longitude % 30
        decanate = int(sign_pos / 10)
        
        # Define strength based on decanate position
        # First decanate (0-10°): Strong
        # Second decanate (10-20°): Moderate
        # Third decanate (20-30°): Weak
        if decanate == 0:
            base_strength = 100
        elif decanate == 1:
            base_strength = 75
        else:
            base_strength = 50
            
        # Fine-tune based on position within decanate
        position_in_decanate = sign_pos % 10
        if position_in_decanate < 3:
            strength = base_strength
        elif position_in_decanate < 7:
            strength = base_strength - 10
        else:
            strength = base_strength - 20
            
        return max(0, min(100, strength))

    def _calculate_saptavargaja_bala(self, planet: Dict[str, Any]) -> float:
        """Calculate seven division strength"""
        # Get planet's longitude
        longitude = planet["longitude"]
        
        # Calculate positions in different vargas
        rasi = longitude % 30  # Sign position
        hora = (longitude * 2) % 30  # Hora position
        drekkana = (longitude * 3) % 30  # Drekkana position
        chaturthamsa = (longitude * 4) % 30  # Chaturthamsa position
        saptamsa = (longitude * 7) % 30  # Saptamsa position
        navamsa = (longitude * 9) % 30  # Navamsa position
        dvadasamsa = (longitude * 12) % 30  # Dvadasamsa position
        
        # Calculate strength for each division
        strengths = []
        
        # Rasi (sign) strength
        if rasi < 10:
            strengths.append(100)
        elif rasi < 20:
            strengths.append(75)
        else:
            strengths.append(50)
            
        # Hora strength
        if hora < 15:
            strengths.append(100)
        else:
            strengths.append(75)
            
        # Drekkana strength
        if drekkana < 10:
            strengths.append(100)
        elif drekkana < 20:
            strengths.append(75)
        else:
            strengths.append(50)
            
        # Chaturthamsa strength
        if chaturthamsa < 7.5:
            strengths.append(100)
        elif chaturthamsa < 15:
            strengths.append(75)
        elif chaturthamsa < 22.5:
            strengths.append(50)
        else:
            strengths.append(25)
            
        # Saptamsa strength
        if saptamsa < 4.3:
            strengths.append(100)
        elif saptamsa < 8.6:
            strengths.append(85)
        elif saptamsa < 12.9:
            strengths.append(70)
        elif saptamsa < 17.2:
            strengths.append(55)
        elif saptamsa < 21.5:
            strengths.append(40)
        elif saptamsa < 25.8:
            strengths.append(25)
        else:
            strengths.append(10)
            
        # Navamsa strength
        if navamsa < 3.33:
            strengths.append(100)
        elif navamsa < 6.66:
            strengths.append(90)
        elif navamsa < 10:
            strengths.append(80)
        elif navamsa < 13.33:
            strengths.append(70)
        elif navamsa < 16.66:
            strengths.append(60)
        elif navamsa < 20:
            strengths.append(50)
        elif navamsa < 23.33:
            strengths.append(40)
        elif navamsa < 26.66:
            strengths.append(30)
        else:
            strengths.append(20)
            
        # Dvadasamsa strength
        if dvadasamsa < 2.5:
            strengths.append(100)
        elif dvadasamsa < 5:
            strengths.append(90)
        elif dvadasamsa < 7.5:
            strengths.append(80)
        elif dvadasamsa < 10:
            strengths.append(70)
        elif dvadasamsa < 12.5:
            strengths.append(60)
        elif dvadasamsa < 15:
            strengths.append(50)
        elif dvadasamsa < 17.5:
            strengths.append(40)
        elif dvadasamsa < 20:
            strengths.append(30)
        elif dvadasamsa < 22.5:
            strengths.append(20)
        elif dvadasamsa < 25:
            strengths.append(10)
        else:
            strengths.append(0)
            
        # Calculate average strength across all divisions
        return sum(strengths) / len(strengths)

    def _calculate_drik_bala(self, planet: Dict[str, Any], chart: Dict[str, Any]) -> float:
        """Calculate aspectual strength"""
        # Define aspect angles and their strengths
        aspect_strengths = {
            0: 100,    # Conjunction
            60: 50,    # Sextile
            90: 25,    # Square
            120: 75,   # Trine
            180: 50    # Opposition
        }
        
        # Get planet's longitude
        planet_long = planet["longitude"]
        
        # Initialize total aspect strength
        total_strength = 0
        num_aspects = 0
        
        # Check aspects from other planets
        for other_planet in chart.get("planets", {}).values():
            if other_planet == planet:  # Skip self
                continue
                
            other_long = other_planet["longitude"]
            
            # Calculate angular distance
            distance = abs(planet_long - other_long)
            if distance > 180:
                distance = 360 - distance
                
            # Check for aspects (allowing some orb)
            for aspect_angle, base_strength in aspect_strengths.items():
                orb = 8  # Allow 8 degree orb
                if abs(distance - aspect_angle) <= orb:
                    # Calculate strength based on exactness of aspect
                    exactness = 1 - (abs(distance - aspect_angle) / orb)
                    aspect_strength = base_strength * exactness
                    
                    # Add to total
                    total_strength += aspect_strength
                    num_aspects += 1
        
        # Calculate average strength
        if num_aspects > 0:
            final_strength = total_strength / num_aspects
        else:
            final_strength = 50  # Neutral strength if no aspects
            
        return max(0, min(100, final_strength))  # Clamp between 0 and 100
