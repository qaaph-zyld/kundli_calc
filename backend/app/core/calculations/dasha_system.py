"""
Enhanced Dasha System Calculator with focus on Vimshottari Dasha
"""
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import swisseph as swe
from decimal import Decimal, ROUND_HALF_UP

class VimshottariDasha:
    """
    Implements the Vimshottari Dasha system with high precision calculations
    """
    
    def __init__(self):
        """Initialize the Vimshottari Dasha calculator"""
        # Dasha periods in years for each planet
        self.maha_dasha_periods = {
            'Ketu': 7,
            'Venus': 20,
            'Sun': 6,
            'Moon': 10,
            'Mars': 7,
            'Rahu': 18,
            'Jupiter': 16,
            'Saturn': 19,
            'Mercury': 17
        }
        
        # Planet sequence in Vimshottari
        self.planet_sequence = [
            'Ketu', 'Venus', 'Sun', 'Moon', 'Mars',
            'Rahu', 'Jupiter', 'Saturn', 'Mercury'
        ]
        
        # Nakshatra lords mapping
        self.nakshatra_lords = {
            1: 'Ketu', 2: 'Venus', 3: 'Sun',
            4: 'Moon', 5: 'Mars', 6: 'Rahu',
            7: 'Jupiter', 8: 'Saturn', 9: 'Mercury',
            10: 'Ketu', 11: 'Venus', 12: 'Sun',
            13: 'Moon', 14: 'Mars', 15: 'Rahu',
            16: 'Jupiter', 17: 'Saturn', 18: 'Mercury',
            19: 'Ketu', 20: 'Venus', 21: 'Sun',
            22: 'Moon', 23: 'Mars', 24: 'Rahu',
            25: 'Jupiter', 26: 'Saturn', 27: 'Mercury'
        }
        
        # Nakshatra span in degrees
        self.nakshatra_span = Decimal('13.333333333333334')  # 13°20'

    def calculate_birth_nakshatra_balance(self, moon_longitude: float) -> Tuple[int, float]:
        """
        Calculate birth nakshatra and remaining dasha balance with high precision
        
        Args:
            moon_longitude: Longitude of Moon (0-360)
            
        Returns:
            Tuple of (nakshatra_number, remaining_portion)
        """
        # Validate moon longitude
        if moon_longitude < 0 or moon_longitude >= 360:
            raise ValueError("Moon longitude must be between 0 and 360 degrees")
            
        # Convert to Decimal for precise calculations
        moon_long = Decimal(str(moon_longitude))
        
        # Handle exact start of zodiac
        if moon_long == Decimal('0'):
            return 1, 1.0
            
        # Calculate nakshatra number (1-27)
        nakshatra_raw = moon_long / self.nakshatra_span
        nakshatra_num = int(nakshatra_raw) + 1
        
        # Handle boundary conditions
        remainder = nakshatra_raw % 1
        
        # Calculate remaining portion with high precision
        remaining = 1 - remainder
        
        # Handle boundary cases
        if remaining > Decimal('0.999999'):
            remaining = Decimal('1')
        elif remaining < Decimal('0.000001'):
            remaining = Decimal('0')
            if nakshatra_num < 27:
                nakshatra_num += 1
                remaining = Decimal('1')
        
        # Handle last nakshatra
        if nakshatra_num > 27:
            nakshatra_num = 27
            remaining = Decimal('0')
        
        return nakshatra_num, float(remaining)

    def get_dasha_sequence(self, birth_nakshatra: int) -> List[str]:
        """
        Get the sequence of dashas starting from birth nakshatra lord
        
        Args:
            birth_nakshatra: Birth nakshatra number (1-27)
            
        Returns:
            List of planets in dasha sequence
        """
        if birth_nakshatra < 1 or birth_nakshatra > 27:
            raise ValueError("Birth nakshatra must be between 1 and 27")
            
        start_lord = self.nakshatra_lords[birth_nakshatra]
        start_idx = self.planet_sequence.index(start_lord)
        
        # Rotate sequence to start from birth nakshatra lord
        return self.planet_sequence[start_idx:] + self.planet_sequence[:start_idx]

    def calculate_dasha_periods(self, birth_date: datetime, moon_longitude: float) -> Dict:
        """
        Calculate all dasha periods from birth date with high precision
        
        Args:
            birth_date: Date and time of birth
            moon_longitude: Longitude of Moon at birth
            
        Returns:
            Dictionary containing dasha periods and their dates
        """
        # Validate moon longitude
        if moon_longitude < 0 or moon_longitude >= 360:
            raise ValueError("Moon longitude must be between 0 and 360 degrees")
            
        nakshatra_num, balance = self.calculate_birth_nakshatra_balance(moon_longitude)
        dasha_sequence = self.get_dasha_sequence(nakshatra_num)
        
        # Convert balance to Decimal for precise calculations
        balance = Decimal(str(balance))
        
        periods = []
        current_date = birth_date
        
        # First period is the remaining portion of the current dasha
        first_planet = dasha_sequence[0]
        first_period_years = Decimal(str(self.maha_dasha_periods[first_planet])) * balance
        
        # Calculate days with higher precision
        days_in_first_period = int((first_period_years * Decimal('365.25')).to_integral_value(ROUND_HALF_UP))
        end_date = current_date + timedelta(days=days_in_first_period)
        periods.append({
            'planet': first_planet,
            'start_date': current_date,
            'end_date': end_date,
            'duration_years': float(first_period_years)
        })
        current_date = end_date
        
        # Calculate subsequent full dashas
        for planet in dasha_sequence[1:]:
            years = Decimal(str(self.maha_dasha_periods[planet]))
            days = int((years * Decimal('365.25')).to_integral_value(ROUND_HALF_UP))
            end_date = current_date + timedelta(days=days)
            
            periods.append({
                'planet': planet,
                'start_date': current_date,
                'end_date': end_date,
                'duration_years': float(years)
            })
            current_date = end_date
            
        return {
            'birth_nakshatra': nakshatra_num,
            'balance': float(balance),
            'periods': periods
        }

    def calculate_antardasha(self, main_period: Dict) -> List[Dict]:
        """
        Calculate antardasha (sub-periods) for a main dasha period with high precision
        
        Args:
            main_period: Dictionary containing main period details
            
        Returns:
            List of sub-periods with dates
        """
        main_planet = main_period['planet']
        start_date = main_period['start_date']
        total_days = (main_period['end_date'] - start_date).days
        
        # Start sub-periods from the main planet
        start_idx = self.planet_sequence.index(main_planet)
        sub_sequence = self.planet_sequence[start_idx:] + self.planet_sequence[:start_idx]
        
        sub_periods = []
        current_date = start_date
        remaining_days = total_days
        
        # Convert to Decimal for precise calculations
        total_days_dec = Decimal(str(total_days))
        
        for i, sub_planet in enumerate(sub_sequence):
            # Calculate sub-period duration proportional to planet's maha dasha years
            sub_years = Decimal(str(self.maha_dasha_periods[sub_planet]))
            if i < len(sub_sequence) - 1:
                period_days = int((sub_years / Decimal('120') * total_days_dec).to_integral_value(ROUND_HALF_UP))
                remaining_days -= period_days
            else:
                # Last period gets remaining days to ensure exact end date match
                period_days = remaining_days
            
            end_date = current_date + timedelta(days=period_days)
            sub_periods.append({
                'main_planet': main_planet,
                'sub_planet': sub_planet,
                'start_date': current_date,
                'end_date': end_date,
                'duration_days': period_days
            })
            current_date = end_date
        
        return sub_periods

    def calculate_pratyantardasha(self, antardasha_period: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calculate Pratyantardasha (sub-sub periods) for a given Antardasha period
        
        Args:
            antardasha_period: Dictionary containing antardasha period details
                Required keys: main_planet, sub_planet, start_date, end_date, duration_days
                
        Returns:
            List of dictionaries containing pratyantardasha details
        """
        if not all(key in antardasha_period for key in ['main_planet', 'sub_planet', 'start_date', 'end_date', 'duration_days']):
            raise ValueError("Missing required keys in antardasha_period")
            
        total_days = antardasha_period['duration_days']
        start_date = antardasha_period['start_date']
        
        # Get dasha sequence starting from sub_planet
        dasha_sequence = self.get_dasha_sequence(
            list(self.nakshatra_lords.keys())[list(self.nakshatra_lords.values()).index(antardasha_period['sub_planet'])]
        )
        
        pratyantardasha_periods = []
        current_date = start_date
        
        for planet in dasha_sequence:
            # Calculate duration based on planet's maha dasha period
            period_days = int((Decimal(str(self.maha_dasha_periods[planet])) / Decimal('120') * Decimal(str(total_days))).to_integral_value())
            
            # Last period gets remaining days to handle rounding
            if planet == dasha_sequence[-1]:
                period_days = total_days - sum(p['duration_days'] for p in pratyantardasha_periods)
            
            end_date = current_date + timedelta(days=period_days)
            
            pratyantardasha_periods.append({
                'main_planet': antardasha_period['main_planet'],
                'sub_planet': antardasha_period['sub_planet'],
                'prat_planet': planet,
                'start_date': current_date,
                'end_date': end_date,
                'duration_days': period_days
            })
            
            current_date = end_date
            
        return pratyantardasha_periods
        
    def calculate_all_dasha_levels(self, birth_date: datetime, moon_longitude: float) -> Dict[str, Any]:
        """
        Calculate all levels of Vimshottari Dasha - Mahadasha, Antardasha, and Pratyantardasha
        
        Args:
            birth_date: Date and time of birth
            moon_longitude: Longitude of Moon at birth (0-360)
            
        Returns:
            Dictionary containing all dasha period details
        """
        # Calculate main dasha periods
        dasha_periods = self.calculate_dasha_periods(birth_date, moon_longitude)
        
        # Calculate antardasha for each main period
        for period in dasha_periods['periods']:
            period['antardasha'] = self.calculate_antardasha(period)
            
            # Calculate pratyantardasha for each antardasha
            for antardasha in period['antardasha']:
                antardasha['pratyantardasha'] = self.calculate_pratyantardasha(antardasha)
                
        return dasha_periods
