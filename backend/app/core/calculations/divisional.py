from typing import Dict, Any, List
import math

class EnhancedDivisionalChartEngine:
    """Enhanced engine for calculating divisional charts with improved precision"""
    
    def __init__(self):
        # Define zodiac signs and their natural lords
        self.zodiac_signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        
        # Define special divisional chart rules
        self.special_divisions = {
            'D9': self._calculate_navamsa,
            'D12': self._calculate_dwadasamsa,
            'D30': self._calculate_trimsamsa
        }
    
    def _normalize_longitude(self, longitude: float) -> float:
        """Normalize longitude to 0-360 range with high precision"""
        return round(longitude % 360, 6)
    
    def _get_sign_from_longitude(self, longitude: float) -> int:
        """Get zodiac sign index (0-11) from longitude"""
        return int(self._normalize_longitude(longitude) / 30)
    
    def _calculate_division_remainder(self, longitude: float, division: int) -> float:
        """Calculate remainder for division charts with high precision"""
        sign_longitude = longitude % 30
        division_size = 30 / division
        division_index = math.floor(sign_longitude / division_size)
        return division_index * division_size
    
    def _calculate_navamsa(self, longitude: float) -> float:
        """
        Calculate Navamsa (D9) position
        - Each sign is divided into 9 equal parts of 3°20'
        - Starting points vary by element:
          Fire signs (Aries, Leo, Sagittarius) -> Start from Aries
          Earth signs (Taurus, Virgo, Capricorn) -> Start from Cancer
          Air signs (Gemini, Libra, Aquarius) -> Start from Libra
          Water signs (Cancer, Scorpio, Pisces) -> Start from Capricorn
        """
        sign_num = int(longitude / 30)  # Current sign number (0-11)
        sign_pos = longitude % 30  # Position within the sign
        
        # Calculate navamsa number within sign (0-8)
        navamsa_size = 30 / 9  # 3°20'
        navamsa_num = int(sign_pos / navamsa_size)
        
        # Determine element (0=Fire, 1=Earth, 2=Air, 3=Water)
        element = sign_num % 4  # Every fourth sign belongs to the same element
        
        # Starting points for each element (in signs)
        start_points = {
            0: 0,   # Fire -> Aries
            1: 3,   # Earth -> Cancer
            2: 6,   # Air -> Libra
            3: 9    # Water -> Capricorn
        }
        
        # Calculate navamsa position
        navamsa_sign = (start_points[element] + navamsa_num) % 12
        navamsa_pos = navamsa_sign * 30 + (sign_pos % navamsa_size) / navamsa_size * 30
        
        return round(navamsa_pos % 360, 6)

    def _calculate_dwadasamsa(self, longitude: float) -> float:
        """
        Calculate Dwadasamsa (D12) position
        - Each sign is divided into 12 equal parts of 2°30'
        - The count starts from the current sign and moves forward
        """
        sign_num = int(longitude / 30)  # Current sign number (0-11)
        sign_pos = longitude % 30  # Position within the sign
        
        # Calculate dwadasamsa number within sign (0-11)
        dwadasamsa_size = 30 / 12  # 2°30'
        dwadasamsa_num = int(sign_pos / dwadasamsa_size)
        
        # Calculate dwadasamsa position
        # Start from the current sign and move forward based on the division number
        dwadasamsa_sign = (sign_num + dwadasamsa_num) % 12
        dwadasamsa_pos = dwadasamsa_sign * 30 + (sign_pos % dwadasamsa_size) / dwadasamsa_size * 30
        
        return round(dwadasamsa_pos % 360, 6)

    def _calculate_trimsamsa(self, longitude: float) -> float:
        """
        Calculate Trimsamsa (D30) position with special rules for odd/even signs
        - Odd signs: 5° each to Mars, Saturn, Jupiter, Mercury, Venus
        - Even signs: 5° each to Venus, Mercury, Jupiter, Saturn, Mars
        """
        sign_index = self._get_sign_from_longitude(longitude)
        sign_longitude = longitude % 30
        
        # Define planet sequences for odd and even signs
        odd_sequence = [0, 6, 4, 2, 1]  # Mars, Saturn, Jupiter, Mercury, Venus
        even_sequence = [1, 2, 4, 6, 0]  # Venus, Mercury, Jupiter, Saturn, Mars
        
        is_odd_sign = sign_index % 2 == 0
        sequence = odd_sequence if is_odd_sign else even_sequence
        
        # Find which 5° segment the longitude falls in
        segment = min(math.floor(sign_longitude / 5), 5)
        planet_index = sequence[segment] if segment < len(sequence) else 0
        
        return planet_index * 30 + (sign_longitude % 5) * 6
    
    def calculate_divisional_chart(
        self,
        longitudes: Dict[str, float],
        division: int,
        apply_special_rules: bool = True
    ) -> Dict[str, float]:
        """
        Calculate divisional chart positions for all planets
        
        Args:
            longitudes: Dictionary of planet longitudes
            division: Division number (1-40)
            apply_special_rules: Whether to apply special rules for D9, D12, D30
        
        Returns:
            Dictionary of calculated divisional positions
        """
        if division < 1 or division > 40:
            raise ValueError("Division must be between 1 and 40")
        
        result = {}
        division_type = f'D{division}'
        
        for planet, longitude in longitudes.items():
            # Check if special calculation is needed
            if apply_special_rules and division_type in self.special_divisions:
                result[planet] = self._normalize_longitude(
                    self.special_divisions[division_type](longitude)
                )
            else:
                # Standard division calculation
                sign_index = self._get_sign_from_longitude(longitude)
                sign_remainder = self._calculate_division_remainder(longitude, division)
                
                result[planet] = self._normalize_longitude(
                    sign_index * 30 + sign_remainder * division
                )
        
        return result
