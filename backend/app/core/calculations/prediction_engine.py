"""
Prediction Engine for Vedic Astrology calculations
Handles event timing, Muhurta, and transit analysis
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import math

class PredictionEngine:
    """
    Core prediction engine implementing event timing and Muhurta calculations
    """
    
    # Muhurta qualities for different activities
    muhurta_qualities = {
        'business': ['Labha', 'Amrita', 'Siddha'],
        'marriage': ['Amrita', 'Siddha', 'Shubha'],
        'travel': ['Amrita', 'Chara', 'Labha'],
        'education': ['Vidya', 'Shubha', 'Amrita'],
        'medical': ['Amrita', 'Mrityu', 'Kala'],
        'spiritual': ['Brahma', 'Amrita', 'Abhijit']
    }
    
    # Planetary strengths required for different activities
    activity_requirements = {
        'business': {
            'mercury': 0.6,
            'jupiter': 0.5,
            'sun': 0.4
        },
        'marriage': {
            'venus': 0.7,
            'jupiter': 0.6,
            'moon': 0.5
        },
        'travel': {
            'mercury': 0.5,
            'moon': 0.5,
            'jupiter': 0.4
        },
        'education': {
            'jupiter': 0.7,
            'mercury': 0.6,
            'venus': 0.4
        },
        'medical': {
            'sun': 0.6,
            'jupiter': 0.5,
            'mars': 0.4
        },
        'spiritual': {
            'jupiter': 0.7,
            'moon': 0.6,
            'venus': 0.5
        }
    }
    
    @classmethod
    def calculate_muhurta(cls, 
                         datetime_utc: datetime,
                         activity_type: str,
                         planet_positions: Dict[str, float],
                         planet_strengths: Dict[str, float]) -> Dict[str, any]:
        """
        Calculate Muhurta suitability for given time and activity
        
        Args:
            datetime_utc: UTC datetime for calculation
            activity_type: Type of activity to analyze
            planet_positions: Current planetary positions
            planet_strengths: Current planetary strengths
            
        Returns:
            Dictionary containing Muhurta analysis
        """
        if activity_type not in cls.muhurta_qualities:
            raise ValueError(f"Invalid activity type: {activity_type}")
            
        # Calculate lunar day (tithi)
        tithi = cls._calculate_tithi(planet_positions['moon'], planet_positions['sun'])
        
        # Calculate lunar mansion (nakshatra)
        nakshatra = math.floor(planet_positions['moon'] / 13.333333)
        
        # Get required planetary strengths
        required_strengths = cls.activity_requirements.get(activity_type, {})
        
        # Check planetary strengths
        strength_analysis = {}
        total_strength = Decimal('0')
        
        for planet, required in required_strengths.items():
            current = planet_strengths.get(planet, 0)
            meets_requirement = current >= required
            strength_analysis[planet] = {
                'required': required,
                'current': current,
                'suitable': meets_requirement
            }
            total_strength += Decimal(str(current))
        
        # Calculate overall suitability
        suitability = total_strength / len(required_strengths)
        
        # Get auspicious Muhurtas for the activity
        auspicious_muhurtas = cls.muhurta_qualities[activity_type]
        
        # Calculate current Muhurta
        hour = datetime_utc.hour
        muhurta_index = (hour * 2) + (1 if datetime_utc.minute >= 30 else 0)
        current_muhurta = cls._get_muhurta_name(muhurta_index)
        
        return {
            'datetime': datetime_utc.isoformat(),
            'activity': activity_type,
            'suitability_score': float(suitability),
            'is_suitable': suitability >= Decimal('0.6'),
            'tithi': tithi,
            'nakshatra': nakshatra,
            'current_muhurta': current_muhurta,
            'is_auspicious_muhurta': current_muhurta in auspicious_muhurtas,
            'planetary_analysis': strength_analysis,
            'recommended_muhurtas': auspicious_muhurtas
        }
    
    @classmethod
    def find_next_suitable_time(cls,
                              start_time: datetime,
                              activity_type: str,
                              planet_positions: Dict[str, float],
                              planet_strengths: Dict[str, float],
                              max_days: int = 7) -> Optional[Dict[str, any]]:
        """
        Find next suitable time for given activity
        
        Args:
            start_time: UTC datetime to start search from
            activity_type: Type of activity to analyze
            planet_positions: Planetary positions
            planet_strengths: Planetary strengths
            max_days: Maximum days to look ahead
            
        Returns:
            Dictionary containing next suitable time and analysis
        """
        current_time = start_time
        end_time = start_time + timedelta(days=max_days)
        
        while current_time <= end_time:
            result = cls.calculate_muhurta(
                current_time,
                activity_type,
                planet_positions,
                planet_strengths
            )
            
            if result['is_suitable'] and result['is_auspicious_muhurta']:
                return result
            
            current_time += timedelta(minutes=30)
            
            # Update planet positions (simplified)
            for planet in planet_positions:
                planet_positions[planet] += 0.0007 # Approximate 30-minute motion
        
        return None
    
    @classmethod
    def analyze_transit_period(cls,
                             start_time: datetime,
                             end_time: datetime,
                             planet: str,
                             natal_position: float,
                             transit_positions: List[Tuple[datetime, float]]) -> Dict[str, any]:
        """
        Analyze transit period effects
        
        Args:
            start_time: Period start time
            end_time: Period end time
            planet: Planet to analyze
            natal_position: Planet's natal position
            transit_positions: List of (time, position) tuples for transit
            
        Returns:
            Dictionary containing transit analysis
        """
        aspects = []
        effects = []
        
        for time, position in transit_positions:
            # Calculate aspect angle
            angle = abs(position - natal_position)
            if angle > 180:
                angle = 360 - angle
            
            # Check major aspects
            aspect = cls._get_aspect_type(angle)
            if aspect:
                aspects.append({
                    'time': time.isoformat(),
                    'type': aspect,
                    'angle': angle,
                    'effect': cls._get_aspect_effect(aspect, planet)
                })
        
        # Analyze overall period
        strength = cls._calculate_transit_strength(aspects)
        
        return {
            'period': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'planet': planet,
            'natal_position': natal_position,
            'aspects': aspects,
            'strength': strength,
            'overall_effect': cls._get_period_effect(strength)
        }
    
    @staticmethod
    def _calculate_tithi(moon_pos: float, sun_pos: float) -> int:
        """Calculate tithi from Moon and Sun positions"""
        angle = moon_pos - sun_pos
        if angle < 0:
            angle += 360
        return math.floor(angle / 12) + 1
    
    @staticmethod
    def _get_muhurta_name(index: int) -> str:
        """Get Muhurta name from index"""
        muhurtas = [
            'Rudra', 'Brahma', 'Vidya', 'Kala', 'Siddha',
            'Amrita', 'Chara', 'Labha', 'Shubha', 'Mrityu'
        ]
        return muhurtas[index % len(muhurtas)]
    
    @staticmethod
    def _get_aspect_type(angle: float) -> Optional[str]:
        """Get aspect type from angle"""
        aspects = {
            0: 'Conjunction',
            60: 'Sextile',
            90: 'Square',
            120: 'Trine',
            180: 'Opposition'
        }
        
        for aspect_angle, aspect_name in aspects.items():
            if abs(angle - aspect_angle) <= 8:  # 8-degree orb
                return aspect_name
        return None
    
    @staticmethod
    def _get_aspect_effect(aspect: str, planet: str) -> str:
        """Get effect description for aspect"""
        effects = {
            'Conjunction': 'Strong influence and new beginnings',
            'Sextile': 'Opportunities and positive growth',
            'Square': 'Challenges and necessary changes',
            'Trine': 'Harmony and natural flow',
            'Opposition': 'Awareness and culmination'
        }
        return effects.get(aspect, 'Neutral effect')
    
    @staticmethod
    def _calculate_transit_strength(aspects: List[Dict]) -> float:
        """Calculate transit period strength"""
        weights = {
            'Conjunction': 1.0,
            'Trine': 0.8,
            'Sextile': 0.6,
            'Square': -0.5,
            'Opposition': -0.8
        }
        
        total_weight = 0
        for aspect in aspects:
            total_weight += weights.get(aspect['type'], 0)
            
        return max(0, min(1, (total_weight + 1) / 2))
    
    @staticmethod
    def _get_period_effect(strength: float) -> str:
        """Get period effect description based on strength"""
        if strength >= 0.8:
            return "Highly favorable period"
        elif strength >= 0.6:
            return "Generally favorable period"
        elif strength >= 0.4:
            return "Mixed influences"
        elif strength >= 0.2:
            return "Some challenges present"
        else:
            return "Difficult period"
