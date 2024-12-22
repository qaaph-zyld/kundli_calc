from typing import Dict, Any, Optional, List
import math

class EnhancedDivisionalChartEngine:
    def __init__(self):
        self.division_rules = {
            'D1': {'denominator': 1, 'special_rules': None},
            'D2': {'denominator': 2, 'special_rules': None},  # Hora
            'D3': {'denominator': 3, 'special_rules': None},  # Drekkana
            'D4': {'denominator': 4, 'special_rules': None},  # Chaturthamsa
            'D7': {'denominator': 7, 'special_rules': None},  # Saptamsa
            'D9': {'denominator': 9, 'special_rules': self._navamsa_special_rules},  # Navamsa
            'D10': {'denominator': 10, 'special_rules': None},  # Dasamsa
            'D12': {'denominator': 12, 'special_rules': self._dwadasamsa_special_rules},  # Dwadasamsa
            'D16': {'denominator': 16, 'special_rules': None},  # Shodasamsa
            'D20': {'denominator': 20, 'special_rules': None},  # Vimsamsa
            'D24': {'denominator': 24, 'special_rules': None},  # Chaturvimsamsa
            'D27': {'denominator': 27, 'special_rules': self._nakshatramsa_special_rules},  # Nakshatramsa
            'D30': {'denominator': 30, 'special_rules': self._trimsamsa_special_rules},  # Trimsamsa
            'D40': {'denominator': 40, 'special_rules': None},  # Khavedamsa
            'D45': {'denominator': 45, 'special_rules': None},  # Akshavedamsa
            'D60': {'denominator': 60, 'special_rules': None},  # Shashtiamsa
        }
        
        # Pada calculation rules
        self.pada_rules = {
            'movable': self._calculate_movable_pada,
            'fixed': self._calculate_fixed_pada,
            'dual': self._calculate_dual_pada
        }
        
        # Sign nature mapping
        self.sign_nature = {
            0: 'movable',  # Aries
            1: 'fixed',    # Taurus
            2: 'dual',     # Gemini
            3: 'movable',  # Cancer
            4: 'fixed',    # Leo
            5: 'dual',     # Virgo
            6: 'movable',  # Libra
            7: 'fixed',    # Scorpio
            8: 'dual',     # Sagittarius
            9: 'movable',  # Capricorn
            10: 'fixed',   # Aquarius
            11: 'dual'     # Pisces
        }
    
    def _get_sign(self, longitude: float) -> int:
        """Get the zodiac sign (0-11) for a given longitude"""
        return int(longitude / 30)
    
    def _get_sign_degree(self, longitude: float) -> float:
        """Get the degree within the sign (0-29.99...)"""
        return longitude % 30
    
    def _calculate_movable_pada(self, longitude: float) -> int:
        """Calculate pada for movable signs"""
        degree = self._get_sign_degree(longitude)
        return int(degree / 7.5) + 1
    
    def _calculate_fixed_pada(self, longitude: float) -> int:
        """Calculate pada for fixed signs"""
        degree = self._get_sign_degree(longitude)
        return int(degree / 7.5) + 1
    
    def _calculate_dual_pada(self, longitude: float) -> int:
        """Calculate pada for dual signs"""
        degree = self._get_sign_degree(longitude)
        return int(degree / 7.5) + 1
    
    def _navamsa_special_rules(self, longitude: float) -> float:
        """Special rules for Navamsa (D9) calculation"""
        sign = self._get_sign(longitude)
        degree = self._get_sign_degree(longitude)
        nature = self.sign_nature[sign]
        
        # Calculate pada
        pada = self.pada_rules[nature](longitude)
        
        # Apply special navamsa rules
        navamsa_longitude = ((sign * 9) + (degree * 0.3)) % 12
        return navamsa_longitude * 30 + (pada - 1) * 3.333333
    
    def _dwadasamsa_special_rules(self, longitude: float) -> float:
        """Special rules for Dwadasamsa (D12) calculation"""
        sign = self._get_sign(longitude)
        degree = self._get_sign_degree(longitude)
        
        # Each sign is divided into 12 parts of 2.5 degrees each
        division = int(degree / 2.5)
        result_sign = (sign + division) % 12
        
        return result_sign * 30 + (degree % 2.5) * 12
    
    def _nakshatramsa_special_rules(self, longitude: float) -> float:
        """Special rules for Nakshatramsa (D27) calculation"""
        # Each nakshatra is 13°20' (13.333... degrees)
        nakshatra = int(longitude / 13.333333)
        remainder = longitude % 13.333333
        
        return nakshatra * 30 + remainder * 2.25
    
    def _trimsamsa_special_rules(self, longitude: float) -> float:
        """Special rules for Trimsamsa (D30) calculation"""
        sign = self._get_sign(longitude)
        degree = self._get_sign_degree(longitude)
        
        # Different division rules for odd and even signs
        if sign % 2 == 0:  # Odd signs (Aries, Gemini, etc.)
            if degree < 5:
                result_sign = 0  # Mars
            elif degree < 10:
                result_sign = 1  # Saturn
            elif degree < 18:
                result_sign = 2  # Jupiter
            elif degree < 25:
                result_sign = 3  # Mercury
            else:
                result_sign = 4  # Venus
        else:  # Even signs (Taurus, Cancer, etc.)
            if degree < 5:
                result_sign = 4  # Venus
            elif degree < 12:
                result_sign = 3  # Mercury
            elif degree < 20:
                result_sign = 2  # Jupiter
            elif degree < 25:
                result_sign = 1  # Saturn
            else:
                result_sign = 0  # Mars
        
        return result_sign * 30 + (degree % 5) * 6
    
    def _calculate_division(self, longitude: float, division: str) -> float:
        """
        Calculate divisional chart position
        
        Args:
            longitude: The longitude to calculate division for
            division: The division to calculate (D1, D9, etc.)
            
        Returns:
            float: The calculated position in the divisional chart
        """
        if division not in self.division_rules:
            raise ValueError(f"Unsupported division: {division}")
        
        rule = self.division_rules[division]
        denominator = rule['denominator']
        special_rules = rule['special_rules']
        
        if special_rules:
            return special_rules(longitude)
        
        # Standard division calculation
        sign = self._get_sign(longitude)
        degree = self._get_sign_degree(longitude)
        
        division_size = 30 / denominator
        division_index = int(degree / division_size)
        result_sign = (sign * denominator + division_index) % 12
        
        return result_sign * 30 + (degree % division_size) * denominator
    
    def calculate_all_divisions(
        self,
        longitude: float,
        divisions: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Calculate all specified divisional charts for a given longitude
        
        Args:
            longitude: The longitude to calculate divisions for
            divisions: List of divisions to calculate (if None, calculates all)
            
        Returns:
            Dict[str, float]: Dictionary of division names and their calculated positions
        """
        if divisions is None:
            divisions = list(self.division_rules.keys())
        
        results = {}
        for division in divisions:
            if division in self.division_rules:
                results[division] = self._calculate_division(longitude, division)
        
        return results
