"""
Interpretations and predictions for Vimshottari Dasha periods
"""
from typing import Dict, List, Optional
from decimal import Decimal

class DashaEffects:
    """
    Provides interpretations and predictions for Vimshottari Dasha periods
    """
    
    # Planet significations and general effects
    planet_significations = {
        'Sun': [
            'authority', 'power', 'leadership', 'government', 'father',
            'self-expression', 'vitality', 'career', 'reputation'
        ],
        'Moon': [
            'mind', 'emotions', 'mother', 'public', 'popularity',
            'comfort', 'peace', 'domestic life', 'mental health'
        ],
        'Mars': [
            'energy', 'courage', 'siblings', 'property', 'technical skills',
            'sports', 'military', 'surgery', 'competition'
        ],
        'Mercury': [
            'intelligence', 'communication', 'business', 'education',
            'analytical skills', 'writing', 'trade', 'short travels'
        ],
        'Jupiter': [
            'wisdom', 'spirituality', 'wealth', 'children', 'higher education',
            'teaching', 'optimism', 'fortune', 'dharma'
        ],
        'Venus': [
            'relationships', 'luxury', 'arts', 'beauty', 'marriage',
            'pleasure', 'vehicles', 'entertainment', 'diplomacy'
        ],
        'Saturn': [
            'longevity', 'discipline', 'service', 'delays', 'hard work',
            'responsibility', 'spiritual progress', 'justice', 'karma'
        ],
        'Rahu': [
            'ambition', 'foreign influences', 'innovation', 'obsession',
            'material desires', 'unconventional paths', 'sudden changes'
        ],
        'Ketu': [
            'spirituality', 'liberation', 'psychic abilities', 'isolation',
            'detachment', 'technical excellence', 'sudden events'
        ]
    }
    
    # Planet combinations and their effects
    planet_combinations = {
        ('Sun', 'Moon'): [
            'Balance of ego and emotions',
            'Public recognition',
            'Success in government or administrative roles'
        ],
        ('Sun', 'Mars'): [
            'Leadership in technical fields',
            'Success in competitive endeavors',
            'Property gains through authority'
        ],
        ('Moon', 'Jupiter'): [
            'Emotional wisdom and stability',
            'Success in teaching or counseling',
            'Spiritual growth with peace of mind'
        ],
        ('Mars', 'Saturn'): [
            'Disciplined action and hard work',
            'Success through persistent effort',
            'Technical achievements through patience'
        ],
        ('Mercury', 'Jupiter'): [
            'Success in education and teaching',
            'Skilled communication of wisdom',
            'Profitable business ventures'
        ],
        ('Venus', 'Mercury'): [
            'Artistic communication abilities',
            'Success in entertainment or media',
            'Profitable creative ventures'
        ]
    }
    
    @classmethod
    def get_planet_effects(cls, planet: str) -> List[str]:
        """Get general effects of a planet's dasha period"""
        return cls.planet_significations.get(planet, [])
    
    @classmethod
    def get_combination_effects(cls, main_planet: str, sub_planet: str) -> List[str]:
        """Get effects of a planet combination in dasha periods"""
        # Check both orders of the combination
        effects = cls.planet_combinations.get((main_planet, sub_planet), [])
        if not effects:
            effects = cls.planet_combinations.get((sub_planet, main_planet), [])
        return effects
    
    @classmethod
    def interpret_dasha_period(cls, 
                             main_planet: str, 
                             sub_planet: Optional[str] = None, 
                             prat_planet: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Generate interpretation for a dasha period
        
        Args:
            main_planet: Main dasha lord (mahadasha)
            sub_planet: Sub-period lord (antardasha), optional
            prat_planet: Sub-sub period lord (pratyantardasha), optional
            
        Returns:
            Dictionary containing interpretations at different levels
        """
        interpretation = {
            'main_effects': cls.get_planet_effects(main_planet),
            'combinations': []
        }
        
        if sub_planet:
            interpretation['sub_effects'] = cls.get_planet_effects(sub_planet)
            interpretation['combinations'].extend(
                cls.get_combination_effects(main_planet, sub_planet)
            )
            
        if prat_planet and sub_planet:
            interpretation['prat_effects'] = cls.get_planet_effects(prat_planet)
            interpretation['combinations'].extend(
                cls.get_combination_effects(sub_planet, prat_planet)
            )
        
        return interpretation
    
    @classmethod
    def get_strength_factors(cls, planet: str) -> Dict[str, Decimal]:
        """
        Get strength factors for a planet's dasha effects
        
        Args:
            planet: Name of the planet
            
        Returns:
            Dictionary of factors that strengthen or weaken the dasha effects
        """
        # Base strength factors for each planet
        base_factors = {
            'Sun': {
                'day': Decimal('1.2'),  # Stronger during day
                'night': Decimal('0.8'),  # Weaker at night
                'season': {
                    'summer': Decimal('1.3'),  # Strong in summer
                    'winter': Decimal('0.7')   # Weak in winter
                }
            },
            'Moon': {
                'day': Decimal('0.8'),
                'night': Decimal('1.2'),
                'phase': {
                    'full': Decimal('1.5'),
                    'new': Decimal('0.5')
                }
            },
            'Mars': {
                'day': Decimal('1.1'),
                'night': Decimal('0.9'),
                'season': {
                    'summer': Decimal('1.2'),
                    'winter': Decimal('0.8')
                }
            },
            'Mercury': {
                'day': Decimal('1.0'),
                'night': Decimal('1.0'),
                'retro': Decimal('0.8')
            },
            'Jupiter': {
                'day': Decimal('1.1'),
                'night': Decimal('0.9'),
                'retro': Decimal('1.2')  # Strong in retrogression
            },
            'Venus': {
                'day': Decimal('0.9'),
                'night': Decimal('1.1'),
                'season': {
                    'spring': Decimal('1.3'),
                    'autumn': Decimal('1.1')
                }
            },
            'Saturn': {
                'day': Decimal('0.8'),
                'night': Decimal('1.2'),
                'retro': Decimal('1.1')
            },
            'Rahu': {
                'day': Decimal('0.9'),
                'night': Decimal('1.1'),
                'eclipse': Decimal('1.5')
            },
            'Ketu': {
                'day': Decimal('0.9'),
                'night': Decimal('1.1'),
                'eclipse': Decimal('1.5')
            }
        }
        
        return base_factors.get(planet, {})
